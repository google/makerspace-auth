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

from authbox.api import BaseWiegandPinThread, GPIO
import time


class WiegandGPIOReader(BaseWiegandPinThread):
  """Badge reader hardware abstraction.

  A Wiegand GPIO badge reader is defined in config as:

    [pins]
    name = WiegandGPIOReader:3:5

  where 3 is the D0 pin (physical numbering), and 5 is the D1 pin (also 
  physical numbering).
  """

  # This is a class variable to store the bitstream transmitted by the reader.
  # It is stored using a string to avoid byte ordering issues as well as to
  # simplify its processing.  It was initially implemented using the
  # "bitstream" package, but this then had a dependency on a C compiler and
  # NumPy
  bits = ''

  def_timeout_in_ms = 15
  timeout = def_timeout_in_ms

  def __init__( self, event_queue, config_name, d0_pin, d1_pin, on_scan=None):
    super(WiegandGPIOReader, self).__init__(
        event_queue, config_name, int(d0_pin), int(d1_pin))
    self._on_scan = on_scan

    if self._on_scan:
        GPIO.add_event_detect(self.d0_pin, GPIO.FALLING, callback=self.decode)
        GPIO.add_event_detect(self.d1_pin, GPIO.FALLING, callback=self.decode)


  def _callback(self):
    """Wrapper to queue events instead of calling them directly."""
    if self._on_scan:
      self.event_queue.put((self._on_scan, self))

  def decode(self, channel):
      if channel == self.d0_pin:
          self.bits = self.bits + "0"
      elif channel == self.d1_pin:
          self.bits = self.bits + "1"
      self.timeout = self.def_timeout_in_ms


  def read_input(self):
    """

    Args:
      None

    This thread will perform a blocking read.  If there are no bits coming in
    the stream, this will actually hold in the timeout state.

    Returns:
      badge value as string
    """
    ## this will currently have a race condition where two cards read back
    ## to back as one giant card
    while self.timeout > 0:
        if self.bits:
            self.timeout = self.timeout -1
        time.sleep(0.001)

    if len(self.bits) > 1 and self.timeout == 0:
        ## TODO: Add a "debug" flag, which will output these values to the
        ## console
        #print "Binary:",self.bits
        #result = int(str(self.bits[1:26]),2)
        #print('Bits is {} bits in length'.format(len(self.bits)))
        #print('{:012X}'.format(int(self.bits[-25:-1], 2)))
        #print('{0:30b}'.format(int(self.bits[-25:-1], 2)))
        b = self.bits
        self.bits = ''
        # change to start=1 to avoid this calculation and the one in
        # the return for this function
        start = 0 - len(self.bits) + 1
        # document the format of the string, noting that for readers
        # which push a string longer than 8 characters 
        self.timeout = self.def_timeout_in_ms
        return '{:08X}'.format(int(b[start:-1], 2))


  def run_inner(self):
    line = self.read_input()
    self.event_queue.put((self._on_scan, line))
