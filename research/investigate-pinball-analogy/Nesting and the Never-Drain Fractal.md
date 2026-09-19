---
tags: [pinball, nesting, fractal, invariance-barrier]
status: verified-with-barrier
created: 2026-09-19
jira: SCRUM-30
---

# Nesting and the Never-Drain Fractal

Question: the machine has infinitely many parts, and big parts are made of small ones. Can the rules of composition guarantee that no machine runs forever?

Answer: the structure is provable and genuinely fractal. The guarantee itself is the Collatz conjecture, and §5–6 show that composition rules alone cannot deliver it. Code: `collatz/pinball/nesting.py`; tests in `tests/test_pinball.py`.

Labels: **Proved** (argument given here), **Verified** (computed), **Classical** (known result, not reproved), **Barrier** (a constraint on any future proof).

## 1. Nesting theorem — Proved, Verified

**Statement.** Let n > 1 be odd with stopping orbit x₁ = 3n+1, x₂, …, x_k = d < n. Then the orbit is x₁ followed by a chain of *complete* stopping orbits of values greater than n, the last of which ends exactly at d. Hence

    stopping_time(n) = 1 + Σ stopping_time(yⱼ),   y₀ = 3n+1,  yⱼ₊₁ = dest(yⱼ).

**Proof.** For 0 < i < k we have xᵢ > n (xᵢ ≥ n by definition of k, and xᵢ = n would make the orbit periodic and never drop). Take yⱼ = x_i with i < k. Since x_k < n < yⱼ, the stopping time of yⱼ is finite and its stopping orbit ends at some x_i′ with i < i′ ≤ k. If that value is below n, then i′ = k because every earlier xᵢ exceeds n. Otherwise it exceeds n and we repeat from yⱼ₊₁ = x_i′. Indices strictly increase, so the chain ends at k. ∎

**Example.** `drop_chain(27) = [(82, 1), (41, 3), (31, 91)]`: 96 = 1 + 1 + 3 + 91. The 91 decomposes again (`drop_tree`). Every stopping orbit is a finite tree whose leaves are single halvings.

**Verified** for every n in 2..5999 by rebuilding the orbit from its chain.

## 2. Termination reduces to draining — Proved

Each drop strictly lowers the value, so a chain of drops n → dest(n) → dest(dest(n)) → … is a strictly decreasing sequence of positive integers and must end. A machine can therefore run forever in only one way: **some ball never drains.** This covers both failure modes. A divergent orbit never drains; so does the minimum element of any cycle other than {1, 2, 4}.

## 3. The never-drain set is a fractal — Verified, rate Classical

Work in the 2-adic integers ℤ₂. A ball stays in play after j Terras steps iff 3^s > 2^j throughout, i.e. its bumper density stays above θ = log₃2 ≈ 0.6309. The never-drain set is the intersection over j of the undrained cylinders: a Cantor-like set, self-similar in the sense of §1.

Caveat: this is the *coefficient* condition (3^s versus 2^j), which ignores the accumulated +1 terms. It agrees with the true first drop for every n tested (`test_table_class_matches_stopping_time`, n < 5000); that the two always agree for n > 1 is itself a known open conjecture. The dimension computed below is that of the coefficient set; I have not proved here that the true never-drain set has the same dimension.

`undrained_count(j)` counts undrained words of length j (the same below-the-line lattice paths as the [[Lattice Path Formula]], counted by length instead of by bumpers). Words of bumper density θ number about 2^(H(θ)·j), so the box-counting dimension is

    H(log₃2) = 0.94996.

| depth j | log₂U(j)/j | log₂(U(2j)/U(j))/j |
|---|---|---|
| 50 | 0.8353 | 0.9241 |
| 100 | 0.8797 | 0.9371 |
| 200 | 0.9084 | 0.9432 |
| 400 | 0.9258 | 0.9464 |
| 800 | 0.9361 | 0.9481 |

Convergence is slow because of a polynomial (ballot-type) prefactor; the difference quotient is within 0.002 of 0.95 at depth 800. Dimension below 1 means measure zero: almost every 2-adic ball drains (**Classical**: Terras 1976, Everett 1977).

**3 is special here — Verified.** For qx+1 with q ≥ 5, θ = log_q 2 < 1/2, typical words already qualify, and the growth rate is 1.000 (measured at depth 200 for q = 5): a positive fraction of balls never drains. q = 3 is the only odd multiplier with a thin never-drain set. Any argument that uses the dimension 0.95 does distinguish 3x+1 from 5x+1.

## 4. Position rules — Proved, Verified

- **Multiples of 3 appear only before the first bumper.** After an odd step the value is 3x+1 ≡ 1 (mod 3), and halving preserves non-divisibility by 3. Verified for n < 5000. (This is the [[3-Adic Lock]] seen from inside the vector.)
- **Position i is fixed modulo a power of 2 by the lane.** The value at position i is (3^sᵢ·n + cᵢ)/2^eᵢ, so its residue modulo the remaining halvings is determined by the lane (see [[Pinball Model]]).
- **Cycles are necklaces.** A cycle's parity word is defined up to rotation, the members are n = C(word)/(2^E − 3^S) for each rotation, and all must be positive integers. That divisibility condition is where no-cycles arguments live; it is not settled (see `shape_of_proof_audit`).

## 5. Composition is free — Proved, Verified

**Statement.** Every 0/1 word of length L is the Terras parity word of exactly one residue class mod 2^L. In particular, every finite sequence of lanes, in any order, is played by exactly one residue class.

**Proof.** Changing bit j of n changes T^j(n) by 3^s, which is odd, so it flips the j-th parity and no earlier one. Choose bits one at a time (`realizing_residue`). ∎

Verified: 200 random concatenations of four lanes each play back exactly as prescribed, with brute-force uniqueness for moduli up to 4096.

**Consequence.** There are no forbidden arrangements of parts. Every infinite arrangement is played by exactly one 2-adic integer. "All bumpers forever" is the ball −1 (`realizing_residue((1,)*L) = 2^L − 1`). The cycles through −5 and −17 are infinite machines too. So the question "can the parts be arranged to run forever" has the answer **yes**, always, in ℤ₂. Rules about which part may follow which cannot forbid anything.

## 6. The barrier

The conjecture is therefore not a statement about composition. It is:

> The never-drain set, a specific fractal of dimension 0.95 in ℤ₂, contains no positive integer greater than 1.

The set does contain negative integers (−1, −5, −17, …) and rationals with odd denominator. Nesting (§1), the fractal (§3), the position rules (§4) and free composition (§5) hold identically for negative n. So:

**Barrier.** Any valid proof must use a property that separates positive integers from −1. Dimension counting separates 3 from 5 (§3) but not positive from negative, because a measure-zero set can still contain any particular point.

## 7. Where the fractal idea can still bite

A positive integer is a 2-adic integer whose expansion ends in infinite zeros; −1 ends in infinite ones. A never-draining ball must keep bumper density above 0.6309 forever. The question "can a finite bit string sustain that?" is the right shape: it uses positivity, and it fails for −1 as it must. This is what the repo's [[Finite Propagation Theorem]] attempts (bits consumed per bounce versus bits created by growth). The nesting theorem sharpens the target. Suppose n > 1 never drains. Its chain y₀ = 3n+1, yⱼ₊₁ = dest(yⱼ) is strictly decreasing and bounded below by n, so it is finite. It can end in only two ways:

- it lands exactly on n — a **cycle** with minimum n; or
- it reaches some y_J > n that itself never drains.

**Corollary (Proved).** A never-draining ball that is not the minimum of a cycle has, in its own orbit, a strictly larger never-draining ball. A divergent orbit therefore contains an infinite strictly increasing sequence m₀ < m₁ < m₂ < … of never-draining integers, each reached from the last through finitely many complete drops.

So divergence needs infinitely many positive integers in a set of dimension 0.95, linked by the orbit. Showing that the link forces more trailing structure than a finite bit string can supply is a precise target. It is open.
