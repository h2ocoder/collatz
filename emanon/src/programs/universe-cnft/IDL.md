# Universe cNFT Program — IDL Reference

Program ID (placeholder): `UniVrsCNFTpq9wUf3NnMo9yGLc4K5AZPrMmQ8RkXhHj`

> **After anchor build:** run `anchor keys list` and replace the placeholder in
> `Anchor.toml` and `programs/universe-cnft/src/lib.rs`.

---

## Instructions

### `initialize_tree`

Register a pre-created Bubblegum Merkle tree for a registry.

**Must be called before any `mint_universe_cnft` calls.**  The Merkle tree
account itself is created off-chain (see
[cnft-tree-management.md](../../../docs/cnft-tree-management.md)).

| Parameter       | Type      | Description                                          |
|-----------------|-----------|------------------------------------------------------|
| `registry_id`   | `[u8;32]` | SHA-256 of the registry's canonical URL              |
| `max_depth`     | `u32`     | Tree depth (min 16; recommended 20 = ~1M leaves)     |
| `max_buffer_size` | `u32`   | Concurrent changelog buffer (recommended 64)         |

**Accounts:**

| Name                  | Writable | Signer | Description                                |
|-----------------------|----------|--------|--------------------------------------------|
| `admin`               | ✓        | ✓      | Payer; becomes the initial mint authority  |
| `registryTreeConfig`  | ✓        |        | PDA `["registry-tree", registry_id]`       |
| `treeAuthorityPda`    |          |        | PDA `["tree-authority", registry_id]`      |
| `merkleTree`          |          |        | Pre-created Bubblegum tree account         |
| `systemProgram`       |          |        | `11111111111111111111111111111111`          |

**Emits:** `TreeInitialized { registry_id, merkle_tree, tree_authority_pda, max_depth, max_buffer_size }`

---

### `mint_universe_cnft`

Mint a compressed NFT certificate for a verified universe delivery.

CPIs into Metaplex Bubblegum `mint_v1`.  The tree-authority PDA signs the CPI.

| Parameter         | Type       | Description                                           |
|-------------------|------------|-------------------------------------------------------|
| `bounty_id_prefix`| `[u8;8]`   | First 8 bytes of bounty UUID (used in cNFT name)      |
| `metadata_uri`    | `String`   | IPFS/Arweave URI to off-chain metadata JSON (≤200 chars) |

**Accounts:**

| Name                  | Writable | Signer | Description                                            |
|-----------------------|----------|--------|--------------------------------------------------------|
| `authority`           |          | ✓      | Must be `registryTreeConfig.admin`                     |
| `registryTreeConfig`  | ✓        |        | PDA `["registry-tree", registry_id]`                   |
| `treeAuthorityPda`    |          |        | PDA `["tree-authority", registry_id]` — signs Bubblegum CPI |
| `buyer`               | ✓        |        | cNFT leaf owner (recipient)                            |
| `miner`               |          |        | Listed as primary creator (95% royalty share)          |
| `merkleTree`          | ✓        |        | Bubblegum tree (must match `registryTreeConfig.merkle_tree`) |
| `payer`               | ✓        | ✓      | Pays any rent/CPI fees                                 |
| `logWrapper`          |          |        | SPL Noop (`noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV`) |
| `compressionProgram`  |          |        | SPL Account Compression (`cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK`) |
| `bubblegumProgram`    |          |        | Metaplex Bubblegum (`BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY`) |
| `systemProgram`       |          |        | `11111111111111111111111111111111`                      |

**Emits:** `UniverseMinted { registry_id, merkle_tree, buyer, miner, bounty_id_prefix, mint_count }`

**cNFT metadata written to tree leaf:**

```json
{
  "name": "Universe <bounty_id_prefix_hex>",
  "symbol": "EMU",
  "uri": "<metadata_uri>",
  "seller_fee_basis_points": 500,
  "is_mutable": true,
  "creators": [
    {"address": "<miner>",          "share": 95, "verified": true},
    {"address": "<tree_authority>", "share":  5, "verified": true}
  ]
}
```

---

### `transfer_admin`

Transfer mint authority to a new pubkey (e.g., the bounty-escrow program PDA).

| Parameter | Type | Description |
|-----------|------|-------------|
| *(none)*  |      |             |

**Accounts:**

| Name                  | Writable | Signer | Description                              |
|-----------------------|----------|--------|------------------------------------------|
| `admin`               |          | ✓      | Current admin                            |
| `registryTreeConfig`  | ✓        |        | PDA `["registry-tree", registry_id]`     |
| `newAdmin`            |          |        | New admin pubkey                         |

**Emits:** `AdminTransferred { registry_id, old_admin, new_admin }`

---

## Accounts

### `RegistryTreeConfig`

PDA seeds: `["registry-tree", registry_id]` — where `registry_id` is the
SHA-256 of the registry's canonical URL.

| Field               | Type      | Size | Description                               |
|---------------------|-----------|------|-------------------------------------------|
| `registry_id`       | `[u8;32]` | 32   | SHA-256 of registry URL (PDA seed)        |
| `merkle_tree`       | `Pubkey`  | 32   | Bubblegum tree address                    |
| `tree_authority_pda`| `Pubkey`  | 32   | Tree-authority PDA address                |
| `mint_count`        | `u64`     |  8   | cNFTs minted (monotonically increasing)   |
| `max_depth`         | `u32`     |  4   | Merkle tree depth                         |
| `max_buffer_size`   | `u32`     |  4   | Concurrent changelog buffer               |
| `admin`             | `Pubkey`  | 32   | Current mint authority                    |
| `bump`              | `u8`      |  1   | RegistryTreeConfig PDA bump               |
| `tree_authority_bump` | `u8`    |  1   | Tree-authority PDA bump (cached)          |

Account size: `8 + 146 + 50 padding = 204` bytes.

---

## Events

| Event              | Fields                                                                |
|--------------------|-----------------------------------------------------------------------|
| `TreeInitialized`  | `registry_id, merkle_tree, tree_authority_pda, max_depth, max_buffer_size` |
| `UniverseMinted`   | `registry_id, merkle_tree, buyer, miner, bounty_id_prefix, mint_count` |
| `AdminTransferred` | `registry_id, old_admin, new_admin`                                   |

---

## Errors

| Code                       | Message                                                         |
|----------------------------|-----------------------------------------------------------------|
| `Overflow`                 | Arithmetic overflow                                             |
| `Unauthorized`             | Signer is not the registered admin                              |
| `TreeMismatch`             | Provided merkle_tree does not match the registered tree         |
| `UriTooLong`               | metadata_uri exceeds maximum length (200 chars)                 |
| `InvalidUri`               | metadata_uri must begin with `ipfs://` or `https://`            |
| `InvalidLogWrapper`        | log_wrapper must be the SPL Noop program                        |
| `InvalidCompressionProgram`| compression_program must be the SPL Account Compression program |
| `InvalidBubblegumProgram`  | bubblegum_program must be the Metaplex Bubblegum program        |
| `TreeTooShallow`           | max_depth must be ≥ 16 (65 536 leaves)                          |
| `InvalidBufferSize`        | max_buffer_size must be > 0                                     |

---

## External Program IDs

| Program                 | Address                                          |
|-------------------------|--------------------------------------------------|
| Metaplex Bubblegum      | `BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY` |
| SPL Account Compression | `cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK`  |
| SPL Noop                | `noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV`  |
