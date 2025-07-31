# ~/.dotfiles/zsh/.zsh/01-fedora.zsh
# Fedora-specific setup

# If 'batcat' exists and 'bat' does not, alias it
if ! command -v bat >/dev/null && command -v batcat >/dev/null; then
  alias bat="batcat"
else
  # Otherwise, make sure no broken alias remains
  unalias bat 2>/dev/null
fi

export EDITOR=nvim
export VISUAL=nvim

