"""Audit checks for the 'structure-cycles' section of the site.

Pages: proofs/affine-orbit.md, proofs/bit-destruction.md, proofs/mixing.md,
       cycles/convergent-elimination.md, cycles/divisibility-obstruction.md

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 structure_cycles_audit.py
Read-only: prints numbers, edits nothing.
"""
from __future__ import annotations

import itertools
import math
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from fractions import Fraction

import numpy as np

getcontext().prec = 60
LOG2_3 = Decimal(3).ln() / Decimal(2).ln()


def f(n: int) -> int:
    return 3 * n + 1 if n & 1 else n >> 1


def drop(n: int):
    """(k, s, dest, orbit) for the un-shortcut map; orbit includes n, excludes dest."""
    x, k, s, orb = n, 0, 0, []
    while True:
        orb.append(x)
        if x & 1:
            s += 1
        x = f(x)
        k += 1
        if x < n:
            return k, s, x, orb


print("=" * 78)
print("A. affine-orbit.md")
print("=" * 78)

# A1. table rows and number of residue classes
by_k = defaultdict(set)
s_of_k = defaultdict(set)
for n in range(2, 1 << 16):
    k, s, d, _ = drop(n)
    if k <= 13:
        by_k[k].add(n % (1 << (k - s)))
    s_of_k[k].add(s)
for k in (1, 3, 6, 8, 11, 13):
    s = next(iter(s_of_k[k]))
    print(f"  k={k:2d} s={s} slope={Fraction(3**s, 2**(k-s))} = {3**s/2**(k-s):.4f}  "
          f"classes mod 2^{k-s}: {len(by_k[k])}  {sorted(by_k[k])[:8]}")
print("  dest(5) =", drop(5)[2], " (3*5+1)/4 =", Fraction(3 * 5 + 1, 4))
print("  dest(3) =", drop(3)[2], " (9*3+5)/16 =", Fraction(9 * 3 + 5, 16))
print("  s values seen per k (n < 2^16), any k with two different s?:",
      {k: v for k, v in s_of_k.items() if len(v) > 1})

# A2. k = ceil(s log2 6)?  and at s = 0
for s in range(0, 6):
    c = int((Decimal(s) * (LOG2_3 + 1)).to_integral_value(rounding="ROUND_CEILING"))
    fl = int((Decimal(s) * (LOG2_3 + 1)).to_integral_value(rounding="ROUND_FLOOR")) + 1
    print(f"  s={s}: ceil(s log2 6)={c}  floor(s log2 6)+1={fl}")

# A3. Coefficient stopping time versus stopping time, all 2 <= n < 2^24 (Terras T-steps)
LEVEL = 24
N = 1 << LEVEL
n0 = np.arange(N, dtype=np.int64)
x = n0.copy()
sodd = np.zeros(N, dtype=np.int64)
tau = np.zeros(N, dtype=np.int64)      # coefficient stopping time (0 = not yet)
sigma = np.zeros(N, dtype=np.int64)    # actual stopping time (0 = not yet)
s_at_tau = np.zeros(N, dtype=np.int64)
s_at_sigma = np.zeros(N, dtype=np.int64)
pow3 = np.array([3**i for i in range(40)], dtype=np.int64)
for j in range(1, LEVEL + 1):
    odd = (x & 1).astype(bool)
    x = np.where(odd, (3 * x + 1) >> 1, x >> 1)
    sodd += odd
    below = pow3[sodd] < (1 << j)
    new_tau = (tau == 0) & below
    tau[new_tau] = j
    s_at_tau[new_tau] = sodd[new_tau]
    new_sig = (sigma == 0) & (x < n0)
    sigma[new_sig] = j
    s_at_sigma[new_sig] = sodd[new_sig]
has_tau = tau > 0
mismatch = has_tau & (sigma != tau)
bad = np.nonzero(mismatch)[0]
print(f"  classes of Terras level <= {LEVEL}: residues with tau<= {LEVEL}: {int(has_tau.sum())} of {N}")
print(f"  residues r < 2^{LEVEL} with tau(r) <= {LEVEL} but sigma(r) != tau(r): {bad.tolist()[:20]}")
# number of classes per level, and matching un-shortcut dropping time
cls = Counter()
for lev in range(1, LEVEL + 1):
    m = (tau == lev) & (n0 < (1 << lev))
    cls[lev] = int(m.sum())
print("  class counts N(level):", [cls[l] for l in range(1, LEVEL + 1) if cls[l]])
print("  total classes:", sum(cls.values()))
lev_s = {}
for lev in range(1, LEVEL + 1):
    m = tau == lev
    if m.any():
        ss = set(np.unique(s_at_tau[m]).tolist())
        lev_s[lev] = ss
print("  level -> s (un-shortcut k = level + s):",
      {lev: (sorted(ss), [lev + s for s in sorted(ss)]) for lev, ss in lev_s.items()})

# A4. direct check for 2 <= n <= 10^7: is the pair (k, s) always (floor(s log2 6)+1, s)?
LIM = 10_000_000
n1 = np.arange(LIM + 1, dtype=np.int64)
x = n1.copy()
sodd = np.zeros(LIM + 1, dtype=np.int64)
e = np.zeros(LIM + 1, dtype=np.int64)
done = np.zeros(LIM + 1, dtype=bool)
done[:2] = True
sfin = np.zeros(LIM + 1, dtype=np.int64)
j = 0
while not done.all():
    j += 1
    odd = (x & 1).astype(bool) & ~done
    act = ~done
    x = np.where(act, np.where(odd, (3 * x + 1) >> 1, x >> 1), x)
    sodd += odd
    newly = act & (x < n1)
    e[newly] = j
    sfin[newly] = sodd[newly]
    done |= newly
    if j > 400:
        break
print(f"  n <= 10^7: all dropped: {bool(done.all())}; max Terras stopping time {int(e.max())}"
      f" (un-shortcut {int((e + sfin).max())})")
viol = 0
pairs = set(zip(e[2:].tolist(), sfin[2:].tolist()))
for (ee, ss) in sorted(pairs):
    ok = (3**ss < 2**ee) and (ss == 0 or 2**(ee - 1) < 3**ss)
    if not ok:
        viol += 1
        print("   VIOLATION pair (e, s) =", ee, ss)
print(f"  distinct (level, s) pairs for n <= 10^7: {len(pairs)}; pairs violating "
      f"level = floor(s log2 3)+1: {viol}")
ks = sorted({ee + ss for ee, ss in pairs})
print("  dropping times seen:", ks[:20], "...")

# A5. is the orbit maximum affine on each class? compare argmax index across members
def parity_word_T(r: int, level: int):
    w, xx = [], r
    for _ in range(level):
        w.append(xx & 1)
        xx = (3 * xx + 1) >> 1 if xx & 1 else xx >> 1
    return w

nonaffine_max = []
checked = 0
for lev in range(1, 21):
    rs = np.nonzero((tau == lev) & (n0 < (1 << lev)))[0].tolist()
    for r in rs:
        members = [r + t * (1 << lev) for t in range(0, 4)]
        members = [m for m in members if m >= 2]
        idxs, maxes = [], []
        for m in members:
            k, s, d, orb = drop(m)
            mx = max(orb)
            idxs.append(orb.index(mx))
            maxes.append(mx)
        checked += 1
        # affine on the class <=> equal second differences for consecutive members
        diffs = {maxes[i + 1] - maxes[i] for i in range(len(maxes) - 1)}
        if len(set(idxs)) > 1 or len(diffs) > 1:
            nonaffine_max.append((lev, r, members, idxs, maxes))
print(f"  orbit-max affinity: classes checked (level<=20): {checked}; "
      f"classes where argmax index differs among first members: {len(nonaffine_max)}")
for row in nonaffine_max[:12]:
    print("   ", row)

print()
print("=" * 78)
print("B. bit-destruction.md")
print("=" * 78)
print("   s   s*log2(3)   beta=1-frac   ceil-s*log   k=s+floor+1")
for s in range(0, 30):
    v = Decimal(s) * LOG2_3
    fl = int(v.to_integral_value(rounding="ROUND_FLOOR"))
    ce = int(v.to_integral_value(rounding="ROUND_CEILING"))
    beta = 1 - (v - fl)
    print(f"  {s:2d}  {float(v):9.3f}   {float(beta):.3f}        {float(ce - v):.3f}      {s + fl + 1}")
for p, s in ((8, 5), (65, 41), (485, 306), (19, 12), (84, 53)):
    v = Decimal(s) * LOG2_3
    fl = int(v.to_integral_value(rounding="ROUND_FLOOR"))
    print(f"  p/s={p}/{s}={p/s:.5f}  log2 3={float(LOG2_3):.5f}  above={Decimal(p)/Decimal(s) > LOG2_3}"
          f"  beta({s})={float(1 - (v - fl)):.5f}")

print()
print("=" * 78)
print("C. mixing.md")
print("=" * 78)


def order(a: int, m: int) -> int:
    o, y = 1, a % m
    while y != 1:
        y = y * a % m
        o += 1
    return o


for B in (2, 3, 4, 5, 6, 8, 10, 12, 16, 20):
    o = order(3, 1 << B)
    print(f"  B={B:2d} 2^B={1 << B:8d} ord={o:7d} ratio={Fraction(o, 1 << B)}")


def v2(n: int) -> int:
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


print("  v2(3^(2^j)-1) for j=0..6:", [v2(3 ** (2 ** j) - 1) for j in range(7)], " (page formula j+2)")
for s in range(1, 9):
    B = 16
    print(f"  s={s} v2(s)={v2(s)}  ord(3^s)/ord(3) mod 2^{B} = {Fraction(order(pow(3, s, 1 << B), 1 << B), order(3, 1 << B))}")

# entropies


def entropy(counter):
    tot = sum(counter.values())
    return -sum(c / tot * math.log2(c / tot) for c in counter.values() if c)


def mi_report(label, ns):
    joint, cur, nxt = Counter(), Counter(), Counter()
    allsets = Counter()
    for n in ns:
        k, s, d, _ = drop(n)
        allsets[k] += 1
        if d < 2:
            continue
        k2 = drop(d)[0]
        joint[(k, k2)] += 1
        cur[k] += 1
        nxt[k2] += 1
    H_all = entropy(allsets)
    H_cur, H_nxt, H_joint = entropy(cur), entropy(nxt), entropy(joint)
    I = H_cur + H_nxt - H_joint
    tot = sum(joint.values())
    # total variation between joint and product of marginals
    tv = 0.5 * sum(abs(joint.get((a, b), 0) / tot - cur[a] / tot * nxt[b] / tot)
                   for a in cur for b in nxt)
    # largest TV between a conditional row and the marginal, weighted mean of row TVs
    row_tv = {}
    for a in cur:
        row_tv[a] = 0.5 * sum(abs(joint.get((a, b), 0) / cur[a] - nxt[b] / tot) for b in nxt)
    wmean = sum(cur[a] / tot * row_tv[a] for a in cur)
    cells = len(cur) * len(nxt)
    bias = (len(cur) - 1) * (len(nxt) - 1) / (2 * tot * math.log(2))
    print(f"  [{label}] pairs={tot}  H(Set of n)={H_all:.3f}  H(cur)={H_cur:.3f}  H(next)={H_nxt:.3f}  "
          f"H(next|cur)={H_joint - H_cur:.3f}  I={I:.4f} bits  I/H(next)={I / H_nxt:.2%}  "
          f"TV(joint,product)={tv:.4f}  mean row TV={wmean:.4f}  cells={cells}  "
          f"plug-in bias approx={bias:.4f}")


mi_report("all 2<=n<50000", range(2, 50000))
mi_report("odd 3<=n<50000", range(3, 50000, 2))
mi_report("all 2<=n<500000", range(2, 500000))
mi_report("odd 3<=n<500000", range(3, 500000, 2))

# the 294583 chain
x = 294583
chain = [x]
ksets = []
for _ in range(7):
    k, s, d, _ = drop(x)
    ksets.append(k)
    chain.append(d)
    x = d
print("  chain:", chain)
print("  dropping sets along it:", ksets)

print()
print("=" * 78)
print("D. cycles pages")
print("=" * 78)
for E, S in ((1, 1), (2, 1), (3, 2), (8, 5), (19, 12), (65, 41), (84, 53), (485, 306)):
    g = 2**E - 3**S
    rel = "above" if Decimal(E) / Decimal(S) > LOG2_3 else "below"
    gs = str(g) if abs(g) < 10**7 else f"{Decimal(g):.3E}"
    print(f"  E={E:3d} S={S:3d} K={E + S:3d} E/S={E / S:.5f} {rel}  gap={gs}")

# D1. 91 circular words, C*256 mod 13
words = []
for ones in itertools.combinations(range(13), 5):
    w = [0] * 13
    for i in ones:
        w[i] = 1
    if any(w[i] and w[(i + 1) % 13] for i in range(13)):
        continue
    words.append(tuple(w))
print("  circular words (length 13, five 1s, no two adjacent):", len(words))
dist = Counter()
for w in words:
    a, b = Fraction(1), Fraction(0)
    for bit in w:
        if bit:
            a, b = 3 * a, 3 * b + 1
        else:
            a, b = a / 2, b / 2
    assert a == Fraction(243, 256)
    val = b * 256
    assert val.denominator == 1
    dist[int(val) % 13] += 1
print("  distribution of C*256 mod 13:", [(r, dist.get(r, 0)) for r in range(13)])
page = {0: 0, 1: 7, 2: 6, 3: 9, 4: 7, 5: 6, 6: 10, 7: 7, 8: 6, 9: 10, 10: 6, 11: 8, 12: 9}
print("  matches the page table:", all(dist.get(r, 0) == page[r] for r in range(13)))
# necklaces
seen, neck = set(), 0
for w in words:
    if w in seen:
        continue
    neck += 1
    for r in range(13):
        seen.add(w[r:] + w[:r])
print("  distinct cyclic words (necklaces):", neck, " chance of no zero at 1/13 each:",
      round((12 / 13) ** neck, 3))

# D2. trivial cycle words
for w in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
    a, b = Fraction(1), Fraction(0)
    for bit in w:
        if bit:
            a, b = 3 * a, 3 * b + 1
        else:
            a, b = a / 2, b / 2
    n = b * 4 / (4 - 3)
    print(f"  word {w}: slope={a} C={b}  n = C*4/(4-3) = {n}")

# D3. orderings for gap 13
coeffs = [81, 27, 9, 3, 1]
def frac_zero(assignments):
    tot = z = 0
    for q in assignments:
        tot += 1
        if sum(c * 2**qq for c, qq in zip(coeffs, q)) % 13 == 0:
            z += 1
    return z, tot
z, tot = frac_zero(itertools.permutations(range(8), 5))
print(f"  any order, exponents from 0..7: zero {z}/{tot} = {z / tot:.4%}  (1/13 = {1 / 13:.4%})")
z, tot = frac_zero(q for q in itertools.permutations(range(8), 5) if min(q) == 0)
print(f"  any order, exponents from 0..7 with min 0: zero {z}/{tot} = {z / tot:.4%}")
z, tot = frac_zero(q for q in itertools.permutations(range(8), 5) if q[0] == 0)
print(f"  any order, q_0 = 0: zero {z}/{tot} = {z / tot:.4%}")
z, tot = frac_zero(itertools.combinations(range(8), 5))
print(f"  increasing, exponents from 0..7: zero {z}/{tot}")
z, tot = frac_zero(q for q in itertools.combinations(range(8), 5) if q[0] == 0)
print(f"  increasing with q_0 = 0: zero {z}/{tot}")

# D4. exhaustive check K <= 30, 0 < g < 10000
pairs_tested, hits = [], []
for S in range(1, 30):
    for E in range(S, 30 - S + 1):
        g = 2**E - 3**S
        if not (0 < g < 10000):
            continue
        pairs_tested.append((S, E, g))
        if S == 1:
            combos = [()]
        else:
            combos = itertools.combinations(range(1, E), S - 1)
        for rest in combos:
            q = (0,) + tuple(rest)
            T = sum(3 ** (S - 1 - j) * 2 ** q[j] for j in range(S))
            if T % g == 0:
                hits.append((S, E, g, q, T // g))
print("  (S,E,g) pairs tested:", len(pairs_tested))
print("   ", pairs_tested)
print("  solutions g | T:", hits)
print("  K values of the pairs with 3 | K:", sorted({S + E for S, E, _ in pairs_tested if (S + E) % 3 == 0}))
