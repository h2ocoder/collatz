# The abc Conjecture Connection

## Statement of abc

<div class="theorem">

**abc Conjecture.** For every $\varepsilon > 0$, there exists $K(\varepsilon)$ such that for all coprime positive integers with $a + b = c$:

$$c < K(\varepsilon) \cdot \text{rad}(abc)^{1+\varepsilon}$$

where $\text{rad}(n)$ is the product of the distinct prime factors of $n$.

</div>

The abc conjecture is open, and I know of no implication between it and the Collatz conjecture in either direction. This page only works out what abc would say about one quantity that appears in the study of Collatz cycles, and compares that with what is already proved.

## The Minimal Radical

The Collatz map involves only two primes: 2 and 3. The radical of any product of their powers is:

$$\text{rad}(2^a \cdot 3^b) = 6$$

regardless of the exponents. This is the **smallest possible radical** for a product of two distinct primes. The terms can be enormous ($2^{485}$, $3^{306}$), yet the radical stays at 6.

## What abc would say about the gap $2^E - 3^S$

The quantity that controls Collatz cycles is the gap $g = 2^E - 3^S$ (see [The Cycle Equation: Small Cases](/cycles/convergent-elimination)). Apply abc with

$$a = 3^S, \quad b = g, \quad c = 2^E.$$

Then $\text{rad}(abc) = 6 \cdot \text{rad}(g)$, and abc gives $2^E < K(\varepsilon) \cdot (6\,\text{rad}(g))^{1+\varepsilon}$. In words: **the radical of the gap would have to be almost as large as $2^E$ itself**, $\text{rad}(g) > 2^{E(1-\varepsilon')}$ up to a constant. The gap could not be built mostly from repeated prime factors.

For the *size* of the gap alone, abc is not needed, and it would say less than what is already proved. That $g > 2^{E(1-\delta)}$ for every $\delta > 0$ and all large $E$ is a theorem of Pillai (1931), made effective by Ellison (1971), who showed $|2^x - 3^y| > 2^x e^{-x/10}$ for $x > 27$. Bounds on linear forms in logarithms give more: $g > 2^E / E^{\kappa}$ up to a constant, with Rhin's $\kappa \approx 13.3$, which for large $E$ is bigger than $2^{E(1-\varepsilon')}$. So that powers of 2 and 3 cannot come unusually close together is known, not a consequence of abc.

That proved statement is what feeds into the results on cycles: the closer $2^E$ can get to $3^S$, the more room there is for a cycle.

## Hierarchy of bounds

How close can $s \log_2 3$ get to an integer — equivalently, how small can the [bit destruction](/proofs/bit-destruction) $\beta(s)$ be? From weakest to strongest:

| Method | Bound on $\beta(s)$ | Status |
|--------|---------------------|--------|
| Irrationality of $\log_2 3$ | $\beta > 0$ | Proved |
| abc conjecture | $\beta > 2^{-\varepsilon s}$ up to a constant, for every $\varepsilon > 0$ | Unproved, and weaker than the next line |
| Linear forms in logarithms (Baker; Rhin) | $\beta > s^{-\kappa}$ up to a constant, with $\kappa \approx 13.3$ (Rhin 1987) | Proved; the strongest of the three for large $s$ |

Bounds of this last kind are the ones actually used in the literature on $m$-cycles (Steiner 1977, Simons and de Weger 2005, Hercher 2023). Eliahou's 1993 lower bound on cycle length uses the continued fraction of $\log_2 3$ and the verified range instead. The [divisibility conjecture](/cycles/divisibility-obstruction) is a different kind of statement: it is equivalent to the absence of nontrivial cycles, so it is not a bound that could be combined with these to finish the job.

## S-Unit Equations

The equation $|2^E - 3^S| = g$ is a special case of the **S-unit equation** with $S = \{2, 3\}$.

For each fixed $g$ there are only **finitely many** solutions $(E, S)$. That is classical (Pólya 1918; Pillai 1931); Evertse (1984) bounded the number of solutions of such equations explicitly. So each gap value appears only finitely often, and the gaps $|2^E - 3^S|$ grow without bound. That alone does not rule out cycles: a cycle does not need a small gap, only one that divides the right sum.

## Why the connection is natural

The Collatz map involves only the primes 2 and 3, the smallest radical two primes can have. Questions about Collatz cycles keep turning into questions about how close powers of 2 and 3 can be — which is the territory of Baker's theorem, and a neighbour of the abc conjecture.

## Related

- [The Cycle Equation: Small Cases](/cycles/convergent-elimination) — the cycle equation and its gap
- [Cycles as a Divisibility Question](/cycles/divisibility-obstruction) — the cycle problem restated term by term
- [Bit Destruction](/proofs/bit-destruction) — the size of a drop in bits
