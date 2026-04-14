# Workflow: Initialize a Universe and Play First Turn

Use this workflow when the user wants to start a new Emanon universe and take
their first turn.

## Prerequisites

- `emanon` binary is installed and on `$PATH`
- User has a name and intent for the universe

## Steps

### 1. Initialize the Universe

```bash
emanon init <universe-name>
```

This creates the canonical `.gitverse/` layout:

```
<universe-name>/
  .git/                      # Standard git repo
  .gitattributes             # Registers Collatz merge drivers
  .gitignore                 # Excludes leverage.cache
  .gitverse/
    values.json              # Resolution preferences (hybrid, attenuated, etc.)
    identity.key             # Player identity (generated on init)
    leverage.cache           # Precomputed leverage metrics
    remotes.registry         # Known universes and trust levels
  regions/                   # Your game-state files go here
  contracts/                 # Signed agreements with other players
  scars/                     # Immutable conflict records
  forks/                     # Fork branch pointers and metadata
```

**Confirm with user**: "Universe `<name>` initialized. What would you like to
name the first region, and what's its starting state?"

### 2. Write Region Files

Region files are the heart of your universe. Each gets a Collatz genus stamp
that governs how it merges with other universes.

```bash
cd <universe-name>
emanon write regions/<your-name>/state.json '{"population": 100, "tech": 1}'
```

The `emanon write` command:
- Writes the content to the file
- Appends a `# emanon-genus: {...}` stamp with `set_k`, `oddity_s`, `index_i`
- The genus is derived from the current snapshot count + path hash

You can write multiple region files before taking a snapshot.

**Example — a starting civilization**:

```bash
emanon write regions/alpha/civilization.json '{"name": "Alpha", "population": 1000}'
emanon write regions/alpha/tech.json '{"level": 1, "fields": ["agriculture"]}'
emanon write regions/alpha/territory.txt "Northern highlands, rich in minerals."
```

### 3. Inspect the Genus Stamp

Before snapshotting, you can inspect what genus was assigned:

```bash
emanon genus regions/alpha/civilization.json
```

Output will show something like:
```
set_k=5 oddity_s=3 index_i=2 writer=<author> snapshot=0
```

### 4. Take a Snapshot

Once the region files look right, commit them as a snapshot:

```bash
emanon snapshot -m "Genesis — civilization Alpha founded"
```

This runs `git add -A` then commits with metadata trailers:
- `Snapshot-Count: 1`
- `Snapshot-Timestamp: <ISO>`

To skip `git add -A` (only commit already-staged files):
```bash
emanon snapshot --no-stage -m "Partial update"
```

### 5. Verify

After the snapshot:
```bash
git log --oneline -3
```

You should see your genesis commit. The universe is ready.

### Next Steps

- **Invite another player**: Share your repo URL so others can add it as a remote
- **Observe other universes**: See `workflows/observe-and-merge.md`
- **Draft a contract**: See `workflows/contract.md`

## Design Reference

See `emanon/docs/2026-04-13-gitverse-design.md` §"The Minimum Viable Gitverse"
for the full layout spec and merge driver configuration.

---

## Worked Examples

### Example 1: First-Time Setup — Solo Exploration Universe

**User says**: "Initialize a new universe called epsilon and set up my first civilization."

**Agent reasoning**:
> The user wants to start fresh. I'll init the universe, write a few starter region files to establish their civilization, check the genus stamps to confirm they're healthy, then snapshot. I should confirm the name before running init.

**Commands the agent should invoke**:

```bash
# Step 1 — create the universe
emanon init epsilon

# Step 2 — enter the universe and write starter files
cd epsilon
emanon write regions/epsilon/civilization.json '{"name": "Epsilon", "population": 1500, "tech": 1, "morale": "high"}'
emanon write regions/epsilon/tech.json '{"level": 1, "fields": ["agriculture", "stonecutting"]}'
emanon write regions/epsilon/territory.txt "Coastal lowlands, fertile delta with access to two rivers."

# Step 3 — verify genus stamps were assigned
emanon genus regions/epsilon/civilization.json
emanon genus regions/epsilon/tech.json

# Step 4 — take the genesis snapshot
emanon snapshot -m "Genesis — civilization Epsilon founded on coastal delta"
```

**Expected outputs**:

After `emanon init epsilon`:
```
Initialized empty universe: epsilon/
Created .gitverse/ layout
Registered merge drivers in .gitattributes
Initial commit: origin
```

After `emanon genus regions/epsilon/civilization.json`:
```
set_k=7 oddity_s=5 index_i=3 writer=player@example.com snapshot=0
```
*(Exact values vary — what matters is no error and all three fields present.)*

After `emanon snapshot -m "..."`:
```
[main abc1234] Genesis — civilization Epsilon founded on coastal delta
 Snapshot-Count: 1
 Snapshot-Timestamp: 2026-04-14T10:00:00Z
```

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `already exists` error on init | Directory `epsilon/` exists | Delete it first or use a different name |
| `not an emanon universe` on write/genus | Ran command outside universe dir | `cd epsilon` before running any emanon commands |
| `nothing to snapshot` | No files written yet | Write at least one region file first |
| Genus stamp missing after write | Binary build issue | Check `emanon write` exit code; the stamp is appended at file bottom |

---

### Example 2: Second Turn — Expanding a Civilization After Snapshot 1

**User says**: "I want to expand my territory and add a market district. Then snapshot as turn 2."

**Agent reasoning**:
> The user has already done their genesis snapshot. They want to add new region files and update existing ones, then take snapshot 2. I should write the new content, check the genus stamps have `snapshot=1` (reflecting the current count of 1), and then snapshot.

**Commands the agent should invoke**:

```bash
# Must be inside the universe directory already
# Confirm we're in the right place
ls .gitverse/

# Update existing civilization file
emanon write regions/epsilon/civilization.json '{"name": "Epsilon", "population": 1750, "tech": 1, "morale": "high", "districts": ["capital", "docks"]}'

# Write new region file for the market
emanon write regions/epsilon/market.json '{"type": "open_market", "goods": ["grain", "timber", "iron"], "established": 2}'

# Check genus on the new file
emanon genus regions/epsilon/market.json

# Snapshot turn 2
emanon snapshot -m "Turn 2 — market district opened, population grows to 1750"
```

**Expected outputs**:

After `emanon genus regions/epsilon/market.json`:
```
set_k=3 oddity_s=1 index_i=0 writer=player@example.com snapshot=1
```
*(`snapshot=1` because one snapshot has already been taken.)*

After `emanon snapshot -m "Turn 2 ..."`:
```
[main def5678] Turn 2 — market district opened, population grows to 1750
 Snapshot-Count: 2
 Snapshot-Timestamp: 2026-04-14T10:15:00Z
```

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `snapshot=0` on new file | No snapshot taken since init | That's correct for first genus stamp; take the snapshot |
| `no changes to snapshot` | Files unchanged since last snapshot | Make sure you've written files before snapshotting |
| Genus stamp shows different `set_k` on re-write | Path hash + snapshot seed changed | Normal — each write produces a new stamp |
