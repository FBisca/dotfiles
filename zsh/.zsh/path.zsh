# ~~~~~~~~~~ Path configuration ~~~~~~~~~~
setopt extended_glob null_glob

path=(
  $path                                       # Keep existing PATH
  $HOME/.local/share/mise/bin
  $HOME/.local/bin
  $HOME/bin
  $HOME/.cargo/bin
  $HOME/.fzf/bin

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

  # WSL interop
  /usr/lib/wsl/lib
  /mnt/c/WINDOWS/system32
  /mnt/c/WINDOWS
  /mnt/c/WINDOWS/System32/Wbem
  /mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/
  /mnt/c/WINDOWS/System32/OpenSSH/
  /mnt/c/Program Files/NVIDIA Corporation/NVIDIA App/NvDLISR
  /mnt/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common
  /mnt/c/Program Files/whkd/bin/
  /mnt/c/Program Files/komorebi/bin/
  /mnt/c/Program Files/Docker/Docker/resources/bin
  /mnt/c/Program Files/YASB/
  /mnt/c/Program Files/dotnet/
  /mnt/c/Users/Rodrigo/AppData/Local/Programs/cursor/resources/app/bin
  /mnt/c/Users/Rodrigo/AppData/Local/Microsoft/WindowsApps
  /mnt/c/Users/Rodrigo/AppData/Local/JetBrains/Toolbox/scripts
  /mnt/c/Users/Rodrigo/AppData/Local/Programs/Microsoft VS Code/bin
  /mnt/c/Users/Rodrigo/.dotnet/tools
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

