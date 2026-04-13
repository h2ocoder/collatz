# Multiverse Ontology Design

> Brainstormed 2026-04-13. Captures the core ontology for Emanon's universe model,
> spatial structure, p-adic entanglement, and interaction loop.

## Core Ontology

### Hex = Universe

Each hex on the map represents a distinct universe — a parallel timeline that
forked from a common genesis. The hex grid IS the multiverse.

All universes share a common origin (the genesis event). Their logs share a
prefix. The further apart two universes are, the earlier their histories
diverged.

### Players share a home universe

All players begin in the same universe — the same hex. This is the shared
social space: trade, alliances, conflict, governance, and politics happen here.

The home universe has its own log, its own star(s), its own planets, its own
economy. This is where most of the day-to-day game happens.

### The multiverse is the strategic layer

Other universes (other hexes) are explored and exploited from the outside.
You never "leave" your home universe. You reach into others through probes
and entanglement.

Each player builds a unique web of connections across the multiverse based
on their choices — which universes they've probed, which they've entangled
with, what they've learned.

## Distance Model

### Two independent notions of distance

**Euclidean distance** — spatial proximity on the hex grid. Universes that are
grid-neighbors. These universes might have wildly different histories — spatial
proximity says nothing about historical similarity.

**P-adic distance** — history similarity. Based on the Eisenstein norm of the
coordinate difference: N(dq, dr) = dq^2 - dq*dr + dr^2. Two universes are
p-adically close when N is highly divisible by a prime p (especially 2 and 3,
since rad=6 is the Collatz base).

P-adically close universes diverged recently. Their logs share a deep common
prefix. Events in one are correlated with events in the other. They "rhyme."

P-adically distant universes diverged early. Their logs are alien to each
other. No correlation. No rhyming.

### Entanglement = p-adic closeness

Entanglement is NOT a thing you build. It's a property of the multiverse's
geometry. Two hexes with small p-adic distance are inherently entangled —
their histories are correlated because they share deep causal structure.

From the seed conversation: "not because information traveled, but because
they were never actually independent."

The deeper the entanglement (higher p-adic valuation), the tighter the
correlation between what happens in each universe.

### Nearby universes start similar

Your immediate neighbors on the hex grid diverged recently (if p-adically
close) or might be alien (if p-adically far). But the Eisenstein lattice
creates a structured pattern — some neighbors are deeply entangled, others
are not.

The 3-adic "highways" and 2-adic "highways" create natural corridors of
entangled universes stretching across the map.

## Interaction Model

The player never leaves their home universe. All interaction with other
universes follows an enter/action/exit loop:

### Probe

Send a probe into a target universe. The probe enters, observes or acts,
and returns with data. This is a one-shot interaction.

- Costs energy proportional to Euclidean distance (travel cost) and
  inverse p-adic distance (how alien the target is)
- Probes into p-adically close universes return high-value intel (the
  target is similar enough that observations are relevant to your own
  situation)
- Probes into p-adically distant universes return noise (the target is
  too different for the data to be actionable)

### Entangle

Create a persistent link between your universe and a target. Now events in
yours ripple into theirs and vice versa. This is a standing connection.

- Requires p-adic closeness above some threshold (you can only entangle
  with universes that share enough history for the link to be coherent)
- Coupled timelines: what happens in one influences the other. Benefits
  (shared intel, resource correlation) and risks (merge conflicts,
  cascade failures)
- Deeper entanglement = tighter coupling = more benefit and more risk

### Observe

Read the data that comes back from probes or flows through entanglement
links. This happens in your log view. The game's primary interface is
reading and interpreting log data, then making decisions.

## UI Model

### Map is strategic overview (30% of screen)

The map shows the hex grid — the multiverse topology. Each hex is colored
by broad state (has star, dead star, black hole, unexplored, etc.). 
Entanglement patterns shimmer. Your position is marked. You click a hex to
open its detail panel.

The map is a radar screen, not a battlefield. No unit icons, no drag and
drop. Glanceable topology.

### Panels and menus are the game (70% of screen)

- **System panel** — opens for a selected hex. Shows its log summary,
  divergence from your universe, entanglement strength, probe history.
- **Action menu** — probe, entangle, observe, scan. Each action has
  costs, expected returns, and tradeoffs. All menu-driven.
- **Log view** — the event history. The primary way you understand what's
  happening. Reading and writing logs IS the game.
- **Home panel** — your universe's state. Economy, planets, star health,
  governance, population. Where the social game lives.

### Information over animation

In a universe where information is the fundamental resource, the primary
interface is reading data, not watching animations. The log view isn't a
debug tool — it IS the game.

## Collatz Connection

### 2 and 3 are the fundamental dynamics

- **2 (compression)** — observable as stellar compression. Stars take
  redundant logs and halve them. Energy is the byproduct. Every star
  the player sees is performing the div-2 operation.
- **3 (creation)** — observable as branching/growth. New causal threads
  emerge, events multiply, complexity increases. Every new event is
  the 3n+1 expansion.

These aren't labeled as "2" and "3" in the UI. They're just the physics:
things compress and things grow. The conservation law
`s * log2(6) = T - log2(n) + epsilon` governs the balance.

### The Eisenstein lattice IS the multiverse's geometry

The hex grid uses the Eisenstein integer lattice (basis vectors 1 and omega
where omega = e^(2*pi*i/3)). This isn't arbitrary — it's the natural
geometry for a system governed by rad=6 dynamics.

The p-adic metric on this lattice (via the Eisenstein norm) determines
entanglement strength between universes.

### Tech tree connects to prime technology

Prime-based technology lets players perceive and exploit the entanglement
structure:

- **Compression Lens** (tier 1) — understand the 2-adic traces left by
  stellar compression. See entanglement along v2 lines.
- **Creation Lens** (tier 1) — understand the 3-adic echoes of branching
  events. See entanglement along v3 lines.
- **Hexagonal Array** (tier 2) — combine both. See the full base-6
  entanglement network. Understand the conservation law.
- **Exotic primes** (tier 3+) — rare tech from black hole archaeology.
  Higher primes reveal deeper layers of the multiverse's structure.

### Black holes are where stars died

A collapsed star becomes a black hole. In game terms, a black hole is a
hex where compression catastrophically failed. These hexes have special
properties:

- They may contain fragments of ancient tech (exotic prime scanners)
- They have extreme entanglement properties (deep p-adic connections)
- They're dangerous to probe but high-reward

## Open Questions

- What do planets within a hex/universe represent?
- How does governance work when multiple players share the home universe?
- What triggers universe divergence — player actions, NPC behavior, or
  environmental events?
- Can players relocate their "home" to a different universe?
- How does combat/conflict work in a menu-driven system?
- What does the "economy" of a single universe look like — what resources
  exist beyond energy from stellar compression?
- How do probes work mechanically — what do you send, what comes back?
- Can entanglement be broken? What happens when you decouple?
