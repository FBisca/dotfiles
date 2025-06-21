# 🧩 asdf

This directory contains the basic `asdf` shell integration. It's intentionally minimal — every developer will have their own preferred plugins and versions.

## 🧠 What's asdf?

[asdf](https://asdf-vm.com/) is a single CLI tool to manage multiple runtime versions. It lets you easily switch between Node, Python, Ruby, Java, Elixir, Rust, and more. Think of it as `nvm`, `rbenv`, `pyenv`, `rustup`, etc. all rolled into one.

> You define what you need in `.tool-versions`. It handles the rest.

## 🧙‍♂️ The Magic of Shims

`asdf` installs a lightweight shim for every executable you install via a plugin. These shims are tiny wrapper scripts that intercept calls to things like `node`, `python`, or `java`, and transparently redirect them to the correct version based on your current directory.

That means you can have:

- Node 20 for one project,
- Python 3.10 for another,
- and Ruby 2.7 in production scripts...

...all working cleanly and automatically based on the local `.tool-versions` file. No manual switching.

## 📁 Files

- `asdf.zsh`  
  Loads asdf into your shell if it's installed:
  ```zsh
  if [ -f "$HOME/.asdf/asdf.sh" ]; then
    source "$HOME/.asdf/asdf.sh"
  fi

  if [ -f "$HOME/.asdf/completions/asdf.bash" ]; then
    fpath+=("${HOME}/.asdf/completions")
    autoload -Uz compinit && compinit
  fi

---

🧩 Return to [dotfiles root](../README.md) for setup instructions and tool list.