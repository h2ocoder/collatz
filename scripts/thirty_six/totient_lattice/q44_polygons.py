"""Q4.4  Geometry to algebra: the lattice point of phi(n) and the construction of the regular n-gon.

Gleason (1988): the regular n-gon is constructible with straightedge, compass and angle
trisector  iff  n = 2^r 3^s p_1 ... p_k with distinct Pierpont primes p_i > 3  iff  phi(n) is
3-smooth.  Write phi(n) = 2^a 3^b.

What the lattice point (a,b) means (proved in the README):
  * Gal(Q(zeta_n)/Q) = (Z/n)* is abelian of order 2^a 3^b: its composition factors are
    a copies of C2 and b copies of C3.
  * the minimal number of trisections in any construction of the n-gon is exactly b.
  * the lattice DECOMPOSITION of (a,b) attached to n (q41_fibre_count.py) is the primary
    decomposition of (Z/n)*: a Pierpont point (i,j) is a cyclic factor C_{2^i} x C_{3^j}, the
    part from 3^beta is C_2 x C_{3^(beta-1)}, the part from 2^alpha is C_2 x C_{2^(alpha-2)}.
    So the partition of b records whether the b trisections are NESTED (one cyclic factor
    C_{3^b}) or INDEPENDENT (several factors).

This script
  1. computes (Z/n)* and the real-subfield group (Z/n)*/{+-1} for the eight n with phi(n) = 36
     by brute force and checks them against the lattice decomposition;
  2. checks the decomposition rule for every n <= 20000 with 3-smooth phi(n);
  3. counts, for small (a,b), how many of the p(a) p(b) abelian group types of order 2^a 3^b
     occur as (Z/n)*;
  4. compares A(a,b) with the Collatz counts on the same lattice: OEIS A100982 (number of
     dropping classes with s odd steps) and the number W(k,s) of not-yet-dropped parity words.

Run:  python -X utf8 q44_polygons.py      (a few seconds)
"""
from __future__ import annotations

import json
import math
import os
import sys
from math import gcd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fibre_decompositions  # noqa: E402
from pierpont import pierpont_points  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q44_polygons.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def partition_from_counts(counts, p):
    """counts[t] = #{g : g^(p^t) = 1}, t = 0, 1, ...; returns the type as a partition."""
    logs = [round(math.log(c, p)) for c in counts]
    conj = [logs[t] - logs[t - 1] for t in range(1, len(logs))]  # number of parts >= t
    parts = []
    for t in range(len(conj), 0, -1):
        m = conj[t - 1] - (conj[t] if t < len(conj) else 0)
        parts += [t] * m
    return tuple(sorted(parts, reverse=True))


def group_types(n, real=False):
    """(2-part, 3-part) of (Z/n)* -- or of (Z/n)*/{+-1} if real -- as partitions, by brute force."""
    units = [g for g in range(1, n) if gcd(g, n) == 1] if n > 1 else [0]
    if real:
        units = [g for g in units if g <= n - g] if n > 2 else units
    res = []
    for p in (2, 3):
        counts, t = [1], 1
        while True:
            e = p ** t
            if real:
                c = sum(1 for g in units if pow(g, e, n) in (1, n - 1))
            else:
                c = sum(1 for g in units if pow(g, e, n) == 1 % n)
            if c == counts[-1]:
                break
            counts.append(c)
            t += 1
        res.append(partition_from_counts(counts + [counts[-1]], p))
    return tuple(res)


def lattice_types(alpha, beta, chosen):
    """(2-part, 3-part) of (Z/n)* predicted from the lattice decomposition."""
    p2 = [i for i, j in chosen]
    p3 = [j for i, j in chosen if j > 0]
    if beta >= 1:
        p2.append(1)
    if beta >= 2:
        p3.append(beta - 1)
    if alpha == 2:
        p2.append(1)
    elif alpha >= 3:
        p2 += [1, alpha - 2]
    return tuple(sorted(p2, reverse=True)), tuple(sorted(p3, reverse=True))


def name(p2, p3):
    f = [f"C{2 ** e}" for e in p2] + [f"C{3 ** e}" for e in p3]
    return " x ".join(f) if f else "1"


def partitions_count(n):
    p = [1] + [0] * n
    for k in range(1, n + 1):
        for m in range(k, n + 1):
            p[m] += p[m - k]
    return p[n]


def main():
    P = pierpont_points(14, 14)

    out("1. THE EIGHT POLYGONS WITH phi(n) = 36 = 2^2 3^2")
    out("   (Z/n)* = Gal(Q(zeta_n)/Q), order 36;  G+ = (Z/n)*/{+-1} = Gal(Q(cos 2pi/n)/Q), order 18.")
    out("     n    lattice parts of (2,2)        (Z/n)*              G+ (real field)     trisections   the two cubic steps")
    for x, alpha, beta, chosen in fibre_decompositions(2, 2, P):
        t = group_types(x)
        assert t == lattice_types(alpha, beta, chosen), (x, t)
        tr = group_types(x, real=True)
        parts = []
        if alpha >= 2:
            parts.append(f"2^{alpha}:({alpha - 1},0)")
        if beta >= 1:
            parts.append(f"3^{beta}:(1,{beta - 1})")
        parts += [f"{(1 << i) * 3 ** j + 1}:({i},{j})" for i, j in chosen]
        kind = "nested (cyclic C9)" if t[1] == (2,) else "independent (C3 x C3)"
        out(f"   {x:>4d}   {' + '.join(parts):<28s}  {name(*t):<18s}  {name(*tr):<18s}       {sum(t[1])}        {kind}")
    out("   group types of order 36: C4xC9, C2xC2xC9, C4xC3xC3, C2xC2xC3xC3;  realised: all but C4 x C3 x C3.")

    out("\n2. THE DECOMPOSITION RULE, checked by brute force for every n <= 20000 with phi(n) 3-smooth")
    checked = 0
    for a in range(0, 15):
        for b in range(0, 10):
            if 2 ** a * 3 ** b > 20000:
                continue
            for x, alpha, beta, chosen in fibre_decompositions(a, b, P):
                if x <= 20000:
                    assert group_types(x) == lattice_types(alpha, beta, chosen), x
                    checked += 1
    out(f"   n checked: {checked}; mismatches: 0")

    out("\n3. HOW MANY GROUP TYPES OF ORDER 2^a 3^b OCCUR AS (Z/n)* ?   entry: realised / p(a) p(b)   [A(a,b)]")
    out("        b=" + "".join(f"{b:>16d}" for b in range(0, 6)))
    for a in range(0, 9):
        row = []
        for b in range(0, 6):
            types = {lattice_types(al, be, ch) for _, al, be, ch in fibre_decompositions(a, b, P)}
            nA = len(fibre_decompositions(a, b, P))
            row.append(f"{len(types)}/{partitions_count(a) * partitions_count(b)} [{nA}]")
        out(f"   a={a:>2d}   " + "".join(f"{r:>16s}" for r in row))
    out("   (the 3-part can be any partition of b only if enough Pierpont points with the right j exist;")
    out("    the 2-part always contains a C2 unless n = 1, 2, so a cyclic 2-part needs a single prime factor)")

    out("\n4. AGAINST THE COLLATZ COUNTS ON THE SAME LATTICE")
    # W(j, s): parity words of length j with s ones, all prefixes not yet dropped (3^s_i > 2^i)
    JMAX = 60
    W = [[0] * (JMAX + 2) for _ in range(JMAX + 2)]
    W[0][0] = 1
    N_of_s = {0: 1}  # the class of even numbers: word '0'
    for j in range(0, JMAX):
        for s in range(0, j + 1):
            w = W[j][s]
            if not w:
                continue
            W[j + 1][s + 1] += w                      # odd step: still above
            if 3 ** s > 2 ** (j + 1):
                W[j + 1][s] += w                      # even step, still above the line
            elif s >= 1:
                N_of_s[s] = N_of_s.get(s, 0) + w      # even step crosses the line: a dropping class
    a100982 = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950, 312455, 663535,
               1900470, 5936673, 13472296, 39993895, 87986917, 257978502, 820236724]
    mine = [N_of_s[s] for s in range(1, 26)]
    out("   N(s) = number of dropping classes (residue classes mod 2^k) with s odd steps, k = floor(s log2 3) + 1:")
    out("     ", mine)
    out("   equals OEIS A100982:", mine == a100982)
    assert mine == a100982
    with open(os.path.join(HERE, "q41_table.json"), encoding="utf-8") as f:
        A = json.load(f)["A"]
    diag = [A[a][a] for a in range(0, 26)]
    out("   A(a,a)  diagonal          :", diag)
    out("   A(a,1)  row b = 1         :", [A[a][1] for a in range(0, 26)])
    out("   A(2,b)  column a = 2      :", [A[2][b] for b in range(0, 26)])
    out("   anti-diagonal sums a+b = n:", [sum(A[a][n - a] for a in range(n + 1)) for n in range(0, 26)])
    stair = [A[int(math.floor(s * math.log2(3))) + 1][s] for s in range(1, 21)]
    out("   A on the Collatz staircase (k(s), s), s = 1..20:", stair)
    out("   A100982, s = 1..20                             :", a100982[:20])
    out("   ratios of consecutive terms:")
    out("     A100982 :", " ".join(f"{a100982[i + 1] / a100982[i]:.2f}" for i in range(4, 24)))
    out("     A(a,a)  :", " ".join(f"{diag[i + 1] / diag[i]:.2f}" for i in range(4, 25)))
    hcrit = -(math.log2(math.log(2) / math.log(3)) * math.log(2) / math.log(3)
              + math.log2(1 - math.log(2) / math.log(3)) * (1 - math.log(2) / math.log(3)))
    out(f"   A100982 grows exponentially: paths hugging the critical slope, limiting ratio 2^(h(log_3 2) log_2 3)"
        f" = {2 ** (hcrit * math.log2(3)):.3f}")
    out(f"   (h = binary entropy, h(log_3 2) = {hcrit:.4f}); geometric mean of the ratios shown: "
        f"{(a100982[24] / a100982[4]) ** (1 / 20):.3f}.  A(a,a) has ratio -> 1 (growth exp(c sqrt)).")
    cand = {"A(a,a)": diag, "row b=1": [A[a][1] for a in range(26)], "col a=2": [A[2][b] for b in range(26)],
            "staircase": stair}
    target = a100982[:12]
    hits = []
    for nm, seq in cand.items():
        for shift in range(0, 6):
            for variant, tr in (("", seq), ("first differences", [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]),
                                ("partial sums", [sum(seq[: i + 1]) for i in range(len(seq))])):
                if tr[shift: shift + 6] == target[:6] or tr[shift: shift + 6] == target[2:8]:
                    hits.append((nm, shift, variant))
    out("   exact matches of 6 consecutive terms between A100982 and A(a,a) / rows / columns / staircase,")
    out("   their first differences or partial sums, at any shift 0..5:", hits if hits else "none")

    out("\n   SUPPORT.  dropping classes sit only on the staircase k = floor(s log2 3) + 1, one cell per s;")
    out("   not-yet-dropped words W(j,s) live strictly on the side 3^s > 2^j;  A(a,b) > 0 on the whole")
    out("   quadrant a >= 1.  W(j,s) for j = 0..12 (rows), s = 0..8 (columns):")
    for j in range(0, 13):
        out("     j=%2d  " % j + " ".join(f"{W[j][s]:>5d}" for s in range(0, 9)))
    out("   A(a,b) on the same cells, a = 0..12 (rows), b = 0..8 (columns):")
    for a in range(0, 13):
        out("     a=%2d  " % a + " ".join(f"{A[a][b]:>5d}" for b in range(0, 9)))


if __name__ == "__main__":
    main()
    LOG.close()
