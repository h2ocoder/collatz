# Emanon Reputation Soulbound — IDL Reference

Program ID (placeholder): `RptnSbnd111111111111111111111111111111111111`

> After `anchor build`, run `anchor keys list` and replace the placeholder
> in `Anchor.toml` and `programs/reputation-soulbound/src/lib.rs`.

---

## Overview

The soulbound reputation NFT is a **PDA-bound on-chain record** — one per
wallet — that accumulates earned achievements across the Emanon protocol.
It cannot be transferred: the `SoulboundRecord` PDA is seeded by the wallet
pubkey, and an explicit `transfer` instruction always returns `Soulbound`.

---

## PDAs

| Account | Seeds | Description |
|---------|-------|-------------|
| `ProtocolConfig` | `["protocol-config"]` | Global config; admin + allowed callers |
| `SoulboundRecord` | `["soulbound", wallet]` | Per-wallet NFT record |
| `AchievementEntry` | `["achievement", wallet, index_u32_le]` | Single achievement |

---

## Instructions

### `initialize_config`

Create the global `ProtocolConfig`.  Called once by the admin.

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `admin` | ✓ | ✓ | Admin paying rent |
| `protocol_config` | ✓ | — | ProtocolConfig PDA (created) |
| `system_program` | — | — | System program |

---

### `add_allowed_caller(caller_authority: Pubkey)`

Add a program authority pubkey to the allowed-callers whitelist (max 8).

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `admin` | — | ✓ | Must match `protocol_config.admin` |
| `protocol_config` | ✓ | — | ProtocolConfig PDA |

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `caller_authority` | `Pubkey` | Authority PDA of the calling program |

---

### `mint`

Create the soulbound NFT record for the signing wallet.  Idempotent: returns
`Ok(())` if the record already exists.

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `wallet` | ✓ | ✓ | Wallet receiving the soulbound NFT (also PDA seed) |
| `soulbound_record` | ✓ | — | SoulboundRecord PDA (created if absent) |
| `system_program` | — | — | System program |

---

### `record_achievement(kind: AchievementKind, evidence_sig: [u8; 64])`

Append a new achievement to the wallet's record.  Only callable by a
`caller_authority` whose pubkey is in the allowed-callers whitelist.

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `caller_authority` | — | ✓ | Must be in `ProtocolConfig.allowed_callers` |
| `protocol_config` | — | — | ProtocolConfig PDA |
| `wallet` | — | — | Wallet whose record is updated |
| `soulbound_record` | ✓ | — | SoulboundRecord PDA |
| `achievement_entry` | ✓ | — | AchievementEntry PDA (created, index = current count) |
| `payer` | ✓ | ✓ | Pays AchievementEntry rent |
| `system_program` | — | — | System program |

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `kind` | `AchievementKind` | Achievement variant (see below) |
| `evidence_sig` | `[u8; 64]` | Ed25519 signature from the calling program |

---

### `read_summary`

Emit a `ReputationRead` event with the wallet's achievement count.

Off-chain clients can also read directly: `program.account.soulboundRecord.fetch(pda)`.

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `reader` | — | ✓ | Any signer |
| `soulbound_record` | — | — | SoulboundRecord PDA to read |

---

### `transfer(new_owner: Pubkey)` — **always fails**

Provided so callers receive a clear `Soulbound` error.  Non-transferability
is enforced by program design: the `SoulboundRecord` PDA is bound to the
wallet pubkey and cannot be reassigned.

**Accounts:**

| Name | Writable | Signer | Description |
|------|----------|--------|-------------|
| `wallet` | — | ✓ | Current wallet (attempting transfer) |
| `soulbound_record` | — | — | SoulboundRecord PDA |

**Always returns:** `SoulboundError::Soulbound`

---

## Achievement Kinds

```rust
pub enum AchievementKind {
    BountyDelivered { bounty_id: [u8; 16], price_usdc: u64 },
    TournamentWon   { tournament_id: [u8; 16], rank: u32  },
    ContractSigned  { contract_id: [u8; 16]               },
    RegistryContribution { entry_id: [u8; 16]             },
}
```

Borsh-encoded max size: **25 bytes** (BountyDelivered variant).

---

## Accounts

### `ProtocolConfig`  (PDA: `["protocol-config"]`)

| Field | Type | Description |
|-------|------|-------------|
| `admin` | `Pubkey` | Admin who may add callers |
| `allowed_callers` | `[Pubkey; 8]` | Whitelist of caller authority pubkeys |
| `allowed_callers_count` | `u8` | Number populated |
| `bump` | `u8` | PDA bump |

Allocated size: **350 bytes**

---

### `SoulboundRecord`  (PDA: `["soulbound", wallet]`)

| Field | Type | Description |
|-------|------|-------------|
| `wallet` | `Pubkey` | Bound wallet (set at mint; immutable) |
| `is_minted` | `bool` | True once minted; never reverted |
| `achievement_count` | `u32` | Number of achievements recorded |
| `bump` | `u8` | PDA bump |

Allocated size: **96 bytes**

---

### `AchievementEntry`  (PDA: `["achievement", wallet, index_u32_le]`)

| Field | Type | Description |
|-------|------|-------------|
| `wallet` | `Pubkey` | Wallet this achievement belongs to |
| `index` | `u32` | Sequential index (0-based) |
| `kind` | `AchievementKind` | Achievement variant |
| `evidence_sig` | `[u8; 64]` | Ed25519 attestation from caller |
| `recorded_at` | `i64` | Unix timestamp (seconds) |
| `bump` | `u8` | PDA bump |

Allocated size: **192 bytes**

---

## Errors

| Code | Name | Message |
|------|------|---------|
| 6000 | `Soulbound` | Non-transferable: soulbound NFTs cannot be transferred |
| 6001 | `Unauthorized` | Signer is not the registered admin |
| 6002 | `UnauthorizedCaller` | caller_authority is not in the whitelist |
| 6003 | `NotMinted` | SoulboundRecord has not been minted yet |
| 6004 | `WalletMismatch` | Provided wallet does not match the SoulboundRecord |
| 6005 | `CallerListFull` | allowed_callers list is at capacity (MAX=8) |
| 6006 | `CallerAlreadyRegistered` | Caller authority is already in the whitelist |
| 6007 | `Overflow` | Arithmetic overflow in achievement_count |

---

## Events

| Event | Fields | Emitted By |
|-------|--------|------------|
| `ConfigInitialized` | `admin` | `initialize_config` |
| `CallerAdded` | `caller_authority`, `index` | `add_allowed_caller` |
| `SoulboundMinted` | `wallet` | `mint` (first call) |
| `MintAttempted` | `wallet`, `was_already_minted` | `mint` |
| `AchievementRecorded` | `wallet`, `index`, `kind`, `recorded_at` | `record_achievement` |
| `ReputationRead` | `wallet`, `achievement_count` | `read_summary` |

---

## CPI Integration

To call `record_achievement` from another Emanon program (e.g. bounty-escrow):

1. Admin calls `add_allowed_caller(escrow_authority_pda)` to whitelist the PDA.
2. The escrow program invokes `record_achievement` via CPI, passing its PDA
   as `caller_authority` (signed with PDA seeds).
3. The program verifies `caller_authority.key()` is in `allowed_callers`.

```rust
// Pseudocode — CPI from bounty-escrow on successful delivery
reputation_soulbound::cpi::record_achievement(
    cpi_ctx,
    AchievementKind::BountyDelivered {
        bounty_id: bounty.id_prefix,
        price_usdc: bounty.price_usdc,
    },
    miner_evidence_sig,
)?;
```

---

## Non-Transferability Proof

The `SoulboundRecord` is non-transferable by three independent mechanisms:

1. **PDA binding:** Seeds include the wallet pubkey — the account cannot exist
   at a different wallet's PDA address.
2. **No setter:** No instruction modifies `SoulboundRecord.wallet` after `mint`.
3. **Explicit rejection:** The `transfer` instruction always returns
   `SoulboundError::Soulbound`, providing a clear error path.
