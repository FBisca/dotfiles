"""install.sh against a temp HOME: skills linking (S7), runtime wiring (S6), config merge (S9)."""

import json
import os
import shutil
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

from support import INSTALL, ROOT, RUNTIME_SRC, HomeCase, make_repo, make_runtime_stub

MERGE = ROOT / "scripts" / "merge-config.py"


def merge(kind, out, *files):
    return subprocess.run([sys.executable, str(MERGE), kind, str(out), *map(str, files)],
                          capture_output=True, text=True)


class SkillsLinkingTest(HomeCase):
    def names(self, directory):
        return sorted(p.name for p in directory.iterdir())

    def test_S7_every_public_and_fleet_skill_is_linked_into_both_homes(self):
        self.install()
        for home in (".claude/skills", ".agents/skills"):
            directory = self.home / home
            self.assertTrue(directory.is_dir() and not directory.is_symlink(), home)
            self.assertEqual(self.names(directory), ["alpha", "beta", "secret"])
            self.assertEqual((directory / "alpha").resolve(), self.skills / "skills" / "alpha")
            self.assertEqual((directory / "secret").resolve(), self.fleet / "skills" / "secret")

    def test_S7_install_is_idempotent(self):
        self.install()
        first = {p: p.resolve() for p in (self.home / ".claude/skills").iterdir()}
        self.install()
        self.assertEqual(first, {p: p.resolve() for p in (self.home / ".claude/skills").iterdir()})

    def test_S7_missing_fleet_is_skipped(self):
        self.install(AGENT_FLEET_DIR=self.tmp / "absent")
        self.assertEqual(self.names(self.home / ".claude/skills"), ["alpha", "beta"])

    def test_S7_migrates_symlinked_skills_dir_and_preserves_data(self):
        old = self.tmp / "old-skills"
        (old / "synced" / "claude-ai-skill").mkdir(parents=True)
        (old / "synced" / "claude-ai-skill" / "SKILL.md").write_text("keep me")
        (old / "upstream-thing").mkdir()
        (old / "upstream-thing" / "SKILL.md").write_text("installed by npx")
        (old / "alpha").mkdir()  # stale tracked copy of a managed skill
        (self.home / ".claude").mkdir()
        (self.home / ".agents").mkdir()
        (self.home / ".claude/skills").symlink_to(old)
        (self.home / ".agents/skills").symlink_to(old)
        self.install()
        claude, agents = self.home / ".claude/skills", self.home / ".agents/skills"
        for directory in (claude, agents):
            self.assertFalse(directory.is_symlink())
        self.assertEqual((claude / "synced/claude-ai-skill/SKILL.md").read_text(), "keep me")
        self.assertEqual((agents / "upstream-thing/SKILL.md").read_text(), "installed by npx")
        self.assertEqual((claude / "upstream-thing/SKILL.md").read_text(), "installed by npx")
        self.assertEqual((claude / "alpha").resolve(), self.skills / "skills" / "alpha")
        self.assertFalse((old / "alpha").exists())
        moved = list((self.home / ".dotfiles-backup").glob("skills-*/alpha"))
        self.assertEqual(len(moved), 1, "the stale copy is backed up, not deleted")

    def test_S7_junk_only_dirs_are_not_salvaged_as_skills(self):
        old = self.tmp / "old-skills"
        (old / "frontend-design" / "__pycache__").mkdir(parents=True)
        (old / "frontend-design" / "__pycache__" / "x.pyc").write_text("")
        (old / "frontend-design" / ".DS_Store").write_text("")
        (self.home / ".agents").mkdir()
        (self.home / ".agents/skills").symlink_to(old)
        self.install()
        self.assertFalse((self.home / ".agents/skills/frontend-design").exists())
        self.assertFalse((self.home / ".claude/skills/frontend-design").exists())

    def test_S7_hints_to_remove_the_old_marketplace_only_when_it_is_registered(self):
        done = self.install()
        self.assertNotIn("marketplace remove dotfiles", done.stdout + done.stderr)
        known = self.home / ".claude/plugins/known_marketplaces.json"
        known.parent.mkdir(parents=True)
        known.write_text('{"dotfiles": {"installLocation": "x"}}')
        done = self.install()
        self.assertIn("claude plugin marketplace remove dotfiles", done.stdout + done.stderr)

    def test_S7_migrates_a_dangling_symlink_using_the_old_dotfiles_skills_dir(self):
        (self.home / ".claude").mkdir()
        (self.home / ".claude/skills").symlink_to(self.tmp / "gone")
        self.install()
        self.assertTrue((self.home / ".claude/skills").is_dir())
        self.assertFalse((self.home / ".claude/skills").is_symlink())

    def test_S7_never_replaces_a_real_skill_dir_it_does_not_own(self):
        (self.home / ".claude/skills/alpha").mkdir(parents=True)
        (self.home / ".claude/skills/alpha/SKILL.md").write_text("mine")
        done = self.install()
        self.assertEqual((self.home / ".claude/skills/alpha/SKILL.md").read_text(), "mine")
        self.assertIn("alpha", done.stdout + done.stderr)

    def test_S7_clones_the_public_repos_when_missing(self):
        origin = make_repo(self.tmp / "origin-skills", ["gamma"])
        target = self.tmp / "cloned" / "agent-skills"
        self.install(AGENT_SKILLS_DIR=target, AGENT_SKILLS_REPO=origin)
        self.assertTrue((target / "skills/gamma/SKILL.md").is_file())
        self.assertTrue((self.home / ".claude/skills/gamma").exists())

    def test_S7_upstream_flag_runs_the_documented_installer(self):
        script = self.skills / "scripts" / "install-upstream.sh"
        script.parent.mkdir(exist_ok=True)
        script.write_text(f'#!/bin/sh\necho ran > "{self.tmp}/upstream.ran"\n')
        script.chmod(0o755)
        self.install()
        self.assertFalse((self.tmp / "upstream.ran").exists())
        self.install("--upstream")
        self.assertTrue((self.tmp / "upstream.ran").exists())
        readme = (ROOT / "README.md").read_text()
        self.assertIn("install-upstream.sh", readme)
        self.assertRegex(readme, r"impeccable.*frontend-design")


@unittest.skipUnless(shutil.which("stow"), "GNU Stow not installed")
class StowMigrationTest(HomeCase):
    """install.sh WITH stow, in a temp HOME migrated from the old layout, leftovers included."""

    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "dotfiles"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        (self.repo / ".git").write_text("gitdir: elsewhere\n")  # install.sh only checks that it exists

    def run_stow_install(self):
        done = subprocess.run([str(self.repo / "install.sh")], env=self.env(), cwd=self.repo, capture_output=True,
                              text=True, timeout=180)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return done

    def test_S7_stow_runs_cleanly_over_ignored_leftovers_of_the_old_skills_dir(self):
        old = self.repo / "agents/.agents/skills"
        (old / "alpha" / "narrator" / "node_modules" / "pkg").mkdir(parents=True)
        (old / "alpha" / "narrator" / "node_modules" / "pkg" / "index.js").write_text("x")
        (old / "alpha" / "scripts" / "__pycache__").mkdir(parents=True)
        (old / "alpha" / "scripts" / "__pycache__" / "m.pyc").write_text("")
        (old / "synced" / "claude-ai").mkdir(parents=True)
        (old / "synced" / "claude-ai" / "SKILL.md").write_text("keep")
        (old / "frontend-design").mkdir()
        (old / "frontend-design" / ".DS_Store").write_text("")
        for name in (".claude", ".agents"):
            (self.home / name).mkdir()
            (self.home / name / "skills").symlink_to(old)
        (self.home / ".claude/settings.json").symlink_to(self.repo / "agents/.claude/settings.base.json")
        self.run_stow_install()
        again = self.run_stow_install()  # and a second run is still clean
        self.assertNotIn("moved leftover", again.stdout)
        claude = self.home / ".claude/skills"
        self.assertFalse(claude.is_symlink())
        self.assertEqual((claude / "alpha").resolve(), self.skills / "skills" / "alpha")
        self.assertEqual((claude / "synced/claude-ai/SKILL.md").read_text(), "keep")
        self.assertFalse((claude / "frontend-design").exists())
        backups = list((self.home / ".dotfiles-backup").glob("skills-*/alpha/narrator/node_modules/pkg/index.js"))
        self.assertEqual(len(backups), 1, "ignored leftovers are backed up, never deleted")
        self.assertTrue((self.home / ".claude/statusline.sh").is_symlink(), "other agent files are still stowed")
        self.assertFalse((self.home / ".claude/settings.json").is_symlink())


class RuntimeWiringTest(HomeCase):
    def test_S6_runtime_install_script_runs_with_the_local_bin_dir(self):
        self.install()
        for name in ("agent-runtime", "agent-runtime-hook", "agent-runtime-mcp"):
            self.assertTrue(os.access(self.home / ".local/bin" / name, os.X_OK), name)

    def test_S6_runtime_clone_is_fetched_when_missing(self):
        origin = make_runtime_stub(self.tmp / "origin-runtime")
        make_repo(origin)
        target = self.tmp / "cloned-runtime"
        self.install(AGENT_RUNTIME_DIR=target, AGENT_RUNTIME_REPO=origin)
        self.assertTrue((target / "install.sh").is_file())
        self.assertTrue((self.home / ".local/bin/agent-runtime-mcp").exists())

    @unittest.skipUnless(RUNTIME_SRC, "needs a local agent-runtime checkout (AGENT_RUNTIME_SRC)")
    def test_S6_codex_mcp_and_hook_commands_resolve_to_the_real_runtime(self):
        """The merged Codex config launches the MCP server and the hook through the installed shims."""
        self.install(AGENT_RUNTIME_DIR=RUNTIME_SRC)
        cfg = tomllib.loads((self.home / ".codex/config.toml").read_text())
        server = cfg["mcp_servers"]["agent-runtime"]
        env = {"PATH": os.environ["PATH"], "HOME": str(self.home)}
        init = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": init},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        done = subprocess.run([server["command"], *server["args"]], input="".join(json.dumps(m) + "\n" for m in lines),
                              env=env, capture_output=True, text=True, timeout=30)
        replies = {r["id"]: r for r in map(json.loads, done.stdout.splitlines()) if "id" in r}
        names = {t["name"] for t in replies[2]["result"]["tools"]}
        self.assertEqual(names, set(server["tools"]))
        hook = cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        payload = {"tool_name": "Bash", "tool_input": {"command": "hc kill t1"}, "agent_id": "a1"}
        done = subprocess.run(["sh", "-c", hook], input=json.dumps(payload), env=env, capture_output=True,
                              text=True, timeout=15)
        self.assertIn("deny", done.stdout)


class ConfigMergeTest(HomeCase):
    def overlay(self, claude=None, codex=None):
        directory = self.tmp / "overlay"
        directory.mkdir(exist_ok=True)
        if claude is not None:
            (directory / "claude-settings.json").write_text(claude if isinstance(claude, str) else json.dumps(claude))
        if codex is not None:
            (directory / "codex-config.toml").write_text(codex)
        return directory

    def live(self):
        return (json.loads((self.home / ".claude/settings.json").read_text()),
                tomllib.loads((self.home / ".codex/config.toml").read_text()))

    def base(self):
        return (json.loads((ROOT / "agents/.claude/settings.base.json").read_text()),
                tomllib.loads((ROOT / "agents/.codex/config.base.toml").read_text()))

    def test_S9_without_an_overlay_live_equals_the_valid_base(self):
        self.install()
        self.assertEqual(self.live(), self.base())

    def test_S9_with_an_overlay_live_is_base_merged_with_overlay(self):
        base_json, base_toml = self.base()
        overlay = self.overlay(
            claude={"autoMode": {"environment": ["x"]}, "model": "sonnet",
                    "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}},
            codex='notify = ["x"]\n[sandbox_workspace_write]\nwritable_roots = ["/tmp/x"]\n'
                  '[[hooks.PreToolUse]]\nmatcher = "^Extra$"\n')
        self.install(DOTFILES_PRIVATE=overlay)
        settings, config = self.live()
        self.assertEqual(settings["autoMode"], {"environment": ["x"]})
        self.assertEqual(settings["model"], "sonnet")
        self.assertEqual(settings["hooks"]["SessionStart"][0]["hooks"][0]["command"], "echo hi")
        self.assertEqual(settings["enabledPlugins"], base_json["enabledPlugins"])
        self.assertEqual(config["notify"], ["x"])
        self.assertEqual(config["sandbox_workspace_write"]["writable_roots"], ["/tmp/x"])
        self.assertTrue(config["sandbox_workspace_write"]["network_access"])
        matchers = [h["matcher"] for h in config["hooks"]["PreToolUse"]]
        self.assertEqual(matchers, [h["matcher"] for h in base_toml["hooks"]["PreToolUse"]] + ["^Extra$"])

    def test_S9_overlay_falls_back_to_the_legacy_claude_overlay_file(self):
        legacy = self.home / ".claude/private-overlay/settings.overlay.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps({"autoMode": {"environment": ["legacy"]}}))
        self.install()
        self.assertEqual(self.live()[0]["autoMode"], {"environment": ["legacy"]})

    def test_S9_an_invalid_overlay_fails_and_leaves_live_files_untouched(self):
        self.install()
        before = (self.home / ".claude/settings.json").read_text()
        done = self.install(check=False, DOTFILES_PRIVATE=self.overlay(claude="{not json"))
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual((self.home / ".claude/settings.json").read_text(), before)
        self.assertEqual(list((self.home / ".claude").glob("settings.json.tmp*")), [])

    def test_S9_replaces_a_symlinked_live_file_without_touching_its_target(self):
        target = self.tmp / "tracked-settings.json"
        target.write_text('{"model": "old"}')
        (self.home / ".claude").mkdir()
        (self.home / ".claude/settings.json").symlink_to(target)
        self.install()
        self.assertFalse((self.home / ".claude/settings.json").is_symlink())
        self.assertEqual(target.read_text(), '{"model": "old"}')
        self.assertTrue(list((self.home / ".claude").glob("settings.json.bak-*")), "previous content is backed up")

    def test_S9_rerun_is_stable_and_does_not_pile_up_backups(self):
        self.install()
        self.install()
        self.assertEqual(list((self.home / ".claude").glob("settings.json.bak-*")), [])

    def test_S9_merge_concatenates_arrays_and_deep_merges_tables(self):
        a, b, out = self.tmp / "a.json", self.tmp / "b.json", self.tmp / "out.json"
        a.write_text(json.dumps({"hooks": {"PreToolUse": [1], "x": {"k": 1}}, "list": ["a"], "s": "base"}))
        b.write_text(json.dumps({"hooks": {"PreToolUse": [2], "x": {"j": 2}}, "list": ["a", "b"], "s": "over"}))
        done = merge("json", out, a, b)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(out.read_text()), {"hooks": {"PreToolUse": [1, 2], "x": {"k": 1, "j": 2}},
                                                       "list": ["a", "b"], "s": "over"})

    def test_S9_toml_round_trips_every_shape_the_config_uses(self):
        src = self.tmp / "a.toml"
        src.write_text('top = 1\nname = "q\\"uote"\nflag = true\n[a.b]\nk = [1, 2]\n[a.b.c]\n"odd key" = "v"\n'
                       '[empty]\n[[arr]]\nm = "x"\n[arr.sub]\nz = 1\n[[arr]]\nm = "y"\n')
        out = self.tmp / "out.toml"
        done = merge("toml", out, src)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(tomllib.loads(out.read_text()), tomllib.loads(src.read_text()))

    def test_S9_codex_runtime_state_in_the_live_file_survives_a_rerun(self):
        overlay = self.overlay(codex='[projects."/overlay/proj"]\ntrust_level = "trusted"\n')
        self.install(DOTFILES_PRIVATE=overlay)
        live = self.home / ".codex/config.toml"
        live.write_text(live.read_text() + '\n[projects."/live/proj"]\ntrust_level = "trusted"\n'
                        '[hooks.state."cfg:pre_tool_use:0:0"]\ntrusted_hash = "sha256:new"\nenabled = true\n'
                        '[notice]\nseen = true\n[plugins."x@y"]\nenabled = true\n')
        self.install(DOTFILES_PRIVATE=overlay)
        config = tomllib.loads(live.read_text())
        self.assertEqual(sorted(config["projects"]), ["/live/proj", "/overlay/proj"])
        self.assertEqual(config["hooks"]["state"]["cfg:pre_tool_use:0:0"]["trusted_hash"], "sha256:new")
        self.assertTrue(config["notice"]["seen"] and config["plugins"]["x@y"]["enabled"])
        self.assertEqual(config["hooks"]["PreToolUse"], self.base()[1]["hooks"]["PreToolUse"], "base still wins elsewhere")

    def test_S9_only_runtime_tables_come_from_the_live_file(self):
        self.install()
        live = self.home / ".codex/config.toml"
        live.write_text(live.read_text().replace('model_reasoning_effort = "medium"', 'model_reasoning_effort = "low"'))
        self.install()
        self.assertEqual(tomllib.loads(live.read_text())["model_reasoning_effort"], "medium")

    def test_S9_claude_runtime_settings_survive_a_rerun(self):
        self.install()
        live = self.home / ".claude/settings.json"
        data = json.loads(live.read_text())
        data["enabledPlugins"]["extra@market"] = True
        data["permissions"]["allow"].append("Bash(ls:*)")
        data["model"] = "changed-in-session"
        live.write_text(json.dumps(data))
        self.install()
        settings = json.loads(live.read_text())
        self.assertIs(settings["enabledPlugins"]["extra@market"], True)
        self.assertIn("Bash(ls:*)", settings["permissions"]["allow"])
        self.assertIn("mcp__notion", settings["permissions"]["allow"])
        self.assertEqual(settings["model"], self.base()[0]["model"], "settings the base owns are regenerated")

    def test_S9_a_trailing_bang_key_replaces_instead_of_concatenating(self):
        a, b, out = self.tmp / "a.json", self.tmp / "b.json", self.tmp / "out.json"
        a.write_text(json.dumps({"args": ["a", "b"], "t": {"list": [1]}, "keep": [1]}))
        b.write_text(json.dumps({"args!": ["c"], "t": {"list!": [2]}, "keep": [2]}))
        self.assertEqual(merge("json", out, a, b).returncode, 0)
        self.assertEqual(json.loads(out.read_text()), {"args": ["c"], "t": {"list": [2]}, "keep": [1, 2]})
        toml_a, toml_b = self.tmp / "a.toml", self.tmp / "b.toml"
        toml_a.write_text('args = ["a"]\n')
        toml_b.write_text('"args!" = ["z"]\n')
        self.assertEqual(merge("toml", self.tmp / "o.toml", toml_a, toml_b).returncode, 0)
        self.assertEqual(tomllib.loads((self.tmp / "o.toml").read_text()), {"args": ["z"]})

    def test_S9_merge_never_writes_an_invalid_result(self):
        bad, out = self.tmp / "bad.json", self.tmp / "out.json"
        bad.write_text("{")
        out.write_text('{"keep": true}')
        self.assertNotEqual(merge("json", out, bad).returncode, 0)
        self.assertEqual(out.read_text(), '{"keep": true}')


if __name__ == "__main__":
    unittest.main()
