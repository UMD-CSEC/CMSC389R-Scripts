#!/usr/bin/env python2

import argparse
from datetime import datetime
import os
from pygit2 import clone_repository, Repository, GitError
from pygit2 import GIT_MERGE_ANALYSIS_UP_TO_DATE, GIT_MERGE_ANALYSIS_FASTFORWARD, GIT_MERGE_ANALYSIS_NORMAL, GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
import subprocess
import sys
import time

'''
This CLI script was created to automatically collect CMSC389R homework 
submitted on GitHub and track late submissions for easy grading.

Usage: ./githandlery.py

First time usage of this script requires that you use the "-c" command 
line option and supply a CSV file consisting of two columns, 
Student Name and GitHub Fork Link. A working CSV can be generated 
with elink2csv.py.

After the initial running of this script, and all repos are cloned, 
use the "-p" option along with a specific homework folder name and
the due date of that homework. This will pull all updates to every
student's repository and produce a late_submissions.txt file that 
contains late submission information for the provided HW assignment.
'''

GIT_REPO_SLUG = "/389Rspring19.git"
DUE_TIME = "-23:59"

# clones student repositories from -c arg, meant for initial usage of this script
def clone(csvfile):
    # loads student names from .csv and clones repos. Assumes CSV was generated by elink2csv.py
    with open(csvfile, "r") as f:
        for line in f.readlines():
            data = line.split(",")
            s_name = data[0]
            s_git = data[1].strip()

            # make directory for student's repo
            if not os.path.isdir(s_name):
                os.mkdir(s_name)
        
            # clone repo into student's directory if its empty
            if len(os.listdir("%s/%s" % (os.getcwd(), s_name))) == 0:
                try:
                    clone_repository(s_git, s_name)
                    print("...cloned repository for %s" % (s_name))
                except GitError:
                    # assume if there's an error they only put in their profile link
                    clone_repository(s_git + GIT_REPO_SLUG, s_name)
                    print("...cloned repository for %s" % (s_name))
        f.close()

# effectively mimics "git pull" command ("git pull" is a combination of several git functions on top of "git fetch")
def do_pull(name, repo, remote_name="origin"):
    for remote in repo.remotes:
        if remote.name == remote_name:
            remote.fetch()
            remote_master_id = repo.lookup_reference("refs/remotes/origin/master").target
            merge_result,_ = repo.merge_analysis(remote_master_id)
            
            # It's up to date, don't do anything
            if merge_result & GIT_MERGE_ANALYSIS_UP_TO_DATE:
                print("Repository for %s already up to date." % (name))
                return
            
            # Fastforward
            elif merge_result & GIT_MERGE_ANALYSIS_FASTFORWARD:
                repo.checkout_tree(repo.get(remote_master_id))
                master_ref = repo.lookup_reference("refs/heads/master")
                master_ref.set_target(remote_master_id)
                repo.head.set_target(remote_master_id)
                print("Repository for %s has been updated from remote." % (name))
            elif merge_result & GIT_MERGE_ANALYSIS_NORMAL:
                print("Pulling remote changes for %s led to a conflict. Check this repo manually." % name)
            else:
                print("Unexpected fetch/merge result when pulling repository for %s: %s" % (name, GIT_MERGE_ANALYSIS_NORMAL))

# updates all student repos and and checks for late submissions of the assignment specified in the command
# assumes you've already run this script with the -c arg
def pull_and_check(hw_name, due_date, late_submissions):
    # go into every repository and pull changes
    dirlist = os.listdir(os.getcwd())
    for name in dirlist:
        if not os.path.isdir(name):
            continue
        
        # get repo object
        repo = Repository("%s/.git" % (name))

        # pull changes
        do_pull(name, repo)

        # find most recent commit where the supplied hw_name was edited
        commits = repo.walk(repo.head.target, GIT_SORT_TIME)
        for commit in commits:
            try:
                diff = repo.diff(commit.parents[0], commit)
                if diff.patch != None and ("/assignments/%s/writeup/README.md" % (hw_name)) in diff.patch:
                    # add due time (11:59 PM) to due date
                    submit_time = commit.commit_time #datetime.utcfromtimestamp(commit.commit_time).strftime('%Y-%m-%d %H:%M:%S')
                    due_time = time.mktime(datetime.strptime(due_date + DUE_TIME, "%Y-%m-%d-%H:%M").timetuple())

                    # check for late submission
                    submit_difference = due_time - submit_time
                    if submit_difference < 0:
                        late_submissions[name] = (submit_difference / 60 / 60)
            except IndexError:
                # repo.diff() throws an IndexError when attempting to obtain a "diff" on the initial commit
                pass

# generates a late_submissions.txt file
def create_latefile(late_submissions, hw_name):
    # rename any old late_submissions.txt file
    if "late_submissions.txt" in os.listdir(os.getcwd()):
        os.system("mv late_submissions.txt late_submissions.txt.old")
        print("Renamed previous late_submissions.txt to late_submissions.txt.old")

    if len(late_submissions) == 0:
        print("No late submissions were found for %s." % (hw_name))
        return
    
    # save late submission info for requested assignment
    late_lst = []
    for name in late_submissions:
        if late_submissions[name] <= 24:
            late_lst.append("%s\t%s\n" % (name, "1 day late"))
        elif late_submissions[name] <= 48:
            late_lst.append("%s\t%s\n" % (name, "2 days late"))
        elif late_submissions[name] <= 72:
            late_lst.append("%s\t%s\n" % (name, "3 days late"))
        else:
            late_lst.append("%s\t%s\n" % (name, "later than 3 days"))
    
    f = open("late_submissions.txt", "w")
    late_lst.sort()
    for line in late_lst:
        f.write(line)
    
    print("Successfully compiled and saved late_submissions.txt with late submission information for %s." % (hw_name))
    f.close()

# handle CLI generation
def cli():
    parser = argparse.ArgumentParser(prog="GitHandler", description="CLI for automating CMSC389R git submission retrieval.")

    parser.add_argument('-c', metavar="CSV", help="Clones student repos from given CSV file.")
    parser.add_argument('-p', nargs=2, metavar=("HWNAME", "YYYY-MM-DD"), help='Pulls all student repos with focus on the given assignment and due date.')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

# entry
if __name__ == "__main__":
    args = cli()
    late_submissions = {}

    if args.c is not None:
        clone(args.c)

    if args.p is not None:
        pull_and_check(args.p[0], args.p[1], late_submissions)
        create_latefile(late_submissions, args.p[0])