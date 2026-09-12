# Periodic Point Proximity

**Date:** 2026-09-10 · **Script:** `scripts/periodic_point_proximity.py` (odd $n \le 10^6$, 5 s)
**Origin:** the "two vectors from $n$" picture — up to $3n+1$, down to $\text{dest}(n)$ — made precise.

## The geometry, exactly

For odd $n$ with dropping $T$-word $w=(L,s,C_w)$, [[Affine Orbit Structure]] gives the down-line $\text{dest} = r\,n + C_w/2^L$ with $r = 3^s/2^L<1$. The line meets the diagonal $\text{dest}=n$ at the **rational periodic point** of the word,
$$x_w = \frac{C_w}{2^L - 3^s},$$
and $n$ drops through $w$ iff $n > x_w$. Define the **shortfall**
$$\sigma(n) = \frac{x_w}{n} = \frac{C_w}{n\,(2^L-3^s)} \in (0,1).$$
Exact identity:
$$\frac{\text{dest}(n)}{n} = r + (1-r)\,\sigma(n).$$
So $\sigma$ is the fraction of the class's promised contraction that $n$ fails to achieve; $\sigma\to 1$ is a cycle. Equivalently $\sigma = (C_w/2^L)\,/\,(n(1-r))$, and $C_w/2^L$ (the "+1 wobble") is $O(1)$ across words (median 0.28, 90th pct 1.11, max 4.47 in the sample), so
$$\sigma(n) \approx \frac{O(1)}{n\,(1-r_w)}.$$
Near-cycles are numbers with $n(1-r_w) = O(1)$: small $n$ carrying a weak-contraction word.

## Findings

**1. The famous small hard numbers are the top of the $\sigma$ ranking.** Among all 499,999 odd $n \le 10^6$: 47 is rank 1 ($\sigma=0.713$: its periodic point is 33.5 and it drops only to 46), 63 rank 2 (0.572), 27 rank 5 (0.323), 71 rank 10, 31 rank 15, 41 rank 71, 703 rank 76, 871 rank 89. The top-50 by $\sigma$ have median $n = 93$ and are hard three times as often as the population (24% vs 8% with $>12$ steps per bit). *The user's intuition — hard numbers sit near a crossing of the diagonal — is literally true for the classical small examples.*

**2. At scale, the nearest misses are the convergent word.** The largest $\sigma$ among $n>10^3$, $>10^4$, $>10^5$ is attained by $n = 4591, 20327, 141639$, **all with word $(L,s) = (65,41)$**, the convergent $65/41$ of $\log_2 3$ ($1 - r = 0.0136$, the weakest contraction any word below the next convergent $(485,306)$ can have). The values $\sigma = 0.044, 0.012, 0.0033$ decay like $\approx 200/n$, exactly $\frac{C_w/2^L}{n(1-r)}$ with $C_w/2^L \approx 2.7$. Proximity to a periodic point is therefore a **Diophantine** quantity: it is controlled by how well $s\log_2 3$ approximates an integer, i.e. by the continued fraction of $\log_2 3$, and effective lower bounds on $2^L - 3^s$ (Baker/Rhin) bound it from above.

**3. It is a small-number phenomenon.** $\sigma$ is below $0.0004$ for 99% of $n\le10^6$ and below 0.012 for every $n>10^4$. The record-setters of total stopping time per bit at large $n$ (35655, 230631, 626331, 837799) all have first-drop $\sigma \le 0.0005$: their hardness comes from the *sequence* of words along the drop chain, not from proximity to any periodic point.

**4. No predictive power beyond the identity.** corr($\sigma$, steps/bit) $=+0.011$; within fixed $(L,s)$ classes $-0.001$; top-decile $\sigma$ vs the rest matched on dropping time differ by $+0.15$ steps/bit out of 7.44 — which is just the first-drop shortfall $(1-r)\sigma$ propagating, as the identity says it must.

## What this gives and what it does not

- **A clean explanation of "why 27"**: 27, 31, 47, 63, 71 are the integers closest to rational periodic points of long words, among all $n\le10^6$. Their first drop barely undershoots them, so they carry an essentially full-length excursion. This is the geometric face of the cycle-exclusion problem: the same denominators $2^L-3^s$.
- **A proof-shaped statement**: for $n$ with word $w$, $\text{dest}/n \le r_w + (1-r_w)\,\frac{4.5}{n(1-r_w)} = r_w + 4.5/n$ (empirical constant), so beyond $n\approx 10^3$ every first drop contracts by essentially its class ratio. Nothing about *which* word $n$ gets, which is the conjecture.
- **Dead end for large $n$**: geometry that only sees the first drop cannot see the chain, and the chain is where large hard numbers live.

## Related

[[Affine Orbit Structure]] · [[Bit Destruction Bound]] ($1-r_w \approx \beta(s)\ln 2$) · [[Three-Bit Countdown]] (minimal avoiders = small members of large classes) · [[Prime Factorization and Dropping Rate]] (the multiplicative view, which sees nothing)
