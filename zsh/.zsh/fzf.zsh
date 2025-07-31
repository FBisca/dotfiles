# Homebrew-installed fzf integration
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# FZF config
export FZF_DEFAULT_COMMAND="fd --type f"
export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --preview '~/.config/fzf/preview.sh {}'"

# Rebind fzf-cd-widget to Ctrl+G
if (( $+widgets[fzf-cd-widget] )); then
  bindkey '^G' fzf-cd-widget
  bindkey -r '^[c'
fi

