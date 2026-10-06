# Thread 2 — figurate numbers as maps on the 2-adic integers

Part of the "36" investigation (`scripts/thirty_six/`). Date: 2026-10-06.

**Fact under test.** 36 = T_8 = 6^2 = 1^3 + 2^3 + 3^3 = T_3^2: one number, three figurate families.
Dropping classes are unions of residue classes mod 2^k, so "how does a figurate family meet the
dropping classes" is a question about the family as a map Z_2 -> Z_2.

**One-paragraph answer.** The three families behave in three exactly describable ways (fold,
collapse, isometry). Those 2-adic types are facts about polynomials mod 2^k and do not involve any
Collatz rule; most of them are classical (hash-table probing, Rivest, Bumby / Webb-Long). For the
fold and isometry families the dropping-class densities are the natural ones for *every* rule, so
they are blind. For the collapsed families (squares, sums of cubes, s = 0 mod 4) the class law is
**not** blind: squares meet exactly two dropping classes for 3x+1 and infinitely many for 3x-1 and
5x+1 (Theorem 2', found in the skeptic pass). That is a statement about the residue of an odd
square mod 4 and about which cycle passes through 1; it is the repo's Three-Step bit again and
cannot bear on the conjecture. Bitwise NOT conjugates 3x+1 to the shifted 3x-1 map (known) and T_n
is its invariant. T_n = n(n+1)/2 is half the product of the distances from n to the two branch
fixed points 0 and -1, which restates the textbook first-run fact n = c 2^a - 1 -> c 3^a - 1;
every rule has such a law, and for 3x+-1 the quadratic happens to be triangular. The number 36
enters only through the pair (8, 9) = (2^3, 3^2), Catalan's pair: it is the triangular number of
the unit cell 2^3 - 3^2 = -1, whose cycle is the mirror cycle {-5, -7, -10}; the same pair is the
unit cell 2^3 - 9 = -1 of the 9x+1 map, with cycle {-1, -2, -4}. **Nothing here is a step toward
proving the conjecture.**

## Conventions (apply to every table)

- Shortcut (Terras) map `T(n) = n/2` (n even), `(3n+1)/2` (n odd). Generalised rule `(q, d)`:
  `(qn+d)/2` on odd n.
- `k` = Terras stopping time = number of T-steps to the first value below n; `s` = odd steps among them.
- Repo dropping time (`collatz.dropping.dropping_time`, Paper 1) counts un-shortcut steps:
  **dropping time = k + s**, and "Dropping Set_j" is indexed by j = k + s.
  `k = 1, 2, 4, 5, 7, 8, 10, 12, ...` (A020914) <-> `Set_1, 3, 6, 8, 11, 13, 16, 19, ...` (A122437).
- A *class* is the set of residues r mod 2^k with coefficient stopping time exactly k
  (first k with 3^s < 2^k along the parity vector). `N(k)` = number of such residues;
  `N = 1, 1, 1, 2, 3, 7, 12, 30, 85, ...` = OEIS A100982 with the class "even" prepended.
  Natural density of the class is `N(k)/2^k`.
- Class versus actual stopping time. If r is the least non-negative residue of a class of level k,
  then for n = r + 2^k t one has T^k(n) - n = (T^k(r) - r) - (2^k - 3^s) t and T^j(n) > n for j < k,
  so every member n >= r has Terras stopping time exactly k as soon as T^k(r) < r. This was checked
  for the least residue of all 81119 classes with k <= 24 (`verify/v8`): the only failures are r = 0
  and r = 1. So for classes of level k <= 24 "class = stopping time" is a theorem for every n >= 2.
  For all k it is Terras's Coefficient Stopping Time conjecture (Lagarias 1985, section 2: open,
  "nearly true" by his Theorem E, and it would imply that there are no non-trivial cycles). It is
  not a known fact and the scripts do not assume it: each counts the exceptions it meets (only the
  values 0 and 1).
- `NOT(x) = -1 - x`. Coordinates: `v = n+1`, `u = 2n+1`, `t = T_n = n(n+1)/2 = (u^2-1)/8`.
- Paper 1 dropping orbit includes n and excludes the destination; Paper 2 stopping orbit excludes n
  and includes it. Only `q25` prints orbits, and it labels both.

## Files

| Script | Output | Covers |
|---|---|---|
| `common.py` | — | conventions, `stop`, `cst`, `class_table` |
| `q21_figurate_residues.py` | `.log`, `.json` | Q2.1: T_n, n^2, n^3, T_n^2 mod 2^k; exact class counts; repo check at 2^16; n < 2^20 and n <= 10^6; rules 3x-1, 5x+-1, 7x+1 |
| `q22_polygonal.py` | `.log`, `.json` | Q2.2: polygonal families s = 3..34, trichotomy, class densities, other figurate families |
| `q23_pell.py` | `.log`, `.json` | Q2.3: square-triangular Pell orbit: identities, periods, closures, classes, null test, Ljunggren check |
| `q24_mirror.py` | `.log`, `.json` | Q2.4: NOT conjugacy, cycles of T on Z in five coordinates, unit cells, 3x+d cycle census |
| `q25_thirty_six.py` | `.log`, `.json` | Q2.5: 36, 35, 8, 17, 6, 37, 9 in the repo's vocabulary |
| `q26_joint_index_value.py` | `.log`, `.json` | beyond the seed: joint law of class(n) and class(T_n); first-run law |

Run any of them with `C:/repos/collatz/.venv/Scripts/python.exe -X utf8 <script>`. Each finishes in
under 20 s. Logs are deterministic (fixed seeds), so a re-run can be diffed against the saved `.log`
apart from the final timing line.

Independent re-checks (skeptic pass, separate code paths, none imports `common.py`), in `verify/`:

| Script | Output | Covers |
|---|---|---|
| `verify/v1_residues_classes.py` | `.log`, `.json` | Q2.1: CRS and fibres k <= 24, windows, N(k) by word DP against A100982, class counts of eight families for five rules, actual integers n < 2^21, squares as seeds of 3x-1 |
| `verify/v2_polygonal_and_cubic.py` | `.log`, `.json` | Q2.2: trichotomy for s = -7..40 from k = 1, CRS criterion, integral reflections, proofs-by-enumeration for the cubic families, matched families F_q |
| `verify/v3_pell.py` | `.log`, `.json` | Q2.3: sequences from Pell numbers, isometry on all pairs with negative indices, true minimal periods k <= 20, closures, classes along the orbit for 3x+1, 3x-1, 5x+1, Ljunggren and 3-smooth checks to j = 5000 |
| `verify/v4_mirror_cycles.py` | `.log`, `.json` | Q2.4, Q2.5: NOT identities, cycles from abs(n) <= 10^6, the unit-cell dictionary for q = 3, 5, 7, 9, 15, 17, anti-diagonal family j <= 80, two-run cycles, census recount, controls for the orbit of 36 |
| `verify/v5_first_run_and_information.py` | `.log`, `.json` | X-1 for seven rules and negative n, X-2 for K = 8..20, the two parabolas |
| `verify/v6_null_calibration.py`, `verify/v6b_rank_test.py` | `.log`, `.json` | Q2.3-f: calibration of the z statistic and a rank test against 300 controls |
| `verify/v7_squares_see_the_sign.py` | `.log`, `.json` | Theorem 2': the two-class law of squares depends on the rule and on the sign |
| `verify/v8_class_equals_stopping_time.py` | `.log`, `.json` | class level = Terras stopping time for every n >= 2 in a class with k <= 24 |

`v3` takes about 50 s; the others under 20 s.

## Results

Status labels: proved / computed / conjecture / null / prior art / numerology. "Mirror" answers the
mirror test: does the statement distinguish 3x+1 from 3x-1 and from 5x+1?

| ID | Statement | Status | Mirror | Role of 36 |
|---|---|---|---|---|
| Q2.1-a | T_0..T_(2^k-1) is a complete residue system mod 2^k for every k. On Z_2, n -> T_n is onto and exactly 2-to-1 with fibres {n, NOT n} (Thm 1). A window [a, a+2^k) is a CRS iff 2^k divides a, so the count must start at T_0 = 0. | prior art (triangular probing: Hopgood-Davenport 1972; Knuth 6.4 ex. 20); proof given | rule-free | none: property of the whole family |
| Q2.1-b | Among the first 2^K triangular numbers exactly `N(k) 2^(K-k)` lie in the class of level k, for every k <= K (Cor 1). As Terras stopping times of actual integers this holds for every K and every k <= 24, apart from T_0 = 0 and T_1 = 1 (least-residue check, `verify/v8`); for all k it would need Terras's CST conjecture. N(k) and its reading as the frequency of a dropping time are OEIS A100982. | proved (residues; integers for k <= 24); prior art for N(k) | blind: identical for 3x-1, 5x+-1, 7x+1 (computed) | none |
| Q2.1-c | Squares: n -> n^2 has image of Haar measure 1/6; odd squares are exactly 1 + 8Z_2, each residue hit 4 times (rule-free, classical). **For 3x+1** every square > 1 is in Set_1 (even) or Set_3 (odd): densities 1/2, 1/2 (Thm 2). | proved | collapse: rule-free. Two-class law: **not blind.** True for 3x+1 and 7x+1; for 3x-1 the odd squares spread over infinitely many classes (103 distinct stopping times for n <= 2*10^5), likewise 5x+-1 (Thm 2') | 36 is an even square, so Set_1 like every even number |
| Q2.1-d | Cubes: x -> x^3 is an isometry of Z_2^x (classical: 3 is prime to the order of the unit group); class counts of n^3 over n mod 2^K are exactly natural (Thm 2). | proved; classical | blind (natural for 3x-1, 5x+-1, 7x+1, computed) | none |
| Q2.1-e | Sums of cubes T_n^2: fold then collapse; for 3x+1 only Set_1 and Set_3, 1/2 each. | proved | as Q2.1-c: two classes for 3x+1, many for 3x-1 and 5x+1 | 36 = T_3^2 is in Set_1 |
| Q2.2-a | Polygonal trichotomy by v_2(s-2): 0 -> free 2-to-1 fold, Haar-preserving; 1 -> affine image of squaring (image measure 1/6); >= 2 -> isometric bijection (Thm 3). Checked s = 3..34, k <= 14, and independently s = -7..40, k = 1..11. | proved (elementary; no source found for the trichotomy as a whole); Rivest 2001 covers the bijection case | rule-free | none |
| Q2.2-b | Class densities: natural `N(k)/2^k` for s odd and s = 2 mod 4, for every rule. For s = 0 mod 4 and the rule 3x+1: (1/2, 1/2) on Set_1, Set_3 and nothing else. | proved (residues), computed (n <= 10^6) | fold and isometry families: blind. s = 0 mod 4: **not blind**, two classes only where 1 mod 4 is a single class (3x+1), 5 to 9 classes at level 16 for 3x-1, 5x+1 | none |
| Q2.2-c | For odd s the first 2^k terms are a CRS mod 2^k iff s = 3 mod 2^k; for all k iff s = 3. The first failing k is v_2(s-3) + 1 (so pentagonal numbers already fail mod 4). | proved | rule-free | none |
| Q2.2-d | The reflection of the s-gonal family, x -> (s-4)/(s-2) - x, maps Z to Z iff s = 3 or 4; centres -1/2 and 0. "Triangular and square" is the meeting of the two polygonal families with an integral symmetry, not of "most uniform" and "most collapsed" (Thm 3, remark). | proved | the centre -1/2 belongs to every dilation x -> qx + (q-1)/2 (3x+1, 7x+3, 11x+5, ...), not to the multiplier 3; for d = +-1 it forces q = 3; it does not see the sign | none: about s = 3, 4 |
| Q2.2-e | Other figurate families: octahedral and stella octangula numbers are isometries of Z_2; square pyramidal numbers are uniformly 2-to-1 (one even and one odd preimage, but not along NOT: f(-1-n) = -f(n)); tetrahedral numbers have multiplicity 5 on 4Z_2 and 1 elsewhere; pronic, centred square, centred hexagonal, centred cube are not onto (Thm 8). | proved (skeptic pass); checked k <= 14 | rule-free | none |
| Q2.3-a | j -> m_j (A001109, roots of square-triangular numbers) satisfies v_2(m_i - m_j) = v_2(i - j): a 2-adic isometry in j; one period 0 <= j < 2^k is a permutation of Z/2^k (Thm 4). | prior art: exactly the Bumby / Webb-Long 1975 criterion (a = 6 = 2 mod 4, b = -1 = 3 mod 4, initial terms of opposite parity), which gives "each residue mod 2^e exactly once per period 2^e"; proof given | not Collatz-facing | none |
| Q2.3-b | Minimal periods mod 2^k: m: 2^k; N = m^2: 2^(k-1) (k >= 2); u: 2^(k-3) (k >= 5); n: 2^(k-2) (k >= 4). | proved (corollary of Q2.3-a), computed k <= 20 (as true minimal periods, not only powers of two, for k <= 11) | not Collatz-facing | none |
| Q2.3-c | The Pell orbit is not thin. closure{N_j} = all 2-adic squares, with exactly the multiplicities of x^2. closure{n_j} = {n = 0 mod 8 or 1 mod 16 : T_n is a 2-adic square}, Haar measure 1/12; with NOT it is the whole solution set (measure 1/6). | proved, computed k <= 18 | sign-blind (NOT-symmetric by construction) | none |
| Q2.3-d | Along the orbit, **for 3x+1**: N_j and n_j alternate Set_1 (j even) / Set_3 (j odd); u_j alternates Set_3 / Set_6; the roots m_j carry exactly the natural law. | proved, computed j <= 600 | **not blind.** For 3x-1 the odd-j terms of N_j, n_j and the even-j terms of u_j spread over 31 to 48 distinct stopping times (j <= 600); for 5x+1 over 20 to 26. Only m_j is blind | 36 = N_2 is "j even" |
| Q2.3-e | n_(j+-1) = (3 n_j + 1) +- 4 m_j, so 3n_j + 1 is the midpoint of the neighbouring indices. | proved (a Chebyshev identity) | blind: the same identity holds with qn+1 for every odd q, and with 3n-1 | pair (8,9): trace 6 = 2*3 and 3^2 - 8 = 1 |
| Q2.3-f | Total stopping times of u_j, n_j, m_j, N_j versus matched random integers: mean z within 1.5 standard errors of 0 in three runs; rank test against 300 controls: KS p = 0.47 (u_j), 0.62 (n_j). | null | — | none |
| Q2.3-g | No relation to the repo's Pythagorean lifts: their discriminant for the cell (k, s) is 4^k + 9^s (odd), never 2*square, so the field is never Q(sqrt 2). (2, 1) is the only cell with a square discriminant, for all k, s. | null (proved) | — | none |
| Q2.3-h | The only triangular numbers whose square is triangular are 0, 1, 6; so 36 is the only sum of the first n cubes (n > 1) that is triangular. Also N_j is 3-smooth only for j = 1, 2 (N = 1, 36). | prior art (Ljunggren 1946, Cassels 1965); the 3-smooth statement is proved (corollary of Levi ben Gerson) | not Collatz-facing | 36 is genuinely unique here |
| Q2.4-a | NOT commutes with x -> 3x+1 and with no halving; NOT T NOT = (m -> 3m/2 if m even, (m-1)/2 if m odd), which is 3x-1 in the coordinate m+1. | prior art (negation conjugates 3x+1 to 3x-1; V(x) = -1-x is in Bernstein-Lagarias 1996, Monks-Yazinski 2004) | this is the mirror | none |
| Q2.4-b | A function on Z_2 is NOT-invariant iff it is a function of T_n. The odd step descends to t -> 9t + 1; halving does not descend (Thm 5). | proved (immediate from Q2.1-a); 9T+1 triangular is classical | forced sign-blind | none: every T_n labels the pair {n, -n-1}; "36 labels {8, -9}" is that tautology |
| Q2.4-c | Unit cells abs(2^k - 3^s) = 1 are (1,0), (1,1), (2,1), (3,2) <-> pairs (1,2), (2,3), (3,4), (8,9) <-> T = 1, 3, 6, 36 <-> cycles {0}, {-1}, {1,2}, {-5,-7,-10}. Every **known** cycle of T on Z except the one through -17 is of this kind (that there are no others is open). | prior art (Levi ben Gerson; Steiner 1977; Lagarias) | sign-aware, but generic: every qx+1 has the same dictionary (5x+1: (4,5), T_4 = 10, {-1,-2}; 7x+1: (7,8), T_7 = 28, {1,2,4}; 9x+1: (8,9), T_8 = 36, {-1,-2,-4}) | 36 <-> cell (3,2) <-> the mirror cycle; really Catalan's pair (8,9), which is also a unit cell of 9x+1 |
| Q2.4-d | In v = n+1 a run of j odd steps walks the anti-diagonal {2^j, 2^(j-1)3, ..., 3^j} of the 3-smooth lattice (times an odd c). The anti-diagonal alone is a cycle iff 3^j + 1 = 2^(j+1) (Collatz: j = 0, 1) or 3^j - 1 = 2^(j+1) (mirror: j = 2). General family: word 1^j 0 is a cycle of 3x + (2^(j+1) - 3^j) with minimum 3^j - 2^j. | prior art in substance (Steiner's circuits; Lagarias's 3x+k cycles); proof given, checked j <= 80 | sign-aware | pair (8,9) gives j = 2 |
| Q2.4-e | 17 = 2^4 + 1: the 17-cycle is two runs, c1 = 139/139 = 1, c2 = 695/139 = 5. No mechanism found. Size-matched base rate for "v0 is a power of two" among primitive 3x+d cycles with abs(v0) <= 16 is 5 of 9 (chance 0.50). | numerology | — | none |
| Q2.4-f | 36 = 2^2 3^2 is the midpoint of anti-diagonal 4, which is the first run of the mirror 11-cycle (16, 24, 36, 54, 81, 40, 60, 90, 135, 67, 33); equivalently 37 lies on the 3x-1 cycle of 17. Under 3x+1 the same lattice point (n = 35) falls to 1. | computed | sign-aware, but shared by 16, 24, 54, 81 | the point (2,2) on an anti-diagonal whose corner (4,0) is what matters |
| Q2.5-a | 36, 8, 6 in Set_1; 17, 37, 9 in Set_3; 35 in Set_6. orbit(36) = [36, 18] + orbit(9). orbit(36) meets 17 and 8: every orbit from n >= 3, n != 4 meets 8, and 44 to 46% meet 17. | computed; nothing | — | none |
| X-1 | First-run law: the first run of the parity vector of n has length v_2(n) + v_2(n+1) = v_2(T_n) + 1 (Thm 6). | prior art (the textbook step n = c 2^a - 1 -> c 3^a - 1, written with T_n) | every rule (q, d) has the law with n((q-2)n + d)/2 (checked for 3x+-1, 5x+-1, 7x+1, 7x+3, 9x+1); only the integrality of the fixed point -d/(q-2) is special to 3x+-1; not sign-aware | none |
| X-2 | For 3x+1, class(n) and class(T_n) share exactly 1/2 bit of mutual information under natural density (Thm 7). | proved (elementary), computed K = 8..20 | 3x-1 with T_(n-1): 1/2 at every K; 5x+-1 with their matched families: 0.266, 0.324 at K = 16 (these drift in the fourth decimal with K) | none |
| T2' | Squares, sums of cubes and the polygonal families with s = 4 mod 8 meet exactly two dropping classes of the rule (q, d) iff the parity word of the integer 1 drops within three letters, i.e. iff q = 3 and d = 1 mod 4, or q in {5, 7} and q + d = 0 mod 8. Otherwise their odd values carry the class law of the ball 1 + 8Z_2 and meet infinitely many classes. Mirror form: n^2 under 3x+1 <-> -n^2 under 3x-1 (Thm 2'). | proved (skeptic pass); computed on a grid of 480 rules | **sign-aware** for d = +-1, through d mod 4 only: this is the repo's Three-Step bit, so it is residue-only and cannot bear on the conjecture | none |

## Proofs

Notation: `|x|` is the 2-adic absolute value, `v_2` the valuation, "Haar" the uniform probability
measure on Z_2.

### Theorem 1 (triangular numbers are a free fold along NOT). *Q2.1-a*

For every k >= 0 the map Z/2^(k+1) -> Z/2^k, n -> T_n, is well defined, onto and exactly 2-to-1,
with fibres {n, NOT n}. The window 0 <= n < 2^k is a complete residue system mod 2^k.

*Proof.* T_a - T_b = (a-b)(a+b+1)/2. The two factors a-b and a+b+1 have opposite parity, so
T_a = T_b mod 2^k iff 2^(k+1) divides one of them, i.e. iff a = b or a = -1-b mod 2^(k+1). Taking
b = a + 2^(k+1) shows the map is well defined mod 2^(k+1). NOT has no fixed point mod 2 (it flips
parity), so every fibre has exactly two elements and the 2^(k+1) inputs cover 2^k outputs. For
0 <= a, b < 2^k: abs(a-b) < 2^k and 0 < a+b+1 < 2^(k+1), so neither factor is divisible by 2^(k+1)
unless a = b. ∎

Passing to the limit: T: Z_2 -> Z_2 is onto, 2-to-1, T(NOT n) = T(n), and pushes Haar to Haar. On
each parity class it doubles 2-adic distances, v_2(T_a - T_b) = v_2(a - b) - 1 for a = b mod 2:
T_(2m) = m(2m+1) and T_(2x-1) = x(2x-1) are isometries in m and x (Theorem 3, third case). In the
coordinate u = 2n+1 the fold is u -> -u and T = (u^2 - 1)/8.

*Remark (the window matters).* The same argument shows that 2^k consecutive indices
a, ..., a + 2^k - 1 give a complete residue system mod 2^k iff 2^k divides a: the sums x + y of two
distinct elements cover every odd residue mod 2^(k+1) except 2a - 1, and the fibre condition is
x + y = -1. So "the first 2^k triangular numbers" must be counted from T_0 = 0; T_1, ..., T_8 mod 8
are 1, 3, 6, 2, 7, 5, 4, 4. (Checked for k = 1..9 and every start a with abs(a) <= 2^(k+1),
`verify/v1`.)

*Prior art.* This is the reason triangular (quadratic) probing visits every slot of a hash table
whose size is a power of two. Nothing here is new.

**Corollary 1 (exact class counts).** *Q2.1-b.* For K >= 1 and k <= K,
`#{0 <= n < 2^K : T_n mod 2^K in class k} = N(k) 2^(K-k)`: the first 2^K triangular numbers contain
each residue once. With A100982: 2^(K-1) in Set_1, 2^(K-2) in Set_3, 2^(K-4) in Set_6,
2*2^(K-5) in Set_8, 3*2^(K-7) in Set_11, 7*2^(K-8) in Set_13, 12*2^(K-10) in Set_16, ...
This is a statement about residues. For actual Terras stopping times it holds for every K and every
k <= 24, apart from the two values T_0 = 0 and T_1 = 1, by the least-residue check described under
Conventions; for larger k it rests on Terras's Coefficient Stopping Time conjecture. Verified
through the repo's `dropping_time` for K = 16 (all classes of modulus <= 2^16), with `common.stop`
for K = 20, and independently for K = 21 (`verify/v1`).

### Theorem 2 (squares collapse, cubes are rigid). *Q2.1-c, d, e*

(a) Squaring maps Z_2^x onto 1 + 8Z_2, 2-to-1 (kernel {+1, -1}); 1 + 8Z_2 is the index-4 subgroup of
Z_2^x. The image of Z_2 under squaring is {0} with the union over i >= 0 of 4^i (1 + 8Z_2), of Haar
measure sum 4^(-i)/8 = 1/6. (b) x -> x^3 is an isometry of Z_2^x. (c) Every odd square, and every
odd value of T_n^2, is 1 mod 8, hence 1 mod 4, hence **for the rule 3x+1** of Terras time 2 (Set_3)
unless it equals 1. Parts (a) and (b) are classical and involve no rule; part (c) is a statement
about 3x+1 and fails for 3x-1 (Theorem 2').

*Proof.* (a) For odd w, w' the even numbers w - w' and w + w' sum to 2w = 2 mod 4, so exactly one
of them is 2 mod 4. If w = w' mod 4 this gives v_2(w^2 - w'^2) = v_2(w - w') + 1. Hence squaring is
injective from the 2^(k-2) classes {w mod 2^k : w = 1 mod 4} into the 2^(k-2) classes
{y mod 2^(k+1) : y = 1 mod 8}, so bijective at every level: it maps 1 + 4Z_2 one-to-one onto
1 + 8Z_2. Since Z_2^x = {+1, -1} x (1 + 4Z_2) the claim on units follows; an even x = 2^i w gives
x^2 = 4^i w^2. (b) For odd
a, b: a^3 - b^3 = (a-b)(a^2 + ab + b^2) and a^2 + ab + b^2 is odd. (c) n = 1 mod 4 gives
(3n+1)/2 even and (3n+1)/4 < n. ∎

Consequences: n^3 over a full residue system mod 2^K has exactly the natural class counts, for
every rule (odd cubes permute the odd residues; even cubes are even, and all even numbers are one
class). For 3x+1, n^2 and T_n^2 meet only Set_1 and Set_3, half each (T_n is odd for n = 1, 2 mod 4).
The number of squares mod 2^k is `(2^(k-1) + 4)/3` (k even) or `(2^(k-1) + 5)/3` (k odd), OEIS
A023105; checked k <= 24.

So the owner's guess is right in all three cases, with one sharpening: "collapse onto an index-4
subgroup" is the statement on units; on all of Z_2 the image has measure 1/6.

### Theorem 2' (the two-class law of squares depends on the rule, and on the sign). *T2'*

Let the rule be T(n) = n/2 or (qn + d)/2 with q >= 3 and d both odd. The odd squares are dense in
the ball B = 1 + 8Z_2 and equidistributed on it (each residue 1 mod 8 mod 2^k is hit 4 times).
Then:

1. The odd squares lie in a single dropping class iff B does, iff the parity word of B (its first
   three letters are those of the integer 1) drops within three letters, iff
   **q = 3 and d = 1 mod 4** (word 10, since 3 < 4; class 1 mod 4) or
   **q in {5, 7} and q + d = 0 mod 8** (word 100, since q < 8; class 1 mod 8).
   Among the rules qx +- 1 these are exactly 3x+1 (1 -> 2 -> 1) and 7x+1 (1 -> 4 -> 2 -> 1): the
   rules for which 1 sits on a short contracting cycle.
2. In every other case the class law of the odd squares is the class law of Haar measure on B,
   which charges infinitely many classes. For 3x-1 the integer 1 is a fixed point with the
   expanding word 111..., so an odd square x starts with exactly v_2(x - 1) >= 3 odd steps.
3. Mirror form: the stopping time of n^2 under 3x+1 equals that of -n^2 under 3x-1 (in absolute
   value), and the stopping time of n^2 under 3x-1 equals that of -n^2 under 3x+1. The two-class
   family of the mirror map is the negatives of the squares, which are -1 mod 8.

*Proof.* (1) A class of level k is a union of residue classes mod 2^k, and two elements of B that
differ mod 2^k have different words of length k. If B were inside a class of level k > 3, every
extension of the three-letter prefix of B would have to drop exactly at step k; the extension by
ones never drops (q > 2), so k <= 3. The first letter is 1. A drop at k = 2 needs the word 10 and
q < 4; the second letter is 0 on B iff q + d = 0 mod 4. A drop at k = 3 needs q^s < 8, so s = 1,
the word 100, q in {3, 5, 7} and qn + d = 0 mod 8 on B, i.e. q + d = 0 mod 8 (for q = 3 that is a
sub-case of the first). (2) Equidistribution on B gives the law. If B is not inside one class it
contains a residue class whose word has not dropped; such a word stays undropped when extended by
ones and drops once enough zeros are appended after that, so classes of arbitrarily high level are
met. For 3x-1, v = n - 1 is multiplied by 3/2 at each odd step (Theorem 6 with the fixed point +1).
(3) T_(3x-1)(y) = -T_(3x+1)(-y). ∎

Computed (`verify/v1`, `verify/v7`): the criterion holds for all 480 rules with q = 3..31 odd,
d = -31..31 odd (level K = 12); class counts of odd squares mod 2^18 equal 4 times those of the
residues 1 mod 8 for seven rules; as seeds of 3x-1 the squares n^2, 2 <= n <= 2*10^5, show 103 distinct Terras stopping
times (most common: 5, 8, 7, 10), against exactly two for 3x+1. The same holds for T_n^2 and for
the polygonal families with s = 4 mod 8, whose odd values are also dense in B. For s = 0 mod 8
(octagonal, ...) the odd values are 1 mod 4 but fall in both 1 and 5 mod 8, so they lie in a single
class only for q = 3, d = 1 mod 4 (computed: 2 classes for 3x+1; 8, 5, 5 determined classes at
level 16 for 3x-1, 5x+1, 7x+1).

Reading. This is the one place in the thread where a dropping-class statement about a figurate
family tells 3x+1 from 3x-1. It does so through a single bit: an odd square is 1 mod 4 and never
-1 mod 4, and the class 1 mod 4 belongs to 3x+1 while 3 mod 4 belongs to 3x-1. That is the repo's
Three-Step Theorem (`scripts/mirror_screen/README.md`) seen through squares. It is a residue
statement and says nothing about the conjecture.

### Theorem 3 (polygonal trichotomy). *Q2.2*

Write a = s - 2, so P_s(n) = n + a n(n-1)/2 and
`P_s(x) - P_s(y) = (x - y)(2 + a(x + y - 1))/2`. Let `iota_s(x) = (s-4)/(s-2) - x` (the reflection
with P_s o iota_s = P_s over Q).

1. **a odd (s = 3, 5, 7, ...): free fold.** Z/2^(k+1) -> Z/2^k is onto and exactly 2-to-1 with
   fibres {x, iota_s(x)}; P_s pushes Haar to Haar.
2. **a = 2 mod 4 (s = 4, 8, 12, ...): ramified fold.** P_s(n) = b(n + c)^2 - b c^2 with b = a/2 odd
   and c = (1-b)/(2b) in Z_2: an affine isometry applied to squaring. Image measure 1/6; the number
   of values mod 2^k equals the number of squares mod 2^k; every odd value is 1 mod 4.
3. **a = 0 mod 4 (s = 6, 10, 14, ...): isometry.** abs(P_s(x) - P_s(y)) = abs(x - y); P_s permutes
   Z/2^k for every k.

*Proof.* (1) Exactly one of x - y and 2 + a(x+y-1) is even (if x - y is even then x + y - 1 is odd
and 2 + odd is odd; if x - y is odd then a(x+y-1) is even). So P_s(x) = P_s(y) mod 2^k iff
x = y mod 2^(k+1) or a(x + y - 1) = -2 mod 2^(k+1), i.e. y = iota_s(x) mod 2^(k+1) (a is invertible).
iota_s flips parity, so it has no fixed point and fibres have exactly two elements. (2) Direct
expansion; c is a 2-adic integer because (1-b)/2 is an integer and b is a unit. For odd n,
P_s(n) - 1 = (n-1)(bn+1) is a product of two even numbers. (3) Here P_s(n) = b n^2 + (1-b) n with b
even, and P_s(x) - P_s(y) = (x-y)(b(x+y) + 1 - b) with an odd second factor. This is also Rivest's
criterion (a_1 odd, a_2 + a_4 + ... even, a_3 + a_5 + ... even). ∎

*Class densities (Q2.2-b).* Cases 1 and 3: every class has its natural density N(k)/2^k, exactly
over one period (2^(K+1) terms in case 1, 2^K in case 3), for every rule. Case 2, for the rule
3x+1: Set_1 and Set_3 with density 1/2 each, all other classes empty; for other rules see Theorem
2' (not two classes for 3x-1 or 5x+-1). Checked at residue level for K = 16 (exact) and on actual
integers for n <= 10^6, s = 3..14 (largest deviation of a class frequency from its density, over
all classes with k <= 16: 2.5*10^-5; the collapsed families give 500000 / 499999 / 0).

*Initial segments (Q2.2-c).* For odd s, [0, 2^k) is a fundamental domain for iota_s mod 2^(k+1) iff
no two of its elements sum to (s-4)/(s-2) mod 2^(k+1); the sums of two distinct elements cover
every odd residue except 2^(k+1) - 1, so the condition is (s-4)/(s-2) = -1, i.e. s = 3 mod 2^k. For
all k this forces s = 3, and for s != 3 the first failing k is v_2(s-3) + 1: s = 5, 9, 13 at k = 2
(pentagonal numbers 0, 1, 5, 12 are 0, 1, 1, 0 mod 4), s = 7 at k = 3, s = 11, 27 at k = 4,
s = 19 at k = 5, s = 35 at k = 6 (`verify/v2`, tested from k = 1).

*Remark (Q2.2-d): is 36 the meeting of the most uniform and the most collapsed family?* Not in
that form. Hexagonal numbers (and every s = 2 mod 4) are strictly more rigid than triangular ones,
and every s = 0 mod 4 collapses exactly as much as the squares. The true statement is: the
reflection iota_s maps Z to Z iff (s-2) divides 2, i.e. iff s = 3 or s = 4. Its centre
(s-4)/(2(s-2)) is -1/2 for triangular numbers and 0 for squares, the fixed points of x -> 3x+1 and
of x -> 3x. For a rule qx + d the reflection through the centre -d/(q-1) is integral iff (q-1)
divides 2d, i.e. iff q = 2d' + 1 with d' a divisor of d: true for 3x + d (every odd d), 7x+-3,
11x+-5, 7x+-9, ..., false for 5x+-1, 7x+1, 9x+1. The centre is -1/2 exactly for the dilations
x -> qx + (q-1)/2, and NOT commutes with all of them (7x+3 as much as 3x+1). So the tie is to the
fixed point -1/2, not to the multiplier 3; only among the rules qx+-1 does it single out q = 3.
It does not see the sign of d.

### Theorem 4 (the Pell orbit of square-triangular numbers). *Q2.3*

Let eps = 3 + sqrt 8, eps^j = u_j + m_j sqrt 8, n_j = (u_j - 1)/2, N_j = m_j^2 = T_(n_j).

(a) `m_i - m_j = 2 m_((i-j)/2) u_((i+j)/2)` for i = j mod 2, and `v_2(m_i - m_j) = v_2(i - j)` for
all integers i != j. Hence j -> m_j extends to an isometry of Z_2, and m_0, ..., m_(2^k - 1) is a
permutation of Z/2^k.

(b) `u_(j+P) - u_j = 16 m_(P/2) m_(j+P/2)` (P even) and `N_(j+P) - N_j = m_P m_(2j+P)`. Minimal
periods mod 2^k: m: 2^k; N: 2 for k = 1 and 2^(k-1) for k >= 2; u: 1, 2, 2, 2 for k = 1..4 and
2^(k-3) for k >= 5; n: 2, 2, 2 for k = 1..3 and 2^(k-2) for k >= 4.

(c) closure{N_j} is the set of all 2-adic squares, and for each k the multiset
{N_j mod 2^k : 0 <= j < 2^k} equals {x^2 mod 2^k : 0 <= x < 2^k}. closure{n_j} is
{n : n = 0 or 1 mod 8 and T_n is a 2-adic square}, of Haar measure 1/12; its NOT-image is the rest
of {n : T_n is a 2-adic square} (measure 1/6). More precisely n_j = 0 mod 8 for j even and
1 mod 16 for j odd, and the whole solution set lies in n = 0, 7 mod 8 and n = 1, 14 mod 16.

(d) For the rule 3x+1 and j >= 2: N_j and n_j are in Set_1 for j even and Set_3 for j odd; u_j is
in Set_3 for j even and Set_6 for j odd. The roots m_j have exactly the natural class counts over
0 <= j < 2^K, for every rule.

(e) `n_(j+1) = (3 n_j + 1) + 4 m_j` and `n_(j-1) = (3 n_j + 1) - 4 m_j`.

*Attribution of (a).* The permutation statement is a special case of the theorem of Bumby and of
Webb and Long (1975): a recurrence w_(n+2) = a w_(n+1) + b w_n is uniformly distributed mod 2^e
(e >= 2) iff a = 2 mod 4, b = 3 mod 4 and w_0, w_1 have opposite parity, and then every residue
mod 2^e appears exactly once in a least period 2^e (statement as in Somer and Krizek, Integers 25
(2025) A1, Theorem 2.3(iv)). Here a = 6, b = -1, (w_0, w_1) = (0, 1). "Every residue once in each
period 2^e, for all e" is the same as v_2(m_i - m_j) = v_2(i - j), so (a) is known; the proof
below is kept because it is three lines. v_2(m_j) = v_2(j) is the standard valuation law for the
Pell numbers, m_j = P_(2j)/2.

*Proof.* (a) eps^(-t) = u_t - m_t sqrt 8. With A = (i-j)/2, B = (i+j)/2:
eps^i - eps^(-i) - eps^j + eps^(-j) = (eps^A - eps^(-A))(eps^B + eps^(-B)) = (2 m_A sqrt 8)(2 u_B);
divide by 2 sqrt 8. All u are odd (u^2 = 1 + 8m^2). From m_(t+1) = u_t + 3 m_t, m_t = t mod 2. Taking
j = 0 gives m_(2A) = 2 m_A u_A, so v_2(m_t) = v_2(t) by induction. Therefore, for i = j mod 2,
v_2(m_i - m_j) = 1 + v_2((i-j)/2) = v_2(i-j), and for i != j mod 2 the difference is odd.
(b) The same product formulas for cosh and for sinh^2:
eps^(j+P) + eps^(-j-P) - eps^j - eps^(-j) = (eps^(P/2) - eps^(-P/2))(eps^(j+P/2) - eps^(-j-P/2)),
and m_a^2 - m_b^2 = m_(a-b) m_(a+b). With (a): v_2(u_(j+2^e) - u_j) = e + 3 + v_2(j + 2^(e-1)), whose
minimum over j is e + 3 for e >= 2 and 4 for e = 1; v_2(N_(j+2^e) - N_j) = e + v_2(2j + 2^e), minimum
e + 1 for e >= 1. The period of n mod 2^k is that of u mod 2^(k+1). (c) By (a) the m_j are dense in
Z_2 and equidistributed mod 2^k over one period, so N_j = m_j^2 inherits everything from squaring.
The map a + b sqrt 8 -> a is a ring homomorphism Z[sqrt 8] -> Z/8, so u_j = 3^j mod 8: u_j is the
square root of 1 + 8 m_j^2 that is 1 mod 4 when m_j is even and 3 mod 4 when m_j is odd. As m runs
over Z_2 this gives a closed set W of u with W and -W disjoint (W lies in {1 mod 16} and
{3 mod 32}) and W together with -W equal to {u : (u^2-1)/8 is a square}. In n = (u-1)/2, W is the
part with n = 0, 1 mod 8 and -W = NOT(W). T pushes Haar to Haar (Theorem 1) and squares have measure
1/6, so the full set has measure 1/6 and each half 1/12. (d) n_(2i) = 8 m_i^2 is even;
n_(2i+1) = (u_i + 4 m_i)^2 is an odd square; N_j = m_j^2 with m_j = j mod 2; u_(2i) = 1 + 16 m_i^2
is 1 mod 16 and u_(2i+1) = 3 u_(2i) + 8 m_(2i) is 3 mod 16, and the class of 3 mod 16 is k = 4. The
statement for m_j is (a). (e) u_(j+-1) = 3 u_j +- 8 m_j and n = (u-1)/2. ∎

Reading. The orbit neither equidistributes over dropping classes nor lives on a thin set: it is as
dense as it can be given that its points are squares (N), squares or twice squares (n), or
1, 3 mod 16 (u), and for 3x+1 those constraints pin the dropping class to two values. Being
triangular puts no 2-adic condition on a square at all (8x^2 + 1 is always a 2-adic square), which
is why the square-triangular numbers are 2-adically indistinguishable from the squares.

Mirror and cousin (computed, `verify/v3`, 2 <= j <= 600, actual integers). The two-value statement
in (d) is a 3x+1 statement, for the reason given in Theorem 2'. Under 3x-1: N_j and n_j for odd j
(odd squares) show 31 and 36 distinct Terras stopping times, u_j for even j (1 mod 16) shows 48,
while u_j for odd j (3 mod 4) is the single class k = 2. Under 5x+1: 26 and 20 distinct values for
the odd-j terms of N_j and n_j, and many of them do not drop at all within the step cap. Only the
statement about the roots m_j is rule-blind.

Pell versus Collatz (Q2.3-e). The identity in (e) says 3n_j + 1 is the midpoint of n_(j-1) and
n_(j+1). It holds because eps has trace 6 = 2*3. The same holds for every odd q: the unit
q + sqrt(q^2 - 1) has trace 2q, and with u = (q-1)n + 1 one gets n_(j+1) + n_(j-1) = 2(q n_j + 1)
(checked q = 3, 5, 7, 9), and for 3x-1 with the index shifted by one. So it is a Chebyshev identity,
not an interaction. Beyond it we found none: u_j = 3^j holds only mod 8.

Why j = 2. n_(2i) = 8 m_i^2 and n_(2i) + 1 = u_i^2, so every even-indexed square-triangular number
comes from the consecutive pair (8 m_i^2, u_i^2). For i = 1 that pair is (8, 9): the pair of
Levi ben Gerson is the fundamental solution 3^2 - 8*1^2 = 1 of the Pell equation, and 36 = T_8 is
its square (3 + sqrt 8)^2 = 17 + 6 sqrt 8. j = 1, 2 are the only j with N_j 3-smooth, and this
needs no search: N_j = T_n is 3-smooth iff n and n+1 are both 3-smooth, the consecutive 3-smooth
pairs are (1,2), (2,3), (3,4), (8,9) (Levi ben Gerson), so T_n is 1, 3, 6 or 36, and the squares
among these are 1 and 36. (Checked anyway for j <= 5000.)

Pythagorean lifts (Q2.3-g). 4^k + 9^s is a perfect square only for (k, s) = (2, 1), for all
k, s >= 1 and not only in the tabulated range: a primitive triple (2^k, 3^s, y) has 2^k = 2ab and
3^s = a^2 - b^2 with b = 1, a = 2^(k-1), and (2^(k-1) - 1)(2^(k-1) + 1) = 3^s forces
2^(k-1) - 1 = 1. (Checked k < 300, s < 200.)

The null test (Q2.3-f). Mean z is within 1.5 standard errors of zero for all four families in
three runs (10 controls per term in `q23`, 30 in `verify/v3` and `verify/v6`). The standard
deviation of z is 1.2 to 1.4 for u_j. With 10 controls about 1.25 is expected, but with 30
controls a calibration in which the Pell term is replaced by a matched random integer gives 1.03
(range 0.90 to 1.24 over 10 replicates), while u_j gave 1.24 and 1.36: the z statistic is
heavy-tailed and u_j sits at the upper edge. A rank test against 300 matched controls per term
(`verify/v6b`) settles it as far as these data go: Kolmogorov-Smirnov p = 0.47 for u_j and 0.62
for n_j; the share of u_j terms in the two outer deciles is 0.269 against 0.200 +- 0.032. No
significant departure; the null stands, with the remark that the dispersion of u_j is the one
figure not comfortably inside the null range.

### Theorem 5 (the mirror). *Q2.4*

(a) NOT o (x -> 3x+1) = (x -> 3x+1) o NOT, because 3x+1 is the dilation by 3 centred at -1/2 and
NOT is the reflection through -1/2. (b) NOT o (x -> x/2) o NOT = (m -> (m-1)/2), so
`TN := NOT o T o NOT` is m -> 3m/2 (m even), (m-1)/2 (m odd), and TN(m) = T^-(m+1) - 1 where T^- is
the 3x-1 shortcut map. (c) A function f on Z_2 satisfies f o NOT = f iff f = g(T_n) for some g.
(d) T_(3n+1) = 9 T_n + 1; there is no function h with T_(n/2) = h(T_n) compatible with the mirror:
at the even member e of a pair {e, NOT e} the two sides act by e -> e/2 and e -> 3e/2
(T(NOT e) = NOT(3e/2)).

*Proof.* (a), (b), (d) are one-line computations (all verified for abs(n) <= 20000 in `q24`).
(c) is Theorem 1: T is onto with fibres exactly the NOT-orbits. ∎

**Which statements about triangular numbers are forced to be sign-blind.** NOT exchanges the
integers n >= 1 with the integers <= -2, and 3x+1 on the latter is 3x-1 on the positive integers.
So: (i) any property of the *index* n that is expressed through T_n (or u^2) holds equally for
-1-n, hence cannot separate 3x+1 from 3x-1; T_n is exactly the mirror-even coordinate. (ii) Any
class statement about the *value* T_n as a seed (Theorem 1, Corollary 1) is blind for a different
reason: the values T_n are equidistributed mod 2^k, so they carry the natural class law of
whatever rule is applied to them. The same holds for every fold and isometry family, and fails for
the collapsed ones (Theorem 2'). (iii) The conjugacy itself is not special to 3x+1: NOT commutes
with every dilation about -1/2, x -> qx + (q-1)/2, so T_n is equally the mirror-even coordinate of
7x+3 against 7x-3.

**The known cycles of T on Z** (the only ones met from abs(start) <= 200000 in `q24`, and from
abs(start) <= 10^6 in `verify/v4`; that there are no others is the open finite-cycles conjecture, so
every "every cycle" below means "every known cycle"; table in `q24_mirror.log`):

| min | word | (k, s) | 2^k - 3^s | n | v = n+1 | NOT(n) | u = 2n+1 | T_n |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | (1,0) | +1 | 0 | 1 | -1 | 1 | 0 |
| -1 | 1 | (1,1) | -1 | -1 | 0 | 0 | -1 | 0 |
| 1 | 10 | (2,1) | +1 | 1, 2 | 2, 3 | -2, -3 | 3, 5 | 1, 3 |
| -5 | 110 | (3,2) | -1 | -5, -7, -10 | -4, -6, -9 | 4, 6, 9 | -9, -13, -19 | 10, 21, 45 |
| -17 | 11110111000 | (11,7) | -139 | -17, -25, -37, -55, -82, -41, -61, -91, -136, -68, -34 | -16, -24, -36, -54, -81, -40, -60, -90, -135, -67, -33 | 16, 24, 36, 54, 81, 40, 60, 90, 135, 67, 33 | -33, ..., -67 | 136, 300, 666, 1485, 3321, 820, 1830, 4095, 9180, 2278, 561 |

*Pattern (explained).* In v = n+1 the shortcut map is v -> 3v/2 (v even), (v+1)/2 (v odd); the
mirror is m -> 3m/2, (m-1)/2. A run of j odd steps from v = c 2^j visits c 2^(j-i) 3^i: an
anti-diagonal of the exponent lattice of 3-smooth numbers, scaled by the odd number c. The fixed
points 0 and -1 are exchanged by NOT (and so are the branches that fix them). The three cycles
{0}, {1,2}, {-5,-7,-10} are single anti-diagonals with c = 1, j = 0, 1, 2: anti-diagonal j closes
after one exit step iff (3^j +- 1)/2 = 2^j. Together with {-1} these are the four unit cells
abs(2^k - 3^s) = 1, i.e. the four consecutive 3-smooth pairs, i.e. the four 3-smooth triangular
numbers 1, 3, 6, 36. The sign of 2^k - 3^s is the sign of the cycle: (3,4) gives the positive
cycle, (2,3) and (8,9) the negative ones. So "1 = 2^1 - 1" and "5 = 2^2 + 1" are instances of
n0 = 3^j - 2^j at the two j with abs(2^(j+1) - 3^j) = 1. For j >= 3 the same word 1^j 0 is a cycle
of 3x - 11, 3x - 49, 3x - 179, ... (checked j <= 80; always primitive, gcd(n0, d_j) = 1).

*How much of this is about 3x+1?* (`verify/v4`.) In a unit cell every parity word gives an integer
periodic point, because the cycle equation has denominator +-1; that is all the dictionary says,
and it exists for every multiplier:

| rule | unit cells (k, s) | pair | triangular number | cycle |
|---|---|---|---|---|
| 3x+1 | (1,0), (1,1), (2,1), (3,2) | (1,2), (2,3), (3,4), (8,9) | 1, 3, 6, 36 | {0}, {-1}, {1,2}, {-5,-7,-10} |
| 5x+1 | (1,0), (2,1) | (1,2), (4,5) | 1, 10 | {0}, {-1,-2} |
| 7x+1 | (1,0), (3,1) | (1,2), (7,8) | 1, 28 | {0}, {1,2,4} |
| 9x+1 | (1,0), (3,1) | (1,2), (8,9) | 1, 36 | {0}, {-1,-2,-4} |
| 15x+1 | (1,0), (4,1) | (1,2), (15,16) | 1, 120 | {0}, {1,2,4,8} |
| 17x+1 | (1,0), (4,1) | (1,2), (16,17) | 1, 136 | {0}, {-1,-2,-4,-8} |

So T_8 = 36 is attached to Catalan's pair (8, 9), which is a unit cell for 3x+1 (as 2^3 - 3^2) and
for 9x+1 (as 2^3 - 9^1), both times with a negative cycle. What is special to the multiplier 3 is
that it has four unit cells where every other odd multiplier has at most two: (1,0), and (k,1)
when q = 2^k +- 1 (for 3 this is Levi ben Gerson's theorem, in general Mihailescu's). In the
non-unit cell (11,7), 330 words give exactly 11 integral periodic points, the cycle of -17.

*Coincidence (not explained).* The cycle through -17 is two scaled anti-diagonals:
-(16, 24, 36, 54, 81) and -5 (8, 12, 18, 27). Solving the two-run equations gives
c1 = [(2^e1 - 1) 3^j2 + (2^e2 - 1) 2^(e1+j2)] / (3^(j1+j2) - 2^k) = (27 + 112)/139 = 1 and
c2 = 695/139 = 5. That c1 = 1 (so 17 = 2^4 + 1) is the numerical accident
2187 - 2048 = 27 + 112; we found no reason. Census of primitive positive cycles of 3x + d,
abs(d) <= 499 (797 cycles with minimum <= 100 abs(d) + 2000; all counts in this paragraph were
reproduced by an independent recount, `verify/v4`): 18 have v0 = 2^j; among two-run cycles 1 of
95 (the 17-cycle itself); but size-matched, among cycles with abs(v0) <= 16 it is 5 of 9 against a chance share of 0.50, and
7 of 19 for abs(v0) <= 32 against 0.31. Small numbers are often powers of two. Label: numerology.
Also checked: all integer solutions of the two-run equations with run lengths <= 24 are the
17-cycle and the doubled trivial cycles.

The u and T coordinates add nothing here: u(n/2) = v(n) identically, so "u is a power of 3 at
-41" restates "v is 3^4 at -82"; and T at the minima (10, 136, with -10, -136 on the cycles) says
the last halving run has length >= j - 1, true in both cases with no mechanism (two instances).

### Theorem 6 (first-run law). *X-1*

For every integer n other than 0 and -1, the first run of equal letters in the 3x+1 parity vector of
n has length `L1(n) = v_2(n) + v_2(n+1) = v_2(T_n) + 1`.

*Proof.* If n is even it halves exactly v_2(n) times before becoming odd, and v_2(n+1) = 0. If n is
odd, v = n+1 is even and each odd step is v -> 3v/2; the iterate stays odd exactly while v stays
even, i.e. for v_2(n+1) steps, and v_2(n) = 0. Exactly one of n, n+1 is even, so
v_2(T_n) = v_2(n) + v_2(n+1) - 1. ∎

T_n = (n - 0)(n - (-1))/2 is half the product of the distances from n to the fixed points of the
two branches x/2 and (3x+1)/2. The content is the textbook step n = c 2^a - 1 -> c 3^a - 1 (the
number of trailing ones of n in binary is the number of consecutive odd steps); writing it with
T_n is a repackaging, not a result. Every rule (qn + d)/2 has the same law,
L1(n) = v_2(n) + v_2((q-2)n + d), because (q-2)n + d vanishes at the fixed point -d/(q-2) of the
odd branch: for 3x-1 the fixed points are 0 and +1 and the quadratic is T_(n-1); for 5x+1 they
are 0 and -1/3 and it is n(3n+1)/2 (second pentagonal numbers); for qx+1 it is n((q-2)n+1)/2,
polygonal only for q = 3 and 5. All of these are free folds in the sense of Theorem 3 (fibres
{x, -d/(q-2) - x}). What is special to 3x+-1 is only that the odd-branch fixed point is an
integer. Verified for 0 < abs(n) <= 300000, negative n included, for 3x+-1, 5x+-1, 7x+1, 7x+3, 9x+1
(`verify/v5`); the two cross-checks of `q26` (5x+1 against T_n, 3x-1 against T_n) fail as they
should.

Reading for 36: T_n is 3-smooth iff both branch coordinates n and n+1 are 3-smooth. n = 8 = 2^3 is
pure in the halving coordinate and v = 9 = 3^2 is the end of the anti-diagonal 4, 6, 9, which is why
the orbit 3 -> 5 -> 8 -> 4 -> 2 -> 1 is one anti-diagonal followed by one pure halving run.

### Theorem 7 (index and value share half a bit). *X-2*

Let n be Haar-distributed (equivalently, natural density on residues), A = class of n, B = class of
T_n for the 3x+1 map. Then I(A; B) = 1/2 bit. The whole dependence is: n = 1 mod 4 implies T_n odd;
n = 3 mod 4 implies T_n even; for n even T_n is independent of n's class.

*Proof.* On the evens A = 1 and T_(2m) = m(2m+1) is an isometry in m, so B has the natural law pi.
On n = 1 mod 4, A = 2 and T_(2x-1) = x(2x-1) with x odd is an isometry preserving parity, so B has
the law pi conditioned on "odd". On n = 3 mod 4, x is even, T_n is even and B = 1. Since
H(pi) = 1 + H(pi | odd)/2 (finite: class densities decay geometrically),
I = H(pi) - [H(pi)/2 + H(pi | odd)/4] = 1/2. ∎

Computed: 0.500000 bits at every level K = 8, 10, ..., 20 for 3x+1 with T_n and for 3x-1 with
T_(n-1) (the proof works level by level, with "undetermined at level K" as one class; for 3x-1 the
same proof applies with the roles of 1 and 3 mod 4 exchanged). The other figures are not constants:
they depend on the truncation level. 3x-1 with T_n: 0.737 (K = 8), 0.7441 (K = 16), 0.7444
(K = 20). 5x+1 with T_n: 0.202, 0.2060, 0.2063. 5x+1 and 5x-1 with their matched families:
0.262, 0.2660, 0.2663 and 0.321, 0.3242, 0.3244 (`verify/v5`). The value 1/2
uses 3 < 4 (the word 10 already drops, so every odd n outside class k = 2 has first run >= 2).
Compare the repo's Three-Step Theorem (`scripts/mirror_screen/README.md`): 3x+1 and 3x-1 share
exactly one bit, n mod 4.

### Theorem 8 (cubic figurate families). *Q2.2-e*

(a) Octahedral numbers O(n) = n(2n^2+1)/3 and stella octangula numbers S(n) = n(2n^2-1) are
isometries of Z_2, hence permutations of Z/2^k for every k. (b) Square pyramidal numbers
Py(n) = n(n+1)(2n+1)/6 satisfy v_2(Py(x) - Py(y)) = v_2(x - y) - 1 for x = y mod 2; each parity
class maps bijectively onto Z_2, so Z/2^(k+1) -> Z/2^k is exactly 2-to-1 with one even and one odd
preimage, and Py pushes Haar to Haar. Unlike T_n this is not a fold along NOT: Py(-1-n) = -Py(n).
(c) Tetrahedral numbers Te(n) = n(n+1)(n+2)/6: the odd n map bijectively onto Z_2
(v_2(Te(x) - Te(y)) = v_2(x - y) - 1), while each of the classes n = 0 mod 4 and n = 2 mod 4 maps
isometrically onto 4Z_2. Hence over one period 2^(k+1) a residue mod 2^k (k >= 2) is hit 5 times
if it is 0 mod 4 and once otherwise, and the class law is half "even" plus half natural.
(d) Pronic numbers 2T_n, centred square numbers 4T_n + 1, centred hexagonal numbers 6T_n + 1 and
centred cubes (2n+1)(n^2+n+1) are not onto (even; 1 mod 4; odd; odd).

*Proof.* (a) S(x) - S(y) = (x-y)(2(x^2+xy+y^2) - 1) and 3(O(x) - O(y)) = (x-y)(2(x^2+xy+y^2) + 1);
the second factors are odd. (b) With u = 2n+1, 24 Py(n) = u^3 - u, so
24(Py(x) - Py(y)) = (u-u')(u^2 + uu' + u'^2 - 1) with u - u' = 2(x-y). If x = y mod 2 then
u' = u + 4t and u^2 + uu' + u'^2 - 1 = 3u^2 - 1 + 12ut + 16t^2 = 2 + 4ut mod 8, of valuation exactly
1. So v_2 = v_2(x-y) + 1 + 1 - 3. Then m -> Py(2m) and m -> Py(2m+1) are isometries of the compact
space Z_2 into itself, hence onto. (c) With w = n+1, 6 Te(n) = w^3 - w. For w, w' even the factor
w^2 + ww' + w'^2 - 1 is odd, giving v_2(x-y) - 1. For w = w' mod 4 odd the same computation as in
(b) gives valuation exactly 1 for that factor, hence v_2(Te(x) - Te(y)) = v_2(x-y); and
(w-1)w(w+1)/6 is in 4Z_2 because one of w-1, w+1 is divisible by 4 and the other by 2. An isometry
from a coset of 4Z_2 into 4Z_2 is onto. (d) is immediate. ∎

Checked by explicit enumeration of fibres for k = 2..13 and on 200000 random signed 70-bit pairs
(`verify/v2`). All of it is rule-free.

## Q2.5: the numbers attached to 36

Repo vocabulary, un-shortcut step counts (full output in `q25_thirty_six.log`):

| n | role | dropping time (k, s) | class | destination | genus (set, modulus, index) | stopping signature | steps to 1 |
|---|---|---|---|---|---|---|---|
| 36 | value | 1 (1, 0) | 0 mod 2 | 18 | (1, 0, 17) | (1, 18, 0) | 21 |
| 35 | v = 36 | 6 (4, 2) | 3 mod 16 | 20 | (6, 0, 2) | (6, 3, 0) | 13 |
| 8 | index | 1 (1, 0) | 0 mod 2 | 4 | (1, 0, 3) | (1, 4, 0) | 3 |
| 17 | u | 3 (2, 1) | 1 mod 4 | 13 | (3, 0, 3) | (3, 4, 0) | 12 |
| 6 | root | 1 (1, 0) | 0 mod 2 | 3 | (1, 0, 2) | (1, 3, 0) | 8 |
| 37 | 36 + 1 | 3 (2, 1) | 1 mod 4 | 28 | (3, 0, 8) | (3, 9, 0) | 21 |
| 9 | 8 + 1 | 3 (2, 1) | 1 mod 4 | 7 | (3, 0, 1) | (3, 2, 0) | 19 |

Structural: orbit(36) = [36, 18] followed by orbit(9), because 36 = 4*9. For v = n+1 = 2^a 3^b the
integer n makes exactly a odd steps and lands on 3^(a+b) - 1; so 15, 23, 35, 53, 80 (v = 16, 24, 36,
54, 81) are consecutive points of the orbit of 15 = 2^4 - 1, and 35's class 3 mod 16 is
"v_2(36) = 2 odd steps, then v_2(3^4 - 1) = 4 halvings available".

Nothing: every class above has density 1/2, 1/4 or 1/16. orbit(36) passing through 17 and 8:
every orbit from n >= 3, n != 4 passes through 8, and 43.7%, 44.9%, 46.0% of the n up to 10^3,
10^4, 10^5 pass through 17. The matching control over indices ("orbit(T_n) contains both n and
2n+1") succeeds for n = 2 and n = 8 only among 2 <= n <= 2000, because for larger n the targets
are large; so the event at 36 exists because 8 and 17 are small (`verify/v4`). Genus index 17 of
36 is 36/2 - 1. T_36 = 666 appears as T_(-37) on the -17 cycle. 36 and 37 having the same total stopping time is the common
merging of neighbours (both reach 28).

## Null results, stated plainly

- No dropping-class statement about T_n, n^3, the odd-s or s = 2 mod 4 polygonal families, or the
  Pell roots m_j distinguishes 3x+1 from 3x-1 or from 5x+1: each has the natural class law of
  whatever rule is used. The statements about squares, T_n^2, s = 0 mod 4 and the Pell terms N_j,
  n_j, u_j do distinguish them (two classes for 3x+1, many for 3x-1 and 5x+1), but only through the
  residue mod 4 or 8 (Theorem 2'). Neither kind bears on the conjecture.
- 36 is not special in any of Theorems 1 to 4 and 6 to 8. Where 36 does appear (Q2.4-c, Q2.3 "why j = 2")
  it is as half the product of Catalan's pair (8, 9), which serves 9x+1 in the same way; the statements
  in which 36 is the unique or extreme solution of something are Ljunggren's theorem and Levi ben
  Gerson's (36 is the largest 3-smooth triangular number), neither of which is about Collatz.
- The Pell orbit has typical total stopping times (means within 1.5 standard errors of zero in
  three runs; rank test against 300 controls, KS p = 0.47 and 0.62). The standard deviation of z
  for u_j, 1.24 to 1.40, is at the upper edge of a calibrated null (mean 1.03, range 0.90 to 1.24);
  not significant on the rank test.
- The square-triangular Pell problem and the repo's Pythagorean-lift Pell problems live in
  different quadratic fields for every cell (4^k + 9^s is odd); the only degenerate lift
  discriminant is 4^2 + 3^2 = 5^2 (Set_3).
- "17 = 2^4 + 1" has no mechanism (see Theorem 5).
- Halving has no image in the triangular coordinate, so there is no "triangular Collatz map".

## Prior art

- Triangular numbers T_0..T_(2^k-1) permute Z/2^k: classical; it is why triangular (quadratic)
  probing visits every slot of a power-of-two hash table. Hopgood and Davenport, "The quadratic hash
  method when the table size is a power of 2", Computer J. 15 (1972) 314-315; Knuth, TAOCP vol. 3,
  section 6.4, exercise 20 (the reference Wikipedia gives for exactly this statement).
  https://en.wikipedia.org/wiki/Quadratic_probing
- R. L. Rivest, "Permutation polynomials modulo 2^w", Finite Fields Appl. 7 (2001) 287-292.
- Terras 1976, Everett 1977: stopping time classes are residue classes mod 2^k. OEIS A100982
  (class counts; its comments already say "a(n)/2^A020914(n) is the frequency of the dropping time
  A020914(n)" and identify the terms with Terras's terminal words), A020914 (Terras times),
  A122437 (repo dropping times), A023105 (squares mod 2^n).
- Coefficient stopping time versus stopping time: Terras 1976; J. C. Lagarias, "The 3x+1 problem
  and its generalizations", Amer. Math. Monthly 92 (1985), section 2 (Coefficient Stopping Time
  Conjecture, Theorem E: all members of a class except possibly the smallest have the class
  stopping time). https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node5.html
- Square-triangular numbers: Euler 1778. OEIS A001110 (N), A001108 (n), A001109 (m), A001541 (u).
  https://en.wikipedia.org/wiki/Square_triangular_number . OEIS A001109 has no comment on residues
  mod 2^k (checked 2026-10-06, and again in the skeptic pass).
- Uniform distribution of second-order recurrences mod p^h: R. T. Bumby, Proc. AMS 50 (1975)
  101-106; W. A. Webb and C. T. Long, Atti Accad. Naz. Lincei 58 (1975) 92-100. Their criterion for
  p = 2, as stated in L. Somer and M. Krizek, Integers 25 (2025) A1, Theorem 2.3(iv)
  (https://math.colgate.edu/~integers/z1/z1.pdf), is satisfied by m_j (a = 6, b = -1), so the
  permutation / isometry statement of Theorem 4(a) is known. Valuations of Lucas sequences
  (v_2(U_n) law): Lucas 1878; C. Sanna, Fibonacci Quart. 54 (2016).
- Triangular numbers whose squares are triangular: W. Ljunggren 1946; J. W. S. Cassels 1965; see
  Ming Luo, Fibonacci Quart. 34 (1996) https://www.mathstat.dal.ca/FQ/Scanned/34-3/luo.pdf .
  Wikipedia's page on 36 states it as "the only triangular number (other than 1) whose square root
  is also a triangular number". https://en.wikipedia.org/wiki/36_(number)
- 8T+1 square (Wikipedia attributes the test to Euler and Lagrange), and aT + (a-1)/8 triangular
  for every odd square a (9T+1, 25T+3, ...): classical; Wikipedia gives no attribution for the
  second and we could not confirm one. https://en.wikipedia.org/wiki/Triangular_number
- The first-run step n = 2^k m - 1 -> 3^k m - 1 ("long Collatz step", k = number of trailing ones
  of n): standard; a recent statement is in F. Charton and A. Narayanan, "Transformers know more
  than they can tell: learning the Collatz sequence", arXiv:2511.10811.
- V(x) = -1 - x on Z_2 in the 3x+1 literature: D. J. Bernstein and J. C. Lagarias, "The 3x+1
  conjugacy map", Canad. J. Math. 48 (1996); K. Monks and J. Yazinski, "The autoconjugacy of the
  3x+1 function", Discrete Math. 275 (2004); A. Edgington, arXiv:1206.0553. There V commutes with
  the shift and is one factor of the autoconjugacy; that V alone conjugates T to the shifted 3x-1 map
  is a one-line consequence and surely known.
- Cycles and circuits: R. P. Steiner 1977 (1-cycles); J. Simons and B. de Weger, Acta Arith. 117
  (2005) (m-cycles); J. Simons, Math. Comp. 74 (2005) (2-cycles); J. C. Lagarias, "The set of
  rational cycles for the 3x+1 problem", Acta Arith. 56 (1990). The negative cycles -1, -5, -17
  and their cells are in Lagarias's 1985 survey. Consecutive 3-smooth numbers: Levi ben Gerson
  1343; Stormer 1897.
- The first-run law (Theorem 6) is the textbook fact n = c 2^a - 1 -> c 3^a - 1 written with T_n.
  We found no source that states Theorem 7, Theorem 2', Theorem 8 or the trichotomy by v_2(s-2) in
  these words (searches: OEIS entries for the sequences involved, web search for polygonal numbers
  modulo powers of two). All are elementary exercises in 2-adic valuations; no novelty is claimed,
  and "not found in a short search" is all that can be said.
- Consecutive powers: the pair (8, 9) is the only pair of consecutive perfect powers (Catalan's
  conjecture, Mihailescu 2002); for powers of 2 and 3 this is Levi ben Gerson's theorem.

## What we tried that went nowhere

- Looking for structure in the u-coordinate of cycles (powers of 3 at u = 3, 9, -1, -3, -9, -27,
  -81): it is the identity u(n/2) = v(n).
- Looking for the Pell unit to interact with u -> 3u beyond the trace: u_j = 3^j only mod 8.
- Treating T_n as a dynamical coordinate: only the odd step descends.
- "Most uniform meets most collapsed": false as stated (hexagonal is more rigid; all s = 0 mod 4
  collapse equally).
- Tetrahedral numbers and centred families: they do have exact 2-adic types (Theorem 8), but
  nothing Collatz-specific comes out of them.

## Leads not finished

- The quotient of the 2-adic Collatz system by NOT is a 2-valued correspondence on the t-line with
  branches t = T_e -> T_(e/2) and T_(3e/2); they are the parabolas (8t' + 1 - 2t)^2 = 8t' + 1 and
  (18t - 8t' + 1)^2 = 8t' + 1 (both checked for even abs(e) <= 2000). Whether this (2,2)-correspondence has a usable invariant measure or height was not examined.
- Theorem 7 for the full parity vectors of n and T_n rather than their classes.
- The matched families n((q-2)n+d)/2 are free folds for every odd q (settled in the skeptic pass,
  Theorem 6 and `verify/v2`). Still open: a closed form for the 5x+-1 mutual informations, whose
  K = 16 values 0.266 and 0.324 are truncation-dependent.
- Theorem 2' gives the class law of squares under 3x-1 as "Haar on 1 + 8Z_2". Its first terms
  (shares 1/4, 1/8, 5/32 of the odd squares at k = 5, 7, 8) could be put in closed form as counts
  of admissible words with a prescribed three-letter prefix; not done.

## Skeptic pass

Second reader, 2026-10-06. Every claim was re-derived or re-computed with separate code
(`verify/v1` to `v8`, none of which imports `common.py`), the proofs were read line by line, the
Collatz-facing statements were re-run for 3x-1 and 5x+1, and prior art was searched (OEIS, web).

**Wrong and corrected.**

- The mirror column said "blind" for squares, sums of cubes, s = 0 mod 4 and the Pell terms, and
  the text said that for 3x-1 the odd squares fall in a different single class and that for another
  rule the Pell orbit would still meet two classes. Neither had been computed. Both are false:
  under 3x-1 the squares up to (2*10^5)^2 show 103 distinct stopping times, and the Pell terms 31
  to 48. The two-class law is a 3x+1 (and 7x+1) statement. Replaced by Theorem 2' and the mirror
  paragraphs of Theorems 3 and 4; the one-paragraph answer and the first null bullet were rewritten.
- "For an actual integer the Terras stopping time equals the class value except for integers on a
  cycle" was stated as a fact. In general it is Terras's Coefficient Stopping Time conjecture. It is
  now proved for every class of level k <= 24 by a least-residue check (`verify/v8`), which is all
  this thread uses, and labelled a conjecture beyond that.
- "Every cycle of T on Z except the one through -17" now reads "every known cycle"; Q2.4-c is
  labelled prior art, not proved.
- The first failure of the CRS property for pentagonal numbers is at k = 2, not k = 3 (the script
  started at k = 3). The general rule v_2(s-3) + 1 was added.
- "Integral reflection is where triangular is tied to the multiplier 3": false for general d
  (7x+3, 11x+5, ... are dilations about -1/2 and commute with NOT). Restated.
- The first-run law was presented as "special to q = 3" and as separating 5x+1. Every rule has
  the law; only the integrality of the odd-branch fixed point is special to 3x+-1. Status changed
  to prior art (it is the textbook step n = c 2^a - 1 -> c 3^a - 1).
- "36 = T_8 labels the mirror pair {8, -9}" removed from the role-of-36 column: every T_n labels
  {n, -n-1}.
- The mutual informations 0.744, 0.206, 0.266, 0.324 are K = 16 values that move in the third or
  fourth decimal with K; only the two values 1/2 are exact.
- The explanation of the inflated standard deviation of z in the null test ("10 controls") was
  incomplete; replaced by a calibrated statement and a rank test. The null verdict stands.
- "T_(3n+1) = 9T_n + 1 is Euler's": no attribution could be confirmed; now "classical".

**Downgraded to prior art.** Q2.1-a (hash-table probing), Q2.1-d (classical), Q2.3-a (exactly the
Bumby / Webb-Long criterion, checked against the statement in Somer and Krizek 2025), Q2.4-a,
Q2.4-c, Q2.4-d in substance, X-1.

**Upgraded.** Q2.2-e from computed to proved (Theorem 8). "N_j is 3-smooth only for j = 1, 2" from
computed to proved (corollary of Levi ben Gerson). "4^k + 9^s is a square only for (2,1)" from
tabulated to proved. Corollary 1 for actual integers from computed to proved for k <= 24.

**Added.** Theorem 2' (which rules give squares two classes); Theorem 8; the window remark under
Theorem 1; the table showing that the unit-cell dictionary exists for every qx+1 and that the pair
(8, 9) with T_8 = 36 is also a unit cell of 9x+1; the control for "orbit(36) meets 8 and 17".

**Reproduced exactly.** N(k) against A100982 through k = 20 (two methods); all residue-level class
counts; actual stopping times for n < 2^21; the trichotomy for s = -7..40; all Pell identities,
periods (as true minimal periods for k <= 11) and closure sets; the five known cycles from
abs(n) <= 10^6; the census figures 797, 18, 1 of 95, 5 of 9, 7 of 19; the repo data for 36, 35,
8, 17, 6, 37, 9.

**Not checked.** The proofs in the cited literature (Ljunggren, Cassels, Bumby, Webb-Long, Steiner)
were not read; Bumby's and Webb-Long's criterion is quoted from a 2025 secondary source. Knuth's
exercise 6.4-20 is cited on Wikipedia's authority. The integer-level frequency table for polygonal
families at n <= 10^6 (`q22` section 4) was not re-run; it follows from the residue statements and
`verify/v8`. No source was found for the trichotomy, Theorem 2', Theorem 7 or Theorem 8, which is
weak evidence of novelty and no evidence of importance: all four are short exercises.

**Verdict.** The mathematics that survives is correct and almost all of it is either classical or
an elementary exercise about polynomials mod 2^k. The only statements that separate 3x+1 from 3x-1
are the ones about cycles and unit cells, which are prior art, and Theorem 2', which does it
through the residue mod 4. Nothing bears on the conjecture. 36 matters only as T_8, half the
product of Catalan's pair (8, 9), and as the unique solution in Ljunggren's theorem.
