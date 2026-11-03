---
tags: [schwarzschild, generalized-collatz, phase-diagram]
status: verified
created: 2026-11-02
jira: SCRUM-65
---

# Collatz-like Maps in General

What the dictionary says about T(n) = (q_r n + a_r)/d with gcd(q_r, d) = 1, the family studied by Möller, Matthews–Watts, and Kontorovich–Sinai (who prove a Brownian limit with drift for (d,g,h)-maps). `collatz/zoo.py` measures some of the same quantities empirically. `collatz/schwarzschild/` computes them exactly from (q, a, d).

## 1. Five phases — Proved (the definitions and boundaries)

| phase | condition | what happens | example |
|---|---|---|---|
| interior | every q_r < d | With offsets ≥ 0, every orbit falls into a hard horizon. A theorem. | (n+1)/2, (1,2,2)/3 |
| thin | g > 0, θ > 1 | E[T(n)] contracts. | (1,2,4)/3, (1,2,5)/3 |
| critical | θ = 1, Σ q_r = d² | n is a martingale up to offsets. | **3x+1**, (1,4,4)/3 |
| heavy | g > 0, θ < 1 | Typical orbits fall, but E[T(n)] grows. | (1,4,5)/3, (1,5,5)/3 |
| outflow | g ≤ 0 | Typical orbits rise. | 5x+1, 7x+1 |

Three critical lines separate them:

- **q_max = d**: the fastest outgoing word stands still, Mach 1 for two branches.
- **Σ q_r = d²**: the mean is conserved, θ = 1.
- **E[log q_r] = log d**: the typical flow stops, g = 0. For d = 2 this is q = 4.

## 2. Hard horizons exist below q = d — Proved

If every q_r < d and every a_r ≥ 0 then T(n) < n on every branch for n > a_r/(d − q_r). So

    r_s = max_r a_r / (d − q_r)

is a true trapping radius, with no statistics, and all orbits enter [0, r_s]. Each branch's bound is the literal definition, the place where the fastest outgoing motion stops, and it has the form M/(d − q). The same formula applied to a composite word gives F(w) = C/(d^k − Q), so the word horizon is this radius for the word's restricted system.

Negative offsets break the interval: d = 3, q = (1,2,2), a = (0,−5,−1) sends 1 to −1. Above q = d no hard horizon exists, and only the information budget remains.

## 3. The first non-trivial map of every base is exactly critical — Proved

Take q₀ = 1 and one multiplier q on all other residues. Then Σ q_r = 1 + (d − 1) q, and θ > 1 would need q < d + 1. But q ≠ d by coprimality, so q < d is interior, and **q = d + 1 is the first map above the hard horizon and it has θ = 1 exactly.** There is no thin uniform map.

So the jump from "provably falls" to "martingale" happens in one integer step, in every base. 3x+1 is the case d = 2. E8 confirms this for d = 2 to 8. Thin maps exist only with mixed multipliers.

## 4. Family results — Verified, with misses

Twelve maps, exhaustive over all n up to the stated bits (E4). The fitted slope uses −log₂ survival in the top block, for thresholds with at least 30 integers. The cut-off is the lift at which the block expects one integer, (B − 1 + log₂ L)/θ.

| map | bits | θ | fitted slope | max lift | cut-off | reach | predicted |
|---|---|---|---|---|---|---|---|
| 3x+1 | 26 | 1 | 0.986 | 22.55 | 24.73 | 1.895 | 2 |
| (1,4,4)/3 | 24 | 1 | 1.015 | 25.96 | 22.79 | 2.118 | 2 |
| (1,1,7)/3 | 24 | 1 | 0.941 | 21.68 | 22.38 | 1.913 | 2 |
| (1,3,5,7)/4 | 24 | 1 | 0.999 | 22.19 | 22.68 | 1.955 | 2 |
| (1,5,5,5)/4 | 24 | 1 | 0.994 | 22.70 | 22.85 | 1.948 | 2 |
| (1,6,6,6,6)/5 | 24 | 1 | 1.016 | 20.61 | 22.86 | 1.891 | 2 |
| (1,2,4)/3 | 24 | 3.499 | 3.512 | 6.23 | 6.34 | 1.262 | 1.286 |
| (1,2,5)/3 | 24 | 1.652 | 1.634 | 12.86 | 13.61 | 1.547 | 1.605 |
| (1,4,4,6,6)/5 | 24 | 4.056 | 4.113 | 6.25 | 5.55 | 1.270 | 1.247 |
| (1,2,7)/3 | 23 | 0.662 | 0.661 | 30.30 | 32.72 | 2.342 | 2.511 |
| (1,4,5)/3 | 22 | 0.427 | 0.435 | 40.09 | 48.88 | 2.893 | 3.342 |
| (1,5,5)/3 | 17 | 0.091 | **0.125** | 179.8 | 176.2 | 11.97 | 12.03 |

![[figures/family.png]]

The fitted slope is within 2% on ten maps, with θ from 0.43 to 4.06, and within 6% on eleven. The max lift lands within 3.7 bits of the cut-off on eleven maps. The cut-off is a statistical edge, and single orbits can pass it.

**Misses, reported as misses:**

- **(1,5,5)/3 slope is 38% high.** This map is near critical and only 17 bits were reachable. Its survival runs at 0.06 to 0.82 of the Haar law. The reach and cut-off still agree.
- **(1,4,5)/3 falls 8.8 bits short of the cut-off**, about three fluctuation widths. Its reach of 2.89 is well under 3.34 at 22 bits. It has several cycles, and I did not separate absorption by cycles from finite size.
- **(1,4,4)/3 overshoots the cut-off by 3.2 bits**, from a single extreme n.
- **Survival ratios spread near the cut-off.** Measured over Haar runs 0.91 to 1.43 for 3x+1 and from 0.44 to 3.02 across the other well-sampled maps, at thresholds with at least 30 integers.

## 5. Lifetimes — Verified, weaker

Steps per bit, measured in the top block against the budget predictions:

| map | mean life | 1/g | longest life | fall bound | longest first drop | hover bound |
|---|---|---|---|---|---|---|
| 3x+1 | 4.76 | 4.82 | 22.8 | 28.9 | 14.5 | 20.0 |
| (1,4,4)/3 | 3.42 | 3.97 | 16.4 | 25.5 | 10.5 | 17.9 |
| (1,1,7)/3 | 1.50 | 1.54 | 6.2 | 9.0 | 4.3 | 6.2 |
| (1,3,5,7)/4 | 2.37 | 3.11 | 11.5 | 19.9 | 8.1 | 14.0 |
| (1,5,5,5)/4 | 3.50 | 3.87 | 16.3 | 26.1 | 10.4 | 18.5 |
| (1,6,6,6,6)/5 | 4.53 | 3.94 | 21.4 | 27.5 | 11.9 | 19.6 |
| (1,2,4)/3 | 1.54 | 1.71 | 4.3 | 5.5 | 1.5 | 2.5 |
| (1,2,5)/3 | 1.90 | 2.09 | 6.7 | 9.2 | 3.3 | 5.5 |
| (1,4,4,6,6)/5 | 1.74 | 2.05 | 5.9 | 7.8 | 2.7 | 3.7 |
| (1,2,7)/3 | 3.07 | 3.17 | 17.6 | 25.0 | 9.6 | 19.1 |
| (1,4,5)/3 | 4.74 | 6.93 | 47.5 | 81.3 | 42.3 | 67.8 |
| (1,5,5)/3 | 17.4 | 27.0 | 480 | 1256 | 473 | 1203 |

Every extreme stays under its bound, as a first-moment bound should at this size. The mean life matches 1/g for 3x+1 and falls short by up to 36% elsewhere. Life here stops at the first repeated value, so maps with many cycles stop early, and (1,6,6,6,6)/5 runs 15% over. I did not model either effect.

## 6. Cycles and captures — Proved and Verified

- **Sign rule.** For offsets ≥ 0 every positive cycle uses a contracting word, and for negative offsets it uses an expanding word.
- **Mass-radius relation.** For a map scaled by m, captured integers grow at least as Σ m, with Σ the map's Haar mean horizon. That lower bound is proved. The matching upper side is measured only ([[Word Horizons]] §8).
- **Near-critical gaps set the cycle size.** 5x+1 has its cycles at 13 and 17 because 2⁷ − 5³ = 3 is small, so F = C/3 is large.

## Related

[[The Schwarzschild Dictionary]] · [[Word Horizons]] · [[Information Radius]] · [[Toy Physics Systems]]
