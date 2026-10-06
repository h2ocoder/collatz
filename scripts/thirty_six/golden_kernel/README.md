# Thread 3: the golden kernel. Why cos 36° = φ/2 is the mixing rate of the 3x+1 map modulo 5

Run of 2026-10-06. Everything below was computed in this directory today; every number comes from a `.log` or `.json` next to the script that produced it.

**Scope.** Nothing here is a step toward the Collatz conjecture. Every statement is about the residue chain of the map modulo N, which is the same chain for 3x+1, 3x−1 and every 3x+c with c prime to N (the kernels are conjugate by x → cx; for gcd(c, N) > 1 the kernel is a different one, e.g. 3x+5 modulo 5 has characteristic polynomial x(x − 2)²(x² + 2x + 2)). The thread sees the multiplier 3 and the relation 3 = 2 + 1. It does not see the sign. A second, skeptical pass re-read the proofs and recomputed most tables with independent code in `verify/`; section 13 lists what was changed, what was added, and what was not checked.

## 0. Answer in one page

1. **Why cos 36°.** Modulo 5 the residue chain of the shortcut map has an exact three-cell quotient that is a simple random walk on a pentagon folded along a mirror: apex {1}, near pair {2, 3}, far pair {0, 4}. Measures that are uniform on the cells stay uniform on the cells, and on them the kernel acts as the folded pentagon walk. Started from n ≡ 1 (mod 5), the residue of T^k(n) has the law of a pentagon walk after k steps, for every k (proved; checked on integers for k ≤ 16). The second eigenvalue of a pentagon walk is cos 144° = −cos 36°, and cos 36° = φ/2 is the apothem of the unit pentagon. That is the reason, and it is a pentagon reason. The five-state chain itself is **not** a pentagon walk: its characteristic polynomial is x(x − 1)(x − 2)(x² + x − 1), the pentagon's is (x − 2)(x² + x − 1)², no relabelling of residues turns one into the other, and from any start other than n ≡ 1 the law is not a pentagon law. The eigenvalues ½ and 0 of K_5 have no pentagon meaning.
2. **But it is not the pentagon one would guess.** The pentagon is 1–2–4–0–3, fixed by the dynamics. It is not the additive pentagon 0–1–2–3–4 of Z/5 and not its pentagram. The observation "x → x/2 turns sides into diagonals" is true and is not the mechanism.
3. **Why 5 and only 5.** Modulo 5 the branch multipliers are 1/2 ≡ 3 and 3/2 ≡ 4, and 3/2 = 1/2 + 1 = (1/2)² = −1. So 1/2 is the golden ratio of F_5 and the odd branch is a reflection. 5 = 3 + 2 = 3² − 2² is the only modulus prime to 6 at which a branch of the 3x+1 map is an involution.
4. **Theorem B (proved for all N).** N = 5 is the only level at which every eigenvalue of the kernel is real. At every other level the eigenvalues have sum of squares 0 and are not all 0.
5. **Census (computed, exact).** For all 132 moduli N prime to 6 up to 400: the golden pair at level 5 is the only irrational cosine. The only cosines anywhere else are 0 and ±1/2. For prime levels the same holds for every prime 5 < p ≤ 7993, with no cap on the order of the cosine (`verify/v3_krylov_scan.py`).
6. **The exceptional primes.** 11 is explained and proved: 11 = 2² + 3·2 + 1 is the closing condition of the trivial cycle {1, 2}, and 5 = 2² + 2 − 1 is the closing condition of the pair of fixed points {0, −1}. Both conditions say that the divisor 2 is a power of the golden ratio in F_p: 2 ≡ −φ (mod 5), 2 ≡ −φ² (mod 11). **31 and 37 are not explained.** No second two-point identity exists, no small configuration exists, no third universal low-degree condition exists. A new exceptional prime of a different kind turned up: at p = 41 the kernel has the five eigenvalues with (2λ)⁵ = −3. No further exceptional prime of either kind exists up to 7993.
7. **Pierpont primes.** Null. 769 and 1297 are simply the smallest primes on their rungs.

Figure: `fig_pentagon.png`.

## 1. Conventions (apply to every table)

- Shortcut (Terras) map T(n) = n/2 for n even, (3n+1)/2 for n odd. No dropping or stopping times are used in this thread, so the Paper 1 / Paper 2 step conventions do not enter.
- On Z/N with gcd(N, 6) = 1 the branches are the affine bijections e(x) = x/2 and o(x) = (3x+1)/2.
- Terras kernel on functions: (K f)(x) = ½ f(e x) + ½ f(o x). This is the Matthews–Watts matrix of the map mod N.
- A = 2K = R_e + R_o is an integer matrix, a sum of two permutation matrices. Eigenvalues of K are eigenvalues of A divided by 2. All exact work is on A.
- A acts on measures by push-forward: δ_x → δ_{e x} + δ_{o x}. "Eigenfunctional" means left eigenvector.
- Level N: the span of the additive characters of exact order N. prim_N is the characteristic polynomial of A on level N, of degree φ(N). charpoly(A_N) = ∏_{d | N} prim_d, with prim_1 = x − 2.
- Ψ_j is the minimal polynomial of 2cos(2π/j). Φ_k is the k-th cyclotomic polynomial. Kronecker (1857): an algebraic integer whose conjugates are all real and in [−2, 2] is 2cos(2πi/j); one whose conjugates all lie in the closed unit disc is 0 or a root of unity. Eigenvalues of A are algebraic integers of modulus at most 2, so a K-eigenvalue is a cosine of a rational angle exactly when its minimal polynomial is some Ψ_j.
- G = (Z/N)^×. m = order of 2 modulo ⟨3⟩, t defined by 2^m = 3^t, idx = [G : ⟨2, 3⟩].
- Generalised pair (q, d): e(x) = x/d, o(x) = (qx+1)/d. Multipliers a = 1/d, b = q/d. For d > 2 this is the formal two-branch kernel of the earlier work, not the residue chain of a d-branch map.

## 2. Results table

Status labels: proved / computed / conjecture / null / prior art / numerology. "Mirror" answers: does the statement distinguish 3x+1 from 3x−1, and from 5x+1?

| id | statement | status | role of 36 | mirror | script |
|---|---|---|---|---|---|
| A | K_5 on cell-uniform measures is the pentagon walk folded along a mirror (an exact three-cell quotient, not an isomorphism of the five-state chain); T^k(n) mod 5 for n ≡ 1 (mod 5) has the pentagon-walk law; rate cos 36° = φ/2 | proved, checked k ≤ 16. The return counts are OEIS A054877 (prior art for the Lucas formula) | none. 36° = 180°/5. The arithmetic is 5 = 3 + 2 = 3² − 2² | 3x−1: no (same pentagon with cells negated, checked). 5x+1: yes (no irrational cosine for 5x+1 at any N ≤ 200) | `q31_pentagon.py`, `verify/v1_pentagon.py` |
| A′ | the folding closes only for N = 5 | proved | none | no / n.a. | `q31_pentagon.py` §7 |
| A″ | tr(A_5^n) = 2^n + 1 + (−1)^n L_n (n ≥ 1); number of length-n words with 5 ∣ 2^n − 3^s and 5 ∣ C(w) is (A_n + 1 + (−1)^n L_n)/5, with A_n = OEIS A038519 | proved (corollary), checked n ≤ 16 with integer C(w) | none | no / yes | `q31_pentagon.py` §5, `verify/v1_pentagon.py` |
| B | N = 5 is the only level with all eigenvalues real; elsewhere Σλ² = 0 | proved; ingredients checked N ≤ 5000 | the cell (2,2) of the Collatz lattice: the word "oo" has multiplier 9/4, and 3² − 2² = 5. Every cell (k, s) has its own moduli, the divisors of 2^k − 3^s; (2,2) enters only because the second power sum decides realness | no / yes (for 5x+1 the deviating levels are 3, 7, 21 and only level 3 is all real) | `q32b_real_spectrum_theorem.py`, `verify/v6_survey.py` §3 |
| C | theorem in lattice form: (x^m − (−1)^{m+t})^{idx} divides prim_N when ord_N(3) is even | proved (restates the repo's theorem) | none in general. At 37 the characters used are the two of order 4 = 2² | no / yes (needs q = d + 1) | `q32_kronecker_census.py` |
| D | P_p(x, θ) = det(x − R_e − θR_o)/(x − 1 − θ) contains only monomials x^{p−1−k}θ^s with p ∣ 2^k − 3^s | proved; exact for p = 5, 7, 11, 13, 37 | none. It is the relation lattice of 2 and 3 mod p | no / no (same statement for any q, d) | `q34_anatomy_37.py` §2 |
| E | eigenvalue 0: kernel = {f = −f∘g}, g(y) = 3y + ½; dimension = number of even cycles of g = (p−1)/ord_p(3) or 0; f(x) = χ(4x+1) for χ(3) = −1 | proved | none | no / no | `q32_kronecker_census.py` |
| E′ | 0 is a semisimple eigenvalue of K_p for every prime p (algebraic = geometric multiplicity); for any N the number of Jordan blocks at 0 is the corank of a pairing of alternating functions; at N = p²q the multiplicity doubles iff p ∤ ord_q(3) | (a), (b) proved (skeptic pass, §4.3); (c) computed on ten levels, six of them predicted | none | no / no (same for any q) | `verify/v9_zero_jordan.py` |
| F | 5 ∣ d² + d − 1 at d = 2 gives eigenvalue +½ (fixed points {0, −1}); 11 ∣ d² + 3d + 1 at d = 2 gives −½ (trivial cycle {1, 2}); both conditions say d = ±φ^{±1} or −φ^{±2} in F_p | proved; explicit eigenvectors checked on all 585 roots with p ≤ 2000 | none | no / yes (family q = d + 1 only) | `q34c_family_base_rate.py`, `verify/v4_family.py` |
| F′ | in the family (d+1, d) the eigenvalue −½ of K, with its geometric multiplicity, is the same for d and 1/d; +½ for d corresponds to +½ of the signed kernel K⁻ for 1/d. For Collatz: −½ ∈ spec K_p iff −½ is an eigenvalue of ½f(2x) + ½f(3x+1) | proved (skeptic pass, §6.2); checked on all 2320 kernels with p ≤ 151 | none | no / yes (family q = d + 1) | `verify/v4_family.py` |
| G | census N ≤ 400: only irrational cosine is the golden pair at level 5; rational cosines 0, ±½ only. Prime levels: same for all 5 < p ≤ 7993, every order j | computed (exact; reproduced row by row with independent code) | none | no / yes | `q32_kronecker_census.py`, `verify/v2_census.py`, `verify/v3_krylov_scan.py` |
| H | cosine and root-of-unity eigenvalues beyond Theorem C at prime levels: K at 5, 11, 31, 37 only, and (2λ)⁵ = −3 at 41, for all primes ≤ 7993 and every order; K⁻ additionally at 13, 23 (primes ≤ 800, orders ≤ 60 above 400) | computed (sound: degree-certified Krylov scan; exact to 400) | 37 = 36 + 1 is on the list, unexplained | no / yes | `q34b_sporadic_scan.py`, `verify/v3_krylov_scan.py` |
| I | generic part of prim_N is a single irreducible factor | computed, 106 of 106 levels with deg ≤ 200 (sympy over Z); certified independently by factor degrees modulo primes for the 26 levels N ≤ 79 | none | no / unknown | `q32_kronecker_census.py`, `verify/v8_twopoint_irreducible.py` |
| J | K_37: ±i/2 from the theorem; +½ twice and −½ twice sporadic, each semisimple of geometric multiplicity 2 | computed (exact) | 36 ≡ −1: the point (2,2) is the half-period of the frequency torus. The same holds for every Pierpont prime 2^a 3^b + 1 with its own (a, b), and it does not explain the eigenvalues | no / n.a. | `q34_anatomy_37.py`, `verify/v5_anatomy.py` |
| K | no second two-point identity; minimal supports at 31, 37, 41 are 19, 24, ≤ 37 points | null (computed, p < 300 for the two-point search) | none | — | `q34_anatomy_37.py` §3, §4, `verify/v8_twopoint_irreducible.py` |
| L | no third universal condition of degree ≤ 4 in the search box | null (computed) | none | — | `q34c_family_base_rate.py` §C |
| M | "p ∣ 2^a ± 3^b for a small cell" as common cause | null: every prime below 50 qualifies | 37 = 2⁶ − 3³ gives a dodecagon in characteristic 37 only: numerology as an explanation (the same construction gives an 18-gon with residues ±1 at p = 181, where ±1 are not eigenvalues) | — | `q34_anatomy_37.py` §5, `verify/v5_anatomy.py` §5 |
| N | other cosines for other (q, d, N): √2/2, √3/2, heptagon, enneagon, 11-gon occur; two proved mechanisms | computed + proved (mechanisms A, B) | none | — | `q33_qd_survey.py`, `q33b_mechanisms.py` |
| O | Pierpont primes: rung distribution and \|λ₂\| not different from neighbours | null | 37 = 6² + 1 and 1297 = 6⁴ + 1: a constraint on orders, nothing more | no / n.a. | `q35_pierpont.py` |
| P | link to the icosian Fibonacci ladder | only the field Q(√5) and its Galois involution | cos 36° = φ/2 is the shared number, not a shared mechanism | — | §8 |

## 3. Q3.1 Why cos 36°

### 3.1 The facts mod 5 (`q31_pentagon.log`, 39 checks, 0 failures)

e(x) = 3x has order 4 and fixes 0. o(x) = 3 − x is a reflection and fixes 4 = −1. ⟨e, o⟩ = AGL(1,5) of order 20; ⟨e², o⟩ = D_5.

charpoly(2K_5) = x(x − 1)(x − 2)(x² + x − 1). Eigenvalues of K_5: 1, ½, 0, cos 72° = 1/(2φ), cos 144° = −cos 36° = −φ/2.

Invariant subspaces over Q: the eigenvalues are distinct, so the invariant subspaces are the 16 sums of
- constants (eigenvalue 2 of 2K),
- δ_{−1} − δ_0 (eigenvalue 1),
- δ_0 + δ_2 − δ_3 − δ_4 (eigenvalue 0),
- the golden plane W = Za + Zb, with a = (2, 1, 0, −1, −2) the centred-residue sawtooth and b = (3, 0, 2, −1, −4).

On W: 2K a = b − a and 2K b = a, the matrix [[−1, 1], [1, 0]], with characteristic polynomial x² + x − 1. The golden eigenvector is (φ⁴, 1, 2φ, −φ², −2φ³) = a + φb. W reduces mod 5 to the affine-linear functions on F_5.

The permutation module of AGL(1,5) is 1 ⊕ (4-dimensional irreducible), so representation theory gives no invariant subspace. The splitting is a property of the element e + o of the group algebra.

### 3.2 Theorem A (folded pentagon)

**Statement.** In Z/5 put Y = {−1/4} = {1}, Z = {−1/2, 1/2} = {2, 3}, X = {0, −1} = {0, 4}. These are: the common image of the point where the branches agree; that point and its negative; the two fixed points of the branches. Then push-forward by 2K_5 sends

1_Y → 1_Z,  1_Z → 2·1_Y + 1_X,  1_X → 1_X + 1_Z.

So measures uniform on the cells stay uniform on the cells, and on span(1_Y, 1_Z, 1_X) the operator 2K_5ᵀ equals the adjacency operator of a 5-cycle restricted to functions symmetric about a vertex, with Y the vertex, Z its two neighbours and X the two far vertices. Its eigenvalues are 2, 2cos 72°, 2cos 144°.

**Proof.** Over Q, for every modulus prime to 6:
- e(0) = 0, o(0) = ½, e(−1) = −½, o(−1) = −1. So δ_0 + δ_{−1} → (δ_0 + δ_{−1}) + (δ_{½} + δ_{−½}).
- e(±½) = ±¼, o(−½) = −¼, o(½) = 5/4. So δ_{½} + δ_{−½} → 2δ_{−¼} + δ_{¼} + δ_{5/4}.
- e(−¼) = −1/8, o(−¼) = 1/8. So δ_{−¼} → δ_{1/8} + δ_{−1/8}.

Modulo 5: ¼ ≡ −1, 5/4 ≡ 0 and {1/8, −1/8} = {2, 3} = {−½, ½}. That gives the three displayed relations. On a 5-cycle with vertices v₀, v_{±1}, v_{±2} the adjacency operator sends 1_{v₀} → 1_{v±1}, 1_{v±1} → 2·1_{v₀} + 1_{v±2}, 1_{v±2} → 1_{v±1} + 1_{v±2}. The two 3×3 matrices are equal. ∎

**Corollary (integers).** For every k ≥ 0, as n runs over the 2^k integers n ≡ 1 (mod 5) in a period 5·2^k, the residue T^k(n) mod 5 is distributed exactly as a simple random walk on a pentagon after k steps, with 1 ↔ start, {2, 3} ↔ its neighbours, {0, 4} ↔ the far vertices. In particular

P(T^k(n) ≡ 1 | n ≡ 1) = (2^k + 2(−1)^k L_k)/(5·2^k)  (L_k the Lucas numbers),

and the distance from uniform decays at rate exactly cos 36° = φ/2 per step.

*Proof.* By Terras, n mod 2^k determines the parity vector of length k bijectively, and by CRT it is independent of n mod 5. T^k(n) mod 5 is the image of n mod 5 under the composed branches. So the empirical law is δ_1·A^k/2^k, and δ_1 = 1_Y. ∎ (Checked by brute force for k = 0..14; counts for k = 8 are [57, 70, 36, 36, 57]. Re-checked for k = 0..16 on a window of 5·2^k consecutive integers that includes negatives, `verify/v1_pentagon.log`.)

**What the corollary does and does not say.**
- The numerators 1, 0, 2, 0, 6, 2, 20, 14, 70, … are OEIS A054877, "closed walks of length n along the edges of a pentagon based at a vertex", and the Lucas formula 5a(n) = 2^n + 2(−1)^n L_n is on that page. The formula is prior art. What this thread adds is the identification with T^k(n) mod 5.
- It holds for the start n ≡ 1 (mod 5) only. From n ≡ 2 every integer lands on residue 1 after one step; a pentagon walk from a neighbour would split evenly. No relabelling of the residues gives a pentagon law from the starts 0, 2, 3, 4.
- The partition is forced: among all 50 non-trivial partitions of Z/5, exactly two have "cell-uniform measures stay cell-uniform", namely {1}, {2, 3}, {0, 4} and its refinement {1}, {2}, {3}, {0, 4}. Controls: modulo 7 no partition has the property, and modulo 11 the only one merges {1, 2}, the trivial cycle of Proposition F.
- The same statement holds for 3x−1 with the cells negated (apex {4}, near {2, 3}, far {0, 1}), and for 3x+c with c prime to 5 with the cells multiplied by c. It is sign-blind.

**A′ (only 5).** The first relation holds for every N. The other two need {¼, 5/4} = {−1, 0} and {±1/8} = {±½}, which hold exactly when N ∣ 5. Confirmed for N < 2000.

### 3.3 Where φ is

A pentagon walk replaces a vertex by the average of its two neighbours. In the convex embedding that average is cos 72° times the vertex. In the star embedding the two "neighbours" are the ends of the opposite side, and their midpoint is −(apothem) times the vertex. The apothem of the unit pentagon is cos 36° = φ/2, and φ = diagonal/side = 2cos 36°. So the answer to "is the diagonal-to-side ratio the reason" is yes, for the pentagon of Theorem A.

### 3.4 What is not the reason (stated plainly)

- **The additive pentagon.** The pentagon of Theorem A is 1–2–4–0–3 (or 1–2–0–4–3; the folding does not distinguish them). Neither is an affine image of 0–1–2–3–4. For the additive pentagon c₁ = t + t⁻¹ and pentagram c₂ = t² + t⁻²: c₁c₂ = c₁ + c₂ = J − I, so c² + c − 1 = 0 off constants; R_e swaps c₁ and c₂; R_o commutes with both. All true. But 2K does not commute with c₁, W is not c₁-invariant, and the golden eigenvector has equal non-zero projections on both D₅-isotypic planes.
- **"2K_5 on W is conjugate to the pentagon / A_4 block."** True and empty. By Latimer–MacDuffee, since Q(√5) has class number 1, every integer 2×2 matrix with characteristic polynomial x² + x − 1 is GL₂(Z)-conjugate to [[0, 1], [1, −1]]. Checked on 104 matrices. The content of Theorem A is an equality of operators on a named subspace, not a conjugacy.
- **Path A_4.** Its spectrum ±φ, ±1/φ is symmetric; 2K_5 has −φ and 1/φ only. The right object is the pentagon folded at a vertex.
- **K_5² = ….** There is no shorter identity: the minimal polynomial of 2K_5 has degree 5. Singular values of 2K_5 are 0, √2, √2, 2, 2: φ is in the eigenvalues only. 2K_5 is not normal.
- **Path-level lumping.** The folding is exact lumpability of measures. It is not strong lumpability: both branches send 2 to 1, and both send 3 to the far pair. The branch digraph has no automorphism and no reversal. Consequently the cell process is a Markov chain only when the start is uniform on its cell; "K_5 is a pentagon walk" without that qualifier is false.

### 3.5 Why 5

Modulo 5 the multipliers are a = 1/2 ≡ 3 and b = 3/2 ≡ 4. Three things coincide: b = a + 1 (always: 3 = 2 + 1), b = a² (only mod 5), b = −1 (only mod 5). So a is a root of x² = x + 1 in F_5, a double root because 5 ramifies in Q(√5). The odd branch is an involution iff 3/2 ≡ −1 iff N ∣ 3 + 2 = 5 (equivalently N ∣ 3² − 2², as N is prime to 6); the even branch never is. In the cell lattice of Collatz words, (k, s) = (2, 2) is the word "oo", and 2² − 3² = −5.

**Role of 36:** 36 = 2²·3² does not enter. What enters is the pair (2, 3) through 3 + 2 = 5 and 3² − 2² = 5. In the 3-smooth exponent lattice the point (1,1) is 6 ≡ 1 (mod 5), which is why x/2 = 3x; (2,2) is 36 ≡ 1 (mod 5) for the same reason and adds nothing.

Two by-products:
- P_5(x, θ) = det(x − R_e − θR_o)/(x − 1 − θ) = (x² − θ²)² + θx − 1. At θ = 1 it is x(x − 1)(x² + x − 1). At θ = −1 it is x(x + 1)(x² − x − 1): the sign-twisted kernel has +φ/2.
- tr(A_5^n) = 2^n + 1 + (−1)^n L_n for n ≥ 1 (at n = 0 the trace is 5, not 4, because of the eigenvalue 0). Read on words: the number B_n of parity words of length n whose cell has 5 ∣ 2^n − 3^s and whose constant C(w) is divisible by 5 equals (A_n + 1 + (−1)^n L_n)/5, where A_n counts the words with 5 ∣ 2^n − 3^s. This is the repo's hidden-colour bias at p = 5 in closed form. A_n = Σ_{s ≡ −n (mod 4)} C(n, s) = 0, 1, 3, 2, 10, 16, 28, 72, 120, 256, … is OEIS A038519. B_n = 0, 1, 0, 2, 0, 7, 0, 24, 9, 76, 66, 263, 312, 988, 1353, 3744 (n = 1..16) was not found in the OEIS (searched 2026-10-06); neither was the trace sequence 2, 8, 5, 24, 22, 83, 100, 304.

## 4. Q3.2 Kronecker census

### 4.1 Theorem B

**Statement.** Let gcd(N, 6) = 1, N > 1. The eigenvalues λ of A on level N satisfy Σλ = 0. If N ≠ 5 they satisfy Σλ² = 0 and are not all 0, so at least one is non-real. At N = 5 they are 1, 0, 1/φ, −φ. Hence N = 5 is the only level whose spectrum consists of cosines.

**Proof.**
1. tr(A_N) counts fixed points of e and o: x = 0 and x = −1, so tr(A_N) = 2.
2. tr(A_N²) counts fixed points of the four two-step words. Their multipliers are 1/4, 3/4, 3/4, 9/4. For the first three, multiplier − 1 is a unit, so each has one fixed point. For "oo", x → (9x + 5)/4, the fixed points solve 5(x + 1) ≡ 0, which has gcd(5, N) solutions. So tr(A_N²) = 3 + gcd(5, N).
3. Level decomposition: R_e ψ_s = ψ_{s/2} and R_o ψ_s = ζ^{s/2} ψ_{3s/2} preserve the additive order of s. Level 1 is the constants, with A = 2. Write S₁(N), S₂(N) for the level sums. Then Σ_{d ∣ N} S₁(d) = 2 and Σ_{d ∣ N} S₂(d) = 3 + gcd(5, N), with S₁(1) = 2, S₂(1) = 4. Induction on N gives S₁(N) = 0 for N > 1, S₂(5) = 4, and S₂(N) = 0 for N > 1, N ≠ 5.
4. If all level-N eigenvalues were real, Σλ² = 0 would force them all to be 0. They are not:
   - if ord_N(3) is odd, Proposition E shows A is injective;
   - if ord_N(3) is even, Theorem C gives an eigenvalue of modulus 1 on level N. ∎

Checks (`q32b_real_spectrum_theorem.log`): steps 1–3 and the cycle structure of g for all 999 moduli N ≤ 3000; exact level polynomials for the 49 levels N ≤ 150 begin x^n + 0·x^{n−1} + 0·x^{n−2} and have non-real roots. Independently (`verify/v6_survey.log` §3, `verify/v2_census.log`): tr(A_N) = 2 and tr(A_N²) = 3 + gcd(5, N) by direct fixed-point counts for all N ≤ 5000, identically for 3x+1 and 3x−1; e₁ = e₂ = 0 and prim_N ≠ x^n at all 131 levels 5 < N ≤ 400.

Mirror and cousin. The theorem is sign-blind (same counts for 3x−1). It does distinguish 5x+1: there tr(A_N²) ≠ 4 exactly at the multiples of 3 or 7 (21 = 5² − 2²), the level sums are non-zero at 3, 7, 21, and the only all-real level up to 200 is N = 3, where the kernel is a reflection plus a translation with spectrum {0, −1}. No level of 5x+1 has an irrational cosine (N ≤ 200, `verify/v2_census_q5.log`).

**Role of 36:** the proof turns on the cell (2,2): "oo" is the only two-step word whose multiplier can be 1, and 3² − 2² = 5. This is the one place in the thread where the lattice point (2,2) genuinely enters, as a Collatz cell (2 steps, 2 odd), not as the number 36.

### 4.2 Theorem C (the repo's theorem, lattice form)

**Statement.** If ord_N(3) is even then (x^m − (−1)^{m+t})^{idx} divides prim_N. Equivalently: K has, on level N, the eigenvalues λ with (2λ)^m = (−1)^{m+t}, each with multiplicity at least idx. Here m is the least positive integer with 2^m ∈ ⟨3⟩, and 2^m = 3^t.

**Proof.** In frequency coordinates, (A_ε φ)(u) = φ(2u) + ε ζ^{u/3} φ(2u/3) for A_ε = R_e + εR_o.
- *Twist.* For a character χ of G put (M_χ φ)(u) = χ(u)φ(u). Then M_χ⁻¹ A_ε M_χ = χ(2)·A_{ε χ̄(3)}. So for χ(3) = −1, A₊ is χ(2) times a conjugate of A₋, block by block.
- *Functional.* Λ(f) = f(−½) − f(−1) annihilates I + R_e − R_o: the branches agree at −½, o fixes −1, and e(−1) = −½. Its Fourier coefficients ζ^{−s/2} − ζ^{−s} are non-zero for s ≠ 0. The operator preserves each ⟨2, 3⟩-orbit of frequencies, so Λ restricted to any such orbit is a non-zero left null vector. Hence −1 is an eigenvalue of A₋ on each of the idx orbits in level N.
- *Count.* A character with χ(3) = −1 exists iff ord_N(3) is even. On ⟨2, 3⟩ ≅ Z²/⟨(ord 3, 0), (−t, m)⟩ such a character has χ(2)^m = (−1)^t, and every m-th root of (−1)^t occurs. So the values −χ(2) are the roots of x^m = (−1)^{m+t}, one family per orbit. ∎

This is the earlier work's theorem and proof (log AZ⁵–AZ⁷), with the multiplicity made explicit and the answer read off the relation lattice {(k, s) : 2^k ≡ 3^s}. No violation at any of the 132 levels N ≤ 400 or the 137 primes ≤ 800. The proof was re-read line by line in the skeptic pass, including the composite case used in Theorem B, and the divisibility is asserted at all 1005 primes 5 ≤ p ≤ 7993 by `verify/v3_krylov_scan.py`.

### 4.3 Propositions D and E

**D (lattice support).** From the twist identity, P_p(x, θ) = P_p(x χ̄(2), θ χ̄(3)) for every χ. So the coefficient of x^i θ^s vanishes unless 2^{p−1−i} ≡ 3^s (mod p). With k = p − 1 − i, the monomials are indexed by the cells (k, s) with p ∣ 2^k − 3^s. Exact check: all lattice cells in the triangle 0 ≤ s ≤ k ≤ p − 1 occur and no others, for p = 5 (5 cells), 7 (6), 11 (8), 13 (11), 37 (21). By Sachs's coefficient theorem the coefficient is a signed count of families of disjoint cycles of the branch graph with k steps and s odd steps; the proposition says these counts cancel off the lattice. At θ = ±2, ±3, 5 the polynomial is irreducible for all ten primes tested (`q34d_side_checks.log` (a)): every factorisation in this thread is special to θ = ±1.

**E (eigenvalue 0).** A f = 0 iff f∘e = −f∘o iff f = −f∘g with g = o∘e⁻¹, g(y) = 3y + ½. Since g(y) + ¼ = 3(y + ¼), g^k = id iff 3^k ≡ 1. So dim ker A = number of even cycles of g. For prime p this is (p − 1)/ord_p(3) if that order is even, else 0, and the kernel is spanned by f(x) = χ(4x + 1), χ(3) = −1. In the coordinate y = 4x + 1 the odd branch is 3 times the even branch, so 2K = R_h(1 + M₃) with h(y) = (y+1)/2 and M₃ the dilation by 3.
Computed: algebraic multiplicity equals this at all 76 primes and all squarefree levels ≤ 400. Ten non-squarefree levels ≤ 400 have a zero. At nine of them (25, 49, 125, 175, 245, 289, 325, 343, 361) the algebraic multiplicity is exactly double (Jordan blocks of size 2; ker A² = ker A³ checked at 25, 49, 175, 245, 325). At the tenth, 275 = 5²·11, it is not: algebraic = geometric = 10. So "non-squarefree implies doubling" is false.

**Proposition E′ (when 0 is defective; found in the skeptic pass).**
(a) *Criterion, any N.* In the coordinate y = 4x + 1 let V_0 be the functions with f(3u) = −f(u) and V_½ the functions with F(3u − 1) = −F(u) (alternating functions on the even cycles of u → 3u around 0, and around ½). Then dim ker A² − dim ker A equals the corank of the pairing V_½ × V_0 → Q, ⟨F, f⟩ = Σ_u F(u) f(u).
(b) *Primes.* For every prime p ≥ 5 the pairing is non-degenerate. So 0 is a semisimple eigenvalue of K_p, and its algebraic multiplicity is (p − 1)/ord_p(3) if that order is even and 0 otherwise. This turns the "computed at 76 primes" above into a theorem.
(c) *Rule at N = p²q (computed).* The multiplicity at level N doubles exactly when p does not divide ord_q(3). It doubles at 175, 245, 325, 425, 539 and not at 275, 775, 1421, 1525, 2107. Of these, 425, 539, 775, 1421, 1525 and 2107 were predictions made from the rule before computing.

*Proof of (a).* A = R_h∘S with (S f)(u) = f(u) + f(3u) and (R_h F)(y) = F(h(y)), h(y) = (y + 1)/2. ker A = ker S = V_0, and im S = (ker Sᵀ)^⊥ = V_0^⊥ because Sᵀ = 1 + M_{1/3} has the same kernel. A Jordan block needs a non-zero vector of ker A ∩ im A = V_0 ∩ R_h(V_0^⊥), and R_h F ∈ V_0 iff F is alternating for h∘(3·)∘h⁻¹, which is u → 3u − 1. So ker A ∩ im A ≅ V_½ ∩ V_0^⊥, the left kernel of the pairing. ∎
*Proof of (b).* V_0 is spanned by the characters χ with χ(3) = −1 (extended by 0), V_½ by the functions χ′(u − ½). Their pairing is Σ_u χ(u)χ′(u − ½) = (χχ′)⁻¹(2)·χ′(−1)·J(χ, χ′), a Jacobi sum up to factors that split as (function of χ)·(function of χ′). With g the Gauss sum and g(1) = −1, J(χ, χ′) = g(χ)g(χ′)·c(χχ′) with c(θ) = θ(−1)g(θ̄)/p, valid also when χχ′ is trivial. Writing χ = χ₀η, χ′ = χ₀η′ with η, η′ in the group Γ of characters trivial on ⟨3⟩, the matrix c(χ₀²ηη′) is a group matrix of Γ up to a permutation, and its eigenvalues are, up to non-zero factors, the Gaussian periods Σ_{h ∈ ⟨3⟩} ζ_p^{ch}. A Gaussian period of a prime is a sum of distinct members of the basis ζ, …, ζ^{p−1} of Q(ζ_p), so it is not 0. ∎
*Why (c) is plausible.* For composite N the same sums over ⟨3⟩ ⊂ (Z/N)^× can vanish: they do when ⟨3⟩ contains the kernel of reduction (Z/p²q)^× → (Z/pq)^×, and at N = p²q that happens iff p ∤ ord_q(3). The proof of (b) has not been carried over to composite levels, so (c) is a computed rule.

Checks (`verify/v9_zero_jordan.log`): (a) at 23 levels up to 361 against the nullities of A and A²; (b) at all 288 primes below 3000 with ord_p(3) even, and independently no Jordan block at 0 at any prime ≤ 7993 (`verify/v3_krylov_scan.py`); (c) at the ten levels listed (ranks modulo 2³¹ − 1 above 400). Mirror: sign-blind. The same proof works for any pair (q, d) with ⟨3⟩ replaced by ⟨q⟩. Role of 36: none.

### 4.4 The census (`q32_kronecker_census.log`, 216 s)

All 132 moduli N prime to 6, 5 ≤ N ≤ 400 (76 primes, 56 composites), exact integer characteristic polynomials, every candidate Ψ_j and Φ_k tested.

| K-eigenvalue on level N | polygon | levels |
|---|---|---|
| 0 | square (j = 4) | 102 |
| +½ | hexagon (j = 6) | 68 |
| −½ | triangle (j = 3) | 65 |
| cos 72°, −cos 36° | pentagon (j = 5) | **1: N = 5** |
| any other cosine (heptagon, enneagon, √2/2, √3/2, …) | — | **0** |
| ½·(primitive k-th root of unity) | k = 3, 4, 5, 6, 10, 12, 18, 20 | 8, 19, 3, 11, 5, 5, 1, 1 |

- Is 5 the only modulus where the whole spectrum is cosines? **Yes, for every N: Theorem B.**
- Is the golden mean the only irrational cosine that ever occurs? **Yes for N ≤ 400 (computed), and for every prime level 5 < p ≤ 7993 with no bound on j (computed, `verify/v3_krylov_scan.py`). Not proved.** A necessary condition for Ψ_j ∣ prim_p is that Ψ_j splits into linear factors modulo p (for p ∤ j: p ≡ ±1 (mod j)), because charpoly(2K_p) ≡ ∏_n (x − 2^{−n}(1 + 3^n)) (mod p) (the earlier work's degree-filtration lemma). Proof of the lemma: functions F_p → F_p are the polynomials of degree < p, and A x^n = (x/2)^n + ((3x+1)/2)^n = 2^{−n}(1 + 3^n) x^n + lower terms, so A is triangular in the monomial basis. The scan uses the sharper form: every root of Ψ_j (or Φ_k) modulo p must be one of the residues κ_n, n = 1..p−1. That leaves a handful of candidates per prime, and each is then refuted modulo 2³¹ − 1.
- 29 of 132 levels have no cosine eigenvalue at all.
- prim_N(x) = x^r·g_N(x^m), and in all 106 levels with deg g_N ≤ 200, g_N is a product of linear factors (0, the theorem's ±1, sporadic) and **one irreducible polynomial**. At N = 5 that irreducible polynomial happens to be y² + y − 1. Seen this way φ appears at 5 because the generic factor has degree 2 there and Theorem A makes it real. (Irreducibility re-certified for the 26 levels N ≤ 79 by a different method, factor-degree patterns modulo primes, `verify/v8_twopoint_irreducible.log`.)
- The whole table was reproduced row by row (132 rows, 0 differences) by `verify/v2_census.py`, which obtains the characteristic polynomials from the power sums tr(A^k) and Newton's identities instead of a Hessenberg reduction, builds Ψ_j from the cyclotomic polynomials, and tests every j with deg Ψ_j ≤ φ(N).

**Role of 36 (census):** none.

## 5. Q3.3 Where does φ appear

**In the 3x+1 kernel.** φ/2-type eigenvalues occur in spec(K_N) iff 5 ∣ N, for N ≤ 400: level 5 is a direct summand of K_N when 5 ∣ N, and no other level has an irrational cosine. Levels 25, 125, 35, 55, … carry no new golden eigenvalue.

**In the generalised kernels** (`q33_qd_survey.log`: 2574 triples, 2 ≤ q, d ≤ 12, q ≠ d, N ≤ 60, exact). 124 triples have an irrational cosine: pentagon j = 5 in 50 triples, decagon j = 10 in 24, octagon √2/2 in 43, dodecagon √3/2 in 8, heptagon in 3, enneagon in 1, 11-gon in 1, and j = 16, 20, 24, 28, 32 in a few (a triple can carry several). With d = 2, the only hits are (3, 2, 5) and (8, 2, 5), the same kernel since 8 ≡ 3 (mod 5). So among qx+1 maps with q ≤ 12 the golden eigenvalue belongs to q ≡ 3 (mod 5) at N = 5 and to nothing else: 5x+1, 7x+1, 9x+1, 11x+1 have no irrational cosine at any N ≤ 60.

Mechanisms (`q33b_mechanisms.log`):

| class | condition mod N | hits | all-real levels in the survey |
|---|---|---|---|
| A: both branches involutions | d² ≡ 1 and q ≡ −d | 29 | 70 of 70 (proved) |
| B: reflection + translation | d ≡ −1 and q ≡ d | 2 | 22 of 22 (proved) |
| C: odd branch a reflection only | q ≡ −d | 33 | 20 of 82 |
| D: even branch an involution only | d² ≡ 1 | 43 | 27 of 153 |
| E: neither | — | 17 | 2 of 2227 |

- *Proof of A.* The permutation matrix of an involution is symmetric, so R_e + R_o is symmetric and its eigenvalues are real; Kronecker makes them cosines. Note the odd branch x → bx + 1/d is an involution iff b = −1; b² = 1 alone gives a translation for o².
- *Proof of B.* R_o is diagonal in the additive characters and R_e swaps ψ_s and ψ_{−s}: 2×2 blocks with eigenvalues 0 and 2cos(2πs/N).
- (8, 6, 7), (10, 8, 9), (12, 10, 11) are class A: the pair (d + 2, d) modulo d + 1 is two reflections, so the heptagon, enneagon and 11-gon appear for the trivial dihedral reason.
- **Collatz mod 5 is class C**, and so is every non-trivial analogue: (4, 3, 7) has (x² − 2)(x⁴ − x² + 2), so the (4x+1)/3 kernel modulo 7 = 4 + 3 has the eigenvalue cos 45°. This is the closest thing to "another number playing the role of φ". A metallic mean other than φ cannot occur: 1 + √2 > 2.
- For the 3x+1 kernel no modulus other than 5 has an involutive branch (checked N < 2000; it is N ∣ 5 or N ∣ 3).
- Reproduced with independent code (`verify/v6_survey.log`): 2574 triples, 124 hits, the same counts per j, the d = 2 hits, (4, 3, 7), 70 of 70 and 22 of 22. The class counts leave out the 20 triples with N = 2, where −1 = 1 and both conditions hold trivially.

**The family containing Collatz mod 5.** G_N = ½(x → −2x) + ½(x → −x − 2) on Z/N is the pair (d+1, d) modulo N = 2d + 1; N = 5 is (3, 2). For odd N ≤ 301: golden at N = 5, 11, 15, 19, 33, 57; octagon at N = 7, 21, 23, 69; nothing else. All eigenvalues real only at N = 5 and 15. The folded-polygon lumping of Theorem A exists only at N = 5: at (4, 3, 7) the coarsest partition has 5 cells and is not invariant. So in this family the mechanism behind the cosines at 7, 11, 19, 23 is **not** Theorem A and is not understood.

For all dilation + reflection kernels ½(x → ax) + ½(x → 1 − x) on Z/p, p ≤ 61: irrational cosines occur for a ∈ {−2, −½} (p = 5, 7, 11, 19, 23), for roots of a² ± a − 1 (p = 11, 19, 29, 31, 41, 59, 61, not all roots), for a = √2, 1/√2, −4, −¼ (p = 23), and for a few unidentified a at p = 29 and 47. Only j = 5, 8, 10 were seen. Computed; no rule proved.

**Role of 36:** none.

## 6. Q3.4 The prime 37 and the other exceptions

### 6.1 spec(K_37), exactly (`q34_anatomy_37.log` §1)

ord 2 = 36, ord 3 = 18, 3 = 2²⁶, m = 2, 2² = 3⁷, idx = 1. 37 = 2⁶ − 3³, so 3/4 has order 3. 6 has order 4, so 36 ≡ −1.

charpoly(2K_37) = (x − 2)·x²·(x² + 1)·(x − 1)²·(x + 1)²·G(x²), with G irreducible of degree 14:

g_37(y) = y(y + 1)(y − 1)²(y¹⁴ + y¹³ + 2y¹² − 7y¹¹ − 6y¹⁰ − 15y⁹ + 11y⁸ + 3y⁷ + 18y⁶ − 13y⁵ − 33y⁴ − 26y³ − 11y² + 26y + 9).

- Rotational symmetry: order m = 2 (λ → −λ).
- |λ₂| = 0.673523, attained at ±0.673523.
- The theorem's eigenvalues: ±i/2, from the two characters of order 4 (χ(3) = −1, χ(2) = ±i). Lattice form: x² = (−1)^{2+7}.
- Eigenvalue 0 twice: (p − 1)/ord 3 = 2.
- **Sporadic: +½ twice and −½ twice.** Both eigenspaces are 2-dimensional and semisimple.

The 36 characters are χ_j with χ_j(2) = e(j/36), and their Galois orbits are the nine divisors of 36. The spectrum uses this lattice only through ⟨2⟩ and ⟨3⟩; the one visible trace is that the theorem's characters are those of order 4 = 2².

### 6.2 What is explained

**Proposition F (two golden conditions).** For the pair (d + 1, d) on Z/p, with e⁻¹(a) = da and o⁻¹(a) = (da − 1)/(d + 1):
- F₁: A(δ_{−1} − δ_0) = δ_{−d} + δ_{−1} − δ_0 − δ_{−1/(d+1)}. This equals δ_{−1} − δ_0 iff d(d + 1) = 1, i.e. **d² + d − 1 ≡ 0**. Eigenvalue +½ of K. The two points are the fixed points of the branches.
- F₂: let x₀ = 1/(d² − d − 1) and x₁ = d·x₀, the 2-cycle of the word "oe" (o x₀ = x₁, e x₁ = x₀). Then A(δ_{x₁} − δ_{x₀}) = −(δ_{x₁} − δ_{x₀}) + δ_{d x₁} − δ_{o⁻¹ x₀}, and the defect vanishes iff (d − 1)(d² + 3d + 1) = 0, i.e. **d² + 3d + 1 ≡ 0**. Eigenvalue −½ of K.

Both have discriminant 5. F₁ = 0 iff d = 1/φ or −φ; F₂ = 0 iff d = −φ² or −φ⁻². In multiplier terms F₁ says b = a² together with b = a + 1: the branch multipliers are (φ, φ²).

For Collatz, d = 2: F₁(2) = 5 and F₂(2) = 11.
- **p = 5:** the +½ is the pair of fixed points {0, −1}. (At 5 it is also predicted by the theorem.)
- **p = 11:** the 2-cycle is the trivial Collatz cycle {1, 2}, which closes mod p iff 4 ≡ 1/3 iff p = 11. That gives −½. The +½ at 11 follows because m = 2 makes the spectrum symmetric under λ → −λ. So **both sporadic eigenvalues at 11 are proved**, and 11 is where 2 ≡ −φ² (φ ≡ 8, φ² ≡ 9).
- Universality: at every one of the 33 roots of F₁ and 32 roots of F₂ with 5 ≤ p ≤ 151 the eigenvalue is present (asserted in the script). Re-checked with the explicit eigenvectors at all 293 + 292 roots with p ≤ 2000, and the converse (these two vectors are eigenvectors only at the roots) for all d with p ≤ 61 (`verify/v4_family.log`).

**Proposition F′ (inversion symmetry; found in the skeptic pass).** Write A_d = R_e + R_o and A⁻_d = R_e − R_o for the pair (d + 1, d) on Z/p, d ≠ 0, ±1, restricted to level p. Then
- dim ker(A_d + 1) = dim ker(A_{1/d} + 1): the eigenvalue −½ of K is shared by d and 1/d with the same geometric multiplicity;
- dim ker(A_d − 1) = dim ker(A⁻_{1/d} − 1): the eigenvalue +½ of K for d is the eigenvalue +½ of the signed kernel for 1/d.

*Proof.* Level p is the (p − 1)-dimensional irreducible representation ρ of AGL(1, p), and A_d + 1 = ρ(1 + e + o). Multiplying by the invertible ρ(e⁻¹) gives ρ(1 + e⁻¹ + e⁻¹o), with the same nullity. The affine maps e⁻¹ and e⁻¹o have multipliers d and d + 1 and distinct fixed points, so some element of AGL(1, p) conjugates them to the normalised pair (e′, o′) of the parameter d′ with 1/d′ = d. Conjugation preserves nullity. For the second statement, A_d − 1 = ρ(e + o − 1), and multiplying by ρ(e⁻¹) gives ρ(1 + e⁻¹o − e⁻¹) = −ρ(e′ − o′ − 1) after the same conjugation, with e′ = e⁻¹ of multiplier d and o′ = e⁻¹o of multiplier d + 1. That is −(A⁻_{1/d} − 1). ∎ (R is an anti-representation on functions, which changes e⁻¹o into oe⁻¹ and nothing else. Constants carry none of these eigenvalues, so the nullities on Z/p and on level p agree.)

Checked on all 2320 kernels with p ≤ 151 (first statement) and all kernels with p ≤ 101 (second). The eigenvalue +½ is **not** shared by d and 1/d in general (1304 of 2320 kernels differ). Consequences:
- F₂ = d² + 3d + 1 is a reciprocal polynomial, as it must be.
- For Collatz, d = 2 and 1/d = ½: the kernel of the parameter ½ is conjugate to ½f(2x) + ½f(3x+1), the kernel of the semigroup ⟨2x, 3x+1⟩. So −½ ∈ spec(K_p) iff −½ is an eigenvalue of that kernel, with equal multiplicity. This explains the agreement at 31 and 37 noted in §10 and its failure for +½ at 37 (multiplicity 2 against 1).
- The "orbit of six sporadic divisors at 37" in §6.3 is three pairs {d, 1/d}. It is three coincidences, not six.

### 6.3 What is not explained: 31, 37, 41 (and 23 for K⁻)

List of Kronecker-type eigenvalues beyond the theorem. For K it is complete for all primes 5 ≤ p ≤ 7993 and every order: cosines Ψ_j for all j, roots of unity Φ_k for all k, Jordan blocks at 0, and integer roots 2 ≤ |c| ≤ min(2^m, 5000) of g_p (`verify/v3_krylov_scan_*.log`). For K⁻ it covers p ≤ 800 for orders ≤ 60 and |c| ≤ 400 only (`q34b_sporadic_scan.log`; that scan had the same cap for K above 400). A miss modulo one prime is a proof of absence; hits agree with the exact census to 400:

| p | kernel | extra factor of charpoly(2K) | status |
|---|---|---|---|
| 5 | K | x² + x − 1 | Theorem A |
| 11 | K | (x − 1)(x + 1) | Proposition F₂ + symmetry |
| 31 | K | x − 1 | **unexplained** |
| 37 | K | (x − 1)²(x + 1)² | **unexplained** |
| 41 | K | x⁵ + 3 | **unexplained**, not on the circle: \|λ\| = 3^{1/5}/2 = 0.6229 |
| 13 | K⁻ | x⁴ − 3 | forced: the block has dimension 3 with eigenvalues 0 and 1 fixed, so the third is the trace |
| 23 | K⁻ | (x − 1)² | **unexplained** (8-point eigenfunction; multiplicity 2 = idx) |

No event for K at any of the 994 primes 41 < p ≤ 7993. For ord_p(3) even, K⁻ is a twist of K and repeats K's events rotated by χ(2) (31: x − 1; 37: (x² + 1)²; 41: x⁵ + 3).

How the wider scan works (`verify/v3_krylov_scan.py`, O(p²) per prime). Berlekamp–Massey gives the minimal polynomial f of the sequence u·A^k v modulo r = 2³¹ − 1 for random u, v. Over Q the eigenvalue 0 has geometric multiplicity z (Proposition E) and each root of the forced factor F = x^m − (−1)^{m+t} has geometric multiplicity at least idx (Theorem C), and ranks can only drop modulo r. So deg f ≤ p − (z − 1)⁺ − (idx − 1)m, and when equality holds the characteristic polynomial modulo r is exactly f·x^{(z−1)⁺}·F^{idx−1}. Equality held at every prime except 37, where the degree is short by 2 because ±1 are double; 37 was resolved with the full characteristic polynomial. An unlucky (u, v) can only lower deg f and flag the prime, never hide an eigenvalue, so the conclusion is not probabilistic. Candidates are the Φ_k with k ∣ p − 1 and the Ψ_j with j ∣ p ± 1 all of whose roots modulo p are among the κ_n (§4.4); each survivor is then tested by division modulo r.

What was tried for 31, 37, 41:

1. **A second identity g(a) − g(b).** Brute force over all primes p < 200, both signs, both sides, all coefficient ratios (`q34_anatomy_37.log` §3). The complete list of eigenvectors and eigenfunctionals of support ≤ 2 is: the theorem's functional δ_{−½} − δ_{−1} for K⁻ (every prime); δ_{−1} − δ_0 for K at p = 5; δ_1 − δ_2 for K at p = 11; δ_{−¼} − δ_{−1} for K⁻ at p = 7; and the trivial null vectors δ_{−¼}, δ_{−½} of K⁻. **Nothing at 23, 31, 37.** The same list comes out of an independent search by exact coefficient bookkeeping over all primes p < 300 (`verify/v8_twopoint_irreducible.log`).
2. **A small closed configuration.** Minimal supports, exact (the eigenspaces have dimension ≤ 2): at 31, 19 points (function) and 29 (functional) of 31; at 37, 24 and 26 of 37 for +½, 24 and 31 for −½; at 41, at most 37 and 32 of 41. The eigenvectors fill the space. The earlier ledger's guess "each a finite closed configuration" holds for 5, 7, 11 and 23 (8 points) and fails for 31, 37, 41.
3. **A third universal condition.** For each prime p ≤ 151 and each d, the kernels (d + 1, d) were tested for eigenvalues ±1 beyond the theorem (`q34c_family_base_rate.log`). All integer polynomials F(d) of degree 2 (|coefficients| ≤ 12), 3 (≤ 7) and 4 (≤ 4) were tested for "every root mod p carries the eigenvalue". Survivors: F₁, F₂, and d² + d + 1, which is the theorem (d a cube root of unity). No irreducible cubic or quartic.
4. **p ∣ 2^a ± 3^b for a small cell.** Every prime below 50 divides such a number with small exponents, so the hypothesis cannot separate 11, 31, 37, 41 from 13, 17, 19, 29, 43, 47. Null as stated.
5. **The characteristic-p shadow.** Modulo p the kernel is triangular in the monomial basis with diagonal κ_n = 2^{−n}(1 + 3^n). When ord(3/4) = k, the degrees n = kj carry κ = η^j + η^{−j} with η = 2^k: a polygon in characteristic p. At 37, k = 3 (because 37 = 2⁶ − 3³) and η = 8 has order 12: **a dodecagon in characteristic 37**, with residues 2, ±√3, ±1, 0, −2. The sporadic ±1 are exactly its entries at n = 6, 30 and n = 12, 24, and both lift with full multiplicity. But ±√3 and −2 do not lift, and at p = 7 the same construction gives a triangle whose second −1 does not lift. So this locates the eigenvalues modulo 37 and does not prove them in characteristic 0. Control (`verify/v5_anatomy.log` §5): a residue κ_n ≡ +1 exists at 306 of the 428 primes below 3000 and κ_n ≡ −1 at 295 (forced cases included), while a sporadic +1 exists at three primes and a sporadic −1 at two. And the same polygon construction at p = 181, where ord(3/4) = 10 and 2¹⁰ has order 18, gives an 18-gon in characteristic 181 with both +1 and −1 among its residues; 2K_181 has neither eigenvalue. As an explanation of 37 the dodecagon is numerology.
6. **The double eigenvalue.** Each of ±1 is a semisimple eigenvalue of 2K_37 of geometric multiplicity 2 (pairing determinants 16/3 and −80/3). Under R_e + (1 + ε)R_o the two eigenvalues split at first order with slopes equal to the roots of 40x² ± 71x − 293, of discriminant 3⁴·641, so the splitting is irreducible over Q. (That P_37 and both partial derivatives vanish at (1, 1) is automatic: the adjugate of a matrix of corank 2 is zero. It carries no information beyond "multiplicity 2".)
7. **Base rate.** Among the 2320 kernels (d + 1, d) with 5 ≤ p ≤ 151, 152 have a sporadic ±1; 52 are roots of F₁ or F₂; 100 are not. Per prime, the unexplained count is 3.9 for p ≤ 41, 4.1 for 43–79, 1.75 for 83–113, 1.0 for 127–151, i.e. 21.5 %, 7.0 %, 1.8 %, 0.7 % of the kernels. At p = 37, 9 of the 34 kernels (Collatz among them) have one. So a sporadic ±½ at a prime below 40 is common in the family that shares the theorem, and the Collatz kernel is not singled out.

**Common cause, honestly.** 5 and 11: yes, the golden conditions F₁, F₂, proved. 31, 37, 41: none found. The data fit "coincidences of small primes whose rate falls with p": no further event up to 7993. At 37 the orbit of d = 2 under d → 1/d and d → −1 − d is {2, 12, 17, 19, 24, 34} and all six are sporadic (4 of 6 at 31, 2 of 6 at 41, 0 of 6 at 43). By Proposition F′ the pairs {2, 19}, {12, 34}, {17, 24} share their −½ automatically, so this is three coincidences, at d = 2, 12, 17, in a table where 9 of 34 divisors are sporadic. The link d → −1 − d between the pairs is not explained, and at 31 it fails.

**Status of the ledger's open item.** The converse "no eigenvalue of modulus ½ other than the theorem's" now reads: for K, exceptions exactly 11 (proved), 31, 37, for all primes ≤ 7993 and all composite levels ≤ 400. Still a conjecture beyond that.

**Role of 36:** 37 = 36 + 1 means 6² ≡ −1, so the lattice point (2,2) is the half-period of the frequency torus Z²/{(a, b) : 2^a 3^b ≡ 1} and complex conjugation is translation by (2,2). True, true in the same way for every Pierpont prime 2^a 3^b + 1 with its own (a, b), and not connected to the sporadic eigenvalues by anything found here. 37 = 2⁶ − 3³ explains where the residues ±1 sit modulo 37 and nothing more (item 5). Linking the eigenvalues to 36 itself would be numerology.

## 7. Q3.5 Pierpont primes (`q35_pierpont.log`)

The half-circle content is fixed by the theorem: (p − 1)/ord_p(3) eigenvalues if ord_p(3) is even. The "rung" is v₂(ord 2) − v₂(ord 3).

- **Rungs.** For all 78,496 primes below 10⁶, grouped by t = v₂(p − 1), the 40 Pierpont primes have rung classes {none 6, a<b 14, a=b 11, rung 1: 5, rung ≥ 2: 4} against {5.2, 19.8, 8.6, 4.4, 2.0} expected from all primes with the same t. χ² = 4.46 on 4 d.o.f. **Null.** (Recomputed, `verify/v7_pierpont.log`. Three expected counts are at or below about 5, so the χ² approximation is rough; with 40 primes the test has little power, and "no difference detected" is all it supports.)
- **Why 769 and 1297 looked special.** They are the smallest primes of rung 3 and rung 2. A rung r needs t ≥ r + 2, and the smallest primes with large t are k·2^t + 1 with tiny k, hence Pierpont. The next primes on those rungs are 7057, 8017, 12097 (rung 2) and 8737, 15937 (rung 3), none Pierpont. Rungs 4 and 5 start at 37441 and 202753, not Pierpont. Selection effect.
- **|λ₂|.** 19 Pierpont primes ≤ 1500 against their four nearest non-Pierpont neighbours: paired difference +0.0089, t = +1.22; for p ≥ 97, +0.0024, t = +0.64. **Null.**
- **Content.** Content/(p − 1) is larger for Pierpont primes (0.043 against 0.009). That is group theory: in a cyclic group of 3-smooth order the subgroup ⟨3⟩ has index 1 with probability 1/3 instead of about 1/2. Nothing about the kernel.
- **6^{2^j} + 1 (7, 37, 1297).** 6^{2^j} = −1 constrains (v₂ ord 2, v₂ ord 3): rungs −1, 1, 2. A constraint on orders, not a property of the kernel. 6⁸ + 1 = 17·98801 is not prime.

**Role of 36:** 37 = 6² + 1 puts 37 on rung 1 (±i/2, the theorem). Its sporadic ±½ are not shared by 7 or 1297.

## 8. Q3.6 Link to the Fibonacci / icosian thread

Only the field. Both threads meet Q(√5) = Q(ζ₅)⁺ and its Galois involution, which exchanges pentagon and pentagram: here it is x → 3x on Z/5 swapping sides and diagonals, there it is the exchange of E_par and E_perp and of {5} and {5/2} faces. Beyond that the mechanisms are different in kind. The icosian ladder is Diophantine and archimedean: φ acts as a unit on a rank-2 module, F_{n+1}/F_n approximates it, and the error shrinks like φ^{−2n}; its group is A₅. The golden eigenvalue of K_5 is finite and exact: five special points of the map coincide with the five residues, the group is the solvable AGL(1,5), there is no approximation and no ladder. The census confirms the absence of a ladder: no golden eigenvalue at the levels 25, 125, 55, or at the Fibonacci and Lucas primes 11, 13, 29, 89, 199. The Fibonacci-looking matrix [[−1, 1], [1, 0]] on the golden plane is forced by Latimer–MacDuffee for any integer operator with characteristic polynomial x² + x − 1, so it is not evidence of a shared mechanism either. The Lucas numbers in tr(A_5^n) are the same statement again. One sentence for the owner: cos 36° = φ/2 is a true and exact fact about the 3x+1 map modulo 5, and it is a fact about the regular pentagon, not about Fibonacci approximants.

## 9. Prior art (brief searches; "not found" means not found in these searches)

- **The chain.** Matthews & Watts, Acta Arith. 43 (1984) and 45 (1985); Leigh, Acta Arith. 46 (1986); Matthews, Colloq. Math. 63 (1992): Markov matrices of generalised Collatz maps modulo m, used for limiting frequencies. No eigenvalue analysis modulo primes prime to 6 found.
- **Random affine walks mod p.** Chung, Diaconis & Graham, Ann. Probab. 15 (1987); Hildebrand, Ann. Probab. 21 (1993) and later: X_{n+1} = a_n X_n + b_n (mod p), mixing in O((log p)²) steps. The Terras kernel is such a walk with (a, b) ∈ {(½, 0), (3/2, ½)}. Exact spectra for it: not found.
- **Kronecker 1857** for both theorems on algebraic integers. **Latimer & MacDuffee 1933** for integer matrices with given characteristic polynomial. **Sachs 1964** coefficient theorem. **Exact lumpability**: Schweitzer 1984; Buchholz, J. Appl. Probab. 31 (1994). Distance partitions of a cycle: Brouwer–Cohen–Neumaier.
- **Within the repo** (SCRUM-30 worktree, read-only): the spectrum of K_5, the theorem −½χ(2) ∈ spec for χ(3) = −1 and its proof, the μ_m symmetry, the 0-eigenvalue criterion, the splitting of the characteristic polynomial mod p, the conjecture and its exceptions 11, 23, 31, 37. This thread builds on all of it.
- **OEIS (checked by terms, 2026-10-06).** A054877, closed walks of length n on a pentagon based at a vertex, 1, 0, 2, 0, 6, 2, 20, 14, 70, …, with the formula 5a(n) = 2^n + 2(−1)^n L_n: this is the return count of the corollary to Theorem A, so the Lucas formula is known. A038519, 1, 0, 1, 3, 2, 10, 16, 28, 72, …, is A_n. Not in the OEIS: B_n (§3.5) and tr(A_5^n).
- **The folding itself** is the standard quotient of the cycle C_5 by a reflection (an equitable partition; Godsil & Royle, *Algebraic Graph Theory*, ch. 9). Nothing about it is new; the content of Theorem A is that the 3x+1 kernel modulo 5 has this quotient.
- **Searches in the skeptic pass** (2026-10-06): "Matthews Watts Markov matrix generalized Collatz modulo m eigenvalues", "Chung Diaconis Graham ax+b mod p eigenvalues two affine maps", "Collatz 3x+1 modulo 5 Markov chain golden ratio pentagon", "sum of two permutation matrices affine maps finite field spectrum". Nothing on the spectrum of the 3x+1 residue chain modulo a prime, on the pentagon quotient, on Theorem B, or on F₁, F₂ was found. Lagarias's annotated bibliography (arXiv math/0309224) lists the Matthews–Watts and Leigh chains without eigenvalue results for moduli prime to 6. Tao's Syracuse random variables (2019) concern the map modulo 3^n, a different object. A Zenodo preprint (Hughes, 2025, record 18024028) uses the words "mod-5 Golden" for an unrelated, unreviewed framework; it is not prior art for anything here.
- **Not found:** the folded-pentagon statement for K_5; Theorem B; the conditions F₁, F₂; Proposition F′; the eigenvalues (2λ)⁵ = −3 at 41. All are elementary and may be folklore. Absence from a handful of searches is weak evidence of novelty, and none is claimed.

## 10. Dead ends and corrections made during the run

- A first guess that the additive pentagon's adjacency algebra explains x² + x − 1: refuted (§3.4).
- Looking for an order-3 or affine symmetry preserving the sporadic eigenspaces at 37: none of the 1331 non-trivial affine maps preserves any of them (`q34d_side_checks.log` (b)).
- Compressions of R_e, R_o to the sporadic eigenspaces at 37: characteristic polynomials 40x² ∓ 151x − 182 and 40x² ± 71x − 293, no structure (`q34d_side_checks.log` (d)).
- "Both branches involutions iff a² = b² = 1": wrong for composite N (b² = 1 gives a translation for o²). Corrected to b = −1; the first version of the table had 31 spurious exceptions.
- A duality d ↔ 1/d of the family (d+1, d): the kernels for d = 2 and d = ½ (the semigroup kernel of x → 2x, x → 3x + 1) have the same spectrum at p = 7 and different spectra at 11, 13, 31, 37. Not a symmetry of the spectrum. It is an exact symmetry of the single eigenvalue −½ (Proposition F′), which is why the two kernels share x + 1 with equal multiplicity at 7, 11, 31, 37 and both lack it at 13 (`q34d_side_checks.log` (c)).
- The binomial event x⁴ = 3 for K⁻ at 13 looked like a companion of x⁵ = −3 at 41; it is forced by a dimension count.

## 11. Leads not finished

1. Prove or refute: the golden pair at level 5 is the only irrational cosine of the 3x+1 kernel at any level.
2. Explain 37: the eigenvalue −½ at the three divisors d = 2, 12, 17 (their inverses follow by Proposition F′), the link d → −1 − d between them, and the multiplicity 2 at d = 2.
3. Explain (2λ)⁵ = −3 at 41 = 2⁵ + 3². Modulo 41 the five eigenvalues sit on the degrees n ≡ −1 (mod 8), where 3^n = 1/3 and κ_n = (4/3)·2^{−n}; g_41 has degree only 8 = ord_41(3), so a chance integer root is not far-fetched.
4. The family G_N: why golden at 11 and 19 and √2 at 7 and 23, with no folding.
5. Irreducibility of the generic factor of prim_N.
6. The sporadic scan now reaches 7993 at cost O(p²) per prime (`verify/v3_krylov_scan.py`); 10⁵ is within reach of a compiled version. The signed kernel K⁻ has not been rescanned beyond the original caps.
7. Eigenvalue 0 at composite levels: prove the rule of Proposition E′(c) by carrying the Jacobi-sum computation to (Z/N)^×, and state it for general N (the expected condition is the vanishing of a period Σ_{h ∈ ⟨3⟩} ζ_N^{ch}).

## 12. Files and reproduction

Run each as `C:/repos/collatz/.venv/Scripts/python.exe -X utf8 <script>` from this directory. Single process each.

| script | output | time | content |
|---|---|---|---|
| `gk_common.py` | — | — | exact characteristic polynomial (Hessenberg mod 24-bit primes + CRT with a proved bound), Ψ_j, Φ_k, integer polynomial arithmetic |
| `selftest_common.py` | `.log` | 11 s | agreement with sympy on charpolys, Ψ_j (j ≤ 40 and four more), Φ_k |
| `q31_pentagon.py` | `.log`, `.json` | 2 s | Q3.1, 39 exact checks |
| `fig_pentagon.py` | `fig_pentagon.png` | 2 s | the figure |
| `q32_kronecker_census.py` | `.log`, `.json` | 216 s | census N ≤ 400 |
| `q32b_real_spectrum_theorem.py` | `.log`, `.json` | 4 s | ingredients of Theorem B, N ≤ 3000 |
| `q33_qd_survey.py` | `.log`, `.json` | 12 s | (q, d, N) survey |
| `q33b_mechanisms.py` | `.log`, `.json` | 80 s | mechanisms, family G_N, reflection kernels (needs `q33_qd_survey.json`) |
| `q34_anatomy_37.py` | `.log`, `.json` | 5 s | K_37, two-variable polynomial, two-point search, anatomy, shadow, double eigenvalue |
| `q34b_sporadic_scan.py` | `.log`, `.json` | 337 s | sporadic scan, primes ≤ 800, K and K⁻ |
| `q34c_family_base_rate.py` | `.log`, `.json` | 22 s | family (d+1, d): F₁, F₂, polynomial search, base rate |
| `q34d_side_checks.py` | `.log` | 3 s | irreducibility at θ ≠ ±1, affine-symmetry search at 37, the 2x / 3x+1 semigroup kernel, compressions |
| `q35_pierpont.py` | `.log`, `.json` | 19 s | Pierpont comparison |

Skeptic's checks, in `verify/`. None imports `gk_common.py`; run from `verify/`.

| script | output | time | content |
|---|---|---|---|
| `v1_pentagon.py` | `.log` | 34 s | Theorem A, the corollary on integers (k ≤ 16, window with negatives), all exactly lumpable partitions of Z/5, Z/7, Z/11, trace and word identities with integer C(w), mirror 3x−1, cousins 3x+c, 5x+1, 7x+1 |
| `v2_census.py [N_MAX] [q] [N_MIN]` | `v2_census.log`, `v2_census_q5.log` | 114 s (N ≤ 400), 3 s (q = 5, N ≤ 200) | independent census: power sums + Newton + CRT; diff against `q32_kronecker_census.json` |
| `v3_krylov_scan.py [P_MAX] [P_MIN]` | `v3_krylov_scan_3000.log`, `_3001_6000.log`, `_6001_8000.log` | 43 s, 209 s, 190 s | degree-certified scan of all primes ≤ 7993, every order |
| `v4_family.py [P_MAX]` | `.log` | 32 s | Proposition F on 585 roots, base rate, Proposition F′ |
| `v5_anatomy.py` | `.log` | 3 s | exact anatomy at 37, 41, 31, 11, 13, 23; Proposition D by interpolation; eigenvalue 0 at 275; controls for the characteristic-p shadow |
| `v6_survey.py` | `.log` | 38 s | (q, d, N) survey, family G_N, Theorem B ingredients for 3x±1, 5x+1, 7x+1 |
| `v7_pierpont.py` | `.log` | 19 s | Pierpont rungs, χ², \|λ₂\| |
| `v8_twopoint_irreducible.py` | `.log` | 7 s | two-point search to p < 300; irreducibility certificates for N ≤ 79 |
| `v9_zero_jordan.py` | `.log` | 2 s | Proposition E′: the pairing criterion, primes below 3000, the rule at p²q |

## 13. Skeptic pass (2026-10-06)

A second pass by a reviewer who did not do the work: every claim re-derived or recomputed with separate code, mirror and cousin tests run, controls added, prior art searched, and this README edited in place.

**Verdict in one line.** The proofs hold and every computed table was reproduced. Nothing was refuted outright. Three statements were wrong or overstated and are corrected above; one result is prior art that was not cited; one new exact symmetry was found; the main scans were extended tenfold.

**What was changed.**
1. *Headline wording.* "The residue chain modulo 5 is exactly a pentagon walk" overstated Theorem A. The five-state chain is not a pentagon walk (different characteristic polynomial, no relabelling works, only the start n ≡ 1 gives the pentagon law). The true statement is an exact three-cell quotient on cell-uniform measures. §0, §2 row A, §3.2 and §3.4 now say so.
2. *Prior art.* The return counts of the corollary are OEIS A054877 and its Lucas formula is on that page; A_n is A038519. Added to §3.2, §3.5, §9. The folding of C_5 is the textbook quotient by a reflection.
3. *Scope sentence.* "The same chain for every 3x+c" needs c prime to N. Fixed, with the counterexample 3x+5 modulo 5.
4. *Eigenvalue 0 (§4.3).* "Exactly double at the nine non-squarefree levels with a zero" was false as written: there are ten such levels and 275 = 5²·11 does not double. Corrected, and replaced by Proposition E′, which proves semisimplicity at every prime and gives a rule for p²q that predicted six further levels correctly.
5. *Sporadic list (§6.3, row H).* "Complete for all primes ≤ 800" was not what the scan established: above 400 it tested orders ≤ 60 only. The claim is now established, and for all primes ≤ 7993 with no cap, by a different and sound method. The K⁻ list keeps the original caps and says so.
6. *The "node" at 37.* Removed as a finding. Vanishing of P and its first derivatives at a double semisimple eigenvalue is automatic. What remains is the multiplicity and the irreducible first-order splitting.
7. *The orbit of six at 37.* Reduced to three coincidences by the new Proposition F′ (the eigenvalue −½ is invariant under d → 1/d). The sentence "one fact argues against pure chance" is gone.
8. *The dodecagon in characteristic 37.* Labelled numerology as an explanation, with the control at p = 181 and the base rate (a residue ±1 exists at about 70 % of primes and lifts at three).
9. *Role of 36.* Two notes added: the "half-period (2,2)" at 37 holds for every Pierpont prime with its own exponents, and every Collatz cell (k, s) has its own special moduli, so the appearance of (2,2) in Theorem B is the second power sum, not the number 36.
10. *Pierpont χ².* Caveat on small expected counts and low power added.
11. *Ranges.* Corollary k ≤ 16; F₁, F₂ on 585 roots (p ≤ 2000); Theorem B ingredients N ≤ 5000; two-point search p < 300; irrational-cosine and sporadic scans to 7993.

**New in this pass.**
- Proposition F′ (§6.2), proved and checked on 2320 kernels.
- Proposition E′ (§4.3): 0 is a semisimple eigenvalue of K_p at every prime (proved, through Jacobi sums and the non-vanishing of Gaussian periods), with a pairing criterion valid for all N and a computed rule at p²q that explains the exception 275.
- The degree-certified Krylov scan (§6.3): O(p²) per prime and still a proof of absence.
- Cousin data: 5x+1 has no irrational cosine at any level ≤ 200, has ±½ at only 5 and 4 of 79 levels (against 68 and 65 of 132 for 3x+1), and its only all-real level is 3.

**Mirror test, restated.** Every statement in this README is identical for 3x−1 (checked directly for Theorem A, the corollary on integers, the characteristic polynomial modulo 5, and the Theorem B counts to N = 5000). None bears on the conjecture. The statements do separate 3x+1 from 5x+1, through the relation 3 = 2 + 1 (Theorem C, F₁, F₂, F′) and through 3 + 2 = 5 (Theorem A).

**Numerology test, restated.** 36 itself enters nowhere. The pentagon is at 5 = 3 + 2. 37 is on the exceptional list without a mechanism, in a family where a quarter of the kernels at that prime are exceptional. 41 = 2⁵ + 3² is a description, not a cause.

**Not checked.**
- The repo-internal attributions in §9 (which parts of Theorem C, the μ_m symmetry and the degree-filtration lemma are in the SCRUM-30 worktree). The proofs given here were checked on their own.
- The phrase "the repo's hidden-colour bias" in §3.5.
- Irreducibility of the generic factor for the 80 levels between 80 and 400 beyond the original sympy factorisation.
- The minimal-support upper bounds at 41, the affine-symmetry search at 37, the compressions of R_e, the irreducibility of P_p at θ = ±2, ±3, 5, and the polynomial search for a third universal condition (§6.3 item 3): the logs were read, not recomputed.
- The dilation + reflection table at the end of §5, and the lumping failures at (4,3,7), (6,5,11), (10,9,19), (12,11,23).
- K⁻ beyond p = 23.

`fig_pentagon.png` was regenerated with one change: the title read "is a folded pentagon walk" and now reads "folds onto a pentagon walk (3 cells)".
