#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import os
import sys
from multiprocessing import Process
import argparse


class Exporter(BaseHTTPRequestHandler):
    def _choose_response(self):
        data_dir = "prometheus_data"
        possibilities = os.listdir(data_dir)
        choice = random.choice(possibilities)
        response = open(f"{data_dir}/{choice}").read().encode()
        return response

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; version=0.0.4")
        self.end_headers()
        response = self._choose_response()
        self.wfile.write(response)


def run(server_class=HTTPServer, handler_class=Exporter, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting exporter on {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prometheus exporter that serves random sets of precalculated data"
    )
    parser.add_argument("--port", type=int, help="Starting port", default=8000)
    parser.add_argument(
        "--num-exporters", type=int, help="Number of exporters to run", default=1
    )
    args = parser.parse_args()
    if args.num_exporters == 1:
        run(port=args.port)
    else:
        exporters = []
        for n in range(args.num_exporters):
            our_port = args.port + n
            exporter = Process(target=run, kwargs={"port": our_port})
            exporters.append(exporter)
            exporter.start()
        for exporter in exporters:
            exporter.join()
