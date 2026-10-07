"""Source-level mechanics checks on site/**/*.md (read-only).

A. Markdown tables: every row has the same number of cells as its header
   (markdown-it silently drops or pads cells, so a stray vertical bar inside
   math loses content without a build error).
B. Every '<' followed by a letter outside code: listed with its tag name so
   prose that Vue would read as a tag stands out.
C. Inline math with a space just inside a dollar sign (not parsed as math).
D. Relative links: target page exists; anchor exists as a heading slug.

Run:  python -X utf8 scripts/site_audit/build_check_source.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
problems: list[str] = []


def pages():
    for md in sorted(SITE.rglob("*.md")):
        if "node_modules" in md.parts:
            continue
        yield md


def split_cells(row: str) -> list[str]:
    s = row.strip()
    cells, cur, i = [], "", 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            cur += s[i:i + 2]
            i += 2
            continue
        if ch == "|":
            cells.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    cells.append(cur)
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return cells


tags = Counter()
tag_where: dict[str, list[str]] = {}
n_tables = 0
n_rows = 0

for md in pages():
    rel = md.relative_to(SITE).as_posix()
    lines = md.read_text(encoding="utf-8").splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        # --- A. tables
        if line.lstrip().startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$", lines[i + 1]):
            head = split_cells(line)
            n_tables += 1
            sep = split_cells(lines[i + 1])
            if len(sep) != len(head):
                problems.append(f"table separator has {len(sep)} cells, header {len(head)}: {rel}:{i + 2}")
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = split_cells(lines[j])
                n_rows += 1
                if len(cells) != len(head):
                    problems.append(
                        f"table row has {len(cells)} cells, header has {len(head)}: {rel}:{j + 1}: {lines[j].strip()[:110]}")
                for c in cells:
                    if c.count("$") % 2:
                        problems.append(f"odd dollar count in a table cell {rel}:{j + 1}: {c.strip()[:80]}")
                j += 1
            for c in head:
                if c.count("$") % 2:
                    problems.append(f"odd dollar count in a table header cell {rel}:{i + 1}: {c.strip()[:80]}")

        stripped = re.sub(r"`[^`]*`", "", line)

        # --- B. '<' followed by a letter
        for m in re.finditer(r"<(/?)([A-Za-z][A-Za-z0-9-]*)([^>]*)(>?)", stripped):
            name = m.group(2)
            tags[name] += 1
            tag_where.setdefault(name, []).append(f"{rel}:{i + 1}")
            if not m.group(4):
                problems.append(f"'<{name}' never closed with '>' on its line: {rel}:{i + 1}: {line.strip()[:110]}")

        # --- C. inline math with inner space next to the dollar
        no_display = re.sub(r"\$\$.*?\$\$", "", stripped)
        if "$$" not in no_display:
            parts = no_display.split("$")
            if len(parts) % 2 == 0 and not no_display.lstrip().startswith("|"):
                problems.append(f"odd number of dollar signs on line {rel}:{i + 1}: {line.strip()[:110]}")
            for k in range(1, len(parts), 2):
                seg = parts[k]
                if seg and (seg[0].isspace() or seg[-1].isspace()):
                    problems.append(f"inline math with a space inside the dollar: {rel}:{i + 1}: ${seg}$")
                if seg == "":
                    pass
        i += 1

# --- D. relative links and anchors (source side)


def slugify(h: str) -> str:
    # VitePress default slugify (mdit-vue): strip markup, lower-case, spaces -> '-',
    # drop most punctuation.  Explicit {#id} wins.
    m = re.search(r"\{#([^}]+)\}\s*$", h)
    if m:
        return m.group(1)
    h = re.sub(r"\$[^$]*\$", lambda mm: mm.group(0).strip("$"), h)
    h = re.sub(r"[`*_]", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    return h


link_rx = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
n_links = 0
for md in pages():
    rel = md.relative_to(SITE).as_posix()
    text = md.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)     # display math is not a link
    text = re.sub(r"\$[^$\n]*\$", "", text)                  # nor is inline math
    for m in link_rx.finditer(text):
        url = m.group(1)
        if re.match(r"^[a-z]+:", url) or url.startswith("#"):
            continue
        n_links += 1
        path = url.split("#")[0]
        if path.endswith(".md") or path.endswith(".html"):
            problems.append(f"link carries an extension in {rel}: {url}")
        base = SITE if path.startswith("/") else md.parent
        p = (base / path.lstrip("/")).resolve() if path else md
        cands = [Path(str(p) + ".md"), p / "index.md", p]
        if not any(c.is_file() for c in cands):
            problems.append(f"link target missing in {rel}: {url}")

print(f"tables: {n_tables}, body rows: {n_rows}; markdown links checked: {n_links}")
print("'<letter' occurrences outside code, by name:")
for name, n in sorted(tags.items()):
    where = tag_where[name]
    print(f"  <{name}> x{n}   e.g. {where[0]}")
print()
if problems:
    print(f"PROBLEMS ({len(problems)}):")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("OK: no problems found")
