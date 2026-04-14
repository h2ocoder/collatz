# Workflow: Draft and Sign a Contract

Use this workflow when players want to formalize an agreement — a contract that
becomes an immutable, byte-identical file in both universes' `contracts/` directory.

## What is a Contract?

In Emanon, a **contract** is a file under `contracts/` that:
- Is byte-identical in at least two universes (enforced by the `emanon-contract` merge driver)
- Records the terms of an agreement between players
- Earns **contract leverage** — once signed, it counts toward your leverage score
- Is append-only after signing (the `emanon-append-only` driver protects `scars/`)

## Prerequisites

- Both players have initialized universes
- Both players can reach each other's repos (shared remote)
- You are inside your universe directory

## Steps

### 1. Draft the Contract

Start a new contract:

```bash
emanon contract new <contract-name>
```

This creates `contracts/<contract-name>.md` with a template. You can also write
it manually with `emanon write`:

```bash
emanon write contracts/trade-agreement.md "# Trade Agreement

Parties: Alpha, Beta
Date: $(date -I)

Terms:
1. Alpha grants Beta access to northern mineral deposits
2. Beta provides Alpha with 2 tech advances per cycle
3. Duration: 10 snapshots from signing date

Signatures:
- Alpha: [pending]
- Beta: [pending]
"
```

The genus stamp on a contract file governs conflict resolution if the terms are
ever disputed during a merge.

### 2. Review the Contract

Inspect the draft:

```bash
cat contracts/trade-agreement.md
emanon genus contracts/trade-agreement.md
```

Confirm the terms with the user before proceeding.

### 3. Sign and Snapshot

If the terms look right, snapshot with a signing message:

```bash
emanon snapshot -m "Sign trade agreement with Beta"
```

### 4. Share with the Other Player

Push (or share the path) so the other player can fetch:

```bash
git push origin main
# or share the path for local testing
```

### 5. Other Player Countersigns

The other player:
1. Fetches your universe
2. Reviews the contract file
3. If they agree — runs `emanon merge your-remote/main`
4. The `emanon-contract` merge driver validates byte-identity
5. They snapshot: `emanon snapshot -m "Countersign trade agreement with Alpha"`

### 6. Verify the Contract is Live

Both players should see:

```bash
git log --oneline -- contracts/trade-agreement.md
```

And the file should be byte-identical:

```bash
git diff <other-player>/main -- contracts/trade-agreement.md
# Should produce no output if identical
```

### 7. Managing Existing Contracts

```bash
# List all contracts
emanon contract list

# Show contract details
emanon contract show <contract-name>

# Sign a contract proposed by another player
emanon contract sign <contract-name>
```

## Contract Merge Driver Behavior

When a merge touches `contracts/`:
- The `emanon-contract` driver checks byte-identity
- If both sides have the same content → auto-resolve (no conflict)
- If content differs → conflict deferred to `emanon negotiate`
- During negotiation, choosing **contract** resolution means accepting the
  other player's version as authoritative

## Leverage Impact

Signed contracts increase your **contract count** component of leverage:
```
leverage = log_size + scar_count + contract_count + fork_depth
```

Contracts align incentives: the more agreements you hold, the more leverage you
have in future negotiations.

## Design Reference

See `emanon/docs/2026-04-13-gitverse-design.md` §"Architecture" (leverage calculator)
and §"The Minimum Viable Gitverse" for the contracts/ directory semantics.

---

## Worked Examples

### Example 1: Proposing a Trade Alliance

**User says**: "I want to offer player delta a trade deal — my iron for their grain, for 5 snapshots."

**Agent reasoning**:
> The user wants to propose a bilateral contract with specific terms. I'll draft it using `emanon write` (which adds a genus stamp, unlike plain file writes), then snapshot to record their signature. After that, I'll tell the user to share the repo URL with delta so delta can countersign.

**Commands the agent should invoke**:

```bash
# Must be inside user's universe
# Step 1 — draft the contract
emanon write contracts/iron-grain-alliance.md "# Iron-Grain Trade Alliance

Parties: Alpha (proposer), Delta (acceptor)
Proposed: $(date -I)

Terms:
1. Alpha provides Delta with iron ore access (regions/alpha/iron-mine.json) for 5 snapshots
2. Delta provides Alpha with grain surplus (regions/delta/granary.json) for 5 snapshots
3. Duration: 5 snapshots from the snapshot where both parties merge this contract
4. Breach: any unilateral modification triggers a battle-resolution scar

Signatures:
- Alpha: signed at snapshot $(git rev-list --count HEAD 2>/dev/null || echo 'N/A')
- Delta: [pending countersignature]
"

# Step 2 — review before signing
cat contracts/iron-grain-alliance.md
emanon genus contracts/iron-grain-alliance.md

# Step 3 — sign (snapshot)
emanon snapshot -m "Propose iron-grain trade alliance with Delta"

# Step 4 — confirm to user
git log --oneline -3
```

**Expected outputs**:

After `emanon genus contracts/iron-grain-alliance.md`:
```
set_k=5 oddity_s=3 index_i=2 writer=alpha@example.com snapshot=4
```

After `emanon snapshot -m "Propose iron-grain trade alliance with Delta"`:
```
[main g7h8i9j] Propose iron-grain trade alliance with Delta
 Snapshot-Count: 5
 Snapshot-Timestamp: 2026-04-14T11:30:00Z
```

**Tell the user**:
> "Contract drafted and signed at snapshot 5. Share your repo URL with delta so they can fetch and countersign. They should run: `git remote add alpha <your-repo-url>`, then `emanon merge alpha/main`, then `emanon snapshot -m 'Countersign iron-grain alliance with Alpha'`."

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| Contract file has no genus stamp | Used `cat >` instead of `emanon write` | Delete and rewrite with `emanon write` |
| Other player's merge shows `contract conflict` | They modified the contract text before merging | Resolve via `emanon negotiate` choosing "contract" (accept their version) or renegotiate terms |
| `emanon contract list` shows nothing | No contract files in `contracts/` | Verify `contracts/iron-grain-alliance.md` exists |

---

### Example 2: Countersigning a Contract Proposed by Another Player

**User says**: "Player gamma sent me a defense pact contract. I want to review it and sign if the terms look fair."

**Agent reasoning**:
> The user is the second party (countersigner). I need to fetch gamma's universe, examine the contract file, report the terms to the user for their decision, then merge and snapshot if they agree. The `emanon-contract` merge driver will auto-resolve if the file is byte-identical in both universes after the merge.

**Commands the agent should invoke**:

```bash
# Step 1 — fetch gamma's universe
git remote add gamma https://github.com/player-gamma/their-universe.git
git fetch gamma

# Step 2 — read the proposed contract
git show gamma/main:contracts/defense-pact.md

# Step 3 — report to user and wait for approval
# (Present the contract terms; don't merge until user says yes)

# If user approves — Step 4: merge to receive the contract file
emanon merge gamma/main
# The emanon-contract driver will detect the contract and auto-resolve if clean

# Step 5 — countersign by snapshotting
emanon snapshot -m "Countersign defense pact with Gamma"

# Step 6 — verify the pact is live on both sides
git log --oneline -- contracts/defense-pact.md
git diff gamma/main -- contracts/defense-pact.md
# Should show no diff (byte-identical)
```

**Expected outputs**:

After `git show gamma/main:contracts/defense-pact.md`:
```
# Mutual Defense Pact

Parties: Gamma (proposer), [Your Name] (acceptor)
Proposed: 2026-04-14

Terms:
1. Either party under attack may call the other for military support
2. Duration: indefinite until either party snapshots a dissolution notice
3. Territory: both parties' regions/ are inviolable

Signatures:
- Gamma: signed at snapshot 8
- [Your Name]: [pending countersignature]

# emanon-genus: {"set_k": 11, "oddity_s": 7, ...}
```

After `emanon merge gamma/main` (byte-identical contract auto-resolves):
```
Fetching gamma...
Running Collatz merge driver...
  contracts/defense-pact.md: contract mode — byte-identical → auto-resolved
Merge committed: k4l5m6n
```

After `git diff gamma/main -- contracts/defense-pact.md`:
```
(no output — files are identical)
```

**Failure modes and recovery**:

| Symptom | Cause | Recovery |
|---|---|---|
| `contract conflict` during merge | Gamma's contract differs from what you have | Run `emanon negotiate` → choose "contract" to accept gamma's version |
| `git diff` shows differences | You accidentally modified the contract | Reset with `git checkout gamma/main -- contracts/defense-pact.md` and snapshot |
| Contract not in `contracts/` after merge | Merge not yet committed | Check `git status` and commit if needed |
