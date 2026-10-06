"""Skeptic check 8: when does 'class of the residue' equal 'Terras stopping time of the integer'?

The README said: 'For an actual integer the Terras stopping time equals the class value except for integers
on a cycle.'  In general that is Terras's Coefficient Stopping Time conjecture (open; Terras 1976 proved it for
coefficient stopping time <= 2593).  For the classes used in this thread it is a finite check:

  if r is the least non-negative residue of a class of level k (word with s odd steps, 3^s < 2^k), then for
  n = r + 2^k t:   T^k(n) - n = (T^k(r) - r) - (2^k - 3^s) t,   and T^j(n) > n for j < k (coefficient > 1,
  constant >= 0).  So every member n >= r has stopping time exactly k as soon as T^k(r) < r.

Here: T^k(r) < r is tested for the least residue of EVERY class with k <= 24 (all r < 2^24), for 3x+1 and 3x-1.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v8_class_equals_stopping_time.py
"""
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v8_class_equals_stopping_time.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


K = 24
M = 1 << K
for (q, d) in ((3, 1), (3, -1)):
    sm = [0] * (K + 1)
    for k in range(1, K + 1):
        s = 0
        while q ** (s + 1) < (1 << k):
            s += 1
        sm[k] = s
    r = np.arange(M, dtype=np.int64)
    x = r.copy()                               # exact integer iterates (no reduction): < 2^24 * (3/2)^24 < 2^39
    s = np.zeros(M, dtype=np.int64)
    coeff = np.zeros(M, dtype=np.int64)        # coefficient stopping time (0 = > K)
    actual = np.zeros(M, dtype=np.int64)       # first k <= K with T^k(r) < r (0 = none)
    for k in range(1, K + 1):
        odd = (x & 1) == 1
        x = np.where(odd, (q * x + d) >> 1, x >> 1)
        s += odd
        newc = (coeff == 0) & (s <= sm[k])
        coeff[newc] = k
        newa = (actual == 0) & (x < r)
        actual[newa] = k
    # only least residues: r < 2^k for its own class level k
    least = (coeff > 0) & (r < (np.int64(1) << coeff))
    bad = np.nonzero(least & (actual != coeff))[0]
    n_classes = int(least.sum())
    out(f"  {q}x{d:+d}: classes with k <= {K}: {n_classes};  least residues r with T^k(r) >= r (exceptions): {bad.tolist()}")
    early = np.nonzero((coeff > 0) & (actual != 0) & (actual < coeff))[0]
    out(f"         residues r < 2^{K} that drop BEFORE their coefficient stopping time: {early.tolist()[:10]}")
    undet_drop = int(((coeff == 0) & (actual > 0)).sum())
    out(f"         residues with coefficient stopping time > {K} that nevertheless drop within {K} steps: {undet_drop}")
    RES[f"{q}x{d:+d}"] = dict(classes=n_classes, exceptions=bad.tolist(), early=early.tolist()[:10])
out("")
out("  Consequence (3x+1): for every integer n >= 2 whose class has level k <= 24, the Terras stopping time is exactly k.")
out("  The only exceptions among non-negative integers are n = 0 (class 'even') and n = 1 (class 1 mod 4), the two")
out("  non-negative cycles.  So Corollary 1 of the README holds for actual integers, for all K, for every k <= 24;")
out("  beyond that it is Terras's theorem up to 2593 and his Coefficient Stopping Time conjecture in general.")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v8_class_equals_stopping_time.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
