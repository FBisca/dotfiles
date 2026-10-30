#!/usr/bin/env python3
"""Stdio MCP server for the agent runtime: JSON-RPC 2.0, one JSON message per line.

stdout carries protocol JSON only; diagnostics go to stderr.
"""

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_runtime as lib  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
SERVER_INFO = {"name": "agent-runtime", "version": "0.1.0"}


def schema(properties=None, required=()):
    return {"type": "object", "properties": properties or {}, "required": list(required)}


def text(description):
    return {"type": "string", "description": description}


TOOLS = [
    ("spawn", "Start one agent on one task in one checkout; put the whole task in the call. "
              "kind=lookup: short read-only work, use the CLI's own subagent tool instead. "
              "kind=worker: implementation, long tasks, Codex, or anything watched. cli defaults to claude. "
              "Returns its name and parent.",
     schema({"kind": {"type": "string", "enum": ["worker", "lookup"]}, "cli": {"type": "string", "enum": ["claude", "codex"]},
             "name": text("unique, a-z 0-9 - _, max 32"), "task": text("complete task text"),
             "cwd": text("checkout directory")}, ["kind", "name", "task", "cwd"])),
    ("message", "Send text to a worker. Never forces input past a permission dialog.",
     schema({"to": text("worker name"), "text": text("message")}, ["to", "text"])),
    ("resume", "Give a finished, idle or interrupted worker another turn. A new spawn is not resumption.",
     schema({"name": text("worker name"), "task": text("what to do next")}, ["name", "task"])),
    ("wait", "Block until the next child reports, none is working, or the named worker stops. Never poll. "
             "Returns the status records of the workers it names.",
     schema({"target": text("any, all or a worker name")}, ["target"])),
    ("status", "State of one agent: {name, runtime, role, parent, state, turn, native, next[]}. "
               "state is working|idle|blocked|done|exited|unknown; blocked needs the user.",
     schema({"name": text("worker name or address")}, ["name"])),
    ("list", "Status records of the agents you started (hc only).", schema()),
    ("collect", "Read a worker's actual result from its screen after its last prompt. Never infer success.",
     schema({"name": text("worker name")}, ["name"])),
    ("stop", "End a worker you started, after its work is accepted.",
     schema({"name": text("worker name")}, ["name"])),
    ("report", "Worker only: send your result or blocker to your parent when done or stuck.",
     schema({"text": text("result or blocker")}, ["text"])),
]
TOOL_NAMES = [name for name, _, _ in TOOLS]


def log(message):
    print("agent-runtime: %s" % message, file=sys.stderr, flush=True)


def tool_result(payload, is_error=False):
    body = payload if isinstance(payload, str) else json.dumps(payload, separators=(",", ":"))
    return {"content": [{"type": "text", "text": body}], "isError": is_error}


def runtime_name(env):
    return lib.resolve(env)["runtime"]


def call_status(arguments, env):
    name = arguments.get("name")
    if not isinstance(name, str) or not name:
        return tool_result("name is required", True)
    return tool_result(lib.status(runtime_name(env), name, env))


def call_list(arguments, env):
    runtime = runtime_name(env)
    if runtime != "hc":
        return tool_result("list is hc-only; use the runtime's own tools", True)
    return tool_result(lib.list_children(runtime, env))


IMPLEMENTED = {"status": call_status, "list": call_list}


def call_tool(name, arguments, env):
    handler = IMPLEMENTED.get(name)
    if handler is None:
        return tool_result("gap: %s not implemented yet; ask the user" % name, True)
    try:
        return handler(arguments, env)
    except Exception as error:  # a tool failure must not kill the server
        log("%s failed: %s" % (name, error))
        return tool_result("%s failed: %s" % (name, error), True)


def rpc_error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message, env):
    """Reply dict for a request, None for notifications and stray responses."""
    if not isinstance(message, dict):
        return rpc_error(None, -32600, "invalid request")
    method, request_id = message.get("method"), message.get("id")
    if not isinstance(method, str):
        if "result" in message or "error" in message:
            return None
        return rpc_error(request_id, -32600, "invalid request")
    if "id" not in message:
        return None
    params = message.get("params")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return rpc_error(request_id, -32602, "params must be an object")
    try:
        return dispatch(method, request_id, params, env)
    except Exception as error:
        log("%s failed: %s" % (method, error))
        return rpc_error(request_id, -32603, "internal error")


def dispatch(method, request_id, params, env):
    if method == "initialize":
        asked = params.get("protocolVersion")
        version = asked if asked in SUPPORTED_VERSIONS else PROTOCOL_VERSION
        result = {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": n, "description": d, "inputSchema": s} for n, d, s in TOOLS]}
    elif method == "tools/call":
        name = params.get("name")
        if name not in TOOL_NAMES:
            return rpc_error(request_id, -32602, "unknown tool: %s" % name)
        arguments = params.get("arguments")
        result = call_tool(name, arguments if isinstance(arguments, dict) else {}, env)
    else:
        return rpc_error(request_id, -32601, "method not found: %s" % method)
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def serve(stdin=None, stdout=None, env=None):
    stdin = stdin or io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace", newline=None)
    stdout = stdout or sys.stdout
    env = dict(os.environ if env is None else env)
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            reply = handle(json.loads(line), env)
        except json.JSONDecodeError:
            reply = rpc_error(None, -32700, "parse error")
        if reply is not None:
            stdout.write(json.dumps(reply, separators=(",", ":")) + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(serve())
