#---------------------------------------------------------------------------------------------
#  Create an application called "Online Auction" with id "online_auc" 
#  
#  Create a device to represent the app server called "OA-AppServer-1" with id "oa-appserver-1" 
#
#  Create a type of entity to represent transactions on an app server called "Transaction" with
#  type id of "TRANSACTION" with two metrics "request_response_time" and "number_of_requests"
#
#  Create two transactions to represent activity on the appserver
#  "Bid Transaction" with id oa-appserver-1.bid-tx
#  "Browse Catalog" with id oa-appserver-1.browse_catalog
#
#  Make the metrcs number_of_requests and request_response time KPI's for the application.
#---------------------------------------------------------------------------------------------

import json
import pycurl

#-------------------------------------------------------
# Specify api key
#-------------------------------------------------------

apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJBcGlLZXkuVElNRVNUQU1QIjoxNDQ1MzA4MDQ0ODI5LCJBcGlLZXkuQUNDT1VOVF9JRCI6IjU4ZTlhMjU4LWE1MTctNGQxOC1iYTgzLWQ4YmEzYWU4OTdjOCIsIkFwaUtleS5URU5BTlRfSUQiOiJlZDJmZGE5NC03NDZiLTQ4ZmMtYTUzNC03MDQzYTQ0YzhkMTgiLCJBcGlLZXkuVEVOQU5UX0NSRUFURURfVElNRSI6MTQ0NTMwODA0Mzc4MH0=.Gw0KG68a5FZzs4uxjxeMfIK98G2rYtoEAaxDnYq5aGU="

#-------------------------------------------------------
# Set up headers
#-------------------------------------------------------
headers = ['Expect:', 'Content-Type: application/json' ,  'X-API-KEY: ' + apikey]

#---------------------------------------------------------------------------------------------
#  Create the application
#---------------------------------------------------------------------------------------------

strTopics = "bmc,servicenow,zenoss,appdynamics,splunkr,apple,microsoft,trump,clinton"
topicArray = strTopics.split(",")


newEntity =  {
        "entity_type_id": "APPLICATION",
        "name": "Twitter Counters",
        "tags": [
            "app_id:twitter_ctr"
        ],
        "cfg_attr_values": {},
        "entity_id": "twitter_ctr",
        "source_id": "sample",
        "cfg_attr_values":
           {
               "kpis":[
                {"entity_type_id":"TWEET_TOPIC",
                  "entity_type_name":"Tweet Topic",
                  "entity_id":"tweet_server.trump" ,
                  "title":"Number of tweets - trump" ,
                  "application_id":"twitter_ctr",
                  "application_name":"Tweet Counters",
                  "metric_name":"Number of Tweets",
                  "metric_uom":"#",
                  "metric_id":"number_of_tweets"},
                  {"entity_type_id":"TWEET_TOPIC",
                  "entity_type_name":"Tweet Topic",
                  "entity_id":"tweet_server.clinton",
                  "title":"Number of tweets - clinton " ,
                  "application_id":"twitter_ctr",
                  "application_name":"Tweet Counters",
                  "metric_name":"Number of Tweets",
                  "metric_uom":"#",
                  "metric_id":"number_of_tweets"}
                  ]
           }
    }

#-------------------------------------------------------
# Specify the uri
#-------------------------------------------------------

url = "https://truesight.bmc.com/api/v1/entities"

#-------------------------------------------------------
# Issue the request
#-------------------------------------------------------

c= pycurl.Curl()
c.setopt(pycurl.URL, url)
c.setopt(pycurl.HTTPHEADER,headers )
c.setopt(pycurl.CUSTOMREQUEST, "POST")
data = json.dumps(newEntity)
c.setopt(pycurl.POSTFIELDS,data)
c.perform()
print ("status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
c.close()

#-------------------------------------------------------
#  Create a device
#-------------------------------------------------------

newEntity =  {
        "entity_type_id": "DEVICE",
        "name": "tweet_server",
        "tags": [
            "app_id:twitter_ctr"
        ],
        "cfg_attr_values": {},
        "entity_id": "tweet_server",
        "source_id": "sample",
    }


#-------------------------------------------------------
# Issue the request
#-------------------------------------------------------

c= pycurl.Curl()
c.setopt(pycurl.URL, url)
c.setopt(pycurl.HTTPHEADER,headers )
c.setopt(pycurl.CUSTOMREQUEST, "POST")
data = json.dumps(newEntity)
c.setopt(pycurl.POSTFIELDS,data)
c.perform()
print ("status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
c.close()

#-------------------------------------------------------
#  Create a monitored instance
#-------------------------------------------------------


strTopics = "bmc,servicenow,zenoss,appdynamics,splunkr,apple,microsoft,trump,clinton"
topicArray = strTopics.split(",")


for topic in topicArray:
    newEntity =  {
        "entity_type_id": "TWEET_TOPIC",
        "name": topic,
        "tags": [
            "app_id:twitter_ctr"
        ],
        "cfg_attr_values": {},
        "entity_id": "tweet_server." + topic,
        "source_id": "sample",
        "parent_entity_type_id":"DEVICE",
        "parent_entity_id":"tweet_server"
      }


    #-------------------------------------------------------
    # Issue the request
    #-------------------------------------------------------

    c= pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER,headers )
    c.setopt(pycurl.CUSTOMREQUEST, "POST")
    data = json.dumps(newEntity)
    c.setopt(pycurl.POSTFIELDS,data)
    c.perform()
    print ("status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
    c.close()

#-------------------------------------------------------
# Create app level metrics
#-------------------------------------------------------

myMetaData = {
    "id": "TWEET_TOPIC",
    "name": "TWEET_TOPIC",
    "metrics": [
       {
            "id": "number_of_tweets",
            "name": "Number of Tweets",
            "data_type": "number",
            "uom": "#",
            "kpi": "True",
            "key": "True",
       }
    ]
}

url = "https://truesight.bmc.com/api/v1/meta"

#-------------------------------------------------------
# Issue the request
#-------------------------------------------------------

c= pycurl.Curl()
c.setopt(pycurl.URL, url)
c.setopt(pycurl.HTTPHEADER,headers )
c.setopt(pycurl.CUSTOMREQUEST, "POST")
data = json.dumps(myMetaData)
c.setopt(pycurl.POSTFIELDS,data)
c.perform()
print ("status code:=" +  str(c.getinfo(pycurl.HTTP_CODE)))
c.close()


