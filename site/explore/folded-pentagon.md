---
description: "Modulo 5 the Collatz map folds onto a pentagon walk and forgets a residue at rate cos 36 degrees. Proved, sign-blind, and not progress on the conjecture."
---

# The Folded Pentagon

The cosine of 36 degrees is half the golden ratio: $\cos 36^\circ = \varphi/2 \approx 0.809$. That number is exactly the rate at which the Collatz map forgets a starting residue modulo 5, and the reason is a pentagon. Sort the five residues into three cells, and mass spread evenly within each cell moves under the map exactly as a random walk moves on a pentagon folded in half along its mirror; a pentagon walk forgets its start by a factor $\cos 36^\circ$ per step. This is proved, it belongs to the modulus 5 and to no other (multiples of 5 only inherit it), and it is a statement about residues only: it reads the same for $3x-1$ once every residue is negated, so it is not progress toward the Collatz conjecture.

This page is one thread of [Thirty-Six](./thirty-six), which asked whether four classical facts about 36 say anything about Collatz; the fact here was $\cos 36^\circ = \varphi/2$. The answer keeps the cosine and drops the 36: the angle is $180^\circ/5$, and the arithmetic is $5 = 3 + 2$.

## Two branches modulo 5

Use the shortcut map $T(n) = n/2$ for even $n$ and $(3n+1)/2$ for odd $n$. Modulo 5, halving is multiplying by 3 (because $2 \cdot 3 \equiv 1$), so the two branches become

$$\begin{aligned} e(x) &= \frac{x}{2} \equiv 3x, \\ o(x) &= \frac{3x+1}{2} \equiv 3 - x \pmod 5. \end{aligned}$$

The even branch is a multiplication of order 4 that fixes $0$. The odd branch is a **reflection**: apply it twice and you are back where you began, and it fixes $4 \equiv -1$. Which branch an integer takes is decided by its parity, and parity knows nothing about the residue modulo 5, so the object to study is the fair mixture of the two,

$$K_5 f(x) = \tfrac12 f\bigl(e(x)\bigr) + \tfrac12 f\bigl(o(x)\bigr),$$

the matrix that Matthews and Watts attached to Collatz-type maps modulo $m$ in 1985. Read on mass, it moves half of the mass at $x$ to $e(x)$ and half to $o(x)$. (It is not the operator of [The Transfer Operator](../connections/hilbert-polya) page, which is weighted, un-shortcut and modulo multiples of 6; nothing here depends on it.)

## The fold

<div class="theorem">

**Theorem A (folded pentagon; proved).** In $\mathbb{Z}/5$ call $\{1\}$ the apex, $\{2, 3\}$ the near pair and $\{0, 4\}$ the far pair, and spread mass evenly over each cell. One step sends the apex's mass to the near pair; the near pair's mass half to the apex and half to the far pair; the far pair's mass half to the near pair, while half stays; and every cell receives its mass evenly. So evenly spread mass stays evenly spread, and on it $K_5$ acts exactly as a simple random walk on a pentagon acts on mass that is symmetric about one vertex, the apex: the near pair is its two neighbours, the far pair the two far vertices. The eigenvalues are $1$, $\cos 72^\circ = 1/(2\varphi)$ and $\cos 144^\circ = -\cos 36^\circ = -\varphi/2$.

</div>

<div class="proof">

Three lines of arithmetic with fractions, before reducing modulo anything. The cells have rational names: the far pair is $\{0, -1\}$, the fixed points of the two branches; the near pair is $\{\tfrac12, -\tfrac12\}$; the apex is $-\tfrac14$.

- $e(0) = 0$, $o(0) = \tfrac12$, $e(-1) = -\tfrac12$, $o(-1) = -1$: the far pair goes to itself and to the near pair.
- $e(\pm\tfrac12) = \pm\tfrac14$, $o(-\tfrac12) = -\tfrac14$, $o(\tfrac12) = \tfrac54$: the near pair goes to the apex twice, and to $\tfrac14$ and $\tfrac54$.
- $e(-\tfrac14) = -\tfrac18$ and $o(-\tfrac14) = \tfrac18$.

Modulo 5 the loose ends close up: $\tfrac14 \equiv -1$, $\tfrac54 \equiv 0$, and $\{\tfrac18, -\tfrac18\} = \{2, 3\} = \{-\tfrac12, \tfrac12\}$. A pentagon's vertex, its two neighbours and its two far vertices exchange mass by the same three rules.

</div>

![Three panels. Left, the residues 0 to 4 on a pentagon in additive order, with blue arrows for the even branch x to 3x and orange arrows for the odd branch x to 3 minus x. Middle, the same residues placed by role with their fractions from the proof, 1 at the apex, 2 and 3 beside it, 4 and 0 at the bottom with a loop on each. Right, a regular pentagon of circumradius 1, the midpoint of a vertex's two neighbours on a dashed chord at height cos 72 degrees, the opposite side at distance cos 36 degrees, half the golden ratio](/data/collatz_folded_pentagon.png)

Where is $\varphi$? A step of the walk replaces each vertex by the average of its two neighbours. On a circle of radius 1, with the vertices joined in the usual order, that average sits on the vertex's own side of the centre at distance $\cos 72^\circ$ (the dashed chord in the right-hand panel). Joined as a star, the two neighbours are the ends of the opposite side, and their midpoint lies across the centre at distance $\cos 36^\circ$, the apothem (the bottom side). The larger, $\varphi/2$, is the factor by which the memory of the start shrinks at each step.

## On actual integers

<div class="corollary">

**Corollary (proved; checked by brute force for every $k \le 16$).** Fix $k$ and take the $2^k$ integers $n \equiv 1 \pmod 5$ in any stretch of $5 \cdot 2^k$ consecutive integers. The residues $T^k(n) \bmod 5$ are distributed exactly as a simple random walk on a pentagon after $k$ steps: residue $1$ is the start, $\{2, 3\}$ its neighbours, $\{0, 4\}$ the far vertices. The proportion back at residue 1 is

$$\frac{2^k + 2(-1)^k L_k}{5 \cdot 2^k},$$

where $L_k = 2, 1, 3, 4, 7, 11, 18, \dots$ are the Lucas numbers, and the distance from the uniform distribution decays at rate exactly $\cos 36^\circ = \varphi/2$ per step.

</div>

For $k = 8$ the 256 integers land $57, 70, 36, 36, 57$ on the residues $0, 1, 2, 3, 4$. The proof is two classical facts: the last $k$ binary digits of $n$ decide its first $k$ parities, and each of the $2^k$ parity patterns comes from exactly one such ending (Terras); and those digits are independent of $n \bmod 5$ (the Chinese remainder theorem). The return counts $1, 0, 2, 0, 6, 2, 20, 14, 70, \dots$ are [OEIS A054877](https://oeis.org/A054877), closed walks on a pentagon, where the Lucas formula already appears. Those numbers are known; the addition here is that $T^k(n) \bmod 5$ produces them.

Below, move the start off residue 1 and the two laws part company; switch to $3x-1$ and the same pentagon returns with every residue negated.

<PentagonWalk />

## What the fold is not

- **The five residues do not walk on a pentagon.** The matrix $2K_5$ has characteristic polynomial $x(x-1)(x-2)(x^2+x-1)$; a pentagon has $(x-2)(x^2+x-1)^2$, and no relabelling turns one into the other (proved). The fold is essential: residue 2 always goes to the apex and residue 3 always to the far pair, and only their even mixture behaves like a pair of pentagon vertices.
- **Only the start $n \equiv 1$ gives the pentagon law.** From $n \equiv 2$ every integer lands on residue 1 after one step, where a walker on a neighbouring vertex would split evenly. No relabelling of the residues rescues the starts 0, 2, 3, 4 (all 120 labellings checked). The rate $\varphi/2$ still holds from every start: after 1, $-\cos 36^\circ$ is the eigenvalue of $K_5$ largest in size, and its eigenvector has no zero entry.
- **It is not the pentagon you would draw first.** The fold gives the pentagon 1–2–4–0–3 (or equally 1–2–0–4–3: it cannot tell the two far residues apart), not the additive pentagon 0–1–2–3–4 or its pentagram.
- **Folding a pentagon is textbook.** It is the quotient of the 5-cycle by a reflection (Godsil and Royle, *Algebraic Graph Theory*). The only content of Theorem A is that the $3x+1$ map modulo 5 has this quotient. A short search did not turn that up; it is elementary and may be folklore.

## Why 5: one half is the golden ratio

Call the two multipliers $a = 1/2$ and $b = 3/2$. Always $b = a + 1$, because $3 = 2 + 1$. Modulo 5, where $a \equiv 3$ and $b \equiv 4$, two more things happen at once: $b = a^2$ and $b = -1$. The first says $a^2 = a + 1$: **one half is the golden ratio of the field with five elements**. The second makes the odd branch a reflection, which needs $3/2 \equiv -1$, that is, a modulus dividing $3 + 2$. So $5 = 3 + 2 = 3^2 - 2^2$ is the only modulus prime to 6 at which a branch of the map is an involution, and the only one at which the three lines of the proof close up (both proved).

## Only 5: elsewhere an eigenvalue leaves the real line

<div class="theorem">

**Theorem B (proved for every modulus).** Let $N \gt 1$ be prime to 6, and call *level $N$* the part of the chain modulo $N$ that is new at $N$, not already visible modulo a smaller divisor. At level 5 every eigenvalue of $K$ is real: $\tfrac12$, $0$, $\cos 72^\circ$ and $-\cos 36^\circ$. At every other level the squares of the eigenvalues sum to zero and the eigenvalues are not all zero, so some of them are not real. Hence 5 is the only level at which every eigenvalue is the cosine of a rational angle.

</div>

The proof counts fixed points. The trace of $A_N = 2K_N$ counts those of the two branches, $x = 0$ and $x = -1$. The trace of $A_N^2$ counts those of the four two-letter words; three of them have exactly one. The fourth, odd then odd, is $x \mapsto (9x+5)/4$, whose fixed points solve $5(x+1) \equiv 0$: one solution, or five when 5 divides $N$. So

$$\operatorname{tr} A_N = 2, \quad \operatorname{tr} A_N^2 = 3 + \gcd(5, N),$$

and it is $9 - 4 = 5$ again. Level by level, the squared eigenvalues of $A$ sum to 4 at level 5 and to 0 at every other level above 1; real numbers whose squares sum to zero all vanish, and the thread shows that they do not. Both trace formulas were also checked by direct count for $N \le 5000$.

**Census (computed, exact).** Over all 132 moduli prime to 6 from 5 to 400, and over every prime up to 7993, the golden pair at level 5 is the only irrational eigenvalue that is the cosine of a rational angle. The only other such cosines are $0$ and $\pm\tfrac12$. Whether this holds at every modulus is open. As a control, the $5x+1$ map has no irrational cosine at any modulus up to 200, and its only all-real level in that range is 3. The pentagon tells the multiplier 3 from the multiplier 5. It does not tell $+1$ from $-1$.

## Eleven, and three primes without an explanation

A theorem proved earlier in this project (Theorem C in the thread README) puts eigenvalues of the form $\tfrac12$ times a root of unity in the spectrum of $K_p$ whenever 3 has even order modulo the prime $p$. A scan of every prime up to 7993 (computed) finds further eigenvalues of that form at only three primes, 11, 31 and 37, and a stranger of another kind at 41.

- **11 is explained (proved).** Replace the two branches by $x/d$ and $((d+1)x+1)/d$ (Collatz is $d = 2$; for larger $d$ this is a formal mixture, not the residue chain of a map). The eigenvalue $+\tfrac12$ appears when $p$ divides $d^2 + d - 1$ and $-\tfrac12$ when $p$ divides $d^2 + 3d + 1$; at $d = 2$ these are 5 and 11. At 5 the eigenvector sits on the two fixed points $\{0, -1\}$; at 11 on the trivial cycle $\{1, 2\}$, whose two outside preimages, $4$ and $1/3$, coincide modulo 11 (the $+\tfrac12$ at 11 then follows from a symmetry of its spectrum). Both conditions say that the divisor 2 is, up to sign, a power of the golden ratio of the field: $2 \equiv -\varphi \pmod 5$ and $2 \equiv -\varphi^2 \pmod{11}$.
- **31, 37 and 41 are not explained.** At 31 there is an extra $+\tfrac12$; at 37 both $+\tfrac12$ and $-\tfrac12$ occur twice; at 41 there are five eigenvalues with $(2\lambda)^5 = -3$. Computed searches found no eigenvector carried by two points or by any small set, and no third low-degree condition on $d$. The base rate is high: at $p = 37$, 9 of the 34 members of that family have a $\pm\tfrac12$ beyond the theorem's, so chance is not excluded. That $37 = 36 + 1$ has no mechanism behind it, and reading 36 into it would be numerology.

## What this page does not claim

- **Nothing about the conjecture, and nothing about 36.** Every statement here is about residues modulo $N$, and every one is sign-blind: for $3x-1$ Theorem A holds with every residue negated (apex 4, near pair 2 and 3, far pair 0 and 1; checked directly). The $3x-1$ map has cycles of its own, such as $5 \to 7 \to 10 \to 5$, so nothing that fails to see the sign can settle $3x+1$. The exponent pair $(2,2)$ enters once, as the two-letter word odd then odd in Theorem B, and not as the number 36.
- **No ladder.** Elsewhere in this project the golden ratio enters through approximation, a ladder of ever better fractions. Here $\varphi/2$ is exact and there is no ladder: no golden eigenvalue at the levels 25, 125 or 55, nor at the Fibonacci and Lucas primes 11, 13, 29, 89, 199 (computed; the extra eigenvalues at 11 are $\pm\tfrac12$). $\cos 36^\circ = \varphi/2$ is a fact about the $3x+1$ map modulo 5, and it is a fact about the regular pentagon.

## Where this lives in the repo

- Research note: [Thirty-Six](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Thirty-Six.md), section 1
- Thread, with every proof, table and the skeptic pass: [`scripts/thirty_six/golden_kernel/README.md`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/golden_kernel/README.md)
- Scripts there: `q31_pentagon.py` (Theorem A), `q32b_real_spectrum_theorem.py` (Theorem B), `q32_kronecker_census.py` (census), `q34c_family_base_rate.py` (the two golden conditions), and `verify/` (the second pass, with separate code)
- This page's figure and the check of the interactive counts: `scripts/thirty_six/site_figures/fig_folded_pentagon.py`, `check_pentagon_walk.mjs`
- Companion page: [Thirty-Six](./thirty-six)
