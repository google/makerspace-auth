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

import tempfile
import time
import unittest

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

import authbox.api
import authbox.badgereader_hid_keystroking
import two_button
from authbox import fake_gpio_for_testing  # noqa: F401

SAMPLE_CONFIG = b"""
[pins]
on_button=Button:11:38
off_button=Button:16:37
enable_output=Relay:ActiveHigh:29
badge_reader=HIDKeystrokingReader:badge_scanner
buzzer=Buzzer:35
[auth]
duration=20s
warning=10s
extend=20s

command = touch enabled
extend_command = touch enabled
deauth_command = rm -f enabled
"""

SAMPLE_CONFIG_DELAYED = b"""
[pins]
on_button=Button:11:38
off_button=Button:16:37
enable_output=Relay:ActiveHigh:29, Relay:ActiveHigh:31
output_off_delay_seconds = [ Relay:ActiveHigh:29 = 0, Relay:ActiveHigh:31 = 1 ]
badge_reader=HIDKeystrokingReader:badge_scanner
buzzer=Buzzer:35
[auth]
duration=20s
warning=10s
extend=20s

command = touch enabled
extend_command = touch enabled
deauth_command = rm -f enabled
"""


# This is the fastest way to ensure that basic logic is right, but it does not
# test the use of BaseDispatcher.event_queue or the way callbacks happen on the
# same thread serialized.
class SimpleDispatcherTest(unittest.TestCase):
    def setUp(self):
        Device.pin_factory = MockFactory()

        try:
            from authbox import fake_evdev_device_for_testing
        except ModuleNotFoundError:
            self.fail("Test requires evdev, but evdev is not available")
        authbox.badgereader_hid_keystroking.evdev.list_devices = (
            fake_evdev_device_for_testing.list_devices
        )
        authbox.badgereader_hid_keystroking.evdev.InputDevice = (
            fake_evdev_device_for_testing.InputDevice
        )

        with tempfile.NamedTemporaryFile() as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            config = authbox.config.Config(f.name)

        self.dispatcher = two_button.Dispatcher(config)

    def is_relay_on(self):
        relay = getattr(self.dispatcher, "enable_output")
        return relay.gpio_relay.value

    def test_auth_flow(self):
        # Out of the box, relay should be off
        self.assertFalse(self.dispatcher.authorized)
        self.assertFalse(self.is_relay_on())
        # Badge scan sets authorized flag, but doesn't enable relay until button
        # press.
        self.dispatcher.badge_scan("1234")
        self.assertTrue(self.dispatcher.authorized)
        self.assertFalse(self.is_relay_on())
        # "On" button pressed
        self.dispatcher.on_button_down(None)
        self.assertTrue(self.dispatcher.authorized)
        self.assertTrue(self.is_relay_on())
        # "Off" button pressed
        self.dispatcher.abort(None)
        self.assertFalse(self.dispatcher.authorized)
        self.assertFalse(self.is_relay_on())


class DelayedOffTest(unittest.TestCase):
    def setUp(self):
        Device.pin_factory = MockFactory()

        try:
            from authbox import fake_evdev_device_for_testing
        except ModuleNotFoundError:
            self.fail("Test requires evdev, but evdev is not available")
        authbox.badgereader_hid_keystroking.evdev.list_devices = (
            fake_evdev_device_for_testing.list_devices
        )
        authbox.badgereader_hid_keystroking.evdev.InputDevice = (
            fake_evdev_device_for_testing.InputDevice
        )

        with tempfile.NamedTemporaryFile() as f:
            f.write(SAMPLE_CONFIG_DELAYED)
            f.flush()
            config = authbox.config.Config(f.name)

        self.dispatcher = two_button.Dispatcher(config)
        for t in self.dispatcher.threads:
            if t.__class__.__name__ == "Timer":
                t.start()

    def _process_events(self):
        while not self.dispatcher.event_queue.empty():
            item = self.dispatcher.event_queue.get_nowait()
            if item is authbox.api.SHUTDOWN_SENTINEL:
                break
            func, args = item[0], item[1:]
            func(*args)

    def is_relay_on(self, index_or_name_or_obj):
        if isinstance(index_or_name_or_obj, int):
            obj = self.dispatcher.outputs[index_or_name_or_obj][0]
        elif isinstance(index_or_name_or_obj, str):
            obj = getattr(self.dispatcher, index_or_name_or_obj)
        else:
            obj = index_or_name_or_obj

        if hasattr(obj, "gpio_relay"):
            return obj.gpio_relay.value
        elif hasattr(obj, "objs"):
            return [r.gpio_relay.value for r in obj.objs]
        else:
            # It might be a mock object or something else
            return obj.is_on if hasattr(obj, "is_on") else False  # Fallback

    def test_delayed_off(self):
        # Out of the box, relay should be off
        self.assertFalse(self.dispatcher.authorized)

        self.assertFalse(self.is_relay_on(0))
        self.assertFalse(self.is_relay_on(1))

        # Badge scan sets authorized flag
        self.dispatcher.badge_scan("1234")
        self.assertTrue(self.dispatcher.authorized)

        # "On" button pressed
        self.dispatcher.on_button_down(None)
        self.assertTrue(self.dispatcher.authorized)
        self.assertTrue(self.is_relay_on(0))
        self.assertTrue(self.is_relay_on(1))

        # "Off" button pressed
        self.dispatcher.abort(None)
        # The dispatcher state should be not authorized
        self.assertFalse(self.dispatcher.authorized)
        # Main output (0) should be off immediately
        self.assertFalse(self.is_relay_on(0))
        # Delayed output (1) should be ON STILL
        self.assertTrue(self.is_relay_on(1))

        # Wait for delay (1s) + buffer
        time.sleep(1.5)
        self._process_events()

        # Delayed output should be OFF
        self.assertFalse(self.is_relay_on(1))

    def test_cancel_delayed_off(self):
        # Badge scan and turn on
        self.dispatcher.badge_scan("1234")
        self.dispatcher.on_button_down(None)
        self.assertTrue(self.is_relay_on(0))
        self.assertTrue(self.is_relay_on(1))

        # Abort
        self.dispatcher.abort(None)
        self.assertFalse(self.is_relay_on(0))
        self.assertTrue(self.is_relay_on(1))

        # Wait 0.5s, then turn back on
        time.sleep(0.5)
        self.dispatcher.on_button_down(None)  # Resume!
        self.assertTrue(self.dispatcher.authorized)
        self.assertTrue(self.is_relay_on(0))
        self.assertTrue(self.is_relay_on(1))

        # Wait for the original delay (1s) to show it was cancelled
        time.sleep(1.5)
        self._process_events()

        # Should STILL be on!
        self.assertTrue(self.is_relay_on(0))
        self.assertTrue(self.is_relay_on(1))
