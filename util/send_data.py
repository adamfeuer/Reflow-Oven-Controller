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
filename = "temp1.txt"
lines = open(filename).readlines()
start = datetime.datetime.today()
count = 0
for line in lines:
   ser.write(line) 
   print line,
   count += len(line)
end = datetime.datetime.today()
delta = end - start
deltaSeconds = delta.total_seconds()
bytesPerSecond = count / deltaSeconds
print "%d bytes sent in %f seconds." % (count, deltaSeconds)
print "Bytes per second: %f" % bytesPerSecond
ser.close()
