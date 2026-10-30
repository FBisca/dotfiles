#!/usr/bin/env python3
"""SubagentStart hook: tell subagents and in-process teammates not to run runtime commands."""

import json
import sys

CONTEXT = ("Subagents and in-process teammates never run runtime commands (hc, herdmates, "
           "agent-runtime spawn/message/stop); report through your return value or SendMessage.")


def main():
    try:
        sys.stdin.read()
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                 "additionalContext": CONTEXT}}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
