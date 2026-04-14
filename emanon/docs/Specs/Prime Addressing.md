---
jira: ALPHA-11
status: draft
type: story
---

# Prime Addressing

## Overview
Every atomic event stream is a prime. Composite universes are products of primes. The address of a universe is its factorization — it tells you which streams to subscribe to in order to reconstruct its state.

## Concepts
- **Prime stream**: an irreducible causal thread, backed by a single container/LLM agent
- **Composite address**: a product of primes (e.g., 30 = 2 x 3 x 5 = streams 2, 3, and 5)
- **Exponents**: depth/time index per stream (e.g., 12 = 2^2 x 3 = stream 2 at depth 2, stream 3 at depth 1)
- **GCD = shared state**: common prime factors = shared event streams
- **LCM = merge**: union of all constituent streams
- **Coprime = independent**: GCD = 1, no shared streams, trivial merge

## Requirements
1. Each prime stream has a unique prime address assigned at genesis
2. Composite addresses are computed as products of constituent primes
3. GCD operation returns shared stream set between two addresses
4. LCM operation returns the merged address
5. Factorization of an address returns the subscription list (which streams to read)
6. New primes can be minted when new causal threads emerge

## Collatz Connection
- `collatz/factorization.py` already implements prime factorization, GCD, LCM
- Collatz orbits navigate the address space: each step maps one composite to another
- Dropping set membership (mod 2^(k-s)) partitions the address space into residue classes

## Tasks
- [ ] Define prime registry (minting, lookup, lifecycle)
- [ ] Implement address factorization and stream subscription
- [ ] Implement GCD/LCM for shared state and merge computation
- [ ] Define exponent semantics (time depth vs. version vs. weight)
- [ ] Integration with existing `collatz/factorization.py`

## Open Questions
- How are new primes allocated? Sequential? Random? Hash-based?
- Do exponents represent time, version depth, or something else?
- Is there a maximum address size (computational cost of factoring)?
