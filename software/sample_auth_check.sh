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

# Usage: sample_auth_check.sh <user> <tool> <auth_minutes>
#
# Checks to see if <user> exists as a line in authorized.txt, and logs to
# log.txt.  This is a simple check for testing, but if you talk to a server
# instead you can get better metrics.
#
# If this script exits 0, the user is allowed, and disallowed otherwise.
# Because of the set -e above, this script exits nonzero if the grep line does.
#
user=$1
tool=$2
auth_minutes=$3
now=$(date)

# If disk is full and we can't log, this exits nonzero.
echo "$now,$1,$2,$3" >> log.txt
# If user is not in the list, this exits nonzero.
grep -qw "$user" authorized.txt
