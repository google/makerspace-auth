# Copyright 2018 Google Inc. All Rights Reserved.
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

"""Test helper that logs instead of altering pin states."""

import time
from RPi import GPIO

class FakeGPIO(object):
  """Fake for the RPi.GPIO module (parts of it)."""

  def __init__(self, fake_time=None):
    self.pin_states = [0] * 10
    self.events = {}
    self.time = fake_time or time

    self.t_zero = self.time.time()
    self.log = []

    GPIO.output = self.output
    GPIO.input = self.input
    GPIO.add_event_detect = self.add_event_detect

  def output(self, n, v):
    self.pin_states[n] = v
    self.log.append((self.time.time() - self.t_zero, n, bool(v)))

  def input(self, n):
    return self.pin_states[n]

  def add_event_detect(self, n, edge, callback=None, bouncetime=None):
    # TODO only supports one callback
    self.events[n] = (edge, callback, bouncetime)

  def press(self, n, edge):
    # TODO support bidirectional edge
    if self.events[n] and self.events[n][0] == edge:
      self.events[n][1]()

  def compare_log(self, expected_log):
    print "Expecting", expected_log
    print "Actual", self.log
    for entry in expected_log:
      for e in self.log:
        if abs(e[0] - entry[0]) < 0.1 and e[1] == entry[1] and e[2] == entry[2]:
          break
      else:
        print "Missing", entry
        return False
    return True


class FakeTime(object):
  """Fake for the module 'time' so tests run faster."""

  def __init__(self):
    self.t = 0

  def time(self):
    return self.t

  def sleep(self, x):
    self.t += x

# TODO: Queue patcher that also advances time
