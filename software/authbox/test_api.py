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

"""Tests for authbox.api"""

import unittest

import authbox.api

class ConfigTest(unittest.TestCase):
  def test_parse_time(self):
    cfg = authbox.api.Config
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

class RecursiveConfigParamLookupTest(unittest.TestCase):
  def test_simple(self):
    d = {'a': 'b'}
    self.assertEquals('abc', authbox.api.recursive_config_lookup('abc', d))
    self.assertEquals('b', authbox.api.recursive_config_lookup('{a}', d))
    self.assertRaises(KeyError, authbox.api.recursive_config_lookup, '{x}', d)

  def test_simple_left_alone(self):
    d = {'a': 'b'}
    self.assertEquals('{0} b', authbox.api.recursive_config_lookup('{0} {a}', d))

  def test_recursive(self):
    d = {'a': '{b}{b}', 'b': '{c}2', 'c': 'd', 'broken': '{b2}', 'b2': '{missing}'}
    self.assertEquals('d2d2', authbox.api.recursive_config_lookup('{a}', d))
    self.assertRaises(KeyError, authbox.api.recursive_config_lookup, '{broken}', d)

  def test_recursive_fail(self):
    d = {'a': '{b}', 'b': '{a}'}
    self.assertRaises(authbox.api.CycleError, authbox.api.recursive_config_lookup, '{a}', d)
