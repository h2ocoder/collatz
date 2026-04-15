---
name: Genus is a classifier, not a magnitude
description: In Emanon, Collatz genus is an identity/kind — rules that impose scalar ordering on it (e.g. "higher wins") work against the underlying math
type: project
originSessionId: 26a38dc0-0432-4437-91b9-5e7de4aa3fd3
---
Collatz genus in Emanon — the (set_k, oddity_s, index) tuple — is a **classifier**, not a scalar. It tells you *which kind of write this is*, not *how big* the write is. This matches the mathematical usage in algebraic geometry / topology, where genus is a topological invariant that identifies equivalence classes (a torus has genus 1; a sphere has genus 0; the number is a label).

**Why:** The user explicitly framed genus as "whatever makes it, it" — identity. The three-path merge spec in `docs/2026-04-13-gitverse-design.md` (same set_k → hybrid merge, same oddity → weighted merge, otherwise → defer to negotiation) only makes sense through this lens: the spec is asking *"how related are these two writes?"*, not *"who has more?"* My interim MVP rule (higher-genus wins on lex order) imposed a total ordering where the math wants a classification relation — it's a tiebreaker, not a resolution rule.

**How to apply:**
- When designing anything that compares two genera — merge resolution, bounty predicates, leverage calculations, distance metrics — start by asking "is this an equivalence/relatedness question, or a magnitude question?" Default to equivalence unless the problem genuinely needs ordering.
- Predicate language: expressions like `set_k == 7` or `set_k ∈ {3, 5, 7}` (classification) are closer to the grain than `set_k >= 100` (magnitude). Both have uses, but the former is more honest about what genus is.
- Leverage, rarity, difficulty — these are secondary derivations from genus, not genus itself. Don't conflate them.
- Current `MergeDriverCommand.ResolveWinner` is explicitly a simplification; when full hybrid/weighted merges are designed, the classifier framing is the right scaffolding.
- Red flag to watch for: code or specs that reduce genus to a single number via `.SetK` alone, `GetHashCode`, or a weighted sum. Usually a sign the classifier structure is being flattened prematurely.
