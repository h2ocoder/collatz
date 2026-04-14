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
