"""Self-test of gk_common: exact charpoly vs sympy, Psi_m vs sympy minimal polynomials, timing.
Run:  python -X utf8 selftest_common.py   (writes selftest_common.log)
"""
import sys
import time
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import charpoly_int, cyclotomic, kronecker_candidates, psi, pstr, two_K  # noqa: E402

out = []


def say(s=""):
    print(s, flush=True)
    out.append(s)


x = sp.symbols("x")
ok = True
for N in (5, 7, 11, 13, 25, 35, 37):
    A = two_K(N)
    c = charpoly_int(A)
    ref = sp.Matrix(A.tolist()).charpoly(x).all_coeffs()[::-1]
    same = [int(v) for v in ref] == c
    ok &= same
    say(f"N = {N:>3}: charpoly_int == sympy charpoly: {same}")
say("charpoly(2K_5) = " + pstr(charpoly_int(two_K(5))) + "   factored: " + str(sp.factor(sp.Poly(charpoly_int(two_K(5))[::-1], x).as_expr())))

for m in list(range(1, 41)) + [60, 97, 105, 120]:
    ref = sp.minimal_polynomial(2 * sp.cos(2 * sp.pi / m), x, polys=True).all_coeffs()[::-1]
    same = [int(v) for v in ref] == psi(m)
    ok &= same
    if not same:
        say(f"Psi_{m} MISMATCH")
say("Psi_m == sympy minimal_polynomial(2cos(2pi/m)) for m = 1..40, 60, 97, 105, 120: " + str(ok))
for k in (1, 2, 3, 4, 5, 8, 12, 15, 16, 105):
    ref = [int(v) for v in sp.Poly(sp.cyclotomic_poly(k, x), x).all_coeffs()[::-1]]
    ok &= ref == cyclotomic(k)
say("Phi_k == sympy cyclotomic_poly for k in (1,2,3,4,5,8,12,15,16,105): " + str(ok))
say("Psi_5 = " + pstr(psi(5)) + ";  Psi_10 = " + pstr(psi(10)) + ";  Psi_7 = " + pstr(psi(7)) + ";  Psi_9 = " + pstr(psi(9)))
ms, ks = kronecker_candidates(100)
say(f"kronecker_candidates(100): {len(ms)} values of m (max {max(ms)}), {len(ks)} values of k (max {max(ks)})")
for N in (101, 199, 397):
    t = time.time()
    c = charpoly_int(two_K(N))
    say(f"timing: exact charpoly of 2K_{N} in {time.time() - t:.2f} s (leading {c[-1]}, constant {c[0]}, value at 2 = {sum(v * 2 ** i for i, v in enumerate(c))})")
say("ALL OK" if ok else "FAILURES")
Path(__file__).with_suffix(".log").write_text("\n".join(out) + "\n", encoding="utf-8")
