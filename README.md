# treadmill-control
Project for controlling your treadmill with an Arduino

It consist of 3 parts :
- some Arduino code to control the treadmill
- some Python code to communicate with the Arduino and interact with the user
- a wrapper around socat to send commands through the CLI

Dependencies:

- Timer module for the Arduino code, can be downloaded athttp://playground.arduino.cc/Code/Timer
- matplotlib, cand be sintalled with : pip install matplotlib
- socat, on debian derivatives, it can be installed with : apt-get install socat

The other details are on the HackaDay project page : https://hackaday.io/project/25881-keyboard-controlled-treadmilldesk



Configuration

For the moment, you need to edit treadmill-server.py if you want to customize the default UDP port or your weight.


Usage

Start the server with the following command line : treadmill-server.py [serial_device [udp_port]]
You can then control the treadmill by calling treadmill-cmd with a parameter:
 s : start/stop the treadmill
 p : increase speed
 m : decrease speed

You can then open localhost:1044 in your favorite browser to check your statistics.
