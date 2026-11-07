# Plan: Pi Bootstrap with MiniMax and Shared Skills

Slug: `pi-bootstrap`. Living spec: `docs/specs/agent-environments.md`. Status: **APPROVED — READY FOR EXECUTION**.

## Why now

Pi must become usable **before** we improve the other repositories, because Pi + MiniMax M3.1 Flash will be used to implement the follow-on plans. A standalone, safe Pi session is the first deliverable; there is no dependency on the open `agent-runtime` worker-lifecycle PRs. The existing dotfiles installer already links every managed skill into `~/.agents/skills`, which Pi discovers natively. Do not duplicate or fork skills to bootstrap Pi.

**Preflight performed by the user (not part of code changes):** Install current Pi using the command published at https://pi.dev/ ; start Pi; use `/login` and `/model` to connect/select the existing MiniMax plan if the provider supports the subscription's API credentials. If the subscription does not authorize Pi, record the blocker and use an explicitly authorised alternative provider; do not assume the Claude Code credentials or quota can be reused. Select low reasoning only if supported by the chosen provider/model; do not infer API compatibility or quota portability from an existing Claude Code MiniMax plan.

## Sources

| Source | What it settles |
|---|---|
| User request, 2026-11-07 | Pi is the highest priority; preserve existing skills, use MiniMax as the trial model and use Pi to build the rest. |
| https://github.com/FBisca/dotfiles/blob/main/install.sh | `setup_skills` makes real `~/.agents/skills` directories and symlinks repo and private-overlay skills; installer manages Claude/Codex configuration. |
| https://github.com/FBisca/dotfiles/blob/main/README.md | Idempotent bootstrap, public-base + private overlay, non-destructive installs. |
| https://github.com/FBisca/agent-skills/blob/main/skills/start-planning/SKILL.md | Use plan format, dated path, scenario/ticket coverage and approval before builds. |
| https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/skills.md | Pi discovers `~/.agents/skills` and invokes skills using `/skill:name`. |
| https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/models.md | Built-in provider authentication via `/login`, model selection via `/model`; custom endpoints only if necessary. |
| https://pi.dev/ | Pi is a lightweight extensible harness; no default permission prompts and no built-in subagents. |
| https://github.com/FBisca/agent-runtime/pull/45 and https://github.com/FBisca/agent-runtime/pull/39 | Runtime session binding and resume attention have active work; avoid touching them during bootstrap. |

## Decisions

| # | Choice | Rejected | Why | Source |
|---|---|---|---|---|
| D1 | Bootstrap Pi as a standalone interactive CLI first. | Rebuild `agent-runtime` before Pi is usable. | The tool needed to build the migration must work without the later migration. | User request; Pi docs |
| D2 | Reuse `~/.agents/skills` in place. | Copy all skills into `~/.pi/agent/skills`. | Existing installer owns the links; Pi discovers them without duplication. | dotfiles install.sh; Pi skills docs |
| D3 | Keep machine credentials and provider endpoint in private local configuration or environment. | Commit subscription token or private endpoint. | Prevent leaks and preserve the private-overlay convention. | dotfiles README; Pi models docs |
| D4 | No mutating `agent-runtime` MCP connection in bootstrap. | Expose unguarded spawn/stop tools immediately. | Pi does not provide Claude's tool hooks or built-in permission prompts; safety needs an explicit adapter later. | agent-runtime README; Pi site |
| D5 | Preserve current Claude/Codex settings and install semantics. | Refactor common config into a new framework. | The goal is an additive, reversible tool bootstrap. | dotfiles README; user request |
| D6 | Keep the initial test on a disposable worktree/repo. | Validate by running unrestricted Pi against live work repos. | The first harness trial is unproven. | User's MiniMax looping report |

## Binding P0 contract — Q1–Q10, Q47–Q53

- **Smallest shippable slice:** independently installed Pi, explicit MiniMax authentication check, one code edit in a disposable worktree, discovered `start-planning` source, no `agent-runtime` mutation tools. Full fresh-context planning fidelity is **P1**, not P0.
- **Installer ownership:** `dotfiles/install.sh` manages only the user's Pi preferences and common skill links; official Pi distribution owns the executable, and the future product installer owns only `agent-runtime` integration. Never install the Pi executable from both places.
- **No implicit provider fallback:** subscription API eligibility, endpoint, model ID, reasoning-effort controls and quota are prerequisites to verify, not guarantees. Failure must not spend from another provider.
- **Bounded safety:** no destructive/publishing actions; manually supervised Pi on a disposable worktree; no ambient company account usage without explicit entitlement. If even the safe smoke cannot run, close P0 as blocked with diagnostics rather than bypassing controls.
- **Independent of runtime PRs:** do not wait for or edit #39/#45 here. Keep existing Claude/Codex setup byte-for-byte unless a user approves a specific change.

## Scenarios

- **S1** WHEN Pi is installed and configured with an authorised MiniMax endpoint, THEN the user can start an interactive session and obtain a successful simple code-edit response without repeatedly calling the same tool.
- **S2** WHEN dotfiles installation is rerun on a machine with existing Claude/Codex configuration, THEN neither those configurations nor existing skill directories are destroyed or rewritten unexpectedly.
- **S3** WHEN Pi starts after dotfiles installation, THEN Pi discovers each *actually installed* managed skill by canonical symlink and `/skill:start-planning` loads that source; if `grilling` is absent from the managed installation, bootstrap reports a missing prerequisite, not an invented bundled skill.
- **S4** WHEN the Pi config is installed, THEN no MiniMax credentials, subscription tokens or private host-specific endpoint strings appear in tracked dotfiles files or logs.
- **S5** WHEN Pi is started during bootstrap, THEN no agent-runtime mutating MCP tools are made available before a safety integration is approved.
- **S6** WHEN a new machine has missing Node/npm/Pi or unsupported credentials, THEN bootstrap reports a clear prerequisite/authorization error and does not silently fall back to another paid provider.

## Out of scope

- Modifying `agent-runtime` session identity, CLI profiles, Herdr lifecycle, PR #39/#45, Pi worker spawning, native subagents or the `orchestrate.py` state machine.
- Making every skill's Claude-specific `Skill`/Task tool semantics work in Pi; this is the next plan.
- Switching to DeepSeek, benchmarks and model routing policy changes.

## Risks

- **Security:** Pi may execute shell commands without interactive permission prompts; work from a disposable checkout, keep secrets outside tracked files and do not wire mutating MCP tools yet.
- **Performance:** MiniMax looping may persist across harnesses; keep the smoke task bounded by elapsed time/tool repetition and record failure without endless retries.
- **Migration:** Installer might overwrite or conflict with user-owned `~/.pi` files; use idempotent operations and backup/refuse conflicting files rather than destructive replacement.
- **Rollback:** Remove only added Pi config/links and stop using Pi; original Claude/Codex configuration remains intact.

## Seams

- Installer behavior: existing shell-install test harness at `tests/`, using a temporary `HOME` and fake binaries.
- Resource discovery: Pi CLI `pi --version`, interactive `/skill:start-planning`, and `/model` as manual acceptance checks.
- Config safety: tests assert no inline keys, no unwanted MCP mutation registrations, and idempotence.

## Tickets

| # | What it delivers | Satisfies | Blocked by | Paths | Size | Difficulty | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| T1 | Add an additive Pi configuration/bootstrap path that reuses existing skill links, handles already-present `~/.pi` safely, checks prerequisites and keeps provider-specific settings private. | S2, S3, S4, S5, S6 | none | `install.sh`, `agents/.pi/`, `README.md` | regular | simple | agent | TO-DO |
| T2 | Add offline installer tests for new-home, existing-home, repeated install, skills discovery paths, secret safety and unchanged Claude/Codex outputs. | S2, S3, S4, S5, S6 | T1 | `tests/`, `install.sh` | regular | simple | agent | TO-DO |
| T3 | Validate MiniMax subscription compatibility and complete a bounded Pi smoke run with discovered shared skills; explicitly record any unavailable `grilling` prerequisite without storing credentials. | S1, S3, S5, S6 | T2 | `README.md` |  |  | user | TO-DO |

**Ready-to-build handoff:** place this plan in the `dotfiles` checkout at `docs/plans/2026-11-07-pi-bootstrap.plan.md`, use the approved plan, and run `/orchestrate docs/plans/2026-11-07-pi-bootstrap.plan.md` from a currently working Claude/Codex lead **or** implement its small tickets directly in Pi after the manual preflight. The existing `orchestrate.py` does not yet support Pi as a `--cli` backend; do not claim otherwise.

## Installer ownership clarification (Q48 accepted; no expansion of P0 scope)

P0 continues to use the existing **dotfiles installer** for personal Pi configuration and shared skill discovery. The future public, selectable `agent-runtime/install.sh` is independently specified by P4c and **must not block Pi bootstrap**. Avoid installing Pi's executable or changing its credentials in both places; the official Pi installer remains authoritative for its binary.


## Execution preflight checklist

- [ ] Temporary HOME fixture test proves existing Claude/Codex symlinks and configs unchanged on second install.
- [ ] Pi installation/version, MiniMax credentials and subscription-specific API access are manually validated without logging secrets.
- [ ] One real edit/test in a disposable worktree completes within declared time/iteration budget, or is recorded as blocked.
- [ ] Existing `~/.agents/skills` source and `start-planning` discovery verified; absent separately installed `grilling` reported.
- [x] Owner approved this plan on 2026-11-07. **Implementation has not yet started.**
