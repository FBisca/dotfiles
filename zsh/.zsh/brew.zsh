# Suppress analytics
export HOMEBREW_NO_ANALYTICS=1

# Speed up updates
export HOMEBREW_NO_AUTO_UPDATE=1

# Don't nag about missing developer tools
export HOMEBREW_NO_ENV_HINTS=1

# Avoid writing to system directories (just in case)
export HOMEBREW_NO_INSTALL_CLEANUP=1

# Silence brew doctor if you don’t care
# export HOMEBREW_NO_EMOJI=1

# Ensure everything resolves through Linuxbrew in WSL
export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
export PATH="/home/linuxbrew/.linuxbrew/sbin:$PATH"
export MANPATH="/home/linuxbrew/.linuxbrew/share/man:$MANPATH"
export INFOPATH="/home/linuxbrew/.linuxbrew/share/info:$INFOPATH"

# Initialize Homebrew environment (Linuxbrew path setup for WSL)
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
