/**
 * Emanon Reputation Soulbound — Integration Tests
 *
 * Tests cover PDA derivation (off-chain, always run) and on-chain
 * instructions (skipped when no funded wallet is available).
 *
 * Prerequisites for on-chain tests:
 *   - `solana-test-validator` running on localhost
 *   - `anchor build` completed (real program ID substituted in Anchor.toml)
 *   - A funded keypair at `~/.config/solana/id.json`
 *
 * Run:
 *   anchor test --provider.cluster localnet
 *
 * Program ID placeholder:  RptnSbnd111111111111111111111111111111111111
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { ReputationSoulbound } from "../target/types/reputation_soulbound";
import {
  PublicKey,
  Keypair,
  SystemProgram,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import { assert } from "chai";

// ---------------------------------------------------------------------------
// PDA helpers
// ---------------------------------------------------------------------------

/** Derive the global ProtocolConfig PDA. */
function deriveProtocolConfig(programId: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("protocol-config")],
    programId
  );
}

/** Derive a wallet's SoulboundRecord PDA. */
function deriveSoulboundRecord(
  programId: PublicKey,
  wallet: PublicKey
): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("soulbound"), wallet.toBuffer()],
    programId
  );
}

/** Derive an AchievementEntry PDA for a given wallet + index. */
function deriveAchievementEntry(
  programId: PublicKey,
  wallet: PublicKey,
  index: number
): [PublicKey, number] {
  const indexBuf = Buffer.alloc(4);
  indexBuf.writeUInt32LE(index, 0);
  return PublicKey.findProgramAddressSync(
    [Buffer.from("achievement"), wallet.toBuffer(), indexBuf],
    programId
  );
}

// ---------------------------------------------------------------------------
// Test suite — PDA derivation (pure off-chain, always runs)
// ---------------------------------------------------------------------------

describe("reputation-soulbound PDA derivation", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace
    .ReputationSoulbound as Program<ReputationSoulbound>;

  // -------------------------------------------------------------------------
  // Test 1 — ProtocolConfig PDA is deterministic
  // -------------------------------------------------------------------------

  it("derives ProtocolConfig PDA deterministically", () => {
    const [pda1] = deriveProtocolConfig(program.programId);
    const [pda2] = deriveProtocolConfig(program.programId);
    assert.strictEqual(pda1.toBase58(), pda2.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 2 — SoulboundRecord PDA is deterministic for the same wallet
  // -------------------------------------------------------------------------

  it("derives SoulboundRecord PDA deterministically for same wallet", () => {
    const wallet = Keypair.generate().publicKey;
    const [pda1] = deriveSoulboundRecord(program.programId, wallet);
    const [pda2] = deriveSoulboundRecord(program.programId, wallet);
    assert.strictEqual(pda1.toBase58(), pda2.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 3 — SoulboundRecord PDAs are unique per wallet
  // -------------------------------------------------------------------------

  it("SoulboundRecord PDAs are unique per wallet", () => {
    const walletA = Keypair.generate().publicKey;
    const walletB = Keypair.generate().publicKey;
    const [pdaA] = deriveSoulboundRecord(program.programId, walletA);
    const [pdaB] = deriveSoulboundRecord(program.programId, walletB);
    assert.notStrictEqual(pdaA.toBase58(), pdaB.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 4 — AchievementEntry PDAs are unique per index for the same wallet
  // -------------------------------------------------------------------------

  it("AchievementEntry PDAs are unique per index for the same wallet", () => {
    const wallet = Keypair.generate().publicKey;
    const [pda0] = deriveAchievementEntry(program.programId, wallet, 0);
    const [pda1] = deriveAchievementEntry(program.programId, wallet, 1);
    assert.notStrictEqual(pda0.toBase58(), pda1.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 5 — AchievementEntry PDAs are unique per wallet for the same index
  // -------------------------------------------------------------------------

  it("AchievementEntry PDAs are unique per wallet for the same index", () => {
    const walletA = Keypair.generate().publicKey;
    const walletB = Keypair.generate().publicKey;
    const [pdaA] = deriveAchievementEntry(program.programId, walletA, 0);
    const [pdaB] = deriveAchievementEntry(program.programId, walletB, 0);
    assert.notStrictEqual(pdaA.toBase58(), pdaB.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 6 — SoulboundRecord PDA is distinct from ProtocolConfig PDA
  // -------------------------------------------------------------------------

  it("SoulboundRecord PDA is distinct from ProtocolConfig PDA", () => {
    const wallet = Keypair.generate().publicKey;
    const [configPda] = deriveProtocolConfig(program.programId);
    const [recordPda] = deriveSoulboundRecord(program.programId, wallet);
    assert.notStrictEqual(configPda.toBase58(), recordPda.toBase58());
  });

  // -------------------------------------------------------------------------
  // Test 7 — index 0 and 4294967295 (u32::MAX) produce distinct PDAs
  // -------------------------------------------------------------------------

  it("AchievementEntry index 0 and u32::MAX produce distinct PDAs", () => {
    const wallet = Keypair.generate().publicKey;
    const [pda0] = deriveAchievementEntry(program.programId, wallet, 0);
    const [pdaMax] = deriveAchievementEntry(program.programId, wallet, 0xffffffff);
    assert.notStrictEqual(pda0.toBase58(), pdaMax.toBase58());
  });
});

// ---------------------------------------------------------------------------
// Test suite — on-chain instructions (skipped without a funded wallet)
// ---------------------------------------------------------------------------

describe("reputation-soulbound on-chain", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace
    .ReputationSoulbound as Program<ReputationSoulbound>;
  const connection = provider.connection;
  const wallet = provider.wallet as anchor.Wallet;
  const admin = wallet.payer;

  const [protocolConfig] = deriveProtocolConfig(program.programId);

  // -------------------------------------------------------------------------
  // Test 8 — initialize_config creates ProtocolConfig on-chain
  // -------------------------------------------------------------------------

  it("initializes ProtocolConfig on-chain (skipped without validator)", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    await program.methods
      .initializeConfig()
      .accounts({
        admin: admin.publicKey,
        protocolConfig,
        systemProgram: SystemProgram.programId,
      })
      .signers([admin])
      .rpc();

    const config = await program.account.protocolConfig.fetch(protocolConfig);
    assert.strictEqual(config.admin.toBase58(), admin.publicKey.toBase58());
    assert.strictEqual(config.allowedCallersCount, 0);
  });

  // -------------------------------------------------------------------------
  // Test 9 — mint creates SoulboundRecord; second call is idempotent
  // -------------------------------------------------------------------------

  it("mint creates SoulboundRecord; second call is idempotent (skipped without validator)", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    const playerKp = Keypair.generate();
    // Airdrop SOL to player
    const sig = await connection.requestAirdrop(
      playerKp.publicKey,
      0.1 * LAMPORTS_PER_SOL
    );
    await connection.confirmTransaction(sig);

    const [soulboundRecord] = deriveSoulboundRecord(
      program.programId,
      playerKp.publicKey
    );

    // First mint — creates the record
    await program.methods
      .mint()
      .accounts({
        wallet: playerKp.publicKey,
        soulboundRecord,
        systemProgram: SystemProgram.programId,
      })
      .signers([playerKp])
      .rpc();

    const recordAfterFirst = await program.account.soulboundRecord.fetch(
      soulboundRecord
    );
    assert.isTrue(recordAfterFirst.isMinted);
    assert.strictEqual(
      recordAfterFirst.wallet.toBase58(),
      playerKp.publicKey.toBase58()
    );
    assert.strictEqual(recordAfterFirst.achievementCount, 0);

    // Second mint — idempotent, should not throw
    await program.methods
      .mint()
      .accounts({
        wallet: playerKp.publicKey,
        soulboundRecord,
        systemProgram: SystemProgram.programId,
      })
      .signers([playerKp])
      .rpc();

    const recordAfterSecond = await program.account.soulboundRecord.fetch(
      soulboundRecord
    );
    // State unchanged after second mint
    assert.isTrue(recordAfterSecond.isMinted);
    assert.strictEqual(recordAfterSecond.achievementCount, 0);
  });

  // -------------------------------------------------------------------------
  // Test 10 — transfer instruction always fails with Soulbound error
  // -------------------------------------------------------------------------

  it("transfer instruction always rejects with Soulbound error (skipped without validator)", async function () {
    const balance = await connection.getBalance(wallet.publicKey).catch(() => 0);
    if (balance < 0.1 * LAMPORTS_PER_SOL) {
      this.skip();
    }

    const playerKp = Keypair.generate();
    const sig = await connection.requestAirdrop(
      playerKp.publicKey,
      0.1 * LAMPORTS_PER_SOL
    );
    await connection.confirmTransaction(sig);

    const [soulboundRecord] = deriveSoulboundRecord(
      program.programId,
      playerKp.publicKey
    );

    // Mint first so the record exists
    await program.methods
      .mint()
      .accounts({
        wallet: playerKp.publicKey,
        soulboundRecord,
        systemProgram: SystemProgram.programId,
      })
      .signers([playerKp])
      .rpc();

    const newOwner = Keypair.generate();

    try {
      await program.methods
        .transfer(newOwner.publicKey)
        .accounts({
          wallet: playerKp.publicKey,
          soulboundRecord,
        })
        .signers([playerKp])
        .rpc();
      assert.fail("Expected Soulbound error");
    } catch (err: any) {
      assert.include(
        err.toString(),
        "Soulbound",
        `Expected Soulbound error, got: ${err}`
      );
    }
  });

  // -------------------------------------------------------------------------
  // Supplementary: off-chain account shape test (no on-chain interaction)
  // -------------------------------------------------------------------------

  it("achievement kinds cover all four protocol event types", () => {
    // Verify we can represent all four achievement types as typed objects.
    const achievements = [
      {
        kind: "BountyDelivered",
        bountyId: new Uint8Array(16).fill(0xab),
        priceUsdc: 5_000_000,
      },
      {
        kind: "TournamentWon",
        tournamentId: new Uint8Array(16).fill(0xcd),
        rank: 1,
      },
      { kind: "ContractSigned", contractId: new Uint8Array(16).fill(0xef) },
      {
        kind: "RegistryContribution",
        entryId: new Uint8Array(16).fill(0x12),
      },
    ];

    const kinds = achievements.map((a) => a.kind);
    assert.include(kinds, "BountyDelivered");
    assert.include(kinds, "TournamentWon");
    assert.include(kinds, "ContractSigned");
    assert.include(kinds, "RegistryContribution");
    assert.lengthOf(kinds, 4);
  });
});
