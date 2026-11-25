"""Where 9/4 comes from in the matrix-multiplication exponent papers, and where
the same number lives in Collatz (SCRUM-82).

Note:  docs/Explorations/Matrix Multiplication Exponent.md
Run:   python -X utf8 scripts/matmul_exponent/nine_fourths.py provenance|collatz|null|all
Logs:  provenance.log, collatz.log, null.log in this folder.

Sources (github.com/openai/math, commit 92b516ef8e2a):
  [LB]   The matrix multiplication exponent is nine fourths (24 Nov 2026)
  [UB]   An Upper Bound of 9/4 for the Matrix Multiplication Exponent (2 Oct 2026)
  [Lean] lean/ComparatorChallenges/MatrixExponent.lean, lean/docs/107.md

Everything here is exact (Fraction) unless a function says "numeric".
"""

import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from collatz.core import collatz_step  # noqa: E402


# --------------------------------------------------------------------------
# A. The tripod: [LB] Section "A lower bound from the price of a shared label"
# --------------------------------------------------------------------------
#
# Three tips sit on a tripod at arm lengths (a_A, a_B, a_C); two tips are at
# distance (sum of their arms). A = first input, B = second input, C = output.
# For the product of an n^x by n^y matrix with an n^y by n^z matrix, index i
# (size n^x) is shared by A and C, j (n^y) by A and B, k (n^z) by B and C.


def tripod_rate(arms):
    """D_*(a) = a1 + a2 + a3 - (1/a1 + 1/a2 + 1/a3)^(-1), [LB] Prop. "Tripod principle".

    The reciprocal term is zero when any arm is zero.
    """
    a = [Fr(v) for v in arms]
    if len(a) != 3 or any(v < 0 for v in a):
        raise ValueError("three non-negative arm lengths expected")
    total = sum(a)
    if any(v == 0 for v in a):
        return total
    return total - 1 / sum(1 / v for v in a)


def pair_sums(weights):
    """(x, y, z) -> (x + y, y + z, z + x): the log-sizes of the matrices at A, B, C."""
    x, y, z = (Fr(v) for v in weights)
    return (x + y, y + z, z + x)


def wire_price(weights, arms):
    """Total wire price divided by log n: x*d(A,C) + y*d(A,B) + z*d(B,C)."""
    return sum(w * Fr(a) for w, a in zip(pair_sums(weights), arms))


def tripod_bound(weights, arms):
    """wire_price / D_*: the exponent compared with log_n(rank) in the three-wire argument."""
    return wire_price(weights, arms) / tripod_rate(arms)


def rectangular_exponent(a, b, c):
    """The closed form in [Lean] `rectangular_exponent`, transcribed.

    Sort the non-negative parts as x >= y >= z; the value is
    x + y + max((x + y) z - x y, 0)^2 / (4 x y z), and x + y on coordinate planes.
    """
    big_a, big_b, big_c = (max(Fr(v), Fr(0)) for v in (a, b, c))
    x = max(big_a, big_b, big_c)
    z = min(big_a, big_b, big_c)
    y = big_a + big_b + big_c - x - z
    if x * y * z == 0:
        return x + y
    return x + y + max((x + y) * z - x * y, Fr(0)) ** 2 / (4 * x * y * z)


def paper_rectangular_lower_bound(x, y, z):
    """[LB] Cor. "rectangular", as an exponent: max of the pair sums and (3/4)(x + y + z)."""
    x, y, z = (Fr(v) for v in (x, y, z))
    return max(max(pair_sums((x, y, z))), Fr(3, 4) * (x + y + z))


def in_triangle_regime(x, y, z):
    """True when the correction term is positive: 1/z < 1/x + 1/y for the smallest weight z."""
    x, y, z = sorted((Fr(v) for v in (x, y, z)), reverse=True)
    return z > 0 and (x + y) * z > x * y


def rectangular_exponent_symmetric(x, y, z):
    """The same value written symmetrically (this repo's algebra, checked in the tests):

    (xy + yz + zx)^2 / (4 xyz) in the triangle regime, the largest pair sum otherwise.
    Negative weights are clamped to zero, as in the Lean statement.
    """
    x, y, z = sorted((max(Fr(v), Fr(0)) for v in (x, y, z)), reverse=True)
    if not in_triangle_regime(x, y, z):
        return x + y
    return (x * y + y * z + z * x) ** 2 / (4 * x * y * z)


def optimal_arms(weights):
    """Arms at which tripod_bound equals the closed form.

    Triangle regime: the arm of a tip is 1 / (e2 - 2 * product of that tip's two
    weights), with e2 = xy + yz + zx. Otherwise all the length goes to the tip
    with the largest pair sum (the flat case).
    """
    x, y, z = (Fr(v) for v in weights)
    if in_triangle_regime(x, y, z):
        e2 = x * y + y * z + z * x
        return (1 / (e2 - 2 * x * y), 1 / (e2 - 2 * y * z), 1 / (e2 - 2 * z * x))
    sums = pair_sums(weights)
    top = sums.index(max(sums))
    return tuple(Fr(1) if i == top else Fr(0) for i in range(3))


def sqrt_equation_defect(weights, lam):
    """sum_i sqrt(lam - w_i) - sqrt(lam) (numeric), w = pair sums.

    The supremum of tripod_bound is the least lam >= max(w) at which this is >= 0.
    """
    lam = float(lam)
    return sum(math.sqrt(max(lam - float(w), 0.0)) for w in pair_sums(weights)) - math.sqrt(lam)


def _bound_float(sums, arms):
    total = arms[0] + arms[1] + arms[2]
    if min(arms) <= 0.0:
        rate = total
    else:
        rate = total - 1.0 / (1.0 / arms[0] + 1.0 / arms[1] + 1.0 / arms[2])
    return (sums[0] * arms[0] + sums[1] * arms[1] + sums[2] * arms[2]) / rate


def _ternary_max(f, lo, hi, iters):
    """Maximise a quasi-concave f on [lo, hi] by ternary search (numeric). Returns (value, x)."""
    for _ in range(iters):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if f(m1)[0] < f(m2)[0]:
            lo = m1
        else:
            hi = m2
    x = (lo + hi) / 2
    return f(x)[0], x


def tripod_sup_numeric(weights, iters=60):
    """Brute-force maximum of tripod_bound over the simplex a_A + a_B + a_C = 1 (numeric).

    Independent of the closed form. The ratio is quasi-concave on the simplex
    (the price is linear and D_* is convex), so a nested ternary search finds
    the global maximum: outer over a_A, inner over a_B. Returns (value, arms).
    """
    sums = tuple(float(w) for w in pair_sums(weights))

    def inner(a0):
        def f(a1):
            return (_bound_float(sums, (a0, a1, max(1.0 - a0 - a1, 0.0))), a1)
        return _ternary_max(f, 0.0, 1.0 - a0, iters)

    value, a0 = _ternary_max(inner, 0.0, 1.0, iters)
    a1 = inner(a0)[1]
    return value, (a0, a1, max(1.0 - a0 - a1, 0.0))


# --------------------------------------------------------------------------
# B. The growth lemma: [UB] Lemma "Diagonal growth"
# --------------------------------------------------------------------------
#
# [UB] has P(a, 3h + a - 1) >= 3 P(a, h). At h = a that is two extra copies of
# P(a, a) for 3a - 1 extra length. The general recursion below takes "m extra
# copies for n*a - 1 extra length"; the paper is (m, n) = (2, 3). The family is
# only a sensitivity check of the lemma's arithmetic, not a claim about tensors.


def growth_ratio(a, m=2, n=3):
    """H_a / H_(a-1) for the extremal solution: (n a - n - 1 + m) / (n a - 1 - m)."""
    return Fr(n * a - n - 1 + m, n * a - 1 - m)


def growth_h(a, m=2, n=3):
    """H_a with H_1 = 1. For (2, 3) this is prod_{j < a} (1 + 1/(3j)), [UB] eq. (normalized-growth)."""
    value = Fr(1)
    for k in range(2, a + 1):
        value *= growth_ratio(k, m, n)
    return value


def growth_d(a, m=2, n=3):
    """D_a = (n a - 1) H_a / m, the lemma's lower bound for P(a, a). For (2, 3): (3a - 1) H_a / 2."""
    return Fr(n * a - 1, m) * growth_h(a, m, n)


def growth_exponent_numeric(m=2, n=3, a=20000):
    """log2(D_2a / D_a) (numeric): tends to 2m/n, which is 4/3 for the paper."""
    log_h = 0.0
    log_d = {}
    for k in range(2, 2 * a + 1):
        log_h += math.log((n * k - n - 1 + m) / (n * k - 1 - m))
        if k in (a, 2 * a):
            log_d[k] = math.log((n * k - 1) / m) + log_h
    return (log_d[2 * a] - log_d[a]) / math.log(2)


def omega_from_growth(m=2, n=3, legs=3):
    """a^(2m/n) <= P(a, a) <= (2a - 1)^(1/t) forces t <= n/(2m); a character has value n^(legs*t)."""
    return legs * Fr(n, 2 * m)


# --------------------------------------------------------------------------
# C. The Collatz side
# --------------------------------------------------------------------------


def terras(n, a=3, c=1):
    """One step of the shortcut map for ax + c: (a n + c)/2 if n is odd, n/2 otherwise."""
    return (a * n + c) // 2 if n % 2 else n // 2


def two_step_branches(a=3, c=1):
    """{r: (slope, offset)} with T(T(n)) = slope*n + offset for n = r (mod 4); a and c odd."""
    if a % 2 == 0 or c % 2 == 0:
        raise ValueError("a and c must be odd")
    branches = {}
    for r in range(4):
        n1, n2 = r + 4, r + 8
        y1, y2 = terras(terras(n1, a, c), a, c), terras(terras(n2, a, c), a, c)
        slope = Fr(y2 - y1, n2 - n1)
        branches[r] = (slope, y1 - slope * n1)
    return branches


def two_step_slopes(a=3, c=1):
    """{slope: density} over the four residue classes mod 4."""
    weights = {}
    for slope, _ in two_step_branches(a, c).values():
        weights[slope] = weights.get(slope, Fr(0)) + Fr(1, 4)
    return dict(sorted(weights.items()))


def four_collatz_steps(n):
    """Four steps of the unshortened map from collatz.core (two odd steps when n = 3 mod 4)."""
    for _ in range(4):
        n = collatz_step(n)
    return n


def cycles(a=3, c=1, limit=1000, max_steps=10000):
    """Cycles of the shortcut map reached from 1..limit, as sorted tuples, sorted by least element."""
    found = set()
    for start in range(1, limit + 1):
        n, seen = start, {}
        for step in range(max_steps):
            if n in seen:
                first = seen[n]
                found.add(tuple(sorted(k for k, s in seen.items() if s >= first)))
                break
            seen[n] = step
            n = terras(n, a, c)
    return sorted(found)


def collatz_exponents():
    """The exponents (logarithms, entropies) that the repo's Collatz work actually uses (numeric)."""
    p = math.log(2) / math.log(3)
    return {
        "log2(3), bits per tripling": math.log2(3),
        "log2(6), stopping-time spectrum k = ceil(s log2 6)": math.log2(6),
        "1 - log2(3)/2, drift in bits per shortcut step": 1 - math.log2(3) / 2,
        "H(log3 2), growth exponent of the cycle-word count": -p * math.log2(p) - (1 - p) * math.log2(1 - p),
        "log2(9/4), bits gained by two odd shortcut steps": math.log2(9 / 4),
    }


# --------------------------------------------------------------------------
# D. Look-elsewhere
# --------------------------------------------------------------------------


def is_3_smooth(n):
    """True when n has no prime factor other than 2 and 3."""
    if n < 1:
        return False
    for p in (2, 3):
        while n % p == 0:
            n //= p
    return n == 1


def exponent_of(n, base):
    """e with n == base**e, or None when n is not a power of base (n >= 1, base >= 2)."""
    if n < 1 or base < 2:
        return None
    e = 0
    while n % base == 0:
        n //= base
        e += 1
    return e if n == 1 else None


def is_shortcut_slope(f):
    """True when f = 3^s / 2^k with k >= s >= 0: the slope of a branch of the shortcut map
    with s odd steps among k (every odd step carries one halving)."""
    f = Fr(f)
    s, k = exponent_of(f.numerator, 3), exponent_of(f.denominator, 2)
    return s is not None and k is not None and k >= s


def simple_rationals(lo, hi, max_den):
    """All rationals in [lo, hi] whose denominator in lowest terms is at most max_den."""
    lo, hi = Fr(lo), Fr(hi)
    out = set()
    for q in range(1, max_den + 1):
        for p in range(math.ceil(lo * q), math.floor(hi * q) + 1):
            out.add(Fr(p, q))
    return sorted(out)


def look_elsewhere(max_den, lo=2, hi=3):
    """(all, three_smooth, slopes) simple rationals in [lo, hi].

    three_smooth: numerator and denominator are both 2^i 3^j.
    slopes: slopes of the shortcut map, see is_shortcut_slope.
    """
    everything = simple_rationals(lo, hi, max_den)
    smooth = [f for f in everything if is_3_smooth(f.numerator) and is_3_smooth(f.denominator)]
    slopes = [f for f in everything if is_shortcut_slope(f)]
    return everything, smooth, slopes


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------


def _fmt(f):
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def report_provenance():
    print("== A. Lower bound: three wires on a tripod ==")
    unit = (1, 1, 1)
    print(f"D_*(1,1,1)            = 3 - 1/3 = {_fmt(tripod_rate(unit))}")
    print(f"wire price (1,1,1)    = 3 wires x length 2 = {_fmt(wire_price(unit, unit))}")
    print(f"ratio                 = {_fmt(tripod_bound(unit, unit))}")
    print("AM-HM over three arms: (sum 1/a)^(-1) <= (sum a)/9, so D_* >= (8/9) sum a and")
    print(f"the ratio 2 sum a / D_* is at most 2 / (1 - 1/9) = {_fmt(Fr(2) / (1 - Fr(1, 9)))}")
    print(f"sqrt(lam) = 3 sqrt(lam - 2) at lam = 9/4: defect {sqrt_equation_defect(unit, Fr(9, 4)):.1e}")
    print()
    print("== Rectangular formats (x, y, z): Lean closed form vs the tripod ==")
    print("weights        Lean form   symmetric   at optimal arms   brute force   optimal arms")
    rows = [
        (1, 1, 1), (1, 1, Fr(3, 4)), (1, 1, Fr(2, 3)), (1, 1, Fr(1, 2)), (1, 1, Fr(1, 4)),
        (2, 1, 1), (3, 2, 2), (5, 4, 3), (3, 1, 1), (2, 2, 1), (1, 1, 0),
        (5, 4, Fr(9, 4)), (1, 1, Fr(51, 100)),
    ]
    for w in rows:
        lean = rectangular_exponent(*w)
        sym = rectangular_exponent_symmetric(*w)
        arms = optimal_arms(w)
        exact = tripod_bound(w, arms)
        brute, _ = tripod_sup_numeric(w)
        scale = sum(arms)
        shown = ", ".join(_fmt(a / scale) for a in arms)
        print(f"{', '.join(_fmt(Fr(v)) for v in w):<14} {_fmt(lean):<11} {_fmt(sym):<11} "
              f"{_fmt(exact):<17} {brute:<13.9f} ({shown})")
    print()
    print("family (1, 1, z):  exponent = (z + 1/2)^2 / z for z >= 1/2, and 2 below")
    for z in (Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(1)):
        print(f"  z = {_fmt(z):<4} Lean {_fmt(rectangular_exponent(1, 1, z)):<7} "
              f"(z + 1/2)^2 / z = {_fmt((z + Fr(1, 2)) ** 2 / z):<7} "
              f"paper's lower bound max(2, 3(2 + z)/4) = {_fmt(paper_rectangular_lower_bound(1, 1, z))}")
    print()
    print("== B. Upper bound: the diagonal growth lemma ==")
    print("a      H_a (float)    H_a^3 >= a   D_a >= a^(4/3)")
    for a in (1, 2, 3, 10, 100, 1000):
        h, d = growth_h(a), growth_d(a)
        print(f"{a:<6} {float(h):<14.6f} {str(h ** 3 >= a):<12} {d ** 3 >= a ** 4}")
    print(f"growth exponent of D_a, numeric: {growth_exponent_numeric():.6f}  (4/3 = {4 / 3:.6f})")
    print(f"t <= 3/4, and three legs give omega <= 3t = {_fmt(omega_from_growth())}")
    print()
    print("sensitivity (m extra copies for n*a - 1 extra length; the paper is m = 2, n = 3):")
    print("m  n   exponent 2m/n   numeric     bound 3n/(2m)")
    for m, n in ((1, 2), (2, 3), (3, 4), (3, 5), (4, 6)):
        print(f"{m}  {n}   {_fmt(Fr(2 * m, n)):<15} {growth_exponent_numeric(m, n):<11.6f} "
              f"{_fmt(omega_from_growth(m, n))}")


def report_collatz():
    print("== C. Where 9/4 lives in Collatz ==")
    print("two shortcut steps, by residue mod 4:")
    for a, c in ((3, 1), (3, -1), (3, 5), (5, 1), (7, 1)):
        branches = two_step_branches(a, c)
        text = "  ".join(f"r={r}: {_fmt(s)} n {'-' if o < 0 else '+'} {_fmt(abs(o))}"
                         for r, (s, o) in branches.items())
        print(f"  {a}x{c:+d}: {text}")
    slopes = two_step_slopes()
    mean = sum(s * w for s, w in slopes.items())
    geo = math.prod(float(s) ** float(w) for s, w in slopes.items())
    print(f"3x+1 slopes and densities: {', '.join(f'{_fmt(s)} ({_fmt(w)})' for s, w in slopes.items())}")
    print(f"arithmetic mean {_fmt(mean)}, geometric mean {geo:.6f} (= 3/4)")
    print(f"omega - 2, omega/3, omega at omega = 9/4: "
          f"{_fmt(Fr(9, 4) - 2)}, {_fmt(Fr(9, 4) / 3)}, {_fmt(Fr(9, 4))}")
    bad = [n for n in range(3, 20000, 4) if 4 * four_collatz_steps(n) != 9 * n + 5]
    print(f"collatz.core check: four steps from n = 3 mod 4 give (9n + 5)/4 for n < 20000: "
          f"{'ok' if not bad else bad[:5]}")
    print()
    print("mirror test: the slopes do not see the offset")
    print(f"  slopes of 3x+1: {[_fmt(s) for s in two_step_slopes(3, 1)]}")
    print(f"  slopes of 3x-1: {[_fmt(s) for s in two_step_slopes(3, -1)]}")
    print(f"  cycles of 3x+1 from 1..1000: {cycles(3, 1)}")
    print(f"  cycles of 3x-1 from 1..1000: {cycles(3, -1)}")
    print()
    print("generalisation ax+1: the largest two-step slope is (a/2)^2")
    for a in (3, 5, 7, 9):
        top = max(two_step_slopes(a, 1))
        print(f"  a = {a}: {_fmt(top)} = {float(top):.4f}{'   in [2, 3]' if 2 <= top <= 3 else ''}")
    print()
    print("type check: 9/4 is an exponent there, a multiplier here")
    for name, value in collatz_exponents().items():
        print(f"  {value:.6f}  {name}")
    print(f"  {9 / 4:.6f}  omega")


def report_null():
    print("== D. Look-elsewhere: simple rationals in [2, 3] ==")
    print("max denominator   all   3-smooth   slopes of T   3-smooth share")
    for q in (4, 6, 8, 12, 16, 32):
        everything, smooth, slopes = look_elsewhere(q)
        print(f"{q:<17} {len(everything):<5} {len(smooth):<10} {len(slopes):<13} "
              f"{len(smooth) / len(everything):.3f}")
    everything, smooth, slopes = look_elsewhere(4)
    print(f"denominator <= 4: {[_fmt(f) for f in everything]}")
    print(f"  3-smooth:       {[_fmt(f) for f in smooth]}")
    print(f"  slopes of T:    {[_fmt(f) for f in slopes]}   (3^s/2^k with k >= s)")


REPORTS = {"provenance": report_provenance, "collatz": report_collatz, "null": report_null}


def main(argv):
    which = argv[1] if len(argv) > 1 else "all"
    if which == "all":
        for i, report in enumerate(REPORTS.values()):
            if i:
                print()
            report()
    elif which in REPORTS:
        REPORTS[which]()
    else:
        print(f"usage: nine_fourths.py {'|'.join(REPORTS)}|all", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
