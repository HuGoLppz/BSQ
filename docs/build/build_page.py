"""Builds docs/index.html from template.html.

Usage:  python3 docs/build/build_page.py

Placeholders in the template:
  {{file:<path>}}         whole file from ex00/ (without the 42 header)
  {{fn:<path>:<name>}}    one function from ex00/<path>
  {{traces}}              traces.json + the source of every traced function
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EX00 = os.path.join(REPO, "ex00")
HEADER_LINES = 12


def read_lines(path):
    with open(os.path.join(EX00, path), encoding="utf-8") as f:
        return f.read().split("\n")


def block(path, code, lang):
    return (f'<pre><span class="file-tag">{path}</span>'
            f'<code data-lang="{lang}">{html.escape(code, quote=False)}</code></pre>')


def find_function(name):
    """Returns (path, first_line_number, lines) of a function in ex00/srcs."""
    start = re.compile(r"^(?:static\s+)?[a-z_]+\s*\t+\**" + re.escape(name) + r"\(")
    for file_name in sorted(os.listdir(os.path.join(EX00, "srcs"))):
        path = "srcs/" + file_name
        lines = read_lines(path)
        for i, line in enumerate(lines):
            if start.match(line):
                end = lines.index("}", i)
                return path, i + 1, lines[i:end + 1]
    raise SystemExit(f"function {name} not found")


def replace(match):
    kind, rest = match.group(1), match.group(2)
    if kind == "file":
        lang = "make" if rest.endswith("Makefile") else "c"
        return block(rest, "\n".join(read_lines(rest)[HEADER_LINES:]).strip("\n"), lang)
    path, name = rest.rsplit(":", 1)
    found_path, _, lines = find_function(name)
    if found_path != path:
        raise SystemExit(f"{name} is in {found_path}, not {path}")
    return block(path, "\n".join(lines), "c")


def traces():
    with open(os.path.join(HERE, "traces.json"), encoding="utf-8") as f:
        data = json.load(f)
    for name, entry in data.items():
        entry["file"], entry["first_line"], entry["lines"] = find_function(name)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main():
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        page = f.read()
    page = page.replace("{{traces}}", traces())
    page = re.sub(r"\{\{(file|fn):([^}]+)\}\}", replace, page)
    left = re.findall(r"\{\{[a-z]+:[^}]*\}\}", page)
    if left:
        raise SystemExit(f"unresolved placeholders: {left}")
    out = os.path.join(REPO, "docs", "index.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    print(f"docs/index.html written ({len(page.encode()) // 1024} KB)")


main()
