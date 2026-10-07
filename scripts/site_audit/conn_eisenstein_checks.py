"""Audit checks for site/connections/eisenstein.md and AlphaPositionChart.vue.

1. Orbit of 27: fraction of the lattice walk below the line h = s*log2(3).
2. Mean relative position of each alpha group, replicating the chart
   (odd n = 3..5999, Syracuse orbits with at least 5 steps, relPos = i/(s-1)),
   with and without the final step into 1 (which always has alpha >= 4).
3. Same statistic for other ranges, to see how range-dependent the 0.74 is.
4. Distribution of alpha by size of x (is 3x+1 'more likely divisible by high powers of 2
   for small x'?).
"""
import math
from collections import defaultdict

LOG23 = math.log2(3)


def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def syr_orbit(m):
    seq = [m]
    while m != 1:
        m = 3 * m + 1
        while m % 2 == 0:
            m //= 2
        seq.append(m)
    return seq


def walk_27():
    orb = syr_orbit(27)
    alphas = [v2(3 * m + 1) for m in orb[:-1]]
    h = s = 0
    below = 0
    pts = []
    for a in alphas:
        s += 1
        h += a
        ex = h - s * LOG23
        pts.append(ex)
        below += ex < 0
    n = len(alphas)
    print(f"27: {n} Syracuse steps, {below} walk points below the line = {below / n:.1%}; "
          f"above at step indices {[i + 1 for i, e in enumerate(pts) if e > 0]}")
    print("    odd values:", orb)
    # first time above
    first = next(i + 1 for i, e in enumerate(pts) if e > 0)
    print(f"    first above the line at Syracuse step {first} of {n} ({first / n:.1%})")


def mean_positions(lo, hi, drop_last=False, min_steps=5):
    tot = defaultdict(float)
    cnt = defaultdict(int)
    last_alpha = defaultdict(int)
    for n in range(lo | 1, hi, 2):
        orb = syr_orbit(n)
        s = len(orb) - 1
        if s < min_steps:
            continue
        last_alpha[v2(3 * orb[s - 1] + 1)] += 1
        rng = range(s - 1) if drop_last else range(s)
        for i in rng:
            a = v2(3 * orb[i] + 1)
            g = min(a, 4)
            tot[g] += i / (s - 1)
            cnt[g] += 1
    return {g: (tot[g] / cnt[g], cnt[g]) for g in sorted(cnt)}, dict(sorted(last_alpha.items()))


if __name__ == "__main__":
    walk_27()
    for lo, hi in ((3, 6000), (3, 100000), (100001, 200000)):
        mp, la = mean_positions(lo, hi)
        mp2, _ = mean_positions(lo, hi, drop_last=True)
        print(f"odd n in [{lo}, {hi}): mean relative position by alpha group (1,2,3,>=4)")
        print("    all steps        :", {g: (round(m, 3), c) for g, (m, c) in mp.items()})
        print("    final step removed:", {g: (round(m, 3), c) for g, (m, c) in mp2.items()})
        print("    alpha of the final step (into 1):", la)

    # 4. alpha distribution by size of x
    print("share of odd x with v2(3x+1) >= 4, by range (exact density is 1/8):")
    for lo, hi in ((1, 100), (1, 1000), (1000, 2000), (10 ** 6, 10 ** 6 + 2000)):
        xs = range(lo | 1, hi, 2)
        k = sum(v2(3 * x + 1) >= 4 for x in xs)
        print(f"    x in [{lo}, {hi}): {k}/{len(xs)} = {k / len(xs):.4f}")
