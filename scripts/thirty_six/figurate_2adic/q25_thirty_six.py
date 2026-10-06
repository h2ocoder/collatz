"""Q2.5  The numbers attached to 36 = T_8 = 6^2, in the repo's own vocabulary.

    36 (the value), 35 (v = n+1 = 36), 8 (index: T_8 = 36), 17 (u = 2*8+1), 6 (root),
    37 (36+1; on the 3x-1 cycle of 17), 9 (8+1; the pair (8,9)).

Uses collatz.core / collatz.dropping / collatz.stopping exactly as shipped.
  Paper 1 dropping time  = steps of the UN-shortcut map f (n/2 | 3n+1) to the first value < n.
  Dropping orbit INCLUDES n and excludes the destination; stopping orbit EXCLUDES n and includes it.
  Terras (k, s): k shortcut steps, s of them odd; dropping time = k + s.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q25_thirty_six.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))

from collatz import core, dropping, stopping  # noqa: E402
from common import Tee, stop, tri, v2  # noqa: E402

out = Tee(os.path.join(HERE, "q25_thirty_six.log"))
res = {}

NUMS = [36, 35, 8, 17, 6, 37, 9]
ROLE = {36: "the value", 35: "v = n+1 = 36", 8: "index, T_8 = 36", 17: "u = 2*8+1, 17^2 = 8*36+1",
        6: "root, 6^2 = 36 = T_3^2", 37: "36+1 (3x-1 cycle of 17)", 9: "8+1 (pair 8,9)"}

out("=" * 100)
out("1. Repo vocabulary (Paper 1 dropping / Paper 2 stopping), un-shortcut step counts")
out("=" * 100)
rows = []
for x in NUMS:
    dt = dropping.dropping_time(x)
    dd = dropping.dropping_destination(x)
    do = dropping.dropping_orbit(x)
    oo = dropping.orbital_oddity(x)
    genus = dropping.dropping_genus(x)
    sig = stopping.stopping_signature(x)
    sp = stopping.stopping_point(x)
    so = stopping.stopping_orbit(x)
    k, s = stop(x)
    orb = core.orbit(x)
    row = dict(n=x, role=ROLE[x], dropping_time=dt, terras_k=k, odd_steps_s=s, destination=dd,
               dropping_orbit=do, orbital_oddity=oo, dropping_genus=genus, stopping_signature=sig,
               stopping_point=sp, stopping_orbit=so, total_stopping_time=core.total_stopping_time(x),
               orbit=orb, residue_mod_2k=x % (1 << k))
    rows.append(row)
    out(f"  n = {x:3d}  ({ROLE[x]})")
    out(f"     dropping time {dt} = k+s with Terras (k,s) = ({k},{s});  class: n = {x % (1 << k)} mod 2^{k};"
        f"  destination {dd};  orbital oddity {oo}")
    out(f"     dropping orbit (incl. n) {do};  stopping orbit (excl. n) {so}")
    out(f"     dropping genus (set, modulus, index) = {genus};  stopping signature (time, page, offset) = {sig};"
        f"  stopping point {sp}")
    out(f"     full orbit ({core.total_stopping_time(x)} steps): {orb}")
res["rows"] = rows

out("")
out("=" * 100)
out("2. What is structural")
out("=" * 100)
out("  (a) 36 and 8 are even, 6 is even: Dropping Set_1, density 1/2.  17, 37, 9 are 1 mod 4: Set_3, density 1/4.")
out("      35 = 3 mod 16: Set_6 (Terras k=4, s=2), density 1/16.  None of these classes is rare.")
out("  (b) orbit(36) = [36, 18] + orbit(9), because 36 = 4*9.  The 3-smooth number 2^a 3^b simply halves a")
out("      times and then follows 3^b.")
out("  (c) v = n+1 = 2^a 3^b  =>  n makes exactly a odd shortcut steps (v -> 3v/2) and lands on 3^(a+b) - 1.")
tab = []
for (a, b) in [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4)]:
    n0 = 2 ** a * 3 ** b - 1
    x = n0
    t = 0
    while x % 2 == 1:
        x = (3 * x + 1) // 2
        t += 1
    tab.append((a, b, n0, t, x))
    out(f"      v = 2^{a} 3^{b} = {n0 + 1:3d}   n = {n0:3d}:  {t} odd steps, then n = {x} = 3^{a + b} - 1,"
        f"  v2(3^{a + b} - 1) = {v2(x)}")
out("      35 is the third point of the orbit of 15 = 2^4 - 1:  15 -> 23 -> 35 -> 53 -> 80 -> 40 -> 20 -> 10 -> 5.")
out("      The whole anti-diagonal a+b = 4 shares the exit 80 = 3^4 - 1 = 2^4 * 5.")
res["antidiagonal_4"] = tab

out("")
out("=" * 100)
out("3. What is nothing (checked against base rates)")
out("=" * 100)
# orbit(36) contains both 8 (index) and 17 (u).  Base rate: how many n <= 1000 have 17 and 8 on their orbit?
N = 1000
has8 = has17 = both = 0
for x in range(1, N + 1):
    o = set(core.orbit(x))
    a, b = 8 in o, 17 in o
    has8 += a
    has17 += b
    both += a and b
out(f"  orbit(36) passes through 17 and 8 (the u and the index of T_8 = 36).  Base rate for 1 <= n <= {N}:")
out(f"     8 on the orbit: {has8} ({has8 / N:.3f});  17 on the orbit: {has17} ({has17 / N:.3f});"
    f"  both: {both} ({both / N:.3f}).  Every orbit through 17 passes 8.")
res["base_rate_17_and_8"] = dict(N=N, has8=has8, has17=has17, both=both)
# total stopping time of 36 relative to neighbours
tsts = [core.total_stopping_time(x) for x in range(2, 101)]
out(f"  total stopping time of 36 is {core.total_stopping_time(36)} un-shortcut steps; for 2..100 the median is"
    f" {sorted(tsts)[len(tsts) // 2]}, min {min(tsts)}, max {max(tsts)} (at 97).  Unremarkable.")
out("  dropping genus of 36 = (1, 0, 17): index 17 because 36 is the 18th even number.  The '17' is 36/2 - 1.")
out("  T_n along the -17 cycle contains T_(-37) = T_36 = 666; no content.")
out("  T_(n0) at the cycle minima -5, -17 equals 10 = T_4, 136 = T_16, and -10, -136 lie on those cycles.")
out("  With n0 = -(2^j + 1): T_(n0) = 2^(j-1) |n0|, and the cycle contains 2^i n0 for i up to the length e of")
out("  its last halving run, so this says e >= j - 1.  Here (j, e) = (2, 1) and (4, 3): two instances, no mechanism.")

with open(os.path.join(HERE, "q25_thirty_six.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, default=str)
out.close()
