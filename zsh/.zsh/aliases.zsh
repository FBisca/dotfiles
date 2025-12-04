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
    yarn docker:db:init && \
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