#! /usr/bin/python3

import asyncio
import sys
import cachetools

REPORTING_TIME = 10
RECENT_REQUESTS = cachetools.TTLCache(10e6, REPORTING_TIME)
RECENT_REQUESTS['total_requests'] = 0


def process_log():
    data = sys.stdin.readline()
    RECENT_REQUESTS[data] = True


@asyncio.coroutine
def report():
    while True:
        yield from asyncio.sleep(REPORTING_TIME)
        print('{} requests in the last {} seconds'.format(
            len(RECENT_REQUESTS), REPORTING_TIME))


def main():
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, process_log)
    loop.run_until_complete(report())


if __name__ == '__main__':
    main()
