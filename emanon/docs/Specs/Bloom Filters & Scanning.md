---
jira: ALPHA-12
status: draft
type: story
---

# Bloom Filters & Scanning

## Overview
Every prime stream maintains a bloom filter over its events. The filter is the universe's spectrum — public, cheap to query, probabilistic. It IS the gravitational signal. Mass and entropy make filters noisy; young sparse universes have clean filters.

## Concepts
- **Bloom filter**: probabilistic set membership — no false negatives, tunable false positive rate
- **Scanning**: checking a filter without triggering an observation event (no causal cost)
- **Gravitational signal**: bloom filter emissions are involuntary — every prime broadcasts its filter
- **Filter saturation**: dense/old universes say "maybe" to everything — their signal is noisy
- See [[Cosmology]] for gravity-as-entropy-leakage

## Requirements
1. Every prime maintains a bloom filter updated on each event emission
2. Filters are public — any prime can scan any filter without causal cost
3. Events are hashed on multiple dimensions: entity, attribute, causal thread, value class
4. Composite filters are the union of constituent prime filters
5. False positive rate scales with log volume (mass) and incompressibility (entropy)
6. [[Merkle Trees & Timeline Verification|Merkle roots]] can be inserted into filters for timeline-level scanning
7. **Anomaly generation**: the persistent world generates bloom filter anomalies — unusual signal patterns that serve as exploration hooks. Anomalies include: Merkle fragments from dead civilizations, dead star remnants, unexplained high-entropy regions
8. **Atlas persistence**: scanned bloom filter signatures persist in the player's meta-profile across runs. Explored regions are marked in the atlas. See [[Roguelite Persistence]]
9. **Merkle fragment seeding**: players carrying Merkle fragments from past runs (black hole collapse loot) start with pre-populated bloom filter entries — they look ancient to scanners

## Collatz Connection
- Residue class membership (mod 2^k) is a deterministic set membership test — the exact version of what bloom filters approximate
- The spectral gap (5/6) governs how fast bloom filter queries "mix" across the address space

## Tasks
- [ ] Implement bloom filter with configurable size and hash count
- [ ] Define hash functions for the four event dimensions
- [ ] Implement filter union for composite addresses
- [ ] Implement scan protocol (query without observation)
- [ ] Metrics: saturation rate, false positive rate, entropy estimate
- [ ] Implement anomaly generation for persistent world (types: merkle fragment, dead star, high-entropy region)
- [ ] Implement atlas integration: record scanned signatures to meta-profile
- [ ] Implement Merkle fragment seeding at genesis from meta-profile

## Open Questions
- What bloom filter size per prime? Fixed or scaling with log length?
- How frequently are filters broadcast? Every tick? On-demand?
- Can filters be pruned/rebuilt, or are they strictly append-only like logs?
