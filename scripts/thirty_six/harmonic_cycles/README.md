# Thread 1 — harmonic_cycles: 36 = T_8 = 6^2, unit cells, and the cycles of 3x+1 on Z

Part of the "36" investigation (five parallel threads). This thread tests one reading of
"36 is both triangular and square": 36 = 8*9/2, and (8, 9) = (2^3, 3^2) is the last pair of
consecutive 3-smooth numbers.

## Verdict (read this first)

1. **What is solid.** There is a clean, fully proved statement in which 36 appears:
   *a cycle of the shortcut map on Z with exactly one even element (parity word 1^a 0, i.e.
   a triplings and a+1 halvings in the non-shortcut count) exists iff 2^(a+1) and 3^a are
   consecutive, iff 6^a is triangular, iff a = 0, 1, 2; the three cycles are {0}, {1, 2},
   {-5, -7, -10}; in the coordinate v = n + 1 the last one is -4 -> -6 -> -9 and
   36 = (-4)(-9) = T_(-9) = T_8 = 6^2.* (Theorem 5 below.) It is the b = 1 case of the
   Davison-Steiner circuit equation, where the divisibility collapses to D | 1; it is
   elementary and not new. The same statement holds verbatim for 3x-1 (cycles {0}, {-1,-2},
   {5,7,10}); for 5x+1 the only such cycles are {0} and {-1,-2}.
2. **What 36 really is here.** In every result the thing doing the work is the pair (8, 9),
   i.e. 9 - 8 = 1, i.e. the lattice point (2,2) reached as v_bot * v_top = 2^2 * 3^2.
   36 is a by-product (half the product of the pair), never an input. The identity
   v * v' = T_v holds at *every* even step of *every* orbit, so "the product is triangular" is
   automatic; the content is v_top = (3/2)^a v_bot with v_bot = +-2^a.
3. **How much of it is new.** Essentially none. Gersonides (1343), Davison (1976),
   Steiner (1977), Lagarias (1990), Halbeisen-Hungerbuhler (1997), Stormer/Lehmer,
   Pillai/Stroeker-Tijdeman and Carey-Clampitt (1989) cover the ingredients. What this thread
   adds is the bookkeeping that ties them to one another and to this repo's vocabulary, plus a
   few small lemmas that are elementary and for which no novelty is claimed.
4. **Bearing on the conjecture: none.** Unit cells are exactly the cells where integrality of
   the cycle equation is automatic. The conjecture is about the infinitely many cells where it
   is not. Every statement here is either sign-symmetric, or separates +1 from -1 only through
   the sign of 2^k - 3^s (an archimedean triviality).
5. **Nulls.** "Known cycles sit at named Pythagorean intervals" is a tautology plus a size
   constraint, and is not a law: in the control family 3x+c it holds for 21 % of 257 cycles
   overall and for about 60 % of the cycles that are large relative to c (the fair comparison);
   the same pattern holds for all five known cycles of 5x+1, so it does not single out 3.
   The fourth 3-smooth triangular number, T_2 = 3, does not fit the product story. Nothing
   about 36 persists beyond denominator 1.

## Conventions (the same in every script and every table)

* Shortcut (Terras) map on all of Z: T(n) = n/2 (n even), (3n+1)/2 (n odd).
  Generalisations: T_q(n) = (qn+1)/2 on odd n; T_c(n) = (3n+c)/2 on odd n.
* A parity word w = (w_0 ... w_(k-1)), w_j = parity of T^j(n). k = number of shortcut steps,
  s = number of odd steps. **Cell** (k, s) = all words with these counts.
* T_w(x) = (3^s x + C(w)) / 2^k, with C(w) = sum over j with w_j = 1 of
  3^(number of ones after j) * 2^j. **Cell denominator** D(k, s) = 2^k - 3^s. Fixed point
  x(w) = C(w) / D.
* Repo conventions differ: `collatz.dropping.dropping_time` counts steps of the NON-shortcut map,
  so repo Dropping Set index K = k + s and `orbital_oddity` = s (checked on 5810 values in
  `q16_dropping_thresholds.py`). The dropping orbit includes n; the stopping orbit excludes it.
* Musical interval of a cell: 3^s / 2^k; cents = 1200 (s log2 3 - k). Positive cents
  (ascending) <=> D < 0 <=> negative-integer side.
* Fact L (Bohm-Sontacchi 1978; Lagarias 1990; via the Terras 2-adic conjugacy): for every word
  w, x(w) is the unique 2-adic integer whose parity sequence is w repeated for ever. Hence an
  integer n is periodic with parity word w iff n = x(w), and integer cycles of T correspond
  to primitive necklaces w with D | C(w).

## Results

Status labels: proved / computed / conjecture / null / prior art / numerology.
"Mirror" = does the statement distinguish 3x+1 from 3x-1 (positive from negative integers) and
from 5x+1.

| id | statement | status | role of 36 | mirror | script |
|----|-----------|--------|------------|--------|--------|
| 1.1-a | T_n is 3-smooth iff {n, n+1} = {2^k, 3^s} with \|2^k - 3^s\| = 1; then T_n = 2^(k-1) 3^s. So n = 1, 2, 3, 8 <-> cells (1,0), (1,1), (2,1), (3,2) <-> T = 1, 3, 6, 36. Bijection, canonical. | proved; prior art (Levi ben Gerson 1343) | 36 = 2^2 3^2 = half of 8*9; really about the pair (8, 9) | n/a (pure number theory) | q11 |
| 1.1-b | For k >= 2, 1 <= s <= k-1: every word of cell (k,s) has an integer fixed point iff two words differing by one adjacent transposition both do iff \|D\| = 1. (Transposition lemma: such a swap changes C(w) by exactly 3^t 2^j.) | proved; elementary. Prior art for the qualitative form (moving a one to the right increases the numerator): Halbeisen-Hungerbuhler 1997, Lemma 4 | none (holds for every cell) | blind to sign and to the multiplier (re-checked for 3x-1, 5x+-1, 7x+1, and for the cyclic swap) | q11 C, D; verify/v1 |
| 1.1-c | The primitive integer cycles living in unit cells are exactly {0}, {-1}, {1,2}, {-5,-7,-10}, one per unit cell. Every other integer cycle needs D \| C(w) with \|D\| > 1 ("accident") and is isolated: no transposition-neighbour is an integer cycle. First accident: the -17 cycle, cell (11,7), D = -139, one necklace out of 30. | proved (classification) + computed (k <= 24: 1,465,020 necklaces, exactly 5 integer cycles; re-derived independently from Lyndon words) | 36 labels the cell (3,2) of the -5 cycle | sign enters only through sign(D): D = +1 -> {0}, {1,2}; D = -1 -> {-1}, {-5..}. For 3x-1 the same cells hold the negated cycles. Separates 3 from 5 (5x+1 has unit cells (1,0), (2,1) only) | q11, q13; verify/v1, v3 |
| 1.1-d | One-even-element theorem: the word 1^a 0 closes on an integer iff \|2^(a+1) - 3^a\| = 1 iff 6^a is triangular iff a in {0,1,2}. In v = n+1: v_bot = m 2^a, v_top = m 3^a, m = +-1, and v_bot * v_top = T_(v_top) = 6^a = 1, 6, 36. | proved; prior art: it is the b = 1 case of the circuit equation (2^(a+b) - 3^a) h = 2^b - 1 of Davison 1976 / Steiner 1977. Wells 1986 records 1, 6, 36 as "the smallest triangular numbers in geometric sequence" | by-product with a mechanism: 36 = (-4)(-9) = T_(-9) = T_8 for the -5 cycle; = lattice point (2,2). Note v * v' = T_v at every even step of every orbit, so only "= 6^a" is specific | sign-symmetric as a statement on Z; for 3x-1 the cycle is 5,7,10 with v = n-1 = 4,6,9. For q != 3 no cycle with one even element and >= 2 odd elements exists (direct search \|n\| <= 2*10^5 for 5x+-1, 7x+-1, 9x+1) | q11 E, F; verify/v1 |
| 1.1-e | The correspondence "triangular number = product of the extreme v-values" covers three of the four cells (those whose cycle has one even element). T_2 = 3 <-> cell (1,1) <-> fixed point -1 has v = 0; it is matched by the cell only. | null (for the fourth element) | n/a | n/a | q11 E |
| 1.2-a | For odd q >= 3: \|2^k - q^s\| = 1 (k >= 1, 0 <= s <= k) iff (k,s) = (1,0); or s = 1 and q = 2^k +- 1; or (q,k,s) = (3,3,2). So q = 3 has 4 unit cells, q = 2^j +- 1 (q != 3) has 2, every other q has 1. Cycles: q = 2^k - 1 -> through +1; q = 2^k + 1 -> through -1. | proved (elementary, no Mihailescu needed) + computed (q <= 2001; direct cycle search q <= 201); special case of Catalan; the cycle through 1 for q = 2^k - 1 is standard (qx+1 literature after Crandall 1978) | 36 appears only for q = 3, a = 2 | separates 3 from every other multiplier; sign-symmetric | q12 A-C |
| 1.2-b | Link to the repo's half-eigenvalue theorem: the functional delta_a - delta_(x_o) is a left eigenvector (eigenvalue -1/2) of the signed kernel mod p iff e(x_o) = a, i.e. iff 2(q-2) = q-1 mod p (x_o = -1/(q-2) fixed point of the odd branch = cell (1,1); a = -1/(q-1) where the branches agree). Over Z this is q = 3. No other universal eigenvalue exists for q = 5 ... 129 (only 0). | proved; this is the d = 2 case of the repo's own theorem (functional delta_(-1/d) - delta_(-1), q = d + 1), restated, not a new result. Computed part re-done (determinant test for primes < 300; exact gcd of characteristic polynomials) | none | residue-only, sign-blind; sees the multiplier | q12 D; verify/v2 |
| 1.2-c | "Three unit cells" vs "3 = 2 + 1": the half-eigenvalue functional is attached to one word at a time and exists exactly when that word's cell has D = -1 (N = 2^k + 1). For the kernel of T itself only the cell (1,1) (3 = 2+1) qualifies. The cell (3,2) (9 = 8+1) carries the same functional in the two-branch kernel (x/8, (9x+C)/8), anchored at the -5 cycle; this is the pair (9,8) already on the repo's "q = d + 1" list. The D = +1 cells ((2,1), 3 = 4-1, cycle {1,2}) carry none. | proved (Proposition 7') + computed (primes < 200) | none | residue-only, sign-blind (sees 9 = 8+1, not the sign of the integers) | verify/v2 part 5 |
| 1.3-a | Cells with 1 <= s < k ordered by \|D\|: 1, 1, 5, 5, 7, 11, 13, 13, 17, 23, 29, 37, 47, 49, ... The signed values D = 5 and D = 13 are each attained twice ((3,1), (5,3); (4,1), (8,5)); \|D\| = 1 is attained twice with opposite signs ((2,1), (3,2)); nothing else repeats for k <= 400. | computed; prior art (Pillai 1945, Stroeker-Tijdeman 1982, for the signed equation 3^x - 2^y = c) | none | - | q13 A; verify/v3 |
| 1.3-b | Identity 2^(k-1) 3^s = n(n + \|D\|)/2, n = min(2^k, 3^s): triangular only when \|D\| = 1. | proved (trivial) | 36 is the last triangular value | - | q13 A |
| 1.3-c | Circuits 1^a 0^b with a, b >= 1 that close on an integer: only (1,1) -> 1 and (2,1) -> -5, for a + b <= 700 (re-checked for every a <= 12000). | computed; prior art (Steiner 1977 for the positive side, via Baker; Rukhin 2018 treats the 3x-1 side, conditionally; Simons 2008 for generalisations) | none | sign-symmetric (3x-1 gives -1 and +5) | q13 B; verify/v3 |
| 1.3-d | Census of all primitive words with k <= 24: each is a primitive cycle of exactly one map 3x + c0, c0 = \|D\|/gcd(C, D). "Free" cycles (\|D\| = c) vs "accidents" tabulated for c <= 49. The number of free cycles of 3x+c is the necklace count of the cell(s) with \|D\| = c (minus the few with gcd > 1): 3x+13 has 8 (7 of them from the single cell (8,5)), 3x+5 has 3, 3x+37 has 3, 3x+47 has 5, 3x+139 has 29. | computed; prior art (Lagarias 1990; Belaga-Mignotte) | none | reported separately for both signs | q13 C; verify/v3 |
| 1.3-e | What persists of 36: for every a the map 3x + \|2^(a+1) - 3^a\| has the one-even-element cycle with v-values m 2^a .. m 3^a and v_bot * v_top = 6^a = n(n+c)/2. Triangular only for a <= 2. | proved (checked by iteration for a <= 60) | 36 = 6^2 is the last triangular member of 6^a | sign-symmetric family statement | q13 B2; verify/v3 |
| 1.3-f | Multiples of unit cells. Doubled: D(2k,2s)^2 = 8 T_n + 1 (3, 5, 7, 17). Tripled: \|D(3k,3s)\| = 6 T_n + 1, a centered hexagonal number (7, 19, 37, 217), where T_n is the cell's triangular number. In particular 37 = 2^6 - 3^3 = 6 T_3 + 1 = 1 + 36. | proved (x^2 - y^2 = x + y and x^3 - y^3 = 1 + 3xy when x - y = 1) | The 36 in "37 = 36 + 1" is 6 * T_3 from the cell (2,1), not T_8; the cell (3,2) that owns 36 = T_8 gives 17 = sqrt(8*36 + 1) and 217 = 6*36 + 1. That 6 * T_3 = T_8 is the coincidence 6 * 6 = 36: numerology beyond the identity | not a Collatz-dynamics statement | q13 A (tier table); verify/v3 |
| 1.4-a | For a finite set M of odd primes, the unit cells of shortcut words over {halve} + {(qx+1)/2 : q in M} are the Stormer pairs of {2} + M with a pure power of two on one side (true by definition: a unit cell is a consecutive pair {2^k, N}). Counts: 4 of 4 for {3}; 6 of 10 for {3,5}; 8 of 23 for {3,5,7}; 9 of 40; 11 of 68. Finiteness proved independently by lifting the exponent: 2^k - 1 <= B k. | proved (bound) + computed (re-checked for k <= 3000); prior art for the pairs (Stormer 1897, Lehmer 1964, OEIS A002071, A117581) | (8,9) is one of the pairs for every M containing 3 | n/a | q14 A, B; verify/v4 |
| 1.4-b | In every unit cell every word is a consistent integer cycle of the letter system (0 failures in 47,654 words). Further cells: 16 - 15 (3 cycles: 7,11,28,14 / 5,13,20,10 / 9,14,7,18) and 64 - 63 (10 cycles). They are cycles of an affine semigroup, not of one map: e.g. 7 is sent by 3 in one cycle and by 5 in another. | proved (consistency) + computed; no published source found in a quick search, no novelty claimed | none | n/a | q14 C; verify/v4 |
| 1.4-c | Every Stormer pair, in both orientations, is a unit cell of the semigroup "divide by the primes on one side, x -> qx+1 for the primes on the other"; all formal cycles are integral (same argument as Proposition 10). Some are cycles of the deterministic maps T_P ("divide by the smallest prime < P dividing x, else Px+1"): all cycles of T_5 and T_7 meeting \|n\| <= 2*10^5 are of this kind (T_5: (4,5), (5,6), (24,25); T_7: (6,7), (7,8), (48,49) and three 12-cycles from (2400,2401)); T_11 and T_13 also have non-Stormer cycles (e.g. T_11 through 17, 1344 - 1331 = 13). | proved (integrality) + computed; curiosity. The maps T_5, T_7 are prior art (Oliveira e Silva; OEIS A133421 ff.); their negative-side cycles were not found in a quick search | none | n/a | q14 D; verify/v4 |
| 1.5-a | Cell intervals of the five known cycles: 0 -> 1/2 (octave), -1 -> 3/2 (fifth), 1 -> 3/4 (fourth), -5 -> 9/8 (whole tone), -17 -> 2187/2048 (apotome, 113.685 cents). Confirmed. | computed | 36 is half the Benedetti height 72 of 9/8 (a tautology: T_n is half the height of (n+1)/n) | the cell and interval of a cycle are identical for 3x+1 and 3x-1 (cycles 1, 5, 17 of 3x-1 sit at 3/2, 9/8, 2187/2048); only the side differs: for 3x+1 positive cycles descend and negative ascend, for 3x-1 the reverse | q15 B; verify/v5 |
| 1.5-b | For a cycle not containing 0: 2^k / 3^s = product over odd elements of (1 + c/(3x)); and 3^s / 2^k = product over circuits of (1 + 1/top)/(1 + 1/bottom): 3/4 = (3/2)(1/2); 9/8 = (5/4)/(10/9); 2187/2048 = (17/16)(41/40)/((82/81)(136/135)). (For {0} the product is empty and the formula fails: 1 != 2.) | proved; rewriting of the cycle equation (Steiner; Simons-de Weger) | 9/8 = (5/4)/(10/9) uses x = 5, 10 and v = 4, 9 | holds on both signs | q15 B; verify/v5 |
| 1.5-c | Record cells (3^s/2^k closer to 1 than for every smaller s on the same side) = convergents and semiconvergents of log2 3 (19 cells, s <= 700). The ladder (1,0), (1,1), (2,1), (3,2), (5,3), (8,5), (11,7), (19,12), ... is the Euclid ladder of well-formed Pythagorean scales; each cell is the sum of two earlier ones. | computed check of a classical theorem (re-checked with exact integer arithmetic for s <= 3000: 23 cells); prior art (best one-sided approximations; Carey-Clampitt 1989; three-gap theorem) | none | sign-blind | q15 A; verify/v5 |
| 1.5-d | The five known cycles occupy five of the first seven record cells. Four are unit cells (= the first four convergents 1/0, 1/1, 2/1, 3/2). For the fifth: a negative cycle other than {-1} with s = 7 can only live in (11,7). The forcing is not special to s = 7: for every s <= 10 at most one negative cell is admissible (s = 2, 4, 6, 7, 8, 9, 10), and only s = 2 and s = 7 give record cells. So "the fifth cycle is at a record cell" is a 2-in-7 coincidence given the forcing. | proved (the size bound, trivial) + numerology (the record-cell reading); the "named interval" part is a tautology | (8,9) again: the only non-trivial unit cell | the cell of a cycle is the same for 3x+1 and 3x-1; only "which side" is sign(D) | q15 C; verify/v5 |
| 1.5-e | Control family: 257 primitive cycles of 3x+c, 5 <= c <= 199, meeting [-20000, 20000]: 21.4 % in record cells (positive side 10.3 %, negative side 45.1 %); 0 % when \|min\| <= 3c, 51.9 % when \|min\| > 3c, 59.6 % when \|min\| >= 5c (the size of the -5 and -17 cycles relative to c = 1). Cousin: all five known cycles of 5x+1 on Z sit at record cells of log2 5. "Cycles sit at (semi)convergents" is not a law, but it is a strong tendency for cycles that are large relative to c, for any multiplier and either sign (Crandall/Eliahou mechanism). | computed; null as a law | none | does not distinguish 3x+1 from 3x-1 or from 5x+1 | q15 D; verify/v5 |
| 1.6-a | Dropping classes: for a dropping word, n drops iff n > x(w) = C(w)/D. The threshold is an integer only in Dropping Set_1 (evens, threshold 0) and Dropping Set_3 (n = 1 mod 4, threshold 1): the two unit cells with D = +1. For 3x-1 the unit cells with D = -1 are rising cells and hold the non-dropping cycles 1 and 5,7,10. | computed (every dropping word with k <= 24; n < 2^20). The general statement is implied by "no non-trivial positive cycle" but is not equivalent to it (see Q1.6) | none | yes, through sign(D) only; for 5x+1 the integer thresholds are 0, 1, 13, 17 (its cycles) | q16; verify/v6 |
| S-1 | The -17 cycle passes through the lattice point (2,2): in v = n+1 its first run of odd steps is -16, -24, -36, -54, -81 = -(2^4, 2^3 3, 2^2 3^2, 2 3^3, 3^4), so n = -37 = -(36+1) is on the cycle. The three non-trivial known cycles contain runs with unit lambda of height 1 ({1,2}), 2 (-5) and 4 (-17), because their minima are 2-1, -(2^2+1), -(2^4+1); the runs are left through the consecutive pairs (3,4), (8,9), (80,81). | computed; the mechanism (a run starting at v = +-2^a traverses an anti-diagonal) is classical, the fact that the -17 cycle starts at -2^4 is not explained. Base rate: among the 67 maps 3x+c with c <= 199 (cycles meeting [-3000, 3000]) 6 have an odd cycle element with \|v\| = 36 and 29 have one with \|v\| = 6^a for some a >= 1. Do not read more into it | 36 appears as \|v\| itself, at n = -37 | mirror: 3x-1 has n = 37, v = n-1 = 36 on its 17-cycle; no bearing on the conjecture | verify/v3 part 7 |

## Proofs

**Theorem 1 (Levi ben Gerson).** For integers k >= 1, s >= 0: |2^k - 3^s| = 1 iff
(k, s) in {(1,0), (1,1), (2,1), (3,2)}.

*Proof.* (i) 2^k - 3^s = 1. If s = 0 then k = 1. If s >= 1 then 2^k = 1 mod 3, so k = 2j and
(2^j - 1)(2^j + 1) = 3^s; two powers of 3 differing by 2 are 1 and 3, so j = 1: (2,1).
(ii) 3^s - 2^k = 1. If k = 1 then s = 1. If k >= 2 then 3^s = 1 mod 4, so s = 2j and
(3^j - 1)(3^j + 1) = 2^k; two powers of 2 differing by 2 are 2 and 4, so j = 1: (3,2). QED

**Proposition 2 (3-smooth triangular numbers).** For n >= 1, T_n = n(n+1)/2 is 3-smooth iff
{n, n+1} = {2^k, 3^s} for a unit cell (k, s), and then T_n = 2^(k-1) 3^s. The map n -> (k,s)
is a bijection {1, 2, 3, 8} -> {(1,0), (1,1), (2,1), (3,2)}.

*Proof.* T_n 3-smooth iff n(n+1) = 2^(a+1) 3^b. As gcd(n, n+1) = 1, the even one of the two
carries all of 2^(a+1) and one of the two carries all of 3^b; so either one is 2^(a+1) and the
other 3^b, or the even one is 2^(a+1) 3^b and the other is 1, which forces n = 1, n + 1 = 2 and
is the pair (3^0, 2^1) again. Conversely each unit cell gives one such n = min(2^k, 3^s).
Apply Theorem 1. QED

(For n <= 0: T_0 = T_(-1) = 0 is not 3-smooth, and T_(-n-1) = T_n, so the negative solutions
n = -2, -3, -4, -9 mirror the positive ones. Checked by direct factoring for |n| <= 3*10^6.)

**Lemma 3 (transposition).** Let w have w_j = 1, w_(j+1) = 0, and let w' be w with these two
letters swapped. Then C(w') - C(w) = 3^t 2^j, t = number of ones of w after position j+1.

*Proof.* Each one contributes 3^(ones after it) * 2^(position). For every other one the count of
later ones is unchanged. The moved one keeps the same t and its position goes from j to j+1:
difference 3^t (2^(j+1) - 2^j). QED

(The inequality C(w') > C(w), for ones moved to the right over any distance, is Lemma 4 of
Halbeisen-Hungerbuhler 1997. For qx + c the increment is c q^t 2^j; checked for 3x-1, 5x+-1,
7x+1. Because every rotation of an integer word is an integer word, the conclusion of
Theorem 4 also covers the cyclic swap of the last and first letters.)

**Theorem 4 (unit cells are the all-integer cells).** Let k >= 2, 1 <= s <= k-1, D = 2^k - 3^s.
The following are equivalent: (a) |D| = 1; (b) every word of the cell has an integer fixed
point; (c) some two words related by one adjacent transposition both have integer fixed points.

*Proof.* (a) => (b) is clear, (b) => (c) because the cell contains 1^s 0^(k-s), which has an
adjacent "10". (c) => (a): D divides C(w') - C(w) = 3^t 2^j, and gcd(D, 6) = 1 since k, s >= 1.
QED

The remaining cells have s = 0 (only word 0^k, fixed point 0) or s = k (only word 1^k, fixed
point -1); these words are primitive only for k = 1, giving the unit cells (1,0) and (1,1).

**Corollary (classification).** A unit cell (k, s) has s in {0, 1, k-1, k}, hence exactly one
necklace, hence exactly one cycle: (1,0) -> {0}; (1,1) -> {-1}; (2,1) -> {1, 2};
(3,2) -> {-5, -7, -10}. Any other integer cycle of T lies in a cell with |D| > 1, satisfies
D | C(w), and by Theorem 4 none of its transposition-neighbours is an integer cycle.

**Honest answer to "bijection, and is it natural?"** n <-> cell is canonical (Proposition 2).
Cell -> cycle is canonical once one notes each unit cell has a single necklace (a small-number
fact: s in {0,1,k-1,k}). The stronger reading "T_n is a product read off the cycle" holds for
three of the four cells only (Theorem 5); T_2 = 3 and the fixed point -1 are matched by the
cell and nothing else.

**Theorem 5 (one even element; the role of 36).** Let a >= 0. The word 1^a 0 (a odd elements
followed by one even element; a triplings and a+1 halvings in the non-shortcut count) has an
integer fixed point iff |2^(a+1) - 3^a| = 1 iff a in {0, 1, 2} iff 6^a is a triangular number.
In the coordinate v = n + 1 the cycle is m 2^a -> m 2^(a-1) 3 -> ... -> m 3^a with
m = 2^(a+1) - 3^a = +-1, and v_bot * v_top = T_(v_top) = 6^a. This is the case b = 1 of the
circuit equation of Davison and Steiner; for b = 1 the divisibility (2^(a+b) - 3^a) | (2^b - 1)
reads D | 1, which is why no Baker-type argument is needed.

*Proof.* x(1^a 0) = (3^a - 2^a)/D with D = 2^(a+1) - 3^a. If D divides 3^a - 2^a it divides
(3^a - 2^a) + D = 2^a, and D is odd, so D = +-1; the converse is trivial. Theorem 1 with
(k, s) = (a+1, a) gives a in {0,1,2}. In v-coordinates an odd step is v -> 3v/2 and an even step
is v -> (v+1)/2. The parities force v_bot = m 2^a with m odd and v_top = m 3^a; closing requires
(v_top + 1)/2 = v_bot, i.e. m D = 1. Then T_(v_top) = v_top (v_top + 1)/2 = v_top v_bot = 6^a m^2.
Finally 6^a triangular iff n(n+1) = 2^(a+1) 3^a iff {n, n+1} = {2^(a+1), 3^a} (coprimality)
iff |D| = 1. QED

For a = 2: n-orbit -5 -> -7 -> -10, v-orbit -4 -> -6 -> -9 = -(2^2, 2*3, 3^2), the whole
anti-diagonal of the exponent lattice at height 2, and 36 = (-4)(-9) = (-6)^2 = T_(-9) = T_8.
"36 is triangular and square" is the statement "a = 2 is an admissible exponent and is even".

Two cautions on how much this says. (i) The identity v * v' = v(v+1)/2 = T_v holds at every
even step of every orbit (v' = (v+1)/2), in a cycle or not; e.g. the -17 cycle has the even
steps -81 -> -40, -135 -> -67, -67 -> -33, -33 -> -16 with products T_80, T_134, T_66, T_32.
Only "the product is 6^a" is specific to the one-even-element cycles. (ii) The statement is
the same for 3x-1 (v = n - 1, cycle 5, 7, 10, v = 4, 6, 9): it does not see the sign.

Caution, checked: for general q the closure condition is |2^(a+1) - q^a| = 1 (only (q,a) =
(3,1), (5,1), (3,2) for odd q < 2000, a <= 60, and provably only these by Theorem 6), but
"(2q)^a is triangular" is equivalent to it only for prime-power q:
(2*3465)^2 = 48024900 = T_9800 with 9800 = 8*35^2, 9801 = 99^2.

**Theorem 6 (why 3).** For odd q >= 3, k >= 1, 0 <= s <= k: |2^k - q^s| = 1 iff s = 0 and
k = 1; or s = 1 and q = 2^k +- 1; or (q, k, s) = (3, 3, 2).

*Proof.* s = 0, 1 are immediate. Let s >= 2. Case q^s - 1 = 2^k: if s is even, q^(s/2) - 1 and
q^(s/2) + 1 are powers of two differing by 2, so q^(s/2) = 3, q = 3, s = 2, k = 3. If s is odd,
(q^s - 1)/(q - 1) is a sum of s odd terms, hence odd and > 1: impossible. Case q^s + 1 = 2^k:
if s is even, q^s = 1 mod 8 so q^s + 1 = 2 mod 8, k = 1, impossible. If s is odd,
(q^s + 1)/(q + 1) is an alternating sum of s odd terms, hence odd and > 1: impossible. QED

Consequences: the word 1 0^(k-1) has fixed point 1/(2^k - q), so q = 2^k - 1 gives the cycle
1 -> 2^(k-1) -> ... -> 1 and q = 2^k + 1 gives -1 -> -2^(k-1) -> ... -> -1. q = 3 is the only
multiplier that is both (3 = 2 + 1 = 4 - 1) and the only one with a cell at s = 2 (9 = 8 + 1).
A related classical fact (not an equivalent one): 2^3 + 1 = 3^2 is the Zsigmondy exception for
sums, and 2^6 - 1 = 3^2 * 7 the exception for differences, in base 2. Theorem 6 was re-checked
from the other side: among 2^k - 1 and 2^k + 1 with k <= 1500 the only perfect power is 9.

**Proposition 7 (the half-eigenvalue functional).** On functions on Z/p (p not dividing
2q(q-1)(q-2)) let e(x) = x/2, o(x) = (qx+1)/2, and K^- = (R_e - R_o)/2 acting on measures by
delta_x K^- = (delta_(e(x)) - delta_(o(x)))/2. Put x_o = -1/(q-2) (fixed point of o) and
a = -1/(q-1) (where e(a) = o(a)). Then delta_a K^- = 0 and
(delta_a - delta_(x_o)) K^- = (delta_(x_o) - delta_(e(x_o)))/2, so delta_a - delta_(x_o) is an
eigen-functional with eigenvalue -1/2 iff e(x_o) = a mod p iff p | q - 3. It holds for every p
iff q = 3.

This is the d = 2 case of the theorem already recorded in this repo (functional
delta_(-1/d) - delta_(-1) for the kernel with branches x/d and (qx+1)/d, which works iff
q = d + 1); Proposition 7 restates it and adds nothing to it.

*Check.* For q = 3, det(I + R_e - R_o) = 0 at all 60 primes 5 <= p < 300. For q != 3, -1/2 is
in spec(K^-_p) at a sporadic set of primes (between 2 and 8 primes below 300 for each of
q = 5, 7, 9, 11, 13, 15, 17, 31, 33, 63, 65, 127, 129; determinant zero modulo two 31-bit
primes, confirmed by an exact integer determinant for p <= 61). That set contains the primes
p >= 5 dividing q - 3, but this is automatic and confirms nothing: K^-_p depends on q only
through q mod p, so at those primes the matrix *is* the q = 3 matrix. The other sporadic primes are not explained by the proposition. Exact gcds
of characteristic polynomials over the primes 7..43 give the common factor x^2 (x + 1) of
2K^- for q = 3 and a power of x alone for q = 5, 7, 9, 15, 17, 31, 33: no universal non-zero
eigenvalue for those multipliers.

**Proposition 7' (which unit cells carry the functional).** Let w be a word with
T_w(x) = (N x + C)/2^k, N odd (N = 3^s for T, N = q^s for T_q), and consider the two-branch
signed kernel
K^-_w f(x) = (f(x/2^k) - f(T_w(x)))/2 on Z/p. Put x_w = C/(2^k - N) (the fixed point of T_w,
i.e. the periodic point with word w) and a = -C/(N - 1) (where the two branches agree). Then
delta_a K^-_w = 0 and (delta_a - delta_(x_w)) K^-_w = (delta_(x_w) - delta_(x_w / 2^k))/2, so
delta_a - delta_(x_w) is an eigen-functional with eigenvalue -1/2 iff x_w / 2^k = a, i.e. iff
(2^k - 1)(2^k + 1 - N) = 0, i.e. iff N = 2^k + 1, i.e. iff the cell of w is a unit cell with
D = -1. The functional is non-zero for every prime p not dividing 6 C (2^k - 1).

*Proof.* x_w/2^k = a reads C(N - 1) = -C 2^k (2^k - N), i.e. 2^(2k) - N 2^k + N - 1 = 0, which
factors as (2^k - 1)(2^k + 1 - N). The rest is the computation of Proposition 7. QED

*Check* (same determinant test, primes < 200): -1/2 is in the spectrum at every non-degenerate
prime for the words 1 (x_w = -1), 110, 101, 011 (x_w = -5, -7, -10) and for the 5x+1 word 10
(x_w = -1, 5 = 4 + 1); only sporadically for the D = +1 words 10, 01 of the cell (2,1) (9 of 44 primes),
for the 7x+1 word 100 (18 of 43) and for the -17 word (3 of 40).

**Answer to "same phenomenon?"** Partly. The half-eigenvalue functional is the unit-cell
condition with the sign D = -1, one word at a time: the repo's "q = d + 1" list ((3,2), (5,4),
(9,8), (17,16), ...) is exactly "the cell of the single odd branch has D = -1". For the kernel
of T itself this is the cell (1,1) only (3 = 2 + 1, fixed point -1). The other negative unit
cell (3,2) (9 = 8 + 1) carries the same functional, anchored at the -5 cycle, but in the
two-branch kernel (x/8, (9x + C)/8), not in the kernel of T. The positive unit cell (2,1)
(3 = 4 - 1, the cycle {1, 2}) carries none. All of this is a residue statement and blind to the
sign of the integers: it sees 9 = 8 + 1, and 3x-1 has the same kernels up to x -> -x.

**Proposition 8 (product formulas).** For a cycle of T_c not containing 0, with odd elements
x_1..x_s and length k: 2^k/3^s = prod (1 + c/(3 x_i)). (The cycle {0} is excluded: T(x)/x is
undefined there, and the empty product 1 is not 2^1/3^0.) If the cycle is cut into circuits
(a run of odd elements starting at x_j, ending at the even element X_j, then halvings), and
c = 1, then 3^s/2^k = prod_j (1 + 1/X_j)/(1 + 1/x_j).

*Proof.* Multiply T(x)/x over the cycle for the first. For the second use v = x + 1: along a
run of a_j odd steps X_j + 1 = (3/2)^(a_j) (x_j + 1), and x_(j+1) = X_j / 2^(b_j); multiply
over j and use prod x_(j+1) = prod x_j. QED

**Proposition 9 (Stormer pairs with a pure power of two).** Let M be a finite set of odd primes,
o_p = ord_p(2), B = prod over p in M of p^(v_p(2^(o_p) - 1)). If 2^k - 1 or 2^k + 1 is a product
of primes of M then 2^k - 1 <= B k.

*Proof.* For p | 2^k - 1, lifting the exponent gives v_p(2^k - 1) = v_p(2^(o_p) - 1) + v_p(k/o_p).
For p | 2^k + 1, p does not divide 2^k - 1, so v_p(2^k + 1) = v_p(2^(2k) - 1) =
v_p(2^(o_p) - 1) + v_p(2k/o_p) <= v_p(2^(o_p) - 1) + v_p(k). Multiply over p. QED

Since 2^k - 1 > B k persists once it holds, the list of unit cells is finite and explicit:
M = {3}: k <= 3; {3,5}: k <= 6; {3,5,7}: k <= 10; {3,..,13}: k <= 18.

**Proposition 10 (consistency in unit cells).** In a unit cell of the letter system
{x/2} + {(qx+1)/2 : q in M}, every word is an integer cycle with the right parities.

*Proof.* Every rotation of the word lies in the same cell, so every intermediate value is an
integer. If x' = x/2 is an integer x is even; if x' = (qx+1)/2 is an integer x is odd. QED

## Details by question

### Q1.1 (`q11_unit_cells.py`)

* All 314,122 three-smooth integers below 10^300: consecutive pairs are (1,2), (2,3), (3,4), (8,9).
* Unit cells with k <= 3000: (1,0), (1,1), (2,1), (3,2) with D = +1, -1, +1, -1.
* Exhaustive words k <= 18 (524,286 words): all-integer cells are the four unit cells plus the
  trivial one-word cells; primitive integer cycles found: 0, -1, {1,2}, {-5,-7,-10}, and the
  -17 cycle in (11,7).
* 98,305 adjacent transpositions (k <= 14): Lemma 3 holds in all; no adjacent integer pair
  outside unit cells.

| n | pair | cell | D | T_n = 2^(k-1) 3^s | cycle (n) | cycle (v = n+1) | v_bot * v_top |
|---|------|------|---|-------------------|-----------|-----------------|---------------|
| 1 | (1,2) | (1,0) | +1 | 1 | 0 | 1 | 1 |
| 2 | (2,3) | (1,1) | -1 | 3 | -1 | 0 | 0 (does not match) |
| 3 | (3,4) | (2,1) | +1 | 6 | 1, 2 | 2, 3 | 6 |
| 8 | (8,9) | (3,2) | -1 | 36 | -5, -7, -10 | -4, -6, -9 | 36 |

### Q1.2 (`q12_why_three.py`)

* 1000 odd multipliers 3 <= q <= 2001, s <= 150: unit cells agree with Theorem 6 in every case.
  4 cells: q = 3. 2 cells: 5, 7, 9, 15, 17, 31, 33, ..., 1023, 1025. 1 cell: the other 982.
* Direct search, q <= 201, starts in [-3000, 3000]: the only cycles outside unit cells are
  q = 3: -17 (D = -139); q = 5: 1 (cell (5,2), D = 7), 13 and 17 (cell (7,3), D = 3);
  q = 181: 27 and 35 (cell (15,2), D = 7). For 87 of the 100 multipliers the only cycle found
  is {0}.
* Kernel: -1/2 is an eigenvalue of K^-_p at all 23 primes 5 <= p < 100 for q = 3, and at 2 to 7
  primes for each other q tested. Universal eigenvalues: q = 3: {-1/2, 0}; every other q: {0}.

### Q1.3 (`q13_tiers.py`)

Convention: 1 <= s <= k-1 (the cells with s = 0 or k hold only 0^k, 1^k).

| \|D\| | sign | cell | n = min(2^k,3^s) | 2^(k-1) 3^s = n(n+\|D\|)/2 | necklaces | cycles there |
|-----|------|------|------|------|------|------|
| 1 | + | (2,1) | 3 | 6 = T_3 | 1 | 3x+1: {1,2} |
| 1 | - | (3,2) | 8 | 36 = T_8 | 1 | 3x+1: {-5,-7,-10} |
| 5 | + | (3,1) | 3 | 12 | 1 | 3x+5: {1,4,2} |
| 5 | + | (5,3) | 27 | 432 | 2 | 3x+5: cycles through 19 and 23 |
| 7 | + | (4,2) | 9 | 72 | 1 | 3x+7: {5,11,20,10} |
| 11 | - | (4,3) | 16 | 216 = 6^3 | 1 | 3x+11: {-19,-23,-29,-38} |
| 13 | + | (4,1) | 3 | 24 | 1 | 3x+13: {1,8,4,2} |
| 13 | + | (8,5) | 243 | 31104 | 7 | 3x+13: seven cycles |
| 17 | - | (6,4) | 64 | 2592 | 2 | 3x+17: two negative cycles |
| 37 | + | (6,3) | 27 | 864 | 3 | 3x+37: three cycles |
| 139 | - | (11,7) | 2048 | 2239488 | 30 | 3x+139: 29 negative cycles; 3x+1: the -17 cycle |

* Repeated denominators (1 <= s < k <= 400): the signed values D = 5 and D = 13, in agreement
  with Stroeker-Tijdeman, and |D| = 1 with both signs. The repetition is not why 3x+5 and
  3x+13 have many cycles: it adds one cycle each (the cells (3,1) and (4,1) have a single
  necklace). The free cycles of 3x+c are the necklaces of the cell(s) with |D| = c, and that
  number is large when |D| is small for the size of the cell: (8,5) gives 3x+13 seven cycles,
  (7,4) gives 3x+47 five, (11,7) gives 3x+139 twenty-nine.
* Circuits: for a, b >= 1, a + b <= 700 the divisibility (2^(a+b) - 3^a) | (2^b - 1) holds only
  for (1,1) and (2,1); re-checked for every a <= 12000 (only two pairs (a, b) even pass the
  size test |D| <= 2^b - 1). Steiner proved this (positive side) with Baker's method; the
  unit-cell argument proves existence, not uniqueness.
* Doubled and tripled unit cells: |D(2k,2s)| = sqrt(8 T_n + 1) = 3, 5, 7, 17 and
  |D(3k,3s)| = 6 T_n + 1 = 7, 19, 37, 217 for T_n = 1, 3, 6, 36. So 37 = 2^6 - 3^3 belongs to
  the cell (2,1) (T_3 = 6), and the numbers attached to 36 = T_8 in this way are 17 and 217.
* Census k <= 24: 1,465,020 primitive necklaces; integer cycles of 3x+1: 0, -1, 1, -5, -17.
  "Free vs accident" for 3x+1: four free, one accident (g = 139).
* Family 6^a: a = 3 gives 3x+11 and v = -8, -12, -18, -27 (product 216); a = 4 gives 3x+49;
  a = 5 gives 3x+179. Same picture, no triangular number.
* Heuristic count necklaces/|D| on the octave-reduced cells, against reality (3x+1):
  (5,3) 0.40 -> 0; (8,5) 0.54 -> 0; (11,7) 0.22 -> 1; (19,12) 0.37 -> 0. The heuristic is not
  calibrated on the positive side (archimedean obstruction; see the repo's earlier audit).

### Q1.4 (`q14_stormer.py`)

* Stormer-Lehmer Pell computation reproduces 4, 10, 23, 40, 68 pairs and agrees with brute
  force below 10^18; largest pairs (8,9), (80,81), (4374,4375), (9800,9801), (123200,123201).
* Unit cells 2^k - N = +-1:

| M | cells (2^k, N) | share of Stormer pairs |
|---|----------------|------------------------|
| {3} | (2,1), (2,3), (4,3), (8,9) | 4 of 4 |
| {3,5} | + (4,5), (16,15) | 6 of 10 |
| {3,5,7} | + (8,7), (64,63) | 8 of 23 |
| {3,5,7,11} | + (32,33) | 9 of 40 |
| {3,..,13} | + (64,65), (4096,4095) | 11 of 68 |

* So the answer to the seed question is: yes for the pairs with a pure power of two, no for the
  others ((5,6), (9,10), (24,25), (80,81) for {2,3,5}); those are unit cells of systems that
  also divide by 3 or 5 (part D of the script).
* Formal cycles exist in every unit cell and are genuine in the sense of Proposition 10, but the
  system is multi-valued at odd numbers. For M = {3,5}: -1 and 7 receive both multipliers.
* Deterministic maps T_P (divide by the smallest prime below P that divides x, otherwise
  x -> Px + 1), all cycles meeting [-2*10^5, 2*10^5], with (product of divisors, product of
  multipliers):

| map | cycles through | (divide, multiply) | Stormer pair? |
|-----|----------------|--------------------|---------------|
| T_5 | -1; 1; -7 | (4,5); (6,5); (24,25) | yes, all 3 |
| T_7 | -1; 1; -11; -509, -701, -961 | (6,7); (8,7); (48,49); (2400,2401) three times | yes, all 6 |
| T_11 | -1; 1; -13, -17; 17 | (10,11); (12,11); (120,121) twice; (1344,1331) | 4 of 5 |
| T_13 | 1; -1; -19; 19; -9959; -99503 | (14,13); (12,13); (168,169); (28800,28561); two long ones | 3 of 6 |

### Q1.5 (`q15_intervals.py`)

| cycle | cell | D | 3^s/2^k | cents | interval | log2 3 status |
|-------|------|---|---------|-------|----------|----------------|
| 0 | (1,0) | +1 | 1/2 | -1200.0 | octave, descending | convergent 1/0 |
| -1 | (1,1) | -1 | 3/2 | +702.0 | perfect fifth | convergent 1/1 |
| 1, 2 | (2,1) | +1 | 3/4 | -498.0 | perfect fourth, descending | convergent 2/1 |
| -5 | (3,2) | -1 | 9/8 | +203.9 | major whole tone | convergent 3/2 |
| -17 | (11,7) | -139 | 2187/2048 | +113.7 | apotome | semiconvergent 11/7 |

The owner's guess about the -17 cycle is correct. The two record cells that are skipped,
(5,3) (minor third 32/27, D = 5) and (8,5) (limma 256/243, D = 13), are exactly the homes of
the 3x+5 and 3x+13 cycles.

**Theorem, tautology or numerology? All three, in separable parts.**

* *Tautology.* Every cell ratio 3^s/2^k is a 3-limit interval, and every such interval with
  small s has a classical name. "Named" carries no information.
* *Theorem (small).* The four unit-cell cycles sit at the four superparticular 3-limit
  intervals 2/1, 3/2, 4/3, 9/8, because "unit denominator" and "superparticular" are the same
  condition (Theorem 1, Theorem 4). These are also the first four convergents of log2 3.
* *Forced (small).* A negative cycle other than {-1} has all odd elements <= -5, so
  1 < 3^s/2^k <= (15/14)^s. For s = 7 the only cell allowed is (11,7). So once a seven-odd-step
  negative cycle exists it is at the apotome; no further information. The same bound allows at
  most one cell for every s <= 10 (s = 2, 4, 6, 7, 8, 9, 10), and only for s = 2 and s = 7 is
  that cell a record cell: the apotome is where a 7-odd-step cycle must be, and 7 happens to be
  one of the two "good" values of s.
* *Classical theorem (large).* For a hypothetical cycle with huge minimum the same inequality
  forces k/s to be a convergent of log2 3 (Crandall 1978, Eliahou 1993, Simons-de Weger 2005).
  That is prior art and is the only place where continued fractions do real work.
* *Not a law, and not about 3.* In the control family 3x+c only 21.4 % of 257 cycles are in
  record cells. That figure is diluted by the 151 cycles with |min| <= 3c, whose interval is far
  from the unison by Proposition 8 (0 % in record cells); among cycles with |min| >= 5c, the
  relative size of the -5 and -17 cycles, it is 53 of 89 = 59.6 %. So two cycles out of two in
  record cells has probability about 0.3 under the control: no signal. The cousin 5x+1 shows the
  same pattern: its five known cycles on Z sit in the cells (1,0), (2,1), (5,2), (7,3), (7,3),
  all record cells of log2 5 (5/4, 32/25, 128/125). And the cell of a cycle is the same for
  3x+1 and 3x-1. In the 3x+c family 124 distinct cells are occupied, 6 of them record cells.
  Four of the six most populated cells
  are nevertheless record cells ((11,7) 29 cycles, (19,12) 8, (27,17) 7, (8,5) 7; the other two
  are (8,4) and (22,14) with 8 each). This matches the heuristic "necklaces/|D| is largest
  where |D| is a record low": 70.5 % of the heuristic weight of the allowed negative non-unit
  cells with s <= 12 sits on (11,7) and (19,12). So "-17 at the apotome" is one
  divisibility accident (139 | C(w) for 1 necklace of 30) in the likeliest place for one.
* *Numerology.* Reading meaning into the particular list octave, fifth, fourth, tone, apotome
  beyond the above.

For the musician: 9/8 = (5/4)/(10/9) is the -5 cycle written with |n| = 5, 10 and |v| = 4, 9
(major third = major tone + minor tone). It is the cycle equation, not an extra fact.

### Q1.6 (`q16_dropping_thresholds.py`, beyond the seed)

| repo Dropping Set K | cell (k,s) | D | dropping words | thresholds C(w)/D | integer? |
|----|-------|---|----|------|------|
| 1 | (1,0) | 1 | 1 | 0 | yes: 0 |
| 3 | (2,1) | 1 | 1 | 1 | yes: 1 |
| 6 | (4,2) | 7 | 1 | 5/7 | no |
| 8 | (5,3) | 5 | 2 | 19/5, 23/5 | no |
| 11 | (7,4) | 47 | 3 | 65/47 .. 85/47 | no |
| 13 | (8,5) | 13 | 7 | 211/13 .. 319/13 | no |

The word counts 1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, ... are OEIS A186009
("length of Collatz dropping time patterns"), i.e. A100982 with one more leading 1 (already
recorded as prior art in this repo). The "n > 0" and "n > 1" in the definitions of
Dropping Set_1 and Dropping Set_3 are the two positive unit cells. This is the cleanest contact
between this thread and the repo's dropping classes, and it is a restatement, not a result.

Re-derived with dropping words generated combinatorially (every prefix has 3^(s_j) > 2^j, the
whole word has 2^k > 3^s) for k <= 24, 81,119 words: integer thresholds occur only in (1,0) and
(2,1), and the largest ratio threshold / smallest member of the class is 0.495 (cell (8,5)).

What this is logically. "No dropping word outside the unit cells has an integer threshold" is
*implied by* "no non-trivial positive cycle" (an integer threshold is a periodic point). It is
not equivalent to it: a cycle's word, read from its minimum, need not be a dropping word, because
the minimum may sit below the non-integer threshold of a shorter dropping word. In the 3x+c
family this happens for 11 of 32 positive cycles (c = 5 .. 29); e.g. for 3x+5 the cycle {1, 4, 2}
has word 100 while the class 1 mod 4 has dropping word 10 with threshold 5. The statement that
does imply "no non-trivial cycle" is Terras' coefficient-stopping-time conjecture (every n >= 2
exceeds the threshold of its class); the converse implication is not known.

Mirror and cousin. For 3x-1 the thresholds are -C(w)/D <= 0, so every positive member of every
dropping class drops; what fails to drop are the cycle minima 1, 5, 17 in cells with D < 0.
For 5x+1 the integer thresholds are 0, 1, 13, 17: the unit cell (1,0) and the three accident
cycles (cells (5,2), D = 7 and (7,3), D = 3).

## Null results and dead ends

* T_2 = 3 does not fit "triangular number = v_bot * v_top" (v = 0 at the fixed point -1).
* "(2q)^a triangular iff the one-even-element circuit of qx+1 closes" is false for composite q
  (q = 3465). True for q = 3.
* No universal eigenvalue of the signed or unsigned kernel of T_q (branches x/2, (qx+1)/2) for
  q = 2^k +- 1, q != 3: in that kernel the cells (k,1) leave no spectral trace. (In the kernel
  with branches x/2^k, (qx+1)/2^k the multipliers q = 2^k + 1 do have the -1/2 functional and
  q = 2^k - 1 do not: Proposition 7'.)
* Nothing about 36 survives beyond |D| = 1: 6^a continues as a product of v-values for the maps
  3x + |2^(a+1) - 3^a| but is not triangular.
* "Circuit closes => unit cell" is not provable by the elementary argument (b >= 2 needs
  Steiner/Baker); only checked for a <= 12000.
* "Known cycles sit at (semi)convergents" is not a law in the control family (21.4 % overall,
  about 60 % for cycles that are large relative to c) and does not distinguish 3 from 5.
* "Integer thresholds only in unit cells" is not a reformulation of "no positive cycle"; it is
  only implied by it (Q1.6).
* The "36" in 37 = 36 + 1 = 2^6 - 3^3 is 6 * T_3, attached to the cell (2,1); it is not the
  36 = T_8 of the cell (3,2). The two meet only through 6 * 6 = 36.
* A numerical coincidence seen and discarded: the element -2363 of the 3x+1931 one-even-element
  cycle equals -C(w) for the -17 word (2363 = 17 * 139). Both are sums of the same shape with
  seven odd steps; no mechanism beyond that. Numerology.

## Prior art

* Levi ben Gerson, *De numeris harmonicis* (1342/43), answering Philippe de Vitry: the only
  consecutive harmonic numbers 2^a 3^b are (1,2), (2,3), (3,4), (8,9).
  https://www.proofwiki.org/wiki/Consecutive_Integers_which_are_Powers_of_2_or_3/Historical_Note
* D. Wells, *Curious and Interesting Numbers* (1986): "1, 6, 36 are the smallest triangular
  numbers in geometric sequence" (as quoted by ProofWiki; no uniqueness statement there).
  https://proofwiki.org/wiki/Triangular_Numbers_in_Geometric_Sequence
* J. L. Davison, "Some comments on an iteration problem", Proc. 6th Manitoba Conf. Numer. Math.
  (1976) 155-159: circuits. R. P. Steiner, "A theorem on the Syracuse problem", Proc. 7th
  Manitoba Conf. Numer. Math. (1977): the only circuit in the positive integers is {1, 2}.
  Theorem 5 is the case b = 1 of their circuit equation. A. Rukhin, "A dual-radix approach to
  Steiner's 1-cycle theorem", arXiv:1805.10496 (2018): algebraic proofs, and the 3x-1 side
  (1-cycles (1) and (5,7)) under an extra growth hypothesis. R. P. Steiner, "On the QX+1
  problem, Q odd", Fibonacci Quart. 19 (1981): circuits for q = 5, 7.
* J. L. Simons, B. de Weger, Acta Arith. 117 (2005) 51-70: no m-cycles for m <= 68;
  C. Hercher, J. Integer Seq. 26 (2023): m <= 91; J. L. Simons, Acta Arith. 131 (2008) 217-254
  (generalised Syracuse sequences).
* C. Bohm, G. Sontacchi (1978); J. C. Lagarias, "The set of rational cycles for the 3x+1
  problem", Acta Arith. 56 (1990) 33-53: every word is a rational cycle; primitive cycles of
  3x+k. E. Belaga, M. Mignotte for 3x+d tables.
* L. Halbeisen, N. Hungerbuhler, "Optimal bounds for the length of rational Collatz cycles",
  Acta Arith. 78 (1997) 227-239. Lemma 2 there is Fact L (credited to Lagarias); Lemma 4 is the
  monotonicity of the numerator phi under moving a one to the right, of which Lemma 3 here is
  the exact adjacent case; their Figure 1 draws a parity word as a staircase against the line of
  slope n/l, which is the lattice-path picture of this investigation's working hypothesis. The
  extremal words are Christoffel words (C. Fernandez, S. Ibanez, arXiv:2607.24844, 2026;
  abstract read only).
* R. E. Crandall, Math. Comp. 32 (1978) 1281-1292: the qx+1 problem, including the q = 181
  cycle 27 -> 611; Z. Franco, C. Pomerance, Math. Comp. 64 (1995) 1333-1336. The cycle through 1
  for q = 2^k - 1 is standard in that literature. The five cycles of 5x+1 on Z (through 0, -1,
  1, 13, 17) are standard.
* S. S. Pillai (1945); R. J. Stroeker, R. Tijdeman (1982): the signed equation 3^x - 2^y = c
  has at most one solution for |c| > 13; the repeated values are 1 = 3 - 2 = 9 - 8,
  -5 = 3 - 8 = 27 - 32, -13 = 3 - 16 = 243 - 256. With absolute values the statement is false
  (3^3 - 2^2 = 23 = 2^5 - 3^2), but the second solution lies outside the Collatz range s < k.
* C. Stormer (1897); D. H. Lehmer, Illinois J. Math. 8 (1964); OEIS A002071 (1, 4, 10, 23, 40,
  68, ...), A117581 (2, 9, 81, 4375, 9801, 123201, ...). The superparticular / just-intonation
  reading is already in the A117581 comments and in the Wikipedia article on Stormer's theorem
  (which cites Halsey-Hewitt 1972).
* N. Carey, D. Clampitt, "Aspects of well-formed scales", Music Theory Spectrum 11 (1989):
  scale hierarchy from the continued fraction of log2(3/2).
* P. Mihailescu (2004) for Catalan (not needed here); K. Zsigmondy (1892).
* J. Williams, "A Coordinate System for Collatz Dynamics", arXiv:2607.01718 (2026): odd n written
  as lambda 2^a 3^b - 1 with the flow (a,b) -> (a-1, b+1). This is the v = n+1 coordinate of the
  seed list; it is classical (it underlies Steiner's circuit equation). Abstract read only.
* OEIS A100982 and A186009 (1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, ...): number of
  dropping words per cell (Q1.6).
* T. Oliveira e Silva, "Computational verification of the 5x+1 and 7x+1 conjectures",
  https://sweet.ua.pt/tos/px+1.html (maps T_5, T_7 on positive integers, verified to 10^16;
  credits K. Matthews and E. Roosendaal); OEIS A133421 ff. for the 7x+1 map. These are the
  deterministic multi-divisor maps of Q1.4-c. Their cycles on negative integers were not found
  there.
* This repo, earlier work on the kernel mod p: the half-eigenvalue theorem for branches x/d,
  (qx+1)/d with q = d + 1 (functional delta_(-1/d) - delta_(-1)). Propositions 7 and 7' restate
  and slightly extend it; they are not independent results.
* Collatz-like maps and Pythagorean tuning: J. H. Conway called his Collatz-like permutation
  (2n -> 3n, 4n+-1 -> 3n+-1) the "amusical permutation" because twelve steps multiply by about
  3^12/2^18 and the Pythagorean comma 3^12/2^19 prevents closure (Conway, "On unsettleable
  arithmetical problems", Amer. Math. Monthly 120 (2013); exposition: P. Lynch,
  https://thatsmaths.com/2023/04/06/amusical-permutations-and-unsettleable-problems/). So the
  general link "3^s/2^k is never 1, the comma is the obstruction" is known. Not found in a
  quick search: a published table placing the individual cycles of 3x+1 on Z at named
  intervals. Given how little content that has (see Q1.5), no claim is made. Also not found: the mixed-multiplier semigroup cycles of Q1.4-b, and
  an OEIS entry for the finite list 1, 3, 6, 36.

## Leads not finished

* The 3x+29 map has two cycles of length 65 in the convergent cell (65,41) (D about 4.2e17, so
  g about 1.4e16). A census of accidents in record cells for c <= 1000 would test the
  "likeliest place" heuristic properly.
* Lemma 3 makes C(w) mod p a walk on Z/p with multiplicative steps 3^t 2^j along the
  transposition graph of a cell. That is the same object as the repo's kernel mod p seen
  combinatorially; an exact count of zeros per cell might follow.
* Part D of `q14_stormer.py`: deterministic cycles of multi-divisor maps coming from Stormer
  pairs (e.g. 7x+1 with /2, /3, /5 on negative integers from (2400, 2401)). Curiosity only.
  Observation worth one more look: every cycle of T_5 and of T_7 found on [-2*10^5, 2*10^5] is a
  Stormer-pair cycle (9 of 9), whereas T_11 and T_13 have accidents (4 of 11 cycles); whether
  T_5 and T_7 have any non-Stormer cycle on Z is open as far as this thread knows.
* 37 = 1 + 36 = D(6,3): the cell (6,3) is the tripled unit cell (2,1), and 2^6 = 3^3 mod 37 is
  consistent with "3 = 2^26 mod 37" in the seed list (26 = 2 mod 12). Hand-over to the totient /
  kernel threads, with the caveat of 1.3-f: this 36 is 6 * T_3, not T_8.
* Proposition 7' gives one -1/2 functional per word of a D = -1 unit cell, in a two-branch
  kernel. Whether the full signed kernel of T^3 (eight branches) sees the cell (3,2) beyond the
  inherited eigenvalue (-1/2)^3 was not examined.

## Reproduce

```
cd C:/repos/collatz/scripts/thirty_six/harmonic_cycles
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q11_unit_cells.py          # ~15 s
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q12_why_three.py           # ~10 s
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q13_tiers.py               # ~20 s, run before q15
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q14_stormer.py             # ~6 s
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q15_intervals.py           # ~5 s
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q16_dropping_thresholds.py # ~1 s
```

Each script writes `<name>.log` (human-readable) and `<name>.json` next to itself, and asserts
the facts quoted above. `hc_common.py` holds the shared definitions.

Independent checks (no import from `hc_common.py`; each writes `verify/<name>.log`):

```
cd C:/repos/collatz/scripts/thirty_six/harmonic_cycles/verify
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v1_unit_cells.py   # ~13 s  Q1.1, mirrors and cousins
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v2_why_three.py    # ~30 s  Q1.2, exact kernel tests, Prop. 7'
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v3_tiers.py        # ~6 s   Q1.3, Lyndon census (reads ../q13_tiers.json), S-1
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v4_stormer.py      # ~7 s   Q1.4, T_5 .. T_13
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v5_intervals.py    # ~2 s   Q1.5, size-matched and 5x+1 controls
C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v6_dropping.py     # ~3 s   Q1.6
```

## Skeptic pass

A second reader re-derived every row with separate code (affine composition with Fractions,
Lyndon words by Duval's algorithm, integer-root tests, exact determinants and characteristic
polynomials, direct iteration) and over wider ranges, ran each Collatz-facing statement for 3x-1
and 5x+1, and searched for prior art. The six original scripts were also re-run; their logs and
JSON files reproduce byte for byte.

What was changed in this README.

* *Wording of the headline.* "Exactly one halving" was wrong for the shortcut map (every odd
  step contains a halving); it is now "exactly one even element", and the theorem is credited
  as the b = 1 case of the Davison-Steiner circuit equation. The remark that v * v' = T_v holds
  at every even step of every orbit was added, since it limits what "36 is a product read off
  the cycle" means.
* *1.2-b.* Relabelled as a restatement of the repo's existing half-eigenvalue theorem. The
  sentence presenting "the eigenvalue also appears at the primes dividing q - 3" as a
  confirmed prediction was replaced: the kernel depends on q only modulo p, so that is automatic.
* *1.2-c.* The claim that the cell (3,2) (9 = 8 + 1) leaves no spectral trace was removed. It
  does, in the two-branch kernel (x/8, (9x+C)/8), which is the pair (9,8) already on the repo's
  q = d + 1 list. New Proposition 7': the functional exists exactly for unit cells with D = -1.
* *1.3-a.* "Only D = 5 and 13 are attained twice" now says signed; |D| = 1 is attained twice
  too. The Pillai / Stroeker-Tijdeman citation was mis-stated with absolute values (false:
  |3^x - 2^y| = 23 has two solutions) and was corrected to the signed equation.
* *1.3-a, 1.3-d.* The sentence "3x+5 and 3x+13 are cycle-rich because 5 and 13 are the repeated
  denominators" was deleted. The repetition contributes one cycle each; the count is the
  necklace number of a cell whose |D| is small for its size.
* *1.3-f.* The role of 36 in 37 = 36 + 1 was downgraded: it is 6 * T_3 (cell (2,1)), and the
  general identity is |D(3k,3s)| = 6 T_n + 1. The link to 36 = T_8 is the coincidence 6 * 6.
* *1.4-a.* Marked the "classification" as true by definition; only the counts and the
  finiteness bound are content. "New cells" in 1.4-b was reworded (no novelty is claimed).
* *1.5-b.* Proposition 8 now excludes the cycle {0}, for which it is false.
* *1.5-d.* Split into the trivial size bound (proved) and the record-cell reading (numerology:
  the cell is forced for every s <= 10 and is a record cell for two of the seven).
* *1.5-e.* Added the size-matched control (about 60 %, not 21 %) and the 5x+1 cousin (5 of 5),
  and the statement that the pattern distinguishes neither the sign nor the multiplier.
* *1.6-a.* "Equivalent to no non-trivial positive cycle" was wrong and is now "implied by",
  with the 3x+c counterexamples to the converse argument. Range extended to k <= 24. OEIS
  A186009 added.
* *Zsigmondy.* "The same fact in another costume" was softened to "related".
* *Added.* Rows S-1 (the -17 cycle passes through v = -36, with its base rate), the doubled /
  tripled cell identities, the T_5 / T_7 observation, and prior art: Davison 1976, Halbeisen-
  Hungerbuhler 1997, Rukhin 2018, Conway 2013, Oliveira e Silva, OEIS A186009.

What survived unchanged: Theorems 1, 4, 5, 6, Lemma 3, Propositions 2, 7, 9, 10 (proofs read
line by line; no gap found beyond the two small ones repaired above), the census numbers
(1,465,020 necklaces, five integer cycles, 166 cycles for c <= 199), the circuit search, the
Stormer counts 4, 10, 23, 40, 68 and the unit-cell counts 4, 6, 8, 9, 11, the record-cell
ladder, the 257-cycle control and all of its percentages.

What could not be checked.

* The contents of Steiner 1977, Davison 1976, Steiner 1981, Simons-de Weger 2005, Simons 2008,
  Hercher 2023, Crandall 1978, Franco-Pomerance 1995, Carey-Clampitt 1989, Wells 1986 and
  Conway 2013 were not read; they are cited from bibliographies, abstracts and secondary pages.
  Halbeisen-Hungerbuhler 1997 was read (pages 227-231). Williams 2026 and Fernandez-Ibanez 2026:
  abstracts only.
* Completeness of the Stormer pair lists beyond 10^15 rests on Stormer's theorem; the
  Pell-equation code in `q14_stormer.py` was not re-derived, only its output was matched by
  brute force.
* The count "3054 odd integers receive conflicting multipliers" and the 47,654-word total of
  1.4-b were not recomputed (the cells 4-3 .. 64-65 were, by direct search).
* The determinant tests for p > 61 are zero modulo two 31-bit primes, not exact.
* Whether the negative-side cycles of T_5, T_7 and the mixed-multiplier semigroup cycles are in
  the literature: a quick search found nothing, which is not evidence of novelty.
* Nothing in this thread was tested against, or bears on, the conjecture itself.
