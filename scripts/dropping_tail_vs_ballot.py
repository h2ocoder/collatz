"""Dropping-time tail (T-map steps, first value < n) vs the exact ballot model.

Model: P(drop time > K) = #{parity words of length K with 3^{s_j} >= 2^j for all j<=K} / 2^K.
For K <= log2 n this equals the empirical frequency exactly (Terras); beyond it, any
difference is the size–residue coupling with no endgame effects.
"""
import sys, math, numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
KMAX = 260
# exact DP: count words of length j, s ones, still not dropped
from collections import defaultdict
alive = {1: 1}  # after first step (must be odd): s=1
surv = [1.0, 1.0]  # P(no drop after 0,1 steps) for odd n
for j in range(2, KMAX + 1):
    nxt = defaultdict(int)
    for s, c in alive.items():
        for b in (0, 1):
            s2 = s + b
            if 3 ** s2 >= 2 ** j:   # still >= n in ratio sense
                nxt[s2] += c
    alive = nxt
    surv.append(sum(alive.values()) / 2 ** (j - 1))
surv = np.array(surv)
# empirical
ns = np.arange(N // 2 + 1, N + 1, 2, dtype=np.int64)
x = ns.copy(); L = np.zeros(len(ns), dtype=np.int64); active = np.ones(len(ns), bool)
k = 0
while active.any() and k < 5000:
    xa = x[active]; odd = (xa & 1) == 1
    x[active] = np.where(odd, (3 * xa + 1) // 2, xa >> 1); k += 1
    dropped = active & (x < ns); L[dropped] = k; active &= ~dropped
print(f"odd n in [{N//2},{N}] ({len(ns)}), log2 N = {math.log2(N):.1f}; T-map dropping time L")
print("| K | empirical P(L>K) | ballot model | ratio |"); print("|---|---|---|---|")
for K in (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120, 150, 200, 250):
    pe = np.mean(L > K); pm = surv[K]
    print(f"| {K} | {pe:.6f} | {pm:.6f} | {pe/pm if pm>0 else float('nan'):.3f} |")
print(f"max L = {L.max()}")
