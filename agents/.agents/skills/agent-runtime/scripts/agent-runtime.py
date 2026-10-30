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


def resolve(env, cli="claude", hc_runner=hc_get):
    """Pure resolution: HERDR_PANE_ID > HC_TERMINAL_ID > native. Never raises on hc failure."""
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
        parent = reply["parent"]
        if parent is None:
            return {"runtime": "hc", "role": "lead", "cli": cli}
        if isinstance(parent, str) and parent and not any(c.isspace() for c in parent):
            return {"runtime": "hc", "role": "worker", "parent": parent, "cli": cli}
        return unknown
    return {"runtime": "native", "role": "lead", "cli": cli}


def format_line(info):
    return " ".join("%s=%s" % (key, info[key]) for key in FIELDS if key in info)


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


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-runtime", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("resolve", help="print the runtime, role and parent of this agent")
    p.add_argument("--cli", choices=("claude", "codex"), default="claude")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_resolve)
    for name, func, text in (("contract", cmd_contract, "print the verbs, gap rule and the resolved runtime's adapter"),
                             ("help", cmd_help, "list the runtime's capabilities and whether each is in the contract")):
        q = sub.add_parser(name, help=text)
        q.add_argument("--cli", choices=("claude", "codex"), default="claude")
        q.add_argument("--runtime", choices=RUNTIMES, help="override the resolved runtime")
        q.set_defaults(func=func)
    return parser


def fallback_resolve(argv):
    """Last resort for hooks: always a valid line, never a failure."""
    cli = "claude"
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
