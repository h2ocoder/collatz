"""Audit checks for site/explore/dropping-dictionary.md and SturmianBridge.vue.

Recomputes every number the page prints.  Exact integer arithmetic for the
word counts; mpmath-free (fractions / big ints only), floats only for display.
"""
from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction

BETA = math.log2(3)


def floor_s_log2_3(s: int) -> int:
    """floor(s*log2 3) exactly: largest m with 2^m <= 3^s."""
    return (3 ** s).bit_length() - 1


def N_words(s_max: int) -> list[int]:
    """N(s) = number of shortcut dropping words with s ones (A100982, offset 1).

    Beatty form: N(s) = #{1 <= t_1 < ... < t_{s-1} : t_i <= floor(i*log2 3)}.
    DP over the position of each successive 1.
    Returns list indexed by s, with index 0 = 1 (the word '0' / E).
    """
    out = [1, 1]
    # cur[t] = number of ways with t_i = t
    cur = {1: 1}  # t_1 = 1 (only choice since floor(log2 3) = 1)
    for s in range(2, s_max + 1):
        # N(s) counts sequences t_1..t_{s-1}
        out.append(sum(cur.values()))
        i = s  # next index
        m = floor_s_log2_3(i)
        nxt: dict[int, int] = defaultdict(int)
        # prefix sums
        keys = sorted(cur)
        acc = 0
        idx = 0
        for t in range(1, m + 1):
            while idx < len(keys) and keys[idx] < t:
                acc += cur[keys[idx]]
                idx += 1
            if acc:
                nxt[t] = acc
        cur = nxt
    return out


def words_bruteforce(s: int):
    """All dropping words (3n+1 / n/2 convention, letters O,E) with s odd steps.

    Coefficient definition: word over {O,E}, O always followed by E, never
    3^o < 2^e at an interior prefix, and 3^o < 2^e at the end.
    Returns list of strings.
    """
    res = []

    def rec(word, o, e, last_o):
        # try O
        if not last_o and o + 1 <= s:
            rec(word + "O", o + 1, e, True)
        # try E
        if 3 ** o < 2 ** (e + 1):
            if o == s:
                res.append(word + "E")
        else:
            rec(word + "E", o, e + 1, False)

    if s == 0:
        return ["E"]
    rec("O", 1, 0, True)
    return res


def word_affine(word: str):
    """dest = (3^s n + C) / 2^e for the word; return (s, e, C)."""
    mult, add = Fraction(1), Fraction(0)
    s = e = 0
    for ch in word:
        if ch == "O":
            mult, add = 3 * mult, 3 * add + 1
            s += 1
        else:
            mult, add = mult / 2, add / 2
            e += 1
    C = add * 2 ** e
    assert C.denominator == 1
    return s, e, int(C)


def word_residue(word: str) -> int:
    """The residue r mod 2^e of the integers n following the word."""
    s, e, C = word_affine(word)
    # find r by building bit by bit
    r, mod = 0, 1
    mult, add = Fraction(1), Fraction(0)
    for ch in word:
        # value = mult*n + add ; n = r + mod*t ; need parity
        val = mult * r + add
        assert val.denominator == 1
        coef = mult * mod
        assert coef.denominator == 1
        if coef % 2 == 0:
            par = int(val) % 2
            assert (par == 1) == (ch == "O"), "word not realisable?"
        else:
            par = int(val) % 2
            want = 1 if ch == "O" else 0
            if par != want:
                r += mod
            mod *= 2
        if ch == "O":
            mult, add = 3 * mult, 3 * add + 1
        else:
            mult, add = mult / 2, add / 2
    return r, mod


def drop(n: int):
    """(k, s, dest) for the 3n+1 / n/2 map; None if no drop within cap."""
    x, k, s = n, 0, 0
    while True:
        if x & 1:
            x = 3 * x + 1
            s += 1
        else:
            x >>= 1
        k += 1
        if x < n:
            return k, s, x
        if k > 100000:
            return None


def main() -> None:
    print("=== 1. counts ===")
    S = 2500
    N = N_words(S)
    print("N(0..13) =", N[:14])
    bf = [len(words_bruteforce(s)) for s in range(0, 13)]
    print("brute    =", bf)
    assert bf == N[:13]
    print("A100982 (offset 1) begins 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045")
    print("page list              = 1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045")
    print(" -> page list == [w_0=1] + A100982 :", N[:14] == [1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045])

    print("\n=== 2. e_s: ceil vs floor+1 ===")
    for s in range(0, 6):
        fl = floor_s_log2_3(s)
        ce = fl if s == 0 else fl + 1
        print(f" s={s}: ceil(s log2 3)={ce}  floor+1={fl+1}  3^s={3**s}  2^(floor+1)={2**(fl+1)}"
              f"  in [3^s,2*3^s)? {3**s <= 2**(fl+1) < 2*3**s}")
    # words agree: length e for every word of level s
    for s in range(0, 10):
        es = {word_affine(w)[1] for w in words_bruteforce(s)}
        assert es == {floor_s_log2_3(s) + 1}, (s, es)
    print(" every word of level s<=9 has e = floor(s log2 3)+1 (incl. s=0: e=1)")

    print("\n=== 3. forward mass sum_s w_s / 2^{e_s} ===")
    for label, e0 in (("e_0 = ceil(0) = 0", 0), ("e_0 = floor(0)+1 = 1", 1)):
        tot = Fraction(0)
        marks = {}
        for s in range(0, S + 1):
            e = e0 if s == 0 else floor_s_log2_3(s) + 1
            tot += Fraction(N[s], 2 ** e)
            if s in (13, 28, 50, 100, 200, 500, 1000, 2000, 2500):
                marks[s] = float(tot)
        print(" ", label, {k: f"{v:.9f}" for k, v in marks.items()})

    print("\n=== 4. backward mass sum_s w_s / 3^s ===")
    tot = Fraction(0)
    for s in range(0, S + 1):
        tot += Fraction(N[s], 3 ** s)
        if s in (5, 13, 28, 50, 100, 200, 500, 1000, 2000, 2500):
            print(f"  up to s={s}: {float(tot):.9f}")

    print("\n=== 5. growth ===")
    lam = BETA ** BETA / (BETA - 1) ** (BETA - 1)
    print(f" lambda = {lam:.6f}; log3 lambda = {math.log(lam, 3):.5f}; lambda/3 = {lam/3:.5f}")
    for s in (50, 100, 200, 500, 1000, 2000, 2500):
        root = math.exp(math.log(N[s]) / s) if N[s] < 10 ** 300 else math.exp((math.log(N[s] >> 900) + 900 * math.log(2)) / s)
        print(f"  N({s})^(1/{s}) = {root:.5f}")

    print("\n=== 6. residues mod 3^s reached at level s: distinct? nested? ===")
    prev = None
    for s in range(1, 13):
        ws = words_bruteforce(s)
        res = []
        for w in ws:
            ss, e, C = word_affine(w)
            # d with predecessor: 2^e d = C mod 3^s
            inv = pow(2 ** e, -1, 3 ** s)
            res.append((C * inv) % 3 ** s)
        distinct = len(set(res)) == len(res)
        nested = None
        if prev is not None:
            nested = all((r % 3 ** (s - 1)) in prev for r in res)
        shown = sorted(set(res)) if s <= 5 else "..."
        print(f"  s={s}: words={len(ws)} distinct residues={len(set(res))} "
              f"all distinct={distinct} contained in level s-1 set={nested} {shown}")
        prev = set(res)

    print("\n=== 7. d = 10 predecessors; dictionary examples ===")
    for n in (11, 13, 15, 20):
        print("  n =", n, "-> (k, s, dest) =", drop(n))

    print("\n=== 8. mean one-round predecessors per destination (direct, no dictionary) ===")
    for X in (3000, 10 ** 5, 10 ** 6):
        cnt = 0
        for n in range(2, 2 * X + 2):
            r = drop(n)
            if r[2] <= X - 1 and r[2] >= 2:
                cnt += 1
        print(f"  d in [2,{X}): mean #predecessors = {cnt / (X - 2):.5f}")

    print("\n=== 9. Beatty increments e_{s+1}-e_s, s = 0.. (with e_s=floor(s log2 3)+1) ===")
    inc_floor = [floor_s_log2_3(s + 1) - floor_s_log2_3(s) for s in range(0, 13)]
    print("  floor version from s=0:", inc_floor)
    e_ceil = [0] + [floor_s_log2_3(s) + 1 for s in range(1, 14)]
    print("  ceil  version from s=0:", [e_ceil[s + 1] - e_ceil[s] for s in range(0, 13)])
    print("  page prints           : 2,1,2,1,2,2,1,2,1,2,2,1")

    print("\n=== 10. continued fractions ===")

    def cf(x, n):
        out = []
        for _ in range(n):
            a = math.floor(x)
            out.append(a)
            x = 1 / (x - a)
        return out

    def convergents(c):
        h0, h1, k0, k1 = 1, c[0], 0, 1
        out = [(h1, k1)]
        for a in c[1:]:
            h0, h1 = h1, a * h1 + h0
            k0, k1 = k1, a * k1 + k0
            out.append((h1, k1))
        return out

    a6 = math.log(3) / math.log(6)
    print("  log6 3 =", a6, "CF", cf(a6, 11))
    print("  convergents", convergents(cf(a6, 11)))
    print("  log2 3 CF", cf(BETA, 10))
    print("  convergents", convergents(cf(BETA, 10)))
    for q in (13, 31, 44, 75, 106, 137, 791):
        eps = q * a6 - round(q * a6)
        print(f"   q={q}: eps = {eps:+.5f}  (round = {round(q*a6)})")

    print("\n=== 11. SturmianBridge RK_TABLE vs N(o)*2^o ===")
    table = {1: 1, 3: 2, 6: 4, 8: 16, 11: 48, 13: 224, 16: 768, 19: 3840,
             21: 21760, 24: 88576, 26: 487424, 29: 1968128,
             32: 10653696, 34: 50855936, 37: 261275648, 39: 1278242816,
             42: 6571913216, 44: 30811815936, 47: 154189103104,
             50: 755015057408, 52: 3445824487424, 55: 17035728519168}
    for o in range(0, 23):
        k = o + floor_s_log2_3(o) + 1
        true = N[o] * 2 ** o
        t = table.get(k)
        flag = "" if t == true else f"  <-- MISMATCH (table/2^o = {t / 2**o if t else None})"
        print(f"  o={o:2d} k={k:2d} N(o)={N[o]:>12d} N*2^o={true:>16d} table={t}{flag}")

    print("\n=== 12. R_19: every representative r in [2, 2^19) of the class drops at step 19 ===")
    ws = words_bruteforce(7)
    bad = 0
    tot = 0
    for w in ws:
        r, mod = word_residue(w)
        assert mod == 2 ** 12
        for j in range(2 ** 7):
            n = r + mod * j
            tot += 1
            if n < 2:
                bad += 1
                print("   representative < 2:", n)
                continue
            d = drop(n)
            if d[0] != 19:
                bad += 1
                print("   fails:", n, d)
    print(f"  {tot} residues, {bad} not dropping at step 19")


if __name__ == "__main__":
    main()
