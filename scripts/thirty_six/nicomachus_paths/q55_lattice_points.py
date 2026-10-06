"""Q5.5  Counting lattice points instead of paths.  Low priority; cheap; expected null.

Exact identities checked
  * pi_3(x) = #{2^a 3^b <= x}.  With alpha = log2 3:
        pi_3(2^K) = sum_{b=0}^{floor(K/alpha)} (K + 1 - ceil(b*alpha))   (a Beatty sum)
    For alpha = 1 this would be T_(K+1): pi_3 is the "triangular number with slope alpha".
  * cells under the critical line: G(S) = sum_{s=1}^{S} (floor(s*alpha) + 1) = number of
    (j, s), 1 <= s <= S, 0 <= j, with 2^j < 3^s.
  * Ramanujan: pi_3(x) ~ ln(2x) ln(3x) / (2 ln 2 ln 3).

Then: does 36 = T_8 appear in any of these counts for a structural reason?

Run: python -X utf8 q55_lattice_points.py     (seconds)
"""
import json
import os
from math import isqrt, log

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q55_lattice_points.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


def fl(s):          # floor(s log2 3)
    return (3 ** s).bit_length() - 1 if s > 0 else 0


def ce(s):          # ceil(s log2 3)
    return fl(s) + 1 if s > 0 else 0


def pi3(x):
    c = 0
    p3 = 1
    while p3 <= x:
        c += (x // p3).bit_length()        # number of a >= 0 with 2^a <= x / 3^b
        p3 *= 3
    return c


def is_tri(m):
    r = isqrt(8 * m + 1)
    return r * r == 8 * m + 1


def is_sq(m):
    r = isqrt(m)
    return r * r == m


def main():
    res = {}
    out("=" * 78)
    out("Q5.5  lattice-point counts")
    out("=" * 78)
    smooth = sorted(2 ** a * 3 ** b for a in range(40) for b in range(26) if 2 ** a * 3 ** b <= 10 ** 9)
    out("3-smooth numbers <= 100:", [x for x in smooth if x <= 100])
    out("pi_3(36) =", pi3(36), " (36 is the 14th 3-smooth number);  number of divisors of 36 =", 9)
    ram = log(2 * 36) * log(3 * 36) / (2 * log(2) * log(3))
    out(f"Ramanujan estimate at x = 36: {ram:.3f}  (actual 14)")

    # Beatty-sum identity
    ok = True
    for K in range(0, 400):
        lhs = pi3(2 ** K)
        b = 0
        rhs = 0
        while 3 ** b <= 2 ** K:
            rhs += K + 1 - ce(b)
            b += 1
        ok &= lhs == rhs
    out("\nBeatty-sum identity pi_3(2^K) = sum_b (K + 1 - ceil(b log2 3)), K < 400:", ok)
    res["beatty_identity_ok"] = ok

    A = [pi3(2 ** K) for K in range(0, 200)]
    B = [pi3(3 ** S) for S in range(0, 200)]
    G = [sum(fl(s) + 1 for s in range(1, S + 1)) for S in range(0, 200)]
    H = [sum(fl(s) - s + 1 for s in range(0, S + 1)) for S in range(0, 200)]   # admissible cells (e,s), s<=S
    out("\npi_3(2^K), K = 0..15:", A[:16])
    out("pi_3(3^S), S = 0..12:", B[:13])
    out("G(S) = #{(j,s): 1<=s<=S, 2^j < 3^s}, S = 0..12:", G[:13])
    out("H(S) = #{admissible cells (e,s), s<=S},  S = 0..12:", H[:13])

    def report(name, seq):
        tri = [(i, v) for i, v in enumerate(seq) if is_tri(v)]
        sq = [(i, v) for i, v in enumerate(seq) if is_sq(v)]
        has36 = [i for i, v in enumerate(seq) if v == 36]
        # expected number of triangular hits for a "random" increasing sequence of this growth:
        # sum over terms of (density of triangular numbers near v) = sum 1/sqrt(2 v)
        exp_tri = sum((2 * v) ** -0.5 for v in seq if v > 0)
        exp_sq = sum(0.5 * v ** -0.5 for v in seq if v > 0)
        out(f"  {name}: index where value = 36: {has36};")
        out(f"      triangular values (first 200 terms): {tri[:10]}  [{len(tri)} hits, ~{exp_tri:.1f} expected by chance]")
        out(f"      square values: {sq[:10]}  [{len(sq)} hits, ~{exp_sq:.1f} expected by chance]")
        return {"has36": has36, "n_tri": len(tri), "exp_tri": round(exp_tri, 2), "n_sq": len(sq), "exp_sq": round(exp_sq, 2)}

    out("\nDoes 36 (or any triangular / square number) occur more often than chance?")
    res["A"] = report("pi_3(2^K)", A)
    res["B"] = report("pi_3(3^S)", B)
    res["G"] = report("G(S)", G)
    res["H"] = report("H(S)", H)
    out("\n  G(6) = 2+4+5+7+8+10 = 36: the six shortest dropping-word lengths A020914(1..6) add up to 36.")
    out("  No mechanism: G is a Beatty sum ~ alpha S^2/2 and hits a square/triangular number about as")
    out("  often as chance predicts.  LABEL: numerology.")
    out("\n  The only exact 'T_8' statement is the trivial one: #{(a,b) : a, b >= 0, a + b <= 7} = T_8 = 36,")
    out("  i.e. 36 is the number of 3-smooth numbers with at most 7 prime factors counted with multiplicity.")
    cnt = sum(1 for a in range(8) for b in range(8) if a + b <= 7)
    out("  check:", cnt)
    json.dump(res, open(os.path.join(HERE, "q55_lattice_points.json"), "w"), indent=1)
    out("\nwrote q55_lattice_points.json")


if __name__ == "__main__":
    main()
    LOG.close()
