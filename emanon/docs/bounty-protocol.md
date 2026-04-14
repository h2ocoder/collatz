# Bounty Protocol

> The **bounty protocol** is Emanon's universe market specification.  A *bounty*
> is a structured, on-chain offer from a buyer to any miner who can produce a
> universe satisfying a stated constraint.  This document defines the wire format,
> the predicate language, the verify/deliver lifecycle, and five worked examples.

---

## 1. Overview

Miners run the Emanon CLI to grow universes (git repos with Collatz-powered physics)
and submit them to buyers via the bounty market.  A buyer posts a *constraint*
expressed as a JSON predicate AST.  Any miner whose universe satisfies the
predicate may bid, negotiate price, and deliver the universe as a `git-bundle`.

The engine verifies delivery by:

1. Cloning the delivered bundle from scratch
2. Re-running the verifiable random seed through the Collatz physics layer
3. Evaluating `verify_predicate(repo_root, constraint)` — the Rust function in
   `emanon/src/cli/src/bounty/`

Settlement is in USDC.  The universe is minted as a compressed NFT (cNFT) on Solana
and transferred to the buyer on escrow release.

---

## 2. Bounty Schema

All bounties are serialised as JSON objects conforming to this schema.

```json
{
  "id": "<uuid-v4>",
  "buyer_pubkey": "ed25519:<base58-encoded-key>",
  "constraint": { ... predicate AST ... },
  "max_price_usdc": <number>,
  "expires_at": "<ISO-8601 datetime>",
  "starter_seed_source": "switchboard-vrf | drand | block-hash",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": <integer ≥ 0>,
  "created_at": "<ISO-8601 datetime>"
}
```

### Field reference

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | UUID v4 string | ✓ | Globally unique bounty identifier |
| `buyer_pubkey` | `"ed25519:<base58>"` | ✓ | Buyer's signing key for escrow authorisation |
| `constraint` | Predicate AST | ✓ | The constraint the mined universe must satisfy |
| `max_price_usdc` | float ≥ 0.00 | ✓ | Ceiling price the buyer will pay, in USDC |
| `expires_at` | ISO-8601 | ✓ | After this timestamp the bounty may not be accepted |
| `starter_seed_source` | enum | ✓ | Randomness source for the universe seed |
| `deliverable_format` | enum | ✓ | Expected format of the delivered universe |
| `min_miner_reputation` | uint | ✓ | Minimum miner reputation score; 0 = open |
| `created_at` | ISO-8601 | ✓ | Bounty creation timestamp |

### `starter_seed_source` values

| Value | Description |
|---|---|
| `switchboard-vrf` | Switchboard V2 verifiable random function on Solana |
| `drand` | drand randomness beacon (Cloudflare/Protocol Labs) |
| `block-hash` | Solana block hash at a specified slot height |

---

## 3. Predicate Language v1

The `constraint` field is a JSON-AST predicate tree.  Each node is a JSON object
with exactly one key.  The value type depends on the predicate kind.

### 3.1 Atomic predicates

#### `path_exists`

```json
{ "path_exists": "<relative-path>" }
```

True if the file or directory at `<relative-path>` (relative to the repo root)
exists in the delivered universe.

---

#### `file_contains`

```json
{ "file_contains": ["<relative-path>", "<substring>"] }
```

True if the UTF-8 text file at `<relative-path>` contains `<substring>` as a
literal byte sequence.

---

#### `jq`

```json
{ "jq": ["<relative-path>", "<jq-filter>"] }
```

Runs `jq -e '<jq-filter>' <relative-path>` against the repository.  True if `jq`
exits 0 and produces a truthy JSON value (not `false` or `null`).

Requires `jq` to be available in `$PATH` on the verifier machine.  Conservative
failure (returns `false`) when `jq` is not available.

---

#### `snapshot_count_at_least`

```json
{ "snapshot_count_at_least": <N> }
```

True if the universe has at least `N` snapshots committed, as recorded in
`.gitverse/snapshot_count`.

---

#### `genus_present`

```json
{ "genus_present": { "set_k": <K> } }
```

True if at least one file under `regions/` was written with Collatz genus
`set_k = K` — i.e., a genus stamp line `# emanon-genus: {"set_k": K, ...}` (or
the legacy `# emanon:genus set_k=K ...` format) is found in the regions tree.

---

#### `merge_count_at_least`

```json
{ "merge_count_at_least": <N> }
```

True if the universe's git history contains at least `N` merge commits (determined
by `git rev-list --count --merges HEAD`).

---

### 3.2 Logical combinators

#### `and`

```json
{ "and": [ <predicate>, ... ] }
```

True if **all** child predicates are true.  Short-circuits on the first false.

---

#### `or`

```json
{ "or": [ <predicate>, ... ] }
```

True if **at least one** child predicate is true.  Short-circuits on the first true.

---

#### `not`

```json
{ "not": <predicate> }
```

True if the child predicate is **false**.

---

## 4. Rust implementation

The canonical implementation lives at `emanon/src/cli/src/bounty/mod.rs`:

- **`Bounty`** — struct matching the wire schema above, with `from_json` / `to_json`
- **`Predicate`** — enum covering all v1 predicate types, with `from_json` / `to_json`
- **`verify_predicate(repo_root: &Path, predicate: &Predicate) -> bool`** — evaluates
  a predicate against a local repo path

```rust
use std::path::Path;
use emanon::bounty::{Predicate, verify_predicate};

let pred = Predicate::And { children: vec![
    Predicate::SnapshotCountAtLeast { n: 5 },
    Predicate::GenusPresentSetK { set_k: 13 },
]};

let satisfied = verify_predicate(Path::new("/path/to/universe"), &pred);
```

---

## 5. Example bounties

### Bounty A — Minimal starter (simple snapshot requirement)

A researcher wants any well-started universe with at least 3 snapshots.

```json
{
  "id": "11111111-0000-4000-a000-000000000001",
  "buyer_pubkey": "ed25519:3BHskyQmW7N8dUMhXmpSPWwVFo5YmEpnPaFGvHCxKwA",
  "constraint": {
    "snapshot_count_at_least": 3
  },
  "max_price_usdc": 1.00,
  "expires_at": "2026-06-01T00:00:00Z",
  "starter_seed_source": "switchboard-vrf",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 0,
  "created_at": "2026-04-14T00:00:00Z"
}
```

### Bounty B — Diplomatic universe (has contracts AND merges)

A player wants a universe that has evidence of player interaction:
at least 2 merge commits and at least 1 contract file.

```json
{
  "id": "22222222-0000-4000-a000-000000000002",
  "buyer_pubkey": "ed25519:5Hq3rJkLoTAZB9LiNfVz7pQdCyWmYbO2sUXR6EgK4vT",
  "constraint": {
    "and": [
      { "merge_count_at_least": 2 },
      { "path_exists": "contracts" }
    ]
  },
  "max_price_usdc": 4.50,
  "expires_at": "2026-07-01T00:00:00Z",
  "starter_seed_source": "drand",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 10,
  "created_at": "2026-04-14T00:00:00Z"
}
```

### Bounty C — Specific genus lineage (Collatz set_k = 13)

A lore collector wants universes seeded from the Collatz orbit of 13
— universes written with a specific mathematical "bloodline".

```json
{
  "id": "33333333-0000-4000-a000-000000000003",
  "buyer_pubkey": "ed25519:9TnWxHvGpBqUcS4mRjLePfZYD2ioKVAE5yO7bXk8dNM",
  "constraint": {
    "genus_present": { "set_k": 13 }
  },
  "max_price_usdc": 6.00,
  "expires_at": "2026-08-01T00:00:00Z",
  "starter_seed_source": "switchboard-vrf",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 0,
  "created_at": "2026-04-14T00:00:00Z"
}
```

### Bounty D — Named sector must exist with a populated JSON planet file

A world-builder needs a universe that has a specific named sector and at
least one planet record, verified via jq.

```json
{
  "id": "44444444-0000-4000-a000-000000000004",
  "buyer_pubkey": "ed25519:2VkLMpQrAsXyTbNjOfHwWceIZUG8uDE6m1PRo9YqKsF",
  "constraint": {
    "and": [
      { "path_exists": "regions/alpha/sector-2/planet.json" },
      { "jq": ["regions/alpha/sector-2/planet.json", ".name != null"] }
    ]
  },
  "max_price_usdc": 8.00,
  "expires_at": "2026-07-15T00:00:00Z",
  "starter_seed_source": "block-hash",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 5,
  "created_at": "2026-04-14T00:00:00Z"
}
```

### Bounty E — Rich universe (combines multiple constraints)

A tournament organiser wants a production-grade universe: 10+ snapshots,
2+ merges, no forbidden path, and must contain a README acknowledging
the Emanon multiverse.

```json
{
  "id": "55555555-0000-4000-a000-000000000005",
  "buyer_pubkey": "ed25519:7GwPnKoAMzYrTscBqVJmDfXeU3Li8CHO1NvRb4WSdth",
  "constraint": {
    "and": [
      { "snapshot_count_at_least": 10 },
      { "merge_count_at_least": 2 },
      { "file_contains": ["README.md", "Emanon"] },
      { "not": { "path_exists": "regions/forbidden" } }
    ]
  },
  "max_price_usdc": 15.00,
  "expires_at": "2026-09-01T00:00:00Z",
  "starter_seed_source": "drand",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 20,
  "created_at": "2026-04-14T00:00:00Z"
}
```

---

## 6. Lifecycle

```
Buyer:   bounty.post(bounty_json)              → bounty published on-chain
Miner:   emanon validate                        → check local universe is well-formed
Miner:   verify_predicate(repo, constraint)     → pre-check before bidding
Miner:   bid.submit(bounty_id, price, eta)      → place bid
Buyer:   accept(bid_id)                         → escrow funded
Miner:   git bundle --all universe.bundle       → package deliverable
Miner:   deliver(bounty_id, bundle_url, seed,
                 attestation, signature)
Engine:  verify(bundle_url, constraint, seed)   → re-run from seed, check predicate
         → escrow.release(price)
         → cnft.mint(buyer, metadata)
```

---

## 7. Security considerations

- **Seed commitment** — the `starter_seed_source` is committed *before* mining begins.
  Miners cannot cherry-pick a seed to make an easy constraint.
- **Predicate determinism** — all v1 predicates (`path_exists`, `file_contains`,
  `snapshot_count_at_least`, etc.) are deterministic given a fixed repo state.
  The engine always re-verifies from the committed seed.
- **jq safety** — the `jq` filter is run in a sandboxed subprocess on the verifier
  machine.  Buyers should be aware that complex filters may time out.
- **Genus authenticity** — genus stamps are written by the `emanon write` command and
  are reproducible from the seed; forged stamps will fail the seed re-run check.

---

## 8. Versioning

This document describes predicate language **v1**.  Future versions will add:

- `git_log_contains` — search commit messages
- `scar_count_at_least` — count battle scars
- `contract_signed_by` — check a specific pubkey has signed a contract
- `reputation_score_at_least` — check the miner's own reputation embedded in the
  universe via `values.json`

Backwards compatibility: v1 predicates will remain valid in all future versions.

---

*Drafted 2026-04-14 as part of ALPHA-47 (M6.1 — Bounty data model and predicate
language spec).*

---

## 9. Off-chain Escrow Board (M6.2)

Until Solana integration is complete, Emanon uses an **off-chain escrow simulation**
stored in the [`emanon-bounty-board`](https://github.com/forgetthefrets/emanon-bounty-board)
GitHub repository.

### Directory layout

```
open/            — Bounties accepting miner bids (one <uuid>.json per bounty)
in-progress/     — Bounties with an accepted miner
settled/         — Completed bounties (delivered + verified)
escrow.json      — Simulation ledger tracking who owes who
schema/          — JSON Schema for validating bounty files
```

### Extended wire format (off-chain)

On-chain bounties do not include `buyer_signature` — the signature is implicit from
the Solana transaction.  Off-chain bounties add a simulation stand-in:

```json
{
  "id": "<uuid-v4>",
  "buyer_pubkey": "ed25519:<base58>",
  "constraint": { ... },
  "max_price_usdc": 5.00,
  "expires_at": "2026-05-14T00:00:00Z",
  "starter_seed_source": "switchboard-vrf",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 0,
  "created_at": "2026-04-14T15:30:00Z",
  "buyer_signature": "sha256-sim:<hex>"
}
```

`buyer_signature` = `sha256(<buyer_pubkey>:<canonical_bounty_json_without_signature>)`.

### Posting a bounty

```sh
# 1. Write a predicate constraint file
cat > spec.json << 'SPEC'
{"snapshot_count_at_least": 5}
SPEC

# 2. Post
emanon bounty post --constraint spec.json --max-price 5

# Output:
# 🎯  Posting bounty 550e8400-...
#     constraint:  {"snapshot_count_at_least": 5}
#     max_price:   $5.00 USDC
#     expires_at:  2026-05-14T15:30:00Z
#     board:       https://github.com/forgetthefrets/emanon-bounty-board
# 🔄  Cloning bounty board...
# 🚀  Pushing branch 'bounty-550e8400'...
# 📬  Opening PR...
# ✅  PR opened: https://github.com/forgetthefrets/emanon-bounty-board/pull/1
#
# Bounty ID:  550e8400-...
# Expires at: 2026-05-14T15:30:00Z
# Signature:  sha256-sim:abc123...
```

### Config

Add to `~/.config/emanon/config.toml`:

```toml
[bounty]
board_url = "https://github.com/forgetthefrets/emanon-bounty-board"
buyer_pubkey = "ed25519:<your-base58-key>"
```

---

*Section added 2026-04-14 as part of ALPHA-48 (M6.2 — `emanon bounty post`).*
