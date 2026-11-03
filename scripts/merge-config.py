#!/usr/bin/env python3
"""Deep-merge JSON or TOML config files into one validated output file.

Usage: merge-config.py {json|toml} OUT BASE [OVERLAY ...] [--live FILE --keep PATH ...]

Later files win for scalars; tables merge recursively; arrays concatenate (equal items
appear once). A key ending in "!" in a later file replaces the earlier value outright
instead (`"args!" = [...]` replaces `args`), for argv-like arrays that must not grow.

--live FILE with --keep PATH (dotted, repeatable) carries state a tool wrote at runtime
into the result: for each PATH present in FILE, FILE is merged over the merged value, so
the live entries win while base and overlay entries it lacks still appear. The result is parsed back before it replaces OUT atomically, so a failure
never leaves an invalid or half-written file. Standard library only (Python 3.11+).
"""

import datetime
import json
import os
import re
import sys
import tempfile
import tomllib

BARE_KEY = re.compile(r"[A-Za-z0-9_-]+\Z")


def merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for key, value in over.items():
            if key.endswith("!"):
                out[key[:-1]] = value
            else:
                out[key] = merge(base[key], value) if key in base else value
        return out
    if isinstance(base, list) and isinstance(over, list):
        return base + [item for item in over if item not in base]
    return over


def key(name):
    return name if BARE_KEY.match(name) else json.dumps(name, ensure_ascii=False)


def scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(scalar(v) for v in value) + "]"
    raise TypeError(f"cannot write {type(value).__name__} inline")


def is_table_array(value):
    return isinstance(value, list) and bool(value) and all(isinstance(v, dict) for v in value)


def emit_table(path, table, lines, array_item=False):
    plain = {k: v for k, v in table.items() if not isinstance(v, dict) and not is_table_array(v)}
    subs = {k: v for k, v in table.items() if k not in plain}
    if path and (array_item or plain or not subs):
        header = ".".join(key(p) for p in path)
        if lines:
            lines.append("")
        lines.append(f"[[{header}]]" if array_item else f"[{header}]")
    for k, v in plain.items():
        lines.append(f"{key(k)} = {scalar(v)}")
    for k, v in subs.items():
        if isinstance(v, dict):
            emit_table(path + [k], v, lines)
        else:
            for item in v:
                emit_table(path + [k], item, lines, array_item=True)


def dump_toml(data):
    lines = []
    emit_table([], data, lines)
    return "\n".join(lines) + "\n"


def load(kind, path):
    with open(path, "rb") as handle:
        return json.load(handle) if kind == "json" else tomllib.load(handle)


def lookup(data, path):
    for part in path.split("."):
        if not isinstance(data, dict) or part not in data:
            return None
        data = data[part]
    return data


def keep_live(merged, live, paths):
    for path in paths:
        value = lookup(live, path)
        if value is None:
            continue
        parts = path.split(".")
        target = merged
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = merge(target.get(parts[-1], {} if isinstance(value, dict) else value), value)


def main(argv):
    args, live, keep = list(argv[1:]), None, []
    while "--live" in args or "--keep" in args:
        flag = "--live" if "--live" in args and ("--keep" not in args or args.index("--live") < args.index("--keep")) else "--keep"
        index = args.index(flag)
        if index + 1 >= len(args):
            sys.exit(__doc__)
        value = args[index + 1]
        del args[index:index + 2]
        if flag == "--live":
            live = value
        else:
            keep.append(value)
    if len(args) < 3 or args[0] not in ("json", "toml"):
        sys.exit(__doc__)
    kind, out, files = args[0], args[1], args[2:]
    try:
        merged = None
        for path in files:
            data = load(kind, path)
            merged = merge({}, data) if merged is None else merge(merged, data)
        if live and keep:
            keep_live(merged, load(kind, live), keep)
        text = json.dumps(merged, indent=2, ensure_ascii=False) + "\n" if kind == "json" else dump_toml(merged)
        reparsed = json.loads(text) if kind == "json" else tomllib.loads(text)
        if reparsed != merged:
            raise ValueError("merged output does not round-trip")
    except (OSError, ValueError, TypeError) as error:  # JSONDecodeError and TOMLDecodeError are ValueErrors
        sys.exit(f"merge-config: {error}")
    directory = os.path.dirname(os.path.abspath(out))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=os.path.basename(out) + ".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, out)
    except BaseException:
        os.unlink(tmp)
        raise


if __name__ == "__main__":
    main(sys.argv)
