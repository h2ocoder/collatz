"""Skeptic check 4: the mirror (NOT), cycles, unit cells, anti-diagonals, the 3x+d census, and Q2.5.

Independent of q24 / q25: cycles are found by the 'first return versus first drop in absolute value' test on
|n| <= 10^6 (the researcher used path-following on |n| <= 2*10^5); cells are analysed word by word with exact
fractions; the dictionary 'unit cell <-> pair <-> triangular number <-> cycle' is run for q = 3, 5, 7, 9 to see
whether it says anything special about 3x+1; the 3x+d census is recounted with a different algorithm.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v4_mirror_cycles.py
"""
import json
import os
import random
import time
from fractions import Fraction
from itertools import combinations
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v4_mirror_cycles.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def Tq(x, q=3, d=1):
    return (q * x + d) // 2 if x % 2 else x // 2


def NOT(x):
    return -1 - x


def v2(n):
    n = abs(n)
    return (n & -n).bit_length() - 1


# ---------------------------------------------------------------------------------------------
out("=" * 100)
out("A. NOT identities on 10^5 random signed 200-bit integers and all |n| <= 10^5")
out("=" * 100)
random.seed(37)
xs = [random.getrandbits(200) - (1 << 199) for _ in range(100000)] + list(range(-100000, 100001))
idn = {
    "NOT(3x+1) = 3 NOT(x) + 1": all(NOT(3 * x + 1) == 3 * NOT(x) + 1 for x in xs),
    "NOT T NOT (m) = 3m/2 | (m-1)/2": all(NOT(Tq(NOT(x))) == (3 * x // 2 if x % 2 == 0 else (x - 1) // 2) for x in xs),
    "NOT T NOT (m) = T_minus(m+1) - 1": all(NOT(Tq(NOT(x))) == Tq(x + 1, 3, -1) - 1 for x in xs),
    "T_(3n+1) = 9 T_n + 1": all((3 * x + 1) * (3 * x + 2) // 2 == 9 * (x * (x + 1) // 2) + 1 for x in xs),
    "halving does not commute: NOT(x/2) != NOT(x)/2 always (NOT(x) is odd)": all(NOT(x) % 2 == 1 for x in xs if x % 2 == 0),
}
for k_, v_ in idn.items():
    out(f"  {v_!s:5s} {k_}")
# the same conjugacy for every rule that is a dilation about -1/2: q x + (q-1)/2
gen = all(NOT(q * x + (q - 1) // 2) == q * NOT(x) + (q - 1) // 2 for q in (3, 7, 11, 15) for x in xs[:2000])
out(f"  {gen!s:5s} NOT commutes with x -> q x + (q-1)/2 for q = 3, 7, 11, 15 (3x+1, 7x+3, 11x+5, 15x+7)")
RES["A"] = {k_: bool(v_) for k_, v_ in idn.items()}

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("B. Cycles of T on Z met from |n| <= 10^6 (first return before first drop in absolute value)")
out("=" * 100)


def cycle_minima(q, d, lim, cap=5000, huge=10 ** 40):
    mins, unresolved = [], 0
    for n0 in range(-lim, lim + 1):
        x, a0 = n0, abs(n0)
        for _ in range(cap):
            x = (q * x + d) // 2 if x % 2 else x // 2
            if x == n0:
                mins.append(n0)
                break
            if abs(x) < a0 or (abs(x) == a0 and x != n0):
                break
            if abs(x) > huge:
                unresolved += 1
                break
        else:
            unresolved += 1
    return mins, unresolved


def cyc(n0, q=3, d=1):
    c, x = [n0], Tq(n0, q, d)
    while x != n0:
        c.append(x)
        x = Tq(x, q, d)
    return c


mins, unres = cycle_minima(3, 1, 10 ** 6)
cycs = [cyc(n0) for n0 in mins]
out("  3x+1: elements of minimal |n| in their cycle:", mins, " unresolved starts:", unres)
for c in cycs:
    k, s = len(c), sum(x % 2 for x in c)
    out(f"     {c}  cell (k,s) = ({k},{s}), 2^k - 3^s = {2 ** k - 3 ** s}")
out("  NOTE: this is a search, not a theorem.  'Every cycle of T on Z' in the README must read 'every KNOWN cycle'")
out("  (that there are no others is the finite-cycles conjecture, open).")
RES["B_minima"] = mins

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("C. Is the dictionary 'unit cell <-> consecutive pair <-> triangular number <-> cycle' special to 3x+1?")
out("   For q x + 1: unit cells |2^k - q^s| = 1 (k <= 400, s <= 250), every parity word of the cell is an integer cycle.")
out("=" * 100)


def word_fixed_point(word, q, d=1):
    """fixed point of the composition of branches along `word` (exact rational)."""
    a, b = Fraction(1), Fraction(0)          # x -> a x + b
    for bit in word:
        if bit:
            a, b = a * q / 2, (b * q + d) / 2
        else:
            a, b = a / 2, b / 2
    return b / (1 - a) if a != 1 else None


def words(k, s):
    for pos in combinations(range(k), s):
        w = [0] * k
        for p in pos:
            w[p] = 1
        yield w


RES["C"] = {}
for q in (3, 5, 7, 9, 15, 17):
    cells = []
    for s in range(0, 251):
        p = q ** s
        for cand in (p - 1, p + 1):
            if cand >= 2 and cand & (cand - 1) == 0:
                cells.append((cand.bit_length() - 1, s))
    rows = []
    for (k, s) in sorted(set(cells)):
        lo = min(2 ** k, q ** s)
        fps = sorted({word_fixed_point(w, q) for w in words(k, s)})
        integral = all(f.denominator == 1 for f in fps)
        rows.append((k, s, 2 ** k - q ** s, lo, lo * (lo + 1) // 2, [int(f) for f in fps], integral))
        out(f"  {q}x+1: cell ({k},{s})  2^k - q^s = {2 ** k - q ** s:+d}   pair ({lo},{lo + 1})   T_{lo} = {lo * (lo + 1) // 2}"
            f"   periodic points of the cell: {[int(f) for f in fps]}  (all integral: {integral})")
    RES["C"][str(q)] = rows
out("  -> the dictionary exists for every q; the pair (8,9) is a unit cell twice: (3,2) for 3x+1 and (3,1) for 9x+1,")
out("     both times with T_8 = 36 and a NEGATIVE cycle.  It is Catalan's pair, not a Collatz phenomenon.")
# the non-unit cell (11,7)
fps = [(w, word_fixed_point(w, 3)) for w in words(11, 7)]
ints = sorted(int(f) for w, f in fps if f.denominator == 1)
out(f"  cell (11,7), 2^11 - 3^7 = -139: {len(fps)} words, integral periodic points: {ints}")
RES["C_cell_11_7"] = ints

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("D. Anti-diagonal family: word 1^j 0 is a cycle of 3x + d_j, d_j = 2^(j+1) - 3^j, minimum 3^j - 2^j  (j <= 80)")
out("=" * 100)
okD = True
for j in range(0, 81):
    d = 2 ** (j + 1) - 3 ** j
    n0 = 3 ** j - 2 ** j
    x, orb = n0, []
    for _ in range(j + 1):
        orb.append(x)
        x = (3 * x + d) // 2 if x % 2 else x // 2
    okD &= x == n0 and min(orb) == n0 and all(y % 2 == 1 for y in orb[:j]) and (j == 0 or orb[j] % 2 == 0)
    okD &= gcd(n0, abs(d)) == 1 if n0 else True
    okD &= n0 + d == 2 ** j
out("  closes after j+1 steps, parity word 1^j 0, minimum n0, gcd(n0, d_j) = 1, n0 + d_j = 2^j:", okD)
out("  |d_j| = 1 only for j = 0, 1, 2:", [j for j in range(0, 2000) if abs(2 ** (j + 1) - 3 ** j) == 1])
RES["D_family_ok"] = okD

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("E. Two-run cycles of 3x-1 on the positive integers: words 1^j1 0^e1 1^j2 0^e2, all run lengths <= 28")
out("   (exact fixed points of the word; the researcher solved a 2x2 linear system instead)")
out("=" * 100)
sols = set()
p3 = [3 ** i for i in range(120)]
for j1 in range(1, 29):
    for e1 in range(1, 29):
        for j2 in range(1, 29):
            for e2 in range(1, 29):
                k, s = j1 + e1 + j2 + e2, j1 + j2
                den = (1 << k) - p3[s]
                # word constant for 1^j1 0^e1 1^j2 0^e2 under 3x-1: x -> (3^s x - c)/2^k
                # after 1^j1: (3^j1 x - (3^j1 - 2^j1))/2^j1 ; after 0^e1: divide by 2^e1 ; etc.
                c = (p3[j1] - (1 << j1)) * p3[j2] + (p3[j2] - (1 << j2)) * (1 << (j1 + e1))
                # fixed point: x (2^k - 3^s) = -c
                if (-c) % den == 0:
                    x = (-c) // den
                    if x > 0:
                        # verify by iteration and reduce to the cycle minimum
                        y, orb = x, []
                        for _ in range(k):
                            orb.append(y)
                            y = (3 * y - 1) // 2 if y % 2 else y // 2
                        if y == x:
                            sols.add((min(orb), len(set(orb))))
out("  positive integer cycles found (minimum, length):", sorted(sols))
out("  -> only the fixed point 1 (doubled words), the 5-cycle (doubled) and the 17-cycle: agrees with q24 section F.")
RES["E_two_run"] = sorted(sols)

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("F. Census recount: primitive positive cycles of 3x+d, d odd, 3 !| d, |d| <= 499, minimum <= 100|d| + 2000")
out("=" * 100)


def census_d(d, nmax):
    found = []
    for n0 in range(1, nmax + 1, 2):
        x = n0
        seen = None
        steps = 0
        while True:
            x = (3 * x + d) >> 1 if x & 1 else x >> 1
            steps += 1
            if x < n0:
                break
            if x == n0:
                found.append(n0)
                break
            if steps == 400:
                seen = set()
            if seen is not None:
                if x in seen:
                    break                 # captured by a cycle that does not contain n0
                seen.add(x)
    return found


def n_runs(n0, d):
    """number of maximal runs of odd steps in the cycle of n0 under 3x+d (cyclic word)."""
    w, x = [], n0
    while True:
        w.append(x & 1)
        x = (3 * x + d) >> 1 if x & 1 else x >> 1
        if x == n0:
            break
    return sum(1 for i in range(len(w)) if w[i] == 1 and w[i - 1] == 0) or 1


tot = pure = 0
size = {16: [0, 0], 32: [0, 0], 64: [0, 0], 128: [0, 0], 256: [0, 0]}
pure_rows = []
two_run = [0, 0]
for d in range(-499, 500, 2):
    if d % 3 == 0:
        continue
    for n0 in census_d(d, 100 * abs(d) + 2000):
        if gcd(n0, abs(d)) != 1:
            continue
        tot += 1
        v0 = n0 + d
        is_pow = v0 > 0 and v0 & (v0 - 1) == 0
        if v0 < 0 and (-v0) & (-v0 - 1) == 0:
            is_pow = True
        pure += is_pow
        if n_runs(n0, d) == 2:
            two_run[0] += 1
            two_run[1] += is_pow
        if is_pow:
            pure_rows.append((d, n0, v0))
        for B in size:
            if 0 < abs(v0) <= B:
                size[B][0] += 1
                size[B][1] += is_pow
out(f"  primitive positive cycles: {tot}   with |v0| a power of two: {pure}   (researcher: 797 and 18)")
out(f"  two-run cycles: {two_run[0]}, of which |v0| = 2^j: {two_run[1]}   (researcher: 95 and 1)")
out("  size-matched (|v0| <= B: cycles, with |v0| = 2^j, share of powers of two among even numbers <= B):")
for B, (a, b) in size.items():
    out(f"     B = {B:3d}: {a:3d} cycles, {b:2d} powers of two ({b / max(a, 1):.3f}); chance share {(B.bit_length() - 1) / (B // 2):.3f}")
out("  rows with |v0| = 2^j:", pure_rows)
RES["F"] = dict(total=tot, pure=pure, size={str(k_): v_ for k_, v_ in size.items()})

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("G. Q2.5: the numbers attached to 36, recomputed without the repo package; and controls")
out("   un-shortcut map f(n) = n/2 | 3n+1; dropping time = steps to the first value < n")
out("=" * 100)


def f(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def drop(n):
    x, t = n, 0
    while True:
        x = f(x)
        t += 1
        if x < n:
            return t, x


def orbit(n):
    o = [n]
    while n != 1:
        n = f(n)
        o.append(n)
    return o


for x in (36, 35, 8, 17, 6, 37, 9):
    t, dest = drop(x)
    out(f"  n = {x:2d}: dropping time {t}, destination {dest}, steps to 1: {len(orbit(x)) - 1}")
for lim in (10 ** 3, 10 ** 4, 10 ** 5):
    c17 = sum(1 for x in range(1, lim + 1) if 17 in orbit(x))
    out(f"  share of 1 <= n <= {lim} whose orbit passes through 17 (hence 8): {c17 / lim:.3f}")
hits = [nn for nn in range(2, 2001) if (lambda o: nn in o and 2 * nn + 1 in o)(set(orbit(nn * (nn + 1) // 2)))]
out(f"  control: indices 2 <= n <= 2000 for which orbit(T_n) contains both n and u = 2n+1: {len(hits)} of 1999;"
    f" first few {hits[:12]}")
only_n = sum(1 for nn in range(2, 2001) if nn in set(orbit(nn * (nn + 1) // 2)))
out(f"           orbit(T_n) contains n: {only_n} of 1999.")
out("  reading: every orbit from n >= 3, n != 4 passes through 8, and about 45% pass through 17, so for T_8 = 36 the")
out("  event has probability about 0.45.  For larger n the targets n and 2n+1 are large and are almost never hit:")
out("  the 'coincidence' at n = 8 exists because 8 and 17 are small, not because of anything about 36.")
all8 = all(8 in orbit(x) for x in range(3, 20001) if x != 4)
out("  every orbit from 3 <= n <= 20000, n != 4 contains 8:", all8)
RES["G_control_hits"] = hits[:40]

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v4_mirror_cycles.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
