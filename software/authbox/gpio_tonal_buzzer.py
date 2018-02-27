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

import Queue
import time

from authbox.api import BasePinThread, GPIO

OFF = 0
ON = 1
BEEPING = 2
HAPPY = 3
SAD = 4
BEEP = 5


# This code DOES NOT yet WORK.  Rough roadmap is:
# 1. use pigpio to get good tones
# 2. add a small driver circuit on an external board like
#    http://web.archive.org/web/20150102021027/http://www.murata.com:80/support/faqs/products/sound/sounder/char/0001
# 3. add API for different tones past happy and sad (are those even universal?)
#    and make sure this also supports the API from regular gpio_buzzer
class TonalBuzzer(BasePinThread):
  def __init__(self, event_queue, config_name, output_pin):
    super(Buzzer, self).__init__(event_queue, config_name, None, int(output_pin))
    self.set_queue = Queue.Queue(None)

    GPIO.output(self.output_pin, False)

  def run_inner(self):
    next_mode = self.set_queue.get(block=True)
    if next_mode == OFF:
      GPIO.output(self.output_pin, False)
    elif next_mode == ON:
      GPIO.output(self.output_pin, True)
    elif next_mode in (BEEP, BEEPING):
      # TODO Support both types of piezo buzzer/transducer.
      # As-is, this provides a logic HIGH to make a 4KHz sound on PK-12N40PQ;
      # newer prototypes include one that requires the Pi to make a 4KHz
      # square wave, which should use pigpio instead of RPi.GPIO.
      print "Beeping"
      while True:
        if not self.set_queue.empty():
          print "Done beeping"
          break
        GPIO.output(self.output_pin, True)
        time.sleep(0.3)
        GPIO.output(self.output_pin, False)
        time.sleep(0.3)
        if next_mode == BEEP:
	  break
        print "...more beep"
    elif next_mode == HAPPY:
      print "Happy"
      # TODO use pigpio
      p = GPIO.PWM(self.output_pin, 440)
      if p is None:
        # FakeRPi.GPIO does this
        return
      p.start(50)
      time.sleep(0.5)
      p.ChangeFrequency(440 * 1.25)
      time.sleep(0.5)
      p.ChangeFrequency(440 * 1.5)
      time.sleep(0.5)
      p.stop()  # TODO make sure it ends up off
    elif next_mode == SAD:
      print "Sad"
      # TODO use pigpio
      p = GPIO.PWM(self.output_pin, 440 * 1.2)
      if p is None:
        # FakeRPi.GPIO does this
        return
      p.start(50)
      time.sleep(0.5)
      p.ChangeFrequency(440 * 0.75)
      time.sleep(0.5)
      p.stop()  # TODO make sure it ends up off
    else:
      print "Error", next_mode

  def _clear(self):
    # This looks like a busy-wait, but isn't because of the exception.
    try:
      while True:
        self.set_queue.get(block=False)
    except Queue.Empty:
      pass

  def happy_noise(self):
    self._clear()
    self.set_queue.put(HAPPY)

  def sad_noise(self):
    self._clear()
    self.set_queue.put(SAD)

  def beepbeep(self):
    self._clear()
    self.set_queue.put(BEEPING)

  def beep(self):
    self._clear()
    self.set_queue.put(BEEP)

  def off(self):
    self._clear()
    self.set_queue.put(OFF)

  def on(self):
    self._clear()
    self.set_queue.put(ON)
