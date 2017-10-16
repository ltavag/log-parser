#! /usr/bin/python
import os
import sys
import subprocess
import shlex


def run_test(logfile):
    cat = subprocess.Popen(shlex.split(
        'cat {}'.format(logfile)), stdout=subprocess.PIPE)
    monitor = subprocess.Popen(shlex.split(
        'python3 ../monitor.py --non-persistent --seconds 1 --alerts-only'), stdin=cat.stdout, stdout=subprocess.PIPE)
    return monitor.communicate()[0]


def test_alerts():
    unencoded_result = b'\x1b[31mHigh Traffic generated an alert - general.hits = 50.166666666666664, triggered at 12:19:42\x1b[0m\n\x1b[32mHigh Traffic alert recovered at 12:21:02\x1b[0m\n\x1b[31mHigh Traffic generated an alert - general.hits = 50.0, triggered at 12:21:22\x1b[0m\n'
    assert(run_test('logs/alert_test_logs')
           ) == unencoded_result, 'Alerts are not being properly triggered'


if __name__ == '__main__':
    print('Usage: {}'.format('python3 -m py.test .'))
