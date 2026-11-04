# ~/.zshenv: sourced by every zsh, including non-interactive, non-login shells (agent tool
# shells, `zsh -c`, scripts). Keep it to PATH; interactive setup lives in ~/.zshrc.

# mise shims first, so project-pinned tool versions (.node-version, .tool-versions,
# mise.toml) win over Homebrew's. The shims work without `mise activate`.
if [[ -d "$HOME/.local/share/mise/shims" ]]; then
  path=("$HOME/.local/share/mise/shims" $path)
fi

# Binaries from `cargo install`, e.g. rastro, which the agent tools launch as an MCP server.
if [[ -d "$HOME/.cargo/bin" ]] && (( ! ${path[(Ie)$HOME/.cargo/bin]} )); then
  path+=("$HOME/.cargo/bin")
fi

# Machine-only additions, never tracked.
if [[ -f "$HOME/.zshenv.local" ]]; then
  source "$HOME/.zshenv.local"
fi
