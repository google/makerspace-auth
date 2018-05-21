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
  """Button hardware abstraction.

  A button is defined in config as:

    [pins]
    name = Button:1:2

  where 1 is the active-low input pin (physical numbering), and 2 is the output
  pin (also physical numbering).  If you have another kind of button, you
  probably need a different class.
  """

  def __init__(self, event_queue, config_name, input_pin, output_pin, on_down=None):
    super(Button, self).__init__(event_queue, config_name, int(input_pin), int(output_pin))

    self._on_down = on_down
    self.blink_command_queue = Queue.Queue()
    self.blink_duration = 0.5  # seconds
    self.blinking = False
    if self._on_down:
      GPIO.add_event_detect(self.input_pin, GPIO.FALLING, callback=self._callback, bouncetime=150)

  def _callback(self, unused_channel):
    """Wrapper to queue events instead of calling them directly."""
    if self._on_down:
      self.event_queue.put((self._on_down, self))

  def run_inner(self):
    """Perform one on/off/blink pulse."""
    try:
      item = self.blink_command_queue.get(block=True, timeout=self.blink_duration)
      self.blinking = item[0]
      if self.blinking:
        # Always begin on; always turn off when disabling
        GPIO.output(self.output_pin, True)
      else:
        GPIO.output(self.output_pin, item[1])
    except Queue.Empty:
      if self.blinking:
        # When blinking, invert every timeout expiration (we might have woken
        # up for some other reason, but this appears to work in practice).
        GPIO.output(self.output_pin, not GPIO.input(self.output_pin))

  def blink(self):
    """Blink the light indefinitely.

    The time for each on or off pulse is `blink_duration`."""
    self.blink_command_queue.put((True,))

  def on(self):
    """Turn the light (if present) on indefinitely.

    If the light is currently in the blink state, it stops blinking."""
    self.blink_command_queue.put((False, True))

  def off(self):
    """Turn the light (if present) off indefinitely.

    If the light is currently in the blink state, it stops blinkin."""
    self.blink_command_queue.put((False, False))
