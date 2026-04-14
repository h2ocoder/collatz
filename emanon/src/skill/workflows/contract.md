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
