import time
import ConfigObject
import sys
import tweepy
import json
import pycurl
from multiprocessing import Pool
import threading

cobj = ConfigObject.ConfigObject()
global tweetCounter
tweetCounter = 0

#--------------------------------------------------
# Raise event function to post events to Pulse
#--------------------------------------------------
def raiseEvent(eventText, userName, userPwd):
    print "starting raiseEvent"
    headers = ['Expect:', 'Content-Type: application/json']
    url =  "https://premium-api.boundary.com/v1/events"
    newEvent = {
        "fingerprintFields": [
           "@title"
        ],
        "source": {
           "ref": "myserver",
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
    print ("status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
    c.close()

#---------------------------------------------------
# Aggregate and send total
#---------------------------------------------------
def AggAndSend():
    global tweetCounter
    while True:
        time.sleep(60)
        print "AggAndSend"
        timestamp = time.mktime(time.localtime())
        headers = ['Expect:', 'Content-Type: application/json']
        url =  "https://premium-api.boundary.com/v1/measurements"
       
        newMeasure =   {
        "source": "myserver",
        "metric": "TweetCount",
        "measure": tweetCounter,
        "timestamp": timestamp
        }

        print "starting pycurl"
        c= pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER,headers )
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.USERPWD, cobj.pulseUserPwd)
        data = json.dumps(newMeasure)
        c.setopt(pycurl.POSTFIELDS,data)
        c.perform()
        print ("metric post status code" +  str(c.getinfo(pycurl.HTTP_CODE)))
        c.close()
        tweetCounter = 0

#------------------------------------------------------
#  Create the metric def in pulsed
#------------------------------------------------------
def CreateMetric():

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

   c= pycurl.Curl()
   c.setopt(pycurl.URL, url)
   c.setopt(pycurl.HTTPHEADER,headers )
   c.setopt(pycurl.CUSTOMREQUEST, "POST")
   c.setopt(pycurl.USERPWD, cobj.pulseUserPwd)
   data = json.dumps(newMetric)
   c.setopt(pycurl.POSTFIELDS,data)
   c.perform()
   print ("Metric create status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
   c.close()

#---------------------------------------------------
# Call back for RaiseEvent
#---------------------------------------------------
def cb(r):
   print("callback for raiseEvent")

#---------------------------------------------------
# Create processing pool for raiseEvent
#---------------------------------------------------
if __name__ == '__main__':
  pool = Pool(processes=5)

#---------------------------------------------------
# Listener for tweepy stream
#---------------------------------------------------
class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.user.screen_name)
        print(status.text)

    def on_data(self, data):
        tweet = json.loads(data)

        if tweet.has_key('user'):
             user = tweet['user']['name']
             text = tweet['text']
             pool.apply_async(raiseEvent,(text,user,cobj.pulseUserPwd,), callback=cb)
             global tweetCounter
             tweetCounter = tweetCounter + 1

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

#-------------------------------------------------------
# Main function
#-------------------------------------------------------
CreateMetric()

#-------------------------------------------------------
#  Start the looping thread to post tweet counts
#-------------------------------------------------------
t = threading.Timer(1.0, AggAndSend)
t.start()

#-------------------------------------------------------
# Create and start the twitter stream
#-------------------------------------------------------
auth = tweepy.OAuthHandler(cobj.consumer_key, cobj.consumer_secret)
auth.set_access_token(cobj.access_token_key, cobj.access_token_secret)
sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
filterArray = cobj.filterString.split(",")
sapi.filter(track=filterArray)

