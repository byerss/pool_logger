#!/usr/bin/env python

import os
import subprocess
import time
import datetime
import requests
import MySQLdb as my
from Adafruit_IO import Client


UPDATETIME = 60
lastValue = 0
ADAFRUIT_IO_KEY = 'XXXX'
aio = Client(ADAFRUIT_IO_KEY)


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





def start():
   print("Initializing...")
   failedCRC = True
   global lastValue
   while failedCRC :
      degreesF, crcResult = read_temperature()
      if crcResult == "YES":
        floatTemp = float(degreesF)
        lastValue = floatTemp
        failedCRC = False
      else:
        print("Failed CRC at Boot! Retrying...")
        time.sleep(2)




# main program entry point - runs continuously updating our datastream with the
# latest temperature reading
def run():
  global lastValue
  start()



  while True:
    degreesF, crcResult = read_temperature()
    floatTemp = float(degreesF)
    
    if crcResult == "YES":
     print("crc Result: YES")


     if floatTemp < 0:
        print("Temperature Below 0")
        time.sleep(1)
        pass
       
     elif floatTemp > 100:
        print("Temperature Above 100")
        time.sleep(1)
        pass
  
     elif abs(floatTemp - lastValue) > 5:
        print("Difference >5 degrees")
        time.sleep(1)
        pass
  
  
     else:
         print("Looks good!")
         lastValue = floatTemp
         print("Update Last Value")
         try:
           db = my.connect(host="192.168.1.22",
           user="rpi",
           passwd="olpride",
           db="test"
           )
           cursor = db.cursor()
           sql = "insert into temperature VALUES(now(), '%s')" % (floatTemp)
           number_of_rows = cursor.execute(sql)
           db.commit()   #Needed to commit changes
           db.close()
         except:
           pass
         
         try:
           aio.send('Pool_Monitor', floatTemp)
         except:
           pass

         time.sleep(60)
         #quit()
    else:
     print("crc Result: NO")
     time.sleep(1)    






run()
