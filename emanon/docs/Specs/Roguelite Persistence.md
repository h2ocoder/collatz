---
jira: ALPHA-21
status: draft
type: story
---

# Roguelite Persistence

## Overview
Between runs, players carry forward loot determined by how their run ended. The persistence layer bridges ephemeral runs with long-term progression. Death isn't failure — it's a different kind of harvest.

## Concepts
- **Meta-profile**: persistent player identity across runs, accumulating loot from each death
- **Loot**: what carries forward — not items, but structural advantages (knowledge, trust, echoes)
- **Death type**: how a run ended determines the loot category
- See [[2026-04-13-game-mechanics-design|Game Mechanics Design]] for full context

## Loot Types

### Atlas Knowledge (from energy death)
You explored well but couldn't sustain. Your map fragments persist.
- Regions of the address space you scanned are marked as "explored" in future runs
- Bloom filter signatures you cataloged are available at genesis
- Starting scans in explored regions are free (no energy cost)
- Atlas grows across runs — veteran players have a richer map

### Trust Residue (from absorption)
You were social but lost sovereignty. Your reputation persists.
- New primes start with a trust floor based on accumulated absorption runs
- Other primes scanning you see a non-zero trust score at genesis
- Higher trust floor = easier early-game sharing (others are more willing to merge)
- Trust residue decays slowly across runs if not reinforced (use it or lose it)

### Merkle Fragments (from black hole collapse)
You went deep. Timeline echoes persist in your bloom filter.
- New primes start with Merkle root hashes in their bloom filter from past runs
- Other primes scanning you get hits on timelines you never lived — you look ancient
- Fragments can unlock narrative hooks: NPCs recognize the echoes and react
- The deepest fragments (from the longest-lived runs) are the most valuable

### Player's Choice (from voluntary exit)
Controlled departure. You pick one loot category and receive a moderate amount.
- Less than the full payout from the corresponding death type
- Strategic: you sacrifice maximum loot for certainty and choice

## Meta-Profile Structure

```
meta_profile:
  player_id: <persistent identity>
  runs_completed: <count>
  atlas:
    explored_regions: [<address ranges>]
    cataloged_signatures: [<bloom filter hashes>]
  trust:
    floor: <0.0 - 1.0>
    decay_rate: <per-run decay>
    reinforcement_history: [<run summaries>]
  fragments:
    merkle_roots: [<hash, source_run, depth>]
    narrative_flags: [<which echoes NPCs can recognize>]
  run_history:
    - run_id, death_type, ticks_survived, loot_received, timestamp
```

## Requirements
1. Meta-profile persists across all runs (both scenario and freeplay)
2. Loot is awarded at run end based on death type
3. Atlas knowledge accumulates additively (explored regions never un-explore)
4. Trust residue decays between runs if not reinforced by new absorption
5. Merkle fragments are permanent but finite (cap on how many you carry)
6. Voluntary exit gives reduced loot of player's chosen category
7. Meta-profile is readable by the game at genesis to seed starting conditions
8. Scenario runs and freeplay runs both contribute to the meta-profile

## Collatz Connection
- The atlas is a map of the Collatz address space — explored composites, known factorizations
- Trust residue mirrors the 2-adic determinism: deeper modular knowledge = deeper trust foundation
- Merkle fragments are frozen Collatz orbits — timeline echoes of past trajectories through the number space

## Tasks
- [ ] Define meta-profile data model (schema, storage format)
- [ ] Implement loot calculation per death type
- [ ] Implement atlas accumulation (region marking, signature cataloging)
- [ ] Implement trust residue with decay mechanics
- [ ] Implement Merkle fragment storage and bloom filter seeding at genesis
- [ ] Implement voluntary exit loot selection UI
- [ ] Implement meta-profile read at genesis to seed starting conditions
- [ ] Persistent storage backend (local file, database, or cloud)

## Open Questions
- How much atlas knowledge per energy death? All explored regions or a sample?
- What's the trust decay rate? Should it vary by how many runs you've done?
- Is there a cap on Merkle fragments, or do they accumulate forever?
- Should the meta-profile be visible to other players in freeplay?
