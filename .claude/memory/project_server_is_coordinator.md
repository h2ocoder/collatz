---
name: Emanon server is a coordinator, not a source of truth
description: The central authority's only genuine role is ordering (who accepted first); all math, predicate validation, and proof verification is self-verifying and could be fully decentralized
type: project
originSessionId: 26a38dc0-0432-4437-91b9-5e7de4aa3fd3
---
The `Emanon.Server` is a convenience layer, not a source of mathematical truth. Genus strings are self-verifying: anyone with a calculator can parse `"set_k=17 oddity_s=3 index_i=17"`, re-run `CollatzMath` to confirm consistency, and evaluate any predicate against it offline. The server does not re-derive genus from a file, verify writer identity (unsigned email compare), or gate anything the math can't gate itself.

The one thing the server uniquely provides is **ordering** — resolving acceptance races between workers ("who accepted this bounty first?"). Everything else could be replaced by git remotes + signed commits + local verification.

**Why:** The user noticed this mid-session — "this seems like just pure math, and the central authority isn't even needed." The observation held up under inspection: looking line by line at `BountyEndpoints.cs`, only the Open→Accepted state-transition race is genuinely centralized. This is a structural property of the protocol, not an implementation accident.

**How to apply:**
- When reviewing or extending server endpoints, ask: "does this need authority, or is it self-verifying math that's been routed through the server for convenience?" Default to the latter interpretation unless there's a coordination race.
- Any feature that would add real authority (e.g. the server becoming the canonical genus oracle, enforcing write ordering beyond bounty acceptance, holding escrow without a blockchain) should trigger an explicit design conversation — we're adding centralization, not inheriting it.
- Decentralization moves (bounty state in shared git repos, signature-gated identity, etc.) are paths that naturally *remove* the server from load-bearing positions. Don't block them just because the current architecture happens to include a server.
- The merge driver already demonstrates the decentralized path: the `regions/**` dispute-resolution path requires zero server coordination, resolved entirely by git + Collatz math at merge time. That's the protocol's "true form"; the server is scaffolding.
