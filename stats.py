#!/usr/bin/env python

import os
import json
import sys
import time
import operator
import datetime

os.chdir(os.path.dirname(os.path.realpath(__file__)))
raw_config=open('data/config.json').read()
config = json.loads(raw_config)

log_pipe = None
if (config['log'] is False):
    print "Logging not enabled in config, cannot generate stats."
    sys.exit(0)

with open(config['log'], 'r') as content_file:
    content = content_file.read()
records = [dict(zip(['time', 'type', 'data'], line.split("\t", 3))) for line in content.lstrip("\n").rstrip("\n").split("\n")]
login_records = filter(lambda x: x['type'] == 'username', records)

date_bins = {}
for record in login_records:
    date_index = int(round(int(record['time']) / (60*60*24))) * (60*60*24)
    if (not date_bins.has_key(date_index)):
        date_bins[date_index] = []
    date_bins[date_index].append(record)

today_bin = int(time.time() / (60*60*24)) * (60*60*24)
logins_today = 0
if date_bins.has_key(today_bin):
    logins_today = len(date_bins[today_bin])

if sys.argv.__contains__('--today'):
    if len(sys.argv) > 2:
        print "Attempts Today: " + str(logins_today)
    else:
        print str(logins_today)

if sys.argv.__contains__('--hist'):
    if len(sys.argv) > 2:
        print "\nAttempts Over Time:"

    graph_height = 8
    padding = 1

    filtered_bins = filter(lambda x: x[0] > (time.time() - (60*60*24*7)), date_bins.iteritems())
    sorted_bins = sorted(filtered_bins, key=operator.itemgetter(0))
    max_val = max([len(bin[1]) for bin in sorted_bins])

    graph_vals = [(graph_height * len(bin[1]) / max_val) for bin in sorted_bins]
    labels = [int(max_val * (float(i+1) / graph_height)) for i in range(0,graph_height)]
    max_len = max([len(str(label)) for label in labels])

    last_label = None
    for i in range(0, graph_height):
        j = graph_height-i
        sys.stdout.write(str(labels[j-1]).rjust(max_len, ' ') + '|      ')
        for val in graph_vals:
            if (val >= j):
                sys.stdout.write('#')
            else:
                sys.stdout.write(' ')
            sys.stdout.write((' ' * padding) + '     ')
        sys.stdout.write("\n")

    print (' ' * max_len) + '+' + ('-' * (padding + 6 + len(graph_vals) * 6))

    sys.stdout.write((' ' * max_len) + (' ' * (padding + 4)))
    for bin in sorted_bins:
        date = datetime.datetime.fromtimestamp(bin[0]).strftime('%m/%d')
        sys.stdout.write(date + (' ' * (padding + 1)))

print ""
sys.exit(0)