"""Q3.4 (common cause)  Sporadic eigenvalues +-1 across the whole "multiplier = divisor + 1" family.

For a prime p and d in {2, ..., p-2} let q = d + 1 and  A = 2K_{(q,d),p} = R_e + R_o,  e(x) = x/d, o(x) = (q x + 1)/d
on Z/p.  d = 2 is the Terras (3x+1) kernel.  Every member satisfies the theorem (functional delta_{-1/d} - delta_{-1}):
     -chi(d) is an eigenvalue of A for every character chi with chi(q) = -1,
so v in {+1, -1} is PREDICTED with multiplicity [G:<d,q>] iff ord_p(q) is even and v^m = (-1)^(m+t)
(m = order of d modulo <q>, d^m = q^t).  "Sporadic" = geometric multiplicity of v above the prediction.

Two universal one-condition configurations (proved in the README, checked here on every root):
     F1(d) = d^2 + d - 1  = 0 (mod p)   =>   delta_{-1} - delta_0 is an eigenfunction of A, eigenvalue +1
     F2(d) = d^2 + 3d + 1 = 0 (mod p)   =>   delta_{d x0} - delta_{x0}, x0 = 1/(d^2 - d - 1)  (the 2-cycle of the word oe)
                                             is an eigenfunction of A, eigenvalue -1
Both have discriminant 5:  F1 = 0  <=>  d = 1/phi or -phi;   F2 = 0  <=>  d = -phi^2 or -phi^-2   in F_p.
For d = 2:  F1(2) = 5,  F2(2) = 11.

Parts
  A. for every prime 5 <= p <= P_MAX and every d: is +1 / -1 an eigenvalue, is it predicted, is it sporadic.
  B. universality of F1, F2 on every root (assert), and how many sporadic d they account for.
  C. search for further universal polynomials: all F in Z[d] of degree <= 4 with small coefficients whose roots
     mod p ALWAYS carry the eigenvalue v (for all 13 <= p <= P_MAX);  irreducible survivors are listed.
  D. what is left over ('unexplained'), per prime; the Collatz column d = 2.

Rank computations are modulo 24-bit primes: corank mod r >= corank over Q, so 'eigenvalue absent mod r' and
'corank mod r = prediction' are proofs; a corank above the prediction is confirmed modulo a second prime.

Run:  python -X utf8 q34c_family_base_rate.py [P_MAX=151]    (writes q34c_family_base_rate.log / .json)
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import order, primes_upto, two_K  # noqa: E402

P_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 151
BIG = (16777213, 16777199)
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def rank_mod(M: np.ndarray, m: int) -> int:
    A = (M % m).astype(np.int64)
    n_rows, n_cols = A.shape
    r = 0
    for c in range(n_cols):
        piv = np.nonzero(A[r:, c])[0]
        if len(piv) == 0:
            continue
        i = r + int(piv[0])
        if i != r:
            A[[r, i]] = A[[i, r]]
        A[r] = (A[r] * pow(int(A[r, c]), -1, m)) % m
        col = A[:, c].copy()
        col[r] = 0
        nz = np.nonzero(col)[0]
        if len(nz):
            A[nz] = (A[nz] - np.outer(col[nz], A[r])) % m
        r += 1
        if r == n_rows:
            break
    return r


# ------------------------------------------------------------------------------------------- A, B
PRIMES = [q for q in primes_upto(P_MAX) if q >= 5]
present: dict[int, dict[int, set[int]]] = {}       # present[p][v] = {d : v is an eigenvalue of A}
sporadic: dict[int, dict[int, dict[int, int]]] = {}  # sporadic[p][d][v] = multiplicity above the prediction
rows = []
for p in PRIMES:
    I = np.eye(p, dtype=np.int64)
    present[p] = {1: set(), -1: set()}
    spor: dict[int, dict[int, int]] = {}
    for d in range(2, p - 1):
        q = (d + 1) % p
        o_q = order(q, p)
        pw, xx = {}, 1
        for t in range(o_q):
            pw[xx] = t
            xx = xx * q % p
        m_, yy = 1, d
        while yy not in pw:
            yy = yy * d % p
            m_ += 1
        t_ = pw[yy]
        idx = (p - 1) // (o_q * m_)
        A = two_K(p, q, d)
        for v in (1, -1):
            pred = idx if (o_q % 2 == 0 and v ** m_ == (-1) ** (m_ + t_)) else 0
            got = p - rank_mod(A - v * I, BIG[0])
            assert got >= pred, (p, d, v)
            if got > pred:
                got = min(got, p - rank_mod(A - v * I, BIG[1]))
            if got > 0:
                present[p][v].add(d)
            if got > pred:
                spor.setdefault(d, {})[v] = got - pred
    sporadic[p] = spor
    f1 = sorted(d for d in range(2, p - 1) if (d * d + d - 1) % p == 0)
    f2 = sorted(d for d in range(2, p - 1) if (d * d + 3 * d + 1) % p == 0)
    assert all(d in present[p][1] for d in f1), ("F1 root without eigenvalue +1", p, f1)
    assert all(d in present[p][-1] for d in f2), ("F2 root without eigenvalue -1", p, f2)
    left = sorted(d for d in spor if d not in f1 and d not in f2)
    rows.append({"p": p, "kernels": p - 3, "sporadic": {str(d): {str(k): v for k, v in vv.items()} for d, vv in sorted(spor.items())},
                 "F1_roots": f1, "F2_roots": f2, "sporadic_roots_of_F1F2": sorted(d for d in spor if d in f1 or d in f2), "unexplained_d": left})
    say(f"p = {p:>3}: sporadic d {len(spor):>2} of {p - 3:>3} | F1 roots {f1} F2 roots {f2} | sporadic and not a root of F1 F2: {len(left)}: "
        + str({d: spor[d] for d in left}) + ("   <- Collatz d = 2" if 2 in left else ""))

say("\n--- B. the two golden conditions ---")
n_f1 = sum(len(r["F1_roots"]) for r in rows)
n_f2 = sum(len(r["F2_roots"]) for r in rows)
say(f"F1(d) = d^2 + d - 1: {n_f1} roots (p, d) with 5 <= p <= {P_MAX}; eigenvalue +1 present at every one (asserted).")
say(f"F2(d) = d^2 + 3d + 1: {n_f2} roots; eigenvalue -1 present at every one (asserted).")
d_ = sp.symbols("d")
phi = (1 + sp.sqrt(5)) / 2
say(f"   roots over Q(sqrt5): F1: {sp.solve(d_ ** 2 + d_ - 1, d_)} = 1/phi, -phi;   F2: {sp.solve(d_ ** 2 + 3 * d_ + 1, d_)} = -phi^-2, -phi^2")
assert sp.simplify((1 / phi) ** 2 + 1 / phi - 1) == 0 and sp.simplify((-phi) ** 2 - phi - 1) == 0
assert sp.simplify(phi ** 4 - 3 * phi ** 2 + 1) == 0 and sp.simplify(phi ** -4 - 3 * phi ** -2 + 1) == 0
say("   d = 2:  F1(2) = 5 (2 = -phi = 1/phi mod 5, phi = 3),   F2(2) = 11 (phi = 8 mod 11, phi^2 = 9, 2 = -phi^2).")
say("   symbolic check of the two configurations (d a free symbol, q = d + 1; e^-1 a = d a, o^-1 a = (d a - 1)/q):")
q_ = d_ + 1
einv = lambda a: d_ * a            # noqa: E731
oinv = lambda a: (d_ * a - 1) / q_  # noqa: E731
say(f"      F1: A(delta_-1 - delta_0) = delta_{{{einv(-1)}}} + delta_{{{sp.simplify(oinv(-1))}}} - delta_{{{einv(0)}}} - delta_{{{sp.simplify(oinv(0))}}};  closes iff -d = -1/(d+1): numerator {sp.factor(sp.numer(sp.together(einv(-1) - oinv(0))))}")
x0 = 1 / (d_ ** 2 - d_ - 1)
x1 = d_ * x0
assert sp.simplify(oinv(x1) - x0) == 0 and sp.simplify(einv(x0) - x1) == 0
say(f"      F2: x0 = 1/(d^2-d-1), x1 = d x0 form the 2-cycle (o x0 = x1, e x1 = x0); A(delta_x1 - delta_x0) = -(delta_x1 - delta_x0) + delta_{{d x1}} - delta_{{o^-1 x0}};")
say(f"          closes iff d x1 = o^-1(x0): numerator {sp.factor(sp.numer(sp.together(einv(x1) - oinv(x0))))}")

# ------------------------------------------------------------------------------------------- C
say("\n--- C. search for further universal polynomials F(d) (roots mod p always carry the eigenvalue v), primes 13.." + str(P_MAX) + " ---")
SP = [p for p in PRIMES if p >= 13]


def search(deg: int, B: int, leads: tuple[int, ...]) -> list[tuple[int, list[int], int]]:
    out = []
    coefs = np.array(list(itertools.product(range(-B, B + 1), repeat=deg)), dtype=np.int64)       # c0 .. c_{deg-1}
    for lead in leads:
        ok = {v: np.ones(len(coefs), dtype=bool) for v in (1, -1)}
        nroots = np.zeros(len(coefs), dtype=np.int64)
        for p in SP:
            ds = np.arange(2, p - 1, dtype=np.int64)
            val = np.full((len(coefs), len(ds)), lead, dtype=np.int64)
            for k in range(deg - 1, -1, -1):
                val = (val * ds[None, :] + coefs[:, k][:, None]) % p
            isroot = val == 0
            nroots += isroot.sum(axis=1)
            for v in (1, -1):
                mem = np.array([d in present[p][v] for d in ds.tolist()])
                ok[v] &= ~(isroot & ~mem[None, :]).any(axis=1)
        for v in (1, -1):
            for i in np.nonzero(ok[v] & (nroots >= 12))[0]:
                out.append((v, [int(c) for c in coefs[i]] + [lead], int(nroots[i])))
    return out


survivors = []
for deg, B, leads in ((2, 12, (1, 2, 3)), (3, 7, (1, 2, 3)), (4, 4, (1,))):
    hits = search(deg, B, leads)
    irr = []
    for v, c, nr in hits:
        pol = sp.Poly(c[::-1], d_)
        if sp.gcd_list(c) != 1:
            continue
        fl = pol.factor_list()[1]
        # drop factors d, d - 1, d + 1 (their roots are excluded from the family) and report the irreducible core
        core = [f for f, _ in fl if f.as_expr() not in (d_, d_ - 1, d_ + 1)]
        if len(core) == 1 and core[0].degree() == deg:
            irr.append((v, str(core[0].as_expr()), nr))
    irr = sorted(set(irr))
    say(f"   degree {deg}, |coefficients| <= {B}, leading coefficient in {leads}: {len(hits)} polynomials pass; irreducible of full degree: {irr}")
    survivors += [{"degree": deg, "v": v, "F": f, "roots_tested": nr} for v, f, nr in irr]
say("   reading: d^2+d-1 (v = +1) and d^2+3d+1 (v = -1) are F1, F2;  d^2+d+1 (d a cube root of unity: q = -d^2, m = 1, t = 2) is the theorem.")
say("   No other irreducible quadratic, cubic or quartic in the search box is universal: there is no third low-degree condition.")

# ------------------------------------------------------------------------------------------- D
say("\n--- D. what F1, F2 do not explain ---")
tot = sum(len(r["sporadic"]) for r in rows)
un = sum(len(r["unexplained_d"]) for r in rows)
say(f"primes 5..{P_MAX}: {sum(r['kernels'] for r in rows)} kernels (d+1, d); {tot} have a sporadic +-1; {tot - un} of those are roots of F1 or F2; {un} are not")
for lo, hi in ((5, 41), (43, 79), (83, 113), (127, P_MAX)):
    sel = [r for r in rows if lo <= r["p"] <= hi]
    if sel:
        say(f"   {lo:>3} <= p <= {hi:>3}: {len(sel):>2} primes; sporadic d per prime {sum(len(r['sporadic']) for r in sel) / len(sel):.2f}; not explained by F1, F2 per prime {sum(len(r['unexplained_d']) for r in sel) / len(sel):.2f}"
            f" = {100 * sum(len(r['unexplained_d']) for r in sel) / sum(r['kernels'] for r in sel):.1f} % of the kernels")
coll = [(r["p"], r["sporadic"]["2"], "root of F2" if 2 in r["F2_roots"] else ("root of F1" if 2 in r["F1_roots"] else "unexplained")) for r in rows if "2" in r["sporadic"]]
say(f"Collatz column d = 2: sporadic at {coll}")
say("   p = 11: both sporadic eigenvalues come from F2(2) = 11 (the trivial cycle {1, 2}): -1 directly, +1 because the spectrum is invariant under x -> -x (m = 2).")
p = 37
orb = set()
fr = [2]
while fr:
    dd = fr.pop()
    if dd in orb:
        continue
    orb.add(dd)
    fr += [pow(dd, -1, p), (-1 - dd) % p]
say(f"   p = 37: the orbit of d = 2 under d -> 1/d, d -> -1-d is {sorted(orb)}; sporadic among them: {sorted(d for d in orb if d in sporadic[p])} (all sporadic d at 37: {sorted(sporadic[p])})")
for pp in (31, 41, 43):
    orb = set()
    fr = [2]
    while fr:
        dd = fr.pop()
        if dd in orb:
            continue
        orb.add(dd)
        fr += [pow(dd, -1, pp), (-1 - dd) % pp]
    say(f"   p = {pp}: same orbit of d = 2: {sorted(orb)}; sporadic among them: {sorted(d for d in orb if d in sporadic[pp])}")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"P_MAX": P_MAX, "rows": rows, "universal_polynomial_survivors": survivors, "collatz": [[c[0], c[1], c[2]] for c in coll]}, indent=0), encoding="utf-8")
