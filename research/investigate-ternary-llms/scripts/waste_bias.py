"""L2: is the mean packing waste at first drop E[w(s)] = 1/2, or biased?

w(s) = bitlen(3^s) - s*log2(3) in (0,1) is the storage waste of an s-trit
register and also the number of bits an orbit sheds at its first drop
(slope 3^s/2^b = 2^-w). Under the dropping-set measure dens(s) = N(s)/2^(b(s)-1):

    dens(s) = 2 * (N(s)/3^s) * 2^(-w(s))

so IF N(s)/3^s is smooth in s, each s is weighted by a Boltzmann factor 2^(-w)
and the conditional mean of w over a window of large s should be

    m* = int_0^1 w 2^-w dw / int_0^1 2^-w dw = 1/ln2 - 1 = 0.442695...

rather than 1/2 (equidistribution). This script tests that with the exact
N(s) from results/admissible_dp.json (run admissible_dp.py 1000 first).

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/waste_bias.py
"""
import json
from pathlib import Path

import mpmath as mp

mp.mp.dps = 60
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"

data = json.load(open(RESULTS / "admissible_dp.json"))
N = [None] + [int(x) for x in data["N"]]
S = len(N) - 1
L3 = mp.log(3, 2)

w = [None] + [mp.mpf((3**s).bit_length()) - s * L3 for s in range(1, S + 1)]
dens = [None] + [mp.mpf(N[s]) / mp.mpf(2) ** ((3**s).bit_length() - 1) for s in range(1, S + 1)]
ratio = [None] + [mp.mpf(N[s]) / mp.mpf(3) ** s for s in range(1, S + 1)]  # N(s)/3^s

m_star = 1 / mp.log(2) - 1
print(f"prediction m* = 1/ln2 - 1 = {mp.nstr(m_star, 10)}   (equidistribution would give 0.5)")

tot = sum(dens[1:])
Ew = sum(dens[s] * w[s] for s in range(1, S + 1)) / tot
print(f"\nGlobal E[w] under the dropping-set measure (s <= {S}): {mp.nstr(Ew, 8)}")

print("\nwindow          mass      E[w | window]   unweighted mean w   pred m*")
windows = [(1, 5), (6, 20), (21, 50), (51, 100), (101, 200), (201, 400), (401, 700), (701, 1000)]
for a, b in windows:
    b = min(b, S)
    mass = sum(dens[s] for s in range(a, b + 1))
    cond = sum(dens[s] * w[s] for s in range(a, b + 1)) / mass
    unw = sum(w[s] for s in range(a, b + 1)) / (b - a + 1)
    print(f"[{a:4d},{b:4d}]   {mp.nstr(mass, 3):>9}   {mp.nstr(cond, 6):>12}   {mp.nstr(unw, 6):>16}   {mp.nstr(m_star, 6)}")

# Is N(s)/3^s smooth?  Detrend log(ratio) by a local geometric mean over +-H
# neighbours and correlate the residual with w(s).  A residual that depends
# on w would mean N(s) itself "knows" the waste, beyond the explicit 2^-w.
H = 6
print(f"\nSmoothness of N(s)/3^s: residual of log2(N/3^s) vs local mean (+-{H}), s in [50, {S-H}]")
xs, ys = [], []
for s in range(50, S - H + 1):
    loc = sum(mp.log(ratio[t], 2) for t in range(s - H, s + H + 1)) / (2 * H + 1)
    xs.append(w[s])
    ys.append(mp.log(ratio[s], 2) - loc)
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
vx = sum((x - mx) ** 2 for x in xs) / n
vy = sum((y - my) ** 2 for y in ys) / n
slope = cov / vx
corr = cov / mp.sqrt(vx * vy)
print(f"  residual std = {mp.nstr(mp.sqrt(vy), 4)} bits;  slope d(residual)/dw = {mp.nstr(slope, 4)};  corr = {mp.nstr(corr, 4)}")
print("  (slope ~ 0 means N(s)/3^s is smooth and the whole bias comes from the explicit 2^-w factor;")
print("   slope ~ +1 would mean N(s) grows like 2^(b(s)) i.e. the register, not like 3^s)")

# Effective weighting exponent: fit dens-weighted histogram of w to c*2^(-a w) on the large-s tail
print("\nHistogram of w under the dropping-set measure, s in [101, S], 5 bins; ratio to bin count:")
lo, hi = 101, S
bins = [mp.mpf(0)] * 5
cnt = [0] * 5
for s in range(lo, hi + 1):
    k = min(int(w[s] * 5), 4)
    bins[k] += dens[s]
    cnt[k] += 1
tot_tail = sum(bins)
for k in range(5):
    centre = (k + 0.5) / 5
    print(f"  w in [{k/5:.1f},{(k+1)/5:.1f})  mass frac = {mp.nstr(bins[k]/tot_tail, 4)}  count = {cnt[k]:3d}  mass/count = {mp.nstr(bins[k]/cnt[k]/ (tot_tail/(hi-lo+1)), 4)}   2^-w/mean = {mp.nstr(mp.mpf(2)**(-centre) / (1/(2*mp.log(2))), 4)}")

json.dump(
    {
        "S": S,
        "m_star": float(m_star),
        "E_w_global": float(Ew),
        "windows": [[a, min(b, S)] for a, b in windows],
        "smooth_slope": float(slope),
        "smooth_corr": float(corr),
    },
    open(RESULTS / "waste_bias.json", "w"),
    indent=1,
)
print(f"\nwrote {RESULTS / 'waste_bias.json'}")
