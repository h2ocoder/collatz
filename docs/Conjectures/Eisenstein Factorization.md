# Eisenstein Factorization of the Collatz Map

**Status:** Proved (algebraic identity + structural analysis)

## Statement

The Collatz Syracuse step $S(n) = (3n+1)/2^{\alpha}$ factors naturally in the Eisenstein integers $\mathbb{Z}[\omega]$ where $\omega = e^{2\pi i/3}$:

$$3n + 1 = \pi \cdot \bar{\pi} \cdot n + 1$$

where $\pi = 1 - \omega$ and $\bar{\pi} = 1 - \omega^2$ are the conjugate Eisenstein primes above 3.

This decomposition separates the Collatz dynamics into two **decoupled** components:

1. **Angular** (phase): deterministic, period 12
2. **Radial** (magnitude): governed by the alpha sequence, determines convergence

## The Eisenstein Primes Above 3

In the Eisenstein integers $\mathbb{Z}[\omega]$, the prime 3 **ramifies**:

$$3 = -\omega^2 \cdot (1-\omega)^2 = \pi \cdot \bar{\pi}$$

| Element | Magnitude | Angle | Role in Collatz |
|---------|-----------|-------|-----------------|
| $\pi = 1-\omega$ | $\sqrt{3}$ | $-30°$ | Half of $\times 3$ growth |
| $\bar{\pi} = 1-\omega^2$ | $\sqrt{3}$ | $+30°$ | Other half of $\times 3$ growth |
| $\pi \cdot \bar{\pi} = 3$ | $3$ | $0°$ | Full $\times 3$ (pure scaling) |
| $2$ (inert) | $2$ | $0°$ | Halving (pure contraction) |

The key asymmetry: $3$ splits into two factors with **opposite rotations**, while $2$ remains inert (no rotation). The Collatz map interleaves these two algebraically different operations.

## The Period-12 Angular Dynamics

After $s$ Syracuse steps, the cumulative Eisenstein phase is:

$$\text{phase}(\pi^s) = -s \times 30° \pmod{360°}$$

This cycles through all 12 half-sectors with **period 12**, independent of the alpha values:

| $s \bmod 12$ | Phase | Sector | Dropping set example |
|---|---|---|---|
| 0 | $0°$ | 0a | (identity) |
| 1 | $330°$ | 5b | $\text{Dset}_3$ |
| 2 | $300°$ | 5a | $\text{Dset}_6$ |
| 3 | $270°$ | 4b | $\text{Dset}_8$ |
| 4 | $240°$ | 4a | $\text{Dset}_{11}$ |
| 5 | $210°$ | 3b | $\text{Dset}_{13}$ |
| 6 | $180°$ | 3a | $\text{Dset}_{16}$ |
| 7 | $150°$ | 2b | $\text{Dset}_{19}$ |
| 8 | $120°$ | 2a | $\text{Dset}_{21}$ |
| 9 | $90°$ | 1b | $\text{Dset}_{24}$ |
| 10 | $60°$ | 1a | $\text{Dset}_{26}$ |
| 11 | $30°$ | 0b | $\text{Dset}_{29}$ |

**Every orbit must visit all 6 Eisenstein sectors** (and both half-sectors) before the angular phase repeats. This is forced by the algebra — no orbit can skip a sector.

## The Radial Dynamics

The magnitude after $s$ Syracuse steps with total halvings $h = \sum \alpha_i$:

$$\left|\frac{\pi^s \cdot \bar{\pi}^s}{2^h}\right| = \frac{3^s}{2^h}$$

This is the **contraction ratio** — the slope from [[Affine Orbit Structure]]. Convergence requires this to be $< 1$ on average, which is equivalent to $h/s > \log_2 3 \approx 1.585$.

The radial and angular dynamics are **decoupled**: the angle depends only on $s \bmod 12$, while the magnitude depends on the specific alpha sequence. The angle is deterministic; only the magnitude is "random."

## The Eisenstein Norm and Loeschian Numbers

For each Collatz pair $(n, \text{dest})$, the Eisenstein integer $z = n + \text{dest} \cdot \omega$ has norm:

$$N(z) = n^2 - n \cdot \text{dest} + \text{dest}^2$$

These norms are **Loeschian numbers** — representable as $x^2 + xy + y^2$. A number is Loeschian if and only if every prime $p \equiv 2 \pmod{3}$ appears to an even power in its factorization.

**Verified:** All Collatz pairs $(n, \text{dest})$ for odd $n < 500$ produce Loeschian Eisenstein norms. Zero violations.

## Dropping Sets on the Eisenstein Unit Circle

Each dropping set $\text{Dset}_k$ (with $s$ Syracuse steps and slope $3^s/2^{k-s}$) maps to an angle on the Eisenstein unit circle:

$$\theta(s) = \arg(1 + \text{slope} \cdot \omega)$$

The slope is $2^{-\{s \cdot \log_2 3\}}$ where $\{x\}$ denotes the fractional part. So the angle is determined by the fractional part of $s \cdot \log_2 3$ — the same equidistribution sequence that governs the [[Lattice Path Formula]], the 44-step quasi-period, and the near-conjugacy rotation number.

The angles span the arc $[30°, 60°]$ — exactly half of one Eisenstein sector — and the sequence $\theta(1), \theta(2), \theta(3), \ldots$ traces a **quasi-periodic orbit**, equidistributed by Weyl's theorem.

## The Period 12 and Diophantine Approximation

The period 12 of the angular dynamics connects to the best rational approximation of $\log_2 3$:

$$\frac{19}{12} \approx \log_2 3 = 1.58496\ldots \qquad \text{gap} = 0.0196$$

After 12 Syracuse steps with near-average halvings:

$$\frac{3^{12}}{2^{19}} = \frac{531441}{524288} = 1.01364\ldots$$

The Eisenstein period (12 steps to complete one full rotation) and the Diophantine near-miss ($3^{12} \approx 2^{19}$) are manifestations of the same arithmetic.

## Why Eisenstein, Not Gaussian

| Property | Gaussian $\mathbb{Z}[i]$ | Eisenstein $\mathbb{Z}[\omega]$ |
|----------|--------------------------|--------------------------------|
| Symmetry | 4-fold | **6-fold** (matches $\text{rad}(6)$) |
| 3 | stays prime | **ramifies** as $\pi \cdot \bar{\pi}$ |
| 2 | ramifies as $-i(1+i)^2$ | **stays inert** |
| Norm | $a^2 + b^2$ (Pythagorean) | $a^2 - ab + b^2$ (Loeschian) |
| Rotation per step | no natural angle | **exactly $-30°$** |

The Gaussian picture (Paper 1) encodes Collatz pairs as Pythagorean triples but treats 3 as opaque. The Eisenstein picture *cracks open* the $\times 3$ into its two conjugate factors, revealing the hidden rotational dynamics.

## Connection to the Discrete Denjoy Bridge

The Denjoy approach requires showing that the Collatz map, viewed as a perturbed irrational rotation, has dense orbits. The Eisenstein factorization provides concrete structure:

1. The **angular** component is an exact $-30°$ rotation (period 12) — not approximate
2. The **radial** component is governed by the fractional parts $\{s \cdot \log_2 3\}$ — equidistributed by Weyl
3. Combined: the orbit traces a **quasi-periodic spiral** in the Eisenstein plane, visiting all sectors and contracting on average

The discrete Denjoy theorem, if proved, would operate on this Eisenstein spiral rather than on the integers directly.

## Connections

- Factors the slope from [[Affine Orbit Structure]] into angular and radial components
- The angular period 12 connects to the Diophantine approximation in [[Lattice Path Formula]]
- The Loeschian norm condition constrains prime factors, connecting to the 3-adic lock in [[Affine Orbit Structure]]
- Provides geometric foundation for the [[Collatz Complementarity Principle]]
- The 6-fold symmetry explains why $\text{rad}(6) = 6$ appears throughout the theory
- Replaces the Pythagorean triple mapping from Paper 1 with a structure that treats $3$ and $2$ asymmetrically, matching their roles in the Collatz map
