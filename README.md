# Purpose

In influx-stress we found a tool that is able to generate a representative data set and write it to influxdb, but we failed to find suitable tools for prometheus and opentsdb.

I had the idea that we could use influx-stress to generate the data set and then create scripts for writing it to prometheus and opentsdb. This is the result. Each time the prometheus or opentsdb script publishes data, it will randomly choose one of the entries from the data set.

# Preprocessing

Input data was generated with

```
$ influx-stress insert --dump data --series 2000000 --points 2000000 --batch-size 1000
```

and then processed for opentsdb and prometheus with

```
$ mkdir prometheus_data
$ mkdir opentsdb_data
$ ./format_data.py
```

For each database that results in 2000 files with 1000 timeseries each in the format they expect for ingestion. All of the timeseries are unique, All of the timeseries are unique.

# Running

## Prometheus

To run a single prometheus exporter, just

```
$ ./prometheus_exporter.py
Starting exporter on 8000
```

To run more than one, specify a starting port and the number to run, e.g.

```
$ ./prometheus_exporter.py --port 8000 --num-exporters=3
Starting exporter on 8001
Starting exporter on 8000
Starting exporter on 8002
```

## OpenTSDB

Before running this you must `pip install requests`

```
usage: opentsdb_writer.py [-h] [--num-writers NUM_WRITERS]
                          [--write-interval WRITE_INTERVAL]
                          [--num-writes NUM_WRITES] [--timeout TIMEOUT]
                          [--verbose]
                          server

Send random sets of precalculated data to OpenTSDB

positional arguments:
  server                OpenTSDB server to write to

optional arguments:
  -h, --help            show this help message and exit
  --num-writers NUM_WRITERS
                        Number of concurrent writers
  --write-interval WRITE_INTERVAL
                        How often to write
  --num-writes NUM_WRITES
                        Total number of writes to make. Default and minimum is
                        number of writers.
  --timeout TIMEOUT     How long to wait for a response before aborting the
                        benchmark
  --verbose             Output status of each request
```
