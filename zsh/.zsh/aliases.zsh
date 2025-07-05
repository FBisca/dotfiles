# ── Utilities ──────────────────────────────────────────────────────────────
alias bat='batcat'                         # Pretty cat with syntax highlighting
alias aliases="grep -E '^alias |^# ---' ~/.zsh/aliases.zsh | bat --language=sh --style=plain --paging=never"

# ── File Management (eza) ───────────────────────────────────────────────────
alias ls='eza --group-directories-first --icons'          # Default view
alias ll='eza -lah --group-directories-first --icons'     # Long + hidden + human-readable
alias la='eza -a --group-directories-first --icons'       # Show all files, including dotfiles
alias lt='eza --tree --level=2 --icons'                   # Tree view, 2 levels deep
alias ld='eza -d */ --group-directories-first --icons'    # List directories only
alias lx='eza -lah --sort=extension --icons'              # Group files by extension

