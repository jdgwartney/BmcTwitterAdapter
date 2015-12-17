#--------------------------------------------------------------
# ConfigObject holds all the options stored in evtweet.conf
#--------------------------------------------------------------

import ConfigParser

class ConfigObject:
   datadir = ""
   confdir = ""
   logdir = ""

   def __init__(self):
      Config = ConfigParser.ConfigParser()
      Config.read("../conf/evtweet.conf")
      self.confdir = Config.get("Directories", "ConfDirectory" )
      self.datadir = Config.get("Directories", "DataDirectory" )
      self.logdir = Config.get("Directories", "LogDirectory" )

