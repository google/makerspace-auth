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

"""Test helper that logs instead of altering pin states."""

from __future__ import print_function

import time

from RPi import GPIO


def _log_match(a, b):
    return abs(a[0] - b[0]) < 0.1 and a[1] == b[1] and a[2] == b[2]


class FakeGPIO(object):
    """Fake for the RPi.GPIO module (parts of it)."""

    def __init__(self, fake_time=None):
        self.pin_states = [0] * 10
        self.events = {}
        self.time = fake_time or time

        self.t_zero = self.time.time()
        self.log = []

        GPIO.output = self.output
        GPIO.input = self.input
        GPIO.add_event_detect = self.add_event_detect

    def output(self, n, v):
        self.pin_states[n] = v
        self.log.append((self.time.time() - self.t_zero, n, bool(v)))

    def input(self, n):
        return self.pin_states[n]

    def add_event_detect(self, n, edge, callback=None, bouncetime=None):
        # TODO only supports one callback
        self.events[n] = (edge, callback, bouncetime)

    def press(self, n, edge):
        # TODO support bidirectional edge
        if self.events[n] and self.events[n][0] == edge:
            self.events[n][1](n)

    def compare_log(self, expected_log):
        """Check that the correct log entries exist in the right order.

        Raises:
          Exception: if that is not true.
        """
        # Entries must appear in the correct order, and only count for one.
        print("Expecting", expected_log)
        print("Actual", self.log)
        expected_count = len(expected_log)
        i = 0

        # Consume entries out of expected_log only if they exist with close enough
        # timestamps and in the proper order.  If any are leftover at the end, the
        # test fails.
        while expected_log and i < len(self.log):
            if _log_match(expected_log[0], self.log[i]):
                expected_log.pop(0)
            i += 1

        if expected_log:
            raise Exception("Missing", expected_log)
        if len(self.log) > expected_count:
            raise Exception("Unexpected", self.log)


class FakeTime(object):
    """Fake for the module 'time' so tests run faster."""

    def __init__(self):
        self.t = 0

    def time(self):
        return self.t

    def sleep(self, x):
        self.t += x


# TODO: Queue patcher that also advances time
