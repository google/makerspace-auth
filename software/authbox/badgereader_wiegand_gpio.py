# Copyright 2018 Ace Monster Toys. All Rights Reserved.
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

"""Wiegand based badge reader directly connected via GPIO
"""

from __future__ import division, print_function

from authbox.api import GPIO, BaseWiegandPinThread
from authbox.compat import queue

DEFAULT_QUEUE_SIZE = 100  # more than enough for a scan
DEFAULT_TIMEOUT_IN_MS = 15


class WiegandGPIOReader(BaseWiegandPinThread):
    """Badge reader hardware abstraction.

    A Wiegand GPIO badge reader is defined in config as:

      [pins]
      name = WiegandGPIOReader:7:13

    where 7 is the D0 pin (physical numbering), and 13 is the D1 pin (also
    physical numbering).  In this configuration the 6 pin J5 connector will be
    structured as follows:
        Pin 1: D0
        Pin 2: D1
        Pin 3: No connection
        Pin 4: Ground
        Pin 5: 12v
        Pin 6: No connection

    Pin 6 is used for the switched +12v provided by the ULN2003AD chip
    (L5_LOGIC).  As we want to constantly power the RFID reader, there is no need
    to populate Pin 6.

    It should also be noted that most GPIO based RFID badge readers operate at 5v
    logic, so one should use care when connecting them to the host.  Most readers
    communicate only from the reader to the host.  If this is the case a simple
    voltage divider is sufficient to protect the GPIO pins on the host, in the
    event that two way communication is needed a level shifter should be used.
    """

    def __init__(
        self,
        event_queue,
        config_name,
        d0_pin,
        d1_pin,
        on_scan=None,
        queue_size=DEFAULT_QUEUE_SIZE,
        timeout_in_ms=DEFAULT_TIMEOUT_IN_MS,
    ):
        super(WiegandGPIOReader, self).__init__(
            event_queue, config_name, int(d0_pin), int(d1_pin)
        )
        self._on_scan = on_scan
        # The limited-size queue protects from a slow leak in case of deadlock, so
        # we can detect and output something (just a print for now)
        self.bitqueue = queue.Queue(int(queue_size))
        self.timeout_in_seconds = float(timeout_in_ms) / 1000

        if self._on_scan:
            GPIO.add_event_detect(self.d0_pin, GPIO.FALLING, callback=self.decode)
            GPIO.add_event_detect(self.d1_pin, GPIO.FALLING, callback=self.decode)

    def decode(self, channel):
        bit = "0" if channel == self.d0_pin else "1"
        try:
            self.bitqueue.put_nowait(bit)
        except queue.Full:
            # This shouldn't happen.
            print("{name} BUG: QUEUE FULL".format(name=self.__class__.__name__))

    def read_input(self):
        """
        This thread will perform a blocking read.  If there are no bits coming in
        the stream, this will actually wait for them to start coming in.

        Args:
          None

        Returns:
          badge value as string of 0's and 1's.
        """
        # Wait for a first bit to come in
        bit = self.bitqueue.get(block=True)

        ## this will currently have a race condition where two cards read back
        ## to back as one giant card
        bits = [bit]
        while True:
            try:
                bit = self.bitqueue.get(timeout=self.timeout_in_seconds)
            except queue.Empty:
                break
            bits.append(bit)

        return "".join(bits)

    def run_inner(self):
        line = self.read_input()
        self.event_queue.put((self._on_scan, line))
