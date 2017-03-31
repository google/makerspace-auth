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

"""Main API for Authbox

"""

import ConfigParser
import os.path
import Queue
import re
import threading

KNOWN_CLASSES = [
    'authbox.badgereader_hid_keystroking.HIDKeystrokingReader',
    'authbox.gpio_button.Button',
    'authbox.gpio_output.Relay',
    'authbox.timer.Timer',
]

# TODO: This is very simplistic, supporting no escapes or indirect lookups
TEMPLATE_RE = re.compile(r'{(\w+)}')

def recursive_config_lookup(value, section, stack=None):
  if stack is None:
    stack = []
  # Typically these are shallow, so this is efficient enough
  if value in stack:
    raise CycleError
  stack.append(value)

  def local_sub(match):
    return recursive_config_lookup(section[match.group(1)], section, stack)
  response = TEMPLATE_RE.sub(local_sub, value)
  stack.pop()
  return response

class CycleError(Exception):
  pass

class Config(object):
  # TODO more than one filename?
  def __init__(self, filename):
    self._config = ConfigParser.RawConfigParser()
    if filename is not None:
      if not self._config.read([os.path.expanduser(filename)]):
        # N.b. if config existed but was invalid, we'd get
        # MissingSectionHeaderError or so.
        raise Exception('Nonexistent config')

  def get(self, section, option):
    # Can raise NoOptionError, NoSectionError
    value = self._config.get(section, option)
    # Just an optimization
    if '{' in value:
      return recursive_config_lookup(value, self._config.items(section))
    else:
      return value

  @classmethod
  def parse_time(cls, time_string):
    # Returns seconds
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }
    if not time_string:
      raise Exception('Empty time_string')
    elif time_string.isdigit():
      # Fine, seconds?
      return int(time_string)
    elif time_string[-1] in units:
      try:
        number = int(time_string[:-1])
      except ValueError:
        number = float(time_string[:-1])
      unit_multiplier = units[time_string[-1]]
      return int(number * unit_multiplier)
    else:
      raise Exception('Unknown time_string format', time_string)


  def get_int_seconds(self, section, option, default):
    if self._config.has_option(section, option):
      return self.parse_time(self.get(section, option))
    else:
      return self.parse_time(default)

class BaseThing(threading.Thread):
  def __init__(self, event_queue, config_name):
    # TODO should they also have numeric ids?
    thread_name = "%s %s" % (self.__class__.__name__, name)
    super(BaseThing, self).__init__(name=thread_name)
    self.daemon = True

    self.event_queue = event_queue
    self.config_name = config_name

class BaseDispatcher(object):
  def __init__(self, config):
    self.config = config
    self.event_queue = Queue.Queue()  # unbounded

  def load_config_object(self, name, **kwargs):
    # N.b. args are from config, kwargs are passed from python
    options = self.config.get('pins', name).split(':')
    cls_name = options[0]
    for c in KNOWN_CLASSES:
      if c.endswith('.' + cls_name):
        cls = c
        break
    else:
      raise Exception('Unknown item', name)
    obj = cls(self.event_queue, *options[1:], **kwargs)
    setattr(self, name, obj)

  def run_loop(self):
    # Doesn't really support calling run_loop() more than once
    while True:
      item = self.event_queue.get()
      if item is SHUTDOWN_SENTINEL:
        break
      # These only happen here to serialize access regardless of what thread
      # handled it.
      func, args = item[0], item[1:]
      func(*args)

    # TODO kill threads, or ensure they were all daemon


SHUTDOWN_SENTINEL = object()

class NoMatchingDevice(Exception):
  pass
