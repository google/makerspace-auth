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

"""Abstraction for blinky buttons.
"""

from authbox.api import BasePinThread
from authbox.compat import queue
import gpiozero
import time


class Button(BasePinThread):
    """Button hardware abstraction.

    A button is defined in config as:

      [pins]
      name = Button:1:2

    where 1 is the active-low input pin (physical numbering), and 2 is the output
    pin (also physical numbering).  If you have another kind of button, you
    probably need a different class.
    """

    def __init__(
        self,
        event_queue,
        config_name,
        input_pin,
        output_pin,
        on_down=None,
        blink_command_queue_cls=queue.Queue,
    ):
        super(Button, self).__init__(
            event_queue, config_name, int(input_pin), int(output_pin)
        )

        self._on_down = on_down
        self.blink_command_queue = blink_command_queue_cls()
        self.blink_duration = 0.5  # seconds
        self.blinking = False
        self.blink_count = 0
        self.steady_state = False
        self.gpio_led = gpiozero.LED(pin="BOARD" + str(self.output_pin))
        button_pin = "BOARD" + str(self.input_pin)
        self.gpio_button = gpiozero.Button(button_pin, bounce_time = 0.15)
        if self._on_down:
            self.gpio_button.when_pressed = self._callback

    def _callback(self):
        """Wrapper to queue events instead of calling them directly."""
        # If we have a callback registered, debounce the switch press
        if (self._on_down):
            # This is a de-bounce filter to prevent spurious signals from triggering the logic
            # Looks for 5 continuous active states (each separated by 10ms)
            maxcount = 15 # Look for 150ms maximum
            lowcount = 0 # Count the number of active states seen
            while ((maxcount > 0) and (lowcount <= 4)):
                time.sleep(0.01) # 10ms delay between each cycle
                maxcount = maxcount - 1 # Decrement remaining cycles
                if (self.gpio_button.is_pressed):
                    lowcount = lowcount + 1 # One more low cycle detected
                else:
                   lowcount = 0 # Not continuously low, reset
            if (lowcount > 4):
                self.event_queue.put((self._on_down, self))

    def run_inner(self):
        """Perform one on/off/blink pulse."""
        try:
            item = self.blink_command_queue.get(block=True, timeout=self.blink_duration)
            self.blinking = item[0]
            if self.blinking:
                # Always begin opposite of current state for immediate visual feedback
                self.gpio_led.toggle()
                # Calculate number of remaining on/off blink toggles after this one
                # A zero count means to keep blinking indefinitely
                self.blink_count = item[1] * 2 - 1 if item[1] else 0
            else:
                # Remember last non-blinking state of the light which will be restored
                # after finite blink count has completed.
                self.steady_state = item[1]
                self.gpio_led.value = item[1]
        except queue.Empty:
            if self.blinking:
                # If blinking a finite number of times, count each on/off transition
                if self.blink_count > 0:
                    self.blink_count -= 1
                    if self.blink_count == 0:
                        # Ensure at the end of finite blink count we always return to
                        # the last on/off steady state, even if a new blink was started
                        # before a previous blink has finished.
                        self.gpio_led.value = self.steady_state
                        self.blinking = False

                # Toggle output if blinking indefinitely or finite count not exhausted
                if self.blinking:
                    # When blinking, invert every timeout expiration (we might have woken
                    # up for some other reason, but this appears to work in practice).
                    self.gpio_led.toggle()

    def blink(self, count=0):
        """Blink the light count number of times. If count is 0 then blink
        indefinitely.

        The time for each on or off pulse is `blink_duration`."""
        self.blink_command_queue.put((True, count))

    def on(self):
        """Turn the light (if present) on indefinitely.

        If the light is currently in the blink state, it stops blinking."""
        self.blink_command_queue.put((False, True))

    def off(self):
        """Turn the light (if present) off indefinitely.

        If the light is currently in the blink state, it stops blinkin."""
        self.blink_command_queue.put((False, False))

    def is_pressed(self):
        """Returns True if the button is currently pressed, False otherwise."""
        return self.gpio_button.is_pressed
