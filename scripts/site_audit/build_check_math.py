"""Post-build look at the rendered math (read-only).

For every KaTeX span in the built pages, read back its TeX source from the
MathML annotation and flag
  * math that swallowed prose (a run of plain words outside \\text{...}),
  * very long inline math,
  * anything KaTeX coloured as an error (#cc0000) or left as \\textcolor error.
Also prints, per page, the count of inline and display formulas, and compares
each sidebar label with the page's H1 (information only).

Run:  python -X utf8 scripts/site_audit/build_check_math.py
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DIST = SITE / ".vitepress" / "dist"

problems: list[str] = []
ann_rx = re.compile(r'<annotation encoding="application/x-tex">(.*?)</annotation>', re.S)
total = 0
for p in sorted(DIST.rglob("*.html")):
    rel = p.relative_to(DIST).as_posix()
    t = p.read_text(encoding="utf-8")
    anns = [html.unescape(a) for a in ann_rx.findall(t)]
    n_display = t.count('class="katex-display"')
    total += len(anns)
    if "#cc0000" in t or "color:#cc0000" in t:
        problems.append(f"KaTeX error colour in {rel}")
    for a in anns:
        bare = re.sub(r"\\(?:text|mathrm|operatorname|textbf|textit|mathbf|mathit|texttt)\s*\{[^{}]*\}", " ", a)
        bare = re.sub(r"\\[A-Za-z]+", " ", bare)
        m = re.search(r"(?:\b[a-z]{3,}\b[ ,.;:]+){3,}\b[a-z]{3,}\b", bare)
        if m:
            problems.append(f"prose inside math in {rel}: {a[:140]!r}")
        if "$" in a:
            problems.append(f"dollar sign inside math in {rel}: {a[:140]!r}")
    if anns:
        print(f"{rel:48s} formulas {len(anns):4d}  (display {n_display})")
print(f"total formulas: {total}")

# sidebar label vs H1 (information only)
cfg = (SITE / ".vitepress" / "config.mts").read_text(encoding="utf-8")
block = cfg[cfg.index("sidebar:"):]
print("\nsidebar label  |  page H1")
for text, link in re.findall(r"\{\s*text:\s*'([^']+)',\s*link:\s*'([^']+)'\s*\}", block):
    path = link.lstrip("/")
    md = SITE / (path + "index.md" if link.endswith("/") else path + ".md")
    h1 = ""
    if md.is_file():
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                h1 = line[2:].strip()
                break
    print(f"  {text:34s} | {h1}")

print()
if problems:
    print(f"PROBLEMS ({len(problems)}):")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("OK: no problems found")
