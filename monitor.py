#! /usr/bin/python3

import asyncio
import sys
from collections import defaultdict
from metrics import MetricStorage, DIMENSIONS
import json
import datetime

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
LAST_TIMESTAMP = None


def rotate_metrics_out():
    global METRICS
    global DB
    if METRICS:
        DB += METRICS
    METRICS = {x: defaultdict(int) for x in DIMENSIONS}
    METRICS['requests'] = 0


rotate_metrics_out()


def parse_log(log):
    """
        This function is responsible for:
            1. Parsing each log
            2. Incrementing metrics using information in the log
            3. Using the timestamp of the log to determine if
               we need to start a new time based partition in our
               metrics data structure
    """
    global LAST_TIMESTAMP

    log_dict = dict(zip(LOG_PARTS, log.split('\t')[:8]))
    log_dict['section'] = log_dict['path'].split('/')[1]
    log_dict['timestamp'] = datetime.datetime.strptime(log_dict['time'][1:-1],
                                                       '%d/%b/%Y:%H:%M:%S %z').timestamp()

    if not LAST_TIMESTAMP:
        LAST_TIMESTAMP = log_dict['timestamp']
    if log_dict['timestamp'] - LAST_TIMESTAMP >= REPORTING_TIME:
        rotate_metrics_out()
        LAST_TIMESTAMP = log_dict['timestamp']

    for k in METRICS:
        if k == 'requests':
            continue
        METRICS[k][log_dict[k]] += 1

    METRICS['requests'] += 1


def process_log(fd):
    data = fd.readline()
    parse_log(data)


@asyncio.coroutine
def report():
    while True:
        yield from asyncio.sleep(REPORTING_TIME)
        print('{} requests in the last {} seconds'.format(
            METRICS['requests'], REPORTING_TIME))

        for section in METRICS['section']:
            print(section, METRICS['section'][section])

        all_stored_requests = DB.window_sum('requests')
        if all_stored_requests / 12. > 9:
            print("High traffic generated an alert - hits = {value}, triggered at {time}".format(
                value=all_stored_requests, time=LAST_TIMESTAMP))


def main():
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, process_log, sys.stdin)
    loop.run_until_complete(report())


if __name__ == '__main__':
    main()
