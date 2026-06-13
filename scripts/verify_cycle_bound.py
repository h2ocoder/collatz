"""Reproducibility check for papers/cycle-bounds/collatz-cycle-bounds.tex.

Verifies, with exact/high-precision arithmetic, every numerical claim behind the
cycle lower bound:

  Lemma (closed-word eq):   (2^K - 3^m) n_0 = S,  S = sum 3^{m-1-i} 2^{V_i}.
  Lemma (geom-mean):        prod (3 + 1/n_i) = 2^K  =>  n_min <= 1/(2^{K/m}-3).
  Theorem:                  with no cycle below B=2^68, K/m lies in (theta, theta+delta]
                            with delta < 2^-69; the simplest fraction there is
                            114208327604 / 72057431991, so any nontrivial cycle has
                            m >= 72057431991, K >= 114208327604, period >= 1.86e11.

Run: .venv/bin/python scripts/verify_cycle_bound.py
"""

from __future__ import annotations

import mpmath as mp

mp.mp.dps = 120


def odd_step(n: int) -> tuple[int, int]:
    x = 3 * n + 1
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return x, v


def closed_word_equation(cycle: list[int]) -> bool:
    """Check (2^K - 3^m) n_0 = S and the product identity on a genuine T-cycle."""
    m = len(cycle)
    K = 0
    S = 0
    V = 0
    prod = mp.mpf(1)
    for i, n in enumerate(cycle):
        nxt, v = odd_step(n)
        assert nxt == cycle[(i + 1) % m], "not a T-cycle"
        S += 3 ** (m - 1 - i) * (1 << V)
        V += v
        K += v
        prod *= mp.mpf(3 * n + 1) / n
    lhs = (1 << K) - 3 ** m
    eq = lhs * cycle[0] == S
    prod_ok = abs(prod - mp.mpf(2) ** K) < mp.mpf(10) ** -40
    gm_ok = mp.mpf(2) ** (mp.mpf(K) / m) <= 3 + mp.mpf(1) / min(cycle) + mp.mpf(10) ** -40
    return eq and prod_ok and gm_ok


def simplest_fraction(lo, hi):
    """Unique least-denominator fraction in (lo, hi]; classical CF descent."""
    fl = int(mp.floor(lo))
    if fl + 1 <= hi:
        return (fl + 1, 1)
    p, q = simplest_fraction(1 / (hi - fl), 1 / (lo - fl))
    return (fl * p + q, p)


def main() -> None:
    theta = mp.log(3) / mp.log(2)

    # ---- lemmas on the trivial cycle {1} (the only equality case) ----
    assert closed_word_equation([1]), "lemmas fail on trivial cycle"
    print("Lemmas (closed-word eq, product identity, GM bound): OK on {1}")
    print(f"  trivial cycle: 2^(K/m)=4 = 3 + 1/1  (equality, as predicted)\n")

    # ---- theorem constants ----
    B = mp.mpf(2) ** 68
    U = mp.log(3 + 1 / B) / mp.log(2)
    delta = U - theta
    p, q = simplest_fraction(theta, U)
    val = mp.mpf(p) / q

    print(f"verification height B = 2^68")
    print(f"forced interval (theta, theta+delta],  delta = 2^{float(mp.log(delta)/mp.log(2)):.3f}")
    print(f"simplest fraction in interval: {p}/{q}")
    assert theta < val <= U, "simplest fraction not in interval"
    assert (p, q) == (114208327604, 72057431991), "constant mismatch"
    print(f"  theta < p/q <= U : {bool(theta < val <= U)}")
    print(f"  p/q - theta      = 2^{float(mp.log(val-theta)/mp.log(2)):.2f}  (< delta)")

    period = q + p
    print("\n=> RIGOROUS (conditional on B=2^68 verification):")
    print(f"   any nontrivial 3x+1 cycle has")
    print(f"     odd elements m >= {q:,}")
    print(f"     halvings     K >= {p:,}")
    print(f"     full period    >= {period:,}  (~{float(period):.3e} steps)")
    print(f"     least element  >= 2^68 = {int(B):,}")
    print("\n   (numerator K coincides with Hercher's published bound — external check)")


if __name__ == "__main__":
    main()
