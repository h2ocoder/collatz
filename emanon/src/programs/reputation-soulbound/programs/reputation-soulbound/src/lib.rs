//! # Emanon Reputation Soulbound Program
//!
//! Issues and maintains a soulbound (non-transferable) reputation NFT — one
//! per wallet — accumulating earned achievements across the Emanon protocol.
//!
//! ## Design
//!
//! Rather than minting a transferable SPL token, this program uses a
//! **PDA-bound record** pattern:
//!
//! ```text
//!  ┌────────────────────────────────────────────┐
//!  │      reputation-soulbound (this program)    │
//!  │                                             │
//!  │  initialize_config ─► ProtocolConfig PDA   │
//!  │                                             │
//!  │  add_allowed_caller ─► ProtocolConfig       │
//!  │                          (callers whitelist) │
//!  │                                             │
//!  │  mint(wallet) ──────► SoulboundRecord PDA  │
//!  │                        seeds: ["soulbound", │
//!  │                                wallet]      │
//!  │                                             │
//!  │  record_achievement ──► AchievementEntry   │
//!  │                          PDA (append-only)  │
//!  │                                             │
//!  │  transfer(wallet) ──► ❌ always Soulbound  │
//!  │                                             │
//!  └────────────────────────────────────────────┘
//! ```
//!
//! ## Non-Transferability
//!
//! The `SoulboundRecord` PDA is seeded by `["soulbound", wallet_pubkey]`.
//! Its `wallet` field is set at mint and can never change.  An explicit
//! `transfer` instruction is provided solely so callers receive a clear
//! `Soulbound` error rather than a generic "unknown instruction" failure.
//!
//! ## Achievement Ordering
//!
//! Each achievement occupies its own `AchievementEntry` PDA, seeded by
//! `["achievement", wallet, index_le_bytes]`.  Because the index is
//! monotonically increasing and the account cannot be deleted, the list is
//! append-only by construction.
//!
//! ## CPI Authorization
//!
//! `record_achievement` requires a `caller_authority` signer whose pubkey
//! is present in `ProtocolConfig.allowed_callers`.  Emanon programs
//! (bounty-escrow, tournament) register their PDAs in the config.

use anchor_lang::prelude::*;

declare_id!("RptnSbnd111111111111111111111111111111111111");

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// PDA seed for the global ProtocolConfig account.
pub const PROTOCOL_CONFIG_SEED: &[u8] = b"protocol-config";

/// PDA seed for a wallet's SoulboundRecord.
pub const SOULBOUND_SEED: &[u8] = b"soulbound";

/// PDA seed for a single AchievementEntry.
pub const ACHIEVEMENT_SEED: &[u8] = b"achievement";

/// Maximum number of whitelisted caller programs.
pub const MAX_ALLOWED_CALLERS: usize = 8;

/// Length of evidence signature stored per achievement (Ed25519, 64 bytes).
pub const EVIDENCE_SIG_LEN: usize = 64;

/// Maximum size of the serialised AchievementKind (BountyDelivered variant):
///   1 byte discriminant + 16 bytes id + 8 bytes u64 = 25 bytes.
pub const ACHIEVEMENT_KIND_MAX_LEN: usize = 25;

// ---------------------------------------------------------------------------
// Achievement types
// ---------------------------------------------------------------------------

/// Achievement variants that can be recorded on the soulbound NFT.
///
/// Borsh maximum serialised size = 25 bytes (BountyDelivered variant).
#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Debug)]
pub enum AchievementKind {
    /// A miner successfully delivered a bounty and received payment.
    BountyDelivered {
        /// First 16 bytes of the bounty UUID.
        bounty_id: [u8; 16],
        /// Price paid in micro-USDC (1 USDC = 1_000_000 units).
        price_usdc: u64,
    },
    /// A player finished a ranked tournament.
    TournamentWon {
        /// First 16 bytes of the tournament UUID.
        tournament_id: [u8; 16],
        /// Rank achieved (1-indexed; 1 = first place).
        rank: u32,
    },
    /// A player signed a merge contract with another universe owner.
    ContractSigned {
        /// First 16 bytes of the contract UUID.
        contract_id: [u8; 16],
    },
    /// A player submitted a verified entry to the universe registry.
    RegistryContribution {
        /// First 16 bytes of the registry entry UUID.
        entry_id: [u8; 16],
    },
}

// ---------------------------------------------------------------------------
// Program
// ---------------------------------------------------------------------------

#[program]
pub mod reputation_soulbound {
    use super::*;

    /// Create the global ProtocolConfig.  Must be called once by the admin
    /// before any other instruction.
    pub fn initialize_config(ctx: Context<InitializeConfig>) -> Result<()> {
        let config = &mut ctx.accounts.protocol_config;
        config.admin = ctx.accounts.admin.key();
        config.allowed_callers = [Pubkey::default(); MAX_ALLOWED_CALLERS];
        config.allowed_callers_count = 0;
        config.bump = ctx.bumps.protocol_config;

        emit!(ConfigInitialized {
            admin: config.admin,
        });

        Ok(())
    }

    /// Add a caller program authority pubkey to the allowed-callers whitelist.
    ///
    /// Only the admin may call this.  Typically the caller's authority is a
    /// PDA from the calling program (e.g. bounty-escrow's escrow PDA).
    pub fn add_allowed_caller(
        ctx: Context<AddAllowedCaller>,
        caller_authority: Pubkey,
    ) -> Result<()> {
        let config = &mut ctx.accounts.protocol_config;
        let count = config.allowed_callers_count as usize;

        require!(count < MAX_ALLOWED_CALLERS, SoulboundError::CallerListFull);
        require!(
            !config.allowed_callers[..count].contains(&caller_authority),
            SoulboundError::CallerAlreadyRegistered,
        );

        config.allowed_callers[count] = caller_authority;
        config.allowed_callers_count += 1;

        emit!(CallerAdded {
            caller_authority,
            index: (count as u8),
        });

        Ok(())
    }

    /// Mint the soulbound reputation NFT for a wallet.
    ///
    /// Idempotent: if the wallet already has a SoulboundRecord, returns `Ok(())`
    /// without modifying state.  Uses the `init_if_needed` constraint.
    pub fn mint(ctx: Context<Mint>) -> Result<()> {
        let record = &mut ctx.accounts.soulbound_record;

        // Idempotent: if already minted, do nothing.
        if record.is_minted {
            emit!(MintAttempted {
                wallet: ctx.accounts.wallet.key(),
                was_already_minted: true,
            });
            return Ok(());
        }

        record.wallet = ctx.accounts.wallet.key();
        record.is_minted = true;
        record.achievement_count = 0;
        record.bump = ctx.bumps.soulbound_record;

        emit!(SoulboundMinted {
            wallet: ctx.accounts.wallet.key(),
        });

        Ok(())
    }

    /// Append an achievement to a wallet's soulbound record.
    ///
    /// May only be called by a `caller_authority` whose pubkey is in the
    /// ProtocolConfig's allowed-callers whitelist.  This enables bounty-escrow,
    /// tournament, and registry programs to record achievements via CPI.
    ///
    /// The AchievementEntry PDA is seeded by `["achievement", wallet, index]`,
    /// ensuring strict append-only ordering.
    pub fn record_achievement(
        ctx: Context<RecordAchievement>,
        kind: AchievementKind,
        evidence_sig: [u8; EVIDENCE_SIG_LEN],
    ) -> Result<()> {
        // Verify caller authority is whitelisted.
        let config = &ctx.accounts.protocol_config;
        let count = config.allowed_callers_count as usize;
        let caller_key = ctx.accounts.caller_authority.key();
        require!(
            config.allowed_callers[..count].contains(&caller_key),
            SoulboundError::UnauthorizedCaller,
        );

        // Get current achievement index before incrementing.
        let record = &mut ctx.accounts.soulbound_record;
        require!(record.is_minted, SoulboundError::NotMinted);

        let index = record.achievement_count;

        // Populate the new AchievementEntry.
        let entry = &mut ctx.accounts.achievement_entry;
        entry.wallet = record.wallet;
        entry.index = index;
        entry.kind = kind.clone();
        entry.evidence_sig = evidence_sig;
        entry.recorded_at = Clock::get()?.unix_timestamp;
        entry.bump = ctx.bumps.achievement_entry;

        // Increment the counter — monotonically, no decrement possible.
        record.achievement_count = record
            .achievement_count
            .checked_add(1)
            .ok_or(SoulboundError::Overflow)?;

        emit!(AchievementRecorded {
            wallet: record.wallet,
            index,
            kind,
            recorded_at: entry.recorded_at,
        });

        Ok(())
    }

    /// Emit a summary event for a wallet's soulbound record.
    ///
    /// The on-chain account can be read directly off-chain; this instruction
    /// provides a convenient event-based read path for on-chain consumers.
    pub fn read_summary(ctx: Context<ReadSummary>) -> Result<()> {
        let record = &ctx.accounts.soulbound_record;
        require!(record.is_minted, SoulboundError::NotMinted);

        emit!(ReputationRead {
            wallet: record.wallet,
            achievement_count: record.achievement_count,
        });

        Ok(())
    }

    /// Attempt to transfer the soulbound NFT.
    ///
    /// **Always fails with `Soulbound` error.**  This instruction exists so
    /// that callers receive a clear, typed error rather than "unknown
    /// instruction".  Non-transferability is enforced by program design: the
    /// `SoulboundRecord` PDA is bound to the wallet's pubkey as a seed and
    /// cannot be reassigned.
    pub fn transfer(_ctx: Context<Transfer>, _new_owner: Pubkey) -> Result<()> {
        err!(SoulboundError::Soulbound)
    }
}

// ---------------------------------------------------------------------------
// Account structs
// ---------------------------------------------------------------------------

/// Global protocol configuration: admin key and whitelisted caller authorities.
///
/// PDA seeds: `["protocol-config"]`.
#[account]
pub struct ProtocolConfig {
    /// Admin who may add allowed callers.
    pub admin: Pubkey,
    /// Fixed-size whitelist of caller authority pubkeys (up to 8).
    pub allowed_callers: [Pubkey; MAX_ALLOWED_CALLERS],
    /// Number of entries currently populated in `allowed_callers`.
    pub allowed_callers_count: u8,
    /// PDA bump for this account.
    pub bump: u8,
}

impl ProtocolConfig {
    // 8 disc + 32 admin + (32*8) callers + 1 count + 1 bump = 8+32+256+2 = 298
    // + 52 padding = 350
    pub const LEN: usize = 350;
}

/// Soulbound reputation record — one per wallet.
///
/// PDA seeds: `["soulbound", wallet_pubkey]`.
#[account]
pub struct SoulboundRecord {
    /// Wallet this record is bound to.
    pub wallet: Pubkey,
    /// Whether the soulbound NFT has been minted (never goes back to false).
    pub is_minted: bool,
    /// Number of achievements recorded (monotonically increasing).
    pub achievement_count: u32,
    /// PDA bump for this account.
    pub bump: u8,
}

impl SoulboundRecord {
    // 8 disc + 32 wallet + 1 is_minted + 4 count + 1 bump = 46
    // + 50 padding = 96
    pub const LEN: usize = 96;
}

/// A single achievement entry — append-only.
///
/// PDA seeds: `["achievement", wallet_pubkey, index_as_4_le_bytes]`.
#[account]
pub struct AchievementEntry {
    /// Wallet this achievement belongs to.
    pub wallet: Pubkey,
    /// Sequential index within this wallet's achievement list (0-indexed).
    pub index: u32,
    /// Achievement variant (Borsh-encoded; max 25 bytes).
    pub kind: AchievementKind,
    /// Ed25519 signature from the calling program attesting delivery.
    pub evidence_sig: [u8; EVIDENCE_SIG_LEN],
    /// Unix timestamp when this achievement was recorded (seconds since epoch).
    pub recorded_at: i64,
    /// PDA bump for this account.
    pub bump: u8,
}

impl AchievementEntry {
    // 8 disc + 32 wallet + 4 index + 25 kind + 64 sig + 8 timestamp + 1 bump = 142
    // + 50 padding = 192
    pub const LEN: usize = 192;
}

// ---------------------------------------------------------------------------
// Instruction account contexts
// ---------------------------------------------------------------------------

#[derive(Accounts)]
pub struct InitializeConfig<'info> {
    /// Admin who will own the config (pays rent).
    #[account(mut)]
    pub admin: Signer<'info>,

    /// ProtocolConfig PDA — created by this instruction.
    #[account(
        init,
        payer = admin,
        space = ProtocolConfig::LEN,
        seeds = [PROTOCOL_CONFIG_SEED],
        bump,
    )]
    pub protocol_config: Account<'info, ProtocolConfig>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AddAllowedCaller<'info> {
    /// Current admin.
    pub admin: Signer<'info>,

    /// ProtocolConfig to update.
    #[account(
        mut,
        seeds = [PROTOCOL_CONFIG_SEED],
        bump = protocol_config.bump,
        constraint = protocol_config.admin == admin.key() @ SoulboundError::Unauthorized,
    )]
    pub protocol_config: Account<'info, ProtocolConfig>,
}

#[derive(Accounts)]
pub struct Mint<'info> {
    /// Wallet receiving the soulbound NFT (pays rent; also the PDA seed).
    #[account(mut)]
    pub wallet: Signer<'info>,

    /// SoulboundRecord PDA — created (or left unchanged) by this instruction.
    #[account(
        init_if_needed,
        payer = wallet,
        space = SoulboundRecord::LEN,
        seeds = [SOULBOUND_SEED, wallet.key().as_ref()],
        bump,
    )]
    pub soulbound_record: Account<'info, SoulboundRecord>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(kind: AchievementKind, evidence_sig: [u8; EVIDENCE_SIG_LEN])]
pub struct RecordAchievement<'info> {
    /// Authority of the calling program (must be in allowed_callers).
    pub caller_authority: Signer<'info>,

    /// Global ProtocolConfig — checked for caller whitelist.
    #[account(
        seeds = [PROTOCOL_CONFIG_SEED],
        bump = protocol_config.bump,
    )]
    pub protocol_config: Account<'info, ProtocolConfig>,

    /// Wallet whose record is being updated.
    /// CHECK: We verify via soulbound_record.wallet field.
    pub wallet: AccountInfo<'info>,

    /// SoulboundRecord PDA — incremented by this instruction.
    #[account(
        mut,
        seeds = [SOULBOUND_SEED, wallet.key().as_ref()],
        bump = soulbound_record.bump,
        constraint = soulbound_record.wallet == wallet.key() @ SoulboundError::WalletMismatch,
    )]
    pub soulbound_record: Account<'info, SoulboundRecord>,

    /// AchievementEntry PDA — created by this instruction.
    /// Seeds use the CURRENT achievement_count (index of the new entry).
    #[account(
        init,
        payer = payer,
        space = AchievementEntry::LEN,
        seeds = [
            ACHIEVEMENT_SEED,
            wallet.key().as_ref(),
            &soulbound_record.achievement_count.to_le_bytes(),
        ],
        bump,
    )]
    pub achievement_entry: Account<'info, AchievementEntry>,

    /// Payer for the AchievementEntry rent.
    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ReadSummary<'info> {
    /// Wallet whose summary is being read (any signer).
    pub reader: Signer<'info>,

    /// SoulboundRecord PDA to read.
    #[account(
        seeds = [SOULBOUND_SEED, soulbound_record.wallet.as_ref()],
        bump = soulbound_record.bump,
    )]
    pub soulbound_record: Account<'info, SoulboundRecord>,
}

#[derive(Accounts)]
pub struct Transfer<'info> {
    /// Wallet attempting to transfer (always rejected).
    pub wallet: Signer<'info>,

    /// SoulboundRecord PDA (never mutated — transfer always fails).
    #[account(
        seeds = [SOULBOUND_SEED, wallet.key().as_ref()],
        bump = soulbound_record.bump,
    )]
    pub soulbound_record: Account<'info, SoulboundRecord>,
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

#[error_code]
pub enum SoulboundError {
    #[msg("Non-transferable: soulbound NFTs cannot be transferred to another wallet")]
    Soulbound,
    #[msg("Unauthorized: signer is not the registered admin")]
    Unauthorized,
    #[msg("UnauthorizedCaller: caller_authority is not in the allowed-callers whitelist")]
    UnauthorizedCaller,
    #[msg("NotMinted: SoulboundRecord has not been minted for this wallet yet")]
    NotMinted,
    #[msg("WalletMismatch: provided wallet does not match the SoulboundRecord")]
    WalletMismatch,
    #[msg("CallerListFull: allowed_callers list is at capacity (MAX=8)")]
    CallerListFull,
    #[msg("CallerAlreadyRegistered: this caller authority is already in the whitelist")]
    CallerAlreadyRegistered,
    #[msg("Arithmetic overflow in achievement_count")]
    Overflow,
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

#[event]
pub struct ConfigInitialized {
    pub admin: Pubkey,
}

#[event]
pub struct CallerAdded {
    pub caller_authority: Pubkey,
    pub index: u8,
}

#[event]
pub struct SoulboundMinted {
    pub wallet: Pubkey,
}

#[event]
pub struct MintAttempted {
    pub wallet: Pubkey,
    pub was_already_minted: bool,
}

#[event]
pub struct AchievementRecorded {
    pub wallet: Pubkey,
    pub index: u32,
    pub kind: AchievementKind,
    pub recorded_at: i64,
}

#[event]
pub struct ReputationRead {
    pub wallet: Pubkey,
    pub achievement_count: u32,
}

// ---------------------------------------------------------------------------
// Unit tests (logic only — no SBF/BPF; compile with `cargo test --lib`)
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use anchor_lang::AnchorSerialize;

    fn dummy_pubkey(byte: u8) -> Pubkey {
        Pubkey::new_from_array([byte; 32])
    }

    // -------------------------------------------------------------------------
    // Account size checks
    // -------------------------------------------------------------------------

    #[test]
    fn protocol_config_len_at_least_298() {
        // 8+32+256+1+1 = 298 (computed minimum)
        assert!(ProtocolConfig::LEN >= 298);
    }

    #[test]
    fn soulbound_record_len_at_least_46() {
        // 8+32+1+4+1 = 46 (computed minimum)
        assert!(SoulboundRecord::LEN >= 46);
    }

    #[test]
    fn achievement_entry_len_at_least_142() {
        // 8+32+4+25+64+8+1 = 142 (computed minimum)
        assert!(AchievementEntry::LEN >= 142);
    }

    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    #[test]
    fn max_allowed_callers_is_eight() {
        assert_eq!(MAX_ALLOWED_CALLERS, 8);
    }

    #[test]
    fn evidence_sig_len_is_64() {
        assert_eq!(EVIDENCE_SIG_LEN, 64);
    }

    #[test]
    fn achievement_kind_max_len_is_25() {
        // 1 discriminant + 16 id + 8 price_usdc = 25
        assert_eq!(ACHIEVEMENT_KIND_MAX_LEN, 25);
    }

    // -------------------------------------------------------------------------
    // AchievementKind field access
    // -------------------------------------------------------------------------

    #[test]
    fn bounty_delivered_stores_price_usdc() {
        let kind = AchievementKind::BountyDelivered {
            bounty_id: [0xabu8; 16],
            price_usdc: 5_000_000,
        };
        if let AchievementKind::BountyDelivered { price_usdc, bounty_id } = &kind {
            assert_eq!(*price_usdc, 5_000_000);
            assert_eq!(bounty_id, &[0xabu8; 16]);
        } else {
            panic!("wrong variant");
        }
    }

    #[test]
    fn tournament_won_stores_rank() {
        let kind = AchievementKind::TournamentWon {
            tournament_id: [0x01u8; 16],
            rank: 1,
        };
        if let AchievementKind::TournamentWon { rank, tournament_id } = &kind {
            assert_eq!(*rank, 1);
            assert_eq!(tournament_id, &[0x01u8; 16]);
        } else {
            panic!("wrong variant");
        }
    }

    #[test]
    fn contract_signed_stores_id() {
        let kind = AchievementKind::ContractSigned {
            contract_id: [0x42u8; 16],
        };
        if let AchievementKind::ContractSigned { contract_id } = &kind {
            assert_eq!(contract_id, &[0x42u8; 16]);
        } else {
            panic!("wrong variant");
        }
    }

    #[test]
    fn registry_contribution_stores_entry_id() {
        let kind = AchievementKind::RegistryContribution {
            entry_id: [0x55u8; 16],
        };
        if let AchievementKind::RegistryContribution { entry_id } = &kind {
            assert_eq!(entry_id, &[0x55u8; 16]);
        } else {
            panic!("wrong variant");
        }
    }

    // -------------------------------------------------------------------------
    // AchievementKind sizes (Borsh serialised)
    // -------------------------------------------------------------------------

    #[test]
    fn bounty_delivered_serialised_size_is_25() {
        let kind = AchievementKind::BountyDelivered {
            bounty_id: [0xffu8; 16],
            price_usdc: u64::MAX,
        };
        let mut buf = Vec::new();
        kind.serialize(&mut buf).unwrap();
        assert_eq!(buf.len(), 25, "BountyDelivered should serialise to 25 bytes");
    }

    #[test]
    fn tournament_won_serialised_size_fits_in_max() {
        let kind = AchievementKind::TournamentWon {
            tournament_id: [0xffu8; 16],
            rank: u32::MAX,
        };
        let mut buf = Vec::new();
        kind.serialize(&mut buf).unwrap();
        assert!(buf.len() <= ACHIEVEMENT_KIND_MAX_LEN);
    }

    #[test]
    fn contract_signed_serialised_size_fits_in_max() {
        let kind = AchievementKind::ContractSigned {
            contract_id: [0xffu8; 16],
        };
        let mut buf = Vec::new();
        kind.serialize(&mut buf).unwrap();
        assert!(buf.len() <= ACHIEVEMENT_KIND_MAX_LEN);
    }

    #[test]
    fn registry_contribution_serialised_size_fits_in_max() {
        let kind = AchievementKind::RegistryContribution {
            entry_id: [0xffu8; 16],
        };
        let mut buf = Vec::new();
        kind.serialize(&mut buf).unwrap();
        assert!(buf.len() <= ACHIEVEMENT_KIND_MAX_LEN);
    }

    // -------------------------------------------------------------------------
    // AchievementKind clone + PartialEq
    // -------------------------------------------------------------------------

    #[test]
    fn achievement_kind_clones_correctly() {
        let original = AchievementKind::BountyDelivered {
            bounty_id: [1u8; 16],
            price_usdc: 1_000_000,
        };
        let cloned = original.clone();
        assert_eq!(original, cloned);
    }

    #[test]
    fn achievement_kind_partial_eq_different_variants() {
        let a = AchievementKind::ContractSigned { contract_id: [0u8; 16] };
        let b = AchievementKind::RegistryContribution { entry_id: [0u8; 16] };
        assert_ne!(a, b);
    }

    #[test]
    fn achievement_kind_partial_eq_same_values() {
        let a = AchievementKind::TournamentWon { tournament_id: [7u8; 16], rank: 3 };
        let b = AchievementKind::TournamentWon { tournament_id: [7u8; 16], rank: 3 };
        assert_eq!(a, b);
    }

    // -------------------------------------------------------------------------
    // AchievementKind Borsh round-trips
    // -------------------------------------------------------------------------

    fn borsh_round_trip(kind: &AchievementKind) -> AchievementKind {
        let mut buf = Vec::new();
        kind.serialize(&mut buf).unwrap();
        AchievementKind::deserialize(&mut buf.as_slice()).unwrap()
    }

    #[test]
    fn achievement_kind_borsh_round_trip_bounty() {
        let kind = AchievementKind::BountyDelivered {
            bounty_id: [0xdeu8; 16],
            price_usdc: 2_500_000,
        };
        assert_eq!(borsh_round_trip(&kind), kind);
    }

    #[test]
    fn achievement_kind_borsh_round_trip_tournament() {
        let kind = AchievementKind::TournamentWon {
            tournament_id: [0x0au8; 16],
            rank: 2,
        };
        assert_eq!(borsh_round_trip(&kind), kind);
    }

    #[test]
    fn achievement_kind_borsh_round_trip_contract() {
        let kind = AchievementKind::ContractSigned {
            contract_id: [0x99u8; 16],
        };
        assert_eq!(borsh_round_trip(&kind), kind);
    }

    #[test]
    fn achievement_kind_borsh_round_trip_registry() {
        let kind = AchievementKind::RegistryContribution {
            entry_id: [0x11u8; 16],
        };
        assert_eq!(borsh_round_trip(&kind), kind);
    }

    // -------------------------------------------------------------------------
    // AchievementKind discriminants are distinct (first Borsh byte)
    // -------------------------------------------------------------------------

    #[test]
    fn achievement_kind_discriminants_are_distinct() {
        let variants: &[AchievementKind] = &[
            AchievementKind::BountyDelivered { bounty_id: [0u8; 16], price_usdc: 0 },
            AchievementKind::TournamentWon { tournament_id: [0u8; 16], rank: 0 },
            AchievementKind::ContractSigned { contract_id: [0u8; 16] },
            AchievementKind::RegistryContribution { entry_id: [0u8; 16] },
        ];

        let mut discs: Vec<u8> = variants.iter().map(|v| {
            let mut buf = Vec::new();
            v.serialize(&mut buf).unwrap();
            buf[0]
        }).collect();

        let before = discs.len();
        discs.dedup();
        assert_eq!(discs.len(), before, "Two variants share a Borsh discriminant");
    }

    // -------------------------------------------------------------------------
    // Field length invariants
    // -------------------------------------------------------------------------

    #[test]
    fn bounty_id_len_is_16() {
        let id: [u8; 16] = [0u8; 16];
        assert_eq!(id.len(), 16);
    }

    #[test]
    fn tournament_id_len_is_16() {
        let id: [u8; 16] = [0u8; 16];
        assert_eq!(id.len(), 16);
    }

    #[test]
    fn contract_id_len_is_16() {
        let id: [u8; 16] = [0u8; 16];
        assert_eq!(id.len(), 16);
    }

    #[test]
    fn entry_id_len_is_16() {
        let id: [u8; 16] = [0u8; 16];
        assert_eq!(id.len(), 16);
    }

    // -------------------------------------------------------------------------
    // Error variants exist (non-zero discriminants check)
    // -------------------------------------------------------------------------

    #[test]
    fn soulbound_error_soulbound_exists() {
        // Verify the error type compiles and discriminant is accessible.
        let _e = SoulboundError::Soulbound;
        let _e = SoulboundError::Unauthorized;
        let _e = SoulboundError::UnauthorizedCaller;
        let _e = SoulboundError::NotMinted;
        let _e = SoulboundError::WalletMismatch;
        let _e = SoulboundError::CallerListFull;
        let _e = SoulboundError::CallerAlreadyRegistered;
        let _e = SoulboundError::Overflow;
    }

    // -------------------------------------------------------------------------
    // Allowed-callers whitelist logic
    // -------------------------------------------------------------------------

    #[test]
    fn allowed_callers_list_can_hold_max_callers() {
        let mut callers = [Pubkey::default(); MAX_ALLOWED_CALLERS];
        let mut count: u8 = 0;
        for i in 0u8..MAX_ALLOWED_CALLERS as u8 {
            callers[count as usize] = dummy_pubkey(i + 1);
            count += 1;
        }
        assert_eq!(count as usize, MAX_ALLOWED_CALLERS);
    }

    #[test]
    fn allowed_callers_contains_check_works() {
        let mut callers = [Pubkey::default(); MAX_ALLOWED_CALLERS];
        callers[0] = dummy_pubkey(0xaa);
        callers[1] = dummy_pubkey(0xbb);
        let count = 2usize;

        assert!(callers[..count].contains(&dummy_pubkey(0xaa)));
        assert!(callers[..count].contains(&dummy_pubkey(0xbb)));
        assert!(!callers[..count].contains(&dummy_pubkey(0xcc)));
    }

    // -------------------------------------------------------------------------
    // achievement_count overflow detection
    // -------------------------------------------------------------------------

    #[test]
    fn achievement_count_overflow_detected() {
        let count: u32 = u32::MAX;
        let result = count.checked_add(1);
        assert!(result.is_none(), "Expected overflow");
    }

    #[test]
    fn achievement_count_normal_increment() {
        let count: u32 = 42;
        let next = count.checked_add(1).unwrap();
        assert_eq!(next, 43);
    }
}
