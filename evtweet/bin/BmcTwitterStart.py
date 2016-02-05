#!/usr/bin/python

#------------------------------------------------------------
# BmcTwitterStart.py - wrapper script to allow the BMC 
# twitter adapter to be run as a daemon
#-------------------------------------------------------------
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
        self.proc = subprocess.Popen(["/home/pbeavers/work/evtweet/bin/BmcTwitterAdapter.py"])
        while True:
            if self.proc.poll() is not None:
                self.proc = subprocess.Popen(["/home/pbeavers/work/evtweet/bin/BmcTwitterAdapter.py"])
            time.sleep(5)

    def handle_exit(self, signum, frame):
        print "Exiting" 

    def __del__(self):
        print "deleting BmcTwitterStart"
        try:
            self.proc.terminate()
        except:
            print "exiting"

#------------------------------------------------------
# main() - create the app object and handle daemon
# command line options.
#------------------------------------------------------
import sys

daemonMode = 0
for arg in sys.argv:
    if arg == "start":
         daemonMode = 1     
    if arg == "stop":
         daemonMode = 1
    if arg == "restart":
         daemonMode = 1

if daemonMode == 1:
    app = BmcTwitterStart()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
else:
    proc = subprocess.Popen(["/home/pbeavers/work/evtweet/bin/BmcTwitterAdapter.py"])
    while True:
        if proc.poll() is not None:
            proc = subprocess.Popen(["/home/pbeavers/work/evtweet/bin/BmcTwitterAdapter.py"])
        time.sleep(5)









