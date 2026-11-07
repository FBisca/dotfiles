"""Pi bootstrap: additive settings, skill discovery, secret safety, no runtime MCP in Pi (S2-S6)."""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from support import ROOT, HomeCase, make_skills

NEEDED_TOOLS = ["git", "python3", "sh", "bash", "dirname", "basename", "cp", "mv", "rm", "cmp", "date",
                 "grep", "find", "sed", "mkdir", "cat", "chmod", "ls", "readlink", "mktemp", "env", "ln"]


class PiBootstrapTest(HomeCase):
    """install.sh against a temp HOME: the Pi path only, never Claude Code or Codex."""

    def agent_dir(self):
        return self.home / ".pi" / "agent"

    def settings(self):
        return json.loads((self.agent_dir() / "settings.json").read_text())

    def pi_only_env(self):
        """A PATH without the Pi binary, to test the missing prerequisite."""
        binaries = self.tmp / "bin-nopi"
        binaries.mkdir(exist_ok=True)
        for name in NEEDED_TOOLS:
            real = shutil.which(name)
            if real:
                (binaries / name).symlink_to(real)
        return {"PATH": str(binaries)}

    # S2: the Pi path is additive and leaves the other tools alone.
    def test_new_home_gets_pi_settings_and_no_credentials(self):
        self.install()
        live = self.agent_dir() / "settings.json"
        self.assertTrue(live.is_file())
        settings = self.settings()
        self.assertIs(settings["enableSkillCommands"], True)
        self.assertNotIn("defaultProvider", settings, "no provider is picked without the user choosing one")
        self.assertFalse((self.agent_dir() / "auth.json").exists(), "the installer never writes credentials")
        self.assertFalse((self.agent_dir() / "models.json").exists())
        text = live.read_text().lower()
        for secret in ("api_key", "apikey", "bearer", "password", "secret", "token"):
            self.assertNotIn(secret, text, secret)

    def test_existing_pi_settings_keep_the_user_keys(self):
        (self.agent_dir()).mkdir(parents=True)
        live = self.agent_dir() / "settings.json"
        live.write_text(json.dumps({"defaultModel": "MiniMax-M3.1-Flash", "lastChangelogVersion": "1.5.0"}))
        self.install()
        settings = self.settings()
        self.assertEqual(settings["defaultModel"], "MiniMax-M3.1-Flash")
        self.assertEqual(settings["lastChangelogVersion"], "1.5.0")
        self.assertIs(settings["enableSkillCommands"], True)
        backups = list(self.agent_dir().glob("settings.json.bak-*"))
        self.assertEqual(len(backups), 1, "the previous file is backed up")
        self.assertEqual(json.loads(backups[0].read_text())["defaultModel"], "MiniMax-M3.1-Flash")

    def test_invalid_pi_settings_are_backed_up_and_left_untouched(self):
        (self.agent_dir()).mkdir(parents=True)
        live = self.agent_dir() / "settings.json"
        live.write_text("{not json")
        done = self.install()
        self.assertEqual(live.read_text(), "{not json")
        self.assertEqual(len(list(self.agent_dir().glob("settings.json.bak-*"))), 1)
        self.assertIn("not valid JSON", done.stdout + done.stderr)

    def test_rerunning_the_installer_leaves_pi_settings_alone(self):
        self.install()
        live = self.agent_dir() / "settings.json"
        first = live.read_text()
        self.install()
        self.assertEqual(live.read_text(), first)
        self.assertEqual(list(self.agent_dir().glob("settings.json.bak-*")), [])

    def test_a_symlinked_pi_settings_file_is_replaced_without_touching_its_target(self):
        target = self.tmp / "pi-settings.json"
        target.write_text(json.dumps({"defaultModel": "MiniMax-M3.1-Flash"}))
        self.agent_dir().mkdir(parents=True)
        live = self.agent_dir() / "settings.json"
        live.symlink_to(target)
        self.install()
        self.assertFalse(live.is_symlink())
        self.assertEqual(target.read_text(), json.dumps({"defaultModel": "MiniMax-M3.1-Flash"}))
        self.assertEqual(self.settings()["defaultModel"], "MiniMax-M3.1-Flash")
        self.assertEqual(len(list(self.agent_dir().glob("settings.json.bak-*"))), 1)

    def test_a_pi_directory_that_is_not_a_directory_is_left_alone(self):
        (self.home / ".pi").write_text("not a directory")
        done = self.install()
        self.assertIn("is not a directory", done.stdout + done.stderr)
        self.assertEqual((self.home / ".pi").read_text(), "not a directory")

    def test_the_private_overlay_sets_the_provider_and_is_not_tracked(self):
        overlay = self.tmp / "overlay"
        overlay.mkdir()
        (overlay / "pi-settings.json").write_text(json.dumps({"defaultProvider": "minimax",
                                                              "defaultThinkingLevel": "low"}))
        self.install(DOTFILES_PRIVATE=overlay)
        settings = self.settings()
        self.assertEqual(settings["defaultProvider"], "minimax")
        self.assertEqual(settings["defaultThinkingLevel"], "low")
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        self.assertNotIn("pi-settings.json", tracked)

    def test_a_missing_pi_binary_is_reported_and_no_provider_is_chosen(self):
        done = self.install(**self.pi_only_env())
        self.assertIn("Pi is not installed", done.stdout + done.stderr)
        self.assertIn("https://pi.dev/install.sh", done.stdout + done.stderr)
        self.assertNotIn("defaultProvider", self.settings(), "a missing Pi never falls back to another provider")

    # S3: the skills Pi finds are the ones already linked, and a missing one is reported.
    def test_pi_reports_the_linked_skills_and_the_missing_prerequisites(self):
        make_skills(self.skills, ["start-planning"])
        done = self.install()
        output = done.stdout + done.stderr
        self.assertIn("Pi skill ready: start-planning", output)
        self.assertIn("missing Pi skill prerequisite: grilling", output)
        self.assertFalse((self.home / ".agents/skills/grilling").exists(), "a missing skill is never invented")
        for name in ("alpha", "beta", "secret", "start-planning"):
            link = self.home / ".agents/skills" / name
            self.assertTrue(link.is_symlink(), name)
            self.assertTrue((link / "SKILL.md").is_file(), name)

    def test_a_user_file_inside_a_skill_directory_survives_a_rerun(self):
        note = self.home / ".agents/skills/alpha/NOTE.md"
        self.install()
        note.write_text("mine")
        self.install()
        self.assertEqual(note.read_text(), "mine")
        self.assertTrue((self.home / ".agents/skills/alpha").is_symlink())

    # S5: Pi must not get the mutating agent-runtime tools.
    def test_the_agent_runtime_mcp_server_is_removed_from_pi_and_backed_up(self):
        (self.agent_dir()).mkdir(parents=True)
        mcp = self.agent_dir() / "mcp.json"
        mcp.write_text(json.dumps({"mcpServers": {
            "agent-runtime": {"command": "sh", "args": ["-c", "agent-runtime-mcp"]},
            "filesystem": {"command": "npx", "args": ["-y", "@modelmodelcontextprotocol/server-filesystem", "."]},
        }}))
        done = self.install()
        servers = json.loads(mcp.read_text())["mcpServers"]
        self.assertNotIn("agent-runtime", servers)
        self.assertIn("filesystem", servers, "other MCP servers stay")
        backups = list(self.agent_dir().glob("mcp.json.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertIn("agent-runtime", json.loads(backups[0].read_text())["mcpServers"])
        self.assertIn("does not expose the agent-runtime MCP tools", done.stdout + done.stderr)

    def test_no_mcp_file_is_created_when_the_user_has_none(self):
        self.install()
        self.assertFalse((self.agent_dir() / "mcp.json").exists())

    # S2: Claude Code and Codex are untouched by the Pi path.
    def test_claude_and_codex_files_are_byte_for_byte_the_same_after_a_rerun(self):
        self.install()
        claude = self.home / ".claude/settings.json"
        codex = self.home / ".codex/config.toml"
        skills = sorted((self.home / ".claude/skills").iterdir())
        before = (claude.read_bytes(), codex.read_bytes(), [(p.name, p.resolve()) for p in skills])
        self.install()
        after = (claude.read_bytes(), codex.read_bytes(),
                 [(p.name, p.resolve()) for p in sorted((self.home / ".claude/skills").iterdir())])
        self.assertEqual(before, after)

    def test_pi_only_leaves_claude_and_codex_untouched(self):
        done = subprocess.run([str(ROOT / "install.sh"), "--no-stow", "--pi-only"], env=self.env(), cwd=self.tmp,
                              capture_output=True, text=True, timeout=120)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue((self.agent_dir() / "settings.json").is_file())
        self.assertFalse((self.home / ".claude/settings.json").exists())
        self.assertFalse((self.home / ".codex/config.toml").exists())

    # S4: nothing secret is tracked in this repo.
    def test_tracked_pi_files_hold_no_credentials(self):
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True,
                                 check=True).stdout.split("\0")
        for path in tracked:
            if not path or not (ROOT / path).is_file():
                continue
            try:
                text = (ROOT / path).read_text()
            except (UnicodeDecodeError, OSError):
                continue
            self.assertIsNone(re.search(r"sk-[A-Za-z0-9]{16,}", text), path)
            if path.startswith("agents/.pi/"):
                for secret in ("api_key", "apikey", "bearer", "password", "secret", "token"):
                    self.assertNotIn(secret, text.lower(), f"{path}: {secret}")


if __name__ == "__main__":
    unittest.main()
