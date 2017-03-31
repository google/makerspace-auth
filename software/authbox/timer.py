#!/usr/bin/python
#
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

"""Abstraction around RPi.GPIO for relay type outputs.
"""

# TODO add pretty error for version mismatch
from RPi import GPIO

import Queue
import threading

from api import BaseThing

class Timer(BaseThing):
  def __init__(self, event_queue, config_name, callback):
    super(Timer, self).__init__(event_queue, config_name)
    self.set_queue = Queue.Queue(1)
    self.cancel_condition = threading.Condition()
    self.callback = callback

  def run(self):
    while True:
      # TODO add a KILL sentinel
      timeout = self.set_queue.get(block=True)
      with self.cancel_condition:
        # Instead of a sleep we just pass it as a timeout here
        self.cancel_condition.wait(timeout)
        self.event_queue.put(self.callback)

  def set(self, delay):
    # TODO this should replace
    try:
      self.set_queue.put_nowait(delay)
    except Queue.Full:
      raise Exception("There is already a queued timeout")

  def cancel(self):
    with self.cancel_condition:
      self.cancel_condition.notify()
    try:
      while True:
        self.set_queue.get_nowait()
    except Queue.Empty:
      pass
