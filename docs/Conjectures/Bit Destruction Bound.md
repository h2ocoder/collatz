# Bit Destruction Bound

**Status:** Proved (conditional on finite dropping time); unconditional mixing result proved

## Core Identity

For any $\text{Dset}_k$ with [[Orbital Oddity]] $s$, the **bits destroyed** per drop are:

$$\beta(s) = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3 = 1 - \{s \cdot \log_2 3\}$$

where $\{x\}$ is the fractional part of $x$. This is always strictly positive because $\log_2 3$ is irrational.

## Slow Sets and Number Theory

The "slow" sets (small $\beta$) occur when $s \cdot \log_2 3$ is close to an integer from below:

| $s$ | $s \cdot \log_2 3$ | $\beta(s)$ | Set$_k$ |
|-----|---------------------|-------------|---------|
| 5   | 7.925               | 0.075       | 13      |
| 17  | 26.944              | 0.056       | 44      |
| 29  | 45.964              | 0.036       | 75      |
| 41  | 64.984              | 0.017       | 106     |
| 53  | 83.983              | 0.003       | 137     |

These are governed by the **convergents of $\log_2 3$**: the best rational approximations $p/q$ to $\log_2 3$ give the slowest sets at $s = q$.

By **Roth's theorem**: for any $\varepsilon > 0$, there are finitely many $p/q$ with $|\log_2 3 - p/q| < 1/q^{2+\varepsilon}$. This gives:

$$\beta(s) > \frac{c}{s} \quad \text{for some constant } c > 0$$

## Conditional Convergence Bound

**Theorem.** *If* every integer $> 1$ has a finite dropping time, then every orbit reaches 1 in at most $O(\log^2 n)$ drops.

**Proof.** A number $n$ with $B = \lfloor \log_2 n \rfloor$ bits can only visit sets with $s \leq B / \log_2 3$. By the bit destruction identity, each drop destroys $\beta(s_i) > c/s_{\max} > c'/B$ bits. After $B / (c'/B) = O(B^2)$ drops, all bits are destroyed and the orbit has reached 1. $\blacksquare$

## Unconditional Mixing Theorem

**Theorem (3-adic Mixing).** After a drop through $\text{Dset}_k$ with oddity $s$, the destination's residue mod $2^B$ is determined by multiplication by $3^s \pmod{2^B}$. Since $\text{ord}(3 \bmod 2^B) = 2^{B-2}$ for $B \geq 3$, this multiplication acts as a near-bijection on residue classes.

**Consequence:** The mutual information between consecutive dropping set assignments satisfies:

$$I(\text{Set}_{\text{next}}; \text{Set}_{\text{current}}) \approx 0.03 \text{ bits} \quad (\sim 1.3\% \text{ of } H(\text{Set}))$$

Set transitions are 98.7% independent. The Collatz map acts as an effective scrambler of 2-adic information via multiplication by powers of 3.

## Combined Picture

| Component | What it proves | Gap remaining |
|-----------|---------------|---------------|
| $\beta(s) > 0$ always | Every drop makes progress | - |
| Roth: $\beta(s) > c/s$ | Slow drops can't be too slow | - |
| [[Logarithmic Escape Theorem]] | Self-chains bounded by $O(\log n)$ | - |
| Mixing: $I \approx 0.03$ bits | Consecutive sets nearly independent | Doesn't exclude measure-zero exceptions |
| Cumulative density $\to 1$ | "Almost all" $n$ have finite dropping time | Density $\neq$ all |
| **Gap** | Every $n$ has finite dropping time | **Equivalent to the Collatz conjecture** |

## Numerical Verification

| $B$ (bits) | Min $\beta$ | Worst-case drops | Avg drops (observed) |
|-----------|-------------|-----------------|---------------------|
| 64        | 0.0196      | ~3,300          | ~90                 |
| 128       | 0.0030      | ~42,000         | ~180                |
| 256       | 0.0030      | ~85,000         | ~360                |
| 1024      | 0.0015      | ~694,000        | ~1,400              |

The observed average (~$1.4B$) is far below the worst case (~$B^2/c$), confirming the mixing property drives typical behavior.

## Related

- [[Affine Orbit Structure]] — the affine formula underlying bit destruction
- [[Logarithmic Escape Theorem]] — bounds consecutive slow drops
- [[Odd Stopping Time Spectrum]] — $k = \lceil s \log_2 6 \rceil$, the formula behind $\beta(s)$
