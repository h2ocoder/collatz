# Dropping Time
**Source:** Paper 1, Definition 3

The minimum number of iterations of the Collatz function required to reach a value less than the starting number $n$.

The final Collatz step will always be division by 2.

**Notation:** $\text{Dtime}_n$

**Example:** $\text{Dtime}_3 = 6$ (orbit: 3 → 10 → 5 → 16 → 8 → 4 → 2)

**Related:** [[Dropping Destination]], [[Dropping Set]], [[Stopping Time]]

**Code:** `collatz.dropping.dropping_time(n)`
