# Emanon Universe Schema

This document specifies the canonical structure that every Emanon universe must
satisfy.  The `emanon validate` command enforces these rules.

---

## Required Directory Layout

```
<universe-root>/
├── .gitverse/
│   ├── values.json          # Resolution preferences (required)
│   └── snapshot_count       # Auto-managed by `emanon snapshot` (optional at init)
├── .gitattributes           # Merge-driver registration (required)
├── regions/                 # Spatial partitions (required directory)
├── contracts/               # Player agreements (required directory)
├── scars/                   # Resolved-conflict records (required directory)
└── forks/                   # Active timeline divergences (required directory)
```

All five subdirectories must exist.  Empty directories may contain a `.gitkeep`
sentinel file (these are ignored by `emanon validate`).

---

## `.gitverse/values.json` Schema

The file must be valid JSON with all four of the following top-level keys:

| Key | Type | Description |
|-----|------|-------------|
| `conflict_preference` | string | Default resolution strategy when `emanon negotiate` opens: `"contract"`, `"battle"`, or `"fork"` |
| `fork_readiness` | string | How readily this universe accepts forks: `"low"`, `"medium"`, or `"high"` |
| `battle_threshold` | number | Leverage advantage required for an auto-battle win (range 0–1) |
| `host_authority_mode` | string | How the universe host enforces rules: `"partition"`, `"consensus"`, or `"dictate"` |

### Example

```json
{
  "conflict_preference": "contract",
  "fork_readiness": "medium",
  "battle_threshold": 0.5,
  "host_authority_mode": "partition"
}
```

---

## `.gitattributes` Requirements

The file must register all three Emanon merge drivers:

```
regions/**       merge=emanon-collatz
contracts/**     merge=emanon-contract
scars/**         merge=emanon-append-only
```

These lines are written automatically by `emanon init`.  Do not remove them.

### Driver summary

| Pattern | Driver | Behaviour |
|---------|--------|-----------|
| `regions/**` | `emanon-collatz` | Collatz genus-based merge; auto-resolves same-set and same-oddity conflicts |
| `contracts/**` | `emanon-contract` | Contract-aware merge (M2+); currently falls back to Collatz with a diagnostic |
| `scars/**` | `emanon-append-only` | Append-only merge (M2+); currently falls back to Collatz with a diagnostic |

---

## Commit Message Format

`emanon snapshot` produces commit subjects of the form:

```
snapshot N: <message>
```

where `N` is the snapshot counter (monotonically increasing integer).  The
bootstrap commit from `emanon init` uses:

```
init: bootstrap <name> universe
```

`emanon validate` warns (but does not fail) on commits that do not match either
pattern, because external tooling may produce additional commits.

---

## Genus Stamps in `regions/`

Text files placed in `regions/` by `emanon write` carry an embedded genus stamp:

```
# emanon-genus: {"set_k": 3, "oddity_s": 1, "index_i": 0, "writer": "user@example.com", "snapshot": 4}
```

`emanon validate` warns on region files that have no parseable genus stamp.
It does **not** fail, because:

- `.gitkeep` sentinels are intentionally stamp-free.
- Binary files may use `.genus` sidecars instead of inline stamps.
- Files imported from outside the emanon toolchain may not have stamps yet.

Use `emanon genus <path>` to inspect or verify a stamp.

---

## Validation Severity Levels

| Check | Severity | Exit |
|-------|----------|------|
| Missing required directory | Error | 1 |
| Missing required file | Error | 1 |
| `values.json` malformed / missing key | Error | 1 |
| `.gitattributes` missing merge line | Error | 1 |
| Commit message format mismatch | Warning | 0 (1 with `--strict`) |
| Region file has no genus stamp | Warning | 0 (1 with `--strict`) |

Run with `--strict` (`-s`) to treat warnings as errors.

---

## Running Validation

```sh
# Basic — exits 0 on success, 1 on error
emanon validate

# Strict — warnings also cause exit 1
emanon validate --strict

# In CI (GitHub Actions)
- name: Validate universe
  run: emanon validate
```
