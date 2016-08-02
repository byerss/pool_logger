#!/usr/bin/env python

import os
import xively
import subprocess
import time
import datetime
import requests

FEED_ID = "1347438342"
API_KEY = "hsvCyBwg6hgQwpGyUYzsz1yqD3CAt0rx8ID8eDcdVssqpvTd"

# initialize api client
api = xively.XivelyAPIClient(API_KEY)

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
   return temperature

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("Pool_Temperature")
    return datastream
  except:
    datastream = feed.datastreams.create("Pool_Temperature", tags="temperature")
    return datastream

# main program entry point - runs continuously updating our datastream with the
# latest temperature reading
def run():
  feed = api.feeds.get(FEED_ID)

  datastream = get_datastream(feed)
  datastream.max_value = None
  datastream.min_value = None

  while True:
    degreesF = read_temperature()
    datastream.current_value = degreesF
    datastream.at = datetime.datetime.utcnow()
    try:
      datastream.update()
    except requests.HTTPError as e:
      print "HTTPError({0}): {1}".format(e.errno, e.strerror)

    time.sleep(60)

run()

