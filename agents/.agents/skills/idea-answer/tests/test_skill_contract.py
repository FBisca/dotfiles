import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text()


def skill_text():
    text = read("SKILL.md")
    prep = ROOT / "prep.md"
    return text + ("\n" + prep.read_text() if prep.exists() else "")


class IdeaAnswerContract(unittest.TestCase):
    def test_S15b_manual_only_invocation(self):
        self.assertRegex(read("SKILL.md"), r"(?m)^disable-model-invocation: true$")
        self.assertRegex(read("agents/openai.yaml"), r"(?m)^\s+allow_implicit_invocation: false$")

    def test_S17_routing_and_handoff(self):
        t = skill_text()
        for p in (
            "operator/user, finance, compliance, decider, engineering",
            "handed to `/start-planning` Gather",
            "only after Felippe's yes",
            "never sends",
            "Felippe's summary",
            "no message bodies, no client or investor names",
            "`Source: unknown`",
            "`entry: decided`",
            "/prototype",
            "90-templates/project.md",
            "`[[assumptions]] [[answers]] [[gates]]` under `## Notes`",
            "`type: note`, `area`, `project: \"[[<Title>]]\"`, `created`, `updated`, `tags: []`",
            "add `[[answers]]` to the index note's `## Notes`",
            "under `## Hours` in the index note",
            "`Owner: <role>`, `Date: YYYY-MM-DD`, `Link: <link>`, `Summary:`",
            "`accepted by <decider role>: engineering, to /start-planning Gather`",
            "`Summary: open → PRD Open Questions`",
            "the index note (`<Title>.md`, the one root-level note with `type: project`)",
            "`type: project`, `status: idea`, `stage: answering`, `entry: decided`, `decider: <role>`",
            "idea-check only needs a non-empty result",
            "python3 ~/.claude/skills/idea-frame/scripts/idea_check.py <folder> --gate 2",
            "gate2: pass by <role>: <reason>",
        ):
            self.assertIn(p, t)
        self.assertLess(t.rindex("`/to-spec`"), t.rindex("`/goldfish <folder>/PRD.md`"))
        self.assertRegex(read("SKILL.md"), r"(?s)Hand-off:\*\*.*`/to-spec`.*`/goldfish")
        self.assertNotIn("idea.md", t)
        self.assertLessEqual(len(read("SKILL.md").splitlines()), 120)


    def test_S28_owner_guidance_and_cap(self):
        text = read("SKILL.md")
        self.assertIn('**Owner guidance** (route by what the question is about):\n- finance: business and finance rules, e.g. "what fee must this clear?"; if an ops owner holds the rule, record finance\n- compliance: legal, security, data access, e.g. "may we store these documents outside the EU?"\n- engineering: how the system behaves, e.g. "does the API return the sync date?"; never operators; goes to `/start-planning` Gather\n- operator/user: how people react to or use it, e.g. "how do ops handle a failed transfer today?"\n- decider: scope and priority, e.g. "is mobile in scope for v1?"\n', text)
        for p in ("Rank the open items by importance", "send at most 12 to people",
                  "owner is not engineering", "marked low priority", "`people-cap`"):
            self.assertIn(p, text)
        self.assertLessEqual(len(text.splitlines()), 120)


if __name__ == "__main__":
    unittest.main()
