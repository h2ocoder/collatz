"""Skeptic finding: 'squares meet only two dropping classes' is NOT rule-blind.  It is sign-aware.

The researcher's README labelled every dropping-class statement about figurate families 'blind' and wrote
'for 3x-1 odd squares fall in a different single class' without computing it.  Computed here:

  * odd squares are dense in 1 + 8 Z_2 (rule-free).  They meet a single dropping class of the rule (q, d)
    iff the whole ball 1 + 8 Z_2 is inside one class, i.e. iff the parity word of the integer 1 drops within
    3 steps.  That is a statement about the cycle through 1:
        3x+1:  1 -> 2 -> 1,        word 10,   3 < 4   -> class 1 mod 4  (Set_3)        TWO classes for squares
        7x+1:  1 -> 4 -> 2 -> 1,   word 100,  7 < 8   -> class 1 mod 8                 TWO classes
        3x-1:  1 -> 1,             word 1,    3 > 2   -> 1 is an expanding fixed point INFINITELY many classes
        5x+1:  1 -> 3 -> 8 -> 4 -> 2 -> 1, word 11000 (drops at k = 5, needs 1 mod 32) many classes
  * exact law in the spread case: class counts of odd squares = 4 * (class counts of the residues 1 mod 8);
  * mirror statement: n^2 under 3x+1  <->  -n^2 under 3x-1 (so the NEGATIVES of squares are the two-class
    family of 3x-1), which is the content of the repo's Three-Step Theorem (the shared bit n mod 4).

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v7_squares_see_the_sign.py
"""
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v7_squares_see_the_sign.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def smax_table(K, q):
    t = [0] * (K + 1)
    for k in range(1, K + 1):
        s = 0
        while q ** (s + 1) < (1 << k):
            s += 1
        t[k] = s
    return t


def class_labels(K, q, d):
    M = 1 << K
    x = np.arange(M, dtype=np.int64)
    s = np.zeros(M, dtype=np.int64)
    lab = np.zeros(M, dtype=np.int64)
    alive = np.ones(M, dtype=bool)
    sm = smax_table(K, q)
    for k in range(1, K + 1):
        odd = (x & 1) == 1
        x = np.where(odd, (q * x + d) >> 1, x >> 1)
        x &= (1 << (K - k)) - 1
        s += odd
        drop = alive & (s <= sm[k])
        lab[drop] = k
        alive &= ~drop
    return lab


def word_of_one(q, d, L=8):
    x, w, s = 1, "", 0
    drop = None
    for k in range(1, L + 1):
        if x & 1:
            x = (q * x + d) >> 1
            s += 1
            w += "1"
        else:
            x >>= 1
            w += "0"
        if drop is None and q ** s < 2 ** k:
            drop = k
    return w, drop


K = 18
M = 1 << K
w = np.arange(1, M, 2, dtype=np.int64)
sq = (w * w) & (M - 1)
out("=" * 100)
out(f"A. Odd squares mod 2^{K} against the dropping classes of seven rules (residue level, exact)")
out("=" * 100)
out("   rule    word of 1   first drop of the word of 1   #classes met by odd squares   share in the largest   law = 4 x (law on 1 mod 8)")
RES["A"] = {}
for (q, d) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (7, -1), (15, 1)):
    lab = class_labels(K, q, d)
    c_sq = np.bincount(lab[sq], minlength=K + 1)
    r = np.arange(1, M, 8, dtype=np.int64)
    c_ball = np.bincount(lab[r], minlength=K + 1)
    exact = bool((c_sq == 4 * c_ball).all())
    ncl = int((c_sq[1:] > 0).sum())
    wd, dr = word_of_one(q, d)
    out(f"   {q:2d}x{d:+d}   {wd}    {str(dr):>4s}                          {ncl:3d}                        "
        f"{c_sq[1:].max() / len(sq):.4f}                 {exact}")
    RES["A"][f"{q}x{d:+d}"] = dict(word=wd, drop=dr, classes=ncl, exact=exact)
out("  -> one class for the odd squares exactly when the word of 1 drops within 3 letters: 3x+1 (10) and 7x+1 (100).")
out("     For 3x-1 the integer 1 is a fixed point with the expanding word 111..., so odd squares (2-adically within")
out("     1/8 of 1) start with at least 3 odd steps and then spread over every later class.")

out("")
out("  criterion over a grid: odd squares lie in ONE class  <=>  (q = 3 and d = 1 mod 4) or (q in {5,7} and q + d = 0 mod 8)")
Kg = 12
Mg = 1 << Kg
wg = np.arange(1, Mg, 2, dtype=np.int64)
sqg = (wg * wg) & (Mg - 1)
okg = True
single = []
for q in range(3, 32, 2):
    for d in range(-31, 32, 2):
        lab = class_labels(Kg, q, d)
        c = np.bincount(lab[sqg], minlength=Kg + 1)
        one = int((c[1:] > 0).sum()) == 1 and c[0] == 0
        pred = (q == 3 and d % 4 == 1) or (q in (5, 7) and (q + d) % 8 == 0)
        okg &= one == pred
        if one:
            single.append((q, d))
out(f"     q = 3..31 odd, d = -31..31 odd (K = {Kg}): criterion holds on the whole grid: {okg}")
out(f"     rules with the one-class property: {single}")
RES["A_grid_ok"] = okg

out("")
out("=" * 100)
out("B. Mirror: n^2 under 3x+1 versus -n^2 under 3x-1, and n^2 under 3x-1 versus -n^2 under 3x+1 (actual integers)")
out("=" * 100)


def stop_abs(x0, q, d, cap=100000):
    """Terras stopping time in absolute value (first k with |T^k x| < |x|)."""
    x, k = x0, 0
    while k < cap:
        x = (q * x + d) // 2 if x % 2 else x // 2
        k += 1
        if abs(x) < abs(x0):
            return k
    return None


okm = True
h_plus, h_minus = {}, {}
for n in range(3, 40001, 2):
    a = stop_abs(n * n, 3, 1)
    b = stop_abs(-n * n, 3, -1)
    c = stop_abs(n * n, 3, -1)
    e = stop_abs(-n * n, 3, 1)
    okm &= a == b and c == e
    h_plus[a] = h_plus.get(a, 0) + 1
    h_minus[c] = h_minus.get(c, 0) + 1
out("  stop(n^2; 3x+1) = stop(-n^2; 3x-1) and stop(n^2; 3x-1) = stop(-n^2; 3x+1) for odd 3 <= n <= 40000:", okm)
out("  odd squares under 3x+1: stopping times", h_plus)
out(f"  odd squares under 3x-1: {len(h_minus)} distinct stopping times; smallest five {sorted(h_minus.items())[:5]}")
out("  first-run length of n^2 under 3x-1 equals v2(n^2 - 1) >= 3 (2-adic distance to the fixed point 1):",
    all((lambda x: ((x - 1) & -(x - 1)).bit_length() - 1)(n * n) >= 3 for n in range(3, 2001, 2)))
RES["B"] = dict(mirror_ok=okm, plus=h_plus, minus_distinct=len(h_minus))

out("")
out("=" * 100)
out("C. Same test for the other collapsed objects of the README")
out("=" * 100)
for (q, d) in ((3, 1), (3, -1), (5, 1), (7, 1)):
    lab = class_labels(16, q, d)
    Mm = 1 << 16
    n = np.arange(Mm, dtype=np.int64)
    rows = []
    for name, f in (("octagonal", (3 * n * n - 2 * n) % Mm), ("dodecagonal", (5 * n * n - 4 * n) % Mm),
                    ("T_n^2", None)):
        if f is None:
            n2 = np.arange(2 * Mm, dtype=np.int64)
            t = (n2 * (n2 + 1) // 2) % Mm
            f = (t * t) % Mm
        c = np.bincount(lab[f], minlength=17)
        rows.append(f"{name}: {int((c[1:] > 0).sum())}")
    out(f"   {q}x{d:+d}: number of determined classes (k <= 16) met  ->  " + ",  ".join(rows))
out("  (octagonal odd values are 1 mod 4 but both 1 and 5 mod 8, so they are a single class only where 1 mod 4 is one.)")

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v7_squares_see_the_sign.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
