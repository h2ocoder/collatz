"""Q3.3  Where does the golden ratio (or any other irrational cosine) appear?  Exact survey of the generalised
two-branch kernels

        (K f)(x) = (1/2) f(x/d) + (1/2) f((q x + 1)/d)      on Z/N,   gcd(N, q d) = 1,

for all pairs 2 <= q, d <= QD_MAX, q != d, and all 2 <= N <= N_MAX prime to q d.   (3, 2) is the Terras kernel.
For d = 2 this is the residue chain of the qx+1 map; for d > 2 it is the formal two-branch kernel used in the
earlier half-eigenvalue work (it is NOT the residue chain of a d-branch generalised Collatz map).

For each (q, d, N): exact integer charpoly of A = 2K, primitive part at level N (division by the primitive parts of
the proper divisors, asserted exact), and every Kronecker factor of it: x, Psi_j (cosines), Phi_k (roots of unity).
Reported: every IRRATIONAL cosine (j not in {1,2,3,4,6}), every level whose whole spectrum is real, and every
level whose whole spectrum is Kronecker.

Run:  python -X utf8 q33_qd_survey.py [QD_MAX=12] [N_MAX=60]     (writes q33_qd_survey.log / .json)
"""
from __future__ import annotations

import json
import sys
import time
from math import gcd
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import (charpoly_int, cyclotomic, divisors, euler_phi, kronecker_candidates, multiplicity,  # noqa: E402
                       order, pdivmod, peval_mod, primes_upto, psi, pstr, two_K)

QD_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
N_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 60
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


PR = primes_upto(60000)
_pts: dict[tuple[int, bool], list[tuple[int, int]]] = {}


def test_points(k: int, cosine: bool) -> list[tuple[int, int]]:
    key = (k, cosine)
    if key not in _pts:
        out = []
        for r in PR:
            if r % k == 1:
                z = next(z for z in (pow(h, (r - 1) // k, r) for h in range(2, r)) if order(z, r) == k)
                out.append((r, (z + pow(z, -1, r)) % r if cosine else z))
                if len(out) == 2:
                    break
        _pts[key] = out
    return _pts[key]


def kronecker_factors(p_: list[int]):
    deg = len(p_) - 1
    rest = p_
    z, rest = multiplicity([0, 1], rest)
    ms, ks = kronecker_candidates(deg)
    ps, ph = {}, {}
    for j in ms:
        if j == 4:
            continue
        if j <= 2 or all(peval_mod(rest, pt, r) == 0 for r, pt in test_points(j, True)):
            mult, rest2 = multiplicity(psi(j), rest)
            if mult:
                ps[j], rest = mult, rest2
    for k in ks:
        if k <= 2:
            continue
        if all(peval_mod(rest, pt, r) == 0 for r, pt in test_points(k, False)):
            mult, rest2 = multiplicity(cyclotomic(k), rest)
            if mult:
                ph[k], rest = mult, rest2
    return z, ps, ph, len(rest) - 1


x = sp.symbols("x")
hits = []           # irrational cosines
all_real = []
all_kron = []
n_cases = 0
per_pair: dict[str, dict] = {}
for d in range(2, QD_MAX + 1):
    for q in range(2, QD_MAX + 1):
        if q == d:
            continue
        prim: dict[int, list[int]] = {1: [-2, 1]}
        pair_hits = []
        for N in range(2, N_MAX + 1):
            if gcd(N, q * d) != 1:
                continue
            cp = charpoly_int(two_K(N, q, d))
            p_ = cp
            for dd in divisors(N):
                if dd < N:
                    p_, r = pdivmod(p_, prim[dd])
                    assert r == [0], (q, d, N, dd)
            prim[N] = p_
            assert len(p_) - 1 == euler_phi(N)
            n_cases += 1
            z, ps, ph, deg_rest = kronecker_factors(p_)
            irr = {j: v for j, v in ps.items() if j not in (1, 2, 3, 6)}
            rec = {"q": q, "d": d, "N": N, "phi_N": len(p_) - 1, "zero": z, "psi": {str(k): v for k, v in ps.items()},
                   "phi": {str(k): v for k, v in ph.items()}, "deg_non_kronecker": deg_rest}
            if irr:
                rec["prim"] = pstr(p_)
                rec["factored"] = str(sp.factor(sp.Poly(p_[::-1], x).as_expr()))
                hits.append(rec)
                pair_hits.append((N, irr))
            if deg_rest == 0 and not ph:
                all_real.append(rec)
            if deg_rest == 0:
                all_kron.append(rec)
        per_pair[f"{q},{d}"] = {"irrational_cosines": pair_hits}
    say(f"d = {d} done ({time.time() - T0:.0f} s, {n_cases} cases so far)")

say(f"\n================ SUMMARY: {n_cases} triples (q, d, N), 2 <= q, d <= {QD_MAX}, q != d, 2 <= N <= {N_MAX}, gcd(N, qd) = 1 ================")
say("IRRATIONAL cosine eigenvalues (K-eigenvalue cos(2 pi i/j), j not in {1,2,3,4,6}) at level N:")
by_j: dict[int, list] = {}
for h in hits:
    for j_s, v in h["psi"].items():
        j = int(j_s)
        if j not in (1, 2, 3, 6):
            by_j.setdefault(j, []).append((h["q"], h["d"], h["N"], v))
names = {5: "pentagon: 1/(2phi), -phi/2", 10: "decagon: phi/2, -1/(2phi)", 8: "octagon: +-sqrt2/2", 12: "dodecagon: +-sqrt3/2",
         7: "heptagon", 14: "14-gon (heptagon, sign flipped)", 9: "enneagon", 18: "18-gon (enneagon, sign flipped)"}
for j in sorted(by_j):
    say(f"   j = {j:>3} ({names.get(j, '')}; Psi_{j} = {pstr(psi(j))}): {len(by_j[j])} triples (q, d, N, mult): {by_j[j]}")
if not by_j:
    say("   none")
say("\nfactorisations at the irrational-cosine levels:")
for h in hits:
    say(f"   (q,d,N) = ({h['q']},{h['d']},{h['N']}): prim = {h['factored']}")
say(f"\nlevels whose whole primitive spectrum is real (all cosines): {[(r['q'], r['d'], r['N']) for r in all_real]}")
say(f"levels whose whole primitive spectrum is Kronecker (0 / cosines / roots of unity): {[(r['q'], r['d'], r['N']) for r in all_kron]}")
gold = [(h["q"], h["d"], h["N"]) for h in hits if "5" in h["psi"] or "10" in h["psi"]]
say(f"\ngolden ratio (j = 5 or 10): {gold}")
say(f"   N-values: {sorted(set(g[2] for g in gold))};  with d = 2: {[g for g in gold if g[1] == 2]};  with q = d + 1: {[g for g in gold if g[0] == g[1] + 1]}")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"QD_MAX": QD_MAX, "N_MAX": N_MAX, "cases": n_cases, "irrational_cosine_hits": hits,
                                                           "all_real": all_real, "all_kronecker": all_kron}, indent=0), encoding="utf-8")
