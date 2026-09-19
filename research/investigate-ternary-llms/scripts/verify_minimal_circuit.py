"""Verify the 5-unit circuit from minimal_circuit.py end-to-end as a recurrent Terras layer.

Reads results/minimal_circuit.json, runs the circuit bit-serially (LSB first) on every
n < 2^16 and on random 64-bit n, and checks the output equals T(n) = n/2 or (3n+1)/2.
Also stacks it with the 3-unit comparator to recompute stopping times.
Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/verify_minimal_circuit.py
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
circ = json.load(open(RESULTS / "minimal_circuit.json"))["circuit"]
LINES = ["start", "x", "p", "prev", "carry"]


def layer(bits):
    """Run the circuit over an LSB-first bit list; return (LSB-first bits of T(n), parity p)."""
    p = prev = carry = 0
    out = []
    for t, x in enumerate(bits):
        vals = {"start": int(t == 0), "x": x, "p": p, "prev": prev, "carry": carry}
        order = []
        for name, w, th in circ:
            ins = LINES + order
            vals[name] = int(sum(wj * vals[n] for wj, n in zip(w, ins)) >= th)
            order.append(name)
        out.append(vals["y"])
        p, prev, carry = vals["p'"], x, vals["carry'"]
    return out[1:] + [0], p


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def to_bits(n, L):
    return [(n >> i) & 1 for i in range(L)]


def from_bits(b):
    return sum(v << i for i, v in enumerate(b))


def less_than(a, b):
    lt = 0
    for ai, bi in zip(a, b):
        lt = int((-ai + bi) >= 1 or ((ai - bi) < 1 and lt))  # same 3-unit comparator, folded
    return lt


def net_stopping_time(n, max_layers=400):
    L = n.bit_length() + max_layers + 2
    x = to_bits(n, L)
    odd = 0
    for k in range(1, max_layers + 1):
        x, p = layer(x)
        odd += p
        if less_than(x, to_bits(n, L)):
            return k + odd
    raise RuntimeError


if __name__ == "__main__":
    bad = sum(from_bits(layer(to_bits(n, 40))[0]) != terras(n) for n in range(1, 1 << 16))
    print(f"5-unit layer vs T(n), n < 65536: mismatches = {bad}")
    rng = random.Random(28)
    bad = 0
    for _ in range(2000):
        n = rng.getrandbits(64) | 1 << 63
        bad += from_bits(layer(to_bits(n, 70))[0]) != terras(n)
    print(f"2000 random 64-bit n: mismatches = {bad}")
    bad = sum(net_stopping_time(n) != stopping_time(n) for n in range(2, 3000))
    print(f"stacked 5-unit layers + comparator vs core.stopping_time, 2 <= n < 3000: mismatches = {bad}")
    print(f"stopping_time(27) via 5-unit network = {net_stopping_time(27)}")
