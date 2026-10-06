"""Q1.2  Why 3?  Unit cells of the family T_q(n) = n/2 | (q n + 1)/2, q odd.

Convention: shortcut map on Z; cell (k, s), D = 2^k - q^s, x(w) = C_q(w)/D.
Output: q12_why_three.log, q12_why_three.json
"""
import json
import os
from fractions import Fraction

import numpy as np

from hc_common import (T, Tee, fixed_point, is_primitive, necklace_rep, orbit,
                       parity_word, word_constant, words)

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q12_why_three.log"))
J = {}

# ---------------------------------------------------------------- A
out("=" * 78)
out("A. Unit cells |2^k - q^s| = 1 (k >= 1, 0 <= s <= k) for odd q in [3, 2001], s <= 150")
out("=" * 78)
QMAX = 2001
SMAX = 150
found = {}
for q in range(3, QMAX + 1, 2):
    cells = []
    qs = 1
    for s in range(0, SMAX + 1):
        # the only candidates are k = bitlength-1 and bitlength of q^s
        for k in {qs.bit_length() - 1, qs.bit_length()}:
            if k >= 1 and k >= s and abs((1 << k) - qs) == 1:
                cells.append((k, s, (1 << k) - qs))
        qs *= q
    found[q] = sorted(set(cells))


def predicted(q):
    cells = [(1, 0, 1)]
    # s = 1: q = 2^k - 1 (D = +1) or q = 2^k + 1 (D = -1)
    if (q + 1) & q == 0:
        cells.append(((q + 1).bit_length() - 1, 1, 1))
    if (q - 1) & (q - 2) == 0:
        cells.append(((q - 1).bit_length() - 1, 1, -1))
    if q == 3:
        cells.append((3, 2, -1))
    return sorted(set(cells))


mismatch = [q for q in found if found[q] != predicted(q)]
out(f"multipliers checked: {len(found)};  mismatches with the theorem's prediction: {mismatch}")
assert not mismatch
by_count = {}
for q, cells in found.items():
    by_count.setdefault(len(cells), []).append(q)
for n in sorted(by_count):
    qs_ = by_count[n]
    out(f"  {n} unit cell(s): {len(qs_)} multipliers" + (f"  -> q = {qs_}" if len(qs_) <= 25 else ""))
J["unit_cell_count_by_q"] = {str(n): (v if len(v) <= 25 else len(v)) for n, v in by_count.items()}
J["unit_cells_special_q"] = {str(q): found[q] for q in found if len(found[q]) > 1}

# ---------------------------------------------------------------- B
out("")
out("=" * 78)
out("B. Every word of every unit cell is the parity word of an integer cycle of T_q")
out("=" * 78)
n_words = 0
for q, cells in found.items():
    for (k, s, D) in cells:
        if k > 40:
            continue
        for w in words(k, s):
            x = fixed_point(w, q)
            assert x.denominator == 1
            pw, back = parity_word(int(x), k, q)
            assert pw == w and back == int(x)
            n_words += 1
out(f"words verified by direct iteration: {n_words}")
out("")
out("  q    cell   D   cycle (starting at the smallest |n| odd element)")
shown = 0
rows = []
for q in sorted(found):
    if len(found[q]) < 2:
        continue
    for (k, s, D) in found[q]:
        if s == 0:
            continue
        w = tuple([1] * s + [0] * (k - s))
        x = int(fixed_point(w, q))
        orb = orbit(x, k, q)
        rows.append({"q": q, "cell": [k, s], "D": D, "cycle": orb})
        if q <= 129:
            out(f"  {q:4d} ({k},{s})  {D:+d}  {orb}")
J["unit_cell_cycles"] = rows

# ---------------------------------------------------------------- C
out("")
out("=" * 78)
out("C. Brute force: all cycles of T_q meeting [-3000, 3000], odd q <= 201")
out("   (trajectory abandoned after 3000 steps or when |n| > 10^40)")
out("=" * 78)


def find_cycles(q, B=3000, max_steps=3000, cap=10 ** 40):
    cycles = {}
    resolved = set()
    for n0 in range(-B, B + 1):
        path = []
        seen = {}
        n = n0
        hit = None
        for i in range(max_steps):
            if n in resolved:
                break
            if n in seen:
                hit = seen[n]
                break
            if abs(n) > cap:
                break
            seen[n] = i
            path.append(n)
            n = T(n, q)
        if hit is not None:
            cyc = path[hit:]
            m = min(cyc, key=lambda z: (abs(z), z))
            i0 = cyc.index(m)
            cyc = cyc[i0:] + cyc[:i0]
            cycles[frozenset(cyc)] = cyc
        resolved.update(path)
    return list(cycles.values())


bf = {}
for q in range(3, 202, 2):
    cyc_list = find_cycles(q)
    recs = []
    for cyc in cyc_list:
        k = len(cyc)
        s = sum(1 for z in cyc if z % 2)
        D = 2 ** k - q ** s
        recs.append({"min": cyc[0], "k": k, "s": s, "D": D, "unit": abs(D) == 1,
                     "cycle": cyc if k <= 16 else cyc[:16] + ["..."]})
    bf[q] = sorted(recs, key=lambda r: (r["k"], r["min"]))
J["brute_force_cycles"] = {str(q): v for q, v in bf.items()}
out("  q   #cycles   cycles as (min element; cell (k,s); D)   [U] = unit cell")
for q in sorted(bf):
    recs = bf[q]
    if q <= 33 or len(recs) > 1:
        desc = ", ".join(f"({r['min']}; ({r['k']},{r['s']}); D={r['D']}{' [U]' if r['unit'] else ''})"
                         for r in recs)
        out(f"  {q:3d}  {len(recs)}  {desc}")
only_zero = [q for q in bf if len(bf[q]) == 1]
out(f"  multipliers q <= 201 whose only cycle found is {{0}}: {len(only_zero)} of {len(bf)}")
# every unit cell cycle must have been found, and every found cycle in a unit cell is predicted
for q in bf:
    got = {(r["k"], r["s"]) for r in bf[q] if r["unit"]}
    want = {(k, s) for k, s, _ in found[q]}
    assert got == want, (q, got, want)
out("  check: for every q <= 201 the cycles found in unit cells are exactly the predicted ones.")
non_unit = [(q, r["min"], r["k"], r["s"], r["D"]) for q in bf for r in bf[q] if not r["unit"]]
out(f"  cycles NOT in unit cells ('divisibility accidents'), (q, min, k, s, D): {non_unit}")
J["non_unit_cycles"] = non_unit

# ---------------------------------------------------------------- D
out("")
out("=" * 78)
out("D. Link to the repo's half-eigenvalue theorem (signed Terras kernel mod p)")
out("   K^-_p f(x) = (1/2) f(x/2) - (1/2) f((q x + 1)/2)  on Z/p.")
out("   Test: is -1/2 an eigenvalue, i.e. det(I + R_e - R_o) = 0 ?  (exact, mod 2^61-1)")
out("=" * 78)
P = (1 << 61) - 1


def det_mod(M, P):
    n = len(M)
    M = [row[:] for row in M]
    det = 1
    for c in range(n):
        piv = None
        for r in range(c, n):
            if M[r][c] % P:
                piv = r
                break
        if piv is None:
            return 0
        if piv != c:
            M[c], M[piv] = M[piv], M[c]
            det = -det
        det = det * M[c][c] % P
        inv = pow(M[c][c], P - 2, P)
        for r in range(c + 1, n):
            if M[r][c] % P:
                f = M[r][c] * inv % P
                Mr, Mc = M[r], M[c]
                for cc in range(c, n):
                    Mr[cc] = (Mr[cc] - f * Mc[cc]) % P
    return det % P


def signed_matrix(p, q, sign=-1):
    """Integer matrix of I*0 + R_e + sign*R_o (so 2K^- for sign = -1, 2K for +1)."""
    inv2 = pow(2, p - 2, p)
    M = [[0] * p for _ in range(p)]
    for x in range(p):
        M[x][x * inv2 % p] += 1
        M[x][(q * x + 1) * inv2 % p] += sign
    return M


primes = [p for p in range(5, 100) if all(p % d for d in range(2, int(p ** 0.5) + 1))]
qs_test = [3, 5, 7, 9, 11, 13, 15, 17, 31, 33, 63, 65, 127, 129]
out("  q : primes p < 100 (p not dividing 2q) at which -1/2 is an eigenvalue of K^-_p")
half_table = {}
for q in qs_test:
    yes, no = [], []
    for p in primes:
        if q % p == 0:
            continue
        M = signed_matrix(p, q, -1)
        for i in range(p):
            M[i][i] += 1
        (yes if det_mod(M, P) == 0 else no).append(p)
    half_table[q] = {"yes": yes, "no": no}
    out(f"  {q:3d} : yes at {len(yes)} of {len(yes)+len(no)} primes"
        + (f"  (all)" if not no else f"  yes = {yes}"))
J["minus_half_eigenvalue_of_signed_kernel"] = {str(q): v for q, v in half_table.items()}
assert not half_table[3]["no"]

out("")
out("  Universal eigenvalues (numerical): values that are eigenvalues of the kernel for")
out("  EVERY prime 7 <= p < 100 not dividing 2q(q-1)(q-2), tolerance 1e-7")
univ = {}
for q in qs_test:
    for sign, name in ((-1, "K^-"), (+1, "K")):
        common = None
        used = 0
        for p in primes:
            if p < 7 or (2 * q * (q - 1) * (q - 2)) % p == 0:
                continue
            A = np.array(signed_matrix(p, q, sign), dtype=float) / 2.0
            ev = np.linalg.eigvals(A)
            used += 1
            if common is None:
                common = list(ev)
            else:
                common = [z for z in common if np.min(np.abs(ev - z)) < 1e-7]
        # dedupe
        ded = []
        for z in common:
            if all(abs(z - y) > 1e-6 for y in ded):
                ded.append(z)
        ded = sorted({(round(z.real, 6) + 0.0, round(z.imag, 6) + 0.0) for z in ded})
        univ[f"{q}:{name}"] = ded
        out(f"  q = {q:3d}  {name:3s}: {ded}   ({used} primes)")
J["universal_eigenvalues"] = univ

out("")
out("  Geometry behind the theorem for general q (d = 2):")
out("    fixed point of the odd branch      x_o = -1/(q-2)   (cell (1,1), D = 2 - q)")
out("    point where the two branches agree a   = -1/(q-1)")
out("    the functional delta_a - delta_{x_o} is a left eigenvector of K^- with eigenvalue")
out("    -1/2  iff  e(x_o) = a  iff  2(q-2) = q-1  iff  q = 3.")
for q in (3, 5, 7, 9):
    xo = Fraction(-1, q - 2)
    a = Fraction(-1, q - 1)
    out(f"    q = {q}: x_o = {xo}, e(x_o) = {xo/2}, a = {a}, e(x_o) == a: {xo/2 == a}")

with open(os.path.join(HERE, "q12_why_three.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q12_why_three.json")
out.close()
