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

regardless of the exponents. This is the **smallest possible radical** for a product of two distinct primes. The abc conjecture is maximally constraining precisely in this setting — the terms can be enormous ($2^{485}$, $3^{306}$), yet the radical stays at 6.

## Application to Collatz Cycles

The cycle equation from the [Affine Orbit Structure](/proofs/affine-orbit):

$$3^S \cdot n + C_\text{total} = 2^E \cdot n$$

can be rewritten as:

$$(2^E - 3^S) \cdot n = C_\text{total}$$

Setting $a = 3^S \cdot n$, $b = C_\text{total}$, $c = 2^E \cdot n$:

$$\text{rad}(abc) = \text{rad}(2^E \cdot 3^S \cdot n^2 \cdot C_\text{total}) \leq 6 \cdot n \cdot C_\text{total}$$

The abc conjecture says $c < K(\varepsilon) \cdot \text{rad}(abc)^{1+\varepsilon}$, giving:

$$2^E \cdot n < K(\varepsilon) \cdot (6 \cdot n \cdot C_\text{total})^{1+\varepsilon}$$

For large cycles ($E$ large), this forces $n$ to be **bounded** — you can't have arbitrarily large cycles of a given pattern.

## Hierarchy of Bounds

| Method | Bound on $\beta(s)$ | Bound on cycle $n$ | Status |
|--------|---------------------|---------------------|--------|
| Irrationality of $\log_2 3$ | $\beta > 0$ | Finite for each pattern | Proved |
| Roth's theorem | $\beta > c/s$ | $n < \exp(c \cdot s^2)$ | Proved |
| Baker's theorem | $\beta > \exp(-c \cdot \log s \cdot \log\log s)$ | $n < \exp(\exp(c \cdot s))$ | Proved |
| Pillai conjecture | $\beta > c$ (constant) | Much tighter | Unproved |
| abc conjecture | $\beta > 2^{-\varepsilon k}$ | Exponential bound on $n$ | Unproved |

Each row strengthens the previous. The abc conjecture gives the strongest constraints but remains unproved. Our **divisibility obstruction** is an independent constraint from the affine structure, orthogonal to all of these.

## S-Unit Equations

The equation $|2^E - 3^S| = g$ is a special case of the **S-unit equation** with $S = \{2, 3\}$.

Evertse (1984) proved: for each fixed $g$, there are **finitely many** solutions $(E, S)$. This means:
- Each gap value $g$ can only appear for finitely many convergents
- The gaps $|2^E - 3^S|$ grow without bound along the convergent sequence

Combined with our framework: if the divisibility obstruction holds for all gaps up to some bound $G$, and Baker's theorem shows all convergents beyond a certain size have gap $> G$, then **all cycles are eliminated** by a finite computation.

## The Punchline

The Collatz conjecture lives in the gap between what we can prove about powers of 2 and 3, and what the abc conjecture says must be true. The two smallest primes, the smallest radical, the tightest constraint. Collatz is the **atomic case of abc**.

## Related

- [Convergent Elimination](/cycles/convergent-elimination) — the computational elimination that abc would strengthen
- [Divisibility Obstruction](/cycles/divisibility-obstruction) — our independent algebraic constraint
- [Bit Destruction Bound](/proofs/bit-destruction) — where Roth's theorem and Pillai enter
- [Path to Proof](/roadmap/path-to-proof) — how all pieces fit together
