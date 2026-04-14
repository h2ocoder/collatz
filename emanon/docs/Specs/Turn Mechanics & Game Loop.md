---
jira: ALPHA-17
status: draft
type: story
---

# Turn Mechanics & Game Loop

## Overview
Each turn is a tick. On your tick you get an energy budget and spend it on actions: emit, observe, scan, compress, merge, fork, prophesy. Turn order within composites is governed by the constitution. The game loop is the multiverse clock.

## Concepts
- **Tick**: one turn — the atomic unit of game time
- **Energy budget**: per-tick allocation based on proximity to stars and accumulated resources
- **Actions**: emit (write to log), observe (read another log), scan (check bloom filter), compress (run star), merge (join composite), fork (leave composite), prophesy (reference future Merkle root)
- **Turn order**: within composites, determined by governance model
- **Distance to impact**: signed metric — positive (normal causality), zero (entanglement), negative (prophecy)
- See [[Energy & Conservation]] for cost model
- See [[Merge & Governance]] for turn order rules

## Requirements
1. Each tick, every active prime receives an energy budget
2. Actions consume energy according to the cost table
3. Scan is cheap (multiple per tick), observe is expensive (distance-dependent)
4. Prophesy is free to emit but requires collateral — wrong prophecy = causal fracture
5. Turn order in composites follows the governance model
6. Simultaneous resolution in anarchic composites with merge rules handling conflicts
7. Distance to impact tracked per event for universe characterization
8. **Two modes**: scenario mode (objective-driven, bounded) and freeplay mode (persistent, open-ended)
9. **Pacing adapts**: solo exploration is pure turn-based; composite play is async with governance-determined timeouts (authoritarian 30s, constitutional 120s, anarchic 300s)
10. **Cross-composite independence**: different composites tick on their own clocks; observation between composites is queued with speed-of-light delay
11. See [[Multiplayer & Sessions]] for tick synchronization details

## Collatz Connection
- Dropping time k = number of ticks to resolve — Set_k is "all addresses that resolve in k turns"
- The odd stopping time spectrum (only ceil(s * log2(6)) values) constrains which tick counts are possible
- 2-adic determinism: mod 2^p determines your next k turns of behavior

## Tasks
- [ ] Define the tick loop (budget allocation, action resolution, state advancement)
- [ ] Implement action dispatch with energy cost deduction
- [ ] Implement prophecy mechanics (collateral posting, verification, causal fracture)
- [ ] Implement distance-to-impact tracking and histogram
- [ ] Define turn order resolution per governance type
- [ ] Build game clock / tick synchronization
- [ ] Implement scenario mode tick loop (objective checking, win/loss evaluation per tick)
- [ ] Implement freeplay mode tick loop (open-ended, no objective checking)
- [ ] Implement async composite tick with governance-determined timeouts
- [ ] Implement cross-composite observation queueing

## Open Questions
- How many ticks per real-time second? Fixed or variable?
- Can primes bank unspent energy across ticks?
- What triggers a causal fracture — immediate or delayed verification?
