# Emanon Project Structure Design

**Date:** 2026-04-13
**Status:** approved
**Jira Project:** ALPHA (Alpha36) on musicalmathmind.atlassian.net
**Cloud ID:** 38e5fd1f-701b-47f6-832d-54a136f621cd

## Overview

Emanon is a sci-fi 4X game built on information-theoretic physics. The multiverse is a distributed event-sourced system where universes are prime-addressed log streams, physics emerges from compression and entropy, and governance is a game mechanic.

This document defines the project structure, documentation conventions, and build order.

## Directory Structure

```
emanon/
  seed.txt                              # Original brainstorming conversation

  docs/                                 # Obsidian vault (standalone, separate from collatz docs/)
    00-Index.md                         # Root hub
    2026-04-13-emanon-structure-design.md  # This document
    Specs/
      Event Schema & Log.md
      Prime Addressing.md
      Bloom Filters & Scanning.md
      Merkle Trees & Timeline Verification.md
      Energy & Conservation.md
      Stellar Compression.md
      Merge & Governance.md
      Turn Mechanics & Game Loop.md
      Em Language Spec.md
      Infrastructure & Scale.md
    Lore/
      Genesis.md
      Log Types.md
      Factions & Governance.md
      Cosmology.md
    Reference/
      Collatz Integration.md
      Seed Conversation.md
      External Sources.md

  src/                                  # Code (empty for now)
```

## Obsidian Conventions

- Standalone vault at `emanon/docs/` (not a subfolder of the Collatz `docs/` vault)
- `[[wikilinks]]` for internal cross-references within the Emanon vault
- Explicit paths when referencing Collatz concepts (no shared wikilink namespace)

### Spec Doc Format

```markdown
---
jira: ALPHA-XX
status: draft | review | approved
type: story
---

# Spec Name

## Overview
One paragraph: what this system is and why it exists.

## Concepts
Key definitions, with [[wikilinks]] to Lore/ docs.

## Requirements
Numbered list of what the system must do.

## Collatz Connection
How this maps to existing Collatz math.

## Tasks
Checklist of implementation tasks (each becomes a Jira Task under the Story).

## Open Questions
Unresolved design decisions.
```

### Lore Doc Format

```markdown
# Title

## Narrative
The in-universe explanation.

## Design Implications
What this means for the specs — constraints, requirements, tradeoffs.

## Related Specs
Links to [[Spec docs]] this lore informs.
```

## Jira Mapping

| Obsidian | Jira | Issue Type |
|----------|------|------------|
| Spec doc | Story | `10008` |
| Task checklist item | Task | `10007` |

- Frontmatter `jira: ALPHA-XX` in each spec links to the Jira Story
- Jira Story description links back to the doc path
- No Epics for now; can group later if needed

## Build Order (Paired Lore + Specs)

### Layer 0 — Foundations
| Specs | Lore |
|-------|------|
| [[Event Schema & Log]] | [[Genesis]] |
| [[Prime Addressing]] | [[Log Types]] |

### Layer 1 — Data Structures
| Specs | Lore |
|-------|------|
| [[Bloom Filters & Scanning]] | [[Cosmology]] |
| [[Merkle Trees & Timeline Verification]] | |

### Layer 2 — Physics
| Specs | Lore |
|-------|------|
| [[Energy & Conservation]] | [[Factions & Governance]] |
| [[Stellar Compression]] | |
| [[Merge & Governance]] | |

### Layer 3 — Game
| Specs | Lore |
|-------|------|
| [[Turn Mechanics & Game Loop]] | (emerges from above) |

### Layer 4 — Language
| Specs | Lore |
|-------|------|
| [[Em Language Spec]] | |

### Cross-cutting
| Specs | Reference |
|-------|-----------|
| [[Infrastructure & Scale]] | [[Collatz Integration]] |

## Collatz Integration Points

The existing `collatz/` Python library provides mathematical backing:

- **`collatz/factorization.py`** — prime factorization, GCD, LCM for universe addressing
- **Dropping sets / stopping classes** — maps to turn structure (Set_k = addresses resolving in k ticks)
- **Conservation law** `s*log2(6) = T - log2(n) + epsilon` — energy conservation model
- **Spectral gap (5/6)** — information propagation speed (speed of light)
- **Affine orbit structure** — local linearity of physics within residue subgroups
