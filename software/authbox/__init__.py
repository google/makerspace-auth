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

"""
Authbox client modules.
"""

__version__ = "1.0.0"

# To facilitate testing, this makes things importable on non-Raspberry Pi
# This module isn't perfect (for example, input() doesn't read what output()
# writes), but at least supports the api, and we can mock where it matters.
try:
    from RPi import GPIO

    del GPIO
except ImportError:
    import warnings

    warnings.warn("Using fake_rpi suitable for testing only!")
    del warnings

    import sys
    import fake_rpi

    sys.modules["RPi"] = fake_rpi.RPi
    del sys, fake_rpi
