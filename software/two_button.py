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

"""Example using two buttons for "on" and "off" once badged.

"""

from authbox.api import BaseDispatcher, Timer

class Dispatcher(BaseDispatcher):
  def __init__(self, config):
    super(Dispatcher, self).__init__(config)

    self.authorized = False
    self.load_config_object('on_button', down=self.on_button_down)
    self.load_config_object('off_button', down=self.abort)
    self.load_config_object('badge_reader', scan=self.badge_scan)
    self.load_config_object('enable_output')
    self.load_config_object('buzzer')
    self.warning_timer = Timer(self.warning)
    self.expire_timer = Timer(self.abort)
    self.expecting_press_timer = Timer(self.abort)

  def badge_scan(self, badge_id):
    # .get does basic interpolation like {foo}, but not {} and {5}
    # .format does the rest
    command = self.config.get('auth', 'command').format(badge_id)
    # TODO this really ought to be a list to avoid the shell,
    # could just call shlex?
    # TODO timeout
    # TODO test with missing command
    rc = subprocess.call(command)
    if rc == 0:
      self.buzzer.happy_noise()
      self.authorized = True
      self.expecting_press_timer.set(30)
      self.on_button.blink()
    else:
      self.buzzer.sad_noise()

  def on_button_down(self, unused_source):
    if not self.authorized:
      self.buzzer.sad_noise()
      return
    self.expecting_press_timer.cancel()
    self.on_button.off()
    self.enable_output.set()
    # Duration is from the time you press 'on' first
    self.warning_timer.set(self.config.get_int_seconds('auth', 'duration', '5m') -
                           self.config.get_int_seconds('auth', 'warning', '10s'))
    self.expire_timer.set(self.config.get_int_seconds('auth', 'duration', '5m'))

  def abort(self, unused_source):
    self.authorized = False
    self.warning_timer.cancel()
    self.expecting_press_timer.cancel()
    self.on_button.off()

  def warning(self, unused_source):
    self.buzzer.beepbeep()


def main():
  config = file_config.load('~/.authboxrc')
  Dispatcher().run_loop(config)

if __name__ == '__main__':
  main()
