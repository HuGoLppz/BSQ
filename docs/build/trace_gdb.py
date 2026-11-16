"""Runs INSIDE gdb (gdb -batch -x trace_gdb.py). Do not run it directly.

Stops at the first call of spec["function"], then executes it line by line
with `next`, recording before every line:
  - the line number that is about to run,
  - the value of every watched expression,
  - the returned value when the line is a `return (...)`,
  - (optional) what the program has written so far to stdout / stderr.

The binary is compiled with -ftrivial-auto-var-init=pattern, so variables
that have not been assigned yet hold the 0xFE byte pattern and are reported
as null ("not initialised yet"). The declaration lines at the top of the
function (where that pattern is written) are skipped.
"""
import json
import os
import re

import gdb

SPEC = json.loads(os.environ["TRACE_SPEC"])
OUT = os.environ["TRACE_OUT"]
MAX_STEPS = 600
DECLARATION = re.compile(r"^\s*[a-z_][\w ]*\t+\**\w+;$")
UNINIT_INTS = {-16843010, -72340172838076674, 0xFEFEFEFE, 0xFEFEFEFEFEFEFEFE}


def run(cmd):
    return gdb.execute(cmd, to_string=True)


def ev(expr):
    return gdb.parse_and_eval(expr)


def as_int(value):
    number = int(value)
    if number in UNINIT_INTS:
        return None
    return number


def read_watch(watch):
    kind = watch.get("kind", "int")
    try:
        if kind == "int":
            return as_int(ev(watch["expr"]))
        if kind == "cstr":
            return ev(watch["expr"]).string(encoding="latin-1")
        if kind == "char":
            code = int(ev(watch["expr"]))
            if code == -2:
                return None
            return chr(code & 0xFF)
        length = as_int(ev(watch["len"]))
        if length is None or length < 0 or length > 100000:
            return None
        pointer = ev(watch["expr"])
        if kind == "str":
            return pointer.string(encoding="latin-1", length=length)
        if kind == "array":
            return [as_int(pointer[k]) for k in range(length)]
        if kind == "strarray":
            return [pointer[k].string(encoding="latin-1") for k in range(length)]
    except (gdb.error, gdb.MemoryError, UnicodeDecodeError, ValueError, OverflowError):
        return None
    return None


def source_lines(frame):
    with open(frame.find_sal().symtab.fullname(), encoding="utf-8") as f:
        return f.read().split("\n")


def returned_value(text):
    text = text.strip()
    if not text.startswith("return (") or not text.endswith(");"):
        return None
    try:
        return int(ev(text[len("return ("):-2]))
    except gdb.error:
        return None


def read_file(path):
    try:
        with open(path, encoding="latin-1") as f:
            return f.read()
    except OSError:
        return ""


def depth(frame):
    count = 0
    while frame is not None:
        frame = frame.older()
        count += 1
    return count


def main():
    for setting in ("pagination off", "confirm off", "width 0", "print elements 0"):
        run("set " + setting)
    run("file " + SPEC["binary"])
    run("cd " + SPEC["cwd"])
    breakpoint = gdb.Breakpoint(SPEC["function"])
    if SPEC.get("condition"):
        breakpoint.condition = SPEC["condition"]
    redirect = " > %s 2> %s" % (SPEC["stdout_file"], SPEC["stderr_file"])
    if SPEC.get("stdin"):
        redirect += " < " + SPEC["stdin"]
    run("run " + " ".join(SPEC.get("args", [])) + redirect)
    breakpoint.delete()
    first = gdb.selected_frame()
    lines = source_lines(first)
    start_depth = depth(first)
    steps = []
    while len(steps) < MAX_STEPS:
        try:
            frame = gdb.selected_frame()
        except gdb.error:
            break
        if frame.name() != SPEC["function"] or depth(frame) != start_depth:
            break
        line = frame.find_sal().line
        text = lines[line - 1]
        if not steps and (text.strip() == "{" or DECLARATION.match(text)):
            run("next")
            continue
        step = {"line": line, "vars": {}}
        for watch in SPEC["watch"]:
            step["vars"][watch["name"]] = read_watch(watch)
        ret = returned_value(lines[line - 1])
        if ret is not None:
            step["ret"] = ret
        if SPEC.get("capture_io"):
            step["stdout"] = read_file(SPEC["stdout_file"])
            step["stderr"] = read_file(SPEC["stderr_file"])
        steps.append(step)
        try:
            run("next")
        except gdb.error:
            break
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(steps, f)


main()
