# Emanon

**A peer-to-peer 4X strategy game where universes are git repositories and Collatz mathematics is the physics.**

You play by writing files. Every file you write gets a Collatz genus stamp that encodes its history. When two players merge universes, the Collatz merge driver decides what survives. No server, no central authority — just git and math.

---

## Try it in three commands

```sh
# 1. Install
cargo install --path emanon/src/cli

# 2. Create your universe
emanon init my-world && cd my-world

# 3. Write your first region and snapshot
emanon write regions/core/origin.md "# Origin\nThis universe began here."
emanon snapshot -m "genesis"
```

That's it. You're playing.

---

## What's actually happening

- `emanon init` sets up a git repository with a canonical `.gitverse/` layout
- `emanon write` embeds a Collatz genus stamp — a mathematical fingerprint derived from your snapshot count and file path — into every file you create
- `emanon snapshot` is a `git commit` that advances your universe's timeline
- When you `emanon merge` another player's universe, the merge driver reads both genus stamps and applies Collatz-based resolution rules to decide what survives conflict

See [Concepts](emanon/docs/concepts.md) for what these terms mean as a player.

---

## Multi-player in 60 seconds

```sh
# Player A observes Player B's universe
git remote add b https://github.com/playerb/their-world
emanon merge b/main

# Conflicts open an interactive TUI
emanon negotiate
```

Conflict resolution has four paths: **battle** (ours wins), **contract** (negotiate terms), **fork** (diverge), or **manual** (your editor). The Collatz genus of each file influences which path is cheapest.

---

## Project layout

```
emanon/
  src/
    cli/            ← Rust CLI (the game engine)
    collatz-rs/     ← Collatz mathematics library
    skill/          ← Claude Code AI companion skill
  docs/
    getting-started.md   ← Full walkthrough, install to first merge
    install.md           ← Installation options
    concepts.md          ← Universe, snapshot, conflict, contract, fork
    2026-04-13-gitverse-design.md    ← Full physics design
    2026-04-13-game-mechanics-design.md
  starter-template/   ← Template repo for new universes
  tests/
    two-player-local.sh   ← End-to-end integration test
```

---

## Install

**From source** (requires Rust ≥ 1.75):

```sh
git clone https://github.com/h2ocoder/collatz
cd collatz/emanon/src/cli
cargo install --path .
emanon --version
```

See [install.md](emanon/docs/install.md) for prebuilt binaries and other options.

---

## Docs

| Document | What's in it |
|---|---|
| [Getting Started](emanon/docs/getting-started.md) | Install, first universe, first merge — step by step |
| [Concepts](emanon/docs/concepts.md) | Plain-English glossary for all game terms |
| [Install](emanon/docs/install.md) | Cargo, binaries, Homebrew |
| [Gitverse Design](emanon/docs/2026-04-13-gitverse-design.md) | Full physics: why universes are repos |
| [Game Mechanics](emanon/docs/2026-04-13-game-mechanics-design.md) | 4X loop, conflict recipes, progression |
| [Starter Template](https://github.com/forgetthefrets/emanon-starter) | GitHub template — fork to start a new universe |

---

## Status

Early development. The core engine (`init`, `snapshot`, `write`, `merge`, `negotiate`, `validate`) is implemented. The AI companion skill is available via Claude Code. Prebuilt binaries and Homebrew tap are planned for the first public release.

---

## License

MIT. See [LICENSE](LICENSE) if present.
