#!/bin/bash

device_name="QCY H3 Pro"
mac=$(bluetoothctl devices | grep "$device_name" | awk '{print $2}')

if [[ -z "$mac" ]]; then
  echo '{"text": "🎧 N/A", "class": "disconnected"}'
  exit 0
fi

connected=$(bluetoothctl info "$mac" | grep "Connected: yes")

if [[ -n "$connected" ]]; then
  echo "{\"text\": \"$device_name 🎧\", \"class\": \"connected\"}"
else
  echo "{\"text\": \"🎧 Disconnected\", \"class\": \"disconnected\"}"
fi
