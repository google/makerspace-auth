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

import evdev


def list_devices():
    yield "foo"
    yield "badge_scanner"


class InputDevice(object):
    """Behaves (slightly) like an evdev device for testing other code."""

    def __init__(self, name):
        self.name = name

    def grab(self):
        pass

    def read_loop(self):
        """Always yields events that should type '8:8<ENTER>'."""
        # TODO: Make this more easily customizable, and catch where it would hang
        # because there are no events [either reading the wrong device, or reading a
        # second time]
        if self.name == "badge_scanner":
            for ev in self.type_eight():
                yield ev
            for ev in self.type_colon():
                yield ev
            for ev in self.type_eight():
                yield ev
            for ev in self.type_enter():
                yield ev

    # These were all found by logging what evdev does on Ubuntu; the timestamps
    # have been replaced with zeroes to make this more readable since we currently
    # don't use them for anything.
    def type_eight(self):
        yield evdev.events.InputEvent(0, 0, 4, 4, 458789)
        yield evdev.events.InputEvent(0, 0, 1, 9, 1)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)
        yield evdev.events.InputEvent(0, 0, 4, 4, 458789)
        yield evdev.events.InputEvent(0, 0, 1, 9, 0)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)

    def type_colon(self):
        yield evdev.events.InputEvent(0, 0, 4, 4, 458977)
        yield evdev.events.InputEvent(0, 0, 1, 42, 1)
        yield evdev.events.InputEvent(0, 0, 4, 4, 458803)
        yield evdev.events.InputEvent(0, 0, 1, 39, 1)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)
        yield evdev.events.InputEvent(0, 0, 4, 4, 458977)
        yield evdev.events.InputEvent(0, 0, 1, 42, 0)
        yield evdev.events.InputEvent(0, 0, 4, 4, 458803)
        yield evdev.events.InputEvent(0, 0, 1, 39, 0)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)

    def type_enter(self):
        yield evdev.events.InputEvent(0, 0, 4, 4, 458792)
        yield evdev.events.InputEvent(0, 0, 1, 28, 1)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)
        yield evdev.events.InputEvent(0, 0, 4, 4, 458792)
        yield evdev.events.InputEvent(0, 0, 1, 28, 0)
        yield evdev.events.InputEvent(0, 0, 0, 0, 0)
