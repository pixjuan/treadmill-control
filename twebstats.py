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


import serial
import socket
import sys
import subprocess
import time
import signal
import datetime
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import csv
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from threading  import Thread


class twebstats(Thread):

    # maximum number of days to be displayed
    MAX_NB_DAYS = 10
    
    def __init__(self, port = 1044):
	Thread.__init__(self)
        self.port = port
        self.daemon = True


    static_html = """
    <html>
    <body>
    <p>
    Your stats :
    </p>
    <img src="hist.png">
    </body>
    </html>
    """

        
    def serve_static(self, http_env, start_response):
        status = '200 OK'

        response_headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(self.static_html)))
        ]
        start_response(status, response_headers)
        
        return [self.static_html]


    def serve_image(self, http_env, start_response):
        status = '200 OK'
        headers = [('Content-type', 'image/png')]
        start_response(status, headers)

        return open("./hist.png", "rb").read()
    
    def application (self, environ, start_response):
        if environ['PATH_INFO'] == '/hist.png':
            return self.serve_image(environ, start_response)
        else:
            return self.serve_static(environ, start_response)

    def run(self):
        httpd = make_server('localhost', self.port, self.application)
        httpd.serve_forever()


    def draw(self):
        fig, ax = plt.subplots()
        dates = sorted(self.meters_per_day.keys())
        if len(dates) > 10:
            print "keeping only the last ten days from " + str(len(dates))
            dates = dates[-10:]
            print "new size " + str(len(dates))
        
        # we remove the year from the date
        dates_wo_year = []
        for d in dates:
            dates_wo_year.append(d[5:])
            
        x_pos = np.arange(len(dates_wo_year))
        meters = []
        for i in dates:
            meters = meters + [self.meters_per_day[i]]
   
        ax.bar(x_pos, meters, align='center',
        color='green')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(dates_wo_year)
        ax.set_ylabel('meters')
        ax.set_xlabel('day')
        ax.set_title(r'Distance per day')
    
        fig.tight_layout()
        fig.savefig('./hist.png',format='png')


    def readCSV(self, filename='./treadmill.log'):
        with open(filename, 'rb') as csvfile:
            treadmill_stats = csv.reader(csvfile, delimiter=',', quotechar='|')
            self.meters_per_day = dict()
            for row in treadmill_stats:
                print ', '.join(row)
                if row[0] in self.meters_per_day:
                    self.meters_per_day[row[0]] += int(row[4])
                else:
                    self.meters_per_day[row[0]] = int(row[4])

            for i in self.meters_per_day.keys():
                print i,self.meters_per_day[i]
    
def main():
    print "drawing from CSV"
    tweb = twebstats()

    tweb.readCSV()
    tweb.draw()
    tweb.start()

    while True:
        # every 10 minutes we update the charts with the latest CSV data
        time.sleep(600)
        print "generating the bar charts"
        tweb.readCSV()
        tweb.draw()




    
if __name__ == "__main__":
    main()
