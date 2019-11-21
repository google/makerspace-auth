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

import unittest
from functools import partial

import authbox.gpio_button
from authbox import fake_gpio_for_testing
from authbox.compat import queue
from RPi import GPIO


class ImpatientQueue(queue.Queue):
    def __init__(self, fake_time):
        queue.Queue.__init__(self)
        self.time = fake_time

    def get(self, block, timeout):
        if self.empty():
            print("Advancing", timeout)
            self.time.sleep(timeout)
            raise queue.Empty
        return queue.Queue.get(self, block=block, timeout=timeout)


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
        for i in range(8):
            self.b.run_inner()

        # Number of on/off transitions corresponds to number of run_inner() calls
        self.fake.compare_log(
            [
                (0.0, 2, True),
                (0.5, 2, False),
                (1.0, 2, True),
                (1.5, 2, False),
                (2.0, 2, True),
                (2.5, 2, False),
                (3.0, 2, True),
                (3.5, 2, False),
            ]
        )

    def test_finite_blink_count_from_off(self):
        self.b.off()
        self.b.run_inner()
        self.time.sleep(10)

        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Has only 2 "on" transitions even after additional run_inner() calls
        self.fake.compare_log(
            [
                (0.0, 2, False),
                (10.0, 2, True),
                (10.5, 2, False),
                (11.0, 2, True),
                (11.5, 2, False),
            ]
        )

    def test_finite_blink_count_from_on(self):
        self.b.on()
        self.b.run_inner()
        self.time.sleep(10)

        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Has only 2 "off" transitions even after additional run_inner() calls
        self.fake.compare_log(
            [
                (0.0, 2, True),
                (10.0, 2, False),
                (10.5, 2, True),
                (11.0, 2, False),
                (11.5, 2, True),
            ]
        )

    def test_steady_state_cancels_blink(self):
        self.b.blink()
        for i in range(2):
            self.b.run_inner()

        # Transitions after 2 cycles of indefinite blinking
        self.fake.compare_log([(0.0, 2, True), (0.5, 2, False)])

        # Changing steady state should cancel blink
        self.b.on()
        for i in range(8):
            self.b.run_inner()

        # No more blink transitions even after additional run_inner() calls
        self.fake.compare_log([(0.0, 2, True), (0.5, 2, False), (0.5, 2, True)])

    def test_overlapping_blink_counts(self):
        # Begin with light in the "on" steady state
        self.b.on()
        self.b.run_inner()
        self.time.sleep(10)

        # Begin first finite blink cycle
        self.b.blink()
        self.b.run_inner()

        # Light is currently "off" and in the middle of the blink cycle
        self.fake.compare_log([(0.0, 2, True), (10.0, 2, False)])

        # New blink cycle starts while light still "off" from the first blink cycle
        self.time.sleep(0.1)
        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Second blink cycle count overrides the first. The final blink transition
        # won't be user visible because it's the same "on" state as the initial
        # steady state to which we return.
        self.fake.compare_log(
            [
                (0.0, 2, True),  # Initial steady state
                (10.0, 2, False),  # First blink cycle starts
                (10.1, 2, True),  # Second blink cycle starts
                (10.6, 2, False),
                (11.1, 2, True),
                (11.6, 2, True),  # Second blink cycle ends after 4 cycles
            ]
        )
