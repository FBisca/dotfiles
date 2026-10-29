import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text()


def skill_text():
    return read("SKILL.md") + "\n" + read("reader.md")


class GoldfishContract(unittest.TestCase):
    def test_S15c_manual_only_invocation(self):
        self.assertRegex(read("SKILL.md"), r"(?m)^disable-model-invocation: true$")
        self.assertRegex(read("agents/openai.yaml"), r"(?m)^\s+allow_implicit_invocation: false$")

    def test_S18_reader_contract(self):
        t = skill_text().lower()
        self.assertIn("only", t)
        self.assertRegex(t, r"only (the|that) (given |one )?(file|document)|opens only")
        self.assertIn("what this says", t)
        self.assertIn("undefined term", t)
        self.assertRegex(t, r"two ways|ambigu")
        self.assertIn("cannot paraphrase", t)
        self.assertIn("blocker", t)
        self.assertRegex(t, r"subagent")
        self.assertRegex(t, r"never edit|does not edit|not edit")

    def test_S19_apache_attribution(self):
        t = read("NOTICE.md")
        for s in ("Apache-2.0", "elephant-goldfish-model", "agents/comprehension.md", "modified"):
            self.assertIn(s, t)
        self.assertTrue((ROOT / "LICENSE").exists())
        self.assertIn("Apache License", read("LICENSE"))


if __name__ == "__main__":
    unittest.main()
