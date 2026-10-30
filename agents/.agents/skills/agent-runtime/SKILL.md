---
name: agent-runtime
description: Runtime contract for delegating to other agents: resolve the runtime, then load its contract and adapter. Use before spawning, messaging or waiting on other agents.
---

# Agent runtime

Run `agent-runtime resolve [--cli claude|codex] [--json]` before delegating. It prints one line, `runtime=<herdmates|hc|native> role=<lead|worker|unknown> [parent=<id>] cli=<claude|codex>`, and always exits 0.

- `HERDR_PANE_ID` set: `herdmates` for Claude, `native` for Codex.
- Else `HC_TERMINAL_ID` set: `hc`; `role` comes from `hc get` (parent null: lead, else worker). A failed or slow `hc get` gives `role=unknown`.
- Else `native`.

`contract`, `help` and `status` arrive in later commands.
