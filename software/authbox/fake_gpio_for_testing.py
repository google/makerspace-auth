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

"""Test helper that logs instead of altering pin states."""

from __future__ import print_function

import time


def _log_match(a, b):
    return abs(a[0] - b[0]) < 0.1 and a[1] == b[1] and a[2] == b[2]

class FakeTime(object):
    """Fake for the module 'time' so tests run faster."""

    def __init__(self):
        self.t = 0

    def time(self):
        return self.t

    def sleep(self, x):
        self.t += x


# TODO: Queue patcher that also advances time
