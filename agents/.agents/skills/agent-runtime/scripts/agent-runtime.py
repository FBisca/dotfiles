#!/usr/bin/env python3
"""Runtime contract helper for delegating to other agents. No model calls or agent spawns."""

import argparse
import json
import os
import subprocess
import sys

HC_TIMEOUT_SECONDS = 2
FIELDS = ("runtime", "role", "parent", "cli")


def hc_get(terminal_id):
    result = subprocess.run(["hc", "get", terminal_id], capture_output=True, text=True,
                            timeout=HC_TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "hc get failed")
    return json.loads(result.stdout)


def resolve(env, cli="claude", hc_runner=hc_get):
    """Pure resolution: HERDR_PANE_ID > HC_TERMINAL_ID > native. Never raises on hc failure."""
    if env.get("HERDR_PANE_ID"):
        runtime = "herdmates" if cli == "claude" else "native"
        return {"runtime": runtime, "role": "lead", "cli": cli}
    terminal_id = env.get("HC_TERMINAL_ID")
    if terminal_id:
        try:
            parent = hc_runner(terminal_id).get("parent")
        except (OSError, RuntimeError, ValueError, AttributeError, subprocess.SubprocessError):
            return {"runtime": "hc", "role": "unknown", "cli": cli}
        if parent:
            return {"runtime": "hc", "role": "worker", "parent": str(parent), "cli": cli}
        return {"runtime": "hc", "role": "lead", "cli": cli}
    return {"runtime": "native", "role": "lead", "cli": cli}


def format_line(info):
    return " ".join("%s=%s" % (key, info[key]) for key in FIELDS if key in info)


def cmd_resolve(args):
    info = resolve(os.environ, args.cli)
    print(json.dumps(info) if args.json else format_line(info))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-runtime", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("resolve", help="print the runtime, role and parent of this agent")
    p.add_argument("--cli", choices=("claude", "codex"), default="claude")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_resolve)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
