/*
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

//from http://playground.arduino.cc/Code/Timer
#include "Timer.h"

// customize this part if you use different pins on the Arduino
#define PIN_SPEED_PLUS 2
#define PIN_SPEED_MINUS 4
#define PIN_START_STOP 3
#define PULSE_LENGTH 200
 
Timer t;

int inByte = 0;         // incoming serial byte

// speed are in tenth of km/h
unsigned int maxSpeed = 80;
// min speed is 0,5 km/h, or 500 meters/h
unsigned int minSpeed = 5;
unsigned int currentSpeed = 5; // the initial value is the speed of the treadmill when it just switched on
unsigned int speedStep = 1; // the step it increases/decreases every time we push a button
int treadmillRunning = 0; // 1 if the treadmill motor is on, 0 otherwise
// this variable must be divided by (3600 * 10)  for km and by 36 for meters
unsigned long totalDistance = 0;
unsigned long previousTotalDistance = 0;
unsigned int minuteCounter = 0;

void countDistance()
{
  if (treadmillRunning)
    totalDistance += currentSpeed;
  if ((minuteCounter++) % 60 == 0) {
    Serial.print("M :");
    Serial.println(totalDistance - previousTotalDistance);
    previousTotalDistance = totalDistance;
  }
  
}

// TODO add a soft or hard reset to reset the speed when the safety clip is removed

void setup() {
  pinMode(PIN_SPEED_PLUS, OUTPUT);
  pinMode(PIN_START_STOP, OUTPUT);
  pinMode(PIN_SPEED_MINUS, OUTPUT);
  digitalWrite(PIN_SPEED_PLUS, HIGH);
  digitalWrite(PIN_START_STOP, HIGH);
  digitalWrite(PIN_SPEED_MINUS, HIGH);

  int kmCounterEvent = t.every(1000, countDistance);
  
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
}

void loop() {
  t.update();
  if (Serial.available() > 0) {
    // get incoming byte:
    inByte = Serial.read();

    if (inByte == 'p') {
      digitalWrite(PIN_SPEED_PLUS, LOW);
      delay(PULSE_LENGTH);
      digitalWrite(PIN_SPEED_PLUS, HIGH);
      if (treadmillRunning && currentSpeed < maxSpeed) {
      currentSpeed += speedStep;
      }
      Serial.print("S :");
      Serial.println(currentSpeed);
    }
    else if (inByte == 'm') {
      digitalWrite(PIN_SPEED_MINUS, LOW);  
      delay(PULSE_LENGTH);
      digitalWrite(PIN_SPEED_MINUS, HIGH);
      if (treadmillRunning  && currentSpeed > minSpeed ){
      currentSpeed -= speedStep;
      }
      Serial.print("S :");
      Serial.println(currentSpeed);
    }
    else if (inByte == 's') {
      digitalWrite(PIN_START_STOP, LOW);
      delay(PULSE_LENGTH);
      digitalWrite(PIN_START_STOP, HIGH);

      // display distance everytime we start/stop
      if (treadmillRunning) {
        Serial.print("D : ");
      }
      else {
        // we signal that the treadmill is starting so that we can start recording
        Serial.print("G : ");
      }
      Serial.println(totalDistance/36);
      treadmillRunning = treadmillRunning?0:1;
    }
    else if (inByte == 'k') {
      Serial.print("D : ");
      Serial.println(totalDistance/36);
    }
    else if (inByte == 'i') { // information
      Serial.print("S : ");
      Serial.println(currentSpeed);
    }
    else {
      Serial.print("#unknown command :");
      Serial.write(inByte);
      Serial.println();
    }
  }
  else {
    delay(10);
  }
    
}
