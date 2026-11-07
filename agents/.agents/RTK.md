# RTK

In Pi, every `bash` command is rewritten through [rtk](https://github.com/rtk-ai/rtk) before it runs, and the output comes back compacted.

**What that means for you.**

- The output you see is rtk's, not the tool's. `git status` prints `* branch...origin/branch` and `clean — nothing to commit`; `npm test` prints the failures and a count, not every passing test. Read it as authoritative but abbreviated.
- The command you asked for is still the command that ran, with a different formatter. `rtk rewrite "<command>"` shows the rewrite without running it.
- Savings per command are recorded by rtk itself:

```sh
RTK_DB_PATH="$TMPDIR/pi-rtk-optimizer/history.db" rtk gain --history
```

- When the `rtk` binary is missing, Pi runs every command unchanged. Nothing breaks; the output is just the raw one.

**Outside Pi**, this file changes nothing: Claude Code and Codex run the plain tools.
