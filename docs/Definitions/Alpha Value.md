# Alpha Value
**Source:** Derived from 2-adic structure of Collatz dynamics

$$\alpha(n) = v_2(3n + 1)$$

The number of halvings that follow a $3n+1$ step for odd $n$. Controls the "shape" of each [[Syracuse Map]] step.

**Determined by residue classes:**
- $n \equiv 3 \pmod{4} \Rightarrow \alpha = 1$
- $n \equiv 1 \pmod{8} \Rightarrow \alpha = 2$
- $n \equiv 5 \pmod{8} \Rightarrow \alpha \geq 3$

**Factorization connection:** For $n = pq$ (odd primes), the first alpha is determined by $(p \bmod 4)(q \bmod 4) \bmod 4$:
- Both $\equiv 1$: first $\alpha \geq 2$
- Both $\equiv 3$: first $\alpha \geq 2$
- Mixed: first $\alpha = 1$

**Related:** [[Alpha Sequence]], [[Syracuse Map]], [[2-adic Valuation]]

**Code:** `collatz.core.alpha_value(n)`
