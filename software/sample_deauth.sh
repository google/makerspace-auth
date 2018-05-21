#!/bin/bash
#
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

set -eu

# Usage: sample_deauth.sh <user> <tool>
#
# Logs a deauth event.  (It can't really "fail", as the client will still turn
# the tool off.)
#
# If this script exits 0, the user is allowed, and disallowed otherwise.
# Because of the set -e above, this script exits nonzero if the echo does.
#
user=$1
tool=$2
now=$(date)

# If disk is full and we can't log, this exits nonzero.
echo "$now,$1,$2,X" >> log.txt
