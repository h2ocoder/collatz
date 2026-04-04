# Affine Orbit Structure

**Status:** Proved by induction on number of Collatz steps

## Statement

For any [[Dropping Set]] $\text{Dset}_k$ with [[Orbital Oddity]] $s$, members within each residue-class subgroup mod $2^{k-s}$ satisfy exact affine relations:

$$\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$$

where $C$ is a constant depending only on the subgroup (residue class), not on $n$.

The slope $3^s / 2^{k-s}$ — the **contraction ratio** — is the same across ALL subgroups of $\text{Dset}_k$. Only the intercept varies.

Similarly, the orbit sum $\sum_{j=0}^{k-1} f^j(n)$ and orbit maximum $\max_{j} f^j(n)$ are exact affine functions of $n$ within each subgroup.

## Verified Examples

| $k$ | $s$ | Slope $3^s/2^{k-s}$ | Decimal | Example formula |
|-----|-----|---------------------|---------|-----------------|
| 1   | 0   | $1/2$               | 0.500   | $\text{dest} = n/2$ |
| 3   | 1   | $3/4$               | 0.750   | $\text{dest} = \tfrac{3}{4}n + \tfrac{1}{4}$ |
| 6   | 2   | $9/16$              | 0.5625  | $\text{dest} = \tfrac{9}{16}n + \tfrac{5}{16}$ |
| 8   | 3   | $27/32$             | 0.844   | Two subgroups, same slope |
| 11  | 4   | $81/128$            | 0.633   | Three subgroups, same slope |
| 13  | 5   | $243/256$           | 0.949   | Seven subgroups, same slope |

Verified exactly (using `Fraction` arithmetic) for all $k$ up to 37.

## Proof

By induction on $k$ (number of Collatz steps).

**Base case** ($k = 0$): $f^0(n) = n = \frac{3^0}{2^0} n + 0$.

**Inductive step** ($k \to k+1$): Assume $f^k(n) = \frac{3^s}{2^{k-s}} n + C_w$ for parity word $w$.

- **Even step** ($s$ unchanged): $f^{k+1}(n) = f^k(n)/2 = \frac{3^s}{2^{k-s+1}} n + C_w/2$. Slope = $3^s/2^{(k+1)-s}$. $\checkmark$
- **Odd step** ($s \to s+1$): $f^{k+1}(n) = 3 \cdot f^k(n) + 1 = \frac{3^{s+1}}{2^{k-s}} n + 3C_w + 1$. Slope = $3^{s+1}/2^{(k+1)-(s+1)}$. $\checkmark$

The parity word (sequence of odd/even steps) is determined by $n \bmod 2^{k-s}$, because each even step consumes one bit of $n$ while each odd step consumes none. $\blacksquare$

## Significance

The contraction ratio $3^s/2^{k-s} < 1$ is equivalent to $k > s \cdot \log_2 6$, linking directly to the [[Odd Stopping Time Spectrum]]. The combined 2-adic ($n \bmod 2^{k-s}$) and 3-adic ($\text{dest} \bmod 3^s$) constraints produce a modulus of $2^{k-2s} \cdot 6^s$, recovering the base-6 lattice from Paper 3.

## Related

- [[Orbital Oddity Conjecture]] — $s$ is constant within $\text{Dset}_k$ (follows as corollary)
- [[Odd Stopping Time Spectrum]] — $k = \lceil s \log_2 6 \rceil$
- [[Dropping Set]]
- [[Logarithmic Escape Theorem]]
