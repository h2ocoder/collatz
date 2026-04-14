---
jira: ALPHA-14
status: draft
type: story
---

# Energy & Conservation

## Overview
Energy is read/write capacity. Conserved, finite, transferable. You need energy to observe, emit, and exist as a ticking process. Without energy your prime goes dark. Energy is the difference between raw and compressed log representations — you can't create it from nothing because you can't compress below Kolmogorov complexity.

## Concepts
- **Energy token**: unit of compression differential (raw volume minus compressed volume)
- **Conservation**: total energy = total compressible redundancy remaining in the system
- **Mass**: log volume — accumulated events, measured in bytes/lines
- **Entropy**: incompressibility — high entropy logs are expensive and noisy
- **E = mc^2 analogy**: energy cost = information content (mass) x propagation cost (distance^2)
- See [[Stellar Compression]] for energy production
- See [[Cosmology]] for thermodynamic lifecycle

## Requirements
1. Energy is a linear resource — consumed by operations, cannot be duplicated
2. Every action has a defined energy cost (emit, observe, scan, compress, merge, fork, prophesy)
3. Conservation law holds: total information in the system is constant
4. Energy production comes from stellar compression (redundancy elimination)
5. Energy scarcity increases as the universe matures and logs become less compressible
6. Primes without energy cannot emit or observe (log freezes, clock stops)
7. **Starting energy budget**: new primes genesis with 100 energy (tunable per scenario)
8. **Energy death**: when energy reaches 0, the prime goes dark — log freezes, no more ticks. This is a roguelite end state that awards atlas knowledge loot. See [[Roguelite Persistence]]
9. **Star ignition threshold**: a star requires log contributions from 2+ primes to begin compression. Solo primes cannot generate energy — this IS the cooperation pressure
10. **Energy per tick**: primes in a star's orbit receive energy proportional to the star's luminosity and their proximity

## Collatz Connection
- The conservation law `s * log2(6) = T - log2(n) + epsilon` is the energy balance
- Base-6 lattice from Paper 3 is the exact balance between 3-growth and 2-destruction
- Each dropping step has a contraction ratio ~0.605 — net energy is released per drop

## Tasks
- [ ] Define energy cost table for all actions
- [ ] Implement energy accounting per prime (budget, spend, receive)
- [ ] Implement conservation validation (system-wide audit)
- [ ] Define energy transfer protocol between primes
- [ ] Model energy scarcity curve over universe lifetime
- [ ] Implement energy death trigger and run-end sequence
- [ ] Implement star ignition threshold (multi-prime fuel requirement)
- [ ] Implement per-tick energy distribution from stars to orbiting primes

## Open Questions
- What's the initial energy allocation for a new prime?
- Can energy be stored/banked, or must it be spent per tick?
- How does energy transfer work across distance (speed-of-light delay)?
