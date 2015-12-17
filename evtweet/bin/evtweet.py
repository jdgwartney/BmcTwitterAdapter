import tweepy
import ConfigObject

cobj = ConfigObject.ConfigObject()

print cobj.confdir

### code to save tweets in json###
import sys
import tweepy
import json

auth = tweepy.OAuthHandler(cobj.consumer_key, cobj.consumer_secret)
auth.set_access_token(cobj.access_token_key, cobj.access_token_secret)
api = tweepy.API(auth)
file = open('today.txt', 'a')

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print status.text

    def on_data(self, data):
        print json.dumps(data)
        json_data = json.loads(data)
        # file.write(str(json_data))

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(track=['Trump'])

