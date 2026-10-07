"""Fixer's independent re-check for the 'structure-cycles' section of the site.

Every number that the edited pages state is recomputed here by a code path that does
not import or copy the auditor's scripts (structure_cycles_audit*.py):

  A. dropping classes of Terras level <= 24 (un-shortcut dropping time k <= 39), built by
     a tree walk over parity words, with exact Fraction affine maps;
  B. 2 <= n <= 10^7 in pure Python: coefficient stopping time versus stopping time;
  C. mutual information between Set(n) and Set(dest(n)) at three sample sizes, and the
     exact residue count behind "independent in density";
  D. bit-destruction table, order of 3 mod 2^B, the cycle pages' tables.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 structure_cycles_fix_check.py
Read-only: prints numbers, edits nothing.
"""
from __future__ import annotations

import itertools
import math
import time
from array import array
from collections import Counter, defaultdict
from fractions import Fraction

import numpy as np

T0 = time.time()


def f(n: int) -> int:
    return 3 * n + 1 if n & 1 else n >> 1


def drop(n: int):
    """Un-shortcut: (k, s, dest, orbit); orbit includes n and excludes dest."""
    x, k, s, orb = n, 0, 0, []
    while True:
        orb.append(x)
        if x & 1:
            s += 1
        x = f(x)
        k += 1
        if x < n:
            return k, s, x, orb


# --------------------------------------------------------------------------- A
print("=" * 78)
print("A. classes of Terras level <= 24, by a tree walk over parity words")
print("=" * 78)
LEVEL = 24
alive = [(0, 0, 0)]          # (residue r mod 2^i, odd steps s, T^i(r))
classes = []                 # (r, level, s)
for i in range(LEVEL):
    nxt = []
    for r, s, x in alive:
        for r2, x2 in ((r, x), (r + (1 << i), x + 3 ** s)):
            if x2 & 1:
                x3, s3 = (3 * x2 + 1) >> 1, s + 1
            else:
                x3, s3 = x2 >> 1, s
            if 3 ** s3 < 1 << (i + 1):
                classes.append((r2, i + 1, s3))
            else:
                nxt.append((r2, s3, x3))
    alive = nxt
per_level = Counter(lev for _, lev, _ in classes)
print("  classes per level:", sorted(per_level.items()))
print("  total classes:", len(classes), " residues still undropped at level 24:", len(alive))
lev_to_s = defaultdict(set)
for _, lev, s in classes:
    lev_to_s[lev].add(s)
assert all(len(v) == 1 for v in lev_to_s.values())
ks = sorted(lev + next(iter(ss)) for lev, ss in lev_to_s.items())
print("  un-shortcut dropping times k = level + s:", ks)
for lev, ss in sorted(lev_to_s.items()):
    s = next(iter(ss))
    assert 2 ** (lev - 1) <= 3 ** s < 2 ** lev          # level = floor(s log2 3) + 1
print("  every level equals floor(s log2 3) + 1 (exact integer test): True")
# an n with Terras stopping time > 24 has s >= 16 at step 24, so k >= 25 + 16 = 41
print("  smallest s with 3^s >= 2^24:", next(s for s in range(40) if 3 ** s >= 2 ** 24),
      " => any n outside these classes has k >= 41")

cst_exceptions = []
bad_affine = bad_sum = bad_max = bad_argmax = 0
members_checked = 0
per_k_classes = Counter()
for r, lev, s in classes:
    m = r if r >= 2 else r + (1 << lev)                 # least member >= 2
    k, s_seen, d, orb = drop(m)
    if k != lev + s or s_seen != s:
        cst_exceptions.append((r, lev, s, m, k, s_seen))
        continue
    per_k_classes[k] += 1
    a, b = Fraction(1), Fraction(0)
    maps = []
    for x in orb:
        maps.append((a, b))
        if x & 1:
            a, b = 3 * a, 3 * b + 1
        else:
            a, b = a / 2, b / 2
    assert a == Fraction(3 ** s, 2 ** lev)
    jstar = max(range(k), key=lambda i: maps[i][0])
    if orb.index(max(orb)) != jstar:
        bad_argmax += 1
    sa = sum(p for p, _ in maps)
    sb = sum(q for _, q in maps)
    for t in range(0, 4):
        n = m + t * (1 << lev)
        k2, s2, d2, orb2 = drop(n)
        members_checked += 1
        if k2 != k or s2 != s or d2 != a * n + b:
            bad_affine += 1
        if sum(orb2) != sa * n + sb:
            bad_sum += 1
        if max(orb2) != maps[jstar][0] * n + maps[jstar][1]:
            bad_max += 1
print(f"  least member >= 2 of each class: dropping time != level + s for {len(cst_exceptions)} classes",
      cst_exceptions[:5])
print(f"  members checked (4 per class): {members_checked}")
print(f"  dest != slope*n + C, or wrong (k, s): {bad_affine}")
print(f"  orbit sum not the affine function sum(a_i) n + sum(b_i): {bad_sum}")
print(f"  least member's maximum not at the largest-slope step: {bad_argmax}")
print(f"  orbit max != (largest-slope affine map)(n) among the 4 members: {bad_max}")
print("  classes per dropping set:", {k: per_k_classes[k] for k in (1, 3, 6, 8, 11, 13, 16)})
print("  residues excluded as < 2:", sorted(r for r, _, _ in classes if r < 2))
for n, want in ((5, Fraction(3, 4) * 5 + Fraction(1, 4)), (3, Fraction(9, 16) * 3 + Fraction(5, 16))):
    print(f"  dest({n}) = {drop(n)[2]}  formula {want}")
print("  5 and 9 are both 1 mod 4: dest", drop(5)[2], drop(9)[2], "(parities differ)")
print(f"  [{time.time() - T0:.0f}s]")

# --------------------------------------------------------------------------- B
print()
print("=" * 78)
print("B. 2 <= n <= 10^7, pure Python")
print("=" * 78)
LIM = 10_000_000
POW3 = [3 ** i for i in range(600)]
kk = array("H", [0]) * (LIM + 1)
dd = array("q", [0]) * (LIM + 1)
early = []                   # n whose coefficient 3^s/2^j fell below 1 before the drop
pairs = set()
for n in range(2, LIM + 1):
    x, s, j = n, 0, 0
    while True:
        if x & 1:
            x = (3 * x + 1) >> 1
            s += 1
        else:
            x >>= 1
        j += 1
        if x < n:
            break
        if POW3[s] < 1 << j:
            early.append(n)
    kk[n] = j + s
    dd[n] = x
    pairs.add((j, s))
print(f"  n with coefficient stopping time < stopping time: {len(early)} {early[:10]}")
viol = [(j, s) for j, s in pairs if not (2 ** (j - 1) <= 3 ** s < 2 ** j)]
print(f"  distinct (Terras level, s) pairs: {len(pairs)}; not of the form level = floor(s log2 3)+1: {viol}")
allk = sorted({j + s for j, s in pairs})
print("  dropping times seen (first 16):", allk[:16], " largest:", allk[-1])
spectrum = set()
for s in range(0, 400):
    j = 1
    while 2 ** j <= 3 ** s:
        j += 1
    spectrum.add(j + s)
print("  all inside {floor(s log2 6) + 1}:", set(allk) <= spectrum)
print(f"  [{time.time() - T0:.0f}s]")

# --------------------------------------------------------------------------- C
print()
print("=" * 78)
print("C. mixing.md")
print("=" * 78)
K = np.frombuffer(kk, dtype=np.uint16).astype(np.int64)
D = np.frombuffer(dd, dtype=np.int64)


def H(counts) -> float:
    c = np.asarray(list(counts), dtype=float)
    p = c[c > 0] / c.sum()
    return float(-(p * np.log2(p)).sum())


for N in (50_000, 500_000, 5_000_000):
    idx = np.arange(3, N)                    # n = 2 has destination 1, which has no set
    cur, nxt = K[idx], K[D[idx]]
    joint = Counter(zip(cur.tolist(), nxt.tolist()))
    hc, hn, hj = H(Counter(cur.tolist()).values()), H(Counter(nxt.tolist()).values()), H(joint.values())
    h_all = H(Counter(K[2:N].tolist()).values())
    print(f"  2 <= n < {N:>9,d}: pairs {len(idx):>9,d}  H(Set)={h_all:.4f}  H(cur)={hc:.4f}  "
          f"H(next)={hn:.4f}  H(next|cur)={hj - hc:.4f}  I={hc + hn - hj:.5f} bits")

# exact residue statement: one class A of level j, one residue b mod 2^B
ok = True
small = [(r, lev, s) for r, lev, s in classes if lev <= 8]
for r, lev, s in small:
    m = r if r >= 2 else r + (1 << lev)
    for B in (1, 3, 6):
        seen = Counter(drop(m + t * (1 << lev))[2] % (1 << B) for t in range(1 << B))
        if len(seen) != 1 << B or set(seen.values()) != {1}:
            ok = False
print("  dest over 2^B consecutive members of a class hits each residue mod 2^B once"
      f" (all {len(small)} classes of level <= 8, B = 1, 3, 6): {ok}")
# and the dropping set of the destination: counts over one full period are N(level')
sets_by_level = defaultdict(set)
for r, lev, s in classes:
    if lev <= 8:
        sets_by_level[lev].add(r)
worst = 0
for r, lev, s in small:
    m = r if r >= 2 else r + (1 << lev)
    for lev2, res in sets_by_level.items():
        cnt = sum(1 for t in range(1 << lev2) if drop(m + t * (1 << lev))[2] % (1 << lev2) in res)
        worst = max(worst, abs(cnt - len(res)))
print("  destinations landing in the classes of level j' over 2^j' consecutive members:"
      f" always exactly N(j') (largest deviation {worst})")

x, chain, sets_ = 294583, [294583], []
for _ in range(7):
    k, s, d, _ = drop(x)
    sets_.append(k)
    chain.append(d)
    x = d
print("  chain:", chain, " sets:", sets_)


def order(a: int, mod: int) -> int:
    o, y = 1, a % mod
    while y != 1:
        y, o = y * a % mod, o + 1
    return o


def v2(n: int) -> int:
    return (n & -n).bit_length() - 1


print("  ord(3 mod 2^B):", {B: order(3, 1 << B) for B in (2, 3, 4, 5, 6, 8, 10, 12, 16, 20)})
print("  v2(3^(2^j) - 1), j = 0..6:", [v2(3 ** (2 ** j) - 1) for j in range(7)])
print("  ord(3^s)/ord(3) mod 2^16, s = 1..8:",
      [str(Fraction(order(pow(3, s, 1 << 16), 1 << 16), order(3, 1 << 16))) for s in range(1, 9)])

# --------------------------------------------------------------------------- D
print()
print("=" * 78)
print("D. bit-destruction.md and the cycles pages")
print("=" * 78)
from decimal import Decimal, getcontext  # noqa: E402

getcontext().prec = 80
L23 = Decimal(3).ln() / Decimal(2).ln()
rows = []
for s in range(30):
    v = Decimal(s) * L23
    fl = int(v // 1)
    ce = fl if v == fl else fl + 1
    rows.append((s, f"{float(v):.3f}", f"{float(fl + 1 - v):.3f}", s + fl + 1,
                 f"{float(ce - v):.3f}"))
print("  s, s*log2(3), floor+1-s*log2(3), k, ceil-form:")
for row in rows:
    print("   ", row)
for p, s in ((8, 5), (65, 41), (485, 306), (19, 12), (84, 53)):
    v = Decimal(s) * L23
    print(f"  {p}/{s}: floor(s log2 3)+1 = {int(v // 1) + 1}  beta = {float(int(v // 1) + 1 - v):.5f}")

for E, S in ((1, 1), (2, 1), (3, 2), (8, 5), (19, 12), (65, 41), (84, 53), (485, 306)):
    g = 2 ** E - 3 ** S
    print(f"  E={E} S={S} K={E + S} gap={g if abs(g) < 10 ** 6 else f'{Decimal(g):.2E}'}")


def affine(word):
    a, b = Fraction(1), Fraction(0)
    for bit in word:
        a, b = (3 * a, 3 * b + 1) if bit else (a / 2, b / 2)
    return a, b


words = []
for ones in itertools.combinations(range(13), 5):
    if any((o + 1) % 13 in ones for o in ones):
        continue
    words.append(tuple(1 if i in ones else 0 for i in range(13)))
dist = Counter(int(affine(w)[1] * 256) % 13 for w in words)
print("  circular words:", len(words), " C*256 mod 13:", [dist.get(r, 0) for r in range(13)])
necklaces = {min(w[i:] + w[:i] for i in range(13)) for w in words}
print("  distinct cyclic words:", len(necklaces), " (12/13)^7 =", round((12 / 13) ** 7, 4))
for w in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
    a, b = affine(w)
    print(f"  word {w}: C = {b}, n = C*4/(4-3) = {b * 4}")

coef = [81, 27, 9, 3, 1]


def zero(q):
    return sum(c * 2 ** e for c, e in zip(coef, q)) % 13 == 0


perms = list(itertools.permutations(range(8), 5))
incs = list(itertools.combinations(range(8), 5))
print(f"  gap 13, any order: {sum(map(zero, perms))} of {len(perms)}"
      f" = {sum(map(zero, perms)) / len(perms):.4%}; increasing: {sum(map(zero, incs))} of {len(incs)}")
# the 56 increasing assignments reduce to the 35 with q_0 = 0 (T = 2^q0 * T'), and those
# are the odd starting points of the 7 cyclic words
reduced = {tuple(e - q[0] for e in q) for q in incs}
print("  increasing assignments after dividing out 2^q0:", len(reduced),
      " all with q_0 = 0 and q_4 <= 7:", all(q[0] == 0 and q[-1] <= 7 for q in reduced))

S_, E_ = 7, 11
g = 2 ** E_ - 3 ** S_
hits = []
for rest in itertools.combinations(range(1, E_), S_ - 1):
    q = (0,) + rest
    T = sum(3 ** (S_ - 1 - j) * 2 ** q[j] for j in range(S_))
    if T % g == 0:
        hits.append(T // g)
orb, y = [], -17
while True:
    orb.append(y)
    y = f(y)
    if y == -17:
        break
print(f"  S=7, E=11, gap {g}: increasing assignments with q_0 = 0 giving g | T: {len(hits)} of"
      f" {math.comb(E_ - 1, S_ - 1)}: {sorted(hits)}")
print("  odd members of the cycle of -17:", sorted(v for v in orb if v % 2))

tested, sols = 0, []
for S in range(1, 30):
    for E in range(1, 30 - S + 1):
        g = 2 ** E - 3 ** S
        if not 0 < g < 10000:
            continue
        tested += 1
        for rest in itertools.combinations(range(1, E), S - 1):
            q = (0,) + rest
            T = sum(3 ** (S - 1 - j) * 2 ** q[j] for j in range(S))
            if T % g == 0:
                sols.append((S, E, q, T // g))
print(f"  K <= 30, 0 < gap < 10000: {tested} pairs; solutions:", sols)
print(f"  [{time.time() - T0:.0f}s]")
