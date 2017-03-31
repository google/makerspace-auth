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

"""Abstraction around RPi.GPIO for blinky buttons.
"""

# TODO add pretty error for version mismatch
from RPi import GPIO
import Queue

from authbox.api import BaseThing

class Button(BaseThing):
  def __init__(self, event_queue, config_name, input_pin, output_pin, on_down=None):
    super(Button, self).__init__(event_queue, config_name)
    self.input_pin = int(input_pin)
    self.output_pin = int(output_pin)

    # TODO options for pullup/down/active high/active low?
    # Right now assumes pullup, and active low
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)  # for reusing pins
    GPIO.setup(self.input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.output_pin, GPIO.OUT)
    GPIO.output(self.output_pin, False)

    self._on_down = on_down
    self.blink_command_queue = Queue.Queue()
    self.blink_rate = 0.5  # seconds

  def _callback(self, channel):
    if self._on_down:
      # TODO pass self or self.config_name as a string?
      self.event_queue.put(self._on_down, self.config_name)

  def run(self):
    GPIO.add_event_detect(self.input_pin, GPIO.GPIO_FALLING, callback=self._callback)
    blinking = False
    while True:
      try:
        # Use blocking get instead of sleep.  Once it returns, assume timeout
        # expired (but that might not be the case if we woke up for a signal).
        item = self.blink_command_queue.get(block=True, timeout=self.blink_rate)
        blinking = item
        # Always begin on; always turn off when disabling
        GPIO.output(self.output_pin, blinking)
      except Queue.Empty:
        if blinking:
          GPIO.output(self.output_pin, not GPIO.input(self.output_pin))

  def blink(self):
    self.blink_command_queue.put(True)

  def off(self):
    self.blink_command_queue.put(False)
  # TODO: def on
