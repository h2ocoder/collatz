"""An exact Collatz computer built only from ternary weights {-1, 0, +1}.

Every neuron is a threshold unit  out = [ sum_j w_j * in_j >= theta ]  with
w_j in {-1, 0, +1} and an integer threshold theta -- the same "no multiplications,
only additions and subtractions" arithmetic that ternary LLMs (BitNet b1.58) use.

Numbers are streamed least-significant bit first. One recurrent layer computes the
Terras map  T(n) = n/2 (n even), (3n+1)/2 (n odd)  as a carry transducer:

    3n + 1 = n + (n << 1) + 1      ->  at bit i: x_i + p*x_{i-1} + carry,  carry_0 = p
    p = x_0 (the parity of n), latched on the start token.

Stacking K identical layers computes T^K(n). A ternary LSB-first comparator on the
side reports the first K with T^K(n) < n, giving the stopping time. Every weight is
checked to be ternary when it is used.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/ternary_syracuse_circuit.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402

WEIGHT_LOG = {}  # unit name -> weight tuple (for counting / zero density)


def unit(name, weights, inputs, theta):
    """Threshold neuron with ternary weights."""
    assert all(w in (-1, 0, 1) for w in weights), (name, weights)
    assert len(weights) == len(inputs)
    WEIGHT_LOG[name] = tuple(weights) + (theta,)
    return int(sum(w * x for w, x in zip(weights, inputs)) >= theta)


def terras_layer(bits):
    """One ternary recurrent layer: LSB-first bits of n -> LSB-first bits of T(n), plus parity p.

    Recurrent state per time step: (p, prev_x, carry). Inputs per step: (start, x).
    The first output bit (always 0, since n + p*(2n+1) is even) is dropped: that is the /2.
    """
    p = prev_x = carry = 0
    out = []
    for t, x in enumerate(bits):
        start = int(t == 0)
        # latch parity on the start token:  p <- p OR (start AND x)
        sx = unit("start_and_x", (1, 1), (start, x), 2)
        p = unit("latch_p", (1, 1), (p, sx), 1)
        # second addend: p AND x_{i-1} (the 2n term), OR the +1 injected at t=0
        px = unit("p_and_prev", (1, 1), (p, prev_x), 2)
        g = unit("addend", (1, 1), (px, sx), 1)
        # full adder on (x, g, carry) with three thresholds of the same sum
        h1 = unit("sum_ge1", (1, 1, 1), (x, g, carry), 1)
        h2 = unit("sum_ge2", (1, 1, 1), (x, g, carry), 2)
        h3 = unit("sum_ge3", (1, 1, 1), (x, g, carry), 3)
        y = unit("parity", (1, -1, 1), (h1, h2, h3), 1)  # h1 - h2 + h3 = sum mod 2
        carry, prev_x = h2, x  # majority is the carry; identity copy of x
        out.append(y)
    return out[1:] + [0], p  # dropping the first bit is a one-step delay


def less_than(a_bits, b_bits):
    """Ternary LSB-first comparator: is a < b ? (the most significant differing bit decides)."""
    lt = 0
    for a, b in zip(a_bits, b_bits):
        b_gt = unit("b_gt_a", (-1, 1), (a, b), 1)
        a_gt = unit("a_gt_b", (1, -1), (a, b), 1)
        lt = unit("lt_update", (1, -1, 1), (b_gt, a_gt, lt), 1)
    return lt


def to_bits(n, L):
    return [(n >> i) & 1 for i in range(L)]


def from_bits(bits):
    return sum(b << i for i, b in enumerate(bits))


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def network_stopping_time(n, max_layers=400):
    """Stack Terras layers until the comparator fires; convert to standard Collatz steps."""
    L = n.bit_length() + max_layers + 2  # T grows by < log2(3/2) bits per layer
    x = to_bits(n, L)
    n_bits = x
    odd_steps = 0
    for k in range(1, max_layers + 1):
        x, p = terras_layer(x)
        odd_steps += p
        if less_than(x, n_bits):
            # each odd Terras step is two Collatz steps (3n+1, then /2)
            return k + odd_steps, x
    raise RuntimeError("no drop within max_layers")


if __name__ == "__main__":
    # 1. single layer == Terras map
    L = 40
    bad = sum(from_bits(terras_layer(to_bits(n, L))[0]) != terras(n) for n in range(1, 1 << 16))
    print(f"single layer vs T(n), n < 65536: mismatches = {bad}")

    # 2. stacked network stopping time == collatz.core.stopping_time
    bad = 0
    for n in range(2, 20_000):
        st, _ = network_stopping_time(n)
        bad += st != stopping_time(n)
    print(f"network stopping time vs core.stopping_time, 2 <= n < 20000: mismatches = {bad}")

    rng = random.Random(28)
    bad = 0
    for _ in range(300):
        n = rng.getrandbits(64) | (1 << 63)
        bad += network_stopping_time(n)[0] != stopping_time(n)
    print(f"300 random 64-bit n: mismatches = {bad}")
    print(f"stopping_time(27) via network = {network_stopping_time(27)[0]}")

    # 3. receptive field: parity of T^j(n) depends only on bits 0..j of n (Terras 1976)
    K = 10
    bad = 0
    for n in range(1, 1 << 14):
        x, parities = to_bits(n, 40), []
        for _ in range(K):
            x, p = terras_layer(x)
            parities.append(p)
        low = n & ((1 << K) - 1)
        y, lowpar = to_bits(low, 40), []
        for _ in range(K):
            y, p = terras_layer(y)
            lowpar.append(p)
        bad += parities != lowpar
    print(f"first {K} parities depend only on n mod 2^{K}, n < 16384: mismatches = {bad}")

    # 4. weight statistics
    ws = [w for v in WEIGHT_LOG.values() for w in v[:-1]]
    z = ws.count(0) / len(ws)
    print(f"\ndistinct units: {len(WEIGHT_LOG)}, stored weights: {len(ws)}, zero weights: {ws.count(0)}")
    for name, v in WEIGHT_LOG.items():
        print(f"  {name:12s} w={v[:-1]} theta={v[-1]}")
