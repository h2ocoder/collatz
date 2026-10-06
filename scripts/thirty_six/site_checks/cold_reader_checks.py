"""Cold-reader review checks for site/explore/thirty-six.md and folded-pentagon.md.

Read-only with respect to the pages, the component and the figures.  Prints:
  1. word counts of the two new pages against the two house-voice pages;
  2. occurrences of process words (run, thread, skeptic) per page;
  3. relative links and image paths that do not resolve;
  4. pixel sizes of the three figures and the height of their smallest type at the 688 px text column;
  5. the PentagonWalk verdict for every (rule, start, k): does the 'unmoved' text ever show for k >= 1?
  6. the limit of 'Ratio of the two' in the component (distance from uniform / (phi/2)^k) from the apex;
  7. triangular numbers that are sums of cubes (for the phrase 'the only triangular sum of cubes').

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 cold_reader_checks.py
"""
from __future__ import annotations

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / "site"
PAGES = {
    "thirty-six": SITE / "explore" / "thirty-six.md",
    "folded-pentagon": SITE / "explore" / "folded-pentagon.md",
    "dropping-dictionary": SITE / "explore" / "dropping-dictionary.md",
    "log6-wobble": SITE / "explore" / "log6-wobble.md",
}

print("== 1. length ==")
for name, p in PAGES.items():
    text = p.read_text(encoding="utf-8")
    print(f"{name:22s} lines {len(text.splitlines()):4d}  words {len(text.split()):5d}  chars {len(text):6d}")

print("\n== 2. process words ==")
for name in ("thirty-six", "folded-pentagon", "dropping-dictionary", "log6-wobble"):
    text = PAGES[name].read_text(encoding="utf-8")
    counts = {w: len(re.findall(rf"\b{w}\b", text, flags=re.I)) for w in ("run", "thread", "threads", "skeptic", "skeptic's", "we")}
    print(f"{name:22s} {counts}")

print("\n== 3. links and images ==")
for name in ("thirty-six", "folded-pentagon"):
    p = PAGES[name]
    text = p.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith("http"):
            continue
        if target.startswith("/data/"):
            f = SITE / "public" / target.lstrip("/")
            ok = f.exists()
        else:
            t = target.split("#")[0]
            f = (p.parent / t)
            ok = f.with_suffix(".md").exists() or (f / "index.md").exists()
        print(f"{name:16s} {'ok ' if ok else 'MISSING'} {target}")
    for script in re.findall(r"`((?:scripts/|q\d|fig_|check_|verify)[^`]*)`", text):
        print(f"{name:16s} mentions {script}")

print("\n== 4. figures ==")
try:
    from PIL import Image
    for f in ("collatz_thirty_six_lattice.png", "collatz_thirty_six_figurate.png", "collatz_folded_pentagon.png",
              "collatz_nested_dropping.png", "collatz_dropping_alphabet.png", "collatz_log6_wobble_traces.png"):
        q = SITE / "public" / "data" / f
        if q.exists():
            w, h = Image.open(q).size
            print(f"{f:36s} {w} x {h}   scale at 688 px column: {688 / w:.3f}   at 360 px phone: {360 / w:.3f}")
        else:
            print(f"{f:36s} missing")
except Exception as exc:  # pragma: no cover
    print("PIL not available:", exc)

print("\n== 5. PentagonWalk verdicts ==")
MAX_STEPS = 16


def order(sign):
    plus = [1, 2, 4, 0, 3]
    return plus if sign == 1 else [(5 - r) % 5 for r in plus]


def residue_counts(k, start, sign):
    counts = [0] * 5
    first = 5 if start == 0 else start
    for j in range(2 ** k):
        n = first + 5 * j
        for _ in range(k):
            n = n // 2 if n % 2 == 0 else (3 * n + sign) // 2
        counts[n % 5] += 1
    return counts


def walk_counts(k, frm):
    w = [0] * 5
    w[frm] = 1
    for _ in range(k):
        nxt = [0] * 5
        for v in range(5):
            nxt[(v + 1) % 5] += w[v]
            nxt[(v + 4) % 5] += w[v]
        w = nxt
    return w


bad = []
for sign in (1, -1):
    o = order(sign)
    for start in range(5):
        v0 = o.index(start)
        for k in range(MAX_STEPS + 1):
            c = residue_counts(k, start, sign)
            w = walk_counts(k, v0)
            mism = sum(1 for v in range(5) if c[o[v]] != w[v])
            verdict = "different" if mism else ("same" if v0 == 0 else "unmoved")
            if verdict == "unmoved" and k > 0:
                bad.append((sign, start, k))
            if v0 == 0 and mism:
                bad.append(("apex mismatch", sign, start, k))
print("cases where the 'Nothing has moved yet' text would show for k >= 1, or the apex disagrees:", bad or "none")

print("\n== 6. ratio shown in the component ==")
half_phi = (1 + math.sqrt(5)) / 4
for k in (1, 2, 3, 4, 6, 8, 10, 12, 14, 15, 16):
    c = residue_counts(k, 1, 1)
    tv = sum(abs(x / 2 ** k - 0.2) for x in c) / 2
    print(f"k = {k:2d}  distance {tv:.5f}  (phi/2)^k {half_phi ** k:.5f}  ratio {tv / half_phi ** k:.4f}")
print("non-apex start, residue 2:")
for k in (1, 2, 4, 8, 12, 16):
    c = residue_counts(k, 2, 1)
    tv = sum(abs(x / 2 ** k - 0.2) for x in c) / 2
    print(f"k = {k:2d}  distance {tv:.5f}  ratio {tv / half_phi ** k:.4f}")

print("\n== 7. triangular numbers that are sums of cubes ==")
tri = {n * (n + 1) // 2 for n in range(1, 2000)}
first_n = [(n, (n * (n + 1) // 2) ** 2) for n in range(1, 2000)]
print("sums of the FIRST n cubes that are triangular:", [(n, v) for n, v in first_n if v in tri or math.isqrt(8 * v + 1) ** 2 == 8 * v + 1][:6])
two = sorted({a ** 3 + b ** 3 for a in range(1, 40) for b in range(a, 40)} & tri)
print("triangular numbers that are a sum of two positive cubes (first few):", two[:8])
