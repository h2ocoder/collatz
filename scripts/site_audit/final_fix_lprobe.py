"""Final-fixer check for the sentence added under the sign-pattern figure on
site/connections/sturmian-l-probe.md:

    over a whole period the chi_6 sum over Dset_{k_o} is  i*sqrt(3) * 2^o * (c_2 - c_1),

c_j = number of residue classes of the dropping set whose destinations are j mod 3.
Direct summation of the character over one whole period (3 * 2^k consecutive integers
starting at 2), against the class count taken from the same integers.

Run:  python -X utf8 scripts/site_audit/final_fix_lprobe.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from collatz.lfunctions import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.eisenstein import EisensteinInt  # noqa: E402

chi = SexticResidueCharacter()


def fl(i):
    return (3 ** i).bit_length() - 1


def k_of(o):
    return o + fl(o) + 1 if o else 1


def drop(n):
    x, t = n, 0
    while True:
        x = 3 * x + 1 if x & 1 else x >> 1
        t += 1
        if x < n:
            return t, x


ok = True
for o in range(1, 7):
    k = k_of(o)
    period = 3 * 2 ** k
    mod = 2 ** (k - o)
    total = 0j
    classes = {}
    for n in range(2, 2 + period):
        t, d = drop(n)
        if t != k:
            continue
        total += chi.evaluate(EisensteinInt(n, d))
        r = n % mod
        classes.setdefault(r, set()).add(d % 3)
    assert all(len(v) == 1 for v in classes.values()), "dest mod 3 is constant on each class"
    c1 = sum(1 for v in classes.values() if v == {1})
    c2 = sum(1 for v in classes.values() if v == {2})
    assert c1 + c2 == len(classes)
    pred = 1j * math.sqrt(3) * 2 ** o * (c2 - c1)
    good = abs(total - pred) < 1e-6
    ok &= good
    gap = k - k_of(o - 1)
    print(f"  o={o} k={k} gap={gap}: classes={len(classes)} c1={c1} c2={c2}  "
          f"sum={total.real:+.3f}{total.imag:+.3f}i  i*sqrt3*2^o*(c2-c1)={pred.imag:+.3f}i  "
          f"[{'OK' if good else 'FAIL'}]")
print("ALL OK" if ok else "SOME CHECKS FAILED")
