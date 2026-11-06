#!/bin/bash
# Install the dotfiles: link skills, wire the agent runtime, generate agent config, stow the rest.
#
# Usage: ./install.sh [--no-stow] [--upstream] [-h]
#   --no-stow    skip GNU Stow (skills, runtime and generated config still run)
#   --upstream   also reinstall the upstream skills agent-skills does not carry
#
# Environment (all optional):
#   AGENT_SKILLS_DIR   agent-skills checkout      (default ~/developer/agent-skills, cloned if missing)
#   AGENT_RUNTIME_DIR  agent-runtime checkout     (default ~/developer/agent-runtime, cloned if missing)
#   AGENT_FLEET_DIR    private skills checkout    (default ~/developer/agent-fleet, skipped if missing)
#   DOTFILES_PRIVATE   private config overlay dir (default $AGENT_FLEET_DIR/overlay)
#   AGENT_SKILLS_REPO / AGENT_RUNTIME_REPO   clone URLs
#
# Safe to re-run. Never deletes user data: replaced files are backed up, skill state is moved.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

AGENT_SKILLS_DIR="${AGENT_SKILLS_DIR:-$HOME/developer/agent-skills}"
AGENT_RUNTIME_DIR="${AGENT_RUNTIME_DIR:-$HOME/developer/agent-runtime}"
AGENT_FLEET_DIR="${AGENT_FLEET_DIR:-$HOME/developer/agent-fleet}"
DOTFILES_PRIVATE="${DOTFILES_PRIVATE:-$AGENT_FLEET_DIR/overlay}"
AGENT_SKILLS_REPO="${AGENT_SKILLS_REPO:-https://github.com/FBisca/agent-skills.git}"
AGENT_RUNTIME_REPO="${AGENT_RUNTIME_REPO:-https://github.com/FBisca/agent-runtime.git}"
LEGACY_CLAUDE_OVERLAY="$HOME/.claude/private-overlay/settings.overlay.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { printf '%b[INFO]%b %s\n' "$BLUE" "$NC" "$1"; }
ok() { printf '%b[OK]%b %s\n' "$GREEN" "$NC" "$1"; }
warn() { printf '%b[WARN]%b %s\n' "$YELLOW" "$NC" "$1" >&2; }
die() { printf '%b[ERROR]%b %s\n' "$RED" "$NC" "$1" >&2; exit 1; }

DO_STOW=1
DO_UPSTREAM=0
for arg in "$@"; do
  case "$arg" in
    --no-stow) DO_STOW=0 ;;
    --upstream) DO_UPSTREAM=1 ;;
    -h | --help) sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) die "unknown option: $arg (see --help)" ;;
  esac
done

[[ -f README.md && -e .git ]] || die "run this script from the dotfiles checkout"
command -v git >/dev/null 2>&1 || die "git is required"
command -v python3 >/dev/null 2>&1 || die "python3 (3.11+) is required"

clone_if_missing() { # dir url
  [[ -d "$1" ]] && return 0
  info "cloning $2 into $1"
  mkdir -p "$(dirname "$1")"
  git clone --quiet "$2" "$1" || die "could not clone $2"
}

# --- skills -----------------------------------------------------------------
# ~/.claude/skills and ~/.agents/skills are real directories, so `npx skills add` and the
# claude.ai synced skills never write into a repo. Each skill from agent-skills and
# agent-fleet is a symlink into them.

resolve_dir() { # symlink -> physical directory it points to (empty when dangling)
  local target
  target="$(readlink "$1")"
  [[ "$target" == /* ]] || target="$(dirname "$1")/$target"
  if [[ -d "$target" ]]; then (cd "$target" && pwd -P); fi
  return 0
}

SKILL_SRCS=()
collect_skill_sources() {
  local repo dir
  for repo in "$AGENT_SKILLS_DIR" "$AGENT_FLEET_DIR"; do
    [[ -d "$repo/skills" ]] || continue
    for dir in "$repo"/skills/*/; do
      if [[ -d "$dir" ]]; then SKILL_SRCS+=("${dir%/}"); fi
    done
  done
}

is_managed() { # name
  local src
  for src in ${SKILL_SRCS[@]+"${SKILL_SRCS[@]}"}; do
    [[ "$(basename "$src")" == "$1" ]] && return 0
  done
  return 1
}

has_content() { # dir: anything beyond .DS_Store and __pycache__ files?
  [[ -n "$(find "$1" -type f ! -name .DS_Store ! -path '*/__pycache__/*' -print -quit)" ]]
}

# Move what a former skills directory held into the new real ones: claude.ai's synced/ stays
# with Claude, everything else (npx installs) goes to ~/.agents/skills. Skills this setup manages
# are left behind, since they are re-linked from their repos. Directories with nothing but
# .DS_Store or __pycache__ are not skills and are skipped.
salvage() { # old_dir claude_dir agents_dir
  local entry name
  [[ -d "$1" ]] || return 0
  for entry in "$1"/*; do
    [[ -e "$entry" && ! -L "$entry" ]] || continue
    name="$(basename "$entry")"
    is_managed "$name" && continue
    if [[ -d "$entry" && "$name" != synced ]] && ! has_content "$entry"; then continue; fi
    if [[ "$name" == synced ]]; then
      [[ -e "$2/synced" ]] || mv "$entry" "$2/synced"
    elif [[ ! -e "$3/$name" ]]; then
      mv "$entry" "$3/$name"
    else
      warn "kept $entry: $3/$name already exists"
    fi
  done
}

link_skill() { # src dest_dir
  local name target
  name="$(basename "$1")"
  target="$2/$name"
  if [[ -L "$target" ]]; then
    ln -sfn "$1" "$target"
  elif [[ -e "$target" ]]; then
    warn "skipped $name: a real entry already exists in $2"
  else
    ln -s "$1" "$target"
  fi
}

# What salvage left in a former skills directory (stale copies of managed skills, ignored
# build leftovers such as node_modules) moves to a timestamped backup, never deleted. That
# also keeps the old checkout directory free of anything Stow could trip over.
backup_leftovers() { # old_dir...
  local old entry backup
  backup="$HOME/.dotfiles-backup/skills-$(date +%Y%m%d%H%M%S)"
  for old in "$@"; do
    [[ -d "$old" ]] || continue
    for entry in "$old"/*; do
      [[ -e "$entry" && ! -L "$entry" ]] || continue
      mkdir -p "$backup"
      mv "$entry" "$backup/$(basename "$entry")"
      info "moved leftover $entry to $backup"
    done
  done
}

setup_skills() {
  local claude="$HOME/.claude/skills" agents="$HOME/.agents/skills"
  local olds=() dir old src entry name
  mkdir -p "$HOME/.claude" "$HOME/.agents"
  collect_skill_sources

  for dir in "$claude" "$agents"; do
    if [[ -L "$dir" ]]; then
      old="$(resolve_dir "$dir")"
      if [[ -n "$old" ]]; then olds+=("$old"); fi
      rm "$dir"
    fi
    mkdir -p "$dir"
  done
  # A dangling link means the old layout is already gone from the checkout; synced/ lives on there.
  olds+=("$ROOT/agents/.agents/skills")
  for old in "${olds[@]}"; do
    salvage "$old" "$claude" "$agents"
  done
  backup_leftovers "${olds[@]}"

  for dir in "$claude" "$agents"; do
    for entry in "$dir"/*; do # drop links whose skill has been removed
      if [[ -L "$entry" && ! -e "$entry" ]]; then rm "$entry"; fi
    done
    for src in ${SKILL_SRCS[@]+"${SKILL_SRCS[@]}"}; do
      link_skill "$src" "$dir"
    done
  done
  for entry in "$agents"/*; do # skills installed into ~/.agents (npx) are visible to Claude too
    name="$(basename "$entry")"
    if [[ -d "$entry" && ! -e "$claude/$name" && ! -L "$claude/$name" ]]; then
      ln -s "$entry" "$claude/$name"
    fi
  done
  ok "skills linked into $claude and $agents (${#SKILL_SRCS[@]} from agent-skills and agent-fleet)"

  if [[ "$DO_UPSTREAM" -eq 1 ]]; then
    [[ -x "$AGENT_SKILLS_DIR/scripts/install-upstream.sh" ]] || die "no install-upstream.sh in $AGENT_SKILLS_DIR"
    info "installing upstream skills"
    "$AGENT_SKILLS_DIR/scripts/install-upstream.sh"
  fi
}

# --- agent runtime ------------------------------------------------------------
setup_runtime() {
  clone_if_missing "$AGENT_RUNTIME_DIR" "$AGENT_RUNTIME_REPO"
  [[ -x "$AGENT_RUNTIME_DIR/install.sh" ]] || die "$AGENT_RUNTIME_DIR/install.sh not found"
  BIN_DIR="$HOME/.local/bin" "$AGENT_RUNTIME_DIR/install.sh" >/dev/null
  ok "agent-runtime shims linked into $HOME/.local/bin"
  # Claude only registers a directory marketplace on an explicit add; settings alone are not enough.
  if command -v claude >/dev/null 2>&1 && [[ -d "$HOME/.claude/plugins" ]] && ! claude plugin list 2>/dev/null | grep -q 'agent-runtime@agent-runtime'; then
    claude plugin marketplace add "$AGENT_RUNTIME_DIR" >/dev/null 2>&1 || warn "could not add the agent-runtime marketplace"
    if claude plugin install agent-runtime@agent-runtime >/dev/null 2>&1; then
      ok "agent-runtime plugin installed"
    else
      warn "install it once with: claude plugin install agent-runtime@agent-runtime"
    fi
  fi
}

# --- rastro MCP -----------------------------------------------------------------
# Claude Code keeps user-scope MCP servers in ~/.claude.json, which is not generated here,
# so register rastro there once. Codex gets it from config.base.toml.
# shellcheck disable=SC2016 # $HOME expands when the server starts, not here
RASTRO_MCP='exec "$HOME/.cargo/bin/rastro" mcp'

setup_rastro() {
  if [[ ! -x "$HOME/.cargo/bin/rastro" ]]; then
    info "rastro not installed; its MCP entries wait for: cargo install --locked --path crates/rastro-cli"
    return 0
  fi
  command -v claude >/dev/null 2>&1 || return 0
  claude mcp get rastro >/dev/null 2>&1 && return 0
  if claude mcp add --scope user rastro -- sh -c "$RASTRO_MCP" >/dev/null 2>&1; then
    ok "rastro MCP server registered for Claude Code"
  else
    warn "register it once with: claude mcp add --scope user rastro -- sh -c '$RASTRO_MCP'"
  fi
}

# --- generated config -----------------------------------------------------------
# Tables the tools write into their own live config at runtime. They are carried over from
# the live file (live wins, base and overlay entries it lacks stay), so re-running the
# installer never reverts them: Codex's trusted hook hashes, project trust, model notices
# and plugin state; Claude's enabled plugins, marketplaces and "always allow" permissions.
CODEX_RUNTIME_KEYS="projects hooks.state notice tui plugins marketplaces"
CLAUDE_RUNTIME_KEYS="enabledPlugins extraKnownMarketplaces permissions"

# Live settings are base + private overlay, deep-merged by scripts/merge-config.py (arrays
# concatenate). The result replaces the live file atomically, so it is never half-written.
generate_config() { # kind base live keep_paths overlay...
  local kind="$1" base="$2" live="$3" keep="$4" new path args=()
  shift 4
  mkdir -p "$(dirname "$live")"
  new="$live.new.$$"
  # Runtime-written state in a regular live file wins for the paths in $keep.
  if [[ -f "$live" && ! -L "$live" ]]; then
    args+=(--live "$live")
    for path in $keep; do args+=(--keep "$path"); done
  fi
  python3 "$ROOT/scripts/merge-config.py" "$kind" "$new" "$base" "$@" ${args[@]+"${args[@]}"} || {
    rm -f "$new"
    die "could not generate $live; it was left untouched"
  }
  if [[ -e "$live" ]] && ! cmp -s "$live" "$new"; then
    cp -L "$live" "$live.bak-$(date +%Y%m%d%H%M%S)"
    warn "$live differed from the generated file; previous copy saved as $live.bak-*"
  fi
  mv -f "$new" "$live" # replaces a symlink to the old tracked file without touching its target
  ok "generated $live"
}

setup_config() {
  local overlay=()
  if [[ -f "$DOTFILES_PRIVATE/claude-settings.json" ]]; then
    overlay=("$DOTFILES_PRIVATE/claude-settings.json")
  elif [[ -f "$LEGACY_CLAUDE_OVERLAY" ]]; then
    overlay=("$LEGACY_CLAUDE_OVERLAY")
  fi
  generate_config json "$ROOT/agents/.claude/settings.base.json" "$HOME/.claude/settings.json" \
    "$CLAUDE_RUNTIME_KEYS" ${overlay[@]+"${overlay[@]}"}

  overlay=()
  if [[ -f "$DOTFILES_PRIVATE/codex-config.toml" ]]; then overlay=("$DOTFILES_PRIVATE/codex-config.toml"); fi
  generate_config toml "$ROOT/agents/.codex/config.base.toml" "$HOME/.codex/config.toml" \
    "$CODEX_RUNTIME_KEYS" ${overlay[@]+"${overlay[@]}"}
}

# --- stow -----------------------------------------------------------------------
MODULES=(git zsh nvim mise gh kitty wezterm fzf env slack agents bin)

stow_modules() {
  command -v stow >/dev/null 2>&1 || die "GNU Stow is not installed (brew install stow), or pass --no-stow"
  # Real folders for agent homes: stow links only the tracked entries inside them, so
  # sessions, credentials and history never land in this repo.
  mkdir -p "$HOME/.claude" "$HOME/.codex" "$HOME/.agents" "$HOME/.config/agent-runtime"
  local module
  for module in "${MODULES[@]}"; do
    if [[ -d "$module" ]]; then
      info "stowing $module"
      stow "$module" || die "failed to stow $module"
    else
      warn "module $module not found, skipping"
    fi
  done
  ok "dotfiles stowed"
}

clone_if_missing "$AGENT_SKILLS_DIR" "$AGENT_SKILLS_REPO"
setup_skills
setup_runtime
setup_rastro
setup_config
if [[ "$DO_STOW" -eq 1 ]]; then stow_modules; fi

ok "done"
if grep -q '"dotfiles"' "$HOME/.claude/plugins/known_marketplaces.json" 2>/dev/null; then
  warn "the old 'dotfiles' Claude marketplace is still registered; remove it once with: claude plugin marketplace remove dotfiles"
fi
cat <<'EOF'
Next steps:
  1. Restart your terminal, or: source ~/.zshrc
  2. Restart Claude Code and Codex so they pick up the generated config.
  3. Optional tools: oh-my-zsh, mise, gh (gh auth login), Nerd Fonts, jq, ripgrep, fzf.
  4. Upstream skills: ./install.sh --upstream
EOF
