# asdf runtime + completions
. "$HOME/.asdf/asdf.sh"
. "$HOME/.asdf/completions/asdf.bash"

# ensure installed binaries from Rust are accessible
if command -v asdf &>/dev/null && asdf where rust &>/dev/null; then
  export PATH="$(asdf where rust)/bin:$PATH"
fi

