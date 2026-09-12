"""Total stopping time vs the Lagarias–Weiss random-walk model, at fixed size.

Empirical: odd n in [N/2, N], standard-step total stopping time T(n), hardness H = T/log2 n.
Model: parity bits i.i.d. fair; odd step: log-size += log2 3 - 1, steps += 2; even: -= 1,
steps += 1; start at log2 n (uniform in the same bit range); stop when log-size <= 0.
The difference between the two tails is the size–residue coupling, isolated.
"""
import sys, math, numpy as np
sys.path.insert(0, 'scripts')
from prime_factorization_dropping import orbit_stats
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
rng = np.random.default_rng(11)
ns = np.arange(N // 2 + 1, N + 1, 2, dtype=np.int64)
_, tst, _, _ = orbit_stats(ns)
H = tst / np.log2(ns.astype(float))
# model
M = len(ns)
size = np.log2(rng.uniform(N / 2, N, M)); steps = np.zeros(M); active = size > 0
a = math.log2(3) - 1
while active.any():
    odd = rng.random(active.sum()) < 0.5
    idx = np.nonzero(active)[0]
    size[idx] += np.where(odd, a, -1.0); steps[idx] += np.where(odd, 2, 1)
    active[idx] = size[idx] > 0
Hm = steps / np.log2(rng.uniform(N / 2, N, M))  # same size distribution
qs = [0.5, 0.9, 0.99, 0.999, 0.9999]
print(f"odd n in [{N//2},{N}]: {M} numbers.  Hardness H = total steps / log2 n")
print("| quantile | empirical | LW model |"); print("|---|---|---|")
for q in qs: print(f"| {q} | {np.quantile(H,q):.3f} | {np.quantile(Hm,q):.3f} |")
print(f"| max | {H.max():.3f} | {Hm.max():.3f} |")
print(f"| mean | {H.mean():.4f} | {Hm.mean():.4f} |")
for h in (12, 15, 18, 21):
    pe, pm = np.mean(H > h), np.mean(Hm > h)
    print(f"P(H>{h}): empirical {pe:.5f}  model {pm:.5f}  ratio {pe/pm if pm else float('nan'):.2f}")
print(f"Lagarias–Weiss predicted limsup H = 41.677 ln2 = {41.677*math.log(2):.2f} steps/bit")
