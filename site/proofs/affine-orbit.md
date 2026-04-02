# Affine Orbit Structure

## Statement

<div class="theorem">

**Theorem (Affine Orbit Structure).** For any Dropping Set $\text{Dset}_k$ with orbital oddity $s$, members within each residue-class subgroup mod $2^{k-s}$ satisfy:

$$\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$$

where $C$ is a constant depending only on the subgroup (residue class), not on $n$. The slope $3^s / 2^{k-s}$ — the **contraction ratio** — is the same across all subgroups of $\text{Dset}_k$. Only the intercept $C$ varies.

Similarly, the orbit sum $\sum_{j=0}^{k-1} f^j(n)$ and orbit maximum $\max_j f^j(n)$ are exact affine functions of $n$ within each subgroup.

</div>

## Significance

This theorem reveals that Collatz dynamics are piecewise-affine: within each residue class of a Dropping Set, the destination, orbit sum, and orbit maximum are all linear functions of the starting value. Every drop is a linear map, making orbits algebraically tractable rather than chaotic. The universal contraction ratio $3^s/2^{k-s}$ connects directly to the Odd Stopping Time Spectrum: $3^s/2^{k-s} < 1$ iff $k > s \cdot \log_2 6$.

## Examples

Table of verified slopes:

| $k$ | $s$ | Slope $3^s/2^{k-s}$ | Decimal | Example |
|-----|-----|---------------------|---------|---------|
| 1 | 0 | $1/2$ | 0.500 | $\text{dest} = n/2$ |
| 3 | 1 | $3/4$ | 0.750 | $\text{dest} = \frac{3}{4}n + \frac{1}{4}$ |
| 6 | 2 | $9/16$ | 0.5625 | $\text{dest} = \frac{9}{16}n + \frac{5}{16}$ |
| 8 | 3 | $27/32$ | 0.844 | Two subgroups, same slope |
| 11 | 4 | $81/128$ | 0.633 | Three subgroups, same slope |
| 13 | 5 | $243/256$ | 0.949 | Seven subgroups, same slope |

Worked example for $\text{Dset}_3$: All members satisfy $n \equiv 1 \pmod{4}$. For $n = 5$: $\text{dest} = \frac{3}{4}(5) + \frac{1}{4} = \frac{16}{4} = 4$. Verify: $5 \to 16 \to 8 \to 4$. ✓

Verified exactly (using `Fraction` arithmetic) for all $k$ up to 37.

## Proof

<div class="proof">

**By induction on $k$ (number of Collatz steps).**

**Base case** ($k = 0$): $f^0(n) = n = \frac{3^0}{2^0} n + 0$. ✓

**Inductive step** ($k \to k+1$): Assume after $k$ steps with parity word $w = (w_0, \ldots, w_{k-1})$ containing $s$ ones:

$$f^k(n) = \frac{3^s}{2^{k-s}} n + C_w$$

We must show this holds at step $k+1$.

**Case 1: $f^k(n)$ is even** (halving step, $s$ unchanged):

$$f^{k+1}(n) = \frac{f^k(n)}{2} = \frac{3^s}{2^{k-s+1}} n + \frac{C_w}{2}$$

Slope = $3^s / 2^{(k+1)-s}$. ✓

**Case 2: $f^k(n)$ is odd** ($3x+1$ step, $s \to s+1$):

$$f^{k+1}(n) = 3 \cdot f^k(n) + 1 = \frac{3^{s+1}}{2^{k-s}} n + 3C_w + 1$$

Slope = $3^{s+1} / 2^{(k+1)-(s+1)}$. ✓

**Key insight (bit consumption):** The parity of $f^k(n)$ is determined by $n \bmod 2^{k-s}$:
- Each **even step** consumes one bit of $n$ (requires knowing one more bit of $n$ to determine the next parity)
- Each **odd step** consumes no additional bits (the result of $3x+1$ is always even, so the next parity is determined for free)

After $k$ steps with $s$ odd steps and $k-s$ even steps, exactly $k-s$ bits of $n$ have been consumed. Therefore, the parity word — and hence the entire affine map — is determined by $n \bmod 2^{k-s}$.

</div>

## Corollaries

<div class="corollary">

**Corollary 1 (Orbital Oddity Invariance).** All members of $\text{Dset}_k$ in the same residue class share the same parity word, hence the same number of odd steps $s$. Since all residue classes defining $\text{Dset}_k$ have the same $k$ and the same $s$ (otherwise they'd belong to a different set), orbital oddity is constant within $\text{Dset}_k$.

</div>

<div class="corollary">

**Corollary 2 (Affine Orbit Sums).** Each intermediate value $f^j(n)$ for $j = 0, \ldots, k-1$ is affine in $n$ (by the theorem at step $j$). Therefore the orbit sum $\sum_{j=0}^{k-1} f^j(n)$ and orbit max $\max_j f^j(n)$ are also affine in $n$ within each subgroup.

</div>

<div class="corollary">

**Corollary 3 (Period of $\text{Dset}_k$).** Members of $\text{Dset}_k$ are exactly the integers in certain residue classes mod $2^{k-s}$. The period is $2^{k-s}$.

</div>

<div class="corollary">

**Corollary 4 (Dropping Condition).** The contraction ratio $3^s / 2^{k-s} < 1$ is equivalent to $k > s \cdot \log_2 6$, linking to the [Odd Stopping Time Spectrum](/proofs/bit-destruction): $k = \lceil s \cdot \log_2 6 \rceil$.

</div>

## Related Results

- [Logarithmic Escape Theorem](/proofs/logarithmic-escape) — uses the affine structure to bound self-chains
- [Bit Destruction Bound](/proofs/bit-destruction) — derives bit destruction rate from the contraction ratio
- [3-Adic Mixing](/proofs/mixing) — the $3^s$ multiplication scrambles residue classes
