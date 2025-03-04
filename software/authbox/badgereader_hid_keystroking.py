# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Wrapper for pcProx RDR-6081AKU and compatible.
"""

from __future__ import print_function

import evdev

from authbox.api import BaseDerivedThread, NoMatchingDevice

class HIDKeystrokingReader(BaseDerivedThread):
    """Badge reader hardware abstraction.

    A badge reader is defined in config as:

      [pins]
      name = HIDKeystrokingReader:<Name>

    Where `<Name>` is the name evdev sees.  This appears to match a substring of
    /dev/input/by-id, for example if that directory contains
    `usb-RFIDeas_USB_Keyboard-event-kbd`, the evdev name is `RFIdeas USB
    Keyboard` with spaces.  You can confirm this in Python by executing:

    >>> import evdev
    >>> [evdev.InputDevice(d).name() for d in evdev.list_devices()]

    This has been tested on a couple of brands of reader and seems to be pretty generic.
    """

    scancodes = {
        # Scancode: ASCIICode
        0: None,
        1: "ESC",
        2: "1",
        3: "2",
        4: "3",
        5: "4",
        6: "5",
        7: "6",
        8: "7",
        9: "8",
        10: "9",
        11: "0",
        12: "-",
        13: "=",
        14: "BKSP",
        15: "TAB",
        16: "q",
        17: "w",
        18: "e",
        19: "r",
        20: "t",
        21: "y",
        22: "u",
        23: "i",
        24: "o",
        25: "p",
        26: "[",
        27: "]",
        28: "CRLF",
        29: "LCTRL",
        30: "a",
        31: "s",
        32: "d",
        33: "f",
        34: "g",
        35: "h",
        36: "j",
        37: "k",
        38: "l",
        39: ";",
        40: '"',
        41: "`",
        42: "LSHFT",
        43: "\\",
        44: "z",
        45: "x",
        46: "c",
        47: "v",
        48: "b",
        49: "n",
        50: "m",
        51: ",",
        52: ".",
        53: "/",
        54: "RSHFT",
        56: "LALT",
        100: "RALT",
    }

    # capscancodes are present to shift badge scans as necessary

    capscancodes = {
        0: None,
        1: "ESC",
        2: "!",
        3: "@",
        4: "#",
        5: "$",
        6: "%",
        7: "^",
        8: "&",
        9: "*",
        10: "(",
        11: ")",
        12: "_",
        13: "+",
        14: "BKSP",
        15: "TAB",
        16: "Q",
        17: "W",
        18: "E",
        19: "R",
        20: "T",
        21: "Y",
        22: "U",
        23: "I",
        24: "O",
        25: "P",
        26: "{",
        27: "}",
        28: "CRLF",
        29: "LCTRL",
        30: "A",
        31: "S",
        32: "D",
        33: "F",
        34: "G",
        35: "H",
        36: "J",
        37: "K",
        38: "L",
        39: ":",
        40: "'",
        41: "~",
        42: "LSHFT",
        43: "|",
        44: "Z",
        45: "X",
        46: "C",
        47: "V",
        48: "B",
        49: "N",
        50: "M",
        51: "<",
        52: ">",
        53: "?",
        54: "RSHFT",
        56: "LALT",
        57: " ",
        100: "RALT",
    }

    LSHIFT_SCANCODE = 42

    # TODO verify args/kwargs here is reasonable
    def __init__(
        self, event_queue, config_name, device_name="<USBBadgeScanner>", on_scan=None
    ):
        super(HIDKeystrokingReader, self).__init__(event_queue, config_name)
        self._on_scan = on_scan
        self._device_name = device_name
        self.f = self.get_scanner_device()
        self.f.grab()

    def setUp(self):
        try:
          import evdev
        except ModuleNotFoundError:
          self.fail("evdev not available")

    def get_scanner_device(self):
        """Finds connected device matching device_name.

        Returns:
          The file for input events that read_input can listen to
        """

        devices = [evdev.InputDevice(x) for x in evdev.list_devices()]
        for dev in devices:
            if str(dev.name) == self._device_name:
                return dev

        raise NoMatchingDevice(
            self._device_name, [d.name for d in devices], "check permissions?"
        )

    def read_input(self):
        """Listens solely to the RFID keyboard and returns the scanned badge.

        Args:
          device: input device to listen to

        Returns:
          badge value as string
        """

        rfid = ""
        capitalized = 0
        device = self.f
        print("About to read_input")
        for event in device.read_loop():
            # print("read_input event", event)
            data = evdev.categorize(event)
            if event.type == evdev.ecodes.EV_KEY and data.keystate == 1:
                if data.scancode == self.LSHIFT_SCANCODE:
                    capitalized = 1
                if data.keycode == "KEY_ENTER":
                    break
                if data.scancode != self.LSHIFT_SCANCODE:
                    if capitalized:
                        rfid += self.capscancodes[data.scancode]
                        capitalized ^= 1
                    else:
                        rfid += self.scancodes[data.scancode]
        print("Badge read:", rfid)
        return rfid

    def run_inner(self):
        line = self.read_input()
        self.event_queue.put((self._on_scan, line))
