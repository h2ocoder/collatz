# Matrix Multiplication Exponent

**Status:** Exploratory (2026-11-25, SCRUM-82). Read: the introduction, the obstruction, consequences and background sections, and the tripod section of the lower-bound paper; the introduction and growth section of the upper-bound paper; the Lean comparator statements. The long technical parts of the lower-bound proof were not checked. One script, with tests. Not skeptic-checked by an independent re-implementation. The lower-bound paper is one day old and unrefereed.

- **The paper.** OpenAI claims that the exponent of square matrix multiplication is exactly 9/4 over every field. The upper bound dates from 2 October 2026 and has independent expositions. The matching lower bound is new.
- **The question.** 9/4 = 3²/2², and in Collatz 3 is the multiplication and 2 is the division. Is that a relation?
- **The answer: no.** The square is real in the paper's own terms, but its 3 counts the three matrices (two inputs and the output) and its 2 counts the two ends of a shared index (§2). Neither is a multiplier or a divisor acting on integers.
- **On the Collatz side** 9/4 is the slope of two consecutive odd steps (§3.1). That is true, generic, and identical for 3x − 1, where the conjecture fails. A relation that cannot tell 3x + 1 from 3x − 1 carries no information about the conjecture (§3.3).
- **The kinds of number differ.** There 9/4 is an exponent; here it is a multiplier. The exponents the repo actually uses are logarithms and entropies built on log₂ 3, and none of them is 9/4 (§3.2).
- **What changes in the repo.** Nothing computational. One line in the proof-of-sequential-work vault changes status (§4).
- **What the comparison did produce.** A short account of where 9/4 comes from: it is 2 ÷ (1 − 1/3²), the largest value of a three-wire price on a tripod (§2.1). The same calculation with unequal wires gives the rectangular closed form in the release's Lean statement, which is (xy + yz + zx)² / (4xyz) (§2.3, derived here).

**Tags.** **[paper]** stated in the cited source and not re-derived. **[checked]** arithmetic or algebra verified by the script and a test. **[derived]** this note's own algebra, proved in the text and checked by the script; not in the sources as far as I read. **[analogy]** a resemblance with no mathematical content claimed.

**Trigger:** OpenAI, *The matrix multiplication exponent is nine fourths* (24 Nov 2026).
**Source:** `github.com/openai/math`, commit 92b516ef8e2a, licence Apache-2.0; `paper.pdf` SHA-256 ddde9ab7…766e5a01. No copy is kept in this repo.
**Script:** `scripts/matmul_exponent/nine_fourths.py`; outputs in `provenance.log`, `collatz.log` and `null.log` in the same folder. Tests: `tests/test_matmul_exponent.py`.
**Companion:** [[The +1 Perturbation]], [[Affine Orbit Structure]], [[Odd Stopping Time Spectrum]], [[Bit Destruction Bound]], [[Collatz Embeddings]], [[Dropping Zeta Spectrum]]. The two earlier checks of OpenAI preprints, *Exponential Time Hypothesis* and *Yang-Mills and QCD*, are uncommitted notes on the main checkout and are not on this branch.

## 1. What the paper claims

Sources are abbreviated **[LB]** (the lower-bound paper), **[UB]** (the 2 October upper-bound paper) and **[Lean]** (the comparator statements and scope note). Full references are at the end.

**Theorem 1.1 [paper, LB].** Over every field F, the exponent of square matrix multiplication is ω_F = 9/4. Here ω_F is the infimum of the s for which two n × n matrices can be multiplied in O(n^s) scalar operations, in formal arithmetic circuits with addition, subtraction, multiplication and division gates.

**Corollaries [paper, LB].**
- **Every size.** For every n ≥ 2, the geometric border rank of the n × n multiplication tensor is at least n^{9/4}, its asymptotic rank equals n^{9/4}, and a circuit needs at least ⌈n^{9/4}/2⌉ nonscalar multiplication or division gates.
- **Rectangular.** For an a × b matrix times a b × c matrix, border rank and asymptotic rank are at least max{ab, bc, ca, (abc)^{3/4}}. The dual exponent α (the largest β for which an n × n^β by n^β × n product has exponent 2) satisfies 1/2 ≤ α ≤ 2/3.
- **Conjectures refuted, if the theorem holds.** ω = 2 is false. Strassen's 1994 conjecture on tight tensors is false. The dyadic border-rank estimate proposed in the first version of a preprint by Sun is contradicted at n = 2⁸.

**How the lower bound is argued [paper, LB].** By contradiction. If ω were below 9/4 over some field, it would be below 9/4 over a finite field. A strict saving would then compress tensor networks on bits: applied a fixed number of times to a sorting network, the compression would test whether lists of words are distinct at a cost per input bit below a counting lower bound for that test. Most of the paper derives the compression from the strict saving.

**What the Lean statement says, and how it differs [paper, Lean].**
- The comparator file states three theorems: the square exponent is 9/4, the dual exponent is exactly 1/2, and a closed form for every rectangular format (§2.3). The scope note attributes them to four papers together.
- That is more than [LB] states. [LB] gives only 1/2 ≤ α ≤ 2/3 and the bound (abc)^{3/4}.
- The cost model differs. The Lean model counts additions, subtractions and multiplications in division-free programs that compute formal polynomial identities. [LB] counts only nonscalar multiplication and division gates.
- A Lean proof certifies its formal statement. I did not build the development.

**How far others have checked it.**
- **Upper bound.** [LB] cites independent expositions: Amanov, van den Berg and Zuiddam (arXiv:2610.30054), Shpilka (ECCC TR26-281), Doğan, Lysikov, Sakabe and Walter (arXiv:2611.09716), and extensions by Lü, Li and Uznański. A web search on 2026-11-25 found these and one more (arXiv:2610.28627). I opened none of them.
- **Lower bound.** Released on 24 November 2026 with eight other manuscripts. The same search found no reaction to it yet.

This note takes the theorem at face value and asks only what it would mean for this repo.

## 2. Where 9/4 comes from

Three derivations give the number. In each one the 3 and the 2 can be named.

### 2.1 Lower-bound paper: three wires and one shared label

**The setting [paper, LB].** A *price* is the logarithm of a quantity that multiplies under tensor products and cannot increase under linear maps. An index shared by two matrices is a *wire*; its price per unit of log-size is a distance between the two matrices. A label shared by all three has a price per unit called the common-label rate D.

- The n × n product has three indices i, j, k, and each is shared by exactly two of the three matrices. Its price is (sum of the three distances) · log n.
- A rank-r decomposition builds the same tensor from one label with r values shared by all three. Its price is D · log r.
- Prices cannot increase, so (sum of the three distances) · log n ≤ D · log r.

**The tripod [paper, LB].** Put the three matrices at the tips of a tripod with arms a₁, a₂, a₃, so that two tips are at distance aᵢ + aⱼ. The paper's Tripod principle says the common-label rate is at least

D\*(a) = a₁ + a₂ + a₃ − (1/a₁ + 1/a₂ + 1/a₃)⁻¹.

**The number [checked].** With unit arms, D\* = 3 − 1/3 = 8/3, the three distances sum to 3 × 2 = 6, and 6 ÷ (8/3) = 9/4. [LB] uses a tripod on which the rate equals 8/3 to get r ≥ n^{9/4}; that tripod appears inside the proof by contradiction.

**Why equal arms [checked].** The harmonic-mean term is at most (a₁ + a₂ + a₃)/9, by the arithmetic–harmonic mean inequality for three numbers. So D\* ≥ (8/9)(a₁ + a₂ + a₃), and the ratio 2(a₁ + a₂ + a₃)/D\* is at most

2 ÷ (1 − 1/3²) = 9/4,

with equality only at equal arms. [LB] uses exactly this to recover the upper bound and to show that at an extremal price every wire has length 3/4.

- **The 2** is "every index is shared by two matrices".
- **The 3²** is the arithmetic–harmonic mean inequality over three arms.
- **The denominator 4** is (3² − 1)/2. It is a power of 2 only because 3² − 1 = 2³.

Equivalently, 9/4 is the root of √λ = 3·√(λ − 2).

### 2.2 Upper-bound paper: three legs and a growth exponent

**[paper, UB].** Every spectral character gives the n × n product the value n^{3t}; the 3 is the number of legs of a trilinear form. The paper studies a profile P(a, b) of polynomial multiplication with input lengths a and b and shows:
- P(1, b) = b, and P(a, b) ≤ (a + b − 1)^{1/t} (interpolation);
- the increments of P do not increase in either length (discrete concavity);
- P(a, 3h + a − 1) ≥ 3·P(a, h) (shifted tripling: the support splits into three sectors).

These force P(a, a) ≥ a^{4/3}. Comparing growth rates gives t ≤ 3/4, so ω ≤ 3t = 9/4.

**The lemma's arithmetic [checked].** The extremal solution is Hₐ = ∏ (1 + 1/(3m)) over m < a, with Hₐ³ ≥ a and Dₐ = (3a − 1)Hₐ/2 ≥ a^{4/3}. Both inequalities hold exactly for a < 400, and the numerical growth exponent of Dₐ is 1.33335.

**Which 3 and which 2 [derived, a sensitivity check only].** At h = a the tripling inequality buys two extra copies of P(a, a) for 3a − 1 extra length. Replace that by "m extra copies for n·a − 1 extra length" and the same proof gives growth exponent 2m/n and the bound 3n/(2m). The script confirms the exponents numerically for five pairs (m, n). The paper is (m, n) = (2, 3), so

9/4 = (3 legs × 3 units of length) ÷ (2 arguments × 2 extra copies).

This family says nothing about tensors. It only shows which constant of the lemma each factor comes from.

### 2.3 The rectangular closed form

**The statement [paper, Lean].** For a product whose three indices have sizes N^x, N^y, N^z, sort the weights so that x ≥ y ≥ z. The exponent is

x + y + max(0, (x + y)z − xy)² / (4xyz).

**A symmetric form [derived, checked].** When (x + y)z > xy this equals

(xy + yz + zx)² / (4xyz),

and otherwise it equals x + y. The two forms agree exactly on a grid of 19³ rational triples, including zeros. This is not claimed as new: the formula is already in the release's Lean statement, and the companion papers, which I did not read, may well write it this way.

- **At (1, 1, 1)** it is 3²/4. The 3 is the number of pair products xy, yz, zx, one for each matrix.
- **On the family (1, 1, z)** with z ≥ 1/2 it is (z + 1/2)²/z, and it is 2 below. At z = 1 that is (3/2)², with 3/2 = 1 + 1/2: the side exponent plus the dual exponent.

**The closed form is the tripod bound [derived, checked].** Give the three tips the pair sums w = (x + y, y + z, z + x), which are the log-sizes of the three matrices. The three-wire price is Σ wᵢaᵢ. Then

sup over arms of (Σ wᵢaᵢ) / D\*(a) = the closed form.

*Proof.* Fix λ ≥ max w. The inequality Σ wᵢaᵢ ≤ λ·D\*(a) for all arms is the same as λ / (Σ 1/aᵢ) ≤ Σ (λ − wᵢ)aᵢ. By Cauchy–Schwarz, (Σ dᵢaᵢ)(Σ 1/aᵢ) ≥ (Σ √dᵢ)², with equality when aᵢ is proportional to 1/√dᵢ. So the inequality holds for all arms exactly when √λ ≤ Σ √(λ − wᵢ). The difference of the two sides increases with λ, so the supremum is the least λ ≥ max w that satisfies it. At λ = (xy + yz + zx)²/(4xyz) one has λ − (x + y) = (xz + yz − xy)²/(4xyz), and likewise for the other two, so the three square roots sum to √λ whenever all three numerators are non-negative. Otherwise λ = max w already satisfies the inequality. ∎

The script checks this three ways (`provenance.log`):
- at the optimal arms the ratio equals the closed form exactly, for all 18³ positive triples of the grid;
- no arms on a grid beat it, for eleven weight triples;
- an independent brute-force search agrees to 10⁻⁸.

**What this does and does not show.**
- **An upper bound, given the Tripod principle.** Any three sites have distances of the form aᵢ + aⱼ. At a spectral point normalised so that D = 1, the principle gives D\*(a) ≤ 1, so the product has value at most N raised to the closed form. Strassen's maximum formula then bounds the asymptotic rank. This is the argument [LB] gives for the square case, run with unequal weights. I did not check the proof of the principle.
- **Not the lower bound.** For unequal weights [LB] proves only max{pair sums, ¾(x + y + z)}, which lies below the closed form with equality only at x = y = z [checked]. [Lean] asserts equality.
- **Consistency [checked].** The closed form gives exponent 2 exactly up to z = 1/2. The bound ¾(2 + z) exceeds 2 only above z = 2/3. That is the gap between "α = 1/2" in [Lean] and "1/2 ≤ α ≤ 2/3" in [LB].

### 2.4 Summary: every 3 and every 2

| Derivation | Expression | The 3 | The 2 |
|---|---|---|---|
| [LB] three wires | 6 ÷ (8/3) | three matrices at three tips | a wire joins two tips, so it spans two arms |
| [LB] extremal price | 2 ÷ (1 − 1/3²) | mean inequality over three arms | each index is shared by two matrices |
| [UB] growth | 3 × 3/4 | three legs; 3a − 1 extra length | two extra copies; two arguments |
| [Lean] closed form | 3²/4, and (1 + 1/2)² | three pair products | the 4 of Cauchy–Schwarz; the dual exponent 1/2 |

In every row the 3 is a count of the three matrices of a bilinear map and the 2 is a count of pairs. The theorem holds over every field, including the fields with two and three elements **[paper]**, so no prime plays a special role.

## 3. The reading "3 is multiplication, 2 is division", tested

### 3.1 Where 9/4 is in Collatz [checked]

Let T be the shortcut map: odd n goes to (3n + 1)/2 and even n goes to n/2. Two steps of T are affine on each residue class mod 4:

| n mod 4 | T(T(n)) | slope |
|---|---|---|
| 0 | n/4 | 1/4 |
| 1 | (3n + 1)/4 | 3/4 |
| 2 | (3n + 2)/4 | 3/4 |
| 3 | (9n + 5)/4 | 9/4 |

- 9/4 is the slope of two consecutive odd steps. In the repo's terms it is the slope 3^s/2^(k−s) of [[Affine Orbit Structure]] with s = 2 odd steps among k = 4 steps of the unshortened map. `collatz.core` confirms (9n + 5)/4 for every n ≡ 3 mod 4 below 20000.
- The slopes 1/4, 3/4, 9/4 have densities 1/4, 1/2, 1/4. Their arithmetic mean is 1 and their geometric mean is 3/4.

Every number 3^s/2^m is the slope of some branch, so finding 9/4 among them is not a coincidence that needs explaining. It is the scaffold of [[The +1 Perturbation]]: the multiplicative part that is fully understood.

### 3.2 Exponent against multiplier [checked]

In the paper 9/4 is an exponent: log rank divided by log n. In Collatz 9/4 is a multiplier. Exponents add under tensor products; multipliers multiply under composition. To compare like with like, take the logarithm of the multiplier or look at the repo's own exponents:

| value | what it is |
|---|---|
| 1.584963 | log₂ 3, bits per tripling |
| 2.584963 | log₂ 6, the spectrum k = ⌈s·log₂ 6⌉ of [[Odd Stopping Time Spectrum]] |
| 0.207519 | 1 − ½·log₂ 3, drift in bits per shortcut step |
| 0.949956 | H(log₃ 2), the growth exponent of cycle words in `docs/plans/path-to-proof.md` |
| 1.169925 | log₂(9/4), bits gained by two odd shortcut steps |
| 2.250000 | ω |

None is 9/4. The Collatz exponents are built on log₂ 3, which is irrational. ω is rational because it is the optimum of an algebraic problem with rational data (§2.1).

### 3.3 The mirror test [checked]

The slopes do not depend on the offset. For 3x − 1, 3x + 5 and 3x − 5 the two-step slopes are again 1/4, 3/4, 9/4 with the same densities. But 3x − 1 has three cycles below 1000 (through 1, 5 and 17) where 3x + 1 has one.

Any statement that uses only the 3 and the 2 holds verbatim for 3x − 1. The repo's standing rule is that an argument about the conjecture must fail there. A relation between 9/4 and "multiply by 3, divide by 2" passes for 3x − 1 as well, so it cannot be about the conjecture.

### 3.4 The generalisation test [checked]

For ax + 1 the largest two-step slope is (a/2)²: 9/4, 25/4, 49/4, 81/4 for a = 3, 5, 7, 9. Only a = 3 lands between 2 and 3, the only interval an exponent of matrix multiplication can occupy.

On the matrix side there is nothing to vary in step with a. The exponent does not depend on the field or on any base. A relation would have to predict something for 5x + 1, and there is no candidate.

### 3.5 Look-elsewhere [checked]

There are seven rationals in [2, 3] with denominator at most 4: 2, 9/4, 7/3, 5/2, 8/3, 11/4, 3.
- Four of them are ratios of numbers of the form 2^i·3^j: 2, 9/4, 8/3, 3.
- Two are a power of 3 over a power of 2: 9/4 and 3.

So a simple answer to this problem had a better than even chance of being built from 2s and 3s, and a two-in-seven chance of being a Collatz slope. §2.4 explains why: a bilinear map has three matrices and its indices come in pairs.

### 3.6 Multiplication and division in the paper [paper, LB]

The circuit bound counts "multiplication or division gates" together. Each gate of either kind contributes at most two products of linear forms, which is where the ½ in ⌈n^{9/4}/2⌉ comes from. The two operations are on the same footing. In Collatz they are the two opposing branches.

A second difference: ω measures the cost of multiplying two unknowns. Collatz multiplies by the constant 3 and divides by the constant 2. Both are linear maps, and a linear map costs nothing in this model.

## 4. Does anything in the repo depend on ω?

**Computation.** On this branch the only dense linear algebra is one eigenvalue computation on a transition matrix (`collatz/zoo.py`), one singular value decomposition with a projection in `notebooks/09-collatz-embeddings.ipynb`, and vector norms in `collatz/embeddings/distance.py`. Nothing multiplies large matrices, and nothing would be faster. [UB] says its proof "does not specify a competitive finite matrix size". The lower bound changes no running time at all.

**Claims.** A search of every Markdown, Python, Rust, notebook, LaTeX and Lean file on this branch found no mention of matrix multiplication, Strassen, Coppersmith–Winograd or ω = 2 outside this note and its script. No claim here assumes a value of ω or the hardness of matrix multiplication.

**One line outside this branch (flagged, not edited).** `research/proof-of-sequential-work/Literature and Prior Art.md` is uncommitted on the main checkout. Its table of verification protocols quotes Thaler (2013): a matrix-product protocol with prover time T(n) + O(n²), "optimal … assuming there is no O(n²) time algorithm for matrix multiplication".
- If ω = 9/4, no arithmetic circuit multiplies matrices in O(n^{2+ε}) operations for any ε < 1/4. In the arithmetic-circuit model that assumption becomes a theorem.
- For time on a machine it remains an assumption.
- The vault's verdict does not rest on that line. The vault also cites a proof-of-useful-work scheme built on matrix multiplication (Komargodski–Weinstein, arXiv:2504.09971), noting that its security rests on an unproved conjecture. The vault read only the abstract, so whether ω = 9/4 bears on that conjecture is not known here.

## 5. Things that look like overlaps but are not

All **[analogy]**, with the reason each is not a link.

- **Prices are logarithms.** In [LB] a q-valued wire costs (distance) · log q, so a 3-valued index costs log₂ 3 times a 2-valued one. That is the trits-to-bits exchange rate that governs Collatz. It is a property of logarithms, shared by every theory that measures size in bits.
- **Limits of roots.** Asymptotic rank is the limit of the j-th roots of the ranks of tensor powers. The repo's growth exponents are limits of the same kind. The shared tool is subadditivity.
- **A tree from a valuation.** [LB] finds its tripod inside a tree "in which two branches meet at the valuation of the difference of their parameters". The 2-adic residue tree is built the same way: two integers share a branch down to the 2-adic valuation of their difference. The construction is the tree of any ultrametric. The field in [LB] is a field of series in a formal parameter t over an arbitrary base field, with rational exponents. Nothing in it is 2-adic.
- **An affine recurrence.** The obstruction argument iterates x ↦ h^{−γ}·x + h^η. A Collatz branch is n ↦ (3^s/2^k)·n + c. Both are contracting affine maps, and summing a geometric series is all they share.
- **Compression against a counting bound.** [LB] shows a faster algorithm would compress a computation below a counting lower bound. The repo has counting arguments too ([[Bit Destruction Bound]]). The resemblance is in the shape of the argument only.
- **Polynomial multiplication.** [UB] gets 9/4 from the tensor of polynomial multiplication. Multiplying an integer by 3 is multiplying its binary polynomial by 1 + x and then carrying. Polynomial multiplication has no carries, and the carries are where Collatz is hard.
- **3² − 2³ = 1.** In 2 ÷ (1 − 1/3²) the denominator is a power of 2 only because 3² − 1 = 2³. The same identity is why 3x − 1 has the cycle through 5 and 7: two odd steps and three halvings give (9n − 5)/8 = n, and the denominator 9 − 8 is 1 [checked: the cycle 5, 7, 10 of the shortcut map]. One elementary identity appears in two places.
- **The three slopes.** {ω − 2, ω/3, ω} = {1/4, 3/4, 9/4}, the three two-step slopes of §3.1 [checked]. This is one coincidence, not three: once ω = 9/4, the other two follow by arithmetic. On the matrix side ω − 2 is the excess over the size of the output and ω/3 is the wire length 3/4 at an extremal price.
- **Tuning.** 9/4 is two stacked fifths, 9/8 is the Pythagorean whole tone, and 8/3 is an octave plus a fourth, so 9/4 = 2 × 9/8 reads as an octave times a tone. Every Collatz slope 3^s/2^m is a Pythagorean interval; that is the reframe in [[Collatz Embeddings]]. What ties Collatz to tuning is the continued fraction of log₂ 3 ([[Dropping Zeta Spectrum]]), and the paper never touches log₂ 3.

## 6. What would count as a relation

None of these was found.
- A statement linking the two that fails for 3x − 1.
- A Collatz exponent (a logarithm, an entropy, a growth rate) equal to an exponent of a tensor.
- A bilinear map in the Collatz dynamics whose rank matters.
- A dependence of ω on the characteristic 2 or 3.

## Verdict

If the paper is correct it settles one of the central questions of algebraic complexity, and against the common expectation that ω = 2. For this repo it is a coincidence of small numbers.

- The 3 and the 2 in 9/4 count the three matrices of a bilinear map and the two ends of a shared index.
- On the Collatz side 9/4 is one slope of the multiplicative scaffold, the same for 3x − 1.
- The two 9/4s are different kinds of number: an exponent and a multiplier.
- Nothing in the repo computes with, or assumes anything about, fast matrix multiplication. One quoted assumption in the proof-of-sequential-work vault would become a theorem in the arithmetic model.
- The useful by-product is §2: 9/4 = 2 ÷ (1 − 1/3²), and the rectangular closed form is the same three-wire calculation with unequal wires.

## Sources

- **[LB]** OpenAI, *The matrix multiplication exponent is nine fourths*, 24 Nov 2026. `github.com/openai/math`, `preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/` (commit 92b516ef8e2a). Read from the LaTeX source in `build/`: `intro.tex`, `obstruction.tex`, `consequences.tex`, `background.tex`, `boundary.tex`, and the statements in `motion.tex`, `valued.tex` and `contact.tex`. Release note: `history.md`, entry of 24 Nov 2026.
- **[UB]** OpenAI, *An Upper Bound of 9/4 for the Matrix Multiplication Exponent*, 2 Oct 2026. Same repository, `preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/build/paper.tex`. Read: the introduction, the polynomial-multiplication section and the growth section.
- **[Lean]** Same repository, `lean/ComparatorChallenges/MatrixExponent.lean` (the three statements) and `lean/docs/107.md` (scope).
- Cited by [LB], not opened: A. Amanov, M. van den Berg, J. Zuiddam, arXiv:2610.30054; A. Shpilka, ECCC TR26-281; M. L. Doğan, V. Lysikov, K. Sakabe, M. Walter, arXiv:2611.09716; H. Lü, arXiv:2610.18914; B. Li, arXiv:2611.04175; P. Uznański, arXiv:2610.10494; Z.-W. Sun, arXiv:2610.13971.
- Web search, 2026-11-25 (titles and abstracts only): https://arxiv.org/abs/2611.09716 ; https://arxiv.org/abs/2610.30054 ; https://arxiv.org/abs/2610.28627 ; https://officechai.com/ai/openai-has-found-a-far-faster-way-to-multiply-matrices-the-math-that-underpins-all-of-modern-ai/ .
- J. Thaler, *Time-optimal interactive proofs for circuit evaluation*, CRYPTO 2013, arXiv:1304.3812, as quoted in the proof-of-sequential-work vault.
- Background, from memory (check the details before quoting them in a paper): V. Strassen, Numer. Math. 13 (1969) 354; V. Strassen, J. reine angew. Math. 384 (1988) 102 (the asymptotic spectrum); R. Terras, Acta Arith. 30 (1976) 241; J. Lagarias, Amer. Math. Monthly 92 (1985) 3.
