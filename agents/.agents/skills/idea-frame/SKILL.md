---
name: idea-frame
description: Grill one raw idea into a frame, an assumption map and a pre-mortem, then gate it. Felippe runs `/idea-frame <one-sentence idea>` before any PRD work.
disable-model-invocation: true
---

# Idea Frame

**Input:** one sentence describing the idea.
**Output:** the idea folder `~/developer/vault/01-projects/<slug>/` with the index note `<Title>.md`, `frame.md`, `assumptions.md`, `premortem.md`, `gates.md`, and an `idea-check --gate 1` result shown to Felippe.
**Hand-off:** `/idea-answer <folder>`

The folder contract (file formats, allowed values, check rules) is the docstring of `~/.claude/skills/idea-frame/scripts/idea_check.py`. Read it before writing any file; the gate fails on anything it does not allow. Vault rules apply: no client or investor names, no message bodies, no secrets.

## Steps

1. **Folder.** Derive a short `<Title>` from the sentence and a kebab `<slug>` from the title. If the folder exists, stop and ask. Create the index note `<Title>.md` (the only root-level note with `type: project`): frontmatter `type: project`, `status: idea`, `stage: framing`, `entry: raw`, `decider: <role>` (ask Felippe which role decides; a role, never a name), `area`, `created`, `updated`; body = the sentence, then `## Hours`.
2. **Grill.** Call the Skill tool with `grilling`, seeding the design tree with [`seeds.md`](seeds.md) (Heilmeier catechism and the internal FAQ on value, usability, feasibility, viability). Extra rules for this grilling:
   - Facts are your job: look them up read-only (fleet brain, code, vault) and record `Source: lookup <link>`. Never ask Felippe for what you can find.
   - Felippe may answer `unknown`. An `unknown` is recorded as `Source: unknown` and becomes an assumption to test; it is never forced into a decision.
   - Stop when the frontier is empty and Felippe confirms.
3. **Write the frame.** From the grilling:
   - `frame.md`: one `## Q<n> <question>` per question with its `Source:` line and the answer.
   - `assumptions.md`: the table `id | risk | assumption | importance | evidence | owner | test | result`. Every `Source: unknown` question is cited as `Q<n>` in at least one assumption. importance and evidence are `high|med|low`; owner is one of `operator/user, finance, compliance, decider, engineering`; every high-importance assumption gets an owner and a test. Engineering questions are left for `/start-planning` Gather.
   - `premortem.md`: about 8 reasons the idea failed, each a bullet ending `→ PRD: <what the PRD must say>` or `→ A<n>`.
4. **Gate 1.** Log the framing time in the index note's `## Hours` (`- YYYY-MM-DD framing <n>h`, ask if unknown). Put the kill criteria to Felippe and wait for his call:
   - kill if there is no named person or role with the problem, no measurable success, or the cost is above his appetite;
   - otherwise continue only if the top 3 assumptions each have an owner type and a test.
   Write the `gates.md` line `- YYYY-MM-DD gate1: continue|kill|reshape: <reason>` and log the gate time as `- YYYY-MM-DD gate1 <n>h`. Then run and show the output of `python3 ~/.claude/skills/idea-frame/scripts/idea_check.py <folder> --gate 1`. Fix every FAIL (ask Felippe where the fix is a judgment) and rerun until none remain.
5. **Outcome.**
   - continue: set `stage: answering`.
   - kill: set `stage: killed`, `status: dropped`; after his yes, move the whole folder to `04-archive/`.
   - reshape: set `stage: reshaped`; restart framing in the same folder, keeping the history.
   Update `updated:` on every edit.

Done when `idea_check.py <folder> --gate 1` shows no FAIL and `gates.md` has the gate 1 line; on continue, name `/idea-answer <folder>` as the next command.
