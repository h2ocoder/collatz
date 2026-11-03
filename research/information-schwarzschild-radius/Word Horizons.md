---
tags: [schwarzschild, horizon, bit-destruction, coefficient-stopping]
status: verified
created: 2026-11-02
jira: SCRUM-65
---

# Word Horizons

The value-space face of the dictionary. Code: `collatz/schwarzschild/horizon.py`. Experiments: E2, E7, E9, E10, E11 in `scripts/schwarzschild_experiments.py`.

Setup: T(n) = (q_r n + a_r)/d on n ≡ r mod d. A word w of length k acts as

    A(n) = (Q n + C) / d^k,    a = Q/d^k,    b = C/d^k

Its **horizon** is the fixed point

    F(w) = C / (d^k − Q) = b / (1 − a)

**Bits destroyed** are β(w) = k log₂ d − log₂ Q, so a = 2^(−β). **Word mass** is ζ(w) = C/Q.

Two examples for the classic map. Word 10 is (3n+1)/4, with F = 1, the trivial cycle. Word 1 is (3n+1)/2, with F = −1, the cycle at −1.

## 1. The lapse identity — Proved, Verified

    1 − A(n)/n = (1 − 2^(−β)) (1 − F/n)

**Proof.** A(n)/n = a + b/n, so 1 − A(n)/n = (1 − a) − b/n = (1 − a)(1 − b/((1−a)n)). ∎

The right-hand factor is the same function as the Schwarzschild 1 − r_s/r. It is positive outside the horizon, zero on it, and negative inside. Tested for every word up to length 5 across nine maps, in exact fractions.

## 2. Infall — Proved, Verified

    A(n) − F = 2^(−β) (n − F)

An orbit falls onto the horizon of its own word, exponentially in the bits destroyed. Example: n = 27 has first contraction word with k = 59, s = 37, β = 0.356, F = 8.73, and 8.73 + 0.781 × 18.27 = 23, its first value below 27.

For a contracting word this gives **A(n) < n ⟺ n > F**. A drop is being outside the horizon.

**The word is a null ray — Proved, Verified.** Interpolate by n(t) − F = 2^(−βt)(n − F). With r = log₂ n this is exactly

    dr/dt = −β (1 − F/n)

so A is the time-1 map of an ingoing null ray with metric function f = 1 − F/n and speed β at infinity. **Bits destroyed are the speed of the ray.**

## 3. One centre, two places — Proved, Verified

F(w) is a rational with denominator prime to d, so it is also a d-adic integer. Word w is realized exactly on the class Q x + C ≡ 0 mod d^k, and F satisfies that congruence because F d^k = Q F + C. So:

- **d-adically**, the class of w is the ball of radius d^(−k) around F(w).
- **In the reals**, word w drops exactly on the half-line above F(w).

A dropping set is a 2-adic ball intersected with a real half-line, and both are centred on the same rational.

## 4. Cycles sit on the horizon — Classical, Verified

n is periodic with word w ⟺ n = F(w) and n realizes w. This is the Böhm–Sontacchi cycle equation (1978) rewritten. Every cycle found by E9, 60 of them across 19 maps, sits exactly on its horizon.

**Sign rule — Proved.** With a > 0, a positive horizon needs d^k > Q, so positive cycles use contracting words. With a < 0 it needs d^k < Q, so positive cycles use expanding words. E9 confirms it: 3x+1, 5x+1 and 3x+5 use contracting words, and 3x−1 uses expanding words for 1, 5 and 17.

## 5. The offset is the mass — Proved, Verified

- **Linear.** F is linear in the offsets. For 3x+a, F_a(w) = a F₁(w). The general form is `CollatzLike.scaled(m)`.
- **Sign.** a → −a flips the horizon, F₋₁(w) = −F₁(w). That is the 3x−1 mirror.
- **It cannot be switched off.** Integrality forces q_r r + a_r ≡ 0 mod d, so a_r ≠ 0 on every unit residue. The +1 is the carry that keeps the orbit integral.
- **Exact value.** Along an orbit with odd values n_i, 1 + ζ/n = Π (1 + 1/(3 n_i)). Each kick at value n contributes log₂(1 + 1/(3n)) ≈ 0.481/n bits, a 1/r potential.
- **Radius.** F = ζ/(2^β − 1), which in the weak field is F ≈ ζ/(β ln 2).

The scaling is Lagarias's correspondence (1990) between cycles of 3x+k and rational cycles of 3x+1 with denominator k.

## 6. Bit destruction sets the horizon — Proved, Verified

On a first-contraction word with s kicks, β is the repo's β(s) = ⌈s log₂ 3⌉ − s log₂ 3. Before digit t the word has not contracted, so Q_t ≥ d^t, and the t-th term of ζ is at most a_r/q_r. For the classic map:

    ζ(w) ≤ s/3    and    F(w) ≤ s 3^(s−1) / (2^k − 3^s)

All first-contraction words by kick count, exact (E2):

| s | Set_k | subgroups | β(s) | F min | F mean | F max | bound |
|---|---|---|---|---|---|---|---|
| 1 | 3 | 1 | 0.415 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | 6 | 1 | 0.830 | 0.71 | 0.71 | 0.71 | 0.86 |
| 3 | 8 | 2 | 0.245 | 3.80 | 4.20 | 4.60 | 5.40 |
| 4 | 11 | 3 | 0.660 | 1.38 | 1.58 | 1.81 | 2.30 |
| **5** | **13** | **7** | **0.075** | **16.2** | **20.2** | **24.5** | **31.2** |
| 6 | 16 | 12 | 0.490 | 2.25 | 2.90 | 3.68 | 4.94 |
| 7 | 19 | 30 | 0.905 | 1.08 | 1.48 | 1.97 | 2.67 |
| 8 | 21 | 85 | 0.320 | 3.87 | 5.82 | 8.18 | 10.7 |
| 9 | 24 | 173 | 0.735 | 1.47 | 2.28 | 3.37 | 4.51 |
| 10 | 26 | 476 | 0.150 | 8.95 | 14.9 | 22.9 | 30.3 |

The slow sets s = 5 and s = 10 have the biggest horizons here. Further out, the bound sets records at s = 5, 17, 29, 41, 94, 147, 200, 253, 306, which are the upper semi-convergents of log₂ 3. Subgroup counts reproduce OEIS A100982.

## 7. Terras's conjecture is a statement about horizons — Classical, restated

Let w be n's first contraction word, the shortest prefix with Q < d^k. Its length is Terras's coefficient stopping time τ(n). Call n **captured** if n ≤ F(w), and define **compactness** C(n) = F(w)/n, the analogue of r_s/R.

**The Coefficient Stopping Time Conjecture** (Terras 1976, Conjecture 2.9; named by Lagarias 1985) says τ(n) = σ(n) for all n ≥ 2. By §2 this is exactly:

    no integer n ≥ 2 lies on or inside the horizon of its first contraction word

Compactness over all n < 2²² (E10):

| n | C(n) | k | s | F |
|---|---|---|---|---|
| 47 | 0.7134 | 54 | 34 | 33.53 |
| 63 | 0.5723 | 54 | 34 | 36.06 |
| 39 | 0.4951 | 8 | 5 | 19.31 |
| 11 | 0.4182 | 5 | 3 | 4.60 |
| 27 | 0.3232 | 59 | 37 | 8.73 |

So **47 is the most compact integer found.** Horizons stay small while n grows, so the largest compactness in a bit size falls quickly, from 0.0033 at 18 bits to 0.00025 at 22 bits.

### A finite certificate — Proved given the computation

Any failure at n with s kicks needs n ≤ F(w) ≤ s 3^(s−1)/(2^k − 3^s). So if every n up to N passes, then no integer of any size fails with any s whose bound is at most N.

E7 checked every n < 2³⁰ and found no failure. `certified_kicks` then gives:

    no integer n ≥ 2 fails the conjecture with s ≤ 47,467 kicks

The next bound is 1.45 × 10⁹, just above 2³⁰. The arithmetic is exact. The certificate is elementary and may well be folklore. It does not prove the conjecture, because nothing bounds s.

## 8. The capture law — lower bound Proved, constant Verified

This is the most direct test of "the offset is mass". Define

    Σ = Σ_w F₁(w) / 2^|w|    over first-contraction words w of 3x+1

This is the Haar mean of F at first contraction. It converges fast, since the measure of words with s kicks decays exponentially, and it can be computed exactly because C is additive over lattice cells (`contraction_sums`):

    Σ = 1.8136703301

**Theorem.** liminf over odd a of #{captured n of 3x+a}/a ≥ Σ.

**Proof.** n realizes w in 3x+a exactly when n ≡ a r mod 2^k, where r is w's class for a = 1, and F_a(w) = a F₁(w). So w captures a F₁(w)/2^k + O(1) integers. Distinct words capture distinct integers. Fix a finite set of words, let a → ∞, then enlarge the set. ∎

The same proof gives the same bound for any map scaled by m coprime to d, with the map's own Σ.

The upper side is open, because the O(1) errors over long words are not controlled. It is measured instead, over all 701 odd a up to 1401:

| a | maps | captured / a | genuine / a | periodic / a | orbit minima / a |
|---|---|---|---|---|---|
| 1–23 | 12 | 2.060 ± 0.608 | 1.105 | 0.488 | 0.467 |
| 25–73 | 25 | 1.917 ± 0.216 | 1.447 | 0.193 | 0.277 |
| 75–199 | 63 | 1.849 ± 0.109 | 1.572 | 0.137 | 0.141 |
| 201–499 | 150 | 1.827 ± 0.061 | 1.643 | 0.094 | 0.089 |
| 501–999 | 250 | 1.821 ± 0.028 | 1.704 | 0.063 | 0.054 |
| 1001–1401 | 201 | 1.817 ± 0.029 | 1.716 | 0.056 | 0.045 |

![[figures/capture.png]]

The count of captured integers is linear in the mass, with constant Σ to within 0.2% in the top band. In form it is r̄_s = Σ M.

Three kinds of captured integer appear. **Genuine** failures are not periodic and later drop below n, so they break the 3x+a version of the conjecture. **Periodic** ones are on a cycle, and those that are not the cycle's minimum also drop below themselves. **Orbit minima** never drop, because they enter a cycle above themselves, as n = 5 does in 5x+1. The stronger guess "captured ⟺ minimum of its own orbit" is **false**: 3x+7 has n = 3, captured and then dropping.

Periodic and orbit-minimum captures shrink as a share of a, so about 94% of the captures in the top band are genuine.

**The result to take away: every odd a from 3 to 1401 has genuine failures, at least 3 of them. For a = 1 none is known:** there is none for n < 2³⁰ and none with s ≤ 47,467. That is what the count expects, because genuine failures run near 1.7 a. Terras's conjecture looks like a low-mass property of 3x+1 and not a structural one.

The count also supplies a warning. For a = 1 the same reasoning, restricted to whole numbers, gives an expected 1.14 captured integers n ≥ 3 (E11), and none is known. In a Poisson model that is a 32% event. This is the expected-count **Barrier**: the first moment is accurate across masses and says nothing about one mass.

The same law holds for three scaled maps, up to the scan limit at n = 1500 m. Rare horizons above that limit are out of the count's reach, so compare with E[min(F, 1500)]:

| map | Σ exact | E[min(F, 1500)], sampled | captured / m, m ≈ 101 to 1201 |
|---|---|---|---|
| (1,4,4)/3 | 2.3620 | 2.268 ± 0.006 | 2.287, 2.272, 2.327, 2.317, 2.309 |
| (1,2,5)/3 | 1.4942 | 1.493 ± 0.003 | 1.406, 1.455, 1.541, 1.535, 1.475 |
| (1,3,5,7)/4 | 3.8396 | 3.757 ± 0.007 | 3.921, 3.791, 3.805, 3.750, 3.728 |

## Related

[[The Schwarzschild Dictionary]] · [[Information Radius]] · docs: `Bit Destruction Bound`, `Affine Orbit Structure`, `Stopping Point Line Conjecture`
