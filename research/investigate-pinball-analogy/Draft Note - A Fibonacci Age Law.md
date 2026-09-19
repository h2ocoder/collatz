---
tags: [pinball, mirror-map, fibonacci, draft-note]
status: draft
created: 2026-09-19
jira: SCRUM-30
---

# A Fibonacci age law for an injective relative of the 3x+1 map, and numerical evidence for an open question of Reyes Jiménez

*Draft. Every theorem below has a proof in this note and a computational check in the repository. Section 6 lists what has and has not been checked in the literature; read it before citing anything here as new.*

## 1. The map

Replace the halving step of the Collatz map by n ↦ n − |n/2|:

    F(n) = 3n + 1  (n odd),      F(n) = n − |n/2|  (n even).

For n > 0 this is the Collatz map. For n < 0 the even step is n ↦ 3n/2, so on magnitudes m = |n|

    G(m) = 3m − 1  (m odd),      G(m) = 3m/2  (m even).                      (1)

More generally, for odd q ≥ 3 and c = ±1 let G_{q,c}(m) = qm + c (m odd), qm/2 (m even). The closest named relative is Mahler's map x ↦ (3x+1)/2, 3x/2 from the Z-number problem [Ma]; (1) differs in the odd branch, which is what makes it injective.

## 2. Elementary properties

**Proposition 1.** G_{q,c} strictly increases every m ≥ 1 and is injective. Its image is {m : q | m} ∪ {m even : m ≡ c (mod q)}, of density 1/q + 1/(2q) = 3/(2q). For q = 3 exactly half of all integers have no predecessor: m ≡ 1 (mod 3) or m ≡ 5 (mod 6) when c = −1.

*Proof.* qm + c > m and qm/2 > m for m ≥ 1. Odd m map to even values ≡ c (mod q); even m map to multiples of q. These images are disjoint, each branch is injective, and every element of the stated set is attained. ∎

**Proposition 2 (valuation transfer).** For odd b write qb + c = 2^a·u with u odd. The next odd value on the orbit of b is q^a·u. In particular its q-adic valuation is a = v₂(qb + c) when gcd(u, q) = 1, which always holds since qb + c ≡ c (mod q).

So G keeps, as a power of q, exactly the power of 2 that the Syracuse map discards.

## 3. The age law

Backward steps from m: **A**: m ↦ 2m/q, available iff q | m. **B**: m ↦ (m − c)/q, available iff m ≡ c (mod q) and m is even. At most one is available. Let age(m) be the number of backward steps until neither is, and let the *age word* record the steps taken.

**Theorem 1.** For every odd q ≥ 3, c = ±1 and t ≥ 1:
1. age words are exactly the words over {A, B} with no factor BB;
2. min(age(m), t) depends only on m mod 2q^t;
3. the number of residues mod 2q^t with age ≥ t is the Fibonacci number F(t+3) (F₁ = F₂ = 1). Hence P(age ≥ t) = F(t+3)/(2q^t).

*Proof.* (i) After B the value (m − c)/q is odd, because m − c is odd and q is odd; B requires an even value. After A the value 2m/q is even, so B's parity requirement is automatic there. Thus the only parity condition in a whole backward walk is on m itself, and only when the first step is B.
(ii) Each backward step has the form m ↦ (um + v)/q with u ∈ {1, 2} a unit mod q. After i steps the ancestor is (U m + V)/q^i with U a unit mod q. The requirement for step i+1 — ancestor ≡ 0 or ≡ c (mod q) — therefore selects exactly one of the q lifts of m mod q^i to m mod q^(i+1). By induction every BB-free word of length t occurs, determines m mod q^t uniquely, and distinct words determine distinct residues.
(iii) By the Chinese remainder theorem a word beginning with A corresponds to 2 residues mod 2q^t (parity of m free) and a word beginning with B to 1 (m even). BB-free words of length t number F(t+1) beginning with A and F(t) beginning with B, and 2F(t+1) + F(t) = F(t+3). ∎

**Corollaries.**
- Mean age = Σ_{t≥1} F(t+3)/(2q^t) = ½·[(2 + x)/(1 − x − x²) − 2] at x = 1/q; for q = 3 this is 11/10.
- The factor complexity of the language of age words is p(n) = F(n+2): it is the full golden-mean shift.
- Every positive integer has unique coordinates (seed, age word), where the seed has no predecessor. The integers are a disjoint union of G-rays.
- *Two clocks.* Forward, the run of even steps after odd b has length v₂(qb + c), geometric of ratio 1/2 under the uniform 2-adic measure. Backward, a run of A steps continues iff q divides the ancestor, geometric of ratio 1/q under the uniform q-adic measure.

Fibonacci here comes from the prime 2 (an odd value cannot take the odd-type step); q enters only through the denominator.

**Checks.** Exhaustive counts for q ∈ {3, 5, 7, 9, 11}, both signs of c, t ≤ 9 (q = 3); mean age 1.09999 over m ≤ 2·3¹¹; run-length tails to four decimals. `scripts/mirror_experiments.py`, `tests/test_pinball.py`.

## 4. The forward dual

Let T(n) = n/2 (n even), (3n+1)/2 (n odd). Reyes Jiménez [RJ, Thm 4.7] proves that exactly F(m+1) odd n ∈ {1, …, 2^m} have T^i(n) ≢ 4 (mod 6) for 1 ≤ i ≤ m − 1, via the spectral radius φ of the mod-6 transition graph with vertex 4 removed.

**Proposition 3.** For odd n, T^i(n) ≡ 4 (mod 6) for some 1 ≤ i ≤ m − 1 iff the Terras parity word of n of length m contains 00.

*Proof.* After an odd step the value is ≡ 2 (mod 3); halving it gives a value ≡ 1 (mod 3); values ≡ 1 (mod 3) arise in no other way, and no value after the first step is ≡ 0 (mod 3). A value is ≡ 4 (mod 6) iff it is ≡ 1 (mod 3) and even, i.e. iff it was produced by a halving and the next step is a halving. ∎

By the Terras bijection between parity words of length m and residues mod 2^m, words beginning with 1 and avoiding 00 correspond to F(m+1) odd residues. This reproves [RJ, Thm 4.7] in a few lines and identifies the counted set: **the n whose first Syracuse exponents are all ≤ 2.** Verified as an equality of sets for m ≤ 14.

| | forward [RJ] | backward (Theorem 1) |
|---|---|---|
| forbidden factor | 00 | BB |
| digit bijection | parity word ↔ n mod 2^m | age word ↔ m mod q^t |
| count | F(m+1) of 2^(m−1) | F(t+3) of 2q^t |
| status | selects a null set of orbits | holds for every integer |

## 5. An open question of Reyes Jiménez: evidence

[RJ, §5] asks whether every odd n > 2 eventually meets 4 (mod 6), and notes that an explicit bound m₀(n) ≤ f(n) on the first such level would settle it. By Proposition 3 this is:

> **(Q)** Does every integer n > 1 have two consecutive halvings in its Terras orbit? Equivalently: is some Syracuse iterate ≡ 5 (mod 8)?

Remarks not in [RJ]:
- **The 3x+1 conjecture implies (Q).** The odd Syracuse predecessors of 1 other than 1 are (4^j − 1)/3, j ≥ 2, reached with exponent 2j ≥ 4.
- **(Q) fails for negative integers**: −1 is fixed with exponent 1, and −5 ↦ −7 ↦ −5 uses exponents 1, 2. Any proof must use positivity.
- The 2-adic integers violating (Q) form a set of Hausdorff dimension log₂φ ≈ 0.694 (the 2-adic integers with infinite coefficient stopping time have box dimension H(log₃2) ≈ 0.950).
- An orbit violating (Q) is either a nontrivial cycle with all exponents ≤ 2 or divergent. Inside the family exponent 1 occurs for n ≡ 3, 7 (mod 8) and exponent 2 for n ≡ 1 (mod 8), so typical members grow: (Q) is a divergence-type question.

**Algorithm.** The residues mod 2^j whose first j steps avoid 00 form a tree with F(j+1) nodes at level j; carrying the exact value T^j(r) and the power 3^s lets each child be produced in O(1). Walk the tree to depth B and finish each of the F(B+1) leaves by direct iteration. Integers that leave the family earlier are pruned, so this is exhaustive for n < 2^B at cost O(φ^B) rather than O(2^B).

**Results** (`scripts/double_halving_rs`, Rust, 32 threads; cross-checked against the Python version at B = 24, 32, 40):

| B | leaves F(B+1) | time | longest survival | at n | steps / log₂n |
|---|---|---|---|---|---|
| 32 | 3,524,578 | < 0.1 s | 100 | 1,548,635,775 | 3.28 |
| 40 | 165,580,141 | 0.2 s | 129 | 971,145,319,023 | 3.24 |
| 48 | 7,778,742,049 | 10.5 s | 152 | 19,914,105,817,593 | 3.44 |
| 56 | 365,435,296,162 | 525 s | 173 | 66,107,737,450,688,865 | 3.10 |
| 60 | 2,504,730,781,961 | 3564 s | 200 | 1,138,814,298,721,115,263 | 3.33 |

**(Q) holds for every n below the largest bound in the table.** A model in which each further step is survived with probability φ/2 predicts record survival log₂n / log₂(2/φ) ≈ 3.27·log₂n; the records sit on that line. We conjecture m₀(n) ≤ 4·log₂n for n ≥ N₀.

**Self-generated digits.** For B = 60, among the 2.50·10¹² integers surviving their own 60 bits, the conditional probability of surviving one more step is 0.809017, 0.809017, 0.809016, 0.809018 at L = 60, 68, 76, 84, against φ/2 = 0.809017. Beyond step B the parity is no longer read from the digits of n but from digits produced by the iteration, and those leave the family at exactly the rate free digits would.

**The backward dual.** Banerji's conjecture [Ba] — backward Syracuse iteration with exponents ≤ 2, which on odd n is the deterministic map b(n) = (2n − 1)/3 or (4n − 1)/3 according to n mod 3, always reaches a multiple of 3 — admits the same algorithm with base-3 digits: survivors of t steps are 2^t of the 3^t odd residues mod 2·3^t. It holds for every odd n < 2·3³² ≈ 2^51.7 (longest survival 83 steps at n = 116,393,404,689,949; per-step survival 0.66667 against 2/3; records 1.78·log₂n against a model value 1.71). The exceptional set is 3-adic of dimension log₃2.

## 6. Related work and what has been checked

- [RJ] M.-A. Reyes Jiménez, *A Fibonacci theorem for Collatz trajectories via modular graph structure*, arXiv:2606.02621 (2026). Forward count; poses (Q). States that no prior Fibonacci count of that kind is known to the author.
- [Ma] K. Mahler, *An unsolved problem on the powers of 3/2*, J. Austral. Math. Soc. 8 (1968). The map (3x+1)/2, 3x/2.
- [AFS] S. Akiyama, C. Frougny, J. Sakarovitch, *Powers of rationals modulo 1 and rational base number systems*, Israel J. Math. 168 (2008); [FK] C. Frougny, K. Klouda, RAIRO-ITA 46 (2012). Base 3/2; step A is their digit-0 edge; backward structure is 3-adic [FK, Lemma 3.5].
- [Ba] Banerji (1996), via Lagarias's annotation: conjectures that backward Syracuse iteration with exponents ≤ 2 always reaches a multiple of 3 — a backward-time dual of (Q).
- [AGU] Albert, Gudmundsson, Ulfarsson, *Collatz meets Fibonacci*, arXiv:1404.3054. Fibonacci enumeration of Collatz-induced permutations.
- Both Lagarias annotated bibliographies (arXiv math/0309224, math/0608208) were text-searched: no entry for the map (1), for an injective variant of this form, or for a Fibonacci count of backward residues. OEIS has no entry for 1, 2, 3, 8, 12, 18, 27, 80, 120, …
- [Wi] G. J. Wirsching, *The Dynamical System Generated by the 3n+1 Function*, LNM 1681 (1998), and Discrete Math. 148 (1996). Per Lagarias's annotations: backward paths are encoded by blocks of 0s, admissible vectors of length m correspond to a unique class mod 3^m, and counts such as 2^(μ−1)·3^((μ−1)(μ−2)/2) appear with moduli 2·3^(i−1). **This is the same mechanism as Theorem 1(ii)** — backward admissibility is decided 3-adically — for the map T, where runs of halvings are unrestricted and the counts are not Fibonacci. Primary text not read.
- [Ge] D.-A. German, *The golden mean shift is the set of 3x+1 itineraries*, NKS 2004. Forward parity words of the unaccelerated map avoid 11.
- [Wk] M. Winkler, arXiv:1412.0519, *Fibonacci enumeration of parity blocks in Collatz trajectories* (title as currently shown): starting numbers s ≡ 1 (mod 4) with a given block length form F_{r−1} residue classes mod 2^(r+2). A forward Fibonacci count mod 2^k that predates [RJ].
- [MS] D. Merlini, N. Sala, *On the Fibonacci's attractor and the long orbits in the 3n+1 problem* (1999). Per Lagarias: a heuristic growth rate c = ½(1 + √(7/3)) for the inverse tree, the root of c² = c + 1/3 — a Fibonacci-type recursion from "an odd predecessor exists one time in three and costs two steps". Heuristic growth rate, not a residue count. Not read.
- Kohl's RCWA papers (2007, 2008) treat surjective non-injective maps; the injective non-surjective case is mentioned only as one where no general conclusion holds.
- Not accessed: the primary texts of [Wi], [MS], Kohl; zbMATH.

**Assessment.** Theorem 1 and Proposition 3 are elementary. We have not found them stated. The ingredients — no two consecutive odd steps, q-adic structure of backward division, Fibonacci counts from mod-6 graphs — are all known, so "folklore, apparently unrecorded" is the prudent description. The honest framing is: *an elementary backward, q-adic companion to the known forward Fibonacci counts [Ge, Wk, RJ], obtained by Wirsching's mechanism [Wi] applied to an injective relative of Mahler's map [Ma].*

## 7. Questions

1. Is there a single bijection explaining both Fibonacci counts, exchanging the roles of 2 and q?
2. Does a single G-ray have the Markov statistics (π_A = 2/3, P(B|A) = 1/2)? Measured (χ² on 200,000 steps, three rays), and of the same difficulty as the distribution of (3/2)^k mod 1.
3. Can (Q) be proved for cycles alone? Known m-cycle bounds (Simons–de Weger, Hercher) do not apply, because a cycle with all exponents ≤ 2 has unboundedly many local minima.
