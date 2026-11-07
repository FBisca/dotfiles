# Agent environments

Paths: install.sh, agents/.pi/, agents/.stow-local-ignore, tests/test_pi.py, tests/test_pi_acceptance.py, README.md

The dotfiles installer owns one machine's agent environments. Claude Code and Codex are configured from `agents/.claude/settings.base.json` and `agents/.codex/config.base.toml`; Pi is configured from `agents/.pi/settings.base.json`. Each one is a tracked base merged with an optional private overlay and, for Claude Code and Codex, with the live file, so the user's own keys always win. The installer never writes credentials: they stay in the tool's own credential store, in the environment or in the private overlay.

Skills are shared, not forked: the installer symlinks them into `~/.agents/skills`, which Pi discovers natively, and reports the skills it found and the ones that are missing. A missing skill is a reported prerequisite, never an invented one.

Pi has no permission prompts, so the mutating `agent-runtime` MCP server is removed from `~/.pi/agent/mcp.json` (other servers stay, the previous file is backed up) until a safety adapter is approved.

The sandbox that guards Pi is configured the same way: `agents/.pi/sandbox.base.json` is the tracked base for the pi-sandbox extension and is merged into the global `~/.pi/agent/sandbox.json`. The live file is the user's own, because that is where the extension writes the grants a permission prompt approved, so base and overlay are merged under it. The installer never grants itself anything: a rule that the tracked base does not have stays behind a prompt.

The rules are autonomous — the agent is not stopped to ask — so the deny list is the safety net: no `.env`, no key and no credential file can be written, anywhere on the machine, and nothing else is blocked.

## Requirements

- **R1** WHEN the published Pi checklist runs on a machine with an authorised MiniMax provider, THEN a bounded edit in a disposable worktree completes without the model repeating the same tool call, and the outcome is recorded in `docs/verification/pi-bootstrap.md`. (from pi-bootstrap/S1)
- **R2** WHEN the installer runs on a machine that already has Claude Code or Codex configuration, THEN those files and the shared skill links are left unchanged, and a rerun is a no-op. (from pi-bootstrap/S2)
- **R3** WHEN Pi starts after the installation, THEN it discovers each installed managed skill by its canonical symlink, and the installer reports `start-planning` and `grilling` as ready or missing. (from pi-bootstrap/S3)
- **R4** WHEN the Pi configuration is installed, THEN no credential, subscription token or private endpoint appears in a tracked file or in the installer's output. (from pi-bootstrap/S4)
- **R5** WHEN the Pi configuration is installed, THEN the `agent-runtime` MCP server is not exposed to Pi and no mutating runtime tool is available there. (from pi-bootstrap/S5)
- **R6** WHEN Pi is not installed or no credential is authorised, THEN the installer reports the missing prerequisite and picks no provider of its own. (from pi-bootstrap/S6)
- **R7** WHEN the installer runs on a machine that uses the pi-sandbox extension, THEN the tracked sandbox base is merged into `~/.pi/agent/sandbox.json`, the grants already present in that live file survive, and no rule is granted without the user or a permission prompt. (from pi-sandbox/S7)
- **R8** WHEN the sandbox rules are in place, THEN the agent is never stopped to ask for a path or a domain, and every `.env`, `.env.*`, key and credential file is hard-blocked for writing, on any path of the machine. (from pi-sandbox/S8)
