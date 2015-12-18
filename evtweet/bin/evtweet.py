import tweepy
import ConfigObject
import sys
import tweepy
import json
import pycurl
from multiprocessing import Pool

cobj = ConfigObject.ConfigObject()

#--------------------------------------------------
# Raise event function to post events to Pulse
#--------------------------------------------------
def raiseEvent(eventText, userName, userPwd):
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
# Call back for RaiseEvent
#---------------------------------------------------
def cb(r):
   print "callback for raiseEvent"

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
        print status.user.screen_name
        print status.text

    def on_data(self, data):
        tweet = json.loads(data)

        if tweet.has_key('user'):
             user = tweet['user']['name']
             text = tweet['text']
             # callPulse(text, user, cobj.pulseUserPwd)
             pool.apply_async(raiseEvent,(text,user,cobj.pulseUserPwd,), callback=cb)

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

#-------------------------------------------------------
# Main function
#-------------------------------------------------------
auth = tweepy.OAuthHandler(cobj.consumer_key, cobj.consumer_secret)
auth.set_access_token(cobj.access_token_key, cobj.access_token_secret)
# api = tweepy.API(auth)
sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
filterArray = cobj.filterString.split(",")
sapi.filter(track=filterArray)

