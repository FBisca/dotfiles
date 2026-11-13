"""Pi acceptance: the published manual checklist and the record of the manual run (S1, S3, S5, S6).

The provider smoke needs the real machine and an authorised provider, so it runs only
with PI_LIVE=1. The offline part checks that the checklist and its recorded outcome
stay in the repo, so a machine that never ran Pi still knows what to run and what
the last run found.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from support import ROOT

README = (ROOT / "README.md").read_text()
VERIFICATION = ROOT / "docs" / "verification" / "pi-bootstrap.md"
RTK_VERIFICATION = ROOT / "docs" / "verification" / "pi-rtk.md"
SPEC = ROOT / "docs" / "specs" / "agent-environments.md"

# The manual checklist the README publishes, one line per check.
CHECKLIST = {
    "S1": "pi --version",
    "S3": "/skill:start-planning",
    "S4": "pi auth check --provider minimax --model MiniMax-M3.1-Flash",
    "S5": "`pi mcp list` shows the `agent-runtime` server",
    "S6": "bounded code edit in a disposable worktree",
}


class PublishedChecklistTest(unittest.TestCase):
    """The manual checks are published and the last run is recorded."""

    def test_the_readme_publishes_every_manual_check(self):
        """S1 S3 S5 S6 the README publishes every manual check."""
        for scenario, needle in CHECKLIST.items():
            self.assertIn(needle, README, f"{scenario}: {needle!r} is not in the README checklist")

    def test_the_manual_run_is_recorded_without_credentials(self):
        """S1 the recorded manual run states its outcome and holds no credential."""
        self.assertTrue(VERIFICATION.is_file(), f"{VERIFICATION} is missing")
        text = VERIFICATION.read_text()
        self.assertIn("pi --version", text)
        self.assertIn("MiniMax-M3.1-Flash", text)
        for pattern in (r"sk-[A-Za-z0-9]{16,}", r"(?i)(api[_ ]?key|bearer|token|password)\s*[:=]\s*\S+"):
            self.assertIsNone(re.search(pattern, text), f"{pattern!r} leaked into the record")

    def test_the_living_spec_covers_every_scenario(self):
        """S1 S2 S3 S4 S5 S6 the living spec keeps a requirement per scenario."""
        text = SPEC.read_text()
        self.assertRegex(text, r"(?m)^Paths: .+")
        for number in range(1, 7):
            self.assertRegex(text, rf"(?m)^- \*\*R{number}\*\* .+\(from [^)]+/S\d+\)$", f"R{number} is missing")
        for number in range(9, 14):
            self.assertRegex(text, rf"(?m)^- \*\*R{number}\*\* .+\(from pi-agent-runtime-mcp/S\d+\)$",
                             f"R{number} is missing")

    def test_the_rtk_requirements_and_record_are_published(self):
        """S7 S8 the spec keeps the RTK requirements and the last RTK run is recorded."""
        text = SPEC.read_text()
        for number in (7, 8):
            self.assertRegex(text, rf"\*\*R{number}\*\*", f"R{number} is missing")
            self.assertIn(f"(from pi-rtk/S{number - 6})", text, f"R{number} has no provenance")
        self.assertTrue(RTK_VERIFICATION.is_file(), f"{RTK_VERIFICATION} is missing")
        record = RTK_VERIFICATION.read_text()
        self.assertIn("rtk --version", record)
        self.assertIn("brew install rtk", README, "the README publishes the prerequisite")
        for pattern in (r"sk-[A-Za-z0-9]{16,}", r"(?i)(api[_ ]?key|bearer|token|password)\s*[:=]\s*\S+"):
            self.assertIsNone(re.search(pattern, record), f"{pattern!r} leaked into the record")


class LiveSmokeTest(unittest.TestCase):
    """The bounded Pi smoke: one edit, one tool call, no repeats (PI_LIVE=1 only)."""

    def test_pi_makes_one_bounded_edit_without_repeating_a_tool_call(self):
        """S1 a bounded Pi edit completes without repeating the same tool call."""
        if os.environ.get("PI_LIVE") != "1":
            self.skipTest("set PI_LIVE=1 to run the live Pi smoke")
        if not shutil.which("pi"):
            self.skipTest("pi is not installed")
        with tempfile.TemporaryDirectory(prefix="pi-smoke-") as directory:
            repo = Path(directory)
            (repo / "calc.py").write_text("def add(a, b):\n    return a - b\n")
            subprocess.run(["git", "init", "-q", "."], cwd=repo, check=True)
            finished = subprocess.run(
                ["pi", "-p", "--mode", "json", "--provider", "minimax", "--model", "MiniMax-M3.1-Flash",
                 "Fix calc.py: the add function subtracts. Edit it once, then reply with the fixed line."],
                cwd=repo, capture_output=True, text=True, timeout=180)
            edited = (repo / "calc.py").read_text()
        self.assertEqual(finished.returncode, 0, finished.stdout + finished.stderr)
        self.assertIn("return a + b", edited)
        calls = [json.loads(line)["toolName"] for line in finished.stdout.splitlines()
                 if line.startswith("{") and json.loads(line).get("type") == "tool_execution_start"]
        self.assertTrue(calls, "the model made no tool call at all")
        self.assertEqual(len(calls), len(set(calls)), f"the model repeated a tool call: {calls}")


class LiveRtkTest(unittest.TestCase):
    """The bounded Pi RTK check: one bash call, rewritten through rtk (PI_LIVE=1 only)."""

    def test_pi_rewrites_a_bash_command_through_rtk(self):
        """S8 Pi runs a bash command through rtk, which prints the compact form."""
        if os.environ.get("PI_LIVE") != "1":
            self.skipTest("set PI_LIVE=1 to run the live Pi smoke")
        if not shutil.which("pi"):
            self.skipTest("pi is not installed")
        if not shutil.which("rtk"):
            self.skipTest("rtk is not installed")
        with tempfile.TemporaryDirectory(prefix="pi-rtk-") as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", "-b", "main", "."], cwd=repo, check=True)
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                            "commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True)
            finished = subprocess.run(
                ["pi", "-p", "--mode", "json", "--provider", "minimax", "--model", "MiniMax-M3.1-Flash",
                 "Run git status in this repository and reply with what it says."],
                cwd=repo, capture_output=True, text=True, timeout=180)
        outputs = []
        for line in finished.stdout.splitlines():
            if not line.startswith("{"):
                continue
            event = json.loads(line)
            if event.get("type") == "tool_execution_end" and event.get("toolName") == "bash":
                content = event.get("result", {}).get("content", [])
                outputs.append("".join(part.get("text", "") for part in content))
        self.assertTrue(outputs, "the model made no bash call")
        self.assertNotIn("On branch", outputs[0], "the command ran as plain git, not through rtk")
        self.assertIn("clean", outputs[0].lower(), outputs[0])


if __name__ == "__main__":
    unittest.main()
