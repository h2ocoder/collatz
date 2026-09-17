---
tags: [collatz, prime-factorization, dropping-class, 2-adic, circuit, research-questions]
status: results-and-questions
created: 2026-09-16
---

# Primes and the Circuit

**Question (from the user).** The circuit multiplies by 3 and adds 1. Can we inspect its behaviour — trits, bits, contraction, dropping class — against the **prime factorisation** of n? What happens when prime powers sit deep in the number? Is there anything the 5-unit gate could "figure out" about factorisation, and could factorisation tell us something about orbits?

Script: `scripts/primes_and_circuit.py`; results `results/primes_and_circuit.json`. Six exact facts first (all **Verified**), then the questions they leave open.

## 1. The structural fact that shapes everything

The circuit reads n least-significant bit first, and every first-drop quantity — dropping class, slope 3^s/2^b, intercept C — is a function of **n mod 2^b** ([[Collatz Bridge - Trits and Stopping Times]]; Terras). The prime factorisation of n is information about n *modulo odd primes*. By the Chinese Remainder Theorem those two kinds of information are independent: fixing n mod p^a for odd p leaves n mod 2^b uniformly distributed. So:

**A. Odd prime powers cannot bias the dropping class.** Among odd multiples of 5, 7, 25, 49, 121, 343 (n < 2²⁰), the class distribution equals the overall one to within sampling noise (max deviation 0.0009 at p^a = 343, where there are only 1,529 multiples). The 5-unit gate is blind to every odd prime factor of n — exactly, not approximately.

**B. Every odd step resets the factorisation.** gcd(3n+1, n) = 1, so whatever odd primes divide n, none divides 3n+1. Prime powers "deep in the number" survive only through an initial run of halvings (if n is even) and die at the first ×3+1. Along a Syracuse orbit, consecutive odd values have coprime factorisations. The known special case is the repo's 3-adic lock (3 never divides any value after the first odd step).

Together: **factorisation of n does not propagate into the orbit, and the orbit's first-drop behaviour does not see it.** The remaining structure is all 2-adic, and there it is rich.

## 2. Where "prime powers deep in the number" *do* act: the power of 2 — Verified

**F. v₂(n+1) = the number of consecutive odd steps at the start of the orbit** (all odd n < 200,001). A number n ≡ −1 (mod 2^k) — i.e. 2^k dividing n+1, or k trailing 1-bits — runs k Terras steps (3x+1)/2 in a row before its first halving, climbing to ≈ (3/2)^k·n. This is Charton–Narayanan's k, the repo's v₂(m+1) countdown, and the one "prime power deep in the number" the circuit reads directly: it is the length of the trailing run of ones. Mersenne numbers 2^k − 1 are the extreme case. Nothing analogous exists for odd primes: n ≡ −1 (mod 3^j) gives 3n+1 ≡ −2 (mod 3^j), which does nothing.

## 3. Prime powers and squares as *residue classes* — Verified, provable

**B′. Every odd square, hence every even power of an odd prime, has stopping time 3.** Odd m ⇒ m² ≡ 1 (mod 8) ⇒ m² ∈ Set₃ (n ≡ 1 mod 4). Checked for all odd m ≤ 1023. Trivial once seen, but it is a genuine "factorisation ⇒ class" implication — the only kind that exists, because it is a statement about n mod 8.

**C. The class sequence of p, p², p³, … is periodic, with a mod-4 skeleton.** Odd a: p^a ≡ p·(square) has the mod-4 residue of p; even a: ≡ 1 mod 4 → class 3. So:
- primes ≡ 1 (mod 4) — 5, 13, 17, 29, … — have **every** power in class 3 (verified a ≤ 16);
- primes ≡ 3 (mod 4) alternate: class 3 at even a, and at odd a a periodic sequence governed by the order of p in (Z/2^b Z)^*: 3 → 6, 21, 6, 8, 6, 19, 6, 8, …; 7 → 11, 8, 16, 8, 19, 8, 21, 8; 11 → 8, 6, 21, 6, 8, 6, 11, 6; 19 → 6, 8, 6, 13, 6, 8, 6, 13.

The odd-exponent subsequences have their own period-2 skeleton (p³ mod 32 = p·p² and p² ≡ 1 or 9 mod 16), and the full period is the multiplicative order of p modulo 2^b — a power of 2. So "the class of p^a" is a finite-state function of a: the circuit's view of prime powers is a **cyclic** one.

## 4. The multiplication table of classes — Verified, and it is the mod-4 wall and nothing else

Class(q·n) is a function of (q mod 2^b, n mod 2^b), so given the classes of q and n it is a *distribution*. Computed exactly over residues mod 2¹² (the "≥21" bucket is the 11% undecided at 12 bits):

| class(q) × class(n) | → 3 | 6 | 8 | 11 | 13 | 16 | 19 | ≥21 |
|---|---|---|---|---|---|---|---|---|
| 3 × 3 | **1.000** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 × {6, 8, 11} (any) | 0 | .250 | .250 | .094 | .109 | .047 | .029 | .221 |
| {6, 8, 11} × {6, 8, 11} (any) | **1.000** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Three rows are the whole table. (i) 1 mod 4 × 1 mod 4 = 1 mod 4: class 3 × class 3 = class 3, always. (ii) 3 mod 4 × 3 mod 4 = 1 mod 4: any two "higher" classes multiply to class 3, always. (iii) 1 mod 4 × 3 mod 4 = 3 mod 4, and then **the product's class is the unconditional distribution of the higher classes, whatever the two factors' classes were** — the row is identical for (3,6), (3,8), (3,11). Class-3 numbers act as perfect randomisers of the finer 2-adic structure; the classes of the factors carry *no* information about the product's class beyond the mod-4 bit. This is the repo's Multiplication Symmetry Theorem (×3 flips the mod-4 wall) generalised to arbitrary odd multipliers, and it closes the CLAUDE.md question "does the classification of composites relate to their prime factors' classifications?": **only through the mod-4 wall, and there completely.**

## 5. Where factorisation re-enters: the intercept — Verified

For p | n, dest(n) = (3^s n + C_r)/2^b ≡ C_r·2^{−b} (mod p): **the destination's residue mod p is a constant of the residue class r**, independent of which multiple of p you started from (27 class × prime checks, 0 variations). So whether p goes on dividing the orbit at the first drop is decided by the subgroup's hidden intercept C_r (the "hidden variable" of the Collatz Complementarity Principle). For Set₈'s two classes mod 32, none of 5, 7, 11, 13 survives the drop; 3 never survives anywhere (3-adic lock). Expect a fraction ≈ 1/p of classes to preserve p-divisibility; the census over all classes is Q3 below.

## 6. Research questions

**Q1 (cheap, exact).** *Census of divisibility-preserving classes.* For each dropping set and each residue class r, compute C_r mod p for p ≤ 50. Which classes satisfy C_r ≡ 0 (mod p)? Is the fraction 1/p (random) or biased (as for p = 3, where it is 0)? A bias would be a new "p-adic lock". Script-sized; uses the affine table already in the repo.

**Q2 (cheap, exact).** *The full multiplication table.* Extend §4 to all classes decidable at mod 2^16 and confirm the three-row structure holds at every depth: the claim is that class(qn) depends on (class(q), class(n)) *only* through their mod-4 bits. If a finer dependence appears at any depth, that is a real finding; if not, it is a clean theorem with a two-line CRT proof — write it up as the general form of the Multiplication Symmetry Theorem.

**Q3 (cheap, exact).** *Class of p^a as a function of a.* Prove: period = ord_{2^b}(p), with class 3 at every even a and a period-(ord/2) pattern at odd a; tabulate the odd-a patterns by p mod 32. Then ask the inverse: given the class sequence of p, p³, p⁵, …, what is p mod 2^b? (It determines p's residue up to the depth the classes reach.)

**Q4 (medium, circuit).** *A circuit that sees one odd prime.* Tracking n mod p LSB-first is itself a p-state transducer (state = partial residue, weight 2 per bit). The product with the 5-state Terras machine has ≤ 5p states; its minimal ternary threshold size is the "cost of one prime" in the circuit model — a natural extension of [[Minimal Ternary Circuit]]. The interesting target is p = 3: a circuit that computes the Terras step *and* certifies the 3-adic lock (output never ≡ 0 mod 3) in one pass.

**Q5 (medium, statistical).** *Factorisation along orbits.* Given B, consecutive odd orbit values are coprime; are orbit values otherwise "typical integers coprime to 3"? Compare the distribution of largest prime factor, ω(n), and smoothness along Syracuse orbits with those of random integers coprime to 3 of the same size. The Lagarias–Weiss stochastic model predicts no bias; a measured bias — e.g. an excess of smooth values, or a deficit of primes, beyond the "≢ 0 mod 3" conditioning — would be new. Null result is likely and still worth one table.

**Q6 (speculative).** *Is there any factorisation-shaped input the circuit favours?* The only known ones are 2-adic (§2, §3). A candidate family with mixed structure: n = 2^k·m − 1 for odd m (k trailing ones *and* an odd cofactor); n = (4^j − 1)/3 (alternating bits, the repo's r_k = (4^⌈k/2⌉ − 1)/3 "drop depth" numbers). Enumerate the classes of such families exactly as functions of (k, m) or j; anything that is not explained by n mod 2^b alone would contradict §1 and is therefore a bug-check as much as a question.

## 8. Q1 and Q2 answered (2026-09-17)

Script `scripts/primes_q1_q2.py`; results `results/primes_q1_q2.json`.

### Q2 is a theorem — Verified at mod 2¹⁶, proof in three lines

**Theorem (class multiplication).** Let U = {n ≡ 1 mod 4} ⊂ (Z/2^b Z)^*, the index-2 subgroup. Set₃ *is* U. Hence: (i) class 3 × class 3 = class 3; (ii) any two classes > 3 multiply to class 3 (since (3 mod 4)² ≡ 1); (iii) for q of class 3 and any n, q·n ranges uniformly over the coset n·U = {m ≡ n mod 4}, so class(q·n) is distributed as a **uniform 3-mod-4 residue, independent of n's class**. Checked at b = 16 over all 11 decidable classes: 3×3 → 3 exactly; all 100 higher×higher cells → 3 exactly; every 3×higher row matches the unconditional 3-mod-4 distribution to within 0.0022 (sampling noise ≈ 0.002). *The dropping class of a product depends on the factors' classes only through their mod-4 bits.* This is the general Multiplication Symmetry Theorem; the repo's ×3 case is the row q ≡ 3 mod 4.

### Q1: p-survival at the first drop is an explicit constant, not 1/p — Verified

For p | n, p | dest(n) ⟺ p | r(v), where r(v) = Σ_{vᵢ=1} 2^i 3^(ones after i) is the parity-vector intercept of n's residue class. So the probability that a multiple of p is still a multiple of p after its first drop is Σ{density of classes with p | r(v)} — a fixed number per p, and the heavy classes have small, specific intercepts:

| class | residue | parity word | r(v) | density | factors |
|---|---|---|---|---|---|
| Set₃ | 1 mod 4 | 10 | **1** | 1/2 | — |
| Set₆ | 3 mod 16 | 1100 | **5** | 1/8 | 5 |
| Set₈ | 11 mod 32 | 11010 | **23** | 1/16 | 23 |
| Set₈ | 23 mod 32 | 11100 | **19** | 1/16 | 19 |
| Set₁₁ | 7, 15, 59 mod 128 | | 73, 65, 85 | 1/64 each | 73; 5·13; 5·17 |
| Set₁₃ | 7 classes mod 256 | | 251, 259, 211, 319, 227, 283, 287 | 1/128 each | 251; 7·37; 211; 11·29; 227; 283; 7·41 |

Resulting survival fractions (density-weighted over the 790 classes decidable at 16 bits) vs the naive 1/p:

| p | 3 | 5 | 7 | 11 | 13 | 17 | 19 | 23 | 29 | 31 | 47 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| survival | **0** | **0.190** | 0.030 | 0.014 | 0.022 | 0.022 | **0.075** | **0.071** | 0.011 | 0.004 | 0.002 |
| 1/p | 0.333 | 0.200 | 0.143 | 0.091 | 0.077 | 0.059 | 0.053 | 0.043 | 0.034 | 0.032 | 0.021 |

Reading: 5 survives its first drop 19% of the time because 5 is the intercept of Set₆; 19 and 23 survive 7% because they *are* the two Set₈ intercepts; 7 survives 3% because it first divides an intercept in Set₁₃; 3 never (the 3-adic lock is the p = 3 row of this table). Unweighted, the counts sit near 1/p (e.g. 115/790 for p = 7) — the intercepts are "random" mod p across classes, but the density weighting concentrates everything on a dozen small numbers. **So there is a p-adic lock landscape, and it is explicit: a prime's survival probability at the first drop is the density of the residue classes whose intercept it divides.** The sequence of intercepts 1, 5, 19, 23, 65, 73, 85, 211, 227, 251, 259, 283, 287, … is not in OEIS (searched 2026-09-17); the r(v) formula is Terras's, the sequence as an object appears unlisted.

## 7. What this says

The circuit is a 2-adic instrument, and factorisation is an odd-prime notion; by CRT they do not talk, and by gcd(3n+1, n) = 1 the map erases factorisation every odd step. Everything factorisation-shaped that *does* reach the circuit is a statement about n mod 2^b in disguise — trailing ones (2^k | n+1), squares (≡ 1 mod 8), the mod-4 wall in products. Those are exact, small, and already provable. The one place odd primes genuinely re-enter is the intercept C_r deciding whether p survives the first drop (Q1), which is the same hidden variable the repo already found carrying all mod-p correlations. So the honest recommendation: do Q1–Q3 (a day, all exact, likely a short note generalising the Multiplication Symmetry Theorem); treat Q5 as a control experiment; do not expect factorisation to constrain orbits.

## Sources

1. [[Collatz Bridge - Trits and Stopping Times]] (class = n mod 2^b; slope, intercept); `docs/Conjectures/Affine Orbit Structure.md`, `docs/Conjectures/Multiplication Symmetry Theorem.md`, `docs/Conjectures/Collatz Complementarity Principle.md` (C as hidden variable; 3-adic lock)
2. [[Minimal Ternary Circuit]], [[Experiment B - Base Polarity]] (Charton's k = v₂(n+1))
3. R. Terras (1976); J. C. Lagarias, "The 3x+1 problem and its generalizations" (1985), Theorem C (classes are congruence classes mod 2^k)
4. `scripts/primes_and_circuit.py`, `results/primes_and_circuit.json`
