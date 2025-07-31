# ~~~~~~~~~~ Path configuration ~~~~~~~~~~
setopt extended_glob null_glob

path=(
  $HOME/.local/bin                            # rc aliases need to come first
  $HOME/bin
  $path                                       # Keep existing PATH
  $HOME/.local/share/mise/bin
  $HOME/.cargo/bin
  $HOME/.fzf/bin
  $HOME/.local/lib/npm-global/bin

  # dev tools
  $HOME/dev/apps/jetbrains-toolbox-2.7.0.48109/bin
  $HOME/.fly/bin

  # mise-installed tools (explicitly listed)
  $HOME/.local/share/mise/installs/cargo-eza/0.22.0/bin
  $HOME/.local/share/mise/installs/cargo-bat/0.25.0/bin
  $HOME/.local/share/mise/installs/cargo-git-delta/0.18.2/bin
  $HOME/.local/share/mise/installs/cargo-rage/0.11.1/bin
  $HOME/.local/share/mise/installs/cargo-ripgrep/14.1.1/bin
  $HOME/.local/share/mise/installs/cargo-fd-find/10.2.0/bin
  $HOME/.local/share/mise/installs/cargo-ncspot/1.2.2/bin
  $HOME/.local/share/mise/installs/node/22.14.0/bin
  $HOME/.local/share/mise/installs/npm-commitizen/4.3.1/bin
  $HOME/.local/share/mise/installs/terraform/1.11.4
  $HOME/.local/share/mise/installs/zig/0.14.1/bin
  $HOME/.local/share/mise/installs/fzf/0.64.0

  # Homebrew (if used)
  /home/linuxbrew/.linuxbrew/bin
  /home/linuxbrew/.linuxbrew/sbin

  # Core system paths
  /usr/local/sbin
  /usr/local/bin
  /usr/sbin
  /usr/bin
  /sbin
  /bin

)

typeset -U path
path=($^path(N))    # Deduplicate and skip nonexistent dirs

export PATH


# Utility function to echo the path
path() {
  local i=1
  for p in ${(s/:/)PATH}; do
    printf "%2d: %s\n" $i "$p"
    ((i++))
  done
}

