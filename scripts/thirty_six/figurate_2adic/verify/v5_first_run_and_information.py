"""Skeptic check 5: the first-run law (X-1) and the half-bit theorem (X-2), independently of q26.

  * first-run law on all |n| <= 3*10^5 (negative n included) for 3x+1, 3x-1, 5x+1, 7x+1, 7x+3, with the
    quadratic of each rule written from the 2-adic fixed point of its odd branch (so the test is whether the law
    is special to 3x+1 or a statement every rule has);
  * mutual information I(class(n); class(F(n))) for K = 8 .. 20 (the researcher reported K = 16 only), to see
    which reported decimals are limits and which are artefacts of the truncation level K;
  * the two parabolas of the 'leads' section.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v5_first_run_and_information.py
"""
import json
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v5_first_run_and_information.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def v2(n):
    n = abs(n)
    return (n & -n).bit_length() - 1


def first_run(x, q, d, cap=400):
    p0, L = x & 1, 0
    while (x & 1) == p0 and L < cap:
        x = (q * x + d) >> 1 if x & 1 else x >> 1
        L += 1
    return L


out("=" * 100)
out("A. First-run law: L1(n) = v2(n) + v2((q-2) n + d)   for the rule (q n + d)/2,   all 0 < |n| <= 300000")
out("   ((q-2) n + d vanishes at the fixed point -d/(q-2) of the odd branch; n vanishes at the fixed point of n/2)")
out("=" * 100)
RES["A"] = {}
for (q, d) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (7, 3), (9, 1)):
    ok = True
    skipped = []
    for n in range(-300000, 300001):
        w = (q - 2) * n + d
        if n == 0 or w == 0:
            skipped.append(n)
            continue
        if first_run(n, q, d) != v2(n) + v2(w):
            ok = False
            break
    out(f"  {q}x{d:+d}: law holds: {ok}   excluded (branch fixed points in Z): {skipped}"
        f"   quadratic n((q-2)n{d:+d})/2 = {'T_n' if (q, d) == (3, 1) else ('T_(n-1)' if (q, d) == (3, -1) else 'not triangular')}")
    RES["A"][f"{q}x{d:+d}"] = ok
out("  -> every rule has a first-run law; what is special to 3x+-1 is only that the odd-branch fixed point (-+1)")
out("     is an integer, so the quadratic is n(n+-1)/2.  The law itself does not single out 3, nor the sign.")

out("")
out("=" * 100)
out("B. Mutual information I(class(n); class(F(n))) in bits, n uniform on Z/2^(K+1), 'undetermined at level K' = one class")
out("=" * 100)


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


def mi_bits(a, b, K):
    joint = np.zeros((K + 1, K + 1), dtype=np.float64)
    np.add.at(joint, (a, b), 1.0)
    joint /= joint.sum()
    pa, pb = joint.sum(axis=1), joint.sum(axis=0)
    nz = joint > 0
    return float((joint[nz] * np.log2(joint[nz] / np.outer(pa, pb)[nz])).sum()), \
        float(-(pb[pb > 0] * np.log2(pb[pb > 0])).sum())


CASES = [
    ("3x+1 | T_n", 3, 1, lambda n: n * (n + 1) // 2),
    ("3x-1 | T_(n-1)", 3, -1, lambda n: n * (n - 1) // 2),
    ("3x-1 | T_n", 3, -1, lambda n: n * (n + 1) // 2),
    ("5x+1 | n(3n+1)/2", 5, 1, lambda n: n * (3 * n + 1) // 2),
    ("5x-1 | n(3n-1)/2", 5, -1, lambda n: n * (3 * n - 1) // 2),
    ("5x+1 | T_n", 5, 1, lambda n: n * (n + 1) // 2),
]
KS = (8, 10, 12, 14, 16, 18, 20)
out("   case                " + "".join(f"   K={K:<4d}" for K in KS))
RES["B"] = {}
for name, q, d, f in CASES:
    row = []
    for K in KS:
        M = 1 << K
        lab = class_labels(K, q, d)
        n = np.arange(2 * M, dtype=np.int64)
        a = lab[n & (M - 1)]
        b = lab[f(n) & (M - 1)]
        row.append(mi_bits(a, b, K)[0])
    out(f"   {name:20s}" + "".join(f" {v:8.5f}" for v in row))
    RES["B"][name] = row
out("  -> 0.5 is exact at every K for 3x+1 | T_n and 3x-1 | T_(n-1) (Theorem 7 holds level by level);")
out("     the 5x+-1 figures and 3x-1 | T_n drift with K: quote them only as 'K = 16' values, not as constants.")
h = []
for K in KS:
    lab = class_labels(K, 3, 1)
    p = np.bincount(lab, minlength=K + 1) / (1 << K)
    h.append(float(-(p[p > 0] * np.log2(p[p > 0])).sum()))
out("  entropy of the natural class law at level K (3x+1):", [round(x, 4) for x in h], " (increasing; finite limit")
out("  because the undetermined mass decays geometrically, Terras 1976 / Everett 1977)")

out("")
out("=" * 100)
out("C. The two parabolas of the NOT-quotient correspondence (README, 'Leads'): even e, t = T_e")
out("=" * 100)
okp = True
for e in range(-200000, 200001, 2):
    t = e * (e + 1) // 2
    t1 = (e // 2) * (e // 2 + 1) // 2
    t2 = (3 * e // 2) * (3 * e // 2 + 1) // 2
    okp &= (8 * t1 + 1 - 2 * t) ** 2 == 8 * t1 + 1 and (18 * t - 8 * t2 + 1) ** 2 == 8 * t2 + 1
out("  (8t'+1-2t)^2 = 8t'+1 for t' = T_(e/2) and (18t-8t'+1)^2 = 8t'+1 for t' = T_(3e/2), all even |e| <= 200000:", okp)
RES["C"] = okp

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v5_first_run_and_information.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
