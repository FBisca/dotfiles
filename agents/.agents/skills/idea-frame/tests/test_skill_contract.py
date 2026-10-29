import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text()


class IdeaFrameContract(unittest.TestCase):
    def test_S15a_manual_only_invocation(self):
        self.assertRegex(read("SKILL.md"), r"(?m)^disable-model-invocation: true$")
        self.assertRegex(read("agents/openai.yaml"), r"(?m)^\s+allow_implicit_invocation: false$")

    def test_S16_grills_with_seeds_and_unknown_rule(self):
        skill, seeds = read("SKILL.md"), read("seeds.md")
        self.assertIn("Call the Skill tool with `grilling`", skill)
        self.assertIn("[`seeds.md`](seeds.md)", skill)
        self.assertIn("`unknown` is recorded as `Source: unknown` and becomes an assumption to test", skill)
        self.assertIn("never forced into a decision", skill)
        for p in ("Heilmeier", "What are you trying to do", "How is success measured",
                  "Internal FAQ", "value", "usability", "feasibility", "viability"):
            self.assertIn(p, seeds)

    def test_S16_writes_files_runs_gate_and_hands_off(self):
        skill = read("SKILL.md")
        for p in ("frame.md", "assumptions.md", "premortem.md", "gates.md",
                  "~/.claude/skills/idea-frame/scripts/idea_check.py",
                  "idea_check.py <folder> --gate 1"):
            self.assertIn(p, skill)
        self.assertTrue(skill.rstrip().splitlines()[-1].startswith("Done when"))
        self.assertIn("**Hand-off:** `/idea-answer <folder>`", skill)
        self.assertLessEqual(len(skill.splitlines()), 120)


if __name__ == "__main__":
    unittest.main()
