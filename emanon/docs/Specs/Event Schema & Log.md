---
jira: ALPHA-10
status: draft
type: story
---

# Event Schema & Log

## Overview
The event is the atom of truth in Emanon. All state is derived from append-only event logs. A "universe" is a fold over its log up to some time t.

## Concepts
- **Event**: the irreducible unit — has a body, causal parents, type, and optional entanglement ID
- **Log**: a Merkle-committed append-only sequence of events; the program's state
- **Genesis event**: line zero of every log — self-referential, no causal parents, "Hello world. I am ______"
- **Causal parents**: DAG edges linking an event to the events it depends on
- See [[Log Types]] for the six prime types (particle, force, field, law, story, witness)

## Requirements
1. Events must declare causal parents (no orphan events except genesis)
2. Logs are append-only and immutable
3. Each log begins with exactly one genesis event
4. Event schema must include: entity, attribute, value, causal parents, entanglement ID (optional)
5. Events must be hashable for Merkle commitment
6. Log type is declared at genesis and constrains valid operations
7. Events carry a **Collatz recipe** — a composition of dropping set rounds that governs how long the event's effects are active (see [[2026-04-13-game-mechanics-design|Game Mechanics Design]])
8. Events have an **active/settled status**: active while the recipe's dropping sets are still iterating, settled once all rounds complete
9. The recipe is determined by **template + modifier**: base template per action type, modified by context (prime address, tick, energy spent, trust relationship)

## Collatz Connection
- The Collatz map is a deterministic causal chain: each step's output is the next step's input
- Dropping orbits are finite event logs with the orbit as the sequence
- The affine structure within residue subgroups means local physics is linear

## Tasks
- [ ] Define event schema (TypeScript interface or Python dataclass)
- [ ] Implement append-only log with hash chaining
- [ ] Implement genesis event creation per log type
- [ ] Define causal parent validation rules
- [ ] Implement Collatz recipe field: template selection, context modifier computation, active/settled tracking
- [ ] Implement recipe tick-down: each game tick advances the recipe's current dropping set round
- [ ] Unit tests: event creation, log append, hash verification, recipe lifecycle

## Open Questions
- Should causal parents be explicit references or content-addressed hashes?
- What's the maximum event body size (mass cap per tick)?
- How do entangled events reference each other across logs?
