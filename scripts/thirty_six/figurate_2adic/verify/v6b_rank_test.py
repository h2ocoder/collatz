"""Skeptic check 6b: rank test for the Pell-orbit total stopping times (follow-up to v6).

v6 found sd(z) = 1.24 .. 1.40 for u_j against a calibrated null of 1.03 (replicate range 0.90 .. 1.24).
z with an estimated sd is heavy-tailed, so here each term is ranked among 300 matched controls instead
(same bit length, same residue mod 16).  Under the null the rank is uniform.  Reported: the share of terms
in the two outer deciles (expected 0.20), the mean rank (expected 0.5) and a Kolmogorov-Smirnov distance
with its asymptotic p-value.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v6b_rank_test.py     (about 2 minutes)
"""
import json
import math
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v6b_rank_test.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def tst(x):
    c = 0
    while x != 1:
        x = (3 * x + 1) >> 1 if x & 1 else x >> 1
        c += 1
    return c


JMIN, JMAX, NC = 5, 160, 300
u, m = [1, 3], [0, 1]
for j in range(2, JMAX + 1):
    u.append(6 * u[-1] - u[-2])
    m.append(6 * m[-1] - m[-2])
n = [(x - 1) // 2 for x in u]
rng = random.Random(41616)


def control(x):
    bl = x.bit_length()
    y = rng.getrandbits(bl - 1) | (1 << (bl - 1))
    return (y >> 4 << 4) | (x & 15)


def ks_p(d, nn):
    lam = (math.sqrt(nn) + 0.12 + 0.11 / math.sqrt(nn)) * d
    return max(0.0, min(1.0, 2 * sum((-1) ** (i - 1) * math.exp(-2 * i * i * lam * lam) for i in range(1, 101))))


def report(name, ranks):
    ranks = sorted(ranks)
    nn = len(ranks)
    outer = sum(1 for r in ranks if r < 0.1 or r > 0.9) / nn
    d = max(max(abs((i + 1) / nn - r), abs(i / nn - r)) for i, r in enumerate(ranks))
    se = math.sqrt(0.2 * 0.8 / nn)
    out(f"  {name:22s} terms {nn:3d}   mean rank {sum(ranks) / nn:.3f}   outer-decile share {outer:.3f}"
        f" (expected 0.200 +- {se:.3f})   KS D = {d:.3f}, p = {ks_p(d, nn):.3f}")
    RES[name] = dict(mean=sum(ranks) / nn, outer=outer, ks=d, p=ks_p(d, nn))


out("=" * 100)
out(f"rank of tst(x_j) among {NC} matched random controls, j = {JMIN}..{JMAX}")
out("=" * 100)
for name, seq in (("u_j", u), ("n_j", n)):
    rk = {}
    for j in range(JMIN, JMAX + 1):
        x = seq[j]
        t = tst(x)
        ctr = [tst(control(x)) for _ in range(NC)]
        below = sum(1 for c in ctr if c < t)
        ties = sum(1 for c in ctr if c == t)
        rk[j] = (below + 0.5 * ties + 0.5) / (NC + 1)
    report(f"Pell {name} all", list(rk.values()))
    report(f"Pell {name} j even", [r for j, r in rk.items() if j % 2 == 0])
    report(f"Pell {name} j odd", [r for j, r in rk.items() if j % 2 == 1])
# calibration: a random matched integer in place of the Pell term
rk = []
for j in range(JMIN, JMAX + 1):
    x = control(u[j])
    t = tst(x)
    ctr = [tst(control(u[j])) for _ in range(NC)]
    rk.append((sum(1 for c in ctr if c < t) + 0.5 * sum(1 for c in ctr if c == t) + 0.5) / (NC + 1))
report("null (u_j sizes)", rk)

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v6b_rank_test.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
