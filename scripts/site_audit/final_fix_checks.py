"""Final-fixer checks: every number the final edits put on (or leave on) the site.

Run:  python -X utf8 scripts/site_audit/final_fix_checks.py
"""
from __future__ import annotations

import math
from fractions import Fraction

L23 = math.log2(3)
ok_all = True


def check(label: str, cond: bool, detail: str = "") -> None:
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'FAIL'}] {label}" + (f" -- {detail}" if detail else ""))


def fl(i: int) -> int:
    """floor(i*log2 3), exact."""
    return (3 ** i).bit_length() - 1


def k_of(o: int) -> int:
    return o + fl(o) + 1 if o > 0 else 1


# --------------------------------------------------------------------------
print("1. Sturmian Bridge, tip B: k_o against the crossings of y = x log2 3")
for o in range(1, 200):
    # crossings with x <= o: o vertical (x = 1..o) and floor(o*alpha) horizontal
    upto = o + fl(o)
    before = (o - 1) + fl(o)          # crossings strictly before the o-th vertical one
    assert k_of(o) == upto + 1
    assert k_of(o) == before + 2
check("k_o = 1 + (crossings up to and including the o-th vertical one), o < 200", True,
      f"k_1 = {k_of(1)}, k_2 = {k_of(2)}; crossings before the 1st, 2nd vertical: 1, 4")

# --------------------------------------------------------------------------
print("2. Sign rule, class by class")


def admissible_classes(o_max: int):
    """Parity vectors of the shortcut map T that end at their first coefficient drop.

    Yields (q, j, residue mod 2^j): q odd terms, j shortcut steps (= halvings).
    Prefix condition 3^q_i > 2^i for 1 <= i < j, final 3^q < 2^j.
    """
    out = []
    # state: (j, q, r, value T^j(r)) ; n = r + 2^j t  =>  T^j(n) = T^j(r) + 3^q t
    stack = [(0, 0, 0, 0)]
    while stack:
        j, q, r, val = stack.pop()
        for p in (0, 1):
            t = (p - val) % 2
            r2 = r + (t << j)
            v2 = val + t * 3 ** q
            assert v2 % 2 == p
            if p:
                v3, q2 = (3 * v2 + 1) // 2, q + 1
            else:
                v3, q2 = v2 // 2, q
            j2 = j + 1
            if 3 ** q2 < 2 ** j2:
                out.append((q2, j2, r2))
            elif q2 <= o_max:
                stack.append((j2, q2, r2, v3))
    return out


def collatz_drop(n: int):
    """(dropping time in single steps, destination)."""
    x, k = n, 0
    while True:
        x = 3 * x + 1 if x & 1 else x >> 1
        k += 1
        if x < n:
            return k, x


O_BRUTE = 10
classes = [c for c in admissible_classes(O_BRUTE) if 1 <= c[0] <= O_BRUTE]
P_brute = {}
D_brute = {}
for q, j, r in classes:
    n = r + (1 << j) * (10 ** 6 + 7)          # a large member of the class
    k, d = collatz_drop(n)
    assert k == q + j == k_of(q), (q, j, r, k)
    assert d % 3 in (1, 2)
    P_brute[q] = P_brute.get(q, 0) + 1
    D_brute[q] = D_brute.get(q, 0) + (1 if d % 3 == 2 else -1)
print("   classes per level (real integers, o = 1..10):", [P_brute[o] for o in range(1, O_BRUTE + 1)])
print("   c2 - c1           (real integers, o = 1..10):", [D_brute[o] for o in range(1, O_BRUTE + 1)])
check("class counts are A100982 from o = 1: 1, 1, 2, 3, 7, 12, 30, 85, 173, 476",
      [P_brute[o] for o in range(1, 11)] == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476])

# exact DP on parity words: M[e'] = prefixes reaching the i-th odd step after e' halvings.
# dest * 2^alpha = 3m + 1  =>  dest = 2^alpha mod 3: dest = 2 mod 3 iff alpha (halvings after
# the last odd step) is odd.  That one line is the whole 'dest mod 3' lemma.
OMAX = 400
M = {0: 1}
P, D = {}, {}
for i in range(1, OMAX + 1):
    e_i = fl(i) + 1
    P[i] = sum(M.values())
    D[i] = sum(v if (e_i - ep) % 2 else -v for ep, v in M.items())
    new, run, keys, idx = {}, 0, sorted(M), 0
    for e2 in range(1, fl(i) + 1):
        while idx < len(keys) and keys[idx] < e2:
            run += M[keys[idx]]
            idx += 1
        if run:
            new[e2] = run
    M = new
check("DP agrees with the real-integer count for o <= 10",
      all(P[o] == P_brute[o] and D[o] == D_brute[o] for o in range(1, O_BRUTE + 1)))
bad = []
A = {1: Fraction(1)}
bad_rec = []
for o in range(1, OMAX + 1):
    gap = k_of(o) - k_of(o - 1)
    eps = 1 if gap == 3 else -1
    if o < OMAX:
        A[o + 1] = (P[o] + (-1) ** gap * A[o]) / 2
    if D[o] != eps * A[o]:
        bad_rec.append(o)
    if ((D[o] > 0) - (D[o] < 0)) != eps:
        bad.append(o)
check(f"sign(c2 - c1) = gap rule for every o <= {OMAX} except o = 3", bad == [3], f"exceptions: {bad}")
check(f"c2 - c1 = eps_o * A_o (the recursion) for every o <= {OMAX}", bad_rec == [], f"mismatches: {bad_rec}")
check("c2 - c1 = 0 at o = 3", D[3] == 0)

# --------------------------------------------------------------------------
print("3. beta(s): the multiplier, and the number itself")


def beta(s: int) -> float:
    return fl(s) + 1 - s * L23


check("5 -> 4 loses log2(5/4) = 0.32 bits, beta(1) = 0.415",
      abs(math.log2(5 / 4) - 0.3219) < 1e-4 and abs(beta(1) - 0.4150) < 1e-4,
      f"{math.log2(5/4):.4f} vs {beta(1):.4f}")
check("3 -> 2 loses 0.585 bits, beta(2) = 0.830",
      abs(math.log2(3 / 2) - 0.585) < 1e-3 and abs(beta(2) - 0.830) < 1e-3)

N = 10 ** 7
tot_beta = 0.0
tot_actual = 0.0
cnt = 0
cst_bad = 0
never_at_least = 0
for n in range(3, N + 1, 2):
    x, k, s = n, 0, 0
    while True:
        if x & 1:
            x = 3 * x + 1
            s += 1
        else:
            x >>= 1
        k += 1
        if x < n:
            break
    if k - s != fl(s) + 1:
        cst_bad += 1
    b = fl(s) + 1 - s * L23
    lost = math.log2(n / x)
    if lost >= b:
        never_at_least += 1
    tot_beta += b
    tot_actual += lost
    cnt += 1
check(f"odd n <= {N}: halvings = floor(s log2 3) + 1 in every case (multiplier = 2^-beta(s))", cst_bad == 0,
      f"{cst_bad} exceptions")
check("the number itself loses LESS than beta(s) bits in every one of those drops", never_at_least == 0,
      f"{never_at_least} drops lose >= beta(s)")
check("mean beta(s) over odd n <= 10^7 is about 0.45", abs(tot_beta / cnt - 0.45) < 0.005,
      f"mean beta = {tot_beta/cnt:.4f}; mean bits lost by the number = {tot_actual/cnt:.4f}")

# --------------------------------------------------------------------------
print("4. The 44 in the article's polar plots")
a6 = math.log(3) / math.log(6)
check("44 radians = 7.003 turns", abs(44 / (2 * math.pi) - 7.003) < 5e-4, f"{44/(2*math.pi):.4f}")
check("44 * log_6 3 = 26.98", abs(44 * a6 - 26.98) < 5e-3, f"{44*a6:.4f}")

# --------------------------------------------------------------------------
print("5. Alphabet-rotation figure: the margins at the convergent denominators")
m = {s: fl(s) + 1 - s * L23 for s in (1, 2, 5, 12, 41, 53)}
print("   margins:", {s: round(v, 4) for s, v in m.items()})
check("margin near 0 at s = 5, 41 and near 1 at s = 12, 53",
      m[5] < 0.08 and m[41] < 0.02 and m[12] > 0.97 and m[53] > 0.99)

# --------------------------------------------------------------------------
print("6. Alpha Sequence: quality under 10000")


def quality(n: int) -> float:
    alphas = set()
    x = n
    while x > 1:
        if x & 1:
            v = 3 * x + 1
            a = 0
            while v % 2 == 0:
                v //= 2
                a += 1
            alphas.add(a)
            x = v
        else:
            x //= 2
    rad = 1
    for a in alphas:
        rad *= a
    return math.inf if rad <= 1 else math.log2(n) / math.log2(rad)


best_odd = max(range(3, 10000, 2), key=quality)
check("highest quality among odd n < 10000 is 7253", best_odd == 7253, f"{best_odd}: {quality(best_odd):.3f}")
check("9670 (even) scores 4.41, above 7253's 4.27", abs(quality(9670) - 4.41) < 0.005 and quality(9670) > quality(7253),
      f"{quality(9670):.3f} vs {quality(7253):.3f}")
check("a power of two scores infinity", quality(4096) == math.inf)

# --------------------------------------------------------------------------
print("7. Dropping-alphabet figure: 2^{e_s} in (3^s, 2*3^s] with e_s = floor(s log2 3) + 1")
check("holds for s = 0..300, with equality 2^{e_0} = 2*3^0 at s = 0 only",
      all(3 ** s < 2 ** (fl(s) + 1) <= 2 * 3 ** s for s in range(0, 301))
      and [s for s in range(0, 301) if 2 ** (fl(s) + 1) == 2 * 3 ** s] == [0])

print()
print("ALL OK" if ok_all else "SOME CHECKS FAILED")
