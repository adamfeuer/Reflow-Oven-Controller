#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as pyplot
import os

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
       #pyplot.xticks([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
       pyplot.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
       ax.xaxis.grid(color='gray', linestyle=':')
       ax.yaxis.grid(color='gray', linestyle=':')
       return fig

   def main(self):
      data = self.read_temps(os.path.join('.', 'temp1.txt'))
      print data
      temps = data['Input']
      minutes = data['Time']
      fig = self.temp_plot(minutes ,temps)
      fig.savefig(os.path.join('.', 'reflow-oven-temperature-plot.png'))

if __name__ == "__main__":
   TempPlot().main()
