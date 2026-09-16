"""VDF feasibility: the Collatz parity-vector map and its closed-form inverse.

Terras (1976): the first k Terras steps T(n) = n/2 (even) | (3n+1)/2 (odd) have a parity
vector v = (v_0..v_{k-1}) that depends only on n mod 2^k, and
    T^k(n) = (3^s n + r(v)) / 2^k,   s = #ones(v),   r(v) = sum_{i: v_i=1} 2^i 3^{#ones(v_{i+1..k-1})}.
Since T^k(n) is an integer, 3^s n + r(v) = 0 (mod 2^k), i.e.
    n = -r(v) * 3^{-s}  (mod 2^k)                                    (closed-form INVERSE)
and n mod 2^k -> v is a bijection of {0,1}^k (Terras).  So a verifier handed v can check that
it is n's parity vector with one modular product, while the only known way to produce v
from n is to iterate.  This script verifies the inverse formula, quantifies the built-in
time-memory tradeoff (a table of 2^p residues jumps p steps per lookup), and measures the
algebraic degree of the output bits as evidence about parallel depth.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/parity_vector_vdf.py
"""
import json
import random
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def parity_vector(n, k):
    """v_0..v_{k-1}: the sequential (evaluator's) computation."""
    v = []
    for _ in range(k):
        v.append(n & 1)
        n = terras(n)
    return v


def r_and_s(v):
    s = sum(v)
    r, pow3 = 0, 1  # pow3 = 3^{#ones after i}, accumulated from the top
    for i in range(len(v) - 1, -1, -1):
        if v[i]:
            r += pow3 << i
            pow3 *= 3
    return r, s


def inverse(v):
    """Closed form: the unique residue n mod 2^k with parity vector v (verifier's side)."""
    k = len(v)
    r, s = r_and_s(v)
    return (-r * pow(3, -s, 1 << k)) % (1 << k)


def check_vector(n, v):
    """Verifier: is v the parity vector of n?  One modular product, no iteration."""
    return inverse(v) == n % (1 << len(v))


if __name__ == "__main__":
    out = {}
    # 1. bijection + inverse formula, exhaustively for k <= 14 and randomly for k = 64, 256
    for k in (4, 8, 12, 14):
        vs = {tuple(parity_vector(n, k)) for n in range(1 << k)}
        ok_inv = all(inverse(parity_vector(n, k)) == n for n in range(1 << k))
        print(f"k={k:2d}: {len(vs)} distinct parity vectors of {1 << k} residues (bijection: {len(vs) == 1 << k}); inverse formula exact: {ok_inv}")
    rng = random.Random(28)
    for k in (64, 256, 1024):
        bad = 0
        for _ in range(200):
            n = rng.getrandbits(k + 40) | 1
            v = parity_vector(n, k)
            r, s = r_and_s(v)
            Tk = n
            for _ in range(k):
                Tk = terras(Tk)
            bad += (3**s * n + r) % (1 << k) != 0 or (3**s * n + r) >> k != Tk or not check_vector(n, v)
        # a wrong vector must be rejected
        v2 = list(v)
        v2[k // 2] ^= 1
        rej = not check_vector(n, v2)
        print(f"k={k:4d}: 200 random n, affine formula + inverse check: {200 - bad}/200 ok; flipped bit rejected: {rej}")
    out["inverse_verified_k"] = [4, 8, 12, 14, 64, 256, 1024]

    # 2. time-memory tradeoff: table of parity vectors for residues mod 2^p, jump p steps per lookup
    p = 12
    table = {n: parity_vector(n, p) for n in range(1 << p)}
    k = 240
    bad = 0
    for _ in range(100):
        n = rng.getrandbits(300) | 1
        v_seq = parity_vector(n, k)
        v_tab, x = [], n
        for _ in range(k // p):
            blk = table[x % (1 << p)]
            v_tab += blk
            r, s = r_and_s(blk)
            x = (3**s * x + r) >> p  # one affine op jumps p steps
        bad += v_tab != v_seq
    print(f"\ntable of 2^{p} residues: {k} steps in {k // p} lookups + {k // p} affine ops; mismatches vs sequential: {bad}/100")
    print("  => memory 2^p buys a p-fold reduction in sequential depth (2^32 table ~ 16 GB -> 32x; 2^40 ~ 5 TB -> 40x)")
    out["table_tradeoff"] = dict(p=p, k=k, mismatches=bad)

    # 3. algebraic degree of output bit v_j as a Boolean function of the k input bits (Mobius transform)
    k = 14
    N = 1 << k
    V = np.zeros((N, k), dtype=np.uint8)
    for n in range(N):
        V[n] = parity_vector(n, k)
    degs = []
    for j in range(k):
        f = V[:, j].copy()
        # Mobius transform over GF(2): f -> ANF coefficients
        h = 1
        while h < N:
            for i in range(0, N, 2 * h):
                f[i + h:i + 2 * h] ^= f[i:i + h]
            h <<= 1
        monos = np.nonzero(f)[0]
        deg = max(bin(m).count("1") for m in monos) if len(monos) else 0
        # how many input bits does v_j depend on (should be j+1: bits 0..j)
        support = sorted({b for m in monos for b in range(k) if m >> b & 1})
        degs.append((j, deg, len(monos), (min(support), max(support)) if support else None))
    print(f"\nANF of v_j over the {k} input bits (degree, #monomials, input-bit range):")
    for j, d, nm, rngb in degs:
        print(f"  v_{j:2d}: degree {d:2d}, monomials {nm:5d}, depends on bits {rngb}")
    out["anf"] = [dict(j=j, degree=d, monomials=nm) for j, d, nm, _ in degs]

    # 4. same for the inverse map: bit j of n = inverse(v) as a function of v
    B = np.zeros((N, k), dtype=np.uint8)
    for code in range(N):
        v = [(code >> i) & 1 for i in range(k)]
        n = inverse(v)
        B[code] = [(n >> i) & 1 for i in range(k)]
    idegs = []
    for j in range(k):
        f = B[:, j].copy()
        h = 1
        while h < N:
            for i in range(0, N, 2 * h):
                f[i + h:i + 2 * h] ^= f[i:i + h]
            h <<= 1
        monos = np.nonzero(f)[0]
        deg = max(bin(m).count("1") for m in monos) if len(monos) else 0
        idegs.append((j, deg, len(monos)))
    print(f"\nANF of inverse: bit n_j as a function of v (degree, #monomials):")
    print("  " + ", ".join(f"n_{j}: {d}/{nm}" for j, d, nm in idegs))
    out["anf_inverse"] = [dict(j=j, degree=d, monomials=nm) for j, d, nm in idegs]

    # 5. timing: evaluator vs verifier at k = 20000 on a big n
    k = 20000
    n = rng.getrandbits(k + 100) | 1
    t0 = time.time()
    v = parity_vector(n, k)
    t_eval = time.time() - t0
    t0 = time.time()
    ok = check_vector(n, v)
    t_ver = time.time() - t0
    print(f"\nk={k}: evaluator (iterate) {t_eval:.3f}s; verifier (one modular product) {t_ver:.3f}s; ok={ok}; ratio {t_eval / t_ver:.1f}x (single thread, Python bigints)")
    out["timing"] = dict(k=k, t_eval=t_eval, t_verify=t_ver)
    json.dump(out, open(RESULTS / "parity_vector_vdf.json", "w"), indent=1)
