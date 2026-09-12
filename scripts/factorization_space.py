"""Collatz drops in prime-exponent space.

Represent n by its exponent vector v(n) = (v_p(n))_p in the space spanned by primes.
For each odd n, the 'up' vector goes to 3n+1 and the 'down' vector to dest(n) (first
value < n).  Exact facts:  <v(n), v(3n+1)> = 0;  gcd(n, dest) | C_w where C_w is the
constant of n's dropping word;  v_3(dest) = 0.

Experiments (odd n <= N):
  A. verify gcd(n, dest) | C_w for every n; per class, compare the observed fraction of
     n with gcd > 1 against the prediction from the primes of C_w.
  B. cosine between v(n) and v(dest) vs. a size-matched random control.
  C. omega(dest) and omega(3n+1) vs. Erdos-Kac (random integers of the same size).
  D. correlation of omega(n) with omega(dest(n)) vs. random pairs.
"""
from __future__ import annotations

import math
import sys
from collections import defaultdict
from math import gcd

import numpy as np
from sympy import factorint

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000
RNG = np.random.default_rng(1)


def spf_sieve(n):
    spf = np.zeros(n + 1, dtype=np.int64)
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i::i][spf[i::i] == 0] = i
    return spf


def factor(m, spf):
    f = {}
    while m > 1:
        p = int(spf[m]); e = 0
        while m % p == 0:
            m //= p; e += 1
        f[p] = e
    return f


def drop_word(n):
    x = n; L = 0; s = 0; c = 0
    while True:
        if x % 2:
            x = (3 * x + 1) // 2; s += 1; c = 3 * c + (1 << L)
        else:
            x //= 2
        L += 1
        if x < n:
            return L, s, c, x


def omega(f):
    return len(f)


def cosine(f, g):
    dot = sum(e * g[p] for p, e in f.items() if p in g)
    na = math.sqrt(sum(e * e for e in f.values())); nb = math.sqrt(sum(e * e for e in g.values()))
    return dot / (na * nb) if na and nb else 0.0


spf = spf_sieve(3 * N + 2)
ns = np.arange(3, N + 1, 2)

# ---- A: gcd(n, dest) | C_w, and class-level prediction
viol = 0
by_class = defaultdict(lambda: [0, 0, None])   # (L,s,C) -> [count, count gcd>1, primes of C]
cos_nd = []; cos_ctrl = []; om_dest = []; om_up = []; om_n = []; om_rand = []
for n in ns.tolist():
    L, s, C, d = drop_word(n)
    g = gcd(n, d)
    if C % g != 0:
        viol += 1
    key = (L, s, C)
    cell = by_class[key]
    cell[0] += 1; cell[1] += (g > 1)
    if cell[2] is None:
        cell[2] = [p for p in factorint(C) if p > 2] if C > 1 else []
    fn = factor(n, spf); fd = factor(d, spf) if d > 1 else {}
    cos_nd.append(cosine(fn, fd))
    m = int(RNG.integers(2, max(3, d + 1)))
    cos_ctrl.append(cosine(fn, factor(m, spf)))
    om_n.append(omega(fn)); om_dest.append(omega(fd)); om_up.append(omega(factor(3 * n + 1, spf)))
    om_rand.append(omega(factor(m, spf)))

print(f"odd n <= {N}: violations of gcd(n,dest) | C_w: {viol}")
print("\nA. classes with >= 2000 members: observed P(gcd(n,dest)>1) vs prediction 1-prod(1-1/p) over odd p | C_w")
print("| (L,s) | C_w | odd primes of C_w | members | observed | predicted |")
print("|---|---|---|---:|---:|---:|")
for key, (cnt, hit, ps) in sorted(by_class.items(), key=lambda kv: -kv[1][0])[:10]:
    pred = 1 - math.prod(1 - 1 / p for p in ps) if ps else 0.0
    print(f"| ({key[0]},{key[1]}) | {key[2]} | {ps} | {cnt} | {hit/cnt:.4f} | {pred:.4f} |")

cos_nd = np.array(cos_nd); cos_ctrl = np.array(cos_ctrl)
print(f"\nB. cosine(v(n), v(dest)): mean {cos_nd.mean():.4f}, P(>0) {np.mean(cos_nd>0):.4f};"
      f"  size-matched random control: mean {cos_ctrl.mean():.4f}, P(>0) {np.mean(cos_ctrl>0):.4f}")

om_dest = np.array(om_dest); om_up = np.array(om_up); om_n = np.array(om_n); om_rand = np.array(om_rand)
print(f"\nC. omega: n {om_n.mean():.4f} | dest {om_dest.mean():.4f} | random of dest's size {om_rand.mean():.4f} | 3n+1 {om_up.mean():.4f}"
      f" | Erdos-Kac loglog(N/2) = {math.log(math.log(N/2)):.4f}")
print(f"   omega(dest) distribution: " + ", ".join(f"{k}: {np.mean(om_dest==k):.3f}" for k in range(0, 6)))
print(f"   omega(rand) distribution: " + ", ".join(f"{k}: {np.mean(om_rand==k):.3f}" for k in range(0, 6)))
print(f"\nD. corr(omega(n), omega(dest)) = {np.corrcoef(om_n, om_dest)[0,1]:+.4f};  corr(omega(n), omega(random)) = {np.corrcoef(om_n, om_rand)[0,1]:+.4f};"
      f"  corr(omega(n), omega(3n+1)) = {np.corrcoef(om_n, om_up)[0,1]:+.4f}")
