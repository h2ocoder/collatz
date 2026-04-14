# Workflow: Observe Another Universe and Merge

Use this workflow when the user wants to fetch from another player's universe,
inspect their state, and merge timelines.

## Prerequisites

- You are inside an initialized universe (`cd <your-universe>`)
- You have a URL or path to another player's universe

## Steps

### 1. Register the Remote Universe

```bash
git remote add <player-name> <repo-url-or-path>
```

Example:
```bash
git remote add beta ../beta-universe
git remote add gamma https://github.com/player-gamma/their-universe.git
```

### 2. Observe (Fetch Without Merging)

Fetch their timeline without merging anything:

```bash
git fetch <player-name>
```

Then observe what they've been doing:

```bash
# See their recent snapshots
git log --oneline <player-name>/main -10

# See what files they've changed
git diff HEAD..<player-name>/main --name-only

# Read one of their region files
git show <player-name>/main:regions/beta/civilization.json

# Check their genus stamps
git show <player-name>/main:regions/beta/civilization.json | grep emanon-genus
```

Summarize what you learn for the user: "Player beta has taken 7 snapshots,
focusing on `regions/beta/`. Their set_k values range from 3 to 11."

### 3. Scan for Open Bounties (Optional)

If the remote has bounties published:

```bash
emanon scan <player-name>
```

### 4. Decide Whether to Merge

Present the user with the choice:
- **Merge now**: timelines combine; Collatz merge driver resolves what it can
- **Wait**: continue observing; fetch again later
- **Fork instead**: don't merge, create a parallel branch (see `workflows/fork.md`)

### 5. Initiate the Merge

```bash
emanon merge <player-name>/main
```

This runs `git fetch` then `git merge --no-commit --no-ff`, letting the Collatz
merge driver process all registered paths (under `regions/`, `contracts/`,
`scars/`).

**Three outcomes**:

#### A. Clean merge (all conflicts auto-resolved)

The Collatz driver resolved everything. Output will say something like:
```
Auto-merged 3 files using Collatz driver
Merge committed: abc1234
```

Done! Show the user the merge commit summary.

#### B. Partial auto-resolve (some conflicts deferred to negotiation)

Output includes:
```
3 paths auto-merged, 2 paths require negotiation
Conflict summary written to .gitverse/pending-merge.json
```

Proceed to step 6.

#### C. Error (fetch failed, auth issue, etc.)

Diagnose: is the remote reachable? Does the user have read access?

### 6. Negotiate Conflicts (If Needed)

When conflicts remain, open the negotiation TUI:

```bash
emanon negotiate
```

The TUI shows each conflict with:
- **File path** being contested
- **Our genus** (set_k, oddity_s, leverage)
- **Their genus**
- **Resolution options**: battle / contract / fork / manual

#### Resolution Options

| Option | Meaning | Result |
|---|---|---|
| **battle** | Keep our version; write a scar | Our file wins; `scars/<path>.scar` records the conflict |
| **contract** | Accept their version; negotiate terms | Their file wins; `contracts/<path>` records agreement |
| **fork** | Branch at their HEAD; no merge | New branch in `forks/`; we diverge |
| **manual** | Open `$EDITOR` for direct edit | User edits the conflict marker |

#### Non-interactive Resolution (for agents)

If you want to programmatically resolve without the TUI:

```bash
echo '[{"path":"regions/shared.json","resolution":"battle"}]' | emanon negotiate --non-interactive
```

### 7. Verify the Merge Commit

```bash
git log --oneline -3
git show HEAD --stat
```

The merge commit includes `Resolved-path:` trailers listing each conflict and
how it was resolved.

### 8. Post-Merge

- Check `scars/` for any battle records
- Check `contracts/` for any new agreements
- Tell the user the leverage delta: "Your universe now has 12 snapshots vs. their 8"

## Design Reference

See `emanon/docs/2026-04-13-gitverse-design.md` §"The merge driver in pseudocode"
for the Collatz resolution rules and §"Architecture" for the negotiation UI.
