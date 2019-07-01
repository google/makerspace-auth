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

"""Tests for two_button.py"""

import sys
import unittest
import tempfile
import threading
import time

import two_button

import authbox.api
import authbox.badgereader_hid_keystroking
from authbox import fake_gpio_for_testing
from authbox import fake_evdev_device_for_testing
# Assumed to be the fake one, by authbox/__init__.py magic.
from RPi import GPIO

SAMPLE_CONFIG = b'''
[pins]
on_button=Button:1:2
off_button=Button:3:4
enable_output=Relay:ActiveHigh:5
badge_reader=HIDKeystrokingReader:badge_scanner
buzzer=Buzzer:9
[auth]
duration=20s
warning=10s
extend=20s

command = touch enabled
extend_command = touch enabled
deauth_command = rm -f enabled
'''

# This is the fastest way to ensure that basic logic is right, but it does not
# test the use of BaseDispatcher.event_queue or the way callbacks happen on the
# same thread serialized.
class SimpleDispatcherTest(unittest.TestCase):
  def setUp(self):
    authbox.badgereader_hid_keystroking.evdev.list_devices = fake_evdev_device_for_testing.list_devices
    authbox.badgereader_hid_keystroking.evdev.InputDevice = fake_evdev_device_for_testing.InputDevice
    self.gpio = fake_gpio_for_testing.FakeGPIO()

    with tempfile.NamedTemporaryFile() as f:
      f.write(SAMPLE_CONFIG)
      f.flush()
      config = authbox.config.Config(f.name)

    self.dispatcher = two_button.Dispatcher(config)

  def test_auth_flow(self):
    # Out of the box, relay should be off
    self.assertFalse(self.dispatcher.authorized)
    self.assertFalse(GPIO.input(5))
    # Badge scan sets authorized flag, but doesn't enable relay until button
    # press.
    self.dispatcher.badge_scan('1234')
    self.assertTrue(self.dispatcher.authorized)
    self.assertFalse(GPIO.input(5))
    # "On" button pressed
    self.dispatcher.on_button_down(None)
    self.assertTrue(self.dispatcher.authorized)
    self.assertTrue(GPIO.input(5))
    # "Off" button pressed
    self.dispatcher.abort(None)
    self.assertFalse(self.dispatcher.authorized)
    self.assertFalse(GPIO.input(5))
