"""Skeptic check 2: Q1.2 (why 3; the half-eigenvalue functional).

Independent code path:
 * Theorem 6 is tested from the OTHER side: for every k <= 1500 decide whether 2^k - 1 or
   2^k + 1 is a perfect power q^s with s >= 2 (integer roots), which covers every odd q at once.
 * Cycle search by Brent's algorithm (their code uses a dictionary of visited values).
 * Kernel statements with EXACT arithmetic over Q: fraction-free (Bareiss) determinants of
   integer matrices and exact characteristic polynomials (sympy), no floating point.

Convention: shortcut map T_q(n) = n/2 (even), (q n + 1)/2 (odd) on Z.
Signed kernel on Z/p:  (K^- f)(x) = ( f(x/2) - f((q x + 1)/2) ) / 2.
Output: v2_why_three.log
"""
import os
from fractions import Fraction
from math import gcd

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v2_why_three.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Theorem 6 from the other side: 2^k -+ 1 = q^s with s >= 2, all k <= 1500")
out("=" * 78)


def iroot(n, r):
    """floor(n^(1/r)) by Newton on integers."""
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + r - 1) // r)
    while True:
        y = ((r - 1) * x + n // x ** (r - 1)) // r
        if y >= x:
            return x
        x = y


powers = []
for k in range(1, 1501):
    for N in ((1 << k) - 1, (1 << k) + 1):
        if N < 9:
            continue
        # only prime exponents need testing
        for r in sp.primerange(2, N.bit_length() + 1):
            if r > N.bit_length() / 1.58 + 1:      # q >= 3 so s <= log_3 N
                break
            q = iroot(N, r)
            if q ** r == N:
                powers.append((k, N, q, r))
out("perfect powers among 2^k - 1, 2^k + 1 (k <= 1500):", powers)
assert powers == [(3, 9, 3, 2)]
out("  -> the only unit cell with s >= 2, for ANY odd q, is (q,k,s) = (3,3,2).  Agrees with Theorem 6.")

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. Brent cycle search for T_q, odd q <= 201, starts |n| <= 3000 (cap 10^30, 4000 steps)")
out("=" * 78)


def T(n, q):
    return n // 2 if n % 2 == 0 else (q * n + 1) // 2


def brent(n0, q, cap=10 ** 30, max_steps=4000):
    """Return an element of the cycle reached from n0 and its length, or None."""
    power = lam = 1
    tort = n0
    hare = T(n0, q)
    steps = 0
    while tort != hare:
        if power == lam:
            tort = hare
            power *= 2
            lam = 0
        hare = T(hare, q)
        lam += 1
        steps += 1
        if abs(hare) > cap or steps > max_steps:
            return None
    return hare, lam


nonunit = []
unit_seen = {}
only_zero = 0
for q in range(3, 202, 2):
    cyc = {}
    for n0 in range(-3000, 3001):
        r = brent(n0, q)
        if r is None:
            continue
        x, lam = r
        orb = [x]
        for _ in range(lam - 1):
            orb.append(T(orb[-1], q))
        if not any(abs(z) <= 3000 for z in orb):
            continue
        cyc[frozenset(orb)] = orb
    if len(cyc) == 1:
        only_zero += 1
    for orb in cyc.values():
        k = len(orb)
        s = sum(1 for z in orb if z % 2)
        D = 2 ** k - q ** s
        m = min(orb, key=abs)
        if abs(D) == 1:
            unit_seen.setdefault(q, []).append((k, s, D, m))
        else:
            nonunit.append((q, m, k, s, D))
out("cycles NOT in unit cells (q, min|n|, k, s, D):", sorted(nonunit))
assert sorted(nonunit) == sorted([(3, -17, 11, 7, -139), (5, 1, 5, 2, 7), (5, 13, 7, 3, 3),
                                  (5, 17, 7, 3, 3), (181, 27, 15, 2, 7), (181, 35, 15, 2, 7)])
out(f"multipliers whose only cycle found is {{0}}: {only_zero} of 100")
multi = {q: sorted(v) for q, v in unit_seen.items() if len(v) > 1}
out("multipliers with more than one unit-cell cycle:", multi)
for q, v in multi.items():
    pred = [(1, 0)]
    if (q + 1) & q == 0:
        pred.append(((q + 1).bit_length() - 1, 1))
    if (q - 1) & (q - 2) == 0:
        pred.append(((q - 1).bit_length() - 1, 1))
    if q == 3:
        pred.append((3, 2))
    assert sorted((k, s) for k, s, _, _ in v) == sorted(set(pred)), q
out("  -> agrees with the researcher's list.  Prior art: the q = 181 cycle 27 -> 611 -> 27 is in Crandall")
out("     (1978); Franco-Pomerance (1995) classify the multipliers |q| < 10^11 having an orbit with two")
out("     odd elements (5 and 181 on this side); the 5x+1 cycles through 13 and 17 are standard.")

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Signed kernel: is -1/2 an eigenvalue?  det(I + R_e - R_o) = 0, primes 5 <= p < 300")
out("   (their range: p < 100, det mod 2^61-1)")
out("=" * 78)


def bareiss_det(M):
    n = len(M)
    M = [row[:] for row in M]
    sign = 1
    prev = 1
    for c in range(n - 1):
        if M[c][c] == 0:
            sw = next((r for r in range(c + 1, n) if M[r][c] != 0), None)
            if sw is None:
                return 0
            M[c], M[sw] = M[sw], M[c]
            sign = -sign
        for r in range(c + 1, n):
            for cc in range(c + 1, n):
                M[r][cc] = (M[r][cc] * M[c][c] - M[r][c] * M[c][cc]) // prev
            M[r][c] = 0
        prev = M[c][c]
    return sign * M[n - 1][n - 1]


def branch_matrix(p, num, const, den, sign):
    """Integer matrix R_e + sign*R_o on Z/p for e(x) = x/den, o(x) = (num x + const)/den."""
    inv = pow(den, -1, p)
    M = [[0] * p for _ in range(p)]
    for x in range(p):
        M[x][x * inv % p] += 1
        M[x][(num * x + const) * inv % p] += sign
    return M


import numpy as np

P1, P2 = 2147483647, 2147483629          # two 31-bit primes (products fit in int64)


def det_mod_np(M, P):
    A = np.array(M, dtype=np.int64) % P
    n = A.shape[0]
    det = 1
    for c in range(n):
        nz = np.nonzero(A[c:, c])[0]
        if nz.size == 0:
            return 0
        piv = c + int(nz[0])
        if piv != c:
            A[[c, piv]] = A[[piv, c]]
            det = -det
        pv = int(A[c, c])
        det = det * pv % P
        inv = pow(pv, P - 2, P)
        f = (A[c + 1:, c] * inv) % P
        A[c + 1:, c:] = (A[c + 1:, c:] - (f[:, None] * A[c, c:][None, :]) % P) % P
    return det % P


def singular(M, exact_limit=61):
    """True iff det(M) = 0: zero modulo two 31-bit primes, and for small sizes also exactly."""
    z = det_mod_np(M, P1) == 0 and det_mod_np(M, P2) == 0
    if z and len(M) <= exact_limit:
        assert bareiss_det(M) == 0
    if not z and len(M) <= 31:
        assert bareiss_det(M) != 0
    return z


primes = list(sp.primerange(5, 300))
their = {5: [11, 13, 17, 29, 31], 7: [11, 19, 23], 9: [5, 19], 11: [13, 19, 29, 31],
         13: [5, 19, 31, 37, 41, 59], 15: [11, 17, 19, 43, 47], 17: [7, 11, 47, 59],
         31: [7, 13, 17, 23], 33: [5, 17, 19, 97], 63: [5, 11, 13, 17, 19, 29, 37], 65: [17, 31],
         127: [11, 19, 29, 31, 37], 129: [5, 7, 11, 13, 19, 31]}
out("  q : primes p < 300 (p not dividing 2q) with det(I + R_e - R_o) = 0")
out("      (zero modulo two 31-bit primes; confirmed by exact Bareiss determinant for p <= 61)")
for q in (3, 5, 7, 9, 11, 13, 15, 17, 31, 33, 63, 65, 127, 129):
    yes = []
    tested = 0
    for p in primes:
        if q % p == 0:
            continue
        tested += 1
        M = branch_matrix(p, q, 1, 2, -1)
        for i in range(p):
            M[i][i] += 1
        if singular(M):
            yes.append(p)
    residue = [p for p in yes if (q - 3) % p == 0]
    out(f"  {q:3d}: {len(yes)} of {tested}" + ("  (all)" if len(yes) == tested else f"  yes = {yes}")
        + (f"   [of these, p | q-3: {residue}]" if q != 3 else ""))
    if q == 3:
        assert len(yes) == tested
    else:
        assert [p for p in yes if p < 100] == their[q], (q, yes)
out("  NOTE (skeptic): K^-_p depends on q only through q mod p.  So 'the yes-list contains the primes")
out("  dividing q - 3' is automatic (the matrix IS the q = 3 matrix there); it is not an independent")
out("  confirmation of Proposition 7.  The remaining 'sporadic' primes are the content, and they are")
out("  unexplained by the proposition.")
# verify the note
for (q, p) in ((13, 5), (17, 7), (31, 7), (33, 5), (63, 5), (65, 31), (129, 7)):
    assert branch_matrix(p, q, 1, 2, -1) == branch_matrix(p, 3, 1, 2, -1)

# ------------------------------------------------------------------ 4
out("")
out("=" * 78)
out("4. Universal eigenvalues, exactly: gcd over several primes of the characteristic")
out("   polynomials of 2K^- = R_e - R_o and 2K = R_e + R_o  (sympy, over Q)")
out("=" * 78)
x = sp.symbols("x")


def charpoly_int(M):
    return sp.Matrix(M).charpoly(x).as_expr()


def universal(q, sign, plist):
    g = None
    for p in plist:
        if (2 * q * (q - 1) * (q - 2)) % p == 0:
            continue
        cp = sp.Poly(charpoly_int(branch_matrix(p, q, 1, 2, sign)), x)
        g = cp if g is None else sp.gcd(g, cp)
    return sp.factor(g.as_expr())


plist = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
for q in (3, 5, 7, 9, 15, 17, 31, 33):
    gm = universal(q, -1, plist)
    gp = universal(q, +1, plist)
    out(f"  q = {q:3d}: gcd charpoly(2K^-) = {gm};   gcd charpoly(2K) = {gp}")
out("  (eigenvalue of K = root / 2.)  q = 3: the common factor of 2K^- contains (x + 1), i.e. -1/2;")
out("  for the other q only powers of x (and x - 2, i.e. eigenvalue 1 of K) are common.  Agrees.")

# ------------------------------------------------------------------ 5
out("")
out("=" * 78)
out("5. NEW (skeptic): the functional exists for every word in a unit cell with D = -1, and for")
out("   no word in a unit cell with D = +1.")
out("   Two-branch signed kernel  (K^-_w f)(x) = ( f(x/2^k) - f(T_w(x)) ) / 2,  T_w(x) = (N x + C)/2^k,")
out("   N = 3^s.  Let x_w = C/(2^k - N) (fixed point of T_w), a = -C/(N - 1) (where the branches agree).")
out("   Then x_w/2^k = a  <=>  (2^k - 1)(2^k + 1 - N) = 0  <=>  N = 2^k + 1  <=>  D = -1,")
out("   and in that case (delta_a - delta_{x_w}) K^-_w = -(1/2)(delta_a - delta_{x_w}),")
out("   a non-zero functional for every prime p not dividing 6*C*(2^k - 1).")
out("=" * 78)
cases = [("q=3 cell (1,1) word 1   (3 = 2+1), x_w = -1", 3, 1, 2),
         ("q=3 cell (3,2) word 110 (9 = 8+1), x_w = -5", 9, 5, 8),
         ("q=3 cell (3,2) word 101,           x_w = -7", 9, 7, 8),
         ("q=3 cell (3,2) word 011,           x_w = -10", 9, 10, 8),
         ("q=3 cell (2,1) word 10  (3 = 4-1), x_w = +1", 3, 1, 4),
         ("q=3 cell (2,1) word 01,            x_w = +2", 3, 2, 4),
         ("q=5 cell (2,1) word 10  (5 = 4+1), x_w = -1", 5, 1, 4),
         ("q=7 cell (3,1) word 100 (7 = 8-1), x_w = +1", 7, 1, 8),
         ("q=3 cell (11,7) word of -17 (D = -139)", 2187, 2363, 2048),
         ("q=3 cell (5,3) word 11100 (D = +5), x_w = 19/5", 27, 19, 32)]
pl = [p for p in sp.primerange(5, 200)]
for name, N, C, den in cases:
    D = den - N
    xw = Fraction(C, D)
    a = Fraction(-C, N - 1)
    functional = (xw / den == a)
    yes = tested = 0
    degenerate = []
    for p in pl:
        if (den * N * (N - 1) * D) % p == 0:
            continue
        M = branch_matrix(p, N, C, den, -1)
        for i in range(p):
            M[i][i] += 1
        z = singular(M)
        if (C * (den - 1)) % p == 0:
            # x_w = a mod p: the two-point functional is zero there
            degenerate.append((p, z))
            continue
        tested += 1
        yes += z
    out(f"  {name}: D = {D:+d}; x_w/2^k == a: {functional};  -1/2 in spectrum at {yes} of {tested} primes"
        + (f";  degenerate primes p | C(2^k-1) (p, eigenvalue present?): {degenerate}" if degenerate else ""))
    if D == -1:
        assert functional and yes == tested
    else:
        assert not functional and yes < tested
out("  (Primes dividing C*(2^k - 1) are set aside: there x_w = a mod p and the functional vanishes.)")
out("  So the repo's 'q = d + 1' criterion (memory note AZ'': pairs (3,2), (5,4), (9,8), (17,16) ...)")
out("  is exactly 'the one-word cell is a unit cell with D = -1'.  Of the three non-trivial unit cells")
out("  of q = 3, the two with D = -1, (1,1) and (3,2), carry the functional, anchored at the negative")
out("  cycles -1 and -5; the D = +1 cell (2,1) (cycle {1,2}) does not.  Residue-only statement:")
out("  it sees 9 = 8 + 1, not the sign of the integers (3x-1 has the same kernels up to x -> -x).")

LOG.close()
