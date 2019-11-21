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

"""Tests for authbox.badgereader_hid_keystroking"""

import unittest

import authbox.badgereader_hid_keystroking
from authbox import fake_evdev_device_for_testing
from authbox.compat import queue


class BadgereaderTest(unittest.TestCase):
    def setUp(self):
        authbox.badgereader_hid_keystroking.evdev.list_devices = (
            fake_evdev_device_for_testing.list_devices
        )
        authbox.badgereader_hid_keystroking.evdev.InputDevice = (
            fake_evdev_device_for_testing.InputDevice
        )
        self.q = queue.Queue()
        self.badgereader = authbox.badgereader_hid_keystroking.HIDKeystrokingReader(
            self.q, "b", "badge_scanner", on_scan=self.record
        )
        self.lines = []

    def record(self, line):
        self.lines.append(line)

    def test_read_loop(self):
        self.badgereader.run_inner()
        item = self.q.get(block=False)
        self.assertEqual(2, len(item))
        self.assertEqual(self.record, item[0])
        self.assertEqual("8:8", item[1])
        self.assertRaises(queue.Empty, self.q.get, block=False)
