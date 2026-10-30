# Adapter: native

Runtime: the agent's own subagent tools, with no terminal runtime. `status` and `list` records carry `native: true`.

## Claude

Use the Agent tool for workers and SendMessage for follow-ups.

- `spawn(role, task, cwd)`: Agent tool with `subagent_type` set to the role (`implementer`); put the task and the exact checkout in the prompt.
- `message(to, text)`: SendMessage to the named agent.
- `report(text)`: a subagent returns its result as its final message.
- `wait(any|all|name)`: the Agent tool returns when the subagent finishes; for background agents, end your turn and let notifications arrive.
- `collect(name)`: the Agent tool result; verify files in the checkout.
- `stop(name)`: let the subagent finish, or stop it with the runtime's own stop tool.
- `status(name)`, `list()`: the runtime's own agent list.

## Codex / MultiAgent V2

Use the live spawn, message, follow-up, wait and inspection tools. Keep runtime IDs in the ledger. `task_name` is a label; it does not select the custom `implementer` role.

Prefer the configured Terra implementer with no full-history fork. If the tool omits role/model selection, report the runtime limitation. Do not silently use an expensive inherited model or change global feature flags to work around it. Resume an existing agent with the runtime's follow-up operation after checking its context and checkout.

Native Codex workers stay visible through Codex's own agent UI. No attachment of a hidden Codex child to a Herdr pane has been verified; `codex resume` is not proof of safe concurrent attachment. Never run native and separate-pane modes for the same task.

Capabilities beyond the contract are listed in `capabilities.json` and shown by `agent-runtime help`.
