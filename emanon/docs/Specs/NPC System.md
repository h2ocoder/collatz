---
jira: ALPHA-23
status: draft
type: story
---

# NPC System

## Overview
NPCs are primes driven by something other than a human player. They speak the same protocol — observe, emit, scan, merge, fork — and the game engine treats them identically to player primes. The difference is internal: what decides their actions. Two tiers exist: scripted (cheap, predictable, for scenarios) and LLM-backed (expensive, emergent, for freeplay).

## Concepts
- **NPC prime**: any prime not driven by a human player
- **Scripted NPC**: behavior tree determines actions per tick. Deterministic given state.
- **LLM NPC**: language model with system prompt determines actions via tool calls. Non-deterministic.
- **Prime protocol**: the shared interface all primes implement regardless of driver
- See [[Infrastructure & Scale]] for container architecture
- See [[Tutorial & Scenario System]] for NPC role in scenarios

## Prime Protocol Interface

Every prime — human, scripted, or LLM — implements:

```
interface Prime {
  genesis(): Event           // declare yourself
  tick(energy: number): Action[]  // decide what to do this tick
  receive_observation(event: Event): void  // someone observed you
  receive_merge_proposal(from: Prime): Accept | Reject
  receive_fork_notice(from: Prime): void
}
```

The game engine calls `tick()` each turn. What happens inside `tick()` is the prime's business.

## Scripted NPCs (Scenario Tier)

### Behavior Tree Structure

```
behavior:
  name: <display name>
  type: <prime type — particle, force, field, law, story, witness>
  personality:
    trust_threshold: <0.0-1.0 — minimum trust to share/merge>
    aggression: <0.0-1.0 — likelihood of hostile actions>
    curiosity: <0.0-1.0 — likelihood of scanning/exploring>
    sociability: <0.0-1.0 — likelihood of initiating contact>
  
  tick_logic:
    priority_1: <survive — if energy low, conserve>
    priority_2: <personality-driven action selection>
    priority_3: <respond to incoming proposals>
  
  responses:
    merge_proposal: <accept if trust > threshold, reject otherwise>
    share_request: <share if sociability > 0.5 AND requester trust > threshold>
    conflict: <fight if aggression > 0.7, negotiate if < 0.3, fork if between>
```

### Preset Personalities

| Name | Trust | Aggression | Curiosity | Sociability | Use Case |
|------|-------|------------|-----------|-------------|----------|
| Friendly | 0.2 | 0.0 | 0.5 | 0.8 | Tutorial helper, easy merge target |
| Cautious | 0.6 | 0.1 | 0.3 | 0.4 | Requires trust before sharing |
| Hostile | 0.9 | 0.8 | 0.2 | 0.1 | Conflict scenarios, forced merge threat |
| Trader | 0.4 | 0.0 | 0.6 | 0.7 | Force-type, couples primes for mutual benefit |
| Observer | 0.1 | 0.0 | 0.9 | 0.3 | Witness-type, scans everything, attests |
| Hermit | 1.0 | 0.0 | 0.1 | 0.0 | Solo prime, never merges, reference point |

### Determinism
Given the same game state, a scripted NPC always makes the same decision. This is critical for scenario reproducibility and playtesting. Random elements use a seeded RNG tied to the scenario seed.

## LLM NPCs (Freeplay Tier)

### System Prompt Structure

```
You are a prime in the Emanon multiverse.

Identity:
  Name: <name>
  Type: <prime type>
  Personality: <narrative description>
  Goals: <what this prime wants>
  
Constraints:
  - You speak only through the prime protocol (observe, emit, scan, merge, fork)
  - You have an energy budget per tick
  - Your actions have consequences governed by Collatz recipes
  
Context:
  - Your current log (recent events)
  - Your bloom filter state
  - Your current energy
  - Recent observations of nearby primes

Decide your actions for this tick.
```

### Tool Calls
The LLM has access to the same actions as a player:
- `scan(target)` — check a bloom filter
- `observe(target)` — read a log (costs energy)
- `emit(event)` — write to own log (costs energy)
- `share(target)` — allow another prime to reference your log
- `propose_merge(target)` — initiate merge
- `propose_fork()` — leave current composite
- `attest(observation)` — witness-only: record testimony

### Personality via Prompt
Different LLM NPCs feel different because their system prompts encode different values:
- A territorial NPC's prompt emphasizes expansion and resource control
- A diplomatic NPC's prompt emphasizes trust-building and coalition
- A philosophical NPC's prompt emphasizes understanding the protocol
- A trickster NPC's prompt emphasizes deception and short-term advantage

### Cost Management
LLM NPCs are expensive. Mitigation strategies:
- LLM is called once per tick, not per action
- Batch multiple decisions into one LLM call
- Cache personality-consistent responses for common situations
- Downgrade to scripted behavior for routine actions (scanning, energy conservation)
- Only use full LLM reasoning for novel situations (first contact, merge proposals, conflicts)

## Tier Switching

In mixed environments (scenario with some LLM NPCs, or freeplay with some scripted background NPCs):
- The prime protocol is the same — the engine doesn't know the tier
- A prime can be hot-swapped from scripted to LLM mid-run (e.g., a background NPC becomes interesting and gets upgraded to full LLM reasoning)
- Player primes going AFK in freeplay could be downgraded to scripted autopilot

## Requirements
1. All NPCs implement the prime protocol interface
2. Scripted NPCs are deterministic given scenario seed
3. LLM NPCs use tool calls through the same action interface as players
4. Personality presets are configurable per scenario
5. LLM cost is managed through batching and selective reasoning
6. Hot-swapping between tiers is supported mid-run
7. NPC actions are indistinguishable from player actions in the event log
8. NPC primes generate valid events (hashable, Merkle-committable, bloom-filterable)

## Collatz Connection
- Scripted NPC behavior trees mirror the deterministic nature of Collatz orbits — given a starting state, the path is fixed
- LLM NPCs are the "high entropy" primes — unpredictable, incompressible behavior, gravitationally bright
- The scripted/LLM distinction maps to the authoritarian/anarchic axis — ordered vs chaotic

## Tasks
- [ ] Define prime protocol interface (shared by all prime drivers)
- [ ] Implement scripted NPC engine (behavior tree evaluator)
- [ ] Define the 6 preset personalities with tuned parameters
- [ ] Implement LLM NPC engine (system prompt generation, tool call routing)
- [ ] Implement cost management (batching, caching, selective reasoning)
- [ ] Implement tier hot-swapping
- [ ] Implement AFK-to-autopilot for player primes in freeplay
- [ ] Integration tests: scripted NPC in scenario, LLM NPC in freeplay, mixed

## Open Questions
- Which LLM for NPC agents? Same model for all or tiered by NPC importance?
- How many LLM NPCs can the system sustain concurrently in freeplay?
- Should players be able to tell if a prime is human or NPC? Or is ambiguity part of the game?
