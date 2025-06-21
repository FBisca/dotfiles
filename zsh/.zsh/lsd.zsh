# Ensure `lsd` is available before aliasing
if command -v lsd &> /dev/null; then
  alias ls='lsd --group-dirs=first'
  alias ll='ls -l'
  alias la='ls -a'
  alias lla='ls -la'
  alias lt='ls --tree'
fi