"""Audit checks for site/explore/log6-wobble.md (and two leftovers for
dropping-dictionary.md).  Nothing is written outside stdout.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

LOG6 = math.log(6)
ALPHA = math.log(3) / LOG6
BETA = math.log2(3)


def orbit(n: int) -> list[int]:
    seq = [n]
    while n != 1:
        n = 3 * n + 1 if n & 1 else n >> 1
        seq.append(n)
    return seq


def eps(q: int) -> float:
    return q * ALPHA - round(q * ALPHA)


def wobble(seq):
    w = np.zeros(len(seq))
    acc = 0.0
    for j, x in enumerate(seq[:-1]):
        if x & 1:
            acc += math.log1p(1.0 / (3.0 * x)) / LOG6
        w[j + 1] = acc
    return w


def main() -> None:
    print("=== 1. W_total = log_6 of Roosendaal's residue Res(n) = 2^E / (3^O n) ===")
    best = (0.0, 0)
    for n in range(3, 100001, 2):
        seq = orbit(n)
        O = sum(1 for x in seq[:-1] if x & 1)
        E = len(seq) - 1 - O
        res = Fraction(2 ** E, 3 ** O * n)
        wt = math.log(res) / LOG6
        if n in (27, 993, 670617279):
            print(f"  n={n}: Res = {float(res):.9f}, W_total = log6 Res = {wt:.7f}, sum of increments = {wobble(seq)[-1]:.7f}")
        if wt > best[0]:
            best = (wt, n)
    print(f"  max W_total over odd n < 10^5: {best[0]:.7f} at n = {best[1]}  (Res = {6 ** best[0]:.9f})")

    print("\n=== 2. orbit of 670617279: Weyl amplitudes with / without wobble, coherence D ===")
    seq = orbit(670617279)
    N = len(seq)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    w = wobble(seq)
    k = np.arange(N)
    rigid = theta[0] + k * ALPHA
    print(f"  points = {N}, steps = {N-1}, sigma_W = {w.std():.4f}, W_total = {w[-1]:.5f}")
    for m in (13, 31, 44, 75, 106, 137):
        a_obs = abs(np.exp(2j * np.pi * m * theta).mean())
        a_rot = abs(np.exp(2j * np.pi * m * rigid).mean())
        D = abs(np.exp(2j * np.pi * m * w).mean())
        print(f"  m={m:3d} eps={eps(m):+.5f}: rigid {a_rot:.4f} -> orbit {a_obs:.4f}  (ratio {a_obs/a_rot:.2f});  D(m) = {D:.3f};  rigid*D = {a_rot*D:.4f}")
    # share of steps on which W is still below 10% of its final value
    print(f"  share of points with W_k < 0.1*W_total: {(w < 0.1 * w[-1]).mean():.3f};"
          f" last 40 points carry {100*(w[-1]-w[-41])/w[-1]:.1f}% of W_total")
    # RMS closure miss
    for q in (31, 44):
        d = (theta[q:] - theta[:-q] + 0.5) % 1.0 - 0.5
        print(f"  q={q}: RMS closure miss = {np.sqrt((d**2).mean()):.4f}; min |miss| = {np.abs(d).min():.5f}; "
              f"identity check max| |eps+dW| - |miss| | = {np.abs(np.abs(eps(q) + (w[q:]-w[:-q])) - np.abs(d)).max():.2e}")

    print("\n=== 3. closure miss is identically |eps_q + dW| (so the 'dip at r = 1' is algebra) ===")
    worst = 0.0
    for n in range(10 ** 6 + 1, 10 ** 6 + 401, 2):
        seq = orbit(n)
        th = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
        ww = wobble(seq)
        for q in (13, 31, 44, 75, 106, 137):
            if len(seq) <= q:
                continue
            d = (th[q:] - th[:-q] + 0.5) % 1.0 - 0.5
            pred = eps(q) + (ww[q:] - ww[:-q])
            pred = (pred + 0.5) % 1.0 - 0.5
            worst = max(worst, float(np.abs(d - pred).max()))
    print(f"  200 orbits, six q: max |miss - wrap(eps_q + dW)| = {worst:.2e}")

    print("\n=== 4. arm-count rule: argmin over ALL q <= 2000 of q^2 + (2 pi k eps_q)^2 ===")
    qs = np.arange(1, 2001)
    e = np.array([eps(int(q)) for q in qs])
    prev = None
    seen = []
    for kk in range(1, 6001):
        val = qs.astype(float) ** 2 + (2 * np.pi * kk * e) ** 2
        b = int(qs[val.argmin()])
        if b != prev:
            seen.append((kk, b))
            prev = b
    print("  (first k, optimal q):", seen)

    print("\n=== 5. the same 12-band parastichy measurement on the RIGID rotation ===")

    def nn_gaps(th, n_pts):
        idx = np.arange(n_pts)
        ang = 2 * np.pi * th[:n_pts]
        x, y = idx * np.cos(ang), idx * np.sin(ang)
        nn = np.empty(n_pts, dtype=int)
        for lo in range(0, n_pts, 500):
            hi = min(lo + 500, n_pts)
            d2 = (x[lo:hi, None] - x) ** 2 + (y[lo:hi, None] - y) ** 2
            d2[np.arange(hi - lo), np.arange(lo, hi)] = np.inf
            nn[lo:hi] = d2.argmin(1)
        return np.abs(nn - idx)

    n_pts = 3450
    th = (0.37 + np.arange(n_pts) * ALPHA) % 1.0
    gaps = nn_gaps(th, n_pts)
    bands = np.linspace(0, n_pts, 13).astype(int)
    out = []
    for lo, hi in zip(bands[:-1], bands[1:]):
        vals, counts = np.unique(gaps[lo:hi], return_counts=True)
        out.append(((lo + hi) // 2, int(vals[counts.argmax()])))
    print("  rigid rotation, 3450 points, (band centre, modal arm count):", out)

    print("\n=== 6. dictionary: congruence 2^e d = C (mod 3^s) versus genuine predecessor ===")

    def drop(n):
        x, kk, s = n, 0, 0
        while True:
            if x & 1:
                x = 3 * x + 1
                s += 1
            else:
                x >>= 1
            kk += 1
            if x < n:
                return kk, s, x
            if kk > 10000:
                return None

    def words(s):
        res = []

        def rec(word, o, ee, last_o):
            if not last_o and o + 1 <= s:
                rec(word + "O", o + 1, ee, True)
            if 3 ** o < 2 ** (ee + 1):
                if o == s:
                    res.append(word + "E")
            else:
                rec(word + "E", o, ee + 1, False)

        if s == 0:
            return ["E"]
        rec("O", 1, 0, True)
        return res

    def affine(word):
        add = Fraction(0)
        s = ee = 0
        for ch in word:
            if ch == "O":
                add = 3 * add + 1
                s += 1
            else:
                add = add / 2
                ee += 1
        return s, ee, int(add * 2 ** ee)

    hits = genuine = 0
    fails = []
    rule_ok = True
    for s in range(0, 9):
        for wd in words(s):
            s_, ee, C = affine(wd)
            for d in range(1, 3000):
                if (2 ** ee * d - C) % 3 ** s:
                    continue
                n = (2 ** ee * d - C) // 3 ** s
                hits += 1
                ok = n >= 2 and drop(n) == (s + ee, s, d)
                genuine += ok
                if ok != (d * (2 ** ee - 3 ** s) > C):
                    rule_ok = False
                if not ok and len(fails) < 8:
                    fails.append((d, wd, n))
    print(f"  levels s<=8, d<3000: congruence hits = {hits}, genuine predecessors = {genuine} ({genuine/hits:.4f})")
    print(f"  first non-genuine (d, word, candidate n): {fails}")
    print(f"  genuine  <=>  congruence and d*(2^e - 3^s) > C : {rule_ok}")

    print("\n=== 7. where s*log2 3 is nearest an integer; contraction 3^s / 2^e_s ===")
    for s in (5, 12, 13, 31, 41, 53, 106, 137, 306):
        x = s * BETA
        fl = (3 ** s).bit_length() - 1
        ratio = Fraction(3 ** s, 2 ** (fl + 1))
        print(f"  s={s:3d}: s*log2 3 = {x:.4f} (distance to nearest integer {abs(x-round(x)):.4f}); "
              f"e_s = {fl+1}, word length k = {s+fl+1}, 3^s/2^e_s = {float(ratio):.5f}")
    print("  convergents p/q of log2 3: 3/2, 8/5, 19/12, 65/41, 84/53, 485/306 ; p+q =", [3+2, 8+5, 19+12, 65+41, 84+53, 485+306])


if __name__ == "__main__":
    main()
