#--------------------------------------------------------------
# ConfigObject holds all the options stored in evtweet.conf
#--------------------------------------------------------------

import ConfigParser

class ConfigObject:
   datadir = ""
   confdir = ""
   logdir = ""
   consumer_key = ""
   consumer_secret = ""
   access_token_key = ""
   access_token_secret = ""
   filterString = ""
   pulseUserPwd = ""
   reportMetrics = False
   raiseEvents = False
   metricInterval = 60 
   regularExpression = {}

   def __init__(self):
      Config = ConfigParser.ConfigParser()
      Config.read("../conf/evtweet.conf")
      self.confdir = Config.get("Directories", "ConfDirectory" )
      self.datadir = Config.get("Directories", "DataDirectory" )
      self.logdir = Config.get("Directories", "LogDirectory" )

      self.consumer_key = Config.get("TwitterAuthentication", "consumer_key" )
      self.consumer_secret = Config.get("TwitterAuthentication", "consumer_secret" )
      self.access_token_key = Config.get("TwitterAuthentication", "access_token_key" )
      self.access_token_secret = Config.get("TwitterAuthentication", "access_token_secret" )

      self.filterString = Config.get("FilterConfig", "filterString" )
      topicArray = self.filterString.split(",")
      for topic in topicArray:
          try:
              self.regularExpression[topic] = Config.get(topic, "regularExpression")
          except:
              self.regularExpression[topic] = "NOT"

      tempString = Config.get("FilterConfig", "reportMetrics")
      if tempString == "Yes":
          self.reportMetrics = True 

      tempString = Config.get("FilterConfig", "raiseEvents")
      if tempString == "Yes":
          self.raiseEvents = True

      tempString = Config.get("FilterConfig", "MetricInterval")
      self.metricInterval = int(tempString)

      self.pulseUserPwd = Config.get("PulseConfig", "UserPwd" )

   def printConfig(self):
      print "datadir=" + self.datadir
      print "configdir=" + self.confdir
      print "logdir=" + self.logdir
      print "filterString=" + self.filterString
      print "reportMetrics=" + str(self.reportMetrics)
      print "raiseEvents=" + str(self.raiseEvents)
      print "metricInterval=" + str(self.metricInterval)
      print "Pulse UserPwd=" + self.pulseUserPwd
      print "consumer_key=" + self.consumer_key
      print "consumer_secreti=" + self.consumer_secret
      print "access_token_key=" + self.access_token_key
      print "access_token_secret=" + self.access_token_secret

      topicArray = self.filterString.split(",")
      for topic in topicArray:
          print topic + " regularExpression=" + self.regularExpression[topic]

