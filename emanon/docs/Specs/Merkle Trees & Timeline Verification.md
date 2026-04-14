---
jira: ALPHA-13
status: draft
type: story
---

# Merkle Trees & Timeline Verification

## Overview
Merkle trees are the skeleton of causal threads. The root is the hash of an entire history. A single bloom filter check against a Merkle root answers "did this entire sequence of events happen here?" Stars build Merkle trees as part of compression.

## Concepts
- **Merkle root**: hash of an entire causal history — proves both content and ordering
- **Subtree proof**: log(n) hashes to verify one event's position in a timeline of n events
- **Common ancestor**: deepest shared subtree between two divergent logs (the merge base)
- **Timeline scanning**: bloom filter check against a Merkle root = checking for entire storylines

## Requirements
1. Each log maintains a Merkle tree over its events
2. Merkle roots are inserted into bloom filters for timeline-level scanning
3. Subtree proofs allow verification of individual events without reading the full log
4. Merge operations use Merkle comparison to find the divergence point
5. Stars produce Merkle trees as output of compression (raw events in, structured tree out)
6. Merkle roots are immutable commitments — changing a past event invalidates the root

## Collatz Connection
- Collatz orbits are totally ordered sequences — natural Merkle tree leaves
- The orbit of n is a verified timeline: each step is deterministic from the previous
- Affine structure means subtrees within a residue subgroup share structural properties

## Tasks
- [ ] Implement Merkle tree construction from event log
- [ ] Implement root computation and insertion into bloom filter
- [ ] Implement subtree proof generation and verification
- [ ] Implement common ancestor detection for merge operations
- [ ] Integration with stellar compression pipeline

## Open Questions
- Binary tree or n-ary? (Binary is standard but n-ary might better fit branching causal DAGs)
- How do Merkle trees handle DAG structure (multiple parents) vs. pure sequences?
- What hash function? SHA-256? Something faster for game performance?
