"""Resolver checks with injected env and hc runner; the real hc is never called."""

import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
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
        self.assertEqual(line({"HERDR_PANE_ID": "p1"}), "runtime=herdmates role=lead cli=claude")

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
        self.assertTrue(out.startswith("runtime=herdmates role=lead"))

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

    def test_json_output_has_same_fields(self):
        buf = io.StringIO()
        with patch.dict(app.os.environ, {}, clear=True), redirect_stdout(buf):
            self.assertEqual(app.main(["resolve", "--json", "--cli", "codex"]), 0)
        self.assertEqual(json.loads(buf.getvalue()), {"runtime": "native", "role": "lead", "cli": "codex"})


if __name__ == "__main__":
    unittest.main()
