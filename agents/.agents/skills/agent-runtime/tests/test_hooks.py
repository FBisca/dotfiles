import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
HOOKS = SKILL / "hooks"
REPO = SKILL.parents[2]  # .../agents
SUFFIX = " · run agent-runtime contract before delegating"


def run_hook(name, payload, args=(), env_extra=None, hc_reply='{"parent": null}'):
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "hc"
        fake.write_text("#!/bin/sh\necho '%s'\n" % hc_reply)
        fake.chmod(0o755)
        env = {"PATH": tmp + ":/usr/bin:/bin", "HOME": tmp}
        env.update(env_extra or {})
        return subprocess.run([sys.executable, "-B", str(HOOKS / name), *args],
                              input=json.dumps(payload), capture_output=True, text=True,
                              env=env, timeout=20)


def bash(command, **extra):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash",
            "tool_input": {"command": command}, **extra}


def decision(result):
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


class SessionStartTests(unittest.TestCase):
    def test_S16_claude_session_context_has_pointer_line(self):
        r = run_hook("session_start.py", {"hook_event_name": "SessionStart"}, ["--cli", "claude"],
                     {"HC_TERMINAL_ID": "w1"}, '{"parent": "lead1"}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(),
                         "agent-runtime: runtime=hc role=worker parent=lead1" + SUFFIX)

    def test_S16_parent_dash_when_none(self):
        r = run_hook("session_start.py", {}, ["--cli", "claude"])
        self.assertEqual(r.stdout.strip(),
                         "agent-runtime: runtime=native role=lead parent=-" + SUFFIX)

    def test_S17_codex_session_context_has_same_line(self):
        r = run_hook("session_start.py", {"hook_event_name": "SessionStart", "source": "startup"},
                     ["--cli", "codex"], {"HERDR_PANE_ID": "p1"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(),
                         "agent-runtime: runtime=native role=lead parent=-" + SUFFIX)

    def test_S16_bad_stdin_still_exits_zero(self):
        r = subprocess.run([sys.executable, "-B", str(HOOKS / "session_start.py"), "--cli", "claude"],
                           input="not json", capture_output=True, text=True, timeout=20,
                           env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(r.returncode, 0)


class SubagentStartTests(unittest.TestCase):
    def test_S18_subagent_told_not_to_run_runtime_commands(self):
        r = run_hook("subagent_start.py", {"hook_event_name": "SubagentStart", "agent_id": "a1"})
        self.assertEqual(r.returncode, 0)
        out = json.loads(r.stdout)["hookSpecificOutput"]
        self.assertEqual(out["hookEventName"], "SubagentStart")
        ctx = out["additionalContext"]
        self.assertIn("subagent", ctx)
        self.assertIn("must not run runtime commands", ctx)
        self.assertIn("SendMessage", ctx)


class PreToolUseTests(unittest.TestCase):
    def assertDenied(self, command, **extra):
        r = run_hook("pre_tool_use.py", bash(command, **extra))
        self.assertEqual(r.returncode, 0)
        out = decision(r)
        self.assertIsNotNone(out, command)
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertTrue(out["permissionDecisionReason"])

    def assertAllowed(self, command, **extra):
        r = run_hook("pre_tool_use.py", bash(command, **extra))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "", command)

    def test_S19_subagent_hc_run_send_kill_denied(self):
        for command in ("hc run claude", "hc send t1 hi", "hc kill t1",
                        "cd x && hc send t1 hi", "echo a; hc kill t1", "echo a | hc run x",
                        "FOO=1 hc send t1 hi", "~/.local/bin/hc send t1 hi",
                        "/Users/x/.local/bin/hc run c", "(hc kill t1)", "  hc   send t1 hi"):
            with self.subTest(command=command):
                self.assertDenied(command, agent_id="a1")

    def test_S19_subagent_other_commands_allowed(self):
        for command in ("hc get t1", "hc ls", 'echo "hc send t1"', "git commit -m 'hc send'",
                        "grep 'hc kill' file", "ls"):
            with self.subTest(command=command):
                self.assertAllowed(command, agent_id="a1")

    def test_S20_teammux_launch_denied_for_everyone(self):
        self.assertDenied("herdmates teammux-launch foo")
        self.assertDenied("cd x && herdmates teammux-launch", agent_id="a1")
        self.assertAllowed('echo "herdmates teammux-launch"')

    def test_S21_lead_hc_send_allowed(self):
        for command in ("hc send t1 hi", "hc run claude", "hc kill t1"):
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_S21_internal_error_allows(self):
        r = subprocess.run([sys.executable, "-B", str(HOOKS / "pre_tool_use.py")],
                           input="garbage", capture_output=True, text=True, timeout=20)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, ""))


class WiringTests(unittest.TestCase):
    NEW = {"SessionStart": "session_start.py", "SubagentStart": "subagent_start.py",
           "PreToolUse": "pre_tool_use.py"}

    def test_S16_hook_scripts_executable(self):
        for name in self.NEW.values():
            self.assertTrue(os.access(HOOKS / name, os.X_OK), name)

    def test_S16_settings_json_has_new_entries_pointing_at_existing_files(self):
        settings = json.loads((REPO / ".claude/settings.json").read_text())
        for event, script in self.NEW.items():
            commands = [h["command"] for g in settings["hooks"][event] for h in g["hooks"]]
            match = [c for c in commands if c.split()[0].endswith("agent-runtime/hooks/" + script)]
            self.assertEqual(len(match), 1, event)
            path = match[0].split()[0].replace('"', "").replace("$HOME/", "")
            self.assertTrue((REPO / path).exists(), path)
        self.assertIn("--cli claude", [c for g in settings["hooks"]["SessionStart"]
                                       for h in g["hooks"] for c in [h["command"]]
                                       if "agent-runtime" in c][0])
        pre = [g for g in settings["hooks"]["PreToolUse"]
               if any("agent-runtime" in h["command"] for h in g["hooks"])]
        self.assertEqual(pre[0]["matcher"], "Bash")
        # existing hooks untouched
        existing = [h["command"] for g in settings["hooks"]["SessionStart"] for h in g["hooks"]]
        self.assertIn("/Users/fbisca/developer/agent-fleet/hooks/session_start.py", existing)

    def test_S17_codex_config_has_session_start_hook(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest("tomllib unavailable on this python; config.toml not parsed")
        config = tomllib.loads((REPO / ".codex/config.toml").read_text())
        hooks = [h for g in config["hooks"]["SessionStart"] for h in g["hooks"]]
        match = [h for h in hooks if "agent-runtime/hooks/session_start.py" in h["command"]]
        self.assertEqual(len(match), 1)
        self.assertIn("--cli codex", match[0]["command"])
        self.assertEqual(match[0]["type"], "command")


if __name__ == "__main__":
    unittest.main()
