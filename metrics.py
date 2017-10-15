#! /usr/bin/python3

from collections import namedtuple, defaultdict
from access_log_generator import RESPONSES


DIMENSIONS = ['section', 'user', 'response_code', 'ip']

"""
    Metric dicts are of the form
    {
        "requests":13,
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

    def window_sum(self, dimension):
        if dimension == 'requests':
            return sum(self[x]['requests'] for x in range(0, self.intervals) if x in self)

        totals = defaultdict(int)
        for interval, metrics in self.items():
            for k, v in metrics.items():
                totals[k] += v

        return totals
