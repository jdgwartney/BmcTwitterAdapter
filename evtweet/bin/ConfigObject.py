#--------------------------------------------------------------
# ConfigObject holds all the options stored in evtweet.conf
#--------------------------------------------------------------

import ConfigParser
import logging
import logging.handlers

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
      Config.read("../conf/BmcTwitterAdapter.conf")
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

   def printConfig(self,mlog):
      mlog.info("datadir=" + self.datadir)
      mlog.info("configdir=" + self.confdir)
      mlog.info("logdir=" + self.logdir)
      mlog.info("filterString=" + self.filterString)
      mlog.info("reportMetrics=" + str(self.reportMetrics))
      mlog.info("raiseEvents=" + str(self.raiseEvents))
      mlog.info("metricInterval=" + str(self.metricInterval))
      mlog.info("Pulse UserPwd=" + self.pulseUserPwd)
      mlog.info("consumer_key=" + self.consumer_key)
      mlog.info("consumer_secreti=" + self.consumer_secret)
      mlog.info("access_token_key=" + self.access_token_key)
      mlog.info("access_token_secret=" + self.access_token_secret)

      topicArray = self.filterString.split(",")
      for topic in topicArray:
          mlog.info(topic + " regularExpression=" + self.regularExpression[topic])

