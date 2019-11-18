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

"""Tests for authbox.timer"""

import unittest

import authbox.timer
from authbox import fake_gpio_for_testing
from authbox.compat import queue


class TimerTest(unittest.TestCase):
    def setUp(self):
        self.fake = fake_gpio_for_testing.FakeGPIO()
        self.q = queue.Queue()
        self.t = authbox.timer.Timer(self.q, "t", self.callback)

    def callback(self, config_name):
        pass

    def test_set_exception(self):
        self.t.set(1)
        with self.assertRaises(Exception):
            self.t.set(1)

    def test_set(self):
        self.t.set(0.001)
        self.t.run_inner()
        self.assertEqual(1, self.q.qsize())

    def test_cancel_drains_queue(self):
        self.t.set_queue.put(None)
        self.t.cancel()
        self.assertTrue(self.t.set_queue.empty())
