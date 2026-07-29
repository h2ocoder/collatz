# Three-Bit Countdown: Design

**Date:** 2026-07-28
**Status:** Approved (countdown framing, discover→verify→prove, scripts + docs)
**Goal:** Find and prove an invariant I₄(m) that forces Syracuse orbits to encounter strong drops (v₂(3m+1) ≥ 4) within bounded time — the depth-3 rung of the countdown hierarchy (plan Tasks 3–4 of `docs/plans/2026-04-04-countdown-hierarchy-plan.md`).

## Background

- Proved: I₂ = v₂(m+1) decreases by exactly 1 per non-dropping step (One-Bit Countdown).
- Proved (immediate case): I₃ = v₂(m−1)/2 decreases per weak Set₃ drop (Two-Bit Countdown).
- Drop depth = 2-adic agreement with −1/3: v₂(3m+1) ≥ k iff m ≡ −1/3 (mod 2^k). Strong drop ⇔ m ≡ 5 (mod 16).
- An orbit "avoids" while its Set₃ encounters have m mod 16 ∈ {1, 9, 13}.

## Phase A: Ansatz search (`scripts/three_bit_ansatz.py`)

Both proved invariants are 2-adic distances to fixed rationals (−1, +1). Test the family
I(m) = v₂(m − a) for a in: truncations of −1/3 (5, 21, 85, …), truncations of 1/3, −1/9, 7/9, small odd constants ±1, ±3, ±5, ±7, and shifted variants v₂(3m+1 − 2^j).

For all odd m₀ ≤ 10⁶: extract maximal avoidance streaks (consecutive Set₃ encounters with v₂(3m+1) ∈ {2,3}); for each candidate, measure along-streak behavior: strict decrease rate, never-increases-twice rate, max increase run, correlation of streak length with initial I. Output: ranked table + figures in `data/`. Exact integer arithmetic; floats only for plotting.

## Phase B: Avoidance tree (`scripts/three_bit_avoidance_tree.py`)

Derive the invariant instead of guessing. The encounter-to-encounter map (Set₃ value → next Set₃ value) is piecewise affine with branches indexed by the intermediate one-bit countdown length. Enumerate branch words of length n; each word that avoids strong drops pins m₀ to a residue class mod 2^{e(word)}. Build this exact tree to depth ~20–30 and measure bits-of-constraint consumed per avoidance step, especially the MINIMUM over the tree (the deterministic countdown rate). One-Bit is this tree at depth 2 with rate exactly 1 bit/step.

Outcomes: (a) uniform rate c > 0 → invariant = remaining constraint budget, proof target = carry-propagation lemma; (b) rate → 0 along some paths → those paths ARE the obstacle characterization (expected: the V=3 bounce family). Either way the deliverable is nonempty.

## Phase C: Proof attempt + writeup

Take the winning structure into `docs/Conjectures/Three-Bit Countdown.md` with each claim marked PROVED / VERIFIED / OPEN; update `docs/plans/path-to-proof.md`. Proof tools: trailing-ones carry characterization, LTE for p=2, the r_k = (4^⌈k/2⌉−1)/3 formula.

## Rigor guards

- Discovery on m ≤ 10⁶; verification on disjoint ranges (10⁷ band + random 128-bit odds).
- Sanity harness must reproduce known results first: One-Bit exact countdown; streak = V/2 for even V = v₂(m−1); no double-increase of v₂(m−1) (0/50K).
- No probabilistic claims in the writeup's PROVED column.
