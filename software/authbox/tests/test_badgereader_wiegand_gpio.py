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

"""Tests for authbox.badgereader_wiegand_gpio"""

import threading
import time
import unittest

import authbox.badgereader_wiegand_gpio
from authbox import fake_gpio_for_testing
from authbox.compat import queue
from RPi import GPIO


class BadgereaderWiegandGPIOTest(unittest.TestCase):
    def setUp(self):
        self.fake = fake_gpio_for_testing.FakeGPIO()
        self.q = queue.Queue()
        self.b = authbox.badgereader_wiegand_gpio.WiegandGPIOReader(
            self.q, "b", "0", "1", on_scan=self.on_scan,
        )

    def on_scan(self, badge_number):
        pass

    def test_simple_scan(self):
        self.fake.press(1, GPIO.FALLING)
        self.fake.press(0, GPIO.FALLING)
        self.b.run_inner()
        self.assertEqual(self.q.get(block=False), (self.on_scan, "10"))

    def test_blocks_until_scan(self):
        def add_bits_later():
            time.sleep(0.2)
            self.fake.press(1, GPIO.FALLING)
            self.fake.press(0, GPIO.FALLING)

        t = threading.Thread(target=add_bits_later)
        t.start()
        self.b.run_inner()
        self.assertEqual(self.q.get(block=False), (self.on_scan, "10"))

    def test_limited_queue_size(self):
        for i in range(500):
            self.fake.press(0, GPIO.FALLING)
        self.b.run_inner()
        self.assertEqual(self.q.get(block=False), (self.on_scan, "0" * 100))
        # Make sure that state is reset.
        self.assertTrue(self.b.bitqueue.empty())
