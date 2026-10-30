# Adapter: herdmates

Runtime: Herdmates hosts Claude's native team processes in Herdr panes. Claude owns task assignment, messaging and shutdown. Use the existing plugin; do not install another tmux shim or reproduce its recorder, hooks or team files. Claude only: Codex in a Herdr pane uses the native adapter.

## Guidance

The `claude()` function in `zsh/.zsh/aliases.zsh` routes Claude through Herdmates inside Herdr. Start a new lead from an available shell pane with `claude`. If that function is unavailable, use `herdmates teammux-launch` directly. Do not probe `herdmates teammux-launch --help`: the launcher can change runtime state before Claude sees the argument.

Do not start the launcher inside an active Claude or Codex conversation. It starts a lead; it does not attach the current agent. If an existing lead lacks the shim, explain that visible teammates require a lead started through Herdmates. Do not restart or duplicate its work.

When the lead is ready:

1. Verify the available native teammate tools and the `implementer` definition.
2. Assign exact checkouts and ownership. Ask Claude to spawn native implementer teammates.
3. Let Herdmates create their panes. Verify returned agent IDs and observed Herdr pane IDs; record the mapping in the task handoff.
4. Check the Herdr sidebar for recognized agents. A shell pane without an agent is not a visible teammate.
5. Use native task completion and messages as work evidence. Sidebar states are presentation signals only.

Shutdown remains with Claude/Herdmates. Do not close panes by name, sweep other sessions, or replace the plugin's lifecycle. Native task and teammate tool schemas vary by version; do not assume obsolete `TeamCreate` or `TeamDelete` tools exist. Inspect the plugin's `docs/sidebar-rows.toml` before changing a sidebar layout and preserve existing configuration.

## Verb mapping

- `spawn(role, task, cwd)`: ask Claude to spawn a native teammate with the `implementer` (or named) definition; put the task and checkout in the spawn prompt.
- `message(to, text)`: SendMessage to the teammate.
- `report(text)`: the teammate replies with SendMessage to the lead.
- `wait(any|all|name)`: end your turn; teammate messages and task completions arrive as input. Do not poll.
- `collect(name)`: read the teammate's final message and the native task result; verify the files in the checkout.
- `stop(name)`: ask the teammate to finish through Claude's own shutdown; never close panes yourself.
- `status(name)`, `list()`: the native task list and teammate roster. Set `native: true` and point `next[]` at those tools.

Capabilities beyond the contract are listed in `capabilities.json` and shown by `agent-runtime help`.
