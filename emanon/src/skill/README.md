# Emanon Skill for Claude Code

A Claude Code skill that wraps the `emanon` CLI, enabling an AI agent to play
the Emanon gitverse game on behalf of a user.

## What is Emanon?

Emanon is a peer-to-peer 4X game where **universes are git repositories** and
**Collatz dynamics are the physics**. Players colonize regions, negotiate
contracts, fight battles, and fork timelines — all through git commits.

See the full design doc: `emanon/docs/2026-04-13-gitverse-design.md`

---

## Installation

### Option 1: Symlink (recommended for development)

```bash
# From the repo root
ln -s "$(pwd)/emanon/src/skill" ~/.claude/skills/emanon
```

### Option 2: Run the install script

```bash
bash emanon/src/skill/install.sh
```

The install script creates a symlink at `~/.claude/skills/emanon` pointing to
this directory. It also checks that the `emanon` binary is on your `$PATH`.

### Verify installation

```bash
# Check the skill is visible to Claude Code
ls ~/.claude/skills/emanon/SKILL.md

# Check the emanon binary
emanon --version
```

---

## Directory Structure

```
emanon/src/skill/
  SKILL.md               ← Skill entry point (Claude reads this first)
  README.md              ← This file
  install.sh             ← Installation helper
  workflows/
    init-and-play.md     ← New universe + first turn
    observe-and-merge.md ← Fetch, inspect, merge another universe
    contract.md          ← Draft and countersign agreements
    fork.md              ← Branch a timeline
  reference/
    cli-cheatsheet.md    ← All commands, quick lookup
```

---

## Testing the Skill

### Manual smoke test (no binary required)

To verify the skill loads correctly in Claude Code:

1. Start a Claude Code session in any directory
2. Ask: *"Initialize a new emanon universe called test-world"*
3. Claude should respond with the `emanon init test-world` command

If the skill is not loaded, Claude won't know about emanon commands.

### Integration test (requires Python 3.9+ and Anthropic API key)

The integration test calls the Claude API with the skill's SKILL.md as context
and verifies the agent produces the correct command sequence for a full play session.

```bash
# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Run the test
cd emanon/tests
python test-skill-integration.py
```

The test:
1. Loads `SKILL.md` and all workflow files as context
2. Issues the prompt: *"Start a new universe named alpha-test, write a planet file
   in regions/alpha, snapshot, then fork it for an alternate timeline"*
3. Verifies `init → write → snapshot → fork` appear in the correct order
4. Optionally asserts filesystem state if the `emanon` binary is installed

See `emanon/tests/test-skill-integration.py` for details.

---

## Workflow Quick Reference

| Goal | Workflow file |
|---|---|
| Start a new universe | `workflows/init-and-play.md` |
| Merge with another player | `workflows/observe-and-merge.md` |
| Sign an agreement | `workflows/contract.md` |
| Branch a timeline | `workflows/fork.md` |
| Command lookup | `reference/cli-cheatsheet.md` |

---

## Failure Recovery Reference

| Error | What happened | Fix |
|---|---|---|
| `not an emanon universe` | Not inside a `.gitverse` directory | `cd <universe-name>` |
| `nothing to snapshot` | Working tree is clean | Write files before snapshotting |
| `pending-merge.json not found` | No active merge | Run `emanon merge <remote>/<branch>` first |
| `exit 1` from merge-driver | Collatz sets are unrelated — conflict | Run `emanon negotiate` |
| `contract conflict` | Contract text differs between players | Use `emanon negotiate` → choose "contract" to accept authoritative version |
| Binary not found: `emanon: command not found` | Binary not installed or not on `$PATH` | Build from source: `cargo build --release -p emanon-cli`, then add to `$PATH` |

---

## Building the Binary

The skill requires the `emanon` binary. Build it from source:

```bash
# From the repo root
cd emanon
cargo build --release -p emanon-cli

# Binary will be at:
./target/release/emanon

# Add to PATH (example for bash):
echo 'export PATH="$HOME/collatz/emanon/target/release:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Requires Rust 1.70+ and a C linker (`cc`/`gcc`).

---

## Development Notes

- The skill is pure markdown — no compiled code
- Workflow files are read by Claude on demand (not all at startup)
- The `SKILL.md` entry point routes to the appropriate workflow based on user intent
- The integration test (`test-skill-integration.py`) validates agent reasoning
  without requiring a live game universe
