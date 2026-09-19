"""SCRUM-30: signed-prime experiments.

E15  Exchange family: on each halving, a 2 is deleted (prob 1-p) or exchanged for a 3
     (prob p). p = 0 is Collatz, p = 1 is the mirror table. Predicted critical point
     p_c = (2 ln 2 - ln 3) / (2 ln 3) = 0.1309.
E16  Liouville sign lambda(n) = (-1)^Omega(n) ('every prime negative') along Collatz
     orbits: conservation under the mirror even step, correlations across the odd
     step, and relation to stopping class.

Run:  python -X utf8 scripts/signed_prime_experiments.py
"""

import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from collatz.core import stopping_time  # noqa: E402

OUT = ROOT / "research" / "investigate-pinball-analogy" / "results" / "signed_prime_experiments.json"
P_CRITICAL = (2 * math.log(2) - math.log(3)) / (2 * math.log(3))


def exchange_orbit_drift(p, rng, start_bits=40, steps=400, deterministic_every=None):
    """Mean log2 growth per odd step for one orbit of the exchange family."""
    b = rng.getrandbits(start_bits) | 1
    start, halvings, used = math.log2(b), 0, 0
    for _ in range(steps):
        if b < 1024:                      # absorbed near 1: stop, or the drift is diluted
            break
        used += 1
        m = 3 * b + 1
        while m % 2 == 0:
            m //= 2
            halvings += 1
            exchange = (halvings % deterministic_every == 0) if deterministic_every else rng.random() < p
            if exchange:
                m *= 3
        b = m
    return (math.log2(b) - start) / used


def e15():
    print(f"E15: exchange family, predicted p_c = {P_CRITICAL:.4f}")
    rng = random.Random(15)
    rows = []
    for p in (0.0, 0.05, 0.10, 0.12, 0.13, 0.14, 0.16, 0.25, 0.5, 1.0):
        drifts = [exchange_orbit_drift(p, rng) for _ in range(300)]
        mean = sum(drifts) / len(drifts)
        predicted = math.log2(3) - 2 + 2 * p * math.log2(3)
        rows.append((p, round(mean, 4), round(predicted, 4)))
        print(f"  p={p:<5} drift/odd step {mean:+.4f} bits   predicted {predicted:+.4f}")
    det = {}
    for every in (6, 7, 8, 9):
        drifts = [exchange_orbit_drift(0, rng, deterministic_every=every) for _ in range(300)]
        det[every] = sum(drifts) / len(drifts)
        print(f"  deterministic: exchange every {every}th halving (p=1/{every}={1 / every:.4f}): "
              f"drift {det[every]:+.4f}")
    return {"p_critical": P_CRITICAL, "iid": rows, "deterministic": det}


def omega_sieve(limit):
    """Omega(n) (prime factors with multiplicity) for n <= limit."""
    spf = np.zeros(limit + 1, dtype=np.int32)
    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
    omega = np.zeros(limit + 1, dtype=np.int16)
    for n in range(2, limit + 1):
        omega[n] = omega[n // spf[n]] + 1
    return omega


def e16():
    limit = 400_000
    print(f"\nE16: Liouville sign along orbits (n <= {limit})")
    omega = omega_sieve(3 * limit + 1)
    lam = 1 - 2 * (omega % 2).astype(np.int64)
    even = np.arange(2, limit, 2)
    print(f"  Omega(3m/2) == Omega(m) for every even m: {bool(np.all(omega[3 * even // 2] == omega[even]))}"
          f"   (mirror even step conserves the factor count)")
    print(f"  Omega(m/2) == Omega(m) - 1 for every even m: {bool(np.all(omega[even // 2] == omega[even] - 1))}")
    odd = np.arange(3, limit, 2)
    corr_odd = float(np.mean(lam[odd] * lam[3 * odd + 1]))
    corr_syr = float(np.mean(lam[odd] * lam[[(3 * int(n) + 1) // ((3 * int(n) + 1) & -(3 * int(n) + 1)) for n in odd]]))
    noise = 1 / math.sqrt(len(odd))
    print(f"  mean lambda(n)*lambda(3n+1) over odd n: {corr_odd:+.5f}   (noise scale {noise:.5f})")
    print(f"  mean lambda(n)*lambda(Syracuse(n)):      {corr_syr:+.5f}")
    print(f"  mean lambda over odd n: {float(np.mean(lam[odd])):+.5f}")
    by_class = {}
    for n in range(3, 200_001, 2):
        k = min(stopping_time(n), 30)
        s, c = by_class.get(k, (0, 0))
        by_class[k] = (s + int(lam[n]), c + 1)
    table = {k: (round(s / c, 4), c) for k, (s, c) in sorted(by_class.items()) if c >= 500}
    print(f"  mean lambda by stopping class (class: mean, count): {table}")
    mean_omega = {k: 0 for k in table}
    return {"corr_odd_step": corr_odd, "corr_syracuse": corr_syr, "noise": noise, "lambda_by_class": table}


if __name__ == "__main__":
    results = {"E15": e15(), "E16": e16()}
    OUT.write_text(json.dumps(results, indent=1, default=str))
    print(f"\nwrote {OUT}")
