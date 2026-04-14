# cNFT Merkle Tree Management

> This document covers how to create and manage the shared Bubblegum Merkle
> tree used by the `universe-cnft` program to mint universe certificates.

## Background

Metaplex Bubblegum uses SPL Account Compression to store cNFT data in a
concurrent Merkle tree.  Each minted cNFT is a leaf in the tree — the tree
account holds only the root hash on-chain, keeping per-cNFT cost near zero.

**Cost summary for a registry tree:**

| Item                         | Cost (approximate)              |
|------------------------------|---------------------------------|
| Tree creation (20-depth)     | ~0.033 SOL (~$5 at $150/SOL)    |
| Per cNFT mint (leaf append)  | ~0.000005 SOL (~$0.00000075)    |
| Per cNFT read (DAS API)      | Free (Helius, Metaplex)         |
| Capacity (20-depth)          | 1,048,576 leaves                |

A single 20-depth tree is sufficient for ~1M universe mints.  At 10 mints/day
this covers 287 years of operation.

---

## Tree Parameters

| Parameter        | Recommended | Notes                                          |
|------------------|-------------|------------------------------------------------|
| `max_depth`      | 20          | 2^20 = 1,048,576 leaves                        |
| `max_buffer_size`| 64          | Concurrent changelog; 64 handles burst minting |
| `canopy_depth`   | 11          | Stores 2^11-1=2047 upper nodes on-chain;       |
|                  |             | reduces proof size for concurrent reads        |

For a smaller deployment (prototype/devnet), `max_depth = 16` (65,536 leaves)
reduces creation cost to ~0.008 SOL.

---

## Step-by-Step: Creating the Tree

### Prerequisites

```bash
# Install Solana CLI toolchain
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Install Metaplex Bubblegum CLI (or use @metaplex-foundation/mpl-bubblegum SDK)
npm install -g @metaplex-foundation/mpl-bubblegum

# Configure devnet wallet
solana config set --url devnet
solana airdrop 1  # Fund wallet for tree creation rent
```

### 1. Derive the tree-authority PDA

The tree authority must be the PDA from the `universe-cnft` program:

```bash
# From any JS/TS script or the emanon CLI:
PROGRAM_ID="UniVrsCNFTpq9wUf3NnMo9yGLc4K5AZPrMmQ8RkXhHj"  # replace after anchor build
REGISTRY_ID_HEX="<sha256-of-registry-url>"  # 64 hex chars = 32 bytes

# PDA derivation (pseudocode — use @solana/web3.js findProgramAddressSync):
# seeds = [b"tree-authority", bytes.fromhex(REGISTRY_ID_HEX)]
# tree_authority_pda, bump = PublicKey.findProgramAddressSync(seeds, PROGRAM_ID)
```

**Helper script** (`scripts/derive-tree-authority.ts`):

```typescript
import { PublicKey } from "@solana/web3.js";
import { createHash } from "crypto";

const PROGRAM_ID = new PublicKey("UniVrsCNFTpq9wUf3NnMo9yGLc4K5AZPrMmQ8RkXhHj");
const registryUrl = "https://registry.emanon.game/r/alpha";  // your registry URL
const registryId = createHash("sha256").update(registryUrl).digest();

const [treeAuthority, bump] = PublicKey.findProgramAddressSync(
  [Buffer.from("tree-authority"), registryId],
  PROGRAM_ID
);

console.log("Registry ID (hex):", registryId.toString("hex"));
console.log("Tree authority PDA:", treeAuthority.toBase58());
console.log("Bump:", bump);
```

### 2. Create the Merkle tree account

```bash
# Using the Bubblegum SDK (recommended):
npx ts-node scripts/create-tree.ts

# create-tree.ts (minimal example):
```

```typescript
import { createUmi } from "@metaplex-foundation/umi-bundle-defaults";
import { createAllocTreeIx } from "@metaplex-foundation/mpl-bubblegum";
import { createSignerFromKeypair, publicKey } from "@metaplex-foundation/umi";
import { Keypair, Connection, sendAndConfirmTransaction, Transaction } from "@solana/web3.js";
import * as fs from "fs";

const connection = new Connection("https://api.devnet.solana.com");
const payer = Keypair.fromSecretKey(
  Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/id.json", "utf8")))
);

// The tree keypair — save the secret key; the public key is the tree address
const treeKeypair = Keypair.generate();
console.log("Tree address:", treeKeypair.publicKey.toBase58());
fs.writeFileSync("tree-keypair.json", JSON.stringify(Array.from(treeKeypair.secretKey)));

// Tree authority = the tree-authority PDA from universe-cnft program
const TREE_AUTHORITY_PDA = new PublicKey("<your-tree-authority-pda>");

const MAX_DEPTH = 20;
const MAX_BUFFER_SIZE = 64;
const CANOPY_DEPTH = 11;

// Create the tree account (allocate space + transfer lamports)
const allocIx = await createAllocTreeIx(
  connection,
  treeKeypair.publicKey,
  payer.publicKey,
  { maxDepth: MAX_DEPTH, maxBufferSize: MAX_BUFFER_SIZE },
  CANOPY_DEPTH
);

// Create the Bubblegum tree (set tree authority)
const createTreeIx = createCreateTreeInstruction(
  {
    treeAuthority: TREE_AUTHORITY_PDA,
    merkleTree: treeKeypair.publicKey,
    payer: payer.publicKey,
    treeCreator: payer.publicKey,
    logWrapper: SPL_NOOP_PROGRAM_ID,
    compressionProgram: SPL_ACCOUNT_COMPRESSION_PROGRAM_ID,
  },
  { maxBufferSize: MAX_BUFFER_SIZE, maxDepth: MAX_DEPTH, public: false }
);

const tx = new Transaction().add(allocIx, createTreeIx);
const sig = await sendAndConfirmTransaction(connection, tx, [payer, treeKeypair]);
console.log("Tree created:", sig);
console.log("Tree address:", treeKeypair.publicKey.toBase58());
```

### 3. Register the tree with `initialize_tree`

```typescript
// Using @coral-xyz/anchor client:
await program.methods
  .initializeTree(
    Array.from(registryId),  // [u8; 32]
    20,                       // max_depth
    64                        // max_buffer_size
  )
  .accounts({
    admin: wallet.publicKey,
    registryTreeConfig,       // PDA derived by client
    treeAuthorityPda,         // PDA derived by client
    merkleTree: treeKeypair.publicKey,
    systemProgram: SystemProgram.programId,
  })
  .rpc();
```

---

## Minting a cNFT

After tree registration, mint via `mint_universe_cnft`:

```typescript
const bountyIdPrefix = Array.from(Buffer.from(bountyUuid.replace(/-/g, ""), "hex").slice(0, 8));
const metadataUri = "ipfs://<your-metadata-cid>";

await program.methods
  .mintUniverseCnft(bountyIdPrefix, metadataUri)
  .accounts({
    authority: adminWallet.publicKey,
    registryTreeConfig,
    treeAuthorityPda,
    buyer: buyerPublicKey,
    miner: minerPublicKey,
    merkleTree: merkleTreePublicKey,
    payer: adminWallet.publicKey,
    logWrapper: SPL_NOOP_PROGRAM_ID,
    compressionProgram: SPL_ACCOUNT_COMPRESSION_PROGRAM_ID,
    bubblegumProgram: BUBBLEGUM_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  })
  .rpc();
```

### Automating mints from the bounty-escrow program

Transfer admin to the bounty-escrow PDA to enable trustless on-release minting:

```typescript
// 1. Find the bounty-escrow PDA for your bounty
const [escrowPda] = PublicKey.findProgramAddressSync(
  [Buffer.from("bounty"), Buffer.from(bountyId)],
  BOUNTY_ESCROW_PROGRAM_ID
);

// 2. Transfer admin
await program.methods
  .transferAdmin()
  .accounts({
    admin: currentAdmin.publicKey,
    registryTreeConfig,
    newAdmin: escrowPda,
  })
  .rpc();

// After this, only the escrow PDA can call mint_universe_cnft.
// The escrow program calls it via CPI after verify_and_release succeeds.
```

---

## Reading cNFTs

### Helius DAS API (recommended)

```bash
# Get all cNFTs owned by a wallet
curl -X POST https://rpc-devnet.helius.xyz/?api-key=<KEY> \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getAssetsByOwner",
    "params": {
      "ownerAddress": "<buyer-pubkey>",
      "page": 1,
      "limit": 100
    }
  }'
```

### Verify a universe cNFT

```bash
# 1. Get the asset data (includes leaf_id, tree, metadata_uri)
curl -X POST https://rpc-devnet.helius.xyz/?api-key=<KEY> \
  -d '{"method": "getAsset", "params": {"id": "<asset-id>"}}'

# 2. Fetch the off-chain metadata from IPFS
curl "https://gateway.ipfs.io/ipfs/<CID>"

# 3. Clone the universe and verify
git clone <storage_pointer>
cd <universe-dir>
emanon validate --strict
# Check HEAD SHA matches metadata.commit_hash
git rev-parse HEAD

# 4. Re-run from seed to verify predicate
emanon mine --seed <metadata.seed> --predicate '<metadata.predicate>' \
  --verify-only  # dry-run mode checks existing universe, no new mining
```

---

## Tree Capacity Planning

| Use case                  | max_depth | Capacity     | Canopy depth | Creation cost |
|---------------------------|-----------|--------------|--------------|---------------|
| Prototype / devnet test   | 16        | 65,536       | 8            | ~0.008 SOL    |
| Small registry (MVP)      | 18        | 262,144      | 10           | ~0.015 SOL    |
| Production registry       | 20        | 1,048,576    | 11           | ~0.033 SOL    |
| Global scale              | 24        | 16,777,216   | 14           | ~0.55 SOL     |

When a tree is full, call `initialize_tree` with a new Merkle tree address
(mint_count on the config resets to 0; old mints remain valid in the old tree).

---

## Security Notes

1. **Tree authority is a PDA** — no private key required; all mints are signed
   via `invoke_signed` inside the program.

2. **Admin transfer** — immediately transfer admin to the bounty-escrow PDA
   after setup to prevent unilateral minting.

3. **Metadata immutability** — `is_mutable = true` is set on mint (Bubblegum
   default) to allow metadata updates for errata.  For production, consider
   `is_mutable = false` after a grace period.

4. **Off-chain metadata pinning** — use Arweave (not just IPFS) for permanent
   storage of the off-chain metadata JSON and the universe repo bundle.

5. **Royalty enforcement** — Bubblegum enforces creator royalties via the
   Metaplex Token Metadata standard; secondary marketplaces honoring the
   Programmable NFT standard will pay the 5% miner royalty automatically.
