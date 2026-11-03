---
tags: [schwarzschild, dictionary, information-theory]
status: complete
created: 2026-11-02
jira: SCRUM-65
---

# The Schwarzschild Dictionary

The question: what is the information-theoretic version of r_s = 2GM/c², and what do radius, mass, gravity and the speed of light correspond to?

The short answer: **the Schwarzschild radius is the address depth needed to carry a given lift.** It has two faces, one in the 2-adic address of a number and one in its value, and they share the exponent θ.

Labels used across the vault: **Proved** (argument given), **Classical** (known result, not reproved), **Verified** (computed), **Heuristic** (a counting model, not a theorem), **Analogy** (a resemblance only), **Barrier** (a constraint on any proof).

All constants below are for the Terras form of the classic map: n/2 on even n, (3n+1)/2 on odd n. A step means one Terras step. Code: `collatz/schwarzschild/`.

## Start from the definition

In general relativity r_s is the radius where escape speed equals the speed of light. The Newtonian form of that sentence is

    ½ c² = G M / r    so    r_s = 2 G M / c²

Three things need translating: what motion is, what the speed limit is, and what escaping costs.

**Motion.** Size in bits, x = log₂ n, moves by log₂(3/2) = +0.585 on a kick and by −1 on a halving. A map has no momentum, so every step is its own velocity.

**The speed limit.** Every step reads exactly one binary digit of the starting number, on either branch. No digit above position t can affect the first t steps. This is the Terras bijection, and it makes a true causal cone with c = 1 bit per step ([[Information Radius]] §1).

**The cost of escaping.** A number only rises if its digits say so. Rising M bits above the start is a property of the low bits, and the set of 2-adic integers that do it has Haar measure about 2^(−θM). So height is paid for in address bits, at a price of θ bits per bit. For 3x+1 the price is exactly 1, because (3/2)¹ + (1/2)¹ = 2.

Now the definition translates directly. A B-bit integer owns B address bits and then zeros, so B is its fuel. Lifting M bits costs r_s(M) = θM + O(1) bits. Counting candidates then gives:

    among B-bit integers, the largest lift is near the M with r_s(M) = B

That has the same shape as the statement that an object of mass M cannot be smaller than r_s(M). The horizon is compactness 1, r_s(M)/B = 1. For 3x+1 it says peak(n) ≈ n², which is the Lagarias–Weiss constant 2.

**This is a first-moment count, not an implication.** Individual integers can beat it, and small ones do: n = 27 has B = 4.75 and a lift of 7.42 bits, which costs about 7.7 address bits. Kontorovich and Lagarias list n = 27, 31, 41, 47, 55 and 63 as the only odd seeds up to 1,042,431 with exponent above 2, and larger seeds such as 319,804,831 exceed it by a small margin. The claim is about how the largest lift scales with B.

## The dictionary

| Schwarzschild | Information version | Definition | 3x+1 | Status |
|---|---|---|---|---|
| **Speed of light** c | Head speed: address digits read per step, the same on every branch | log₂ d | 1 bit/step | **Proved** |
| Local light speed | Fastest motion relative to the mean flow | σ, half the gap between the two speeds | ½ log₂ 3 = 0.7925 bits/step | **Proved** (two branches) |
| **Gravity** G | Drift: size lost per step, independent of n | g = log₂ d − E[log₂ q_r] | 1 − ½ log₂ 3 = 0.2075 bits/step | Exact under Haar |
| Memory | Bits written into residues mod q per step | m = E[log₂ q_r] | 0.7925 bits/step | Exact under Haar |
| **Mass**, address face | Lift: bits of size an orbit climbs above its start | M = log₂(peak/n) | | Definition |
| **Mass**, value face | The additive constant, summed along a word | ζ(w) = C/Q, proportional to a | ζ ≤ s/3 on a first-contraction word | **Proved** |
| **Radius**, address face | Depth of a 2-adic set | −log₂ of Haar measure | | Definition |
| **Radius**, value face | The value itself | n | | Definition |
| **Schwarzschild radius**, address face | Address depth that can carry lift M | r_s(M) = −log₂ μ(lift ≥ M) = θM + ρ₀ | θ = 1, ρ₀ = 0.27 | **Classical** (Cramér–Lundberg) |
| Weak-field formula | Gaussian limit of the above | 2GM/c² with G = g, c = σ, in nats of address | 0.953 against the exact 1 | **Proved** (as g → 0) |
| **Schwarzschild radius**, value face | Fixed point of a parity word | F(w) = C/(d^k − Q) | F(10) = 1, the trivial cycle | **Proved** |
| Mean radius per unit mass | Haar mean horizon, the stand-in for 2G/c² | Σ = E[F] at the first contraction | Σ = 1.8137 | **Proved** (converges, using Baker-type bounds on β) |
| Metric factor 1 − r_s/r | Lapse of a word | 1 − A(n)/n = (1 − 2^−β)(1 − F/n) | | **Proved** |
| Ingoing null ray | A word is its time-1 map, r = log₂ n | dr/dt = −β (1 − F/n) | speed β at infinity | **Proved** |
| Bits destroyed | The denominator of the value-face radius | F = ζ/(2^β − 1) | β(5) = 0.075 gives F ≈ 20 | **Proved** |
| Horizon | Compactness 1: B = r_s(M) | | peak ≈ n² | **Heuristic** |
| Equivalence principle | Every n falls at the same rate | g does not depend on n | | Exact under Haar |

## The bridge between the two faces

The two faces are one object seen from two places. For a Haar-typical long word, the value-space horizon F has a Kesten–Goldie tail

    μ(F > t) ~ C t^(−θ)

with the same θ. Rewriting with t = 2^M: **a value-space horizon of M bits costs θM bits of address.** For 3x+1 one bit of real radius costs exactly one bit of 2-adic radius, and the tail constant has a closed form, C = 1/ln(27/16) = 1.9111. The functional equation confirms it to five digits ([[Information Radius]] §6).

## Bit destruction

This is where the ideation about bit destruction lands. The identity

    F(w) = ζ(w) / (2^β(w) − 1)

puts the bits destroyed in the denominator of the radius, exactly where c² sits. In the weak field it reads F ≈ ζ/(β ln 2), which has the form r = (mass)/(c²/2G). A slow set, one with small β(s), is a word with a large horizon. The largest horizons come from the upper semi-convergents of log₂ 3 ([[Word Horizons]] §6). Bits destroyed are also the speed of the word's null ray ([[Word Horizons]] §2).

## A second reading of the same law

Take M = log₂ n instead. The orbit of an M-bit number stays inside radius (1 + 1/θ)M, so for 3x+1 r = 2M. That is the Schwarzschild formula in geometrized units with G = c = 1.

It is a pleasant coincidence and I would not lean on it. In this reading a stronger drift gives a smaller radius, which is the wrong direction for G, and "G = 1" is only the statement θ = 1. The address-face reading has the right dependence on all three quantities: more drift gives a larger r_s, more spread gives a smaller one, and more mass gives a larger one.

## Where the analogy breaks

These are real limits, not footnotes.

1. **There is no inertia.** Collatz dynamics are first order, so g is a velocity, not an acceleration. The square and the factor 2 in 2GM/c² do not come from kinetic energy here. They come from diffusion: a drifted random walk has first-passage exponent 2|μ|/σ². The form matches, and the mechanism is different.
2. **There is no hard horizon for q > d.** Nothing forbids an orbit from climbing past its budget. Past step B an integer's digits are zeros, not coin flips, so the price list is a first-moment heuristic. Only maps with every q_r < d have a true trapping radius ([[Collatz-like Maps in General]] §2).
3. **The +1 pushes outward.** In value space the offset lifts n, and the drain pulls it down. F is attracting from both sides under its own word. That matches Schwarzschild-coordinate null rays, dr/dt = −c f(r), which also stall at the horizon, but nothing falls through.
4. **Mass means two things.** On the address face it is lift. On the value face it is the offset. The bridge above relates them, but they are not the same quantity.
5. **The 4D scalings fail.** Entropy is linear in size, not quadratic, and the emission law does not depend on size. The system belongs with two-dimensional dilaton gravity, not Schwarzschild ([[Toy Physics Systems]] §1).
6. **Temperature is a convention.** Haar measure makes a state of E bits have probability 2^(−E), which is a Boltzmann law at T = 1/ln 2 by definition. There is no physics in that number.
7. **It is classical.** There is no phase, no entanglement and no unitarity, in line with the repo's earlier CHSH result.

## Earlier tables

`docs/Conjectures/Finite Propagation Theorem.md` and `site/journey/the-picture.md` assign "speed of light" to a carry speed of about 1.58 or 1.92 bits per bounce and "Hawking radiation" to bounce growth. Those rest on the unproved Finite Propagation Theorem and on averages. The head speed here is a different quantity and is exact. Those tables are left unchanged, because rewriting them is out of scope, but this dictionary should replace them if the site is revisited.

## Related

[[00 Index]] · [[Word Horizons]] · [[Information Radius]] · [[Collatz-like Maps in General]] · [[Toy Physics Systems]] · [[Audit]]
