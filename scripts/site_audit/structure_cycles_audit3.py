"""Third audit check: coefficient stopping time versus stopping time for 2 <= n <= 10^7.

tau(n)   = first j with 3^(s_j) < 2^j along the Terras parity vector of n
sigma(n) = first j with T^j(n) < n
Terras's Coefficient Stopping Time Conjecture: tau(n) = sigma(n) for all n >= 2.

The comparison 3^s < 2^j is done as s*log2(3) < j in float64; for s <= 400 the distance
from s*log2(3) to the nearest integer is > 1e-3, far above float error (asserted below).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 structure_cycles_audit3.py
"""
from __future__ import annotations

import math

import numpy as np

L = math.log2(3)
gap = min(abs(s * L - round(s * L)) for s in range(1, 401))
print("min distance of s*log2(3) to an integer, 1 <= s <= 400:", gap)
assert gap > 1e-3

LIM = 10_000_000
n = np.arange(LIM + 1, dtype=np.int64)
x = n.copy()
s = np.zeros(LIM + 1, dtype=np.int64)
tau = np.zeros(LIM + 1, dtype=np.int64)
sigma = np.zeros(LIM + 1, dtype=np.int64)
active = np.ones(LIM + 1, dtype=bool)
active[:2] = False
j = 0
while active.any():
    j += 1
    odd = (x & 1).astype(bool) & active
    x = np.where(active, np.where(odd, (3 * x + 1) >> 1, x >> 1), x)
    s += odd
    new_tau = active & (tau == 0) & (s * L < j)
    tau[new_tau] = j
    new_sig = active & (sigma == 0) & (x < n)
    sigma[new_sig] = j
    active &= ~((tau > 0) & (sigma > 0))
    assert j < 1000 and int(s.max()) <= 400
bad = np.nonzero(tau[2:] != sigma[2:])[0] + 2
print(f"2 <= n <= {LIM}: max sigma = {int(sigma.max())}, max tau = {int(tau.max())}")
print("n with tau(n) != sigma(n):", bad.tolist()[:20], " count:", len(bad))
