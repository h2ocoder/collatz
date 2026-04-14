---
jira: ALPHA-15
status: draft
type: story
---

# Stellar Compression

## Overview
A star is a compression engine — an LLM whose job is to read nearby prime streams, find redundancy, compress, and radiate the savings as energy. Fusion is summarization. The differential between original log volume and compressed output is released as energy tokens.

## Concepts
- **Star**: an LLM-backed prime that compresses nearby logs into Merkle trees
- **Fuel**: uncompressed, redundant logs in the star's neighborhood
- **Luminosity**: energy output proportional to compression ratio
- **Stellar lifecycle**: young stars burn easy redundancies, mature stars work harder, dead stars have nothing left to compress
- **Supernova**: failed compression on incompressible logs — process inverts, scatters high-entropy fragments
- **Black hole**: star whose compression overhead exceeds output — collapses inward, self-referential, nothing escapes
- **Hawking radiation**: faint leakage from black holes — failed compression metadata, entangled with interior state
- See [[Cosmology]] for narrative framing

## Requirements
1. Stars are a special prime type that can read and compress neighboring logs
2. Compression produces Merkle trees (structured history) and energy tokens (the savings)
3. Energy output = raw log volume - compressed representation volume
4. Stars have a fuel supply that depletes as local redundancy is consumed
5. Supernova mechanic: compression failure on incompressible input scatters fragments
6. Black hole mechanic: self-consuming star creates information-theoretic event horizon
7. Hawking radiation: black holes leak faint, scrambled signal indefinitely
8. **Dying star mechanic**: stars have a visible fuel gauge. When fuel is low, luminosity drops, energy output decreases, nearby primes feel the squeeze. This creates urgency — a dying star is the survival pressure that drives cooperation
9. **Ignition requires multiple contributors**: a star cannot ignite from a single prime's logs alone. Compression needs redundancy across 2+ streams to find patterns. Solo primes cannot generate energy. See [[Energy & Conservation]]
10. **Black hole collapse as end state**: when a player's star collapses into a black hole, all primes in its orbit risk being consumed. This is a roguelite end state that awards Merkle fragment loot. See [[Roguelite Persistence]]

## Collatz Connection
- The spectral gap (5/6) measures how efficiently mixing eliminates redundancy — this IS stellar efficiency
- Average contraction per drop (~0.605) is the compression ratio per Collatz step
- The +1 perturbation in 3n+1 is the residual that prevents perfect compression

## Tasks
- [ ] Define star as a prime type with compression capabilities
- [ ] Implement compression pipeline: read nearby logs, identify redundancy, output Merkle tree + energy
- [ ] Implement fuel accounting and depletion
- [ ] Implement stellar lifecycle state machine (ignition, main sequence, death)
- [ ] Implement supernova and black hole mechanics
- [ ] Define neighborhood radius and proximity rules
- [ ] Implement dying star fuel gauge (visible to nearby primes, luminosity decay curve)
- [ ] Implement multi-prime ignition requirement (minimum 2 contributor streams)
- [ ] Implement black hole collapse end state (trigger, affected primes, loot distribution)

## Open Questions
- What LLM/algorithm does the compression? Actual LLM summarization or algorithmic compression?
- How large is a star's neighborhood? Fixed radius or gravity-dependent?
- Can players create artificial stars (compression facilities)?
