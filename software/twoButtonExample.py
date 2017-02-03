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

"""An example implementation using two buttons:On/Extend and Off.

On a successful badge read, On/Extend will blink. If not pressed, the badge
value is wiped. If pressed, the connected device comes on. After a given span
of time, On/Extend will blink again (prompting to be extended) and ultimately
turn off the connected device and wipe the badge value. At any point, the
connected device can be powered off by pressing the Off button.
"""

import threading
import auth_lib
from RPi import GPIO


def unpress_button(button, evt):
  """Removes a button's press_event value and manually sets a threading event.

  Args:
    button: the button object to remove press_event from.
    evt: the threading.Event object to set.
  """
  button.press_event.clear()
  button.pressed = False
  evt.set()


def arbitrary():
  """Dummy function to instantiate thread/timer objects.

  """
  pass


def main():
  GPIO.setmode(GPIO.BOARD)
  evt = threading.Event()
  # the red button has a lock object passed to prevent multiple instances of a
  # blinking thread starting.
  blink_lock = threading.Lock()
  red = auth_lib.Button(12, 29, press_event=evt, lock=blink_lock)
  blue = auth_lib.Button(15, 31, press_event=evt)
  # configures power tail
  # uses the pins for light 5
  power_tail = auth_lib.PowerSwitch(37)
  # configures buzzer using default values
  # uses the pins for light 4
  notify_tone = auth_lib.Buzzer(35)
  # have to set up timers here to reference inside press event
  beep_timer = threading.Timer(30, arbitrary)
  shutoff_timer = threading.Timer(40, arbitrary)
  # creates a list of the timer objects to be used for cancelling the timers
  # must be re-declared when new timers are made with the new timer objects
  thread_list = [beep_timer, shutoff_timer]
  dev = auth_lib.get_scanner_device()
  badge = None
  while True:
    if badge is None:
      badge = auth_lib.read_input(dev)
    if badge:
      # sets button._blinking to True for blink_thread
      red.light_blink()
      if not power_tail.get_status():
        badge_timer = threading.Timer(5, blue.press, args=[blue.input_gpio])
        badge_timer.start()
      while True:
        blink_thread = threading.Thread(target=red.continuous_blink)
        blink_thread.start()
        if evt.wait():
          # checks if no buttons are pressed, regardless of number of instances
          # used to clear evt if it is manually set to prevent unintended loops
          if not auth_lib.check_all_buttons(auth_lib.Button.instances):
            evt.clear()
          if red.pressed and not blue.pressed:
            badge_timer.cancel()
            auth_lib.cancel_timers(thread_list)
            # unpresses red, but also sets evt manually so that blink_thread
            # can start
            beep_timer = threading.Timer(5, unpress_button, args=[red, evt])
            shutoff_timer = threading.Timer(10, blue.press,
                                            args=[blue.input_gpio])
            beep_timer.start()
            shutoff_timer.start()
            # new list with new timer objects
            thread_list = [beep_timer, shutoff_timer]
            red.light_on()
            power_tail.activate()
            notify_tone.happy_tune()
            break
          if blue.pressed:
            badge = auth_lib.power_off(badge_timer, red, badge, thread_list)
            power_tail.deactivate()
            notify_tone.sad_tune()
            break

      evt.clear()
      if red.pressed:
        evt.wait()
      elif blue.pressed:
        blue.unpress()

if __name__ == '__main__':
  main()
