---
jira: ALPHA-16
status: draft
type: story
---

# Merge & Governance

## Overview
Merging is the fundamental social operation. Two primes join a composite by interleaving their logs under agreed-upon rules. The governance model — where a faction sits on the individual-collective spectrum — determines how conflicts are resolved. Forgiveness is mutual recomputation.

## Concepts
- **Merge**: interleaving two event logs, checking for conflicts on shared (entity, attribute) pairs
- **Fork**: splitting from a composite, costs energy proportional to entanglement depth
- **Conflict**: two events in merged logs targeting the same (entity, attribute) with incompatible values
- **Constitution**: the merge policy a composite ratifies — defines conflict resolution rules
- **Anarchic composite**: any prime can fork at any time, low trust, high freedom
- **Constitutional composite**: protected attributes that can't be overridden, bill of rights for primes
- **Authoritarian composite**: sovereign prime has write authority over the merge
- **Forgiveness**: mutual pruning — the forgiven loses mass (reverts to last honest root), the collective loses coherence (dangling references), the star loses energy (recompression cost)
- See [[Factions & Governance]] for narrative framing

## Requirements
1. Merge requires mutual agreement (both parties opt in)
2. Conflict detection: identify shared (entity, attribute) pairs with incompatible values
3. Conflict resolution governed by the composite's constitution
4. Fork operation available to any prime (cost varies by governance model)
5. Skin in the game: joining a composite posts your Merkle root as collateral
6. Corruption detection: trust = inverse compressibility of cross-references (Kolmogorov complexity of reputation)
7. Forgiveness protocol: prune tainted Merkle subtree, recompute from last honest root, mutual cost
8. **Absorption end state**: when a composite grows large enough that an individual prime's identity is subsumed — the prime "wins" (was social, contributed) but loses sovereignty. Triggers trust residue loot. See [[Roguelite Persistence]]
9. **Governance-determined timeouts**: the composite's constitution sets how long primes have to submit actions per tick (authoritarian=tight, anarchic=loose). See [[Multiplayer & Sessions]]
10. **Forced merge (exterminate)**: hostile observation — imposing your event log onto another stream. Conflicts ARE the battle. Resolution mechanics determine the winner

## Collatz Connection
- Dropping set transitions are fully connected (every Set_k reaches every Set_j) — no forbidden merges
- The 3-adic lock (destinations locked mod 3^s) constrains what states a merge can produce
- Residue class structure partitions the address space into natural governance boundaries

## Tasks
- [ ] Implement merge operation with conflict detection
- [ ] Define constitution schema (merge policy, protected attributes, resolution rules)
- [ ] Implement fork operation with entanglement cost calculation
- [ ] Implement trust metric (cross-reference compressibility)
- [ ] Implement forgiveness protocol (prune, recompute, mutual cost)
- [ ] Define the three governance archetypes as constitution presets
- [ ] Implement absorption detection (threshold for identity submersion)
- [ ] Implement forced merge mechanics (hostile observation, conflict-as-combat)
- [ ] Implement governance timeout configuration per constitution type

## Open Questions
- Can constitutions be amended? What's the amendment protocol?
- Is forgiveness always available, or does it require collective vote?
- How deep can entanglement go before fork becomes prohibitively expensive?
