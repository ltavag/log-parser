#! /usr/bin/python3

import asyncio
import sys
from collections import defaultdict
from metrics import MetricStorage, DIMENSIONS
import json
import datetime
from display import *

REPORTING_TIME = 5
ALERT_INTERVAL = 25
LOG_PARTS = ['ip',
             'userid',
             'user',
             'time',
             'method',
             'path',
             'response_code',
             'size']
METRICS = None
LAST_TIMESTAMP = None
INTERVALS = int(ALERT_INTERVAL / REPORTING_TIME)
DB = MetricStorage(intervals=INTERVALS)
ALERTS = json.load(open('alerts.json'))
ALERT_STATUSES = {k: False for k in ALERTS}


def rotate_metrics_out():
    global METRICS
    global DB
    if METRICS:
        DB += METRICS
    METRICS = {x: defaultdict(int) for x in DIMENSIONS}


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
    log_dict['general'] = 'hits'
    # print(log_dict)

    if not LAST_TIMESTAMP:
        LAST_TIMESTAMP = log_dict['timestamp']
    if log_dict['timestamp'] - LAST_TIMESTAMP >= REPORTING_TIME:
        rotate_metrics_out()
        LAST_TIMESTAMP = log_dict['timestamp']

    for k in METRICS:
        METRICS[k][log_dict[k]] += 1


def process_log(fd):
    data = fd.readline()
    parse_log(data)


@asyncio.coroutine
def display_report():
    while True:
        yield from asyncio.sleep(REPORTING_TIME)
        last_metrics = DB.get_current_metrics()

        if last_metrics:
            display_regular_stats(last_metrics)
            evaluate_alerts()
            print('\n')


def display_regular_stats(metrics):
    """
        Make sure we report from the last full bucket
        of metrics. This way we can prevent issues where
        a delay in the logs causes our reporting interval
        to get out of sync with the access logs coming in.
    """
    display_message('Last {} seconds'.format(REPORTING_TIME))

    hits = metrics['general']['hits']
    pct_200 = str(metrics['response_code']['200'] * 100 / float(hits))[:4]

    display_stats({'Total Requests': hits,
                   '200 Success %': pct_200})

    top_sections = [x for x in metrics['section']
                    if metrics['section'][x] == max(metrics['section'].values())]
    top_users = [x for x in metrics['user'] if metrics['user']
                 [x] == max(metrics['user'].values())]

    display_stats({'Top Section(s)': ','.join(top_sections),
                   'Top User(s)': ','.join(top_users)})


def evaluate_alerts():
    for alert_name, alert in ALERTS.items():
        triggered, alert_val = DB.alert_triggered(**alert)

        if not ALERT_STATUSES[alert_name] and \
                triggered:
            ALERT_STATUSES[alert_name] = True
            display_alert_triggered("{alert_name} generated an alert - {dimension} = {value}, triggered at {time}".format(
                dimension=alert['dimension'],
                alert_name=alert_name,
                value=alert_val,
                time=LAST_TIMESTAMP))

        if ALERT_STATUSES[alert_name] and \
                not triggered:
            ALERT_STATUSES[alert_name] = False
            display_alert_resolved("{alert_name} alert has recovered".format(
                alert_name=alert_name))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, process_log, sys.stdin)
    loop.run_until_complete(display_report())
