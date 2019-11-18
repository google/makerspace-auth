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

"""Abstraction around RPi.GPIO for buzzer type outputs.
"""
from __future__ import print_function

import time

from authbox.api import GPIO, BasePinThread
from authbox.compat import queue

OFF = 0
ON = 1
BEEPING = 2
# HAPPY = 3
# SAD = 4
BEEP = 5


class Buzzer(BasePinThread):
    """Buzzer hardware abstraction.

    A buzzer is defined in config as:

      [pins]
      name = Buzzer:1

    where 1 is the active-high output pin.  This only works with buzzers that
    sound when driven with DC.  If you need to output a square wave, investigate
    gpio_tonal_buzzer.py in the source history, and making that work with pigpio
    for more stable frequency.
    """

    def __init__(self, event_queue, config_name, output_pin):
        super(Buzzer, self).__init__(event_queue, config_name, None, int(output_pin))
        self.set_queue = queue.Queue()

        GPIO.output(self.output_pin, False)

    def run_inner(self, block=True):
        item = self.set_queue.get(block=block)
        next_mode = item[0]
        if next_mode == OFF:
            GPIO.output(self.output_pin, False)
        elif next_mode == ON:
            GPIO.output(self.output_pin, True)
        elif next_mode in (BEEP, BEEPING):
            # As-is, this provides a logic HIGH to make a 4KHz sound on PK-12N40PQ;
            print("Beeping")
            while True:
                if not self.set_queue.empty():
                    print("Done beeping")
                    break
                GPIO.output(self.output_pin, True)
                time.sleep(item[1])
                GPIO.output(self.output_pin, False)
                time.sleep(item[2])
                if next_mode == BEEP:
                    break
                print("...more beep")
        else:
            print("Error", next_mode)

    def _clear(self):
        # This looks like a busy-wait, but isn't because of the exception.
        try:
            while True:
                self.set_queue.get(block=False)
        except queue.Empty:
            pass

    def beepbeep(self, on_time=0.3, off_time=0.3):
        # rename to keep_beeping
        self._clear()
        self.set_queue.put((BEEPING, on_time, off_time))

    def beep(self, on_time=0.3, off_time=0.3):
        self._clear()
        self.set_queue.put((BEEP, on_time, off_time))

    def off(self, clear=True):
        if clear:
            self._clear()
        self.set_queue.put((OFF,))

    def on(self, clear=True):
        if clear:
            self._clear()
        self.set_queue.put((ON,))
