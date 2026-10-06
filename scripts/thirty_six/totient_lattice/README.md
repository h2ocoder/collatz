# Thread 4: the totient fibre of 36 on the 3-smooth lattice

Fact under test: 36 is the least n with exactly eight solutions of phi(x) = n
(x = 37, 57, 63, 74, 76, 108, 114, 126).

Working hypothesis under test: this is a fact about the lattice point (2,2) of the exponent
lattice of 3-smooth numbers 2^a 3^b, the same lattice on which Collatz parity words are monotone
paths and dropping classes are paths on one side of the line 2^a = 3^b.

## Bottom line

* The totient side is completely explained on the lattice. The number A(a,b) of solutions of
  phi(x) = 2^a 3^b has an exact generating function (proved), and
  A(2,2) = 1 + 2[7 prime] + 3[19 prime] + 2[37 prime] = 8. So 36 genuinely enters, as the point (2,2)
  together with the three Pierpont points (1,1), (1,2), (2,2) below it.
* The Collatz side is a clean null. The totient height, totient fibres and A(a,b) share the
  lattice and the two weights ln 2, ln 3 with Collatz, and nothing else that I could measure:
  no dependence survives once n mod 2^k and size are controlled; A(a,b) is not a dropping-class
  count; nothing singular happens at the critical slope.
* Two exact Collatz-facing statements did come out, both elementary and both sign-blind (they
  hold verbatim for 3x-1): Shapiro's additive totient height of n+1 is conserved by the odd step
  (3n+1)/2 (and equally by the odd step of 3x+5 or 3x+7, and equally with v_2 + v_3 in place of
  the totient height: it needs neither Collatz nor the totient), and the multiplicity of a
  dropping destination is a 3-adically locally constant function with M(d) = 1 whenever 3 | d
  (the textbook fact that a multiple of 3 has no odd predecessor).
* Geometry: the lattice point (a,b) of phi(n) counts exactly the steps needed to reach the number
  cos(2 pi/n): a - 1 square roots and b trisections, each trisection being of an angle whose
  cosine already lies in the field below. For the eight polygons with phi = 36: one square root
  and two trisections.
* Nothing here is a step towards the conjecture. Every statement below about Collatz orbits fails
  the mirror test for the sign (it holds verbatim for 3x-1).
* Every claim below was re-derived by a second pass with independent code (`verify/`); what that
  pass changed is listed in the last section.

## Conventions (the same on every table)

* Standard map f(n) = n/2 or 3n+1 (the repo's `collatz.core`). Shortcut map T(n) = n/2 or (3n+1)/2.
* sigma(n): dropping time in the repo convention (`collatz.dropping.dropping_time`): number of
  STANDARD steps until the first value < n. k(n) = number of shortcut steps to drop = number of
  halvings; s(n) = number of odd steps; sigma = k + s. Example: sigma(3) = 6, k = 4, s = 2.
* dest(n): the first value < n. It is the same number in both conventions.
* sig_inf(n): number of standard steps to reach 1 (`collatz.core.total_stopping_time`).
* H(n): number of iterations of phi needed to reach 1 (OEIS A003434). C(n) = H(n) - 1 is Shapiro's
  class for n >= 2 (Shapiro sets C(1) = C(2) = 0). F(n) (OEIS A064415): F = H for even n, H - 1
  for odd n > 1, F(1) = 0.
* Lattice coordinates: m = 2^a 3^b is the point (a,b); X = a ln 2, Y = b ln 3, L = X + Y = ln m,
  theta = X/L. The Collatz critical line 2^a = 3^b is theta = 1/2, slope b/a = ln 2/ln 3 = 0.6309.
* Pierpont point: (i,j) with 2^i 3^j + 1 prime, i >= 1, (i,j) != (1,0). P is the set of them.

## Files

Run each as `C:/repos/collatz/.venv/Scripts/python.exe -X utf8 <script>`. Each writes `<script>.log`.

| script | what it does | time |
|---|---|---|
| `pierpont.py` | Pierpont points with PROVED primality (Lucas certificates, p-1 fully factored) | <1 s |
| `common.py` | totient sieve, H, F, vectorised dropping data, fibre enumeration | - |
| `q41_fibre_count.py` | exact table A(a,b), a,b <= 40; the eight decompositions; brute force; A014197/A007374 | 3 s |
| `q41_rays.py` | A(a,b) for a <= 480, b <= 300: rays, ridge, symmetry, 200 random controls | 45 s |
| `q42_pillai_shapiro.py` | Pillai/Shapiro bounds, additivity, lattice form, the invariant, to 10^7 | 10 s |
| `q42_independence.py` | F against sigma and sig_inf: partial correlation, mutual information, shuffles | 3 min |
| `q43_fibres.py` | fibres phi^-1(m), m <= 10^5, against dropping times; Collatz data of the fibre of 36 | 25 s |
| `q44_polygons.py` | (Z/n)* for the eight polygons; group types; comparison with A100982 | 10 s |
| `q45_destination_multiplicity.py` | multiplicity of dropping destinations, 3-adic structure, mirror maps | 10 s |
| `x_pierpont_cycle_cells.py` | side question: 2^k - 3^s = 2^i 3^j + 1; Pierpont cuban primes | 2 s |

Data: `q41_table.json` (exact A and D for 0 <= a,b <= 40, and the Pierpont points),
`q41_pierpont_points_480x300.json`.

Independent re-checks (second pass, no shared code; each writes `verify/<script>.log`):

| script | what it re-derives | time |
|---|---|---|
| `verify/v1_fibre_count.py` | A(a,b) by explicit (alpha, beta, S) enumeration and by an inverse-totient recursion that knows nothing about Pierpont primes (all a,b <= 22); A014197 for m <= 6000 | 2 s |
| `verify/v1b_lattice.py` | Pierpont box by BPSW; A(a,b) EXACT for a <= 480, b <= 300; ridge by another estimator; 120 random controls; sensitivity of the growth fit | 30 s |
| `verify/v2_shapiro.py` | F from its additive definition, H by dynamic programming, to 3*10^7; the invariant for q x + c maps and negative n | 8 s |
| `verify/v3_destination.py` | destination multiplicity with the standard map to d <= 10^7; classes by brute force over residues; martingale identity | 15 s |
| `verify/v4_polygons.py` | (Z/n)* by counting roots of 1; exact cyclotomic arithmetic for the cubic steps; A100982 by brute force | 22 s |
| `verify/v5_sunit.py` | 2^k - 3^s = 2^i 3^j + 1: other loop order, proof steps, mirror and cousin equations, cuban numbers | 5 s |
| `verify/v6_nulls.py`, `verify/v6b_mi_placebo.py` | the statistical nulls on a disjoint range (10^7, 4*10^7], by pair differences and by a placebo test | 1.5 + 3 min |
| `verify/v7_misc.py` | sieve counts, A007374 (35 terms), level sets a + b = n, saddle weights | 1 s |

## Results at a glance

Status labels: proved / computed / conjecture / null / prior art / numerology.

| id | statement | status | role of 36 | mirror test |
|---|---|---|---|---|
| Q4.1-a | generating function of A(a,b) = #{x : phi(x) = 2^a 3^b} (Theorem 1) | proved (standard multiplicative argument; row b = 0 is OEIS A058321) | (2,2) is one coefficient | not Collatz-facing |
| Q4.1-b | A(2,2) = 1 + 2[7 prime] + 3[19 prime] + 2[37 prime] = 8, the eight decompositions | proved | genuine as the point (2,2); the mechanism is generic (every 3-smooth m has such a decomposition) | not Collatz-facing |
| Q4.1-c | 36 is the least m with exactly eight solutions (OEIS A007374(8) = 36; 35 terms recomputed) | prior art | genuine for the count, accidental for "least": 24 jumps from 6 to 10 | not Collatz-facing |
| Q4.1-d | table A(a,b): exact for a <= 480, b <= 300 (`verify/v1b_lattice.py`); equals the sieve count for all 142 3-smooth m <= 10^6 and an inverse-totient count for all a,b <= 22 | computed | none | not Collatz-facing |
| Q4.1-e | ln A ~ 2 sqrt(c L m(theta)), symmetric under 2^a <-> 3^b | conjecture (heuristic; the data support the exponent 1/2 and the shape in theta, not the constant) | none | sign-blind; 5x+1 would use another lattice |
| Q4.1-f | no kink at the critical slope; ridge of A at slope 0.55-0.58 for L <= 320, within 1.2-1.6 sd of random sets | null | none | sign-blind |
| Q4.1-g | centre of mass of the 1142 Pierpont points below e^329.58: theta = 0.4975 +- 0.0098; about 8 Pierpont primes per decade | computed; the count per decade is prior art (795 below 10^100) | none | not Collatz-facing |
| Q4.2-a | 2^(H-1) < n <= 2*3^(H-1); F completely additive; 2^F <= n <= 3^F | prior art (Pillai, Shapiro), verified to 3*10^7, short proofs given | none | not Collatz-facing |
| Q4.2-b | F(2^a 3^b) = a + b; sigma(n) = k + s = H(2^k 3^s); totient chain is one L-shaped path | proved (a relabelling: both sides are k + s by definition) | 36 -> 12 -> 4 -> 2 -> 1 is the chain of (2,2) | sign-blind |
| Q4.2-c | F(T(n)+1) = F(n+1) for odd n; 3 is the only odd q with F(q) = F(2) | proved (trivial) | none (35 -> 53 -> 80 is v = 36 -> 54 -> 81 as an example) | holds for 3x-1, 3x+5, 3x+7 and for negative n; fails for 5x+-1, 7x+1: separates 3 from 5, not + from - |
| Q4.2-d | F and sigma, sig_inf independent once n mod 2^k and size are controlled | null (replicated on a disjoint range) | none | n/a |
| Q4.3-a | fibres are closed under x <-> 2x (x odd) and contain {3y, 4y, 6y} together (y coprime to 6); Collatz reads these as halvings | proved (trivial) | {37,74}, {63,126}, {57,76,114}, {108} | n/a |
| Q4.3-b | dropping times of fibre-mates are not more alike than chance beyond x mod 16 | null (replicated; mechanism of the residue effect identified) | none | n/a |
| Q4.3-c | Collatz arrows inside fibres (phi(T(x)) = phi(x)): 59 below 10^6, chance level 62 +- 8 | numerology | none; phi^-1(6) = {18 -> 9 -> 14 -> 7} | n/a |
| Q4.4-a | Q(cos 2pi/n) is reached by exactly a - 1 square roots and b = v_3(phi(n)) trisections, each of an angle whose cosine lies in the field below; b is the minimal number of trisections | proved here (corollary of Gleason 1988 plus classical Kummer theory) | all eight polygons: one square root, two trisections | not Collatz-facing |
| Q4.4-b | the lattice decomposition of (a,b) is the primary decomposition of (Z/n)* | proved (standard) | 63- and 126-gon: two independent trisections; the other six: nested | not Collatz-facing |
| Q4.4-c | A(a,b) is not a dropping-class count: no match with A100982, different growth, different support | null | none | n/a |
| Q4.5-a | n/2 <= dest(n) < n; M(d) >= 1; M(d) = 1 whenever 3 divides d | proved (folklore: multiples of 3 have no odd predecessor) | none | same for 3x-1; 5x+1 with 5 in place of 3 |
| Q4.5-b | M(d) = number of dropping classes through the 3-adic residue of d | proved from Terras, on the range where his stopping-time equality is verified | none | sign-blind |
| Q4.5-c | Pr[M = 1] = 0.5313; mean M = sum A100982(s)/3^s = 1.6903605922 (proved); every m = 1..18 occurs below 10^7; mean of dest(n)/n = 0.6199493034 | proved (the two means) / computed (the distribution) | none | identical for 3x-1 to 4 digits; 5x+1 differs |
| X-a | 2^k - 3^s = 2^i 3^j + 1 has exactly nine solutions, seven with s >= 1; 37 is the largest prime one | proved (given Ellison 1971); contained in Alex-Foster 1992 | coincidence: it is the cuban identity 4^3 - 3^3 = 37 of X-b; on the 3x-1 side the same statement singles out 72, not 36 | the equation changes with the sign (3^s - 2^k on the 3x-1 side) but says nothing about the conjecture |
| X-b | the Pierpont cuban primes of the first kind are exactly 7, 19, 37, and they are the primes that build the fibre of 36 | proved core, coincidence of two small sets (numerology) | 36 = 6 T_3 = T_3^2 because T_3 = 6 | not Collatz-facing |

---

## Q4.1 The fibre count as a partition problem

### Theorem 1 (generating function). proved

phi(x) is 3-smooth iff x = 2^alpha 3^beta p_1 ... p_r with distinct Pierpont primes p_t > 3, and

    sum_{a,b >= 0} A(a,b) X^a Y^b = (1 + 1/(1-X)) (1 + X/(1-Y)) prod_{(i,j) in P} (1 + X^i Y^j).

Proof. phi(x) = prod p^(e-1) (p-1) over p^e || x. If p >= 5 divides x with e >= 2 then p divides
phi(x); so e = 1, and p - 1 must be 3-smooth: p = 2^i 3^j + 1 with i >= 1 (p is odd) and
(i,j) != (1,0) (p is not 3). Conversely every such x has 3-smooth totient. By unique factorisation
x corresponds to exactly one triple (alpha, beta, S), S a finite subset of P, and

    phi(x) = phi(2^alpha) phi(3^beta) prod_{(i,j) in S} 2^i 3^j,
    phi(2^alpha) = 2^(alpha-1) (alpha >= 1),   phi(3^beta) = 2 * 3^(beta-1) (beta >= 1).

So 2^alpha contributes the lattice vector (alpha-1, 0), 3^beta contributes (1, beta-1), and each
chosen Pierpont prime contributes its point (i,j), used at most once. The three factors of the
generating function are these three choices. QED

Equivalently, with D(c,d) = number of sets of distinct Pierpont points with sum (c,d) and R(u,v) =
number of 3-smooth x with phi(x) = 2^u 3^v,

    A(a,b) = sum_{c <= a, d <= b} D(c,d) R(a-c, b-d),
    R(0,0) = 2, R(0,v) = 0 (v > 0), R(1,0) = 3, R(u,0) = 2 (u >= 2), R(1,v) = 2, R(u,v) = 1 (u >= 2, v >= 1).

The asymmetry R(0,v) = 0 is the whole story of the small cases: a power of 3 always brings a
factor 2, so nothing absorbs a pure power of 3.

Corollaries (all checked in `q41_fibre_count.log`):

* Row b = 0: A(a,0) = a + 2 for a <= 31 and 32 for 32 <= a <= 40 (classical; the five Fermat primes;
  OEIS A058321, with the solutions themselves in A058213).
* Column a = 1: A(1,b) = 2 + 2[2*3^b + 1 prime] for b >= 1.
* Column a = 2, b >= 1:
  A(2,b) = 1 + 2 #{1 <= d < b : 2*3^d + 1 prime} + 3[2*3^b + 1 prime] + 2[4*3^b + 1 prime]
  + 2 #{d1 < d2, d1 + d2 = b : 2*3^d1 + 1 and 2*3^d2 + 1 both prime}. Verified for b <= 40.

### The eight solutions as lattice decompositions of (2,2). proved

    x     = 2^alpha * 3^beta * Pierpont primes     (2,2) = [2^alpha] + [3^beta] + Pierpont points
     37   = 37                                      (2,2)
     74   = 2 * 37                                  (2,2)
     57   = 3 * 19                                  (1,0) + (1,2)
     76   = 2^2 * 19                                (1,0) + (1,2)
    114   = 2 * 3 * 19                              (1,0) + (1,2)
     63   = 3^2 * 7                                 (1,1) + (1,1)
    126   = 2 * 3^2 * 7                             (1,1) + (1,1)
    108   = 2^2 * 3^3                               (1,0) + (1,2)

A(2,2) = D(2,2)R(0,0) + D(1,2)R(1,0) + D(1,1)R(1,1) + D(0,0)R(2,2) = 2 + 3 + 2 + 1 = 8. The other
Pierpont points below (2,2) are (2,0) [the prime 5] and (2,1) [13]; they would leave remainders
(0,2) and (0,1), which nothing absorbs, so 5 and 13 divide no solution.

By the column formula, A(2,2) = 1 + 2[7 prime] + 3[19 prime] + 2[37 prime], and 8 is the largest
value the formula allows at b = 2: **phi(x) = 36 has eight solutions exactly because 6 + 1, 18 + 1
and 36 + 1 are all prime.**

Role of 36: genuine. It is the point (2,2), and the count is decided by the three points
(1,1), (1,2), (2,2), i.e. by 36/6 + 1, 36/2 + 1, 36 + 1.

Control (how special is this?). The mechanism is generic: every 3-smooth m has such a decomposition,
and the count 8 is not rare (phi(x) = m has exactly eight solutions also for m = 64 = (6,0) and
324 = (2,4) on the lattice, and for 176, 200, 224, 280, ... off it). The three numbers m/6 + 1,
m/2 + 1, m + 1 are simultaneously prime for m = 12, 36, 72, 1152, 2592, 2916 among 3-smooth
m <= 10^6; only at (2,2) do they decide the count, because only there are they the only usable
Pierpont points. The neighbours 35 and 37 have no solutions (odd), 24 has ten, 48 has eleven. So
"36 = (2,2) explains the eight" is a true reading of the fact, not a distinction of 36.

### Why (2,2) is the FIRST eightfold point. prior art, recomputed

OEIS A014197 (number of x with phi(x) = m) and A007374 (least m with exactly k solutions; a(8) = 36)
are recomputed from a totient sieve to 10^7, which provably sees every solution for m <= 10^6
(phi(x) <= 10^6 forces at most 7 distinct primes, so x <= 5.54 phi(x)). The recomputed A007374 agrees
with the OEIS data for k = 2..36 (all 35 terms listed in the entry; checked a second time with an
inverse-totient recursion instead of a sieve).

Multiplicities below 36: {1:2, 2:3, 4:4, 6:4, 8:5, 10:2, 12:6, 16:6, 18:4, 20:5, 22:2, 24:10, 28:2,
30:2, 32:7}. The values 2,...,7 are first reached at 1, 2, 4, 8, 12, 32, all 3-smooth; 24 = (3,1)
jumps from 6 straight to 10 (at b = 1 the prime 5 can take part, e.g. 35 = 5*7, 45 = 9*5), so 8 is
first reached at 36. "First eightfold" is therefore a small-number accident on top of the exact
count: the count 8 is structural, the word "least" is not.

Small k-fold champions are 3-smooth because 3-smooth totient values have heavy fibres: mean fibre
size over totient values <= 10^6 is 10.8, over the 130 3-smooth ones 115.5. The least m with exactly
k solutions is 3-smooth for k = 2..8, 10, 11, 17, 19, 21, 27, 28 and not otherwise for k <= 31.

Prior art: Carmichael 1907/1922 (no multiplicity one, conjectured), Ford 1999 (every k >= 2 occurs),
OEIS A014197, A007374, and A058321 / A058213 for the row b = 0 (phi(x) = 2^n). The generating
function is the standard multiplicative decomposition. No OEIS entry was found (term searches on
2026-10-06, twice) for the diagonal 2, 4, 8, 19, 39, 82, 166, 322, 610, 1126, ..., the row
b = 1 (4, 6, 10, 11, 17, 21, 27, 32, ...), the column a = 1 (3, 4, 4, 2, 4, 4, 4, 2, 2, 4, ...), the
column a = 2 (4, 6, 8, 9, 8, 12, 18, 15, ...) or the anti-diagonal sums (2, 3, 8, 15, 26, 48, 77, ...).
That is absence from OEIS, not a novelty claim: the result is a two-line exercise.

### A(a,b) as a function on the lattice

Computed exactly for a,b <= 40 and in float64 for a <= 480, b <= 300 (the two agree on the overlap;
1625 Pierpont points with proved primality among candidates of up to 955 bits). The whole box was
recomputed in exact integers in `verify/v1b_lattice.py` (the float table is right to 1.2e-15), with
the 1625 points confirmed by an independent BPSW test; A(100,100) = 1224398428241739.

**Growth.** Along every ray ln A grows like sqrt(L), not like L:

    slope b/a   theta    heuristic h   fitted coefficient of sqrt(L)   fitted coefficient of ln L
     0.1000    0.8632      2.535              2.687                        -2.04
     0.2500    0.7162      3.123              3.315                        -1.84
     0.3981    0.6131      3.310              3.441                        -1.61
     0.5000    0.5579      3.359              3.465                        -1.60
     0.6309    0.5000      3.376              3.479                        -1.74     <- critical slope
     0.7960    0.4422      3.359              3.459                        -1.88
     1.0000    0.3869      3.310              3.409                        -1.99
     1.5923    0.2838      3.123              3.215                        -2.10
     2.5000    0.2015      2.857              2.923                        -1.96

(fit ln A = alpha sqrt(L) + beta ln L + gamma over L >= 40; rows 2 and 8, 3 and 7, 4 and 6 are mirror
pairs under theta -> 1 - theta.)

**Heuristic (status: conjecture).** Assume Pierpont points have density kappa/(X+Y) per unit dX dY,
i.e. N(L) = #{p Pierpont, ln(p-1) <= L} ~ kappa L. Then

    ln prod_P (1 + e^(-sX - tY)) ~ kappa (pi^2/12) ln(s/t)/(s - t),
    ln A(a,b) ~ 2 sqrt(c L m(theta)),  c = kappa pi^2/12,
    m(theta) = min_{lam > 0} psi(lam) (theta + lam (1 - theta)),  psi(lam) = ln(lam)/(lam - 1),

and m(theta) = m(1 - theta) with maximum m(1/2) = 1. (Derivation: 1/(X+Y) = int_0^inf e^(-u(X+Y)) du
gives int int e^(-sX-tY)/(X+Y) = ln(s/t)/(s-t); the alternating sum over the expansion of ln(1+z)
gives pi^2/12; then the saddle point.) With the measured kappa = 3.465 the predicted coefficients are
the column "heuristic h"; the fitted ones have the same shape in theta. The size of the agreement
(2 to 6 per cent) is a property of the three-parameter fit and not a test of the constant: on the
critical ray the fitted coefficient of sqrt(L) is 3.26 without the ln L term, 3.48 to 3.51 with it
and 3.32 to 3.55 with a further 1/sqrt(L) term (heuristic 3.376); the local slope d ln A/d sqrt(L)
is 3.18, 3.27, 3.34 at L = 150, 300, 600 and ln A/(2 sqrt(cL)) is 0.75, 0.84, 0.88 at
L = 100, 300, 600. The data support the exponent 1/2 and the theta-profile; the constant c is open.

The heuristic says: to leading order A depends on (ln 2^a, ln 3^b) symmetrically, so on a level set
of the SIZE of m the multiplicity should peak on the line 2^a = 3^b. The reason is the prime number
theorem (the chance that 2^i 3^j + 1 is prime depends on its size only), not anything about Collatz.

**What the data say about the critical slope (status: null).**

1. No singularity. Second differences of ln A in theta on level sets are smooth through theta = 1/2
   (L = 300: -185.9, -168.7, -162.6, -165.8, -177.4, -197.1, -227.2 at theta = 0.35, ..., 0.65).
2. The ridge is near the line but not on it. On size level sets L = 60, ..., 320 the maximum of A is
   at theta* = 0.522, 0.523, 0.528, 0.531, 0.534, 0.535, 0.536, 0.536, i.e. slope b/a = 0.58 falling
   to 0.55, against 0.631.
3. The offset is explained. In the saddle-point approximation (no density assumption needed)
   d(ln A)/d(theta) = L (s - t) on a level set, so the ridge is where the two saddle multipliers
   are equal; there every Pierpont prime p has weight 1/(1 + (p-1)^s), and the ridge direction is
   the weighted centre of mass of the Pierpont points (plus small absorption terms). Evaluated on
   the exact generating function this predicts theta = 0.522, ..., 0.531 for the same levels
   (measured 0.522, ..., 0.536). At L = 300 the weights reach only primes up to about e^30, where
   the 2-parts happen to be heavier (centre of mass 0.56 for ln(p-1) <= 40).
4. It is within noise for a random set. 200 random point sets with the same density give
   theta* = 0.507 +- 0.019 at L = 300; the real value 0.536 is +1.5 sd (6.5 per cent of controls are
   higher). Reflecting the real set across the critical line moves the ridge to 0.474: the offset is
   carried by the positions of the actual primes (+-0.031), not by the lattice (mean 0.505).
   (Second pass, other estimator and seed, 120 sets: real 0.533, control 0.508 +- 0.021, +1.2 sd.)
5. The premise of the symmetry holds as far as it can be tested. Over the 1142 Pierpont points with
   ln(p-1) <= 329.58 (the full cap of the box), sum i ln 2 = 94986.1 and sum j ln 3 = 95959.4:
   theta_cm = 0.4975 +- 0.0098. (With the cutoff 329 it is 1138 points and 0.4996; for cutoffs
   between 20 and 320 it wanders between 0.479 and 0.547. The honest statement is "consistent with
   1/2 at the 1 sd level", not "0.4996".) The angular distribution is consistent with uniform
   (chi^2 = 14.2 on 9 d.o.f.).
6. On level sets a + b = n the maximum is at b/a = 0.75 to 0.82, a different place. "Where A is
   largest" depends on the level set; only the size level set has the symmetry.

Answer to the seed question: as expected, nothing special happens at the Collatz critical slope. The
line 2^a = 3^b is the (conjectural, asymptotic) symmetry axis of A, for a prime-number-theorem
reason, and at computable sizes the ridge sits at slope 0.55 to 0.58.

Role of 36: none; this is about the whole lattice. Mirror test: the line 2^a = 3^b is the same for
3x-1; for 5x+1 the analogous object would live on the lattice of 2^a 5^b. Not a Collatz statement.

Side measurement (prior art): Pierpont primes are rarer than Gleason's "about 9 per decade". 1142 of
them (above 3) below e^329.58 = 10^143.1 is 7.98 per decade, kappa = 3.465 +- 0.103 against
3/(ln 2 ln 3) = 3.940. This is already in the published counts: 42, 65, 157, 795 Pierpont primes
below 10^6, 10^9, 10^20, 10^100 (Wikipedia "Pierpont prime", OEIS A005109), i.e. 7.95 per decade;
the point set here reproduces those four counts exactly. Gleason's 9 is the naive constant
3 ln 10/(ln 2 ln 3) = 9.07.

---

## Q4.2 The totient descent between log_3 and log_2

### Statements (prior art) and short proofs

Let F be the completely additive function with F(2) = 1 and F(p) = F(p-1) for odd primes p
(OEIS A064415; Shapiro 1943).

**Lemma 1.** F(phi(n)) = F(n) - 1 for even n, F(phi(n)) = F(n) for odd n >= 3. Hence H(n) = F(n) for
even n and H(n) = F(n) + 1 for odd n >= 3.
Proof. phi(n) = n prod_{p | n} (p-1)/p, so F(phi(n)) = F(n) + sum_{p | n} (F(p-1) - F(p)), and the
only non-zero term is p = 2, which gives -1. For n >= 3, phi(n) is even; from an even number each
step lowers F by one until F = 1, which among even numbers means the number 2; one more step gives 1.
QED

**Lemma 2.** 2^F(n) <= n, with equality iff n is a power of 2. (Induction: for an odd prime,
2^F(p) = 2^F(p-1) <= p - 1 < p; products multiply.)

**Lemma 3.** n <= 3^F(n) for odd n and n <= 2*3^(F(n)-1) for even n; equality n = 3^F(n) iff n is a
power of 3. (Induction: for an odd prime, p - 1 is even, so p <= 2*3^(F(p)-1) + 1 <= 3^F(p), with
equality only for p = 3; products of odd numbers multiply; for n = 2m, F(n) = F(m) + 1 and both
parities of m give n <= 2*3^(F(n)-1).)

Consequences, all verified for every n <= 10^7 in exact integer arithmetic (`q42_pillai_shapiro.log`),
and again for every n <= 3*10^7 with F built from its additive definition (`verify/v2_shapiro.log`):

* **log_3 n <= F(n) <= log_2 n** for all n >= 1, with equality exactly on the powers of 3 and of 2.
* Pillai 1929: 2^(H-1) < n <= 2*3^(H-1), i.e. log_3(n/2) + 1 <= H(n) < log_2(n) + 1 (usually quoted
  as ceil(log_3 n) <= H(n) <= ceil(log_2 n)). The largest number with H = h is 2*3^(h-1) (verified
  for h <= 16, where it is below 3*10^7); H(2^k) = k.
* Shapiro 1943: C(mn) = C(m) + C(n) + [m and n both even] for m, n >= 2. (At m = 1 the formula needs
  Shapiro's convention C(1) = 0; with C = H - 1 one has C(1) = -1 and it fails.) Odd numbers of
  class C lie in (2^C, 3^C], even ones in [2^(C+1), 2*3^C] (Shapiro's three sections I: (2^C, 2^(C+1)),
  II: [2^(C+1), 3^C], III: (3^C, 2*3^C]). Least elements of the classes equal OEIS A007755 for
  h <= 25.
* F(n)/ln n lies in [1/ln 3, 1/ln 2] = [0.910, 1.443]; its mean over [10^6, 10^7) is 1.2157
  (Erdos-Granville-Pomerance-Spiro 1990 conjecture H(n) ~ alpha ln n for almost all n).

Role of 36: none. The extremal numbers are 2^k and 2*3^k.

### Is there a structural dictionary with Collatz? (status: proved where stated, otherwise "resemblance")

What is exact:

1. On the 3-smooth lattice F is the L1 norm: F(2^a 3^b) = a + b, and H(2^a 3^b) = a + b for a >= 1.
   The Pillai-Shapiro sandwich restricted to the lattice is the triviality
   a log_3 2 + b <= a + b <= a + b log_2 3.
2. The repo's dropping time is the same L1 norm: a word with k halvings and s triplings takes
   sigma = k + s standard steps, so **sigma(n) = H(2^k(n) 3^s(n))** (checked for n <= 20000). This is
   a relabelling, not a relation: both sides are k + s by definition, and it would be equally true
   of any function equal to a + b on 2^a 3^b (for instance the number of prime factors). The
   set of dropping times {1, 3, 6, 8, 11, 13, 16, ...} is the set of L1 norms of the staircase points
   (floor(s log_2 3) + 1, s) (OEIS A122437, already recorded in this repo as prior art).
3. The totient chain of 2^a 3^b is a monotone lattice path, but always the same one: straight down
   in b, then straight down in a. 36 -> 12 -> 4 -> 2 -> 1 is (2,2) -> (2,1) -> (2,0) -> (1,0) -> (0,0).

What is not there: a Collatz word is one of many paths to (k,s), chosen by n mod 2^k and constrained
by the line; the totient chain is one fixed path per point, chosen by nothing, and unconstrained.
The totient descent is sandwiched between the two linear functionals log_3 and log_2; a dropping
class is cut out by the sign of their difference k ln 2 - s ln 3. Same lattice, same two weights,
different objects. **Verdict: a resemblance plus the L1-norm identity, not a dictionary.**

Role of 36: only as the worked example (2,2). Mirror test: the L1-norm identity is the same for
3x-1 and, with 5 in place of 3, false for the totient (F(5) = 2, not 1).

### An exact invariant (status: proved, trivial, sign-blind)

**Proposition.** For odd n, F(T(n) + 1) = F(n + 1), where T(n) = (3n+1)/2.
Proof. T(n) + 1 = 3(n+1)/2 and F is completely additive with F(3) = F(2) = 1. QED

In the coordinate v = n + 1 the odd shortcut step is v -> 3v/2: it moves along the anti-diagonal
a + b = const of the lattice and keeps Shapiro's height. Example: n = 35 -> 53 -> 80 is
v = 36 = 2^2 3^2 -> 54 = 2*3^3 -> 81 = 3^4, with F = 4 throughout. At an even step v -> (v+1)/2 and
F is not conserved (mean change -0.69, sd 1.27 over even n < 10^7).

3 is the only odd prime q with F(q) = F(2): F(q) = F(q-1) = 1 forces q - 1 = 2. So among "q x + 1"
maps the odd step preserves F only for q = 3; for 5x+1 the odd step is v -> 5v/2 in v = 3n+1 and F
rises by exactly 1 each time (verified on 666666 odd n).

Mirror test: for 3x-1 the same holds with v = n - 1 (verified on 3.3 million odd n). In general the
odd step of q x + c is v -> q v/2 in the coordinate v = (q - 2) n + c, and F(v) changes by
F(q) - 1: 0 for 3x+1, 3x-1, 3x+5, 3x+7 and for negative n under 3x+1 (with F(|v|)); +1 for
5x+1, 5x-1, 7x+1, 9x+1 (`verify/v2_shapiro.log`, up to 10^7 odd n each). The invariant separates
3 from 5 (because phi(3) = 2) but not +1 from -1, nor Collatz from 3x+5 (which has several
cycles). It cannot bear on the conjecture. It is true of any completely additive f with
f(2) = f(3); the totient supplies one, and g(v) = v_2(v) + v_3(v) is another (checked: conserved
on every odd n < 10^6), so the totient is not needed either.
Role of 36: none.

### Empirical question: is F related to Collatz times? (status: null)

Odd n only (even n have sigma = 1). Sample for the controlled tests: the 2.5 million odd n in
(5*10^6, 10^7]. Size is controlled by bins of ln n inside the octave; residues by class means or
strata of n mod 2^k (and n mod 3^j). Full output: `q42_independence.log`.

Partial correlation (Pearson; standard error 0.00063):

    pair               size only   + n mod 4   + n mod 16   + n mod 256   + n mod 65536
    F(n),   sigma       -0.0101     -0.0036     -0.0011      -0.0008        -0.0010
    F(n),   sig_inf     -0.0025     -0.0010     -0.0009      -0.0008        -0.0010
    F(n+1), sigma       +0.1557     +0.0846     +0.0251      +0.0028        +0.0015
    F(n+1), sig_inf     +0.0333     +0.0164     +0.0037      -0.0000        -0.0003

Mutual information in bits, excess over a shuffle of F within strata (size bin, n mod 2^k):

    pair               k = 1                k = 2          k = 4          k = 8          k = 12
    F(n),   sigma      +3.3e-4 (z = +36)    +4.7e-5 (+5.6) +0.9e-5 (+0.9) +1.0e-5 (+1.2) +0.7e-5 (+0.6)
    F(n),   sig_inf    +9.5e-5 (z = +1.5)   +4.5e-5 (+1.0) +1.3e-5 (+0.2) +5.7e-5 (+1.0)  see note
    F(n+1), sigma      +2.9e-2 (z > 3000)   +8.0e-3 (+776) +1.6e-3 (+45)  +9.0e-5 (+3.2) +0.3e-5 (+0.1)
    F(n+1), sig_inf    +2.4e-4 (z = +3.6)   +3.8e-4 (+7.2) +1.3e-4 (+2.1) -0.2e-5 (-0.0)  see note
    positive control   +9.4e-3 (z = +119)   ... the same at every k

Reading:

* There IS a dependence between F(n) and the dropping time, and it is entirely mediated by n mod 16.
  (For odd n the residue mod 4, 8, 16 is correlated with the 2-power content of p - 1 over the
  primes p | n, hence with F; mean F is 19.083 for n = 1 mod 4 against 19.057 for n = 3 mod 4.) Once
  n mod 16 is fixed, nothing is left: excess 0.9e-5 bits, z = 0.9.
* F(n+1) is strongly tied to sigma (0.029 bits) because F(n+1) contains v_2(n+1), the length of the
  initial run of odd steps. That is a statement about n mod 2^k, and for sigma it is gone by k = 12
  (for sig_inf about 1e-4 bits remain, carried by higher residue bits: see the replication below).
* Nothing survives for sig_inf either. Note on size: F and sig_inf both grow with ln n, and a coarse
  size control manufactures dependence. With 8 size bins per octave the "excess" between F and
  sig_inf is 1.5e-3 bits (z = 24); with 32 bins 2.1e-4; with 128 bins 9.5e-5; with 512 bins 2.4e-5
  (z = 0.45). The k = 12 column used 32 bins and for F(n) shows this artefact (+1.7e-4), not a
  dependence (with 1024 bins it is -2e-5 in the second pass). For F(n+1) the k = 12 value
  (+1.45e-4) is not a size artefact; it is residue-mediated (item 3 of the replication below).
  A first version of the script stratified by octave only and "found" 0.02 bits.
* Residual partial correlations of F(n) with sigma and with sig_inf sit at about -0.0009, 1.3 to 1.9
  standard errors, for every k >= 4. This did not replicate (see below) and is noise.
* The positive control (sig_inf + 1 on a random 2 per cent of the n with F even) is detected at
  9.4e-3 bits, z > 100, so the test could have seen a dependence 50 times smaller than that.

**Replication on a disjoint range (second pass, `verify/v6_nulls.log`, `verify/v6b_mi_placebo.log`).**
Odd n in (10^7, 4*10^7], other code, other statistics.

1. Pair differences. For pairs (n, n + 2^k) with the same residue mod 2^k and almost the same size,
   the correlation of (F(n') - F(n), Y(n') - Y(n)) over 7.5 million pairs (s.e. 0.00037):

       k     F(n), sigma     F(n), sig_inf    F(n+1), sigma    F(n+1), sig_inf
       2      +0.0031         +0.0011          +0.0640          +0.0222
       4      +0.0009         +0.0006          +0.0241          +0.0052
       8      -0.0003         -0.0007          +0.0021          +0.0000
      12      +0.0006         -0.0002          +0.0002          +0.0007
      16      +0.0003         +0.0002          +0.0001          +0.0003
      20      +0.0001         -0.0002          -0.0001          +0.0006

   The first pass's residual of -0.0009 for F(n) is not there: at k = 16 the two values are +0.0003
   and +0.0002, and over the three sub-ranges (1, 2], (2, 3], (3, 4] * 10^7 the sign changes
   (+0.0008, +0.0006, -0.0006 for sigma; +0.0008, +0.0001, -0.0003 for sig_inf). (A pair controls
   n mod 2^k but its members differ in bit k, so the k = 2 and k = 4 rows still contain the
   dependence carried by n mod 8 and n mod 32.)
2. Mutual information against within-stratum shuffles, re-implemented, odd n in (10^7, 2*10^7]:
   F(n) against sigma has no excess at k = 4, 8, 12 (z = +0.3, -0.9, -0.5): mediated by n mod 16, as
   claimed. F(n+1) against sigma: 1.5e-3 bits at k = 4, 8e-5 at k = 8, 5e-6 (z = 0.5) at k = 12: gone
   by k = 12, as claimed. (The pair statistic of item 1 only sees linear effects of about 0.001 in
   correlation; the shuffle test is the sensitive one.)
3. One statement needed correcting. F(n+1) against sig_inf keeps an excess of about 1e-4 bits at
   k = 8 and at k = 12 (z between 2.5 and 5 for 256, 1024 and 4096 size bins), where the first pass
   reported none at k = 8. A placebo settles what it is: P(n) = F(n + 1 + 2^17), a different number
   with the same residue mod 2^17 as n + 1, shows the same excess within noise (0.9 to 1.1e-4 bits
   at k = 8, 0.6 to 1.0e-4 at k = 12; and 1.57e-3 against sigma at k = 4, identical to F(n+1)). So
   whatever this is, it is shared by a number that has nothing in common with n + 1 except its
   residue mod 2^17 and its size: it is not the arithmetic of n + 1. The placebo for F(n),
   Q(n) = F(n + 2^17), behaves like F(n) (both within 1.5 sd of zero, one cell at +2.9). The null
   stands, with the sharper wording: no dependence that is not a function of n mod 2^17 and of
   size.

Role of 36: none.

---

## Q4.3 Fibres against dropping classes

All fibres phi^-1(m), m <= 10^5, are complete below 10^6 (proof of the bound in the script header):
20254 totient values, 194429 preimages.

**Forced structure (proved, trivial).** x odd implies phi(2x) = phi(x); y coprime to 6 implies
phi(3y) = phi(4y) = phi(6y) = 2 phi(y). Every fibre has as many members 2*odd as odd members
(64816 each). Members divisible by 8 or by 12 belong to neither pattern (108 = 4 * 27 stands
alone in the fibre of 36), so a fibre is not simply a union of such sets. Collatz reads this
structure as plain halvings, and every even member has sigma = 1.
In the fibre of 36: 74 -> 37, 126 -> 63, 114 -> 57, 76 -> 38 -> 19, 108 -> 54 -> 27.

**Beyond doubling (null).** Take the 52863 odd members x >= 3 lying in the 8301 fibres that contain at
least two of them (533373 pairs). Probability that two fibre-mates have the same dropping time:
0.30760. Shuffling sigma among all these x gives 0.30294 +- 0.00255 (z = +1.8); shuffling within
x mod 4 gives 0.30742 +- 0.00046 (z = +0.4); within x mod 16, 0.30788 +- 0.00036 (z = -0.8). The
between-fibre share of the variance of ln sigma is 0.2102; global shuffle 0.1570 (z = +22), within
x mod 4: 0.2092 (z = +0.5), within x mod 16: 0.2107 (z = -0.3), within x mod 4096: 0.2111 (z = -1.3).

So fibre-mates do share dropping behaviour, and the whole effect is that they share residues mod 4
and mod 8 more often than chance (Pr[x = x' mod 4] = 0.53 against 0.50; mod 8: 0.278 against 0.250).
Past x mod 16 there is nothing. Two rows deserve honesty: the mod-8 shuffle gives z = -3.2 for
ln sigma (the mod 16 structure given mod 8 is slightly anti-clustered; the mod-16 shuffle absorbs it),
and the raw eta^2 of sigma, a heavy-tailed statistic, sits near -2 sd for all k >= 2 while the robust
versions do not. I do not read either as evidence of structure.

Mechanism of the residue effect (second pass, `verify/v6_nulls.log`; the pair-agreement numbers above
were reproduced: 0.30760 observed; shuffles within x mod 16, 256, 4096 give z = -0.8, -0.9, -1.2).
Odd fibre-mates are mostly P*y and Q*y with phi(P) = phi(Q) and a common cofactor y: the most
frequent reduced ratios are 7:9, 13:21, 19:27, 25:33, 43:49, 13:15 (from 39:45), 41:55, 35:39. Then
x - x' = (Q - P) y has a forced 2-adic valuation (9 - 7 = 2, 21 - 13 = 27 - 19 = 8, 39 - 35 = 4), so
v_2(x - x') = 1, 2, 3, 4, >= 5 has frequencies 0.4685, 0.2532, 0.1419, 0.0695, 0.0668 against
1/2, 1/4, 1/8, 1/16, 1/16 for independent odd numbers. That is the 0.53 against 0.50 above, and
the 13:21 and 19:27 pairs (same residue mod 8, different mod 16) are the anti-clustering seen in
the mod-8 row. Fibre-mates are 2-adically closer than chance for an arithmetic reason that has
nothing to do with Collatz, and the dropping time, being a function of the 2-adic residue, inherits
exactly that and nothing more.

**Collatz arrows inside fibres (numerology).** Odd x <= 10^6 with phi((3x+1)/2) = phi(x): 59. Chance
level: T(x) = (3x+1)/2 is always 2 mod 3, so a fair null must keep that residue and the parity;
y = T(x) + 6t for t = -25..25, t != 0, gives 62 +- 8 (range 42 to 82), so 59 is at chance level
(z = -0.4). (A null that ignores the residue, y uniform within 10 per cent of T(x), gives 93 +- 10
and would make 59 look like a deficit of 3 sd: a trap.) Curiosities with 3-smooth totient:
phi^-1(6) = {7, 9, 14, 18} is the single shortcut path 18 -> 9 -> 14 -> 7; phi^-1(1) = {1, 2} is the
trivial cycle; 1729 = 7*13*19 -> 2594 = 2*1297 -> 1297 stays inside phi^-1(6^4). No mechanism.

**The fibre of 36** (sigma = standard steps to drop, repo convention; k = shortcut steps = halvings;
s = odd steps; word = shortcut parity word up to the drop; sig_inf = standard steps to 1):

      x   factorisation   lattice parts   x mod 16  sigma   k   s  dest  word  sig_inf  orbit max   v = x+1     F(v)
     37   37              (2,2)               5        3    2   1    28  10        21       112     2*19         4
     57   3*19            (1,0)+(1,2)         9        3    2   1    43  10        32       196     2*29         5
     63   3^2*7           (1,1)+(1,1)        15       88   54  34    61  (54 letters) 107  9232     2^6          6
     74   2*37            (2,2)              10        1    1   0    37  0         22       112     3*5^2        5
     76   2^2*19          (1,0)+(1,2)        12        1    1   0    38  0         22        88     7*11         5
    108   2^2*3^3         (1,0)+(1,2)        12        1    1   0    54  0        113      9232     109          5
    114   2*3*19          (1,0)+(1,2)         2        1    1   0    57  0         33       196     5*23         6
    126   2*3^2*7         (1,1)+(1,1)        14        1    1   0    63  0        108      9232     127          5

Dropping-time multiset: {1, 1, 1, 1, 1, 3, 3, 88}. The outlier is 63 = 2^6 - 1 (v = 64 climbs to 3^6 =
729 in six odd steps); 63 and 108 both run into the orbit of 27. Nothing here is a property of the
fibre: 37 and 57 are 1 mod 4, 63 is -1 mod 64.

Role of 36: the fibre is the object, but its Collatz data are those of eight unrelated residues.

---

## Q4.4 Geometry to algebra

**Gleason 1988 (prior art).** The regular n-gon is constructible with straightedge, compass and angle
trisector iff n = 2^r 3^s p_1 ... p_k with distinct Pierpont primes p_i > 3 (Amer. Math. Monthly 95,
p. 191), i.e. iff phi(n) is 3-smooth (OEIS A048135; A122254 is the same list started at n = 1). The
same class is constructible by origami.

**What the lattice point (a,b) of phi(n) = 2^a 3^b counts (proved here).**

1. Gal(Q(zeta_n)/Q) = (Z/n)* is abelian of order 2^a 3^b: a composition factors C2, b factors C3.
   The real field Q(cos 2 pi/n) has degree 2^(a-1) 3^b.
2. The minimal number of trisections in any construction of the regular n-gon is exactly b.
   Lower bound: a trisection adjoins a root of 4x^3 - 3x - cos(t), of degree 1, 2 or 3 over the
   current field, and compass steps have degree 1 or 2; so the 3-adic valuation of the degree of the
   field reached is at most the number of trisections, and that field contains Q(cos 2 pi/n).
   Upper bound: the Galois group of the real field is abelian, so there is a tower of real fields
   with steps cyclic of degree 2 or 3, exactly b of them cubic, and each cubic step costs one
   trisection by item 3.
3. Each cubic step is the trisection of an angle whose cosine already lies in the field below; no
   auxiliary square root is needed.

   **Proposition (classical: Kummer theory over K(omega)).** Let K < K' be real fields with K'/K
   cyclic of degree 3, Gal = <tau>, w = e^(2 pi i/3). For y in K' not in K put
   R = y + w tau(y) + w^2 tau^2(y), R~ = y + w^2 tau(y) + w tau^2(y), N = R R~, x = (R^2 + R~^2)/N.
   Then x is in K', K' = K(x), and x^3 - 3x - c = 0 with c = (R^6 + R~^6)/N^3 in K and |c| < 2. So
   x = 2 cos(psi/3) with 2 cos(psi) = c in K.

   Proof. tau(R) = w^2 R and tau(R~) = w R~, and complex conjugation swaps R and R~; so
   N = (1/2)[(y - tau y)^2 + (tau y - tau^2 y)^2 + (tau^2 y - y)^2] > 0 and R^6 + R~^6 are real and
   tau-invariant, i.e. in K. Put alpha = R/R~: |alpha| = 1, tau(alpha) = w alpha, x = alpha + 1/alpha
   is real and x^3 - 3x = alpha^3 + alpha^-3 = c, with |c| <= 2. Expanding,
   x N = 2y^2 - (tau y)^2 - (tau^2 y)^2 - 2 y tau(y) - 2 y tau^2(y) + 4 tau(y) tau^2(y), so x is in
   K'. If x were in K then tau(x) = x gives alpha^2 = w^2, so alpha^3 = +-1 and R^3 is real or
   purely imaginary, i.e. R^3 (which is tau-invariant, hence in K(w)) lies in K or in sqrt(-3) K.
   Then R^3 or R^6 is an element beta of K with a cube root in K'(w). If beta is not a cube in K,
   K(beta^(1/3)) is a non-normal cubic extension of K inside K'(w), impossible since K'(w)/K is
   abelian; if it is a cube, R or R^2 lies in K(w) and is tau-invariant, contradicting
   tau(R) = w^2 R unless R = 0, i.e. y in K. Hence x generates K' and |c| < 2. QED

   So the tower of Q(cos 2 pi/n) consists of a - 1 square roots and b trisections of this kind:
   **the lattice point (a,b) counts exactly the quadratic and cubic steps needed to reach the number
   cos(2 pi/n)** (and one more square root gives sin(2 pi/n), unless 4 divides n, when it is already
   there). The seed sentence "each [of the eight polygons] needs one square root and two
   trisections" is correct: the real field has degree 18 = 2 * 3^2.

   Gleason's own construction of the heptagon uses sqrt(7) (he trisects the angle with
   cos(psi_G) = 1/(2 sqrt 7), solving each cubic by x = 2 sqrt(-p/3) cos(psi/3)); that square root is
   a feature of the method, not of the polygon. Trisecting the doubled angle removes it: with
   cos(psi) = 13/14 the three numbers x_m = 2 cos((psi + 2 pi m)/3) generate Q(cos 2 pi/7), and
   explicitly 2 cos(2 pi/7) = -1/3 + x_0 + x_1/3 (checked to 50 digits). In general the
   cubic subfield of Q(zeta_p), p = 1 mod 3, 4p = L^2 + 27 M^2, is Q(cos(psi/3)) with the RATIONAL
   cosine cos(psi) = +-(L^2 - 27 M^2)/(4p): 13/14 for p = 7, 1/26 for 13, 11/38 for 19, 47/74 for 37
   (this is the classical G^3 = p J for the cubic Gauss sum, J = (L + 3M sqrt(-3))/2, read as
   e^(i psi) = J/J~; verified in exact integer arithmetic in Z[zeta_p] for p = 7, 13, 19, 37, 73, 97,
   109; `verify/v4_polygons.log`). For the eight polygons:

       n            square root   first trisection (cos psi)    second trisection
       37, 74       sqrt(37)      47/74                         nested: 2 cos(psi') in the cubic field
       57, 114      sqrt(57)      11/38                         nested (the 19-gon)
       76           sqrt(19)      11/38                         nested (the 19-gon)
       108          sqrt(3)       -1/2 (psi = 120 deg, 9-gon)   nested: cos(psi') = cos(2 pi/9) (27-gon)
       63, 126      sqrt(21)      13/14 (7-gon)                 independent: -1/2 (9-gon)

   Small cases of the same dictionary: the decagon is the point (2,0), one square root and no
   trisection, which is the statement cos 36 deg = (1 + sqrt 5)/4 = half the golden ratio; the
   heptagon and the nonagon are (1,1), no square root and one trisection (cos psi = 13/14 and -1/2);
   the 36-gon itself is (2,1), phi(36) = 12: sqrt(3) and one trisection (10 deg = 30 deg / 3).

   The nested steps were checked to 50 digits (c is tau-invariant, x = 2 cos(psi/3)). To draw the
   angle psi from its cosine one also needs sin(psi), which lies in sqrt(3) K because the
   discriminant 27(4 - c^2) of x^3 - 3x - c is a square in K; so a compass-and-trisector drawing
   uses the 60-degree angle as well, once.

Gleason's proof (as summarised by Bolker in the Gleason memorial volume) is the tower of quadratic and
real-rooted cubic adjunctions; I could not open his text, so I do not know whether he states the
count b or the square-root-free form. Both are elementary corollaries and are proved above.

**The decomposition is the group structure (proved, standard).** The lattice decomposition of (a,b)
attached to n in Theorem 1 is the primary decomposition of (Z/n)*: a Pierpont point (i,j) is a factor
C_(2^i) x C_(3^j); 3^beta gives C_2 x C_(3^(beta-1)); 2^alpha gives C_2 x C_(2^(alpha-2)) (alpha >= 2).
Checked by brute force for all 1472 n <= 20000 with 3-smooth phi(n) (and, counting 2-power and
3-power roots of unity instead, for all 1808 such n <= 30000). For the eight polygons:

      n    parts of (2,2)          (Z/n)*              real field group    the two trisections
     37    37:(2,2)                C4 x C9             C2 x C9             nested (cyclic of order 9)
     74    37:(2,2)                C4 x C9             C2 x C9             nested
     57    3:(1,0) + 19:(1,2)      C2 x C2 x C9        C2 x C9             nested
     76    4:(1,0) + 19:(1,2)      C2 x C2 x C9        C2 x C9             nested
    114    3:(1,0) + 19:(1,2)      C2 x C2 x C9        C2 x C9             nested
    108    4:(1,0) + 27:(1,2)      C2 x C2 x C9        C2 x C9             nested
     63    9:(1,1) + 7:(1,1)       C2 x C2 x C3 x C3   C2 x C3 x C3        independent (7-gon and 9-gon)
    126    9:(1,1) + 7:(1,1)       C2 x C2 x C3 x C3   C2 x C3 x C3        independent

Three of the four abelian groups of order 36 occur; C4 x C3 x C3 does not. So the partition of b
inside the decomposition says whether the b trisections are nested or independent: that is the honest
content of "the lattice bridges geometry and algebra" for this fact.

Role of 36: genuine and specific to (2,2): two trisections, split 2 or 1 + 1.

**Is A(a,b) a "number of dropping classes"-like quantity? No (null).**

* Sequences. A100982 = 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, ... (recomputed here by path counting).
  A(a,a) = 2, 4, 8, 19, 39, 82, 166, 322, 610, 1126, ...; the row b = 1, the column a = 2, the
  anti-diagonal sums and A along the Collatz staircase were compared, with first differences and
  partial sums, at shifts 0..5: no match of six consecutive terms.
* Growth. A100982 grows exponentially (limiting ratio 2^(h(log_3 2) log_2 3) = 2.84, the entropy of
  paths along the critical slope); A(a,a) has consecutive ratios 2.10, 2.02, 1.94, ..., 1.48 falling
  to 1, i.e. exp(c sqrt(L)).
* Support. Dropping classes live on the staircase k = floor(s log_2 3) + 1, one cell per s, and
  not-yet-dropped words live strictly on the side 3^s > 2^j. A(a,b) is positive on the whole quadrant
  a >= 1 and (conjecturally) symmetric across the line.
* Species. A counts unordered sets of distinct parts from a sparse set (partitions); Collatz counts
  ordered unit steps constrained by a line (paths). Different combinatorial objects on one lattice.

---

## Q4.5 Fibre multiplicity inside Collatz

M(d) = #{n >= 2 : dest(n) = d}. Computed for all d <= 5*10^6 from n <= 10^7 (and again, with the
standard map and other code, for all d <= 10^7 from n <= 2*10^7: `verify/v3_destination.log`).

**(a) proved.** n/2 <= dest(n) < n: the step into dest(n) decreases, so it is a halving from 2 dest(n),
and 2 dest(n) >= n. Hence the fibre of d lies in (d, 2d], is finite, and contains 2d: M(d) >= 1.

**(b) proved.** If 3 | d then M(d) = 1. Proof: let dest(n) = d, n != 2d. The orbit from n to d contains
an odd step (otherwise n = 2^j d and dest(n) = n/2 forces n = 2d). After the last odd step, from
m, only halvings follow: (3m+1)/2 = 2^j d with j >= 1, so 3m + 1 = 2^(j+1) d and 3 does not divide d.
QED. Also M(d) >= 2 for d = 1 mod 3, d > 1 (take n = (4d-1)/3).
This is the textbook fact that a multiple of 3 has no odd predecessor (3m + 1 is never divisible by
3: the multiples of 3 are the leaves of the Collatz tree), read through the dropping destination.

So multiplicity one has density at least 1/3: **the opposite of a Carmichael-type statement.**

**(c) proved on the verified range.** By Terras, on a dropping class n = r + 2^k t the first k parities
are constant and T^k(n) = d_r + 3^s t. Terras' coefficient stopping time equals the dropping time for
every 2 <= n <= 10^7 (checked here; known far beyond; open in general), so on that range

    M(d) = #{dropping classes (r, k, s) : d = d_r (mod 3^s), (d - d_r)/3^s >= t_min(r)},

t_min = 1 for r in {0, 1} and 0 otherwise. The dropping time is a locally constant function of n in
the 2-adic topology; **the destination multiplicity is a locally constant function of d in the 3-adic
topology** (more exactly: each class contributes the indicator of d = d_r mod 3^s restricted to
d >= d_r, so every truncation M_K is eventually periodic with period 3^S, and M is their increasing
limit; classes with large k add a set of small density). Checked: the formula with k <= 24 (81119
classes) is a lower bound for M(d) everywhere and exact for 98.7 per cent of d <= 300000; and with
the classes rebuilt by brute force over residues mod 2^16 (791 classes),
#{n : dest(n) = d, k(n) <= 16} equals the class count for every d <= 200000 without exception.

**(d) computed.**

      m    frequency (d <= 5*10^6)    least d            m    frequency    least d
      1        0.531321                  1               10    0.000144       6275
      2        0.337621                  2               11    0.000062        767
      3        0.078480                 20               12    0.000026      17479
      4        0.028869                 10               13    0.000012      81388
      5        0.015371                 91               14    0.000004    1000226
      6        0.004822                122               15    0.000003     348391
      7        0.002065                 61               16    4e-7         795134
      8        0.000859               1144               17    4e-7         293501
      9        0.000340               3844

* Pr[M = 1] = 0.5313 = 1/3 + (1/3)(0.594): all d = 0 mod 3, no d = 1 mod 3 except d = 1, and 59.4 per
  cent of d = 2 mod 3. The exact 3-adic density of {M_K = 1} for the truncation k <= K decreases:
  0.5556 (= 5/9), 0.5432 (= 44/81), 0.5368 (= 1174/2187), 0.5354, 0.5336, 0.5330 for
  K = 4, 8, 12, 16, 20, 24. The natural density of {M = 1} exists (the classes with k > 24 meet a set
  of d of density at most sum_{s > 15} N(s)/3^s = 0.0233) and lies in [0.5097, 0.5330].
* **Mean multiplicity = sum_{s >= 0} N(s)/3^s = 1.6903605922** (proved), N(s) = A100982 (N(0) = 1);
  it is also the mean of n/dest(n). Observed 1.690363 (d <= 5*10^6), 1.690397 (d <= 10^7).
  Proof. (1/D) sum_{d <= D} M(d) = #{n : dest(n) <= D}/D. A class (r, k, s) contributes the n with
  d_r + 3^s t <= D, i.e. D/3^s + O(1) of them, so the liminf is at least sum_{k <= K} N/3^s for every
  K. For the upper bound, dest(n) <= D forces n <= 2D, and the n <= 2D outside the classes with
  k <= K number at most 2D delta_K + O_K(1), where delta_K -> 0 is the density of residues mod 2^K
  not yet dropped (Terras 1976; Everett 1977). The series converges because
  N(s)/3^s <= 2 N(s)/2^k(s) and sum N(s)/2^k(s) = 1. QED
* **Mean of dest(n)/n = sum_s N(s) 3^s/4^k(s) = 0.6199493034 = 1 - p** (second pass; proved the same
  way, dest(n)/n being bounded and tending to 3^s/2^k along each class; observed 0.619956 for
  n <= 2*10^7). Here X_j = 3^(s_j)/2^j is a martingale under fair parity bits (the two letters
  multiply it by 3/2 and 1/2), so for every j

      sum over classes dropped by step j of 3^s/4^k  +  sum over words alive at step j of 3^s/4^j  =  1

  exactly (checked in rationals for j <= 40), and p = 0.3800506966 is the probability that the
  size-biased walk (odd step with probability 3/4) never drops. Sign-blind like everything else here
  (the word counts are the same for 3x-1); not found in OEIS by its digits.
* Ford-type question: every multiplicity from 1 to 17 occurs for d <= 5*10^6, and 18 for d <= 10^7
  (first at d = 7789084); the record grows slowly (7, 11, 11, 13, 17, 17, 18 for d <= 10^2, ..., 10^6,
  5*10^6, 10^7). d = 293501 has 17 preimages with shortcut dropping times from 1 to 83. "Every
  m >= 1 occurs" is a conjecture I did not prove.
* The pair (k, d) almost determines n: among 10^7 values of n only two pairs repeat
  (n = 311291, 311295 and n = 9534459, 9534463: orbits that merge before they drop).

Comparison with the totient: there multiplicity 0 is common, 1 conjecturally never occurs
(Carmichael), every k >= 2 occurs (Ford). For dropping destinations 0 never occurs, 1 occurs for 53
per cent of d, and all small m occur. The analogy is in name only.

**Mirror test.** 3x-1 gives the same picture to four digits (mean M = 1.69033, max 18, the same
distribution; M = 1 on every multiple of 3). This is forced: the classes are counted by the same
A100982 and the 3-adic measure is symmetric under d -> -d. 5x+1 differs (17.6 per cent of n <= 2*10^6
do not drop within the cap, mean M = 1.454, M = 1 on every multiple of 5). Sign-blind, hence no
bearing on the conjecture.

Prior art: the affine structure of dropping classes is Terras 1976; the counts are OEIS A100982; the
3-adic reading is the standard one (Lagarias 1985; Wirsching 1998 for predecessor sets). I found the
sequence M(1), M(2), ... = 1, 2, 1, 2, 2, 1, 2, 1, 1, 4, ... and the constant 1.69036059 absent from
OEIS (searched by terms and by digits). I did not search the Collatz literature further; this is a
routine consequence of known structure, not a discovery.

Role of 36: none.

---

## Side question: where the Pierpont lattice meets the cycle lattice

37 = 2^2 3^2 + 1 is the Pierpont point (2,2), and 37 = 2^6 - 3^3 is the cycle denominator of the
Collatz cell (k,s) = (6,3). All solutions of 2^k - 3^s = 2^i 3^j + 1 (the list is complete, see the
theorem below):

    (k,s) = (2,0) 3;  (3,0) 7;  (3,1) 5;  (4,1) 13;  (4,2) 7;  (5,3) 5;  (6,2) 55;  (6,3) 37;  (8,5) 13.

With s >= 1 there are seven, the largest prime is 37 and the largest k is 8.

**Theorem (the list is complete; proved, given Ellison's theorem).** The equation
2^k = 1 + 3^s + 2^i 3^j (k >= 1; s, i, j >= 0) has exactly the nine solutions above.
Proof. (1) i >= 1 by parity and i < k; 3^s + 1 = 2^i (2^(k-i) - 3^j) with the bracket odd, so
i = v_2(3^s + 1), which is 1 for s even and 2 for s odd. (2) s = 0: 2^(k-1) = 1 + 3^j, so
(k-1, j) = (1,0), (2,1) (Levi ben Gerson). (3) s >= 1, j = 0: s even gives 2^k = 3^s + 3, impossible;
s odd gives 2^k - 3^s = 5. (4) s >= 1, j >= 1: 2^k = 1 mod 3, so k = 2K and
v_3(2^k - 1) = 1 + v_3(K). If j > s this valuation is s, so 3^s <= 3K and
0 < 2^(k-i) - 3^j = (1 + 3^s)/2^i <= (1 + 3k/2)/2. If j < s it is j, so 3^j <= 3K and
0 < 2^k - 3^s = 1 + 2^i 3^j <= 1 + 6k. If j = s then 2^k - 1 = 3^s (1 + 2^i): i = 1 gives
2^k - 3^(s+1) = 1, so s = 0; i = 2 gives 4^K - 1 = 5 * 3^s with 3^(s-1) | K, only K = 2, s = 1.
(5) So every remaining case is 0 < 2^x - 3^y <= 6x + 13 with y >= 1, x in {k, k-1, k-2}. Ellison
(1971, Theorem 3): |2^x - 3^y| > 2^x e^(-x/10) for all positive integers x, y with x not in
{1, ..., 11, 13, 14, 16, 19, 27}; for x >= 28 the right side exceeds 10^7. Hence k <= 29, and the
exhaustive search (k <= 2000 in `verify/v5_sunit.py`, also in the loop order i, s, j) finishes. QED
(Independently of Ellison, 0 < 2^x - 3^y <= 6x + 13 was checked to have no solution with
8 < x <= 6000.) The statement is also a special case of Alex and Foster 1992, who determined all
solutions of 1 + x + y = z in integers composed of 2, 3 and 5 by congruence arguments; their table
was not consulted.

So "37 is the largest prime 2^k - 3^s (s >= 1) of Pierpont form" is a theorem. Its bearing on 36 is
another matter (status of the role of 36: coincidence):

* It is the same identity as the cuban one below: 2^6 - 3^3 = 4^3 - 3^3 = 3*3*4 + 1, the difference
  of the cubes of the consecutive 3-smooth numbers 3 and 4. Four of the nine solutions arise this
  way from squares and cubes of Gersonides pairs (2^2 - 1 = 3, 2^4 - 3^2 = 7, 2^3 - 1 = 7,
  2^6 - 3^3 = 37). X-a and X-b are one coincidence, not two.
* 36 is one of five values: the 3-smooth m with m + 1 = 2^k - 3^s, s >= 1, are 4, 6, 12, 36, 54; the
  denominators 5 and 13 even occur twice (5 = 2^3 - 3 = 2^5 - 3^3, 13 = 2^4 - 3 = 2^8 - 3^5). 36 is
  singled out only by the superlative "largest with m + 1 prime".
* On the mirror side the superlative moves. For 3x-1 a positive cycle needs 3^s > 2^k, and
  3^s - 2^k = 2^i 3^j + 1 has the nine solutions 7, 25, 5, 19, 73, 65, 49, 17, 217 (k <= 400); its
  largest prime is 73 = 3^4 - 2^3 = 72 + 1. The same sentence about 3x-1 names 72, not 36.
* There is no mechanism connecting "37 is a cycle denominator" to the fibre count.

Note (6,3) is not on the dropping staircase (k(3) = 5); the staircase cells in the list are (4,2),
(5,3), (8,5). Mirror test: the equation itself depends on the sign (2^k - 3^s against 3^s - 2^k) and
on the multiplier (for q = 5: denominators 3, 3, 11, 3, 251), but it is a statement about S-units
and says nothing about orbits.

**Cuban primes (proved core, otherwise numerology).** 7 = 2^3 - 1^3, 19 = 3^3 - 2^3, 37 = 4^3 - 3^3.
(n+1)^3 - n^3 = 6 T_n + 1 is of Pierpont form iff n(n+1) is 3-smooth iff n in {1, 2, 3, 8} (the
consecutive 3-smooth pairs, Levi ben Gerson: this is a proof, not only a search), and 217 = 7*31 is
composite. So the Pierpont cuban primes of the first kind (differences of consecutive cubes) are
exactly 7, 19, 37, and they are exactly the primes that build the fibre of 36. The restriction to
the first kind matters: cuban primes of the second kind, ((n+2)^3 - n^3)/2 = 3(n+1)^2 + 1, are of
Pierpont form whenever n + 1 is 3-smooth (13, 109, 193, 433, 769, 3889, 12289, ...; 23 of them with
n < 10^5), and the first of them is 13 = 2^2 3 + 1, one of the two Pierpont primes that divide NO
solution of phi(x) = 36. This ties three of the owner's facts together (36 = 1^3 + 2^3 + 3^3 = T_3^2;
36 = 6 T_3; the eight solutions) through one small identity: T_3^2 = 6 T_3 because T_3 = 6. But the
fibre needs the points (1,1), (1,2), (2,2) for the structural reason in Q4.1, and that these are
6 T_1, 6 T_2, 6 T_3 is a coincidence of small numbers. Label: numerology with a true statement inside.

---

## Null results and dead ends, plainly

* Critical slope: nothing singular; ridge near but not on the line; consistent with random sets
  (two independent estimators, 200 and 120 control sets).
* F against sigma and sig_inf: no dependence that is not a function of n mod 2^k and of size. For
  F(n) and sigma, n mod 16 is enough. For F(n+1) the residues matter up to high k (through
  v_2(n+1)); a placebo number with the same residue mod 2^17 reproduces what is left at k = 8, 12.
  Replicated on the disjoint range (10^7, 4*10^7].
* Fibre membership against dropping time: no dependence beyond x mod 16; the residue effect itself is
  explained (fibre-mates are P*y and Q*y with phi(P) = phi(Q)).
* A(a,b) against A100982: no relation.
* Carmichael analogue for dropping destinations: false in the strongest way (density 0.53 of ones).
* Dead end: a Bateman-Horn constant for the density of Pierpont primes. The partial Euler products
  3 prod (1 - f_q)/(1 - 1/q) keep falling over the range computed (2.80, 2.77, 2.62, 2.46, 2.38 for
  q <= 10^2, ..., 3*10^5); the local factors are not 1 + O(1/q^2) because the subgroup generated by 2
  and 3 mod q is proper for a positive density of q. That is an observation, not a proof of
  divergence. No constant is claimed; the empirical kappa = 3.465 is used.
* Trap recorded: stratifying size by octave manufactures 0.02 bits of "dependence" between F and
  sig_inf. The bin-width scan in `q42_independence.log` is the cure.
* Trap recorded (second pass): a pooled 3 x 3 sign-table chi-square over pairs (n, n + 2^k) gave
  chi^2 = 59 at k = 16. It is not a valid test: the residue classes have different marginal
  distributions and pooling them creates association. Dropped; the placebo test replaces it.
* Withdrawn: the residual partial correlation of -0.0009 between F(n) and the stopping times (first
  pass, 1.3 to 1.9 s.e.) is absent on (10^7, 4*10^7] (+0.0003 and +0.0002, s.e. 0.0004, sign
  unstable across sub-ranges).
* Not done: a proof of the leading-order asymptotics of ln A; tables beyond L = 660.

## Prior art

* R. D. Carmichael, On Euler's phi-function, Bull. AMS 13 (1907) 241-243; Note, 28 (1922) 109-110.
* S. S. Pillai, On a function connected with phi(n), Bull. AMS 35 (1929) 837-841.
* H. Shapiro, An arithmetic function arising from the phi function, Amer. Math. Monthly 50 (1943) 18-30.
* P. A. Catlin, Concerning the iterated phi-function, Amer. Math. Monthly 77 (1970) 60-61.
* P. Erdos, A. Granville, C. Pomerance, C. Spiro, On the normal behavior of the iterates of some
  arithmetic functions, Analytic Number Theory (Birkhauser 1990) 165-204.
* T. D. Noe, Primes in classes of the iterated totient function, J. Integer Seq. 11 (2008) 08.1.2.
* K. Ford, The number of solutions of phi(x) = m, Ann. of Math. 150 (1999) 283-311.
* A. M. Gleason, Angle trisection, the heptagon, and the triskaidecagon, Amer. Math. Monthly 95
  (1988) 185-194 (summary by E. Bolker in the Gleason memorial pages, celebratio.org).
  R. C. Alperin, Trisections and totally real origami, arXiv:math/0408159.
* P. E. Conner, R. Perlis, A Survey of Trace Forms of Algebraic Number Fields (World Scientific
  1984): the trace form of a Galois extension of odd degree is the unit form (one way to see the
  generator x^3 - 3x - c of a cyclic cubic step; the Kummer-theory proof is given in Q4.4). Cited
  from memory, not opened.
* R. Terras, A stopping time problem on the positive integers, Acta Arith. 30 (1976) 241-252.
  C. J. Everett, Iteration of the number-theoretic function f(2n) = n, f(2n+1) = 3n+2, Adv. Math. 25
  (1977) 42-45.
* W. J. Ellison, On a theorem of S. Sivasankaranarayana Pillai, Sem. Theorie des Nombres de Bordeaux
  1970-71, exp. 12 (numdam.org): |2^x - 3^y| > 2^x e^(-x/10) for x outside
  {1, ..., 11, 13, 14, 16, 19, 27}. Read for this pass.
* L. J. Alex, L. L. Foster, On the Diophantine equation 1 + x + y = z, Rocky Mountain J. Math. 22
  (1992) 11-62 (all solutions with xyz = 2^r 3^s 5^t; cited from their 1995 sequel in Rev. Mat.
  Univ. Complut. Madrid 8, which was read; the 1992 table itself was not).
* R. Tijdeman, L. Wang, Sums of products of powers of given prime numbers, Pacific J. Math. 132
  (1988) 177-193.
* Wikipedia, "Pierpont prime": 42, 65, 157, 795 Pierpont primes below 10^6, 10^9, 10^20, 10^100, and
  Gleason's estimate of 9 per decade.
* OEIS: A014197, A007374 (fibre sizes); A058321, A058213 (phi(x) = 2^n); A003434, A064415, A007755
  (iterated totient); A005109 (Pierpont primes); A048135, A122254 (3-smooth totient); A100982,
  A122437 (dropping classes).

## Leads not finished

* Prove ln A(a,b) ~ 2 sqrt(c L m(theta)) under an explicit density hypothesis on Pierpont primes (a
  two-dimensional Meinardus theorem). The saddle statement "ridge = weighted centre of mass of the
  Pierpont points" is the precise form of the symmetry and is testable far beyond these tables. The
  constant c is not pinned down by the present data.
* The 3-adic density of {M = 1} (between 0.5097 and 0.5330, observed 0.5313) and the two constants
  sum A100982(s)/3^s = 1.6903605922 and sum A100982(s) 3^s/4^k(s) = 0.6199493034: are they in the
  Terras-Lagarias literature under another name? Is M unbounded, and does every m occur (1..18 seen)?
* Read Alex-Foster 1992 and confirm that their table contains exactly the nine solutions of
  2^k - 3^s = 2^i 3^j + 1; prove completeness of the mirror list 3^s - 2^k = 2^i 3^j + 1 the same way.
* Read Gleason 1988 for what he says about the number of trisections and about avoiding the
  auxiliary square root.

## Skeptic pass

A second pass re-derived every claim with independent code (`verify/`, logs next to the scripts),
on wider ranges where that was cheap, and edited this file in place. What changed:

Corrected

* Q4.4-a, item 3. The first pass said a construction needs "more than one square root" because each
  cubic step needs an auxiliary sqrt(-p/3) outside the field, and called the seed sentence ("one
  square root and two trisections") wrong about the square roots. That was wrong. Every cyclic cubic
  step between real fields is K(2 cos(psi/3)) with 2 cos(psi) in K (proved in Q4.4; exact check for
  p = 7, 13, 19, 37, 73, 97, 109; 50-digit check for the nested steps of 19, 27, 37). The heptagon
  field is Q(cos(psi/3)) with cos(psi) = 13/14. The seed sentence is right.
* X-a. Upgraded from "computed for k <= 1500" to a theorem (valuations plus Ellison 1971; contained
  in Alex-Foster 1992), and its "role of 36" downgraded from genuine to coincidence: it is the same
  identity as X-b (2^6 - 3^3 = 4^3 - 3^3), 36 is one of five values, and the mirror equation names
  72. "Sign-blind" replaced by the accurate statement.
* X-b. "The Pierpont cuban primes are exactly 7, 19, 37" holds only for cuban primes of the first
  kind; 13 = 2^2 3 + 1 is a Pierpont cuban prime of the second kind and divides no solution.
* Q4.1-g. The centre of mass was quoted for the cutoff 329, not 329.6: at the full cap there are
  1142 points (not 1138) and theta_cm = 0.4975, not 0.4996. The count per decade is prior art.
* Q4.1-e. "Fitted coefficients 2 to 6 per cent above the heuristic" is fit-dependent (3.26 to 3.55
  against 3.376 on the critical ray); the claim is now limited to the exponent and the shape.
* Q4.2-a. Shapiro's formula C(mn) = C(m) + C(n) + [both even] needs m, n >= 2 (or C(1) = 0).
* Q4.2-c. The invariant holds equally for 3x+5 and 3x+7 (which have other cycles), for negative n,
  and with v_2 + v_3 in place of F: it is about the multiplier 3 only.
* Q4.2-d. The residual correlation of -0.0009 did not replicate and is withdrawn. "F(n+1) is gone by
  k = 12" is true for sigma; for sig_inf about 1e-4 bits remain at k = 8 and 12, and a placebo
  (another number with the same residue mod 2^17) shows the same, so it is residue-mediated.
* Q4.3-a. "Fibres are unions of {y, 2y} and {3y, 4y, 6y}" was false as worded (108 is in neither).
* Q4.3-c. The chance level for arrows inside fibres is 62 +- 8, not 93 +- 10 (T(x) = 2 mod 3 always).
* Q4.2-b. Marked as a relabelling: sigma = k + s = H(2^k 3^s) holds by definition of both sides.

Added

* The mean of M(d) is proved (not only computed) to be sum A100982(s)/3^s; the mean of dest(n)/n is
  sum A100982(s) 3^s/4^k(s) = 0.6199493034 = 1 - p by a martingale identity that is exact at every
  level; multiplicity 18 occurs (d = 7789084); the density of {M = 1} exists.
* The exact table A(a,b) for a <= 480, b <= 300; the mechanism of the residue effect in fibres;
  controls for "36 is special" (other m with eight solutions, other triples of primes).
* Prior art: A058321/A058213, Ellison, Alex-Foster, Everett, Conner-Perlis, the published Pierpont
  counts.

Confirmed without change

* Theorem 1 and the table (three independent ways, including an inverse-totient recursion for all
  a,b <= 22); the eight decompositions; A007374 (35 terms); Pillai-Shapiro to 3*10^7; the structure
  of (Z/n)* for the eight n and for all 1808 n <= 30000 with 3-smooth totient; no match with
  A100982; Q4.5-a, b and the distribution in Q4.5-c to d <= 10^7, with the same mirror behaviour
  (3x-1 identical to four digits with the residues 1 and 2 mod 3 exchanged; 5x+1 different); the
  ridge and its random controls; the fibre null; the Collatz data of the eight solutions.

Could not check

* The texts of Gleason 1988, Pillai 1929, Shapiro 1943, Noe 2008, Tijdeman-Wang 1988, Conner-Perlis
  1984 and the table of Alex-Foster 1992 were not opened; statements attributed to them rest on
  secondary sources (OEIS, Wikipedia, the Bolker summary, an arXiv abstract) and on the proofs
  given here.
* Completeness of the mirror list 3^s - 2^k = 2^i 3^j + 1 beyond k = 400.
* Not recomputed: the mirrored-point-set control, the second-difference and symmetry tables and the
  full saddle (with absorption terms) of Q4.1-f (smoothness was checked by a quartic residual and
  the saddle in its points-only form); the eta^2 variants of Q4.3 (only the pair-agreement
  statistic was redone); the group-type census of Q4.4 beyond (2,2); the 3-adic densities of
  {M_K = 1} for K = 16, 20, 24 (K = 4, 8, 12 were redone exactly).
* The heuristic of Q4.1-e beyond L = 660, and whether the Euler product of the dead end diverges.
* Whether M(d), the constants 1.69036 and 0.61995, or the array A(a,b) appear in the literature
  outside OEIS; only OEIS term and digit searches and a few web searches were made.
