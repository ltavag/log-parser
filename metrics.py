#! /usr/bin/python3

from collections import namedtuple
from access_log_generator import RESPONSES


DIMENSIONS = ['section', 'user', 'response_code', 'ip']

"""
    Metric dicts are of the form
    {
        "section":{
                    "politics":1,
                    "jobs":1,
                    ..
                  },
        "user":{
                    "...
               }
    }
"""


class MetricStorage(dict):
    current_interval = 0

    def __init__(self, intervals=12):
        self.intervals = intervals

    def store(self, metrics):
        if self.current_interval == self.intervals - 1:
            self.current_interval = 0
        else:
            self.current_interval += 1

        self[self.current_interval] = metrics

    def get_current_metrics(self):
        return self[current_interval]

    def __add__(self, metrics):
        self.store(metrics)
        return self

    def high_traffic(self, threshold):
        avg = sum(self[x]['response'][y]
                  for x in range(0, self.intervals)
                  for y in RESPONSES) / float(self.intervals)
        return avg > threshold
