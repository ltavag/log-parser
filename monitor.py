#! /usr/bin/python3

import asyncio
import sys
from collections import defaultdict
from metrics import MetricStorage, DIMENSIONS
import json

REPORTING_TIME = 2
LOG_PARTS = ['ip',
             'userid',
             'user',
             'time',
             'method',
             'path',
             'response_code',
             'size']
DB = MetricStorage()
METRICS = None


def rotate_metrics_out():
    global RECENT_REQUESTS
    global TOP_SECTIONS
    global METRICS
    global DB

    print(json.dumps(DB, indent=2))
    if METRICS:
        DB += METRICS
    RECENT_REQUESTS = 0
    METRICS = {x: defaultdict(int) for x in DIMENSIONS}


rotate_metrics_out()


def parse_log(log):
    log_dict = dict(zip(LOG_PARTS, log.split('\t')[:8]))
    log_dict['section'] = log_dict['path'].split('/')[1]
    for k in METRICS:
        METRICS[k][log_dict[k]] += 1


def process_log(fd):
    global RECENT_REQUESTS
    data = fd.readline()
    RECENT_REQUESTS += 1
    parse_log(data)


@asyncio.coroutine
def report():
    while True:
        yield from asyncio.sleep(REPORTING_TIME)
        print('{} requests in the last {} seconds'.format(
            RECENT_REQUESTS, REPORTING_TIME))

        for section in METRICS['section']:
            print(section, METRICS['section'][section])

        rotate_metrics_out()


def main():
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, process_log, sys.stdin)
    loop.run_until_complete(report())


if __name__ == '__main__':
    main()
