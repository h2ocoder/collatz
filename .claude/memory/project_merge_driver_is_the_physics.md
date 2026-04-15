---
name: The merge driver is the physics
description: Emanon's load-bearing novel mechanism is Collatz-genus-as-conflict-resolution via git's merge driver — weight roadmap decisions accordingly
type: project
originSessionId: 26a38dc0-0432-4437-91b9-5e7de4aa3fd3
---
Emanon's central novel claim isn't "bounties for Collatz math" or "a universe stored in git." Those are primitives. The protocol's actual novelty is **Collatz-genus-as-dispute-resolution** — two writers edit the same region, git detects the conflict, the custom merge driver picks a resolution deterministically from the genera of the two sides. No human, no authority, no race.

This is the single mechanism that ties the whole system together: the math is there to compute genus, the git repo is there because git already has the merge-conflict infrastructure, the server exists to coordinate things that can't be resolved by merge alone. Everything orbits the driver.

**Why:** The user asked what next E2E test would move claims from "plausible" to "proven" — the merge-driver test was the clear answer, and building it surfaced that essentially everything else in the system is either scaffolding for it or an interface on top of it. The MVP driver (winner-takes-all by genus lex order) is explicitly a placeholder for the three-path spec in `docs/2026-04-13-gitverse-design.md`: same-set_k → hybrid merge; same-oddity → weighted merge with bit-destruction attenuation; otherwise → defer to negotiation.

**How to apply:**
- When prioritizing work, weight merge-driver progress ahead of features that assume it (new bounty types, UI polish, federation). The driver is load-bearing; features stacked on a placeholder driver are stacked on sand.
- The next substantial driver work is implementing `hybrid_merge` / `weighted_merge` / `bit_destruction` from the spec. That's research-ish (how do you textually combine two conflicting writes by a math weight?), not just engineering. It needs a design pass before a build pass.
- The `--contract-mode` and `--append-only` drivers registered by `emanon init` are currently defer-only stubs. They need to exist as real drivers before anyone can rely on `contracts/**` or `scars/**` auto-merge. Same weight as the regions driver.
- Negotiation UI (for the "defer" path) is part of this layer, not a separate concern. A complete physics needs a way for humans to resolve what math can't.
- If we ever hit a choice like "spend a week on server features vs. a week on the driver," default to the driver unless the server work unblocks real users today.
