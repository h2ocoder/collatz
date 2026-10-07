"""Fixer-side checks for the 'connections' section: every number the rewritten pages state.

1. Role-of-c table (universal-dynamics.md): odd starts 3..499, share that pass through 1,
   number of distinct cycles reached (the cycle through 1 included when 1 lies on one).
2. ZooExplorer survey: over the whole slider grid, how many starts end as 'timeout'
   (no result in 2000 steps) rather than 'passed 1e15'?
3. L-probe: exactness over random windows of 3*2^k consecutive integers > 1, and over the
   shorter window 3*2^e (e = k - o, the Terras modulus).
4. Transfer matrix (independent re-implementation): loops for M = 6..108, rank and
   asymmetry at M = 24 and 96, loops of 5x+1, 7x+1 and 3x-1 at M = 24.
5. Eisenstein: walk of 27; alpha table growth factors.
"""
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from collatz.lfunctions import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.eisenstein import EisensteinInt  # noqa: E402

LOG23 = math.log2(3)


# ---------------------------------------------------------------- 1. role of c
def end_state(c, x0, max_steps=200_000):
    """Follow 3x+c, x/2 from x0. Return (passed_through_1, frozenset(cycle))."""
    x = x0
    seen = {x: 0}
    seq = [x]
    hit1 = (x == 1)
    for _ in range(max_steps):
        x = x // 2 if x % 2 == 0 else 3 * x + c
        if x == 1:
            hit1 = True
        if x in seen:
            return hit1, frozenset(seq[seen[x]:])
        seen[x] = len(seq)
        seq.append(x)
    return hit1, None


def role_of_c():
    print("1. role of c: odd starts 3..499 (and 3..999)")
    for c in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19):
        for hi in (500, 1000):
            cyc = set()
            hits = tot = unresolved = 0
            for x0 in range(3, hi, 2):
                tot += 1
                h, cy = end_state(c, x0)
                hits += h
                if cy is None:
                    unresolved += 1
                else:
                    cyc.add(cy)
            one_on_cycle = any(1 in cy for cy in cyc)
            print(f"   c={c:2d} starts 3..{hi - 1}: pass through 1: {hits}/{tot} = {hits / tot:.1%}; "
                  f"distinct cycles reached: {len(cyc)} (minima {sorted(min(cy) for cy in cyc)}); "
                  f"1 on a cycle: {one_on_cycle}; unresolved: {unresolved}")


# ---------------------------------------------------------------- 2. widget grid
def widget_run(n, y, c, x0, max_steps=2000):
    x = x0
    seen = {x0}
    for _ in range(max_steps):
        x = x // y if x % y == 0 else n * x + c
        if x == 1:
            return 'converged'
        if x <= 0 or x > 1e15:
            return 'diverged'
        if x in seen:
            return 'cycle'
        seen.add(x)
    return 'timeout'


def widget_grid():
    print("2. ZooExplorer grid (n 2..15, y 2..6, c odd 1..19; starts 3..499 odd, y not dividing)")
    tot = {'converged': 0, 'cycle': 0, 'diverged': 0, 'timeout': 0}
    with_timeout = []
    for n in range(2, 16):
        for y in range(2, 7):
            for c in range(1, 20, 2):
                loc = {'converged': 0, 'cycle': 0, 'diverged': 0, 'timeout': 0}
                for x0 in range(3, 500, 2):
                    if x0 % y == 0:
                        continue
                    loc[widget_run(n, y, c, x0)] += 1
                for k in tot:
                    tot[k] += loc[k]
                if loc['timeout']:
                    with_timeout.append((n, y, c, loc['timeout']))
    print("   totals:", tot)
    print(f"   settings with at least one timeout: {len(with_timeout)}; first few {with_timeout[:12]}")
    for (n, y, c) in ((3, 2, 1), (5, 2, 1), (7, 2, 1), (9, 2, 1), (2, 3, 1)):
        loc = {'converged': 0, 'cycle': 0, 'diverged': 0, 'timeout': 0}
        for x0 in range(3, 500, 2):
            if x0 % y == 0:
                continue
            loc[widget_run(n, y, c, x0)] += 1
        t = sum(loc.values())
        print(f"   ({n}x+{c}, x/{y}): {loc}  -> reach 1 {loc['converged'] / t:.1%}, cycle {loc['cycle'] / t:.1%}, "
              f"past 1e15 {loc['diverged'] / t:.1%}, timeout {loc['timeout'] / t:.1%}")
    for x0 in (27,):
        for (n, y, c) in ((3, 2, 1), (5, 2, 1), (3, 2, 5), (3, 2, 7)):
            print(f"   sample orbit x={x0} under {n}x+{c}, x/{y}: {widget_run(n, y, c, x0)}")


# ---------------------------------------------------------------- 3. L-probe
chi = SexticResidueCharacter()


def B(j):
    return int(math.floor(j * LOG23)) if j else 0


def k_of(o):
    return o + B(o) + 1


def gap(o):
    return k_of(o) - k_of(o - 1)


def drop(n):
    x, t = n, 0
    while True:
        x = 3 * x + 1 if x & 1 else x >> 1
        t += 1
        if x < n:
            return t, x


def paths(o_minus_1):
    f = {0: 1}
    for j in range(1, o_minus_1 + 1):
        g = {}
        for T, cnt in f.items():
            for a in range(1, B(j) - T + 1):
                g[T + a] = g.get(T + a, 0) + cnt
        f = g
    return f


def A_P(o):
    Nd = paths(o - 1)
    P = sum(Nd.values())
    A = sum((-1) ** (B(o - 1) - T) * cnt for T, cnt in Nd.items())
    return A, P


def window_sum(k, lo, hi):
    s = 0j
    cnt = 0
    for n in range(lo | 1, hi + 1, 2):
        if n < 3:
            continue
        t, d = drop(n)
        if t == k:
            s += chi.evaluate(EisensteinInt(n, d))
            cnt += 1
    return s, cnt


def lprobe():
    print("3. L-probe: D over a window = (i/sqrt3) * eps * (A/P) * (terms in window) ?")
    rng = random.Random(36)
    for o in range(1, 8):
        k = k_of(o)
        e = k - o
        A, P = A_P(o)
        eps = 1 if gap(o) == 3 else -1
        for label, per in (("3*2^k", 3 * 2 ** k), ("3*2^e", 3 * 2 ** e)):
            ok = True
            worst = 0.0
            trials = 12 if per < 400_000 else 3
            cnts = set()
            for _ in range(trials):
                lo = rng.randrange(2, 5 * per)
                d, cnt = window_sum(k, lo, lo + per - 1)
                pred = 1j * eps * A / P * cnt / math.sqrt(3)
                worst = max(worst, abs(d - pred))
                ok &= abs(d - pred) < 1e-6
                cnts.add(cnt)
            print(f"   o={o} k={k} e={e} A/P={A}/{P} window {label}={per}: {trials} random windows (start >= 2), "
                  f"all exact: {ok} (worst |diff| {worst:.2e}); terms per window {sorted(cnts)}; "
                  f"per-period value i*sqrt3*eps*A*2^o = {eps * math.sqrt(3) * A * 2 ** o:+.4f}i")
    print("   o=1, range starting at 1 (n = 1 never drops): D over [1, 24] =",
          "{:.4f}".format(window_sum(3, 1, 24)[0]), " terms:", window_sum(3, 1, 24)[1])
    for N in (23, 96, 100, 768, 1000):
        d, cnt = window_sum(8, 3, N)
        print(f"   o=3: D^(8)({N}) = {d.real:+.4f}{d.imag:+.4f}i  |D| = {abs(d):.4f}")
    # size per non-zero term
    for o in range(1, 9):
        A, P = A_P(o)
        print(f"   o={o} k={k_of(o)} gap={gap(o)}: A/P = {Fraction(A, P)}  (sqrt3/2)*A/P = {math.sqrt(3) / 2 * A / P:.4f}")


# ---------------------------------------------------------------- 4. transfer matrix
def phi(x, M, n, c=1):
    return x // 2 if x % 2 == 0 else (n * x + c) % M


def loops(M, n, c=1):
    out = []
    state = [0] * M
    for s in range(M):
        if state[s]:
            continue
        path = []
        x = s
        while state[x] == 0:
            state[x] = 1
            path.append(x)
            x = phi(x, M, n, c)
        if state[x] == 1:
            cyc = path[path.index(x):]
            w = Fraction(1)
            for v in cyc:
                w *= Fraction(2) if v % 2 == 0 else Fraction(1, n)
            j = cyc.index(min(cyc))
            out.append((tuple(cyc[j:] + cyc[:j]), w))
        for p in path:
            state[p] = 2
    return out


def mat(M, n, c=1):
    L = np.zeros((M, M))
    for x in range(M):
        L[phi(x, M, n, c), x] += 2.0 if x % 2 == 0 else 1.0 / n
    return L


def transfer():
    print("4. transfer matrix")
    clean = [M for M in range(6, 114, 6) if sorted(c for c, _ in loops(M, 3)) == [(0,), (1, 4, 2)]]
    print("   multiples of 6 below 114 whose only loops are {0} and {1,4,2}:", len(clean), "of", len(range(6, 114, 6)))
    print("   M=114 loops:", [(c, str(w)) for c, w in loops(114, 3)])
    ev = [e for e in np.linalg.eigvals(mat(114, 3)) if abs(e) > 1e-3]
    print("   M=114 non-zero eigenvalue moduli:", sorted(round(abs(e), 4) for e in ev))
    for M in (6, 12, 24, 48, 96):
        L = mat(M, 3)
        ev = [e for e in np.linalg.eigvals(L) if abs(e) > 1e-3]
        print(f"   M={M}: non-zero eigenvalues {len(ev)}, moduli {sorted({round(abs(e), 4) for e in ev})}, "
              f"rank {np.linalg.matrix_rank(L)}, |L-L^T|/|L| = {np.linalg.norm(L - L.T) / np.linalg.norm(L):.3f}")
    for n in (3, 5, 7):
        ls = loops(24, n)
        ev = [e for e in np.linalg.eigvals(mat(24, n)) if abs(e) > 1e-3]
        print(f"   {n}x+1, M=24: loops {[(c, str(w), round(float(w) ** (1 / len(c)), 4)) for c, w in ls]}; "
              f"numpy moduli {sorted({round(abs(e), 4) for e in ev}, reverse=True)} ({len(ev)} non-zero)")
    ls = loops(24, 3, c=-1)
    print(f"   3x-1, M=24: loops {[(c, str(w), round(float(w) ** (1 / len(c)), 4)) for c, w in ls]}")


# ---------------------------------------------------------------- 5. Eisenstein
def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def eisenstein():
    print("5. Eisenstein walk of 27")
    m = 27
    h = s = 0
    pts = []
    vals = [27]
    while m != 1:
        a = v2(3 * m + 1)
        m = (3 * m + 1) >> a
        s += 1
        h += a
        pts.append((h - s * LOG23, m, a))
        vals.append(m)
    below = sum(1 for e, _, _ in pts if e < 0)
    print(f"   {len(pts)} steps; {below} points below the line ({below / len(pts):.1%}); "
          f"above at steps {[i + 1 for i, (e, _, _) in enumerate(pts) if e > 0]}; end excess {pts[-1][0]:.4f} "
          f"vs log2(27) = {math.log2(27):.4f}")
    # is every point below the line a value above the start, and every point above within 2^0.33 of start or lower?
    print("   below line => value > 27:", all(v > 27 for e, v, _ in pts if e < 0),
          "; above line => value < 27 * 1.26:", all(v < 27 * 1.26 for e, v, _ in pts if e > 0))
    print("   alpha of the last three steps:", [a for _, _, a in pts[-3:]], "values", vals[-4:])
    for a in (1, 2, 3, 4):
        z = complex(a - 0.5, math.sqrt(3) / 2)
        print(f"   alpha={a}: angle {math.degrees(math.atan2(z.imag, z.real)):.1f} deg, norm {a * a - a + 1}, "
              f"growth 3/2^{a} = {Fraction(3, 2 ** a)}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5"]
    if "1" in which:
        role_of_c()
    if "2" in which:
        widget_grid()
    if "3" in which:
        lprobe()
    if "4" in which:
        transfer()
    if "5" in which:
        eisenstein()
