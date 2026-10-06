"""Q3.2  Kronecker census: which regular polygons does the Terras kernel see mod N?

Conventions: gk_common.py (shortcut map; A = 2K_N = R_e + R_o on functions on Z/N, gcd(N, 6) = 1).

For every N prime to 6 with 5 <= N <= N_MAX:
  * exact characteristic polynomial of A (integer matrix; multimodular + CRT with a proved bound);
  * primitive part  prim_N = charpoly(2K_N) / prod_{d | N, d < N} prim_d  (exact division asserted; the
    kernel is block diagonal by the additive order of the frequency; prim_1 = x - 2; deg prim_N = phi(N));
  * symmetry reduction: with G = (Z/N)^x and m = order of 2 modulo <3>, prim_N(x) = x^r0 g_N(x^m)
    (asserted on the coefficients); everything is then read in y = x^m = (2 lambda)^m;
  * EVERY Kronecker factor of prim_N:  x  (eigenvalue 0),  Psi_j  (2K-eigenvalue 2cos(2 pi i/j), i.e. the
    K-eigenvalue cos(2 pi i/j)),  Phi_k  (K-eigenvalue = root of unity / 2), with multiplicities.
    Candidates are ALL j with deg Psi_j <= phi(N) and ALL k with phi(k) <= phi(N) (rigorous cap), prefiltered
    by a necessary condition mod two primes, then decided by exact division over Z.
  * the unit-circle content predicted by the repo's theorem in lattice form (README section 4):
        (x^m - (-1)^(m+t))^[G:<2,3>]  divides prim_N   when ord_N(3) is even,   2^m = 3^t in G;
    "sporadic" = anything on the unit circle beyond that;
  * integer roots c of g_N other than 0 and the predicted +-1:  eigenvalues with (2 lambda)^m = c  ("binomial");
  * multiplicity of 0 against the number of even cycles of y -> 3y + 1/2 (geometric multiplicity);
  * full factorisation of g_N over Z (sympy) when deg g_N <= FACTOR_MAX_DEG.

Run:  python -X utf8 q32_kronecker_census.py [N_MAX=400] [FACTOR_MAX_DEG=200]
Writes q32_kronecker_census.log / .json
"""
from __future__ import annotations

import json
import sys
import time
from math import gcd
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import (charpoly_int, cyclotomic, divisors, euler_phi, is_prime, kronecker_candidates,  # noqa: E402
                       multiplicity, order, pdivmod, peval_mod, primes_upto, psi, pstr, two_K)

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 400
FACTOR_MAX_DEG = int(sys.argv[2]) if len(sys.argv) > 2 else 200
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


PR = primes_upto(200000)


def element_of_order(k: int, r: int) -> int:
    for h in range(2, r):
        z = pow(h, (r - 1) // k, r)
        if order(z, r) == k:
            return z
    raise ValueError


def prefilter(prim: list[int], k: int, cosine: bool) -> bool:
    """necessary condition for Psi_k | prim (cosine) or Phi_k | prim: vanishing at a root modulo two primes r = 1 mod k."""
    if k <= 2:
        return True
    hits = 0
    for r in PR:
        if r % k == 1:
            z = element_of_order(k, r)
            pt = (z + pow(z, -1, r)) % r if cosine else z
            if peval_mod(prim, pt, r) != 0:
                return False
            hits += 1
            if hits == 2:
                return True
    return True


def theorem_prediction(N: int):
    """(m, t, index, ord3):  m = least m >= 1 with 2^m in <3>, 2^m = 3^t, index = [G : <2,3>]."""
    o3 = order(3, N)
    pw, xx = {}, 1
    for t in range(o3):
        pw[xx] = t
        xx = xx * 3 % N
    m, y = 1, 2 % N
    while y not in pw:
        y = y * 2 % N
        m += 1
    return m, pw[y], euler_phi(N) // (o3 * m), o3


def even_cycles_total(N: int) -> int:
    """number of even-length cycles of g(y) = 3y + 1/2 on Z/N = dim ker(R_e + R_o) on C^(Z/N)
    (f(e x) = -f(o x) for all x  <=>  f = -f o g,  g = o e^-1)."""
    inv2 = pow(2, -1, N)
    seen = bytearray(N)
    cnt = 0
    for s in range(N):
        if seen[s]:
            continue
        L, y = 0, s
        while not seen[y]:
            seen[y] = 1
            y = (3 * y + inv2) % N
            L += 1
        if L % 2 == 0:
            cnt += 1
    return cnt


x, yv = sp.symbols("x y")
prim: dict[int, list[int]] = {1: [-2, 1]}
zero_geo_prim: dict[int, int] = {1: 0}
rows = []
Ns = [n for n in range(5, N_MAX + 1) if gcd(n, 6) == 1]
for N in Ns:
    tN = time.time()
    cp = charpoly_int(two_K(N))
    p_ = cp
    for d in divisors(N):
        if d < N:
            p_, r = pdivmod(p_, prim[d])
            assert r == [0], f"prim_{d} does not divide charpoly(2K_{N})"
    prim[N] = p_
    deg = len(p_) - 1
    assert deg == euler_phi(N)
    m_, t_, idx, o3 = theorem_prediction(N)
    r0 = deg % m_
    assert all(c == 0 for i, c in enumerate(p_) if (i - r0) % m_), f"mu_m symmetry fails at N = {N}"
    g = [p_[i] for i in range(r0, deg + 1, m_)]

    # --- Kronecker factors of prim_N (in x)
    rest = p_
    z_mult, rest = multiplicity([0, 1], rest)
    ms, ks = kronecker_candidates(deg)
    psi_found: dict[int, int] = {}
    for j in ms:
        if j == 4:
            continue
        if prefilter(rest, j, True):
            mult, rest2 = multiplicity(psi(j), rest)
            if mult:
                psi_found[j] = mult
                rest = rest2
    phi_found: dict[int, int] = {}
    for k in ks:
        if k <= 2:               # Phi_1 = x - 1 = Psi_6, Phi_2 = x + 1 = Psi_3: already counted as cosines
            continue
        if prefilter(rest, k, False):
            mult, rest2 = multiplicity(cyclotomic(k), rest)
            if mult:
                phi_found[k] = mult
                rest = rest2

    # --- theorem (lattice form) and sporadic unit-circle content
    circle_obs = {f"Phi_{k}": v for k, v in phi_found.items()}
    if 6 in psi_found:
        circle_obs["Phi_1"] = psi_found[6]
    if 3 in psi_found:
        circle_obs["Phi_2"] = psi_found[3]
    circle_pred: dict[str, int] = {}
    thm_ok = None
    if o3 % 2 == 0:
        sgn = (-1) ** (m_ + t_)
        pred_poly = [-sgn] + [0] * (m_ - 1) + [1]          # x^m - sgn
        k_obs, _ = multiplicity(pred_poly, p_)
        thm_ok = k_obs >= idx
        ds = divisors(m_) if sgn == 1 else [d for d in divisors(2 * m_) if m_ % d]
        for d in ds:
            circle_pred[f"Phi_{d}"] = idx
    extra = {k: v - circle_pred.get(k, 0) for k, v in circle_obs.items() if v != circle_pred.get(k, 0)}
    missing = {k: v for k, v in circle_pred.items() if k not in circle_obs}

    # --- zero eigenvalue
    tot_even = even_cycles_total(N)
    zero_geo_prim[N] = tot_even - sum(zero_geo_prim[d] for d in divisors(N) if d < N)

    # --- g_N(y): integer roots and factor degrees
    g_nz = list(g)
    zg = 0
    while g_nz[0] == 0:
        g_nz = g_nz[1:]
        zg += 1
    int_roots: dict[int, int] = {}
    g_fact = None
    if len(g) - 1 <= FACTOR_MAX_DEG:
        fl = sp.Poly(g[::-1], yv).factor_list()[1]
        g_fact = sorted([(f.degree(), e_) for f, e_ in fl])
        for f, e_ in fl:
            if f.degree() == 1:
                c = -int(f.all_coeffs()[1])
                int_roots[c] = e_
        low = [(str(f.as_expr()), e_) for f, e_ in fl if 2 <= f.degree() <= 3]
    else:
        low = None
        for c in range(-min(2 ** m_, 3000), min(2 ** m_, 3000) + 1):
            if c and peval_mod(g_nz, c % 1000003, 1000003) == 0:
                mult, _ = multiplicity([-c, 1], g_nz)
                if mult:
                    int_roots[c] = mult
    binomial = {c: v for c, v in int_roots.items() if c not in (0, 1, -1)}
    cos_irr = {j: v for j, v in psi_found.items() if j not in (1, 2, 3, 6)}
    row = {
        "N": N, "prime": is_prime(N), "deg_prim": deg, "ord2": order(2, N), "ord3": o3,
        "m": m_, "t": t_, "index_<2,3>": idx, "deg_g": len(g) - 1,
        "zero_mult": z_mult, "zero_geo_pred": zero_geo_prim[N],
        "psi": {str(k): v for k, v in psi_found.items()},
        "phi": {str(k): v for k, v in phi_found.items()},
        "irrational_cosines_m": {str(k): v for k, v in cos_irr.items()},
        "circle_pred": circle_pred, "circle_obs": circle_obs, "circle_extra": extra, "circle_missing": missing,
        "theorem_divides": thm_ok,
        "g_integer_roots": {str(c): v for c, v in sorted(int_roots.items())},
        "binomial_roots": {str(c): v for c, v in sorted(binomial.items())},
        "g_factor_degrees": g_fact, "g_low_degree_factors": low,
        "deg_non_kronecker": len(rest) - 1,
        "all_cosines": (len(rest) - 1 == 0 and not phi_found),
        "all_kronecker": len(rest) - 1 == 0,
    }
    if N <= 13 or N == 25 or N == 35:
        row["prim"] = pstr(p_)
    rows.append(row)
    tag = "p" if row["prime"] else "c"
    say(f"N={N:>3}{tag} phi {deg:>3} ord2 {row['ord2']:>3} ord3 {o3:>3} (m,t,idx)=({m_},{t_},{idx}) | x^{z_mult}(geo {zero_geo_prim[N]}) | cos j:{dict(psi_found)} | "
        f"circle obs {circle_obs} pred {circle_pred}" + (f" EXTRA {extra}" if extra else "") + (f" MISSING {missing}" if missing else "")
        + (f" | BINOMIAL (2lam)^{m_} = {binomial}" if binomial else "")
        + f" | g deg {len(g) - 1}" + (f" factors {g_fact}" if g_fact else " (not factored)")
        + (f" low {low}" if low else "") + f" | non-Kronecker deg {len(rest) - 1} [{time.time() - tN:.1f}s]")

# ----------------------------------------------------------------------------- summary
say("\n================ SUMMARY ================")
say(f"moduli: all {len(rows)} N prime to 6 with 5 <= N <= {N_MAX}  ({sum(r['prime'] for r in rows)} primes, {sum(not r['prime'] for r in rows)} composites); primitive blocks (level N) only")
allm: dict[int, list[int]] = {}
for r in rows:
    for m_s in r["psi"]:
        allm.setdefault(int(m_s), []).append(r["N"])
say("cosine eigenvalues of K at level N (factor Psi_j of prim_N; j = 4 is the eigenvalue 0):")
for j in sorted(allm):
    Ns_ = allm[j]
    say(f"   j = {j:>3}  (K-eigenvalues cos(2 pi i/{j}); Psi_{j} = {pstr(psi(j))}): {len(Ns_)} moduli" + (f": {Ns_}" if len(Ns_) <= 30 else f", first {Ns_[:12]} ..."))
zero_Ns = [r["N"] for r in rows if r["zero_mult"]]
say(f"   j =   4  (eigenvalue 0): {len(zero_Ns)} moduli")
irr = [(r["N"], r["irrational_cosines_m"]) for r in rows if r["irrational_cosines_m"]]
say(f"IRRATIONAL cosines (j not in 1,2,3,4,6) at level N: {irr}")
say(f"levels whose whole primitive spectrum is cosines (all eigenvalues real): {[r['N'] for r in rows if r['all_cosines']]}")
say(f"levels whose whole primitive spectrum is Kronecker (0, cosines, roots of unity/2): {[r['N'] for r in rows if r['all_kronecker']]}")
allk: dict[int, list[int]] = {}
for r in rows:
    for k_s in r["phi"]:
        allk.setdefault(int(k_s), []).append(r["N"])
say("K-eigenvalues (1/2) * (primitive k-th root of unity), k >= 3:")
for k in sorted(allk):
    say(f"   k = {k:>3}: {len(allk[k])} moduli: {allk[k][:25]}{' ...' if len(allk[k]) > 25 else ''}")
bad_thm = [r["N"] for r in rows if r["theorem_divides"] is False]
say(f"theorem (lattice form) violated at: {bad_thm}   (must be empty)")
ex = [(r["N"], r["circle_extra"]) for r in rows if r["circle_extra"]]
say(f"levels with unit-circle eigenvalues of 2K BEYOND the theorem (sporadic): {ex}")
say(f"   primes among them: {[n for n, _ in ex if is_prime(n)]}")
miss = [(r["N"], r["circle_missing"]) for r in rows if r["circle_missing"]]
say(f"levels with predicted unit-circle eigenvalues missing: {miss}   (must be empty)")
bi = [(r["N"], r["m"], r["binomial_roots"]) for r in rows if r["binomial_roots"]]
say(f"binomial eigenvalues (2 lambda)^m = c, integer c not in {{0, 1, -1}}: (N, m, {{c: mult}}) = {bi}")
zbad = [(r["N"], r["zero_mult"], r["zero_geo_pred"]) for r in rows if r["zero_mult"] != r["zero_geo_pred"]]
say(f"algebraic multiplicity of 0 vs number of even cycles of y -> 3y + 1/2 at level N: mismatches (N, alg, geo) = {zbad}")
say(f"   of which prime N: {[z for z in zbad if is_prime(z[0])]}")
no_real = [r["N"] for r in rows if not r["psi"] and not r["zero_mult"]]
say(f"levels with NO cosine eigenvalue at all: {len(no_real)} of {len(rows)}")
shape: dict[str, int] = {}
for r in rows:
    if r["g_factor_degrees"] is not None:
        big = [d for d, e_ in r["g_factor_degrees"] if d > 1]
        key = "one irreducible generic factor" if len(big) == 1 else ("no generic factor" if not big else f"{len(big)} non-linear factors")
        shape[key] = shape.get(key, 0) + 1
        if len(big) != 1:
            say(f"   generic part of g_N not a single irreducible factor at N = {r['N']}: {r['g_factor_degrees']}  low: {r['g_low_degree_factors']}")
say(f"shape of g_N after removing linear factors (levels with deg g <= {FACTOR_MAX_DEG}): {shape}")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"N_MAX": N_MAX, "rows": rows}, indent=0), encoding="utf-8")
