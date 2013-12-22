
You can test the realtime graphing without having a RocketScream reflow oven controller connected.

1. Install the socat utility

2. Use socat to create 2 connected virtual serial ports:

  $ socat -d -d pty,raw,echo=1 pty,raw,echo=1

3. Use the send_data.py script to send the sample data file to the serial port using PySerial:

  $ ./send_data.py /dev/ttys020 57600

4. Launch the wx_reflow_plot.py script using the other virtual serial port:

  $ python wx_reflow_plot.py /dev/ttys021 57600

5. The send_data.py script emulates the reflow oven controller.

