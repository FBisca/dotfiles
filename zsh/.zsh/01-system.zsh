# ~/.dotfiles/zsh/.zsh/01-system.zsh
# macOS system setup

# Set default editor
export EDITOR=nvim
export VISUAL=nvim

# macOS-specific aliases and settings
alias ls='ls -G'  # Enable colorized output on macOS
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

