#!/usr/bin/env python

import os
import xively
import subprocess
import time
import datetime
import requests

FEED_ID = "1347438342"
API_KEY = "hsvCyBwg6hgQwpGyUYzsz1yqD3CAt0rx8ID8eDcdVssqpvTd"
UPDATETIME = 60

# initialize api client
api = xively.XivelyAPIClient(API_KEY)
lastValue = 0


# function to read the temperature from ds18b20 temperature sensor on i2c
def read_temperature():
   tempfile = open("/sys/bus/w1/devices/28-03164598f0ff/w1_slave")
   thetext = tempfile.read()
   tempfile.close()
   tempdata = thetext.split("\n")[1].split(" ")[9]
   temperature = float(tempdata[2:])
   temperature = (temperature * 1.8) + 32000
   temperature = temperature / 1000
   temperature = "{0:.2f}".format(temperature)
   crcResult = thetext.split("\n")[0].split(" ")[11]
   return temperature, crcResult

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("Water_Temperature")
    return datastream
  except:
    datastream = feed.datastreams.create("Water_Temperature", tags="temperature")
    return datastream



def start():
   print "Initializing..."
   failedCRC = True
   global lastValue
   while failedCRC :
      degreesF, crcResult = read_temperature()
      if crcResult == "YES":
        floatTemp = float(degreesF)
        lastValue = floatTemp
        failedCRC = False
      else:
        print "Failed CRC at Boot! Retrying..."
        time.sleep(2)




# main program entry point - runs continuously updating our datastream with the
# latest temperature reading
def run():
  global lastValue
  feed = api.feeds.get(FEED_ID)  
  datastream = get_datastream(feed)
  datastream.max_value = None
  datastream.min_value = None
  start()





  
  #degreesF, crcResult = read_temperature()
  #if crcResult == "YES":  
  #   floatTemp = float(degreesF)
  #   lastValue = floatTemp
  #else:
  #   print "Failed CRC at Boot!"
  #   start()


  while True:
    degreesF, crcResult = read_temperature()
    floatTemp = float(degreesF)
    


    if crcResult == "YES":
       print "crc Result: YES"
       if floatTemp < 0:
          print "Temperature Below 0"
          time.sleep(1)
          pass
         
       elif floatTemp > 100:
          print "Temperature Above 100"
          time.sleep(1)
          pass
         
       elif abs(floatTemp - lastValue) > 5:
          print "Difference >5 degrees"
          time.sleep(1)
          pass


       else:
           print "Looks good!"
           datastream.current_value = degreesF
           datastream.at = datetime.datetime.utcnow()
           lastValue = floatTemp
           print "Update Last Value"
           
           try:
              datastream.update()
              print "Update Xively"
              time.sleep(UPDATETIME)
           except requests.HTTPError as e:
              print "HTTPError({0}): {1}".format(e.errno, e.strerror)
              time.sleep(1)
       
    else:
       print "crc Result: NO"
       time.sleep(1)
  

    

run()



