---
description: "Four classical facts about 36, tested against the Collatz map: where each one lands, what was already known, and why none of it is progress on the conjecture."
---

# Thirty-Six

Four classical facts about one number. Thirty-six is triangular and square at once, $36 = T_8 = 6^2$. It is the sum of the first three cubes, $1^3 + 2^3 + 3^3$. It is the least $n$ for which $\phi(x) = n$ has exactly eight solutions, $\phi$ being Euler's totient. And $\cos 36^\circ$ is half the golden ratio. The Collatz map is made of the primes 2 and 3, and $36 = 2^2 \cdot 3^2$ is their squares multiplied. So: do any of the four facts say something about Collatz orbits?

A research run in October 2026 took the question apart in five threads, one per fact and one more on triangle, square and cube together. Each thread then got a second, adversarial pass with its own code: the claims re-derived or recomputed (each thread file lists the few that were not), the same statement run for $3x-1$ and $5x+1$, prior art searched. The answer is half a yes. Every fact does land on one object, the lattice of numbers $2^a 3^b$ on which a Collatz parity word is a path. But the four facts land at three different addresses, and 36 itself is almost never what does the work: the work is done by the pair $(8, 9)$, by the exponent point $(2, 2)$, and by the modulus $5 = 3 + 2$. **None of it is progress on the Collatz conjecture.** Every Collatz-facing statement below either holds equally for $3x-1$, a map with cycles of its own, or depends only on residues.

![Four small copies of the lattice of numbers 2^a 3^b, a counting factors of 2 across and b factors of 3 upward, each crossed by the line 2^a = 3^b. Top left: the consecutive pairs 1 and 2, 2 and 3, 3 and 4, 8 and 9 joined by links labelled 2:1, 3:2, 4:3 and 9:8, with the corner 72 = 8 times 9 ringed beside 36. Top right: arrows from 4 to 6 to 9 along one anti-diagonal, and a rectangle from 4 and 9 to the corner 36. Bottom left: the points 6, 18 and 36 highlighted in the shaded three-by-three block of divisors of 36, tagged 6 + 1 = 7, 18 + 1 = 19 and 36 + 1 = 37. Bottom right: links from 2 to 3 labelled 3 + 2 = 5 and from 4 to 9 labelled 9 - 4 = 5](/data/collatz_thirty_six_lattice.png)

In the figure: top row, the first fact; bottom left, the point $(2, 2)$ of the second and third; bottom right, the fourth.

## Four facts, three addresses

$T(n)$, with brackets, is the shortcut map, $n/2$ for even $n$ and $(3n+1)/2$ for odd $n$; $T_n$, with a subscript, is the triangular number $n(n+1)/2$. The **parity word** of $n$ lists its steps, 1 for odd and 0 for even. Every step halves and an odd step also triples, so a word of $k$ letters, $s$ of them 1, is a path to the lattice point $(k, s)$, the number $2^k 3^s$; that point, with its words, is the **cell** $(k, s)$. The one number a word carries back to itself is a fraction $C/(2^k - 3^s)$ with $C$ an integer (classical: Böhm and Sontacchi 1978, Lagarias 1990), so in a cell where $2^k - 3^s = \pm 1$ every word closes on an integer for free. One such cell is $(3, 2)$: the point $72 = 8 \cdot 9$, next to 36, and $T_8 = 36$ is half of it.

| Fact | Where it lives | What does the work |
|---|---|---|
| triangular and square | the cell $(3, 2)$ | the pair $(8, 9)$: $3^2 - 2^3 = 1$ |
| sum of the first three cubes | the exponent point $(2, 2)$ | the shape $p^2 q^2$, and $T_3 = 6 = 2 \cdot 3$ |
| eight solutions of $\phi(x) = 36$ | the exponent point $(2, 2)$ | the primes 7, 19, 37 at the points $(1,1)$, $(1,2)$, $(2,2)$ |
| $\cos 36^\circ$ is half the golden ratio | the modulus 5 | $5 = 3 + 2 = 3^2 - 2^2$ |

## Triangular and square: the last harmonic pair

The composer Philippe de Vitry asked which *harmonic numbers*, the numbers $2^a 3^b$ of medieval music theory, differ by one. Levi ben Gerson answered in 1343: only $(1,2)$, $(2,3)$, $(3,4)$ and $(8,9)$. To a musician those are the octave, the fifth, the fourth and the whole tone, and there the list stops. Thirty-six is the triangular number of the last pair, $T_8 = 8 \cdot 9 / 2$, and since $T_n$ is built from 2s and 3s only when $n$ and $n+1$ both are, the list of such triangular numbers is exactly as short: 1, 3, 6, 36 (proved; a corollary of Levi's theorem).

| Pair | Interval | Triangular number | Cell $(k, s)$ | Cycle of $T$ on the integers |
|---|---|---|---|---|
| $(1, 2)$ | octave 2:1 | 1 | $(1, 0)$ | $\{0\}$ |
| $(2, 3)$ | fifth 3:2 | 3 | $(1, 1)$ | $\{-1\}$ |
| $(3, 4)$ | fourth 4:3 | 6 | $(2, 1)$ | $\{1, 2\}$ |
| $(8, 9)$ | whole tone 9:8 | 36 | $(3, 2)$ | $\{-5, -7, -10\}$ |

Each pair is a cell with $2^k - 3^s = \pm 1$, and the four cells hold exactly these four cycles, one each (proved, and known: Steiner 1977, Lagarias).

<div class="theorem">

**Theorem (one even element; proved, and not new).** A cycle of $T$ on the integers with exactly one even element, parity word $1^a 0$, exists if and only if $2^{a+1}$ and $3^a$ are consecutive, if and only if $6^a$ is a triangular number, if and only if $a \in \{0, 1, 2\}$. The three cycles are $\{0\}$, $\{1, 2\}$ and $\{-5, -7, -10\}$ (the table's fourth, $\{-1\}$, has no even element). In the coordinate $v = n + 1$, where an odd step is just $v \mapsto \tfrac32 v$, the last one reads

$$-4 \;\to\; -6 \;\to\; -9, \qquad (-4)(-9) = (-6)^2 = 36 = T_8 .$$

</div>

This is the one place in the run where 36 appears in a Collatz statement with a mechanism, and the mechanism is $9 - 8 = 1$. The cycle climbs one anti-diagonal of the lattice, $4, 6, 9$, and the single even step $v \mapsto (v+1)/2$ carries $-9$ back to $-4$ because 9 and 8 are neighbours. Thirty-six is the product of the two ends: a by-product, never an input. The theorem is the case of a single even step ($b = 1$) of the circuit equation of Davison (1976) and Steiner (1977), where their divisibility condition collapses to "divides 1". And it does not see the sign: for $3x-1$ the same cell holds the cycle $5 \to 7 \to 10$, with $v = n - 1 = 4, 6, 9$.

**Why the multiplier 3.** For an odd multiplier $q$, the equation $\lvert 2^k - q^s \rvert = 1$ forces $s \le 1$ unless $(q, k, s) = (3, 3, 2)$ (proved, elementary; a special case of Catalan's problem). So 3 has four such cells, a multiplier $2^j \pm 1$ other than 3 has two, and every other odd multiplier has one. Only 3 has a cell at $s = 2$, and that cell is $9 = 8 + 1$.

**The fifth cycle, and a law that is not one.** The only other known cycle of $T$ on the integers runs through $-17$, in the cell $(11, 7)$, where $3^7 / 2^{11} = 2187/2048$ is the apotome of Pythagorean tuning. Octave, fifth, fourth, whole tone, apotome: it is tempting to hear a law, and it is a tautology plus a size constraint. Every ratio $3^s/2^k$ with small $s$ has a classical name, and a cycle that is large compared with the $+1$ is pushed toward the *record cells*, the best one-sided approximations of $\log_2 3$ (Crandall 1978, Eliahou 1993), where all five known cycles sit. Of the 257 primitive cycles of the maps $3x + c$, $5 \le c \le 199$, that meet $[-20000, 20000]$, 21% sit there too, and about 60% of those matched in size to the $-5$ and $-17$ cycles (53 of 89); the five known cycles of $5x+1$ all sit in record cells of $\log_2 5$ (computed). The pattern tells apart neither the sign nor the multiplier.

## Fold, collapse, rigid: how three shapes meet the dropping sets

A [dropping set](../foundations/definitions) $\text{Dset}_j$ holds the integers whose orbit first falls below its start after exactly $j$ steps, counting $3n+1$ and $n/2$ separately; the values of $j$ known to occur are 1, 3, 6, 8, 11, 13, ... The classes behind these sets are residue classes modulo powers of 2 (Terras 1976), so the way a family of numbers meets them is decided by the family modulo $2^k$. Triangle, square and cube do three different things there, all classical and none involving a Collatz rule:

- **Triangular numbers fold.** $T_0, \dots, T_{2^k - 1}$ hit every residue modulo $2^k$ exactly once, and $n \mapsto T_n$ glues $n$ to $-1-n$. (It is why triangular probing visits every slot of a hash table of size $2^k$: Hopgood and Davenport 1972.)
- **Cubes are rigid.** On the odd residues modulo $2^k$, cubing is a permutation that keeps every 2-adic distance: an isometry. (Even cubes stay even, in $\text{Dset}_1$.)
- **Squares collapse.** Every odd square is $1 \bmod 8$, and the squares cover only a sixth of the 2-adic integers.

A fold or a rigid map cannot disturb proportions, so triangular numbers and cubes carry the natural law of the dropping sets exactly. Among the first $2^K$ triangular numbers, half lie in $\text{Dset}_1$, a quarter in $\text{Dset}_3$, a sixteenth in $\text{Dset}_6$, a sixteenth in $\text{Dset}_8$, and so on down the list of [The Dropping Dictionary](./dropping-dictionary): the same shares as among all integers, exactly and not just on average. This is proved as a count of residues, and for actual dropping times in every class modulo $2^{24}$ or less (0 and 1, which never drop, excepted); in general it is Terras's coefficient stopping time conjecture. The residue statement holds for every rule, each with its own shares (for $5x+1$ they begin 1/2, 1/8, 1/16), so it distinguishes nothing. Squares are another matter.

<div class="theorem">

**Theorem (squares see the sign; proved; elementary, no novelty claimed).** Under $3x+1$ every square greater than 1 lies in $\text{Dset}_1$ (the even squares) or in $\text{Dset}_3$ (the odd ones), and nowhere else. Under $3x-1$ the odd squares spread over infinitely many dropping sets.

</div>

![Four bar charts of the share of the first 65,536 members of a family in each dropping set, with black ticks marking the share of all integers. Triangular numbers under 3x+1 and cubes under 3x+1 meet the ticks exactly in every set: 50 percent, 25 percent, 6.25 percent, 6.25 percent and on down. Squares under 3x+1 sit on two bars only, 50 percent each at dropping times 1 and 3. Squares under 3x-1 have 50 percent at dropping time 1, nothing at 3 or 6, and then bars spread over every later set](/data/collatz_thirty_six_figurate.png)

Computed: the squares of $2, \dots, 200{,}000$ show 103 different dropping times under $3x-1$, and exactly two under $3x+1$. (The sums of the first $n$ cubes are the squares $T_n^2$, and behave the same way.) This is the only statement about figurate numbers here that tells $3x+1$ from $3x-1$, and it does so with one bit. An odd square is $1 \bmod 4$ and never $3 \bmod 4$; under $3x+1$ the class $1 \bmod 4$ is a single dropping set, and under $3x-1$ it is the class $3 \bmod 4$ that is. A statement about $n \bmod 4$ cannot bear on the conjecture.

## Sum of cubes: a map that can be solved completely

Nicomachus: $1^3 + 2^3 + \dots + k^3 = T_k^2$. Liouville stretched it over the divisors of any $n$: $\sum_{d \mid n} \tau(d)^3 = \bigl(\sum_{d \mid n} \tau(d)\bigr)^2$, where $\tau$ counts divisors, and at $n = 36$ both sides are $36^2$: the inner sum $F(n) = \sum_{d \mid n} \tau(d)$ sends 36 to itself. So iterate $F$. It is multiplicative with $F(p^a) = T_{a+1}$, so $72 = 2^3 \cdot 3^2$ goes to $T_4 \cdot T_3 = 60$, and on:

$$72 \to 60 \to 54 \to 30 \to 27 \to 10 \to 9 \to 6 \to 9 \to 6 \to \cdots$$

<div class="theorem">

**Theorem (the divisor map $F$, completely solved; proved).** Every orbit of $F$ ends at one of the fixed points $1$, $3$, $18$, $36$ or in the 2-cycle $6 \leftrightarrow 9$. Outside the ten numbers $1, 2, 3, 4, 6, 8, 12, 18, 24, 36$, every $n$ has $F(n) \lt n$.

</div>

The fixed points are known (OEIS A097989); the full dynamics takes a few lines. **Why 36:** for any two distinct primes, $\tau_k(p^2 q^2) = T_k^2 = 1^3 + \dots + k^3$, where $\tau_k$ counts the ways to write a number as an ordered product of $k$ factors and $\tau_3 = F$. So for $k \ge 2$ the sum of the first $k$ cubes is a fixed point of $\tau_k$ exactly when $T_k$ is a product of two distinct primes: $k = 3, 4, 5, 6, 10, 13, \dots$ (OEIS A164977), giving $36, 100, 225, 441, \dots$ (proved; elementary; not found in a short OEIS and web search; no novelty claimed). The shape $p^2 q^2$ carries the cube identity for every pair of primes. That the primes are 2 and 3 is the accident $T_3 = 6$.

$F$ is a pleasant toy and shares none of what makes Collatz hard: it forgets the primes of $n$, keeps only their exponents, and outside ten numbers only counts down.

On the Collatz side of this thread, among the dropping-word counts $N(s)$ (how many parity words with $s$ odd steps end at their first drop: OEIS A100982, the letters of [The Dropping Dictionary](./dropping-dictionary)), the number 36 does nothing. What governs them is the continued fraction of $\log_2 3$, and the strongest statement is three weeks older than the run: Winkler's preprint (arXiv:2609.22303, 2026) squeezes $N(s)$ between two cycle-lemma binomials and shows that it meets a bound exactly when $s$ is the denominator of a one-sided best approximation of $\log_2 3$, where its value is a rational Catalan number. His Proposition 9 and Bizley's 1954 formula give closed forms at multiples of convergent denominators too, for instance $N(10) = 476$ and $N(36) = 38{,}088{,}111{,}350{,}198$ (proved given Bizley, and verified; the values are terms of A100982, and whether the closed forms are new is unknown). Thirty-six is on that list because $36 = 3 \cdot 12$ and 12 is a convergent denominator, not because $36 = 2^2 \cdot 3^2$. All of it is identical for $3x-1$.

## Eight solutions: eight ways to split the point (2, 2)

Euler's $\phi(x)$ is a number $2^a 3^b$ exactly when $x$ is a power of 2, times a power of 3, times distinct primes of the form $2^i 3^j + 1$ larger than 3 (Pierpont primes). Each ingredient brings a lattice vector: $2^\alpha$ brings $(\alpha - 1, 0)$, $3^\beta$ brings $(1, \beta - 1)$, and a Pierpont prime brings its own point $(i, j)$. Solving $\phi(x) = 2^a 3^b$ means splitting the point $(a, b)$ into such parts, and the number of ways has an exact generating function (proved; the standard multiplicative argument). Under $(2, 2)$ the usable primes are $7 = 6 + 1$, $19 = 18 + 1$ and $37 = 36 + 1$, at the points $(1,1)$, $(1,2)$ and $(2,2)$, and the count is $1 + 2 + 3 + 2 = 8$:

| Solutions $x$ | Built from | Parts of $(2, 2)$ |
|---|---|---|
| 108 | $2^2 \cdot 3^3$, no prime | $(1,0) + (1,2)$ |
| 63, 126 | $3^2 \cdot 7$, and twice that | $(1,1) + (1,1)$ |
| 57, 76, 114 | $3 \cdot 19$, $2^2 \cdot 19$, $2 \cdot 3 \cdot 19$ | $(1,0) + (1,2)$ |
| 37, 74 | $37$, and twice that | $(2,2)$ |

So $\phi(x) = 36$ has eight solutions exactly because 7, 19 and 37 are all prime. That 36 is the *least* number with eight (OEIS A007374) is a small-number accident: the count is structural, the word "least" is not.

The same lattice point measures a construction. Gleason showed in 1988 that a regular $n$-gon can be drawn with straightedge, compass and an angle trisector exactly when $\phi(n)$ has the form $2^a 3^b$. The point $(a, b)$ then counts the steps (proved here from Gleason's theorem and classical Kummer theory; whether his paper already states it was not checked): $\cos(2\pi/n)$ takes exactly $a - 1$ square roots and $b$ trisections, and no fewer trisections will do. So the eight polygons with $\phi(n) = 36$ each need one square root and two trisections. The decagon sits at $(2, 0)$: one square root and no trisection, which is the statement $\cos 36^\circ = (1 + \sqrt 5)/4$.

**The Collatz side is a null, and a replicated one** (computed). The totient height (how many steps $\phi$ takes to reach 1) shows no dependence on dropping times beyond $n \bmod 2^k$ and the size of $n$, on the odd $n$ from $5 \cdot 10^6$ to $10^7$ and again, with a placebo test, on the disjoint range up to $4 \cdot 10^7$; nor do the totient fibres (the $x$ sharing one $\phi(x)$) for totient values up to $10^5$. The solution counts show no relation to the counts $N(s)$ and no feature along the line $2^a = 3^b$. One elementary by-product, identical for $3x-1$: the number of integers whose first value below themselves is a given $d$ is finite, and is exactly 1 whenever 3 divides $d$ (proved; a multiple of 3 has no odd predecessor). Its average is the 1.69 of [The Dropping Dictionary](./dropping-dictionary).

## cos 36°: the folded pentagon

The fourth fact has a page of its own, [The Folded Pentagon](./folded-pentagon). Sort the five residues modulo 5 into three groups, and mass spread evenly within each group moves under the Collatz map exactly as a random walk moves on a pentagon folded along a mirror, so the memory of a starting residue fades by a factor $\cos 36^\circ$ per step (proved). It is special to 5, the only modulus prime to 6 at which every eigenvalue of the residue chain, the matrix of Matthews and Watts, is real (proved). The reason is $5 = 3 + 2 = 3^2 - 2^2$. The number 36 does not enter, and the same holds for $3x-1$.

## What 36 is, and is not

- **Genuine, with a mechanism.** The largest triangular number built from 2s and 3s (the pair $(8, 9)$ and the cycle through $-5$). A fixed point of $F$ (the shape $p^2 q^2$; that it is the largest is an accident of $k = 3$). An eightfold point of the totient (7, 19 and 37 are prime; that it is the first is a small-number accident). And the only sum of the first $n$ cubes beyond 1 that is triangular (Ljunggren 1946: the only triangular numbers with a triangular square are 0, 1 and 6). Only the first of these touches Collatz, and it reads the same for $3x-1$.
- **Not 36 but its neighbours.** The pentagon is $5 = 9 - 4$. On the companion page $37 = 36 + 1$ is one of three primes (31, 37, 41) with unexplained extra eigenvalues, and nothing found ties it to 36.
- **Numerology, listed so that nobody has to find it twice.** The named intervals as a law for cycles. $F(n) = 3n/2$ as "an odd Collatz step" (true at $n = 2, 4, 6, 12$ only). "Every dropping word with two or more odd steps passes through the cell $(2, 2)$" (true, and forced only because $3 \lt 4$).

## Where this lives in the repo

- Research note: [Thirty-Six](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Thirty-Six.md), the synthesis of the five threads
- Threads, each with its proofs, tables and a closing skeptic pass, under [`scripts/thirty_six/`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/README.md): [`harmonic_cycles`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/harmonic_cycles/README.md) (the pair 8, 9), [`figurate_2adic`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/figurate_2adic/README.md) (fold, collapse, rigid), [`totient_lattice`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/totient_lattice/README.md) (eight solutions), [`nicomachus_paths`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/nicomachus_paths/README.md) (the map $F$, dropping-word counts), [`golden_kernel`](https://github.com/h2ocoder/collatz/blob/main/scripts/thirty_six/golden_kernel/README.md) (the pentagon)
- This page's figures, and a script that recomputes the worked numbers printed here (the statistical nulls and the larger verifications stay with the threads): `scripts/thirty_six/site_figures/fig_thirty_six_lattice.py`, `fig_thirty_six_figurate.py`, `check_thirty_six_page.py`
- Companion pages: [The Folded Pentagon](./folded-pentagon), [The Dropping Dictionary](./dropping-dictionary), [Definitions](../foundations/definitions)
