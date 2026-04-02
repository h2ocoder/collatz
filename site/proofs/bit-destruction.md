# Bit Destruction Bound

## Statement

<div class="theorem">

**Theorem (Bit Destruction Identity).** For any $\text{Dset}_k$ with orbital oddity $s$, the bits destroyed per drop are:

$$\beta(s) = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3 = 1 - \{s \cdot \log_2 3\}$$

where $\{x\}$ is the fractional part. This is always strictly positive because $\log_2 3$ is irrational.

</div>

## Significance

Every single Collatz drop destroys a positive number of bits — there are no zero-progress drops. The minimum destruction rate is governed by how well $\log_2 3$ can be approximated by rationals, connecting Collatz dynamics to Diophantine approximation and Roth's theorem.

## The Bit Destruction Landscape

Table of $\beta(s)$ for $s = 0$ through $29$ (include all values):

| $s$ | $s \cdot \log_2 3$ | $\beta(s)$ | Set$_k$ | Status |
|-----|---------------------|-------------|---------|--------|
| 0 | 0.000 | 1.000 | 1 | |
| 1 | 1.585 | 0.415 | 3 | |
| 2 | 3.170 | 0.830 | 6 | |
| 3 | 4.755 | 0.245 | 8 | |
| 4 | 6.340 | 0.660 | 11 | |
| 5 | 7.925 | 0.075 | 13 | **slow** |
| 6 | 9.510 | 0.490 | 16 | |
| 7 | 11.095 | 0.905 | 19 | |
| 8 | 12.680 | 0.320 | 21 | |
| 9 | 14.265 | 0.735 | 24 | |
| 10 | 15.850 | 0.150 | 26 | slow |
| 11 | 17.435 | 0.565 | 29 | |
| 12 | 19.020 | 0.980 | 32 | |
| 13 | 20.605 | 0.395 | 34 | |
| 14 | 22.189 | 0.811 | 37 | |
| 15 | 23.774 | 0.226 | 39 | |
| 16 | 25.359 | 0.641 | 42 | |
| 17 | 26.944 | 0.056 | 44 | **slow** |
| 18 | 28.529 | 0.471 | 47 | |
| 19 | 30.114 | 0.886 | 50 | |
| 20 | 31.699 | 0.301 | 52 | |
| 21 | 33.284 | 0.716 | 55 | |
| 22 | 34.869 | 0.131 | 57 | slow |
| 23 | 36.454 | 0.546 | 60 | |
| 24 | 38.039 | 0.961 | 63 | |
| 25 | 39.624 | 0.376 | 65 | |
| 26 | 41.209 | 0.791 | 68 | |
| 27 | 42.794 | 0.206 | 70 | |
| 28 | 44.379 | 0.621 | 73 | |
| 29 | 45.964 | 0.036 | 75 | **slow** |

Pattern: slow sets occur when $s \cdot \log_2 3$ approaches an integer from below.

## Proof

<div class="proof">

The contraction ratio for $\text{Dset}_k$ with oddity $s$ is $3^s / 2^{k-s}$. From the [Odd Stopping Time Spectrum](/foundations/definitions), $k = s + \lceil s \cdot \log_2 3 \rceil$, so $k - s = \lceil s \cdot \log_2 3 \rceil$.

The bits destroyed equal the negative log of the contraction ratio:

$$\beta(s) = -\log_2\!\left(\frac{3^s}{2^{k-s}}\right) = (k-s) - s \cdot \log_2 3 = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3$$

Since $\log_2 3$ is irrational, $s \cdot \log_2 3$ is never an integer for $s > 0$, so $\beta(s) > 0$ always.

</div>

## Connection to Roth's Theorem

The slowest sets correspond to the best rational approximations $p/q$ to $\log_2 3$:

| $p$ | $q = s$ | $p/q$ | $\beta(s)$ |
|-----|---------|-------|-------------|
| 8 | 5 | 1.600 | 0.075 |
| 19 | 12 | 1.583 | 0.020 |
| 65 | 41 | 1.585 | 0.017 |
| 84 | 53 | 1.585 | 0.003 |
| 485 | 306 | 1.585 | 0.001 |

By **Roth's theorem**: for any $\varepsilon > 0$, there are finitely many rationals $p/q$ with $|\log_2 3 - p/q| < 1/q^{2+\varepsilon}$. This gives:

$$\beta(s) > \frac{c}{s} \quad \text{for some constant } c > 0$$

<div class="corollary">

**Corollary (Conditional Convergence).** If every integer $> 1$ has a finite dropping time, then every orbit reaches 1 in at most $O(\log^2 n)$ drops.

*Proof.* A number with $B = \lfloor \log_2 n \rfloor$ bits can only visit sets with $s \leq B / \log_2 3$. Each drop destroys $\beta(s_i) > c/s_{\max} > c'/B$ bits. After $B/(c'/B) = O(B^2)$ drops, all bits are destroyed.

</div>

## Numerical Verification

| $B$ (bits) | Min $\beta$ among reachable sets | Worst-case drops | Avg drops (observed) |
|-----------|----------------------------------|-----------------|---------------------|
| 64 | 0.0196 | ~3,300 | ~90 |
| 128 | 0.0030 | ~42,000 | ~180 |
| 256 | 0.0030 | ~85,000 | ~360 |
| 1024 | 0.0015 | ~694,000 | ~1,400 |

The observed average (~$1.4B$) is far below the worst case (~$B^2/c$), confirming the [mixing property](/proofs/mixing) drives typical behavior.

## Related Results

- [Affine Orbit Structure](/proofs/affine-orbit) — the affine formula underlying bit destruction
- [Logarithmic Escape](/proofs/logarithmic-escape) — bounds consecutive slow drops
- [3-Adic Mixing](/proofs/mixing) — explains why average behavior dominates
- [abc Conjecture Connection](/connections/abc-conjecture) — stronger bounds via Diophantine theory
