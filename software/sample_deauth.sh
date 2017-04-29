#!/bin/bash
set -eu

user=$1
tool=$2
now=$(date)

# If disk is full and we can't log, this exits nonzero.
echo "$now,$1,$2,X" >> log.txt
