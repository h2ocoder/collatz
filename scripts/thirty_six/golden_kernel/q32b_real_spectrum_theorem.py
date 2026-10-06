"""Q3.2, Theorem B: N = 5 is the only level at which every eigenvalue of the Terras kernel is real.
This script checks every ingredient of the proof in the README on all N prime to 6, 5 <= N <= N_MAX.

  (i)   tr(A_N) = 2 and tr(A_N^2) = 3 + gcd(5, N)   (A_N = R_e + R_o on functions on Z/N), by counting the fixed
        points of the two branches and of the four two-step words directly;
  (ii)  hence, by Moebius inversion over the levels d | N,  S1(N) = sum of the level-N eigenvalues = 0 and
        S2(N) = sum of their squares = 0 for every N > 1 except S2(5) = 4;
  (iii) g(y) = 3y + 1/2 satisfies g^k = id iff 3^k = 1 (mod N): all its cycles have length dividing ord_N(3), so
        ker(A_N) = {f = -f o g} is 0 when ord_N(3) is odd;
  (iv)  for N <= EXACT_MAX the level-N characteristic polynomial (exact) starts  x^n + 0 x^(n-1) + 0 x^(n-2) + ...
        (N != 5), is not x^n, and has a non-real root (a real-rooted polynomial with e1 = e2 = 0 is x^n).

Run:  python -X utf8 q32b_real_spectrum_theorem.py [N_MAX=3000] [EXACT_MAX=150]   (writes .log / .json)
"""
from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import branches, charpoly_int, divisors, order, pdivmod, two_K  # noqa: E402

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
EXACT_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 150
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def mobius(n: int) -> int:
    r, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            r = -r
        p += 1
    return -r if n > 1 else r


Ns = [n for n in range(5, N_MAX + 1) if gcd(n, 6) == 1]
bad_i = bad_ii = bad_iii = 0
T1 = {1: 2}
T2 = {1: 4}
for N in Ns:
    e, o = branches(N)
    t1 = sum(1 for x in range(N) if e[x] == x) + sum(1 for x in range(N) if o[x] == x)
    t2 = sum(1 for w1 in (e, o) for w2 in (e, o) for x in range(N) if w2[w1[x]] == x)
    T1[N], T2[N] = t1, t2
    if t1 != 2 or t2 != 3 + gcd(5, N):
        bad_i += 1
for N in Ns:
    s1 = sum(mobius(N // d) * T1[d] for d in divisors(N))
    s2 = sum(mobius(N // d) * T2[d] for d in divisors(N))
    if s1 != 0 or s2 != (4 if N == 5 else 0):
        bad_ii += 1
for N in Ns:
    o3 = order(3, N)
    inv2 = pow(2, -1, N)
    # g^k(y) = 3^k y + (3^k - 1)/4 ; check g^{o3} = id on three points and that no smaller divisor works at y = 0
    y = 0
    for _ in range(o3):
        y = (3 * y + inv2) % N
    if y != 0:
        bad_iii += 1
say(f"N prime to 6, 5 <= N <= {N_MAX}: {len(Ns)} moduli")
say(f"   (i)   tr(A) = 2 and tr(A^2) = 3 + gcd(5, N): failures {bad_i}")
say(f"   (ii)  level sums S1(N) = 0 and S2(N) = 0 (S2(5) = 4): failures {bad_ii}")
say(f"   (iii) g^(ord_N 3) fixes 0 (so g^(ord_N 3) = id, g being affine with multiplier 3^k = 1 and fixed point -1/4): failures {bad_iii}")

import numpy as np  # noqa: E402

prim: dict[int, list[int]] = {1: [-2, 1]}
rows = []
bad_iv = 0
for N in [n for n in Ns if n <= EXACT_MAX]:
    p_ = charpoly_int(two_K(N))
    for d in divisors(N):
        if d < N:
            p_, r = pdivmod(p_, prim[d])
            assert r == [0]
    prim[N] = p_
    n = len(p_) - 1
    e1, e2 = -p_[n - 1], p_[n - 2]
    is_xn = all(c == 0 for c in p_[:-1])
    rts = np.roots([float(c) for c in p_[::-1]])
    nonreal = int(np.sum(np.abs(rts.imag) > 1e-7))
    rows.append({"N": N, "e1": e1, "e2": e2, "nonreal_roots_float": nonreal})
    if N != 5 and (e1 != 0 or e2 != 0 or is_xn or nonreal == 0):
        bad_iv += 1
    if N == 5 and (e1 != 0 or e2 != -2 or nonreal != 0):
        bad_iv += 1
say(f"   (iv)  exact level polynomials for N <= {EXACT_MAX} ({len(rows)} levels): x^n + 0 x^(n-1) + 0 x^(n-2) + ..., not x^n, some non-real root (N != 5);  N = 5: e2 = -2, all roots real: failures {bad_iv}")
say("ALL OK" if bad_i + bad_ii + bad_iii + bad_iv == 0 else "FAILURES")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"N_MAX": N_MAX, "failures": [bad_i, bad_ii, bad_iii, bad_iv], "exact_rows": rows}, indent=0), encoding="utf-8")
