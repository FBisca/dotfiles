# ── Utilities ──────────────────────────────────────────────────────────────
alias aliases="grep -E '^alias |^# ---' ~/.zsh/aliases.zsh | bat --language=sh --style=plain --paging=never"

# ── File Management (eza) ───────────────────────────────────────────────────
alias ls='eza --group-directories-first --icons'          # Default view
alias ll='eza -lah --group-directories-first --icons'     # Long + hidden + human-readable
alias la='eza -a --group-directories-first --icons'       # Show all files, including dotfiles


# --- Project Specific Aliases ---
alias h-svc="cd $HOME/developer/heritage/svc-platform"
alias h-server="cd $HOME/developer/heritage/svc-platform/packages/server"
alias h-webapp="cd $HOME/developer/heritage/web-app"
alias h-admin="cd $HOME/developer/heritage/admin-panel"

# --- Sync database from production server ---
h-db-sync() {
  local original_dir=$(pwd)
  
  h-server && \
    echo "🔄 Syncing database from production server..." && \
    ssh -A ${ICONIC_SSH_USER}@${ICONIC_SSH_HOST} "docker exec db mysqldump -u ${ICONIC_DB_USER} -p${ICONIC_DB_PASSWORD} ${ICONIC_DB_NAME}" > db_dump.sql && \
    echo "🔄 Database dumped successfully" && \
    pnpm docker:db:init && \
    echo "✅ Database synced successfully"

  cd "$original_dir"
}


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

# --- Claude Code / Ollama profiles ---
# Vanilla Anthropic Claude Code remains:
#   claude
#
# Do not globally export ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN,
# or ANTHROPIC_API_KEY. Ollama routing should be opt-in only.
alias claude-minimax='CLAUDE_CODE_MAX_CONTEXT_TOKENS="512000" ollama launch claude --model minimax-m3:cloud'

claude-minimax-api() {
  env \
    -u ANTHROPIC_API_KEY \
    -u ANTHROPIC_AUTH_TOKEN \
    -u ANTHROPIC_BASE_URL \
    ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$MINIMAX_API_KEY" \
    API_TIMEOUT_MS="3000000" \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1" \
    ANTHROPIC_MODEL="MiniMax-M3" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="MiniMax-M3" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="MiniMax-M3" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="MiniMax-M3" \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW="512000" \
    CLAUDE_CODE_MAX_CONTEXT_TOKENS="512000" \
    claude "$@"
}

claude-glm() {
  env \
    CLAUDE_CODE_MAX_CONTEXT_TOKENS="812000" \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW="812000" \
    ollama launch claude --model glm-5.3:cloud
}

claude-glm-flash() {
  env \
    CLAUDE_CODE_MAX_CONTEXT_TOKENS="812000" \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW="812000" \
    ollama launch claude --model glm-5.3-flash:cloud
}

claude-chino() {
  env \
    CLAUDE_CODE_MAX_CONTEXT_TOKENS="512000" \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW="512000" \
    ollama launch claude --model deepseek-v4-flash:0731-cloud
}

claude-k3() {
  env \
    CLAUDE_CODE_MAX_CONTEXT_TOKENS="964000" \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW="964000" \
    ollama launch claude --model kimi-k3:cloud
}

alias ccm='claude-minimax-api'

claude-ollama() {
  local model="${1:-deepseek-v4-pro:cloud}"

  if [[ $# -gt 0 ]]; then
    shift
  fi

  ollama launch claude --model "$model" "$@"
}

claude-ollama-p() {
  local model="${1:-deepseek-v4-pro:cloud}"

  if [[ $# -gt 0 ]]; then
    shift
  fi

  ollama launch claude --model "$model" -- "$@"
}
# --- End Claude Code / Ollama profiles ---
