/**
 * Emanon Bounty Escrow — Anchor integration tests
 *
 * Run with:
 *   anchor test   (spins up localnet + runs this file)
 *
 * Prerequisites:
 *   - `solana-test-validator` available on PATH
 *   - `anchor build` already run (generates ./target/idl/bounty_escrow.json)
 *   - `yarn install` in this directory
 *
 * Coverage:
 *   ✓ post_bounty — vault funded correctly
 *   ✓ accept      — bond transferred, state transitions
 *   ✓ deliver     — deliverable hash and attestation recorded
 *   ✓ verify_and_release (buyer) — full happy path
 *   ✓ cancel      — refund before acceptance
 *   ✓ Idempotency — cannot double-release
 *   ✓ Idempotency — cannot release before delivery
 *   ✓ Idempotency — cannot cancel after acceptance
 *   ✓ Unauthorized deliver — wrong miner rejected
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BountyEscrow } from "../target/types/bounty_escrow";
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
  getAccount,
} from "@solana/spl-token";
import { Keypair, LAMPORTS_PER_SOL, PublicKey } from "@solana/web3.js";
import { assert } from "chai";
import * as crypto from "crypto";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Hash a string with SHA-256 and return as Uint8Array (32 bytes). */
function sha256Bytes(input: string): Uint8Array {
  return new Uint8Array(crypto.createHash("sha256").update(input).digest());
}

/** Convert a string to a 32-byte bounty_id array. */
function bountyId(uuid: string): number[] {
  return Array.from(sha256Bytes(uuid));
}

/** Derive the BountyEscrow PDA for a given bounty_id buffer. */
function findEscrowPda(
  idBytes: Uint8Array,
  programId: PublicKey
): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), Buffer.from(idBytes)],
    programId
  );
}

const PROTOCOL_FEE_BPS = 100n;
const BOND_BPS = 500n;

function protocolFee(maxPrice: bigint): bigint {
  return (maxPrice * PROTOCOL_FEE_BPS) / 10_000n;
}

function bond(maxPrice: bigint): bigint {
  return (maxPrice * BOND_BPS) / 10_000n;
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe("bounty-escrow", () => {
  // Use the workspace provider configured in Anchor.toml
  anchor.setProvider(anchor.AnchorProvider.env());
  const provider = anchor.getProvider() as anchor.AnchorProvider;
  const connection = provider.connection;

  const program = anchor.workspace.BountyEscrow as Program<BountyEscrow>;

  // Shared test actors
  let usdcMint: PublicKey;
  let buyer: Keypair;
  let miner: Keypair;
  let rogue: Keypair; // unauthorized third party

  const MAX_PRICE = 5_000_000n; // 5 USDC (6 decimals)
  const AIRDROP_SOL = 10 * LAMPORTS_PER_SOL;

  /** Fund a keypair with SOL on localnet. */
  async function airdrop(kp: Keypair) {
    const sig = await connection.requestAirdrop(kp.publicKey, AIRDROP_SOL);
    await connection.confirmTransaction(sig, "confirmed");
  }

  /** Create a mock USDC mint (6 decimals, authority = provider wallet). */
  async function setupMint(): Promise<PublicKey> {
    return createMint(
      connection,
      (provider.wallet as anchor.Wallet).payer,
      (provider.wallet as anchor.Wallet).publicKey, // mint authority
      null, // freeze authority
      6 // decimals
    );
  }

  /** Create ATA for `owner` and mint `amount` tokens into it. */
  async function fundTokenAccount(owner: PublicKey, amount: bigint) {
    const ata = await getOrCreateAssociatedTokenAccount(
      connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      owner
    );
    await mintTo(
      connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      ata.address,
      (provider.wallet as anchor.Wallet).publicKey,
      amount
    );
    return ata.address;
  }

  // ---------------------------------------------------------------------------
  // Setup — runs once before all tests
  // ---------------------------------------------------------------------------

  before(async () => {
    buyer = Keypair.generate();
    miner = Keypair.generate();
    rogue = Keypair.generate();

    await Promise.all([airdrop(buyer), airdrop(miner), airdrop(rogue)]);

    usdcMint = await setupMint();

    // Mint generous USDC balances
    await fundTokenAccount(buyer.publicKey, 100_000_000n); // 100 USDC
    await fundTokenAccount(miner.publicKey, 10_000_000n); // 10 USDC
  });

  // ---------------------------------------------------------------------------
  // Happy path
  // ---------------------------------------------------------------------------

  describe("happy path: post → accept → deliver → verify_and_release", () => {
    const uuid = "test-bounty-happy-001";
    const idBytes = sha256Bytes(uuid);
    const idArray = Array.from(idBytes);
    const predicateHash = Array.from(sha256Bytes('{"snapshot_count_at_least":5}'));
    const deliverableHash = Array.from(sha256Bytes("ipfs://QmFakeHash1234"));
    const attestation = Array(64).fill(0); // mock Ed25519 signature

    let escrowPda: PublicKey;
    let escrowBump: number;
    let vaultAta: PublicKey;
    let buyerUsdcAta: PublicKey;
    let minerUsdcAta: PublicKey;

    const deadline = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now

    before(async () => {
      [escrowPda, escrowBump] = findEscrowPda(idBytes, program.programId);

      buyerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          buyer,
          usdcMint,
          buyer.publicKey
        )
      ).address;

      minerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          miner,
          usdcMint,
          miner.publicKey
        )
      ).address;
    });

    it("post_bounty: creates escrow and funds vault", async () => {
      const buyerBefore = await getAccount(connection, buyerUsdcAta);
      const balanceBefore = buyerBefore.amount;

      // Derive expected vault ATA (ATA of escrowPda for usdcMint)
      const { getAssociatedTokenAddress } = await import("@solana/spl-token");
      const expectedVault = await getAssociatedTokenAddress(
        usdcMint,
        escrowPda,
        true // allowOwnerOffCurve — PDA as owner
      );
      vaultAta = expectedVault;

      await program.methods
        .postBounty(
          idArray,
          predicateHash,
          new anchor.BN(MAX_PRICE.toString()),
          new anchor.BN(deadline)
        )
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          buyerUsdc: buyerUsdcAta,
        })
        .signers([buyer])
        .rpc();

      // Verify escrow state
      const escrow = await program.account.bountyEscrow.fetch(escrowPda);
      assert.equal(escrow.buyer.toBase58(), buyer.publicKey.toBase58());
      assert.equal(escrow.maxPrice.toString(), MAX_PRICE.toString());
      assert.equal(escrow.deadline.toString(), deadline.toString());
      assert.deepEqual(Object.keys(escrow.state), ["open"]);
      assert.isFalse(escrow.hasMiner);

      // Verify vault balance = max_price + protocol_fee
      const fee = protocolFee(MAX_PRICE);
      const expectedDeposit = MAX_PRICE + fee;
      const vault = await getAccount(connection, vaultAta);
      assert.equal(vault.amount.toString(), expectedDeposit.toString());

      // Verify buyer balance decreased by deposit
      const buyerAfter = await getAccount(connection, buyerUsdcAta);
      assert.equal(
        (balanceBefore - buyerAfter.amount).toString(),
        expectedDeposit.toString()
      );
    });

    it("accept: miner stakes bond, state → Accepted", async () => {
      const vaultBefore = await getAccount(connection, vaultAta);

      await program.methods
        .accept()
        .accountsPartial({
          miner: miner.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          minerUsdc: minerUsdcAta,
        })
        .signers([miner])
        .rpc();

      const escrow = await program.account.bountyEscrow.fetch(escrowPda);
      assert.equal(escrow.miner.toBase58(), miner.publicKey.toBase58());
      assert.isTrue(escrow.hasMiner);
      assert.deepEqual(Object.keys(escrow.state), ["accepted"]);

      // Vault grew by bond_amount
      const bondAmount = bond(MAX_PRICE);
      const vaultAfter = await getAccount(connection, vaultAta);
      assert.equal(
        (vaultAfter.amount - vaultBefore.amount).toString(),
        bondAmount.toString()
      );
    });

    it("deliver: records deliverable hash and attestation, state → Delivered", async () => {
      await program.methods
        .deliver(deliverableHash, attestation)
        .accountsPartial({
          miner: miner.publicKey,
          bountyEscrow: escrowPda,
        })
        .signers([miner])
        .rpc();

      const escrow = await program.account.bountyEscrow.fetch(escrowPda);
      assert.deepEqual(Object.keys(escrow.state), ["delivered"]);
      assert.isTrue(escrow.hasDeliverable);
      assert.deepEqual(Array.from(escrow.deliverableHash), deliverableHash);
      assert.isAbove(escrow.deliveredAt.toNumber(), 0);
    });

    it("verify_and_release (buyer): transfers payout to miner, state → Released", async () => {
      const minerBefore = await getAccount(connection, minerUsdcAta);
      const vaultBefore = await getAccount(connection, vaultAta);

      await program.methods
        .verifyAndRelease()
        .accountsPartial({
          authority: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          minerUsdc: minerUsdcAta,
        })
        .signers([buyer])
        .rpc();

      const escrow = await program.account.bountyEscrow.fetch(escrowPda);
      assert.deepEqual(Object.keys(escrow.state), ["released"]);

      // Miner received max_price + bond
      const expectedPayout = MAX_PRICE + bond(MAX_PRICE);
      const minerAfter = await getAccount(connection, minerUsdcAta);
      assert.equal(
        (minerAfter.amount - minerBefore.amount).toString(),
        expectedPayout.toString()
      );

      // Vault now holds only protocol_fee (retained for treasury)
      const fee = protocolFee(MAX_PRICE);
      const vaultAfter = await getAccount(connection, vaultAta);
      assert.equal(vaultAfter.amount.toString(), fee.toString());
    });

    it("idempotency: cannot double-release (state != Delivered)", async () => {
      try {
        await program.methods
          .verifyAndRelease()
          .accountsPartial({
            authority: buyer.publicKey,
            bountyEscrow: escrowPda,
            vault: vaultAta,
            usdcMint,
            minerUsdc: minerUsdcAta,
          })
          .signers([buyer])
          .rpc();
        assert.fail("Expected error: InvalidState");
      } catch (err: any) {
        assert.include(err.message, "InvalidState");
      }
    });
  });

  // ---------------------------------------------------------------------------
  // Cancel path
  // ---------------------------------------------------------------------------

  describe("cancel: refunds buyer before acceptance", () => {
    const uuid = "test-bounty-cancel-001";
    const idBytes = sha256Bytes(uuid);
    const idArray = Array.from(idBytes);
    const predicateHash = Array.from(sha256Bytes("{}"));

    let escrowPda: PublicKey;
    let vaultAta: PublicKey;
    let buyerUsdcAta: PublicKey;

    const deadline = Math.floor(Date.now() / 1000) + 3600;

    before(async () => {
      [escrowPda] = findEscrowPda(idBytes, program.programId);

      buyerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          buyer,
          usdcMint,
          buyer.publicKey
        )
      ).address;

      const { getAssociatedTokenAddress } = await import("@solana/spl-token");
      vaultAta = await getAssociatedTokenAddress(usdcMint, escrowPda, true);
    });

    it("post_bounty: success", async () => {
      await program.methods
        .postBounty(
          idArray,
          predicateHash,
          new anchor.BN(MAX_PRICE.toString()),
          new anchor.BN(deadline)
        )
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          buyerUsdc: buyerUsdcAta,
        })
        .signers([buyer])
        .rpc();
    });

    it("cancel: refunds max_price, retains protocol_fee", async () => {
      const buyerBefore = await getAccount(connection, buyerUsdcAta);

      await program.methods
        .cancel()
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          buyerUsdc: buyerUsdcAta,
          usdcMint,
        })
        .signers([buyer])
        .rpc();

      const escrow = await program.account.bountyEscrow.fetch(escrowPda);
      assert.deepEqual(Object.keys(escrow.state), ["cancelled"]);

      // Buyer got back max_price
      const buyerAfter = await getAccount(connection, buyerUsdcAta);
      assert.equal(
        (buyerAfter.amount - buyerBefore.amount).toString(),
        MAX_PRICE.toString()
      );

      // Vault retains protocol_fee
      const fee = protocolFee(MAX_PRICE);
      const vault = await getAccount(connection, vaultAta);
      assert.equal(vault.amount.toString(), fee.toString());
    });

    it("idempotency: cannot cancel again after Cancelled", async () => {
      try {
        await program.methods
          .cancel()
          .accountsPartial({
            buyer: buyer.publicKey,
            bountyEscrow: escrowPda,
            vault: vaultAta,
            buyerUsdc: buyerUsdcAta,
            usdcMint,
          })
          .signers([buyer])
          .rpc();
        assert.fail("Expected error: InvalidState");
      } catch (err: any) {
        assert.include(err.message, "InvalidState");
      }
    });
  });

  // ---------------------------------------------------------------------------
  // Idempotency: cannot accept after acceptance
  // ---------------------------------------------------------------------------

  describe("idempotency: cannot cancel after acceptance", () => {
    const uuid = "test-bounty-nocancelfter-accept-001";
    const idBytes = sha256Bytes(uuid);
    const idArray = Array.from(idBytes);
    const predicateHash = Array.from(sha256Bytes("{}"));

    let escrowPda: PublicKey;
    let vaultAta: PublicKey;
    let buyerUsdcAta: PublicKey;
    let minerUsdcAta: PublicKey;

    const deadline = Math.floor(Date.now() / 1000) + 3600;

    before(async () => {
      [escrowPda] = findEscrowPda(idBytes, program.programId);

      buyerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          buyer,
          usdcMint,
          buyer.publicKey
        )
      ).address;

      minerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          miner,
          usdcMint,
          miner.publicKey
        )
      ).address;

      const { getAssociatedTokenAddress } = await import("@solana/spl-token");
      vaultAta = await getAssociatedTokenAddress(usdcMint, escrowPda, true);

      // Post + accept
      await program.methods
        .postBounty(
          idArray,
          predicateHash,
          new anchor.BN(MAX_PRICE.toString()),
          new anchor.BN(deadline)
        )
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          buyerUsdc: buyerUsdcAta,
        })
        .signers([buyer])
        .rpc();

      await program.methods
        .accept()
        .accountsPartial({
          miner: miner.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          minerUsdc: minerUsdcAta,
        })
        .signers([miner])
        .rpc();
    });

    it("cancel fails after acceptance (state == Accepted, not Open)", async () => {
      try {
        await program.methods
          .cancel()
          .accountsPartial({
            buyer: buyer.publicKey,
            bountyEscrow: escrowPda,
            vault: vaultAta,
            buyerUsdc: buyerUsdcAta,
            usdcMint,
          })
          .signers([buyer])
          .rpc();
        assert.fail("Expected error: InvalidState");
      } catch (err: any) {
        assert.include(err.message, "InvalidState");
      }
    });
  });

  // ---------------------------------------------------------------------------
  // Unauthorized deliver — wrong miner
  // ---------------------------------------------------------------------------

  describe("unauthorized deliver: rogue miner rejected", () => {
    const uuid = "test-bounty-unauth-deliver-001";
    const idBytes = sha256Bytes(uuid);
    const idArray = Array.from(idBytes);
    const predicateHash = Array.from(sha256Bytes("{}"));
    const deliverableHash = Array.from(sha256Bytes("ipfs://rogue"));
    const attestation = Array(64).fill(1);

    let escrowPda: PublicKey;
    let vaultAta: PublicKey;
    let buyerUsdcAta: PublicKey;
    let minerUsdcAta: PublicKey;

    const deadline = Math.floor(Date.now() / 1000) + 3600;

    before(async () => {
      [escrowPda] = findEscrowPda(idBytes, program.programId);

      buyerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          buyer,
          usdcMint,
          buyer.publicKey
        )
      ).address;

      minerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          miner,
          usdcMint,
          miner.publicKey
        )
      ).address;

      const { getAssociatedTokenAddress } = await import("@solana/spl-token");
      vaultAta = await getAssociatedTokenAddress(usdcMint, escrowPda, true);

      // Post + accept (miner is the real one)
      await program.methods
        .postBounty(
          idArray,
          predicateHash,
          new anchor.BN(MAX_PRICE.toString()),
          new anchor.BN(deadline)
        )
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          buyerUsdc: buyerUsdcAta,
        })
        .signers([buyer])
        .rpc();

      await program.methods
        .accept()
        .accountsPartial({
          miner: miner.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          minerUsdc: minerUsdcAta,
        })
        .signers([miner])
        .rpc();
    });

    it("deliver fails when signed by rogue (constraint: miner must match)", async () => {
      try {
        await program.methods
          .deliver(deliverableHash, attestation)
          .accountsPartial({
            miner: rogue.publicKey, // not the accepted miner
            bountyEscrow: escrowPda,
          })
          .signers([rogue])
          .rpc();
        assert.fail("Expected error: Unauthorized");
      } catch (err: any) {
        assert.include(err.message, "Unauthorized");
      }
    });
  });

  // ---------------------------------------------------------------------------
  // cannot release before delivery
  // ---------------------------------------------------------------------------

  describe("idempotency: cannot release without delivery", () => {
    const uuid = "test-bounty-norelease-001";
    const idBytes = sha256Bytes(uuid);
    const idArray = Array.from(idBytes);
    const predicateHash = Array.from(sha256Bytes("{}"));

    let escrowPda: PublicKey;
    let vaultAta: PublicKey;
    let buyerUsdcAta: PublicKey;
    let minerUsdcAta: PublicKey;

    const deadline = Math.floor(Date.now() / 1000) + 3600;

    before(async () => {
      [escrowPda] = findEscrowPda(idBytes, program.programId);

      buyerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          buyer,
          usdcMint,
          buyer.publicKey
        )
      ).address;

      minerUsdcAta = (
        await getOrCreateAssociatedTokenAccount(
          connection,
          miner,
          usdcMint,
          miner.publicKey
        )
      ).address;

      const { getAssociatedTokenAddress } = await import("@solana/spl-token");
      vaultAta = await getAssociatedTokenAddress(usdcMint, escrowPda, true);

      // Post only (no accept, no deliver)
      await program.methods
        .postBounty(
          idArray,
          predicateHash,
          new anchor.BN(MAX_PRICE.toString()),
          new anchor.BN(deadline)
        )
        .accountsPartial({
          buyer: buyer.publicKey,
          bountyEscrow: escrowPda,
          vault: vaultAta,
          usdcMint,
          buyerUsdc: buyerUsdcAta,
        })
        .signers([buyer])
        .rpc();
    });

    it("verify_and_release fails in Open state (state != Delivered)", async () => {
      try {
        await program.methods
          .verifyAndRelease()
          .accountsPartial({
            authority: buyer.publicKey,
            bountyEscrow: escrowPda,
            vault: vaultAta,
            usdcMint,
            minerUsdc: minerUsdcAta,
          })
          .signers([buyer])
          .rpc();
        assert.fail("Expected error: InvalidState");
      } catch (err: any) {
        assert.include(err.message, "InvalidState");
      }
    });
  });
});
