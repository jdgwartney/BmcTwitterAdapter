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

      tempString = Config.get("FilterConfig", "reportMetrics")
      if tempString == "Yes":
          self.reportMetrics = True 

      tempString = Config.get("FilterConfig", "raiseEvents")
      if tempString == "Yes":
          self.raiseEvents = True

      tempString = Config.get("FilterConfig", "MetricInterval")
      self.metricInterval = int(tempString)

      self.pulseUserPwd = Config.get("PulseConfig", "UserPwd" )

