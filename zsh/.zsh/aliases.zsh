# ── Utilities ──────────────────────────────────────────────────────────────
alias aliases="grep -E '^alias |^# ---' ~/.zsh/aliases.zsh | bat --language=sh --style=plain --paging=never"

# ── File Management (eza) ───────────────────────────────────────────────────
alias ls='eza --group-directories-first --icons'          # Default view
alias ll='eza -lah --group-directories-first --icons'     # Long + hidden + human-readable
alias la='eza -a --group-directories-first --icons'       # Show all files, including dotfiles

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

