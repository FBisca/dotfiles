#!/bin/bash

fullscreen=$(hyprctl activewindow -j | jq -r '.fullscreen // 0')
window_title=$(hyprctl activewindow -j | jq -r '.title')

if [[ "$fullscreen" -ne 0 ]]; then
  notify-send "🛑 Can't kill" "\"$window_title\" is fullscreen"
  exit 0
fi

hyprctl dispatch killactive

