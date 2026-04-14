---
jira: ALPHA-18
status: draft
type: story
---

# Em Language Spec

## Overview
Em is the programming language of Emanon. Causality is syntactic — you can't emit without declaring parents. Energy is a linear type — the compiler enforces conservation. Prime types constrain valid operations at compile time. The compiler is a physicist.

## Concepts
- **Event as primitive**: not a value or expression — an event with body, parents, and type
- **Log as state**: no variables, no assignment — state is derived by folding logs
- **Prime as process**: first-class cryptographic identity rooted in genesis event
- **Composite as merge**: linguistic construct for shared Merkle history
- **Filter as query type**: `scan` is a first-class expression returning probabilistic results
- **Energy as linear type**: like Rust ownership but for computational resources — compiler rejects conservation violations
- See [[Log Types]] for the six prime type declarations

## Requirements
1. Causal provenance is grammatical — events must declare parents
2. Energy cost is in the type system — operations that cost energy require it in scope
3. Prime types (particle, force, field, law, story, witness) constrain valid operations at compile time
4. Pattern matching works on event sequences (log folding), not data structures
5. Scan results are typed as probabilistic — can't treat as certain without observe
6. Phase 1: notation and specification (hand-simulated examples)
7. Phase 2: transpiler targeting Elixir/BEAM (or alternative host)
8. Phase 3: native Emanon VM (far future)

## Collatz Connection
- The Collatz map is a minimal Em program: one prime, one law (3n+1 / n/2), deterministic causal chain
- Dropping sets are type classes — Set_k constrains what operations produce in k steps
- The conservation law is enforceable at compile time

## Tasks
- [ ] Write Em grammar specification (BNF or PEG)
- [ ] Define type system with prime types and energy linearity
- [ ] Write hand-simulated example programs (two-prime interaction, merge, scan)
- [ ] Define compilation target (Elixir GenServer, TypeScript, or Python)
- [ ] Prototype parser for core syntax

## Open Questions
- Elixir/BEAM vs TypeScript vs Rust as phase 2 transpilation target?
- How much of the physics is compile-time vs runtime enforcement?
- Should Em support higher-order events (events about events)?
