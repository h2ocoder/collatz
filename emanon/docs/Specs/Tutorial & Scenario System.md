---
jira: ALPHA-22
status: draft
type: story
---

# Tutorial & Scenario System

## Overview
The tutorial teaches mechanics through silent objectives and an optional witness narrator. Scenarios are controlled playtests that isolate specific strategies. Together they form the playtest lab — each scenario is a hypothesis about what's fun, and the metrics tell us if we're right. Design by exploration.

## Concepts
- **Silent objective**: a short goal displayed in the corner with no explanation of how to achieve it
- **Witness narrator**: an ancient witness prime whose log contains instructive testimony from past events
- **Scenario**: a controlled environment with defined starting conditions, objectives, NPCs, and metrics
- **Playtest lab**: the scenario system as a design tool, not just a player-facing feature
- See [[2026-04-13-game-mechanics-design|Game Mechanics Design]] for scenario definitions

## Tutorial: First Light

### Structure
Silent objectives + witness narrator. Objectives guide the player through the core loop. The witness is there for curious players who want to understand why things work.

### Objective Chain

| # | Objective | Teaches | Completion Trigger |
|---|-----------|---------|-------------------|
| 1 | "Declare yourself." | Genesis, prime types, identity | Player submits genesis line |
| 2 | "Scan your surroundings." | Scanning is cheap, map reveals signals | Player performs 3+ scans |
| 3 | "Observe something." | Observation costs energy, logs are readable | Player observes any prime |
| 4 | "Share your log." | Sharing builds trust and visibility | Player shares log with any prime |
| 5 | "Light a star." | Cooperation produces energy, can't sustain alone | Star ignites (requires 2+ log contributors) |
| 6 | "Survive 20 ticks." | Energy management, full cycle | Player reaches tick 20 with energy > 0 |
| 7 | "Make a choice." | The core tension, no right answer | Player chooses merge or solo exploration |

### Witness Narrator
- Prime type: witness
- Behavior: scripted (not LLM)
- Log contains 5-8 attestation events from "past events":
  - "I was here when the last star died. No one shared their logs."
  - "I saw two primes merge. Their star burned for a hundred ticks."
  - "I witnessed a prime hoard its log. It went dark at tick 14."
- The witness doesn't approach the player — the player discovers it through scanning
- Reading the witness's log is optional but illuminating

### Tutorial Starting Distribution
Highly controlled:
- 1 dim star (enough fuel for ~30 ticks if fed)
- 1 friendly NPC prime (scripted, willing to share/merge)
- 1 cautious NPC prime (scripted, only shares after player shares first)
- 1 witness narrator prime
- 1 bloom filter anomaly (for objective 7's exploration path)
- Player starts with 100 energy

## Scenario Framework

### Scenario Definition Schema

```
scenario:
  id: <unique identifier>
  name: <display name>
  tag: <strategy category — territory, exploration, conflict, specialist>
  premise: <1-2 sentence narrative setup>
  
  distribution:
    star_count: <number and type of stars>
    npc_primes: [<list of NPC definitions>]
    anomalies: [<list of anomaly definitions>]
    player_start_energy: <number>
    address_space_bounds: <region definition>
  
  objectives:
    - id: <objective id>
      text: <display text>
      trigger: <completion condition>
      optional: <boolean>
  
  win_condition: <expression over objectives and game state>
  loss_conditions:
    - <expression over game state>
  
  recipes:
    <action overrides for this scenario's dropping set templates>
  
  loot_table:
    win: <loot definition>
    loss: <loot definition — reduced>
  
  metrics:
    - <list of measurements to record>
  
  max_ticks: <optional hard time limit>
  player_count:
    min: 1
    max: <number>
```

### Scenario 1: The Frontier (Explore + Expand)

```
scenario:
  id: frontier
  name: "The Frontier"
  tag: territory + exploration
  premise: "A fertile region with scattered primes and a dying star. Explore, merge, survive."
  
  distribution:
    star_count: 1 (dying — fuel for ~50 ticks without additional input)
    npc_primes:
      - type: particle, behavior: willing_to_merge, trust: 0.3
      - type: particle, behavior: cautious, trust: 0.1
      - type: particle, behavior: hostile, trust: 0.0
      - type: force, behavior: trader, trust: 0.5
      - type: witness, behavior: observer, trust: 0.7
    anomalies:
      - type: merkle_fragment, depth: medium
      - type: dead_star_remnant
    player_start_energy: 100
    address_space_bounds: 1000 addresses
  
  objectives:
    - id: find_3, text: "Find 3 primes", trigger: observed_primes >= 3
    - id: merge_3, text: "Build a composite of 3+", trigger: composite_size >= 3
    - id: sustain_star, text: "Keep the star alive for 50 ticks", trigger: star_alive_at_tick_50
    - id: composite_5, text: "Grow to composite of 5+", trigger: composite_size >= 5, optional: true
  
  win_condition: find_3 AND merge_3 AND sustain_star
  loss_conditions:
    - star_dead AND composite_size < 3
    - player_energy <= 0
  
  loot_table:
    win: atlas_knowledge(full) + trust_residue(moderate)
    loss: atlas_knowledge(partial)
  
  metrics:
    - ticks_survived
    - merge_success_rate
    - merge_rejection_count
    - energy_efficiency (produced / spent)
    - territory_controlled (address count)
    - time_to_first_merge
    - npc_interaction_log
  
  max_ticks: 100
  player_count: { min: 1, max: 4 }
```

### Scenario 2: The Collision (Conflict)

```
scenario:
  id: collision
  name: "The Collision"
  tag: conflict
  premise: "Two composites sharing prime factors. Contested streams. Resolve or dominate."
  
  distribution:
    star_count: 1 (healthy — not the constraint here)
    npc_primes:
      - faction_a: [3 particles, 1 force] — aggressive governance, authoritarian
      - faction_b: [3 particles, 1 force] — defensive governance, constitutional
      - contested_streams: [2 primes shared by both factions]
    anomalies: none (conflict IS the content)
    player_start_energy: 120
    address_space_bounds: 500 addresses (tight — forced proximity)
  
  objectives:
    - id: assess, text: "Observe both factions", trigger: observed_faction_a AND observed_faction_b
    - id: resolve, text: "Resolve the contested streams", trigger: contested_streams_resolved
  
  win_condition: resolve (by any method — merge, fork, dominance, negotiation)
  loss_conditions:
    - both_factions_collapsed
    - player_energy <= 0
    - max_ticks exceeded without resolution
  
  loot_table:
    win: trust_residue(high) + merkle_fragments(from resolution)
    loss: trust_residue(low)
  
  metrics:
    - resolution_method (merge / fork / dominance / negotiation)
    - forgiveness_events
    - governance_changes
    - casualties (primes lost)
    - time_to_resolution
    - player_alignment (which faction, if any)
  
  max_ticks: 80
  player_count: { min: 1, max: 2 }
```

### Scenario 3: The Witness (Specialist)

```
scenario:
  id: witness
  name: "The Witness"
  tag: specialist
  premise: "Two factions merging. Your attestation determines trust. Choose carefully."
  
  distribution:
    star_count: 1 (shared between factions)
    npc_primes:
      - faction_a: [2 particles, 1 law] — claims rightful ownership of stream
      - faction_b: [2 particles, 1 story] — claims historical precedent
      - contested: 1 shared stream with ambiguous history
    anomalies:
      - type: historical_record (merkle fragment that supports one faction's claim)
    player_start_energy: 80
    player_forced_type: witness
    address_space_bounds: 300 addresses
  
  objectives:
    - id: observe_both, text: "Hear both sides", trigger: read_faction_a_log AND read_faction_b_log
    - id: find_evidence, text: "Investigate the record", trigger: read_anomaly, optional: true
    - id: attest, text: "Give your testimony", trigger: attestation_emitted
  
  win_condition: attest AND (stable_merge OR deliberate_fork)
  loss_conditions:
    - false_attestation_discovered (attestation contradicts merkle evidence)
    - both_factions_reject_player
    - player_energy <= 0
  
  loot_table:
    win: trust_residue(very_high) + merkle_fragments(from witnessed events)
    loss: trust_residue(negative — reputation damaged)
  
  metrics:
    - attestation_accuracy (matched evidence?)
    - factions_trust_in_player
    - outcome_stability (did the resolution hold?)
    - evidence_found (did player investigate?)
    - time_to_attestation
  
  max_ticks: 60
  player_count: { min: 1, max: 1 }
```

## Requirements
1. Tutorial runs on first launch (or when player selects it)
2. Objectives display in corner — appear one at a time, no explanation of how
3. Witness narrator is a regular prime using the game's own mechanics
4. Scenario framework supports arbitrary scenario definitions via the schema above
5. Scenario starting conditions are deterministic given a seed (reproducible for testing)
6. Metrics are recorded per run for analysis
7. Scenarios can be played solo or multiplayer (up to player_count.max)
8. Completion of a scenario unlocks the next in sequence (tutorial → frontier → collision → witness)
9. Cold drop is always available regardless of scenario progress

## Collatz Connection
- Tutorial objective 5 ("Light a star") requires understanding that compression needs redundancy across multiple streams — this is the spectral gap in action
- Scenario recipes use dropping set templates that players experience as consequence duration
- The Frontier's dying star has a fuel metric tied to the conservation law

## Tasks
- [ ] Implement objective display system (corner overlay, sequential reveal)
- [ ] Build witness narrator prime with scripted attestation log
- [ ] Implement scenario definition parser (load from schema)
- [ ] Implement scenario starting distribution generator (deterministic from seed)
- [ ] Implement win/loss condition evaluator
- [ ] Implement metrics recording and storage
- [ ] Build scenario selection screen
- [ ] Implement scenario unlock progression
- [ ] Build The Frontier scenario
- [ ] Build The Collision scenario
- [ ] Build The Witness scenario

## Open Questions
- Should scenarios be replayable with different seeds for variety?
- Should scenario metrics be visible to the player (scorecard) or internal only?
- Can players create custom scenarios (modding)?
