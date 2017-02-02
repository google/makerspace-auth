#!/usr/bin/python
#
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import evdev
import threading
import re

from RPi import GPIO


scancodes = {
  # Scancode: ASCIICode
  0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 
  8: u'7', 9: u'8', 10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP',
  15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r', 20: u't', 21: u'y', 
  22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF',
  29: u'LCTRL', 30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 
  36: u'j', 37: u'k', 38: u'l', 39: u';', 40: u'"', 41: u'`', 42: u'LSHFT',
  43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n', 
  50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 
  100: u'RALT'
}

# capscancodes are present to shift badge scans as necessary

capscancodes = {
  0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 
  8: u'&', 9: u'*', 10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 
  15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R', 20: u'T', 21: u'Y', 
  22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 
  29: u'LCTRL', 30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 
  36: u'J', 37: u'K', 38: u'L', 39: u':', 40: u'\'', 41: u'~', 42: u'LSHFT', 
  43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N', 
  50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT', 57: u' ',
  100: u'RALT'
}


class Button(object):

  def __init__(self, input_gpio, light_gpio, press_event=None):
    self.input_gpio = input_gpio
    self.light_gpio = light_gpio
    self.press_event = press_event
    self.pressed = False
    self._blinking = False

    GPIO.setup(self.input_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
      self.input_gpio, GPIO.FALLING, callback=self._callback,
      bouncetime=100)
    GPIO.setup(self.light_gpio, GPIO.OUT)

    def light_on(self):
      self._blinking = False
      GPIO.output(self.light_gpio, 1)

    def light_off(self):
      self._blinking = False
      GPIO.output(self.light_gpio, 0)

    def light_blink(self):
      self._blinking = True
      self._blink_value = 1
      GPIO.output(self.light_gpio, self._blink_value)

    def idle(self):
      if self._blinking:
        self._blink_value ^= 1
        GPIO.output(self.light_gpio, self._blink_value)

  # removes the press events, allows the script to loop without breaking
    def unpress(self):
      self.press_event.clear()
      self.pressed = False

    def _callback(self, channel):
      self.press_event.set()
      self.pressed = True

# looks at connected devices, returns device matching name given
def get_scanner_device():
  deviceName = '<NameOfUSBBadgeScanner>'
  devices = [evdev.InputDevice(x) for x in evdev.list_devices()]
  device = None
  for dev in devices:
    if str(dev.name) == deviceName:
      device = dev
      break
  return device

# read_input listens solely to the RFID keyboard and returns the scanned badge
def read_input(device):
  rfid=''
  capitalized = 0
  for event in device.read_loop():
    data = evdev.categorize(event)
    if event.type == evdev.ecodes.EV_KEY and data.keystate == 1:
      #detects if the keyboard uses "LSHFT"
      if data.scancode == 42:
        capitalized = 1
      if data.keycode == "KEY_ENTER":
        break
      if data.scancode != 42:
        if capitalized:
          rfid += capscancodes[data.scancode]
          capitalized ^= 1
        else:
          rfid += scancodes[data.scancode]
  return rfid

def main():
  GPIO.setmode(GPIO.BOARD)
  evt = threading.Event()
  red = Button(12, 29, evt)
  blue = Button(15, 31, evt)
  # configures power tail 
  GPIO.setup(37, GPIO.OUT)
  dev = get_scanner_device()
  badge = None
  while True:
    if badge == None:
      badge = read_input(dev)
    if badge:
      red.light_blink()
      while True:
        red.idle()
        blue.idle()
        if evt.wait(timeout=0.5):
          if red.pressed and not blue.pressed:
            red.light_on()
            GPIO.output(37, 1)
            break
          if blue.pressed:
            GPIO.output(37, 0)
            red.light_off()
            badge = None
            red.unpress()
            break
      evt.clear()
      if not blue.pressed:
        evt.wait()
      elif blue.pressed:
        blue.unpress()
      
if __name__ == '__main__':
  main()
