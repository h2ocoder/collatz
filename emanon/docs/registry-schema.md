# Emanon Registry Schema

> The **emanon-registry** is a public, forkable GitHub repository where players
> publish signed pointers to their universes. Each universe corresponds to one
> JSON file under `entries/<name>.json`. A GitHub Actions CI workflow validates
> every incoming PR before it is merged.

## Repository

- **Canonical URL:** `https://github.com/forgetthefrets/emanon-registry`
- **Structure:**
  ```
  entries/
    example.json       ← sample valid entry (shipped with the repo)
    alice-prime.json   ← a player-submitted entry
  schema/
    entry.schema.json  ← JSON Schema (draft-07) for an entry file
  .github/
    workflows/
      validate.yml     ← CI that validates every PR
  README.md
  ```

## Registry Entry Schema

One file per universe in `entries/<name>.json`. The filename **must** match
the `name` field inside the file.

```json
{
  "name": "alice-prime",
  "owner_pubkey": "ed25519-base58",
  "git_url": "https://github.com/alice/her-world",
  "head_commit": "abc1234def5678901234567890123456789012345678",
  "snapshot_count": 42,
  "values_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "scrambled_root_hash": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "created_at": "2026-04-14T00:00:00Z",
  "updated_at": "2026-04-14T00:00:00Z",
  "tags": ["solo", "early"],
  "cnft_mint": null
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✓ | Unique universe name. Alphanumeric, hyphens, underscores. Must match filename. |
| `owner_pubkey` | string | ✓ | Ed25519 public key in Base58. Used to verify the entry file's GPG/SSH signature. |
| `git_url` | string (URL) | ✓ | HTTPS URL of the universe repository. Must be publicly reachable. |
| `head_commit` | string | ✓ | SHA-1 of the latest commit in the universe (40 hex chars). CI verifies this matches the remote HEAD. |
| `snapshot_count` | integer | ✓ | Value of `snapshot_count` in `.gitverse/values.json` at `head_commit`. |
| `values_hash` | string | ✓ | `sha256:<hex>` of the `.gitverse/values.json` content at `head_commit`. |
| `scrambled_root_hash` | string | ✓ | `sha256:<hex>` of the $T^k$-scrambled Merkle root. See the [Collatz Scrambling Protocol](2026-04-13-collatz-scrambling-protocol.md). |
| `created_at` | string (ISO 8601) | ✓ | Timestamp when the entry was first submitted. |
| `updated_at` | string (ISO 8601) | ✓ | Timestamp of the last update. |
| `tags` | array of strings | ✓ | Searchable tags. Must be lowercase alphanumeric. May be empty `[]`. |
| `cnft_mint` | string \| null | ✓ | Solana compressed-NFT mint address representing this universe, or `null` if not yet minted. |

### Constraints

- `name` must match `^[a-z0-9][a-z0-9_-]{1,62}[a-z0-9]$` (3–64 chars).
- `owner_pubkey` must be a valid Base58-encoded 32-byte Ed25519 key.
- `git_url` must start with `https://`.
- `head_commit` must be exactly 40 lowercase hex characters.
- `values_hash` and `scrambled_root_hash` must match `^sha256:[0-9a-f]{64}$`.
- `tags` entries must each match `^[a-z0-9_-]{1,32}$`.
- `cnft_mint` must be a Base58 string of length 32–44 chars, or `null`.
- The entry file itself must be GPG-signed by the key identified in `owner_pubkey`.

## Formal JSON Schema

The machine-readable version lives at `schema/entry.schema.json` in the registry
repo. It is JSON Schema draft-07 and is used by the CI workflow to validate every
`entries/*.json` file in a PR.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/forgetthefrets/emanon-registry/blob/main/schema/entry.schema.json",
  "title": "EmanonRegistryEntry",
  "type": "object",
  "required": [
    "name", "owner_pubkey", "git_url", "head_commit",
    "snapshot_count", "values_hash", "scrambled_root_hash",
    "created_at", "updated_at", "tags", "cnft_mint"
  ],
  "additionalProperties": false,
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9_-]{1,62}[a-z0-9]$"
    },
    "owner_pubkey": {
      "type": "string",
      "minLength": 43,
      "maxLength": 44
    },
    "git_url": {
      "type": "string",
      "format": "uri",
      "pattern": "^https://"
    },
    "head_commit": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$"
    },
    "snapshot_count": {
      "type": "integer",
      "minimum": 0
    },
    "values_hash": {
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$"
    },
    "scrambled_root_hash": {
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9_-]{1,32}$"
      }
    },
    "cnft_mint": {
      "oneOf": [
        {
          "type": "string",
          "minLength": 32,
          "maxLength": 44
        },
        { "type": "null" }
      ]
    }
  }
}
```

## CI Validation Workflow

The GitHub Actions workflow (`validate.yml`) runs on every PR that touches
`entries/**`. It performs four checks:

### 1 — Schema validation

Every changed `entries/<name>.json` is validated against `schema/entry.schema.json`
using `ajv-cli`. If any field is missing or malformed, the PR is rejected with a
diff of the validation errors.

### 2 — Filename ↔ name consistency

The `name` field inside the JSON must exactly equal the filename stem. E.g.,
`entries/alice-prime.json` must contain `"name": "alice-prime"`.

### 3 — Remote reachability + HEAD commit

The workflow fetches the remote's advertised refs (`git ls-remote <git_url>`) and
verifies that `HEAD` matches `head_commit`. If the URL is unreachable or HEAD has
advanced past `head_commit`, the PR is rejected.

### 4 — Signature verification (advisory)

Entries should be GPG-signed by the key identified in `owner_pubkey`. The CI
emits a **warning** (non-blocking in the initial release) when the signature is
absent or unverifiable. Full signature enforcement is planned for the mainnet
launch.

### Failure messages

| Check | Example failure message |
|-------|------------------------|
| Schema | `entries/alice-prime.json: field 'snapshot_count' must be integer, got string` |
| Filename | `entries/alice-prime.json: name field 'alice_prime' does not match filename stem 'alice-prime'` |
| Reachability | `entries/alice-prime.json: git_url 'https://...' not reachable or returned error` |
| HEAD mismatch | `entries/alice-prime.json: head_commit abc123 does not match remote HEAD def456` |
| Signature | `WARN entries/alice-prime.json: signature absent or unverifiable (non-blocking)` |

## Submitting Your Universe

1. Fork `forgetthefrets/emanon-registry`.
2. Copy `entries/example.json` to `entries/<your-universe-name>.json`.
3. Fill in all fields. Run `emanon validate` inside your universe repo to get
   the correct `values_hash`.
4. *(Optional)* GPG-sign the file:
   ```bash
   gpg --clearsign --output entries/my-universe.json entries/my-universe.json
   ```
5. Open a PR. CI validates automatically. Fix any reported errors.
6. A maintainer merges the PR once CI is green.

## Updating Your Entry

Open a new PR with an updated `entries/<name>.json`. Update `updated_at` and
`head_commit` to the new values. CI re-validates the full entry.

## Removing Your Entry

Open a PR that deletes your `entries/<name>.json`. Include a brief reason in
the PR description. Maintainers will merge without requiring a CI check
(deletion always passes schema validation).

## Design Notes

- **One file per universe** keeps history clean — `git blame entries/alice-prime.json`
  shows the full update history for a universe.
- **No merge conflicts** in the registry: each entry is an independent file, so
  concurrent PRs never conflict.
- **Offline-first**: the registry is a git repo; players can clone it and search
  locally without hitting any API.
- **Extensible**: additional fields can be added as optional fields in a future
  schema revision. The `additionalProperties: false` constraint is intentional
  and will be relaxed when the schema version bumps.
