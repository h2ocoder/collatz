"""Skeptic check 4: Q1.4 (Stormer pairs, mixed-multiplier unit cells, multi-divisor maps).

Independent code path:
 * consecutive smooth pairs from a heap-free recursive generator of smooth numbers up to 10^15
   (no Pell equations), and a second, completely naive sieve below 2*10^6;
 * unit cells 2^k -+ 1 smooth for k <= 3000 (far beyond the LTE bound);
 * mixed words checked by plain iteration from every start in a window (no fixed-point formula);
 * deterministic multi-divisor maps T_P (divide by the smallest available prime below P,
   otherwise x -> P x + 1), P = 5, 7, 11, 13, searched by plain iteration on [-200000, 200000].

Output: v4_stormer.log
"""
import os
from itertools import permutations
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v4_stormer.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")
    LOG.flush()


def smooth_upto(primes, limit):
    res = []

    def rec(i, v):
        if i == len(primes):
            res.append(v)
            return
        p = primes[i]
        while v <= limit:
            rec(i + 1, v)
            v *= p
    rec(0, 1)
    res.sort()
    return res


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Consecutive P-smooth pairs below 10^15 (recursive enumeration) and below 2*10^6 (sieve)")
out("=" * 78)
PAIRS = {}
for P in ([2, 3], [2, 3, 5], [2, 3, 5, 7], [2, 3, 5, 7, 11], [2, 3, 5, 7, 11, 13]):
    sm = smooth_upto(P, 10 ** 15)
    pairs = [(a, b) for a, b in zip(sm, sm[1:]) if b - a == 1]
    # naive sieve
    L = 2_000_000
    rem = list(range(L + 2))
    for p in P:
        for m in range(p, L + 2, p):
            while rem[m] % p == 0:
                rem[m] //= p
    naive = [(n, n + 1) for n in range(1, L + 1) if rem[n] == 1 and rem[n + 1] == 1]
    assert naive == [pr for pr in pairs if pr[0] <= L]
    PAIRS[tuple(P)] = pairs
    out(f" P = {P}: {len(pairs)} pairs below 10^15, largest {pairs[-1]}")
assert [len(v) for v in PAIRS.values()] == [4, 10, 23, 40, 68]
out(" counts 4, 10, 23, 40, 68 = OEIS A002071; largest upper members 9, 81, 4375, 9801, 123201 = A117581.")
out(" (Completeness beyond 10^15 is Stormer's theorem, not this computation.)")

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. Unit cells: 2^k - 1 or 2^k + 1 smooth over M, k <= 3000")
out("=" * 78)
want = {(3,): [(1, 1), (1, 3), (2, 3), (3, 9)],
        (3, 5): [(1, 1), (1, 3), (2, 3), (2, 5), (3, 9), (4, 15)],
        (3, 5, 7): [(1, 1), (1, 3), (2, 3), (2, 5), (3, 7), (3, 9), (4, 15), (6, 63)],
        (3, 5, 7, 11): [(1, 1), (1, 3), (2, 3), (2, 5), (3, 7), (3, 9), (4, 15), (5, 33), (6, 63)],
        (3, 5, 7, 11, 13): [(1, 1), (1, 3), (2, 3), (2, 5), (3, 7), (3, 9), (4, 15), (5, 33), (6, 63),
                            (6, 65), (12, 4095)]}
for M in want:
    cells = []
    for k in range(1, 3001):
        for N in ((1 << k) - 1, (1 << k) + 1):
            r = N
            for p in M:
                while r % p == 0:
                    r //= p
            if r == 1:
                cells.append((k, N))
    n_st = len(PAIRS[tuple([2] + list(M))])
    out(f" M = {list(M)}: {len(cells)} unit cells (k, N): {cells}   [{len(cells)} of {n_st} Stormer pairs]")
    assert cells == want[M]
    # every one of them is a Stormer pair with a pure power of two; and conversely
    st = PAIRS[tuple([2] + list(M))]
    pure = sorted((max(a, b).bit_length() - 1 if (max(a, b) & (max(a, b) - 1)) == 0 else
                   min(a, b).bit_length() - 1, a if a % 2 else b)
                  for a, b in st if any(x & (x - 1) == 0 and x > 1 for x in (a, b)) and (a % 2 or b % 2))
    assert sorted(cells) == pure, (cells, pure)
out(" -> 4/4, 6/10, 8/23, 9/40, 11/68 confirmed.  NOTE: 'unit cells = Stormer pairs with a pure power")
out("    of two on one side' is true BY DEFINITION (a unit cell is a consecutive pair {2^k, N}); only")
out("    the counts and the finiteness bound carry information.")

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Mixed-multiplier words by plain iteration (no fixed-point formula).")
out("   For each arrangement of the letters, search x in [-5000, 5000] with: letter 0 applied to")
out("   an even value, letter q applied to an odd value, and the word returning to x.")
out("=" * 78)


def run_word(word, x):
    y = x
    for L in word:
        if L == 0:
            if y % 2:
                return None
            y //= 2
        else:
            if y % 2 == 0:
                return None
            y = (L * y + 1) // 2
    return y


def canon(word):
    return min(word[i:] + word[:i] for i in range(len(word)))


for letters, label in (((3, 0), "4 - 3"), ((3, 3, 0), "8 - 9"), ((5, 0), "4 - 5"),
                       ((3, 5, 0, 0), "16 - 15"), ((7, 0, 0), "8 - 7"),
                       ((3, 3, 7, 0, 0, 0), "64 - 63"), ((3, 11, 0, 0, 0), "32 - 33"),
                       ((5, 13, 0, 0, 0, 0), "64 - 65")):
    words = set(permutations(letters))
    cyc = {}
    n_ok = 0
    for w in words:
        hits = [x for x in range(-5000, 5001) if run_word(w, x) == x]
        if len(hits) == 1:
            n_ok += 1
            x = hits[0]
            orb = []
            y = x
            for L in w:
                orb.append(y)
                y = y // 2 if L == 0 else (L * y + 1) // 2
            cyc.setdefault(canon(w), orb)
    out(f" cell {label}: {len(words)} words, {n_ok} with exactly one consistent integer fixed point, "
        f"{len(cyc)} necklaces")
    if len(cyc) <= 3:
        for c_, orb in sorted(cyc.items()):
            out(f"      {c_}: {orb}")
    assert n_ok == len(words)
out(" -> 16 - 15: 3 cycles (7,11,28,14 / 5,13,20,10 / 9,14,7,18 up to rotation); 64 - 63: 10.  Confirmed.")
out("    7 is multiplied by 3 in one cycle and by 5 in another: this is a semigroup, not a map.")

# ------------------------------------------------------------------ 4
out("")
out("=" * 78)
out("4. Deterministic multi-divisor maps T_P: divide by the smallest prime < P that divides x,")
out("   otherwise x -> P x + 1.  (Prior art for T_5, T_7 on positive integers: T. Oliveira e Silva,")
out("   sweet.ua.pt/tos/px+1.html; OEIS A133421 ff.)  All cycles meeting [-200000, 200000].")
out("=" * 78)


def px1_cycles(P, divisors, B=200000, cap=10 ** 40, max_steps=20000):
    def f(x):
        for d in divisors:
            if x % d == 0:
                return x // d
        return P * x + 1
    done = set()
    cycles = {}
    for n0 in range(-B, B + 1):
        if n0 == 0:
            continue
        path = []
        pos = {}
        y = n0
        while y not in pos and y not in done and abs(y) < cap and len(path) < max_steps:
            pos[y] = len(path)
            path.append(y)
            y = f(y)
        if y in pos:
            cy = path[pos[y]:]
            m = min(cy, key=lambda z: (abs(z), z))
            i = cy.index(m)
            cycles[frozenset(cy)] = cy[i:] + cy[:i]
        done.update(path)
    return sorted(cycles.values(), key=lambda c_: (len(c_), abs(c_[0])))


n_unit = n_all = 0
for P, divs in ((5, (2, 3)), (7, (2, 3, 5)), (11, (2, 3, 5, 7)), (13, (2, 3, 5, 7, 11))):
    cyc = px1_cycles(P, divs)
    out(f" {P}x+1 with divisors {divs}: {len(cyc)} cycles")
    for cy in cyc:
        mul = sum(1 for z in cy if all(z % d for d in divs))
        dcount = {d: 0 for d in divs}
        for z in cy:
            for d in divs:
                if z % d == 0:
                    dcount[d] += 1
                    break
        Ndiv = 1
        for d, e in dcount.items():
            Ndiv *= d ** e
        Nmul = P ** mul
        n_all += 1
        n_unit += abs(Ndiv - Nmul) == 1
        out(f"      length {len(cy):2d}, min {cy[0]:6d}: divide by {Ndiv}, multiply by {Nmul}, "
            f"difference {Ndiv - Nmul:+d}   {cy if len(cy) <= 14 else str(cy[:8]) + ' ...'}")
out(f" -> {n_unit} of {n_all} cycles found have (divide, multiply) differing by +-1, i.e. come from a")
out("    Stormer pair; the others are 'accidents' in the sense of Q1.1-c.")

LOG.close()
