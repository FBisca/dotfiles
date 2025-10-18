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

# macOS Homebrew paths
export PATH="/opt/homebrew/bin:$PATH"
export PATH="/opt/homebrew/sbin:$PATH"
export MANPATH="/opt/homebrew/share/man:$MANPATH"
export INFOPATH="/opt/homebrew/share/info:$INFOPATH"

# Initialize Homebrew environment
eval "$(/opt/homebrew/bin/brew shellenv)"
