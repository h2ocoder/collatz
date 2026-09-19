# The abc Conjecture Connection

## Statement of abc

<div class="theorem">

**abc Conjecture.** For every $\varepsilon > 0$, there exists $K(\varepsilon)$ such that for all coprime positive integers with $a + b = c$:

$$c < K(\varepsilon) \cdot \text{rad}(abc)^{1+\varepsilon}$$

where $\text{rad}(n)$ is the product of the distinct prime factors of $n$.

</div>

## The Minimal Radical

The Collatz map involves only two primes: 2 and 3. The radical of any product of their powers is:

$$\text{rad}(2^a \cdot 3^b) = 6$$

regardless of the exponents. This is the **smallest possible radical** for a product of two distinct primes. This is where abc has the most to say — the terms can be enormous ($2^{485}$, $3^{306}$), yet the radical stays at 6.

## What abc would say about the gap $2^E - 3^S$

The quantity that controls Collatz cycles is the gap $g = 2^E - 3^S$ (see [Convergent Elimination](/cycles/convergent-elimination)). Apply abc with

$$a = 3^S, \quad b = g, \quad c = 2^E.$$

Then $\text{rad}(abc) = 6 \cdot \text{rad}(g) \leq 6g$, and abc gives $2^E < K(\varepsilon) \cdot (6g)^{1+\varepsilon}$. In words: **the gap would have to be almost as large as $2^E$ itself**, $g > 2^{E(1-\varepsilon')}$ up to a constant. Powers of 2 and 3 could not come unusually close together.

That is exactly the kind of statement that feeds into lower bounds on cycle length: the closer $2^E$ can get to $3^S$, the more room there is for a cycle.

## Hierarchy of bounds

How close can $s \log_2 3$ get to an integer — equivalently, how small can the [bit destruction](/proofs/bit-destruction) $\beta(s)$ be?

| Method | Bound on $\beta(s)$ | Status |
|--------|---------------------|--------|
| Irrationality of $\log_2 3$ | $\beta > 0$ | Proved |
| Baker's theory of linear forms in logarithms | $\beta > s^{-\kappa}$, effective $\kappa$ (Rhin: $\kappa \approx 13$) | Proved |
| abc conjecture | $\beta > 2^{-\varepsilon s}$ up to a constant, for every $\varepsilon > 0$ | Unproved |

Baker's bound is the one actually used in the literature on cycles (Eliahou 1993, Simons and de Weger 2005, Hercher 2023). The [divisibility obstruction](/cycles/divisibility-obstruction) is a different kind of statement: it is equivalent to the absence of nontrivial cycles, so it is not a bound that could be combined with these to finish the job.

## S-Unit Equations

The equation $|2^E - 3^S| = g$ is a special case of the **S-unit equation** with $S = \{2, 3\}$.

Evertse (1984) proved: for each fixed $g$, there are **finitely many** solutions $(E, S)$. So each gap value appears only finitely often, and the gaps $|2^E - 3^S|$ grow without bound. That alone does not rule out cycles: a cycle does not need a small gap, only one that divides the right sum.

## Why the connection is natural

The Collatz map involves only the primes 2 and 3, the smallest radical there is. Questions about Collatz cycles keep turning into questions about how close powers of 2 and 3 can be — which is exactly the territory of Baker's theorem and the abc conjecture.

## Related

- [Convergent Elimination](/cycles/convergent-elimination) — the cycle equation and its gap
- [Divisibility Obstruction](/cycles/divisibility-obstruction) — the cycle problem as a divisibility question
- [Bit Destruction](/proofs/bit-destruction) — the size of a drop in bits
