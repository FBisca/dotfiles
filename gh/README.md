# 🧩 gh

This directory contains shell integration for [`gh`](https://cli.github.com/), the GitHub CLI. If you’re doing anything serious with GitHub, `gh` makes life better — from cloning, creating issues, checking out PRs, even running workflows.

## ✅ Assumptions

* You have `gh` installed. If not, install it:
  [https://github.com/cli/cli#installation](https://github.com/cli/cli#installation)
* You’re authenticated.
  Run `gh auth login` and follow the prompts. We assume HTTPS mode, not SSH (though SSH also works fine if you prefer).

## 📁 Files

This directory may include:

* `config.yml` – General preferences like default protocol, editor, aliases, etc.
* `hosts.yml` – Your GitHub credentials and tokens (⚠️ **Never commit this. It's in `.gitignore`**).

## ⚠️ Security

If you’re using the GitHub CLI with HTTPS authentication, it will store your personal access token (PAT) in `hosts.yml`. That file **must never be committed** to version control — this repo ignores it by default via:

```gitignore
.gh/hosts.yml
```

Use `gh auth status` to verify your auth, and `gh auth logout` if needed.

## 🧠 Pro Tips

* Want to check out a PR by number?

  ```sh
  gh pr checkout 42
  ```
* Want to create a PR?

  ```sh
  gh pr create --fill
  ```
* Trigger GitHub Actions manually:

  ```sh
  gh workflow run build.yml
  ```
* Clone a repo from the terminal like a wizard:

  ```sh
  gh repo clone owner/repo
  ```

## 🚫 Don't Track Credentials

We place overrides in `gh/.config/gh/hosts.yml`, and `.gitignore` ensures it won't be committed. If you're setting up from scratch, it's safe to run:

```sh
gh auth login
```

Just make sure your token has the scopes:
`repo`, `read:org`, and `workflow`.

---

🧩 Return to [dotfiles root](../README.md) for setup instructions and tool list.
