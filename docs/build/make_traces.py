"""Generates docs/build/traces.json by running the real bsq under gdb.

Usage (Linux, needs cc + gdb with Python):  python3 docs/build/make_traces.py

1. Compiles ex00 with -g3 -O0 -ftrivial-auto-var-init=pattern (debug build,
   uninitialised locals get a recognisable pattern).
2. For every run below, starts gdb with trace_gdb.py, which stops at the
   function and records every line it executes with the watched values.
3. Writes all runs to traces.json, which build_page.py embeds in the page.
"""
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EX00 = os.path.join(REPO, "ex00")
MAPS = os.path.join(REPO, "tests", "maps")

DP_MAP = "4.ox\n.o....\n......\n....o.\n......\n"


def w(name, expr=None, kind="int", length=None, hidden=False):
    watch = {"name": name, "expr": expr or name, "kind": kind}
    if length:
        watch["len"] = length
    if hidden:
        watch["hidden"] = True
    return watch


WATCH = {
    "main": [
        w("argc"), w("i"), w("argv[i]", kind="cstr"),
        w("argv", kind="strarray", length="argc", hidden=True),
    ],
    "read_all": [
        w("fd"), w("capacity"), w("bytes"), w("map->len"),
    ],
    "parse_number": [
        w("len"), w("i"), w("str[i]", kind="char"), w("digit"),
        w("*result"), w("str", kind="str", length="len", hidden=True),
    ],
    "validate_map": [
        w("map->rows"), w("map->cols"), w("map->grid_len"), w("i"), w("col"),
        w("map->grid[i]", kind="char"),
        w("map->empty", kind="char", hidden=True),
        w("map->obstacle", kind="char", hidden=True),
        w("grid", "map->grid", kind="str", length="map->grid_len", hidden=True),
    ],
    "process_row": [
        w("row"), w("col"), w("line[col]", kind="char"), w("above"), w("diag"),
        w("best->size"), w("best->row"), w("best->col"),
        w("map->obstacle", kind="char", hidden=True),
        w("dp", kind="array", length="map->cols + 1", hidden=True),
        w("line", kind="str", length="map->cols", hidden=True),
    ],
    "fill_square": [
        w("best->size"), w("best->row"), w("best->col"), w("row"), w("col"),
        w("map->cols"), w("map->full", kind="char", hidden=True),
        w("map->obstacle", kind="char", hidden=True),
        w("grid", "map->grid", kind="str", length="map->grid_len", hidden=True),
    ],
}

# function, label, input files {name: content} or args on real test maps
RUNS = [
    ("main", "3 archivos", {"args": ["valid/one_cell_empty", "invalid/fewer_lines",
                                     "valid/single_row"], "cwd": MAPS,
                            "capture_io": True}),
    ("read_all", "archivo de ~300 KB", {"generate": "big"}),
    ("parse_number", "9", {"files": {"in.map": "9.ox\n.\n"}}),
    ("parse_number", "2147483647", {"files": {"in.map": "2147483647.ox\n.\n"}}),
    ("parse_number", "2147483648", {"files": {"in.map": "2147483648.ox\n.\n"}}),
    ("validate_map", "mapa válido", {"files": {"in.map": "3.ox\n..o.\n....\n.o..\n"}}),
    ("validate_map", "filas desiguales", {"files": {"in.map": "3.ox\n..o.\n...\n.o...\n"}}),
    ("validate_map", "falta una fila", {"files": {"in.map": "3.ox\n..o.\n....\n"}}),
    ("process_row", "fila 3", {"files": {"in.map": DP_MAP}, "condition": "row == 3"}),
    ("fill_square", "lado 3", {"files": {"in.map": DP_MAP}}),
]


def compile_debug(tmp):
    binary = os.path.join(tmp, "bsq_trace")
    sources = sorted(os.path.join(EX00, "srcs", f) for f in os.listdir(os.path.join(EX00, "srcs"))
                     if f.endswith(".c"))
    subprocess.run(["cc", "-g3", "-O0", "-ftrivial-auto-var-init=pattern",
                    "-Wall", "-Wextra", "-Werror", "-I", os.path.join(EX00, "includes"),
                    *sources, "-o", binary], check=True)
    return binary


def big_map(tmp):
    path = os.path.join(tmp, "big.map")
    with open(path, "w") as f:
        subprocess.run(["perl", os.path.join(REPO, "tests", "gen_map.pl"), "600", "500", "2"],
                       stdout=f, check=True)
    return path


def trace(binary, tmp, index, function, label, options):
    run_dir = os.path.join(tmp, "run%02d" % index)
    os.makedirs(run_dir)
    args = options.get("args", [])
    shown_input = None
    if "files" in options:
        for name, content in options["files"].items():
            with open(os.path.join(run_dir, name), "w", newline="\n") as f:
                f.write(content)
            shown_input = content
        args = list(options["files"])
    if options.get("generate") == "big":
        args = [big_map(tmp)]
    spec = {
        "binary": binary, "function": function, "cwd": options.get("cwd", run_dir),
        "args": args, "watch": WATCH[function], "condition": options.get("condition"),
        "capture_io": options.get("capture_io", False),
        "stdout_file": os.path.join(run_dir, "stdout"),
        "stderr_file": os.path.join(run_dir, "stderr"),
    }
    out = os.path.join(run_dir, "trace.json")
    env = dict(os.environ, TRACE_SPEC=json.dumps(spec), TRACE_OUT=out, DEBUGINFOD_URLS="")
    subprocess.run(["gdb", "-q", "-nx", "-batch", "-x", os.path.join(HERE, "trace_gdb.py")],
                   env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(out, encoding="utf-8") as f:
        steps = json.loads(f.read().replace(json.dumps(binary)[1:-1], "./bsq"))
    command = "./bsq " + " ".join(os.path.basename(a) if options.get("generate") else a
                                  for a in args)
    print("%-13s %-18s %4d steps" % (function, label, len(steps)))
    return {"label": label, "command": command, "input": shown_input, "steps": steps}


def main():
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_debug(tmp)
        for index, (function, label, options) in enumerate(RUNS):
            entry = result.setdefault(function, {"watch": WATCH[function], "runs": []})
            entry["runs"].append(trace(binary, tmp, index, function, label, options))
    with open(os.path.join(HERE, "traces.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))


main()
