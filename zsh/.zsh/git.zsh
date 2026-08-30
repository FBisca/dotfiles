# ── git checkout, worktree-aware ────────────────────────────────────────────
# Overrides oh-my-zsh's `alias gco='git checkout'`.
#
# `gco <branch>` — if <branch> is currently held by another worktree, git
# refuses the checkout ("already checked out at ..."). This removes that
# worktree first, then checks the branch out here. A clean worktree goes
# without ceremony; a dirty one shows its changes and asks before forcing.
#
# Anything that isn't a plain `gco <branch>` (flags, paths, `--`) is handed
# straight to `git checkout` untouched.

unalias gco 2>/dev/null

# Print the worktree path holding $1, or return 1 if no worktree holds it.
_gco_worktree_for() {
  local branch="$1" wtpath="" line
  while IFS= read -r line; do
    if [[ "$line" == worktree\ * ]]; then
      wtpath="${line#worktree }"
    elif [[ "$line" == "branch refs/heads/$branch" ]]; then
      printf '%s\n' "$wtpath"
      return 0
    fi
  done < <(git worktree list --porcelain)
  return 1
}

gco() {
  git rev-parse --git-dir >/dev/null 2>&1 || {
    echo "gco: not a git repository" >&2
    return 1
  }

  local branch=""
  if [[ $# -eq 1 ]]; then
    if [[ "$1" == "-" ]]; then
      branch="$(git rev-parse --symbolic-full-name '@{-1}' 2>/dev/null)"
      branch="${branch#refs/heads/}"
    elif [[ "$1" != -* ]]; then
      branch="$1"
    fi
  fi

  # Only an existing local branch can be pinned by a worktree.
  if [[ -z "$branch" ]] || ! git show-ref --verify --quiet "refs/heads/$branch"; then
    git checkout "$@"
    return $?
  fi

  local wt
  wt="$(_gco_worktree_for "$branch")" || {
    git checkout "$@"
    return $?
  }

  # We're already standing in it — nothing to evict.
  if [[ "${wt:A}" == "${$(git rev-parse --show-toplevel):A}" ]]; then
    git checkout "$@"
    return $?
  fi

  # Worktree directory is gone; just clear the stale registration.
  if [[ ! -d "$wt" ]]; then
    echo "gco: pruning stale worktree $wt"
    git worktree prune
    git checkout "$@"
    return $?
  fi

  local -a force=()
  local dirty
  dirty="$(git -C "$wt" status --porcelain 2>/dev/null)"
  if [[ -n "$dirty" ]]; then
    echo "gco: worktree $wt has uncommitted changes:" >&2
    printf '%s\n' "$dirty" >&2
    if [[ ! -t 0 ]]; then
      echo "gco: refusing to remove a dirty worktree non-interactively" >&2
      return 1
    fi
    local reply
    read -r "reply?Remove anyway? [y/N] "
    [[ "$reply" == [yY]* ]] || { echo "gco: aborted" >&2; return 1 }
    force=(--force)
  fi

  git worktree remove "${force[@]}" "$wt" || {
    echo "gco: could not remove worktree $wt" >&2
    return 1
  }
  echo "gco: removed worktree $wt"

  git checkout "$@"
}
