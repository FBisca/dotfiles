# ── Utilities ──────────────────────────────────────────────────────────────
alias aliases="grep -E '^alias |^# ---' ~/.zsh/aliases.zsh | bat --language=sh --style=plain --paging=never"

# ── File Management (eza) ───────────────────────────────────────────────────
alias ls='eza --group-directories-first --icons'          # Default view
alias ll='eza -lah --group-directories-first --icons'     # Long + hidden + human-readable
alias la='eza -a --group-directories-first --icons'       # Show all files, including dotfiles


# --- Utilities functions ---
lt() {                                                    # Filtered tree view, 2 levels deep by default
  local level=${1:-2}
  shift
  eza --tree --level="$level" --icons --ignore-glob='node_modules|dist|.git|.turbo' "$@"
}

lta() {                                                    # Full tree view, 2 levels deep by default
  local level=${1:-2}
  shift
  eza --tree --level="$level" --icons "$@"
}

# --- macOS Natural Scroll ---
natural-scroll-status() {
  local current
  current=$(defaults read -g com.apple.swipescrolldirection 2>/dev/null || echo 1)
  if [[ "$current" == "1" ]]; then
    echo "Natural scroll: ON"
  else
    echo "Natural scroll: OFF"
  fi
}

natural-scroll-on() {
  defaults write -g com.apple.swipescrolldirection -boolean YES
  echo "Natural scroll enabled"
  killall cfprefsd
}

natural-scroll-off() {
  defaults write -g com.apple.swipescrolldirection -boolean NO
  echo "Natural scroll disabled"
  killall cfprefsd
}

natural-scroll-toggle() {
  local current
  current=$(defaults read -g com.apple.swipescrolldirection 2>/dev/null || echo 1)

  if [[ "$current" == "1" ]]; then
    natural-scroll-off
  else
    natural-scroll-on
  fi
}

