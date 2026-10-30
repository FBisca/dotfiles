#!/usr/bin/env python3
"""PreToolUse(Bash) guard: subagents may not run hc run/send/kill; nobody may run teammux-launch."""

import json
import os
import shlex
import sys

HC_BLOCKED = {"run", "send", "kill"}
SEPARATORS = {";", "&", "&&", "|", "||", "(", ")", "|&", ";;"}
WRAPPERS = {"env", "command", "exec", "nohup", "time", "sudo", "builtin"}
SHELLS = {"sh", "bash", "zsh"}


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    current = []
    for token in lexer:
        if token in SEPARATORS or set(token) <= set(";&|()"):
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def invocations(command, depth=0):
    """Yield (program basename, args) for each simple command, descending into sh -c."""
    try:
        parsed = list(segments(command))
    except ValueError:
        return
    for words in parsed:
        i = 0
        while i < len(words) and ((("=" in words[i]) and not words[i].startswith("=")
                                   and words[i].split("=")[0].replace("_", "").isalnum())
                                  or words[i] in WRAPPERS or words[i].startswith("-") and i):
            i += 1
        if i >= len(words):
            continue
        program, args = os.path.basename(words[i]), words[i + 1:]
        yield program, args
        if program in SHELLS and depth < 3 and "-c" in args and args.index("-c") + 1 < len(args):
            yield from invocations(args[args.index("-c") + 1], depth + 1)


def verdict(command, is_subagent):
    for program, args in invocations(command):
        if program == "herdmates" and args[:1] == ["teammux-launch"]:
            return "herdmates teammux-launch is not allowed inside an agent session."
        if is_subagent and program == "hc" and args[:1] and args[0] in HC_BLOCKED:
            return ("Subagents must not run 'hc %s': it would act on the lead's terminal. "
                    "Report through your return value or SendMessage." % args[0])
    return None


def main():
    try:
        data = json.load(sys.stdin)
        command = data.get("tool_input", {}).get("command", "")
        reason = verdict(command, bool(data.get("agent_id")))
        if reason:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                     "permissionDecision": "deny",
                                                     "permissionDecisionReason": reason}}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
