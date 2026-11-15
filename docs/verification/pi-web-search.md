# Pi web search: manual acceptance record

The web search checks need the real machine (the `pi-web-search-lite` package and an authorised Exa key), so they are run by hand and recorded here. The checklist itself lives in the [README](../../README.md#manual-checks); this file is what the last run found.

## Run of 2026-11-15

Machine: macOS, Pi 1.5.2 at `~/.pi/agent/bin/pi`, `pi-web-search-lite` 0.13.1, repository `~/developer/dotfiles` at `5a3f9dd`.

| Check | Command | Result |
|---|---|---|
| The package is installed for Pi | `pi list` | `npm:pi-web-search-lite` at `~/.pi/agent/npm/node_modules/pi-web-search-lite` |
| The package is declared in the tracked base | `agents/.pi/settings.base.json` | `"packages": [..., "npm:pi-web-search-lite"]` and `"defaultTools": ["+tool_search"]` |
| The installer writes the extension's own config | `./install.sh --pi-only` | `Pi web search config ready at /Users/fbisca/.pi/agent/pi-web-search-lite/config.json` |
| The key is a reported prerequisite | `./install.sh --pi-only` | `Pi web search key: EXA_API_KEY is set in the environment` (the value is never printed) |
| The tools are found on demand | `pi -p "use web_search to find the current stable version of the python programming language"` | the model called `web_search` and `web_fetch` without them being in the starting tool list: `tool_search` declared them |
| The search reaches Exa | same run | `web_search: 5 results (provider: exa, max_results: 5)`, with python.org among the results |
| The fetch spills instead of flooding | same run | `details.fullOutputPath` pointed at `/tmp/pi-web-search-lite-*/web-fetch.md` (21 718 characters fetched, 1 895 inlined) |

The live check is a manual command, since it spends a provider call:

```sh
pi -p "use web_search to find the current stable version of the python programming language, then tell me only the version number"
```

## What is still open

- The key lives in the zsh secrets (`~/.zsh/secrets/secrets.zsh`) and is exported from there, so it reaches Pi only from an interactive shell. A script that starts Pi without that environment has no key and the extension reports it.
- The tracked defaults keep the results small (3 by default, 5 at most) and the inline text at 4 000 characters; a longer answer is written to a temporary file that the model reads with `read`. The temporary directory is the extension's own, not the repository's.
- The other providers (tavily, brave, firecrawl, perplexity, parallel, keenable, deepseek) are available in the extension and unused here: switching is a change in the user's own config file, and the installer merges the tracked defaults under it.
