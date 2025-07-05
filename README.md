# 🛠️ Rodrigo's Dotfiles

A modular, minimal dotfiles setup managed with [GNU Stow](https://www.gnu.org/software/stow/).
Each tool lives in its own directory and is easy to track, modify, or replace.

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

## ⚡ Getting Started

```bash
git clone https://github.com/rodrigopsasaki/dotfiles ~/.dotfiles
cd ~/.dotfiles
stow git zsh nvim mise gh
```

## 🔧 Requirements

- You have [`git`](https://git-scm.com/) installed.
- You have [`gh`](https://cli.github.com/) installed and authenticated via `gh auth login`.
- Your system supports symlinks (tested on Linux with GNU Stow).

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

## 📁 Layout

Each tool has its own folder. Use `stow <tool>` to activate.

```
~/.dotfiles/
├── git/
├── zsh/
├── nvim/
├── mise/
└── gh/
```

---

## 🧠 Philosophy

- **Modular** — everything lives in its own namespace
- **Safe** — secrets go in private overrides and are gitignored
- **Explicit** — no surprises, no clever magic

---
