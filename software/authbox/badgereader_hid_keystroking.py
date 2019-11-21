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
        1: u"ESC",
        2: u"1",
        3: u"2",
        4: u"3",
        5: u"4",
        6: u"5",
        7: u"6",
        8: u"7",
        9: u"8",
        10: u"9",
        11: u"0",
        12: u"-",
        13: u"=",
        14: u"BKSP",
        15: u"TAB",
        16: u"q",
        17: u"w",
        18: u"e",
        19: u"r",
        20: u"t",
        21: u"y",
        22: u"u",
        23: u"i",
        24: u"o",
        25: u"p",
        26: u"[",
        27: u"]",
        28: u"CRLF",
        29: u"LCTRL",
        30: u"a",
        31: u"s",
        32: u"d",
        33: u"f",
        34: u"g",
        35: u"h",
        36: u"j",
        37: u"k",
        38: u"l",
        39: u";",
        40: u'"',
        41: u"`",
        42: u"LSHFT",
        43: u"\\",
        44: u"z",
        45: u"x",
        46: u"c",
        47: u"v",
        48: u"b",
        49: u"n",
        50: u"m",
        51: u",",
        52: u".",
        53: u"/",
        54: u"RSHFT",
        56: u"LALT",
        100: u"RALT",
    }

    # capscancodes are present to shift badge scans as necessary

    capscancodes = {
        0: None,
        1: u"ESC",
        2: u"!",
        3: u"@",
        4: u"#",
        5: u"$",
        6: u"%",
        7: u"^",
        8: u"&",
        9: u"*",
        10: u"(",
        11: u")",
        12: u"_",
        13: u"+",
        14: u"BKSP",
        15: u"TAB",
        16: u"Q",
        17: u"W",
        18: u"E",
        19: u"R",
        20: u"T",
        21: u"Y",
        22: u"U",
        23: u"I",
        24: u"O",
        25: u"P",
        26: u"{",
        27: u"}",
        28: u"CRLF",
        29: u"LCTRL",
        30: u"A",
        31: u"S",
        32: u"D",
        33: u"F",
        34: u"G",
        35: u"H",
        36: u"J",
        37: u"K",
        38: u"L",
        39: u":",
        40: u"'",
        41: u"~",
        42: u"LSHFT",
        43: u"|",
        44: u"Z",
        45: u"X",
        46: u"C",
        47: u"V",
        48: u"B",
        49: u"N",
        50: u"M",
        51: u"<",
        52: u">",
        53: u"?",
        54: u"RSHFT",
        56: u"LALT",
        57: u" ",
        100: u"RALT",
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
