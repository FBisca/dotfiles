"""Resolver checks with injected env and hc runner; the real hc is never called."""

import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import os
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agent-runtime.py"
spec = importlib.util.spec_from_file_location("agent_runtime", SCRIPT)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


def hc_returning(parent):
    return lambda terminal_id: {"id": terminal_id, "parent": parent}


def hc_failing(terminal_id):
    raise RuntimeError("hc failed")


def line(env, cli="claude", hc=None):
    return app.format_line(app.resolve(env, cli, hc or hc_failing))


class ResolveTests(unittest.TestCase):
    def test_S1_herdr_pane_with_claude_is_herdmates(self):
        self.assertEqual(line({"HERDR_PANE_ID": "p1"}), "runtime=herdmates role=unknown cli=claude")

    def test_S2_herdr_pane_with_codex_is_native(self):
        self.assertEqual(line({"HERDR_PANE_ID": "p1"}, cli="codex"), "runtime=native role=lead cli=codex")

    def test_S3_hc_terminal_without_parent_is_lead(self):
        self.assertEqual(line({"HC_TERMINAL_ID": "t1"}, hc=hc_returning(None)), "runtime=hc role=lead cli=claude")

    def test_S4_hc_terminal_with_parent_is_worker(self):
        self.assertEqual(line({"HC_TERMINAL_ID": "t1"}, hc=hc_returning("tX")),
                         "runtime=hc role=worker parent=tX cli=claude")

    def test_S5_no_variables_is_native_lead(self):
        self.assertEqual(line({}), "runtime=native role=lead cli=claude")

    def test_S6_herdr_pane_wins_over_hc_terminal(self):
        out = line({"HERDR_PANE_ID": "p1", "HC_TERMINAL_ID": "t1"}, hc=hc_returning("tX"))
        self.assertEqual(out, "runtime=herdmates role=unknown cli=claude")

    def test_S7_hc_failure_or_timeout_is_unknown_and_exits_zero(self):
        self.assertEqual(line({"HC_TERMINAL_ID": "t1"}), "runtime=hc role=unknown cli=claude")
        timeout = subprocess.TimeoutExpired("hc", 2)
        with patch.object(app.subprocess, "run", side_effect=timeout) as run:
            buf = io.StringIO()
            with patch.dict(app.os.environ, {"HC_TERMINAL_ID": "t1"}, clear=True), redirect_stdout(buf):
                code = app.main(["resolve"])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().strip(), "runtime=hc role=unknown cli=claude")
        self.assertEqual(run.call_args.kwargs["timeout"], 2)

    def test_S5_json_output_has_same_fields(self):
        buf = io.StringIO()
        with patch.dict(app.os.environ, {}, clear=True), redirect_stdout(buf):
            self.assertEqual(app.main(["resolve", "--json", "--cli", "codex"]), 0)
        self.assertEqual(json.loads(buf.getvalue()), {"runtime": "native", "role": "lead", "cli": "codex"})


BIN = Path(__file__).resolve().parents[5] / "bin" / "bin" / "agent-runtime"


class CliTests(unittest.TestCase):
    """Run the symlinked executable with a controlled env and a fake hc on PATH."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bindir = Path(self.temp.name)

    def fake_hc(self, body):
        path = self.bindir / "hc"
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_cli(self, *args, env=None):
        full = {"PATH": str(self.bindir) + ":/usr/bin:/bin"}
        full.update(env or {})
        done = subprocess.run([sys.executable, "-B", str(BIN), *args], env=full,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=15)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def hc_out(self, text):
        self.fake_hc("cat <<'EOF'\n%s\nEOF" % text)
        return self.run_cli("resolve", env={"HC_TERMINAL_ID": "t1"})

    def test_S3_null_parent_through_symlink_is_lead(self):
        self.assertEqual(self.hc_out('{"parent": null}'), "runtime=hc role=lead cli=claude")

    def test_S4_parent_through_symlink_is_worker(self):
        self.assertEqual(self.hc_out('{"parent": "tX"}'), "runtime=hc role=worker parent=tX cli=claude")

    def test_S4_non_string_empty_or_spaced_parent_is_unknown(self):
        for parent in ("5", '""', '"a b"', "[]", "true"):
            with self.subTest(parent=parent):
                self.assertEqual(self.hc_out('{"parent": %s}' % parent), "runtime=hc role=unknown cli=claude")

    def test_S7_missing_hc_is_unknown(self):
        self.assertEqual(self.run_cli("resolve", env={"HC_TERMINAL_ID": "t1"}),
                         "runtime=hc role=unknown cli=claude")

    def test_S7_nonzero_exit_is_unknown(self):
        self.fake_hc("exit 3")
        self.assertEqual(self.run_cli("resolve", env={"HC_TERMINAL_ID": "t1"}),
                         "runtime=hc role=unknown cli=claude")

    def test_S7_non_json_is_unknown(self):
        self.assertEqual(self.hc_out("not json"), "runtime=hc role=unknown cli=claude")

    def test_S7_json_list_or_missing_parent_is_unknown(self):
        self.assertEqual(self.hc_out("[1]"), "runtime=hc role=unknown cli=claude")
        self.assertEqual(self.hc_out("{}"), "runtime=hc role=unknown cli=claude")

    def test_S5_bad_cli_value_falls_back_and_exits_zero(self):
        self.assertEqual(self.run_cli("resolve", "--cli", "gemini"), "runtime=native role=unknown cli=claude")
        self.assertEqual(self.run_cli("resolve", "--bogus", "--cli", "codex"),
                         "runtime=native role=unknown cli=codex")


if __name__ == "__main__":
    unittest.main()
