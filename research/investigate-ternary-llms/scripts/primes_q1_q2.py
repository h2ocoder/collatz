"""Q1 and Q2 from 'Primes and the Circuit'.

Q1  Census of divisibility-preserving residue classes.  For each dropping set k = s + b and each
    of its residue classes r mod 2^b, the intercept C_r satisfies  2^b dest(n) = 3^s n + r(v)  with
    r(v) the parity-vector constant, so for p | n:  p | dest(n)  <=>  p | r(v).  We count, for each
    odd prime p <= 47, the fraction of classes (weighted by their density 2^-(b-1)) with r(v) = 0
    (mod p), and compare with 1/p.  p = 3 must give 0 (3-adic lock).

Q2  Multiplication table of classes to mod 2^16.  Theorem (proved in the note): Set_3 is exactly
    the residue class 1 mod 4 = the index-2 subgroup U of (Z/2^b)^*; for q uniform in U and any n,
    q n is uniform on the coset n U.  Hence class(q n) for class(q) = 3 is distributed as a uniform
    residue = n mod 4, independent of n's class; and class(q) , class(n) both > 3 gives q n = 1 mod 4,
    class 3.  Checked here by sampling at b = 16.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/primes_q1_q2.py
"""
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def terras_parity_vector_until_drop(n):
    """Terras steps from n until value < n; returns parity vector v (list) and s = #ones."""
    v, x = [], n
    while True:
        v.append(x & 1)
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
        if x < n:
            return v


def r_of(v):
    r, pow3 = 0, 1
    for i in range(len(v) - 1, -1, -1):
        if v[i]:
            r += pow3 << i
            pow3 *= 3
    return r


if __name__ == "__main__":
    out = {}
    # ---------------- Q1
    B = 16  # classify residues mod 2^16: every class with b(s) <= 16 is complete
    classes = defaultdict(dict)  # k -> {r mod 2^b : r(v)}
    seen = set()
    for n in range(3, 1 << B, 2):
        v = terras_parity_vector_until_drop(n)
        b = len(v)
        if b > B:
            continue
        s = sum(v)
        k = s + b
        r = n % (1 << b)
        if (k, r) not in seen:
            seen.add((k, r))
            classes[k][r] = (r_of(v), s, b)
    print("Q1. residue classes per dropping set found at 16 bits:", {k: len(d) for k, d in sorted(classes.items())})
    print("    fraction of classes (density-weighted) whose intercept r(v) is 0 mod p, vs 1/p:")
    print("     p    fraction    1/p     ratio    (unweighted count / classes)")
    q1 = {}
    for p in PRIMES:
        w0 = wt = Fraction(0)
        c0 = ct = 0
        for k, d in classes.items():
            for r, (rv, s, b) in d.items():
                w = Fraction(1, 1 << (b - 1))
                wt += w
                ct += 1
                if rv % p == 0:
                    w0 += w
                    c0 += 1
        frac = float(w0 / wt)
        q1[p] = dict(fraction=frac, count=c0, classes=ct)
        print(f"    {p:3d}   {frac:.4f}    {1/p:.4f}   {frac*p:5.2f}    ({c0} / {ct})")
    out["Q1"] = q1
    # the r(v) values mod 3: all nonzero?  and mod p distribution flatness
    resid3 = Counter(rv % 3 for d in classes.values() for rv, s, b in d.values())
    print(f"    r(v) mod 3 over all classes: {dict(resid3)}   (0 never: 3-adic lock)")

    # ---------------- Q2
    M = 1 << 16
    cls = {}
    for n in range(1, M, 2):
        if n == 1:
            cls[n] = 3
            continue
        k = stopping_time(n)
        cls[n] = k if k <= 26 else 99  # 99 = undecided at 16 bits
    byc = defaultdict(list)
    for r, c in cls.items():
        byc[c].append(r)
    labels = sorted(byc)
    print("\nQ2. multiplication table at mod 2^16 (sampled 200k pairs per cell); rows: class(q), class(n)")
    rng = np.random.default_rng(0)
    uncond_hi = Counter(cls[r] for r in range(3, M, 4))  # residues 3 mod 4
    tot_hi = sum(uncond_hi.values())
    print("    unconditional distribution over 3-mod-4 residues: " + " ".join(f"{c}:{uncond_hi[c]/tot_hi:.3f}" for c in labels if c != 3))
    maxdev_row3 = 0.0
    all_hi_to_3 = True
    q2 = {}
    for a in labels:
        for b in labels:
            qa, nb = np.array(byc[a]), np.array(byc[b])
            prods = (rng.choice(qa, 200000) * rng.choice(nb, 200000)) % M
            dist = Counter(int(cls[int(x)]) for x in prods)
            row = {c: dist[c] / 200000 for c in labels}
            q2[f"{a}x{b}"] = row
            if a == 3 and b == 3:
                ok = row[3] == 1.0
            elif a == 3 or b == 3:
                dev = max(abs(row[c] - uncond_hi[c] / tot_hi) for c in labels if c != 3)
                maxdev_row3 = max(maxdev_row3, dev)
            else:
                all_hi_to_3 &= row[3] == 1.0
    print(f"    3 x 3 -> 3 exactly: {q2['3x3'][3] == 1.0}")
    print(f"    higher x higher -> 3 exactly, all {(len(labels)-1)**2} cells: {all_hi_to_3}")
    print(f"    3 x higher rows vs the unconditional 3-mod-4 distribution: max deviation {maxdev_row3:.4f} (sampling noise ~0.002)")
    out["Q2"] = dict(max_dev_row3=maxdev_row3, all_hi_to_3=all_hi_to_3, labels=labels)
    json.dump(out, open(RESULTS / "primes_q1_q2.json", "w"), indent=1)
