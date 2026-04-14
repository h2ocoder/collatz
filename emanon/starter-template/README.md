# emanon-starter

> **Your universe begins here.**

This is the official starter template for [Emanon](https://github.com/h2ocoder/collatz) — a peer-to-peer 4X strategy game where universes are git repositories and Collatz sequence dynamics are the physics.

---

## What is Emanon?

Emanon is a game that runs *inside git*. Every universe is a repository. Every snapshot is a commit. When two universes interact, it's a `git merge` — and Collatz mathematics determines how their histories resolve.

| Game concept     | Git primitive               |
|------------------|-----------------------------|
| Universe         | Repository / branch         |
| Snapshot         | Commit                      |
| Region           | Directory under `regions/`  |
| Contract         | Co-signed merge commit      |
| Scar             | Merge commit with metadata  |
| Fork             | Branch or repo fork         |
| Observation      | `git log other-remote`      |

Read the [full design doc](https://github.com/h2ocoder/collatz/blob/main/emanon/docs/2026-04-13-gitverse-design.md) to understand the physics.

---

## Quick Start

```sh
# 1. Fork this template into your own universe
gh repo create my-world --template h2ocoder/emanon-starter --public --clone
cd my-world

# 2. Take your first snapshot
emanon snapshot -m "genesis"

# 3. Write your first region
emanon write regions/core/origin.md "# Origin\nThis universe began here."
```

That's it — you're playing. Every `emanon snapshot` is a commit. Every `emanon write` stamps a [Collatz genus](https://github.com/h2ocoder/collatz/blob/main/emanon/docs/2026-04-13-gitverse-design.md) onto your file.

---

## Installing the Emanon CLI

```sh
# From source (requires Rust toolchain)
git clone https://github.com/h2ocoder/collatz
cd collatz/emanon/src/cli
cargo install --path .
```

Verify: `emanon --version`

---

## Universe Structure

```
my-world/
├── regions/        ← spatial partitions of your universe
├── contracts/      ← agreements with other players / universes
├── scars/          ← records of resolved conflicts
├── forks/          ← active timeline divergences
├── .gitverse/
│   ├── values.json          ← conflict-resolution preferences
│   └── snapshot_count       ← current snapshot counter
├── .gitattributes           ← merge driver registration
└── .gitignore               ← excludes ephemeral cache files
```

---

## Interacting with Other Universes

```sh
# Observe another universe
git remote add neighbor https://github.com/other-player/their-world
git fetch neighbor

# Attempt a merge
emanon merge neighbor/main

# Resolve conflicts with the TUI
emanon negotiate
```

---

## Merge Driver

The `.gitattributes` in this repo registers three Emanon merge drivers:

| Path pattern   | Driver                | Behavior                              |
|----------------|-----------------------|---------------------------------------|
| `regions/**`   | `emanon-collatz`      | Collatz genus resolution              |
| `contracts/**` | `emanon-contract`     | Contract-aware merge                  |
| `scars/**`     | `emanon-append-only`  | Append-only (scar history preserved)  |

Drivers are registered in `.git/config` by `emanon init` — but since this is a template, you should run:

```sh
emanon init --force .
```

…once after cloning (or forking) to register the drivers in your local `.git/config`.

---

## Configuration

Edit `.gitverse/values.json` to set your universe's conflict preferences:

```json
{
  "conflict_preference": "contract",
  "fork_readiness": "medium",
  "battle_threshold": 0.5,
  "host_authority_mode": "partition"
}
```

| Field                  | Values                              | Meaning                                      |
|------------------------|-------------------------------------|----------------------------------------------|
| `conflict_preference`  | `contract`, `battle`, `fork`        | Default resolution when facing a conflict    |
| `fork_readiness`       | `low`, `medium`, `high`             | How willing you are to diverge timelines     |
| `battle_threshold`     | 0.0–1.0                             | Leverage ratio needed to win a battle        |
| `host_authority_mode`  | `partition`, `consensus`, `anarchy` | Governance model for this universe           |

---

## Further Reading

- [Gitverse Design Doc](https://github.com/h2ocoder/collatz/blob/main/emanon/docs/2026-04-13-gitverse-design.md) — full game physics
- [Economy & Platform Doc](https://github.com/h2ocoder/collatz/blob/main/emanon/docs/2026-04-13-economy-and-platform.md) — three-market economy, cNFT integration
- [CLI Reference](https://github.com/h2ocoder/collatz/tree/main/emanon/src/cli) — all subcommands
- [Emanon Skill for Claude](https://github.com/h2ocoder/collatz/tree/main/emanon/src/skill) — play via AI assistant

---

## License

MIT — see [LICENSE](LICENSE).
