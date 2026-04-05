# Countdown Hierarchy: Plan of Attack

> **For agentic workers:** This is a mathematical proof plan, not a software implementation plan. Each "task" is an algebraic argument + computational verification. Use the research-compute-prove cycle: investigate computationally, identify the pattern, then write the formal proof.

**Goal:** Prove that every Collatz orbit converges to 1, by extending the deterministic countdown hierarchy to force drops of every depth.

**Architecture:** The proof has three layers:
1. **The Countdown Hierarchy** (Route C) — extend v₂ countdowns to all bit-depths, forcing every orbit through arbitrarily deep drops. This is deterministic and doesn't require mixing arguments.
2. **The Net Contraction Bound** — prove the forced drops provide enough cumulative contraction to overcome the growth from weak drops.
3. **The Convergence Conclusion** — combine countdowns + contraction + no-cycles (Front 1) to prove every orbit reaches 1.

**Key Principle:** The +1 in 3n+1 creates carry propagation in binary. At each bit-depth B, the carry forces the orbit to visit specific residue classes mod 2^B. This is the engine of the countdowns, and it's DETERMINISTIC — no probabilistic mixing needed.

**Prior Results:**
- Front 1 (no cycles): COMPLETE
- One-Bit Countdown (forces Set_3): PROVED — `docs/Conjectures/Proof Attempt - Denjoy Bridge.md`
- Two-Bit Countdown (forces medium drops): PROVED for immediate — same file
- E[log₂(factor)] = log₂3 - 2 = -0.415 exactly
- Each v₂ depth = exactly one residue class mod 2^{k+1}

---

## Task 1: Formalize the Carry Propagation Engine

**Goal:** Prove that the +1 carry in 3m+1 deterministically transforms the bit structure of m in a predictable way, and characterize exactly how v₂(3m+1) depends on m's bits.

**Files:**
- Create: `docs/Conjectures/Carry Propagation Theorem.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: Prove the trailing-ones characterization**

v₂(3m+1) = number of trailing 1-bits of 3m (in binary). Prove this algebraically:
3m is odd, so its binary ends in 1. Adding 1 creates a carry chain through consecutive 1-bits.
Therefore v₂(3m+1) = (length of trailing 1-run in 3m's binary).

- [ ] **Step 2: Characterize trailing 1-bits of 3m in terms of m's bits**

3m = 2m + m. The binary addition 2m + m (left-shift + original) has carry behavior determined by m's bit pattern. Derive: the trailing bits of 3m are a specific function of m's trailing bits. Verify computationally for m up to 2^20.

- [ ] **Step 3: Prove the one-residue-per-depth theorem**

We verified: v₂(3m+1) = k iff m ≡ r_k (mod 2^{k+1}) for a unique odd residue r_k. Prove this algebraically from step 2. The residue r_k is determined by the carry chain: each additional trailing 1 in 3m requires one more bit of m to be fixed.

- [x] **Step 4: Derive the explicit formula for r_k** ✅ DONE

r_k = (4^⌈k/2⌉ - 1)/3 = 2-adic truncation of -1/3.
v₂(3m+1) ≥ k iff m ≡ -1/3 (mod 2^k).
Drop depth = number of 2-adic digits m agrees with -1/3.
The bit pattern is alternating ...010101 = 1/3 in Z₂.

- [x] **Step 5: Additional finding — Conditional expectations**

E[log₂(factor) | prev_depth = i] is NEGATIVE for ALL i ∈ {1,2,3,4,5,6}.
Range: [-1.365, -0.285]. Orbit is a supermartingale.
MI between consecutive depths = 0.047 bits (2.5% of entropy).
BUT: deterministic orbits can deviate from conditional expectation.

- [ ] **Step 6: Write up and commit**

---

## Task 2: Extend the Two-Bit Countdown to Non-Immediate Drops

**Goal:** The two-bit countdown (v₂(m-1) decreasing by 2) was proved only for IMMEDIATE weak drops (consecutive Set_3 encounters with no non-dropping phase between them). Extend it to cover non-immediate cases.

**Files:**
- Modify: `docs/Conjectures/Proof Attempt - Denjoy Bridge.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: Trace what happens after a weak drop with a non-dropping phase**

After weak Set_3 drop at m ≡ 1 (mod 8): d = (3m+1)/4. If d ≡ 3 (mod 4), a non-dropping phase begins. Track v₂(d+1) through the non-dropping phase to the next Set_3. Compute what v₂(m'-1) is at the next Set_3 value m', in terms of the original v₂(m-1).

- [ ] **Step 2: Identify the non-immediate countdown invariant**

The non-dropping phase has length v₂(d+1) - 1 steps. During this phase, the orbit grows by (3/2)^{v₂(d+1)-1}. At the end, the new Set_3 value m' has some v₂(m'-1). Is v₂(m'-1) ≤ v₂(m-1) - 1? If so, the countdown continues (at reduced rate).

- [x] **Step 3: Result: v₂(m'-1) decreases 75%, stays 12.5%, increases 12.5%**

v₂(m-1) does NOT monotonically decrease through non-immediate drops.
BUT: it never increases TWICE consecutively (0 cases in 50K tested).
The net trend is strongly downward. After one increase, the next step must decrease.

- [x] **Step 3b: Critical window analysis**

The product of W consecutive cycle factors (weak streak + deep drop) is:
- W=10: max product 0.76 (< 1 for m ≤ 50K)
- W=13: max product 0.32 (< 1 for m ≤ 100K)  
- W=14: max product 0.59 (< 1 for m ≤ 200K)
- W grows as ~O(log m), giving O(log² m) convergence

KEY FINDING: the geometric mean per cycle is 0.362. Every 15-cycle window contracts.
The critical window W(m) appears to grow logarithmically, not as a constant.

If the countdown works for both immediate and non-immediate weak drops (possibly at different rates), then the total weak streak is bounded by v₂(m₀-1) × c for some constant c.

- [ ] **Step 4: Compute the maximum weak streak as a function of v₂(m₀-1)**

For all m₀ up to 200000: compute the max weak streak and v₂(m₀-1). Plot the relationship. If it's linear: streak ≤ c × v₂(m₀-1) for some c.

- [ ] **Step 5: Write up and commit**

---

### Task 2 Key Results (2026-04-05):
- v₂(m-1) can increase once, never twice consecutively (0/50K exceptions)
- Streak bifurcates: V even → streak = V/2 exactly; V odd → streak ≤ V/2 + 15
- The V=3 bouncing regime has max length ~16, CONSTANT independent of m
- Min v₂(m-1) at m≡1(mod32) is exactly 5 (threshold for exiting 3-bit trap)
- The two-bit countdown v₂(m-1) drives ALL levels via a SINGLE invariant
- m≡1(mod32) → always weak next; m≡17(mod32) → always deep next (deterministic!)

## Task 3: The Three-Bit Countdown

**Goal:** Prove that the orbit must encounter v₂(3m+1) ≥ 4 (strong drop) within a bounded number of Set_3 encounters.

**Files:**
- Create: `docs/Conjectures/Three-Bit Countdown.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: Characterize which c mod 8 give strong drops**

From the table: strong drops (v₂ ≥ 4) occur when (v even, c ≡ 1 mod 8) or (v odd, c ≡ 3 mod 8). The pattern is periodic in v with period 2. Prove this from the Lifting the Exponent Lemma for p = 2.

- [ ] **Step 2: Track c mod 8 through the Syracuse orbit**

After a Set_3 drop: c_new = odd_part(d+1). Express c_new mod 8 in terms of c_old mod 8, v, and the drop depth. Check if this is deterministic (depends only on c mod 8 and v mod 2) or depends on higher bits.

From the session data: the transition is NOT deterministic from (c mod 8, v mod small) alone. It depends on higher bits. But the REACHABLE set of c_new mod 8 from any c_old includes all 4 values {1,3,5,7}.

- [ ] **Step 3: Prove the c mod 8 transition is "non-degenerate"**

Show that from any c_old mod 8, the set of possible c_new mod 8 values (over all possible higher bits) includes BOTH strong-drop classes and non-strong classes. This means the orbit CAN reach strong drops from any starting configuration.

- [ ] **Step 4: Find a deterministic countdown for the three-bit level**

The carry propagation at the third bit level: when the orbit stays in non-strong territory (c ∈ {5,7} mod 8 or c ∈ {1,3} mod 8 in the wrong v-parity), identify a quantity that decreases. Candidates:
- v₂(c - r_strong) for some target residue r_strong
- v₂(something involving m and the accumulated carry)
- A modular invariant that tracks the "distance" to strong-drop residues

- [ ] **Step 5: If no clean three-bit countdown exists, characterize the obstacle**

The obstacle might be that three-bit mixing is genuinely non-deterministic (depends on bits beyond the immediate neighborhood). In that case, document exactly what's needed: a bound on how many steps the higher bits can conspire to avoid strong drops.

- [ ] **Step 6: Write up and commit**

---

## Task 4: The General Countdown Principle

**Goal:** Either prove the countdown hierarchy extends to all bit-depths, or identify the precise level at which it fails and characterize why.

**Files:**
- Create: `docs/Conjectures/General Countdown Principle.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: Formulate the general conjecture**

**Countdown Principle (Conjecture):** For each depth k ≥ 2, there exists an invariant I_k(m) with the properties:
(a) I_k(m) is determined by m mod 2^{f(k)} for some function f(k)
(b) I_k decreases along the orbit when the orbit avoids drops of depth ≥ k
(c) When I_k = 0, the orbit must encounter a drop of depth ≥ k
(d) I_k(m) ≤ g(k) × v₂(m ± something) for some function g(k)

- [ ] **Step 2: Verify for k = 2, 3, 4**

k=2: I₂ = v₂(m+1), decreases by 1 per non-dropping step. PROVED.
k=3: I₃ = v₂(m-1)/2, decreases by 1 per immediate weak drop. PROVED (immediate).
k=4: I₄ = ??? Find it computationally by tracking orbits that avoid v₂ ≥ 4 and measuring what decreases.

- [ ] **Step 3: Look for the pattern in the invariants**

Do I₂, I₃, I₄ follow a pattern? Are they all of the form v₂(m + a_k) / b_k for specific constants a_k, b_k?

- [ ] **Step 4: If the pattern exists, prove it by induction**

The induction step: given I_k, construct I_{k+1}. The +1 carry at bit level k+1 provides the mechanism. The carry propagation at each level "reads" one more bit, decreasing the invariant.

- [ ] **Step 5: If the pattern doesn't exist, characterize the failure mode**

Possible outcomes:
(a) The hierarchy works for all k → proof complete
(b) The hierarchy works up to some k₀, then fails → need a different argument for deeper levels
(c) The hierarchy has a different structure than expected → reformulate

- [ ] **Step 6: Write up and commit**

---

## Task 5: Net Contraction from the Countdown Hierarchy

**Goal:** Assuming the countdown hierarchy forces drops of every depth, prove the cumulative contraction is sufficient for convergence.

**Files:**
- Modify: `docs/Conjectures/Proof Attempt - Denjoy Bridge.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: Compute the worst-case net factor per countdown cycle at each level**

Level k: the orbit avoids depth ≥ k for at most I_k steps. During this avoidance, the orbit grows by at most (3/2)^{steps}. The forced drop of depth k contracts by 3/2^k. Net factor:

F_k = (3/2)^{max_steps(k)} × 3/2^k

Compute F_k for k = 2, 3, 4, ..., 10. Is F_k < 1 for large enough k?

- [ ] **Step 2: Compute the product of net factors across all levels**

The orbit passes through levels 2, 3, 4, ..., B (where B = bit-length). The total net factor is:

Π_{k=2}^{B} F_k

If this product → 0 as B → ∞, every orbit converges.

- [ ] **Step 3: Handle the interaction between levels**

The levels aren't independent — a deep drop at level k also satisfies levels 2, ..., k-1. Account for this: the orbit doesn't need to separately visit each level.

- [ ] **Step 4: Prove or disprove: cumulative contraction < 1**

If the net factor per level is bounded (F_k ≤ c < 1 for all k ≥ k₀), then the product over B levels gives total factor c^B → 0. This proves stopping_time(n) = O(B) = O(log n).

- [ ] **Step 5: Write up and commit**

---

## Task 6: Alternative Route — Discrete Denjoy-Koksma

**Goal:** If the countdown hierarchy stalls at some level, use the near-conjugacy to irrational rotation as a complementary tool. The Denjoy-Koksma inequality bounds Birkhoff sums along rotation orbits; adapt it to the Collatz setting.

**Files:**
- Create: `docs/Conjectures/Discrete Denjoy-Koksma.md`
- Verify: `notebooks/08-countdown-hierarchy.ipynb`

- [ ] **Step 1: State the classical Denjoy-Koksma inequality precisely**

For rotation by irrational α with convergent denominators q_n: |Σ_{i=0}^{q_n-1} φ(x + iα) - q_n ∫φ| ≤ Var(φ).

- [ ] **Step 2: Formulate the perturbed version needed for Collatz**

The Collatz orbit in log₆ coordinates: x_{n+1} = x_n + log₆(3) + ε_n. Cumulative error bounded by M ≈ 0.5. State the bound: if Var(φ) < q_n × coverage - 2M × Var'(φ), the orbit visits the support of φ.

- [ ] **Step 3: Apply to φ = indicator of depth-k drop zone**

The depth-k drop zone has density 1/2^k on the circle. Its variation depends on how many "arcs" it forms. Compute Var(φ_k) for k = 2, 3, 4, 5.

- [ ] **Step 4: Find the minimum k for which DK gives a non-vacuous bound**

The DK bound is useful when q_n × density > Var(φ) + 2M correction. For convergent q_n = 44 (from 27/44 ≈ log₆(3)): q_n × 1/2^k > Var(φ_k) + correction. Find the threshold k.

- [ ] **Step 5: Combine with the countdown hierarchy**

If the countdown handles levels 2 through k₀ and DK handles levels k₀+1 and above, the combination covers all levels. Write the combined proof.

- [ ] **Step 6: Write up and commit**

---

## Task 7: Assembly — The Complete Proof

**Goal:** Assemble all components into a single coherent proof document.

**Files:**
- Create: `docs/Conjectures/Complete Proof Attempt.md`
- Modify: `docs/plans/path-to-proof.md`

- [ ] **Step 1: Write the proof assuming all components are proved**

Structure:
1. Front 1: No cycles (complete)
2. The Countdown Hierarchy: forces drops at every depth (from Tasks 1-4)
3. Net Contraction: cumulative contraction < 1 (from Task 5)
4. Convergence: cascade of drops → reaches 1
5. QED

- [ ] **Step 2: Identify and flag any remaining gaps**

Mark each step as PROVED, VERIFIED (computationally), or OPEN. For OPEN steps, state exactly what's needed.

- [ ] **Step 3: Update the path-to-proof with final status**

- [ ] **Step 4: Commit the complete proof document**

---

## Decision Points

After each task, evaluate:

1. **After Task 1 (Carry Propagation):** Do we have the algebraic tools to extend countdowns? If the carry structure is too complex, pivot to Route D (Denjoy).

2. **After Task 3 (Three-Bit Countdown):** Does a deterministic countdown exist at level 3? If YES: continue to Task 4 (general principle). If NO: jump to Task 6 (Denjoy-Koksma) for a complementary approach.

3. **After Task 5 (Net Contraction):** Is the cumulative contraction sufficient? If YES: proceed to Task 7 (assembly). If NO: the countdown hierarchy provides the structure but needs a stronger contraction argument — revisit the spectral gap (Route B).

## Success Criteria

The proof is complete when:
- Every step in the proof is either PROVED algebraically or VERIFIED computationally with a clear path to formalization
- No step relies on probabilistic/heuristic arguments ("almost all", "on average")
- The entire argument is deterministic: for any specific integer m, the proof shows its orbit converges
