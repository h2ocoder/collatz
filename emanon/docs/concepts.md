# Concepts

> Plain-English explanations of everything Emanon. No prior git knowledge required, but it helps.

---

## Universe

A universe is a git repository. Every player has one. It has a history — a sequence of snapshots going back to genesis. Your universe is yours: you control what goes in it, who can observe it, and whether you allow merges.

When you run `emanon init my-world`, you create a new universe at `my-world/`. Internally it's a git repo with a `.gitverse/` directory that stores metadata the engine uses to track your position in the multiverse.

**As a player:** your universe is your territory. The files in `regions/` are the parts of space you control.

---

## Snapshot

A snapshot is a saved state of your universe — a git commit. Every time you run `emanon snapshot`, the engine hashes everything in your universe and saves it immutably.

Snapshots are permanent. You can always go back to any previous snapshot with standard git tools. Your snapshot count (`emanon snapshot --list` or `.gitverse/snapshot_count`) is part of how the Collatz genus stamps work — it seeds the mathematics.

**As a player:** think of a snapshot as "sealing" your current move. Until you snapshot, changes are provisional.

---

## Region

A region is a directory under `regions/`. Regions are spatial partitions of your universe — think of them as zones, territories, or sectors of space that you control and develop.

```
my-world/
└── regions/
    ├── core/           ← your home territory
    ├── frontier/       ← newly discovered space
    └── contested/      ← space someone else has also touched
```

The Collatz merge driver operates at the file level within regions. When two universes merge, conflicting regions are where the game happens.

---

## Genus Stamp

Every file you write with `emanon write` gets a Collatz genus stamp — a mathematical fingerprint embedded at the bottom of the file:

```
# emanon-genus: {"set_k": 5, "oddity_s": 3, "index_i": 12, "writer": "you@example.com", "snapshot": 7}
```

These three numbers — `set_k`, `oddity_s`, `index_i` — encode the Collatz trajectory of a seed derived from your snapshot count and file path. They're what the merge driver reads when two files conflict.

**As a player:** you don't need to understand the math. The genus is like a "combat stat" that determines what happens when your file meets another player's version of the same file.

See the [Gitverse Design](2026-04-13-gitverse-design.md) if you want the full mathematics.

---

## Merge

A merge is what happens when two universes interact. You run:

```sh
git remote add neighbor https://github.com/playertwo/their-world
emanon merge neighbor/main
```

The engine fetches their history, attempts a three-way merge, and identifies all files where your version and their version diverge. For each conflict, it reads both genus stamps and determines what kind of conflict this is.

**Three auto-resolution cases:**
1. **Same `set_k`:** both files have the same Collatz set — they're compatible. The driver produces a hybrid (both versions concatenated).
2. **Same `oddity_s`, different `set_k`:** related but different Collatz trajectories. The driver attenuates — keeps the numerically lower genus value.
3. **Unrelated genus:** conflict is unresolvable automatically. Escalates to `emanon negotiate`.

After the merge, unresolved conflicts are recorded in `.gitverse/pending-merge.json`.

---

## Conflict Resolution

When `emanon merge` can't resolve everything automatically, you run `emanon negotiate`. This opens a terminal interface (TUI) listing every unresolved conflict. For each one, you choose:

| Resolution | What happens |
|---|---|
| **Battle** | Your version wins. Their version is discarded. A scar record is written to `scars/`. |
| **Contract** | You accept their version, but terms are written to `contracts/`. The merge is recorded as a cooperative agreement. |
| **Fork** | Neither version wins. A new git branch is created at their commit, and a fork pointer is written to `forks/`. Both timelines continue. |
| **Manual** | Opens your `$EDITOR`. You resolve it yourself. |

After all conflicts are resolved, `emanon negotiate` creates a merge commit with metadata trailers recording what was resolved and how.

---

## Contract

A contract is a file in `contracts/` that records an agreement between two universes. When you use the "contract" resolution in `emanon negotiate`, the engine writes a contract file with the terms: which file was in dispute, which version was accepted, and who was party to the agreement.

Contracts are part of your universe's permanent history — they show up in `git log`. Over time they build a trust record: other players can see whether you keep your agreements.

---

## Scar

A scar is a record of a battle. When you resolve a conflict with "battle" (your version wins), the engine writes a scar to `scars/` noting that a conflict happened, what path was contested, and what genus values were involved.

Scars are permanent. They're a form of history that other players can read to understand your style of play.

---

## Fork

A fork is a timeline divergence. When you choose the "fork" resolution in `emanon negotiate`, instead of either player's version winning, both timelines continue to exist — one as a git branch in your repo.

Forks are expensive (you carry both timelines) but sometimes necessary if you and another player have genuinely incompatible directions.

---

## Values

Your universe has a `.gitverse/values.json` file that describes your conflict-resolution preferences. These are hints to the merge driver — not hard rules — about how you want disputes settled when the Collatz math doesn't auto-resolve them.

Example:
```json
{
  "resolution_preference": "negotiate",
  "fork_on_irreconcilable": true,
  "player_email": "you@example.com",
  "universe_name": "my-world"
}
```

---

## Leverage

When `emanon merge` runs, it calculates **leverage** — how many commits each side has made since the last common ancestor. Higher leverage means more history invested. Leverage is recorded in `.gitverse/pending-merge.json` and influences how the negotiate TUI presents conflicts (higher-leverage side is shown first).

---

## Validation

`emanon validate` checks that your universe is well-formed: required directories exist, `values.json` is valid, `.gitattributes` has the merge driver registrations, and genus stamps in `regions/` files are parseable.

Run it before merging or sharing your universe to catch structural problems early.

```sh
cd my-world && emanon validate
emanon validate --strict   # treat warnings as errors
```
