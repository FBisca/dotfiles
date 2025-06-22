if [ -n "$TTY" ] || tty &>/dev/null; then
  export GPG_TTY=$(tty)
fi

