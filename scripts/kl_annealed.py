"""Annealed (mean-over-lifts) KL system: the object behind lambda_k -> 2.

(1) mu_2 = Perron root of the squared-weight generation operator (predicts rho = sqrt(mu_2)
    if the lift-spread is a CLT fluctuation).
(2) The annealed eigenvector at lambda = 2 for k = 2..KMAX; its relative spread across the
    three lifts of the top digit (mean and max over classes) as a function of k.
(3) Reduction check: with the annealed eigenvector c_k at level k, the largest lambda for
    which c_k <= M_min,lambda c_k holds (a feasible certificate built from the annealed vector),
    compared with lambda_k.
"""
import math, sys
import numpy as np
ALPHA = math.log2(3)
KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 14

def squared_generation_root(j):
    N = 3 ** j; P = np.arange(2, N, 3); idx = {int(m): i for i, m in enumerate(P)}; n = len(P)
    D = np.zeros((n, n)); O = np.zeros((n, n))
    for i, m in enumerate(P):
        m = int(m); D[i, idx[(4 * m) % N]] += 0.25 ** 2
        if m % 9 == 2:
            t = ((4 * m - 2) % N) // 3
            for l in range(3): O[i, idx[(t + l * 3 ** (j - 1)) % N]] += (0.75 ** 2) / 3
        elif m % 9 == 8:
            t = ((2 * m - 1) % N) // 3
            for l in range(3): O[i, idx[(t + l * 3 ** (j - 1)) % N]] += (1.5 ** 2) / 3
    G = np.linalg.solve(np.eye(n) - D, O)
    return max(abs(np.linalg.eigvals(G)))

print("1. squared-weight generation operator: mu_2 and sqrt(mu_2)")
for j in range(2, 8):
    mu2 = squared_generation_root(j); print(f"   j={j}: mu_2={mu2:.5f}  sqrt={math.sqrt(mu2):.5f}")

def annealed_system(k, lam):
    N = 3 ** k; Nk1 = N // 3
    P = np.arange(2, N, 3, dtype=np.int64)
    idx4 = ((4 * P) % N).astype(np.int32)
    is2 = P % 9 == 2; is8 = P % 9 == 8
    t2 = (((4 * P[is2] - 2) % N) // 3).astype(np.int32); t8 = (((2 * P[is8] - 1) % N) // 3).astype(np.int32)
    pos2 = np.nonzero(is2)[0]; pos8 = np.nonzero(is8)[0]; Pi = P.astype(np.int32)
    a4 = lam ** -2; a2 = lam ** (ALPHA - 2); a8 = lam ** (ALPHA - 1)
    def apply(c, use_min=False):
        C = c.reshape(3, Nk1)
        d = C.min(axis=0) if use_min else C.mean(axis=0)
        out = np.zeros(N); vals = a4 * c[idx4]
        vals[pos2] += a2 * d[t2]; vals[pos8] += a8 * d[t8]
        out[Pi] = vals; return out
    return apply, N, Pi

def power(apply, N, iters=3000, tol=1e-12, **kw):
    c = np.ones(N); r = 1
    for it in range(iters):
        Mc = apply(c, **kw); nrm = Mc.max(); rn = nrm / c.max(); c = Mc / nrm
        if it > 50 and abs(rn - r) < tol: r = rn; break
        r = rn
    return r, c

print("\n2. annealed eigenvector at λ=2: Perron root, relative top-digit spread (mean, max over classes)")
print("| k | root | mean spread | max spread | mean/prev | max/prev |"); print("|---|---|---|---|---|---|")
prev = None; vecs = {}
for k in range(2, KMAX + 1):
    apply, N, Pi = annealed_system(k, 2.0)
    r, c = power(apply, N); vecs[k] = c
    Nk1 = N // 3; C = c.reshape(3, Nk1); T = np.arange(2, Nk1, 3); sub = C[:, T]
    sp = (sub.max(0) - sub.min(0)) / sub.mean(0)
    ms, xs = sp.mean(), sp.max()
    print(f"| {k} | {r:.6f} | {ms:.5f} | {xs:.5f} | {'' if prev is None else f'{ms/prev[0]:.3f}'} | {'' if prev is None else f'{xs/prev[1]:.3f}'} |")
    prev = (ms, xs)

print("\n3. reduction: largest λ with c_ann(λ) <= M_min,λ c_ann(λ)  (feasible certificate from the annealed vector) vs λ_k")
lamk = {2:1.353400,3:1.527679,4:1.612287,5:1.662760,6:1.694452,7:1.720191,8:1.744963,9:1.761532,10:1.777126,11:1.792231,12:1.806424,13:1.818824,14:1.830772}
for k in range(4, KMAX + 1):
    lo, hi = 1.0, 2.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        apply, N, Pi = annealed_system(k, mid)
        r, c = power(apply, N, iters=1500, tol=1e-11)
        Mc = apply(c, use_min=True)
        if np.all(Mc[Pi] >= c[Pi] * (1 - 1e-9)): lo = mid
        else: hi = mid
    print(f"   k={k}: annealed-certificate λ = {lo:.6f} (γ={math.log2(lo):.5f})   true λ_k = {lamk.get(k, float('nan')):.6f}   gap ratio (2-λ_cert)/(2-λ_k) = {(2-lo)/(2-lamk[k]):.3f}")
