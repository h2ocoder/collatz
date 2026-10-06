"""Reviewer check (lens: mathematics) of site/explore/thirty-six.md, part C.

Read-only checks of the figure scripts (nothing is drawn or written by them here):
  * import fig_thirty_six_lattice  -> its top-level assertions run
  * fig_thirty_six_figurate.compute() -> compare with the JSON saved next to the figure script
  * which numbers printed on the page are NOT recomputed by check_thirty_six_page.py
  * pixel sanity of the two PNGs (size only)

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 mathcheck_thirty_six_c.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "site_figures"
ROOT = HERE.parents[2]
sys.path.insert(0, str(FIG))

import fig_thirty_six_lattice as lat          # noqa: E402  (assertions at import)

print("lattice script imported: all top-level assertions passed")
print("  pairs:", [(lat.num(*p), lat.num(*q)) for p, q in lat.PAIRS])
print("  cycle v:", lat.CYCLE_V, " anti-diagonal:", [lat.num(*p) for p in lat.ANTI])
print("  Pierpont:", list(zip(lat.PIERPONT, lat.PRIMES)))
print("  slope of the grey line b = a*log_3(2):", round(lat.SLOPE, 4),
      "-> at a = 3 the line is at b =", round(3 * lat.SLOPE, 3), "(below the node 72 at b = 2: 8 < 9)")

import fig_thirty_six_figurate as fg          # noqa: E402

data = fg.compute()
saved = json.loads((FIG / "fig_thirty_six_figurate.json").read_text(encoding="utf-8"))
same = all([str(x) for x in v] == saved["exact"][k] for k, v in data.items())
print("figurate compute() equals the saved JSON:", same)
print("  labels:", fg.LABELS)

src = (FIG / "check_thirty_six_page.py").read_text(encoding="utf-8")
page = (ROOT / "site" / "explore" / "thirty-six.md").read_text(encoding="utf-8")
probes = {
    "classes modulo 2^24 (actual dropping times)": r"2\s*\*\*\s*24|1\s*<<\s*24|LV\s*=\s*24|<=\s*24",
    "M(d) = 1 when 3 divides d (destination multiplicity)": r"destination|\bdest\b|M\(d\)",
    "F(n) = 3n/2 at four integers": r"3\s*\*\s*n\s*==\s*2|3n/2|Fraction\(3,\s*2\)\s*\*\s*n",
    "squares cover a sixth of the 2-adic integers": r"sixth|Fraction\(1,\s*6\)|measure",
    "Ljunggren: T^2 triangular only for 0, 1, 6": r"Ljunggren|8\s*\*\s*tri\(n\)\s*\*\*\s*2",
    "NOT conjugacy n -> -1-n to the 3x-1 map": r"-1\s*-\s*T\(|NOT",
}
print("numbers on the page that check_thirty_six_page.py does not recompute:")
for what, pat in probes.items():
    hit = re.search(pat, src)
    print(f"  {'covered ' if hit else 'MISSING '} {what}")

try:
    from PIL import Image
    for name in ("collatz_thirty_six_lattice.png", "collatz_thirty_six_figurate.png"):
        im = Image.open(ROOT / "site" / "public" / "data" / name)
        print(f"  {name}: {im.size[0]} x {im.size[1]} px")
except Exception as exc:                       # pragma: no cover
    print("  (PIL not available:", exc, ")")

print("page facts: lines =", page.count("\n") + 1,
      "| 'Dset' mentions =", page.count("Dset"), "| '{{' present:", "{{" in page, "| '}}' present:", "}}" in page)
