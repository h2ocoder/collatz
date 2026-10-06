# Thirty-Six

**Status:** Exploratory, skeptic-checked (2026-10-06). Five threads, each investigated and then attacked by an independent reviewer who re-derived every claim with separate code, ran the 3x−1 and 5x+1 controls, and searched prior art. Nothing here is a step toward the conjecture: every Collatz-facing statement is sign-blind or residue-only.
**Companion:** [[Lattice Path Formula]], [[Collatz Transfer Operator Spectrum]], [[Dropping Set]], [[Dropping Time]], [[Dropping Destination]], [[Orbital Oddity]], [[The +1 Perturbation]]
**Scripts:** `scripts/thirty_six/` (index in its `README.md`; one directory per thread, each with a `verify/` folder)

## The question

Four facts about 36 = 2²·3²: it is triangular and square; it is the sum of the first three cubes; it is the least n with exactly eight solutions of φ(x) = n; and cos 36° is half the golden ratio. Do any of them say something about orbits, dropping orbits or dropping classes?

**Working hypothesis.** Each fact is a fact about the point (2,2) of the exponent lattice of the numbers $2^a 3^b$, the lattice on which a parity word with $k$ halvings and $s$ triplings is a monotone path, a [[Dropping Set]] is a family of paths on one side of the line of slope $\log_2 3$, and a cycle in the cell $(k,s)$ needs $2^k - 3^s$ to divide the word constant.

**Verdict on the hypothesis.** Half right. Every fact does land on that lattice, but at three different places, and 36 itself is almost never the input:

| Fact | Where it lives | What does the work |
|---|---|---|
| triangular and square | the cell $(3,2)$ | the pair $(8,9)$: $3^2 - 2^3 = 1$ |
| sum of the first three cubes | exponent point $(2,2)$ | the signature $p^2q^2$, and $T_3 = 6 = 2\cdot 3$ |
| eight solutions of φ(x) = 36 | exponent point $(2,2)$ | the primes 7, 19, 37 at the lattice points $(1,1)$, $(1,2)$, $(2,2)$ |
| cos 36° = φ/2 | the modulus 5 | $5 = 3 + 2 = 3^2 - 2^2$ |

Conventions below: shortcut map $T(n) = n/2$ or $(3n+1)/2$; $N(s)$ is OEIS A100982; repo [[Dropping Time]] counts un-shortcut steps, so Dropping Set index $= k + s$.

## 1. cos 36° = φ/2: Collatz modulo 5 is a folded pentagon

`scripts/thirty_six/golden_kernel/`. The kernel is $K_N f(x) = \tfrac12 f(x/2) + \tfrac12 f((3x+1)/2)$ on $\mathbb{Z}/N$ (the Matthews–Watts matrix); see [[Collatz Transfer Operator Spectrum]].

**Theorem A (folded pentagon; proved).** In $\mathbb{Z}/5$ put $Y = \{1\}$, $Z = \{2,3\}$, $X = \{0,4\}$. Measures uniform on these cells stay uniform on them, and on such measures $2K_5$ is the adjacency operator of a 5-cycle restricted to functions symmetric about a vertex: $Y$ is the vertex, $Z$ its neighbours, $X$ the far pair. Its eigenvalues are $2$, $2\cos 72°$, $2\cos 144°$, so the chain forgets at rate $\cos 36° = \varphi/2$, the apothem of the unit pentagon.

**Corollary (integers).** Over the $2^k$ integers $n \equiv 1 \pmod 5$ in a period $5\cdot 2^k$, the residue $T^k(n) \bmod 5$ has exactly the $k$-step law of a simple random walk on a pentagon, and

$$P\bigl(T^k(n) \equiv 1 \mid n \equiv 1\bigr) = \frac{2^k + 2(-1)^k L_k}{5\cdot 2^k}, \qquad L_k \text{ the Lucas numbers}.$$

The numerators are OEIS A054877 (closed walks on a pentagon); the formula is prior art, the identification with $T^k(n) \bmod 5$ is what this adds.

What it is **not**: the five-state chain is not itself a pentagon walk (characteristic polynomial $x(x-1)(x-2)(x^2+x-1)$ against $(x-2)(x^2+x-1)^2$), only the start $n \equiv 1$ gives the pentagon law, and the pentagon is $1$–$2$–$4$–$0$–$3$, not the additive pentagon of $\mathbb{Z}/5$. "$x \mapsto x/2$ turns sides into diagonals" is true and is not the mechanism.

**Why 5.** Modulo 5 the branch multipliers are $a = 1/2 \equiv 3$ and $b = 3/2 \equiv 4$, and $b = a + 1 = a^2 = -1$. So $1/2$ is the golden ratio of $\mathbb{F}_5$ and the odd branch is a reflection; $5$ is the only modulus prime to 6 at which a branch is an involution.

**Theorem B (only 5; proved for every N).** For $\gcd(N,6) = 1$: $\operatorname{tr}(2K_N) = 2$ and $\operatorname{tr}((2K_N)^2) = 3 + \gcd(5,N)$, because the word "odd, odd" is $x \mapsto (9x+5)/4$ and $9 - 4 = 5$. Hence on every level $N \ne 5$ the eigenvalues have sum of squares 0 and are not all real. $N = 5$ is the only level whose whole spectrum is cosines. Ingredients checked for $N \le 5000$.

**Census (computed, exact).** Over all 132 moduli prime to 6 up to 400, and all primes up to 7993, the golden pair at level 5 is the only irrational cosine eigenvalue; elsewhere the only cosines are $0$ and $\pm\tfrac12$. Conjecture: this holds at every level. For 5x+1 there is no irrational cosine at any level up to 200.

**The exceptional primes of the half-circle ladder.** The September conjecture on $|\lambda| = \tfrac12$ eigenvalues had unexplained exceptions 11, 31, 37.

- **11 is explained (Proposition F, proved).** In the family "$x/d$ and $((d+1)x+1)/d$", $\delta_{-1} - \delta_0$ gives eigenvalue $+\tfrac12$ when $p \mid d^2 + d - 1$, and the 2-cycle $\{x_0, d x_0\}$ gives $-\tfrac12$ when $p \mid d^2 + 3d + 1$. Both conditions have discriminant 5. At $d = 2$ they read $p = 5$ and $p = 11$; at 11 the 2-cycle is the trivial Collatz cycle $\{1,2\}$. Explicit eigenvectors checked on all 585 roots with $p \le 2000$.
- **Proposition F′ (found by the skeptic; proved).** The eigenvalue $-\tfrac12$, with multiplicity, is the same for $d$ and $1/d$.
- **31 and 37 are not explained.** No second two-point identity, no small configuration, no third low-degree condition. At 37 both $+\tfrac12$ and $-\tfrac12$ are double. A new exception of another kind appeared at 41: $(2\lambda)^5 = -3$. No further exceptional prime up to 7993. Base rate: in the family $(d+1, d)$ about a quarter of the kernels at $p = 37$ are exceptional (9 of 34), so chance is not excluded.

**Eigenvalue 0 (Proposition E′, found by the skeptic; proved).** For every prime $p \ge 5$ the eigenvalue 0 of $K_p$ is semisimple, with multiplicity $(p-1)/\operatorname{ord}_p(3)$ when that order is even and 0 otherwise. The proof is a Jacobi-sum pairing whose determinant is a non-zero multiple of the Gaussian periods of $\langle 3\rangle$. At composite levels $N = p^2q$ the multiplicity doubles iff $p \nmid \operatorname{ord}_q(3)$ (computed; it predicted six levels correctly before they were run; not proved).

**Nulls.** The link to the icosian Fibonacci ladder is only the field $\mathbb{Q}(\sqrt5)$, not a mechanism. Pierpont primes $2^a3^b + 1$ (such as 37) are not special for the kernel. "37 = 2⁶ − 3³" explains nothing: the same construction fails at $p = 181$.

**Mirror.** The kernel of 3x+c is conjugate to that of 3x+1 for $c$ prime to $N$, so all of this is sign-blind. It does separate the multiplier 3 from 5 and 7.

## 2. Triangular and square: the pair (8,9) and the −5 cycle

`scripts/thirty_six/harmonic_cycles/`. $36 = T_8 = 8\cdot 9/2$, and $(8,9) = (2^3, 3^2)$ is the last pair of consecutive 3-smooth numbers (Levi ben Gerson, 1343).

**Dictionary (prior art, assembled).** $T_n$ is 3-smooth iff $n \in \{1,2,3,8\}$, giving $T = 1, 3, 6, 36$. These are the four cells with $|2^k - 3^s| = 1$, where every word has an integer fixed point, and they hold exactly the cycles $\{0\}$, $\{-1\}$, $\{1,2\}$, $\{-5,-7,-10\}$. The cycle through $-17$ is the first that needs a real divisibility accident ($2^{11} - 3^7 = -139$).

**One-even-element theorem (proved; the $b = 1$ case of the Davison–Steiner circuit equation).** The word $1^a0$ closes on an integer iff $|2^{a+1} - 3^a| = 1$ iff $6^a$ is triangular iff $a \in \{0,1,2\}$. In the coordinate $v = n + 1$, where the odd step is $v \mapsto 3v/2$, the $-5$ cycle is $-4 \to -6 \to -9$ and $36 = (-4)(-9) = (-6)^2 = T_8$. This is the one place where 36 appears with a mechanism, and the mechanism is $9 - 8 = 1$. It holds verbatim for 3x−1.

**Why 3 (proved, elementary).** For odd $q$, $|2^k - q^s| = 1$ forces $s \le 1$ unless $(q,k,s) = (3,3,2)$. So 3 has four unit cells, $q = 2^j \pm 1$ has two, every other multiplier has one.

**Link to the half-eigenvalue theorem (Proposition 7′, found by the skeptic).** The functional behind "$-\tfrac12\chi(2) \in \operatorname{spec}(K_p)$" is attached to one word at a time and exists exactly when that word's cell has $2^k - 3^s = -1$. For $T$ itself that is the cell $(1,1)$, i.e. $3 = 2 + 1$. The cell $(3,2)$, i.e. $9 = 8 + 1$, carries the same functional in the two-branch kernel $(x/8,\ (9x + C)/8)$, anchored at the $-5$ cycle.

**Intervals.** The cells of the five known cycles are $3^s/2^k = 1/2,\ 3/2,\ 3/4,\ 9/8,\ 2187/2048$: octave, fifth, fourth, whole tone, apotome. As a law this is a tautology plus a size constraint: in the 3x+c control family 21% of 257 cycles sit at record cells overall and about 60% of the size-matched ones, and all five cycles of 5x+1 do too.

**Curiosity.** $n = -37$ is on the $-17$ cycle: in $v$ its first run is $-(16, 24, 36, 54, 81)$. Equivalently 37 is on the 3x−1 cycle of 17. Shared by 16, 24, 54, 81; base rate not small.

## 3. Triangle, square, cube: three 2-adic types

`scripts/thirty_six/figurate_2adic/`. Dropping classes are residue classes mod $2^k$, so a figurate family meets them as a map on $\mathbb{Z}_2$.

- **Triangular = fold.** $T_0,\dots,T_{2^k-1}$ is a complete residue system mod $2^k$; $n \mapsto T_n$ is exactly 2-to-1 with fibres $\{n, -1-n\}$ (classical: triangular hash probing). So among the first $2^K$ triangular numbers exactly $N(k)\,2^{K-k}$ lie in the class of level $k$: the natural law, for every rule.
- **Cube = isometry** on odd residues; natural law again.
- **Square = collapse** onto $1 + 8\mathbb{Z}_2$ (image measure $1/6$).
- **Polygonal trichotomy (proved).** For $s$-gonal numbers the type is decided by $v_2(s-2)$: 0 fold, 1 collapse, $\ge 2$ isometry.

**Theorem 2′ (squares see the sign; found by the skeptic, proved).** For the rule $(qn+d)/2$, squares (and sums of cubes $T_n^2$) meet exactly two dropping classes iff the parity word of 1 drops within three letters: $q = 3$ with $d \equiv 1 \pmod 4$, or $q \in \{5,7\}$ with $q + d \equiv 0 \pmod 8$. For 3x+1 every square $> 1$ is in Set₁ or Set₃; for 3x−1 the odd squares spread over infinitely many classes (103 distinct stopping times for $n \le 2\cdot10^5$). This is the only figurate statement here that separates 3x+1 from 3x−1, and it does so through $n \bmod 4$ alone.

**The mirror.** Bitwise NOT, $n \mapsto -1-n$, commutes with $x \mapsto 3x+1$ and conjugates $T$ to the shifted 3x−1 map (known). A function is NOT-invariant iff it is a function of $T_n$, so $T_n$ is the complete mirror-even coordinate, and anything read through it is forced to be sign-blind.

**First-run law (textbook, restated).** The first run of the parity vector of $n$ has length $v_2(n) + v_2(n+1) = v_2(T_n) + 1$; $T_n$ is half the product of the distances from $n$ to the branch fixed points $0$ and $-1$.

**Where 36 is genuinely unique.** Ljunggren (1946): the only triangular numbers whose square is triangular are 0, 1, 6. So 36 is the only sum of the first $n$ cubes ($n > 1$) that is triangular.

## 4. Eight solutions: totient fibres as lattice partitions

`scripts/thirty_six/totient_lattice/`. $\varphi(x)$ is 3-smooth iff $x = 2^\alpha 3^\beta \times$ (distinct Pierpont primes $2^i3^j + 1 > 3$).

**Theorem (generating function; standard argument, proved).** With $A(a,b) = \#\{x : \varphi(x) = 2^a3^b\}$ and $P$ the set of Pierpont points,

$$\sum_{a,b} A(a,b)\,X^aY^b = \Bigl(1 + \frac{1}{1-X}\Bigr)\Bigl(1 + \frac{X}{1-Y}\Bigr)\prod_{(i,j)\in P}\bigl(1 + X^iY^j\bigr).$$

At $(2,2)$: $A = 1 + 2 + 3 + 2 = 8$, from the primes 7, 19, 37. The eight solutions 37, 57, 63, 74, 76, 108, 114, 126 are the eight ways to split the point $(2,2)$.

**Geometry to algebra (proved; Gleason 1988 plus Kummer theory).** If $\varphi(n) = 2^a3^b$, then $\cos(2\pi/n)$ is reached by exactly $a - 1$ square roots and $b$ angle trisections, and $b$ is the minimal number of trisections. Each of the eight polygons with $\varphi = 36$ needs one square root and two trisections. The decagon sits at $(2,0)$: one square root, no trisection, which is the statement $\cos 36° = \varphi/2$.

**Collatz side: null**, replicated on a disjoint range with a placebo test. Totient height, totient fibres and $A(a,b)$ carry no dropping-time information beyond $n \bmod 2^k$ and size; $A(a,b)$ is unrelated to A100982; nothing happens at the critical slope.

**Two exact by-products about [[Dropping Destination]] (elementary, sign-blind).** The number $M(d)$ of $n$ with destination $d$ is finite, equals 1 whenever $3 \mid d$, and is 3-adically locally constant: dropping *time* is 2-adic, destination *multiplicity* is 3-adic. This is the counting side of the repo's Dual Constraint (membership in Set$_k$ is 2-adic, destinations are locked mod $3^s$). Its mean is $\sum_s N(s)/3^s = 1.69036\ldots$; every multiplicity 1..18 occurs below $10^7$.

## 5. Sum of cubes: a solvable toy, and what is already known about N(s)

`scripts/thirty_six/nicomachus_paths/`. Liouville: $\sum_{d\mid n}\tau(d)^3 = \bigl(\sum_{d\mid n}\tau(d)\bigr)^2$; at $n = 36$ both sides are $36^2$.

**A baby Collatz that is completely solved (proved).** $F(n) = \sum_{d\mid n}\tau(d)$. Every orbit ends in a fixed point $1, 3, 18, 36$ or the 2-cycle $\{6,9\}$; $F(n) < n$ outside $\{1,2,3,4,6,8,12,18,24,36\}$. The fixed points are OEIS A097989. It is decidable because it contracts outside a finite set; it shares no structure with Collatz.

**Why 36 (proved; not found in the literature, elementary).** $\tau_k(p^2q^2) = T_k^2 = 1^3 + \dots + k^3$ for all primes $p \ne q$, so $T_k^2$ is a fixed point of the $k$-fold divisor function iff $T_k$ is a product of two distinct primes ($k = 3, 4, 5, 6, 10, 13, \dots$; fixed points $36, 100, 225, 441, \dots$).

**Dropping-word counts.** [[Lattice Path Formula]] should now cite **Winkler, arXiv:2609.22303 (14 Sep 2026)**: $N(s)$ is squeezed between two cycle-lemma binomials and equals a rational Catalan number exactly at the one-sided best approximations of $\log_2 3$. Added here, as corollaries of his Proposition 9 and Bizley (1954): the exact window of orders on which a rational slope reproduces $N(s)$, and closed forms at multiples of convergent denominators, e.g. $N(10) = 476$, $N(36) = 38\,088\,111\,350\,198$. Novelty of those values unknown. So "no ballot formula" is too strong: there are ballot formulas at the listed orders, and none of that type at $s = 8, 9, 11, 13, 14, 16$. Identical for 3x−1.

**Null.** No Nicomachus-type identity among Collatz path counts (209,434 multisets tested).

## What 36 is, after all five threads

- **Genuine, with a mechanism:** largest 3-smooth triangular number (pair $(8,9)$, the $-5$ cycle); largest attractor of $F$ (signature $p^2q^2$); first eightfold point of the totient (three Pierpont primes below $(2,2)$); only triangular sum of cubes (Ljunggren).
- **Not 36 but its neighbours:** the pentagon is $5 = 9 - 4$; the exceptional prime is $37$, unexplained.
- **Numerology, labelled as such in the thread files:** named Pythagorean intervals as a law; $F$ multiplying by $3/2$; "every dropping word passes through the cell $(2,2)$"; the dodecagon mod 37; $37 = 36 + 1$ read as $T_8 + 1$.

## Open leads

1. Prove the golden pair at level 5 is the only irrational cosine of the 3x+1 kernel at every level (true to $N = 400$ and all primes to 7993).
2. Explain 31, 37 and the binomial eigenvalues at 41.
3. Irreducibility of the generic factor of the level-$N$ characteristic polynomial (106 of 106 levels): a proof would settle the converse of the half-eigenvalue theorem up to linear factors.
4. The Bizley values $N(kQ_n)$ as a comment on OEIS A100982, after reading Winkler's two ResearchGate preprints.
5. The 3-adic structure of the destination multiplicity $M(d)$: is it unbounded, and does every multiplicity occur?
