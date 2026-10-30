#!/usr/bin/env python3
"""SubagentStart hook: tell subagents and in-process teammates not to run runtime commands."""

import json
import sys

CONTEXT = ("You are a subagent or in-process teammate of a lead agent. You must not run runtime "
           "commands (hc, herdmates): they act on the lead's terminal. Report through your return "
           "value or SendMessage.")


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
