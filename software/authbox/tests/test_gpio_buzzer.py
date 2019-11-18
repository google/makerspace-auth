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

"""Tests for authbox.gpio_buzzer"""

import unittest

import authbox.gpio_buzzer
from authbox import fake_gpio_for_testing
from authbox.compat import queue


class BuzzerTest(unittest.TestCase):
    def setUp(self):
        self.time = fake_gpio_for_testing.FakeTime()
        self.fake = fake_gpio_for_testing.FakeGPIO(self.time)
        authbox.gpio_buzzer.time = self.time

        self.q = queue.Queue()
        self.b = authbox.gpio_buzzer.Buzzer(self.q, "b", "1")

    def test_on(self):
        self.time.sleep(2)
        self.b.on()
        self.b.run_inner(False)
        self.assertRaises(queue.Empty, self.b.run_inner, False)
        self.fake.compare_log([(0, 1, False), (2, 1, True)])

    def test_off(self):
        self.time.sleep(2)
        self.b.off()
        self.b.run_inner(False)
        self.assertRaises(queue.Empty, self.b.run_inner, False)
        self.fake.compare_log([(0, 1, False), (2, 1, False)])

    def test_beep(self):
        self.b.beep()
        self.b.run_inner(False)
        self.b.on()
        self.b.run_inner(False)
        self.assertRaises(queue.Empty, self.b.run_inner, False)
        self.fake.compare_log(
            [(0, 1, False), (0, 1, True), (0.3, 1, False), (0.6, 1, True)]
        )

    # BEEPING mode is not very testable, due to the infinite loop and empty
    # check.  We could put this in another thread, but that's a test for another
    # day...
    # def test_beeping(self):
    #  self.b.beepbeep()
    #  self.b.off(clear=False)  # Unusual, but avoids races in test.
    #  self.b.run_inner(False)
    #  # Queue is not empty.
    #  self.fake.compare_log([
    #      (0, 1, False), (0.3, 1, True), (0.6, 1, False)])
