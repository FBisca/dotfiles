#!/usr/bin/env bash
if [[ -d "$1" ]]; then
  ls -la "$1"
else
  bat --style=numbers --color=always --line-range=:500 "$1" 2>/dev/null || cat "$1"
fi
