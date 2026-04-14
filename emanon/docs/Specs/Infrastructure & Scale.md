---
jira: ALPHA-19
status: draft
type: story
---

# Infrastructure & Scale

## Overview
The multiverse runs as a distributed system of containers. Each prime stream is a Docker container running an LLM agent. Observation is an API call. Speed of light is a bounded read cursor. Entanglement is a shared reference in a coordination layer. The architecture must scale to thousands of concurrent primes.

## Concepts
- **Container per prime**: each prime stream runs in its own isolated container
- **Speed of light as read cursor**: universe A sees universe B's log up to an index that advances at a bounded rate
- **Entanglement registry**: coordination service that tracks shared references across containers
- **Orchestration layer**: knows which containers to read from based on an address's factorization
- **LLM agent**: each prime's behavior is driven by an LLM with tool calls (observe, emit, entangle)
- **Proof of work**: mining = exploring random addresses by factoring, scanning bloom filters, verifying discoveries

## Requirements
1. Each prime runs as an isolated container with its own event log
2. Inter-container communication via observation API (read) and emission API (write)
3. Speed-of-light delay enforced as bounded read cursor advance rate
4. Entanglement registry as a shared coordination service above containers
5. Orchestration layer routes reads based on address factorization
6. System scales horizontally — adding primes = adding containers
7. Proof-of-work mining: random seed, factor address, scan bloom filters, submit verified observations
8. **Multiplayer session management**: scenario sessions are isolated instances; freeplay is one persistent world. See [[Multiplayer & Sessions]]
9. **NPC tiers**: scripted NPCs run lightweight (no LLM, just behavior tree evaluation); LLM NPCs run full model inference per tick. Mixed environments supported. See [[NPC System]]
10. **Persistent world storage**: event-sourced — the world's own log IS its persistence. Snapshots at intervals for fast recovery. World stays alive via NPC activity when no players are online
11. **VDF (Verifiable Delay Function)** integration: proof-of-work for exploration uses VDFs to ensure mining effort is genuine and non-parallelizable. The VDF output seeds the bloom filter scan, making the proof both verifiable and tied to real computation time

## Collatz Connection
- The Collatz Zoo (`collatz/zoo.py`) explores parameter variations — analogous to spinning up universes with different physics
- Container orchestration mirrors the dropping set transition graph — fully connected, every container can reach every other

## Tasks
- [ ] Define container spec (base image, LLM integration, log storage)
- [ ] Implement observation API with speed-of-light delay
- [ ] Implement entanglement registry (shared coordination service)
- [ ] Implement orchestration layer (address factorization -> container routing)
- [ ] Define proof-of-work mining protocol with VDF integration
- [ ] Load testing: target concurrent prime count and tick throughput
- [ ] Implement scenario session lifecycle (create, join, start, end, cleanup)
- [ ] Implement persistent world storage (event-sourced, snapshots, recovery)
- [ ] Implement NPC tier infrastructure (lightweight scripted runner, full LLM runner)
- [ ] Implement world population daemon (NPC activity when no players online)

## Open Questions
- LLM provider per container? Local models vs API calls?
- How is speed-of-light delay computed? Hop count? Shared factor distance?
- Where does the entanglement registry run? Single service or distributed?
- What's the minimum viable deployment (local Docker Compose vs cloud)?
