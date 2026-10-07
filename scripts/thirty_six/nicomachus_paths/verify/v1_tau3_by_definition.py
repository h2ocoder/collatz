"""Skeptic check 1 (Q5.1-a, Q5.2-a..d).  INDEPENDENT code path.

F(n) = sum_{d|n} tau(d) is computed here straight from the DEFINITION by two additive
divisor sieves (no multiplicativity, no triangular-number formula):
    tau[m]  += 1        for every multiple m of d
    F[m]    += tau[d]   for every multiple m of d
The researcher's script instead builds F multiplicatively from prod T_(a+1).

Then: E_3, fixed points, cycles, sup F(n)/n, basins, transient distribution, preimages of 36,
basin(3) == primes, and edge cases.

Run: python -X utf8 v1_tau3_by_definition.py     (about 1-2 min)
"""
import os
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v1_tau3_by_definition.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


N = 10 ** 7
t0 = time.time()
tau = np.zeros(N + 1, dtype=np.int32)
for d in range(1, N + 1):
    tau[d::d] += 1
out(f"tau sieve done {time.time()-t0:.1f}s; tau(36) = {tau[36]}, max tau = {tau.max()}")
F = np.zeros(N + 1, dtype=np.int64)
taul = tau.tolist()
for d in range(1, N + 1):
    F[d::d] += taul[d]
out(f"F sieve done {time.time()-t0:.1f}s; F(36) = {F[36]}, F(1..12) = {F[1:13].tolist()}")

# Liouville as a side check on the sieve: sum_{d|n} tau(d)^3 == F(n)^2 for n <= 2*10^5
M = 2 * 10 ** 5
C = np.zeros(M + 1, dtype=np.int64)
for d in range(1, M + 1):
    C[d::d] += taul[d] ** 3
out("Liouville sum tau(d)^3 == F(n)^2 for n <= 2e5:", bool(np.all(C[1:] == F[1:M + 1] ** 2)))
out("n <= 2e5 with sum_{d|n} tau(d)^3 == n^2:", [n for n in range(1, M + 1) if C[n] == n * n])

idx = np.arange(N + 1, dtype=np.int64)
ge = (np.nonzero(F[1:] >= idx[1:])[0] + 1).tolist()
out("E_3 = {n <= 1e7 : F(n) >= n} =", ge)
out("fixed points:", [n for n in ge if F[n] == n])
out("ascents     :", [(n, int(F[n])) for n in ge if F[n] > n])
best = max(Fraction(int(F[n]), n) for n in ge)
out("max F(n)/n =", best, "at", [n for n in ge if Fraction(int(F[n]), n) == best])
out("3F(n) == ... F(n) = 3n/2 exactly at n =", (np.nonzero(2 * F[1:] == 3 * idx[1:])[0] + 1).tolist())

# attractors: iterate everything simultaneously
periodic = np.zeros(N + 1, dtype=bool)
# find periodic points honestly: n is periodic iff F^j(n) = n for some j >= 1 (test j <= 40)
per = []
for n in range(1, 2000):
    x = n
    for _ in range(40):
        x = int(F[x])
        if x == n:
            per.append(n)
            break
out("periodic points below 2000 (direct test F^j(n)=n, j<=40):", per)
# beyond E_3 every n has F(n) < n, so a periodic point's cycle minimum is in E_3: no others
periodic[per] = True
x = idx.copy()
x[0] = 1
trans = np.zeros(N + 1, dtype=np.int16)
for step in range(60):
    mask = ~periodic[x]
    if not mask.any():
        break
    trans += mask
    x = np.where(mask, F[x], x)
out("all n <= 1e7 reach a periodic point; steps needed:", step, " max transient:", int(trans[1:].max()))
# label by cycle minimum
lab = x.copy()
lab[lab == 9] = 6
for X in (10, 100, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    row = {a: int(np.count_nonzero(lab[1:X + 1] == a)) for a in (1, 3, 18, 36, 6)}
    out(f"  basins X={X:>9}: {row}  sum={sum(row.values())}")

# primes by tau == 2
primes = np.nonzero(tau == 2)[0]
out("pi(1e7) =", len(primes), "; basin(3) == primes:",
    bool(np.array_equal(np.nonzero(lab == 3)[0], primes)))
out("non-primes n with F(n) prime:", int(np.count_nonzero((tau[F[2:]] == 2) & (tau[2:] != 2))))

tmax = int(trans[1:].max())
dist = [int(np.count_nonzero(trans[1:] == t)) for t in range(tmax + 1)]
out("transient distribution t=0..:", dist, " mean:", float(trans[1:].mean()))
out("first n with each t:", [int(np.argmax(trans[1:] == t)) + 1 for t in range(tmax + 1)])
for a, nm in ((3, "3"), (18, "18"), (36, "36"), (6, "{6,9}")):
    sel = trans[1:][lab[1:] == a]
    out(f"  basin {nm}: " + ", ".join(f"t={t}:{int(np.count_nonzero(sel == t))}" for t in range(tmax + 1)))

pre36 = np.nonzero(F == 36)[0]
out("#n <= 1e7 with F(n)=36:", len(pre36), "; tau values among them (9 <-> p^2q^2, 8 <-> p^7):",
    {int(v): int(c) for v, c in zip(*np.unique(tau[pre36], return_counts=True))})
out("first preimages of 36:", pre36[:12].tolist())

# numerology control: how often is 'F(n) = m' achieved, for m near 36 (is 36 special as a VALUE?)
vals, cnts = np.unique(F[1:], return_counts=True)
d = dict(zip(vals.tolist(), cnts.tolist()))
out("number of n <= 1e7 with F(n) = m, m = 27..54:", {m: d.get(m, 0) for m in range(27, 55)})
out("values m <= 60 attained by F:", [m for m in range(1, 61) if m in d])
out(f"total {time.time()-t0:.1f}s")
LOG.close()
