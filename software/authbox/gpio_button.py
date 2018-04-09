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

"""Abstraction around RPi.GPIO for blinky buttons.
"""

import Queue

from authbox.api import BasePinThread, GPIO

class Button(BasePinThread):
  def __init__(self, event_queue, config_name, input_pin, output_pin, on_down=None):
    super(Button, self).__init__(event_queue, config_name, int(input_pin), int(output_pin))

    self._on_down = on_down
    self.blink_command_queue = Queue.Queue()
    self.blink_duration = 0.5  # seconds
    if self._on_down:
      GPIO.add_event_detect(self.input_pin, GPIO.FALLING, callback=self._callback, bouncetime=150)


  def _callback(self, unused_channel):
    if self._on_down:
      self.event_queue.put((self._on_down, self))

  def run(self):
    # run is only expected to be called once.
    blinking = False
    blink_count = 0
    steady_state = False
    while True:
      try:
        item = self.blink_command_queue.get(block=True, timeout=self.blink_duration)
        blinking = item[0]
        if blinking:
          # Always begin opposite of current state for immediate visual feedback
          GPIO.output(self.output_pin, not GPIO.input(self.output_pin))
          # Counts every on/off transition internally
          blink_count = item[1] * 2
        else:
          steady_state = item[1]
          GPIO.output(self.output_pin, steady_state)
      except Queue.Empty:
        if blinking:
          # When blinking, invert every timeout expiration (we might have woken
          # up for some other reason, but this appears to work in practice).
          GPIO.output(self.output_pin, not GPIO.input(self.output_pin))
          if blink_count > 0:
            blink_count -= 1
            if blink_count == 0:
              # Ensure at the end of finite blink count we always return to
              # the last on/off steady state, even if a new blink was started
              # before a previous blink has finished.
              GPIO.output(self.output_pin, steady_state)
              blinking = False

  def blink(self, count=0):
    self.blink_command_queue.put((True, count))

  def on(self):
    self.blink_command_queue.put((False, True))

  def off(self):
    self.blink_command_queue.put((False, False))
