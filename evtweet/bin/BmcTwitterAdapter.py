import time
import ConfigObject
import sys
import tweepy
import json
import pycurl
from multiprocessing import Pool
from threading import Thread
from Queue import Queue
import threading
import re
import logging
import logging.handlers

#---------------------------------------------------
# Thread class for processing
#---------------------------------------------------
class Worker(Thread):
        """Thread executing tasks from a given tasks queue"""
        def __init__(self, tasks):
            Thread.__init__(self)
            self.tasks = tasks
            self.daemon = True
            self.start()

        def run(self):
            while True:
                func, args, kargs = self.tasks.get()
                try:
                    func(*args, **kargs)
                except Exception, e:
                    print e
                finally:
                    self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


#---------------------------------------------------
# Listener for tweepy stream
#---------------------------------------------------
class CustomStreamListener(tweepy.StreamListener):
    
    cobj = ConfigObject.ConfigObject()
    continueThread = 1
    tweetCounter = 0
    tweetCounterArray = {}

    topicArray =  cobj.filterString.split(",")
    for topic in topicArray:
        tweetCounterArray[topic] = 0 

    t = 0

    #--------------------------------------------------
    # Raise event function to post events to Pulse
    #--------------------------------------------------
    def raiseEvent(self, eventText, userName, userPwd, topic):

        headers = ['Expect:', 'Content-Type: application/json']
        url =  "https://premium-api.boundary.com/v1/events"
        newEvent = {
            "fingerprintFields": [
               "@title"
            ],
            "source": {
            "ref": topic,
            "type": "host",
            },
            "title": userName + ":" + eventText
        }

        c= pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER,headers )
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.USERPWD, userPwd)
        c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
        data = json.dumps(newEvent)
        c.setopt(pycurl.POSTFIELDS,data)
        c.perform()
        c.close()

    #---------------------------------------------------
    # Set Tweet Counters
    #---------------------------------------------------
    def SetTweetCounters(self,tweetText):
       foundKeywords = False
       foundTopic = False

       lowerTweetText = tweetText.lower()

       returnString = "NOT"
       topicArray =  self.cobj.filterString.split(",")
       for topic in topicArray:
           if topic.lower() in lowerTweetText:
               foundTopic = True
               returnString = topic 
               break

       if foundTopic == True:
           regularExpression=self.cobj.regularExpression[returnString]
           if regularExpression != "NOT":
               searchResults = re.search(regularExpression, lowerTweetText)
               if searchResults:
                    foundKeywords = True
               else:
                    foundKeywords = False
           else:
               foundKeywords = True         

       if foundTopic == True and foundKeywords == True:
           self.tweetCounterArray[returnString] = self.tweetCounterArray[returnString] + 1
       else:
           returnString = "NOT"
       
       return returnString 


    #---------------------------------------------------
    #  Post metrics to TrueSight Intelligence 
    #---------------------------------------------------
    def PostMetricsTsi(self, timestamp, newTweetCounterArray):
        self.mlog.debug("Calling PostMetricsTsi")  
        #-------------------------------------------------------
        # Specify the header 
        #-------------------------------------------------------

        apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcGlLZXkuVElNRVNUQU1QIjoxNDQ1MzA4MDQ0ODI5LCJBcGlLZXkuQUNDT1VOVF9JRCI6IjU4ZTlhMjU4LWE1MTctNGQxOC1iYTgzLWQ4YmEzYWU4OTdjOCIsIkFwaUtleS5URU5BTlRfSUQiOiJlZDJmZGE5NC03NDZiLTQ4ZmMtYTUzNC03MDQzYTQ0YzhkMTgiLCJBcGlLZXkuVEVOQU5UX0NSRUFURURfVElNRSI6MTQ0NTMwODA0Mzc4MH0=.Gw0KG68a5FZzs4uxjxeMfIK98G2rYtoEAaxDnYq5aGU="


        # print "Api Key=" + self.cobj.tsiApiKey
        headers = ['Expect:', 'Content-Type: application/json' ,  'X-API-KEY: ' + apiKey]
        url = "https://truesight.bmc.com/api/v1/metrics?async=false"

        topicArray =  self.cobj.filterString.split(",")
        for topic in topicArray:
            tweetCount = newTweetCounterArray[topic]

            #--------------------------------------------------
            #  Create data structure for metrics posting
            #--------------------------------------------------
            myMetrics = [
            {
                "entity_type_id": "TWEET_TOPIC",
                "entity_id": "tweet_server." + topic,
                "time_series": [
                {
                    "metric_id": "number_of_tweets",
                    "values": [
                    { "v": tweetCount, "t": timestamp }
                    ]
                }
                ]
            }
            ]

            #-------------------------------------------------------
            # Issue the request
            #-------------------------------------------------------

            c= pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER,headers )
            c.setopt(pycurl.CUSTOMREQUEST, "POST")
            data = json.dumps(myMetrics)
            c.setopt(pycurl.POSTFIELDS,data)

            try:
               c.perform()
            except Exception, e:
               self.mlog.warning(e)
            
            c.close()

        self.mlog.debug("PostMetricsTsi complete")  




    #---------------------------------------------------
    #  Post metrics to TrueSight Pulse
    #---------------------------------------------------
    def PostMetrics(self, timestamp, newTweetCounterArray):
        self.mlog.debug("Calling PostMetrics")  
        headers = ['Expect:', 'Content-Type: application/json']
        url =  "https://premium-api.boundary.com/v1/measurements"

        topicArray =  self.cobj.filterString.split(",")
        for topic in topicArray:
            tweetCount = newTweetCounterArray[topic]

            newMeasure =   {
            "source": topic,
            "metric": "TweetCount",
            "measure":  tweetCount,
            "timestamp": timestamp
            }

            c= pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER,headers )
            c.setopt(pycurl.CUSTOMREQUEST, "POST")
            c.setopt(pycurl.USERPWD, self.cobj.pulseUserPwd)
            c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
            data = json.dumps(newMeasure)
            c.setopt(pycurl.POSTFIELDS,data)
            try:
               c.perform()
            except Exception, e:
               self.mlog.warning(e)
            c.close()

        self.mlog.debug("PostMetrics complete")  

    #---------------------------------------------------
    # Aggregate and send total
    #---------------------------------------------------
    def AggAndSend(self):
        while self.continueThread > 0:
            time.sleep(self.cobj.metricInterval)
            timestamp = time.mktime(time.localtime())
            
            newTweetCounterArray = {}
            topicArray =  self.cobj.filterString.split(",")

            # Add a lock here
            for topic in topicArray:
                newTweetCounterArray[topic] = self.tweetCounterArray[topic]
                self.tweetCounterArray[topic] = 0   # potential thread safety issue
               
            self.pool.add_task(self.PostMetrics,timestamp, newTweetCounterArray)
            self.pool.add_task(self.PostMetricsTsi,timestamp, newTweetCounterArray)
            # Release the lock here

    #------------------------------------------------------
    #  Create the metric def in pulsed
    #------------------------------------------------------
    def CreateMetric(self):

        headers = ['Expect:', 'Content-Type: application/json']
        url =  "https://premium-api.boundary.com/v1/metrics"
        newMetric = {
        "name": "TweetCount",
        "description": "Tweet Count",
        "displayName": "Tweet Count",
        "displayNameShort": "Tweets",
        "unit": "number",
        "defaultAggregate": "sum"
        }

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER,headers )
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.USERPWD, self.cobj.pulseUserPwd)
        c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
        data = json.dumps(newMetric)
        c.setopt(pycurl.POSTFIELDS,data)
        c.perform()
        c.close()

    #---------------------------------------------------
    # Call back for RaiseEvent
    #---------------------------------------------------

    def __init__(self):

        self.pool = ThreadPool(20)
        self.mlog = logging.getLogger("MyLogger")

        LOG_FILENAME = self.cobj.logdir + "/BmcTwitterAdapter.log"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.mlog = logging.getLogger('MyLogger')
        self.mlog.setLevel(logging.WARNING)
        self.handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=100000000, backupCount=5)
        self.handler.setFormatter(formatter)
        self.mlog.debug("__init__() for CustomStreamListener.")
        
        #-------------------------------------------------------------------
        # Make a call to Pulse to ensure the metric definition is in place.
        # This is done on initialization only.
        #-------------------------------------------------------------------
        self.CreateMetric()
       
        #------------------------------------------------------------------------
        # Start the thread process to calculae and send metrics.  This is 
        # done with a timer.  The metrics are totalled in the instance variable 
        # tweetCounter array.  The AggAndSend metric simply reads this array
        # on an interval and sends the metrics to BMC TrueSight Pulse
        #------------------------------------------------------------------------
        if self.cobj.reportMetrics == True:
            self.pool.add_task(self.AggAndSend)

    #--------------------------------------------------------------------------
    # Our main processing object is a sublass of Tweepy's stream listener
    # we do not have a need for the on_status method so it is commented out
    #--------------------------------------------------------------------------

    def on_status(self, status):
        self.mlog.debug("Received on_status callback")

    #--------------------------------------------------------------------------
    # Our main processing object is a sublass of Tweepy's stream listener
    # The on_data method is invokded when a tweet satisfying the given filter
    # is received.
    #--------------------------------------------------------------------------
    def on_data(self, data):
        self.mlog.debug("Received on_data callback")
        tweet = json.loads(data)
        if tweet.has_key('user'):
             user = tweet['user']['name']
             text = tweet['text']
             self.tweetCounter = self.tweetCounter + 1

             # add a lock here

             #------------------------------------------------------------------
             # Our set tweet counters method does two things.  1) it applies 
             # a regular expression to the tweet text to see if this tweet
             # counts. 2) it increments the required counter and 3) it tells
             # us whether or not we need to post the tweet intself as an
             # event.
             #------------------------------------------------------------------

             topic = self.SetTweetCounters(text)
             if topic != "NOT":
                 if self.cobj.raiseEvents == True:
                     #------------------------------------------------------------
                     # Add the tweet to the thread pool to be raised as an event
                     #------------------------------------------------------------
                     self.pool.add_task(self.raiseEvent,text,user,self.cobj.pulseUserPwd,topic)

             # release the lock here

    def on_error(self, status_code):
        self.mlog.warning("Received on_error call back")
        self.mlog.warning("on_error() encountered error with status code: " + str(status_code))
        return True # Don't kill the stream

    def on_timeout(self):
        self.mlog.warning("Receidved on_timeout callback")
        self.mlog.warning("on_timeout() timeout triggered.  Not killing stream.")
        return True # Don't kill the stream

    def __del__(self):
        self.continueThread = 0
        time.sleep(4)
        self.mlog.info("killing thread")
        self.pool.wait_completion()

class BmcTwitterAdapter():
    cobj = ConfigObject.ConfigObject()

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/home/pbeavers/foo.pid'
        self.pidfile_timeout = 5

        LOG_FILENAME = self.cobj.logdir + "/BmcTwitterAdapter.log"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.mlog = logging.getLogger('MyLogger')
        self.mlog.setLevel(logging.DEBUG)
        self.handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=100000000, backupCount=5)
        self.handler.setFormatter(formatter)
        self.mlog.addHandler(self.handler)


    def run(self):
        auth = tweepy.OAuthHandler(self.cobj.consumer_key, self.cobj.consumer_secret)
        auth.set_access_token(self.cobj.access_token_key, self.cobj.access_token_secret)
        self.sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
        filterArray = self.cobj.filterString.split(",")
        self.sapi.filter(track=filterArray)

    def handle_exit(self, signum, frame):
        print "Exiting" 

    def manual_run(self):
        auth = tweepy.OAuthHandler(self.cobj.consumer_key, self.cobj.consumer_secret)
        auth.set_access_token(self.cobj.access_token_key, self.cobj.access_token_secret)
        self.sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
        self.sapi.mlog = self.mlog
        filterArray = self.cobj.filterString.split(",")
        self.sapi.filter(track=filterArray)

    def __del__(self):
        print "deleting BmcTwitterAdapter"






