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

"""Tests for authbox.gpio_relay"""

import unittest

import authbox.gpio_relay
from authbox import fake_gpio_for_testing
from authbox.compat import queue

class TestRelay(authbox.gpio_relay.Relay):
    def assert_states(self, expected_states):
        assert len(self.gpio_relay.pin.states) == len(expected_states)
        self.gpio_relay.pin.assert_states(expected_states)
    def clear_states(self):
      self.gpio_relay.pin.clear_states()

class RelayTest(unittest.TestCase):
    def setUp(self):
        self.time = fake_gpio_for_testing.FakeTime()
        self.q = queue.Queue()

    def test_activehigh(self):
        self.b = TestRelay(self.q, "b", "ActiveHigh", "15")
        self.b.clear_states()
        self.time.sleep(5)
        self.b.on()
        self.b.assert_states([False, True])

    def test_activelow(self):
        self.b = TestRelay(self.q, "b", "ActiveLow", "15")
        self.b.clear_states()
        self.time.sleep(5)
        self.b.on()
        self.b.assert_states([True, False])
