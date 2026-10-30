# Adapter: hc

`$HC_TERMINAL_ID` is your address; terminals you start are your children.

- `spawn`: `lookup` is Claude's Agent tool without a name, or Codex's MultiAgent V2 spawn tool; no terminal. `worker`: always `--bg`, a unique name (a-z 0-9 - _, max 32), task inside `run` (a later send can be dropped).
  - Claude: `hc run --bg --name <n> --cwd <dir> claude --agent implementer "<task>"`
  - Codex: `hc run --bg --name <n> --cwd <dir> codex --no-daemon "<developer_instructions of ~/.codex/agents/implementer.toml + task>"`.
  - If `first_message.sent` is false, the task was not sent: `hc read <n>`; for a trust dialog `hc keys <n> down enter`, then send it. No blind resend.
  - Exact scope; no `worker`s of its own unless assigned; report via `hc send $HC_TERMINAL_ID`.
- `message`: `hc send <n> "<text>"`. Never `--force` past a permission dialog.
- `report`: `hc send <parent> "<result or blocker>"`.
- `wait`: `hc wait --children any|all`, `hc wait <n>`. A `message` or `timeout` wake-up is not completion.
- `collect`: `hc read --lines N <n>`, then the result files.
- `stop`: `hc kill <n>`, then `hc rm <n>`; your own terminals only.
- `status`/`list`: `list` is hc-only; wrap `hc get <n>` (`native` keeps address, name, state, status, turn, exit_code, reason, argv) (`status` is an object `{app, state}`) and `hc ls` (`status` is a string; it lists the user's other terminals too, so filter to your children by `hc get` parent). `idle`, `working`, `done`, `blocked` map directly; a finished terminal is `exited`; anything else (`error`, missing) is `unknown`. `blocked` means a person is needed: its `next` includes the raw `hc keys` row as a gap.
