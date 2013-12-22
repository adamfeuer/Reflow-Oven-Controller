#!/usr/bin/env python

"""

reflow_plot.py - make a temperature plot from 
the output of a RocketScream reflow oven controller
using matplotlib

For more info see:

   http://www.rocketscream.com/blog/documents/reflow-controller-shield/
   https://github.com/rocketscream/Reflow-Oven-Controller

The MIT License (MIT)

Copyright (c) 2013 Adam Feuer <adam@adamfeuer.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import sys, os, argparse
import numpy as np
import matplotlib.pyplot as pyplot

def seconds2minutes(seconds):
   return float(seconds.strip())/60.0

class TempPlot:
   def __init__(self):
      pass

   def read_temps(self,file_name):
       dtypes = np.dtype({ 'names' : ('Time', 'Input'),
                           'formats' : [np.float, np.float] })

       data = np.loadtxt(file_name, delimiter=' ', skiprows=1, 
               converters = { 0: seconds2minutes },
               usecols=(0,2), dtype=dtypes)

       return data

   def temp_plot(self, minutes, temps):
       fig = pyplot.figure(figsize=(12,5))
       ax = fig.add_subplot(1,1,1)
       pyplot.title('Reflow oven temperature plot')
       pyplot.ylabel('Temperature ($^\circ$C)')
       pyplot.xlabel('Minutes')
       pyplot.plot(minutes, temps, linestyle="-")
       pyplot.legend(loc='lower right')
       pyplot.yticks([25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275])
       pyplot.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
       ax.xaxis.grid(color='gray', linestyle=':')
       ax.yaxis.grid(color='gray', linestyle=':')
       return fig

   def parse_args(self):
      parser = argparse.ArgumentParser(description='Plot temperature graph from RocketScream reflow oven controller.')
      parser.add_argument('input_filename', metavar='input_filename', type=str, 
                         help='Input data from the reflow oven')
      parser.add_argument('output_filename', metavar='output_filename', type=str,
                         help='Output plot image filename (PNG)')
      args = parser.parse_args()
      self.input_filename = args.input_filename
      self.output_filename = args.output_filename
      print self.input_filename
      print self.output_filename

   def main(self):
      self.parse_args()
      data = self.read_temps(self.input_filename)
      temps = data['Input']
      minutes = data['Time']
      fig = self.temp_plot(minutes ,temps)
      fig.savefig(self.output_filename)

if __name__ == "__main__":
   TempPlot().main()
