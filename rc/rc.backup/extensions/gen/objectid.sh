#!/usr/bin/env bash

# generate a MongoDB-style ObjectID (24-character hex string)
timestamp=$(printf '%08x' $(($(date +%s))))
random=$(hexdump -n 8 -e '8/1 "%02x"' /dev/urandom)

objectid="${timestamp}${random}"
echo "$objectid"
