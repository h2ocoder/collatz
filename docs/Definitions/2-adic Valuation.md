# 2-adic Valuation
**Source:** Standard number theory

$$v_2(n) = \max\{k : 2^k \mid n\}$$

The largest power of 2 dividing $n$. Equivalently, the number of trailing zeros in the binary representation.

**Examples:** $v_2(12) = 2$, $v_2(8) = 3$, $v_2(7) = 0$

Central to Collatz dynamics because the Collatz function's behavior is governed by parity (mod 2 structure).

**Related:** [[Alpha Value]], [[Syracuse Map]]

**Code:** `collatz.core.v2(n)`
