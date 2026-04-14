# External Sources

Papers, projects, and prior art relevant to Emanon's design.

## Directly Referenced

### Shakibaei Asli (arxiv 2601.04289)
- Collatz in log_6 coordinates = rotation by log_6(3) + epsilon(x)
- User's PPR(x,6) function = same transformation, independently discovered
- Relevant to: [[Energy & Conservation]], base-6 lattice as energy balance

### Chang (arxiv 2603.25753)
- Reduces Collatz to "one-bit orbit mixing" at mod 32
- Relevant to: [[Turn Mechanics & Game Loop]], deterministic tick behavior

## Architectural Influences

### Event Sourcing
- Martin Fowler's event sourcing pattern
- The universe as a fold over an append-only log

### CRDTs (Conflict-free Replicated Data Types)
- Automatic convergence under concurrent writes
- Alternative to explicit merge conflict resolution
- Relevant to: [[Merge & Governance]]

### Erlang/OTP and the BEAM
- Actor model: isolated processes communicating by messages
- Supervisors managing process lifecycles
- Hot code reloading
- Relevant to: [[Em Language Spec]], [[Infrastructure & Scale]]

### Unison Language
- Content-addressed code (every function identified by hash of AST)
- Merkle thinking applied to code
- Relevant to: [[Merkle Trees & Timeline Verification]], [[Em Language Spec]]

### Bitcoin / Proof of Work
- Mining as exploration rather than wasted computation
- Bloom filter response as hash (verification = re-running the scan)
- Relevant to: [[Infrastructure & Scale]]

## Philosophical / Narrative

### Borges — "The Library of Babel"
- Infinite library containing every possible book
- The address space before mining = Tehom = the unobserved library

### Kierkegaard — Leap of Faith
- Genesis event as existential commitment
- Relevant to: [[Genesis]]

### Nash Equilibrium
- The balance/rest condition of the multiverse
- Genius/madness threshold as energy budget for protocol-reading
