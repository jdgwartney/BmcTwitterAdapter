

import ConfigParser
Config = ConfigParser.ConfigParser()

Config.read("../conf/evtweet.conf")
options=Config.options("Directories")

dict1 = {}
for option in options:
        try:
            dict1[option] = Config.get("Directories", option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None

        print option
        print dict1[option]






