import json
from display import *
import datetime


class Alerter():
    def __init__(self, alert_file, alert_interval):
        self.alerts = json.load(open(alert_file))
        self.alert_interval = alert_interval
        self.alert_statuses = {k: False for k in self.alerts}

    def evaluate_alerts(self, DB):
        triggered_alerts, resolved_alerts = [], []
        human_time = datetime.datetime.fromtimestamp(
            DB.last_timestamp).strftime('%H:%M:%S')
        for alert_name, alert_details in self.alerts.items():
            triggered, alert_val = DB.alert_triggered(**alert_details)

            if not self.alert_statuses[alert_name] and \
                    triggered:
                self.alert_statuses[alert_name] = True
                triggered_alerts.append("{alert_name} generated an alert - {dimension} = {value}, triggered at {time}".format(
                    dimension=alert_details['dimension'],
                    alert_name=alert_name,
                    value=alert_val,
                    time=human_time))

            if self.alert_statuses[alert_name] and \
                    not triggered:
                self.alert_statuses[alert_name] = False
                resolved_alerts.append("{alert_name} alert recovered at {time}".format(
                    alert_name=alert_name,
                    time=human_time))

        return triggered_alerts, resolved_alerts
