# ~~~~~~~~~~ Path configuration ~~~~~~~~~~
setopt extended_glob null_glob

path=(
  $HOME/bin
  $path                                       # Keep existing PATH
  $HOME/.local/share/mise/bin
  $HOME/.cargo/bin
  $HOME/.fzf/bin
  $HOME/.local/lib/npm-global/bin

  # Node.js package managers
  $HOME/Library/pnpm

  # mise-installed tools (dynamic paths)
  $HOME/.local/share/mise/installs/*/bin
  $HOME/.local/share/mise/installs/*/current/bin

  # Flutter paths
  $HOME/developer/flutter/bin

  # Homebrew paths
  /opt/homebrew/bin
  /opt/homebrew/sbin

  # Core system paths
  /usr/local/bin
  /usr/bin
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

