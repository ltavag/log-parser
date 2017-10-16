#! /usr/bin/python3

from collections import namedtuple, defaultdict

DIMENSIONS = ['section', 'user', 'response_code', 'ip', 'general']

"""
    Metric dicts are of the form
    {
        "hits":13,
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
    """
        This data structure is meant to
        keep track of a moving window of stats.
        Once all intervals have stats, it loops
        back around so that the a constant amount
        of space is used once full.
    """
    current_interval = 0
    last_timestamp = None

    def __init__(self, intervals=12):
        self.intervals = intervals

    def store(self, metrics):
        if self.current_interval == self.intervals - 1:
            self.current_interval = 0
        else:
            self.current_interval += 1

        self[self.current_interval] = metrics

    def get_current_metrics(self):
        return self.get(self.current_interval, {})

    def __add__(self, metrics):
        self.store(metrics)
        return self

    def window_sum(self, dimension):
        x, y = dimension.split('.')
        return sum(self[i][x][y] for i in self.keys())

    def alert_triggered(self, dimension, operator, threshold):
        total = self.window_sum(dimension)
        avg = total / self.intervals

        if operator == 'GREATER':
            if avg >= threshold:
                return True, total

        if operator == 'LESS':
            if avg <= threshold:
                return True, total

        return False, None
