#!/usr/bin/env python

import sys
import os
import csv

"""
This script is designed to generate a CSV file containing student names and their
corresponding submitted link for an ELMS assignment requiring a link submission.

Usage:
1. In ELMS, go to the "grades" tab
2. Click the arrow under the desired link-submission assignment and hit "download submissions"
3. Extract the downloaded zip file of all student submissions
4. Run ./elink2csv.py <path to extracted directory> <ELMS assignment title>
5. CSV file will be generated at <path to extracted directory>/link_submissions.csv
"""

if len(sys.argv) < 3:
    print('Incorrect usage. Try ./elink2csv.py <directory path> <ELMS assignment title>')
    sys.exit(0)

directory = sys.argv[1]
title = '<title>'
for i in range(2, len(sys.argv)):
    title += sys.argv[i].lower() + ' '
    if i == len(sys.argv) - 1:
        title = title[:-1] + ':'

if os.path.isdir(directory) == False:
    print('The supplied directory does not exist. Please use an existing directory.')
    sys.exit(0)

os.chdir(directory)
files = os.listdir(directory)

with open('link_submissions.csv', 'wb') as csvf:
    for fname in files:
        if fname[-9:] == 'link.html':
            f = open(fname)
            if title not in f.read().lower():
                print('The supplied ELMS assignment title is not accurate. Please try again.')
                sys.exit(0)
            f.seek(0)
            row = [None]*2
            for line in f:
                if title in line.lower():
                    student = line[line.find(': ')+2:-9]
                    row[0] = student
                if 'Click Here to go to the submission' in line:
                    row[1] = line[9:-41]
            writer = csv.writer(csvf)
            writer.writerow(row)
            f.close()
csvf.close()
