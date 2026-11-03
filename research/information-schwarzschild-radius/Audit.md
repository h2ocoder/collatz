---
tags: [schwarzschild, audit, barriers, prior-art]
status: complete
created: 2026-11-02
jira: SCRUM-65
---

# Audit

**Bottom line: nothing in this vault is a step toward proving the Collatz conjecture.** It is a dictionary, a set of exact identities, some family-wide laws, and one finite certificate. The rest of this note says why, and what is classical.

## The barrier list

| barrier | what it does to these results |
|---|---|
| Measure | The Haar statements hold for almost every 2-adic integer. Positive integers are a null set. The integer survival law past step B is measured, not derived. |
| Mirror 3x−1 | c, g, m, σ, θ and the digit laws are identical for 3x+1 and 3x−1, so none of them can separate the two. Only the sign of F differs, and that is the cycle equation again. |
| Cousin 5x+1 | The word identities hold for 5x+1 too, so they cannot imply convergence. Rates do separate it (g < 0), but that is the classical heuristic. |
| Quotient | The causal cone and the digit bijection live on residues. Every residue statement also holds for the n → 3n/2 "away" map, whose positive orbits diverge. |
| Finite modulus | The 3-adic limit needs all levels m. Any finite level sees only an average. |
| Expected count | The reach law, the hover and fall bounds and the capture count at a = 1 are first-moment counts. The capture count shows the danger directly: it is accurate across 701 masses and predicts about 1.14 captures at a = 1, where none is known. |
| Uniformity | Everything statistical is about typical points. A proof must handle every n. Tao's theorem, which is used in [[Information Radius]] §8, stops at almost all n for the same reason. |
| Z₂ | −1 has an infinite address, so its budget argument is void, and its rates are the same. The fuel picture says why integers might differ. It does not show that they do. |
| Transcendence | The horizon bound on F needs a lower bound on β(s). Baker-type bounds give F ≤ polynomial in s, so a failure at n needs s ≥ n^c for some c > 0. Ruling that out needs an upper bound on s in terms of n, and nobody has one. |

## Status of the claims

| claim | status |
|---|---|
| Lapse, infall, null-ray flow, two-place centre, mass scaling, sign rule, ζ ≤ s/3, F bound | **Proved** here, elementary |
| Causal cone, digit bijection, ledger | **Proved** here or **Classical** |
| r_s(M) = θM + O(1) under Haar | **Classical** (Cramér–Lundberg) |
| Weak-field limit, Mach equation | **Proved** here |
| Tail of F, C = 1/ln(27/16) | **Proved** given Goldie, **Verified** to five digits |
| Capture lower bound, for any scaled map | **Proved** here |
| Capture constant Σ for the upper side | **Verified** only |
| Memory tight, erased bits → g | **Proved** given Tao, **Verified** in trend |
| Certificate: no failure with s ≤ 47,467 | **Proved** given the computation |
| q = d + 1 is critical, no thin uniform map | **Proved** here, trivial |
| Reach 1 + 1/θ for integers | **Heuristic**, **Verified** on 12 maps with misses |
| Lifetime bounds for integers | **Heuristic** |
| Genuine failures for every odd a in 3..1401 | **Verified** |
| No failure for a = 1 | **Open**: Terras's conjecture. Verified for n < 2³⁰ and for s ≤ 47,467 |
| 2D dilaton, acoustic, barometric, Page readings | **Analogy** |

## Independent checks

A separate adversarial audit reimplemented the key computations in scratch code, which is not committed, so these numbers cannot be reproduced from this repo:

- A u128 rescan matched the capture table for all 701 masses, and the capture ratio stayed on Σ = 1.81367 at far larger masses: 1.81383 ± 0.00009 near a = 1.3 × 10⁵ and 1.81368 ± 0.00001 near a = 1.5 × 10⁸.
- All n < 2³⁶ pass the coefficient stopping test. That would extend the certificate from s ≤ 47,467 to s ≤ 190,536. The bound arithmetic for that figure was rechecked here.
- Σ, the Kesten constant, the 3-adic identity, the saturation equation and the certificate logic were each rederived.

The audit also forced corrections now in these notes: lift can exceed B, the first moment at a = 1 had counted real length and not integers, and the hard trapping radius needs non-negative offsets.

## What is classical, and what may be new

Prior art, to cite and not to claim:

- Stopping and coefficient stopping: Terras, *A stopping time problem on the positive integers*, Acta Arith. 30 (1976), Conjecture 2.9. Lagarias, *The 3x+1 problem and its generalizations*, Amer. Math. Monthly 92 (1985).
- Cycle equation: Böhm and Sontacchi (1978). Rational cycles and 3x+k: Lagarias, Acta Arith. 56 (1990).
- Digit bijection for general maps: Möller (1978), Matthews and Watts, Acta Arith. 43 (1984).
- Peak exponent 2, stopping constant 41.677647: Lagarias and Weiss, Ann. Appl. Probab. 2 (1992). Survey: Kontorovich and Lagarias, arXiv:0910.1944, Conjecture 4.2.
- Brownian limit with drift for (d,g,h)-maps: Kontorovich and Sinai, arXiv:math/0601622.
- 3-adic densities: Wirsching, Lecture Notes in Math. 1681 (1998). Fine-scale mixing: Tao, Forum Math. Pi 10 (2022), arXiv:1909.03562, Proposition 1.14.
- Random recursions: Kesten, Acta Math. 131 (1973). Goldie, Ann. Appl. Probab. 1 (1991).
- Physics: Unruh, PRL 46 (1981). Hamilton and Lisle, Am. J. Phys. 76 (2008). Witten, PRD 44 (1991). Mandal, Sengupta and Wadia, Mod. Phys. Lett. A6 (1991). Callan, Giddings, Harvey and Strominger, PRD 45 (1992). Metric form as used here: Suresh and Kuriakose, arXiv:1501.04852. Bennett (1973). Landauer (1961). Page, PRL 71 (1993).

Searching for a rigorous link between Collatz and the Schwarzschild radius found only metaphors and unreviewed preprints claiming resolutions, none of which this work uses.

Possibly new, though the search was not exhaustive, so treat as unclaimed until checked:

1. The closed form 1/ln(27/16) for the tail. It is one line from Goldie.
2. The cross-section Σ and the capture law, and the observation that every odd mass from 3 to 1401 has genuine failures.
3. The extension of the peak exponent to 1 + 1/θ with evidence across a family.
4. The identity H(coin | y mod 3^m) = 1 − (H_m − H_(m−1))/2 and its link to Tao.
5. The kick certificate, which is probably folklore.

## Corrections noticed on the way

`docs/Conjectures/Bit Destruction Bound.md` cites Roth's theorem for β(s) > c/s. Roth applies to algebraic numbers and log₂ 3 is transcendental, and the site page already uses Baker instead. Left as it is, because it is out of scope here.

## Related

[[00 Index]] · [[The Schwarzschild Dictionary]]
