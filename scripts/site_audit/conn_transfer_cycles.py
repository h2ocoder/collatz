"""Audit check for site/connections/hilbert-polya.md, part 2.

The page's operator (the reading that reproduces its numbers) has ONE non-zero entry per
column: column x carries weight 2 at row x/2 (x even, halving the representative in 0..M-1)
or weight 1/n at row (n x + 1) mod M (x odd).  It is the weighted adjacency matrix of a
deterministic map phi on {0..M-1}.  For such a matrix the non-zero eigenvalues are exactly
the L-th roots of the weight product around each cycle of phi of length L.

This script
  1. lists the cycles of phi for every multiple of 6 up to a bound (n = 3) and reports
     every M whose cycle set is NOT { {0}, {1,4,2} };
  2. cross-checks the cycle prediction against numpy eigenvalues for small M;
  3. does the same for n = 5, 7, 9, 11, 13 at the moduli the site's widget offers
     (6, 12, 24, 48, 96) and at multiples of 2n;
  4. reports matrix rank (the page says "rank 4").
"""
from fractions import Fraction
import numpy as np


def phi(x, M, n):
    return x // 2 if x % 2 == 0 else (n * x + 1) % M


def cycles(M, n):
    """Return list of (cycle as tuple starting at min element, weight Fraction)."""
    state = [0] * M  # 0 unseen, 1 on current path, 2 done
    out = []
    for s in range(M):
        if state[s]:
            continue
        path = []
        x = s
        while state[x] == 0:
            state[x] = 1
            path.append(x)
            x = phi(x, M, n)
        if state[x] == 1:
            i = path.index(x)
            cyc = path[i:]
            j = cyc.index(min(cyc))
            cyc = tuple(cyc[j:] + cyc[:j])
            w = Fraction(1)
            for c in cyc:
                w *= Fraction(2) if c % 2 == 0 else Fraction(1, n)
            out.append((cyc, w))
        for p in path:
            state[p] = 2
    return out


def matrix(M, n):
    L = np.zeros((M, M))
    for x in range(M):
        L[phi(x, M, n), x] += 2.0 if x % 2 == 0 else 1.0 / n
    return L


def predicted_eigs(M, n):
    ev = []
    for cyc, w in cycles(M, n):
        L = len(cyc)
        r = float(w) ** (1.0 / L)
        for k in range(L):
            ev.append(r * np.exp(2j * np.pi * k / L))
    return ev


def match(M, n):
    pred = sorted(predicted_eigs(M, n), key=lambda z: (round(abs(z), 6), round(np.angle(z), 6)))
    num = [e for e in np.linalg.eigvals(matrix(M, n)) if abs(e) > 1e-3]
    num = sorted(num, key=lambda z: (round(abs(z), 6), round(np.angle(z), 6)))
    if len(pred) != len(num):
        return False
    # greedy nearest matching
    rem = list(num)
    for p in pred:
        d = [abs(p - q) for q in rem]
        i = int(np.argmin(d))
        if d[i] > 1e-6:
            return False
        rem.pop(i)
    return True


if __name__ == "__main__":
    print("== 1. n = 3: multiples of 6 whose cycle set differs from {0}, {1,4,2}")
    BOUND = 6000
    bad = []
    for M in range(6, BOUND + 1, 6):
        cs = cycles(M, 3)
        key = sorted(c for c, _ in cs)
        if key != [(0,), (1, 4, 2)]:
            bad.append((M, cs))
    print(f"   multiples of 6 up to {BOUND}: {BOUND // 6} moduli, {len(bad)} with extra cycles")
    for M, cs in bad[:25]:
        extra = [(c, str(w), len(c), round(float(w) ** (1 / len(c)), 5)) for c, w in cs
                 if c not in ((0,), (1, 4, 2))]
        print(f"   M={M}: extra cycles (cycle, weight, length, |lambda|):")
        for e in extra:
            cyc = e[0] if len(e[0]) <= 12 else e[0][:12] + ("...",)
            print(f"        {cyc}  w={e[1]}  L={e[2]}  |lam|={e[3]}")
    if len(bad) > 25:
        print(f"   ... and {len(bad) - 25} more; first few M: {[b[0] for b in bad[:60]]}")
    pow2 = [6 * 2 ** j for j in range(0, 14)]
    print("   moduli 6*2^j, j=0..13 all clean:",
          all(sorted(c for c, _ in cycles(M, 3)) == [(0,), (1, 4, 2)] for M in pow2))

    print("== 1b. n = 3, all M (not only multiples of 6) up to 200: which are clean")
    clean = [M for M in range(5, 201) if sorted(c for c, _ in cycles(M, 3)) == [(0,), (1, 4, 2)]]
    print("   clean M:", clean)

    print("== 2. numpy cross-check of 'eigenvalues = roots of cycle weights'")
    ok = True
    for n in (3, 5, 7):
        for M in list(range(6, 200, 6)) + [10, 14, 20, 28, 40, 70, 100, 130]:
            if not match(M, n):
                ok = False
                print("   MISMATCH", n, M)
    print("   all matched:", ok)

    print("== 3. other multipliers: non-zero spectrum from cycles")
    for n in (5, 7, 9, 11, 13):
        for M in (6, 12, 24, 48, 96, 2 * n, 4 * n, 8 * n, 16 * n, 6 * n, 12 * n, 1000 * n):
            cs = cycles(M, n)
            desc = []
            for c, w in cs:
                if c == (0,):
                    continue
                desc.append(f"L={len(c)} w={w} |lam|={float(w) ** (1 / len(c)):.5f} min={c[0]}")
            print(f"   n={n:2d} M={M:6d}: page predicts |lam|=(4/{n})^(1/{n})={(4 / n) ** (1 / n):.5f}; "
                  f"actual non-trivial cycles: {desc}")

    print("== 4. rank of the matrix, n = 3")
    for M in (6, 12, 18, 24, 30, 48, 96):
        print(f"   M={M}: rank={np.linalg.matrix_rank(matrix(M, 3))}  "
              f"non-zero eigenvalues={sum(len(c) for c, _ in cycles(M, 3))}")

    print("== 5. sign test: 3x-1 on the same footing (weights 2 and 1/3)")

    def cycles_minus(M):
        def ph(x):
            return x // 2 if x % 2 == 0 else (3 * x - 1) % M
        seen = [0] * M
        out = []
        for s in range(M):
            if seen[s]:
                continue
            path = []
            x = s
            while seen[x] == 0:
                seen[x] = 1
                path.append(x)
                x = ph(x)
            if seen[x] == 1:
                cyc = path[path.index(x):]
                w = Fraction(1)
                for c in cyc:
                    w *= Fraction(2) if c % 2 == 0 else Fraction(1, 3)
                out.append((min(cyc), len(cyc), w, float(w) ** (1 / len(cyc))))
            for p in path:
                seen[p] = 2
        return out

    for M in (6, 12, 24, 48, 96, 192, 384):
        print(f"   3x-1, M={M}: cycles (min, length, weight, |lam|) = "
              f"{[(a, b, str(c), round(d, 5)) for a, b, c, d in cycles_minus(M)]}")
