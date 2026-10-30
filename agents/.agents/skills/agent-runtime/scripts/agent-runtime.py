#!/usr/bin/env python3
"""Runtime contract helper for delegating to other agents. No model calls or agent spawns."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HC_TIMEOUT_SECONDS = 2
SKILL_DIR = Path(__file__).resolve().parent.parent
RUNTIMES = ("herdmates", "hc", "native")
FIELDS = ("runtime", "role", "parent", "cli")


def hc_get(terminal_id):
    result = subprocess.run(["hc", "get", terminal_id], capture_output=True, text=True,
                            stdin=subprocess.DEVNULL, timeout=HC_TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "hc get failed")
    return json.loads(result.stdout)


CODEX_ENV_MARKERS = ("CODEX_THREAD_ID", "CODEX_SANDBOX")


def detect_cli(env):
    """Codex sets CODEX_THREAD_ID (and CODEX_SANDBOX when sandboxed) for the commands it runs.
    Claude Code sets CLAUDECODE=1, which wins over a marker inherited from a parent Codex."""
    if env.get("CLAUDECODE"):
        return "claude"
    return "codex" if any(env.get(name) for name in CODEX_ENV_MARKERS) else None


def foreground_cli(reply):
    """Fallback under hc: the terminal's foreground program is codex or claude."""
    foreground = reply.get("foreground") if isinstance(reply, dict) else None
    argv = foreground.get("argv") if isinstance(foreground, dict) else None
    if isinstance(argv, list) and argv and isinstance(argv[0], str):
        name = os.path.basename(argv[0])
        return name if name in ("codex", "claude") else None
    return None


def resolve(env, cli=None, hc_runner=hc_get):
    """Pure resolution: HERDR_PANE_ID > HC_TERMINAL_ID > native. Never raises on hc failure.
    cli=None detects it from the environment, then from hc, then defaults to claude."""
    explicit = cli
    cli = explicit or detect_cli(env) or "claude"
    if env.get("HERDR_PANE_ID"):
        runtime = "herdmates" if cli == "claude" else "native"
        return {"runtime": runtime, "role": "lead" if runtime == "native" else "unknown", "cli": cli}
    terminal_id = env.get("HC_TERMINAL_ID")
    if terminal_id:
        unknown = {"runtime": "hc", "role": "unknown", "cli": cli}
        try:
            reply = hc_runner(terminal_id)
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError):
            return unknown
        if not isinstance(reply, dict) or "parent" not in reply:
            return unknown
        if not explicit and not detect_cli(env):
            cli = foreground_cli(reply) or cli
            unknown["cli"] = cli
        parent = reply["parent"]
        if parent is None:
            return {"runtime": "hc", "role": "lead", "cli": cli}
        if isinstance(parent, str) and parent and not any(c.isspace() for c in parent):
            return {"runtime": "hc", "role": "worker", "parent": parent, "cli": cli}
        return unknown
    return {"runtime": "native", "role": "lead", "cli": cli}


def format_line(info):
    return " ".join("%s=%s" % (key, info[key]) for key in FIELDS if key in info)


CONTRACT_STATES = ("working", "idle", "blocked", "done", "exited", "unknown")
READ_ERRORS = (OSError, RuntimeError, ValueError, subprocess.SubprocessError)


def run_command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                            timeout=HC_TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Command failed: " + argv[0])
    return result.stdout.strip()


def row(why, do, verb=None):
    return {"why": why, "do": do, "verb": verb, "gap": verb is None}


def record(runtime, name, state, role="unknown", parent=None, turn=None, native=None, next_rows=()):
    return {"name": name, "runtime": runtime, "role": role, "parent": parent, "state": state,
            "turn": turn, "native": native, "next": list(next_rows)}


def hc_state(raw):
    """Map an `hc get`/`hc ls` record (status is an object {app, state} or a string) to a contract state."""
    if raw.get("state") == "finished":
        return "exited"
    status = raw.get("status")
    if isinstance(status, dict):
        status = status.get("state")
    return status if status in ("working", "idle", "blocked", "done") else "unknown"


def hc_next(name, state):
    if state == "done":
        return [row("work finished", "read the result", "collect"), row("worker no longer needed", "end it", "stop")]
    if state == "idle":
        return [row("turn ended, awaiting input", "send the next instruction", "message"),
                row("read what it produced", "read the result", "collect")]
    if state == "working":
        return [row("still running", "block until it reports", "wait")]
    if state == "blocked":
        return [row("a person is needed (permission or question)", "read the screen and ask the user", "collect"),
                row("answer the dialog only with the user's say-so", "hc keys %s <keys>" % name)]
    if state == "exited":
        return [row("process ended", "read the output", "collect"), row("clean up", "end it", "stop")]
    return [row("state not reported", "check again", "status"), row("see the screen", "read the output", "collect")]


HC_NATIVE_KEYS = ("address", "name", "state", "status", "turn", "exit_code", "reason")
HERDR_NOTE = "read only; verify live agent identity before mapping a task to this pane"


def hc_native(raw):
    native = {key: raw.get(key) for key in HC_NATIVE_KEYS}
    foreground = raw.get("foreground")
    native["foreground"] = {"argv": foreground.get("argv")} if isinstance(foreground, dict) else None
    return native


def hc_record(name, raw):
    state = hc_state(raw)
    parent = raw.get("parent")
    return record("hc", raw.get("name") or raw.get("address") or name, state,
                  role="worker" if parent else "lead", parent=parent, turn=raw.get("turn"),
                  native=hc_native(raw), next_rows=hc_next(raw.get("name") or raw.get("address") or name, state))


def herdr_snapshot(pane, session, env):
    if env.get("HERDR_ENV") != "1":
        raise ValueError("Herdr inspection requires a Herdr-managed caller")
    if not (env.get("HERDR_SOCKET_PATH") and env.get("HERDR_PANE_ID")):
        raise ValueError("missing Herdr caller identity")
    if not (session and session.strip()):
        raise ValueError("supply the exact Herdr session name")
    inherited = env.get("HERDR_SESSION")
    if inherited and inherited != session:
        raise ValueError("session differs from caller's session")
    target = pane or env["HERDR_PANE_ID"]
    if target.startswith("-"):
        raise ValueError("invalid pane ID")
    result = json.loads(run_command(["herdr", "pane", "get", target, "--session", session]))
    return {"session": session, "pane": target, "snapshot": result}


def find_key(value, key):
    if isinstance(value, dict):
        if key in value:
            return value[key]
        value = list(value.values())
    if isinstance(value, list):
        for item in value:
            found = find_key(item, key)
            if found is not None:
                return found
    return None


def status(runtime, name, env, session=None):
    """One contract record for one agent. Never raises on runtime failures."""
    try:
        if runtime == "hc":
            return hc_record(name, json.loads(run_command(["hc", "get", name, "--json"])))
        if runtime == "herdmates":
            snap = herdr_snapshot(name, session or env.get("HERDR_SESSION"), env)
            herdr = find_key(snap["snapshot"], "agent_status")
            state = herdr if herdr in ("idle", "working", "blocked", "done") else "unknown"
            rows = {"working": [row("still running", "end your turn; its message arrives as input", "wait")],
                    "idle": [row("turn ended", "send the next instruction", "message"),
                             row("read what it produced", "read its last message", "collect")],
                    "done": [row("work finished", "read its last message and the task result", "collect"),
                             row("no longer needed", "ask Claude to shut it down", "stop")],
                    "blocked": [row("a person is needed", "read the pane and ask the user", "collect")],
                    }.get(state, [row("state not reported", "check the native task list", "status")])
            native = {"pane": snap["pane"], "session": snap["session"], "agent_status": herdr, "note": HERDR_NOTE}
            return record("herdmates", snap["pane"], state, native=native, next_rows=rows)
    except READ_ERRORS as error:
        return record(runtime, name, "unknown", native={"error": str(error)},
                      next_rows=[row("status could not be read", "check again", "status"),
                                 row("see the output", "read it", "collect")])
    return record("native", name, "unknown", native={},
                  next_rows=[row("no process to query", "use the subagent's return value", "collect"),
                             row("ask it directly", "SendMessage to %s" % name, "message")])


def list_children(runtime, env):
    """hc: one record per live terminal whose parent is the caller. Other runtimes have no list."""
    if runtime != "hc":
        return []
    me = env.get("HC_TERMINAL_ID")
    infos = []
    if not me:
        return infos
    try:
        listing = json.loads(run_command(["hc", "ls", "--all", "--json"]))
    except READ_ERRORS:
        return infos
    for entry in listing.get("terminals", []):
        if entry.get("parent") != me:
            continue
        address = entry.get("address")
        try:
            infos.append(hc_record(address, json.loads(run_command(["hc", "get", address, "--json"]))))
        except READ_ERRORS:
            continue
    return infos
    for entry in listing.get("terminals", []):
        address = entry.get("address")
        try:
            raw = json.loads(run_command(["hc", "get", address, "--json"]))
        except READ_ERRORS:
            continue
        if me and raw.get("parent") == me:
            infos.append(hc_record(address, raw))
    return infos


def cmd_resolve(args):
    info = resolve(os.environ, args.cli)
    print(json.dumps(info) if args.json else format_line(info))
    return 0


def read_text(relative):
    return (SKILL_DIR / relative).read_text(encoding="utf-8")


def runtime_arg(args):
    return args.runtime or resolve(os.environ, args.cli)["runtime"]


def gap_rule():
    text = read_text("references/contract.md")
    start = text.index("## Gap rule")
    end = text.find("\n## ", start + 1)
    return text[start:end if end != -1 else len(text)].strip()


def cmd_contract(args):
    runtime = runtime_arg(args)
    print(read_text("references/contract.md").rstrip())
    print()
    print(read_text("adapters/%s.md" % runtime).rstrip())
    return 0


def cmd_help(args):
    runtime = runtime_arg(args)
    rows = json.loads(read_text("adapters/capabilities.json"))[runtime]
    print("Capabilities of runtime %s:" % runtime)
    for row in rows:
        print("- %s | in-contract: %s | %s" % (row["capability"], row["in_contract"], row["how"]))
    print()
    print(gap_rule())
    return 0


def dump(value, args):
    return json.dumps(value, indent=2) if args.pretty else json.dumps(value, separators=(",", ":"))


def cmd_status(args):
    info = status(runtime_arg(args), args.name, os.environ, session=args.session)
    print(dump(info, args))
    return 0


def cmd_list(args):
    runtime = runtime_arg(args)
    if runtime != "hc":
        print("list is only available under hc; use the runtime's own tools", file=sys.stderr)
    print(dump(list_children(runtime, os.environ), args))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-runtime", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("resolve", help="print the runtime, role and parent of this agent")
    p.add_argument("--cli", choices=("claude", "codex"), default=None,
                   help="default: detected from the environment, else claude")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_resolve)
    for name, func, text in (("contract", cmd_contract, "print the verbs, gap rule and the resolved runtime's adapter"),
                             ("help", cmd_help, "list the runtime's capabilities and whether each is in the contract")):
        q = sub.add_parser(name, help=text)
        q.add_argument("--cli", choices=("claude", "codex"), default=None,
                   help="default: detected from the environment, else claude")
        q.add_argument("--runtime", choices=RUNTIMES, help="override the resolved runtime")
        q.set_defaults(func=func)
    p = sub.add_parser("status", help="one JSON record for one agent")
    p.add_argument("name", help="hc terminal name or address; Herdr pane ID under herdmates")
    p.add_argument("--session", help="exact Herdr session name (herdmates)")
    p.add_argument("--cli", choices=("claude", "codex"), default=None,
                   help="default: detected from the environment, else claude")
    p.add_argument("--runtime", choices=RUNTIMES, help="override the resolved runtime")
    p.add_argument("--pretty", action="store_true", help="indent the JSON")
    p.set_defaults(func=cmd_status)
    p = sub.add_parser("list", help="JSON records for the agents you started (hc)")
    p.add_argument("--cli", choices=("claude", "codex"), default=None,
                   help="default: detected from the environment, else claude")
    p.add_argument("--runtime", choices=RUNTIMES, help="override the resolved runtime")
    p.add_argument("--pretty", action="store_true", help="indent the JSON")
    p.set_defaults(func=cmd_list)
    return parser


def fallback_resolve(argv):
    """Last resort for hooks: always a valid line, never a failure."""
    cli = detect_cli(os.environ) or "claude"
    for i, arg in enumerate(argv):
        value = arg.split("=", 1)[1] if arg.startswith("--cli=") else (
            argv[i + 1] if arg == "--cli" and i + 1 < len(argv) else None)
        if value in ("claude", "codex"):
            cli = value
    info = {"runtime": "native", "role": "unknown", "cli": cli}
    print(json.dumps(info) if "--json" in argv else format_line(info))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv[:1] == ["resolve"]:
        try:
            args = build_parser().parse_args(argv)
            return args.func(args)
        except (Exception, SystemExit):
            return fallback_resolve(argv)
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
