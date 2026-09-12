"""Mechanism of the geometric law 2 - lambda_k ~ rho^k in the Krasikov–Lagarias system.

Hypothesis: the min over the three lifts of the unknown top 3-adic digit costs a fluctuation
of the weight at odd generation k; CLT => relative spread ~ mu^{-k/2}, mu = growth of weight
per odd generation of the annealed (lambda = 2) operator.  Predicts rho = mu^{-1/2}.

Tests:
  1. mu = Perron root of the generation-transfer operator G = (I - D)^{-1} O on classes mod 3^j
     (D: double-doubling m -> 4m, weight 1/4; O: odd routes, weights 3/4 and 3/2), for j = 2..7.
  2. digit influence: for the saved eigenvector at level k, V_j = mean relative change of c when
     3-adic digit j (0 = bottom) is changed, j = 0..k-1.  Predicts V_j ~ rho^j at the top digits.
  3. spread among lifts of the top digit vs k, i.e. mean (max-min)/mean over classes at level k-1.
"""
import math, sys
import numpy as np

ALPHA = math.log2(3)

def generation_operator_root(j, lam=2.0):
    N = 3 ** j
    P = np.arange(2, N, 3)                      # principal classes
    idx = {int(m): i for i, m in enumerate(P)}
    n = len(P)
    D = np.zeros((n, n)); O = np.zeros((n, n))
    a4 = lam ** -2; a2 = lam ** (ALPHA - 2); a8 = lam ** (ALPHA - 1)
    for i, m in enumerate(P):
        m = int(m)
        D[i, idx[(4 * m) % N]] += a4
        if m % 9 == 2:
            t = ((4 * m - 2) % N) // 3            # class mod 3^(j-1); spread uniformly over its 3 lifts (annealed)
            for l in range(3):
                O[i, idx[(t + l * 3 ** (j - 1)) % N]] += a2 / 3
        elif m % 9 == 8:
            t = ((2 * m - 1) % N) // 3
            for l in range(3):
                O[i, idx[(t + l * 3 ** (j - 1)) % N]] += a8 / 3
    G = np.linalg.solve(np.eye(n) - D, O)         # weight reaching the next odd generation
    ev = np.linalg.eigvals(G)
    A = D + O
    return max(abs(ev)), max(abs(np.linalg.eigvals(A)))

print("1. annealed operator at λ=2: per-odd-generation growth μ and per-step Perron root")
print("| j (digits) | μ | μ^(-1/2) | Perron root of D+O |"); print("|---|---|---|---|")
for j in range(2, 8):
    mu, r = generation_operator_root(j)
    print(f"| {j} | {mu:.5f} | {mu**-0.5:.5f} | {r:.5f} |")

print("\n2. digit influence V_j on the level-k eigenvector (relative mean |Δc| when digit j changes)")
rows = {}
for k in range(11, 18):
    try:
        c = np.load(f"data/kl_eigvec_k{k}.npy").astype(np.float64)
    except FileNotFoundError:
        continue
    N = 3 ** k
    P = np.arange(2, N, 3, dtype=np.int64)
    cP = c[P]; mean = cP.mean()
    V = []
    for j in range(1, k):                       # digit 0 fixed (=2) for principal classes
        step = 3 ** j
        m2 = (P + step) % N                     # digit j -> digit j + 1 (mod 3)
        V.append(np.mean(np.abs(c[m2] - cP)) / mean)
    rows[k] = V
    print(f"k={k}: " + " ".join(f"{v:.4f}" for v in V))
print("\n   ratios V_j/V_(j-1) for k=16:", " ".join(f"{rows[16][j]/rows[16][j-1]:.3f}" for j in range(1, len(rows[16]))) if 16 in rows else "")

print("\n3. spread among the 3 lifts of the top digit, (max-min)/mean over classes at level k-1, vs 2-λ_k")
lam = {11:1.792231,12:1.806424,13:1.818824,14:1.830772,15:1.841968,16:1.852235,17:1.861689}
for k in range(11, 18):
    try:
        c = np.load(f"data/kl_eigvec_k{k}.npy").astype(np.float64)
    except FileNotFoundError:
        continue
    N = 3 ** k; Nk1 = N // 3
    C = c.reshape(3, Nk1)
    T = np.arange(2, Nk1, 3)
    sub = C[:, T]
    spread = np.mean((sub.max(0) - sub.min(0)) / sub.mean(0))
    print(f"k={k}: spread {spread:.5f}   2-λ_k {2-lam[k]:.5f}   ratio {(2-lam[k])/spread:.3f}")
