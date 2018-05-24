# Copyright 2017-2018 Google Inc. All Rights Reserved.
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

"""Abstraction around RPi.GPIO for 3-position switches.

We assume that it's two pins active-low, with the third state represented by
pullups.
"""

import logging
import time

from authbox.api import BasePinThread, GPIO


class ThreePosSwitch(BasePinThread):
  """3-position switch+light abstraction.

  A switch is defined in config as

    [pins]
    name = ThreePosSwitch:1:2:3:4:5

  The switch is intended to be something like an E-Switch 100SP3T4B1M1QEH; it
  has 3 positions which are signaled to authboard by shorting pin 1 to GND,
  shorting none to GND, and shorting pin 2 to GND, respectively.  These 3
  positions correspond to green, yellow, and red.  On Authboard v1.0 there is a
  connector J5 which is intended for this.

  The output is pins 3,4,5 which correspond to green, yellow, and red.

  It will also issue callbacks on change, which the business logic code can use
  to report status elsewhere.
  """

  def __init__(self, event_queue, config_name, input1_pin, input2_pin,
               green_pin, yellow_pin, red_pin, on_change=None):
    super(ThreePosSwitch, self).__init__(event_queue, config_name, None, None)
    self._on_change = on_change
    self.input1_pin = int(input1_pin)
    self.input2_pin = int(input2_pin)
    self.green_pin = int(green_pin)
    self.yellow_pin = int(yellow_pin)
    self.red_pin = int(red_pin)
    self.state = None
    for p in (self.green_pin, self.yellow_pin, self.red_pin):
      GPIO.setup(p, GPIO.OUT)
      GPIO.output(p, 0)

    if self._on_change:
      GPIO.setup(self.input1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(self.input2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  def change_color(self):
    """Read/write pins.

    Returns: Whether the color changed.
    """
    p1 = GPIO.input(self.input1_pin)
    p2 = GPIO.input(self.input2_pin)
    # Decode these into [0, 1, 2] representing the three states.
    states = {
        (1, 0): 0,
        (1, 1): 1,
        (0, 1): 2,
        (0, 0): None,  # Wiring error?
    }
    if states[(p1, p2)] == self.state:
      #print "No change"
      return False
    self.state = states[(p1, p2)]
    color_map = {
        0: (1, 0, 0),
        1: (0, 1, 0),
        2: (0, 0, 1),
        None: (1, 1, 1),  # Error
    }
    m = color_map[self.state]
    logging.info('Given switch %d %d %s -> color %s', p1, p2, self.state, m)
    GPIO.output(self.green_pin, m[0])
    GPIO.output(self.yellow_pin, m[1])
    GPIO.output(self.red_pin, m[2])
    return True

  def run_inner(self):
    # An extremely simple ratelimit like this acts like a debounce, while
    # always ensuring that we correctly read the current state.  In testing, it
    # appeared that events generated while in the callback do not cause another
    # callback to happen.
    time.sleep(0.5)
    if self.change_color() and self._on_change:
      self.event_queue.put((self._on_change, self))
