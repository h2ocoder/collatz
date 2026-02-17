# Proportional Power Ratio
**Source:** Paper 3 (Medium article)

$$P(x) = \frac{x - b^k}{b^{k+1} - b^k}$$

where $k = \lfloor \log_b(x) \rfloor$ and $b$ is the chosen base.

Maps integers to $[0, 1)$, spreading values between consecutive powers of $b$. Interesting patterns emerge in base 6, revealing a 44-cycle in polar plots.

**Code:** `collatz.geometry.proportional_power_ratio(x, base)`
