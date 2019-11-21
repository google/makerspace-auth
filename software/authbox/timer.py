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

from __future__ import print_function

import threading
import time

from authbox.api import BaseDerivedThread
from authbox.compat import queue


class Timer(BaseDerivedThread):
    def __init__(self, event_queue, config_name, callback):
        super(Timer, self).__init__(event_queue, config_name)
        self.set_queue = queue.Queue(1)
        self.cancel_condition = threading.Condition()
        self.callback = callback

    def run_inner(self):
        # TODO: This is not robust to spurious wakeups, see details in
        # https://bugs.python.org/issue1175933 that

        # TODO add a KILL sentinel
        timeout = self.set_queue.get(block=True)
        print(self, "got", timeout)
        with self.cancel_condition:
            # Instead of a sleep we just pass it as a timeout here (so it's
            # interruptable if someone sets cancel_condition)
            t0 = time.time()
            self.cancel_condition.wait(timeout)
            expired = (time.time()) - t0 >= timeout
            print(self, "expired", expired)
            if expired:
                # The idea here is that we call callback once per set_queue item
                self.event_queue.put((self.callback, self.config_name))

    def set(self, delay):
        # TODO this should replace
        try:
            self.set_queue.put_nowait(delay)
        except queue.Full:
            raise Exception("There is already a queued timeout")

    def cancel(self):
        print(self, "cancel")
        with self.cancel_condition:
            self.cancel_condition.notify()
        try:
            while True:
                self.set_queue.get_nowait()
        except queue.Empty:
            pass
