---
tags: [collatz, ternary, log2-3, information-theory, stopping-time, prior-art]
status: verified
created: 2026-09-16
---

# Collatz Bridge — Trits and Stopping Times

The one place where the ternary-LLM paper and the Collatz research share real mathematics, not just the number 1.585. Every claim is labelled **Verified**, **Conjecture**, **Analogy only**, or **Dead end**.

**Bottom line.** Nothing in the BITCOS paper itself ([[Paper - Breaking the 1.58-bit Barrier]]) transfers to Collatz — no kernel, bitmap or sparsity idea. But the packing arithmetic it rests on, 3^t ≤ 2^b, is *literally the same object* as the odd stopping-time spectrum, and chasing that through OEIS turned up **prior art for two of the repo's headline results**, with bounds the repo does not yet have. That is the real deliverable.

| # | Claim | Label |
|---|---|---|
| 1 | Odd stopping time k(s) = s + ⌈s log₂3⌉ = s + (min bits for s trits) = bitlen(6^s) | **Verified**; known (OEIS A122437, Noe 2006) |
| 2 | Contraction at first drop = 2^(−packing waste); record packings = weakest-contraction sets; five-trit byte ↔ Set₁₃ | **Verified** |
| 3 | Repo's N(s) = OEIS A100982 "admissible sequences" (Wagon 1985, Roosendaal, Zarubin, Winkler) | **Verified** prior art |
| 4 | Dropping classes = complete prefix code on low bits of n; Kraft sum 1; expected length = Wagon's constant 9.4779… | **Verified**; known (A122790) |
| 5 | BITCOS tie point z* = 2 − log₂3 = Collatz per-step drift | **Verified** arithmetic, **Analogy only** |
| 6 | Presence/sign ↔ 2-adic/3-adic or Eisenstein sign split | **Dead end** |
| 7 | Zero density z ≈ 1/3 ↔ odd-step density | **Dead end** |
| 8 | 128-block padding ↔ Three Distance | **Dead end** |

## 1. Odd stopping time = trits + bits — Verified (and known)

The repo's theorem (`docs/Conjectures/Odd Stopping Time Spectrum.md`): for odd n > 1 with s odd steps in its stopping orbit,

$$k(s) = \lceil s \log_2 6 \rceil = s + \lceil s \log_2 3 \rceil = s + \operatorname{bitlen}(3^s) = \operatorname{bitlen}(6^s).$$

Since 3^s is never a power of two, ⌈s log₂ 3⌉ is exactly `bitlen(3^s)`, the smallest b with 3^s ≤ 2^b — the **minimum number of bits needed to store s trits** ([[Trit Packing and log2(3)]]). So:

> **A stopping orbit with s Syracuse steps contains exactly as many halvings as it takes bits to store s trits — and the stopping time is the number of bits in 6^s.**

Integer-exact checks against `collatz.core.stopping_time`:

| Check | Result |
|---|---|
| all odd n in [3, 10⁶): k = s + bitlen(3^s) **and** #halvings = bitlen(3^s) exactly | 0 violations, 103 distinct s, max s = 111 |
| 20,000 random odd 128-bit n | 0 violations, max s = 103 |
| independent re-derivation from the raw map, odd n < 262,144 (agent A) | 0 violations, 80 distinct s |

Scripts: `scripts/stopping_time_trit_bits.py`, `scripts/collatz_packing_check.py`.

**Prior art.** This is OEIS **A122437**, "Allowable values of the dropping time of the Collatz (3x+1) iteration" (T. D. Noe, 2006), with formula a(n+1) = ⌊1 + n + n log₂3⌋ and the comment *"a(n) is also the number of binary digits of 6^(n−1)"* [1]. The bit-count ⌈s log₂3⌉ is **A020914** [4]. The underlying fact goes back to Terras (1976) and is tabulated in Wagon (1985) [2]. The repo's Odd Stopping Time Spectrum is a rediscovery — cite it rather than claim it.

**Is the information reading meaningful?** Partly:
- The parity vector of the first k steps is a k-bit word determined by n mod 2^k (Terras), so a stopping orbit literally *reads* k bits of n.
- Each ×3 adds log₂3 bits of magnitude; each halving removes exactly 1. Dropping needs Σαᵢ ≥ ⌈s log₂3⌉ — the packing inequality 3^s ≤ 2^Σα verbatim. "One bit per trit" is accurate in that sense.
- What it does **not** give: any control on how long n waits for that budget. The inequality is about the first drop of one orbit; divergence is about infinitely many windows. No compression argument here touches that.

## 2. Contraction = packing waste — Verified

Let b(s) = ⌈s log₂3⌉ and w(s) = b(s) − s log₂3 ∈ (0, 1) be the storage waste of an s-trit register. By `docs/Conjectures/Affine Orbit Structure.md`, within each subgroup of Set_k,

$$\operatorname{dest}(n) = \frac{3^s}{2^{b(s)}}\,n + C, \qquad \frac{3^s}{2^{b(s)}} = 2^{-w(s)}.$$

**The asymptotic contraction of a first drop is 2^(−waste): the orbit sheds exactly the bits the packing wastes.**

| s | b(s) | k | w(s) | slope 3^s/2^b | note |
|---|---|---|---|---|---|
| 1 | 2 | 3 | 0.4150 | 0.7500 | the naive 2-bit format |
| 3 | 5 | 8 | 0.2451 | 0.84375 | bitnet.cpp TL2-style 3-in-5 |
| 5 | 8 | 13 | **0.0752** | **0.94921875 = 243/256** | **five trits per byte** (llama.cpp TQ1_0) |
| 12 | 20 | 32 | 0.9805 | 0.5068 | Pythagorean comma: 12 trits *overflow* 19 bits |
| 17 | 27 | 44 | 0.0556 | 0.9622 | next record after the byte |
| 41 | 65 | 106 | 0.0165 | 0.9886 | record |
| 53 | 85 | 138 | 0.9970 | 0.5011 | 53-EDO overflow |
| 306 | 485 | 791 | 0.0015 | 0.9990 | best record under 400 trits |

Record lows of w (s = 1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, …) are the *upper* semiconvergents of log₂3 = the record trit packings; near-maxima (s = 2, 7, 12, 53, 665) are the *lower* convergents, where 3^s just fails to fit. So the repo's two families of "special s" — the packing records and the musical commas — are the two sides of one continued fraction: **lower convergents = orbits that barely fail to drop one halving earlier; upper = orbits that barely drop.** Set₁₃'s slope 243/256 (checked: 7 residue classes mod 256, 0 slope violations for n < 200,000) *is* the five-trit byte, and 3¹²/2¹⁹ *is* "12 trits do not fit in 19 bits" — which is why Set₃₂ contracts by ~0.507 rather than ~1.

Caution: s = 5 and s = 41 are rare sets (density 0.0547 and tiny); this says nothing about typical orbits.

## 3. N(s) is OEIS A100982 — Verified prior art

The Lattice Path Formula sequence 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, … is **OEIS A100982**, "Number of admissible sequences of order n; related to 3x+1 problem and Wagon's constant" [2] (next terms 17637, 51033). Three definitions agree for s ≤ 12 (`scripts/collatz_packing_check.py`):

- **repo / lattice path:** a₁ = 1, aᵢ ≥ 1, partial sums < i·log₂3;
- **OEIS:** #{1 ≤ s₁ < … < s_{s−1} : sᵢ ≤ ⌊i log₂3⌋};
- **packing:** bit-budget schedules that are *under*-capacity at every prefix, 2^(b₁+…+bᵢ) < 3ⁱ for all i < s.

So **N(s) counts partial trit packings that never (yet) have enough bits.** The complementary object is **A076227** (binary words with 2^m < 3^(v₁+…+v_m) for all m — residues mod 2ⁿ whose dropping time is still undecided) [5].

What the literature adds that the repo lacks:
- **Zarubin's recursion** (Theorem 1 on the OEIS page) computes a(k) from a(1..k−1).
- **Winkler's bounds** (2026), with m_s = ⌊s log₂3⌋: (1/s)·C(m_s−1, s−1) ≤ N(s) ≤ (1/s)·C(m_s, s−1). Verified here for s ≤ 12. These pin the exponential growth rate the repo's note calls "irregular growth" — worth importing into `docs/Conjectures/Lattice Path Formula.md`.
- **Roosendaal** enumerated to order 1000 (2005); a b-file to n = 2218 exists. The repo's "verified to s = 10" is far behind.
- **Wagon's constant** A122790 = 9.4779555565… = Σ_s k(s)·N(s)/2^(b(s)−1) = E[stopping time] [3]. This is exactly the repo's density formula N(s)/2^(b(s)−1), already published.
- **Asymptotics:** lattice paths under an *irrational* slope — Nakamigawa–Tokushige's cycle lemma [6]; Banderier–Wallner's rational-slope paper [7] announced an irrational-slope sequel (not located).

## 4. The prefix-code statement — Verified

Because the class of n depends only on n mod 2^(b(s)) (no overlaps for b ≤ 17, all residues accounted for), the dropping classes form a **complete prefix-free code on the low bits of n**: codeword = low b(s) bits, length = minimal register for s trits, multiplicity N(s). The Kraft sum Σ N(s)/2^(b(s)−1) = 1 (0.99407 at s ≤ 32) is Terras's density-one theorem. Consequences:

- **Period of Set_k = smallest power of two that holds s trits.** The repo's modulus hierarchy 4, 16, 32, 128, 256, 1024, 4096 is the sequence of minimal trit registers; "89% classified by mod 4096" reads "89% of odd numbers are decided once you can hold 7 trits".
- **Expected bits read = Wagon's constant ≈ 9.478.** At s ≤ 32: E[s] ≥ 3.23 Syracuse steps and E[b(s)] ≥ 5.56 halvings — a typical drop stores ~3.2 trits in ~5.6 bits, between the (3, 5) and (5, 8) records. Mean waste E[w(s)] ≈ 0.45 bits (partial sum).

## 5. One real identity: the drift — Verified arithmetic, Analogy only

BITCOS ties the uniform-ternary bound at z* = 2 − log₂3 = log₂(4/3) = 0.41504. The Collatz per-Syracuse-step drift is E[α] − log₂3 = 2 − log₂3 under the 2-adic Haar measure (P(α = j) = 2^(−j)). Same number, same reason: both are "what a 2-bit-per-ternary-symbol layout spends above the information content". *A ternary LLM whose zeros are dense enough to reach the entropy bound is at exactly the compression ratio that makes a Collatz orbit descend at the average rate.* Pretty and true, but one subtraction — do not build on it.

## 6. Dead ends, stated plainly

- **Presence + sign factorisation.** BITCOS's split pays off only because z ≠ 1/3. Collatz has no "zero" symbol: the only 3-state alphabet is the residue mod 3, where by the 3-Adic Lock destinations are *never* ≡ 0 — the opposite statistics. A bitmap would be pure overhead. Mirror image (Collatz uses 2 of 3 residue states; 2-bit packing uses 3 of 4 binary states), no mechanism. The [[Ternary Syracuse Circuit]] makes the parity/sign split concrete as a circuit, but there is no theorem.
- **Eisenstein sign.** The χ₆ sign is a character value, not a compression flag. Both being "one bit" is not evidence.
- **Zero density z ≈ 1/3.** H(z) peaks at log₂3 at z = 1/3. The odd-step fraction of a stopping orbit is s/k → 1/log₂6 = 0.38685; the full-trajectory heuristic gives 1/3. Neither has a derivational link to z; proximity to BITCOS's break-even 0.375 is coincidence.
- **128-block padding.** The paper's 1.625 bpw is byte alignment: ⌈128 log₂3⌉ = 203 bits = 25.4 bytes → 26; already optimal among byte-aligned layouts. Only 0.13 of the 5.1 excess bits is Three-Distance waste. Collatz's only "block" is the modulus 2^(b(s)), which is by construction the minimal register (zero padding). Nothing to import; the Three Distance structure enters through w(t) = 1 − {t log₂3}, not block sizes.
- **Balanced ternary Collatz.** No substantive literature; the map's ternary content is a *multiplier*, not a digit alphabet. Setun stored trits in two cores each (the (1, 2) packing) and never exploited log₂3 either [9].

## 7. Open questions

1. **(Conjecture)** Use Winkler's bounds to get an explicit tail bound for the densities N(s)/2^(b(s)−1). Is (1/s)·C(m_s, s−1)·2^(−(b(s)−1)) summable fast enough to quantify "89% by mod 4096 → 100%"?
2. **(Conjecture)** Is E[w(s)] under the dropping-set measure 1/2 (equidistribution) or biased low (~0.45 from partial sums)? A bias would say drops are systematically tighter packings than random — a real structural statement.
3. **(Analogy, cheap to kill)** Does a BITCOS-style variable-rate layout (bitmap over rare events + compacted stream) describe the bounce/streak bookkeeping in `docs/Conjectures/Finite Propagation Theorem.md` more compactly? Probably not; it is the only part of the paper with a shot at transferring.

See also [[Summary - Findings and Open Questions]].

## Sources

1. OEIS A122437, "Allowable values of the dropping time of the Collatz (3x+1) iteration" (T. D. Noe, 2006) — https://oeis.org/A122437
2. OEIS A100982, "Number of admissible sequences of order n; related to 3x+1 problem and Wagon's constant" — https://oeis.org/A100982 (cites S. Wagon, "The Collatz problem", *Math. Intelligencer* 7 (1985) 72–76; E. Roosendaal 2005; V. M. Zarubin 2015/2019; M. Winkler 2011–2026)
3. OEIS A122790, "Decimal expansion of Wagon's constant" — https://oeis.org/A122790
4. OEIS A020914, "Number of digits in base-2 representation of 3^n" — https://oeis.org/A020914
5. OEIS A076227, surviving Collatz residues mod 2^n — https://oeis.org/A076227
6. T. Nakamigawa, N. Tokushige, "Counting lattice paths via a new cycle lemma", *SIAM J. Discrete Math.* 26(2) (2012) — https://www.semanticscholar.org/paper/8455f72ab1829e3ad976b73dc1a3ebd8994b9745
7. C. Banderier, M. Wallner, "Lattice paths below a line of rational slope" — https://link.springer.com/chapter/10.1007/978-3-030-11102-1_7
8. P. Hellekalek, "On the 3x+1 conjecture" — https://arxiv.org/pdf/1605.02634
9. Russian Virtual Computer Museum, "Development of ternary computers at Moscow State University" (Setun) — https://www.computer-museum.ru/english/setun.htm
10. M. Winkler, "Deterministic Structures in the Stopping Time Dynamics of the 3x+1 Problem", arXiv:1709.03385 — https://arxiv.org/pdf/1709.03385
11. E. Georganas, A. Heinecke, P. Dubey, "Breaking the 1.58-bit Barrier for Ternary LLMs", arXiv:2609.16338 — https://arxiv.org/abs/2609.16338
12. `docs/Conjectures/Odd Stopping Time Spectrum.md`, `docs/Conjectures/Affine Orbit Structure.md`, `docs/Conjectures/Lattice Path Formula.md` (this repo).
13. Scripts: `scripts/stopping_time_trit_bits.py`, `scripts/collatz_packing_check.py`, `scripts/packing_records.py`.
