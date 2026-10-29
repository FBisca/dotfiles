# My feature workflow

From a raw idea to shipped code. Every step is a skill in `agents/.agents/skills/`; the ones marked *you* need me in the session. Steps marked *user-invoked* never start on their own: each hand-off names the next command.

Evidence levels: none of the source methods has an RCT; "adoption" means widely used, not proven. My own backtests live in `~/developer/workflow-evals/` (`discovery/` for the PRD-writing methods, `idea-backtest/` for this pipeline).

## Which door

| I have | Start at |
|---|---|
| A raw idea, nothing written | 1. `/idea-frame` |
| A decided feature with sources (a request, an RFC, a kickoff) | 3. `/to-spec`; or 4. `/idea-answer` first if a few items need owners' answers (it creates the folder with `entry: decided`) |
| A PRD already | 6. `/start-planning` |
| A small fix with no product question | `/tdd` or `/diagnosing-bugs` directly |

## The steps

| # | Step | Skill | Who | What it does | Based on |
|---|---|---|---|---|---|
| 1 | Frame | `/idea-frame` (user-invoked) | you + agent | Grills me with seed questions; facts are looked up, never asked; an answer I can't know becomes `Source: unknown` and an assumption to test. Writes the idea folder in the vault: frame, assumption map (importance × evidence on value, usability, feasibility, viability and ethical; reordered leap-of-faith first), a story-map pass (actors × steps, "what must be true here?") feeding it, pre-mortem. | Heilmeier catechism (DARPA); internal FAQ from Working Backwards PR/FAQ (Bryar & Carr 2021); Cagan's four risks; assumption mapping (Torres, *Continuous Discovery Habits*, 2021); story mapping (Patton 2014); assumption mapping (Bland & Osterwalder, *Testing Business Ideas*, 2019) via Torres 2021; Torres's five assumption categories; pre-mortem (Klein, HBR 2007); my `grilling` skill |
| 2 | Gate 1 | inside `/idea-frame` | you | Kill, reshape or continue. Kill when no named role has the problem, success isn't measurable, or the cost is above my appetite. `idea-check --gate 1` must pass. On continue, the frame and assumption map are loaded into the conversation for step 3. | Stage-Gate (Cooper); appetite from Shape Up (Singer 2019) |
| 3 | PRD | `/to-spec` (user-invoked), then `/goldfish` (user-invoked) | agent, you fix | `/to-spec` writes `PRD.md` in the project folder from the conversation and the idea folder; its Further Notes list every open assumption (`A<n>`, risk, owner type) as an open question. The index note moves to `stage: prd`. `/goldfish` has a zero-context reader paraphrase the PRD; anything it can't paraphrase is a blocker I fix. | Pocock's spec template; Elephant-Goldfish Model's comprehension check (Google 2026, Apache-2.0) |
| 4 | Answer round (optional) | `/idea-answer` (user-invoked) | you, with owners | Only for the 3–5 open items I pick, ranked by importance. Routes each to the owner who can answer it (operator/user, finance, compliance, decider; engineering goes to step 6). Prepares each conversation; I hold it; answers are my summaries with links. Outreach drafted only after my yes. | Assumption tests (Torres 2021); The Mom Test (Fitzpatrick 2013); dual-track discovery (Sy 2007, Patton, Cagan); routing to owners is mine, from the discovery backtest |
| 5 | Gate 2 (only with step 4) | inside `/idea-answer` | decider | The decider signs off: every high-importance assumption tested or accepted, every open question answered or moved to the PRD with an owner. `idea-check --gate 2` must pass. | Stage-Gate (Cooper) |
| 6 | Plan | `/start-planning` (calls `grilling`) | you + agent | Gathers sources and settled decisions, grills only what's open, writes WHEN/THEN scenarios, decisions with the rejected option and source, vertical tickets with Paths. One approval. | Spec-driven development (OpenSpec, GitHub Spec Kit, Pocock); EARS-style scenarios; ADRs (Nygard); tracer bullets / vertical slices; ISO/IEC/IEEE 29148 requirement qualities |
| 7 | Build | `/orchestrate` (user-invoked) | agents | One implementer per ticket in its own worktree; each scenario becomes a test that fails first. | TDD red-green-refactor (`/tdd`); ATDD |
| 8 | Gate each ticket | `/converge`, fresh-context review | code + agent | `converge` checks every scenario has a test, every changed test carries an ID, the diff stays in Paths. An Opus reviewer that never saw the build checks correctness and conventions. Then PR and merge. | Spec Kit `converge`, OpenSpec `verify`; independent review |
| 9 | Archive | `/orchestrate` + `converge --final` | agent | Scenarios become numbered requirements in the living spec `docs/specs/<area>.md`; tests are renamed to them. | OpenSpec living spec and delta specs |
| 10 | Measure | backtest D extraction | agent + you | After a feature ships, count the product decisions that arrived after its PRD. Baseline 27–32 per feature. | My discovery backtest (2026-10-29) |

## What the evidence says so far

- **Discovery backtest** (3 shipped Heritage features): no PRD-writing method beat `/to-spec` on its own documents. 72% of the decisions made after the PRD could have been caught before it by asking their owners. The agents' questions already named 56% of them; nobody answered.
- **Idea pipeline backtest v1**: steps 1–3 named 59% of those later decisions (to-spec 40%), mostly by asking more, and routed only 46% to the right owner. FAIL against its 65% / 70% bar.
- **v2**, after adding owner guidance and the 12-item cap: FAIL, and lower. It named 52% (to-spec 40%), but the items that reach people named about 38%, no better than to-spec. Routing fell to 40%, and that metric compares against who *caused* a decision, not who should have been asked, so it can't be read reliably.
- **What I keep:** the assumption map, which names 11–19 points more than to-spec in both runs. That's why step 3 follows gate 1 directly and step 4 is optional: whether owners' answers prevent late decisions needs real conversations, not a backtest.
- **Real trial**: my next 3–5 ideas, judged 2027-01-29. Keep if at least one is killed or reshaped at a gate with the decider's agreement, my median time to the PRD is ≤ 4 h, and shipped ideas have ≤ 15 late decisions. The rule is in the vault, `01-projects/idea-to-prd/trial.md`.

## Where things live

- **Skills:** `agents/.agents/skills/<name>/` (this repo), linked into `~/.claude/skills`.
- **Ideas, PRDs and plans:** the vault, `01-projects/<slug>/`: the index note, `frame.md`, `assumptions.md`, `premortem.md`, `answers.md`, `gates.md`, `PRD.md`, `plans/`.
- **The folder contract:** the docstring of `agents/.agents/skills/idea-frame/scripts/idea_check.py`.
- **Living specs:** `docs/specs/<area>.md` in the repo that holds the code.
