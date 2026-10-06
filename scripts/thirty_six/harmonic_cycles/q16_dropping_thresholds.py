"""Q1.6 (beyond the seed)  Unit cells seen from the repo's dropping classes.

Two step counts are in play -- stated on every table:
  * repo / Paper 1:  dropping_time(n) = number of steps of the NON-shortcut map
    (n -> n/2, n -> 3n+1) until the first value < n;  Dropping Set_K = {n : dropping_time = K};
    orbital_oddity = number of odd values in the dropping orbit (which includes n).
  * this thread: shortcut word w of length k with s ones.  For the same n:
        K = k + s,   orbital_oddity = s.
For a dropping word w (first passage below n) with D = 2^k - 3^s > 0:
        T^k(n) = (3^s n + C(w))/2^k < n   <=>   n > x(w) = C(w)/D     ("threshold").
Output: q16_dropping_thresholds.log, q16_dropping_thresholds.json
"""
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, "C:/repos/collatz")
from collatz import dropping as repo_dropping          # noqa: E402

from hc_common import T, Tee, word_constant            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q16_dropping_thresholds.log"))
J = {}

NMAX = 1 << 17
classes = defaultdict(lambda: defaultdict(list))        # (k,s) -> word -> members
for n in range(2, NMAX):
    w = []
    m = n
    while True:
        w.append(m & 1)
        m = T(m)
        if m < n:
            break
        if len(w) > 400:
            raise RuntimeError(n)
    w = tuple(w)
    classes[(len(w), sum(w))][w].append(n)

# cross-check the convention against the repo's own functions
chk = 0
for (k, s), d in classes.items():
    for w, members in d.items():
        for n in members[:2]:
            assert repo_dropping.dropping_time(n) == k + s, (n, k, s)
            assert repo_dropping.orbital_oddity(n) == s, (n, k, s)
            chk += 1
out(f"convention check against collatz.dropping (dropping_time = k + s, orbital_oddity = s): {chk} values OK")

out("")
out("Dropping classes of 2 <= n < 2^17, grouped by shortcut cell (k, s).   K = k + s is the")
out("repo's Dropping Set index.  'words' = distinct shortcut dropping words seen (inner subsets).")
out("  K   (k,s)    D=2^k-3^s  words  thresholds x(w)=C(w)/D (min .. max)   smallest member   integer threshold?")
rows = []
for (k, s) in sorted(classes, key=lambda c: (c[0] + c[1])):
    if k > 16:
        continue
    D = 2 ** k - 3 ** s
    assert D > 0
    thr = []
    integer_thr = []
    for w, members in classes[(k, s)].items():
        x = Fraction(word_constant(w), D)
        thr.append(x)
        assert all(n > x for n in members)
        if x.denominator == 1:
            integer_thr.append((''.join(map(str, w)), int(x)))
    smallest = min(min(m) for m in classes[(k, s)].values())
    out(f" {k+s:3d}  ({k},{s})".ljust(14) + f"{D:<10d} {len(thr):<6d} "
        f"{str(min(thr)):>10s} .. {str(max(thr)):<14s}   {smallest:<16d}  {integer_thr if integer_thr else 'no'}")
    rows.append({"K": k + s, "k": k, "s": s, "D": D, "words_seen": len(thr),
                 "thr_min": str(min(thr)), "thr_max": str(max(thr)), "smallest_member": smallest,
                 "integer_thresholds": integer_thr})
J["dropping_cells"] = rows
int_cells = [(r["K"], r["k"], r["s"], r["integer_thresholds"]) for r in rows if r["integer_thresholds"]]
out("")
out(f"cells with an integer threshold: {int_cells}")
out("  -> Dropping Set_1 (evens, threshold 0) and Dropping Set_3 (n = 1 mod 4, threshold 1):")
out("     exactly the two unit cells with D = +1.  These are the '> 0' and '> 1' in the repo docstring")
out("     'Dropping Set_3 = {n : n = 1 (mod 4), n > 1}'.")
J["cells_with_integer_threshold"] = int_cells
assert [(c[1], c[2]) for c in int_cells] == [(1, 0), (2, 1)]

# the mirror: 3x-1 on positive integers (= 3x+1 on negative integers)
out("")
out("Mirror map T-(n) = n/2 | (3n-1)/2 on positive integers: thresholds are -C(w)/D < 0, so every")
out("member of every dropping class drops; the unit cells with D = -1, (1,1) and (3,2), are RISING")
out("cells and hold the fixed point 1 and the cycle 5 -> 7 -> 10, whose members never drop:")
for n in (1, 5, 7, 10, 17):
    m = n
    seq = [m]
    for _ in range(12):
        m = m // 2 if m % 2 == 0 else (3 * m - 1) // 2
        seq.append(m)
    out(f"   n = {n}: {seq}")

with open(os.path.join(HERE, "q16_dropping_thresholds.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q16_dropping_thresholds.json")
out.close()
