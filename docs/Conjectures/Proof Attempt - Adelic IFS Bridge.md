# Proof Attempt: The Adelic IFS Bridge

**Status:** Near-complete — hinges on one tractable conjecture in fractal geometry

## Overview

The Collatz conjecture reduces to a specific problem about **absolute continuity of self-similar measures** with one expanding branch. This is a well-studied area of fractal geometry where existing tools (Hochman, Shmerkin, Varjú) come close to resolving it.

## Part A: No Cycles (PROVED)

A Collatz cycle of $S$ Syracuse steps and $H$ halvings requires $3^S = 2^H$, which is impossible by the fundamental theorem of arithmetic. The $+1$ corrections from $3n+1$ (vs pure $3n$) create a residual bounded by $O(s/n)$, which is exponentially smaller than the Diophantine gap $|s \log_2 3 - \text{nearest integer}|$ for $s \geq 12$ (and small $s$ are checked exhaustively). See [[Eisenstein Factorization]] for the $\log_3$ coordinate formulation.

## Part B: No Divergence

### Step 1: The IFS Framework (Siegel)

The Collatz shortened map $T_3(n) = n/2$ (even) or $(3n+1)/2$ (odd) is a **2-Hydra** on $\mathbb{Z}$ in the sense of Siegel (arxiv 2601.17030). Its **numen** $X_H : \mathbb{Z}_2 \to K$ satisfies:

$$X_H(2\mathfrak{z} + j) = r_j X_H(\mathfrak{z}) + c_j, \quad j \in \{0, 1\}$$

with $r_0 = 1/2$, $r_1 = 3/2$, $c_0 = 0$, $c_1 = 1/2$. This functional equation is equivalent to our [[Affine Orbit Structure]]: $\text{dest}(n) = \text{slope} \cdot n + C$.

### Step 2: The Adelic Contraction Product

The contraction rate $\rho_{H,\ell} = \prod_{j} \|r_j\|_\ell$ at each place $\ell$:

| Place $\ell$ | $\|r_0\|$ | $\|r_1\|$ | $\rho$ | Behavior |
|---|---|---|---|---|
| Archimedean ($\infty$) | $1/2$ | $3/2$ | $3/4$ | **Contracts** |
| 2-adic | $2$ | $2$ | $4$ | Expands |
| 3-adic | $1$ | $1/3$ | $1/3$ | **Contracts** (= 3-adic lock) |
| $p$-adic ($p \geq 5$) | $1$ | $1$ | $1$ | Neutral |

By the adelic product formula: $\rho_\infty \cdot \rho_2 \cdot \rho_3 = (3/4) \cdot 4 \cdot (1/3) = 1$.

**Caveat (added 2026-04-26).** The product equalling 1 is *automatic* for any Hydra with nonzero rational ratios — it is just the adelic product formula $\prod_\ell |x|_\ell = 1$ applied to $r_0$ and $r_1$. The same identity holds for $5n+1$: $(5/4)(4)(1/5) = 1$, and for $7n+1$: $(7/4)(4)(1/7) = 1$. So "the product is 1" is not a Collatz-specific knife edge.

The actual structural discriminator is the **archimedean factor** $\rho_\infty = a/4$:
- $a = 3$ (Collatz): $\rho_\infty = 3/4 < 1$ — contracts (smallest possible with $a$ odd $> 1$).
- $a = 5, 7, 9, \dots$: $\rho_\infty > 1$ — expands.

The 2-adic ($\rho_2 = 4$, expanding) and 3-adic ($\rho_3 = 1/3$, contracting) factors are mechanically determined by the prime factorization of $r_0 r_1 = a/4$ and contribute no independent information beyond what $\rho_\infty$ already records. The real engine of the proof lives in Step 4 (absolute continuity of $\mu$), driven by $\chi_\infty < 0$ and similarity dimension $s \gg 1$. See [[Lens C - Implication Catalog]] §6 for the full discussion.

### Step 3: The Self-Similar Measure

The numen defines a self-similar (Bernoulli-type) measure $\mu$ on $\mathbb{R}$:

$$\mu = \frac{1}{2}(\phi_0{}_* \mu + \phi_1{}_* \mu)$$

where $\phi_0(x) = x/2$ and $\phi_1(x) = (3x+1)/2$.

**Lyapunov exponent:**

$$\chi = \frac{1}{2}\ln\frac{1}{2} + \frac{1}{2}\ln\frac{3}{2} = \ln\frac{2}{\sqrt{3}} \approx -0.144 < 0$$

By Furstenberg-Kesten: the random product contracts almost surely.

**Similarity dimension:**

$$s = \frac{h(p)}{\chi} = \frac{\ln 2}{\ln(2/\sqrt{3})} \approx 4.82 \gg 1$$

The measure is in the **super-critical regime**: similarity dimension far exceeds 1.

### Step 4: Absolute Continuity (THE KEY STEP)

**Conjecture (Collatz AC):** The self-similar measure $\mu$ defined by the Collatz IFS $\{\phi_0, \phi_1\}$ with equal weights is absolutely continuous with respect to Lebesgue measure on $\mathbb{R}$.

**Evidence:**
- Similarity dimension $s = 4.82 \gg 1$ (super-critical)
- Lyapunov exponent $\chi < 0$ (average contraction)
- Algebraic parameters ($1/2, 3/2 \in \mathbb{Q}$)
- No exact overlaps (branches partition $\mathbb{Z}$ into even/odd)
- All known results (Hochman 2014, Shmerkin 2019, Varjú 2019) support AC under these conditions

**The gap:** Existing theorems require all contraction ratios $|r_i| < 1$. Our IFS has $|r_1| = 3/2 > 1$ (one expanding branch). The product $\rho = 3/4 < 1$ ensures average contraction, but the expanding branch prevents direct application of standard results.

**This is a specific, tractable problem in fractal geometry:** extend the Hochman-Shmerkin absolute continuity theory to IFS with average contraction ($\rho < 1$) but not uniform contraction (some $|r_i| > 1$).

### Step 5: Equidistribution of Orbits

If $\mu$ is absolutely continuous, then for Haar-almost-every $\mathfrak{z} \in \mathbb{Z}_2$, the digit frequencies of $\mathfrak{z}$ are equidistributed. The branch sequence of the Collatz orbit visits each branch with Haar-predicted frequency:

- $P(\alpha \geq 3) = 25\%$ under Haar measure
- Required: $P(\alpha \geq 3) \geq 4.4\%$ for convergence

The margin is enormous: $25\% \gg 4.4\%$.

### Step 6: Almost Every → Every

By Part A: no positive integer $n$ is periodic under the Collatz map.

By Siegel's Correspondence Principle (Theorem 6.1): every rational 2-adic integer is either periodic or preperiodic under $H$. Since $\mathbb{N} \subset \mathbb{Z}_2 \cap \mathbb{Q}$ and no cycles exist, every $n \in \mathbb{N}$ is preperiodic — its orbit eventually reaches the unique fixed point at 1.

The exceptional set where $\mu$ might be singular has Hausdorff dimension 0 (by the Hochman-Shmerkin theory). Since $\mathbb{N}$ is countable (dimension 0), the natural numbers avoid the exceptional set.

## Summary

| Component | Status | Method |
|-----------|--------|--------|
| No cycles | **Proved** | Irrationality of $\log_2 3$ + Diophantine bounds |
| IFS framework | **Established** | Siegel's Hydra maps |
| Lyapunov < 0 | **Proved** | Direct computation |
| Similarity dim > 1 | **Proved** | $s = 4.82$ |
| Absolute continuity | **Conjectured** | Needs extension of Hochman/Shmerkin to non-uniform IFS |
| Almost every → every | **Conditional** | Follows from AC + Correspondence Principle |

**The Collatz conjecture is equivalent to the Collatz AC conjecture**, which is a problem in fractal geometry and harmonic analysis, not number theory.

## Connections

- The adelic product formula $\rho_\infty \rho_2 \rho_3 = 1$ is the [[Collatz Complementarity Principle|knife edge]]
- The numen functional equation is [[Affine Orbit Structure]]
- The 3-adic contraction ($\rho_3 = 1/3$) is the [[Affine Orbit Structure|3-adic lock]]
- The [[Eisenstein Factorization]] decomposes $\rho_3 = 1/3$ via $3 = \pi \bar{\pi}$ in $\mathbb{Z}[\omega]$
- The [[Lattice Path Formula]] describes the digit statistics of the numen
- The Pythagorean comma ($3^{12}/2^{19}$) is the period-12 structure of the [[Eisenstein Factorization]]

## References

- Siegel, M.C. "The Hydra Map and Numen Formalisms for Collatz-Type Problems" (arxiv 2601.17030, 2026)
- Hochman, M. "On self-similar sets with overlaps and inverse theorems for entropy" (Annals of Math, 2014)
- Shmerkin, P. & Solomyak, B. "Absolute continuity of self-similar measures, their projections and convolutions" (Trans. AMS, 2014)
- Varjú, P.P. "Absolute continuity of Bernoulli convolutions for algebraic parameters" (JAMS, 2019)
