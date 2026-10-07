"""Skeptic check 7: Pierpont primes (Q3.5) and a few second-eigenvalue moduli, recomputed independently.

rung(p) = v2(ord_p 2) - v2(ord_p 3) when ord_p(3) is even ('none' when it is odd).  The 2-adic valuations are
computed by repeated squaring of a^(odd part of p-1), not from the orders.

CONVENTION: Terras kernel K_p = (R_e + R_o)/2 on Z/p; |lambda_2| = largest modulus below 1 (float, numpy).
Run:  python -X utf8 v7_pierpont.py
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import sympy as sp

T0 = time.time()
LOG: list[str] = []
FAIL: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)


def v2_order(a: int, p: int) -> int:
    u = p - 1
    while u % 2 == 0:
        u //= 2
    y = pow(a, u, p)
    j = 0
    while y != 1:
        y = y * y % p
        j += 1
    return j


def is_pierpont(p: int) -> bool:
    n = p - 1
    while n % 2 == 0:
        n //= 2
    while n % 3 == 0:
        n //= 3
    return n == 1


def klass(p: int) -> str:
    a, b = v2_order(2, p), v2_order(3, p)
    if b == 0:
        return "none"
    r = a - b
    return "<0" if r < 0 else ("0" if r == 0 else ("1" if r == 1 else ">=2"))


say("=== 1. rung classes, all primes 5 <= p < 10^6 ===")
primes = [int(p) for p in sp.primerange(5, 10 ** 6)]
cls = {p: klass(p) for p in primes}
pier = [p for p in primes if is_pierpont(p)]
say(f"   primes: {len(primes)};  Pierpont: {len(pier)}")
check("78496 primes, 40 Pierpont", len(primes) == 78496 and len(pier) == 40)
names = ["none", "<0", "0", "1", ">=2"]
obs = {k: sum(cls[p] == k for p in pier) for k in names}
by_t: dict[int, dict[str, int]] = {}
for p in primes:
    t = ((p - 1) & -(p - 1)).bit_length() - 1
    by_t.setdefault(t, {k: 0 for k in names})[cls[p]] += 1
exp = {k: 0.0 for k in names}
for p in pier:
    t = ((p - 1) & -(p - 1)).bit_length() - 1
    tot = sum(by_t[t].values())
    for k in names:
        exp[k] += by_t[t][k] / tot
chi2 = sum((obs[k] - exp[k]) ** 2 / exp[k] for k in names)
say(f"   observed {obs};  expected {{{', '.join(f'{k}: {v:.2f}' for k, v in exp.items())}}};  chi^2 = {chi2:.2f} on 4 d.o.f.")
check("observed {none 6, <0 14, 0 11, 1: 5, >=2: 4}, chi^2 = 4.46", (obs["none"], obs["<0"], obs["0"], obs["1"], obs[">=2"]) == (6, 14, 11, 5, 4) and abs(chi2 - 4.46) < 0.01)
say("   CAVEAT: three of the five expected counts are near or below 5 (5.2, 4.4, 2.0), so the chi^2 approximation is rough; the null is")
say("   supported by the counts themselves, not by the p-value.")
for r in (1, 2, 3, 4, 5):
    first = []
    for p in primes:
        if cls[p] in ("1", ">=2") and v2_order(2, p) - v2_order(3, p) == r:
            first.append((p, "P" if is_pierpont(p) else "-"))
            if len(first) == 5:
                break
    say(f"   rung {r}: first primes {first}")
check("769 is the smallest prime of rung 3 and 1297 the smallest of rung 2",
      min(p for p in primes if cls[p] == ">=2" and v2_order(2, p) - v2_order(3, p) == 3) == 769
      and min(p for p in primes if cls[p] == ">=2" and v2_order(2, p) - v2_order(3, p) == 2) == 1297)

say("\n=== 2. |lambda_2| (float) ===")


def lam2(p: int) -> float:
    i2 = pow(2, -1, p)
    K = np.zeros((p, p))
    for t in range(p):
        K[t, t * i2 % p] += 0.5
        K[t, (3 * t + 1) * i2 % p] += 0.5
    ev = np.sort(np.abs(np.linalg.eigvals(K)))[::-1]
    return float(ev[1])


vals = {p: lam2(p) for p in (5, 7, 11, 13, 37)}
say("   " + ", ".join(f"p = {p}: {v:.4f}" for p, v in vals.items()))
check("seed values 0.8090, 0.7139, 0.6692, 0.6693, 0.6735", all(abs(vals[p] - v) < 6e-5 for p, v in ((5, 0.80902), (7, 0.7139), (11, 0.6692), (13, 0.6693), (37, 0.6735))))
pier_s = [p for p in pier if p <= 1500]
nonp = [p for p in primes if p <= 1700 and not is_pierpont(p)]
diffs, diffs97 = [], []
cache: dict[int, float] = {}
for p in pier_s:
    below = [q for q in nonp if q < p][-2:]
    above = [q for q in nonp if q > p][:2]
    nb = below + above
    for q in [p] + nb:
        if q not in cache:
            cache[q] = lam2(q)
    d_ = cache[p] - sum(cache[q] for q in nb) / len(nb)
    diffs.append(d_)
    if p >= 97:
        diffs97.append(d_)
for name, dd in (("all 19", diffs), ("p >= 97", diffs97)):
    arr = np.array(dd)
    t_ = arr.mean() / (arr.std(ddof=1) / np.sqrt(len(arr)))
    say(f"   paired difference Pierpont - mean of nearest non-Pierpont neighbours ({name}, n = {len(arr)}): mean {arr.mean():+.4f}, t = {t_:+.2f}")
check("paired differences +0.0089 (t = 1.22) and +0.0024 (t = 0.64)", abs(np.mean(diffs) - 0.0089) < 2e-4 and abs(np.mean(diffs97) - 0.0024) < 2e-4)

say(f"\n{len(FAIL)} failures;  total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
