---
tags: [pinball, mirror-map, three-adic, fibonacci, reversible]
status: verified
created: 2026-09-19
jira: SCRUM-30
---

# The Mirror Table: n → n − |n/2|

Idea: replace the halving step with n → n − |n/2|. For positive n nothing changes. For negative n the "shape" is different. Does that probe orbits, and what does it say about stopping classes?

Code: `collatz/pinball/mirror.py`; five tests in `tests/test_pinball.py`.

Labels: **Proved**, **Verified**, **Barrier**.

## 1. What the map is — Proved

For even n < 0, n − |n/2| = 3n/2. On magnitudes m = |n|:

    m → 3m − 1   (m odd)        m → 3m/2   (m even)

`mirror_orbit(-1, 6) = [-1, -2, -3, -8, -12, -18, -27]`.

- **Every step raises the magnitude.** All negative orbits escape monotonically. The Collatz cycles through −1, −5, −17 do not exist on this table.
- **The map is injective.** Odd magnitudes land on even values ≡ 2 (mod 3); even magnitudes land on multiples of 3. The two images are disjoint and each branch is one-to-one. No two orbits ever merge. Verified for m < 20,000.

## 2. Halvings become powers of three — Proved, Verified

Write 3b − 1 = 2^a·c with c odd. The even steps turn 2^a·c into 3^a·c. So the odd-to-odd map is

    b → 3^a · (3b − 1)/2^a,     a = v₂(3b − 1).

Collatz throws the 2^a away, which is why Collatz orbits merge and the inverse is a branching tree. The mirror table converts 2^a into 3^a and keeps it. **The 3-adic valuation of each odd value records the halving count that produced it** (tested for odd b < 4000). The mirror is a lossless version of the 3x−1 Syracuse map: same α-sequence statistics (α = a with probability 2^−a, measured), but the history is written into the number instead of erased.

## 3. Age classes: the 3-adic mirror of stopping classes — Proved, Verified

Because the map is injective and increasing, walking backwards is deterministic and must stop:

- branch **A**: m = 3p/2, possible iff 3 | m, p = 2m/3
- branch **B**: m = 3p − 1, possible iff m ≡ 2 (mod 6), p = (m+1)/3
- no predecessor iff m ≡ 1 (mod 3) or m ≡ 5 (mod 6) — density exactly 1/2

Define **age(m)** = steps back to a predecessor-free **seed(m)**. Then (seed, age) are unique coordinates for every negative integer: the negative integers are a disjoint union of rays. `age(27) = 6`, `seed(27) = 1`, `age_word(27) = 'AAABAB'`.

| | Stopping class (positive side) | Age class (mirror side) |
|---|---|---|
| Defined by | first time the orbit falls below n | steps back to a value with no predecessor |
| Determined by | n mod 2^(k−s) — **2-adic** | m mod 2·3^t — **3-adic** |
| Allowed words | parity words under the line y = x·log₂3 | words with no "BB" (golden-mean shift) |
| Count | N(s): 1, 1, 2, 3, 7, 12, 30, 85, … | Fibonacci |
| Density | N(s)/2^(k−s−2) among n ≡ 3 mod 4 | **P(age ≥ t) = F(t+3) / (2·3^t)** |
| Map direction | forward, many-to-one, shrinking | backward, one-to-one, shrinking |

**Verified exactly** for t = 1..9: the number of residues mod 2·3^t with age ≥ t is 3, 5, 8, 13, 21, 34, 55, 89, 144; the number of distinct age words is 2, 3, 5, 8, …, 89; none contains "BB". min(age, t) depends only on m mod 2·3^t.

**Why no "BB" (Proved).** Branch B lands on an odd value; branch B can only leave values ≡ 2 (mod 6), which are even.

**Why Fibonacci and not the N(s) sequence.** Stopping classes have a second constraint — the orbit must stay above n, the "below the line" condition — and that irrational boundary is what makes N(s) irregular and Sturmian. Age classes have only the local no-"BB" rule, so they count like Fibonacci. The tail decays like (φ/3)^t ≈ 0.539^t.

So the answer to "what does it say about stopping classes": the mirror table has a clean analogue with the primes swapped. Stopping classes are what you see reading a positive integer's **2-adic** digits forward; age classes are what you see reading a negative integer's **3-adic** digits backward. This is the repo's [[Dual Constraint]] (membership is 2-adic, destinations are 3-adic) turned into two halves of one map.

## 4. Does it probe positive orbits? — Barrier

Honestly: not directly.

- Positive orbits never reach negative values, so changing the negative side changes nothing about any positive orbit.
- The barrier from [[Nesting and the Never-Drain Fractal]] §6 is a statement about *arguments*, not about which map we write down. The original negative Collatz (equivalently 3x−1 on positives) still exists with its cycles, and any argument that would apply to it is still invalid. Redefining the negative side does not remove that test.

What it does give:

1. **A third control system.** The 2-adic parity bijection holds on the mirror side too (verified: all 2^L words occur exactly once mod 2^L for L = 4, 8, 12, using one-halving-per-step form). So we now have three tables sharing the same composition structure with three different global behaviours: positives (conjecturally all drain), Collatz negatives (cycles), mirror negatives (provably all escape). Any proposed structural argument can be run against all three.
2. **A reversible bookkeeping model.** Collatz's difficulty is partly that it forgets. The mirror map shows exactly what is forgotten — the α-sequence — and where it could be stored — the 3-adic valuation.

All four experiments below were run, plus six more: see [[Mirror Experiments]].

## 5. Experiments proposed (now done)

1. **Carry the bookkeeping to the positive side.** Define the lossless lift (n, register) → (T(n), register·3^α). Every positive orbit then has a 3-adic register that encodes its whole α-history. Test: is the register's growth rate versus n's shrink rate the same conservation law already in the repo (s·log₂6 = T − log₂n + ε)?
2. **Seeds as a sieve.** Seeds have density 1/2 and ages decay like (φ/3)^t. Which seeds lie on the ray of −1, −5, −17 (the old cycle members)? Do the three old cycles land on finitely many rays or spread out?
3. **Mixed-radix coordinates.** A positive integer has (k, s, residue mod 2^(k−s), j); a mirror integer has (seed, age word). Test whether the two coordinate systems are independent on |n| (the prediction from the spectral-gap/CRT results is yes).
4. **Age words versus Sturmian words.** The stopping-class sign sequence is Sturmian with slope log₂3; age words are the golden-mean shift. Compare block complexity: n+1 versus Fibonacci growth. Same tools as `scripts/sturmian_block_entropy.py`.
