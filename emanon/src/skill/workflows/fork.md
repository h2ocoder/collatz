# Workflow: Fork a Universe

Use this workflow when a player wants to branch their timeline — creating a
parallel universe that shares ancestry but diverges from the original.

## What is a Fork?

In Emanon, a **fork** is a branch point where a universe splits into two
divergent timelines. Forks are recorded in `forks/` with metadata explaining
the reason. Forks:
- Create **fork ancestry depth** contributing to leverage
- Allow parallel experimentation without losing the original timeline
- Can be proposed during negotiation (when neither battle nor contract is right)
- Are irreversible — once forked, the timelines have independent histories

## When to Fork

Consider forking when:
- A merge conflict cannot be resolved by battle or contract
- You want to explore an alternative strategy without committing
- Another player's universe is interesting but incompatible with your values
- You want to hold a "shadow" timeline as a bargaining chip

## Steps

### 1. Fork the Current Timeline

```bash
emanon fork --reason "Diverging after failed contract with Beta"
```

This:
1. Creates a new branch at `HEAD` (named with timestamp + reason slug)
2. Records fork metadata in `forks/<timestamp>-<slug>.json`
3. Snapshots the fork pointer with a commit

The `--reason` flag is optional but strongly recommended — it's recorded in the
fork metadata and in the merge history.

### 2. What Gets Created

```
forks/
  2026-04-14-diverging-after-failed-contract.json
```

The fork file contains:
```json
{
  "fork_at": "abc1234...",
  "branch": "fork/2026-04-14-diverging-after-failed-contract",
  "reason": "Diverging after failed contract with Beta",
  "timestamp": "2026-04-14T10:00:00Z",
  "parent_snapshot": 7
}
```

### 3. Switch to the Fork Branch

To work on the forked timeline:

```bash
git checkout fork/2026-04-14-diverging-after-failed-contract
```

From here you can:
- Write new region files
- Take snapshots
- Merge from other universes independently

### 4. Fork During Negotiation

Forks can also be created during `emanon negotiate`. When reviewing a conflict:
1. Select the conflicting path
2. Press `f` (or choose **fork** in the menu)
3. The negotiation UI creates a fork branch at `FETCH_HEAD` and records it in `forks/`

After negotiation completes, the main timeline has a merge commit; the fork
exists as a separate branch tracking the other player's divergence.

### 5. View Your Fork Tree

```bash
git branch | grep fork/
git log --oneline --graph --all -20
```

### 6. Merging a Fork Back (Optional)

If a forked timeline proves valuable and you want to reunite:

```bash
# While on main branch
emanon merge fork/<fork-branch-name>
```

The Collatz merge driver applies again — now both sides have evolved under the
map, so set_k and oddity_s values may have drifted further apart.

### 7. Leverage Impact

Fork depth counts toward your leverage score:
```
leverage = log_size + scar_count + contract_count + fork_depth
```

More forks = more strategic options = higher leverage. But forks also fragment
your attention — each active fork requires snapshots to stay current.

## Design Reference

See `emanon/docs/2026-04-13-gitverse-design.md` §"Architecture" (fork ancestry
in leverage calculator) and §"The Minimum Viable Gitverse" (`forks/` directory).

---

## Worked Examples

### Example 1: Forking to Explore an Alternate Tech Path

**User says**: "I want to try a high-tech low-population strategy, but I don't want to lose my current civilization. Fork the universe and experiment."

**Agent reasoning**:
> The user wants to run an experiment in isolation without risking their main timeline. This is a clean fork off the current HEAD — no merge conflict involved. I'll fork with a descriptive reason, report the new branch name, then switch to it so they can start experimenting.

**Commands the agent should invoke**:

```bash
# Must be inside the universe
# Step 1 — confirm current state
git log --oneline -3
git status

# Step 2 — create the fork
emanon fork --reason "Exploring high-tech low-population path"

# Step 3 — check what was created
cat forks/$(ls forks/ | tail -1)
git branch | grep fork/

# Step 4 — switch to the fork branch to work in the alternate timeline
git checkout $(git branch | grep fork/ | tail -1 | tr -d ' ')

# Step 5 — write experimental region files on the fork
emanon write regions/alpha/tech.json '{"level": 5, "fields": ["cybernetics", "fusion"], "population_efficiency": 10}'
emanon snapshot -m "Fork experiment: tech-5 with low population"
```

**Expected outputs**:

After `emanon fork --reason "Exploring high-tech low-population path"`:
```
Created fork: fork/2026-04-14-exploring-high-tech-low-population-path
Fork metadata: forks/2026-04-14-exploring-high-tech-low-population-path.json
Snapshot committed on main: [ALPHA-TEST abc1234] Fork pointer: exploring-high-tech-low-population-path
```

After `cat forks/2026-04-14-exploring-high-tech-low-population-path.json`:
```json
{
  "fork_at": "abc1234...",
  "branch": "fork/2026-04-14-exploring-high-tech-low-population-path",
  "reason": "Exploring high-tech low-population path",
  "timestamp": "2026-04-14T10:00:00Z",
  "parent_snapshot": 5
}
```

After `git log --oneline --graph --all -10`:
```
* def5678 (fork/2026-04-14-exploring-high-tech-low-population-path) Fork experiment: tech-5 with low population
* abc1234 (HEAD -> main) Fork pointer: exploring-high-tech-low-population-path
* 789abcd Turn 5 — market district opened
```

**Tell the user**:
> "Fork created at `fork/2026-04-14-exploring-high-tech-low-population-path`. I've switched you to that branch. Your main timeline is untouched at `main`. When you're done experimenting, run `git checkout main` to return."

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| Fork branch not visible in `git branch` | Used `git branch` without the `fork/` prefix filter | Run `git branch --list 'fork/*'` |
| Fork metadata file missing | `emanon fork` exited with an error | Check exit code; look for error message; retry |
| Changes on fork accidentally affect main | Committed to wrong branch | `git checkout main` and verify with `git log --oneline -3` |

---

### Example 2: Forking During Negotiation (Irreconcilable Conflict)

**User says**: "My merge with player omega produced a conflict on regions/shared/ocean.json. I don't want to battle or sign a contract — I want to diverge from omega entirely."

**Agent reasoning**:
> The user wants a fork resolution during negotiation. The `emanon negotiate` command supports this with `--non-interactive` mode using `"resolution": "fork"`. This will create a fork branch at FETCH_HEAD and record it in `forks/`. The main timeline's merge commit will have a `Resolved-path: ... (fork)` trailer.

**Commands the agent should invoke**:

```bash
# Step 1 — verify there's an active pending merge
cat .gitverse/pending-merge.json

# Step 2 — confirm the contested path
# (The user says it's regions/shared/ocean.json)

# Step 3 — non-interactive fork resolution
echo '[
  {"path": "regions/shared/ocean.json", "resolution": "fork"}
]' | emanon negotiate --non-interactive

# Step 4 — check what was created
git branch | grep fork/
ls forks/
cat forks/$(ls forks/ | tail -1)

# Step 5 — verify merge commit on main
git log --oneline -3
git show HEAD --stat
```

**Expected outputs**:

After `cat .gitverse/pending-merge.json`:
```json
{
  "merge_head": "omega_sha...",
  "ours_leverage": 12,
  "theirs_leverage": 9,
  "conflicts": [
    {
      "path": "regions/shared/ocean.json",
      "ours_set_k": 13,
      "theirs_set_k": 7,
      "ours_oddity_s": 9,
      "theirs_oddity_s": 5
    }
  ]
}
```

After non-interactive negotiate with fork resolution:
```
Resolved regions/shared/ocean.json: fork
  Created branch: fork/2026-04-14-omega-divergence
  Fork metadata: forks/2026-04-14-omega-divergence.json
All conflicts resolved. Committing merge...
Merge committed: n7o8p9q
  Resolved-path: regions/shared/ocean.json (fork)
```

After `git show HEAD --stat`:
```
commit n7o8p9q (HEAD -> main)
Merge: abc1234 omega_sha
Resolved-path: regions/shared/ocean.json (fork)

 regions/shared/ocean.json | 0 (unmodified — fork took their branch, not our content)
 forks/2026-04-14-omega-divergence.json | 8 ++++++++
```

**Tell the user**:
> "Done. Omega's version of `regions/shared/ocean.json` lives on the fork branch `fork/2026-04-14-omega-divergence`. Your main timeline keeps your version. The fork adds to your leverage score."

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `pending-merge.json not found` | No active merge | Run `emanon merge omega/main` first |
| Fork resolution creates branch but merge still shows conflict | Partial plan — other paths still unresolved | Add all conflict paths to the JSON plan |
| Fork branch not appearing in `git branch` | Negotiate didn't complete cleanly | Check exit code; inspect `.gitverse/pending-merge.json` for remaining entries |
