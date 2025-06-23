if tty -s; then
  export GPG_TTY=$(tty)
else
  # fallback, adjust if needed
  export GPG_TTY=/dev/pts/0
fi

