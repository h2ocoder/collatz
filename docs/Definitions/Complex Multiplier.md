# Complex Multiplier
**Source:** Paper 1, Section 5

A complex number $z_0$ connecting $z = n + ni$ to $z' = (n-d) + di$:

$$z_0 = \frac{z'}{z} = \frac{1}{2} + \frac{2d - n}{2n}i$$

Key properties:
- $\text{Re}(z_0) = \frac{1}{2}$ always (mirrors the Riemann Hypothesis critical line)
- $\text{Im}(z_0) \in (0, \frac{1}{2})$ for odd $n$

**Code:** `collatz.geometry.complex_multiplier(n)`
