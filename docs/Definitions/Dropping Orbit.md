# Dropping Orbit
**Source:** Paper 1, Definition 5

The sequence of numbers when following Collatz rules from $n$ until reaching $2 \times \text{Ddest}_n$. Includes $n$, excludes the destination.

**Example:** $\text{Dorbit}_5 = [5, 16, 8]$ (destination is 4, orbit ends at 8 = 2×4)

**Related:** [[Dropping Time]], [[Orbital Oddity]], [[Stopping Orbit]]

**Code:** `collatz.dropping.dropping_orbit(n)`
