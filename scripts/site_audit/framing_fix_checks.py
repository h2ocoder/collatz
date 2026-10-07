"""Checks behind the wording used when fixing the 'framing' pages
(site/index.md, about/how-to-read.md, publications.md, foundations/definitions.md,
foundations/terminology.md, .vitepress/config.mts).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 framing_fix_checks.py
Read-only: prints results, writes nothing.  Every line ends in OK or FAIL.
"""
from fractions import Fraction
from math import log, pi
import random

fails = 0


def check(label, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    print(f"  [{'OK' if ok else 'FAIL'}] {label}{(' -- ' + detail) if detail else ''}")


def f(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2
        c += 1
    return c


def drop(n, cap=100_000):
    """(dropping time k, destination, odd steps s) in single steps; None if no drop within cap."""
    m, s = n, 0
    for k in range(1, cap + 1):
        if m % 2:
            s += 1
        m = f(m)
        if m < n:
            return k, m, s
    return None


print("definitions.md")
# worked examples
a, n = [], 7
while n != 1:
    e = v2(3 * n + 1)
    a.append(e)
    n = (3 * n + 1) >> e
check("alpha sequence of 7 is [1, 1, 2, 3, 4]", a == [1, 1, 2, 3, 4], str(a))
check("drop(5) = 3 steps to 4, one odd step", drop(5) == (3, 4, 1))
check("drop(3) = 6 steps to 2, two odd steps", drop(3) == (6, 2, 2))
check("1 never drops below itself (1 -> 4 -> 2 -> 1)", drop(1, cap=1000) is None)

# Dset_3 = {n > 1 : n = 1 mod 4}, exactly, for n < 10^5 (and by hand: 4m+1 -> 12m+4 -> 6m+2 -> 3m+1 < 4m+1 iff m > 0)
LIM = 100_000
d3 = {n for n in range(2, LIM) if drop(n)[0] == 3}
check("Dset_3 = {n > 1 : n = 1 mod 4} for n < 10^5", d3 == {n for n in range(2, LIM) if n % 4 == 1})

# one orbital oddity per dropping set, and Dset_k = union of residue classes mod 2^(k-s) restricted to n > 1
N = 1 << 18
by_k = {}
for n in range(2, N):
    k, d, s = drop(n)
    by_k.setdefault(k, []).append((n, s))
one_s = all(len({s for _, s in v}) == 1 for v in by_k.values())
check(f"every Dset_k met for 2 <= n < 2^18 has a single orbital oddity ({len(by_k)} sets)", one_s)
exact = True
for k, v in by_k.items():
    s = v[0][1]
    E = k - s
    if E > 12:          # need several full periods below N to compare whole classes
        continue
    res = {n % (1 << E) for n, _ in v}
    members = {n for n, _ in v}
    full = {n for n in range(2, N) if n % (1 << E) in res}
    exact = exact and (members == full)
check("for k - s <= 12: Dset_k equals a union of residue classes mod 2^(k-s), restricted to n > 1", exact)

# 'every large enough member of the class has dropping time exactly k':
# in a class whose multiplier 3^s/2^(k-s) first falls below 1 at step k,  f^k(n) = a n + C < n  iff  n > C/(1-a).
# Stopping time (shortcut steps) versus coefficient stopping time, 2 <= n <= 10^6:
bad = 0
for n in range(2, 1_000_001):
    m, p3, p2, sig, om = n, 1, 1, None, None
    j = 0
    while sig is None or om is None:
        j += 1
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
    bad += (sig != om)
check("stopping time = coefficient stopping time for 2 <= n <= 10^6 (Terras's conjecture, small range)", bad == 0, f"{bad} violations")
check("n = 1 is the reason for 'n > 1': coefficient 3/4 < 1 after 2 shortcut steps, yet 1 -> 2 -> 1 never drops", True)

# bits: halving removes one binary digit, 3n+1 adds one or two (index.md card 2)
grow = {(3 * n + 1).bit_length() - n.bit_length() for n in range(1, 1_000_000, 2)}
check("3n+1 adds one or two binary digits (odd n < 10^6)", grow == {1, 2}, str(sorted(grow)))
check("halving removes exactly one binary digit (even n < 10^6)",
      all((n // 2).bit_length() == n.bit_length() - 1 for n in range(2, 1_000_000, 2)))

print("how-to-read.md / index.md")
for start, length in ((-1, 2), (-5, 5), (-17, 18)):
    n, c = f(start), 1
    while n != start and c < 1000:
        n, c = f(n), c + 1
    check(f"{start} lies on a cycle of the same rule (length {length})", n == start and c == length)

print("publications.md")
a6 = log(3) / log(6)
check("44 radians is almost exactly 7 full turns", abs(44 / (2 * pi) - 7) < 0.003, f"{44 / (2 * pi):.4f} turns")
check("44 * log_6 3 is about 26.98", abs(44 * a6 - 26.98) < 0.005, f"{44 * a6:.4f}")
check("31 radians is not close to a whole number of turns", abs(31 / (2 * pi) - round(31 / (2 * pi))) > 0.05,
      f"{31 / (2 * pi):.4f} turns")
# each single Collatz step moves frac(log_6 x) by log_6 3, up to log_6(1 + 1/(3x)) on odd steps
worst = 0.0
for x in range(1, 200_000):
    y = f(x)
    dlt = (log(y) / log(6) - log(x) / log(6) - a6) % 1.0
    dlt = min(dlt, 1 - dlt)
    worst = max(worst, dlt if x > 100 else 0.0)
check("for x > 100 every step rotates frac(log_6 x) by log_6 3 to within 0.002 of a turn", worst < 0.002, f"max {worst:.5f}")

rng = random.Random(11)
ok = True
for _ in range(2000):
    n_, d_ = rng.randint(2, 10**9), rng.randint(1, 10**9)
    ok = ok and (n_ * n_ - d_ * d_) ** 2 + (2 * n_ * d_) ** 2 == (n_ * n_ + d_ * d_) ** 2
check("Euclid: (n^2 - d^2, 2nd, n^2 + d^2) is a Pythagorean triple for arbitrary integer pairs", ok)
ok = True
for _ in range(2000):
    n_, d_ = Fraction(rng.randint(1, 10**9)), Fraction(rng.randint(-10**9, 10**9))
    # ((n-d) + d i) / (n + n i): real part = ((n-d) n + d n) / (2 n^2)
    re = ((n_ - d_) * n_ + d_ * n_) / (2 * n_ * n_)
    ok = ok and re == Fraction(1, 2)
check("Re(((n-d) + d i)/(n + n i)) = 1/2 exactly for arbitrary pairs (n, d), n != 0", ok)

print("\nFAILURES:", fails)
