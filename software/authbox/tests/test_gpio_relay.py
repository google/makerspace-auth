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


class RelayTest(unittest.TestCase):
    def setUp(self):
        self.time = fake_gpio_for_testing.FakeTime()
        self.fake = fake_gpio_for_testing.FakeGPIO(self.time)
        self.q = queue.Queue()

    def test_activehigh(self):
        self.b = authbox.gpio_relay.Relay(self.q, "b", "ActiveHigh", "1")
        self.time.sleep(5)
        self.b.on()
        self.fake.compare_log([(0, 1, False), (5, 1, True)])

    def test_activelow(self):
        self.b = authbox.gpio_relay.Relay(self.q, "b", "ActiveLow", "1")
        self.time.sleep(5)
        self.b.on()
        self.fake.compare_log([(0, 1, True), (5, 1, False)])
