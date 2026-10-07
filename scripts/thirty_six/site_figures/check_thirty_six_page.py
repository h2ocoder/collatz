"""Recompute the worked numbers and examples printed on site/explore/thirty-six.md.

Self-contained (no import from the `collatz` package or from the thread directories), exact
integer arithmetic throughout.  Writes `check_thirty_six_page.log` next to itself and exits
with status 1 if any check fails.

Not recomputed here (they live in the thread directories under scripts/thirty_six/): the
statistical nulls of the totient thread, the trisection counts, the search for a cube identity
among path counts (209,434 multisets), and the verifications of the dropping-word counts
beyond s = 400 (the threads go to s = 2218).  Ljunggren's theorem is checked only for n < 10^5.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 check_thirty_six_page.py     (about 10 s)

Conventions
* Shortcut (Terras) map T(n) = n/2 (n even), (3n+1)/2 (n odd); rule (q, d): (qn+d)/2 on odd n.
* A cell (k, s): k shortcut steps, s of them odd.
* Site dropping time (site/foundations/definitions.md) counts UN-shortcut steps, so a class of
  Terras level k with s odd steps is the site's Dset_(k+s):  k = 1, 2, 4, 5, 7, 8, 10, ...
  <->  Dset_1, 3, 6, 8, 11, 13, 16, ...
"""
from __future__ import annotations

import math
import sys
import time
from collections import Counter
from fractions import Fraction
from math import comb, gcd, isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG: list[str] = []
FAILS: list[str] = []
T0 = time.time()


def say(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.append(msg)


def check(cond: bool, msg: str) -> None:
    say(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def section(title: str) -> None:
    say()
    say(f"== {title}")


def tri(n: int) -> int:
    return n * (n + 1) // 2


def step(n: int, q: int = 3, d: int = 1) -> int:
    """One shortcut step of the rule (q, d)."""
    return n // 2 if n % 2 == 0 else (q * n + d) // 2


def stop_ks(n: int, q: int = 3, d: int = 1, cap: int = 100000) -> tuple[int, int] | None:
    """(k, s): shortcut steps and odd steps until the first value below n (n >= 2)."""
    x, k, s = n, 0, 0
    while k < cap:
        if x % 2:
            x = (q * x + d) // 2
            s += 1
        else:
            x //= 2
        k += 1
        if x < n:
            return k, s
    return None


def is_square(m: int) -> bool:
    return m >= 0 and isqrt(m) ** 2 == m


# --------------------------------------------------------------------------- dropping words
def dropping_word_counts(s_max: int) -> list[int]:
    """N(s), s = 0..s_max: words with s ones whose every proper prefix (j letters, t ones)
    has 2^j < 3^t and whose full length L has 2^L > 3^s.  N(0) = 1 is the word '0'."""
    out = [0] * (s_max + 1)
    alive = {0: 1}                      # ones -> count, at the current length j
    j = 0
    pow3 = [3 ** t for t in range(s_max + 2)]
    while alive:
        j += 1
        two = 1 << j
        nxt: dict[int, int] = {}
        for t, c in alive.items():
            for t2 in (t, t + 1):
                if t2 > s_max:
                    continue
                if two > pow3[t2]:      # dropped at this letter
                    if t2 == t:         # a drop can only happen on a 0
                        out[t2] += c
                    else:               # appending a 1 never drops
                        raise AssertionError("drop on an odd letter")
                else:
                    nxt[t2] = nxt.get(t2, 0) + c
        # words that have run past s_max ones are discarded; they cannot return
        alive = nxt
        if j > 2 * s_max + 5:
            break
    return out


def level_of(s: int) -> int:
    """Terras level k of the order-s classes: least k with 2^k > 3^s."""
    return (3 ** s).bit_length()


# ============================================================================================
def main() -> int:
    # ---------------------------------------------------------------- 0. the four facts
    section("0. The four facts about 36")
    check(tri(8) == 36 == 6 ** 2, "36 = T_8 = 6^2 (triangular and square)")
    check(1 ** 3 + 2 ** 3 + 3 ** 3 == 36 == tri(3) ** 2, "36 = 1^3 + 2^3 + 3^3 = T_3^2")
    phi_gold = (1 + 5 ** 0.5) / 2
    check(abs(math.cos(math.radians(36)) - phi_gold / 2) < 1e-15, "cos 36 deg = phi/2 (float, 1e-15)")

    # ---------------------------------------------------------------- 1. consecutive pairs
    section("1. Consecutive numbers 2^a 3^b (Levi ben Gerson)")
    LIM = 10 ** 100
    smooth = sorted(2 ** a * 3 ** b for a in range(340) for b in range(215) if 2 ** a * 3 ** b < LIM)
    pairs = [(x, y) for x, y in zip(smooth, smooth[1:]) if y - x == 1]
    say(f"      {len(smooth)} three-smooth numbers below 10^100")
    check(pairs == [(1, 2), (2, 3), (3, 4), (8, 9)], f"consecutive pairs below 10^100: {pairs}")
    # for each k the only candidates are the s next to k / log2(3)
    units = []
    for k in range(1, 3001):
        s0 = int(k / math.log2(3))
        for s in range(max(0, s0 - 2), s0 + 3):
            if abs((1 << k) - 3 ** s) == 1:
                units.append((k, s))
    check(units == [(1, 0), (1, 1), (2, 1), (3, 2)], f"cells with |2^k - 3^s| = 1, k <= 3000: {units}")
    tri_smooth = []
    for n in range(1, 200001):
        t = tri(n)
        while t % 2 == 0:
            t //= 2
        while t % 3 == 0:
            t //= 3
        if t == 1:
            tri_smooth.append((n, tri(n)))
    check(tri_smooth == [(1, 1), (2, 3), (3, 6), (8, 36)],
          f"three-smooth triangular numbers T_n, n <= 200000: {tri_smooth}")
    for (k, s), (n, t) in zip(units, tri_smooth):
        check(t == 2 ** (k - 1) * 3 ** s and {n, n + 1} == {2 ** k, 3 ** s},
              f"cell ({k},{s}): pair ({n},{n+1}), T_{n} = 2^{k-1} 3^{s} = {t}")
    cents = lambda r: 1200 * math.log2(r)
    for name, r, want in (("octave 2/1", Fraction(2, 1), 1200.0), ("fifth 3/2", Fraction(3, 2), 701.955),
                          ("fourth 4/3", Fraction(4, 3), 498.045), ("whole tone 9/8", Fraction(9, 8), 203.910),
                          ("apotome 2187/2048", Fraction(2187, 2048), 113.685)):
        check(abs(cents(r) - want) < 0.001, f"{name} = {cents(r):.3f} cents")

    # ---------------------------------------------------------------- 2. cycles
    section("2. The cycles in the unit cells, and the cycle through -17")
    table = {0: ((1, 0), [0]), -1: ((1, 1), [-1]), 1: ((2, 1), [1, 2]), -5: ((3, 2), [-5, -7, -10]),
             -17: ((11, 7), [-17, -25, -37, -55, -82, -41, -61, -91, -136, -68, -34])}
    for start, (cell, want) in table.items():
        orb, x = [start], step(start)
        while x != start:
            orb.append(x)
            x = step(x)
            assert len(orb) < 100
        k, s = len(orb), sum(1 for y in orb if y % 2)
        check(orb == want and (k, s) == cell,
              f"cycle {orb}: cell ({k},{s}), 2^k - 3^s = {2**k - 3**s}")
    v = [n + 1 for n in (-5, -7, -10)]
    check(v == [-4, -6, -9] and v[0] * v[2] == 36 == v[1] ** 2 == tri(8) == tri(-9),
          "v = n + 1 on the -5 cycle: -4 -> -6 -> -9; (-4)(-9) = (-6)^2 = T_8 = T_(-9) = 36")
    check(all(3 * a == 2 * b for a, b in zip(v, v[1:])) and (v[2] + 1) // 2 == v[0],
          "in v the odd step is v -> 3v/2 and the even step is v -> (v+1)/2")
    m3 = lambda n: n // 2 if n % 2 == 0 else (3 * n - 1) // 2
    check([m3(5), m3(7), m3(10)] == [7, 10, 5], "3x-1: cycle 5 -> 7 -> 10 -> 5, v = n - 1 = 4, 6, 9")
    check(2 ** 11 - 3 ** 7 == -139 and Fraction(3 ** 7, 2 ** 11) == Fraction(2187, 2048),
          "cell (11,7): 2^11 - 3^7 = -139, interval 3^7/2^11 = 2187/2048")
    run = [n + 1 for n in (-17, -25, -37, -55, -82)]
    check(run == [-16, -24, -36, -54, -81], f"first run of the -17 cycle in v: {run}")

    section("2b. One-even-element theorem (word 1^a 0)")
    closes, triang = [], []
    for a in range(0, 401):
        D = 2 ** (a + 1) - 3 ** a
        C = 3 ** a - 2 ** a                      # sum_{j<a} 3^(a-1-j) 2^j
        if C % D == 0:
            x = C // D
            y, par = x, []
            for _ in range(a + 1):
                par.append(y % 2)
                y = step(y)
            assert y == x and par == [1] * a + [0], (a, x, par)
            closes.append((a, x))
        if is_square(8 * 6 ** a + 1):
            triang.append(a)
    check(closes == [(0, 0), (1, 1), (2, -5)], f"1^a 0 closes on an integer, a <= 400: {closes}")
    check(triang == [0, 1, 2], f"6^a triangular, a <= 400: a in {triang}")
    check([abs(2 ** (a + 1) - 3 ** a) for a in range(4)] == [1, 1, 1, 11], "|2^(a+1) - 3^a| = 1, 1, 1, 11, ...")

    section("2c. Why 3: cells with |2^k - q^s| = 1 for odd q")
    hist: dict[int, list[int]] = {}
    for q in range(3, 2002, 2):
        cnt = 1                                   # (k, s) = (1, 0)
        for s in range(1, 121):
            for val in (q ** s - 1, q ** s + 1):
                if val > 1 and val & (val - 1) == 0 and val.bit_length() - 1 >= s:
                    cnt += 1
        hist.setdefault(cnt, []).append(q)
    check(hist.get(4) == [3], "q = 3 is the only odd multiplier <= 2001 with four unit cells")
    two = hist.get(2, [])
    check(all(((q + 1) & q) == 0 or ((q - 1) & (q - 2)) == 0 for q in two) and 3 not in two,
          f"two unit cells exactly for q = 2^j +- 1 (q != 3): {two[:8]} ... ({len(two)} values)")
    check(sorted(hist) == [1, 2, 4] and len(two) == 17 and len(hist[1]) == 982,
          f"every other q has one: {len(hist[1])} values")

    section("2d. Control: do cycles of 3x+c sit at record cells?")
    def records(alpha_num: int, s_max: int) -> set[tuple[int, int]]:
        """Cells (k, s) whose ratio q^s/2^k is closer to 1 than for every smaller s on its side."""
        rec = set()
        best_up, best_dn = None, None             # ratios as Fractions
        for s in range(0, s_max + 1):
            p = alpha_num ** s
            k_dn = p.bit_length()                 # 2^k > q^s  (ratio < 1)
            r = Fraction(p, 1 << k_dn)
            if best_dn is None or r > best_dn:
                best_dn = r
                rec.add((k_dn, s))
            if s >= 1:
                k_up = k_dn - 1                   # 2^k < q^s  (ratio > 1)
                r = Fraction(p, 1 << k_up)
                if best_up is None or r < best_up:
                    best_up = r
                    rec.add((k_up, s))
        return rec
    rec3 = records(3, 700)
    ladder = sorted(rec3, key=lambda c: (c[1], c[0]))
    say(f"      record cells of log2 3 (s <= 700): {len(rec3)}; first: {ladder[:8]}")
    check(ladder[:8] == [(1, 0), (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (11, 7), (19, 12)],
          "record ladder starts (1,0), (1,1), (2,1), (3,2), (5,3), (8,5), (11,7), (19,12)")
    check(len(rec3) == 19, "19 record cells with s <= 700")
    R = 20000
    cyc_all = []                                   # (c, min, k, s)
    for c in range(5, 200, 2):
        seen: set[int] = set()
        for start in range(-R, R + 1):
            if start in seen:
                continue
            path, pos, n = [], {}, start
            while n not in seen and n not in pos:
                pos[n] = len(path)
                path.append(n)
                n = n // 2 if n % 2 == 0 else (3 * n + c) // 2
                assert len(path) < 10 ** 6
            if n in pos:
                cyc = path[pos[n]:]
                mn = min(cyc, key=abs)
                if any(abs(x) <= R for x in cyc) and mn != 0 and gcd(abs(mn), c) == 1:
                    cyc_all.append((c, mn, len(cyc), sum(1 for x in cyc if x % 2)))
            seen.update(path)
    n_all = len(cyc_all)
    in_rec = [t for t in cyc_all if (t[2], t[3]) in rec3]
    big = [t for t in cyc_all if abs(t[1]) >= 5 * t[0]]
    big_rec = [t for t in big if (t[2], t[3]) in rec3]
    pos_c = [t for t in cyc_all if t[1] > 0]
    neg_c = [t for t in cyc_all if t[1] < 0]
    say(f"      primitive cycles of 3x+c, 5 <= c <= 199, meeting [-{R}, {R}]: {n_all}")
    say(f"      in record cells: {len(in_rec)} = {100*len(in_rec)/n_all:.1f} %"
        f"   (positive {sum(1 for t in pos_c if (t[2],t[3]) in rec3)}/{len(pos_c)},"
        f" negative {sum(1 for t in neg_c if (t[2],t[3]) in rec3)}/{len(neg_c)})")
    say(f"      with |min| >= 5c: {len(big_rec)} of {len(big)} = {100*len(big_rec)/max(1,len(big)):.1f} %")
    check(n_all == 257, "257 primitive cycles in the control family")
    check(round(100 * len(in_rec) / n_all, 1) == 21.4, "21.4 % of them in record cells")
    check((len(big_rec), len(big)) == (53, 89), "size-matched (|min| >= 5c): 53 of 89 = 59.6 %")
    rec5 = records(5, 200)
    five = []
    for start in (0, -1, 1, 13, 17):
        orb, x = [start], step(start, 5, 1)
        while x != start:
            orb.append(x)
            x = step(x, 5, 1)
            assert len(orb) < 100
        five.append((len(orb), sum(1 for y in orb if y % 2)))
    check(five == [(1, 0), (2, 1), (5, 2), (7, 3), (7, 3)] and all(c in rec5 for c in five),
          f"5x+1: the five known cycles sit in cells {five}, all record cells of log2 5")

    # ---------------------------------------------------------------- 3. figurate families
    section("3. Triangle, square, cube against the dropping classes")
    S_MAX = 700
    N = dropping_word_counts(S_MAX)
    check(N[:14] == [1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045],
          f"N(s), s = 0..13: {N[:14]}  (A100982 with the class 'even' prepended)")
    check([level_of(s) for s in range(8)] == [1, 2, 4, 5, 7, 8, 10, 12]
          and [level_of(s) + s for s in range(8)] == [1, 3, 6, 8, 11, 13, 16, 19],
          "Terras levels 1, 2, 4, 5, 7, 8, 10, 12 <-> site Dset_1, 3, 6, 8, 11, 13, 16, 19")
    check(stop_ks(5) == (2, 1) and stop_ks(3) == (4, 2),
          "site examples: drop(5) = 3 = 2 + 1, drop(3) = 6 = 4 + 2")
    K = 16
    M = 1 << K
    for kk in range(1, K + 1):
        vals = sorted(tri(n) % (1 << kk) for n in range(1 << kk))
        assert vals == list(range(1 << kk)), kk
    check(True, f"T_0 .. T_(2^k - 1) is a complete residue system mod 2^k for k = 1..{K}")
    check(all(tri(n) == tri(-1 - n) for n in range(-50, 50)), "T_n = T_(-1-n): the fold is n <-> -1-n")
    check(sorted(pow(x, 3, M) for x in range(1, M, 2)) == list(range(1, M, 2)),
          f"x -> x^3 permutes the odd residues mod 2^{K}")
    check({(x * x) % 8 for x in range(1, 200, 2)} == {1}, "every odd square is 1 mod 8")

    def class_counts(values, q=3, d=1):
        """Count values by Terras level, using the actual stopping time for v >= 2.
        v = 0 and v = 1 (which do not drop) are filed by residue for 3x+1: 0 -> level 1,
        1 -> level 2; for 3x-1 the value 1 is a fixed point and is filed under 'never'."""
        cnt: dict = {}
        for vv in values:
            if vv == 0:
                key = 1
            elif vv == 1:
                key = 2 if (q, d) == (3, 1) else "never"
            else:
                ks = stop_ks(vv, q, d)
                key = ks[0] if ks else "never"
            cnt[key] = cnt.get(key, 0) + 1
        return cnt

    natural = {level_of(s): N[s] * (M >> level_of(s)) for s in range(0, 11)}     # levels <= 16
    check(max(natural) == 16 and sum(natural.values()) < M, f"levels <= {K}: {sorted(natural)}")
    cT = class_counts(tri(n) for n in range(M))
    cC = class_counts(n ** 3 for n in range(M))
    cS = class_counts(n * n for n in range(M))
    cSm = class_counts((n * n for n in range(M)), 3, -1)
    check(all(cT.get(k, 0) == natural[k] for k in natural),
          f"first 2^{K} triangular numbers: exactly N(k) 2^(K-k) in every class of level k <= {K}")
    check(all(cC.get(k, 0) == natural[k] for k in natural),
          f"first 2^{K} cubes: exactly N(k) 2^(K-k) in every class of level k <= {K}")
    check(cS == {1: M // 2, 2: M // 2}, f"first 2^{K} squares under 3x+1: {cS}  (Dset_1 and Dset_3 only)")
    odd = M // 2
    say(f"      squares under 3x-1 by Terras level: "
        f"{ {k: cSm[k] for k in sorted(k for k in cSm if isinstance(k, int))} }, never: {cSm.get('never', 0)}")
    check(cSm.get(1) == M // 2 and cSm.get(2, 0) == 0 and cSm.get(4, 0) == 0,
          "squares under 3x-1: half in Dset_1 (even), none in Dset_3 or Dset_6")
    check((cSm.get(5), cSm.get(7), cSm.get(8)) == (odd // 4, odd // 8, 5 * odd // 32),
          "odd squares under 3x-1: shares 1/4, 1/8, 5/32 at Terras levels 5, 7, 8")
    n_classes_m = len([k for k in cSm if isinstance(k, int)])
    say(f"      distinct stopping times of the first 2^{K} squares under 3x-1: {n_classes_m}")

    t31, t3m = set(), set()
    for n in range(2, 200001):
        sq = n * n
        t31.add(stop_ks(sq)[0])
        t3m.add(stop_ks(sq, 3, -1)[0])
    check(t31 == {1, 2}, "squares n^2, 2 <= n <= 200000, under 3x+1: Terras stopping times {1, 2} only")
    check(len(t3m) == 103, f"same squares under 3x-1: {len(t3m)} distinct stopping times")
    c31, c3m = set(), set()
    for n in range(2, 50001):
        sc = tri(n) ** 2                              # 1^3 + ... + n^3
        c31.add(stop_ks(sc)[0])
        c3m.add(stop_ks(sc, 3, -1)[0])
    check(c31 == {1, 2} and len(c3m) > 20,
          f"sums of cubes T_n^2, 2 <= n <= 50000: two stopping times under 3x+1, {len(c3m)} under 3x-1")
    # mirror form of Theorem 2': n^2 under 3x-1 behaves as -n^2 under 3x+1
    def stop_abs(n, q, d, cap=10000):
        x, k = n, 0
        while k < cap:
            x = step(x, q, d)
            k += 1
            if abs(x) < abs(n):
                return k
        return None
    check(all(stop_abs(n * n, 3, -1) == stop_abs(-n * n, 3, 1) for n in range(2, 3000)),
          "mirror: stopping time of n^2 under 3x-1 = that of -n^2 under 3x+1 (in absolute value), n < 3000")
    # polygonal trichotomy by v_2(s - 2), residue level
    ok = True
    for sg in range(3, 35):
        P = lambda n, a=sg - 2: n + a * n * (n - 1) // 2
        k = 10
        a = sg - 2
        v2 = (a & -a).bit_length() - 1
        if v2 == 0:      # fold: Z/2^(k+1) -> Z/2^k exactly 2-to-1
            img = Counter(P(n) % (1 << k) for n in range(1 << (k + 1)))
            ok &= len(img) == 1 << k and set(img.values()) == {2}
        elif v2 == 1:    # collapse: as many values as squares mod 2^k
            ok &= len({P(n) % (1 << k) for n in range(1 << (k + 1))}) == len({(n * n) % (1 << k) for n in range(1 << k)})
        else:            # isometry: permutation of Z/2^k
            ok &= len({P(n) % (1 << k) for n in range(1 << k)}) == 1 << k
    check(ok, "polygonal trichotomy by v_2(s - 2): fold / collapse / isometry, s = 3..34, mod 2^10")

    # ---------------------------------------------------------------- 4. totient
    section("4. Eight solutions of phi(x) = 36")
    X = 3000                                        # phi(x) >= sqrt(x/2), so phi(x) <= 36 forces x <= 2592
    phi = list(range(X + 1))
    for p in range(2, X + 1):
        if phi[p] == p:
            for m in range(p, X + 1, p):
                phi[m] -= phi[m] // p
    check(all(phi[x] ** 2 * 2 >= x for x in range(1, X + 1)), "phi(x) >= sqrt(x/2) on the sieve range")
    sols = [x for x in range(1, X + 1) if phi[x] == 36]
    check(sols == [37, 57, 63, 74, 76, 108, 114, 126], f"phi(x) = 36: {sols}")
    mult = {m: sum(1 for x in range(1, X + 1) if phi[x] == m) for m in range(1, 37)}
    check(mult[36] == 8 and all(mult[m] != 8 for m in range(1, 36)),
          "36 is the least n with exactly eight solutions (multiplicities below 36: "
          + ", ".join(f"{m}:{c}" for m, c in mult.items() if c and m < 36) + ")")
    check(all(pr - 1 == v for pr, v in ((7, 2 * 3), (19, 2 * 9), (37, 4 * 9))),
          "7 = 2*3 + 1, 19 = 2*3^2 + 1, 37 = 2^2 3^2 + 1: lattice points (1,1), (1,2), (2,2)")

    def lattice_parts(x: int):
        parts, al, be = [], 0, 0
        while x % 2 == 0:
            x //= 2
            al += 1
        while x % 3 == 0:
            x //= 3
            be += 1
        if al:
            parts.append((f"2^{al}", (al - 1, 0)))
        if be:
            parts.append((f"3^{be}", (1, be - 1)))
        p = 5
        while x > 1:
            if x % p == 0:
                x //= p
                assert x % p != 0
                m, i, j = p - 1, 0, 0
                while m % 2 == 0:
                    m //= 2
                    i += 1
                while m % 3 == 0:
                    m //= 3
                    j += 1
                assert m == 1
                parts.append((str(p), (i, j)))
            p += 2
        return parts
    for x in sols:
        parts = lattice_parts(x)
        tot = (sum(v[0] for _, v in parts), sum(v[1] for _, v in parts))
        check(tot == (2, 2), f"{x:>4} = " + " * ".join(n for n, _ in parts) + "  ->  "
              + " + ".join(str(v) for _, v in parts) + " = (2,2)")
    check(sum(1 for x in sols if x % 37 == 0) == 2 and sum(1 for x in sols if x % 19 == 0) == 3
          and sum(1 for x in sols if x % 7 == 0) == 2 and sols.count(108) == 1,
          "8 = 1 (no prime: 108) + 2 (with 7) + 3 (with 19) + 2 (with 37)")
    check(all(phi[x] // 2 == 18 == 2 * 3 ** 2 for x in sols) and phi[10] == 4,
          "degree of cos(2 pi/n) is phi(n)/2 = 18 = 2 * 3^2 for the eight n; phi(10) = 4 = 2^2")
    check(abs(math.cos(2 * math.pi / 10) - (1 + 5 ** 0.5) / 4) < 1e-15, "cos(2 pi/10) = (1 + sqrt 5)/4")

    # ---------------------------------------------------------------- 5. the solvable map F
    section("5. F(n) = sum over d | n of tau(d)")
    LIMF = 10 ** 6
    tau = [0] * (LIMF + 1)
    for dd in range(1, LIMF + 1):
        for m in range(dd, LIMF + 1, dd):
            tau[m] += 1
    Fv = [0] * (LIMF + 1)
    for dd in range(1, LIMF + 1):
        t = tau[dd]
        for m in range(dd, LIMF + 1, dd):
            Fv[m] += t
    def F_big(n: int) -> int:                     # by the product formula, for values past the sieve
        out, p = 1, 2
        while p * p <= n:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            out *= tri(e + 1)
            p += 1
        return out * (3 if n > 1 else 1)
    check(all(Fv[n] == F_big(n) for n in range(1, 5001)), "F from the definition = product of T_(a+1), n <= 5000")
    orbit = [72]
    while len(orbit) < 9:
        orbit.append(Fv[orbit[-1]])
    check(orbit == [72, 60, 54, 30, 27, 10, 9, 6, 9], "orbit " + " -> ".join(map(str, orbit)))
    check([n for n in range(1, LIMF + 1) if Fv[n] == n] == [1, 3, 18, 36], "fixed points up to 10^6: 1, 3, 18, 36")
    check([n for n in range(1, LIMF + 1) if Fv[n] >= n] == [1, 2, 3, 4, 6, 8, 12, 18, 24, 36],
          "F(n) < n outside {1, 2, 3, 4, 6, 8, 12, 18, 24, 36}, n <= 10^6")
    check(Fv[6] == 9 and Fv[9] == 6, "2-cycle 6 <-> 9")
    check(Fv[36] == 36 and tau[36] == 9, "the nine divisors of 36 have 36 divisors in all: F(36) = 36")
    check([n for n in range(1, LIMF + 1) if 2 * Fv[n] == 3 * n] == [2, 4, 6, 12],
          "F(n) = 3n/2 exactly at n = 2, 4, 6, 12 (n <= 10^6)")
    ends: dict = {}
    for n in range(1, LIMF + 1):
        x = n
        while x not in (1, 3, 18, 36, 6, 9):
            x = Fv[x]
        key = "{6,9}" if x in (6, 9) else x
        ends[key] = ends.get(key, 0) + 1
    check(sum(ends.values()) == LIMF and ends[36] == 1594 and ends[3] == 78498,
          f"every orbit from n <= 10^6 ends at 1, 3, 18, 36 or {{6,9}}: {ends}")
    def tau_k(k: int, exps) -> int:
        out = 1
        for e in exps:
            out *= comb(e + k - 1, e)
        return out
    check(all(tau_k(k, (2, 2)) == tri(k) ** 2 == sum(i ** 3 for i in range(1, k + 1)) for k in range(1, 200)),
          "tau_k(p^2 q^2) = T_k^2 = 1^3 + ... + k^3 for k < 200")
    def factor(n: int) -> dict:
        f, p = {}, 2
        while p * p <= n:
            while n % p == 0:
                f[p] = f.get(p, 0) + 1
                n //= p
            p += 1
        if n > 1:
            f[n] = f.get(n, 0) + 1
        return f
    fam, semi = [], []
    for k in range(2, 61):
        tk = tri(k)
        if tau_k(k, [2 * e for e in factor(tk).values()]) == tk ** 2:
            fam.append(k)
        f = factor(tk)
        if len(f) == 2 and all(e == 1 for e in f.values()):
            semi.append(k)
    check(fam == semi and fam[:6] == [3, 4, 5, 6, 10, 13],
          f"T_k^2 fixed by tau_k iff T_k = p*q: k = {fam} (k <= 60); fixed points "
          + ", ".join(str(tri(k) ** 2) for k in fam[:4]))

    section("5b. Dropping-word counts: Winkler's sandwich and the Bizley values")
    check(N[10] == 476 and N[36] == 38088111350198, f"N(10) = {N[10]}, N(36) = {N[36]}")
    F85 = lambda j: Fraction(comb(8 * j, 3 * j), 8 * j)
    F1912 = lambda j: Fraction(comb(19 * j, 7 * j), 19 * j)
    check(F85(2) - F85(1) ** 2 / 2 == 476, "N(10) = F_2 - F_1^2/2 with F_j = C(8j,3j)/(8j)  (convergent 8/5)")
    check(F1912(3) + F1912(1) * F1912(2) + F1912(1) ** 3 / 6 == N[36],
          "N(36) = F_3 + F_1 F_2 + F_1^3/6 with F_j = C(19j,7j)/(19j)  (convergent 19/12)")
    lo_eq, up_eq, bad = [], [], 0
    for s in range(1, 401):
        m = (3 ** s).bit_length() - 1              # floor(s log2 3)
        lo, up = Fraction(comb(m - 1, s - 1), s), Fraction(comb(m, s - 1), s)
        if not lo <= N[s] <= up:
            bad += 1
        if N[s] == lo:
            lo_eq.append(s)
        if N[s] == up:
            up_eq.append(s)
    check(bad == 0, "C(m-1,s-1)/s <= N(s) <= C(m,s-1)/s for s <= 400  (Winkler)")
    check(lo_eq == [1, 2, 7, 12, 53, 359] and up_eq == [1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306],
          f"equality orders <= 400: lower {lo_eq}, upper {up_eq}")
    none = [s for s in range(1, 17) if s not in set(lo_eq) | set(up_eq) | {4, 6, 10, 15}]
    check(none == [8, 9, 11, 13, 14, 16], f"orders <= 16 with no closed form of this type: {none}")
    mean = sum(Fraction(N[s], 3 ** s) for s in range(S_MAX + 1))
    say(f"      sum_(s <= {S_MAX}) N(s)/3^s = {float(mean):.10f}   (last term {float(Fraction(N[S_MAX], 3**S_MAX)):.2e})")
    check(abs(float(mean) - 1.6903605922) < 2e-9, "mean number of one-round predecessors = 1.69036059...")

    # ---------------------------------------------------------------- 6. cos 36 teaser
    section("6. The folded pentagon modulo 5 (teaser for the companion page)")
    luc = [2, 1]
    while len(luc) < 20:
        luc.append(luc[-1] + luc[-2])
    ok = True
    for k in range(0, 15):
        hits = 0
        for t in range(1 << k):
            x = 1 + 5 * t
            for _ in range(k):
                x = step(x)
            hits += x % 5 == 1
        ok &= 5 * hits == 2 ** k + 2 * (-1) ** k * luc[k]
    check(ok, "P(T^k(n) = 1 mod 5 | n = 1 mod 5) = (2^k + 2(-1)^k L_k)/(5 * 2^k), k <= 14, by brute force")
    try:
        import sympy as sp
        A = sp.zeros(5, 5)
        inv2 = pow(2, -1, 5)
        for x in range(5):
            A[x, (x * inv2) % 5] += 1
            A[x, ((3 * x + 1) * inv2) % 5] += 1
        xs = sp.symbols("x")
        cp = sp.factor(A.charpoly(xs).as_expr())
        check(sp.expand(cp - xs * (xs - 1) * (xs - 2) * (xs ** 2 + xs - 1)) == 0, f"charpoly(2 K_5) = {cp}")
    except ImportError:
        say("      sympy not available: characteristic polynomial not checked")
    check(abs(2 * math.cos(math.radians(144)) - (-phi_gold)) < 1e-15, "2 cos 144 deg = -phi, a root of x^2 + x - 1")
    check(3 + 2 == 5 == 3 ** 2 - 2 ** 2, "5 = 3 + 2 = 3^2 - 2^2")

    # ---------------------------------------------------------------- 7. further statements
    section("7. Further statements on the page")
    # 7a. class = actual dropping time for every class of level <= 24, apart from 0 and 1
    KMAX = 24
    alive = [(0, 0, 0)]                             # (least residue r mod 2^j, T^j(r), odd steps)
    n_classes, late = 0, []
    for j in range(KMAX):
        two_next = 1 << (j + 1)
        nxt = []
        for r, a, s in alive:
            for r2, a2 in ((r, a), (r + (1 << j), a + 3 ** s)):
                if a2 % 2:
                    a3, s3 = (3 * a2 + 1) // 2, s + 1
                else:
                    a3, s3 = a2 // 2, s
                if 3 ** s3 < two_next:              # the class of r2 mod 2^(j+1) drops here
                    n_classes += 1
                    if not a3 < r2:                 # ... and so does r2 itself, unless listed
                        late.append(r2)
                else:
                    nxt.append((r2, a3, s3))
        alive = nxt
    check(n_classes == 81119 == sum(N[:16]), f"{n_classes} dropping classes of level <= {KMAX}")
    check(sorted(late) == [0, 1],
          f"least residues that do not drop at their class level, levels <= {KMAX}: {sorted(late)}")

    # 7b. the residue law of the triangular numbers for 5x+1, with that rule's own shares
    def coeff_level(r: int, kk: int, q: int):
        x, s = r, 0
        for k in range(1, kk + 1):
            if x % 2:
                x, s = (q * x + 1) // 2, s + 1
            else:
                x //= 2
            if q ** s < 1 << k:
                return k
        return None
    K5 = 12
    nat5 = Counter(coeff_level(r, K5, 5) for r in range(1 << K5))
    tri5 = Counter(coeff_level(tri(n) % (1 << K5), K5, 5) for n in range(1 << K5))
    first = [Fraction(nat5[k], 1 << K5) for k in sorted(k for k in nat5 if k is not None)[:3]]
    check(first == [Fraction(1, 2), Fraction(1, 8), Fraction(1, 16)] and tri5 == nat5,
          f"5x+1: natural shares begin 1/2, 1/8, 1/16, and the first 2^{K5} triangular numbers carry them exactly")

    # 7c. bitwise NOT turns the 3x+1 map into the shifted 3x-1 map
    check(all(-1 - step(-1 - m) == m3(m + 1) - 1 for m in range(-2000, 2001)),
          "NOT T NOT (m) = T_(3x-1)(m + 1) - 1 for |m| <= 2000")

    # 7d. squares cover a sixth of the residues
    n_sq = len({(x * x) % M for x in range(M)})
    check(n_sq == (M // 2 + 4) // 3, f"{n_sq} squares modulo 2^{K}: a share {n_sq / M:.5f}, near 1/6")

    # 7e. Ljunggren: the only triangular numbers whose square is triangular are 0, 1, 6
    is_tri = lambda m: is_square(8 * m + 1)
    check([tri(n) for n in range(100000) if is_tri(tri(n) ** 2)] == [0, 1, 6],
          "T_n^2 is triangular only for T_n = 0, 1, 6 (n < 10^5): 36 is the only sum of the first n > 1 cubes that is triangular")
    check(is_tri(1 + 27) and is_tri(27 + 64), "but 1^3 + 3^3 = 28 and 3^3 + 4^3 = 91 are triangular: 'the first n cubes' matters")

    # 7f. destinations: exactly one integer drops onto a multiple of 3
    def dest(n: int, c: int, cap: int = 5000):
        x = n
        for _ in range(cap):
            x = x // 2 if x % 2 == 0 else 3 * x + c
            if x < n:
                return x
        return None
    DMAX = 30000
    for c in (1, -1):
        mult = [0] * (DMAX + 1)
        for n in range(2, 2 * DMAX + 1):
            dd = dest(n, c)
            if dd is not None and 0 < dd <= DMAX:
                mult[dd] += 1
        check(all(mult[dd] == 1 for dd in range(3, DMAX + 1, 3)),
              f"3x{c:+d}: exactly one n drops onto each multiple of 3 up to {DMAX} (mean multiplicity {sum(mult) / DMAX:.4f})")

    say()
    say(f"{len(FAILS)} failure(s); {time.time() - T0:.0f} s")
    (HERE / "check_thirty_six_page.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
