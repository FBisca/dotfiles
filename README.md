# 🛠️ Dotfiles

A modular, minimal dotfiles setup managed with [GNU Stow](https://www.gnu.org/software/stow/).
Each tool lives in its own directory and is easy to track, modify, or replace.

Special thanks to [rodrigopsasaki](https://github.com/rodrigopsasaki), the original author of the repository this project was forked from.

## 🧭 Table of Contents

- [🧩 Getting Started](#-getting-started)
- [🧰 Requirements](#-requirements)
- [🛠️ Tools](#-tools)
  - [🔧 Git](#-git)
  - [🧩 Neovim](#-neovim)
  - [🐚 Zsh](#-zsh)
  - [📦 mise](#-mise)
  - [🐙 GitHub CLI (gh)](#-github-cli-gh)
- [📁 Layout](#-layout)
- [🧠 Philosophy](#-philosophy)
- [🔁 Feature workflow](docs/workflow.md): idea → PRD → plan → build, the skill behind each step and the method it comes from

## ⚡ Getting Started

### Quick Install

```bash
git clone https://github.com/Fbisca/dotfiles ~/.dotfiles
cd ~/.dotfiles
./install.sh
```

## 🔧 Requirements

- You have [`stow`](https://www.gnu.org/software/stow/) installed.
- You have [`git`](https://git-scm.com/) installed.
- You have [`gh`](https://cli.github.com/) installed and authenticated via `gh auth login`.
- Your system supports symlinks (tested on macOS ARM with GNU Stow).

`install.sh` creates `~/.claude`, `~/.codex` and `~/.agents` as real folders before stowing, so tool state (sessions, credentials, history) stays out of this repo and only the tracked entries are linked. If those folders already hold tracked files on a machine, move them into this repo first or run `stow --adopt agents` once.

## 📦 Tools

### 🔧 Git

[→ See full README](./git/README.md)

Opinionated `git` setup with dozens of helpful aliases, delta-powered diffs, and scoped overrides.

```bash
# Example Aliases
git s       # short status
git l       # graph log
git go foo  # checkout or create branch 'foo'
git ca      # add all and commit verbosely
git all pull  # pull across all sub-repos
```

---

### 🐚 Zsh

[→ See full README](./zsh/README.md)

Zsh configuration split into modular files and sourced from `.zshrc`. Includes:

- Plugin support (autosuggestions, syntax highlighting)
- FZF integration
- Clean alias and path management

---

### 🧩 Neovim

[→ See full README](./nvim/README.md)

Neovim configuration written in Lua. Fast startup, modern plugins, sane defaults.

---

### 📦 mise

[→ See full README](./mise/README.md)

Handles language runtime management with [`mise`](https://mise.jdx.dev/).

---

### 🐙 GitHub CLI (gh)

[→ See full README](./gh/README.md)

GitHub CLI configuration. Tokens and credentials are not tracked in git.

You must run:

```bash
gh auth login
```

...to authenticate before using the `gh` command set.

---

### 🤖 Agent Tooling

Shared agent configuration is also tracked for local CLI tools:

- `agents/.claude` stores shared Claude Code settings plus custom agents and commands.
- `agents/.codex` stores shared Codex defaults and command rules. Sensitive MCP credentials stay in local overrides.
- `agents/.agents` stores every skill: `~/.agents/skills` (Codex) and `~/.claude/skills` (Claude Code) are both one link to `agents/.agents/skills`, so no agent keeps its own copy. Skills installed with `npx skills add -g` land here too and show up as git changes.
- `agents/plugins/agent-runtime` is a Claude Code plugin (also wired into Codex through `agents/.codex/config.toml`) that serves the `agent-runtime` MCP tools for delegating to other agents: `spawn`, `message`, `resume`, `report`, `wait`, `task`, `collect`, `stop`, `status`, `list`. Its hooks keep subagents and workers off commands that would reach their lead. `agent-runtime resolve|status|list` remain as debug commands.
  - **Dispatch upgrade:** `spawn`/`resume` return promptly with `worker_id` and `assignment_id`; one `wait(all)` returns reports, assignment states, peer messages and a `receipt` to pass on the next call. Workers use `report(kind=progress|complete|blocked|decision, assignment_id)`; `task` manages shared tasks (`cursor` pages `list`), and `spawn`/`resume` take an optional `task_id` to link one. `status`/`collect` are diagnostics only; `status`, `list`, `collect` and `task list` return inbox messages only when the call carries a `receipt` (`wait` and mutating tools always do). `stop` also works on workers whose terminal vanished.
  - **Activation:** structured dispatch is on through `AGENT_RUNTIME_DISPATCH=1` in `agents/plugins/agent-runtime/.mcp.json` (Claude) and `[mcp_servers.agent-runtime.env]` in `agents/.codex/config.toml` (Codex). Both hosts use a 600s tool timeout (`"timeout": 600000`, `tool_timeout_sec = 600`); `wait` caps at 590s. Absent the variable the server still runs the legacy transport.
  - **Install:** the tracked `dotfiles` marketplace is a directory source at `~/developer/dotfiles/agents`, so Claude loads the plugin in place from the checkout. Edits apply at the next Claude/Codex session; there is no update step, and version bumps are record-only.
  - **Store:** `${XDG_STATE_HOME:-~/.local/state}/agent-runtime/dispatch.sqlite3` (mode 0600, schema-versioned).
  - **Rollback:** stop the team, disable the plugin or revert these config lines, keep the store for recovery. Restart every Claude/Codex session (and the plugin) afterwards. Queued structured reports are not translated into legacy text; once a worker's server restarts in legacy mode its report ignores `kind`/`assignment_id`.
  - **Migration:** workers live before the upgrade keep their old MCP process and don't know `report(kind, assignment_id)`; `resume` does not restart it, so `stop` them and `spawn` a fresh assignment.
- `agents/.stow-local-ignore` lists what Stow skips in this package (Stow reads ignore files per package, not from the repo root).

Install everything with `stow agents` or let `./install.sh` treat it like any other module.

---

## 📁 Layout

Each tool has its own folder. Use `stow <tool>` to activate.

```
~/.dotfiles/
├── git/
├── zsh/
├── nvim/
├── mise/
├── gh/
├── kitty/
├── wezterm/
├── fzf/
├── env/
├── slack/
├── agents/
│ ├── .agents/
│ ├── .claude/
│ └── .codex/
└── bin/        # scripts on PATH via ~/bin (e.g. wait-checks)
```

---

## 🧠 Philosophy

- **Modular** — everything lives in its own namespace
- **Safe** — secrets go in private overrides and are gitignored
- **Explicit** — no surprises, no clever magic

---
