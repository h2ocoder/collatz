# Session State: 2026-04-03/04

## What We Accomplished

### Front 1: No Cycles — COMPLETE
- Second moment (Parseval) bound rigorously eliminates all convergents with S ≥ 306
- MITM eliminates (41, 65). All other convergents eliminated by enumeration or ascending argument.
- **No non-trivial Collatz cycles exist.**

### Front 2: No Divergence — Major Progress, Not Closed

#### Proved Results
1. **3-adic lock**: dest(n) ≡ r₃ (mod 3^s) per subgroup. Algebraic proof.
2. **Conservation law**: s·log₂6 = T - log₂n + ε, ε ∈ [-0.33, 0]
3. **One-Bit Countdown**: v₂(m+1) decreases by exactly 1 per non-dropping Syracuse step → forces Set_3 encounter within v₂(m+1)-1 steps
4. **Two-Bit Countdown**: v₂(m-1) decreases by 2 per immediate weak Set_3 drop → forces medium/strong drop
5. **Each v₂ depth is exactly one residue class**: v₂(3m+1) = k ↔ m ≡ r_k (mod 2^{k+1}), density 1/2^k

#### Verified Computationally
- Spectral gap → 5/6, λ₂ → 1/6 (up to M = 1296)
- Cheeger constant h ≥ 0.44 (increasing with M)
- No absorbing subsets on (2^12, 3^6) lattice (1.5M points)
- Every orbit hits v₂ ≥ 4 (strong drop) — 0 exceptions in 44K tested
- Stopping time = O(log n): ratio stop_time/bits ∈ [8, 19]
- Geometric mean contraction = 0.755 per Syracuse step
- E[log₂(factor)] = log₂3 - 2 = -0.415 exactly

#### Key Connections Found
- User's PPR(x,6) = Shakibaei Asli's near-conjugacy to rotation by log₆(3) (arxiv 2601.04289)
- Chang's one-bit reduction (arxiv 2603.25753) matches our one-bit countdown
- 44-step quasi-period = convergent 27/44 of log₆(3)
- Denjoy theorem as potential bridge: irrational rotation + bounded perturbation → minimal

## Where We Got Stuck (Last Computation)

**The Syracuse chain on Z/2^B Z is NOT irreducible.** Every state maps to only 1 successor (the chain is deterministic), so there are no large communicating classes. Each state is its own SCC of size 1.

This means the ergodic theorem for finite Markov chains does NOT directly apply. The chain isn't mixing — it's a deterministic map.

**This is actually obvious in hindsight**: S(m) mod 2^B is a FUNCTION, not a random process. Each m has exactly one successor. There's no randomness and no mixing at the chain level. The "mixing" we observed earlier came from the TRANSITION MATRIX, which was built by averaging over MANY integers m in each residue class. But a specific integer m follows a specific path.

## The Actual Remaining Gap

The conjecture reduces to:

> **For every odd m > 1, the Syracuse orbit eventually visits a value < m.**

Equivalently: stopping_time(n) is finite for all n.

What we know:
1. If the orbit drops, the cascade converges (no cycles + β > 0)
2. E[log₂(factor)] = -0.415 < 0 (the average step contracts)
3. The Collatz map on Z₂ is ergodic w.r.t. Haar measure (known result)
4. This gives "almost all" orbits converge (Terras 1976, reproved via our framework)
5. The countdowns force periodic Set_3 encounters (proved)
6. But Set_3 alone gives net growth (9/8 per cycle) — need higher drops

The gap between "almost all" and "all" requires one of:
- **(A)** Prove unique ergodicity of Collatz on Z₂ (Haar is only invariant measure)
- **(B)** Prove uniform spectral gap ≥ c > 0 for all B (for the averaged chain)
- **(C)** Extend the countdown hierarchy to force deep drops for all naturals
- **(D)** Use the near-conjugacy to irrational rotation + discrete Denjoy theorem

## What To Try Next Session

### Most Promising: Route (C) — Countdown Hierarchy
The one-bit and two-bit countdowns are DETERMINISTIC (no mixing needed). Extending to three-bit and beyond would force every orbit through deep drops. The pattern:
- Level 1: v₂(m+1) forces Set_3 [PROVED]
- Level 2: v₂(m-1) forces medium drops [PROVED for immediate]  
- Level 3: some invariant forces strong drops [TO PROVE]
- The +1 carry propagation is the engine at each level

### Also Promising: Route (D) — Denjoy Bridge
- Shakibaei Asli: Collatz ≈ rotation by log₆(3) + O(1/x) error
- Cumulative error bounded (≈ 0.5)
- Need: discrete version of Denjoy-Koksma inequality for perturbed rotations
- Key theorem (classical): bounded perturbation of irrational rotation → dense orbit
- But our M ≈ 0.5 makes the standard bound vacuous (2M = 1.0 ≥ circle circumference)

### Fallback: Route (B) — Spectral Gap
- The AVERAGED transition matrix (treating each residue class as a distribution) has gap ≈ 5/6
- Need to show this averaging is justified: the orbit of a specific integer "looks like" a random sample from the chain
- The Cheeger constant h ≥ 0.44 quantifies this
- Proving h ≥ c > 0 for all M would close everything

## Key Files
- `docs/Conjectures/Proof Attempt - Denjoy Bridge.md` — full proof writeup
- `docs/Conjectures/Spectral Mixing Theorem.md` — spectral analysis
- `docs/Conjectures/The +1 Perturbation.md` — the core obstacle
- `docs/plans/path-to-proof.md` — overall roadmap
- `notebooks/07-conjugate-variables.ipynb` — all computations
- Key references: arxiv 2601.04289 (near-conjugacy), arxiv 2603.25753 (one-bit reduction)
