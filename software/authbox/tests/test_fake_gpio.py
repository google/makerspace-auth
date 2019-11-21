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

"""Tests for authbox.fake_gpio_for_testing"""

import time
import unittest

from authbox import fake_gpio_for_testing


class FakeGPIOTest(unittest.TestCase):
    def test_compare_log_simple(self):
        fake_time = fake_gpio_for_testing.FakeTime()
        gpio = fake_gpio_for_testing.FakeGPIO(fake_time)
        gpio.output(1, True)
        fake_time.sleep(1.5)
        gpio.output(1, False)
        gpio.compare_log([(0, 1, True), (1.5, 1, False)])
        # Timestamps are approximate (mainly for use with real time, instead of
        # fake_time)
        gpio.compare_log([(0, 1, True), (1.55, 1, False)])
        # Any of these are reasons for compare_log to fail
        # value
        self.assertRaises(Exception, gpio.compare_log, [(0, 1, True), (1.5, 1, True)])
        # time
        self.assertRaises(Exception, gpio.compare_log, [(0, 1, True), (2.0, 1, False)])
        # pin number
        self.assertRaises(Exception, gpio.compare_log, [(0, 1, True), (1.5, 2, False)])

    def test_compare_log_with_regular_time(self):
        gpio = fake_gpio_for_testing.FakeGPIO()
        gpio.output(1, True)
        time.sleep(0.001)
        gpio.output(1, False)
        # This is a much-truncated version of the above test, because I'm pretty
        # confident in it working right and this makes the tests much faster.
        gpio.compare_log([(0, 1, True), (0.001, 1, False)])
