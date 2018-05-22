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

"""Tests for authbox.gpio_switch_three"""

import sys
import unittest
import Queue

import authbox.gpio_switch_three
from authbox import fake_gpio_for_testing
from RPi import GPIO


class ThreePosSwitchTest(unittest.TestCase):
  def setUp(self):
    self.time = fake_gpio_for_testing.FakeTime()
    authbox.gpio_switch_three.time = self.time
    self.fake = fake_gpio_for_testing.FakeGPIO(self.time)
    self.q = Queue.Queue()
    self.s = authbox.gpio_switch_three.ThreePosSwitch(
        self.q, 's', '1', '2', '3', '4', '5', on_change=lambda x: None)

  def get_queue(self):
    try:
      while True:
        yield self.q.get(block=False)[1]
    except Queue.Empty:
      pass

  def test_colors(self):
    # "Left" position, should be green
    self.fake.output(1, 1)
    self.fake.output(2, 0)
    self.s.run_inner()
    self.assertEqual([self.s], list(self.get_queue()))
    self.assertEqual(0, self.s.state)
    self.assertEqual([1, 0, 0], [self.fake.input(i) for i in [3, 4, 5]])

    # Both pulled high, middle position
    self.fake.output(1, 1)
    self.fake.output(2, 1)
    self.s.run_inner()
    self.assertEqual([self.s], list(self.get_queue()))
    self.assertEqual(1, self.s.state)
    self.assertEqual([0, 1, 0], [self.fake.input(i) for i in [3, 4, 5]])

    # "Right" position, should be red
    self.fake.output(1, 0)
    self.fake.output(2, 1)
    self.s.run_inner()
    self.assertEqual([self.s], list(self.get_queue()))
    self.assertEqual(2, self.s.state)
    self.assertEqual([0, 0, 1], [self.fake.input(i) for i in [3, 4, 5]])

    # No change, run_inner does not reissue callback
    self.s.run_inner()
    self.assertEqual([], list(self.get_queue()))
    self.assertEqual(2, self.s.state)
    self.assertEqual([0, 0, 1], [self.fake.input(i) for i in [3, 4, 5]])
