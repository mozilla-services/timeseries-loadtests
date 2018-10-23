#!/usr/bin/env python3

import re
import json

prometheus_batchnum = 0
prometheus_batchsize = 1000
prometheus_batch = []

opentsdb_batchnum = 0
opentsdb_batchsize = 1000
opentsdb_batch = []

input = open("data", "r")
for line in input:
    m = re.match(r"ctr,some=(tag-\w+) n=(\d+)i (\d+)", line)
    if m:
        tagvalue = m.group(1)
        fieldvalue = int(m.group(2))
        timestamp = int(m.group(3))

        # ignoring timestamp for prometheus
        prometheus_metric = 'ctr{some="%s",field="n"} %s\n' % (tagvalue, fieldvalue)
        prometheus_batch.append(prometheus_metric)

        opentsb_metric = {
            "metric": "ctr",
            # convert nanoseconds since epoch to seconds
            "timestamp": round(timestamp / 1000000000),
            "value": fieldvalue,
            "tags": {"some": tagvalue, "field": "n"},
        }
        opentsdb_batch.append(opentsb_metric)

    if len(prometheus_batch) == prometheus_batchsize:
        print("Writing prometheus batch %s" % prometheus_batchnum)
        batchfile = open("prometheus_data/%s" % prometheus_batchnum, "w")
        batchfile.writelines(prometheus_batch)
        prometheus_batch = []
        prometheus_batchnum = prometheus_batchnum + 1

    if len(opentsdb_batch) == opentsdb_batchsize:
        print("Writing opentsdb batch %s" % opentsdb_batchnum)
        batchfile = open("opentsdb_data/%s" % opentsdb_batchnum, "w")
        batchfile.writelines(json.dumps(opentsdb_batch))
        opentsdb_batch = []
        opentsdb_batchnum = opentsdb_batchnum + 1
