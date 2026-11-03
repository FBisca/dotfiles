"""What the repo itself must look like: moved content gone, CI present, hygiene (S7a, S10, S11)."""

import re
import subprocess
import unittest

from support import ROOT


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p and (ROOT / p).exists() or (ROOT / p).is_symlink()]


class MovedContentTest(unittest.TestCase):
    def test_S7a_workflow_doc_lives_in_agent_skills_and_the_readme_links_it(self):
        self.assertFalse((ROOT / "docs/workflow.md").exists())
        self.assertIn("https://github.com/FBisca/agent-skills/blob/main/docs/workflow.md", (ROOT / "README.md").read_text())

    def test_runtime_and_skills_are_not_vendored_any_more(self):
        for path in ("agents/plugins", "agents/.claude-plugin", "docs/specs", "agents/.claude/skills"):
            self.assertFalse((ROOT / path).exists(), path)
        self.assertEqual(list((ROOT / "agents/.agents").glob("skills/*")) if (ROOT / "agents/.agents/skills").exists() else [], [])
        self.assertEqual([p for p in tracked() if p.startswith("bin/bin/agent-runtime")], [])
        self.assertEqual([p for p in tracked() if p.startswith("docs/plans/2026-10-30")], [])

    def test_live_config_files_are_generated_not_stowed(self):
        for path in ("agents/.claude/settings.json", "agents/.codex/config.toml"):
            self.assertFalse((ROOT / path).exists(), path)
        ignore = (ROOT / "agents/.stow-local-ignore").read_text()
        self.assertIn("settings\\.base\\.json", ignore)
        self.assertIn("config\\.base\\.toml", ignore)


class CiTest(unittest.TestCase):
    def setUp(self):
        self.ci = (ROOT / ".github/workflows/ci.yml").read_text()

    def test_S10_ci_runs_shellcheck_a_stow_dry_run_and_the_contract_tests(self):
        self.assertIn("shellcheck", self.ci)
        for target in ("install.sh", "bin/"):
            self.assertIn(target, self.ci)
        self.assertRegex(self.ci, r"stow -n")
        self.assertIn("macos", self.ci)
        self.assertIn("python3 -B -m unittest discover -s tests", self.ci)
        self.assertIn("FBisca/agent-runtime", self.ci, "contract tests run against the real runtime")

    def test_S10_shellcheck_is_clean_when_available(self):
        import shutil
        if not shutil.which("shellcheck"):
            self.skipTest("shellcheck not installed")
        done = subprocess.run(["shellcheck", "install.sh", "bin/bin/wait-checks"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout)


class PublicRepoTest(unittest.TestCase):
    def test_S11_has_an_mit_license_a_readme_with_install_steps_and_ci(self):
        license_text = (ROOT / "LICENSE").read_text()
        self.assertIn("MIT License", license_text)
        self.assertRegex(license_text, r"Copyright \(c\) 2026 Felippe Bisca")
        readme = (ROOT / "README.md").read_text()
        self.assertRegex(readme, r"(?m)^## Install")
        self.assertIn("./install.sh", readme)
        self.assertIn("actions/workflows/ci.yml", readme)
        self.assertIn("rodrigopsasaki", readme, "credit to the original author stays")
        self.assertIn("```mermaid", readme)

    def test_no_absolute_home_paths_in_tracked_files(self):
        for path in tracked():
            if (ROOT / path).is_symlink():
                continue
            try:
                text = (ROOT / path).read_text()
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            self.assertIsNone(re.search(r"/(?:Users|home)/\w", text), path)

    def test_no_dangling_symlinks_gitlinks_or_ds_store(self):
        files = tracked()
        for path in files:
            link = ROOT / path
            if link.is_symlink():
                self.assertTrue(link.exists(), f"dangling symlink {path}")
        self.assertEqual([p for p in files if p.endswith(".DS_Store")], [])
        staged = subprocess.run(["git", "ls-files", "-s"], cwd=ROOT, capture_output=True, text=True).stdout
        self.assertNotIn("160000", staged, "gitlink without .gitmodules")
        self.assertNotIn("ai-job-search", (ROOT / "zsh/.zshrc").read_text())


if __name__ == "__main__":
    unittest.main()
