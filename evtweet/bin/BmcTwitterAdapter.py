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
        data = json.dumps(newEvent)
        c.setopt(pycurl.POSTFIELDS,data)
        c.perform()
        c.close()

    #---------------------------------------------------
    # Set Tweet Counters
    #---------------------------------------------------
    def SetTweetCounters(self,tweetText):
       lowerTweetText = tweetText.lower()

       topicArray =  self.cobj.filterString.split(",")
       for topic in topicArray:
           if topic.lower() in lowerTweetText:
               self.tweetCounterArray[topic] = self.tweetCounterArray[topic] + 1
               return topic
       return "NOT" 
    
    #---------------------------------------------------
    # Aggregate and send total
    #---------------------------------------------------
    def AggAndSend(self):
        while self.continueThread > 0:
            time.sleep(self.cobj.metricInterval)
            timestamp = time.mktime(time.localtime())
            headers = ['Expect:', 'Content-Type: application/json']
            url =  "https://premium-api.boundary.com/v1/measurements"
       
            topicArray =  self.cobj.filterString.split(",")
            for topic in topicArray:
                tweetCount = self.tweetCounterArray[topic]
           
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
                data = json.dumps(newMeasure)
                c.setopt(pycurl.POSTFIELDS,data)
                c.perform()
                c.close()
                self.tweetCounter = 0
                self.tweetCounterArray[topic] = 0

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
        data = json.dumps(newMetric)
        c.setopt(pycurl.POSTFIELDS,data)
        c.perform()
        c.close()

    #---------------------------------------------------
    # Call back for RaiseEvent
    #---------------------------------------------------

    def __init__(self):
        self.pool = ThreadPool(20)
        self.CreateMetric()

        
        if self.cobj.reportMetrics == True:
            self.pool.add_task(self.AggAndSend)

    #def on_status(self, status):

    def on_data(self, data):
        tweet = json.loads(data)
        if tweet.has_key('user'):
             user = tweet['user']['name']
             text = tweet['text']
             self.tweetCounter = self.tweetCounter + 1
             topic = self.SetTweetCounters(text)
             if topic != "NOT":
                 # pool.apply_async(self.raiseEvent,args=(text,user,self.cobj.pulseUserPwd,), callback=cb)
                 # self.raiseEvent(text,user,self.cobj.pulseUserPwd)
                 if self.cobj.raiseEvents == True:
                     self.pool.add_task(self.raiseEvent,text,user,self.cobj.pulseUserPwd,topic)

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

    def __del__(self):
        self.continueThread = 0
        time.sleep(4)
        print "killing thread"
        self.pool.wait_completion()

class BmcTwitterAdapter():
    cobj = ConfigObject.ConfigObject()

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/home/pbeavers/foo.pid'
        self.pidfile_timeout = 5

    def run(self):
        auth = tweepy.OAuthHandler(self.cobj.consumer_key, self.cobj.consumer_secret)
        auth.set_access_token(self.cobj.access_token_key, self.cobj.access_token_secret)
        self.sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
        filterArray = self.cobj.filterString.split(",")
        self.sapi.filter(track=filterArray)

    def handle_exit(self, signum, frame):
        print "exiting..."

    def manual_run(self):
        auth = tweepy.OAuthHandler(self.cobj.consumer_key, self.cobj.consumer_secret)
        auth.set_access_token(self.cobj.access_token_key, self.cobj.access_token_secret)
        self.sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
        filterArray = self.cobj.filterString.split(",")
        self.sapi.filter(track=filterArray)

    def __del__(self):
        print "deleting BmcTwitterAdapter"






