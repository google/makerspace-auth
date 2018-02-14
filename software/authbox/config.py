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

"""Config API for Authbox.

"""
import re
import os.path
import ConfigParser


# TODO: This is very simplistic, supporting no escapes or indirect lookups
TEMPLATE_RE = re.compile(r'{((?!\d)\w+)}')


def recursive_config_lookup(value, config, section, stack=None):
  """Looks up format references in ConfigParser objects.

  For the sample config:

      [s]
      k = v

  Args:
    value: The format string, e.g. passing '{k}' (and 's' for section) will return 'v'
    config: A ConfigParser object.
    section: The section in which values will be looked up.
    stack: Omit for client call; will be provided when recursing to check for
      infinite loops.
  Returns:
    A string with references replaced.
  """
  if stack is None:
    stack = []
  # Typically these are shallow, so this is efficient enough
  if value in stack:
    raise CycleError
  stack.append(value)

  def local_sub(match):
    return recursive_config_lookup(config.get(section, match.group(1)), config, section, stack)
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
        raise Exception('Nonexistent config', filename)

  def get(self, section, option):
    # Can raise NoOptionError, NoSectionError
    value = self._config.get(section, option)
    # Just an optimization
    if '{' in value:
      return recursive_config_lookup(value, self._config, section)
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
