"""Q1.4  Stormer pairs and unit cells of mixed-multiplier affine words.

Shortcut letters:  '0': x -> x/2      'q': x -> (q x + 1)/2   for q in a set M of odd primes.
A word with k letters, a_q of them equal to q, composes to
      x -> (N x + C) / 2^k,   N = prod q^(a_q),      fixed point C / (2^k - N).
Unit cell: |2^k - N| = 1, i.e. {2^k, N} is a Stormer pair with a PURE power of two.

Non-shortcut letters (part E):  '/p': x -> x/p,  '*q': x -> q x + 1; a word composes to
      x -> (N_mul x + C) / N_div,  fixed point C / (N_div - N_mul).
Output: q14_stormer.log, q14_stormer.json
"""
import json
import os
from fractions import Fraction
from math import isqrt

from sympy.utilities.iterables import multiset_permutations

from hc_common import Tee, factorint_small

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q14_stormer.log"))
J = {}


# ---------------------------------------------------------------- A
def smooth_numbers(primes, limit):
    xs = [1]
    for p in primes:
        new = []
        for x in xs:
            v = x
            while v <= limit:
                new.append(v)
                v *= p
        xs = new
    return sorted(xs)


def pell_fundamental(N):
    """Fundamental solution of x^2 - N y^2 = 1 (N not a square), via continued fractions."""
    a0 = isqrt(N)
    m, d, a = 0, 1, a0
    h1, h0 = 1, a0
    k1, k0 = 0, 1
    while h0 * h0 - N * k0 * k0 != 1:
        m = d * a - m
        d = (N - m * m) // d
        a = (a0 + m) // d
        h1, h0 = h0, a * h0 + h1
        k1, k0 = k0, a * k0 + k1
    return h0, k0


def is_smooth(n, primes):
    for p in primes:
        while n % p == 0:
            n //= p
    return n == 1


def stormer_lehmer(primes):
    """All pairs (S, S+1) of P-smooth numbers, by Lehmer's (1964) form of Stormer's theorem:
    for every squarefree P-smooth q != 2 examine the first max(3, (p_max+1)/2) solutions of
    x^2 - 2 q y^2 = 1 and keep S = (x-1)/2 when S and S+1 are P-smooth."""
    sqfree = [1]
    for p in primes:
        sqfree += [x * p for x in sqfree]
    nsol = max(3, (max(primes) + 1) // 2)
    pairs = set()
    for q in sqfree:
        if q == 2:
            continue
        N = 2 * q
        x1, y1 = pell_fundamental(N)
        x, y = x1, y1
        for _ in range(nsol):
            S = (x - 1) // 2
            if x % 2 == 1 and is_smooth(S, primes) and is_smooth(S + 1, primes):
                pairs.add((S, S + 1))
            x, y = x1 * x + N * y1 * y, x1 * y + y1 * x
    return sorted(pairs)


out("=" * 78)
out("A. Consecutive P-smooth pairs: Stormer-Lehmer Pell method vs brute force below 10^18")
out("=" * 78)
stormer = {}
for primes in ([2, 3], [2, 3, 5], [2, 3, 5, 7], [2, 3, 5, 7, 11], [2, 3, 5, 7, 11, 13]):
    pl = stormer_lehmer(primes)
    sm = smooth_numbers(primes, 10 ** 18)
    bf = [(a, b) for a, b in zip(sm, sm[1:]) if b - a == 1]
    assert pl == bf, (primes, pl, bf)
    stormer[tuple(primes)] = pl
    out(f"P = {primes}: {len(pl)} pairs, largest {pl[-1]}   (Pell method == brute force < 10^18: True)")
    if len(primes) <= 4:
        out(f"     {pl}")
J["stormer_pairs"] = {str(list(k)): v for k, v in stormer.items()}
assert [len(stormer[k]) for k in stormer] == [4, 10, 23, 40, 68]

# ---------------------------------------------------------------- B
out("")
out("=" * 78)
out("B. Unit cells |2^k - N| = 1, N a product of primes of M (independent proof of")
out("   completeness: lifting-the-exponent bound 2^k - 1 <= B*k, B = prod p^v_p(2^ord_p(2) - 1))")
out("=" * 78)


def mult_order(a, p):
    o, x = 1, a % p
    while x != 1:
        x = x * a % p
        o += 1
    return o


def vp(n, p):
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


unit_cells = {}
for M in ([3], [3, 5], [3, 5, 7], [3, 5, 7, 11], [3, 5, 7, 11, 13]):
    B = 1
    for p in M:
        B *= p ** vp(2 ** mult_order(2, p) - 1, p)
    kmax = 1
    while 2 ** (kmax + 1) - 1 <= B * (kmax + 1):
        kmax += 1
    # beyond kmax the inequality 2^k - 1 <= B k fails for good (2^k grows faster)
    assert all(2 ** k - 1 > B * k for k in range(kmax + 1, kmax + 200))
    cells = []
    for k in range(1, kmax + 1):
        for N in (2 ** k - 1, 2 ** k + 1):
            if is_smooth(N, M):
                cells.append((k, N, 2 ** k - N, factorint_small(N) if N > 1 else {}))
    def pow2_exp(x):
        return x.bit_length() - 1 if x >= 2 and (x & (x - 1)) == 0 else None

    from_stormer = []
    for a, b in stormer[tuple([2] + M)]:
        if pow2_exp(a) is not None and b % 2 == 1:
            from_stormer.append((pow2_exp(a), b))
        if pow2_exp(b) is not None and a % 2 == 1:
            from_stormer.append((pow2_exp(b), a))
    mine = sorted((k, N) for k, N, _, _ in cells)
    out(f"M = {M}: B = {B}, only k <= {kmax} possible; unit cells (k, N, D=2^k-N, factor N):")
    for c in cells:
        out(f"      {c}")
    stormer_side = sorted(set(from_stormer))
    out(f"      pure-power-of-two Stormer pairs give the same list: {stormer_side == mine}"
        f"   ({len(mine)} of {len(stormer[tuple([2] + M)])} Stormer pairs)")
    assert stormer_side == mine
    unit_cells[tuple(M)] = cells
J["unit_cells"] = {str(list(k)): [(c[0], c[1], c[2], {str(p): e for p, e in c[3].items()})
                                  for c in v] for k, v in unit_cells.items()}

# ---------------------------------------------------------------- C
out("")
out("=" * 78)
out("C. Formal cycles in the unit cells (shortcut letters 0, q).  For every distinct")
out("   word: fixed point must be an integer, parities must be consistent (letter 0 on")
out("   even values, letter q on odd values), and iterating the letters must close up.")
out("=" * 78)


def apply_letter(L, x):
    if L == 0:
        if x % 2:
            return None
        return x // 2
    if x % 2 == 0:
        return None
    return (L * x + 1) // 2


def word_fixed_point(word):
    num, const, den = 1, 0, 1          # x -> (num x + const)/den
    for L in word:
        if L == 0:
            den *= 2
        else:
            num, const, den = num * L, L * const + den, den * 2
    return Fraction(const, den - num)


def canon(word):
    k = len(word)
    return min(tuple(word[i:] + word[:i]) for i in range(k))


formal = {}
printed = set()
for M, cells in unit_cells.items():
    rows = []
    letter_at = {}
    for (k, N, D, fac) in cells:
        letters = []
        for p, e in fac.items():
            letters += [p] * e
        letters += [0] * (k - len(letters))
        if len(letters) != k:
            out(f"   M={list(M)} cell k={k}, N={N}: needs {len(letters)} > k letters -- impossible, skipped")
            continue
        n_words = 0
        necklaces = {}
        bad = 0
        repeats = 0
        for word in multiset_permutations(letters):
            n_words += 1
            x = word_fixed_point(word)
            if x.denominator != 1:
                bad += 1
                continue
            x = int(x)
            y = x
            orb = []
            ok = True
            for L in word:
                orb.append(y)
                y = apply_letter(L, y)
                if y is None:
                    ok = False
                    break
            if not ok or y != x:
                bad += 1
                continue
            c = canon(word)
            if c not in necklaces:
                necklaces[c] = orb
                if len(set(orb)) != len(orb):
                    repeats += 1
                for L, v in zip(word, orb):
                    letter_at.setdefault(v, set()).add(L)
        prim = [c for c in necklaces if all(c[i:] + c[:i] != c for i in range(1, k))]
        rows.append({"k": k, "N": N, "D": D, "letters": letters, "words": n_words,
                     "bad_words": bad, "necklaces": len(necklaces), "primitive_necklaces": len(prim),
                     "cycles_with_repeated_value": repeats,
                     "examples": [{"word": list(c), "cycle": necklaces[c]} for c in sorted(necklaces)[:4]]})
        if (k, N) not in printed:      # cells of a smaller M are not printed again
            printed.add((k, N))
            out(f"   M={list(M)}  k={k}  N={N}  D={D:+d}: {n_words} words, {bad} failures, "
                f"{len(necklaces)} necklaces ({len(prim)} primitive), "
                f"{repeats} cycles visiting some integer twice")
            if len(necklaces) <= 12:
                for c in sorted(necklaces):
                    out(f"         word {c} : {necklaces[c]}")
    conflicts = {v: sorted(Ls) for v, Ls in letter_at.items()
                 if len([L for L in Ls if L != 0]) > 1}
    out(f"   M={list(M)}: odd integers that receive two different multipliers in different "
        f"formal cycles: {len(conflicts)}"
        + (f"  e.g. {dict(sorted(conflicts.items(), key=lambda kv: abs(kv[0]))[:6])}" if conflicts else ""))
    formal[str(list(M))] = {"cells": rows, "n_conflicting_integers": len(conflicts)}
    assert all(r["bad_words"] == 0 for r in rows)
J["formal_cycles_shortcut"] = formal

# ---------------------------------------------------------------- D
out("")
out("=" * 78)
out("D. ALL Stormer pairs as unit cells of affine semigroups (non-shortcut letters).")
out("   Pair (n, n+1): orientation '+': divide by the primes of n+1, multiply by those of n")
out("   (D = +1, cycles >= 0);  orientation '-': divide by primes of n, multiply by primes of")
out("   n+1 (D = -1, cycles <= 0).  A word is DETERMINISTIC-consistent if the multiplier is a")
out("   single prime q and the word obeys: divide by the smallest available divisor prime")
out("   whenever one divides x, else x -> q x + 1.")
out("=" * 78)


def nonshortcut_cycles(div_fac, mul_fac, limit_words=400000):
    letters = []
    for p, e in div_fac.items():
        letters += [("/", p)] * e
    for q, e in mul_fac.items():
        letters += [("*", q)] * e
    if not mul_fac or not div_fac:
        return None
    div_primes = sorted(div_fac)
    single_q = list(mul_fac)[0] if len(mul_fac) == 1 else None
    seen = set()
    n_words = bad = n_det = 0
    det_cycles = []
    for word in multiset_permutations(letters):
        n_words += 1
        if n_words > limit_words:
            return {"skipped": True}
        num, const, den = 1, 0, 1
        for typ, p in word:
            if typ == "/":
                den *= p
            else:
                num, const = num * p, p * const + den
        x = Fraction(const, den - num)
        if x.denominator != 1:
            bad += 1
            continue
        x = int(x)
        y = x
        orb = []
        ok = True
        det = single_q is not None
        for typ, p in word:
            orb.append(y)
            avail = [d for d in div_primes if y % d == 0]
            if typ == "/":
                if y % p:
                    ok = False
                    break
                if det and (not avail or avail[0] != p):
                    det = False
                y //= p
            else:
                if det and avail:
                    det = False
                y = p * y + 1
        if not ok or y != x:
            bad += 1
            continue
        key = min(tuple(word[i:] + word[:i]) for i in range(len(word)))
        if key in seen:
            continue
        seen.add(key)
        if det:
            n_det += 1
            m = min(orb, key=abs)
            i0 = orb.index(m)
            det_cycles.append(orb[i0:] + orb[:i0])
    return {"words": n_words, "bad": bad, "necklaces": len(seen),
            "deterministic": n_det if single_q is not None else "n/a",
            "det_cycles": det_cycles[:6]}


rowsD = []
for primes in ([2, 3, 5], [2, 3, 5, 7]):
    out(f" P = {primes}")
    out("   pair            split (primes of n | primes of n+1)   orient  necklaces  det-consistent  example")
    for (a, b) in stormer[tuple(primes)]:
        fa = factorint_small(a) if a > 1 else {}
        fb = factorint_small(b)
        pure2 = (a & (a - 1)) == 0 or (b & (b - 1)) == 0
        for orient, (div_fac, mul_fac) in (("+", (fb, fa)), ("-", (fa, fb))):
            res = nonshortcut_cycles(div_fac, mul_fac)
            if res is None:
                continue
            assert res.get("skipped") or res["bad"] == 0
            ex = res.get("det_cycles", [])[:1]
            out(f"   ({a},{b})".ljust(18) + f"{sorted(fa.items())} | {sorted(fb.items())}".ljust(42)
                + f"{orient}      {res.get('necklaces', '-'):<10} {res.get('deterministic', '-'):<15} {ex}")
            rowsD.append({"pair": [a, b], "orient": orient, "pure_power_of_two_side": pure2,
                          "div": {str(k): v for k, v in div_fac.items()},
                          "mul": {str(k): v for k, v in mul_fac.items()}, **res})
J["all_stormer_pairs_as_unit_cells"] = rowsD

with open(os.path.join(HERE, "q14_stormer.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q14_stormer.json")
out.close()
