###IMPROVEMENTS

Heres a list of ways we can improve functionality of this naive monitoring application.

- Allow for alerts using 'dimension.any'. This would allow us to create alerts that let us check if any user is over a particular threshold.
- Monitor avg bandwidth per interval since this could have cost implications. 
- Allow for serialization of the MetricStorage, so that we could store historical data on disk
- Graphs to better visualize traffic patterns 
- Allow for keyboard input to switch views

Usage:
	```./access_log_generator.py | ./monitor.py ```
