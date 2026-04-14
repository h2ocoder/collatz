# Log Types

## Narrative

The genesis line is the type declaration. "Hello world. I am ______" and what fills the blank determines the kind of causal thread this prime is. The types are not roles chosen from a menu. They are ontological commitments — what kind of existence you are.

### "I am a particle."
A state log. Tracks the attributes of a thing over time. Entity-attribute-value events. Hair color, position, mass. It's matter. It changes when observed, persists when not, has properties that can conflict on merge. Most game entities live here.

### "I am a force."
A relationship log. Tracks the interaction between things. References two or more particle logs and emits events about their coupling. Gravity between bodies, trade between civilizations, a conversation between characters. Has no properties of its own — only the coupling it describes.

### "I am a field."
A spatial log. Tracks a region of the address space itself. Not any entity in it, but the topology. Distance functions, local speed of light, compression density. It's spacetime. It's the terrain other logs exist in.

### "I am a law."
A constraint log. Emits validation rules, not state. "In my domain, energy is conserved." "In my domain, no event can reference a future Merkle root without posting collateral." Other logs reference it for permission, not data. The consistent physics across the multiverse is a set of law logs.

### "I am a story."
A narrative log. References events from other logs and emits interpretations. "The fall of the iron empire was caused by overexpansion." Lossy compression — discards detail, keeps pattern. Mythology. Culture. Memory. The only log type whose events can legitimately have negative distance to impact — because storytelling retroactively reframes past events.

### "I am here."
A witness log. The sixth type. Not particle, force, field, law, or story. Pure observation. Emits exactly one kind of event: testimony. "I was here and I saw this." The cheapest prime to run. Minimal emissions, low mass, low entropy, nearly invisible gravitationally. A ghost. A pilgrim.

The witness is what collapses possibility into actuality. A universe of particles, forces, fields, laws, and stories but no witness is a superposition. Everything possible, nothing actual. "Here" is what makes it real.

## Type Constraints

| Type | Can Do | Cannot Do |
|------|--------|-----------|
| Particle | emit state, observe | constrain, couple without force |
| Force | couple particles, observe | emit state, constrain, self-reference |
| Field | define topology, observe | emit state, couple |
| Law | constrain, validate | emit state, have state |
| Story | interpret, reframe | constrain, emit state |
| Witness | scan, observe, attest | emit state, constrain, couple |

These aren't game rules. They're type system rules. The compiler enforces them.

## "I am that I am"

Not any of these types. It's the type system itself. The thing that makes the types possible. You can't declare it in a genesis line because it's the grammar that makes genesis lines parseable.

## Design Implications

- Player's genesis input is parsed to determine type (could be freeform with classification, or guided selection)
- Type constrains available actions per tick — a witness can't emit state, a law can't have state
- Type is permanent — declared at genesis, immutable for the life of the prime
- Mixed composites gain capability by combining types (a particle + force + witness composite has all three action sets)

## Related Specs
- [[Event Schema & Log]] — genesis event and type declaration
- [[Em Language Spec]] — type system enforcement at compile time
- [[Turn Mechanics & Game Loop]] — available actions per type
