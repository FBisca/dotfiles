"""MCP server driven over stdio with a fake hc on PATH, and plugin wiring checks."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SERVER = PLUGIN / "server" / "mcp_server.py"
MARKETPLACE = PLUGIN.parents[1] / ".claude-plugin" / "marketplace.json"
TOOLS = ["spawn", "message", "resume", "wait", "status", "list", "collect", "stop", "report"]


class Session:
    """One server subprocess speaking newline-delimited JSON-RPC."""

    def __init__(self, env):
        self.proc = subprocess.Popen([sys.executable, "-B", str(SERVER)], env=env, text=True,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.next_id = 0

    def send(self, method, params=None, notify=False):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        if not notify:
            self.next_id += 1
            message["id"] = self.next_id
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        reply = json.loads(self.proc.stdout.readline())
        assert reply["id"] == self.next_id, reply
        return reply

    def handshake(self):
        reply = self.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                         "clientInfo": {"name": "test", "version": "0"}})
        self.send("notifications/initialized", notify=True)
        return reply

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=10)
        self.proc.stdout.close()
        self.proc.stderr.close()


class ServerCase(unittest.TestCase):
    def start(self, hc_body=None, env=None):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        bindir = Path(temp.name)
        if hc_body is not None:
            hc = bindir / "hc"
            hc.write_text("#!/bin/sh\n" + hc_body + "\n")
            hc.chmod(0o755)
        full = {"PATH": "%s:/usr/bin:/bin" % bindir}
        full.update(env or {})
        session = Session(full)
        self.addCleanup(session.close)
        return session


class ToolListTests(ServerCase):
    def test_S1_tools_list_returns_the_nine_tools_within_400_words(self):
        """agent-runtime-tools/S1"""
        session = self.start()
        init = session.handshake()
        self.assertIn("tools", init["result"]["capabilities"])
        tools = session.send("tools/list")["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], TOOLS)
        for tool in tools:
            self.assertEqual(tool["inputSchema"]["type"], "object")
        words = sum(len(t["description"].split()) for t in tools)
        self.assertLessEqual(words, 400)

    def test_ping_and_unknown_method(self):
        session = self.start()
        session.handshake()
        self.assertEqual(session.send("ping")["result"], {})
        self.assertEqual(session.send("nope")["error"]["code"], -32601)

    def test_stdout_carries_only_protocol_json(self):
        session = self.start()
        session.handshake()
        session.send("tools/list")
        session.proc.stdin.write("not json\n")
        session.proc.stdin.flush()
        reply = json.loads(session.proc.stdout.readline())
        self.assertEqual(reply["error"]["code"], -32700)


class ToolCallTests(ServerCase):
    def call(self, session, name, arguments):
        return session.send("tools/call", {"name": name, "arguments": arguments})["result"]

    def test_status_wraps_the_library_with_a_fake_hc(self):
        raw = {"address": "t9", "name": "w1", "parent": "t0", "status": {"app": "x", "state": "idle"}}
        session = self.start("echo '%s'" % json.dumps(raw), env={"HC_TERMINAL_ID": "t0"})
        session.handshake()
        result = self.call(session, "status", {"name": "w1"})
        self.assertFalse(result.get("isError"))
        info = json.loads(result["content"][0]["text"])
        self.assertEqual((info["runtime"], info["state"], info["parent"]), ("hc", "idle", "t0"))

    def test_list_returns_children_of_the_caller(self):
        body = ('case "$1" in ls) echo \'{"terminals":[{"address":"t5","parent":"t0"},{"address":"t6","parent":"tX"}]}\';;'
                ' get) echo \'{"address":"t5","name":"w5","parent":"t0","status":"working"}\';; esac')
        session = self.start(body, env={"HC_TERMINAL_ID": "t0"})
        session.handshake()
        result = self.call(session, "list", {})
        rows = json.loads(result["content"][0]["text"])
        self.assertEqual([r["name"] for r in rows], ["w5"])

    def test_unimplemented_tools_return_an_error_result(self):
        session = self.start()
        session.handshake()
        result = self.call(session, "spawn", {})
        self.assertTrue(result["isError"])
        self.assertIn("not implemented", result["content"][0]["text"])

    def test_unknown_tool_is_a_protocol_error(self):
        session = self.start()
        session.handshake()
        reply = session.send("tools/call", {"name": "bogus", "arguments": {}})
        self.assertEqual(reply["error"]["code"], -32602)


class WiringTests(unittest.TestCase):
    def load(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def test_S18_manifest_mcp_and_hooks_files_are_valid_and_wired(self):
        """agent-runtime-tools/S18"""
        manifest = self.load(PLUGIN / ".claude-plugin" / "plugin.json")
        self.assertEqual(manifest["name"], "agent-runtime")
        self.assertTrue(manifest["description"])
        mcp = self.load(PLUGIN / ".mcp.json")
        server = mcp["mcpServers"]["agent-runtime"]
        self.assertEqual(server["command"], "python3")
        self.assertEqual(server["args"], ["${CLAUDE_PLUGIN_ROOT}/server/mcp_server.py"])
        for name in ("HC_TERMINAL_ID", "HC_SCOPE", "HC_TERMINAL_SOCKET", "HERDR_PANE_ID", "HERDR_ENV",
                     "HERDR_SOCKET_PATH", "HERDR_SESSION"):
            self.assertEqual(server["env"][name], "${%s:-}" % name)
        hooks = self.load(PLUGIN / "hooks" / "hooks.json")
        self.assertIsInstance(hooks["hooks"], dict)
        self.assertTrue(SERVER.is_file())

    def test_S18_local_marketplace_lists_the_plugin_by_relative_source(self):
        """agent-runtime-tools/S18"""
        market = self.load(MARKETPLACE)
        self.assertTrue(market["name"])
        self.assertTrue(market["owner"]["name"])
        entry = {p["name"]: p for p in market["plugins"]}["agent-runtime"]
        self.assertEqual(entry["source"], "./plugins/agent-runtime")
        self.assertTrue((MARKETPLACE.parents[1] / entry["source"] / ".claude-plugin" / "plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
