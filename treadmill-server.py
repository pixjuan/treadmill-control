#! /usr/bin/python

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# usage : treadmill-server.py [serial_device [udp_port]]

import serial
import socket
import sys
import subprocess
import time
import signal
from tmwebstats import tmwebstats

treadmill_log = None


def sigint_handler(signal, frame):
        print('cleaning on exit')
        if treadmill_log is not None:
            treadmill_log.close()
        sys.exit(0)


class treadmill_server:

    SERIAL_DEVICE = '/dev/ttyUSB0'
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    OSD_ENABLED = 1
    WEB_SERVER_ENABLED = 1
    LOGFILE = './treadmill.log'
    minute_counter = 0
    treadmill_log = None
    cumulative_distance = 0
    treadmill_running = False
    start_time = time.strftime('%Y-%m-%d,%H,%M,%S')
    user_weight = 75
    treadmill_speed = 5
    webstats = None

    def get_calories(self, t, speed, wkg):
        # C = (0.0215 x KPH3 - 0.1765 x KPH2 + 0.8710 x KPH + 1.4577) x WKG x T
        return (0.0215 * speed * speed * speed - 0.1765 * speed * speed
                + 0.8710 * speed + 1.4577) * wkg * t

    def treadio(self, msg):
        if msg[0] == '#':
            print msg
        else:
            kv = msg.split(':')
            if kv[0][0] == 'M':
                self.cumulative_distance += int(kv[1])
                print "delta dist : {0} / session : {1}".format(
                    kv[1].strip(), str(self.cumulative_distance/36))
                self.minute_counter += 1

            elif kv[0][0] == 'D':
                # each time we stop the treadmill, we add an entry in the CSV
                # file with the following format:
                # date, hours, minutes, seconds, distance, duration, calories

                print("updating CSV file")
                self.treadmill_log.write(self.start_time + ',' +
                                         str(self.cumulative_distance/36) +
                                         ',')
                self.treadmill_log.write(str(self.minute_counter) + ',')
                calories = self.get_calories(self.minute_counter / 60.0,
                                             self.treadmill_speed/10.0,
                                             self.user_weight)
                self.treadmill_log.write(str(int(calories)) + '\n')
                self.treadmill_log.flush()
                self.cumulative_distance = 0
                self.minute_counter = 0
                if self.OSD_ENABLED:
                    subprocess.call(['/usr/bin/notify-send',
                                     'distance : ' + kv[1]])
                if self.webstats is not None:
                    self.webstats.readCSV()
                    self.webstats.draw()
                    
            elif kv[0][0] == 'G':
                self.start_time = time.strftime('%Y-%m-%d,%H,%M,%S')
            elif kv[0][0] == 'S':
                self.treadmill_speed = int(kv[1])
            else:
                print "unknown : " + str(kv)

    def main_loop(self):

        ser = serial.Serial(self.SERIAL_DEVICE, 9600, timeout=0)
        if ser is None:
            raise RuntimeError("serial connection failed")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(2)
        sock.bind((self.UDP_IP, self.UDP_PORT))

        self.treadmill_log = open(self.LOGFILE, 'a+')

        while True:
            data = ""
            try:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            except socket.timeout, e:
                err = e.args[0]
                if err == 'timed out':
                    time.sleep(1)
                else:
                    print e
                    sys.exit(1)

            if len(data) > 0:
                print "received UDP message:", data
                ser.write(data[0])  # only write the first byte
                if data[0] != 'p' and data[0] != 'm':
                    time.sleep(1)
                    if ser.inWaiting() > 0:
                        treadData = ser.read(ser.inWaiting()).decode('ascii')

                        lines = treadData.split('\n')
                        print "read Arduino data : " + treadData
                        for i in lines:
                            if len(i) > 0:
                                self.treadio(i)


def main():
    global treadmill_log

    s = treadmill_server()

    # we need globals for sigint handler
    treadmill_log = s.treadmill_log

    if len(sys.argv) >= 2:
        s.SERIAL_DEVICE = sys.argv[1]
    if len(sys.argv) >= 3:
        s.UDP_PORT = sys.argv[1]

    signal.signal(signal.SIGINT, sigint_handler)

    if s.WEB_SERVER_ENABLED:
        print "starting web server"
        
        t = tmwebstats()
        s.webstats = t
        with open(s.LOGFILE, 'a+') as f:
            pass
        t.readCSV()
        t.draw()
        t.start()

    s.main_loop()


if __name__ == "__main__":
    main()
