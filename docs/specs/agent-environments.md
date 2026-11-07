# Agent environments

Paths: install.sh, agents/.pi/, agents/.stow-local-ignore, tests/test_pi.py, tests/test_pi_acceptance.py, docs/verification/pi-rtk.md, README.md

The dotfiles installer owns one machine's agent environments. Claude Code and Codex are configured from `agents/.claude/settings.base.json` and `agents/.codex/config.base.toml`; Pi is configured from `agents/.pi/settings.base.json`. Each one is a tracked base merged with an optional private overlay and, for Claude Code and Codex, with the live file, so the user's own keys always win. The installer never writes credentials: they stay in the tool's own credential store, in the environment or in the private overlay.

Skills are shared, not forked: the installer symlinks them into `~/.agents/skills`, which Pi discovers natively, and reports the skills it found and the ones that are missing. A missing skill is a reported prerequisite, never an invented one.

Pi has no permission prompts, so the mutating `agent-runtime` MCP server is removed from `~/.pi/agent/mcp.json` (other servers stay, the previous file is backed up) until a safety adapter is approved.

Pi's RTK optimizer is declared in the tracked base settings as the package `npm:pi-rtk-optimizer@0.9.0`, so Pi installs it at its next start and rewrites every bash command through the `rtk` binary, which prints the compact form of git, build and test output. The binary is a prerequisite this repo never installs: the installer detects it and reports the `brew install rtk` line when it is missing, and every command still runs unchanged without it.

## Requirements

- **R1** WHEN the published Pi checklist runs on a machine with an authorised MiniMax provider, THEN a bounded edit in a disposable worktree completes without the model repeating the same tool call, and the outcome is recorded in `docs/verification/pi-bootstrap.md`. (from pi-bootstrap/S1)
- **R2** WHEN the installer runs on a machine that already has Claude Code or Codex configuration, THEN those files and the shared skill links are left unchanged, and a rerun is a no-op. (from pi-bootstrap/S2)
- **R3** WHEN Pi starts after the installation, THEN it discovers each installed managed skill by its canonical symlink, and the installer reports `start-planning` and `grilling` as ready or missing. (from pi-bootstrap/S3)
- **R4** WHEN the Pi configuration is installed, THEN no credential, subscription token or private endpoint appears in a tracked file or in the installer's output. (from pi-bootstrap/S4)
- **R5** WHEN the Pi configuration is installed, THEN the `agent-runtime` MCP server is not exposed to Pi and no mutating runtime tool is available there. (from pi-bootstrap/S5)
- **R6** WHEN Pi is not installed or no credential is authorised, THEN the installer reports the missing prerequisite and picks no provider of its own. (from pi-bootstrap/S6)
- **R7** WHEN the installer sets Pi up, THEN it reports the `rtk` binary it found, or the `brew install rtk` prerequisite when it is missing, and the packages Pi will install at its next start, and a missing `rtk` never fails the install. (from pi-rtk/S1)
- **R8** WHEN Pi starts with the tracked base settings, THEN it installs the declared `pi-rtk-optimizer` package and rewrites its bash commands through `rtk`, and every command still runs unchanged when `rtk` is missing. (from pi-rtk/S2)
