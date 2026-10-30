---
name: agent-runtime
description: Runtime contract for delegating to other agents: resolve the runtime, then load its contract and adapter. Use before spawning, messaging or waiting on other agents.
---

# Agent runtime

Run `agent-runtime resolve [--cli claude|codex] [--json]` before delegating. It prints one line, `runtime=<herdmates|hc|native> role=<lead|worker|unknown> [parent=<id>] cli=<claude|codex>`, and always exits 0 (any error prints `runtime=native role=unknown`).

- `HERDR_PANE_ID` set: `herdmates` (role `unknown`: teammate panes are not distinguishable yet) for Claude, `native` for Codex.
- Else `HC_TERMINAL_ID` set: `hc`; `role` comes from `hc get` (parent null: lead, a plain id: worker). A failed, slow or malformed `hc get` gives `role=unknown`.
- Else `native`.

`contract`, `help` and `status` arrive in later commands.
