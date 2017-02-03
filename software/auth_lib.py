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

"""The library used to create software for the Auth project.

This file is intended to store the classes and (majority of) functions used in
the code for an implementation. It currently contains the button, buzzer,
and power_switch classes.
"""

import re
import time
import weakref

import evdev
import RPi.GPIO as GPIO

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


class Buzzer(object):
  """Buzzer that creates a tone when device powers on or off.
  """

  def __init__(self, buzzer_gpio, interval=0.1, duty_cycle=90):
    self.buzzer_gpio = buzzer_gpio
    self.duty_cycle = duty_cycle
    self.interval = interval

    GPIO.setup(self.buzzer_gpio, GPIO.OUT)
    # initialize PWM instance with arbitrary frequency (always changed in use)
    self.buzzer_obj = GPIO.PWM(buzzer_gpio, 1)

  def happy_tune(self):
    # steps up from E5 to B5
    pitches = [660, 988]
    for x in pitches:
      self.buzzer_obj.ChangeFrequency(x)
      self.buzzer_obj.start(self.duty_cycle)
      time.sleep(self.interval)
      self.buzzer_obj.stop()
      time.sleep(self.interval)

  def sad_tune(self):
    # steps down from B5 to E5
    pitches = [988, 660]
    for x in pitches:
      self.buzzer_obj.ChangeFrequency(x)
      self.buzzer_obj.start(self.duty_cycle)
      time.sleep(self.interval)
      self.buzzer_obj.stop()
      time.sleep(self.interval)


class PowerSwitch(object):
  """Object to control power for connected device.
  """

  def __init__(self, switch_gpio):
    self.switch_gpio = switch_gpio

    GPIO.setup(self.switch_gpio, GPIO.OUT)

  def activate(self):
    GPIO.output(self.switch_gpio, 1)

  def deactivate(self):
    GPIO.output(self.switch_gpio, 0)

  def get_status(self):
    tail_status = GPIO.input(self.switch_gpio)
    return tail_status


class Button(object):
  """Represents physical buttons used to dictate flow in Auth software.
  """
  # tracks instances of buttons
  # used in the case that a value needs checked within all instances
  instances = []

  def __init__(self, input_gpio, light_gpio, press_event=None, lock=None):
    self.__class__.instances.append(weakref.proxy(self))
    self.input_gpio = input_gpio
    self.light_gpio = light_gpio
    self.press_event = press_event
    self.pressed = False
    self._blinking = False
    self.lock = lock

    GPIO.setup(self.input_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        self.input_gpio, GPIO.FALLING, callback=self.press,
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

  # intended to be run as a thread, only loops when lock isn't set.
  def continuous_blink(self):
    if self.lock.locked():
      return
    else:
      with self.lock:
        while not self.press_event.is_set() and self._blinking:
          self._blink_value ^= 1
          GPIO.output(self.light_gpio, self._blink_value)
          time.sleep(0.5)

  # removes the press events, allows the script to loop without breaking
  def unpress(self):
    self.press_event.clear()
    self.pressed = False

  # channel appears unused, but is necessary as the GPIO event detect callback
  # passes a second argument to this function
  def press(self, channel):
    self.press_event.set()
    self.pressed = True


def get_scanner_device():
  """Finds connected device matching name given.

  Returns:
    The file for input events that read_input can listen to
  """

  device_name = '<USBBadgeScanner>'
  devices = [evdev.InputDevice(x) for x in evdev.list_devices()]
  device = None
  for dev in devices:
    if str(dev.name) == device_name:
      device = dev
      break
  return device


def read_input(device):
  """Listens solely to the RFID keyboard and returns the scanned badge.

  Args:
    device: input device to listen to

  Returns:
    badge value as string
  """

  rfid = ''
  capitalized = 0
  for event in device.read_loop():
    data = evdev.categorize(event)
    if event.type == evdev.ecodes.EV_KEY and data.keystate == 1:
    # detects if the keyboard uses "LSHFT"
      if data.scancode == 42:
        capitalized = 1
      if data.keycode == 'KEY_ENTER':
        break
      if data.scancode != 42:
        if capitalized:
          rfid += capscancodes[data.scancode]
          capitalized ^= 1
        else:
          rfid += scancodes[data.scancode]
  return rfid


def thread_check(timer):
  """Finds status of thread/timer objects.

  Thread/timer objects can be in either 'initial', 'started', or 'stopped'
  (which is seen if you print the object). Checking if an object's state matches
  'initial' checks if it has been made but not started.

  Args:
    timer: thread/timer object to be checked.

  Returns:
    thread state between 'initial', 'started', or 'stopped'.
  """
  joiner = ''.join(map(str, re.findall(r'[A-Za-z\s]', timer.__repr__())))
  split = joiner.split()
  return split[1]


def cancel_timers(timer_list):
  """Given a list of timer objects, cancels all of them.

  Args:
    timer_list: a list of timer objects
  """
  for x in timer_list:
    if x.is_alive() or thread_check(x) == 'initial':
      x.cancel()


def power_off(badge_timer, red, badge, timer_list):
  """Removes value from badge.

  Args:
    badge_timer: badge_timer object
    red: On/Extend button object to unpress
    badge: badge variable as string
    timer_list: list of timer objects that will be cancelled

  Returns:
    badge value of None
  """
  badge_timer.cancel()
  red.light_off()
  cancel_timers(timer_list)
  badge = None
  red.unpress()
  return badge


def check_all_buttons(button_list):
  """Makes sure no buttons are currently pressed.

  It may be necessary to manually set a threading event (which passes
  threading.Event().wait()) without a button being pressed. This allows an
  action to be taken should no buttons be pressed, but an event object is set.

  Args:
    button_list: list of buttons to be checked (commonly Button.instances)

  Returns:
    True if a button is pressed.
    False if no buttons in the list are pressed.
  """
  for x in button_list:
    if x.pressed:
      return True
    else:
      pass
  return False

