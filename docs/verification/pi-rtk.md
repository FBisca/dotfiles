# Pi RTK: manual acceptance record

The RTK checks need the real machine (the `rtk` binary and an authorised provider), so they are run by hand and recorded here. The checklist itself lives in the [README](../../README.md#manual-checks); this file is what the last run found.

## Run of 2026-11-07

Machine: macOS, Pi 1.5.0 at `~/.pi/agent/bin/pi`, `rtk` 1.1.0 at `/opt/homebrew/bin/rtk`, repository `~/developer/dotfiles` at `fe65444` (PR #16).

| Check | Command | Result |
|---|---|---|
| The binary is installed | `rtk --version` | `rtk 1.1.0` |
| The package is installed for Pi | `pi list` | `npm:pi-rtk-optimizer@0.9.0` at `~/.pi/agent/npm/node_modules/pi-rtk-optimizer` |
| The package is declared in the tracked base | `agents/.pi/settings.base.json` | `"packages": ["npm:pi-rtk-optimizer@0.9.0"]`; Pi installs a declared package at its next start |
| The installer reports the prerequisite | `./install.sh --pi-only` | `rtk found at /opt/homebrew/bin/rtk (rtk 1.1.0)` and `Pi installs these packages at its next start: npm:pi-rtk-optimizer@0.9.0` |
| A bash command is rewritten | `pi -p --mode json "run git status"` in this repository | the tool result is rtk's compact output (`* feat/pi-lead-support...origin/feat/pi-lead-support`, `clean — nothing to commit`) instead of git's `On branch …` |
| The saving is real | `RTK_DB_PATH="$TMPDIR/pi-rtk-optimizer/history.db" rtk gain --history` | 52 commands, 13.4K input tokens in, 5.1K out, saved 8.3K (62.2%), 10 ms average per command |

The live check is automated behind a flag, so the next machine can repeat it instead of guessing:

```sh
PI_LIVE=1 python3 -B -m unittest discover -s tests -p test_pi_acceptance.py
```

## What is still open

- The rewrite is invisible in the `tool_execution_start` event: Pi reports the arguments the model asked for, and the rewrite happens on the arguments that are executed. The check therefore reads the tool **result**, not the tool call, and `rtk rewrite "<command>"` is the direct way to see a rewrite.
- The package's `peerDependencies` name Pi `0.74`–`0.80` while this machine runs `1.5.0`. Pi installs managed packages with `--legacy-peer-deps`, so the install succeeds and the extension loads; the pin is ours to bump when a newer release lands.
- rtk's own analytics live under the database path the package sets per command (`$TMPDIR/pi-rtk-optimizer/history.db`), not under the default `~/.local/share/rtk`, so `rtk gain --history` needs `RTK_DB_PATH` to read them.
- The package's configuration is the user's own file, `~/.pi/agent/extensions/pi-rtk-optimizer/config.json`; it is not tracked here, because it holds machine-specific choices.
- Blocking dangerous commands is not part of this record. Pi has no permission prompts, so that gap is still open.
