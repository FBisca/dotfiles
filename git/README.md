# Git Config

This is my shared, modular Git configuration, managed with [GNU Stow](https://www.gnu.org/software/stow/).

It’s clean, public, and free of personal identity — ready to be dropped onto any machine or shared with collaborators.

---

## 🧼 What This Is

* ✅ **Safe to share**: no name, no email, no GPG keys
* 🧠 **Curated**: useful aliases, smart defaults, and powerful patterns
* 🧩 **Modular**: identity and per-project settings handled via `includeIf`

---

## 🔐 Private Identity with `includeIf`

This config uses Git’s `[includeIf]` directive to cleanly separate personal or sensitive data.

It includes this block:

```ini
[includeIf "gitdir:~/"]
  path = ~/.config/git/config.local
```

This automatically loads a personal file (`config.local`) when you're in your home directory (or anywhere under it).
You should create `~/.config/git/config.local` with your identity:

```ini
[user]
  name = Your Name
  email = your@email.com
  signingkey = YOURKEYID

[commit]
  gpgsign = true

[gpg]
  program = gpg

[credential]
  helper = /usr/local/bin/git-credential-manager
```

Want different configs for work and personal projects?

```ini
[includeIf "gitdir:~/projects/work/"]
  path = ~/.config/git/work.gitconfig

[includeIf "gitdir:~/projects/personal/"]
  path = ~/.config/git/personal.gitconfig
```

This allows Git to auto-switch identities and settings based on the project path.

To test what Git is actually loading:

```bash
git config --show-origin --list
```

---

## 🧪 Git Aliases

Here’s a full list of the aliases included in this config:

| Alias                             | Command                                     | Description                          |
| --------------------------------- | ------------------------------------------- | ------------------------------------ |
| `l`                               | `log --graph ...`                           | Pretty graph of last 30 commits      |
| `s`                               | `status -s`                                 | Short status format                  |
| `d`                               | `diff`                                      | Show unstaged changes                |
| `di 2`                            | `diff HEAD~2`                               | Diff from 2 commits ago              |
| `p`                               | `pull --recurse-submodules`                 | Pull everything including submodules |
| `c`                               | `clone --recursive`                         | Clone a repo with submodules         |
| `ca`                              | `add -A && commit -av`                      | Add and commit all changes           |
| `go <branch>`                     | Checkout or create branch                   |                                      |
| `tags`                            | `tag -l`                                    | List tags                            |
| `branches`                        | `branch -a`                                 | List local and remote branches       |
| `remotes`                         | `remote -v`                                 | Show remote URLs                     |
| `aliases`                         | `config --get-regexp alias`                 | List all aliases                     |
| `amend`                           | `commit --amend --reuse-message=HEAD`       | Amend current commit                 |
| `credit "Name" email@example.com` | Amend commit author                         |                                      |
| `reb 5`                           | `rebase -i HEAD~5`                          | Interactive rebase of last 5 commits |
| `retag v1.0.0`                    | Delete and recreate a tag                   |                                      |
| `fb <hash>`                       | Show branches containing a commit           |                                      |
| `ft <hash>`                       | Show tags containing a commit               |                                      |
| `fc <code>`                       | Search commits by code content              |                                      |
| `fm <msg>`                        | Search commits by message                   |                                      |
| `dm`                              | Delete merged branches                      |                                      |
| `contributors`                    | List contributors by commit count           |                                      |
| `all <cmd>`                       | Run any Git command across all nested repos |                                      |
| → `git all pull`                  | Pull all nested Git repos                   |                                      |
| → `git all status`                | Show status in all nested Git repos         |                                      |

---

## 🎨 UX Defaults

This config also includes:

* 🎨 **Delta** as the default pager for better diffs
* 🔸 Colorized branch, diff, and status output
* ⚔️ `merge.conflictstyle = diff3` for better conflict resolution
* 🚀 `pull.rebase = true` for cleaner history
* ⬆️ `push.followTags = true` for tag-aware pushes

---

## 💥 Final Thoughts

This config is designed to be elegant, extensible, and safe — whether you're spinning up a new dev box or sharing setup ideas with friends.

Use it, tweak it, fork it. Just don’t add your name and email to the wrong file 😉.

---

🧩 Return to [dotfiles root](../README.md) for setup instructions and tool list.