"""Post-build HTML nesting check (read-only).

A block element inside a <p> is repaired differently by the browser than by
the server renderer, which gives a Vue hydration mismatch on that page (the
interactive components on it can then misbehave).  The production build does
not report it.  This scans the server-rendered pages for
  * a block element opened inside an unclosed <p>,
  * unbalanced div / table / ul / ol / details inside the markdown container.

Run:  python -X utf8 scripts/site_audit/build_check_nesting.py
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "site" / ".vitepress" / "dist"

BLOCK = {"div", "table", "ul", "ol", "p", "pre", "blockquote", "figure", "h1", "h2",
         "h3", "h4", "h5", "h6", "details", "section", "hr", "form", "dl"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
TRACK = {"div", "table", "ul", "ol", "details", "p", "span", "a", "strong", "em",
         "thead", "tbody", "tr", "td", "th", "li", "svg", "g", "button", "label", "select"}

problems: list[str] = []


class Nest(HTMLParser):
    def __init__(self, rel: str) -> None:
        super().__init__(convert_charrefs=True)
        self.rel = rel
        self.stack: list[tuple[str, int]] = []
        self.in_svg = 0

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        if tag in BLOCK and not self.in_svg:
            for t, _ in self.stack:
                if t == "p":
                    a = dict(attrs)
                    problems.append(
                        f"<{tag} class={a.get('class')!r}> inside an open <p> in {self.rel} (line {line})")
                    break
        if tag == "svg":
            self.in_svg += 1
        if tag not in VOID:
            self.stack.append((tag, line))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "svg":
            self.in_svg = max(0, self.in_svg - 1)
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
            return
        # mismatched close
        names = [t for t, _ in self.stack]
        if tag in names:
            i = len(names) - 1 - names[::-1].index(tag)
            skipped = [t for t in names[i + 1:] if t in TRACK]
            if skipped and not self.in_svg:
                problems.append(
                    f"</{tag}> closes over unclosed {skipped} in {self.rel} (line {self.getpos()[0]})")
            del self.stack[i:]
        elif tag in TRACK:
            problems.append(f"stray </{tag}> in {self.rel} (line {self.getpos()[0]})")

    def close(self):
        super().close()
        left = [t for t, _ in self.stack if t in TRACK]
        if left:
            problems.append(f"unclosed at end of {self.rel}: {left}")


n = 0
for p in sorted(DIST.rglob("*.html")):
    rel = p.relative_to(DIST).as_posix()
    h = Nest(rel)
    h.feed(p.read_text(encoding="utf-8"))
    h.close()
    n += 1

print(f"pages scanned: {n}")
if problems:
    print(f"PROBLEMS ({len(problems)}):")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("OK: no block element inside a paragraph, no unbalanced containers")
