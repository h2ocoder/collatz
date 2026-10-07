"""Fixer's own verification of every number written into the 'explore' pages.

Independent of explore_check_*.py (the auditor's scripts): different code for
the word counts, the stopping times and the wobble statistics.  Prints only.

    python -X utf8 explore_fix_verify.py            # everything except the slow parts
    python -X utf8 explore_fix_verify.py slow       # adds the 10^7 and 20000-term runs
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction

import numpy as np

SLOW = len(sys.argv) > 1 and sys.argv[1] == "slow"
BETA = math.log2(3)
LOG6 = math.log(6)
ALPHA = math.log(3) / LOG6


def fl(s: int, q: int = 3) -> int:
    """floor(s*log2 q), exact."""
    return (q ** s).bit_length() - 1


# ------------------------------------------------------------------ words
def level_profile(s: int, q: int = 3) -> dict[int, int]:
    """f[t] = number of dropping words of level s whose LAST odd step comes after
    t even steps.  Word = odd/even steps of the map x -> qx+1, x -> x/2 (single
    steps), no two odd steps adjacent, q^o > 2^e at every proper prefix, q^o < 2^e
    at the end.  The i-th odd step sits after t_i evens with
    0 = t_1 < t_2 < ... and t_{i+1} <= floor(i log2 q)."""
    f = {0: 1}
    for i in range(1, s):
        m = fl(i, q)
        g: dict[int, int] = {}
        acc = 0
        prev = sorted(f)
        j = 0
        for t in range(1, m + 1):
            while j < len(prev) and prev[j] < t:
                acc += f[prev[j]]
                j += 1
            if acc:
                g[t] = acc
        f = g
    return f


def counts(s_max: int, q: int = 3) -> list[int]:
    """N_q(s) for s = 0..s_max (N(0) = 1: the word E), by one pass of the DP."""
    out = [1]
    f = {0: 1}
    for s in range(1, s_max + 1):
        out.append(sum(f.values()))
        m = fl(s, q)
        g: dict[int, int] = {}
        acc = 0
        prev = sorted(f)
        j = 0
        for t in range(1, m + 1):
            while j < len(prev) and prev[j] < t:
                acc += f[prev[j]]
                j += 1
            if acc:
                g[t] = acc
        f = g
    return out


def words_direct(s: int) -> list[str]:
    """Dropping words with s odd steps by direct search on the coefficient test."""
    if s == 0:
        return ["E"]
    res: list[str] = []
    stack = [("O", 1, 0)]
    while stack:
        w, o, e = stack.pop()
        # next letter E
        if 3 ** o < 2 ** (e + 1):
            if o == s:
                res.append(w + "E")
        else:
            stack.append((w + "E", o, e + 1))
        # next letter O (not after O)
        if w[-1] == "E" and o < s:
            stack.append((w + "O", o + 1, e))
    return res


def affine(word: str) -> tuple[int, int, int]:
    """(s, e, C) with dest = (3^s n + C) / 2^e."""
    c = Fraction(0)
    s = e = 0
    for ch in word:
        if ch == "O":
            c = 3 * c + 1
            s += 1
        else:
            c /= 2
            e += 1
    C = c * 2 ** e
    assert C.denominator == 1
    return s, e, int(C)


def drop(n: int, q: int = 3, cap: int = 10 ** 6, sign: int = 1):
    """(k, s, d): steps, odd steps, first value below n (single-step convention)."""
    x, k, s = n, 0, 0
    while k < cap:
        if x & 1:
            x = q * x + sign
            s += 1
        else:
            x >>= 1
        k += 1
        if x < n:
            return k, s, x
    return None


def orbit(n: int) -> list[int]:
    seq = [n]
    while n != 1:
        n = 3 * n + 1 if n & 1 else n >> 1
        seq.append(n)
    return seq


def wobble(seq: list[int]) -> np.ndarray:
    w = np.zeros(len(seq))
    acc = 0.0
    for j, x in enumerate(seq[:-1]):
        if x & 1:
            acc += math.log1p(1.0 / (3.0 * x)) / LOG6
        w[j + 1] = acc
    return w


def eps(q: int) -> float:
    return q * ALPHA - round(q * ALPHA)


def cf(x: float, n: int) -> list[int]:
    out = []
    for _ in range(n):
        a = math.floor(x)
        out.append(a)
        x = 1 / (x - a)
    return out


def convergents(c: list[int]) -> list[tuple[int, int]]:
    h0, h1, k0, k1 = 1, c[0], 0, 1
    out = [(h1, k1)]
    for a in c[1:]:
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        out.append((h1, k1))
    return out


# ================================================================== A
def part_dictionary() -> None:
    print("=== A. dropping-dictionary.md ===")
    N = counts(520)
    direct = [len(words_direct(s)) for s in range(0, 13)]
    print("A1 N(0..13) DP    :", N[:14])
    print("   direct search  :", direct)
    oeis = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950,
            312455, 663535, 1900470, 5936673, 13472296, 39993895, 87986917, 257978502, 820236724]
    print("   N(1..25) == A100982 data fetched from oeis.org:", N[1:26] == oeis)
    print("   page list 1,1,1,2,3,7,... == [w_0 = 1] + A100982:", N[:14] == [1] + oeis[:13])

    ok = True
    for s in range(0, 11):
        for w in words_direct(s):
            if affine(w)[1] != fl(s) + 1:
                ok = False
    print("A2 every word of level s <= 10 has floor(s log2 3) + 1 halvings (E: 1):", ok)
    print("   ceil(0 * log2 3) =", math.ceil(0 * BETA), "; 2^e_s in (3^s, 2*3^s] for s = 0..200:",
          all(3 ** s < 2 ** (fl(s) + 1) <= 2 * 3 ** s for s in range(201)))

    fwd = Fraction(0)
    bwd = Fraction(0)
    for s in range(0, 521):
        fwd += Fraction(N[s], 2 ** (fl(s) + 1))
        bwd += Fraction(N[s], 3 ** s)
        if s in (13, 50, 100, 200, 500, 520):
            print(f"A3 s <= {s:3d}: forward sum = {float(fwd):.10f}   backward sum = {float(bwd):.10f}")
    fwd_ceil0 = fwd + Fraction(1, 1) - Fraction(1, 2)
    print(f"   with e_0 = ceil(0) = 0 the forward sum would be {float(fwd_ceil0):.6f}")

    print("A4 predecessors of 10:", {n: drop(n) for n in (11, 13, 15, 20)})

    prev = None
    alld = True
    nested_any = False
    for s in range(1, 13):
        res = []
        for w in words_direct(s):
            _, e, C = affine(w)
            res.append(C * pow(2 ** e, -1, 3 ** s) % 3 ** s)
        alld &= len(set(res)) == len(res)
        if prev is not None and all(r % 3 ** (s - 1) in prev for r in res):
            nested_any = True
        if s <= 2:
            print(f"A5 level {s}: residues {sorted(res)} mod {3 ** s}")
        prev = set(res)
    print("   residues distinct at every level s <= 12:", alld, "; some level contained in the one below:", nested_any)

    hits = genuine = 0
    fails = []
    rule = True
    nonpos = 0
    for s in range(0, 9):
        for w in words_direct(s):
            _, e, C = affine(w)
            for d in range(1, 3000):
                num = 2 ** e * d - C
                if num % 3 ** s:
                    continue
                n = num // 3 ** s
                hits += 1
                if n <= 0:
                    nonpos += 1
                g = n >= 2 and drop(n) == (s + e, s, d)
                genuine += g
                if g != (n > d):
                    rule = False
                if not g:
                    fails.append((d, w, n))
    print(f"A6 levels <= 8, 1 <= d < 3000: candidates {hits}, genuine {genuine}, failures {fails}, "
          f"non-positive candidates {nonpos}, genuine <=> n > d: {rule}")

    for X in (3000, 10 ** 6):
        cnt = 0
        for n in range(2, 2 * X + 1):
            x = n
            while True:
                x = 3 * x + 1 if x & 1 else x >> 1
                if x < n:
                    break
            if 2 <= x < X:
                cnt += 1
        print(f"A7 mean number of n with first value below n equal to d, over 2 <= d < {X}: {cnt / (X - 2):.5f}")
    # the figure's histogram: letters of at most 22 steps only
    cnt = 0
    for n in range(2, 6001):
        k, s, d = drop(n)
        if k <= 22 and 2 <= d < 3000:
            cnt += 1
    print(f"   same, counting only n with dropping time <= 22, 2 <= d < 3000: {cnt / 2998:.4f}")

    e = [fl(s) + 1 for s in range(0, 15)]
    print("A8 e_s, s = 0..14:", e)
    print("   increments from s = 0:", [e[i + 1] - e[i] for i in range(13)])
    print("   increments from s = 1:", [e[i + 1] - e[i] for i in range(1, 13)])

    c6 = cf(ALPHA, 11)
    c2 = cf(BETA, 9)
    print("A9 CF log6 3:", c6, " denominators:", [k for _, k in convergents(c6)])
    conv2 = convergents(c2)
    print("   CF log2 3:", c2, " convergents:", conv2)
    for p, q in conv2[2:8]:
        k = q + fl(q) + 1
        print(f"   p/q = {p}/{q}: p+q = {p + q}; q*log2 3 = {q * BETA:.4f}; letter length at level q = {k}"
              f" ({'p+q' if k == p + q else 'p+q+1' if k == p + q + 1 else '??'})")
    for s in (13, 31, 137):
        print(f"   s = {s}: s*log2 3 = {s * BETA:.4f}")
    print("   27/44 between 8/13 and 19/31:", 8 / 13 > 27 / 44 > 19 / 31 or 8 / 13 < 27 / 44 < 19 / 31,
          "; 44 = 13 + 31, 27 = 8 + 19")

    lam = BETA ** BETA / (BETA - 1) ** (BETA - 1)
    print(f"A10 lambda = {lam:.6f}; lambda/3 = {lam / 3:.5f}; N(s)^(1/s) at s = 100, 300, 520: "
          + ", ".join(f"{math.exp(math.log(N[s]) / s):.4f}" for s in (100, 300, 520)))

    # T^j(2^j - 1) = 3^j - 1 for the shortcut map
    okT = True
    for j in range(1, 40):
        x = 2 ** j - 1
        for _ in range(j):
            x = (3 * x + 1) // 2 if x & 1 else x // 2
        okT &= x == 3 ** j - 1
    print("A13 shortcut map: T^j(2^j - 1) = 3^j - 1 for j < 40:", okT)
    vals = []
    for j in (4, 6, 8, 10, 12, 14):
        seen = set()
        for L in range(1 << j):
            x = L
            for _ in range(j):
                x = (3 * x + 1) // 2 if x & 1 else x // 2
            seen.add(x)
        vals.append(len(seen))
    print("    distinct values of T^j(L), L < 2^j, j = 4, 6, ..., 14:", vals)

    # 3x - 1: direct non-droppers below 2^20
    nd = [n for n in range(2, 1 << 20) if drop(n, 3, 2000, -1) is None]
    print("A12 3x-1: integers in [2, 2^20) that have not dropped after 2000 steps:", nd)
    # ... and its classes are the negatives: n drops under 3x-1 with word w iff -n follows w under 3x+1
    okneg = True
    for s in range(1, 7):
        for w in words_direct(s):
            _, e, C = affine(w)
            r = (-C * pow(3 ** s, -1, 2 ** e)) % 2 ** e      # 3x+1 class of the word
            rm = (-r) % 2 ** e                                # its negative
            n = rm + 2 ** e * 5                               # a large member
            x, word = n, ""
            for _ in range(s + e):
                if x & 1:
                    x, word = 3 * x - 1, word + "O"
                else:
                    x, word = x >> 1, word + "E"
            okneg &= word == w and x < n and x == (3 ** s * n - C) // 2 ** e
    print("    3x-1: the class of each word (levels 1..6) is the negative of the 3x+1 class, dest = (3^s n - C)/2^e:", okneg)


# ================================================================== B
def part_sturmian() -> None:
    print("\n=== B. sturmian-bridge.md / SturmianBridge.vue / sturmian-fractals.md ===")
    N = counts(60)
    table = {1: 1, 3: 2, 6: 4, 8: 16, 11: 48, 13: 224, 16: 768, 19: 3840,
             21: 21760, 24: 88576, 26: 487424, 29: 1968128,
             32: 10862592, 34: 65904640, 37: 288964608, 39: 1672249344,
             42: 7140147200, 44: 40954101760, 47: 173941719040,
             50: 996393615360, 52: 6225052827648, 55: 28253452500992}
    mine = {o + fl(o) + 1: N[o] * 2 ** o for o in range(0, 22)}
    print("B1 corrected q = 3 table equals N(o) * 2^o for o = 0..21:", mine == table,
          "; largest below 2^53:", max(mine.values()) < 2 ** 53)
    old = {32: 10653696, 34: 50855936, 37: 261275648, 39: 1278242816, 42: 6571913216,
           44: 30811815936, 47: 154189103104, 50: 755015057408, 52: 3445824487424, 55: 17035728519168}
    print("   old component values that differ:", sum(1 for k in old if old[k] != mine[k]), "of", len(old))
    # brute-force |R_32| : count residues mod 2^(e) of level 12 = number of words
    print("   direct word count at level 12:", len(words_direct(12)), "-> |R_32| =", len(words_direct(12)) * 2 ** 12)
    for q, tab in ((5, {1: 1, 4: 2, 7: 8, 10: 40, 14: 224, 17: 1792}),
                   (7, {1: 1, 4: 2, 8: 8, 12: 56, 16: 480}),
                   (9, {1: 1, 5: 2, 9: 12, 13: 96})):
        Nq = counts(8, q)
        got = {o + fl(o, q) + 1: Nq[o] * 2 ** o for o in range(0, len(tab))}
        print(f"   q = {q}: component table matches N_q(o) * 2^o:", got == tab)

    for q in (3, 5, 7, 9):
        Nq = counts(400, q)
        tot = Fraction(0)
        marks = []
        for o in range(0, 401):
            tot += Fraction(Nq[o], 2 ** (fl(o, q) + 1))
            if o in (20, 100, 200, 400):
                marks.append(f"o<={o}: {float(tot):.6f}")
        print(f"B2 q = {q}: sum N_q(o)/2^(floor(o log2 q)+1): " + ", ".join(marks))

    # R_19 representatives
    bad = tot = 0
    for w in words_direct(7):
        s, e, C = affine(w)
        r = (-C * pow(3 ** s, -1, 2 ** e)) % 2 ** e
        for j in range(2 ** 7):
            n = r + 2 ** e * j
            tot += 1
            if n < 2 or drop(n)[0] != 19:
                bad += 1
    print(f"B3 R_19: {tot} residues below 2^19, {bad} of them not dropping at exactly step 19")

    # 5x+1 below 2^16
    cyc = set()
    for st in (1, 13, 17):
        x = st
        while True:
            cyc.add(x)
            x = 5 * x + 1 if x & 1 else x >> 1
            if x == st:
                break
    nd = [n for n in range(2, 1 << 16) if drop(n, 5, 2000) is None]
    print(f"B4 5x+1: {len(nd)} of {(1 << 16) - 2} integers in [2, 2^16) have not dropped after 2000 steps "
          f"({len(nd) / ((1 << 16) - 2):.4f}); on the known cycles: {[n for n in nd if n in cyc]}; "
          f"known cycle elements {len(cyc)}")

    # sign of c2 - c1 against the gap rule
    exc = []
    first = []
    for o in range(1, 61):
        f = level_profile(o)
        e_o = fl(o) + 1
        c2c1 = sum(v if (e_o - t) % 2 else -v for t, v in f.items())
        gap = 1 + (fl(o) - fl(o - 1))
        want = 1 if gap == 3 else -1
        got = (c2c1 > 0) - (c2c1 < 0)
        if got != want:
            exc.append((o, gap, c2c1))
        if o <= 8:
            first.append((o, gap, c2c1))
    print("B5 (o, gap, c2 - c1) for o <= 8:", first)
    print("   o in 1..60 where sign(c2 - c1) differs from the gap rule:", exc)

    for p, q in ((3, 2), (8, 5), (19, 12), (84, 53)):
        g = [(j * p) // q - ((j - 1) * p) // q for j in range(1, 6 * q + 1)]
        per = all(g[i] == g[i + q] for i in range(len(g) - q))
        agree = 0
        while (agree + 1) * p // q == fl(agree + 1):
            agree += 1
        print(f"B6 slope {p}/{q}: gaps periodic with period {q} from the first symbol: {per}; "
              f"floor(j p/q) = floor(j log2 3) for j = 1..{agree}")

    print("   12*log2(3/2) =", round(12 * (BETA - 1), 4), "; 53*log2(3/2) =", round(53 * (BETA - 1), 4))

    if SLOW:
        # parity of A100982 by the same DP over GF(2)
        L = 20000
        par = np.zeros(L + 1, dtype=np.uint8)
        f = np.zeros(1, dtype=np.uint8)
        f[0] = 1
        for s in range(1, L + 1):
            par[s] = int(f.sum()) & 1
            m = fl(s)
            c = np.bitwise_xor.accumulate(f)
            # g[t] = xor of f[0..t-1], t = 1..m
            g = np.zeros(m + 1, dtype=np.uint8)
            upto = min(len(c), m)
            g[1:upto + 1] = c[:upto]
            if m > len(c):
                g[len(c) + 1:] = c[-1]
            f = g
        seq = par[1:]
        Nsmall = counts(40)
        print("B7 parity DP agrees with exact counts for o <= 40:",
              all(int(seq[o - 1]) == Nsmall[o] % 2 for o in range(1, 41)))
        dens = float(seq.mean())
        print(f"   share of 1s among the first {L} terms: {dens:.5f}; "
              f"{abs(dens - 0.5) / math.sqrt(0.25 / L):.1f} standard errors from 1/2")
        for n in (5, 8, 11, 12):
            blocks = {seq[i:i + n].tobytes() for i in range(L - n + 1)}
            print(f"   distinct blocks of length {n}: {len(blocks)} of {2 ** n}")

        # coefficient stopping time = stopping time for 2 <= n <= 10^7 (shortcut map)
        LIM = 10 ** 7
        floors = np.array([fl(i) for i in range(600)], dtype=np.int64)
        viol = 0
        longest = 0
        biggest = 0
        for lo in range(2, LIM + 1, 10 ** 6):
            n0 = np.arange(lo, min(lo + 10 ** 6, LIM + 1), dtype=np.int64)
            x = n0.copy()
            o = np.zeros(len(n0), dtype=np.int64)
            k = 0
            while len(x):
                k += 1
                odd = (x & 1) == 1
                x = np.where(odd, (3 * x + 1) >> 1, x >> 1)
                biggest = max(biggest, int(x.max()))
                o = o + odd
                coef = k > floors[o]            # 2^k > 3^o
                below = x < n0
                viol += int((coef != below).sum())
                done = coef | below
                if done.any():
                    longest = max(longest, k)
                keep = ~done
                n0, x, o = n0[keep], x[keep], o[keep]
        print(f"B8 2 <= n <= 10^7: steps at which 'coefficient below 1' and 'value below n' disagree: {viol}; "
              f"longest shortcut stopping time {longest}; largest value met {biggest} (int64 safe: {biggest < 2 ** 61})")


# ================================================================== C
def part_wobble() -> None:
    print("\n=== C. log6-wobble.md ===")
    seq = orbit(670617279)
    n_pts = len(seq)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    w = wobble(seq)
    deltas = [(x, math.log1p(1 / (3 * x)) / LOG6) for x in seq[:-1] if x & 1]
    tot = sum(d for _, d in deltas)
    print(f"C1 orbit of 670617279: {n_pts} points; W_total = {tot:.5f}; "
          f"{100 * sum(d for x, d in deltas if x < 100) / tot:.1f}% from odd values below 100; sigma_W = {w.std():.4f}")
    ms = np.arange(1, 151)
    D = np.array([abs(np.exp(2j * np.pi * m * w).mean()) for m in ms])
    sig = w.std()
    print(f"   min D(m), m <= 150: {D.min():.3f} at m = {ms[D.argmin()]}; Gaussian of that sigma: half at m = "
          f"{math.sqrt(math.log(2) / (2 * math.pi ** 2)) / sig:.1f}, value at m = 60: {math.exp(-2 * math.pi ** 2 * 3600 * sig ** 2):.4f}")
    k = np.arange(n_pts)
    for m in (13, 31, 44, 75, 106, 137):
        a_orb = abs(np.exp(2j * np.pi * m * theta).mean())
        a_rot = abs(np.exp(2j * np.pi * m * k * ALPHA).mean())
        print(f"C2 m = {m:3d} eps = {eps(m):+.5f}: rotation {a_rot:.4f}, orbit {a_orb:.4f}, ratio {a_orb / a_rot:.2f}, D(m) = {D[m - 1]:.3f}")
    print(f"C3 share of points with W_k below a tenth of W_total: {(w < 0.1 * w[-1]).mean():.3f}; "
          f"number of odd steps: {len(deltas)}")
    for q in (31, 44):
        d = (theta[q:] - theta[:-q] + 0.5) % 1.0 - 0.5
        print(f"C4 q = {q}: RMS {q}-step miss = {math.sqrt((d ** 2).mean()):.4f}; smallest |miss| = {np.abs(d).min():.5f}")

    # the 500 orbits of the resonance script
    used, n = 0, 10 ** 6 + 1
    worst_id = 0.0
    max_w = 0.0
    max_sum = 0.0
    first_n, last_n = None, None
    while used < 500:
        s = orbit(n)
        n += 2
        if len(s) < 250:
            continue
        used += 1
        first_n = first_n or n - 2
        last_n = n - 2
        th = np.array([(math.log(x) / LOG6) % 1.0 for x in s])
        ww = wobble(s)
        max_w = max(max_w, float(ww[-1]))
        for q in (13, 31, 44, 75, 106, 137):
            if len(s) <= q:
                continue
            d = (th[q:] - th[:-q] + 0.5) % 1.0 - 0.5
            dw = ww[q:] - ww[:-q]
            worst_id = max(worst_id, float(np.abs(np.abs(d) - np.abs(eps(q) + dw)).max()))
            max_sum = max(max_sum, float(np.abs(eps(q) + dw).max()))
    print(f"C5 500 orbits (odd seeds {first_n}..{last_n}, at least 250 points): max | |miss| - |eps_q + dW| | = {worst_id:.1e}; "
          f"largest |eps_q + dW| = {max_sum:.3f}; largest W_total = {max_w:.4f}")

    # rigid rotation, 3450 points, 12 bands
    def nn_gaps(th: np.ndarray) -> np.ndarray:
        m = len(th)
        idx = np.arange(m)
        ang = 2 * np.pi * th
        X, Y = idx * np.cos(ang), idx * np.sin(ang)
        nn = np.empty(m, dtype=int)
        for lo in range(0, m, 400):
            hi = min(lo + 400, m)
            d2 = (X[lo:hi, None] - X) ** 2 + (Y[lo:hi, None] - Y) ** 2
            d2[np.arange(hi - lo), np.arange(lo, hi)] = np.inf
            nn[lo:hi] = d2.argmin(1)
        return np.abs(nn - idx)

    for th0 in (0.0, 0.37, 0.81):
        th = (th0 + np.arange(3450) * ALPHA) % 1.0
        g = nn_gaps(th)
        b = np.linspace(0, 3450, 13).astype(int)
        modes = []
        for lo, hi in zip(b[:-1], b[1:]):
            v, c = np.unique(g[lo:hi], return_counts=True)
            modes.append(int(v[c.argmax()]))
        print(f"C6 rigid rotation by log6 3, 3450 points, start {th0}: modal index gap per band = {modes}")

    best = (0.0, 0)
    for m in range(3, 100000, 2):
        s = orbit(m)
        O = sum(1 for x in s[:-1] if x & 1)
        E = len(s) - 1 - O
        r = math.log(2) * E - math.log(3) * O - math.log(m)
        if r > best[0]:
            best = (r, m)
    print(f"C7 largest 2^E/(3^O n) over odd n < 10^5: {math.exp(best[0]):.9f} at n = {best[1]}; "
          f"log6 of it = {best[0] / LOG6:.6f}")
    s = orbit(27)
    O = sum(1 for x in s[:-1] if x & 1)
    T = len(s) - 1
    e_book = O * math.log2(6) - (T - math.log2(27))
    print(f"C8 n = 27: s = {O}, T = {T}; eps := s*log2 6 - (T - log2 n) = {e_book:.5f}; "
          f"-W_total*log2 6 = {-wobble(s)[-1] * math.log2(6):.5f}")
    print(f"   resonance dip altitudes 6.12, 4.62, 3.62, 2.38 as values: "
          + ", ".join(f"{6 ** a:.0f}" for a in (6.12, 4.62, 3.62, 2.38)))


# ================================================================== D
def part_misc() -> None:
    print("\n=== D. alpha-sequence.md / binary-shortcut.md ===")

    def alphas(n: int) -> list[int]:
        out = []
        while n > 1:
            if n & 1:
                n = 3 * n + 1
                a = 0
                while n % 2 == 0:
                    n //= 2
                    a += 1
                out.append(a)
            else:
                n //= 2
        return out

    def quality(n: int) -> float:
        rad = math.prod(set(alphas(n)))
        return math.log2(n) / math.log2(rad)

    for n in (3, 7, 27, 5461, 7253):
        a = alphas(n)
        print(f"D1 n = {n}: {len(a)} odd steps, alphas {a if len(a) < 8 else str(a[:6]) + '...'}, distinct {sorted(set(a))}")
    print("   27: steps", len(orbit(27)) - 1, "peak", max(orbit(27)))
    top = sorted(((quality(n), n) for n in range(3, 10000, 2)), reverse=True)[:3]
    print("   highest quality among odd n < 10000:", [(n, round(q, 3)) for q, n in top])
    print("D2 (4^k - 1)/3 has alpha sequence [2k] for k = 2..40:",
          all(alphas((4 ** k - 1) // 3) == [2 * k] for k in range(2, 41)),
          "; quality at k = 8, 20, 38:", [round(quality((4 ** k - 1) // 3), 2) for k in (8, 20, 38)])
    ok = True
    for n in range(3, 20001, 2):
        m = 0
        while (n >> m) & 1:
            m += 1
        a = alphas(n)
        ok &= a[:m - 1] == [1] * (m - 1) and (len(a) < m or a[m - 1] >= 2)
    print("D3 odd n < 20000 with m trailing 1-bits: alphas start with m-1 ones, then one that is >= 2:", ok)


if __name__ == "__main__":
    part_dictionary()
    part_sturmian()
    part_wobble()
    part_misc()
