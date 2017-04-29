#!/bin/bash
set -eu

user=$1
tool=$2
auth_minutes=$3
now=$(date)

# If disk is full and we can't log, this exits nonzero.
echo "$now,$1,$2,$3" >> log.txt
# If user is not in the list, this exits nonzero.
grep -qw "$user" authorized.txt
