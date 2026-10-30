#!/usr/bin/env python3
"""PreToolUse(Bash) guard: subagents may run only read-only hc subcommands; nobody may run teammux-launch."""

import json
import os
import shlex
import sys

HC_ALLOWED = {"get", "ls", "read", "wait", "templates", "events", "file", "exec", "schema"}
HC_INFO_FLAGS = {"--help", "-h", "--version"}
SEPARATORS = ";&|()"
KEYWORDS = {"then", "do", "else", "elif", "if", "while", "until", "{", "!", "time", "builtin",
            "command", "exec", "nohup", "env", "sudo"}
# wrapper -> options that consume a separate value; `positional` wrappers take one fixed arg
VALUE_FLAGS = {"timeout": {"-s", "-k", "--signal", "--kill-after"}, "nice": {"-n", "--adjustment"},
               "xargs": {"-n", "-I", "-P", "-L", "-d", "-s", "-E", "-a"}, "env": {"-u", "-C"},
               "sudo": {"-u", "-g", "-C", "-h", "-p"}}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    current = []
    for token in lexer:
        if set(token) <= set(SEPARATORS):
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def is_assignment(word):
    name, eq, _ = word.partition("=")
    return bool(eq) and name.replace("_", "a").isalnum() and not name[0].isdigit()


def command_start(words):
    """Index of the program word after env assignments, keywords and wrapper options."""
    i = 0
    while i < len(words):
        word = words[i]
        if is_assignment(word) or word in KEYWORDS:
            i += 1
            if word in ("env", "nohup", "sudo", "command", "exec", "time", "builtin"):
                i = skip_options(words, i, word)
        elif os.path.basename(word) in ("timeout", "nice", "xargs"):
            name = os.path.basename(word)
            i = skip_options(words, i + 1, name)
            if name == "timeout" and i < len(words):
                i += 1  # the duration
        else:
            return i
    return len(words)


def skip_options(words, i, name):
    while i < len(words) and words[i].startswith("-") and words[i] != "-":
        i += 2 if words[i] in VALUE_FLAGS.get(name, ()) else 1
    return i


def invocations(command, depth=0):
    """Yield (program basename, args) for each simple command, descending into sh -c."""
    try:
        parsed = list(segments(command))
    except ValueError:
        return
    for words in parsed:
        i = command_start(words)
        if i >= len(words):
            continue
        program, args = os.path.basename(words[i]), words[i + 1:]
        yield program, args
        if program in SHELLS and depth < 3:
            for j, arg in enumerate(args):
                if arg.startswith("-") and not arg.startswith("--") and "c" in arg and j + 1 < len(args):
                    yield from invocations(args[j + 1], depth + 1)
                    break


def hc_subcommand(args):
    """First non-option argument of hc; None when only options (or info flags) are present."""
    for arg in args:
        if arg in HC_INFO_FLAGS:
            return None
        if not arg.startswith("-"):
            return arg
    return None


def verdict(command, is_subagent):
    for program, args in invocations(command):
        if program == "herdmates" and args[:1] == ["teammux-launch"]:
            return "herdmates teammux-launch is not allowed inside an agent session."
        if is_subagent and program == "hc":
            sub = hc_subcommand(args)
            if sub is not None and sub not in HC_ALLOWED:
                return ("Subagents must not run 'hc %s': it could act on the lead's terminal. "
                        "Only read-only hc commands (%s) are allowed; report through your "
                        "return value or SendMessage." % (sub, ", ".join(sorted(HC_ALLOWED))))
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
