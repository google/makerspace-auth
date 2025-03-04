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

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

import authbox.gpio_button
from authbox import fake_gpio_for_testing
from authbox.compat import queue

class TestButton(authbox.gpio_button.Button):
    def drive_high(self):
        self.gpio_button.pin.drive_high()

    def clear_states(self):
        self.gpio_button.pin.clear_states()
        self.gpio_led.pin.clear_states()

    def assert_button_states(self, expected_states):
        assert len(self.gpio_button.pin.states) == len(expected_states) 
        self.gpio_button.pin.assert_states(expected_states)

    def assert_led_states(self, expected_states):
        assert len(self.gpio_led.pin.states) == len(expected_states)
        self.gpio_led.pin.assert_states(expected_states)

    def close(self):
        self.gpio_button.close()
        self.gpio_led.close()

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
        Device.pin_factory = MockFactory()
        self.time = fake_gpio_for_testing.FakeTime()
        # self.fake = fake_gpio_for_testing.FakeGPIO(self.time)
        self.q = queue.Queue()
        self.b = TestButton(
            self.q,
            "b",
            "15",
            "40",
            on_down=self.on_down,
            blink_command_queue_cls=partial(ImpatientQueue, self.time),
        )

    def tearDown(self):
      self.b.close()

    def on_down(self):
        pass

    def test_on(self):
        # Verify pins are correctly configured
        self.assertEqual('input', self.b.gpio_button.pin._function)
        self.assertEqual('output', self.b.gpio_led.pin._function)

        self.b.drive_high()
        self.b.run_inner()

        # Assert that button states went from off to on
        self.assertTrue(self.b.is_pressed)
        self.b.assert_button_states([False, True])

    def test_blinking_thread(self):
        self.b.blink()
        for i in range(8):
            self.b.run_inner()

        # Number of on/off transitions corresponds to number of run_inner() calls
        self.b.assert_led_states([False, True, False, True, False, True, False, True, False])

    def test_finite_blink_count_from_off(self):
        self.b.off()
        self.b.run_inner()
        self.time.sleep(10)

        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Has only 2 "on" transitions even after additional run_inner() calls
        self.b.assert_led_states([False, True, False, True, False])

    def test_finite_blink_count_from_on(self):
        self.b.on()
        self.b.run_inner()
        self.time.sleep(10)

        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Has only 2 "off" transitions even after additional run_inner() calls
        self.b.assert_led_states([False, True, False, True, False, True])

    def test_steady_state_cancels_blink(self):
        self.b.blink()
        for i in range(2):
            self.b.run_inner()

        # Transitions after 2 cycles of indefinite blinking
        self.b.assert_led_states([False, True, False])

        # Changing steady state should cancel blink
        self.b.on()
        for i in range(8):
            self.b.run_inner()

        # No more blink transitions even after additional run_inner() calls
        self.b.assert_led_states([False, True, False, True])

    def test_overlapping_blink_counts(self):
        # Begin with light in the "on" steady state
        self.b.on()
        self.b.run_inner()
        self.time.sleep(10)

        # Begin first finite blink cycle
        self.b.blink()
        self.b.run_inner()

        # Light is currently "off" and in the middle of the blink cycle
        self.b.assert_led_states([False, True, False])

        # New blink cycle starts while light still "off" from the first blink cycle
        self.time.sleep(0.1)
        self.b.blink(count=2)
        for i in range(8):
            self.b.run_inner()

        # Second blink cycle count overrides the first. The final blink transition
        # won't be user visible because it's the same "on" state as the initial
        # steady state to which we return.
        self.b.assert_led_states(
            [   
                False, # Startup off state      
                True,  # Initial steady state
                False, # First blink cycle starts
                True,  # Second blink cycle starts
                False,
                True,  # Second blink cycle ends after 4 cycles
            ]
        )
