#!/bin/sh
# Claude Code status line: model, context bar, % and tokens used / window size.
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
[ -z "$used" ] && { echo "$model"; exit 0; }
pct=$(printf '%.0f' "$used")
fill=$((pct * 10 / 100))
bar=""
i=0
while [ "$i" -lt 10 ]; do # a loop, not tr: tr would split the multibyte glyphs in the C locale
  if [ "$i" -lt "$fill" ]; then bar="$bar█"; else bar="$bar░"; fi
  i=$((i + 1))
done
k() { awk -v n="$1" 'BEGIN { if (n >= 1000000) printf "%.1fM", n/1000000; else printf "%.0fk", n/1000 }'; }
if [ -n "$size" ]; then
  tokens=$(awk -v p="$used" -v s="$size" 'BEGIN { printf "%d", p * s / 100 }')
  printf '%s [%s] %d%% · %s/%s\n' "$model" "$bar" "$pct" "$(k "$tokens")" "$(k "$size")"
else
  printf '%s [%s] %d%%\n' "$model" "$bar" "$pct"
fi
