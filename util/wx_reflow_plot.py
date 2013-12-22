#!/usr/bin/env python

import os, pprint, random, sys, wx, serial, argparse
import numpy as np
import matplotlib.pyplot as pyplot

"""

wx_reflow_plot.py - make a temperature plot from
the output of a RocketScream reflow oven controller
in real time using pyserial, matplotlib, and WxPython

WxPython graphing based on public domain code by Eli Bendersky (eliben@gmail.com)

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


# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
      FigureCanvasWxAgg as FigCanvas, \
      NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab

class DataGen(object):
   def __init__(self, init=50):
      self.data = self.init = init
      self.pos = 0
      self.openSerialPort()

   def parse_args(self):
      parser = argparse.ArgumentParser(description='Plot temperature graph from RocketScream reflow oven controller.')
      parser.add_argument('serial_port', metavar='serial_port', type=str,
                         help='serial port name (/dev/ttyS0 or similar on Unix')
      parser.add_argument('baud_rate', metavar='baud_rate', type=int,
                         help='Baud rate')
      args = parser.parse_args()
      self.serial_port = args.serial_port
      self.baud_rate = args.baud_rate

   def openSerialPort(self):
      self.parse_args()
      self.ser = serial.Serial(port=self.serial_port, baudrate=self.baud_rate)
      print "using device: %s" % self.ser.portstr

   def next(self):
      line = self.ser.readline().strip()
      print line
      fields = line.split(' ')
      if len(fields) == 4:
         try:
            temp = float(fields[2].strip())
            return temp
         except:
            return None
      else:
         return None

class BoundControlBox(wx.Panel):
   """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
   """
   def __init__(self, parent, ID, label, initval):
      wx.Panel.__init__(self, parent, ID)

      self.value = initval

      box = wx.StaticBox(self, -1, label)
      sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

      self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
      self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
      self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)

      self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
      self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

      manual_box = wx.BoxSizer(wx.HORIZONTAL)
      manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
      manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

      sizer.Add(self.radio_auto, 0, wx.ALL, 10)
      sizer.Add(manual_box, 0, wx.ALL, 10)

      self.SetSizer(sizer)
      sizer.Fit(self)

   def on_update_manual_text(self, event):
      self.manual_text.Enable(self.radio_manual.GetValue())

   def on_text_enter(self, event):
      self.value = self.manual_text.GetValue()

   def is_auto(self):
      return self.radio_auto.GetValue()

   def manual_value(self):
      return self.value


class GraphFrame(wx.Frame):
   """ The main frame of the application
   """
   title = 'Reflow monitor'

   def __init__(self):
      wx.Frame.__init__(self, None, -1, self.title)

      self.paused = False
      self.datagen = DataGen()
      self.data = []
      self.append_data()

      self.create_menu()
      self.create_status_bar()
      self.create_main_panel()

      self.redraw_timer = wx.Timer(self)
      self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
      self.redraw_timer.Start(100)

   def create_menu(self):
      self.menubar = wx.MenuBar()

      menu_file = wx.Menu()
      m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
      self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
      menu_file.AppendSeparator()
      m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
      self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

      self.menubar.Append(menu_file, "&File")
      self.SetMenuBar(self.menubar)

   def create_main_panel(self):
      self.panel = wx.Panel(self)

      self.init_plot()
      self.canvas = FigCanvas(self.panel, -1, self.fig)

      self.vbox = wx.BoxSizer(wx.VERTICAL)
      self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        

      self.panel.SetSizer(self.vbox)
      self.vbox.Fit(self)

   def create_status_bar(self):
      self.statusbar = self.CreateStatusBar()

   def init_plot(self):
      self.dpi = 100
      self.fig = Figure((6.0, 3.0), dpi=self.dpi)

      self.axes = self.fig.add_subplot(111)
      self.axes.set_axis_bgcolor('black')
      self.axes.set_title('Oven temperature', size=12)

      pylab.setp(self.axes.get_xticklabels(), fontsize=8)
      pylab.setp(self.axes.get_yticklabels(), fontsize=8)

      # plot the data as a line series, and save the reference 
      # to the plotted line series
      #
      self.plot_data = self.axes.plot(
            self.data, 
            linewidth=1,
            color=(1, 1, 0),
            )[0]

   def draw_plot(self):
      """ Redraws the plot """
      # when xmin is on auto, it "follows" xmax to produce a 
      # sliding window effect. therefore, xmin is assigned after
      # xmax.
      #
      xmax = len(self.data) if len(self.data) > 100 else 100
      #xmin = xmax - 50
      xmin = 0

      # for ymin and ymax, find the minimal and maximal values
      # in the data set and add a mininal margin.
      # 
      # note that it's easy to change this scheme to the 
      # minimal/maximal value in the current display, and not
      # the whole data set.
      # 
      ymin = round(min(self.data), 0) - 0
      ymax = round(max(self.data), 0) + 50

      self.axes.set_xbound(lower=xmin, upper=xmax)
      self.axes.set_ybound(lower=ymin, upper=ymax)

      # anecdote: axes.grid assumes b=True if any other flag is
      # given even if b is set to False.
      # so just passing the flag into the first statement won't
      # work.
      #
      self.axes.grid(True, color='gray')

      # Using setp here is convenient, because get_xticklabels
      # returns a list over which one needs to explicitly 
      # iterate, and setp already handles this.
      #  
      pylab.setp(self.axes.get_xticklabels(), 
            visible=True)

      self.plot_data.set_xdata(np.arange(len(self.data)))
      self.plot_data.set_ydata(np.array(self.data))

      self.canvas.draw()

   def on_save_plot(self, event):
      file_choices = "PNG (*.png)|*.png"

      dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)

      if dlg.ShowModal() == wx.ID_OK:
         path = dlg.GetPath()
         self.canvas.print_figure(path, dpi=self.dpi)
         self.flash_status_message("Saved to %s" % path)

   def on_redraw_timer(self, event):
      # if paused do not add data, but still redraw the plot
      # (to respond to scale modifications, grid change, etc.)
      #
      if not self.paused:
         self.append_data()

      self.draw_plot()

   def append_data(self):
      data = self.datagen.next()
      if data is not None:
         self.data.append(data)

   def on_exit(self, event):
      self.Destroy()

   def flash_status_message(self, msg, flash_len_ms=1500):
      self.statusbar.SetStatusText(msg)
      self.timeroff = wx.Timer(self)
      self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
      self.timeroff.Start(flash_len_ms, oneShot=True)

   def on_flash_status_off(self, event):
      self.statusbar.SetStatusText('')

   def main(self):
      self.parse_args()

if __name__ == '__main__':
   app = wx.PySimpleApp()
   app.frame = GraphFrame()
   app.frame.Show()
   app.MainLoop()

