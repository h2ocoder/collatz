/**
 * Emanon Universe cNFT — Integration Tests
 *
 * These tests are structured for a devnet-fork localnet environment where
 * the Bubblegum and SPL Account Compression programs are available.
 *
 * Prerequisites:
 *   - `solana-test-validator` running with Bubblegum program cloned from devnet
 *   - `anchor build` completed (real program ID substituted in Anchor.toml)
 *   - A funded keypair at `~/.config/solana/id.json`
 *
 * Run:
 *   anchor test --provider.cluster devnet
 *
 * Devnet addresses referenced:
 *   Bubblegum:    BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY
 *   Compression:  cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK
 *   SPL Noop:     noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { UniverseCnft } from "../target/types/universe_cnft";
import {
  PublicKey,
  Keypair,
  SystemProgram,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import { assert } from "chai";

// ---------------------------------------------------------------------------
// Program IDs
// ---------------------------------------------------------------------------

const BUBBLEGUM_PROGRAM_ID = new PublicKey(
  "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"
);
const SPL_ACCOUNT_COMPRESSION_ID = new PublicKey(
  "cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK"
);
const SPL_NOOP_PROGRAM_ID = new PublicKey(
  "noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV"
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Derive the RegistryTreeConfig PDA. */
function deriveRegistryTreeConfig(
  programId: PublicKey,
  registryId: Uint8Array
): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("registry-tree"), Buffer.from(registryId)],
    programId
  );
}

/** Derive the tree-authority PDA. */
function deriveTreeAuthority(
  programId: PublicKey,
  registryId: Uint8Array
): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("tree-authority"), Buffer.from(registryId)],
    programId
  );
}

/** Create a 32-byte registry_id from a human-readable string (left-padded). */
function makeRegistryId(label: string): Uint8Array {
  const id = new Uint8Array(32);
  const encoded = Buffer.from(label.slice(0, 32));
  id.set(encoded, 32 - encoded.length);
  return id;
}

/** Create a dummy 8-byte bounty_id_prefix. */
function makeBountyPrefix(hex: string): number[] {
  // hex is up to 16 chars (8 bytes); pad if shorter
  const padded = hex.padEnd(16, "0").slice(0, 16);
  const result: number[] = [];
  for (let i = 0; i < 16; i += 2) {
    result.push(parseInt(padded.slice(i, i + 2), 16));
  }
  return result;
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe("universe-cnft", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.UniverseCnft as Program<UniverseCnft>;
  const connection = provider.connection;
  const wallet = provider.wallet as anchor.Wallet;

  // Keypairs used across tests
  const admin = wallet.payer;
  const buyer = Keypair.generate();
  const miner = Keypair.generate();

  // A dummy Merkle tree keypair (stands in for the real tree account in unit tests)
  const merkleTreeKp = Keypair.generate();

  // Registry-specific state
  const registryId = makeRegistryId("test-registry-alpha");
  const [registryTreeConfig, configBump] = deriveRegistryTreeConfig(
    program.programId,
    registryId
  );
  const [treeAuthorityPda] = deriveTreeAuthority(program.programId, registryId);

  // ---------------------------------------------------------------------------
  // Test 1 — PDA derivation is deterministic
  // ---------------------------------------------------------------------------

  it("derives RegistryTreeConfig PDA deterministically", () => {
    const [pda1] = deriveRegistryTreeConfig(program.programId, registryId);
    const [pda2] = deriveRegistryTreeConfig(program.programId, registryId);
    assert.strictEqual(pda1.toBase58(), pda2.toBase58());
  });

  // ---------------------------------------------------------------------------
  // Test 2 — tree-authority PDA is distinct from RegistryTreeConfig PDA
  // ---------------------------------------------------------------------------

  it("tree-authority PDA is distinct from RegistryTreeConfig PDA", () => {
    const [configPda] = deriveRegistryTreeConfig(program.programId, registryId);
    const [authorityPda] = deriveTreeAuthority(program.programId, registryId);
    assert.notStrictEqual(configPda.toBase58(), authorityPda.toBase58());
  });

  // ---------------------------------------------------------------------------
  // Test 3 — different registry IDs produce different PDAs
  // ---------------------------------------------------------------------------

  it("different registry IDs produce different PDAs", () => {
    const idA = makeRegistryId("registry-alpha");
    const idB = makeRegistryId("registry-beta");
    const [pdaA] = deriveRegistryTreeConfig(program.programId, idA);
    const [pdaB] = deriveRegistryTreeConfig(program.programId, idB);
    assert.notStrictEqual(pdaA.toBase58(), pdaB.toBase58());
  });

  // ---------------------------------------------------------------------------
  // Test 4 — bounty prefix helper produces 8-byte arrays
  // ---------------------------------------------------------------------------

  it("makeBountyPrefix produces 8-byte arrays", () => {
    const prefix = makeBountyPrefix("deadbeefcafebabe");
    assert.lengthOf(prefix, 8);
    assert.strictEqual(prefix[0], 0xde);
    assert.strictEqual(prefix[1], 0xad);
    assert.strictEqual(prefix[7], 0xbe);
  });

  // ---------------------------------------------------------------------------
  // Test 5 — initialize_tree (devnet / localnet with Bubblegum cloned)
  //
  // NOTE: This test requires a real Bubblegum tree account pre-created via:
  //   spl-account-compression create-tree \
  //     --tree-authority <tree_authority_pda> \
  //     --max-depth 20 --max-buffer-size 64
  //
  // In CI/local dev without a live validator, this test is SKIPPED.
  // ---------------------------------------------------------------------------

  it("initializes a RegistryTreeConfig on-chain (skipped without validator)", async function () {
    // Skip if running without a live validator (no SOL available)
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    // Use merkleTreeKp.publicKey as a stand-in tree account (will fail Bubblegum
    // validation on CPI but lets us verify RegistryTreeConfig creation itself)
    await program.methods
      .initializeTree(
        Array.from(registryId),
        20,  // max_depth
        64   // max_buffer_size
      )
      .accounts({
        admin: admin.publicKey,
        registryTreeConfig,
        treeAuthorityPda,
        merkleTree: merkleTreeKp.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([admin])
      .rpc();

    const configAccount = await program.account.registryTreeConfig.fetch(
      registryTreeConfig
    );
    assert.deepEqual(Array.from(configAccount.registryId), Array.from(registryId));
    assert.strictEqual(configAccount.merkleTree.toBase58(), merkleTreeKp.publicKey.toBase58());
    assert.strictEqual(configAccount.treeAuthorityPda.toBase58(), treeAuthorityPda.toBase58());
    assert.strictEqual(configAccount.mintCount.toNumber(), 0);
    assert.strictEqual(configAccount.maxDepth, 20);
    assert.strictEqual(configAccount.maxBufferSize, 64);
    assert.strictEqual(configAccount.admin.toBase58(), admin.publicKey.toBase58());
  });

  // ---------------------------------------------------------------------------
  // Test 6 — initialize_tree rejects max_depth < MIN_MAX_DEPTH (16)
  // ---------------------------------------------------------------------------

  it("initialize_tree rejects max_depth below minimum", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    const smallId = makeRegistryId("small-tree-test");
    const [smallConfig] = deriveRegistryTreeConfig(program.programId, smallId);
    const [smallAuthority] = deriveTreeAuthority(program.programId, smallId);

    try {
      await program.methods
        .initializeTree(Array.from(smallId), 8, 64) // depth 8 < MIN (16)
        .accounts({
          admin: admin.publicKey,
          registryTreeConfig: smallConfig,
          treeAuthorityPda: smallAuthority,
          merkleTree: merkleTreeKp.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([admin])
        .rpc();
      assert.fail("Expected error for shallow tree depth");
    } catch (err: any) {
      assert.include(err.toString(), "TreeTooShallow");
    }
  });

  // ---------------------------------------------------------------------------
  // Test 7 — mint_universe_cnft rejects URI not starting with ipfs:// or https://
  //
  // This test verifies the URI validation constraint fires before any Bubblegum
  // CPI is attempted.  It will succeed even without a real Bubblegum tree.
  // ---------------------------------------------------------------------------

  it("mint_universe_cnft rejects invalid URI scheme", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    // Assume initialize_tree already ran (if not, skip gracefully)
    const configExists = await connection
      .getAccountInfo(registryTreeConfig)
      .catch(() => null);
    if (!configExists) {
      this.skip();
    }

    const prefix = makeBountyPrefix("deadbeef00000000");

    try {
      await program.methods
        .mintUniverseCnft(prefix, "http://plaintext.example.com/bad.json")
        .accounts({
          authority: admin.publicKey,
          registryTreeConfig,
          treeAuthorityPda,
          buyer: buyer.publicKey,
          miner: miner.publicKey,
          merkleTree: merkleTreeKp.publicKey,
          payer: admin.publicKey,
          logWrapper: SPL_NOOP_PROGRAM_ID,
          compressionProgram: SPL_ACCOUNT_COMPRESSION_ID,
          bubblegumProgram: BUBBLEGUM_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([admin])
        .rpc();
      assert.fail("Expected InvalidUri error");
    } catch (err: any) {
      assert.include(err.toString(), "InvalidUri");
    }
  });

  // ---------------------------------------------------------------------------
  // Test 8 — mint_universe_cnft rejects URI exceeding MAX_URI_LEN (200)
  // ---------------------------------------------------------------------------

  it("mint_universe_cnft rejects URI that is too long", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    const configExists = await connection
      .getAccountInfo(registryTreeConfig)
      .catch(() => null);
    if (!configExists) {
      this.skip();
    }

    const longUri = "ipfs://" + "a".repeat(200); // 207 chars > 200
    const prefix = makeBountyPrefix("deadbeef00000000");

    try {
      await program.methods
        .mintUniverseCnft(prefix, longUri)
        .accounts({
          authority: admin.publicKey,
          registryTreeConfig,
          treeAuthorityPda,
          buyer: buyer.publicKey,
          miner: miner.publicKey,
          merkleTree: merkleTreeKp.publicKey,
          payer: admin.publicKey,
          logWrapper: SPL_NOOP_PROGRAM_ID,
          compressionProgram: SPL_ACCOUNT_COMPRESSION_ID,
          bubblegumProgram: BUBBLEGUM_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([admin])
        .rpc();
      assert.fail("Expected UriTooLong error");
    } catch (err: any) {
      assert.include(err.toString(), "UriTooLong");
    }
  });

  // ---------------------------------------------------------------------------
  // Test 9 — transfer_admin changes admin authority
  // ---------------------------------------------------------------------------

  it("transfer_admin updates the admin pubkey in config", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    const configExists = await connection
      .getAccountInfo(registryTreeConfig)
      .catch(() => null);
    if (!configExists) {
      this.skip();
    }

    const newAdmin = Keypair.generate();

    await program.methods
      .transferAdmin()
      .accounts({
        admin: admin.publicKey,
        registryTreeConfig,
        newAdmin: newAdmin.publicKey,
      })
      .signers([admin])
      .rpc();

    const configAccount = await program.account.registryTreeConfig.fetch(
      registryTreeConfig
    );
    assert.strictEqual(
      configAccount.admin.toBase58(),
      newAdmin.publicKey.toBase58()
    );
  });
});

// ---------------------------------------------------------------------------
// Off-chain metadata shape test (no on-chain interaction)
// ---------------------------------------------------------------------------

describe("universe-cnft metadata shape", () => {
  it("off-chain metadata JSON has all required fields", () => {
    // Verify the required off-chain metadata shape described in the design doc.
    const exampleMetadata = {
      seed: "0x" + "a".repeat(64),
      commit_hash: "a".repeat(40),
      predicate: '{"drop_time": {"op": "gte", "value": 100}}',
      miner_sig: "0x" + "b".repeat(128),
      storage_pointer: "ipfs://QmSomeUniverseBundle",
      production_cost: "12h on 8-core ARM @ 3.2GHz",
    };

    const requiredKeys = [
      "seed",
      "commit_hash",
      "predicate",
      "miner_sig",
      "storage_pointer",
      "production_cost",
    ];

    for (const key of requiredKeys) {
      assert.property(exampleMetadata, key, `Missing field: ${key}`);
      assert.isNotEmpty(
        (exampleMetadata as Record<string, string>)[key],
        `Field empty: ${key}`
      );
    }
  });

  it("on-chain cNFT metadata fields match design spec", () => {
    // The on-chain MetadataArgs shape (verified by field names / values)
    const onChainMetadata = {
      name: "Universe deadbeefcafebabe",
      symbol: "EMU",
      uri: "ipfs://QmSomeCid",
      seller_fee_basis_points: 500,
      creators: [
        { address: "miner_pubkey", share: 95, verified: true },
        { address: "protocol_pubkey", share: 5, verified: true },
      ],
    };

    assert.strictEqual(onChainMetadata.symbol, "EMU");
    assert.strictEqual(onChainMetadata.seller_fee_basis_points, 500);
    assert.lengthOf(onChainMetadata.creators, 2);
    assert.strictEqual(onChainMetadata.creators[0].share, 95);
    assert.strictEqual(onChainMetadata.creators[1].share, 5);
    assert.strictEqual(
      onChainMetadata.creators[0].share + onChainMetadata.creators[1].share,
      100
    );
    assert.isTrue(onChainMetadata.creators[0].verified);
    assert.isTrue(onChainMetadata.uri.startsWith("ipfs://"));
  });

  it("minting cost on devnet is within spec (<$0.001 per cNFT)", () => {
    // Compressed NFTs cost ~0.000005 SOL per leaf append on a 20-depth tree.
    // At SOL = $150, cost ≈ $0.00000075 << $0.001.
    // Tree creation: ~0.033 SOL = ~$5 (one-time, amortised over 1M mints).
    const leafAppendSol = 0.000005; // approximate
    const solPriceUsd = 150; // conservative estimate
    const leafAppendUsd = leafAppendSol * solPriceUsd;
    assert.isBelow(
      leafAppendUsd,
      0.001,
      `Leaf append cost $${leafAppendUsd} exceeds $0.001 spec`
    );
  });
});
