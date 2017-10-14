#! /usr/bin/python3

"""
    The purpose of this program is to generate
    what looks like access logs from a specific
    website in the Common Log Format.
    https://en.wikipedia.org/wiki/Common_Log_Format
"""

import random
import string
import requests
import shlex
import subprocess
import datetime
import json
import time
import sys

NUMBER_OF_USERS = 20
NUMBER_OF_IPS = 20
NUMBER_OF_AGENTS = 20
MAX_DELAY = 400


def get_ips(number):
    """
        This function uses nmap to pick random
        IPs for our logs given the number to generate
    """
    CMD = "nmap -n -iR {} -sL".format(number)
    for line in subprocess.check_output(shlex.split(CMD)).decode('utf-8').split('\n'):
        if 'report' in line:
            yield line.split(' ')[-1]


def get_users(number):
    """
        This function uses the endpoint of the
        website listofrandomnames.com to generate
        a specific number of usernames for our logs
    """
    url = 'http://listofrandomnames.com/index.cfm?generated'
    data = {'action': 'main.generate',
            'numberof': number,
            'nameType': 'na',
            'fnameonly': 1,
            'allit': 0}

    r = requests.post(url, data=data)
    for line in r.text.split('\n'):
        if 'firstname' in line:
            start = line.find('>')
            name = line[start + 1:line.find('<', start)]
            yield name


def get_timestamp():
    est = datetime.timezone(datetime.timedelta(hours=-5))
    now = datetime.datetime.now(tz=est)
    return '[{}]'.format(now.strftime('%d/%b/%Y:%H:%M:%S %z'))


def generate_log():
    site = random.choice(list(ROUTES.keys()))
    section = random.choice(list(ROUTES[site].keys()))
    size = ROUTES[site][section]
    return '\t'.join([
        random.choice(IPS),
        '-',
        random.choice(USERS),
        get_timestamp(),
        'GET',
        '/' + '/'.join([site, section]),
        random.choice(RESPONSES),
        str(size)])


if __name__ == '__main__':
    global USERS, IPS, METHODS, ROUTES, RESPONSES
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--number-of-ips',default=NUMBER_OF_IPS,help='The number of IPs to cycle through in the logs')
    parser.add_argument('--number-of-users',default=NUMBER_OF_USERS,help='The number of User IDs to cycle through in the logs')
    args = parser.parse_args()

    USERS = [x.lower() for x in get_users(args.number_of_users)]
    IPS = list(get_ips(args.number_of_ips))
    METHODS = ['GET']
    ROUTES = json.load(open('site.json'))
    RESPONSES = ['200'] * 10 + ['500', '408']

    while True:
        time.sleep(random.choice(range(0, MAX_DELAY)) / 1000.)
        print(generate_log())
        sys.stdout.flush()
