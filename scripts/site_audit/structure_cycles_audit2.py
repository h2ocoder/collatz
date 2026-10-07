"""Second batch of audit checks for the 'structure-cycles' section.

1. Orbit maximum: is it one affine function on each dropping class? (rigorous for level <= 24)
2. The increasing-order constraint for a negative gap (the -17 cycle, gap -139).
3. Mutual information between consecutive dropping sets at several ranges, with the
   plug-in bias, and total-variation variants.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 structure_cycles_audit2.py
"""
from __future__ import annotations

import itertools
import math
from collections import Counter
from fractions import Fraction

import numpy as np


def f(n: int) -> int:
    return 3 * n + 1 if n & 1 else n >> 1


# ---------------------------------------------------------------- 1. orbit maximum
LEVEL = 24
N = 1 << LEVEL
n0 = np.arange(N, dtype=np.int64)
x = n0.copy()
sodd = np.zeros(N, dtype=np.int64)
tau = np.zeros(N, dtype=np.int64)
pow3 = np.array([3**i for i in range(40)], dtype=np.int64)
for j in range(1, LEVEL + 1):
    odd = (x & 1).astype(bool)
    x = np.where(odd, (3 * x + 1) >> 1, x >> 1)
    sodd += odd
    new_tau = (tau == 0) & (pow3[sodd] < (1 << j))
    tau[new_tau] = j

checked = bad = 0
bad_rows = []
for lev in range(1, LEVEL + 1):
    rs = np.nonzero((tau == lev) & (n0 < (1 << lev)))[0].tolist()
    for r in rs:
        m = r if r >= 2 else r + (1 << lev)       # least member >= 2
        # un-shortcut orbit up to the drop, with slope of each iterate as (s, e): 3^s / 2^e
        xx, s, e = m, 0, 0
        vals, slopes = [], []
        while True:
            vals.append(xx)
            slopes.append((s, e))
            if xx & 1:
                xx = 3 * xx + 1
                s += 1
            else:
                xx >>= 1
                e += 1
            if xx < m:
                break
        # index of largest slope (exact comparison of 3^s/2^e)
        jstar = max(range(len(slopes)), key=lambda i: Fraction(3 ** slopes[i][0], 2 ** slopes[i][1]))
        jmax = vals.index(max(vals))
        checked += 1
        if jstar != jmax:
            bad += 1
            bad_rows.append((lev, r, m, jstar, jmax))
print(f"1. orbit max: classes of Terras level <= {LEVEL} checked: {checked}; "
      f"least member >= 2 has its maximum away from the largest-slope step: {bad}")
print("   ", bad_rows[:10])
print("   (if the least member peaks at the largest-slope step, every larger member does:"
      " f^j(n) <= f^j*(n) is n(a* - a_j) >= b_j - b*, monotone in n; so the max is affine"
      " on the whole class)")

# ---------------------------------------------------------------- 2. negative gap
S, E = 7, 11
g = 2**E - 3**S
zeros = []
tot = 0
for rest in itertools.combinations(range(1, E), S - 1):
    q = (0,) + rest
    T = sum(3 ** (S - 1 - j) * 2 ** q[j] for j in range(S))
    tot += 1
    if T % g == 0:
        zeros.append((q, T // g))
print(f"2. S={S}, E={E}, gap={g}: increasing assignments with q_0=0: {tot}; with g | T: {len(zeros)}")
for q, n in zeros:
    print("    q =", q, " n = T/g =", n)
orb, y = [], -17
for _ in range(18):
    orb.append(y)
    y = f(y)
print("   orbit of -17:", orb)

# ---------------------------------------------------------------- 3. mutual information


def tables(limit: int):
    """k (un-shortcut dropping time) and dest for 2 <= n < limit, vectorised."""
    n1 = np.arange(limit, dtype=np.int64)
    x = n1.copy()
    sodd = np.zeros(limit, dtype=np.int64)
    e = np.zeros(limit, dtype=np.int64)
    dest = np.zeros(limit, dtype=np.int64)
    done = np.zeros(limit, dtype=bool)
    done[:2] = True
    j = 0
    while not done.all():
        j += 1
        act = ~done
        odd = (x & 1).astype(bool) & act
        x = np.where(act, np.where(odd, (3 * x + 1) >> 1, x >> 1), x)
        sodd += odd
        newly = act & (x < n1)
        e[newly] = j
        dest[newly] = x[newly]
        done |= newly
    return e + sodd, dest


def H(counts):
    c = np.asarray(list(counts), dtype=float)
    c = c[c > 0]
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def report(limit: int, odd_only: bool):
    k, dest = tables(limit)
    idx = np.arange(2, limit)
    if odd_only:
        idx = idx[idx % 2 == 1]
    idx = idx[dest[idx] >= 2]
    cur = k[idx]
    nxt = k[dest[idx]]
    Ntot = len(idx)
    joint = Counter(zip(cur.tolist(), nxt.tolist()))
    c_cur, c_nxt = Counter(cur.tolist()), Counter(nxt.tolist())
    Hc, Hn, Hj = H(c_cur.values()), H(c_nxt.values()), H(joint.values())
    I = Hc + Hn - Hj
    bias = (len(joint) - len(c_cur) - len(c_nxt) + 1) / (2 * Ntot * math.log(2))
    tv_joint = 0.5 * sum(abs(joint.get((a, b), 0) / Ntot - c_cur[a] / Ntot * c_nxt[b] / Ntot)
                         for a in c_cur for b in c_nxt)
    # marginal of the next set versus the dropping-set law of ALL n in range
    allk = Counter(k[2:limit].tolist())
    keys = set(allk) | set(c_nxt)
    tv_marg = 0.5 * sum(abs(allk.get(a, 0) / (limit - 2) - c_nxt.get(a, 0) / Ntot) for a in keys)
    print(f"   limit={limit:>9,d} {'odd n' if odd_only else 'all n'}: pairs={Ntot:>9,d} "
          f"H(cur)={Hc:.3f} H(next)={Hn:.3f} H(next|cur)={Hj - Hc:.3f} I={I:.4f} bits "
          f"({I / Hn:.2%} of H(next)); nonempty joint cells={len(joint)}; "
          f"Miller-Madow bias={bias:.4f}; I-bias={I - bias:+.4f}; "
          f"TV(joint,product)={tv_joint:.4f}; TV(next marginal, all-n law)={tv_marg:.4f}")


print("3. mutual information between Set(n) and Set(dest(n))")
for limit in (50_000, 500_000, 5_000_000):
    for odd_only in (False, True):
        report(limit, odd_only)
