"""Post-build checks on site/.vitepress/dist (read-only).

1. 'katex-error' anywhere in the built HTML or JS chunks.
2. Every internal href / src in every built page resolves to a file in dist,
   and every #anchor resolves to an id on the target page.
3. Every nav / sidebar link in .vitepress/config.mts has a built page.
4. Rendering smells in the visible text of each page (outside code and KaTeX):
   leftover dollar signs, literal markdown markers, literal table pipes,
   leftover TeX commands, doubled curly braces, wikilinks.
5. Source smells in the markdown: doubled curly braces outside code fences,
   a raw less-than sign followed by a letter that is not a known tag/component.

Run:  python -X utf8 scripts/site_audit/build_check_dist.py
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DIST = SITE / ".vitepress" / "dist"

problems: list[str] = []
notes: list[str] = []


def bad(msg: str) -> None:
    problems.append(msg)


# ---------------------------------------------------------------- 1. katex
for p in sorted(DIST.rglob("*")):
    if p.suffix in {".html", ".js"}:
        t = p.read_text(encoding="utf-8", errors="replace")
        n = t.count("katex-error")
        if n:
            bad(f"katex-error x{n} in {p.relative_to(DIST)}")


# ------------------------------------------------- 2. links and anchors
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []   # (attr, value)
        self.stack: list[tuple[str, dict]] = []
        self.text: list[tuple[str, str]] = []    # (context, text) for main content
        self.in_main = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a and a["id"]:
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append((f"{tag}[{k}]", a[k]))
        if tag not in VOID:
            self.stack.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def _ctx(self) -> str:
        in_doc = False
        in_comp = False
        for tag, a in self.stack:
            cls = a.get("class") or ""
            if in_doc and any(k.startswith("data-v-") for k in a):
                # a scoped element BELOW the markdown container: text written in
                # one of the site's Vue component templates, not in markdown
                # (the theme's own wrappers above .vp-doc are scoped too)
                in_comp = True
            if tag in {"script", "style"}:
                return "skip"
            if "vp-doc" in cls.split() or "VPHome" in cls.split():
                in_doc = True
            if tag in {"code", "pre"}:
                return "code"
            if "katex" in cls.split() or "katex-block" in cls.split() \
                    or "katex-display" in cls.split():
                return "katex"
            if tag == "svg":
                return "component" if in_doc else "chrome"
        if in_doc and in_comp:
            return "component"
        return "doc" if in_doc else "chrome"

    def handle_data(self, data):
        c = self._ctx()
        if c in {"doc", "component"} and data.strip():
            self.text.append((c, data))


pages: dict[Path, Page] = {}
for p in sorted(DIST.rglob("*.html")):
    pg = Page()
    pg.feed(p.read_text(encoding="utf-8"))
    pages[p] = pg


def resolve(from_page: Path, url: str) -> tuple[Path | None, str]:
    u = urlparse(url)
    if u.scheme or url.startswith("//") or url.startswith("mailto:"):
        return None, ""
    path = unquote(u.path)
    frag = unquote(u.fragment)
    if not path:
        return from_page, frag
    target = (DIST / path.lstrip("/")) if path.startswith("/") else (from_page.parent / path)
    target = Path(str(target))
    cands = [target]
    if target.suffix == "":
        cands += [target.with_name(target.name + ".html"), target / "index.html"]
    if path.endswith("/"):
        cands = [target / "index.html"]
    for c in cands:
        if c.is_file():
            return c.resolve(), frag
    return Path("MISSING") / path, frag


n_links = 0
n_anchor = 0
external: set[str] = set()
cross: set[str] = set()
for p, pg in pages.items():
    rel = p.relative_to(DIST).as_posix()
    for attr, url in pg.links:
        if url.startswith(("http://", "https://")):
            external.add(url)
            continue
        if url.startswith(("data:", "javascript:")):
            continue
        tgt, frag = resolve(p, url)
        if tgt is None:
            continue
        n_links += 1
        if tgt.parts and tgt.parts[0] == "MISSING":
            bad(f"dead link in {rel}: {attr} -> {url}")
            continue
        if frag and tgt.suffix == ".html":
            n_anchor += 1
            if tgt != p.resolve():
                cross.add(f"{rel} -> {url}")
            tp = pages.get(tgt) or pages.get(Path(str(tgt)))
            if tp is None:
                # resolve() gives an absolute path; match by samefile
                for q in pages:
                    if q.resolve() == tgt:
                        tp = pages[q]
                        break
            if tp is not None and frag not in tp.ids:
                bad(f"dead anchor in {rel}: {attr} -> {url}")

notes.append(f"internal links checked: {n_links} (with anchors: {n_anchor})")
notes.append(f"external links: {len(external)}")
notes.append(f"cross-page anchor links, all resolved unless listed under PROBLEMS: {len(cross)}")
for c in sorted(cross):
    notes.append("   " + c)


# -------------------------------------------------- 3. nav and sidebar
cfg = (SITE / ".vitepress" / "config.mts").read_text(encoding="utf-8")
cfg_links = re.findall(r"link:\s*'([^']+)'", cfg)
n_cfg = 0
for l in cfg_links:
    if l.startswith("http"):
        continue
    n_cfg += 1
    path = l.lstrip("/")
    md = SITE / (path + "index.md" if (l.endswith("/") or l == "/") else path + ".md")
    html = DIST / (path + "index.html" if (l.endswith("/") or l == "/") else path + ".html")
    if not md.is_file():
        bad(f"config link {l}: source {md.relative_to(SITE)} missing")
    if not html.is_file():
        bad(f"config link {l}: built page {html.relative_to(DIST)} missing")
notes.append(f"nav/sidebar links checked: {n_cfg}")

# every markdown page is reachable from the sidebar (orphans are a note, not an error)
side = {l for l in cfg_links}
for md in sorted(SITE.rglob("*.md")):
    if "node_modules" in md.parts:
        continue
    r = "/" + md.relative_to(SITE).as_posix()[:-3]
    if r.endswith("/index"):
        r = r[:-5]
    if r == "/index":
        r = "/"
    if r not in side:
        notes.append(f"page not in nav/sidebar: {r}")


# ------------------------------------------------ 4. rendered text smells
SMELLS = [
    ("dollar sign", re.compile(r"\$")),
    ("bold/italic marker", re.compile(r"\*\*|__(?=\w)")),
    ("literal pipe", re.compile(r"\|")),
    ("TeX command", re.compile(r"\\(?:mid|lvert|rvert|frac|log|lfloor|lceil|to|equiv|cdot|le|ge|times|text|pmod|bmod)\b")),
    ("double curly", re.compile(r"\{\{|\}\}")),
    ("wikilink", re.compile(r"\[\[|\]\]")),
    ("markdown link", re.compile(r"\]\([^)]*\)")),
    ("html entity leak", re.compile(r"&(?:lt|gt|amp|nbsp);")),
    ("backtick", re.compile(r"`")),
    ("undefined/NaN", re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]")),
]
for p, pg in pages.items():
    rel = p.relative_to(DIST).as_posix()
    for ctx, t in pg.text:
        for name, rx in SMELLS:
            m = rx.search(t)
            if m:
                s = max(0, m.start() - 60)
                snippet = " ".join(t[s:m.end() + 60].split())
                msg = f"{name} in visible text ({ctx}) of {rel}: ...{snippet}..."
                if name == "literal pipe" and ctx == "component":
                    notes.append(msg + "  [component text, not a markdown table]")
                else:
                    bad(msg)


# ---------------------------------------------------- 5. source smells
KNOWN_TAGS = {
    "a", "b", "i", "em", "strong", "br", "div", "span", "p", "img", "sup", "sub",
    "table", "thead", "tbody", "tr", "td", "th", "ul", "ol", "li", "code", "pre",
    "details", "summary", "figure", "figcaption", "small", "script", "style",
    "h1", "h2", "h3", "h4", "hr", "svg", "path", "g", "rect", "circle", "line",
    "text", "clientonly", "kbd", "blockquote", "template", "button", "input",
}
comp_dir = SITE / ".vitepress" / "theme" / "components"
COMPONENTS = {f.stem for f in comp_dir.rglob("*.vue")}
used_components: dict[str, list[str]] = {}

for md in sorted(SITE.rglob("*.md")):
    if "node_modules" in md.parts:
        continue
    rel = md.relative_to(SITE).as_posix()
    in_fence = False
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = re.sub(r"`[^`]*`", "", line)       # inline code is v-pre
        if "{{" in stripped or "}}" in stripped:
            bad(f"doubled curly brace in {rel}:{i}: {line.strip()[:120]}")
        for m in re.finditer(r"<(/?)([A-Za-z][A-Za-z0-9-]*)", stripped):
            name = m.group(2)
            if name in COMPONENTS:
                used_components.setdefault(name, []).append(rel)
                continue
            if name.lower() not in KNOWN_TAGS:
                bad(f"raw '<{name}' in {rel}:{i}: {line.strip()[:120]}")
        # a table row whose math contains a literal vertical bar
        if stripped.lstrip().startswith("|"):
            for mm in re.finditer(r"\$[^$]*\$", stripped):
                if "|" in mm.group(0):
                    bad(f"vertical bar inside math in table row {rel}:{i}: {mm.group(0)[:80]}")
            # unbalanced dollars in a table row usually means a bar split the math
            if stripped.count("$") % 2:
                bad(f"odd number of dollar signs in table row {rel}:{i}")

theme_index = (SITE / ".vitepress" / "theme" / "index.ts").read_text(encoding="utf-8")
registered = set(re.findall(r"app\.component\('([A-Za-z0-9]+)'", theme_index))
for c in sorted(used_components):
    if c not in registered:
        bad(f"component <{c}> used in {sorted(set(used_components[c]))} but not registered")
for c in sorted(registered - set(used_components)):
    notes.append(f"registered component not used on any page: {c}")

# images referenced from markdown exist in public/
for md in sorted(SITE.rglob("*.md")):
    if "node_modules" in md.parts:
        continue
    rel = md.relative_to(SITE).as_posix()
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", md.read_text(encoding="utf-8")):
        src = m.group(1)
        if src.startswith("http"):
            continue
        f = (SITE / "public" / src.lstrip("/")) if src.startswith("/") else (md.parent / src)
        if not f.is_file():
            bad(f"image missing for {rel}: {src}")


print(f"pages built: {len(pages)}")
for n in notes:
    print("note:", n)
print()
if problems:
    print(f"PROBLEMS ({len(problems)}):")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("OK: no problems found")
