# Copyright 2019 Tim Hatch All Rights Reserved.
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
Ease Python 3 transition by handling all the python2 differences in one place.
"""

try:
    import Queue as queue
except ImportError:
    import queue  # noqa: F401

try:
    import ConfigParser as configparser
except ImportError:
    import configparser  # noqa: F401
