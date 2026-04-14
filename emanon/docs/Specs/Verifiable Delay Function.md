---
jira: ALPHA-20
status: draft
type: story
---

# Verifiable Delay Function (VDF)

## Overview
Emanon's proof of work IS a Collatz orbit. The VDF is not a separate cryptographic primitive bolted onto the game — it's the same mathematics that governs the physics. A miner traces the Collatz trajectory of a seed address. The orbit can't be parallelized (each step depends on the previous). The result is cheaply verifiable (retrace the steps). The dropping set determines difficulty tier. The orbit properties determine reward.

## The Core Elegance

Within any dropping Set_k, there are **infinitely many numbers** — and they all take exactly k steps to drop. The number 5 and the number 12,341,234,123,412,341 might both be in Set_3. Both take 3 steps. Same operation count. Same orbit *shape*. But vastly different **mass**.

The bit length of the seed is its weight. A 4-bit number in Set_3 and a 60-bit number in Set_3 produce the same structural work (3 dropping steps) but the larger number involves larger values at every step, touches a different region of the address space, and carries more information about where it's been.

This is the separation of **structure** and **scale**:
- **Structure** = which dropping set (how many steps, what shape)
- **Scale** = how large the seed is (what magnitude, what region)

Same recipe, different mass. Same orbit shape, different gravitational weight. The proof of work has two independent dimensions to tune.

## Why Collatz Orbits Are a Natural VDF

### Sequential (non-parallelizable)
Each Collatz step depends on the previous value. You must compute step 1 before step 2. There is no shortcut, no lookahead, no way to distribute the computation across cores. The orbit IS the delay.

### Cheaply verifiable
Given the seed n and the claimed orbit, any verifier retraces the same steps in O(k) time. The verification cost equals the computation cost — but verification only needs to happen once while mining requires searching across many seeds.

### Deterministic
The orbit of n is unique. No randomness, no nonce grinding. The same seed always produces the same proof. Two miners with the same seed produce identical results — no wasted redundant work.

### Tied to the game's physics
The VDF output isn't an arbitrary hash. It's a trajectory through the game's address space. The orbit visits specific numbers, each of which is a composite address in the multiverse. Mining is literally exploring — tracing a path through the universe.

## VDF Structure

### Input
- **Seed**: a composite number (universe address) — either randomly generated or chosen from the persistent world's unexplored frontier
- **Target dropping set**: optionally specified to constrain difficulty

### Computation
1. Compute the Collatz orbit of the seed: n → T(n) → T(T(n)) → ... → dest(n)
2. At each step, record: the value, the operation applied (3n+1 or n/2), the step number
3. Continue until the orbit drops below the seed (reaches the dropping destination)

### Output (the proof)
```
vdf_proof:
  seed: <the starting composite address>
  dropping_set: <k — how many steps the orbit took>
  dropping_destination: <where the orbit ended>
  orbit: [<sequence of values visited>]
  orbit_max: <highest value reached during the orbit>
  orbit_sum: <total of all values in the orbit — total "distance traveled">
  alpha_sequence: [<sequence of odd-step positions — the route pattern>]
  genus: <(S, M, I) — the odd/even/identity step counts>
  bit_length: <bit length of the seed — the mass>
  hash: <cryptographic hash of the full orbit for compact verification>
```

### Verification
1. Verifier receives the proof
2. Recomputes the orbit from the seed
3. Confirms: orbit matches, dropping set is correct, destination is correct
4. Cost: O(k) steps — same as computation but only done once per proof

## Difficulty and Reward Tuning

### Dropping Set as Difficulty Tier

| Dropping Set | Steps | Difficulty | Frequency | Use Case |
|-------------|-------|------------|-----------|----------|
| Set_3 | 3 | Easy | Very common | Quick scans, routine exploration, cheap energy |
| Set_6 | 6 | Medium | Common | Standard mining, moderate discoveries |
| Set_8 | 8 | Hard | Less common | Deeper exploration, better rewards |
| Set_11+ | 11+ | Very hard | Rare | Deep mining, rare finds, high-value loot |

The odd stopping time spectrum constrains which dropping sets are even possible for odd seeds: only ceil(s * log2(6)) values. Gap classes (4, 5, 7, 9, 10, ...) never occur for odd numbers. This is a natural difficulty ladder built into the mathematics.

### Bit Length as Mass/Weight

Two seeds in the same dropping set have the same orbit *shape* but different *weight*:

| Seed | Bit Length | Dropping Set | Steps | Mass | Region Explored |
|------|-----------|-------------|-------|------|-----------------|
| 5 | 3 bits | Set_3 | 3 | Light | Near origin |
| 21 | 5 bits | Set_3 | 3 | Medium | Local neighborhood |
| 12,341,234,123,412,341 | 54 bits | Set_3 | 3 | Heavy | Deep frontier |

Same work structure. Same verification cost. But the heavy seed:
- Touches a different (possibly unexplored) region of the address space
- Involves larger intermediate values (more information per step)
- Its orbit visits composites that factorize differently (different prime streams)
- Carries more "gravitational weight" as a discovery

### Orbit Properties as Reward Heuristics

| Property | What It Measures | Reward Implication |
|----------|-----------------|-------------------|
| `dropping_set` (k) | Structural difficulty | Base reward tier |
| `bit_length` | Mass/scale | Multiplier on base reward |
| `orbit_max` | How "far" the trajectory went | Exploration depth bonus |
| `orbit_sum` | Total work done | Energy value of the proof |
| `alpha_sequence` | Route pattern (odd step positions) | Uniqueness/rarity bonus |
| `genus` | Step composition (S, M, I counts) | Structural rarity |
| `dropping_destination` | Where you ended up | What region was discovered |

### Pseudorandom Balance

The distribution of dropping sets across the number line is well-understood:
- ~50% of odd numbers are in Set_3 (residue class mod 4)
- ~12.5% in Set_6 (mod 16)
- ~12.5% in Set_8 (mod 32)
- Deeper sets are exponentially rarer (mod 128, 256, 1024, ...)

This gives us a natural loot table. Easy work is abundant. Hard work is rare. And within each tier, the bit length adds a second axis of value. A game designer can tune rewards by adjusting:
- **Which dropping sets are "in season"** (rotating reward bonuses per epoch)
- **Bit length thresholds** (minimum mass for premium rewards)
- **Orbit shape bonuses** (rare alpha sequences or genus triples get multipliers)

## Collatz Connection

This spec IS the Collatz connection. Every concept maps directly:

| Emanon Concept | Collatz Math |
|---------------|-------------|
| VDF computation | Collatz orbit |
| Difficulty tier | Dropping set k |
| Mass/weight | Bit length of seed |
| Route pattern | Alpha sequence |
| Structural signature | Dropping genus (S, M, I) |
| Destination/discovery | Dropping destination |
| Work done | Orbit sum |
| Exploration depth | Orbit max |
| Verification | Orbit retracement |
| Difficulty distribution | 2-adic residue class density |
| Impossible difficulties | Gap classes in odd stopping time spectrum |

### Key Proven Properties That Support Game Balance

- **Affine orbit structure**: dest(n) = (3^s / 2^(k-s)) * n + C within each residue subgroup. The slope is universal — same "physics" at every scale within a dropping set.
- **2-adic determinism**: mod 2^p determines which Set_k a number belongs to. The game can pre-classify regions of the address space by difficulty.
- **Conservation law**: s * log2(6) = T - log2(n) + epsilon. The energy balance of each orbit is bounded. No orbit produces unbounded reward.
- **Logarithmic escape**: self-chains in any Set_k are bounded by O(log n). You can't stay in the same difficulty tier forever — the orbit must eventually escape to a different set.
- **Spectral gap (5/6)**: mixing across difficulty tiers is fast. The mining economy doesn't get stuck in one tier.

## Integration Points

- **[[Infrastructure & Scale]]**: VDF replaces generic proof-of-work. Mining = computing Collatz orbits.
- **[[Energy & Conservation]]**: VDF output (orbit sum, orbit max) maps to energy tokens. The conservation law bounds energy production per orbit.
- **[[Bloom Filters & Scanning]]**: VDF destination seeds the bloom filter scan. The miner's discovery is tied to where the orbit ended.
- **[[Event Schema & Log]]**: VDF proofs are events in the miner's log. The orbit IS the causal chain.
- **[[Turn Mechanics & Game Loop]]**: mining is an action that costs a tick (you spend the tick computing the orbit).
- **[[Roguelite Persistence]]**: atlas knowledge from mining persists — explored regions are VDF destinations from past runs.

## Tasks
- [ ] Implement Collatz orbit computation as VDF (using existing `collatz/core.py`)
- [ ] Implement VDF proof structure (seed, orbit, properties, hash)
- [ ] Implement VDF verification (orbit retracement, property confirmation)
- [ ] Define reward function: f(dropping_set, bit_length, orbit_properties) → energy + loot
- [ ] Implement difficulty targeting (constrain mining to specific dropping sets)
- [ ] Implement bit-length-based mass weighting
- [ ] Implement orbit property extraction (alpha sequence, genus, max, sum)
- [ ] Implement "in season" rotation mechanic for dropping set reward bonuses
- [ ] Integration with bloom filter scanning (VDF destination → scan target)
- [ ] Integration with atlas persistence (VDF destinations → explored regions)
- [ ] Balance testing: run mining simulations across difficulty tiers, measure reward distributions

## Open Questions
- Should miners choose their seed or be assigned one? (Choice = strategy, assignment = fairness)
- Is there a minimum bit length to prevent trivial mining of small numbers?
- How do we handle the ~89% of odd numbers classifiable by mod 4096? Pre-computed difficulty maps?
- Should VDF proofs be tradeable between primes? (Selling your exploration work)
- Can orbit properties unlock specific game content? (e.g., a rare alpha sequence opens a hidden region)
