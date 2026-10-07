"""Skeptic check 2: independent Kronecker census of the Terras kernel mod N (Theorems B, C, Prop. E, census G).

Different code path from gk_common.py / q32_kronecker_census.py:
  * characteristic polynomial from the power sums tr(A^k), k = 1..N (column gathers, no linear algebra),
    Newton's identities modulo 62-bit primes, CRT with the bound |coef| <= 3^N;
  * Psi_j built from the cyclotomic polynomial: Phi_j(z) = z^h Psi_j(z + 1/z), expanded in the polynomials
    C_k(x) (z^k + z^-k = C_k(z + 1/z)); the researcher used C_m - 2 = prod Psi_d^e and a polynomial square root;
  * candidate j, k: ALL with deg <= phi(N), bound found by sieving Euler phi up to 2*(2*deg)^2 (rigorous since
    phi(n) >= sqrt(n/2)); filter = evaluation at a root modulo one prime r = 1 (mod j) (sound for absence);
    survivors decided by exact division over Z.
At the end the rows are compared with the researcher's q32_kronecker_census.json.

CONVENTION: shortcut map; A = 2K_N = R_e + R_o, e(x) = x/2, o(x) = (q x + 1)/2 on Z/N, gcd(N, 2q) = 1.
Run:  python -X utf8 v2_census.py [N_MAX=400] [q=3]
"""
from __future__ import annotations

import json
import sys
import time
from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 400
Q = int(sys.argv[2]) if len(sys.argv) > 2 else 3
N_MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 3        # levels below N_MIN are computed only when needed as divisors
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


# ---------------------------------------------------------------- big primes for the CRT
BIG = []
_r = 2 ** 62
while len(BIG) < 14:
    _r = sp.prevprime(_r)
    BIG.append(int(_r))


def charpoly_newton(N: int, q: int) -> list[int]:
    """coefficients c[k] of x^k of det(x - A_N), exact."""
    inv2 = (N + 1) // 2
    e = [(xx * inv2) % N for xx in range(N)]
    o = [((q * xx + 1) * inv2) % N for xx in range(N)]
    einv = np.zeros(N, dtype=np.int64)
    oinv = np.zeros(N, dtype=np.int64)
    for xx in range(N):
        einv[e[xx]] = xx
        oinv[o[xx]] = xx
    need = 2 * 3 ** N + 1
    mods, res, prod = [], [], 1
    for r in BIG:
        M = np.eye(N, dtype=np.int64)
        tr = [0] * (N + 1)
        for k in range(1, N + 1):
            M = M[:, einv] + M[:, oinv]            # M <- M A   (entries < 2^63)
            M -= r * (M >= r)
            tr[k] = sum(int(v) for v in M.diagonal()) % r     # Python ints: the int64 trace would overflow
        el = [1] + [0] * N                          # elementary symmetric functions
        for k in range(1, N + 1):
            s = 0
            for i in range(1, k + 1):
                term = el[k - i] * tr[i]
                s += term if i % 2 else -term
            el[k] = s % r * pow(k, -1, r) % r
        res.append([(el[N - k] if (N - k) % 2 == 0 else -el[N - k]) % r for k in range(N + 1)])
        mods.append(r)
        prod *= r
        if prod > need:
            break
    else:
        raise RuntimeError("not enough moduli")
    out = [0] * (N + 1)
    Mm = 1
    for rr, m in zip(res, mods):
        inv = pow(Mm % m, -1, m)
        for i in range(N + 1):
            out[i] += Mm * (((rr[i] - out[i]) * inv) % m)
        Mm *= m
    return [c - Mm if c > Mm // 2 else c for c in out]


def pdivmod(a: list[int], b: list[int]):
    a = list(a)
    db = len(b) - 1
    assert b[-1] == 1
    if len(a) - 1 < db:
        return [0], a
    qq = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            qq[i - db] = c
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    rem = a[:db] if db else [0]
    return qq, rem


def mult_of(b, a):
    k = 0
    while len(a) >= len(b):
        qq, rem = pdivmod(a, b)
        if any(rem):
            break
        a, k = qq, k + 1
    return k, a


# ---------------------------------------------------------------- Euler phi sieve and candidate lists
MAXDEG = N_MAX
CAP = 2 * (2 * MAXDEG) ** 2 + 16
ph = np.arange(CAP + 1, dtype=np.int64)
for i in range(2, CAP + 1):
    if ph[i] == i:
        ph[i::i] -= ph[i::i] // i
J_ALL = [int(j) for j in np.nonzero(ph[1:] <= 2 * MAXDEG)[0] + 1]      # phi(j) <= 2*deg: all Psi_j of degree <= deg
say(f"candidates: all j with phi(j) <= {2 * MAXDEG}: {len(J_ALL)} values, largest j = {max(J_ALL)} (sieve to {CAP})")

_x = sp.symbols("x")
_psi: dict[int, list[int]] = {}
_phi: dict[int, list[int]] = {}


def Phi(k: int) -> list[int]:
    if k not in _phi:
        _phi[k] = [int(c) for c in sp.Poly(sp.cyclotomic_poly(k, _x), _x).all_coeffs()[::-1]]
    return _phi[k]


def Psi(j: int) -> list[int]:
    """minimal polynomial of 2cos(2 pi/j)."""
    if j in _psi:
        return _psi[j]
    if j == 1:
        r = [-2, 1]
    elif j == 2:
        r = [2, 1]
    else:
        f = Phi(j)
        h = (len(f) - 1) // 2
        # Phi_j(z)/z^h = f[h] + sum_{k>=1} f[h+k] (z^k + z^-k)
        Ck_prev, Ck = [2], [0, 1]
        r = [f[h]] + [0] * h
        for k in range(1, h + 1):
            for i, c in enumerate(Ck):
                r[i] += f[h + k] * c
            nxt = [0] + Ck
            for i, c in enumerate(Ck_prev):
                nxt[i] -= c
            Ck_prev, Ck = Ck, nxt
        assert r[-1] == 1
    _psi[j] = r
    return r


def prime_factors(n: int) -> list[int]:
    return [int(p) for p in sp.factorint(n)]


_root: dict[int, tuple[int, int]] = {}


def root_data(j: int) -> tuple[int, int]:
    """(r, z): prime r = 1 (mod j), r > 2^24, and z of exact order j modulo r."""
    if j not in _root:
        r = (2 ** 24 // j + 1) * j + 1
        while not sp.isprime(r):
            r += j
        pf = prime_factors(j)
        h = 2
        while True:
            z = pow(h, (r - 1) // j, r)
            if all(pow(z, j // p_, r) != 1 for p_ in pf) and (j > 1 or z == 1):
                break
            h += 1
        _root[j] = (r, z)
    return _root[j]


def horner(a: list[int], pt: int, r: int) -> int:
    v = 0
    for c in reversed(a):
        v = (v * pt + c) % r
    return v


def order(a: int, n: int) -> int:
    k, y = 1, a % n
    while y != 1:
        y = y * a % n
        k += 1
    return k


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def even_cycles(N: int) -> int:
    """even cycles of g(y) = 3y + 1/2 on Z/N (independent implementation: follow orbits with a set)."""
    inv2 = (N + 1) // 2
    seen: set[int] = set()
    cnt = 0
    for s in range(N):
        if s in seen:
            continue
        L, y = 0, s
        while y not in seen:
            seen.add(y)
            y = (Q * y + inv2) % N
            L += 1
        cnt += (L % 2 == 0)
    return cnt


prim: dict[int, list[int]] = {1: [-2, 1]}
zero_geo: dict[int, int] = {1: 0}
rows = []
Ns = [n for n in range(3, N_MAX + 1) if gcd(n, 2 * Q) == 1 and (n >= N_MIN or n <= N_MAX // 5)]
for N in Ns:
    tN = time.time()
    cp = charpoly_newton(N, Q)
    assert cp[N] == 1 and (Q != 3 or cp[N - 1] == -2), "trace of A must be 2 for q = 3"
    p_ = cp
    for d in divisors(N):
        if d < N:
            p_, rem = pdivmod(p_, prim[d])
            assert not any(rem), f"prim_{d} does not divide charpoly at N = {N}"
    prim[N] = p_
    deg = len(p_) - 1
    assert deg == int(ph[N])
    # Theorem B
    s1_zero = p_[deg - 1] == 0
    s2_zero = p_[deg - 2] == 0 if deg >= 2 else None       # e2 = 0 together with e1 = 0 <=> sum of squares 0
    nilpotent = all(c == 0 for c in p_[:-1])
    # zero eigenvalue
    zmult = 0
    while p_[zmult] == 0:
        zmult += 1
    zero_geo[N] = even_cycles(N) - sum(zero_geo[d] for d in divisors(N) if d < N)
    rest = p_[zmult:]
    # Kronecker factors
    psi_found, phi_found = {}, {}
    for j in J_ALL:
        if j == 4:
            continue
        dpsi = 1 if j <= 2 else int(ph[j]) // 2
        if dpsi <= deg:
            r, z = root_data(j)
            c = (z + pow(z, -1, r)) % r
            if horner(rest, c, r) == 0:
                k_, rest2 = mult_of(Psi(j), rest)
                if k_:
                    psi_found[j] = k_
                    rest = rest2
    for k in J_ALL:
        if k <= 2 or int(ph[k]) > deg:
            continue
        r, z = root_data(k)
        if horner(rest, z, r) == 0:
            k_, rest2 = mult_of(Phi(k), rest)
            if k_:
                phi_found[k] = k_
                rest = rest2
    row = {"N": N, "deg": deg, "zero_mult": zmult, "zero_geo": zero_geo[N], "psi": psi_found, "phi": phi_found,
           "s1_zero": s1_zero, "s2_zero": s2_zero, "nilpotent": nilpotent, "non_kronecker_deg": len(rest) - 1}
    if Q == 3:
        o3 = order(3, N)
        pw, y = {}, 1
        for t in range(o3):
            pw[y] = t
            y = y * 3 % N
        m, y = 1, 2 % N
        while y not in pw:
            y = y * 2 % N
            m += 1
        t = pw[y]
        idx = deg // (o3 * m)
        row.update({"ord3": o3, "m": m, "t": t, "idx": idx})
        # mu_m symmetry
        r0 = deg % m
        row["mu_m_symmetry"] = all(c == 0 for i, c in enumerate(p_) if (i - r0) % m)
        if o3 % 2 == 0:
            sgn = (-1) ** (m + t)
            k_, _ = mult_of([-sgn] + [0] * (m - 1) + [1], p_)
            row["thmC_mult"] = k_
            row["thmC_ok"] = k_ >= idx
            # predicted cyclotomic content
            ks = divisors(m) if sgn == 1 else [d for d in divisors(2 * m) if m % d]
            pred = {k: idx for k in ks}
        else:
            pred = {}
        obs = dict(phi_found)
        if 6 in psi_found:
            obs[1] = psi_found[6]
        if 3 in psi_found:
            obs[2] = psi_found[3]
        row["circle_extra"] = {k: v - pred.get(k, 0) for k, v in obs.items() if v != pred.get(k, 0)}
        row["circle_missing"] = {k: v for k, v in pred.items() if obs.get(k, 0) < v}
        # integer roots c of g_N (x^m = c), |c| >= 2
        g = [p_[i] for i in range(r0, deg + 1, m)]
        while g[0] == 0:
            g = g[1:]
        binom = {}
        rr = BIG[0]
        for c in range(-min(2 ** m, 5000), min(2 ** m, 5000) + 1):
            if abs(c) >= 2 and horner(g, c % rr, rr) == 0:
                k_, _ = mult_of([-c, 1], g)
                if k_:
                    binom[c] = k_
        row["binomial"] = binom
    rows.append(row)
    say(f"N={N:>3} deg {deg:>3} x^{zmult}(geo {zero_geo[N]}) psi {psi_found} phi {phi_found}"
        + (f" (m,t,idx)=({row['m']},{row['t']},{row['idx']}) extra {row['circle_extra']} binom {row['binomial']}" if Q == 3 else "")
        + f" non-Kronecker deg {len(rest) - 1} [{time.time() - tN:.1f}s]")

say("\n================ SUMMARY (skeptic, independent code) ================")
say(f"q = {Q}; moduli N prime to {2 * Q}, 3 <= N <= {N_MAX}: {len(rows)}")
irr = [(r["N"], {j: v for j, v in r["psi"].items() if j not in (1, 2, 3, 6)}) for r in rows]
irr = [t for t in irr if t[1]]
say(f"levels with an irrational cosine (Psi_j, j not in 1,2,3,4,6): {irr}")
say(f"levels with x - 1 (K-eigenvalue +1/2): {sum(6 in r['psi'] for r in rows)};  x + 1 (-1/2): {sum(3 in r['psi'] for r in rows)};  eigenvalue 0: {sum(r['zero_mult'] > 0 for r in rows)}")
say(f"levels with no cosine at all: {sum((not r['psi']) and r['zero_mult'] == 0 for r in rows)}")
allk: dict[int, list[int]] = {}
for r in rows:
    for k in r["phi"]:
        allk.setdefault(k, []).append(r["N"])
say("Phi_k (k >= 3) at level N: " + "; ".join(f"k={k}: {len(v)}" for k, v in sorted(allk.items())))
say(f"Theorem B: sum of eigenvalues != 0 at: {[r['N'] for r in rows if not r['s1_zero']]};  sum of squares != 0 at: {[r['N'] for r in rows if r['s2_zero'] is False]};  nilpotent levels: {[r['N'] for r in rows if r['nilpotent']]}")
say(f"all-Kronecker levels: {[r['N'] for r in rows if r['non_kronecker_deg'] == 0]};  all-real (no Phi_k, k >= 3) among them: {[r['N'] for r in rows if r['non_kronecker_deg'] == 0 and not r['phi']]}")
zbad = [(r["N"], r["zero_mult"], r["zero_geo"]) for r in rows if r["zero_mult"] != r["zero_geo"]]
say(f"zero: algebraic multiplicity != number of even cycles of y -> {Q}y + 1/2 at (N, alg, geo): {zbad}")
if Q == 3:
    say(f"mu_m symmetry fails at: {[r['N'] for r in rows if not r['mu_m_symmetry']]}")
    say(f"Theorem C violated at: {[r['N'] for r in rows if r.get('thmC_ok') is False]};  predicted content missing at: {[r['N'] for r in rows if r['circle_missing']]}")
    say(f"sporadic unit-circle content (beyond Theorem C): {[(r['N'], r['circle_extra']) for r in rows if r['circle_extra']]}")
    say(f"binomial eigenvalues (2 lambda)^m = c, |c| >= 2: {[(r['N'], r['m'], r['binomial']) for r in rows if r['binomial']]}")
    # ------------------------------------------------ diff against the researcher's JSON
    ref_path = Path(__file__).resolve().parent.parent / "q32_kronecker_census.json"
    if ref_path.exists():
        ref = {r["N"]: r for r in json.loads(ref_path.read_text(encoding="utf-8"))["rows"]}
        diffs = []
        for r in rows:
            rr = ref.get(r["N"])
            if rr is None:
                continue
            mine = ({str(k): v for k, v in r["psi"].items()}, {str(k): v for k, v in r["phi"].items()}, r["zero_mult"], r["zero_geo"],
                    {str(k): v for k, v in r["binomial"].items()}, r["m"], r["t"], r["idx"])
            theirs = (rr["psi"], rr["phi"], rr["zero_mult"], rr["zero_geo_pred"], rr["binomial_roots"], rr["m"], rr["t"], rr["index_<2,3>"])
            if mine != theirs:
                diffs.append((r["N"], mine, theirs))
        say(f"rows compared with q32_kronecker_census.json: {sum(r['N'] in ref for r in rows)};  differences: {diffs}")
say(f"total time {time.time() - T0:.0f} s")
suffix = ("" if Q == 3 else f"_q{Q}") + ("" if N_MIN == 3 else f"_{N_MIN}_{N_MAX}")
Path(__file__).with_name(f"v2_census{suffix}.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
