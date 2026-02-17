# Orbital Triple Mapping
**Source:** Paper 1, Section 4.1

Maps each integer $j$ to a Pythagorean triple $(a, b, c)$ using:
- $a = j^2 - d^2$
- $b = 2dj$
- $c = j^2 + d^2$

where $d = \text{Ddest}_j$ (the [[Dropping Destination]]).

**Collatz-Pythagorean Convergence:** $b + c = (j + d)^2$

**Code:** `collatz.geometry.orbital_triple(n)`
