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

"""Tests for authbox.config"""

import unittest

import authbox.config


class ConfigTest(unittest.TestCase):
  def test_parse_time(self):
    cfg = authbox.config.Config
    # ints
    self.assertEquals(61, cfg.parse_time("61"))
    self.assertEquals(61, cfg.parse_time("61s"))
    self.assertEquals(3660, cfg.parse_time("61m"))
    self.assertEquals(7200, cfg.parse_time("2h"))
    self.assertEquals(86400, cfg.parse_time("1d"))

    # TODO: floats
    self.assertEquals(4320, cfg.parse_time("1.2h"))
    # TODO: "" raises
    # TODO: Unknown format raises


class OneSectionConfig(object):
  def __init__(self, contents):
    self.contents = contents
  def get(self, section_name, key):
    if section_name == 'section':
      return self.contents[key]


class RecursiveConfigParamLookupTest(unittest.TestCase):
  def test_simple(self):
    c = OneSectionConfig({'a': 'b'})
    self.assertEquals('abc', authbox.config.recursive_config_lookup('abc', c, 'section'))
    self.assertEquals('b', authbox.config.recursive_config_lookup('{a}', c, 'section'))
    self.assertRaises(KeyError, authbox.config.recursive_config_lookup, '{x}', c, 'section')

  def test_simple_left_alone(self):
    c = OneSectionConfig({'a': 'b'})
    self.assertEquals('{0} b', authbox.config.recursive_config_lookup('{0} {a}', c, 'section'))
    self.assertEquals('{} b', authbox.config.recursive_config_lookup('{} {a}', c, 'section'))

  def test_recursive(self):
    c = OneSectionConfig({'a': '{b}{b}', 'b': '{c}2', 'c': 'd',
                          'broken': '{b2}', 'b2': '{missing}'})
    self.assertEquals('d2d2', authbox.config.recursive_config_lookup('{a}', c, 'section'))
    self.assertRaises(KeyError, authbox.config.recursive_config_lookup, '{broken}', c, 'section')

  def test_recursive_fail(self):
    c = OneSectionConfig({'a': '{b}', 'b': '{a}'})
    self.assertRaises(authbox.config.CycleError, authbox.config.recursive_config_lookup, '{a}', c, 'section')
