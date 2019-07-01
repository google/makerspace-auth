#!/usr/bin/python
#
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

"""Example to test all the buttons.

"""
from __future__ import print_function

import sys
import time

from authbox.api import BaseDispatcher
from authbox.config import Config
from authbox.timer import Timer

DEVNULL = open('/dev/null', 'r+')

class Dispatcher(BaseDispatcher):
  def __init__(self, config):
    super(Dispatcher, self).__init__(config)

    for i in range(1, 6+1):
      self.load_config_object('j%d' % i, on_down=self.on_button_down)

    self.load_config_object('buzzer')
    self.load_config_object('relays')
    # This may be a MultiProxy, which makes this easier.
    self.relays.on()
    self.relay_value = True

    # Run fans for 10 seconds on startup
    self.relay_timer = Timer(self.event_queue, 'relay_timer', self.toggle_relays)
    self.relay_toggle_interval = 10
    self.relay_timer.set(self.relay_toggle_interval)
    self.threads.extend([self.relay_timer])

  def on_button_down(self, source):
    print("Button down", source)
    self.buzzer.beep()

    source.on()
    time.sleep(0.3)
    source.off()

  def toggle_relays(self, source):
    print("Toggle relay", self.relay_value)
    if self.relay_value:
      self.relays.off()
      self.relay_value = False
    else:
      self.relays.on()
      self.relay_value = True
    self.relay_timer.set(self.relay_toggle_interval)


def main(args):
  if not args:
    config_filename = 'qa.ini'
  else:
    config_filename = args[0]

  config = Config(config_filename)
  Dispatcher(config).run_loop()

if __name__ == '__main__':
  main(sys.argv[1:])
