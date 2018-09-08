#!/usr/bin/env python

"""
This script is designed to generate a CSV file containing student names and their
corresponding submitted link for an ELMS assignment requiring a link submission.

Usage:
1. In ELMS, go to the "grades" tab
2. Click the arrow under the desired link-submission assignment and hit "download submissions"
3. Extract the downloaded zip file of all student submissions
4. Run ./elink2csv.py <path to extracted directory>
5. CSV file will be generated at <path to extracted directory>/link_submissions.csv
"""


