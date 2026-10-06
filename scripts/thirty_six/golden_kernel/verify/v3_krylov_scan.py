"""Skeptic check 3: scan of ALL primes 5 <= p <= P_MAX for cosine / root-of-unity eigenvalues of 2K_p beyond
Theorem C, with NO cap on the order (the researcher's scan q34b tests Phi_k, Psi_j only for k, j <= 60 when p > 400).

Method (O(p^2) per prime, different from the O(p^3) Hessenberg route, and sound):
 (1) Krylov / Berlekamp-Massey: f = minimal polynomial of the sequence u.A^k v modulo r = 2^31 - 1, for random u, v.
     f divides the minimal polynomial mu_r of A mod r, which divides the characteristic polynomial chi_r = chi mod r.
 (2) Degree certificate.  Over Q the eigenvalue 0 has geometric multiplicity z (Prop. E) and every root of the
     forced factor F = x^m - (-1)^(m+t) has geometric multiplicity >= idx (Theorem C, one per <2,3>-orbit).  Ranks can
     only drop modulo r, so chi_r / mu_r is divisible by x^(z-1) F^(idx-1) (r does not divide m).  Hence
            deg f <= deg mu_r <= p - (z-1)^+ - (idx-1) m =: D_exp,
     and if deg f = D_exp then f = mu_r and chi_r = f * x^(z-1) * F^(idx-1) EXACTLY.  No probabilistic gap is left:
     an unlucky (u, v) lowers deg f and the prime is flagged, never silently accepted.
 (3) With chi_r known, c = f / ((x-2) x^[z>0] F^[forced]) contains every remaining eigenvalue with its full
     multiplicity.  Tested on c:  x | c (Jordan block at 0);  gcd(c, F) != 1 (forced value occurring again);
     Phi_k | c for every k | p-1 and Psi_j | c for every j | p-1 or j | p+1 that survives the residue filter below;
     integer roots of g (c = x^a g(x^m)) with 2 <= |root| <= CMAX.   'F does not divide c modulo r' proves
     'F does not divide chi over Z'.
 (4) Residue filter (proved in the README, section 4.4): on functions F_p -> F_p (polynomials of degree < p) A is
     triangular in the monomial basis with diagonal kappa_n = 2^-n (1 + 3^n), so prim_p = prod_{n=1}^{p-1} (x - kappa_n)
     mod p.  A factor Phi_k (p not dividing k) therefore needs k | p-1 and all primitive k-th roots among the kappa_n;
     a factor Psi_j needs j | p-1 or j | p+1 and all its roots among the kappa_n.  (p | k or p | j would need a root
     of multiplicity >= (p-1)/2 among the kappa_n; the largest multiplicity is recorded and checked.)
 Flagged primes (deg f < D_exp) are resolved by the full characteristic polynomial modulo r (power sums + Newton).

CONVENTION: shortcut map; A = 2K_p = R_e + R_o on functions on Z/p, (A f)(x) = f(x/2) + f((3x+1)/2).
Run:  python -X utf8 v3_krylov_scan.py [P_MAX=3000] [P_MIN=5]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp

P_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
P_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 5
CMAX = 5000
R = 2 ** 31 - 1
T0 = time.time()
LOG: list[str] = []
rng = np.random.default_rng(20261006)


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def dot_mod(a: np.ndarray, b_lo: np.ndarray, b_hi: np.ndarray) -> int:
    """sum a_i b_i mod R with b = b_hi * 2^16 + b_lo, all entries < 2^31, length < 2^15."""
    return (int(np.dot(a, b_lo)) + ((int(np.dot(a, b_hi)) % R) << 16)) % R


def berlekamp_massey(s: np.ndarray) -> list[int]:
    """minimal polynomial (ascending coefficients, monic) of the sequence s modulo R."""
    n = len(s)
    s_lo, s_hi = s & 0xFFFF, s >> 16
    C = np.zeros(n + 2, dtype=np.int64)
    C[0] = 1
    B = np.array([1], dtype=np.int64)
    L, m, b = 0, 1, 1
    for i in range(n):
        if L:
            d = (int(s[i]) + dot_mod(C[1:L + 1], s_lo[i - L:i][::-1], s_hi[i - L:i][::-1])) % R
        else:
            d = int(s[i]) % R
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, -1, R) % R
        if 2 * L <= i:
            Tm = C[:L + 1].copy()
            C[m:m + len(B)] = (C[m:m + len(B)] - coef * B) % R
            L, B, b, m = i + 1 - L, Tm, d, 1
        else:
            C[m:m + len(B)] = (C[m:m + len(B)] - coef * B) % R
            m += 1
    return [int(C[L - k]) for k in range(L + 1)]          # f(x) = x^L + C_1 x^(L-1) + ... + C_L


def krylov_minpoly(p: int, e: np.ndarray, o: np.ndarray) -> list[int]:
    n = 2 * p + 6
    u = rng.integers(1, R, size=p, dtype=np.int64)
    v = rng.integers(1, R, size=p, dtype=np.int64)
    u_lo, u_hi = u & 0xFFFF, u >> 16
    s = np.zeros(n, dtype=np.int64)
    for k in range(n):
        s[k] = dot_mod(v, u_lo, u_hi)
        v = v[e] + v[o]                                   # (A f)(x) = f(e x) + f(o x)
        v -= R * (v >= R)
    return berlekamp_massey(s)


def pdiv_small(a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    """a / b mod R, b monic, plain Python (used for low-degree b)."""
    a = list(a)
    db = len(b) - 1
    if len(a) - 1 < db:
        return [0], a
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i] % R
        if c:
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % R
    return q, [t % R for t in a[:db]]


def div_binomial(a: list[int], m: int, s: int) -> tuple[list[int], bool]:
    """a / (x^m - s) mod R; returns (quotient, exact?)."""
    a = [t % R for t in a]
    n = len(a) - 1
    if n < m:
        return [0], not any(a)
    q = [0] * (n - m + 1)
    for i in range(n, m - 1, -1):
        c = a[i]
        q[i - m] = c
        a[i - m] = (a[i - m] + s * c) % R
        a[i] = 0
    return q, not any(a[:m])


def poly_gcd_deg(a: list[int], b: list[int]) -> int:
    """degree of gcd(a, b) over F_R (plain Euclid; the smaller polynomial has low degree)."""
    def trim(z):
        z = [t % R for t in z]
        while z and z[-1] == 0:
            z.pop()
        return z
    a, b = trim(a), trim(b)
    while b:
        inv = pow(b[-1], -1, R)
        bm_ = [t * inv % R for t in b]
        _, rem = pdiv_small(a, bm_)
        a, b = bm_, trim(rem)
    return len(a) - 1


def order_mod(a: int, n: int) -> int:
    k, y = 1, a % n
    while y != 1:
        y = y * a % n
        k += 1
    return k


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


_x = sp.symbols("x")


def Phi(k: int) -> list[int]:
    return [int(c) for c in sp.Poly(sp.cyclotomic_poly(k, _x), _x).all_coeffs()[::-1]]


def Psi(j: int) -> list[int]:
    if j == 1:
        return [-2, 1]
    if j == 2:
        return [2, 1]
    f = Phi(j)
    h = (len(f) - 1) // 2
    Ck_prev, Ck = [2], [0, 1]
    r_ = [f[h]] + [0] * h
    for k in range(1, h + 1):
        for i, c in enumerate(Ck):
            r_[i] += f[h + k] * c
        nxt = [0] + Ck
        for i, c in enumerate(Ck_prev):
            nxt[i] -= c
        Ck_prev, Ck = Ck, nxt
    return r_


def full_charpoly_mod(p: int, einv: np.ndarray, oinv: np.ndarray) -> list[int]:
    M = np.eye(p, dtype=np.int64)
    tr = [0] * (p + 1)
    for k in range(1, p + 1):
        M = M[:, einv] + M[:, oinv]
        M -= R * (M >= R)
        tr[k] = sum(int(t) for t in M.diagonal()) % R
    el = [1] + [0] * p
    for k in range(1, p + 1):
        s = 0
        for i in range(1, k + 1):
            term = el[k - i] * tr[i]
            s += term if i % 2 else -term
        el[k] = s % R * pow(k, -1, R) % R
    return [(el[p - k] if (p - k) % 2 == 0 else -el[p - k]) % R for k in range(p + 1)]


def f2_mul(a, b, D, p):
    """multiplication in F_p[sqrt D]."""
    return ((a[0] * b[0] + D * a[1] * b[1]) % p, (a[0] * b[1] + a[1] * b[0]) % p)


def f2_pow(a, n, D, p):
    out = (1, 0)
    while n:
        if n & 1:
            out = f2_mul(out, a, D, p)
        a = f2_mul(a, a, D, p)
        n >>= 1
    return out


events, flagged, rows = [], [], []
max_kappa_mult_ratio = 0.0
primes = [int(q) for q in sp.primerange(max(P_MIN, 5), P_MAX + 1)]
for p in primes:
    tp = time.time()
    inv2 = (p + 1) // 2
    xs = np.arange(p, dtype=np.int64)
    e = (xs * inv2) % p
    o = ((3 * xs + 1) * inv2) % p
    o3 = order_mod(3, p)
    pw, y = {}, 1
    for t in range(o3):
        pw[y] = t
        y = y * 3 % p
    m, y = 1, 2
    while y not in pw:
        y = y * 2 % p
        m += 1
    t = pw[y]
    idx = (p - 1) // (o3 * m)
    forced = o3 % 2 == 0
    z = (p - 1) // o3 if forced else 0
    sgn = (-1) ** (m + t)
    D_exp = p - max(z - 1, 0) - ((idx - 1) * m if forced else 0)

    f = krylov_minpoly(p, e, o)
    D = len(f) - 1
    note = ""
    if D > D_exp:
        raise AssertionError(f"p = {p}: deg f = {D} > D_exp = {D_exp}: the multiplicity lemma would be violated")
    if D < D_exp:                                         # retry once with fresh vectors, then resolve exactly
        f = krylov_minpoly(p, e, o)
        D = len(f) - 1
    if D < D_exp:
        flagged.append((p, D, D_exp))
        note = f" FLAGGED deg f = {D} < {D_exp}"
        einv = np.zeros(p, dtype=np.int64)
        oinv = np.zeros(p, dtype=np.int64)
        einv[e] = xs
        oinv[o] = xs
        if p <= 1500:
            chi = full_charpoly_mod(p, einv, oinv)
            c, rem = pdiv_small(chi, [(-2) % R, 1])
            assert not any(rem)
            for _ in range(z):
                c, rem = pdiv_small(c, [0, 1])
                assert not any(rem)
            if forced:
                for _ in range(idx):
                    c, ok = div_binomial(c, m, sgn)
                    assert ok
            note += " (resolved with the full characteristic polynomial mod r)"
        else:
            say(f"p = {p}: FLAGGED and too large for the fallback; skipped")
            continue
    else:
        c, rem = pdiv_small(f, [(-2) % R, 1])
        assert not any(rem), (p, "x - 2 must divide")
        if z > 0:
            c, rem = pdiv_small(c, [0, 1])
            assert not any(rem), (p, "x must divide when ord_p(3) is even")
        if forced:
            c, ok = div_binomial(c, m, sgn)
            assert ok, (p, "Theorem C factor must divide")

    ev: dict[str, int] = {}
    # (a) Jordan block at 0 / zero eigenvalue where none is predicted
    k0 = 0
    while c[k0] % R == 0:
        k0 += 1
    if k0:
        ev["x"] = k0
    # (b) forced values occurring again
    if forced:
        folded = [0] * m
        for i, coef in enumerate(c):
            folded[i % m] = (folded[i % m] + coef * pow(sgn, i // m, R)) % R
        gd = poly_gcd_deg([(-sgn) % R] + [0] * (m - 1) + [1], folded)
        if gd > 0:
            ev[f"gcd(c, x^{m}-({sgn})) of degree"] = gd
    # (c) residue filter
    kap = [(pow(2, -n, p) * (1 + pow(3, n, p))) % p for n in range(1, p)]
    cnt: dict[int, int] = {}
    for v_ in kap:
        cnt[v_] = cnt.get(v_, 0) + 1
    max_kappa_mult_ratio = max(max_kappa_mult_ratio, max(cnt.values()) / ((p - 1) / 2)) if p > 13 else max_kappa_mult_ratio
    g0 = int(sp.primitive_root(p))
    cand_phi, cand_psi = [], []
    for k in divisors(p - 1):
        zk = pow(g0, (p - 1) // k, p)
        rts = [pow(zk, i, p) for i in range(1, k + 1) if np.gcd(i, k) == 1]
        if all(rt in cnt for rt in rts):
            cand_phi.append(k)
        if k not in (1, 2, 3, 4, 6):
            if all(((rt + pow(rt, -1, p)) % p) in cnt for rt in rts):
                cand_psi.append(k)
    # j | p + 1: norm-one elements of F_p[sqrt D]
    Dn = 2
    while pow(Dn, (p - 1) // 2, p) != p - 1:
        Dn += 1
    pf = [int(q) for q in sp.factorint(p + 1)]
    a0 = 1
    while True:
        a0 += 1
        w = f2_pow((a0, 1), p - 1, Dn, p)                 # norm one
        if all(f2_pow(w, (p + 1) // q, Dn, p) != (1, 0) for q in pf):
            break
    for j in divisors(p + 1):
        if j in (1, 2, 3, 4, 6):
            continue
        wj = f2_pow(w, (p + 1) // j, Dn, p)
        ok, cur = True, (1, 0)
        for i in range(1, j // 2 + 1):
            cur = f2_mul(cur, wj, Dn, p)
            if np.gcd(i, j) == 1 and (2 * cur[0]) % p not in cnt:
                ok = False
                break
        if ok:
            cand_psi.append(j)
    for k in cand_phi:
        if k <= 2:
            pol = [(-1) % R, 1] if k == 1 else [1, 1]
        else:
            pol = [t % R for t in Phi(k)]
        if len(pol) - 1 <= len(c) - 1:
            mult = 0
            cc = c
            while True:
                q_, rem = pdiv_small(cc, pol)
                if any(rem):
                    break
                cc, mult = q_, mult + 1
            if mult:
                ev[f"Phi_{k}"] = mult
    for j in cand_psi:
        pol = [t % R for t in Psi(j)]
        if len(pol) - 1 <= len(c) - 1:
            q_, rem = pdiv_small(c, pol)
            if not any(rem):
                ev[f"Psi_{j}"] = 1
    # (d) integer roots of g, c(x) = x^a g(x^m)
    cnz = c[k0:]
    if all(coef % R == 0 for i, coef in enumerate(cnz) if i % m):
        g = np.array(cnz[::m], dtype=np.int64)
        lim = min(2 ** m, CMAX) if m < 40 else CMAX
        cs = np.array([v_ for v_ in range(-lim, lim + 1) if abs(v_) >= 2], dtype=np.int64)
        if len(cs):
            val = np.zeros(len(cs), dtype=np.int64)
            csm = cs % R
            for coef in g[::-1]:
                val = (val * csm) % R                      # < 2^62
                val = (val + int(coef)) % R
            for c0 in cs[val == 0]:
                ev[f"x^{m}={int(c0)}"] = 1
    else:
        ev["mu_m symmetry of the cofactor fails"] = 1
    if ev:
        events.append((p, ev))
    rows.append((p, m, t, idx, o3, D, D_exp, len(cand_phi), len(cand_psi)))
    if ev or note or p < 60 or p % 50 < 2:
        say(f"p = {p:>5} (m,t,idx)=({m},{t},{idx}) ord3 {o3:>5} deg f {D} = D_exp {D_exp}: {D == D_exp}{note} | residue-filter survivors: Phi {cand_phi[:8]}{'...' if len(cand_phi) > 8 else ''} Psi {cand_psi[:8]} | events beyond Theorem C: {ev if ev else '-'}  [{time.time() - tp:.1f}s, total {time.time() - T0:.0f}s]")

say("\n================ SUMMARY ================")
say(f"primes {primes[0]} <= p <= {primes[-1]}: {len(primes)};  modulus r = 2^31 - 1")
say(f"flagged primes (deg f < D_exp after one retry; resolved exactly when p <= 1500): {flagged}")
say(f"events beyond Theorem C (cosines Psi_j with ANY j, roots of unity Phi_k with ANY k, Jordan blocks at 0, integer roots 2 <= |c| <= {CMAX} of g): ")
for p, ev in events:
    say(f"   p = {p}: {ev}")
say(f"largest prime with an event: {max((p for p, _ in events), default=None)};  primes above it scanned clean: {sum(1 for p in primes if p > max((q for q, _ in events), default=0))}")
say(f"largest multiplicity of a residue kappa_n, as a fraction of (p-1)/2, over primes p > 13: {max_kappa_mult_ratio:.4f}  (< 1: no factor Phi_k or Psi_j with p | k, j is possible)")
say(f"total time {time.time() - T0:.0f} s")
tag = "" if P_MIN <= 5 else f"_{P_MIN}"
Path(__file__).with_name(f"v3_krylov_scan{tag}_{P_MAX}.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
