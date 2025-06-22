# Load all secrets in ~/.zsh/secrets
[[ -d ~/.zsh/secrets ]] && for file in ~/.zsh/secrets/*.zsh; do
  [ -f "$file" ] && source "$file"
done
