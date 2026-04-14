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

---

## Worked Examples

### Example 1: Clean Auto-Merge (Same set_k, No Conflicts)

**User says**: "Player beta pushed updates to their universe. I want to merge them in."

**Agent reasoning**:
> The user wants to pull in beta's changes. I should first observe what beta has done (are they working in the same regions?), then attempt the merge. If their genus `set_k` values match ours in the shared files, the Collatz driver will auto-resolve with a hybrid merge. I'll report on what I find before merging.

**Commands the agent should invoke**:

```bash
# Must be inside user's universe
# Step 1 — register remote if not already done
git remote add beta ../beta-universe  # or the actual URL

# Step 2 — observe beta's state
git fetch beta
git log --oneline beta/main -5
git diff HEAD..beta/main --name-only
git show beta/main:regions/beta/civilization.json | grep emanon-genus

# Step 3 — report to user, then merge
emanon merge beta/main

# Step 4 — verify outcome
git log --oneline -3
git show HEAD --stat
```

**Expected outputs**:

After `git log --oneline beta/main -5`:
```
f1e2d3c Turn 5 — beta expands to eastern plains
a9b8c7d Turn 4 — beta opens spice trade route
8765432 Turn 3 — beta builds harbor
```

After `emanon merge beta/main` (clean auto-resolve case):
```
Fetching beta...
Running Collatz merge driver on 2 paths...
  regions/shared/map.json: set_k match (k=5) → hybrid merge
  regions/beta/civilization.json: no conflict (beta-only file)
All paths resolved. Committing merge...
Merge committed: abc1234
```

After `git show HEAD --stat`:
```
commit abc1234 (HEAD -> main)
Merge: 1a2b3c4 f1e2d3c
Resolved-path: regions/shared/map.json (hybrid)

 regions/beta/civilization.json | 12 ++++++++++++
 regions/shared/map.json        |  8 ++++----
 2 files changed, 16 insertions(+), 4 deletions(-)
```

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `fatal: 'beta' does not appear to be a git repository` | Remote path wrong | Verify path/URL with `git remote -v` |
| `pending-merge.json not found` after attempted negotiate | No active merge | Run `emanon merge beta/main` before `emanon negotiate` |
| `set_k mismatch` forces negotiation | Different Collatz sets collide | Proceed to `emanon negotiate`; choose battle/contract/fork |

---

### Example 2: Partial Conflict — Negotiation Required

**User says**: "Merge with gamma, but I'm worried we've been developing the same territory. I want to battle for my version of regions/shared/capital.json."

**Agent reasoning**:
> The user has a specific conflict resolution preference upfront — they want to keep their version via "battle" for `regions/shared/capital.json`. I'll observe gamma's genus stamps first to confirm there's a real conflict, then merge and use `--non-interactive` negotiation with the battle resolution. That way I don't open the TUI interactively.

**Commands the agent should invoke**:

```bash
# Observe gamma's genus stamps on the contested file
git remote add gamma https://github.com/player-gamma/their-universe.git
git fetch gamma
git show gamma/main:regions/shared/capital.json | grep emanon-genus

# Compare with our genus stamp
emanon genus regions/shared/capital.json

# Initiate the merge
emanon merge gamma/main
# Expected: conflict written to .gitverse/pending-merge.json

# Non-interactive resolution: battle for capital.json, contract for anything else
echo '[
  {"path": "regions/shared/capital.json", "resolution": "battle"}
]' | emanon negotiate --non-interactive

# Verify the outcome
git log --oneline -3
ls scars/
cat scars/regions/shared/capital.json.scar 2>/dev/null || echo "check scars/ directory"
```

**Expected outputs**:

After `emanon merge gamma/main`:
```
Fetching gamma...
Running Collatz merge driver on 3 paths...
  regions/shared/capital.json: unrelated sets (our k=13, their k=7) → deferred
  regions/gamma/state.json: no conflict (gamma-only file)
1 path requires negotiation.
Conflict summary written to .gitverse/pending-merge.json
```

After non-interactive negotiate:
```
Resolved regions/shared/capital.json: battle (our version kept)
Writing scar: scars/regions/shared/capital.json.scar
All conflicts resolved. Committing merge...
Merge committed: def5678
  Resolved-path: regions/shared/capital.json (battle)
```

After `ls scars/`:
```
regions/
```
*(Scars are stored mirroring the original path.)*

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `pending-merge.json has 2 entries but you only resolved 1` | Resolution plan incomplete | Add all conflicting paths to the JSON array |
| `merge conflict in untracked file` | Git reports a conflict the driver didn't catch | Run `emanon negotiate` (TUI) to handle manually |
| Scar file empty | Binary file conflict | Check `.genus` sidecar files; binary scars store genus-only |
