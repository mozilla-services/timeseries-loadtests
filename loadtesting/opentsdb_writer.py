#!/usr/bin/env python3

import argparse
import logging
import os
import math
import random
import requests
import time
from datetime import datetime
from collections import defaultdict
import concurrent.futures

# mostly copypaste from prometheus exporter
def choose_data():
    data_dir = "opentsdb_data"
    possibilities = os.listdir(data_dir)
    choice = random.choice(possibilities)
    response = open(f"{data_dir}/{choice}").read().encode()
    return response


def writer(server, write_interval, num_writes, timeout):
    # splay starts of writers
    time.sleep(random.randint(0, write_interval))
    # store info on writes
    metrics = defaultdict(int)
    log = logging.getLogger(__name__)
    for i in range(num_writes):
        data = choose_data()

        start_time = datetime.now()
        # http://opentsdb.net/docs/build/html/api_http/put.html
        r = requests.post(f"{server}/api/put", data=data, timeout=timeout)
        stop_time = datetime.now()
        duration = (stop_time - start_time).total_seconds()

        if r.status_code == 204:
            log.debug(f"Successful request to {r.url}")
            metrics["success_count"] = metrics["success_count"] + 1
            metrics["success_duration"] = metrics["success_duration"] + duration
        else:
            log.debug(f"Failed request to {r.url}")
            log.debug(r.content)
            metrics["failure_count"] = metrics["failure_count"] + 1
            metrics["failure_duration"] = metrics["failure_duration"] + duration

        if duration > write_interval:
            metrics["overrun_count"] = metrics["overrun_count"] + 1
        else:
            sleep_length = write_interval - duration
            time.sleep(sleep_length)
    return metrics


def combine_results(results):
    combined_result = defaultdict(int)
    for result in results:
        for key in (
            "success_count",
            "success_duration",
            "failure_count",
            "failure_duration",
            "overrun_count",
        ):
            combined_result[key] = combined_result[key] + result[key]
    return combined_result


def print_result(result):
    for key in (
        "success_count",
        "success_duration",
        "failure_count",
        "failure_duration",
        "overrun_count",
    ):
        print(f"{key}: {result[key]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send random sets of precalculated data to OpenTSDB"
    )
    parser.add_argument("server", type=str, help="OpenTSDB server to write to")
    parser.add_argument(
        "--num-writers", type=int, help="Number of concurrent writers", default=1
    )
    parser.add_argument(
        "--write-interval", type=int, help="How often to write", default=1
    )
    parser.add_argument(
        "--num-writes",
        type=int,
        help="Total number of writes to make. Default and minimum is number of writers.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="How long to wait for a response before aborting the benchmark",
        default=10,
    )
    parser.add_argument(
        "--verbose", help="Output status of each request", action="store_true"
    )
    args = parser.parse_args()
    logging.basicConfig()

    if args.verbose:
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)

    if args.num_writes:
        writes_per_writer = math.ceil(args.num_writes / args.num_writers)
    else:
        writes_per_writer = 1

    if args.num_writers == 1:
        result = writer(
            args.server, args.write_interval, writes_per_writer, args.timeout
        )
        print_result(result)
    else:
        # approach from https://docs.python.org/3.7/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=args.num_writers
        ) as executor:
            futures = [
                executor.submit(
                    writer,
                    args.server,
                    args.write_interval,
                    writes_per_writer,
                    args.timeout,
                )
                for i in range(args.num_writers)
            ]
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    print(f"Writer generated an exception: {exc}")
            result = combine_results(results)
            print_result(result)

