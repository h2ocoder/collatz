"""Trit-into-bit packing: record-efficient (t, b) pairs, continued fractions,
Three-Distance waste, and the Collatz dictionary.

    t trits fit in b bits  <=>  3^t <= 2^b  <=>  b >= bitlen(3^t) = ceil(t log2 3)

Everything below uses exact integer arithmetic (bit_length of 3**t) or mpmath at
80 digits; no float comparisons decide anything.

Run: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/packing_records.py
"""
from __future__ import annotations

from fractions import Fraction

import mpmath as mp

mp.mp.dps = 120
ALPHA = mp.log(3) / mp.log(2)          # log2 3
TMAX = 20000


def minbits(t: int) -> int:
    """Minimum number of bits that can hold t trits = ceil(t log2 3) (exact)."""
    return (3 ** t).bit_length()        # 3^t is never a power of 2 for t >= 1


def cf(x, n: int):
    """Continued fraction expansion of x, n terms."""
    terms, y = [], mp.mpf(x)
    for _ in range(n):
        a = int(mp.floor(y))
        terms.append(a)
        y = 1 / (y - a)
    return terms


def convergents(terms):
    p0, q0, p1, q1 = 1, 0, terms[0], 1
    out = [Fraction(p1, q1)]
    for a in terms[1:]:
        p0, q0, p1, q1 = p1, q1, a * p1 + p0, a * q1 + q0
        out.append(Fraction(p1, q1))
    return out


def semiconvergents(terms, kmax=14):
    """All best one-sided approximations: p_{k-1}+j*p_k over q_{k-1}+j*q_k."""
    p0, q0, p1, q1 = 1, 0, terms[0], 1
    out = []
    for k, a in enumerate(terms[1:kmax], start=1):
        for j in range(1, a + 1):
            out.append(Fraction(p0 + j * p1, q0 + j * q1))
        p0, q0, p1, q1 = p1, q1, a * p1 + p0, a * q1 + q0
    return out


def main() -> None:
    print("=" * 78)
    print("1. Continued fraction of log2(3)")
    print("=" * 78)
    terms = cf(ALPHA, 20)
    print("  log2 3 =", mp.nstr(ALPHA, 25))
    print("  CF     = [%d; %s]" % (terms[0], ", ".join(map(str, terms[1:]))))
    convs = convergents(terms)
    print(f"  {'k':>2s} {'p/q':>14s} {'value':>18s} {'side':>6s}")
    for k, f in enumerate(convs[:13]):
        side = "above" if mp.mpf(f.numerator) / f.denominator > ALPHA else "below"
        print(f"  {k:2d} {str(f):>14s} {mp.nstr(mp.mpf(f.numerator)/f.denominator, 16):>18s} {side:>6s}")

    print()
    print("=" * 78)
    print("2. Record-efficient packings: t trits in b = ceil(t log2 3) bits")
    print("=" * 78)
    best = mp.mpf(10)
    records = []
    for t in range(1, TMAX + 1):
        b = minbits(t)
        r = mp.mpf(b) / t
        if r < best:
            best = r
            records.append((t, b))
    print(f"  {'t':>7s} {'b':>7s} {'b/t':>12s} {'waste b - t*log2 3':>20s} {'byte-aligned?':>14s}")
    for t, b in records:
        w = b - t * ALPHA
        print(f"  {t:7d} {b:7d} {mp.nstr(mp.mpf(b)/t, 10):>12s} "
              f"{mp.nstr(w, 8):>20s} {'yes' if b % 8 == 0 else '':>14s}")

    semis = [f for f in semiconvergents(terms) if mp.mpf(f.numerator) / f.denominator > ALPHA]
    rec_fracs = {Fraction(b, t) for t, b in records}
    semi_fracs = {f for f in semis if f.denominator <= TMAX}
    print()
    print("  records that are upper semiconvergents/convergents of log2 3:",
          sorted(rec_fracs & semi_fracs, key=lambda f: f.denominator))
    print("  records NOT semiconvergents:",
          sorted(rec_fracs - semi_fracs, key=lambda f: f.denominator))
    print("  upper semiconvergents that are NOT records:",
          sorted(semi_fracs - rec_fracs, key=lambda f: f.denominator))
    print("  A206788 (denominators of semiconvergents to log2 3) first terms:")
    print("   ", sorted({f.denominator for f in semiconvergents(terms) if f.denominator <= 700}))

    print()
    print("=" * 78)
    print("3. Packing into fixed registers / blocks (what hardware actually does)")
    print("=" * 78)
    print(f"  {'register b bits':>16s} {'max trits t':>12s} {'bits/weight':>12s} {'slack bits':>11s}")
    for b in (8, 16, 32, 64, 128, 256, 512, 1024):
        t = int(mp.floor(b / ALPHA))
        while minbits(t + 1) <= b:
            t += 1
        print(f"  {b:16d} {t:12d} {mp.nstr(mp.mpf(b)/t, 8):>12s} "
              f"{mp.nstr(b - t*ALPHA, 6):>11s}")
    print()
    print("  Fixed power-of-two BLOCK of n weights (the deployed case):")
    print(f"  {'n':>6s} {'min bits':>9s} {'min bytes':>10s} {'5-trit bytes':>13s} "
          f"{'bpw(opt)':>9s} {'bpw(byte)':>10s} {'bpw(5-trit)':>12s}")
    for n in (16, 32, 64, 128, 256, 512, 1024):
        mb = minbits(n)
        bytes_opt = -(-mb // 8)
        bytes_5 = -(-n // 5)
        print(f"  {n:6d} {mb:9d} {bytes_opt:10d} {bytes_5:13d} "
              f"{mp.nstr(mp.mpf(mb)/n, 6):>9s} {8*bytes_opt/n:10.4f} {8*bytes_5/n:12.4f}")
    print()
    print("  => for n = 128: optimal-but-byte-aligned == the deployed 26 bytes.")

    print()
    print("=" * 78)
    print("4. Music: the same (t, b) pairs are the commas")
    print("=" * 78)
    for t, b, name in ((5, 8, "Pythagorean limma 256/243"),
                       (12, 19, "Pythagorean comma 3^12/2^19"),
                       (41, 65, "3^41/2^65 (41-EDO)"),
                       (53, 84, "Mercator's comma 3^53/2^84"),
                       (306, 485, "3^306/2^485 (306-EDO)"),
                       (665, 1054, "3^665/2^1054 (665-EDO)")):
        ratio = mp.mpf(3) ** t / mp.mpf(2) ** b
        fits = 3 ** t <= 2 ** b
        print(f"  t={t:4d} b={b:5d}  3^t/2^b = {mp.nstr(ratio, 10):>14s}  "
              f"{'FITS' if fits else 'OVERFLOWS':>9s}   {name}")

    print()
    print("=" * 78)
    print("5. Collatz dictionary (odd n): s Syracuse steps = s trits")
    print("=" * 78)
    # A100982 = number of admissible sequences of order s  (= repo's N(s))
    N = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033,
         108950, 312455, 663535, 1900470, 5936673, 13472296, 39993895,
         87986917, 257978502, 820236724, 1899474678, 5723030586, 12809477536,
         38036848410, 84141805077, 248369601964, 794919136728]
    print(f"  {'s':>3s} {'b=minbits(s)':>12s} {'k=s+b':>6s} {'waste w(s)':>11s} "
          f"{'slope 3^s/2^b':>13s} {'N(s)':>13s} {'density N/2^(b-1)':>18s}")
    kraft = mp.mpf(0)
    exp_k = mp.mpf(0)
    exp_w = mp.mpf(0)
    for s in range(1, len(N) + 1):
        b = minbits(s)
        k = s + b
        w = b - s * ALPHA
        dens = mp.mpf(N[s - 1]) / mp.mpf(2) ** (b - 1)
        kraft += dens
        exp_k += dens * k
        exp_w += dens * w
        if s <= 16:
            print(f"  {s:3d} {b:12d} {k:6d} {mp.nstr(w, 6):>11s} "
                  f"{mp.nstr(mp.mpf(3)**s/mp.mpf(2)**b, 8):>13s} {N[s-1]:13d} "
                  f"{mp.nstr(dens, 8):>18s}")
    print(f"  ... partial sums over s <= {len(N)}:")
    print(f"    Kraft sum  sum_s N(s)/2^(b(s)-1)      = {mp.nstr(kraft, 12)}  (-> 1)")
    print(f"    E[stopping time] (partial)            = {mp.nstr(exp_k, 12)}"
          f"   [Wagon's constant = 9.477955556...]")
    print(f"    E[waste w(s)] = E[bits shed at drop]  = {mp.nstr(exp_w, 8)}")
    print(f"    E[contraction] sum_s dens*3^s/2^b     = "
          f"{mp.nstr(sum(mp.mpf(N[s-1])/mp.mpf(2)**(minbits(s)-1) * mp.mpf(3)**s/mp.mpf(2)**minbits(s) for s in range(1, len(N)+1)), 8)}")

    print()
    print("  Increment sequence b(s+1) - b(s) (Sturmian, slope log2 3):")
    print("   ", [minbits(s + 1) - minbits(s) for s in range(1, 41)])
    print("  Increment sequence k(s+1) - k(s):")
    print("   ", [(minbits(s + 1) + s + 1) - (minbits(s) + s) for s in range(1, 41)])


if __name__ == "__main__":
    main()
