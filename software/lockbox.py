#!/usr/bin/python
#
# Copyright 2019-2020 Google Inc. All Rights Reserved.
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

"""Example using a badge swipe to pop open a cabinet lock.

"""
from __future__ import print_function

import atexit
import os
import sys
import subprocess
import shlex

from authbox.api import BaseDispatcher, GPIO
from authbox.config import Config
from authbox.timer import Timer

DEVNULL = open('/dev/null', 'r+')

class Dispatcher(BaseDispatcher):
  def __init__(self, config):
    super(Dispatcher, self).__init__(config)

    self.load_config_object('badge_reader', on_scan=self.badge_scan)
    self.load_config_object('output_relay')

    self.disable_timer = Timer(self.event_queue, 'disable_timer', self.disable)
    # Otherwise, start them manually!
    self.threads.extend([self.disable_timer])


  def _get_command_line(self, section, key, format_args):
    """Constructs a command line, safely.

    The value can contain {key}, {}, and {5} style interpolation:
      - {key} will be resolved in the config.get; those are considered safe and
        spaces will separate args.
      - {} works on each arg independently (probably not what you want).
      - {5} works fine.
    """
    value = self.config.get(section, key)
    pieces = shlex.split(value)
    return [p.format(*format_args) for p in pieces]

  def badge_scan(self, badge_id):
    # Malicious badge "numbers" that contain spaces require this extra work.
    command = self._get_command_line('auth', 'command', [badge_id])
    # TODO timeout
    # TODO test with missing command
    rc = subprocess.call(command)

    if rc == 0:
      self.disable_timer.cancel()
      self.output_relay.on()
      self.disable_timer.set(self.config.get_int_seconds('auth', 'duration', '1s'))

  def disable(self, source=None):
    self.output_relay.off()

def main(args):
  atexit.register(GPIO.cleanup)

  if not args:
    root = '~'
  else:
    root = args[0]

  config = Config(os.path.join(root, '.authboxrc'))
  Dispatcher(config).run_loop()

if __name__ == '__main__':
  main(sys.argv[1:])
