# Dropping Modulus
**Source:** Paper 1, Definition 8

A positive integer classifying $n$ into distinct inner subsets within a [[Dropping Set]].

For $k \geq 8$, Dropping Sets contain multiple inner subsets. The Dropping Modulus identifies which subset $n$ belongs to.

- $\text{Dset}_8$ has 2 moduli (0 and 1)
- Modulus 0: $a_n = 32n - 21$
- Modulus 1: $a_n = 32n - 9$

OEIS: Number of moduli per set in [A100982](https://oeis.org/A100982)

**Related:** [[Dropping Set]], [[Dropping Index]], [[Stopping Modulus]]

**Code:** `collatz.dropping.dropping_modulus(n)`
