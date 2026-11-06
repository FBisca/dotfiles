- When reporting information to me, be extremely concise and sacrifice grammar for the sake of concision.
- When delegating Codex do via agent-runtime `spawn` with `cli: "codex"`.

## Model classes

Skills name a class (`small`, `medium`, `large`) and an effort, never a model. Resolve the class here unless I said otherwise in this session; pass the skill's effort as `effort`.

| Class | Claude | Codex |
|---|---|---|
| small | `model: "haiku"` | `gpt-6.1-luna` |
| medium | `model: "sonnet"` | `gpt-6.1-terra` |
| large | `model: "opus"` | `gpt-6.1-sol` |
