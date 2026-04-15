---
name: Re-confirm when new information changes what "done" means
description: If mid-task discovery (a spec, constraint, or side effect) diverges from the approach the user approved, pause and surface it rather than silently incorporating or ignoring it
type: feedback
originSessionId: 26a38dc0-0432-4437-91b9-5e7de4aa3fd3
---
When the user has approved an approach and I then discover information that would materially change the scope, semantics, or outcome — a spec I hadn't read, a constraint I didn't know about, a side effect I just realized, a latent bug that changes the terrain — I should stop, surface the divergence explicitly, and re-confirm before proceeding. Not press on using the prior "yes" as authorization for the new version of the task.

**Why:** Their approval was scoped to the approach as I described it, not to the underlying task generically. Silently incorporating new info (or silently ignoring it) drifts toward shipping *something* instead of toward their actual intent. The user validated this behavior after I flagged that my proposed merge-driver rule ("higher genus wins") was a simplification of a richer three-path spec I'd just found in the docs — even though they'd already said "let's do it" to my simpler version. They called the pause memory-worthy.

**How to apply:**
- Watch for these moments explicitly: grep results that surface design docs, build output that reveals latent bugs, a file read that contradicts an assumption I pitched earlier.
- When it happens: in one message, name the divergence (what I proposed vs what I now see), name the two-to-three honest options, recommend one, ask.
- Keep the pause short. The cost of one confirming exchange is tiny compared to the cost of shipping work that doesn't match intent.
- This is different from bike-shedding or over-asking. Trivial details don't need re-confirmation. Reserve this for changes that would make the user say "wait, that's not quite what I had in mind" if they saw the final result.
- Related failure mode to avoid: pretending the new info doesn't exist to preserve a clean path to done. That's the lazy shortcut this rule is meant to block.
