"""Checks behind the 'framing' audit (site/index.md, about/how-to-read.md, publications.md,
foundations/definitions.md, foundations/terminology.md, .vitepress/config.mts).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 framing_checks.py
Read-only: prints results, writes nothing.
"""
from fractions import Fraction
from math import log, pi, floor, ceil
import random


def f(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def section(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


# ---------------------------------------------------------------------------
section("1. how-to-read: the -1 test.  Cycles of 3n+1 on negative integers")
for start in (-1, -5, -17):
    n, orb = start, [start]
    while True:
        n = f(n)
        if n == start:
            break
        orb.append(n)
    print(f"  {start}: cycle of length {len(orb)}: {orb}")

# ---------------------------------------------------------------------------
section("2. definitions.md worked examples")


def orbit(n):
    o = [n]
    while n != 1:
        n = f(n)
        o.append(n)
    return o


def drop(n):
    """(dropping time k, destination, dropping orbit, odd count s)"""
    m, k, orb = n, 0, []
    while True:
        orb.append(m)
        m = f(m)
        k += 1
        if m < n:
            return k, m, orb, sum(1 for x in orb if x % 2)


def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2
        c += 1
    return c


def alpha_seq(n):
    out = []
    while n != 1:
        a = v2(3 * n + 1)
        out.append(a)
        n = (3 * n + 1) >> a
    return out


print("  orbit(6)        =", orbit(6))
print("  drop(5)         =", drop(5))
print("  drop(3)         =", drop(3))
print("  alpha_seq(3)    =", alpha_seq(3), " (page: [1, 4])")
print("  alpha_seq(7)    =", alpha_seq(7), " (page: [1, 1, 1, 3, 4])")
print("  orbit(7)        =", orbit(7))
print("  halvings in orbit(7) =", sum(1 for x in orbit(7)[:-1] if x % 2 == 0),
      "; sum of page's list =", sum([1, 1, 1, 3, 4]), "; sum of correct list =", sum(alpha_seq(7)))
print("  v2(3*17+1) =", v2(52), "(17 is the third odd value in the orbit of 7)")

# ---------------------------------------------------------------------------
section("3. definitions.md: 'Each dropping set is a union of arithmetic progressions (a fact...)'")
print("  Terras: sigma(n) = stopping time (shortcut map T), omega(n) = coefficient stopping time")
print("  = first j with 3^(odd steps) < 2^j.  'Dset_k is exactly a union of residue classes'")
print("  holds iff sigma(n) = omega(n) for all n >= 2 (Coefficient Stopping Time conjecture).")


def sigma_omega(n, cap=10_000):
    """Return (sigma, omega) for the shortcut map; None if not reached within cap."""
    m, s, sig, om = n, 0, None, None
    p3, p2 = 1, 1
    for j in range(1, cap + 1):
        if m % 2:
            m = (3 * m + 1) // 2
            p3 *= 3
        else:
            m //= 2
        p2 *= 2
        if om is None and p3 < p2:
            om = j
        if sig is None and m < n:
            sig = j
        if sig is not None and om is not None:
            break
    return sig, om


print("  n = 1: (sigma, omega) =", sigma_omega(1, cap=50),
      " -> 1 lies in the class 1 mod 4 (omega = 2) but never drops: the reason for 'n > 1'")
N = 2_000_000
bad = []
for n in range(2, N + 1):
    sg, om = sigma_omega(n)
    if sg != om:
        bad.append((n, sg, om))
print(f"  2 <= n <= {N}: violations of sigma = omega: {len(bad)} {bad[:5]}")

# same thing in the page's own terms: Dset_k (un-shortcut steps) versus residue classes
LIM = 1 << 16
by_k = {}
for n in range(2, 4 * LIM):
    k, d, orb, s = drop(n)
    by_k.setdefault(k, []).append((n, s))
print("  Dset_k for 2 <= n < 2^18, k <= 16:  E = k - s, residues mod 2^E, exact union of classes?")
for k in sorted(by_k):
    if k > 16:
        break
    ss = {s for _, s in by_k[k]}
    s = next(iter(ss))
    E = k - s
    res = sorted({n % (1 << E) for n, _ in by_k[k]})
    members = {n for n, _ in by_k[k]}
    full = {n for n in range(2, 4 * LIM) if n % (1 << E) in set(res)}
    print(f"    k={k:2d}  oddities={sorted(ss)}  E={E:2d}  #classes={len(res):3d}  "
          f"Dset_k == union of those classes (n>1): {members == full}")
print("  counts of classes above are A100982 with the class 'even' in front: 1,1,2,3,7,12")

# How far does a finite check of sigma = omega reach?  A violator with s odd steps before its
# coefficient stopping time E = ceil(s log2 3) has all earlier iterates >= n, so
#   1 <= T^E(n)/n <= (3^s/2^E) (1 + 1/(3n))^s   =>   n <= s / (3 ln2 * beta(s)),
# beta(s) = E - s log2 3.  So "no violation for 2 <= n <= X" proves "class = dropping set" for
# every s with s / (3 ln2 beta(s)) < X.
from decimal import Decimal, getcontext
getcontext().prec = 60
L2_3 = Decimal(3).ln() / Decimal(2).ln()
LN2 = Decimal(2).ln()


def reach(X, smax=200_000):
    for s in range(1, smax + 1):
        x = s * L2_3
        beta = (x.to_integral_value(rounding="ROUND_CEILING")) - x
        if Decimal(s) / (3 * LN2 * beta) >= X:
            return s - 1
    return smax


for X, src in ((N, "this script"), (10**7, "site_audit/explore_check_sturmian (F)"),
               (Decimal("2.8e19"), "Rozier-Terracol 2026, Cor. 5.4")):
    S = reach(Decimal(X))
    E = int((S * L2_3).to_integral_value(rounding="ROUND_CEILING"))
    more = " (at least; search capped)" if S == 200_000 else ""
    print(f"  checked n <= {X} [{src}]: exact for every s <= {S}, i.e. Dset_k for k <= {S + E}{more}")
print("  Any nontrivial positive cycle would be a violator (its least element has omega finite,")
print("  sigma infinite), as n = 1 is: 'class = dropping set for every k' implies no nontrivial")
print("  cycle, so it cannot be 'a fact that follows from the affine orbit structure'.")
print("  Lagarias 1985 sec. 2: Coefficient Stopping Time Conjecture (Terras), open.")

# ---------------------------------------------------------------------------
section("4. publications.md: 27/44 and log_6 3")
a = log(3) / log(6)
print(f"  log_6 3 = {a:.9f}")
x, cf = Fraction(a).limit_denominator(10**12), []
y = x
for _ in range(12):
    q = y.numerator // y.denominator
    cf.append(q)
    y = y - q
    if y == 0:
        break
    y = 1 / y
print("  continued fraction:", cf)
h0, h1, k0, k1 = 1, cf[0], 0, 1
convs = [(h1, k1)]
for q in cf[1:]:
    h0, h1 = h1, q * h1 + h0
    k0, k1 = k1, q * k1 + k0
    convs.append((h1, k1))
print("  convergents:", convs[:10])
print("  27/44 is a convergent:", (27, 44) in convs, "; mediant of 8/13 and 19/31:", (8 + 19, 13 + 31))
for q in (13, 31, 44, 75, 106, 137):
    e = q * a - round(q * a)
    print(f"    q={q:4d}: q*log_6(3) = {q * a:9.4f}   miss = {e:+.4f} turns")

section("5. publications.md: where the 44 spokes of the Medium article's polar plots come from")
print("  The article plots theta = step index (matplotlib polar => radians), r = P(value, 6).")
for q in (13, 22, 31, 44, 75, 88, 106, 137, 355, 710):
    r = q % (2 * pi)
    r = r if r < pi else r - 2 * pi
    print(f"    {q:4d} rad = {q / (2 * pi):8.4f} turns   angular miss = {r:+.4f} rad = {r * 180 / pi:+7.2f} deg")
print("  -> 44 rad = 7.0028 turns (22/7 ~ pi). Points 44 steps apart share an angle whatever is plotted;")
print("     points 31 steps apart are 24 degrees apart.")


def P(xv, b=6):
    k = 0
    while b ** (k + 1) <= xv:
        k += 1
    return (xv - b ** k) / (b ** (k + 1) - b ** k)


def mean_dist(vals, lag, ang_per_step):
    """mean Euclidean distance between plotted points lag steps apart (r in [0,1))."""
    import cmath
    pts = [v * cmath.exp(1j * ang_per_step * i) for i, v in enumerate(vals)]
    d = [abs(pts[i + lag] - pts[i]) for i in range(len(pts) - lag)]
    return sum(d) / len(d)


for seed in (27, 670617279):
    orb = orbit(seed)
    rs = [P(v) for v in orb]
    print(f"  seed {seed}: {len(orb) - 1} steps")
    rnd = rs[:]
    random.Random(1).shuffle(rnd)
    for lag in (13, 31, 44, 75):
        print(f"    lag {lag:3d}: mean distance, theta=index rad: orbit {mean_dist(rs, lag, 1.0):.3f}"
              f" | radii shuffled {mean_dist(rnd, lag, 1.0):.3f}"
              f" || mean |r_i+lag - r_i| alone: {sum(abs(rs[i + lag] - rs[i]) for i in range(len(rs) - lag)) / (len(rs) - lag):.3f}")
print("  Reading: with theta = index in radians only lag 44 brings points back to the same angle;")
print("  the radius also nearly returns at lag 44 (27/44) and, better, at lag 31 (19/31), but lag 31")
print("  is invisible in that plot because 31 rad is not a whole number of turns.")

# ---------------------------------------------------------------------------
section("6. index.md card 3: 'a loop would need 2^E to sit absurdly close to 3^S'")
print("  cycle: prod over odd elements (3 + 1/n_i) = 2^E  =>  0 < E ln2 - S ln3 < S/(3 n_min).")
print("  With n_min > 2^68 (verified range):  2^E/3^S - 1 < S / (3 * 2^68) = S * %.3e" % (1 / (3 * 2 ** 68)))

section("7. definitions.md: Dset_1, Dset_3, Dset_6 as stated")
print("  Dset_1 (n < 40):", [n for n, _ in by_k[1] if n < 40][:10])
print("  Dset_3 (n < 40):", [n for n, _ in by_k[3] if n < 40], " = 1 mod 4 with n > 1 (1 itself never drops)")
print("  Dset_6 (n < 80):", [n for n, _ in by_k[6] if n < 80])

# ---------------------------------------------------------------------------
section("8. publications.md: what the two 'connections' of Paper 1 are")
print("  Orbital triple (collatz/geometry.py): (n^2 - d^2, 2nd, n^2 + d^2) = Euclid's formula on (n, d).")
rng = random.Random(7)
ok = all((m * m - d * d) ** 2 + (2 * m * d) ** 2 == (m * m + d * d) ** 2
         for m, d in ((rng.randint(2, 10**6), rng.randint(1, 10**6)) for _ in range(1000)))
print("  identity holds for 1000 random integer pairs with no relation to Collatz:", ok)
print("  'Riemann' link (paper sec. 5.2): z = n + n i, z' = (n - d) + d i, z0 = z'/z, 'Re z0 = 1/2'.")
vals = [(complex(n - d, d) / complex(n, n)).real for n, d in ((rng.uniform(1, 1e6), rng.uniform(-1e6, 1e6)) for _ in range(1000))]
print("  Re(z'/z) over 1000 random real pairs (n, d): min %.12f max %.12f" % (min(vals), max(vals)))
print("  -> ((n-d) + d i)/(n(1+i)) = 1/2 + i(2d-n)/(2n) identically: true for any two numbers.")
