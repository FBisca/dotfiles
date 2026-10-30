# Adapter: native

The agent's own subagent tools; `status` has `native: {}`; its `next` rows point to the return value or SendMessage.

## Claude

- `spawn`: `lookup` is the Agent tool without a name. `worker` is a named teammate, `subagent_type` = role (`implementer`); task and exact checkout in the prompt.
- `message`: SendMessage to the named agent.
- `report`: a subagent returns its result as its final message.
- `wait`: the Agent tool returns on finish; for background agents end your turn and let notifications arrive.
- `collect`: the Agent result; verify files in the checkout.
- `stop`: let it finish, or use the runtime's stop tool.
- `status`/`list`: the runtime's agent list.

## Codex / MultiAgent V2

`spawn` maps `lookup` and `worker` to MultiAgent V2 (a worker is a named, long-lived agent). Use the live spawn, message, follow-up, wait and inspection tools; keep runtime IDs in the ledger. `task_name` is a label, not a role. Prefer the Terra implementer with no full-history fork; if role or model selection is missing, report the limitation instead of using an inherited expensive model. Resume with the follow-up operation. Codex workers stay visible in Codex's own agent UI.
