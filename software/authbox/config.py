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
TIME_RE = re.compile(r'([\d.]+)([smhd])')
SIMPLE_FLOAT_RE = re.compile(r'^[\d.]+$')

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
  """A wrapper around ConfigParser."""
  def __init__(self, filename):
    """Initialize.

    Args:
      filenames: may be a string or sequence.  If None, start with an empty
          config.
    """
    self._config = ConfigParser.RawConfigParser()
    if filename is not None:
      if isinstance(filename, basestring):
        filenames = [filename]
      else:
        filenames = filename

      for f in filenames:
        # Read one at a time for better error messages.
        if not self._config.read([os.path.expanduser(f)]):
          # N.b. if config existed but was invalid, we'd get
          # MissingSectionHeaderError or so.
          raise Exception('Nonexistent config', f)

  def get(self, section, option, **kwargs):
    """Get one config value.

    Args:
      section: The section name
      option: The key name
      default: Return this value if the option (or whole section) is missing.
          Must be specified as kwarg, so that None can be handled easily.

    Returns:
      The value from config (with {params} looked up), or default.

    Raises:
      NoOptionError, NoSectionError: If default is not provided.
    """
    if 'default' in kwargs and not self._config.has_option(section, option):
      return kwargs['default']
    value = self._config.get(section, option)
    # Just an optimization
    if '{' in value:
      return recursive_config_lookup(value, self._config, section)
    else:
      return value

  @classmethod
  def parse_time(cls, time_string, bare_number_suffix='s'):
    """Parse a time string.

    Allowable suffixes include:

      s: seconds
      m: minutes
      h: hours
      d: days

    and can be mixed, e.g. 1m30s.

    Returns the value in seconds, as an int if possible, otherwise a float.
    """
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }
    if not time_string:
      raise Exception('Empty time_string')
    elif isinstance(time_string, (int, float)):
      return time_string * units[bare_number_suffix]
    elif time_string.isdigit():
      # ints
      return int(time_string) * units[bare_number_suffix]
    elif SIMPLE_FLOAT_RE.match(time_string):
      # simple floats like '1.1', not '1e5'
      # invalid ones like '1.1.1' raise an exception
      return float(time_string) * units[bare_number_suffix]
    else:
      # Ensure that everything is matched.
      if TIME_RE.sub('', time_string) != '':
        raise Exception('Unknown time_string format', time_string)
      total = 0
      for m in TIME_RE.finditer(time_string):
        try:
          number = int(m.group(1))
        except ValueError:
          number = float(m.group(1))
        unit_multiplier = units[m.group(2)]
        total += unit_multiplier * number
      return total

  def get_int_seconds(self, section, option, default):
    return self.parse_time(self.get(section, option, default=default))
