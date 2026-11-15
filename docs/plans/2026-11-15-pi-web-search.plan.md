# Plan: Web Search for Pi

Slug: `pi-web-search`. Living spec: `docs/specs/agent-environments.md`. Status: COMPLETE 2026-11-15.

## Why now

Pi is the harness this repo configures for daily work, and it has no way to reach the web: the model knows what it was trained on and nothing else. The `pi-web-search-lite` extension gives it `web_search` and `web_fetch` with a configurable provider, and it keeps the tools out of the context until they are needed (`activation: deferred` plus Pi's own `tool_search` discovery).

The setup is machine-independent except for the key: the extension reads `EXA_API_KEY` from the environment, the zsh secrets already hold it, and no tracked file may ever carry it.

## Sources

| Source | What it settles |
|---|---|
| User request, 2026-11-15 | Install `pi-web-search-lite` for Pi, use the Exa provider, discover the tools on demand, keep the key in the zsh secrets. |
| https://www.npmjs.com/package/pi-web-search-lite | The package name, the `pi install npm:pi-web-search-lite` install line, the two tools and the eight search providers. |
| https://github.com/setwhite/pi-extensions/tree/main/packages/pi-web-search-lite#readme | The one config file (`<pi agent dir>/pi-web-search-lite/config.json`), its keys, the environment variables that override it and the strict-JSON requirement. |
| https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md | `defaultTools` with `+name` entries changes the inherited selection instead of replacing it; `tool_search` is a built-in tool that is off by default. |
| dotfiles `install.sh`, `agents/.pi/settings.base.json` | Where Pi's preferences live and how the tracked base is merged under the user's own file. |

## Decisions

| # | Choice | Rejected | Why | Source |
|---|---|---|---|---|
| D1 | The extension's config lives in the tracked base (`agents/.pi/pi-web-search-lite.config.json`) and the installer merges it under the user's file. | A hand-written file in `~/.pi` that only this machine has. | A new machine gets the same setup from `./install.sh`, and the user's own choices still win. | dotfiles install.sh; extension README |
| D2 | The search key stays in the environment (`EXA_API_KEY`), never in a tracked file and never in the extension's config. | `apiKeys.exa` in the config file. | The config file is generated from a tracked base; a key in it would leak into the repo. The extension reads the environment first anyway. | extension README; spec R4 |
| D3 | The tools are declared `deferred` and Pi's `tool_search` is enabled. | `eager`, both tools always in the context. | Search results are long; the extension spills the full text to a file and the model reads it only when it needs to. | extension README; Pi settings docs |
| D4 | The installer reports the key as a prerequisite and never writes it. | Writing the key into the config or failing the install without it. | The installer never writes credentials, and a missing key must not fail a setup that is otherwise fine. | dotfiles README; spec R4 |

## Scenarios

- **S1** WHEN the installer sets Pi up, THEN the tracked Pi base declares the `npm:pi-web-search-lite` package and enables `tool_search`, so the extension's tools are found when the model needs them.
- **S2** WHEN the installer sets Pi up, THEN `~/.pi/agent/pi-web-search-lite/config.json` carries the tracked defaults (exa provider, deferred activation, 3 results, 4000 inline characters, 100 inline lines, spill to file), the user's own values in that file win over the tracked ones, and a rerun changes nothing.
- **S3** WHEN the live web-search configuration is not valid JSON, THEN it is backed up and left untouched.
- **S4** WHEN the Pi configuration is installed, THEN no search credential appears in a tracked file, the key is read from the environment, and a missing `EXA_API_KEY` is reported without failing the install.
- **S5** WHEN Pi starts with the tracked base settings, THEN it installs the declared package and the extension's `web_search` and `web_fetch` tools are discoverable through `tool_search`.

## Out of scope

- Other search providers, a proxy, the fetch extractor chain and the guidance overrides: the tracked defaults leave them alone.
- Web search for Claude Code and Codex: they have their own tools and their own configuration.
- The key's storage: it stays where the user put it, in the zsh secrets.

## Risks

- **Security:** the config file is generated and the key is not in it; a tracked file that carried the key would leak it.
- **Cost:** a search key is a billable credential; the defaults keep the number of results small.
- **Context:** the tools are declared on demand, so the model's context does not carry the extension's schema unless it searches.

## Seams

- Installer behaviour: `tests/test_pi_web_search.py` runs `install.sh` against a temporary `HOME`, like the other Pi tests.
- Resource discovery: `pi list` shows the package, `pi -p` finds the tools through `tool_search`.

## Tickets

| # | What it delivers | Satisfies | Blocked by | Paths | Size | Difficulty | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| T1 | Declare the package and enable `tool_search` in the tracked Pi base. | S1, S5 | none | `agents/.pi/settings.base.json` | small | simple | agent | DONE |
| T2 | Track the extension's config defaults and have the installer merge them under the user's file, with the backup and the untouched-invalid-file behaviour. | S2, S3 | T1 | `agents/.pi/pi-web-search-lite.config.json`, `install.sh` | regular | simple | agent | DONE |
| T3 | Report the `EXA_API_KEY` prerequisite without writing the key. | S4 | T2 | `install.sh` | small | simple | agent | DONE |
| T4 | Cover the new behaviour with installer tests and record the requirements in the living spec. | S1, S2, S3, S4 | T2, T3 | `tests/test_pi_web_search.py`, `docs/specs/agent-environments.md` | regular | simple | agent | DONE |
| T5 | Install the package on the real machine, export the key from the zsh secrets and record the manual acceptance. | S5 | T4 | `docs/verification/pi-web-search.md`, `README.md` | small | simple | user | DONE (2026-11-15: package installed, `EXA_API_KEY` exported from the zsh secrets, one live search returned Exa results) |
