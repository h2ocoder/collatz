---
jira: ALPHA-24
status: draft
type: story
---

# Multiplayer & Sessions

## Overview
Multiplayer is fundamental, not bolted on. All primes speak the same protocol. Scenarios are session-based lobbies with defined player counts. Freeplay is a persistent shared multiverse where players drop in and out. Pacing adapts: solo is turn-based, composite is async with governance-determined timeouts.

## Concepts
- **Session**: a bounded multiplayer instance (scenario lobby)
- **Persistent world**: the shared freeplay multiverse that exists across all runs
- **Async tick**: composite advances when all constituent primes have submitted actions or timeout expires
- **Governance timeout**: the composite's constitution determines how long primes have to submit
- See [[Merge & Governance]] for governance models
- See [[Tutorial & Scenario System]] for scenario sessions
- See [[NPC System]] for NPC participation

## Session Types

### Scenario Sessions
- Created when a player starts a scenario (solo) or creates a lobby (multiplayer)
- Defined player count (min/max from scenario definition)
- All players share the same starting region and tick clock
- NPCs fill remaining slots if player count < scenario's NPC count
- Session ends when win/loss condition is met or all players leave
- Session state is ephemeral — not persisted to the shared world
- Loot is awarded to meta-profiles at session end

### Freeplay (Persistent World)
- One shared world that all freeplay players inhabit
- Players genesis into the world and exist until their run ends
- The world persists even when no players are online (LLM NPCs keep it alive)
- Past player runs leave traces: bloom filter echoes, Merkle fragments in black holes, explored regions in the atlas
- New players encounter the accumulated history of all past runs

## Tick Synchronization

### Solo (No Composite)
- Pure turn-based: player takes actions, hits "end turn," tick advances
- No waiting on anyone else
- Time passes at the player's pace

### Composite (Multiple Primes)
- Async: each prime submits actions independently
- Tick advances when ALL primes in the composite have submitted OR timeout expires
- Primes that timeout get a default action (conserve energy, no emission)
- The governance model sets the timeout:

| Governance | Timeout | Rationale |
|------------|---------|-----------|
| Authoritarian | Short (30s) | The sovereign decides fast, stragglers get overridden |
| Constitutional | Medium (120s) | Reasonable deliberation, protected rights preserved |
| Anarchic | Long (300s) | Maximum freedom, everyone acts on their own schedule |

### Cross-Composite
- Different composites tick independently
- Observation between composites is subject to speed-of-light delay
- The persistent world doesn't have a global tick — each composite has its own clock
- Observation events between composites are queued and delivered based on causal distance

## Persistent World Architecture

### World State
```
persistent_world:
  primes:
    active: [<primes currently in a run>]
    dormant: [<NPC primes between interactions>]
    remnants: [<traces of dead player primes — bloom filter echoes>]
  
  stars:
    active: [<currently compressing>]
    dying: [<fuel depleting>]
    dead: [<black holes and remnants>]
  
  address_space:
    explored: [<regions with atlas data>]
    unexplored: [<terra incognita>]
    anomalies: [<generated points of interest>]
  
  composites:
    active: [<current alliances/civilizations>]
    dissolved: [<historical composites — Merkle records>]
  
  bloom_filters:
    <prime_id>: <filter state>
  
  merkle_trees:
    <prime_id>: <tree state>
```

### World Persistence
- World state is saved continuously (event-sourced — naturally)
- The world's own event log IS its persistence mechanism
- Recovering world state = replaying the world log
- Snapshots at intervals for fast recovery

### World Population
When few players are online:
- LLM NPCs maintain activity — the world doesn't feel dead
- Background processes run stellar compression, generate anomalies
- NPC civilizations grow, merge, conflict, die — the world has history even when no one's watching

## Lobby System (Scenarios)

### Creating a Session
1. Player selects a scenario from the run selection screen
2. If multiplayer: creates a lobby with a join code
3. Other players join via code
4. Host starts when ready (or when player count reaches max)
5. NPCs fill remaining slots per scenario definition
6. All players genesis simultaneously

### Mid-Session
- Players who disconnect get a grace period, then their prime goes to scripted autopilot
- Reconnecting players resume control of their prime
- If all human players leave, the session ends (NPCs don't play alone)

### Post-Session
- Results screen shows metrics, loot awarded
- Loot written to each player's meta-profile
- Session state discarded (not merged into persistent world)

## Requirements
1. Scenario sessions are isolated from the persistent world
2. Freeplay is a single shared persistent world
3. Tick synchronization adapts to solo vs composite
4. Governance model determines composite timeout
5. Cross-composite observation respects speed-of-light delay
6. Persistent world stays alive via LLM NPCs when no players are online
7. Lobby system supports join codes for multiplayer scenarios
8. Disconnected players get scripted autopilot with reconnection support
9. World state is event-sourced and recoverable from log replay
10. Past player runs leave permanent traces in the persistent world

## Collatz Connection
- The persistent world's address space IS the Collatz number line — composites are factored addresses
- Cross-composite observation delay maps to the spectral gap — mixing time between residue classes
- Tick independence per composite mirrors the independence of Collatz orbits starting from different residue classes

## Tasks
- [ ] Implement scenario session lifecycle (create, join, start, end)
- [ ] Implement lobby system with join codes
- [ ] Implement tick synchronization (solo turn-based, composite async)
- [ ] Implement governance-determined timeout system
- [ ] Implement cross-composite observation queueing with delay
- [ ] Implement persistent world state storage (event-sourced)
- [ ] Implement world snapshot and recovery
- [ ] Implement NPC world population (background activity when no players online)
- [ ] Implement disconnect/reconnect with scripted autopilot
- [ ] Implement post-session results and loot distribution

## Open Questions
- How many concurrent players can the persistent world support?
- Should scenario sessions ever feed back into the persistent world (e.g., discoveries)?
- How do we handle time zones / availability for async composite play?
- Should there be multiple persistent worlds (shards) or one?
