#!/usr/bin/env bash

# Generate a random alphanumeric string (default length: 16)
LENGTH=${1:-16}

# Use /dev/urandom and base64, then filter to alphanumerics
random_string=$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$LENGTH")

echo "$random_string"

