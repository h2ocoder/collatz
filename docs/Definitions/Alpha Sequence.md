# Alpha Sequence
**Source:** Derived from [[Syracuse Map]] dynamics

The sequence of [[Alpha Value]]s along the Syracuse orbit. A complete fingerprint of the orbit's branching pattern.

$$\alpha\text{-seq}(n) = [\alpha(n), \alpha(S(n)), \alpha(S^2(n)), \ldots]$$

**Examples:**
- $\alpha\text{-seq}(3) = [1, 4]$
- $\alpha\text{-seq}(7) = [1, 1, 2, 3, 4]$

**Key identity:** $\text{total\_stopping\_time}(n) = \text{len}(\alpha\text{-seq}) + \text{sum}(\alpha\text{-seq})$

For $n = 27$: $|\alpha| = 41$, $\sum\alpha = 70$, total = $111$ ✓

**Related:** [[Alpha Value]], [[Syracuse Map]], [[Orbital Oddity]]

**Code:** `collatz.core.alpha_sequence(n)`
