#!/usr/bin/env python

import sys, serial, time, datetime

argsLen = len(sys.argv)
if argsLen < 2 or argsLen > 3:
   print "Usage: send_test [serial device name] [baudrate]"
   sys.exit()
PORT = sys.argv[1]
BAUDRATE = sys.argv[2]

chars = ""
ser = serial.Serial(port=PORT, baudrate=BAUDRATE)
print "using device: %s" % ser.portstr
while 1:
   line = ser.readline().strip()
   print line
ser.close()
