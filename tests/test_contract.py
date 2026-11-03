"""Contracts between this repo's agent config and the agent-runtime plugin it consumes.

Re-homed from the runtime's own suite: these read dotfiles files, so they live here."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from support import ROOT, RUNTIME_SRC

SETTINGS = json.loads((ROOT / "agents/.claude/settings.base.json").read_text())
CODEX = tomllib.loads((ROOT / "agents/.codex/config.base.toml").read_text())
RUNTIME = CODEX["mcp_servers"]["agent-runtime"]
TOOLS = ["spawn", "message", "resume", "wait", "status", "list", "collect", "stop", "report", "task"]
MUTATING = ["spawn", "message", "resume", "stop", "report", "task"]
ENV_VARS = ["HC_TERMINAL_ID", "HC_SCOPE", "HC_TERMINAL_SOCKET", "HERDR_PANE_ID",
            "HERDR_ENV", "HERDR_SOCKET_PATH", "HERDR_SESSION"]
PLUGIN_TOOL = "mcp__plugin_agent-runtime_agent-runtime"


class CodexWiringTest(unittest.TestCase):
    def test_mcp_server_has_env_vars_and_approval_modes(self):
        self.assertEqual(RUNTIME["env_vars"], ENV_VARS)
        self.assertEqual(RUNTIME["env"]["AGENT_RUNTIME_DISPATCH"], "1")
        self.assertEqual(RUNTIME["default_tools_approval_mode"], "auto")
        self.assertEqual(RUNTIME["tool_timeout_sec"], 600)
        self.assertEqual(sorted(RUNTIME["tools"]), sorted(TOOLS))
        for tool in TOOLS:
            self.assertEqual(RUNTIME["tools"][tool]["output_token_limit"], 524288, tool)
        for tool in MUTATING:
            self.assertEqual(RUNTIME["tools"][tool]["approval_mode"], "approve", tool)
        for tool in set(TOOLS) - set(MUTATING):
            self.assertNotIn("approval_mode", RUNTIME["tools"][tool], tool)

    def test_mcp_command_runs_the_installed_shim_through_a_shell(self):
        self.assertEqual(RUNTIME["command"], "sh")
        self.assertIn("$HOME/.local/bin/agent-runtime-mcp", " ".join(RUNTIME["args"]))

    def test_pre_tool_use_hooks_guard_bash_and_the_runtime_tools(self):
        hooks = CODEX["hooks"]
        self.assertNotIn("SessionStart", hooks)
        pre = hooks["PreToolUse"]
        self.assertEqual([entry["matcher"] for entry in pre], ["^Bash$", "^mcp__agent-runtime__.*$"])
        self.assertRegex("mcp__agent-runtime__task", pre[1]["matcher"])
        for entry in pre:
            self.assertEqual(entry["hooks"][0]["command"], '"$HOME/.local/bin/agent-runtime-hook" --cli codex')
            self.assertEqual(entry["hooks"][0]["timeout"], 5)

    def test_every_tool_the_runtime_serves_is_configured(self):
        if RUNTIME_SRC is None:
            self.skipTest("needs a local agent-runtime checkout")
        text = (RUNTIME_SRC / "server" / "mcp_server.py").read_text()
        for tool in TOOLS:
            self.assertIn(f'("{tool}",', text)


class ClaudeSettingsTest(unittest.TestCase):
    def test_R75_plugin_and_marketplace_are_enabled_and_tools_allowed(self):
        self.assertIs(SETTINGS["enabledPlugins"].get("agent-runtime@agent-runtime"), True)
        self.assertIn(PLUGIN_TOOL, SETTINGS["permissions"]["allow"])
        self.assertNotIn("PreToolUse", SETTINGS.get("hooks", {}), "subagent denials come from the plugin's own hooks")

    def test_R87_marketplace_is_a_home_relative_directory_source(self):
        market = SETTINGS["extraKnownMarketplaces"]["agent-runtime"]["source"]
        self.assertEqual(market, {"source": "directory", "path": "~/developer/agent-runtime"})
        for bad in ("/" + "Users/", "/" + "home/", str(Path.home())):
            self.assertNotIn(bad, json.dumps(SETTINGS))

    def test_base_settings_hold_nothing_machine_specific(self):
        text = json.dumps(SETTINGS)
        self.assertNotIn("autoMode", SETTINGS)
        self.assertNotIn("hooks", SETTINGS)
        self.assertNotIn("heavy-jobs", text)

    def test_statusline_script_is_tracked_and_referenced_home_relative(self):
        command = SETTINGS["statusLine"]["command"]
        self.assertIn("$HOME/.claude/statusline.sh", command)
        self.assertTrue((ROOT / "agents/.claude/statusline.sh").is_file())
        done = subprocess.run(["sh", str(ROOT / "agents/.claude/statusline.sh")], capture_output=True, text=True,
                              input=json.dumps({"model": {"display_name": "M"},
                                                "context_window": {"used_percentage": 50, "context_window_size": 200000}}))
        self.assertEqual(done.returncode, 0)
        self.assertIn("50%", done.stdout)

    def test_R88_marketplace_registers_at_the_expanded_home_path(self):
        if os.environ.get("AGENT_RUNTIME_LIVE") != "1" or not shutil.which("claude") or RUNTIME_SRC is None:
            self.skipTest("set AGENT_RUNTIME_LIVE=1 with claude on PATH and a runtime checkout")
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir()
            (home / "developer").mkdir()
            (home / "developer" / "agent-runtime").symlink_to(RUNTIME_SRC)
            (home / ".claude" / "settings.json").write_text(json.dumps(
                {"extraKnownMarketplaces": {"agent-runtime": SETTINGS["extraKnownMarketplaces"]["agent-runtime"]},
                 "enabledPlugins": {"agent-runtime@agent-runtime": True}}))
            run = subprocess.run(["claude", "-p", "reply ok", "--max-turns", "1"], cwd=tmp, timeout=90,
                                 env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            known = json.loads((home / ".claude/plugins/known_marketplaces.json").read_text())
            self.assertEqual(known["agent-runtime"]["installLocation"], f"{tmp}/developer/agent-runtime", run.stderr)

    def test_R93_enabled_plugin_key_matches_the_runtime_marketplace(self):
        if RUNTIME_SRC is None:
            self.skipTest("needs a local agent-runtime checkout")
        market = json.loads((RUNTIME_SRC / ".claude-plugin/marketplace.json").read_text())
        plugin, _, marketplace = "agent-runtime@agent-runtime".partition("@")
        self.assertEqual(market["name"], marketplace)
        self.assertIn(plugin, [p["name"] for p in market["plugins"]])
        self.assertEqual(
            json.loads((RUNTIME_SRC / ".mcp.json").read_text())["mcpServers"].keys(), {"agent-runtime"})


class ImplementerAgentTest(unittest.TestCase):
    def test_claude_worker_tools_include_the_dispatch_flow(self):
        text = (ROOT / "agents/.claude/agents/implementer.md").read_text()
        line = next(l for l in text.split("---")[1].splitlines() if l.startswith("tools:"))
        tools = {t.strip() for t in line[len("tools:"):].strip().strip("[]").split(",")}
        for tool in ("report", "message", "wait", "task", "status"):
            self.assertIn(f"{PLUGIN_TOOL}__{tool}", tools)

    def test_both_implementers_report_through_tool_results(self):
        for path in ("agents/.claude/agents/implementer.md", "agents/.codex/agents/implementer.toml"):
            text = (ROOT / path).read_text()
            self.assertIn("report(kind, assignment_id)", text, path)
            self.assertIn("tool results", text, path)
            self.assertIn("wait(target=inbox, timeout=0)", text, path)
            self.assertNotIn("native messaging", text, path)


@unittest.skipUnless(shutil.which("zsh"), "zsh not installed")
class CodexWrapperTest(unittest.TestCase):
    def run_codex(self, *args, hc=True):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "codex"
            fake.write_text('#!/bin/sh\necho "ARGS:$*"\n')
            fake.chmod(0o755)
            env = {"PATH": f"{tmp}:/usr/bin:/bin", "HOME": tmp}
            if hc:
                env["HC_TERMINAL_ID"] = "t1"
            out = subprocess.run(["zsh", "-fc", f'source "{ROOT / "zsh/.zsh/aliases.zsh"}"; codex "$@"', "zsh", *args],
                                 env=env, text=True, capture_output=True, check=True).stdout
            return out.strip().splitlines()[-1]

    def test_codex_wrapper_adds_no_daemon_under_hc(self):
        self.assertEqual(self.run_codex("exec", "hi"), "ARGS:--no-daemon exec hi")

    def test_codex_wrapper_is_unchanged_without_hc(self):
        self.assertEqual(self.run_codex("exec", "hi", hc=False), "ARGS:exec hi")

    def test_codex_wrapper_respects_explicit_daemon_flags(self):
        self.assertEqual(self.run_codex("--daemon", "x"), "ARGS:--daemon x")
        self.assertEqual(self.run_codex("--no-daemon", "x"), "ARGS:--no-daemon x")


class ReadmeAgentSectionTest(unittest.TestCase):
    def section(self):
        text = (ROOT / "README.md").read_text()
        start = text.index("## Agent tooling")
        end = text.find("\n## ", start + 1)
        return text[start:end if end > 0 else None]

    def test_R91_readme_says_in_place_next_session_record_only_and_no_update_steps(self):
        section = self.section()
        self.assertRegex(section, r"(?i)in place")
        self.assertRegex(section, r"(?i)next (Claude/Codex )?session")
        self.assertRegex(section, r"(?i)record[- ]only")
        self.assertNotIn("marketplace update", section)
        self.assertNotIn("plugin update", section)

    def test_readme_links_both_repos_and_the_workflow_doc(self):
        section = self.section()
        for url in ("https://github.com/FBisca/agent-runtime", "https://github.com/FBisca/agent-skills",
                    "https://github.com/FBisca/agent-skills/blob/main/docs/workflow.md"):
            self.assertIn(url, section)


if __name__ == "__main__":
    unittest.main()
