"""How close does n sit to the periodic point of its own dropping word?

For odd n with dropping T-word w = (L, s, C_w):  dest = r n + C_w/2^L,  r = 3^s/2^L < 1.
The line crosses the diagonal at the rational periodic point  x_w = C_w / (2^L - 3^s),
and n drops iff n > x_w.  Define  rho(n) = n / x_w  (> 1).  Exact identity:

        dest / n  =  r + (1 - r) / rho(n)

so sigma = 1/rho is the fraction of the class's promised contraction that n fails to
achieve; sigma -> 1 would be a cycle.

Experiments (odd n <= N):
  1. distribution of sigma; the near-miss champions (largest sigma, i.e. n nearest a
     periodic point) and their words.
  2. sigma for the classical hard numbers and for the record-setters of T(n)/log2 n.
  3. does sigma predict hardness (total stopping time / log2 n, number of drops)
     beyond the dropping word?  Correlations overall, within fixed (L,s), and along the
     whole drop chain (mean sigma of the chain, size-controlled).
"""
from __future__ import annotations

import math
import sys
from collections import defaultdict
from fractions import Fraction

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from prime_factorization_dropping import orbit_stats  # vectorised total stopping time etc.

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000


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


def sigma_of(n):
    """(sigma, L, s, dest) for odd n.  sigma = x_w / n = C / (n (2^L - 3^s))."""
    L, s, C, d = drop_word(n)
    return C / (n * ((1 << L) - 3 ** s)), L, s, d


ns = np.arange(3, N + 1, 2, dtype=np.int64)
dt, tst, lpk, nd = orbit_stats(ns)
lg = np.log2(ns.astype(float))
hard = tst / lg                      # total stopping time per bit
sig = np.empty(len(ns)); Ls = np.empty(len(ns), dtype=np.int64); Ss = np.empty(len(ns), dtype=np.int64)
dests = np.empty(len(ns), dtype=np.int64)
for i, n in enumerate(ns.tolist()):
    sig[i], Ls[i], Ss[i], dests[i] = sigma_of(n)

print(f"odd n <= {N}: {len(ns)} numbers")
q = np.quantile(sig, [0.5, 0.9, 0.99, 0.999, 1.0])
print(f"\n1. sigma = 1/rho quantiles: median {q[0]:.4f}, 90% {q[1]:.4f}, 99% {q[2]:.4f}, 99.9% {q[3]:.4f}, max {q[4]:.4f}")
idx = np.argsort(-sig)[:12]
print("   near-miss champions (n nearest its word's periodic point):")
print("   | n | sigma | (L,s) | dest/n | word contraction r | total steps/bit |")
print("   |---|---|---|---|---|---|")
for i in idx:
    n = int(ns[i]); r = 3 ** int(Ss[i]) / 2 ** int(Ls[i])
    print(f"   | {n} | {sig[i]:.4f} | ({Ls[i]},{Ss[i]}) | {dests[i]/n:.4f} | {r:.4f} | {hard[i]:.2f} |")

# 2. classical hard numbers and record setters of hardness
print("\n2. sigma for record-setters of total steps / log2 n (records among odd n):")
print("   | n | total steps/bit | sigma (first drop) | (L,s) | mean sigma along drop chain | drops |")
print("   |---|---|---|---|---|---|")
best = -1
sig_lookup = {int(n): float(s) for n, s in zip(ns.tolist(), sig)}
def chain_sigmas(n):
    out = []
    while n > 1:
        if n % 2 == 0:
            n //= 2; continue
        s, L, S, d = sigma_of(n); out.append(s); n = d
    return out
for i in range(len(ns)):
    if hard[i] > best and ns[i] > 100:
        best = hard[i]; n = int(ns[i]); cs = chain_sigmas(n)
        print(f"   | {n} | {hard[i]:.2f} | {sig[i]:.4f} | ({Ls[i]},{Ss[i]}) | {np.mean(cs):.4f} | {len(cs)} |")
for n in (27, 31, 41, 47, 63, 71, 97, 703, 871, 6171, 77031):
    if n <= N:
        i = (n - 3) // 2; cs = chain_sigmas(n)
        print(f"   classic {n}: steps/bit {hard[i]:.2f}, sigma {sig[i]:.4f}, ({Ls[i]},{Ss[i]}), chain mean sigma {np.mean(cs):.4f}, drops {len(cs)}")

# 3. predictive power
print("\n3. does sigma predict hardness?")
print(f"   corr(sigma, total steps/bit) = {np.corrcoef(sig, hard)[0,1]:+.4f}")
print(f"   corr(log dropping time, total steps/bit) = {np.corrcoef(np.log(dt), hard)[0,1]:+.4f}")
# partial: within fixed (L,s) classes with >= 500 members
cls = defaultdict(list)
for i in range(len(ns)):
    cls[(int(Ls[i]), int(Ss[i]))].append(i)
ws = []; cs_ = []
for key, ii in cls.items():
    if len(ii) >= 500:
        ii = np.array(ii); c = np.corrcoef(sig[ii], hard[ii])[0, 1]
        ws.append(len(ii)); cs_.append(c)
print(f"   within-class corr(sigma, hardness), weighted mean over {len(ws)} classes = {np.average(cs_, weights=ws):+.4f}")
# hardness of top-decile sigma vs rest, matched on dropping time
top = sig >= np.quantile(sig, 0.9)
by_k_top = defaultdict(list); by_k_rest = defaultdict(list)
for i in range(len(ns)):
    (by_k_top if top[i] else by_k_rest)[int(dt[i])].append(hard[i])
num = 0.0; den = 0
for k in by_k_top:
    if k in by_k_rest and len(by_k_top[k]) >= 50:
        num += (np.mean(by_k_top[k]) - np.mean(by_k_rest[k])) * len(by_k_top[k]); den += len(by_k_top[k])
print(f"   top-decile sigma vs rest, matched on dropping time: mean hardness difference = {num/den:+.4f} steps/bit (overall mean hardness {hard.mean():.3f})")
# chain-level: mean sigma along chain vs hardness, controlling for size by dyadic bins
rng = np.random.default_rng(3)
sample = rng.choice(len(ns), 40000, replace=False)
cm = np.array([np.mean(chain_sigmas(int(ns[i]))) for i in sample])
print(f"   corr(mean sigma along drop chain, total steps/bit) on 40k sample = {np.corrcoef(cm, hard[sample])[0,1]:+.4f}")
print(f"   corr(mean sigma along drop chain, number of drops / bit) = {np.corrcoef(cm, nd[sample]/lg[sample])[0,1]:+.4f}")
