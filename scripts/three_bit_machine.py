"""The gated two-tank machine: cycle enumeration, value weights, and the
2-adic fixed-point trichotomy.

States (avoidance only): weak(V) for V>=3, medium(W) for W>=4 (med(6) forces
strong at the NEXT encounter, so it has no avoidance continuation).  Edges
follow the proved refill table; growth-phase lengths (g>=1) and hatch/exit
outcomes are free choices (an over-approximation - sound for lower bounds).

Per encounter, the BACKWARD value multiplier is 2^(d+g)/3^(1+g):
    beta = (d - log2 3) - (log2 3 - 1) g   bits/encounter
and the class-constraint cost is  eps = d + g  bits/encounter.

What this script certifies:
 1. The value-weighted min-mean-cycle is NEGATIVE (e.g. weak3 -g1-> weak3 has
    beta = -0.17): value-telescoping alone CANNOT prove the countdown.
 2. Every cycle word is an affine map x -> (3^S x + C)/2^E with C > 0, so its
    2-adic fixed point x* = C/(2^E - 3^S) satisfies
        beta_cycle < 0  <=>  3^S > 2^E  <=>  x* < 0.
    A negative fixed point means length-n truncations of the cycle word have
    class representative ~ 2^(eps n) - |x*|: reps grow at the FULL bits rate
    (eps >= 2 bits/enc).  The same C > 0 positivity that eliminated ascending
    cycles in Front 1 rescues the countdown from value-shrinking words.
 3. Positive non-integer rational fixed points also force Theta(2^(eps n))
    reps (2-adic digits of a non-integer rational are eventually periodic and
    nonzero infinitely often).  The only integer fixed point is x* = 1, the
    trivial cycle (pure-weak word).
Hence every eventually-periodic avoidance word has rep growth at ~4^n or
more, and the observed A(n) ~ (4/3)^n must come from generic transient words
- the density rate.  The deterministic gap is bounding aperiodic words, where
the natural tool is Front 1's second-moment / Parseval method applied to
avoidance-class residues.
"""

from __future__ import annotations

import math
from fractions import Fraction
from itertools import product

LOG2_3 = math.log2(3)
V_CAP, W_CAP, G_CAP, LEN_CAP = 9, 10, 3, 5


def all_states():
    return [("weak", V) for V in range(3, V_CAP + 1)] + \
           [("med", W) for W in range(4, W_CAP + 1)]


def edges_from(state):
    """List of (next_state, (d, g)) avoidance edges of the machine."""
    kind, fuel = state
    out = []
    if kind == "weak":
        V = fuel
        if V >= 5:
            out.append((("weak", V - 2), (2, 0)))
        elif V == 4:  # hatch: choose W' >= 4 (W' = 3 would force strong)
            out += [((("med", Wp)), (2, 0)) for Wp in range(4, W_CAP + 1)]
        else:  # V == 3: growth phase, then free exit
            out += [(nxt, (2, g)) for g in range(1, G_CAP + 1) for nxt in all_states()]
    else:
        W = fuel
        if W >= 7 and W - 3 >= 4:
            out.append((("med", W - 3), (3, 0)))
        elif W == 5:  # hatch: choose V' >= 3
            out += [((("weak", Vp)), (3, 0)) for Vp in range(3, V_CAP + 1)]
        elif W == 4:  # growth phase, then free exit
            out += [(nxt, (3, g)) for g in range(1, G_CAP + 1) for nxt in all_states()]
        # W == 6: no avoidance continuation (W' = 3 -> strong forced)
    return out


def cycle_word_stats(word):
    """word = [(d, g), ...] per encounter.  Returns (S, E, C, x*, beta, eps)
    for the periodic word's affine map x -> (3^S x + C)/2^E."""
    a, b = Fraction(1), Fraction(0)
    S = E = 0
    for d, g in word:
        for dd in [d] + [1] * g:  # the drop, then g growth steps
            a, b = 3 * a / 2**dd, (3 * b + 1) / 2**dd
            S += 1
            E += dd
    xstar = b / (1 - a)
    C = (b * 2**E).numerator // (b * 2**E).denominator if b else 0
    n = len(word)
    return S, E, C, xstar, (E - S * LOG2_3) / n, E / n


def enumerate_cycles():
    states = all_states()
    edge_map = {s: edges_from(s) for s in states}
    seen, results = set(), []
    for L in range(1, LEN_CAP + 1):
        for path in product(states, repeat=L):
            labels = []
            for i in range(L):
                nxt = path[(i + 1) % L]
                lab = next((l for (s, l) in edge_map[path[i]] if s == nxt), None)
                if lab is None:
                    break
                labels.append(lab)
            else:
                key = frozenset(zip(path, labels))
                if key not in seen:
                    seen.add(key)
                    results.append((path, labels))
    return results


def main() -> None:
    cycles = enumerate_cycles()
    print(f"enumerated {len(cycles)} distinct machine cycles "
          f"(len <= {LEN_CAP}, V <= {V_CAP}, W <= {W_CAP}, g <= {G_CAP})")

    neg, pos_frac, pos_int = [], [], []
    for path, word in cycles:
        S, E, C, xstar, beta, eps = cycle_word_stats(word)
        assert C > 0, "affine constant must be positive"
        assert (beta < 0) == (3**S > 2**E) == (xstar < 0), (word, beta, xstar)
        (neg if xstar < 0 else pos_int if xstar.denominator == 1 else pos_frac
         ).append((beta, eps, word, xstar))

    print(f"\nbeta < 0 (value-shrinking) cycles: {len(neg)} -- every one has x* < 0")
    for b, e, w, x in sorted(neg)[:6]:
        print(f"  beta={b:+.3f}  eps={e:.2f}  word={w}  x* = {x}")

    print(f"\nx* positive non-integer cycles: {len(pos_frac)} "
          f"(rep growth Theta(2^(eps n)), eps >= 2)")
    for b, e, w, x in sorted(pos_frac)[:4]:
        print(f"  beta={b:+.3f}  eps={e:.2f}  word={w}  x* = {x}")
    print(f"\nx* positive integer cycles: {len(pos_int)}")
    for b, e, w, x in pos_int:
        print(f"  beta={b:+.3f}  eps={e:.2f}  word={w}  x* = {x}   <-- integer")

    allc = neg + pos_frac + pos_int
    vmin = min(b for b, _, _, _ in allc)
    emin = min(e for _, e, _, _ in allc)
    print(f"\nvalue-weighted min-mean-cycle = {vmin:+.3f} bits/enc "
          f"({'NEGATIVE: value-telescoping insufficient' if vmin < 0 else 'positive'})")
    print(f"bits-weighted  min-mean-cycle = {emin:+.3f} bits/enc "
          f"(rep-growth floor for eventually-periodic words)")


if __name__ == "__main__":
    main()
