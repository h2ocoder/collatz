//! # Emanon Bounty Escrow Program
//!
//! Holds USDC in a PDA-owned vault against a bounty until verifiable delivery,
//! then releases to the miner.
//!
//! ## State machine
//!
//! ```text
//!          post_bounty
//!  (none) ──────────────► Open
//!                            │
//!                    accept  │         cancel
//!                            ▼          ◄──
//!                        Accepted ────────► Cancelled
//!                            │
//!                    deliver │
//!                            ▼
//!                        Delivered
//!                            │
//!             verify_and_release (buyer │ 24h auto-accept)
//!                            ▼
//!                         Released
//! ```
//!
//! ## Verification (v1 limitation)
//!
//! On-chain verification is limited to:
//!   - Checking that the delivery has been submitted (`state == Delivered`)
//!   - Requiring the buyer's signature OR a 24-hour auto-accept window
//!
//! The `attestation` field (Ed25519 signature over `deliverable_hash`) is
//! stored for off-chain inspection but is **not verified on-chain in v1**.
//!
//! A future oracle network will re-run the universe mining from the VRF seed
//! to verify predicate satisfaction on-chain before releasing escrow.  The
//! architecture is forward-compatible: the oracle would call
//! `verify_and_release` with the oracle's keypair after validating off-chain.

use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::AssociatedToken,
    token::{self, Mint, Token, TokenAccount, Transfer},
};

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// Protocol fee on bounty post and cancellation: 1% (100 bps).
pub const PROTOCOL_FEE_BPS: u64 = 100;

/// Miner bond required at accept: 5% of max_price (500 bps).
pub const BOND_BPS: u64 = 500;

/// Auto-accept window after delivery: 24 hours in seconds.
pub const AUTO_ACCEPT_SECS: i64 = 86_400;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn fee_of(amount: u64, bps: u64) -> Result<u64> {
    amount
        .checked_mul(bps)
        .and_then(|v| v.checked_div(10_000))
        .ok_or(error!(EmanonError::Overflow))
}

// ---------------------------------------------------------------------------
// Program
// ---------------------------------------------------------------------------

#[program]
pub mod bounty_escrow {
    use super::*;

    /// Post a new bounty.
    ///
    /// The buyer deposits `max_price + protocol_fee` USDC into the vault PDA.
    /// A [`BountyEscrow`] account is created to track state.
    ///
    /// # Parameters
    /// - `bounty_id`      — SHA-256 of the off-chain bounty UUID string.
    /// - `predicate_hash` — SHA-256 of the predicate JSON constraint.
    /// - `max_price`      — Maximum payout in USDC lamports (6 decimals).
    /// - `deadline`       — Unix timestamp; acceptance must occur before this.
    pub fn post_bounty(
        ctx: Context<PostBounty>,
        bounty_id: [u8; 32],
        predicate_hash: [u8; 32],
        max_price: u64,
        deadline: i64,
    ) -> Result<()> {
        let clock = Clock::get()?;
        require!(deadline > clock.unix_timestamp, EmanonError::DeadlineInPast);
        require!(max_price > 0, EmanonError::ZeroPrice);

        let protocol_fee = fee_of(max_price, PROTOCOL_FEE_BPS)?;
        let bond_amount = fee_of(max_price, BOND_BPS)?;
        let total_deposit = max_price
            .checked_add(protocol_fee)
            .ok_or(EmanonError::Overflow)?;

        // Transfer buyer USDC → vault (max_price + protocol_fee)
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.buyer_usdc.to_account_info(),
                    to: ctx.accounts.vault.to_account_info(),
                    authority: ctx.accounts.buyer.to_account_info(),
                },
            ),
            total_deposit,
        )?;

        // Initialise escrow state
        let escrow = &mut ctx.accounts.bounty_escrow;
        escrow.bounty_id = bounty_id;
        escrow.buyer = ctx.accounts.buyer.key();
        escrow.miner = Pubkey::default();
        escrow.has_miner = false;
        escrow.usdc_mint = ctx.accounts.usdc_mint.key();
        escrow.vault_ata = ctx.accounts.vault.key();
        escrow.predicate_hash = predicate_hash;
        escrow.max_price = max_price;
        escrow.protocol_fee = protocol_fee;
        escrow.bond_amount = bond_amount;
        escrow.deadline = deadline;
        escrow.state = BountyState::Open;
        escrow.deliverable_hash = [0u8; 32];
        escrow.has_deliverable = false;
        escrow.attestation = [0u8; 64];
        escrow.delivered_at = 0;
        escrow.bump = ctx.bumps.bounty_escrow;

        emit!(BountyPosted {
            bounty_id,
            buyer: ctx.accounts.buyer.key(),
            max_price,
            deadline,
        });

        Ok(())
    }

    /// Accept a bounty.
    ///
    /// The miner stakes a bond (5% of max_price) into the vault.  Only one
    /// miner may accept; acceptance is locked once state moves to `Accepted`.
    /// Fails if the deadline has already passed.
    pub fn accept(ctx: Context<Accept>) -> Result<()> {
        let clock = Clock::get()?;
        let escrow = &mut ctx.accounts.bounty_escrow;

        require!(escrow.state == BountyState::Open, EmanonError::InvalidState);
        require!(clock.unix_timestamp < escrow.deadline, EmanonError::BountyExpired);

        let bond_amount = escrow.bond_amount;

        // Transfer miner bond → vault
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.miner_usdc.to_account_info(),
                    to: ctx.accounts.vault.to_account_info(),
                    authority: ctx.accounts.miner.to_account_info(),
                },
            ),
            bond_amount,
        )?;

        escrow.miner = ctx.accounts.miner.key();
        escrow.has_miner = true;
        escrow.state = BountyState::Accepted;

        emit!(BountyAccepted {
            bounty_id: escrow.bounty_id,
            miner: ctx.accounts.miner.key(),
        });

        Ok(())
    }

    /// Submit a delivered universe.
    ///
    /// Records the SHA-256 of the git bundle and the miner's Ed25519 attestation.
    /// Only the accepted miner may call this instruction.
    ///
    /// # v1 limitation
    /// The attestation is stored but **not verified on-chain**.  A future oracle
    /// upgrade will verify predicate satisfaction before releasing escrow.
    pub fn deliver(
        ctx: Context<Deliver>,
        deliverable_hash: [u8; 32],
        attestation: [u8; 64],
    ) -> Result<()> {
        let clock = Clock::get()?;
        let escrow = &mut ctx.accounts.bounty_escrow;

        require!(
            escrow.state == BountyState::Accepted,
            EmanonError::InvalidState
        );

        escrow.deliverable_hash = deliverable_hash;
        escrow.has_deliverable = true;
        escrow.attestation = attestation;
        escrow.delivered_at = clock.unix_timestamp;
        escrow.state = BountyState::Delivered;

        emit!(BountyDelivered {
            bounty_id: escrow.bounty_id,
            miner: ctx.accounts.miner.key(),
            deliverable_hash,
        });

        Ok(())
    }

    /// Release escrow to the miner after verified delivery.
    ///
    /// Two release paths:
    /// 1. **Buyer sign-off** — buyer (or designated authority) signs at any time
    ///    after `deliver`.
    /// 2. **Auto-accept** — anyone may call after 24 hours have elapsed since
    ///    delivery (trustless fallback).
    ///
    /// Payout: `max_price + bond_amount` → miner's USDC ATA.
    /// The `protocol_fee` remains in the vault and is swept by the protocol
    /// treasury in a separate instruction (not in scope for v1).
    ///
    /// Idempotency: fails unless `state == Delivered`.
    pub fn verify_and_release(ctx: Context<VerifyAndRelease>) -> Result<()> {
        let clock = Clock::get()?;
        let escrow = &ctx.accounts.bounty_escrow;

        require!(
            escrow.state == BountyState::Delivered,
            EmanonError::InvalidState
        );
        require!(escrow.has_miner, EmanonError::NoMiner);

        let is_buyer = ctx.accounts.authority.key() == escrow.buyer;
        let auto_accept = clock
            .unix_timestamp
            .saturating_sub(escrow.delivered_at)
            >= AUTO_ACCEPT_SECS;
        require!(is_buyer || auto_accept, EmanonError::Unauthorized);

        // Snapshot values before mutable borrow
        let bounty_id = escrow.bounty_id;
        let bump = escrow.bump;
        let miner = escrow.miner;
        let max_price = escrow.max_price;
        let bond_amount = escrow.bond_amount;

        // miner receives max_price + their bond back
        let payout = max_price
            .checked_add(bond_amount)
            .ok_or(EmanonError::Overflow)?;

        // BountyEscrow PDA signs for the vault ATA transfer
        let signer_seeds: &[&[&[u8]]] = &[&[b"bounty", bounty_id.as_ref(), &[bump]]];

        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.vault.to_account_info(),
                    to: ctx.accounts.miner_usdc.to_account_info(),
                    authority: ctx.accounts.bounty_escrow.to_account_info(),
                },
                signer_seeds,
            ),
            payout,
        )?;

        // Transition state — must happen after transfer to prevent re-entrancy
        let escrow = &mut ctx.accounts.bounty_escrow;
        escrow.state = BountyState::Released;

        emit!(BountyReleased {
            bounty_id,
            miner,
            amount: payout,
        });

        Ok(())
    }

    /// Cancel a bounty before any miner accepts.
    ///
    /// Refunds `max_price` to the buyer.  The `protocol_fee` is retained as a
    /// cancellation fee (remains in vault for treasury sweep).
    ///
    /// Idempotency: fails unless `state == Open`.
    pub fn cancel(ctx: Context<Cancel>) -> Result<()> {
        let escrow = &ctx.accounts.bounty_escrow;

        require!(escrow.state == BountyState::Open, EmanonError::InvalidState);

        let bounty_id = escrow.bounty_id;
        let bump = escrow.bump;
        let max_price = escrow.max_price;

        // BountyEscrow PDA signs for vault ATA transfer
        let signer_seeds: &[&[&[u8]]] = &[&[b"bounty", bounty_id.as_ref(), &[bump]]];

        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.vault.to_account_info(),
                    to: ctx.accounts.buyer_usdc.to_account_info(),
                    authority: ctx.accounts.bounty_escrow.to_account_info(),
                },
                signer_seeds,
            ),
            max_price,
        )?;

        let escrow = &mut ctx.accounts.bounty_escrow;
        escrow.state = BountyState::Cancelled;

        emit!(BountyCancelled {
            bounty_id,
            buyer: ctx.accounts.buyer.key(),
        });

        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Account structs
// ---------------------------------------------------------------------------

/// On-chain state for a single bounty escrow.
///
/// PDA seeds: `["bounty", bounty_id]`.
/// Vault ATA: associated token account of this PDA for `usdc_mint`.
#[account]
pub struct BountyEscrow {
    /// SHA-256 of the off-chain bounty UUID string (used as PDA seed).
    pub bounty_id: [u8; 32],
    /// Pubkey of the buyer who posted the bounty.
    pub buyer: Pubkey,
    /// Pubkey of the accepted miner (`Pubkey::default()` until accepted).
    pub miner: Pubkey,
    /// True after a miner has accepted.
    pub has_miner: bool,
    /// USDC mint address (devnet: Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB).
    pub usdc_mint: Pubkey,
    /// Address of the vault ATA (ATA of this PDA for `usdc_mint`).
    pub vault_ata: Pubkey,
    /// SHA-256 of the predicate JSON constraint the universe must satisfy.
    pub predicate_hash: [u8; 32],
    /// Maximum payout in USDC lamports (USDC has 6 decimals).
    pub max_price: u64,
    /// Protocol fee (1% of max_price) deposited alongside max_price.
    pub protocol_fee: u64,
    /// Miner bond amount (5% of max_price) required at acceptance.
    pub bond_amount: u64,
    /// Unix timestamp deadline for acceptance.
    pub deadline: i64,
    /// Current state-machine state.
    pub state: BountyState,
    /// SHA-256 of the delivered git bundle (`[0u8;32]` until delivered).
    pub deliverable_hash: [u8; 32],
    /// True after the miner has submitted a deliverable.
    pub has_deliverable: bool,
    /// Ed25519 signature from miner over `deliverable_hash` (stored, not verified on-chain in v1).
    pub attestation: [u8; 64],
    /// Unix timestamp when the deliverable was submitted.
    pub delivered_at: i64,
    /// BountyEscrow PDA bump seed.
    pub bump: u8,
}

impl BountyEscrow {
    // 8 disc + 32+32+32+1+32+32+32+8+8+8+8+1+32+1+64+8+1 = 8+342 = 350
    // Add 50 bytes of forward-compatibility padding → 400.
    pub const LEN: usize = 400;
}

/// State machine for a bounty escrow.
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum BountyState {
    /// Bounty posted; awaiting miner acceptance.
    Open,
    /// Miner has accepted and staked their bond.
    Accepted,
    /// Miner has submitted a deliverable; awaiting buyer release.
    Delivered,
    /// Escrow released to miner.
    Released,
    /// Buyer cancelled before any miner accepted.
    Cancelled,
}

impl Default for BountyState {
    fn default() -> Self {
        BountyState::Open
    }
}

// ---------------------------------------------------------------------------
// Instruction account contexts
// ---------------------------------------------------------------------------

#[derive(Accounts)]
#[instruction(bounty_id: [u8; 32])]
pub struct PostBounty<'info> {
    /// Buyer — pays rent and deposits USDC.
    #[account(mut)]
    pub buyer: Signer<'info>,

    /// BountyEscrow PDA created by this instruction.
    #[account(
        init,
        payer = buyer,
        space = BountyEscrow::LEN,
        seeds = [b"bounty", bounty_id.as_ref()],
        bump,
    )]
    pub bounty_escrow: Account<'info, BountyEscrow>,

    /// Vault: ATA of the BountyEscrow PDA for `usdc_mint`.
    /// Created by this instruction; owned (authority) by `bounty_escrow`.
    #[account(
        init,
        payer = buyer,
        associated_token::mint = usdc_mint,
        associated_token::authority = bounty_escrow,
    )]
    pub vault: Account<'info, TokenAccount>,

    /// USDC mint (mainnet: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v,
    ///           devnet:  Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB).
    pub usdc_mint: Account<'info, Mint>,

    /// Buyer's USDC ATA (must hold ≥ max_price + protocol_fee).
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyer,
    )]
    pub buyer_usdc: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Accept<'info> {
    /// Miner — stakes the bond.
    #[account(mut)]
    pub miner: Signer<'info>,

    /// BountyEscrow state account.
    #[account(
        mut,
        seeds = [b"bounty", bounty_escrow.bounty_id.as_ref()],
        bump = bounty_escrow.bump,
    )]
    pub bounty_escrow: Account<'info, BountyEscrow>,

    /// Vault — verified against stored `vault_ata`.
    #[account(
        mut,
        constraint = vault.key() == bounty_escrow.vault_ata @ EmanonError::InvalidMint,
    )]
    pub vault: Account<'info, TokenAccount>,

    /// USDC mint — verified against stored `usdc_mint`.
    #[account(
        constraint = usdc_mint.key() == bounty_escrow.usdc_mint @ EmanonError::InvalidMint,
    )]
    pub usdc_mint: Account<'info, Mint>,

    /// Miner's USDC ATA (must hold ≥ bond_amount).
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = miner,
    )]
    pub miner_usdc: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Deliver<'info> {
    /// Miner — must be the accepted miner recorded in the escrow.
    pub miner: Signer<'info>,

    /// BountyEscrow — verified that `miner` matches the accepted miner.
    #[account(
        mut,
        seeds = [b"bounty", bounty_escrow.bounty_id.as_ref()],
        bump = bounty_escrow.bump,
        constraint = bounty_escrow.has_miner && bounty_escrow.miner == miner.key()
            @ EmanonError::Unauthorized,
    )]
    pub bounty_escrow: Account<'info, BountyEscrow>,
}

#[derive(Accounts)]
pub struct VerifyAndRelease<'info> {
    /// Signer releasing the escrow.
    ///
    /// Must be either:
    /// - The buyer (immediate release), or
    /// - Any signer after `AUTO_ACCEPT_SECS` have elapsed (trustless fallback).
    pub authority: Signer<'info>,

    /// BountyEscrow state account.
    #[account(
        mut,
        seeds = [b"bounty", bounty_escrow.bounty_id.as_ref()],
        bump = bounty_escrow.bump,
    )]
    pub bounty_escrow: Account<'info, BountyEscrow>,

    /// Vault — verified against stored `vault_ata`.
    #[account(
        mut,
        constraint = vault.key() == bounty_escrow.vault_ata @ EmanonError::InvalidMint,
    )]
    pub vault: Account<'info, TokenAccount>,

    /// USDC mint — for ATA derivation of `miner_usdc`.
    #[account(
        constraint = usdc_mint.key() == bounty_escrow.usdc_mint @ EmanonError::InvalidMint,
    )]
    pub usdc_mint: Account<'info, Mint>,

    /// Miner's USDC ATA — receives `max_price + bond_amount`.
    /// Owner is verified against `bounty_escrow.miner`.
    #[account(
        mut,
        token::mint = usdc_mint,
        constraint = miner_usdc.owner == bounty_escrow.miner @ EmanonError::Unauthorized,
    )]
    pub miner_usdc: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Cancel<'info> {
    /// Buyer — must match `bounty_escrow.buyer`.
    pub buyer: Signer<'info>,

    /// BountyEscrow — verified that buyer matches.
    #[account(
        mut,
        seeds = [b"bounty", bounty_escrow.bounty_id.as_ref()],
        bump = bounty_escrow.bump,
        constraint = bounty_escrow.buyer == buyer.key() @ EmanonError::Unauthorized,
    )]
    pub bounty_escrow: Account<'info, BountyEscrow>,

    /// Vault — verified against stored `vault_ata`.
    #[account(
        mut,
        constraint = vault.key() == bounty_escrow.vault_ata @ EmanonError::InvalidMint,
    )]
    pub vault: Account<'info, TokenAccount>,

    /// Buyer's USDC ATA — receives the `max_price` refund.
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyer,
    )]
    pub buyer_usdc: Account<'info, TokenAccount>,

    /// USDC mint — for ATA derivation.
    #[account(
        constraint = usdc_mint.key() == bounty_escrow.usdc_mint @ EmanonError::InvalidMint,
    )]
    pub usdc_mint: Account<'info, Mint>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

#[error_code]
pub enum EmanonError {
    #[msg("Deadline must be in the future")]
    DeadlineInPast,
    #[msg("max_price must be greater than zero")]
    ZeroPrice,
    #[msg("Arithmetic overflow")]
    Overflow,
    #[msg("Invalid state transition for this instruction")]
    InvalidState,
    #[msg("Bounty deadline has already passed")]
    BountyExpired,
    #[msg("Unauthorized: wrong signer or auto-accept window not yet elapsed")]
    Unauthorized,
    #[msg("No miner assigned to this bounty")]
    NoMiner,
    #[msg("Provided mint or vault does not match escrow record")]
    InvalidMint,
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

#[event]
pub struct BountyPosted {
    pub bounty_id: [u8; 32],
    pub buyer: Pubkey,
    pub max_price: u64,
    pub deadline: i64,
}

#[event]
pub struct BountyAccepted {
    pub bounty_id: [u8; 32],
    pub miner: Pubkey,
}

#[event]
pub struct BountyDelivered {
    pub bounty_id: [u8; 32],
    pub miner: Pubkey,
    pub deliverable_hash: [u8; 32],
}

#[event]
pub struct BountyReleased {
    pub bounty_id: [u8; 32],
    pub miner: Pubkey,
    pub amount: u64,
}

#[event]
pub struct BountyCancelled {
    pub bounty_id: [u8; 32],
    pub buyer: Pubkey,
}

// ---------------------------------------------------------------------------
// Unit tests (logic only — no SBF/BPF; compile with `cargo test --lib`)
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fee_of_1_pct() {
        // 1 USDC (1_000_000 lamports) * 100 bps / 10000 = 10_000
        assert_eq!(fee_of(1_000_000, 100).unwrap(), 10_000);
    }

    #[test]
    fn fee_of_5_pct_bond() {
        // 10 USDC * 500 bps / 10000 = 500_000 (0.5 USDC)
        assert_eq!(fee_of(10_000_000, 500).unwrap(), 500_000);
    }

    #[test]
    fn fee_of_zero_amount() {
        assert_eq!(fee_of(0, 100).unwrap(), 0);
    }

    #[test]
    fn fee_of_overflow_returns_err() {
        // u64::MAX * 100 overflows
        assert!(fee_of(u64::MAX, 100).is_err());
    }

    #[test]
    fn bounty_state_default_is_open() {
        assert_eq!(BountyState::default(), BountyState::Open);
    }

    #[test]
    fn bounty_escrow_len_at_least_350() {
        // Calculated minimum is 350; our constant must be >= that.
        assert!(BountyEscrow::LEN >= 350);
    }

    #[test]
    fn auto_accept_secs_is_24h() {
        assert_eq!(AUTO_ACCEPT_SECS, 86_400);
    }

    #[test]
    fn auto_accept_elapsed_math() {
        let delivered_at: i64 = 1_700_000_000;
        let now = delivered_at + AUTO_ACCEPT_SECS;
        let elapsed = now.saturating_sub(delivered_at);
        assert!(elapsed >= AUTO_ACCEPT_SECS);
    }

    #[test]
    fn auto_accept_not_elapsed() {
        let delivered_at: i64 = 1_700_000_000;
        let now = delivered_at + AUTO_ACCEPT_SECS - 1;
        let elapsed = now.saturating_sub(delivered_at);
        assert!(elapsed < AUTO_ACCEPT_SECS);
    }

    #[test]
    fn total_deposit_math() {
        let max_price: u64 = 5_000_000; // 5 USDC
        let protocol_fee = fee_of(max_price, PROTOCOL_FEE_BPS).unwrap(); // 50_000 (0.05 USDC)
        let total = max_price.checked_add(protocol_fee).unwrap(); // 5_050_000
        assert_eq!(protocol_fee, 50_000);
        assert_eq!(total, 5_050_000);
    }

    #[test]
    fn payout_math() {
        let max_price: u64 = 5_000_000;
        let bond = fee_of(max_price, BOND_BPS).unwrap(); // 250_000 (0.25 USDC)
        let payout = max_price.checked_add(bond).unwrap(); // 5_250_000
        assert_eq!(bond, 250_000);
        assert_eq!(payout, 5_250_000);
    }

    #[test]
    fn cancel_refund_math() {
        // Cancel refunds max_price; protocol_fee stays as cancellation fee.
        let max_price: u64 = 3_000_000;
        let protocol_fee = fee_of(max_price, PROTOCOL_FEE_BPS).unwrap(); // 30_000
        let deposited = max_price + protocol_fee; // 3_030_000
        let refund = max_price; // 3_000_000
        let retained = deposited - refund; // 30_000 = protocol_fee
        assert_eq!(retained, protocol_fee);
    }
}
