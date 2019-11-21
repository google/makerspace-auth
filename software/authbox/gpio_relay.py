# Copyright 2017-2018 Google Inc. All Rights Reserved.
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

"""Abstraction around RPi.GPIO for relay type outputs.
"""


from authbox.api import GPIO, BasePinThread

types = {
    "ActiveHigh": 1,
    "ActiveLow": 0,
}


class Relay(BasePinThread):
    """Relay hardware abstraction.

    A relay is defined in config as:

      [pins]
      name = Relay:ActiveHigh:1

    where ActiveHigh may instead be ActiveLow, as appropriate, and 1 is the output
    pin (physical numbering).
    """

    def __init__(self, event_queue, config_name, output_type, output_pin):
        super(Relay, self).__init__(
            event_queue, config_name, None, int(output_pin), not types[output_type]
        )
        self.output_on_val = types[output_type]
        # TODO: Push this initial setup into BasePinThread, to avoid a momentary glitch
        self.off()

    def run(self):
        pass  # Don't need a thread

    def on(self):
        GPIO.output(self.output_pin, self.output_on_val)

    def off(self):
        GPIO.output(self.output_pin, not self.output_on_val)
