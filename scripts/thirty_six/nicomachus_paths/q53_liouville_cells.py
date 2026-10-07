"""Q5.3  Liouville's identity on the cells of 2^k 3^s, and a systematic search for
Nicomachus-type identities  sum x^3 = (sum x)^2  among Collatz path counts.

A finite multiset X of positive integers is called a CS-multiset ("cubes-squares";
Mason 2001, Barbeau-Seraj 2013) if  sum_{x in X} x^3 = (sum_{x in X} x)^2.
  * {1,...,n} is CS (Nicomachus);  {tau(d) : d | n} is CS (Liouville);
  * {m, m, ..., m} (m copies of m) is CS;  the product of two CS-multisets is CS.

CONVENTIONS
  * cell (e, s): e = number of EVEN shortcut steps, s = number of ODD shortcut steps; word
    length j = e + s; the cell is the 3-smooth "number" 2^j vs 3^s, i.e. the point (j, s) of
    the exponent lattice.  A prefix is admissible if 2^j' < 3^s' at each of its points
    (j' >= 1), i.e. e' <= floor(s' * log2(3/2)).
  * A(e, s) = number of admissible prefixes ending in cell (e, s).
    N(s) = A(floor(s*theta), s) = OEIS A100982(s).
  * S(j) = sum_{e+s=j} A(e, s) = number of parity words of length j that have not dropped.

Run: python -X utf8 q53_liouville_cells.py     (well under a minute)
Output: q53_liouville_cells.log / .json
"""
import json
import os
from math import comb, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q53_liouville_cells.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


def T(n):
    return n * (n + 1) // 2


def defect(X):
    return sum(x ** 3 for x in X) - sum(X) ** 2


def bfloor(s):
    """floor(s * log2(3/2)) = floor(s*log2 3) - s, exact."""
    return (3 ** s).bit_length() - 1 - s


def tau(n):
    c = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            c += 1 if i * i == n else 2
        i += 1
    return c


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def trivial_kind(X):
    """Classify a CS multiset as one of the known trivial shapes, else 'NON-TRIVIAL'."""
    Y = sorted(X)
    if Y == list(range(1, len(Y) + 1)):
        return "{1..n} (Nicomachus)"
    if len(set(Y)) == 1 and len(Y) == Y[0]:
        return "{m^m} (m copies of m)"
    # tau-multiset of some n?  (product of chains)
    if len(Y) <= 40:
        for n in range(1, 400):
            if sorted(tau(d) for d in divisors(n)) == Y:
                return f"Liouville multiset of n={n}"
    return "NON-TRIVIAL"


def main():
    res = {}
    out("=" * 78)
    out("Q5.3  Liouville on Collatz cells")
    out("=" * 78)

    # ---- 1. Liouville on the grid of 2^k 3^s
    ok = True
    for k in range(0, 41):
        for s in range(0, 41):
            lhs = sum(((i + 1) * (j + 1)) ** 3 for i in range(k + 1) for j in range(s + 1))
            rhs = (T(k + 1) * T(s + 1)) ** 2
            ok &= lhs == rhs
    out("[1] sum_{i<=k, j<=s} ((i+1)(j+1))^3 = (T_(k+1) T_(s+1))^2 for 0 <= k,s <= 40:", ok)
    ok2 = all(sum(tau(d) ** 3 for d in divisors(n)) == sum(tau(d) for d in divisors(n)) ** 2
              for n in range(1, 3001))
    out("    Liouville  sum_{d|n} tau(d)^3 = (sum_{d|n} tau(d))^2  for n <= 3000:", ok2)
    out("    at (k,s) = (2,2), n = 36: sum tau(d)^3 =", sum(tau(d) ** 3 for d in divisors(36)),
        "= 36^2;  sum tau(d) =", sum(tau(d) for d in divisors(36)), "= 36")
    fp = [n for n in range(1, 3001) if sum(tau(d) ** 3 for d in divisors(n)) == n * n]
    out("    n <= 3000 with sum_{d|n} tau(d)^3 = n^2 (equivalently F(n) = n):", fp)
    res["liouville_grid_ok"] = ok
    res["liouville_ok"] = ok2

    # tau_k(p^2 q^2) = T_k^2 = 1^3 + ... + k^3  (number of (k-1)-multichains of the 3x3 grid)
    ok3 = all(comb(k + 1, 2) ** 2 == sum(i ** 3 for i in range(1, k + 1)) for k in range(1, 200))
    out("    tau_k(p^2 q^2) = C(k+1,2)^2 = 1^3 + ... + k^3 for k < 200:", ok3)

    # ---- 2. intervals vs maximal chains of the (k+1) x (s+1) grid
    hits = [(k, s) for k in range(0, 400) for s in range(k, 400)
            if T(k + 1) * T(s + 1) == comb(k + s, k) ** 2]
    out("\n[2] #intervals = (#maximal chains)^2, i.e. T_(k+1) T_(s+1) = C(k+s,k)^2, 0 <= k <= s < 400:", hits)
    hits2 = [(k, s) for k in range(0, 200) for s in range(0, 200) if T(k + 1) * T(s + 1) == 2 ** k * 3 ** s]
    out("    #intervals = n, i.e. T_(k+1) T_(s+1) = 2^k 3^s, 0 <= k,s < 200:", hits2,
        "-> n =", [2 ** k * 3 ** s for k, s in hits2])
    hits3 = [(k, s) for k in range(0, 200) for s in range(0, 200) if comb(k + s, k) == 2 ** k * 3 ** s]
    out("    #maximal chains = n, i.e. C(k+s,k) = 2^k 3^s:", hits3)
    res["intervals_eq_chains_sq"] = hits
    res["intervals_eq_n"] = hits2

    # ---- 3. CS search over Collatz path-count families
    out("\n[3] CS search:  sum x^3 = (sum x)^2  over families of path counts")
    all_hits = []

    def test(family, label, X):
        X = [x for x in X if x > 0]
        if not X:
            return
        if defect(X) == 0:
            all_hits.append((family, label, sorted(X) if len(X) <= 12 else f"{len(X)} values", trivial_kind(X)))

    counts = {}

    def bump(fam):
        counts[fam] = counts.get(fam, 0) + 1

    # (a) all monotone paths to cell (i,j): C(i+j, i), rectangles [0..k] x [0..s]
    KMAX = 40
    for k in range(KMAX + 1):
        for s in range(k, KMAX + 1):
            X = [comb(i + j, i) for i in range(k + 1) for j in range(s + 1)]
            test("all paths, rectangle", (k, s), X)
            bump("all paths, rectangle")
    # (b) Pascal rows (Franel numbers vs 4^n) and Pascal triangles
    for n in range(0, 301):
        test("all paths, Pascal row", n, [comb(n, i) for i in range(n + 1)])
        bump("all paths, Pascal row")
    for n in range(0, 81):
        test("all paths, triangle i+j<=n", n, [comb(m, i) for m in range(n + 1) for i in range(m + 1)])
        bump("all paths, triangle i+j<=n")

    # (c) admissible prefix triangle
    SMAX = 220
    A = [[1]]                       # row s = 0: only e = 0
    for s in range(1, SMAX + 1):
        prev = A[-1]
        b = bfloor(s)
        row = []
        run = 0
        for e in range(b + 1):
            # A(e,s) = A(e,s-1) [O-step, needs e <= b_(s-1)] + A(e-1,s) [E-step]
            up = prev[e] if e < len(prev) else 0
            left = row[e - 1] if e >= 1 else 0
            row.append(up + left)
        A.append(row)
    N = [None] + [A[s][bfloor(s)] for s in range(1, SMAX + 1)]
    assert N[1:14] == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045], N[1:14]
    out("    admissible-prefix triangle A(e,s), rows s = 0..7:")
    for s in range(0, 8):
        out(f"      s={s}: {A[s]}")
    for s in range(0, SMAX + 1):
        test("admissible, row s", s, A[s])
        bump("admissible, row s")
    for e in range(0, 100):
        col = [A[s][e] for s in range(0, SMAX + 1) if e < len(A[s])]
        for upto in range(1, min(len(col), 60) + 1):
            test("admissible, column e (first m cells)", (e, upto), col[:upto])
            bump("admissible, column e (first m cells)")
    JMAX = 200
    S = []
    diag = []
    for j in range(0, JMAX + 1):
        d = [A[s][j - s] for s in range(0, min(j, SMAX) + 1) if 0 <= j - s < len(A[s])]
        diag.append(d)
        S.append(sum(d))
        test("admissible, antidiagonal j (words of length j)", j, d)
        bump("admissible, antidiagonal j (words of length j)")
    out("    S(j) = #admissible prefixes of length j, j = 0..20:", S[:21])
    for smax in range(0, 120):
        test("admissible, all cells with s <= S", smax, [x for s in range(smax + 1) for x in A[s]])
        bump("admissible, all cells with s <= S")
    for jmax in range(0, 120):
        test("admissible, all cells with j <= J", jmax, [x for j in range(jmax + 1) for x in diag[j]])
        bump("admissible, all cells with j <= J")
    # (c') divisor-lattice rectangles of 2^j 3^s weighted by A (cells (j', s') with j' <= j, s' <= s)
    for jj in range(0, 60):
        for ss in range(0, 40):
            X = [A[s][j - s] for s in range(0, ss + 1) for j in range(s, jj + 1) if 0 <= j - s < len(A[s])]
            test("admissible, divisor rectangle of 2^j 3^s", (jj, ss), X)
            bump("admissible, divisor rectangle of 2^j 3^s")

    # (d) windows of A100982 and of S(j)
    for a in range(1, SMAX + 1):
        for b in range(a, SMAX + 1):
            test("A100982 window [a..b]", (a, b), N[a:b + 1])
            bump("A100982 window [a..b]")
    for a in range(0, JMAX + 1):
        for b in range(a, JMAX + 1):
            test("S(j) window [a..b]", (a, b), S[a:b + 1])
            bump("S(j) window [a..b]")

    out("\n    families tested (number of multisets):")
    for fam, c in counts.items():
        out(f"      {fam:<50} {c:>7}")
    out(f"\n    CS hits: {len(all_hits)}   (grouped by family and shape; up to 3 examples each)")
    groups = {}
    for h in all_hits:
        groups.setdefault((h[0], h[3]), []).append(h)
    nontriv = 0
    for (fam, kind), hs in groups.items():
        out(f"      {fam:<50} {kind:<24} x{len(hs)}")
        for h in hs[:3]:
            out(f"          label {h[1]}: {h[2]}")
        if kind == "NON-TRIVIAL":
            nontriv += len(hs)
    out(f"    non-trivial hits: {nontriv}")
    out("    (column e = 1 of the admissible triangle is A(1,s) = s-1 for s >= 2: the single even step can")
    out("     sit after any of the ones number 2..s.  Its initial segments are literally {1,...,m}.)")
    col1 = [A[s][1] for s in range(2, 60)]
    assert col1 == list(range(1, 59))
    res["cs_tests"] = counts
    res["cs_hits"] = [[str(x) for x in h] for h in all_hits]
    res["cs_nontrivial"] = nontriv

    # ---- 4. near misses: is sum x^3 at least a perfect square for the natural families?
    out("\n[4] weaker test: is sum x^3 a perfect square? (rows of the admissible triangle, s <= 220)")
    sq_rows = [s for s in range(0, SMAX + 1) if isqrt(sum(x ** 3 for x in A[s])) ** 2 == sum(x ** 3 for x in A[s])]
    out("    rows s with sum of cubes a perfect square:", sq_rows)
    sqN = [(a, b) for a in range(1, 80) for b in range(a + 1, 80)
           if isqrt(sum(x ** 3 for x in N[a:b + 1])) ** 2 == sum(x ** 3 for x in N[a:b + 1])]
    out("    windows [a..b] (a<b<80) of A100982 with sum of cubes a perfect square:", sqN)
    res["rows_cubesum_square"] = sq_rows
    res["windows_cubesum_square"] = sqN

    json.dump(res, open(os.path.join(HERE, "q53_liouville_cells.json"), "w"), indent=1)
    out("\nwrote q53_liouville_cells.json")


if __name__ == "__main__":
    main()
    LOG.close()
