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

"""Tests for authbox.gpio_button"""

import sys
import time
import unittest
from functools import partial

import authbox.gpio_button
from authbox import fake_gpio_for_testing
from authbox.compat import queue
from RPi import GPIO


class ImpatientQueue(queue.Queue):
    def __init__(self, fake_time):
        super().__init__()
        self.time = fake_time

    def get(self, block, timeout):
        if self.empty():
            print("Advancing", timeout)
            self.time.sleep(timeout)
            raise queue.Empty
        return super().get(block=block, timeout=timeout)


class BlinkTest(unittest.TestCase):
    def setUp(self):
        self.time = fake_gpio_for_testing.FakeTime()
        self.fake = fake_gpio_for_testing.FakeGPIO(self.time)
        self.q = queue.Queue()
        self.b = authbox.gpio_button.Button(
            self.q,
            "b",
            "1",
            "2",
            on_down=self.on_down,
            blink_command_queue_cls=partial(ImpatientQueue, self.time),
        )

    def on_down(self):
        pass

    def test_on(self):
        self.b.on()
        self.b.run_inner()
        # 2 is output
        self.fake.compare_log([(0, 2, True)])
        # 1 is input
        self.assertEqual(GPIO.FALLING, self.fake.events[1][0])
        self.fake.events[1][1](None)
        self.assertEqual(self.q.get(block=False), (self.on_down, self.b))

    def test_blinking_thread(self):
        self.b.blink()
        for i in range(4):
            self.b.run_inner()
        self.fake.compare_log(
            [(0.0, 2, True), (0.5, 2, False), (1.0, 2, True), (1.5, 2, False)]
        )
