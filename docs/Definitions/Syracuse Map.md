# Syracuse Map
**Source:** Standard Collatz literature; applied here to factor analysis

The Syracuse map (or "odd-only" Collatz map) strips away even steps:

$$S(n) = \frac{3n + 1}{2^{v_2(3n+1)}}$$

where $v_2$ is the [[2-adic Valuation]]. This sends odd numbers directly to odd numbers.

**Example:** $S(7) = 11$ (since $3 \times 7 + 1 = 22 = 2 \times 11$)

The Syracuse orbit is the Collatz orbit with all even numbers removed:
- $\text{Sorbit}_{Syracuse}(7) = [7, 11, 17, 13, 5, 1]$

**Key identity:** $\text{total\_stopping\_time}(n) = |\alpha\text{-sequence}| + \sum \alpha\text{-sequence}$

**Related:** [[Alpha Value]], [[Alpha Sequence]], [[Stopping Time]]

**Code:** `collatz.core.syracuse_step(n)`, `collatz.core.syracuse_orbit(n)`
