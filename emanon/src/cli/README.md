# Emanon CLI

The `emanon` command-line tool is the primary interface for human players and AI agents
interacting with the Emanon multiverse game engine.

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0.1 — CLI scaffold (this PR) | ✅ Done — all subcommands stubbed |
| M0.2 — `init` implementation | 🔲 Upcoming |
| M0.3 — `snapshot` implementation | 🔲 Upcoming |
| M1+ — Remaining subcommands | 🔲 Upcoming |

## Build

Requires Rust 1.70+ with Cargo. Install via [rustup](https://rustup.rs/):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Then build:

```bash
cd emanon/src/cli
cargo build --release
# Binary at: target/release/emanon
```

## Usage

```
emanon --help
```

All subcommands are currently stubbed — each prints a "not yet implemented" message.
Implementation arrives in later milestones.

### Subcommands

| Command | Description |
|---------|-------------|
| `emanon init <name>` | Initialize a new Emanon universe (git repo) |
| `emanon snapshot [-m message]` | Capture current state as a snapshot (commit) |
| `emanon merge <remote>/<branch>` | Merge a remote timeline via the Collatz driver |
| `emanon fork [-r reason]` | Fork the current timeline |
| `emanon contract draft\|sign\|list` | Manage inter-player contracts |
| `emanon scan <remote>` | Scan a remote universe |
| `emanon bounty post\|list\|accept\|deliver` | Manage bounties |
| `emanon tournament join\|leave\|play` | Manage tournament participation |
| `emanon registry push\|pull\|list` | Publish/pull from the registry |

## Architecture

See `emanon/docs/2026-04-13-emanon-structure-design.md` for the full architecture overview.

The CLI is a thin Rust binary that will wrap `git` plus the Collatz merge driver.
Rust was chosen for: single static binary, fast startup, compatibility with the Solana
toolchain used in later milestones.
