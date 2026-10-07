# Thread 5 — Nicomachus, the 3×3 divisor grid, and lattice paths under log₂3

Written 2026-10-06.  One of five threads on "does 36 = 2²·3² say anything about Collatz?".
This thread starts from 36 = 1³+2³+3³ = (1+2+3)² (Nicomachus) and Liouville's generalisation
Σ_{d|n} τ(d)³ = (Σ_{d|n} τ(d))².

**Bottom line, stated before anything else.**

* 36 genuinely enters exactly one place: it is the largest fixed point of
  F(n) = Σ_{d|n} τ(d) = τ₃(n), and that is a fact about 36 = T₃² = (2·3)², the sum of the first
  three cubes.  It is a fact about a *toy* system, not about Collatz.  The fixed points are OEIS
  A097989 (2004; also De Koninck's entry for 36); the full dynamics of F is proved here in a few
  lines.  The reason is self-referential: τ₃(p²q²) = T₃² for every pair of primes, and T₃ = 6
  happens to be 2·3.
* On the Collatz side the number 36 does nothing.  What governs the dropping-word counts
  (OEIS A100982) is the continued fraction of log₂3.  The strongest statement — A100982 is squeezed
  between two cycle-lemma binomial bounds and attains them exactly at the semiconvergent
  denominators, where its values are rational Catalan numbers — was published three weeks ago by
  Mike Winkler (arXiv:2609.22303, 14 Sep 2026).  This thread re-verifies it (to s = 2218, the whole
  OEIS b-file) and records two corollaries, neither of which is a new theorem: the exact
  *window* of orders on which each rational slope reproduces A100982 (immediate from Winkler's
  Proposition 9 and the classical theory of one-sided best approximations), and Bizley's 1954
  formula applied inside those windows, which gives closed forms at the multiples s = k·Qₙ of
  convergent denominators (orders that are not equality orders of his sandwich; whether anyone
  has written these values down before is unknown).
* Every path statement here is identical for 3x+1 and 3x−1.  None of it bears on the conjecture.

---

## 0. Conventions (apply to every table below)

* Shortcut (Terras) map T(n) = n/2 (n even), (3n+1)/2 (n odd).
* A **dropping word of order s** is a 0/1 word (1 = odd step) with exactly s ones in which every
  proper prefix with j letters and s_j ones has 2^j < 3^(s_j), and the whole word of length L has
  2^L > 3^s.  Then L = ⌊s·log₂3⌋ + 1 (OEIS A020914).
* N(s) = number of dropping words of order s = **OEIS A100982**(s), offset 1:
  1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, …
* Paper 1 (`collatz.dropping.dropping_time`) counts 3n+1 and n/2 as separate steps, so its dropping
  time is k = L + s (OEIS A122437); `dropping_time(3) = 6`.  The dropping orbit includes n, the
  stopping orbit excludes it; nothing below depends on that difference.
* Beatty form (same as Winkler's): with α = log₂3 and m_i = ⌊iα⌋,
  N(s) = #{1 ≤ t₁ < … < t_(s−1) : t_i ≤ m_i}, t_i = number of letters before the (i+1)-th one.
* For a rational slope a/b two boundaries are used:
  **weak** m_i = ⌊i·a/b⌋ (a lattice point on the rational line is allowed) and
  **strict** m_i = ⌈i·a/b⌉ − 1 (forbidden).  c_s(a/b) is the count with that boundary.
* F(n) = Σ_{d|n} τ(d) = τ₃(n) = Π T_(a_i+1) over the prime exponents a_i, T_m = m(m+1)/2.
  "Transient length" t(n) = least t with F^t(n) periodic.

Verification of the conventions against the repo package (`q5x_verify_classes_and_mirrors.log`):

| s | L (shortcut) | k = L+s (Paper 1) | residue classes mod 2^L with `dropping_time` = k | A100982(s) |
|---|---|---|---|---|
| 1 | 2 | 3 | 1 | 1 |
| 2 | 4 | 6 | 1 | 1 |
| 3 | 5 | 8 | 2 | 2 |
| 4 | 7 | 11 | 3 | 3 |
| 5 | 8 | 13 | 7 | 7 |
| 6 | 10 | 16 | 12 | 12 |
| 7 | 12 | 19 | 30 | 30 |
| 8 | 13 | 21 | 85 | 85 |
| 9 | 15 | 24 | 173 | 173 |

N(s) was also compared with the OEIS b-file of A100982 for s = 1..1000: all agree.  The skeptic
pass (`verify/v4_paths_independent.log`) recomputed N(s) three independent ways (word DP to
s = 2218 = the whole b-file, Zarubin's inclusion–exclusion recursion to s = 700, brute-force word
enumeration to s = 14), extended the class table to s = 11 (476 and 961 classes for s = 10, 11)
with its own dropping-time code, and found no member n ≥ 2 of any class that drops at a different
time.  "Class" means a residue class mod 2^L of the *coefficient* stopping time (Terras); that
every member n ≥ 2 actually drops at step L is the coefficient-stopping-time conjecture, checked
here only on small and large representatives.

---

## 1. Results table

Status labels: **proved** (proof in this file), **computed** (exact computation, range stated),
**prior art**, **null**, **numerology**, **open**.

| id | statement | status | role of 36 |
|---|---|---|---|
| Q5.1-a | F(n) = n ⇔ n ∈ {1, 3, 18, 36} | **prior art**: OEIS A097989 (Beedassy 2004, keywords fini, full; it cites De Koninck, *Ces nombres qui nous fascinent*, entry 36, and De Koninck–Mercier, *1001 problèmes*); self-contained proof in §2 | genuine: 36 = T₃·T₃ = (2·3)², exponent point (2,2) |
| Q5.1-b | n ∈ {1,3,18,36} ⇔ n equals the number of intervals e \| d \| n of its own divisor lattice ⇔ Σ_{d\|n} τ(d)³ = n² | proved (restatement + Liouville; A097988) | genuine: a 3×3 board has C(4,2)² = 36 rectangles |
| Q5.1-c | for k ≥ 2: T_k² = 1³+…+k³ is a fixed point of τ_k ⇔ T_k is a product of two distinct primes ⇔ k ∈ OEIS A164977 (3, 4, 5, 6, 10, 13, 22, 37, …) | proved (§3.4); checked for k ≤ 20 000 (379 values). The index set is exactly A164977 ("m such that m(m+1)/2 is the product of two primes"; T_m is never a prime square), the T_k are A068443; the fixed-point statement itself was not found in OEIS or by web search. Elementary; no novelty claimed | genuine: 36 is the first member (k = 3) of the family 36, 100, 225, 441, 3025, 8281, … All members have the signature p²q² (the "(2,2)" part is general); the primes {2,3} are the accident T₃ = 6 |
| Q5.2-a | every F-orbit is eventually periodic; the attractors are exactly the fixed points 1, 3, 18, 36 and the 2-cycle {6, 9} | proved (§3.1); sieve check to 10⁷, repeated from the definition (two additive divisor sieves) in `verify/v1` | 36 is the largest attractor |
| Q5.2-b | F(n) > n ⇔ n ∈ {2,4,6,8,12,24}; sup F(n)/n = 3/2, attained exactly at n = 2, 4, 6, 12 | proved (§3.1) | indirect: the expansion set is {2^a·3^b : 1 ≤ a ≤ 3, b ≤ 1}; (2,2) sits on its boundary |
| Q5.2-c | basin of 1 is {1}; basin of 3 is exactly the set of primes | proved (§3.2) | none |
| Q5.2-d | basin sizes and transient-length distribution for n ≤ 10⁷ (tables in §3.3) | computed (reproduced exactly by `verify/v1`) | basin of 36 holds 0.14 % of n ≤ 10⁷ |
| Q5.2-e | least n with transient length t, among all n < 10⁴⁰: t = 0..12 (table §3.3); t = 13 occurs (an example near 10⁷¹, none below 10⁴⁰); is t unbounded? | computed (reproduced by `verify/v5`); unboundedness **open** — it follows from Dickson's conjecture (§3.3) | none |
| Q5.2-f | "F multiplies by 3/2 like the Collatz step in v = n+1" | numerology: true at four integers only | none |
| Q5.2-g | cousins τ_k, k = 2..8: complete lists of fixed points and cycles (§3.5); τ₅ repeats the τ₃ pattern with (2,3) → (3,5): 1, 5, 75, 225, {15, 25} | computed by an exact finite enumeration (pruning bound proved, Lemma 1); reproduced by an independent enumeration and by brute force to 3·10⁶ (`verify/v2`) | 36 ↔ 225 = 1³+…+5³ |
| Q5.3-a | Liouville on the grid of 2^k·3^s is the product of two Nicomachus identities | prior art (Liouville 1857; one line) | n = 36 is the case k = s = 2, where both sides are 36² |
| Q5.3-b | no Nicomachus-type identity Σx³ = (Σx)² among Collatz path counts: 54 889 multisets tested, 0 non-trivial hits (skeptic re-run: 209 434 multisets, 0 non-trivial hits) | **null** | none |
| Q5.3-c | the only hits are literal {1,…,m}: column "one even step" of the admissible triangle is 1, 2, 3, … | proved (trivial) | A100982(2..4) = 1, 2, 3 gives 36 — numerology |
| Q5.3-d | #intervals = (#maximal chains)² on the (k+1)×(s+1) grid only for (k,s) = (0,0) and (2,2), for all k ≤ s | proved (elementary, §4); a curiosity with no Collatz content — **numerology** as far as the question goes | 36 = T₃·T₃ = C(4,2)²; the mechanism is only that a 3×(s+1) grid has T_(s+1) maximal chains |
| Q5.4-a | (1/s)·C(m−1, s−1) ≤ N(s) ≤ (1/s)·C(m, s−1), m = ⌊s·log₂3⌋, with equality exactly at the denominators of the lower / upper one-sided best approximations of log₂3 | **prior art**: Winkler, arXiv:2609.22303 (Thm 6–8). Re-verified here for s ≤ 2218 | none |
| Q5.4-b | **window**: if a/b is a one-sided best approximation of log₂3 and b⁺ is the next order on the same side, then c_s(a/b) = N(s) ⇔ s ≤ b⁺ (natural convention); in the other convention ⇔ s ≤ b.  Cell form: for every real β > 1, c_s(β) = N(s) ⇔ ℓ_s ≤ β < u_s, the best lower / upper approximations with denominator < s | proved (§5.2), but **not a new theorem**: it is Winkler's Prop. 9 (the constant cells of α ↦ c_s(α)) plus the classical description of one-sided best approximations (Hančl–Turek; Berstel–Séébold). Only the explicit b⁺ is not written in arXiv:2609.22303 | none |
| Q5.4-c | **Bizley closed forms**: for a convergent P/Q of log₂3 and k ≤ 1 + ⌊Q′/Q⌋ (Q′ the next convergent denominator): N(kQ) = φ_k(P−Q, Q) (lower convergent) or ψ_k(P−Q, Q) (upper) | proved given Bizley 1954 (§5.3), a corollary of Q5.4-b; verified for all cases with kQ ≤ 2218 by direct lattice-path counting. Not in arXiv:2609.22303 (coprime endpoints only); Winkler's two ResearchGate preprints could not be read (HTTP 403), so novelty is **unknown** | N(36) = 38 088 111 350 198 is one of these values, because 36 = 3·12 and 12 is a convergent denominator. Accident of 36 = 3·12, not of 36 = 2²·3² |
| Q5.4-d | for every s ≤ 7: N(s) = A047749(s) = (s−2h+1)/(s+h+1)·C(s+h+1, h), h = ⌊s/2⌋ | proved (window for 3/2 + classical ballot theorem with integer slope 2); verified.  For s = 1, 2, 3, 5, 7 this is Winkler's Theorem 8; only s = 4 and s = 6 are extra, and they are the cases k = 2, 3 of Q5.4-c | none; the window ends at 7 = 2+5 |
| Q5.4-e | OEIS identification of the rational counts (§5.4) | prior art / computed | none |
| Q5.4-f | Gersonides' pairs (2,3), (3,4), (8,9) are the first three convergents 1/1, 2/1, 3/2; their rational counts leave A100982 after s = 2, 3, 7 | proved (special case of Q5.4-b) | (8,9) is the cell (3,2), not (2,2) |
| Q5.4-g | all of Q5.4 is identical for 3x−1 (the classes are the negatives) and different for 5x+1 (A174795), 7x+1 (A174796) | proved (conjugation n → −n) + computed | none |
| Q5.5-a | #{3-smooth ≤ 2^K} = Σ_b (K+1−⌈b·log₂3⌉) (OEIS A022331); no identity involving T₈ | **null**; G(6) = 36 is numerology | none |
| Q5.x | every dropping word with s ≥ 2 starts 11, i.e. passes through the cell 2² vs 3² | proved (trivial; this is the repo's "a₁ = 1 always", n ≡ 3 mod 4) | none beyond naming: the cell (1,1) (2 vs 3, "6") is forced in the same way, and (2,2) is forced only because 3 < 4 — for 5x+1 and 7x+1 the only forced cell is (1,1).  **Numerology** as a statement about 36 |

---

## 2. Q5.1 — the fixed points of F

F(n) = Σ_{d|n} τ(d) is the Dirichlet convolution 1∗1∗1 = τ₃ = d₃, OEIS A007425: the number of
ordered factorisations n = r·s·t, equivalently the number of pairs e | d | n, i.e. the number of
intervals [e, d] of the divisor lattice.  It is multiplicative with F(p^a) = C(a+2, 2) = T_(a+1).

Write g(p, a) = T_(a+1) / p^a, so F(n)/n = Π g(p_i, a_i).

```
g(2,a): 1, 3/2, 3/2, 5/4, 15/16, 21/32, …   (ratio g(2,a+1)/g(2,a) = (a+3)/(2a+2) < 1 for a ≥ 2)
g(3,b): 1, 1,   2/3, 10/27, …               (ratio (b+3)/(3b+3) < 1 for b ≥ 1)
g(p,c) ≤ 3/p ≤ 3/5 for p ≥ 5, c ≥ 1         (ratio (c+3)/(p(c+1)) < 1)
```

**Theorem 1.**  E₃ := {n : F(n) ≥ n} = {1, 2, 3, 4, 6, 8, 12, 18, 24, 36}, with F(n) = n exactly for
n ∈ {1, 3, 18, 36} and F(n) > n exactly for n ∈ {2, 4, 6, 8, 12, 24}.

*Proof.*  If a prime p ≥ 5 divides n then F(n)/n ≤ (3/2)·1·(3/5) = 9/10 < 1.  So n = 2^a·3^b.
If b ≥ 3 then F(n)/n ≤ (3/2)(10/27) < 1.  If b = 2 we need g(2,a) ≥ 3/2, which forces a ∈ {1, 2} and
gives equality: n = 18, 36.  If b ∈ {0, 1} then g(3,b) = 1 and we need g(2,a) ≥ 1: a = 0 gives
equality (n = 1, 3); a = 1, 2, 3 give strict inequality (n = 2, 4, 8 and 6, 12, 24); a ≥ 4 fails. ∎

*Combinatorial meaning.*  The divisor lattice of 2^a·3^b is the (a+1)×(b+1) grid; its intervals
are the (possibly degenerate) sub-rectangles, T_(a+1)·T_(b+1) of them.  So 36 is the largest
integer equal to the number of intervals of its own divisor lattice: the 3×3 grid has
C(4,2)² = 36 of them.  By Liouville, Σ_{d|n} τ(d)³ = F(n)², so the same four numbers are the
solutions of Σ_{d|n} τ(d)³ = n².

*Prior art.*  OEIS **A097989** "Numbers n such that n = tau_3(n) = A007425(n)": 1, 3, 18, 36
(Lekraj Beedassy, 2004; keywords fini, full), with the comment "n is equal to the total number of
divisors of all divisors of n" and references to J.-M. De Koninck, *Ces nombres qui nous
fascinent* (entry 36) and De Koninck–Mercier, *1001 problèmes en théorie classique des nombres*.
A097988 is Σ_{d|n} τ(d)³ = (Σ_{d|n} τ(d))².  Nothing here is new.

*How special is this?* (`verify/v5_controls.log`)  Every prime p is a fixed point of τ_p
(τ_k(p) = k), so "n is a fixed point of some k-fold divisor function" is not rare.  The
*composite* numbers ≤ 300 with that property are 18, 36 (k = 3), 75, 225 (k = 5) and 100, 200,
224 (k = 4); 36 is the smallest square among them.  So the property does single out 36 among its
neighbours (35, 37, 48 do not have it non-trivially), but it is one of seven such numbers below
300, and it singles 36 out inside a toy.

*Role of 36.*  Genuine.  In exponent coordinates the fixed points are (0,0), (0,1), (1,2), (2,2);
(2,2) is the outermost lattice point of the bounded region T_(a+1)·T_(b+1) ≥ 2^a·3^b.  That region
is a bounded neighbourhood of the origin.  It has nothing to do with the line of slope log₂3,
which is unbounded and passes far from (2,2) (2² < 3²).  Gersonides' theorem is *not* needed for
the proof.  (One can argue through it — T_(a+1)·T_(b+1) = 2^a·3^b forces both factors to be
3-smooth triangular numbers, so a+1, b+1 ∈ {1, 2, 3, 8} — but that is a detour, and the factor
T₈ = 36 never occurs at a fixed point.)

*Mirror test.*  Not applicable: no Collatz statement is made.

---

## 3. Q5.2 — F as a toy dynamical system

### 3.1 Complete solution

**Theorem 2.**  Every orbit of F is eventually periodic.  The periodic orbits are the fixed points
1, 3, 18, 36 and the 2-cycle 6 ↔ 9, and no others.  sup F(n)/n = 3/2.

*Proof.*  By Theorem 1, F(n) < n for n ∉ E₃, so an orbit strictly decreases until it enters E₃.
From E₃: 1, 3, 18, 36 are fixed; 2 → 3; 4 → 6 → 9 → 6; 8 → 10 → 9; 12 → 18;
24 → 30 → 27 → 10 → 9.  A cycle of length ≥ 2 has a least element m with F(m) > m, so
m ∈ {2, 4, 6, 8, 12, 24}; of these only 6 lies on a cycle.  The ratio list gives the supremum. ∎

Each attractor is "the F-value of its own prime signature":

| signature | F | example |
|---|---|---|
| p | 3 | 3 → 3 |
| p·q | 9 | 6 → 9 |
| p² | 6 | 9 → 6 |
| p·q² | 18 | 18 → 18 |
| p²·q² | 36 | 36 → 36 |
| p⁷ | T₈ = 36 | 128 → 36 |

F(n) = 36 ⇔ n = p⁷ or n = p²q² (the two ways to write 36 as a product of triangular numbers > 1:
T₈ and T₃·T₃).  This is the one place where "36 is both triangular and square" is literally used.

### 3.2 Two basins in closed form

**Proposition.**  The basin of 1 is {1}; the basin of 3 is exactly the set of primes.

*Proof.*  F(n) = 1 ⇔ n = 1.  F(n) = Π T_(a_i+1) with every factor in {3, 6, 10, 15, …}; T_m is prime
only for m = 2.  So F(n) is prime ⇔ F(n) = 3 ⇔ n is prime, and no non-prime maps to a prime. ∎

### 3.3 Computed tables (n ≤ 10⁷, `q51_q52_tau3_dynamics.log`)

Basin sizes #{n ≤ X}:

| X | 1 | 3 (= π(X)) | 18 | 36 | {6,9} |
|---|---|---|---|---|---|
| 10³ | 1 | 168 | 149 | 11 | 671 |
| 10⁴ | 1 | 1 229 | 1 316 | 50 | 7 404 |
| 10⁵ | 1 | 9 592 | 13 269 | 244 | 76 894 |
| 10⁶ | 1 | 78 498 | 140 650 | 1 594 | 779 257 |
| 10⁷ | 1 | 664 579 | 1 494 407 | 14 010 | 7 827 003 |
| share at 10⁷ | — | 6.65 % | 14.94 % | 0.14 % | 78.27 % |

The shares drift with X (the basin of an n is decided by its prime signature, whose distribution
moves on the log log X scale).  No claim is made about limiting densities, except that the share
of the basin of 3 tends to 0 by the prime number theorem.

Transient length t(n), n ≤ 10⁷ (mean 3.134):

| t | count | least n | orbit of the least n |
|---|---|---|---|
| 0 | 6 | 1 | periodic points 1, 3, 6, 9, 18, 36 |
| 1 | 2 927 343 | 2 | 2 → 3 |
| 2 | 98 391 | 8 | 8 → 10 → 9 |
| 3 | 4 512 337 | 30 | 30 → 27 → 10 → 9 |
| 4 | 160 480 | 24 | 24 → 30 → 27 → 10 → 9 |
| 5 | 1 016 192 | 60 | 60 → 54 → 30 → … |
| 6 | 458 414 | 72 | 72 → 60 → … |
| 7 | 546 582 | 180 | 180 → 108 → 60 → … |
| 8 | 148 503 | 360 | 360 → 180 → … |
| 9 | 121 494 | 1 800 | 1800 → 360 → … |
| 10 | 10 258 | 37 800 | 37800 → 1800 → … |

Beyond the sieve (exact, over all 5 754 126 least-of-signature numbers below 10⁴⁰):
t = 11 first at n = 49 896 000 = 2⁶3⁴5³·7·11, t = 12 first at n = 105 700 299 921 216 000
= 2⁹3⁶5³7³11²13²·17·19; no n < 10⁴⁰ has t ≥ 13.  The Collatz-style "dropping time" (first t with
F^t(n) < n) is 1 for every n ∉ E₃.  The sequence of least n (1, 2, 8, 30, 24, 60, 72, 180, 360,
1800, 37800, 49896000, …) was not found in OEIS (search 2026-10-06).

**Open.**  Is t(n) unbounded?  A number has a preimage iff it is a product of triangular
numbers > 1; to continue a backward chain one needs, at every step, a preimage that is again such a
product.  The t = 12 record does have one (it equals 136·171·91²·55²·28·10·6³·3 =
T₁₆T₁₈T₁₃²T₁₀²T₇T₄T₃³T₂), so every number with signature (17,15,12,12,9,9,6,3,2,2,2,1) has
t = 13; the least of them is about 10⁷¹, and the least n with t = 13 was not determined.

*Conditional answer (skeptic pass, `verify/v5_controls.log`).*  A squarefree n with j ≥ 3 prime
factors goes n → 3^j → T_(j+1), so t(n) = 2 + t(T_(j+1)) (checked for j < 60).  Hence if
(H) *for every j ≥ 3 there is a squarefree triangular number with exactly j prime factors*,
then t is unbounded: start with j₀ = 3 and let j_(i+1) = m − 1 where T_m is squarefree with
exactly j_i prime factors; squarefree numbers with j_i prime factors then have t = 3 + 2i.
(First two steps: T₁₁ = 66 = 2·3·11 gives t = 5 for squarefree numbers with 10 prime factors;
T₂₅₄₅₄₀ = 32 395 433 070 has 10 prime factors and gives t = 7 for squarefree numbers with 254 539
prime factors.)  The least such triangular numbers are OEIS A127637 (3, 6, 66, 210, 3570, 207690,
…).  (H) follows from Dickson's prime k-tuples conjecture (take m = A·x with A a product of j − 2
odd primes and ask that x and (A·x + 1)/2 both be prime; the pair of linear forms is admissible),
but an unconditional proof needs the exact number of prime factors of m(m+1), which is a
parity-problem question.  So: unbounded under Dickson's conjecture; unconditionally open.  (The
chain is hopelessly inefficient compared with the records in the table; it is a proof strategy,
not a way to find them.)

### 3.4 Why 36: the general statement

τ_k(n) = Π C(a_i + k − 1, a_i) is the number of ordered factorisations into k factors (τ₂ = τ,
τ₃ = F).  For every prime p, τ_k(p²) = C(k+1, 2) = T_k.  Hence for primes p ≠ q

```
τ_k(p² q²) = T_k² = 1³ + 2³ + … + k³          (Nicomachus)
```

i.e. the number of (k−1)-step multichains of the 3×3 divisor grid is the sum of the first k cubes.

**Theorem 3.**  Let k ≥ 2.  T_k² is a fixed point of τ_k if and only if T_k is a product of two
distinct primes.

*Proof.*  Write T_k = Π p_i^(e_i), ω = number of primes.  Then τ_k(T_k²) = Π C(2e_i + k − 1, 2e_i),
and C(2e + k − 1, 2e) is strictly increasing in e with value T_k at e = 1.  So
τ_k(T_k²) ≥ T_k^ω, with equality iff T_k is squarefree.  For k ≥ 3 the two coprime factors of
k(k+1)/2 are both > 1, so ω ≥ 2 (for k = 2, T₂ = 3 and τ₂(9) = 3 ≠ 9).  If ω ≥ 3 then
τ_k(T_k²) ≥ T_k³ > T_k².  If ω = 2, equality τ_k(T_k²) = T_k² holds iff T_k is squarefree. ∎

So 36 = T₃² is the first member of the family 36, 100, 225, 441, 3025, 8281, 64009, … (k = 3, 4, 5,
6, 10, 13, 22, 37, …).  The index set is exactly OEIS **A164977** ("numbers m such that m(m+1)/2
is the product of two primes"; T_m is never the square of a prime, so the two primes are
distinct) and the T_k are the semiprime triangular numbers, OEIS A068443.  Whether
the family is infinite is a Sophie-Germain-type question (p and 2p±1 both prime) and is open.
Checked numerically for 2 ≤ k ≤ 3000 (`q51b_tau_k_family.log`): 94 values of k; and, evaluating
τ_k on the integer T_k² directly, for 2 ≤ k ≤ 20 000 (`verify/v3_theorem3_family.log`): 379
values, no counterexample.  For k ≤ 12 these are the only perfect squares m² with m ≤ 3000 fixed
by τ_k (apart from 1).  T_k² is the *largest* fixed point of τ_k for k = 3 and 5 but not for
k = 4 (1920) or k = 6 (19 559 232), so "36 is the largest fixed point" is a k = 3 accident, not a
feature of the family.

More generally, if B = C(a+k−1, a) is squarefree with exactly a prime factors then B^a is a fixed
point of τ_k (same computation): (k, a) = (3, 2) gives 6² = 36, (7, 4) gives 210⁴, (9, 3) gives
165³.  And if k and q = (k+1)/2 are both prime (k = 3, 5, 13, 37, 61, 73, …) then τ_k has the fixed
points k, q·k², (q·k)² and the 2-cycle {q·k, k²} — for k = 3 this is 3, 18, 36, {6, 9}.
(The fixed point k needs only k prime: τ_k(p) = k for every prime p.  Checked for all 35 such
k < 2000 in `verify/v3_theorem3_family.log`.)

### 3.5 The cousins τ_k (complete attractor lists, exact enumeration)

**Lemma 1 (pruning bound).**  For k ≥ 2 put g_k(p, a) = C(a+k−1, a)/p^a.  The ratio
g_k(p, a+1)/g_k(p, a) = (a+k)/((a+1)p) decreases in a, and for p ≥ k it is ≤ (k+1)/(2k) < 1 while
g_k(p, 1) = k/p ≤ 1.  So only primes < k can expand, each by at most M_k(p) = max_a g_k(p, a) < ∞,
and E_k = {n : τ_k(n) ≥ n} is finite; a depth-first search over primes in increasing order that
abandons a branch when (current ratio)·Π_{later p < k} M_k(p) < 1 enumerates E_k exactly. ∎

Every cycle of length ≥ 2 contains an ascent, so following the orbits of E_k finds all cycles.

| k | \|E_k\| | max E_k | fixed points | cycles of length ≥ 2 | max τ_k(n)/n |
|---|---|---|---|---|---|
| 2 | 2 | 2 | 1, 2 | — | 1 |
| 3 | 10 | 36 | 1, 3, 18, 36 | {6, 9} | 3/2 |
| 4 | 100 | 5 040 | 1, 100, 200, 224, 560, 1344, 1920 | {16, 35}, {480, 896} | 10/3 |
| 5 | 1 011 | 1 330 560 | 1, 5, 75, 225 | {15, 25} | 175/24 |
| 6 | 12 309 | 1 037 836 800 | 1, 441, 19 559 232 | one 11-cycle through 1 596 672 | 441/20 |
| 7 | 159 565 | 1.85·10¹² | 1, 7, 72 030, 133 111 440, 399 334 320, 1 944 810 000 | seven cycles (five 2-cycles, two 3-cycles) | 3773/60 |
| 8 | 2 208 054 | 3.38·10¹⁵ | 1, 11 859 210 000, 311 203 233 792 | six cycles (lengths 2, 2, 2, 5, 14, 2) | 4576/21 |

k = 3 was cross-checked by a sieve to 10⁷, k = 2, 3, 4 by direct search.  The lists for k = 4..8
were not found in OEIS (search 2026-10-06 for the k = 4, 5, 6 fixed-point lists: no result;
repeated by the skeptic for k = 4 and k = 5: no result).  The whole table was reproduced by an
independent integer-arithmetic enumeration (`verify/v2_tauk_attractors.log`: same |E_k|, same
fixed points, same cycles element by element, k = 8 in 9 s), and the part of every E_k below
3·10⁶ by brute force from the definition τ_k = 1 ∗ τ_(k−1).  No literature on iterating τ_k for
k ≥ 3 was found (iterating τ = τ₂ is classical: OEIS A036450, A036459).

### 3.6 What makes F decidable where Collatz is not

The project's "shape of the proof" audit (September 2026) uses a checklist of nine barriers
(measure, mirror 3x−1, cousin 5x+1, quotient, finite-modulus, expected-count, uniformity, Z₂,
transcendence).  F faces none of them, for these structural reasons:

* **The expansion set is finite.**  F(n) > n for six integers; Collatz multiplies by 3/2 on a set
  of density 1/2.  So n itself is a Lyapunov function for F outside a ten-element set, pointwise,
  for every n (no measure barrier, no expected-count barrier, no uniformity barrier).
* **F forgets the primes.**  F(n) depends only on the exponent multiset, and F(n) = n^(o(1)).  After
  one step the state is tiny.  The Collatz step keeps all of n and the +1 mixes the additive and
  multiplicative structure; F is purely multiplicative.
* **No conjugacy to a shift.**  The Collatz map extends to Z₂ where every parity sequence occurs,
  including the phantom orbits of −1, −5, −17; F has no such extension and no residue-class
  structure at all (quotient, finite-modulus and Z₂ barriers are vacuous).
* **No Diophantine input.**  Cycles of F are found by a finite search; Collatz cycles need lower
  bounds for |2^k − 3^s| (transcendence barrier).
* **The cousins do not disagree.**  For every τ_k the same argument gives the same conclusion
  (finitely many attractors, all orbits eventually periodic); only the list changes.  For Collatz
  the truth differs between 3x+1, 3x−1 and 5x+1, so a proof must use something that tells them
  apart.  Here nothing needs to be told apart.

"F multiplies by 3/2, exactly the Collatz step in v = n+1": F(n) = 3n/2 holds for n ∈ {2, 4, 6, 12}
and for no other n (2 → 3, 4 → 6 → 9, 12 → 18 are steps (a, b) → (a−1, b+1) of the exponent
grid, as v → 3v/2 is).  Four coincidences of small triangular numbers; **numerology**.

F is a pleasant, completely solvable "baby" system, but calling it a baby *Collatz* would
oversell it: it shares none of the features that make Collatz hard.

---

## 4. Q5.3 — Liouville on Collatz cells (null)

**Identity.**  On the divisor grid of 2^k·3^s, τ(2^i·3^j) = (i+1)(j+1), so Liouville reads

```
Σ_{i≤k, j≤s} ((i+1)(j+1))³  =  (T_(k+1)·T_(s+1))²
```

which is the product of two Nicomachus identities (the weight is a product of a function of i and
a function of j, and "Σx³ = (Σx)²" is closed under such products).  At k = s = 2 both sides are 36².

**Search.**  A multiset X of positive integers is CS if Σx³ = (Σx)² (Mason 2001; Barbeau–Seraj
2013).  Tested, with exact integers (`q53_liouville_cells.log`):

| family | multisets |
|---|---|
| all monotone paths C(i+j, i) on rectangles [0..k]×[0..s], k ≤ s ≤ 40 | 861 |
| Pascal rows n ≤ 300 (Franel numbers vs 4ⁿ); Pascal triangles n ≤ 80 | 382 |
| admissible-prefix triangle A(e, s): rows s ≤ 220; columns (first m cells); antidiagonals (words of length j ≤ 200); cumulative regions; divisor rectangles of 2^j·3^s | 9 035 |
| windows [a..b] of A100982, b ≤ 220 | 24 310 |
| windows of S(j) = #surviving words of length j (OEIS A076227), j ≤ 200 | 20 301 |
| **total** | **54 889** |

Hits: 182, every one of them the literal multiset {1, …, m} (m = 1 in 116 cases).  The only
family with m > 4 is the column "exactly one even step": A(1, s) = s − 1 for s ≥ 2, because the single
0 can follow any of the ones number 2..s; its initial segments are {1, …, m}.  (The others: the
sequences A100982 and A076227 happen to contain the runs 1, 2, 3 and 1, 2, 3, 4.)
**Non-trivial hits: 0.**

Skeptic re-run with independent code and a wider range (`verify/v5_controls.log`): all windows of
A100982 up to s = 420 and of A076227 up to j = 400, all rows and antidiagonals of the admissible
triangle in that range, and all windows of the partial sums and of the first differences of
A100982 (s < 200) — 209 434 multisets, 21 hits, every one a literal {1, …, m} with m ≤ 4.

*Why the null is structural.*  Liouville's identity is multiplicativity: the weight of the cell
(i, j) factors as w(i)·w(j).  Path counts do not factor, and the dropping constraint (stay on one
side of a line of irrational slope) couples the two coordinates as tightly as possible.

*Role of 36.*  None.  A100982(2..4) = 1, 2, 3 has cube sum 36 only because the sequence starts
1, 1, 2, 3.

*Q5.3-d: intervals versus maximal chains.*  T_(k+1)·T_(s+1) = C(k+s, k)² ("number of intervals =
square of the number of maximal chains" on the (k+1)×(s+1) grid) holds, for k ≤ s, only at
(0,0) and (2,2).  Proof: k = 0 gives T_(s+1) = 1, s = 0.  k = 1 gives 3(s+2) = 2(s+1), impossible.
k = 2: C(s+2, 2) = T_(s+1), so the equation is T₃·T_(s+1) = T_(s+1)², i.e. T_(s+1) = 6, s = 2.
k ≥ 3: C(k+s, k) ≥ C(s+3, 3) and T_(k+1)T_(s+1) ≤ T_(s+1)², while
C(s+3, 3)² = ((s+3)/3)²·T_(s+1)² ≥ 4·T_(s+1)². ∎  (Search k ≤ 2, s < 1500 and 3 ≤ k ≤ s < 40 in
`verify/v5_controls.log`, k ≤ s < 400 in `q53_liouville_cells.log`.)  So 36 = T₃·T₃ = C(4,2)² is a
true and provable small-number fact whose only mechanism is "a grid with three rows has a
triangular number of maximal chains".  It says nothing about dropping words: as far as the
question goes it is numerology.

*Mirror test.*  Not applicable (null).

---

## 5. Q5.4 — rational-slope ballot numbers along the convergents of log₂3

log₂3 = [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, …], convergents 1/1, 2/1, 3/2, 8/5, 19/12, 65/41, 84/53,
485/306, 1054/665, …  Orders of the one-sided best approximations (strict records of the
fractional part {s·log₂3}):

```
lower  L₃ : 1, 2, 7, 12, 53, 359, 665, …            (1/1, 3/2, 11/7, 19/12, 84/53, 569/359, …)
upper  U₃ : 1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971, …   (2/1, 5/3, 8/5, 27/17, 46/29, 65/41, …)
```

### 5.1 Prior art (read this first)

* **Mike Winkler, "Admissible qx+1 Sequences, Semiconvergents, and Rational Catalan Numbers",
  arXiv:2609.22303 (14 Sep 2026).**  Proves, for every odd q ≥ 3, with m = ⌊s·log₂q⌋:
  (1/s)·C(m−1, s−1) ≤ a_q(s) ≤ (1/s)·C(m, s−1) (cycle lemma); equality in the lower / upper bound
  exactly at the strict record minima / maxima of {s·log₂q}, i.e. at the denominators of the
  convergents and semiconvergents (Hančl–Turek 2019); at those orders the words are rational Dyck
  paths and a_q(s) = C(m, s)/m or C(m+1, s)/(m+1); a rigidity statement (Prop. 9): for real slopes
  α < β, c_s(α) = c_s(β) iff ⌊iα⌋ = ⌊iβ⌋ for i < s; growth constant 2.8395…  The OEIS entry
  A100982 carries the bounds and the equality criterion in a comment dated 15 Sep 2026 (read
  directly from oeis.org on 2026-10-06).  The same entry links R. H. G. van Tol's picture of the
  sequence as lattice walks under y = x·(log₂3 − 1), and a comment by Ph. Cochin (21 Sep 2026)
  identifies the words with Terras's "terminal words".
* **"A100982 is the limit of rational Catalan / Bizley numbers along the convergents of log₂3" is
  known** in exactly this form.  (The sandwich was also re-derived in this session; that has no
  priority value.)  The paper also already contains one "window" phenomenon explicitly: for
  q = 7 it explains why A174796 agrees with A006013 through order 6 and then breaks (its §5), the
  exact analogue of Q5.4-d below.
* Bizley 1954 (lattice paths under a rational line, non-coprime endpoints; cited by Winkler for
  the coprime case); Gorsky–Mazin–Vazirani, arXiv:1703.02668, and Birmajer–Gil–Weiner,
  arXiv:1606.02183 (rational Dyck paths in the non-coprime case); Dvoretzky–Motzkin 1947
  and Raney 1960 (cycle lemma); Duchon 2000 (slope 2/3, OEIS A060941); Banderier–Wallner,
  arXiv:1606.08412 (kernel method for any rational slope, algebraic generating functions; they
  announce a companion paper on irrational slopes); Zarubin's recursion and Roosendaal's table in
  OEIS A100982; Terras 1976, Wagon 1985 for the Collatz side.
* Earlier repo note "no ballot formula because the reflection principle breaks": still true for a
  general order s, but there *is* a ballot formula at every order listed in §5.3.

Independent re-verification (`q54_rational_ballot.log`, s ≤ 1000): no violation of the sandwich;
lower equality at s = 1, 2, 7, 12, 53, 359, 665 and upper equality at s = 1, 3, 5, 17, 29, 41, 94,
147, 200, 253, 306, 971 — exactly L₃ and U₃.  Same check for q = 5 and q = 7 (s ≤ 400).
Skeptic pass (`verify/v4_paths_independent.log`): the same for s ≤ 2218 (one more upper equality
order, 1636 = 971 + 665), the rational Catalan values of Theorem 8 at every equality order, and
q = 5, 7 for s ≤ 600.

### 5.2 Window theorem (a corollary of Winkler's Proposition 9)

**What this section is.**  Winkler's Prop. 9 says: for real 1 < α < β, c_s(α) = c_s(β) ⇔
⌊iα⌋ = ⌊iβ⌋ for 1 ≤ i < s, so α ↦ c_s(α) is a step function whose constant cells are the cells
of the Beatty prefix.  Spelled out for α = log₂3 this reads (**cell form**):

> for every s ≥ 2 and every real β ≥ 1 (β = 1 by Lemma 2 below), with ℓ_s = max_{i<s} ⌊iα⌋/i and u_s = min_{i<s} (⌊iα⌋+1)/i:
> the weak count c_s(β) (boundary ⌊iβ⌋) equals N(s) ⇔ ℓ_s ≤ β < u_s, and for rational β the
> strict count (boundary ⌈iβ⌉ − 1) equals N(s) ⇔ ℓ_s < β ≤ u_s.

ℓ_s and u_s are the best lower and upper approximations to log₂3 with denominator < s, i.e. the
fractions ⌊bα⌋/b and ⌈bα⌉/b at the largest lower / upper record order b < s (classical:
Hančl–Turek 2019, Thm 4.5; checked for s < 400 in `verify/v4_paths_independent.log`).  That is
the whole content of Theorem 4 below, and it covers every rational slope at once, best
approximation or not: e.g. 7/4 and 13/8 lie in [ℓ_s, u_s) exactly for s ≤ 3 and s ≤ 5, and
30/19, 49/31 for s ≤ 12, as computed.  Lemma 2 and Theorem 4 are kept because they give a
self-contained elementary proof, not because they are new.

Let α > 1 be irrational, δ_i = {iα}, N(s) = c_s(⌊iα⌋).

**Lemma 2 (rigidity; Winkler's Prop. 9 for arbitrary boundaries).**  Let m ≤ m′ be integer
sequences with m_i ≥ i − 1, m′_i ≥ i and m′_(i+1) − m′_i ≥ 1.  Then c_s(m) ≤ c_s(m′), with
equality iff m_i = m′_i for all 1 ≤ i < s.

*Proof.*  Inclusion is clear.  If m_j < m′_j with j < s, the sequence t_i = i (i < j),
t_j = m_j + 1, t_i = m_j + 1 + (i − j) (i > j) is increasing (m_j + 1 > j − 1), obeys m′
(i ≤ m′_i; m_j + 1 ≤ m′_j; then the increments of m′) and violates m at j. ∎

All boundaries used here satisfy the hypotheses: ⌊iα⌋ and ⌊i·a/b⌋ are ≥ i with increments ≥ 1
when α, a/b ≥ 1; ⌈i·a/b⌉ − 1 is ≥ i when a/b > 1 and equals i − 1 for a/b = 1.

**Theorem 4 (window).**  (a) Let a/b < α with a = ⌊bα⌋ and δ_b < δ_j for 1 ≤ j < b, and let
b⁺ = min{i > b : δ_i < δ_b}.  Then ⌊i·a/b⌋ = ⌊iα⌋ for 1 ≤ i < b⁺ and ⌊b⁺·a/b⌋ < ⌊b⁺α⌋.  Hence the
weak count satisfies c_s(a/b) = N(s) ⇔ s ≤ b⁺, and c_s(a/b) < N(s) for all s > b⁺.
(b) Symmetrically, let a/b > α with a = ⌈bα⌉ and δ_b > δ_j for j < b, b⁺ the next strict record
maximum.  Then ⌈i·a/b⌉ − 1 = ⌊iα⌋ for 1 ≤ i < b⁺ and not for i = b⁺; the strict count satisfies
c_s(a/b) = N(s) ⇔ s ≤ b⁺, and c_s(a/b) > N(s) for s > b⁺.
(c) In the other convention (lower a/b with the strict boundary, upper a/b with the weak one) the
boundaries first differ at i = b, so the counts agree ⇔ s ≤ b.

*Proof of (a).*  Since a/b < α, ⌊i·a/b⌋ ≤ ⌊iα⌋, and the inequality is strict exactly for i in
D = {i : there is an integer c with a/b < c/i < α}.  Note iα − i·a/b = (i/b)·δ_b.
(1) No i ≤ b lies in D: such a c would give δ_i ≤ iα − c < (i/b)δ_b ≤ δ_b, contradicting the record
property (i < b) or absurd (i = b).
(2) Let i₀ = min D with c = ⌊i₀α⌋, and put i′ = i₀ − b ≥ 1, c′ = c − a.  From cb > a·i₀ we get
c′/i′ > a/b.  By minimality i′ ∉ D, so c′/i′ > α, i.e. c − a > (i₀ − b)α, i.e. δ_(i₀) < δ_b.
Hence i₀ ≥ b⁺.
(3) b⁺ ∈ D: δ_(b⁺) < δ_b < (b⁺/b)·δ_b gives ⌊b⁺α⌋ > b⁺·a/b.
So min D = b⁺, and Lemma 2 (the boundaries are comparable, and differ first at index b⁺) gives
the statement about counts.  (b) is the mirror image with ε_i = 1 − δ_i; (c) is immediate because
⌈i·a/b⌉ − 1 and ⌊i·a/b⌋ differ exactly when b | i. ∎

For a principal convergent P_n/Q_n the next same-side order is Q_n + Q_(n+1).  So the task's
guess "agreement until the first lattice point between the two lines, governed by the next
convergent" needs one correction: the separating lattice point is the next **same-side
semiconvergent** (the mediant with the next convergent), not the next convergent itself, which
lies on the other side of the line.

Computed windows (all confirmed; "natural" = weak for lower, strict for upper):

| slope a/b | side | kind | agrees with A100982 for s ≤ (natural) | (other convention) |
|---|---|---|---|---|
| 1/1 | lower | convergent | 2 | 1 |
| 2/1 | upper | convergent | 3 | 1 |
| 3/2 | lower | convergent | 7 | 2 |
| 5/3 | upper | semiconvergent | 5 | 3 |
| 8/5 | upper | convergent | 17 | 5 |
| 11/7 | lower | semiconvergent | 12 | 7 |
| 19/12 | lower | convergent | 53 | 12 |
| 27/17 | upper | semiconvergent | 29 | 17 |
| 46/29 | upper | semiconvergent | 41 | 29 |
| 65/41 | upper | convergent | 94 | 41 |
| 84/53 | lower | convergent | 359 | 53 |
| 485/306 | upper | convergent | 971 | 306 |
| 1054/665 | lower | convergent | 16 266 (by Theorem 4, = 665 + 15 601; beyond the computed range) | 665 (by Theorem 4c; not computed) |

The theorem was checked for every one-sided best approximation with denominator ≤ 400 (17 slopes,
s ≤ 1000), and for q = 5, 7.  Rational slopes that are not best approximations (7/4, 13/8, 30/19,
49/31) part from A100982 earlier, as they must.  Skeptic pass: all 19 best approximations with
denominator ≤ 1000 for s ≤ 2218, both conventions, including the floor statement itself (first i
with boundary ≠ ⌊iα⌋ equals b⁺), the new case 1539/971 (window 1636), strict one-sidedness beyond
each window, agreement of 1054/665 up to s = 2218, non-reduced slopes (6/4 behaves as 3/2, 16/10 as
8/5), and q = 5, 7 for s ≤ 600.  All confirmed.

*Status.*  Proved, and the proof above was read line by line (Lemma 2: the witness sequence is
increasing because m_j ≥ j − 1; Theorem 4: steps (1)–(3) are correct; a one-sided best
approximation is automatically in lowest terms).  It is a corollary of prior art: Winkler's
Prop. 9 is the rigidity, his Lemma 4 the agreement for i < b, and the continuation up to b⁺ is
the classical agreement of Sturmian and Christoffel prefixes (Berstel–Séébold in Lothaire 2002).
Only the explicit window b⁺ is not written in arXiv:2609.22303.  Not a new theorem.

### 5.3 Bizley closed forms at multiples of convergent denominators

Bizley (1954): for coprime m, n let F_j = C(j(m+n), jm) / (j(m+n)).  The number φ_k of lattice
paths (0,0) → (km, kn) that never rise above the line joining the endpoints, and the number ψ_k of
those touching it only at the two ends, satisfy

```
Σ φ_k t^k = exp(Σ_j F_j t^j),        Σ ψ_k t^k = 1 − exp(−Σ_j F_j t^j).
```

**Corollary 5.**  Let P/Q ≠ 1/1 be a convergent of log₂3, Q′ the next convergent denominator, and
1 ≤ k ≤ 1 + ⌊Q′/Q⌋.  Then N(kQ) = φ_k(P−Q, Q) if P/Q < log₂3 and N(kQ) = ψ_k(P−Q, Q) if
P/Q > log₂3.

*Proof.*  kQ ≤ Q + Q′ = b⁺, so by Theorem 4 N(kQ) is the rational count.  Put t_(kQ) = kP and
y_i = t_i − t_(i−1) − 1 ≥ 0; then Σy_i = k(P−Q), and the conditions t_i ≤ iP/Q (lower, weak) resp.
t_i < iP/Q (upper, strict) for i < kQ say that the path E N^(y₁) E N^(y₂) … from (0,0) to
(kQ, k(P−Q)) stays weakly below the diagonal resp. meets it only at its ends. ∎

k = 1 is Winkler's rational Catalan value.  For k ≥ 2 the order kQ is not an equality order, the
value lies strictly inside his sandwich, and the endpoint (kQ, k(P−Q)) is not coprime, so his
Theorem 8 does not apply.  With F_j = C(8j, 3j)/(8j) (convergent 8/5) and F_j = C(19j, 7j)/(19j)
(convergent 19/12):

```
N(10) = F₂ − F₁²/2          = 1001/2 − 49/2                 = 476
N(15) = F₃ − F₁F₂ + F₁³/6   = 163438/3 − 7007/2 + 343/6     = 51033
N(24) = F₂ + F₁²/2          = 257 978 502                   (F₁ = 2652)
N(36) = F₃ + F₁F₂ + F₁³/6   = 38 088 111 350 198
N(48) = F₄ + F₁F₃ + F₂²/2 + F₁²F₂/2 + F₁⁴/24 = 6 687 324 379 116 300 569
```

Verified against the exact count for every admissible (P/Q, k) with kQ ≤ 1000: 3/2 (k ≤ 3),
8/5 (k ≤ 3), 19/12 (k ≤ 4), 65/41 (k ≤ 2), 84/53 (k ≤ 6), 485/306 (k ≤ 3); and the first k
outside each window fails, as predicted (e.g. φ₄(1,2) = 55 ≠ 85 = N(8)).  The implementation of
φ, ψ was checked against brute-force path enumeration.

Skeptic pass (`verify/v4_paths_independent.log`): for every (P/Q, k) with kQ ≤ 2218 the number of
lattice paths (0,0) → (kQ, k(P−Q)) that never rise above the diagonal (lower convergents) or meet
it only at the ends (upper convergents) was counted directly by a 2-D DP and compared with N(kQ)
and with Bizley's formula written as a sum over the partitions of k.  All in-window cases agree
(adding 1054/665 with k = 2, 3, i.e. s = 1330, 1995), and the first k outside each window fails
(2/1 k = 4, 3/2 k = 4, 8/5 k = 4, 19/12 k = 5, 65/41 k = 3, 84/53 k = 7, 485/306 k = 4).

Only principal convergents give k ≥ 2: for an intermediate fraction with denominator
b = Q_(n−1) + j·Q_n (j ≥ 1) the window ends at b⁺ = b + Q_n < 2b.

Orders s ≤ 1000 with a closed form:

```
Winkler (rational Catalan):  1, 2, 3, 5, 7, 12, 17, 29, 41, 53, 94, 147, 200, 253, 306, 359, 665, 971
added by Corollary 5:        4, 6, 10, 15, 24, 36, 48, 82, 106, 159, 212, 265, 318, 612, 918
added by Q5.4-d (below):     nothing further (s ≤ 7 is covered by the two lines above)
first orders with none:      8, 9, 11, 13, 14, 16   (N = 85, 173, 961, 8045, 17637, 108950)
```

*Status.*  Proved (given Bizley's theorem and §5.2); verified.  It is Bizley's 1954 formula
applied inside the window — every ingredient is prior art (Bizley for non-coprime endpoints; see
also Gorsky–Mazin–Vazirani and Birmajer–Gil–Weiner).  The specific values N(k·Qₙ) are not in
arXiv:2609.22303, which treats coprime endpoints only, and an OEIS search for the consecutive
terms 476, 51033, 257978502, 38088111350198 returns nothing (2026-10-06).  Winkler cites two ResearchGate preprints of his own ("Coefficient
First-Passage Words…", "Marked Rotations and Factorization Heights for Dual Beatty Passage
Counts") that could not be read (HTTP 403 again in the skeptic pass); the second title suggests
non-coprime cases may be covered there.  **Novelty unknown; do not claim it.**

*Role of 36.*  36 is in the list because 36 = 3·12, 12 is the denominator of 19/12 and the next
partial quotient is 3.  That is a fact about 12 (the Pythagorean-comma convergent 3¹² ≈ 2¹⁹), not
about 2²·3².  24 and 48 are there for the same reason.

### 5.4 The first window, and OEIS identifications

**Q5.4-d.**  For slope 3/2 the excess slope is 1/2 = 1/(integer), so the classical ballot theorem
with integer slope 2 applies to *every* endpoint: with h = ⌊s/2⌋,

```
c_s(3/2, weak) = (s − 2h + 1)/(s + h + 1) · C(s + h + 1, h) = A047749(s)
               = C(3m, m)/(2m+1) for s = 2m,   C(3m+1, m+1)/(2m+1) for s = 2m+1.
```

(Verified for s ≤ 400; by the skeptic for s ≤ 1000 and against the OEIS b-file of A047749.)  By
the window theorem N(s) equals this for s ≤ 7 and not for s = 8 (55 ≠ 85); in fact
N(s) = A047749(s) holds for s = 1..7 and for no other s < 300.  So the first seven terms
1, 1, 2, 3, 7, 12, 30 of A100982 are terms 1..7 of A047749 (offset 0: 1, 1, 1, 2, 3, 7, 12, 30,
55, …), for a reason.  How much of this is new: at s = 1, 2, 3, 5, 7 the value is Winkler's
rational Catalan number (his Theorem 8); only s = 4 and s = 6 are added, and those are
φ₂(1,2) = 3 and φ₃(1,2) = 12 of Corollary 5.  Winkler's paper notes the analogous coincidence for
q = 7 (A174796 = A006013 through order 6).  The A047749 entry does not mention A100982 or the
3x+1 problem (read 2026-10-06).  No later convergent has excess slope 1/integer (3/5, 7/12,
24/41, …), so the integer-slope ballot theorem is not available in later windows; I know of no
closed form valid for every s there, but that is an absence of a formula, not a proof that none
exists (the generating functions are algebraic, see lead 2 in §8).

| slope, convention | c_s, s = 1, 2, … | OEIS | agrees with A100982 for |
|---|---|---|---|
| 1/1 weak | 1, 1, 1, 1, … | A000012 | s ≤ 2 |
| 2/1 strict | 1, 1, 2, 5, 14, 42, … | Catalan A000108(s−1) | s ≤ 3 |
| 2/1 weak | 1, 2, 5, 14, 42, … | A000108(s); equals A174795 (5x+1) for s ≤ 4 | s ≤ 1 |
| 3/2 weak | 1, 1, 2, 3, 7, 12, 30, 55, 143, 273, 728, … | A047749(s) | s ≤ 7 |
| 3/2 strict | 1, 1, 1, 2, 3, 7, 12, 30, 55, … | A047749(s−1) | s ≤ 2 |
| 5/3 strict | 1, 1, 2, 3, 7, 19, 37, 99, 293, 624, 1768, 5452, … | not found; the terms s = 3k are A293946 | s ≤ 5 |
| 5/3 weak | 1, 1, 2, 5, 9, 23, 66, 136, 377, 1144, 2504, 7229, … | not found; the terms s = 3k are Duchon's numbers A060941 | s ≤ 3 |
| 8/5 strict | A100982(1..17), then 975990, 2212925, 6561583, … | not found | s ≤ 17 |
| 11/7 weak | A100982(1..12), then 5393, 14985, 45729, … | not found | s ≤ 12 |
| 19/12 weak | A100982(1..53), … | (a search returns A100982 itself) | s ≤ 53 |

"Not found" = no result on oeis.org for the listed term strings on 2026-10-06.  The task's
"Duchon slope-3/2 numbers A060941" belong to the fake slope 5/3 (rectangle 2×3), an upper
semiconvergent; the OEIS cross-references from A100982 to A060941 and A293946 are explained by
this, and the only order at which they share a value with A100982 is s = 3 (value 2).

### 5.5 Gersonides' unit cells

|2^P − 3^Q| = 1 exactly for the convergents 1/1, 2/1, 3/2 (pairs (2,3), (3,4), (8,9)); from 8/5 on
the differences are 13, −7153, …  By Theorem 4 the three "unit" slopes reproduce A100982 for
s ≤ 2, 3, 7, and the lattice points that separate them from the true line are the next same-side
semiconvergents 3/2, 5/3, 11/7.  So: the unit cells are the first three convergents and their
windows are the three shortest; nothing else distinguishes them in the path counts.  The pair
(8, 9) is the cell (3, 2), not (2, 2).

### 5.6 Mirror test for all of §5

* **3x−1.**  T₋(n) = −T₊(−n), so the parity word of n under 3x−1 is that of −n under 3x+1.  The
  dropping classes of 3x−1 are the negatives of those of 3x+1 mod 2^L, the counts are the same
  N(s), and every statement in §5 holds verbatim.  Checked on actual 3x−1 orbits for s ≤ 8
  (`q5x_verify_classes_and_mirrors.log`).  **Sign-blind.**
* **5x+1, 7x+1.**  The counts are A174795, A174796 — different sequences with the same theory
  (log₂5 = [2; 3, 9, 2, …], log₂7 = [2; 1, 4, 5, …]); sandwich, equality sets and windows verified
  for s ≤ 400.  **Distinguishes the multiplier, not the sign.**
* Consequence: §5 describes the coefficient (2-adic, density) structure of dropping classes.  It
  cannot separate 3x+1 from 3x−1 and therefore cannot bear on the conjecture.

---

## 6. Q5.5 — lattice points instead of paths (null)

`q55_lattice_points.log`.  π₃(x) = #{2^a·3^b ≤ x}; π₃(2^K) = Σ_{b ≥ 0, 3^b ≤ 2^K} (K + 1 − ⌈b·log₂3⌉)
(a Beatty sum; OEIS A022331; checked K < 400).  For slope 1 in place of log₂3 the sum would be
T_(K+1), so π₃ is "a triangular number with irrational slope" — but that is all.

* π₃(36) = 14; Ramanujan's ln(2x)·ln(3x)/(2·ln2·ln3) gives 13.1 at x = 36.
* Among π₃(2^K), π₃(3^S), G(S) = #{(j, s) : 1 ≤ s ≤ S, 2^j < 3^s} and the number of admissible
  cells with s ≤ S, triangular and square values occur about as often as chance predicts
  (3–6 hits in 200 terms against 3–7 expected).
* The value 36 occurs once: G(6) = 2+4+5+7+8+10 = 36 (the six shortest dropping-word lengths).  No
  mechanism.  **Numerology.**  Control: the four sequences above take 10 of the 21 values in
  25..45 (26, 27, 28, 32, 34, 36, 37, 38, 41, 45; `verify/v5_controls.log`), so one of them
  hitting 36 is roughly a coin flip.
* The only exact T₈ statement is the trivial one: #{(a, b) : a + b ≤ 7} = T₈ = 36.

*Role of 36.*  None.  *Mirror test.*  Not applicable (sign-blind lattice counts).

---

## 7. What was tried and failed

* Hoped Liouville's cube identity would survive on path counts in some weighted form: clean null
  (§4), with a structural reason.
* Hoped "A100982 = limit of Bizley numbers along the convergents" would be new.  It is Winkler's
  theorem of September 2026.  What remains is the explicit window (a corollary of his Prop. 9) and
  the non-coprime Bizley values (Bizley 1954 applied inside the window), neither checked against
  his unpublished preprints.
* Looked for a closed form valid for *every* s inside the 8/5 and 19/12 windows: none found.  The
  generating function of c_s(a/b) is algebraic (kernel method), but I did not derive it.
* Tried to prove that the transient length of F is unbounded: reduces to always finding a preimage
  inside the multiplicative semigroup generated by the triangular numbers; not settled
  unconditionally (it follows from Dickson's conjecture, §3.3).
* Looked for T₈ = 36 in 3-smooth lattice-point counts: chance level only.
* Tried to connect the F-picture and the path picture through the shared lattice: they live on
  the same grid but have nothing to do with each other.  F is governed by the bounded region
  T_(a+1)·T_(b+1) ≥ 2^a·3^b around the origin; dropping words by the unbounded line 2^j = 3^s.
  The working hypothesis "each fact about 36 is a fact about the point (2,2)" is confirmed for
  Nicomachus/Liouville in this precise sense: τ_k(p²q²) = T_k² for every pair of primes, so the
  signature (2,2) carries the cube identity, and 36 is a fixed point because in addition
  T₃ = 2·3.  The point (2,2) has no special position relative to the Collatz line: every word
  with s ≥ 2 passes through it, but every word also passes through (1,1), and (2,2) is forced
  only because 3 < 4 (for 5x+1 and 7x+1 the only forced cell is (1,1)).

## 8. Open questions / leads

1. Obtain Winkler's ResearchGate preprints and check whether Corollary 5 (Bizley values at k·Qₙ)
   and the window b⁺ are there.  If not, they are a two-line comment for OEIS A100982.
2. Kernel-method generating function for c_s(8/5) and c_s(19/12) (Banderier–Wallner): an explicit
   algebraic equation would give N(s) for all s ≤ 17 resp. s ≤ 53.
3. Is the transient length of F unbounded unconditionally (it is under Dickson's conjecture,
   §3.3)?  What is the least n with t = 13 (it is at most about 10⁷¹ and above 10⁴⁰)?  Do the
   basins of 18, 36, {6,9} have limiting densities?
4. The τ_k attractor lists: is the longest cycle unbounded in k (lengths 2, 2, 2, 11, 3, 14 for
   k = 3..8)?  Is the family of Theorem 3 infinite?
5. Nothing in this thread is a step towards the conjecture, and none of the leads is either.

## 9. Files

All scripts are single-process, exact arithmetic, and write a `.log` and `.json` next to
themselves.  Run with `C:/repos/collatz/.venv/Scripts/python.exe -X utf8 <script>`.

| file | what | time |
|---|---|---|
| `q51_q52_tau3_dynamics.py` | E_k, fixed points and cycles of τ_k (k = 2..8); sieve of F to 10⁷; basins; transients; least n per transient below 10⁴⁰ | 5.5 min (5 of them k = 8) |
| `q51b_tau_k_family.py` | Theorem 3 for k ≤ 3000; the B^a family; the (k, q) family | 1 s |
| `q53_liouville_cells.py` | Liouville on the grid; CS search over 54 889 multisets | 3 s |
| `q54_rational_ballot.py` | N(s) to s = 1000 vs OEIS b-file; sandwich; windows; Bizley; OEIS sequences; q = 5, 7 (run with `-I`, it reads `oeis_data/`) | 5 s |
| `q55_lattice_points.py` | Beatty sums, chance-level test | < 1 s |
| `q5x_verify_classes_and_mirrors.py` | N(s) vs `collatz.dropping.dropping_time`; gateway cell; 3x−1; 5x+1 | 1 s |
| `oeis_data/` | b-files of A100982, A174795, A174796, A047749 downloaded from oeis.org on 2026-10-06 (data only) | — |
| `verify/v1_tau3_by_definition.py` | skeptic: F from the definition (two additive divisor sieves) to 10⁷; E₃, attractors, basins, transients, preimages of 36 | 45 s |
| `verify/v2_tauk_attractors.py` | skeptic: independent enumeration of E_k and all cycles of τ_k, k = 2..8; brute force to 3·10⁶ | 1 min |
| `verify/v3_theorem3_family.py` | skeptic: Theorem 3 for k ≤ 20 000 (τ_k evaluated on T_k² itself), A164977, edge cases, the two satellite families | 1 min |
| `verify/v4_paths_independent.py` | skeptic: N(s) three ways to s = 2218; sandwich; windows and floor statement; Bizley by direct path counting; slope 3/2; 5x+1, 7x+1; residue classes of 3x+1, 3x−1, 5x+1; forced cells (run with `-I`) | 35 s |
| `verify/v5_controls.py` | skeptic: transient records below 10⁴⁰; fixed points of any τ_k below 300; Q5.3-d proof check and wider cube search; Q5.5 control; conditional unboundedness | 45 s |

## 10. References

* M. Winkler, Admissible qx+1 sequences, semiconvergents, and rational Catalan numbers, arXiv:2609.22303 (2026).
* M. T. L. Bizley, J. Inst. Actuaries 80 (1954) 55–62.
* A. Dvoretzky, Th. Motzkin, Duke Math. J. 14 (1947) 305–313; N. Dershowitz, S. Zaks, Europ. J. Combin. 11 (1990) 35–40.
* P. Duchon, On the enumeration and generation of generalized Dyck words, Discrete Math. 225 (2000) 121–135.
* C. Banderier, M. Wallner, The kernel method for lattice paths below a line of rational slope, arXiv:1606.08412.
* J. Hančl, O. Turek, One-sided Diophantine approximations, J. Phys. A 52 (2019) 045205.
* J. Berstel, P. Séébold, Sturmian words, in Lothaire, Algebraic Combinatorics on Words (2002).
* R. Terras, Acta Arith. 30 (1976) 241–252; S. Wagon, Math. Intelligencer 7 (1985) 72–76.
* J. Mason, Generalising "sums of cubes equal to squares of sums", Math. Gazette 85 (2001); E. Barbeau, S. Seraj, Sum of cubes is square of sum, arXiv:1306.5257.
* J.-M. De Koninck, Ces nombres qui nous fascinent, Ellipses 2008 (entry 36); J.-M. De Koninck, A. Mercier, 1001 problèmes en théorie classique des nombres, Ellipses 2004 (both cited in OEIS A097989).
* E. Gorsky, M. Mazin, M. Vazirani, Rational Dyck paths in the non relatively prime case, arXiv:1703.02668; D. Birmajer, J. B. Gil, M. D. Weiner, On rational Dyck paths and the enumeration of factor-free Dyck words, arXiv:1606.02183.
* C. Kimberling, Best lower and upper approximates to irrational numbers, Elem. Math. 52 (1997) 122–126.
* L. E. Dickson, A new extension of Dirichlet's theorem on prime numbers, Messenger of Math. 33 (1904) 155–161 (the conjecture used conditionally in §3.3).
* OEIS: A007425, A097988, A097989, A068443, A164977, A127637, A036450, A036459 (τ side); A100982, A174795, A174796, A020914, A122437, A076227, A206788, A047749, A006013, A060941, A293946, A000108, A022331 (path side).

---

## 11. Skeptic pass (2026-10-06)

A second agent re-derived or re-computed every claim with its own code (`verify/`, logs next to
the scripts) and read every proof.  **No claim was refuted.**  What changed:

*Status downgrades and re-framings.*

* Q5.4-b (window theorem): relabelled as a corollary of prior art.  It is Winkler's
  Proposition 9 specialised to α = log₂3 plus the classical description of one-sided best
  approximations; the cell form in §5.2 states it for every real slope at once.  The bottom line
  no longer calls it an addition of this thread.
* Q5.4-d: for s = 1, 2, 3, 5, 7 the identity N(s) = A047749(s) is Winkler's Theorem 8; only
  s = 4, 6 are extra and they are Corollary 5.  The sentence "no later window has a one-line
  formula" was an unproved opinion and now says so.
* Q5.3-d: upgraded from "computed for k ≤ s < 400, no mechanism" to "proved for all k ≤ s", with
  the (trivial) mechanism; it stays numerology as far as Collatz is concerned.
* Q5.x: the role of 36 is now "none beyond naming": the cell (1,1) is forced as well, and (2,2)
  is forced only because 3 < 4 (not for 5x+1 or 7x+1).
* Q5.1-a and Q5.3-a are listed as prior art first, proof second.
* The remark that the sandwich was derived before the paper was found is reduced to one neutral
  clause; it cannot be checked and carries no weight.

*Prior art added.*  De Koninck (entry 36) and De Koninck–Mercier for the fixed points of τ₃
(via OEIS A097989, read directly); OEIS A164977 as the exact index set of Theorem 3; OEIS A127637;
Gorsky–Mazin–Vazirani and Birmajer–Gil–Weiner for non-coprime rational Dyck paths; Winkler's own
q = 7 window remark.  arXiv:2609.22303 was downloaded and read in full (14 pages): the README's
description of Theorems 6–8, Lemma 4, Proposition 9 and the growth constant is accurate, and the
OEIS comment of 15 Sep 2026 exists as described.

*Independent confirmations (all agree with the researcher's numbers).*

* F from the definition to 10⁷: E₃, the six periodic points, basin sizes at 10¹..10⁷, the
  transient distribution (mean 3.134462), 879 preimages of 36 (875 of type p²q², 4 of type p⁷),
  basin(3) = primes.
* τ_k, k = 2..8: |E_k| = 2, 10, 100, 1011, 12309, 159565, 2208054; identical fixed points and
  cycles; brute force to 3·10⁶ for every k.
* Theorem 3 for k ≤ 20 000; transient records below 10⁴⁰ (5 754 126 signatures, same thirteen
  records).
* The four files in `oeis_data/` are byte-identical to fresh downloads from oeis.org.
* N(s) three independent ways; b-file agreement to s = 2218; sandwich and equality sets to 2218;
  windows for all 19 best approximations with denominator ≤ 1000; Bizley values by direct path
  counting to s = 2218; residue classes for s ≤ 11.

*Mirror and cousin tests re-run.*  3x−1: the classes are the negatives of the 3x+1 classes for
s ≤ 10 (actual 3x−1 orbits of two large representatives per class), so every path statement is
sign-blind.  5x+1, 7x+1: different counts (A174795, A174796), same theory (sandwich, equality
sets, windows verified to s = 600).  Nothing on the path side distinguishes 3x+1 from 3x−1;
nothing on the τ side is a Collatz statement at all.

*Numerology controls run.*  Fixed points of any τ_k below 300 (§2); "T_k² is the largest fixed
point" fails for k = 4, 6 (§3.4); values near 36 in the lattice-point sequences (§6); forced
cells for q = 3, 5, 7 (results table, Q5.x).

*New in this pass.*  The cell form of the window (§5.2, a restatement of prior art); the proof of
Q5.3-d for all k ≤ s (§4); the conditional unboundedness of the transient under Dickson's
conjecture and the explicit t = 13 signature (§3.3); the remark that only principal convergents
give Bizley values with k ≥ 2 (§5.3); two further Bizley orders 1330 and 1995.

*Could not check.*  Winkler's two ResearchGate preprints (HTTP 403), so the novelty of the Bizley
values N(k·Qₙ) stays unknown.  De Koninck's books were not consulted directly (cited through
OEIS).  "Not found in OEIS" means a term search returned nothing on 2026-10-06, nothing more.
The least n with transient 13 was not computed.  That every member n ≥ 2 of a coefficient
stopping class really drops at step L is the coefficient-stopping-time conjecture; only small and
large representatives were tested.
