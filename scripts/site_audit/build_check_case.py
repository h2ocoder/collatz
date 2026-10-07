"""Case-sensitive check of every internal href / src in the built pages (read-only).

Windows resolves a path whatever its letter case; the web host does not.  Each
internal link is matched against the exact names on disk in dist.

Run:  python -X utf8 scripts/site_audit/build_check_case.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "site" / ".vitepress" / "dist"

exact = {p.relative_to(DIST).as_posix() for p in DIST.rglob("*") if p.is_file()}
problems: list[str] = []
seen: set[str] = set()
rx = re.compile(r'(?:href|src)="([^"]+)"')
for p in sorted(DIST.rglob("*.html")):
    rel = p.relative_to(DIST).as_posix()
    for url in rx.findall(p.read_text(encoding="utf-8")):
        u = urlparse(url.replace("&amp;", "&"))
        if u.scheme or url.startswith(("//", "#", "data:", "mailto:")):
            continue
        path = unquote(u.path)
        if not path:
            continue
        if path.startswith("/"):
            t = path.lstrip("/")
        else:
            t = (Path(rel).parent / path).as_posix()
        parts: list[str] = []
        for seg in t.split("/"):
            if seg == "..":
                if parts:
                    parts.pop()
            elif seg not in ("", "."):
                parts.append(seg)
        t = "/".join(parts)
        cands = [t, t + ".html", (t + "/index.html").lstrip("/")]
        if path.endswith("/") or t == "":
            cands = [(t + "/index.html").lstrip("/")]
        seen.add(t)
        if not any(c in exact for c in cands):
            problems.append(f"{rel}: {url}")

print(f"distinct internal targets: {len(seen)}; files in dist: {len(exact)}")
if problems:
    print(f"PROBLEMS ({len(problems)}): no file with exactly this name")
    for x in sorted(set(problems)):
        print(" -", x)
    sys.exit(1)
print("OK: every internal link matches a file name exactly (case-sensitive)")
