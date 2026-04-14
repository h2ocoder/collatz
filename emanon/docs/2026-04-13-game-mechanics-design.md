# Emanon Game Mechanics & Player Experience Design

**Date:** 2026-04-13
**Status:** approved

## Game Identity

Emanon is a **roguelite 4X** built on information-theoretic physics. Each run, you genesis as a single prime, explore a procedurally-seeded neighborhood, and navigate the tension between self-preservation and collective survival. Choices have consequences governed by Collatz dropping sets. Between runs, your death type determines what loot carries forward.

Multiplayer is supported from day one. All primes — human players, scripted NPCs, LLM-backed NPCs — speak the same protocol. The system doesn't know or care what drives a prime.

## Modes

### Scenarios
Objective-based, session-based multiplayer lobbies. Controlled environments for testing specific strategies. Clean start, clean end.

Each scenario defines:
- Starting distribution (tuned seed)
- Objective chain (ordered goals)
- NPC primes (scripted, pre-configured)
- Recipe templates (which dropping sets are active)
- Win/loss conditions
- Loot table (what carries forward)

Each scenario measures:
- Ticks survived
- Energy efficiency (spent vs produced)
- Trust score at end
- Composite size reached
- Address space explored
- Player choices at decision points

### Cold Drop (Freeplay)
Persistent shared multiverse. No objectives. No guidance. Encounter other players and LLM-backed NPCs organically. Multiple end states. The real roguelite experience.

## Core Tension

Self-preservation vs collective preservation at every decision point:
- Sharing logs builds trust and fuels stars, but makes you visible and harder to rewrite
- Hoarding preserves sovereignty but leads to energy starvation and isolation
- The physics makes cooperation advantageous without mandating it

Incentive layers by progression stage:
1. **Early game:** Share to get found (bloom filter visibility = discovery)
2. **Mid game:** Share to light a star (stellar ignition requires fuel from multiple primes)
3. **Late game:** Trust score unlocks governance roles and composite access (cross-references build reputation)

## Run Structure

### Genesis (Tick 0)
- Loading screen: the word "EMANON"
- Genesis prompt: "Hello world. I am ______"
- Player's input determines prime type and faction affinity
- The tutorial IS the genesis event — no separate onboarding

### Starting Distribution
Pseudorandom but tuned. Not purely random — shaped to guarantee interesting conditions:
- At least one weak star within scanning range (survival loop reachable)
- At least one other prime nearby (social loop reachable)
- At least one bloom filter anomaly (exploration loop has a hook)
- Distribution parameters are dials we tune through playtesting

### Early Game (Ticks 1-10)
1. **First scan** — discover the neighborhood. Map view shows bloom filter signals as light.
2. **First observation** — spend energy to read another prime's log. Log view.
3. **First sharing decision** — share your log or stay hidden. Core tension introduced.
4. **Survival pressure** — energy depletes. Can't light a star alone. Physics pushes cooperation.

### Mid Game (Ticks 20-100)
Three viable playstyles (all available, tested via scenarios):
- **Territory building** — merge with primes, grow composite, become gravitationally significant
- **Deep exploration** — push outward, mine new regions, catalog anomalies, stay light
- **Specialization** — lean into prime type strengths, find composites that need your role

### End States

**Scenarios:** End on objective completion or failure.

**Freeplay (multiple organic endings):**
- **Energy death** — go dark when energy hits zero
- **Absorption** — composite grows so large you lose individual identity (you "won" but you're gone)
- **Black hole collapse** — your star consumes itself and takes you with it
- **Voluntary exit** — choose to end the run and bank your loot

## Consequence System (Collatz Recipes)

Choices have active effects governed by Collatz dropping sets. While an event is "dropping" (hasn't reached below its starting value), its effects are live. Once it reaches its dropping destination, the event settles — still in the bloom filter forever (the universe remembers), but no longer exerting active force.

### Recipes
A recipe is a composition of dropping set rounds:
- **Set_3 rounds** — fast resolution. Immediate effects.
- **Set_6 rounds** — medium duration. Ripple effects.
- **Deep Set_k rounds** — slow burn. Long echo.

### Recipe Assignment: Template + Modifier
Each action type has a **base recipe template** (the design lever):

| Action | Example Recipe | Feel |
|--------|---------------|------|
| Scan | `[2 x Set_3]` | Quick pulse, gone |
| Observe | `[3 x Set_3, 1 x Set_6]` | Brief with short tail |
| Share log | `[2 x Set_3, 2 x Set_6]` | Moderate sustained effect |
| Merge | `[3 x Set_3, 4 x Set_6, 2 x Set_8, 1 x Set_k]` | Shock + restructuring + long tail |
| Fork/betray | `[1 x Set_3, 1 x Set_very_deep]` | Brief flash, long slow burn |

**Context modifiers** adjust the recipe based on:
- Your prime address and the target's address
- Tick number
- Energy spent
- Trust relationship between parties

The same action type with different context produces different recipe durations. A merge with a high-trust prime has shorter deep-set rounds. A merge with an unknown prime has longer ones.

### Bloom Filter Permanence
The bloom filter records the event hash forever. The dropping set governs how long it *matters mechanically*. The bloom filter is the scar. The dropping set is the wound. Wounds heal. Scars are permanent.

## Roguelite Persistence

### Loot by Death Type
What carries forward between runs depends on how the run ended:

| End State | Loot Type | Rationale |
|-----------|-----------|-----------|
| Energy death | Atlas knowledge (map fragments) | You explored well but couldn't sustain |
| Absorption | Trust residue (meta-reputation) | You were social but lost sovereignty |
| Black hole collapse | Merkle fragments (timeline echoes) | You went deep |
| Voluntary exit | Player chooses one category | Controlled departure, controlled reward |

### Persistent Effects
- **Atlas knowledge:** Start subsequent runs with a better map of the address space
- **Trust residue:** New primes start with a trust floor based on past runs
- **Merkle fragments:** Start with echoes in your bloom filter — other primes see a weirdly experienced newborn

## Tutorial System

### Purpose
The tutorial is also the playtest harness. Build the tutorial, build the game loop in miniature.

### Structure: Silent Objectives + Witness Narrator
- **Silent objectives** appear in the corner — short, no explanation of how. Player figures it out by interacting with the physics.
- **Witness narrator** is an ancient witness prime nearby on the first run. Its log contains testimony from past events. Optional depth for curious players.

### Objective Chain
1. **"Declare yourself."** — Type genesis line. Teaches: you are a log, type matters.
2. **"Scan your surroundings."** — Use scan on bloom filters. Teaches: scanning is cheap, map reveals signals.
3. **"Observe something."** — Read another prime's log. Teaches: observation costs energy.
4. **"Share your log."** — Let another prime reference your events. Teaches: sharing builds trust and visibility.
5. **"Light a star."** — Contribute logs with another prime. Teaches: cooperation produces energy.
6. **"Survive 20 ticks."** — Experience the full energy loop. Teaches: energy management.
7. **"Make a choice."** — Fork: merge with composite (safety) or explore anomaly alone (risk). Teaches: the core tension. No right answer.

Objective 7 transitions from tutorial to real gameplay.

## Scenarios

### Scenario 1: The Frontier (Explore + Expand)
- **Premise:** Fertile region with scattered primes and a dying star. Explore to find primes, merge to build a composite, sustain energy before the star goes out.
- **Strategy tested:** Exploration and territory building combined
- **Objectives:** Find 3+ primes, merge into composite of 3+, keep star alive for 50 ticks
- **NPCs:** Scripted primes with varying willingness to merge
- **Win:** Star sustained + composite of 5+
- **Loss:** Star dies or energy death
- **Metrics:** Ticks survived, merge success rate, territory controlled, energy efficiency

### Scenario 2: The Collision (Conflict)
- **Premise:** Two composites sharing prime factors. Contested streams. Resolve or dominate.
- **Strategy tested:** Conflict resolution, governance under pressure
- **Objectives:** Resolve or win the contested streams
- **NPCs:** Two scripted factions with opposing interests
- **Win:** Contested streams resolved (via merge, fork, or dominance)
- **Loss:** Both composites collapse (mutual destruction) or energy death
- **Metrics:** Conflict resolution method, forgiveness used, governance changes, casualties

### Scenario 3: The Witness (Specialist)
- **Premise:** Two factions merging. Your attestation determines trust. Choose carefully.
- **Strategy tested:** Witness mechanics, diplomacy, trust
- **Objectives:** Attest truthfully or strategically, influence the outcome
- **NPCs:** Two scripted factions seeking your testimony
- **Win:** Stable merge achieved (or deliberate fork if warranted)
- **Loss:** False attestation discovered (trust destroyed) or both factions reject you

### Future Scenarios
Built as playtesting reveals what mechanics need isolation and testing.

## Multiplayer Architecture

### Principle: All Primes Are Equal
Human players, scripted NPCs, and LLM-backed NPCs all implement the same prime protocol. The system routes observe/emit/scan calls identically regardless of what's driving the prime.

### Session Types
- **Scenarios:** Multiplayer lobbies. Players join a scenario together, shared starting region, same tick clock. Defined player count.
- **Freeplay:** Persistent shared multiverse. Players drop in and out. Encounter whoever's there.

### Pacing
- **Solo exploration:** Pure turn-based. Think as long as you want.
- **In a composite:** Async turn-based. All primes submit actions, universe advances when all have submitted or timeout hits.
- **Governance determines timeout:** Authoritarian composites have tight deadlines. Anarchic composites have loose ones.

### NPC Tiers
- **Scripted NPCs (scenarios):** Behavior trees. Predictable, tunable, cheap. Test fixtures.
- **LLM-backed NPCs (freeplay):** Full LLM agents with system prompts defining personality/strategy. Unpredictable, emergent, expensive. Living world.

## UI Design Principles

### Map View (Navigation)
- Bloom filter signals rendered as light/heat sources
- Energy bar always visible
- Nearby primes as nodes with type indicators
- Scan radius visualized
- Anomalies pulsing

### Log View (Interaction)
- Read another prime's event history
- Decision prompts at the bottom (share / observe silently / propose merge)
- Cost of each action shown

### Core Principle
**Surface what matters, help the player prioritize.** The UI's job is not to show everything — it's to help the player figure out which decisions are important and give them the information to make those decisions well.

## Specs Requiring Updates

Based on this design, the following existing specs need additions:

| Spec | Addition Needed |
|------|----------------|
| [[Event Schema & Log]] | Collatz recipe field on events; active/settled status |
| [[Turn Mechanics & Game Loop]] | Scenario mode vs freeplay mode; async composite ticks; timeout governance |
| [[Merge & Governance]] | Absorption end state; governance-determined timeouts |
| [[Energy & Conservation]] | Starting energy budget; energy death mechanics; star ignition threshold |
| [[Bloom Filters & Scanning]] | Anomaly generation; atlas persistence between runs |
| [[Infrastructure & Scale]] | Multiplayer session management; NPC tiers; persistent world storage |
| [[Stellar Compression]] | Dying star mechanics; star ignition requirements (multi-prime fuel) |

## New Specs Needed

| Spec | Purpose |
|------|---------|
| Roguelite Persistence | Loot types, death-to-loot mapping, meta-profile, atlas |
| Tutorial & Scenario System | Objective framework, scenario definitions, witness narrator, metrics |
| NPC System | Scripted behavior trees, LLM agent protocol, tier switching |
| Multiplayer & Sessions | Lobby system, persistent world, async tick coordination |
