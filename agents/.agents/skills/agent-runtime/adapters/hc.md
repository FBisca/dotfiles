# Adapter: hc

`$HC_TERMINAL_ID` is your address; terminals you start are your children and end when you end. Flags are from `hc <cmd> --help`; `hc --skill` has the manual.

- `spawn`: always `--bg`, a unique name (a-z 0-9 - _, max 32), task inside `run` (a later send can be dropped).
  - Claude: `hc run --bg --name <n> --cwd <dir> claude --agent implementer "<task>"`
  - Codex: `hc run --bg --name <n> --cwd <dir> codex --no-daemon "<implementer instructions + task>"` (without `--no-daemon` commands run outside hc).
  - Check `first_message.sent`. If false the task was not sent: `hc read <n>`; if a trust dialog shows, `hc keys <n> down enter`, then send the task. Never resend blindly.
  - Tell the worker its exact scope, not to start agents, and to report with `hc send $HC_TERMINAL_ID`.
- `message`: `hc send <n> "<text>"` (`--wait` waits for the turn). Refuses blocked terminals; never `--force` past a permission dialog.
- `report`: `hc send <parent> "<result or blocker>"`.
- `wait`: `hc wait --children any|all`, `hc wait <n>`. `reason: message` arrives as your next input; `reason: timeout` is a check-in. Wait again.
- `collect`: `hc read --lines N <n>`, then the result files. Reports arrive as `<hc from="t7 review">…</hc>`.
- `stop`: `hc kill <n>` then `hc rm <n>`, only your own terminals.
- `status`/`list`: `hc get <n>` (`status` is an object `{app, state}`), `hc ls` (`status` is a string). States `idle`, `working`, `done`, `blocked` map directly; `error`, a missing status or anything else is `unknown`; a finished terminal is `exited`. `blocked` means a person is needed.
