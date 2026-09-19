"""L3: Winkler's binomial bounds on N(s) and the tail of undecided odd numbers.

Winkler (OEIS A100982, 2026):  C(m-1, s-1)/s <= N(s) <= C(m, s-1)/s,  m = floor(s log2 3) = b(s) - 1.
Density of the dropping set with s Syracuse steps among odd n: dens(s) = N(s)/2^m.
Fraction of odd n NOT yet decided by their low p bits:  U(p) = sum_{s : b(s) > p} dens(s).

Because m ~ s log2 3 and s-1 ~ theta*m with theta = 1/log2 3, the binomial gives
    dens(s) = 2^{ m (H(theta) - 1) + O(log s) },   H = binary entropy,
so  U(p) = 2^{ -(1 - H(theta)) p + o(p) }.  This script checks the bounds exactly,
measures the rate, and produces an explicit numeric bound U(p) <= A * 2^(-c p).

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/winkler_tail.py
Needs results/admissible_dp.json from admissible_dp.py 1000.
"""
import json
from fractions import Fraction
from math import comb
from pathlib import Path

import mpmath as mp

mp.mp.dps = 30
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
data = json.load(open(RESULTS / "admissible_dp.json"))
N = [None] + [int(x) for x in data["N"]]
S = len(N) - 1


def b(s):
    return (3**s).bit_length()


def lower(s):
    m = b(s) - 1
    return Fraction(comb(m - 1, s - 1), s)


def upper(s):
    m = b(s) - 1
    return Fraction(comb(m, s - 1), s)


# 1. bounds hold?  how tight?
viol = [s for s in range(1, S + 1) if not (lower(s) <= N[s] <= upper(s))]
print(f"Winkler bounds checked for s = 1..{S}: violations = {len(viol)} {viol[:5]}")
print("\n   s     N/lower    N/upper    upper/lower")
for s in (5, 10, 20, 50, 100, 200, 500, 1000):
    print(f"{s:5d}  {float(N[s]/lower(s)):9.4f}  {float(N[s]/upper(s)):9.4f}  {float(upper(s)/lower(s)):9.4f}")

# 2. rate constant
theta = 1 / mp.log(3, 2)
H = -theta * mp.log(theta, 2) - (1 - theta) * mp.log(1 - theta, 2)
c_bit = 1 - H                 # per low bit
c_step = c_bit * mp.log(3, 2)  # per Syracuse step
print(f"\ntheta = 1/log2 3 = {mp.nstr(theta, 8)},  H(theta) = {mp.nstr(H, 8)}")
print(f"predicted decay: dens(s) ~ 2^(-{mp.nstr(c_step, 6)} s),  U(p) ~ 2^(-{mp.nstr(c_bit, 6)} p)")

dens = [None] + [Fraction(N[s], 2 ** (b(s) - 1)) for s in range(1, S + 1)]
print("\nmeasured local rate  -log2(dens(s+100)/dens(s))/100 :")
for s in (100, 200, 400, 600, 800):
    r = -(mp.log(mp.mpf(dens[s + 100].numerator) / dens[s + 100].denominator, 2)
          - mp.log(mp.mpf(dens[s].numerator) / dens[s].denominator, 2)) / 100
    print(f"  s={s:4d}: {mp.nstr(r, 5)}   (predicted asymptote {mp.nstr(c_step, 5)}; finite-s correction ~ 1.5/(s ln2) = {mp.nstr(1.5/(s*mp.log(2)), 4)})")

# 3. exact U(p) from the DP (valid for p up to b(S) - 1 since all s with b(s) <= p are included)
by_b = {}
for s in range(1, S + 1):
    by_b.setdefault(b(s), []).append(s)
p_max = b(S) - 1
total = sum(dens[1:])
U = {}
dec = Fraction(0)
for p in range(1, p_max + 1):
    for s in by_b.get(p, []):
        dec += dens[s]
    U[p] = 1 - dec  # exact: includes the (tiny) mass beyond s = S, which is < 1e-27
print(f"\nexact U(p) (1 - decided mass; the mass beyond s={S} is {float(1-total):.1e}):")
for p in (12, 16, 24, 32, 48, 64, 100, 200, 400, 800, 1200):
    if p <= p_max:
        print(f"  p={p:5d}: U = {float(U[p]):.4e}   -log2(U)/p = {float(-mp.log(mp.mpf(U[p].numerator)/U[p].denominator, 2)/p):.5f}")

# 4. Winkler-upper-bound tail: T(p) = sum_{s: b(s) > p} upper(s)/2^(b(s)-1), computed to s = S_B
S_B = 3000
ub = {}
for s in range(1, S_B + 1):
    ub[s] = upper(s) / 2 ** (b(s) - 1)
# tail from S_B onward bounded geometrically.  b(s) steps by 1 or 2 (Sturmian), so
# one-step ratios fluctuate above 1; over 12 steps b always advances by 19 and the
# ratio is safely < 1.  Bound the tail by 12 interleaved geometric series.
K = 12
r12 = max(float(ub[s + K] / ub[s]) for s in range(S_B - 300, S_B - K + 1))
assert r12 < 1, r12
rq = Fraction(r12).limit_denominator(10**6)
geo = sum(ub[s] for s in range(S_B - K + 1, S_B + 1)) * rq / (1 - rq)
print(f"\nupper-bound tail computed to s={S_B}; 12-step ratio ub(s+12)/ub(s) near the end <= {r12:.5f} (< 1, series converges)")
print(f"  geometric remainder beyond s={S_B}: {float(geo):.2e}")

# 5. how close is N(s) to the upper bound, and does it depend on the waste w(s)?
w = {s: b(s) - s * float(mp.log(3, 2)) for s in range(1, S + 1)}
exact_eq = [s for s in range(1, S + 1) if N[s] == upper(s)]
print(f"\nN(s) == Winkler upper bound C(m,s-1)/s EXACTLY at s = {exact_eq[:40]}{' ...' if len(exact_eq) > 40 else ''}  ({len(exact_eq)} values <= {S})")
print("  waste w(s) at those s:", [round(w[s], 4) for s in exact_eq[:12]])
print("\nN(s)/upper(s) binned by waste w(s), s in [50, 1000]:")
bins = [[] for _ in range(10)]
for s in range(50, S + 1):
    bins[min(int(w[s] * 10), 9)].append(float(N[s] / upper(s)))
for k in range(10):
    if bins[k]:
        mean = sum(bins[k]) / len(bins[k])
        print(f"  w in [{k/10:.1f},{(k+1)/10:.1f}): mean N/upper = {mean:.4f}   min {min(bins[k]):.4f}  max {max(bins[k]):.4f}   n={len(bins[k])}")
# T(p) = sum over s with b(s) > p
suffix = {}
acc = geo
for s in range(S_B, 0, -1):
    acc += ub[s]
    suffix[s] = acc
print("\n  p     exact U(p)     Winkler tail T(p)    T/U     A_p := T(p) 2^(c p)")
worstA = 0
for p in list(range(2, 60)) + [64, 100, 200, 400, 800, 1200]:
    if p > p_max:
        break
    s0 = next(s for s in range(1, S_B + 1) if b(s) > p)  # smallest s with b(s) > p
    T = suffix[s0]
    A = float(mp.mpf(T.numerator) / T.denominator * mp.mpf(2) ** (c_bit * p))
    worstA = max(worstA, A)
    if p in (2, 4, 8, 12, 16, 24, 32, 48, 64, 100, 200, 400, 800, 1200):
        print(f"{p:4d}   {float(U[p]):.4e}    {float(T):.4e}      {float(T/U[p]):6.2f}    {A:.3f}")
print(f"\nExplicit bound (assuming Winkler's upper bound):  U(p) <= {worstA:.3f} * 2^(-{mp.nstr(c_bit, 5)} p)  for all p checked,")
print("i.e. the fraction of odd n undecided after p low bits is at most that; the exponent 1 - H(1/log2 3) is sharp.")

json.dump(
    {
        "S": S, "violations": viol, "theta": float(theta), "H_theta": float(H),
        "c_per_bit": float(c_bit), "c_per_step": float(c_step), "A": worstA,
        "U_exact": {p: float(U[p]) for p in U if p <= 1500},
    },
    open(RESULTS / "winkler_tail.json", "w"), indent=1,
)
print(f"wrote {RESULTS / 'winkler_tail.json'}")
