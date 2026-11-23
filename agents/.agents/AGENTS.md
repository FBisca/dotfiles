- When reporting information to me, be extremely concise.
- When delegating between harnesses do via agent-runtime `spawn`.
- Never add a `Co-Authored-By` trailer naming nor a "Generated with" line, to a commit or PR body, even when the repo's history has them. My commits are mine alone.

## Answer footer

End every answer with a `---` line, then a `## 80/20` section: the bottom line only, nothing new, because I read it first. Show a line only when it has content:

- ✅ Result: always, one line.
- 👉 Next: only if I must act; numbered, the action in bold.
- ❓ Decide: only if the choice is mine.
- ⚠️ Watch out: only a real risk.
- 🔀 Git: only if a repo changed.

## Model classes

Skills name a class (`small`, `medium`, `large`) and an effort, never a model. Resolve the class here unless I said otherwise in this session; pass the skill's effort as `effort`.

| Class | Claude | Codex | Pi |
|---|---|---|---|
| small | `model: "haiku"` | `gpt-6.1-luna` | `minimax/MiniMax-M3.1-Flash` |
| medium | `model: "sonnet"` | `gpt-6.1-terra` | `ollama-cloud/glm-5.3` |
| large | `model: "opus"` | `gpt-6.1-sol` | `ollama-cloud/kimi-k3.1-pro` |

@RTK.md
