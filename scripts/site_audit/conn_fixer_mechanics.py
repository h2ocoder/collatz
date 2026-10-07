"""Mechanics check for the connections pages and their components (no site build).

- no two consecutive opening or closing curly braces in the .md pages
- no raw '<' directly followed by a letter in prose (component and div tags excepted)
- tables: every row has the header's number of cells; no literal '|' inside math in a cell
- internal links: target page exists
- components: no raw $...$ TeX left in a <template> caption
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / "site"
PAGES = sorted((SITE / "connections").glob("*.md"))
COMPONENTS = [SITE / ".vitepress/theme/components/journey" / n for n in
              ("AlphaPositionChart.vue", "EisensteinWalk.vue", "SpectrumVisualizer.vue", "ZooExplorer.vue")]
ALLOWED_TAGS = ("div", "/div", "SpectrumVisualizer", "ZooExplorer", "EisensteinWalk", "AlphaPositionChart")

problems = 0


def report(*a):
    global problems
    problems += 1
    print("  PROBLEM:", *a)


for p in PAGES:
    text = p.read_text(encoding="utf-8")
    lines = text.split("\n")
    print(p.name, f"({len(lines)} lines)")
    for i, l in enumerate(lines, 1):
        if "{{" in l or "}}" in l:
            report(p.name, i, "double brace:", l.strip()[:90])
        for m in re.finditer(r"<([A-Za-z/][A-Za-z]*)", l):
            if m.group(1) not in ALLOWED_TAGS:
                report(p.name, i, "raw < + letter:", l.strip()[:90])
    header = None
    for i, l in enumerate(lines, 1):
        if l.startswith("|"):
            cells = re.split(r"(?<!\\)\|", l.strip()[1:-1] if l.strip().endswith("|") else l.strip()[1:])
            if header is None:
                header = (i, len(cells))
            elif len(cells) != header[1]:
                report(p.name, i, f"{len(cells)} cells, header at line {header[0]} has {header[1]}")
            for c in cells:
                if c.count("$") % 2:
                    report(p.name, i, "literal | inside math:", c.strip()[:60])
            if "\\|" in l:
                report(p.name, i, "escaped pipe in table row (use \\lvert or \\mid)")
        else:
            header = None
    for m in re.finditer(r"\]\((/[^)#\s]*|\.{1,2}/[^)#\s]*)(#[^)]*)?\)", text):
        target = m.group(1)
        if target.startswith("/data/"):
            f = SITE / "public" / target[1:]
            if not f.exists():
                report(p.name, "missing image", target)
            continue
        rel = target[1:] if target.startswith("/") else str((p.parent / target).resolve().relative_to(SITE))
        cand = [SITE / (rel + ".md"), SITE / rel / "index.md"]
        if not any(c.exists() for c in cand):
            report(p.name, "broken link", target)
        if m.group(2):
            # anchor: check a heading with that slug exists in the target
            tgt = next(c for c in cand if c.exists())
            slugs = set()
            for h in re.findall(r"^#+\s+(.*)$", tgt.read_text(encoding="utf-8"), flags=re.M):
                s = re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-")
                slugs.add(re.sub(r"-+", "-", s))
            if m.group(2)[1:] not in slugs:
                report(p.name, "anchor not found", target + m.group(2), sorted(slugs))
    if text.count("$$") % 2:
        report(p.name, "odd number of $$")

for c in COMPONENTS:
    text = c.read_text(encoding="utf-8")
    tm = re.search(r"<template>(.*)</template>", text, flags=re.S)
    tpl = tm.group(1) if tm else ""
    print(c.name)
    for m in re.finditer(r"\$[^$\n{}`]*\\[a-z]+[^$\n]*\$", tpl):
        report(c.name, "raw TeX in template:", m.group(0)[:60])
    # every {{ has a matching }} on the same line or later; crude balance check
    if tpl.count("{{") != tpl.count("}}"):
        report(c.name, "unbalanced mustaches", tpl.count("{{"), tpl.count("}}"))

print("problems:", problems)
sys.exit(1 if problems else 0)
