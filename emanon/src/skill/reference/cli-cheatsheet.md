# Emanon CLI Cheatsheet

Quick reference for all `emanon` commands. Run `emanon --help` or
`emanon <command> --help` for full usage.

---

## Universe Management

### `emanon init <name>`

Initialize a new universe (git repo with `.gitverse/` layout).

```bash
emanon init my-universe        # Create ./my-universe/
emanon init my-universe -f     # Force (overwrite existing dir check)
```

Creates: `.gitverse/`, `.gitattributes`, `regions/`, `contracts/`, `scars/`, `forks/`

---

## Turn Actions

### `emanon snapshot [-m <message>] [--no-stage]`

Capture current state as a snapshot (commit).

```bash
emanon snapshot                          # Auto-message
emanon snapshot -m "Turn 3: expand north"  # Custom message
emanon snapshot --no-stage -m "Hotfix"  # Only commit staged files
```

Adds metadata trailers: `Snapshot-Count:`, `Snapshot-Timestamp:`

### `emanon write <path> [content]`

Write a file into the universe with an embedded Collatz genus stamp.

```bash
emanon write regions/alpha/state.json '{"pop": 100}'   # Text content
echo -n '\x89PNG...' | emanon write regions/map.png    # Binary (stdin)
```

Text files: genus stamp appended as `# emanon-genus: {...}`
Binary files: `.genus` sidecar created at `<path>.genus`

### `emanon genus <path>`

Print the Collatz genus stamp embedded in a file.

```bash
emanon genus regions/alpha/state.json
# Output: set_k=5 oddity_s=3 index_i=2 writer=alice@example.com snapshot=3
```

Exits 1 if no stamp found.

---

## Merge & Negotiation

### `emanon merge <remote>/<branch>`

Merge a remote timeline using the Collatz merge driver.

```bash
emanon merge beta/main
emanon merge origin/feature-branch
```

Runs `git fetch` then `git merge --no-commit --no-ff`. Auto-resolves:
- Same `set_k` → hybrid merge
- Same `oddity_s` → attenuated merge
- Unrelated → deferred to `emanon negotiate`

On conflict: writes `.gitverse/pending-merge.json`

### `emanon negotiate [--non-interactive]`

Interactively resolve conflicts from `emanon merge`.

```bash
emanon negotiate                          # Opens TUI
echo '[{"path":"regions/x.json","resolution":"battle"}]' | emanon negotiate --non-interactive
```

TUI controls:
- `↑↓` — navigate conflicts
- `b` — battle (keep ours, write scar)
- `c` — contract (accept theirs)
- `f` — fork (branch at FETCH_HEAD)
- `m` — manual (open $EDITOR)
- `q` — quit (without committing)

Non-interactive JSON schema per entry:
```json
{"path": "regions/foo.json", "resolution": "battle|contract|fork|manual"}
```

### `emanon merge-driver [--contract-mode|--append-only] <base> <ours> <theirs> <path>`

Low-level merge driver invoked by git via `.gitattributes`. Not called directly by players.

```bash
# Called automatically by git:
#   regions/**     → emanon merge-driver %O %A %B %P
#   contracts/**   → emanon merge-driver --contract-mode %O %A %B %P
#   scars/**       → emanon merge-driver --append-only %O %A %B %P
```

---

## Contracts

### `emanon contract new <name>`

Create a new contract draft under `contracts/<name>.md`.

### `emanon contract list`

List all contracts in this universe.

### `emanon contract show <name>`

Show contract details and signature status.

### `emanon contract sign <name>`

Sign a contract proposed by another player.

---

## Forking

### `emanon fork [--reason <text>]`

Fork the current timeline into a parallel branch.

```bash
emanon fork --reason "Exploring alternative tech path"
```

Creates: `forks/<timestamp>-<slug>.json`, new git branch

---

## Discovery & Registry

### `emanon scan <remote>`

Scan a remote universe for open bounties and forks.

```bash
emanon scan beta
emanon scan https://github.com/player-gamma/their-universe.git
```

### `emanon registry publish`

Publish this universe to the multiverse registry.

### `emanon registry list`

List known universes in the registry.

### `emanon registry join <url>`

Join a registry (set as a known remote).

---

## Bounties

### `emanon bounty post <description>`

Post a bounty (open task for collaboration).

### `emanon bounty list [<remote>]`

List active bounties (local or from a remote).

### `emanon bounty claim <id>`

Claim a bounty.

---

## Tournaments

### `emanon tournament join <url>`

Join a tournament.

### `emanon tournament status`

Show current tournament standing.

---

## Quick Workflows

### New universe, first turn

```bash
emanon init my-world
cd my-world
emanon write regions/alpha/state.json '{"pop": 100}'
emanon snapshot -m "Genesis"
```

### Observe and merge

```bash
git remote add beta <repo-url>
git fetch beta
git log --oneline beta/main -5
emanon merge beta/main
# If conflicts:
emanon negotiate
```

### Contract agreement

```bash
emanon write contracts/trade-pact.md "Terms: ..."
emanon snapshot -m "Propose trade pact"
# Other player fetches, merges, countersigns
```

---

## Key Files

| Path | Purpose |
|---|---|
| `.gitverse/values.json` | Universe resolution preferences |
| `.gitverse/identity.key` | Player signing key |
| `.gitverse/leverage.cache` | Cached leverage metrics |
| `.gitverse/remotes.registry` | Known universes |
| `.gitverse/pending-merge.json` | Active merge conflict state |
| `.gitattributes` | Merge driver registrations |
| `regions/` | Game-state files (genus-stamped) |
| `contracts/` | Signed multi-party agreements |
| `scars/` | Immutable battle records |
| `forks/` | Fork branch pointers and metadata |

## Design Reference

Full physics: `emanon/docs/2026-04-13-gitverse-design.md`
Economy & platform: `emanon/docs/2026-04-13-economy-and-platform.md`
Project structure: `emanon/docs/2026-04-13-emanon-structure-design.md`
