---
name: emanon
description: Use when the user wants to play the Emanon gitverse game — initialize a universe, take a turn, observe other universes, merge with negotiation, draft contracts, or fork. Wraps the `emanon` CLI.
---

# Emanon Skill

Emanon is a peer-to-peer 4X game where **universes are git repositories** and
**Collatz dynamics are the physics**. You are an AI agent helping a player navigate
this game via the `emanon` CLI.

## Core Concepts

| Concept | Implementation |
|---|---|
| Universe | A git repository with `.gitverse/` layout |
| Snapshot | A commit (`emanon snapshot`) |
| Player identity | `.gitverse/identity.key` + git author |
| Region | A file under `regions/` with a Collatz genus stamp |
| Contract | A co-signed file under `contracts/`, byte-identical in all signatories |
| Scar | An immutable conflict record under `scars/` |
| Fork | A branch point recorded under `forks/` |
| Leverage | Your universe's commit-count advantage in a negotiation |

## When to Use This Skill

Trigger this skill when the user asks to:
- **Start a new universe** — "create a new universe", "init a world called X"
- **Take a turn** — "play a turn", "snapshot my changes", "write a region file"
- **Explore another universe** — "scan remote Y", "observe what player Z has done"
- **Merge / negotiate** — "merge with player Y", "resolve conflicts", "negotiate"
- **Draft or sign a contract** — "propose a contract", "sign the contract"
- **Fork** — "fork this universe", "branch my timeline"
- **Check genus** — "what's the genus of this file?"

## Workflow Selection Guide

Choose the appropriate workflow based on what the user wants to do:

| User intent | Workflow |
|---|---|
| First time setup, new universe | `workflows/init-and-play.md` |
| Merging with another player | `workflows/observe-and-merge.md` |
| Drafting or signing a contract | `workflows/contract.md` |
| Branching the timeline | `workflows/fork.md` |
| Just need a command | `reference/cli-cheatsheet.md` |

## Quick Start

```bash
# 1. Initialize a universe
emanon init my-universe

# 2. Write a region file (with Collatz genus stamp)
cd my-universe
emanon write regions/alpha/state.json '{"population": 100, "tech": 1}'

# 3. Take a snapshot (commit)
emanon snapshot -m "First turn"

# 4. Check the genus stamp
emanon genus regions/alpha/state.json
```

## Agent Behavior Guidelines

- **Always run `emanon` from inside the universe directory** (where `.gitverse/` lives)
- **Do not call `git` directly** for game actions — use `emanon` commands which wrap git with game semantics
- **Genus stamps are automatic** — `emanon write` handles stamping; never add them by hand
- **After every `emanon snapshot`**, confirm with the user before taking the next action
- **When a merge produces conflicts**, use `emanon negotiate` to resolve them interactively
- **If the user wants to force something**, explain the game consequence (leverage, scar, fork) before proceeding
- **Design doc reference**: `emanon/docs/2026-04-13-gitverse-design.md` has the full physics

## Error Handling

| Error | Meaning | Action |
|---|---|---|
| `nothing to snapshot` | Working tree is clean | Tell user no changes to commit |
| `exit 1` from merge-driver | Unrelated Collatz sets — negotiation required | Run `emanon negotiate` |
| `pending-merge.json not found` | No active merge | Remind user to run `emanon merge <remote>/<branch>` first |
| `not an emanon universe` | Not in a `.gitverse` directory | `cd` into the universe or run `emanon init` |
