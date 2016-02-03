#!/usr/bin/python

import time
import threading
from daemon import runner
import subprocess

class BmcTwitterStart():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/home/pbeavers/foo.pid'
        self.pidfile_timeout = 5

    def run(self):
         while (1):
             subprocess.call("/home/pbeavers/work/evtweet/bin/BmcTwitterAdapter.py")
             print "processes terminated - restarting"

    def handle_exit(self, signum, frame):
        print "Exiting" 

    def __del__(self):
        print "deleting BmcTwitterStart"

#------------------------------------------------------
#
#------------------------------------------------------
app = BmcTwitterStart()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()







