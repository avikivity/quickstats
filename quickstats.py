#!/usr/bin/python3

from datetime import datetime
import re, time, argparse

from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('--threshold', metavar='RATE', type=float, default=0.,
                dest='threshold',
                help='Rate (in MB/s) below which output is supressed')
ap.add_argument('--interval', metavar='INTERVAL', type=float, default=1000.,
                dest='interval',
                help='Sampling interval (in milliseconds)')

args = ap.parse_args()

threshold = args.threshold
interval = args.interval / 1000.

line_re = re.compile(r'\s*(.*):\s*(\d+)(?:\s+\d+){7}\s+(\d+)(?:\s+\d+){7}\s*')

then = None
old_stat = {}
while True:
    now = datetime.utcnow()
    new_stat = {}
    for line in open('/proc/net/dev').readlines()[2:]:
        m = line_re.match(line)
        dev, rx, tx = m.groups()
        new_stat[dev] = (int(rx), int(tx))
    rates = {}
    for key in old_stat.keys() & new_stat.keys():
        new = new_stat[key]
        old = old_stat[key]
        def rate(n):
            return int((new[n] - old[n]) / (now - then).total_seconds())
        rates[key] = (rate(0), rate(1))
    if any([rate[0] >= threshold or rate[1] >= threshold
            for rate in rates.values()]):
        print('{} UTC'.format(now), end='', flush=False)
        for key in rates.keys():
            rx, tx = rates[key]
            print(' {:8} {:10} {:10}'.format(key, rx, tx),
                  end='', flush=False)
        print('', flush=True)
    old_stat = new_stat
    then = now
    time.sleep(interval)
