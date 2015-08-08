#!/usr/bin/env python

# run-cron.py
# sets environment variable crontab fragments and runs cron

from subprocess import call

# read docker environment variables and set them in the appropriate crontab
# fragment
args = ["cron", "-f", "-L 15"]
call(args)
