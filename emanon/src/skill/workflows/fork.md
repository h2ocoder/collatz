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
