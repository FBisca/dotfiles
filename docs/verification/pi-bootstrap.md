# Pi bootstrap: manual acceptance record

The Pi checks need the real machine and an authorised provider, so they are run by hand and recorded here. The checklist itself lives in the [README](../../README.md#manual-checks); this file is what the last run found.

## Run of 2026-11-07

Machine: macOS, Pi 1.5.0 at `~/.pi/agent/bin/pi`, repository `~/developer/dotfiles` at `40ca070` (PR #15).

| Check | Command | Result |
|---|---|---|
| Pi is installed | `pi --version` | `1.5.0` |
| The credential resolves | `pi auth check --provider minimax --model MiniMax-M3.1-Flash` | `ready` (the key comes from `MINIMAX_API_KEY` in the shell) |
| The installer sets Pi up | `./install.sh --pi-only` | `Pi settings ready at ~/.pi/agent/settings.json` (the previous file was saved as `settings.json.bak-20261107…`), `Pi discovers 38 skill(s)`, `Pi skill ready: start-planning`, `Pi skill ready: grilling` |
| The skills are found | `pi -p "/skill:start-planning"` in a scratch repo | the skill loaded from `~/.agents/skills/start-planning` and ran its planning flow |
| The bounded edit | `pi -p --mode json --provider minimax --model MiniMax-M3.1-Flash "Fix calc.py…"` in a disposable git repo | the file was edited in one `edit` tool call, 4.0 s wall clock, no tool call repeated |
| No runtime tool in Pi | `pi mcp list` | `No MCP servers configured`; `~/.pi/agent/mcp.json` does not exist |

The live smoke is automated behind a flag, so the next machine can repeat it:

```sh
PI_LIVE=1 python3 -B -m unittest discover -s tests -p test_pi_acceptance.py
```

## What is still open

- `pi auth check` proves that the credential resolves, and the smoke proves that the API call is authorised and billed by the provider. Whether the MiniMax plan's subscription covers this API usage, rather than a separate balance, cannot be observed from the client side.
- `grilling` is present on this machine (it comes from `agent-skills`); the installer reports it as missing on a machine that has not installed it, which is the intended behaviour.
- Pi itself warns about `Nested mappings are not allowed in compact mappings` in some installed skills. That is pre-existing in `agent-skills` and out of scope here.
