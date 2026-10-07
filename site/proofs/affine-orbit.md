# Affine Orbit Structure

The affine structure of orbits within residue classes is due to Terras (1976) and Everett (1977). This page explains it in the dropping-set notation used on this site.

## Statement

<div class="theorem">

**Theorem (Terras 1976, Everett 1977; stated in dropping-set notation).** For any integer $n$ with [dropping time](/foundations/definitions#dropping-time) $k$ and orbital oddity $s$, within each residue class mod $2^{k-s}$:

$$\text{dest}(n) = \frac{3^s}{2^{k-s} } \cdot n + C$$

where $C$ is a constant depending only on the residue class, not on $n$. The slope $3^s / 2^{k-s}$ is the **contraction ratio**.

Similarly, the orbit sum $\sum_{j=0}^{k-1} f^j(n)$ is an exact affine function of $n$ within each residue class.

</div>

The theorem speaks about one residue class at a time. Whether every residue class of $\text{Dset}_k$ has the same $s$, and so the same slope, is a separate question. Terras proved that each $\text{Dset}_k$ agrees, apart from at most finitely many integers, with a union of residue classes mod $2^{k-s}$ that all have the same $s$. That there are no exceptions at all among $n \geq 2$ is his *coefficient stopping time conjecture*. It is open, and it would imply that there are no nontrivial cycles (Lagarias, *The 3x+1 problem and its generalizations*, 1985). Checked by computer: there is no exception in any dropping set with $k \le 39$, nor at any $n \le 10^7$. In that range the slope is the same across all residue classes of $\text{Dset}_k$, and only the intercept $C$ varies.

## Why it matters

Collatz dynamics are piecewise-affine: within each residue class of a Dropping Set, the destination and the orbit sum are affine functions of the starting value (and so is the orbit maximum in every class I have checked, $k \le 39$). Each individual drop is simple; the difficulty is in how the pieces chain together. The contraction ratio $3^s/2^{k-s}$ connects directly to the list of possible dropping times: $3^s/2^{k-s} < 1$ iff $k > s \cdot \log_2 6$.

## Examples

Table of verified slopes:

| $k$ | $s$ | Slope $3^s/2^{k-s}$ | Decimal | Example |
|-----|-----|---------------------|---------|---------|
| 1 | 0 | $1/2$ | 0.500 | $\text{dest} = n/2$ |
| 3 | 1 | $3/4$ | 0.750 | $\text{dest} = \frac{3}{4}n + \frac{1}{4}$ |
| 6 | 2 | $9/16$ | 0.5625 | $\text{dest} = \frac{9}{16}n + \frac{5}{16}$ |
| 8 | 3 | $27/32$ | 0.844 | Two residue classes, same slope |
| 11 | 4 | $81/128$ | 0.633 | Three residue classes, same slope |
| 13 | 5 | $243/256$ | 0.949 | Seven residue classes, same slope |

Worked example for $\text{Dset}_3$: All members satisfy $n \equiv 1 \pmod{4}$. For $n = 5$: $\text{dest} = \frac{3}{4}(5) + \frac{1}{4} = \frac{16}{4} = 4$. Verify: $5 \to 16 \to 8 \to 4$. ✓

Checked exactly (using `Fraction` arithmetic) on the first four members of each of the 81,119 residue classes that make up the dropping sets with $k \le 39$.

## Proof

<div class="proof">

**By induction on $k$ (number of Collatz steps).**

**Base case** ($k = 0$): $f^0(n) = n = \frac{3^0}{2^0} n + 0$. ✓

**Inductive step** ($k \to k+1$): Assume after $k$ steps with parity word $w = (w_0, \ldots, w_{k-1})$ containing $s$ ones:

$$f^k(n) = \frac{3^s}{2^{k-s} } n + C_w$$

We must show this holds at step $k+1$.

**Case 1: $f^k(n)$ is even** (halving step, $s$ unchanged):

$$f^{k+1}(n) = \frac{f^k(n)}{2} = \frac{3^s}{2^{k-s+1} } n + \frac{C_w}{2}$$

Slope = $3^s / 2^{(k+1)-s}$. ✓

**Case 2: $f^k(n)$ is odd** ($3x+1$ step, $s \to s+1$):

$$f^{k+1}(n) = 3 \cdot f^k(n) + 1 = \frac{3^{s+1} }{2^{k-s} } n + 3C_w + 1$$

Slope = $3^{s+1} / 2^{(k+1)-(s+1)}$. ✓

**Key insight (bit consumption):** The parities of the first $k$ iterates $n, f(n), \ldots, f^{k-1}(n)$ are determined by $n \bmod 2^{k-s}$ whenever the $k$-th step is a halving, as it is at a drop:
- Each **even step** consumes one bit of $n$ (requires knowing one more bit of $n$ to determine the next parity)
- Each **odd step** consumes no additional bits (the result of $3x+1$ is always even, so the next parity is determined for free)

After $k$ steps with $s$ odd steps and $k-s$ even steps, exactly $k-s$ bits of $n$ have been consumed. Therefore, the parity word — and hence the entire affine map — is determined by $n \bmod 2^{k-s}$.

</div>

## Corollaries

<div class="corollary">

**Corollary 1 (Orbital Oddity).** All members of $\text{Dset}_k$ in the same residue class share the same parity word, hence the same number of odd steps $s$. That two different residue classes of the same $\text{Dset}_k$ also share $s$ is not proved in general; it would follow from the coefficient stopping time conjecture. It holds for every $k \le 39$ and every $n \le 10^7$.

</div>

<div class="corollary">

**Corollary 2 (Affine Orbit Sums).** Each intermediate value $f^j(n)$ for $j = 0, \ldots, k-1$ is affine in $n$ (by the theorem at step $j$). Therefore the orbit sum $\sum_{j=0}^{k-1} f^j(n)$ is also affine in $n$ within each residue class. The orbit maximum $\max_j f^j(n)$ is the largest of $k$ affine functions, which in general is only piecewise affine. In every dropping set with $k \le 39$ it is a single affine function on each residue class (checked by computer: the maximum is always reached at the step whose slope is largest). For larger $k$ the same holds for all large enough $n$ in a residue class; I have no proof for the smallest ones.

</div>

<div class="corollary">

**Corollary 3 (Period of $\text{Dset}_k$).** Apart from at most finitely many exceptions, the members of $\text{Dset}_k$ are the integers $n \geq 2$ in certain residue classes mod $2^{k-s}$ (Terras 1976). The period is $2^{k-s}$. For $k \le 39$ there are no exceptions (checked by computer); that there are none for any $k$ is the coefficient stopping time conjecture.

</div>

<div class="corollary">

**Corollary 4 (Dropping Condition).** A drop needs the contraction ratio $3^s / 2^{k-s}$ to be below 1 (because $C \geq 0$), which is equivalent to $k > s \cdot \log_2 6$. So every dropping time satisfies $k \geq \lfloor s \cdot \log_2 6 \rfloor + 1$. In every case checked ($k \le 39$, and all $n \le 10^7$) the dropping time is exactly this smallest value, $k = \lfloor s \cdot \log_2 6 \rfloor + 1 = 1, 3, 6, 8, 11, 13, \ldots$ These are the "allowable" dropping times of OEIS A122437, whose own comments note that it is not known whether every $n$ obeys the formula. See [Bit Destruction](/proofs/bit-destruction) for the size of each drop.

</div>

## Related Results

- [Bit Destruction](/proofs/bit-destruction) — the size of a drop, from the contraction ratio
- [Mixing Modulo Powers of Two](/proofs/mixing) — how the $3^s$ factor spreads destinations over residue classes
