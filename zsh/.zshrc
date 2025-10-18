# 🩹 Claude shell snapshot fixer
if [[ "$SNAPSHOT_FILE" == *snapshot-zsh-* && -n "$ZSH_VERSION" ]]; then
  {
    echo "# Patched snapshot"

    echo "# Functions"
    for func in ${(k)functions}; do
      echo "function $func() {"
      functions[$func]
      echo "}"
      echo
    done

    echo "# Shell Options"
    setopt | sed 's/^/setopt /'

    echo "# Aliases"
    alias | sed 's/^alias /alias -- /'

    echo "# PATH"
    echo "export PATH=\"$PATH\""
  } >| "$SNAPSHOT_FILE"

  # Make absolutely sure we stop here
  kill -INT $$
fi

# ── [Powerlevel10k Instant Prompt Guard for Cursor] ──
if [[ "$TERM_PROGRAM" == "vscode" || -n "$VSCODE_PID" ]]; then
  typeset -g POWERLEVEL9K_INSTANT_PROMPT=off
fi

# ── [Powerlevel10k Instant Prompt] ──
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ── [Oh My Zsh Core] ──
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# ── [Powerlevel10k Config] ──
[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh

# ── [Modular Zsh Config] ──
for file in ~/.zsh/*.zsh; do
  source "$file"
done


