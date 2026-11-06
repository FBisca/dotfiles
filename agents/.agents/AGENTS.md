- When reporting information to me, be extremely concise and sacrifice grammar for the sake of concision.
- When I say "ask Codex" or "use Codex", delegate via agent-runtime `spawn` with `cli: "codex"`, then `wait(target="all")`.

## Model classes

Skills name a class (`small`, `medium`, `large`) and an effort, never a model. Resolve the class here unless I said otherwise in this session; pass the skill's effort as `effort`.

| Class | Claude subagent | Codex | agent-runtime `spawn` |
|---|---|---|---|
| small | `model: "haiku"` | `gpt-6.1-terra` | `cli: "minimax"` |
| medium | `model: "sonnet"` | `gpt-6.1-terra` | `cli: "codex"` (worker profile), or `cli: "claude"`, `model: "sonnet"` |
| large | `model: "opus"` | `gpt-6.1-sol` | `cli: "claude"`, `model: "opus"` |
