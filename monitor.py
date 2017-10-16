#! /usr/bin/python3

import asyncio
import sys
from collections import defaultdict
from metrics import MetricStorage, DIMENSIONS
import json
import datetime
from display import *
import alerts

ALERT_INTERVAL = 25
REPORTING_TIME = 5
LOG_PARTS = ['ip',
             'userid',
             'user',
             'time',
             'method',
             'path',
             'response_code',
             'size']
METRICS = None
INTERVALS = int(ALERT_INTERVAL / REPORTING_TIME)
DB = MetricStorage(intervals=INTERVALS)
AlertSystem = alerts.Alerter('alerts.json', ALERT_INTERVAL)


def commit_metrics():
    global METRICS
    global DB
    if METRICS:
        DB += METRICS
    METRICS = {x: defaultdict(int) for x in DIMENSIONS}


commit_metrics()


def special_split(x):
    """
        Special split method to prevent
        fragmentation of time stamp.
    """
    ret = []
    split = iter(x.split())
    for y in split:
        if y.startswith('['):
            y += ' ' + split.__next__()
        ret.append(y)
    return ret


def process_log(fd):
    """
        This function is responsible for:
            1. Parsing each log
            2. Incrementing metrics using information in the log
            3. Using the timestamp of the log to determine if
               we need to start a new time based partition in our
               metrics data structure
    """

    log = fd.readline()
    log_dict = dict(zip(LOG_PARTS, special_split(log)[:8]))
    if not log_dict:
        return
    split_path = log_dict.get('path', '').split('/')
    log_dict['section'] = split_path[1] if len(split_path) > 1 else ''
    log_dict['timestamp'] = datetime.datetime.strptime(log_dict['time'][1:-1],
                                                       '%d/%b/%Y:%H:%M:%S %z').timestamp()
    log_dict['general'] = 'hits'

    if not DB.last_timestamp:
        DB.last_timestamp = log_dict['timestamp']

    if log_dict['timestamp'] - DB.last_timestamp >= REPORTING_TIME:
        DB.last_timestamp = log_dict['timestamp']
        commit_metrics()
        display_report()

    for k in METRICS:
        METRICS[k][log_dict[k]] += 1


def calculate_stats(metrics):
    hits = metrics['general']['hits']
    pct_200 = str(metrics['response_code']['200'] * 100 / float(hits))[:4]
    top_sections = [x for x in metrics['section']
                    if metrics['section'][x] == max(metrics['section'].values())]
    top_users = [x for x in metrics['user'] if metrics['user']
                 [x] == max(metrics['user'].values())]

    all_stats = []
    all_stats.append({'Total Requests': hits, '200 Success %': pct_200})
    all_stats.append({'Top Section(s)': ','.join(
        top_sections), 'Top User(s)': ','.join(top_users)})
    return all_stats


def display_report():
    stats = calculate_stats(DB.get_current_metrics())
    triggered, resolved = AlertSystem.evaluate_alerts(DB)

    display_message('Last {} seconds'.format(REPORTING_TIME))
    display_stats(stats)
    display_alerts(triggered, resolved)
    print('\n')


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.add_reader(sys.stdin, process_log, sys.stdin)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
