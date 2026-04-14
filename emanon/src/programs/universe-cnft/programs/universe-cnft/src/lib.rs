//! # Emanon Universe cNFT Program
//!
//! Mints compressed NFTs (cNFTs) via Metaplex Bubblegum to certify mined
//! universes as on-chain assets.  Each minted cNFT represents a
//! *certificate of computation* — proof that a universe was produced from a
//! verifiable random seed, satisfies a bounty predicate, and was delivered
//! by a specific miner.
//!
//! ## Architecture
//!
//! ```text
//!  ┌─────────────────────────────────────────┐
//!  │        universe-cnft (this program)      │
//!  │                                          │
//!  │  initialize_tree ─► RegistryTreeConfig   │
//!  │                          │               │
//!  │  mint_universe_cnft      │               │
//!  │        │                 │               │
//!  │        ▼                 ▼               │
//!  │   CPI → mpl-bubblegum (BGUMAp9Gq...)    │
//!  │        │                                 │
//!  │        ▼                                 │
//!  │   cNFT leaf in shared Merkle tree        │
//!  └─────────────────────────────────────────┘
//! ```
//!
//! ## cNFT Metadata Structure
//!
//! On-chain (via Bubblegum leaf):
//! ```json
//! {
//!   "name": "Universe <bounty-id-prefix>",
//!   "symbol": "EMU",
//!   "uri": "ipfs://<metadata-json-cid>",
//!   "creators": [
//!     {"address": "<miner>",    "share": 95, "verified": true},
//!     {"address": "<protocol>", "share":  5, "verified": true}
//!   ],
//!   "seller_fee_basis_points": 500
//! }
//! ```
//!
//! Off-chain (at the IPFS URI):
//! ```json
//! {
//!   "seed": "<vrf-seed-hex>",
//!   "commit_hash": "<git-head-sha>",
//!   "predicate": "<bounty-predicate-json>",
//!   "miner_sig": "<ed25519-sig-hex>",
//!   "storage_pointer": "<ipfs-or-arweave-url>",
//!   "production_cost": "<compute-attestation>"
//! }
//! ```
//!
//! ## Merkle Tree Management
//!
//! A single shared Bubblegum tree is used per registry.  The tree is created
//! off-chain using the `spl-account-compression` CLI (or SDK) and then
//! registered via `initialize_tree`.  The tree authority is a protocol PDA
//! (`["tree-authority", registry_id]`), which signs all mint CPIs.
//!
//! See `emanon/docs/cnft-tree-management.md` for tree creation instructions.

use anchor_lang::prelude::*;
use anchor_lang::solana_program;

declare_id!("UniVrsCNFTpq9wUf3NnMo9yGLc4K5AZPrMmQ8RkXhHj");

// ---------------------------------------------------------------------------
// External program IDs
// ---------------------------------------------------------------------------

/// Metaplex Bubblegum program (devnet + mainnet).
pub mod bubblegum {
    use anchor_lang::prelude::*;
    declare_id!("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY");
}

/// SPL Account Compression program.
pub mod spl_account_compression {
    use anchor_lang::prelude::*;
    declare_id!("cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK");
}

/// SPL Noop program (required by Bubblegum for event logging).
pub mod spl_noop {
    use anchor_lang::prelude::*;
    declare_id!("noopb9bkMVfRPU8AsbpTUg8AQkHtKwMYZiFUjNRtMmV");
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// PDA seed for the tree-authority account.
pub const TREE_AUTHORITY_SEED: &[u8] = b"tree-authority";

/// PDA seed for the RegistryTreeConfig account.
pub const REGISTRY_TREE_SEED: &[u8] = b"registry-tree";

/// cNFT symbol for all Emanon universes.
pub const EMU_SYMBOL: &str = "EMU";

/// Seller fee in basis points (5%).
pub const SELLER_FEE_BPS: u16 = 500;

/// Protocol creator share (5%).
pub const PROTOCOL_CREATOR_SHARE: u8 = 5;

/// Miner creator share (95%).
pub const MINER_CREATOR_SHARE: u8 = 95;

/// Maximum length of the IPFS URI (ipfs://<CIDv1> ≈ 100 chars, padded to 200).
pub const MAX_URI_LEN: usize = 200;

/// Maximum length of the cNFT name ("Universe " + 16 hex chars = 25 chars).
pub const MAX_NAME_LEN: usize = 32;

/// Minimum Merkle tree max_depth supported (16 = 65 536 leaves; enough for M8).
pub const MIN_MAX_DEPTH: u32 = 16;

/// Recommended Merkle tree max_depth (~1M universes).
pub const RECOMMENDED_MAX_DEPTH: u32 = 20;

/// Recommended concurrent change log buffer size.
pub const RECOMMENDED_MAX_BUFFER_SIZE: u32 = 64;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Format the cNFT name from the first 8 bytes of the bounty_id.
///
/// Result: `"Universe <16-hex-chars>"` — always ≤ 25 bytes.
pub fn format_universe_name(bounty_id_prefix: &[u8; 8]) -> String {
    let hex: String = bounty_id_prefix
        .iter()
        .map(|b| format!("{:02x}", b))
        .collect();
    format!("Universe {}", hex)
}

/// Serialize a `MetadataArgs`-equivalent struct into the byte layout expected
/// by the Bubblegum `mint_v1` instruction discriminator.
///
/// Bubblegum instruction discriminant (sha256("global:mint_v1")[..8]):
/// `[145, 98, 192, 118, 184, 147, 118, 104]`
///
/// The full layout is:
///   8 bytes  — discriminant
///   MetadataArgs (Borsh-serialized)
///
/// `MetadataArgs` Borsh layout (in order):
///   String  name               (4-byte len prefix + UTF-8 bytes)
///   String  symbol             (4-byte len prefix + UTF-8 bytes)
///   String  uri                (4-byte len prefix + UTF-8 bytes)
///   u16     seller_fee_basis_points
///   bool    primary_sale_happened
///   bool    is_mutable
///   Option<u8>  edition_nonce  (0 = None, 1 + value = Some)
///   Option<u8>  token_standard (0 = None, 1 + value = Some — 0 = NonFungible)
///   Option<Collection>  collection (0 = None)
///   Option<Uses>  uses         (0 = None)
///   u8      token_program_version (0 = Original)
///   Vec<Creator>  creators     (4-byte len prefix, then Creator structs)
///
/// `Creator` Borsh layout:
///   [u8; 32] address
///   bool     verified
///   u8       share
pub fn build_mint_v1_data(
    name: &str,
    symbol: &str,
    uri: &str,
    seller_fee_basis_points: u16,
    miner: &Pubkey,
    protocol: &Pubkey,
) -> Vec<u8> {
    // Bubblegum mint_v1 discriminant
    let discriminant: [u8; 8] = [145, 98, 192, 118, 184, 147, 118, 104];

    let mut data = discriminant.to_vec();

    // Helper: Borsh-encode a String
    let encode_str = |s: &str| -> Vec<u8> {
        let bytes = s.as_bytes();
        let mut v = (bytes.len() as u32).to_le_bytes().to_vec();
        v.extend_from_slice(bytes);
        v
    };

    data.extend(encode_str(name));
    data.extend(encode_str(symbol));
    data.extend(encode_str(uri));
    data.extend(seller_fee_basis_points.to_le_bytes());
    data.push(0); // primary_sale_happened = false
    data.push(1); // is_mutable = true

    // edition_nonce: None
    data.push(0);
    // token_standard: Some(NonFungible = 0)
    data.push(1);
    data.push(0);
    // collection: None
    data.push(0);
    // uses: None
    data.push(0);
    // token_program_version: Original = 0
    data.push(0);

    // creators: Vec<Creator> (2 elements)
    data.extend(2u32.to_le_bytes()); // length prefix

    // Creator 0: miner (share 95, verified)
    data.extend_from_slice(miner.as_ref());
    data.push(1); // verified = true
    data.push(MINER_CREATOR_SHARE);

    // Creator 1: protocol PDA (share 5, verified)
    data.extend_from_slice(protocol.as_ref());
    data.push(1); // verified = true
    data.push(PROTOCOL_CREATOR_SHARE);

    data
}

// ---------------------------------------------------------------------------
// Program
// ---------------------------------------------------------------------------

#[program]
pub mod universe_cnft {
    use super::*;

    /// Register a pre-created Bubblegum Merkle tree for a registry.
    ///
    /// The Merkle tree account must be created beforehand using the
    /// `spl-account-compression` CLI or SDK, with tree authority set to the
    /// PDA derived by `["tree-authority", registry_id]`.
    ///
    /// This instruction records the tree address and configuration in a
    /// [`RegistryTreeConfig`] PDA so that `mint_universe_cnft` can find it.
    ///
    /// # Parameters
    /// - `registry_id`      — SHA-256 of the registry's canonical URL.
    /// - `max_depth`        — Merkle tree depth (20 → ~1M leaves, 32 → 4B).
    /// - `max_buffer_size`  — Concurrent change log buffer (64 is standard).
    pub fn initialize_tree(
        ctx: Context<InitializeTree>,
        registry_id: [u8; 32],
        max_depth: u32,
        max_buffer_size: u32,
    ) -> Result<()> {
        require!(max_depth >= MIN_MAX_DEPTH, CnftError::TreeTooShallow);
        require!(max_buffer_size > 0, CnftError::InvalidBufferSize);

        let config = &mut ctx.accounts.registry_tree_config;
        config.registry_id = registry_id;
        config.merkle_tree = ctx.accounts.merkle_tree.key();
        config.tree_authority_pda = ctx.accounts.tree_authority_pda.key();
        config.mint_count = 0;
        config.max_depth = max_depth;
        config.max_buffer_size = max_buffer_size;
        config.admin = ctx.accounts.admin.key();
        config.bump = ctx.bumps.registry_tree_config;
        config.tree_authority_bump = ctx.bumps.tree_authority_pda;

        emit!(TreeInitialized {
            registry_id,
            merkle_tree: ctx.accounts.merkle_tree.key(),
            tree_authority_pda: ctx.accounts.tree_authority_pda.key(),
            max_depth,
            max_buffer_size,
        });

        Ok(())
    }

    /// Mint a universe cNFT to the buyer's wallet.
    ///
    /// CPIs into Metaplex Bubblegum's `mint_v1` instruction, using the
    /// protocol's tree-authority PDA as the signer.  The leaf is added to the
    /// registry's shared Merkle tree.
    ///
    /// Called by the bounty-escrow program (or directly by the protocol)
    /// after successful delivery + verification.
    ///
    /// # Parameters
    /// - `bounty_id_prefix` — First 8 bytes of the bounty UUID (for name).
    /// - `metadata_uri`     — IPFS/Arweave URI to the off-chain metadata JSON.
    ///
    /// # Signers required
    /// - `authority` — must be the registered `admin` OR the bounty-escrow
    ///   program's PDA (for automated mint-on-release).
    pub fn mint_universe_cnft(
        ctx: Context<MintUniverseCnft>,
        bounty_id_prefix: [u8; 8],
        metadata_uri: String,
    ) -> Result<()> {
        require!(
            metadata_uri.len() <= MAX_URI_LEN,
            CnftError::UriTooLong
        );
        require!(
            metadata_uri.starts_with("ipfs://") || metadata_uri.starts_with("https://"),
            CnftError::InvalidUri
        );

        let config = &mut ctx.accounts.registry_tree_config;
        let tree_authority_bump = config.tree_authority_bump;
        let registry_id = config.registry_id;

        let name = format_universe_name(&bounty_id_prefix);
        let protocol = ctx.accounts.tree_authority_pda.key();
        let miner = ctx.accounts.miner.key();

        // Build Bubblegum mint_v1 instruction data (hand-rolled Borsh serialisation)
        let ix_data = build_mint_v1_data(
            &name,
            EMU_SYMBOL,
            &metadata_uri,
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );

        // Account list for Bubblegum mint_v1 (order is spec-mandated):
        //   0  tree_authority        [writable, signer]  ← our PDA
        //   1  leaf_owner            [writable]
        //   2  leaf_delegate         []
        //   3  merkle_tree           [writable]
        //   4  payer                 [signer]
        //   5  tree_creator_or_delegate []
        //   6  log_wrapper           (noop)
        //   7  compression_program
        //   8  system_program
        let accounts = vec![
            anchor_lang::solana_program::instruction::AccountMeta::new(
                ctx.accounts.tree_authority_pda.key(),
                true,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new(
                ctx.accounts.buyer.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.buyer.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new(
                ctx.accounts.merkle_tree.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.payer.key(),
                true,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.tree_authority_pda.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.log_wrapper.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.compression_program.key(),
                false,
            ),
            anchor_lang::solana_program::instruction::AccountMeta::new_readonly(
                ctx.accounts.system_program.key(),
                false,
            ),
        ];

        let ix = anchor_lang::solana_program::instruction::Instruction {
            program_id: bubblegum::ID,
            accounts,
            data: ix_data,
        };

        // Tree-authority PDA signs the CPI
        let signer_seeds: &[&[&[u8]]] = &[&[
            TREE_AUTHORITY_SEED,
            registry_id.as_ref(),
            &[tree_authority_bump],
        ]];

        solana_program::program::invoke_signed(
            &ix,
            &[
                ctx.accounts.tree_authority_pda.to_account_info(),
                ctx.accounts.buyer.to_account_info(),
                ctx.accounts.merkle_tree.to_account_info(),
                ctx.accounts.payer.to_account_info(),
                ctx.accounts.log_wrapper.to_account_info(),
                ctx.accounts.compression_program.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
                ctx.accounts.bubblegum_program.to_account_info(),
            ],
            signer_seeds,
        )?;

        // Update mint count
        config.mint_count = config
            .mint_count
            .checked_add(1)
            .ok_or(CnftError::Overflow)?;

        emit!(UniverseMinted {
            registry_id,
            merkle_tree: ctx.accounts.merkle_tree.key(),
            buyer: ctx.accounts.buyer.key(),
            miner,
            bounty_id_prefix,
            mint_count: config.mint_count,
        });

        Ok(())
    }

    /// Transfer admin authority over the RegistryTreeConfig to a new pubkey.
    ///
    /// Used when the bounty-escrow program PDA should become the sole minting
    /// authority for automated on-release minting.
    pub fn transfer_admin(ctx: Context<TransferAdmin>) -> Result<()> {
        let config = &mut ctx.accounts.registry_tree_config;
        let old_admin = config.admin;
        config.admin = ctx.accounts.new_admin.key();

        emit!(AdminTransferred {
            registry_id: config.registry_id,
            old_admin,
            new_admin: ctx.accounts.new_admin.key(),
        });

        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Account structs
// ---------------------------------------------------------------------------

/// On-chain configuration for a registry's shared Bubblegum Merkle tree.
///
/// PDA seeds: `["registry-tree", registry_id]`.
#[account]
pub struct RegistryTreeConfig {
    /// SHA-256 of the registry's canonical URL (used as PDA seed).
    pub registry_id: [u8; 32],
    /// Address of the Bubblegum Merkle tree account.
    pub merkle_tree: Pubkey,
    /// Address of the tree-authority PDA that owns the tree.
    pub tree_authority_pda: Pubkey,
    /// Number of cNFTs minted so far (monotonically increasing).
    pub mint_count: u64,
    /// Merkle tree depth (20 = ~1M leaves; 32 = 4B leaves).
    pub max_depth: u32,
    /// Concurrent change log buffer size (64 is standard).
    pub max_buffer_size: u32,
    /// Admin pubkey allowed to mint.  Transferable to bounty-escrow PDA.
    pub admin: Pubkey,
    /// RegistryTreeConfig PDA bump.
    pub bump: u8,
    /// Tree-authority PDA bump (cached for cheaper mint CPIs).
    pub tree_authority_bump: u8,
}

impl RegistryTreeConfig {
    // 8 disc + 32+32+32+8+4+4+32+1+1 = 8+146 = 154 bytes.
    // Add 50 bytes forward-compatibility padding → 204.
    pub const LEN: usize = 204;
}

// ---------------------------------------------------------------------------
// Instruction account contexts
// ---------------------------------------------------------------------------

#[derive(Accounts)]
#[instruction(registry_id: [u8; 32])]
pub struct InitializeTree<'info> {
    /// Admin creating this config (pays rent).
    #[account(mut)]
    pub admin: Signer<'info>,

    /// RegistryTreeConfig PDA — created by this instruction.
    #[account(
        init,
        payer = admin,
        space = RegistryTreeConfig::LEN,
        seeds = [REGISTRY_TREE_SEED, registry_id.as_ref()],
        bump,
    )]
    pub registry_tree_config: Account<'info, RegistryTreeConfig>,

    /// Tree-authority PDA that Bubblegum will recognise as the tree delegate.
    ///
    /// Must be created before calling Bubblegum `create_tree` off-chain, using
    /// seeds `["tree-authority", registry_id]` from *this* program.
    /// CHECK: Verified by seeds constraint; used as signer in mint CPIs only.
    #[account(
        seeds = [TREE_AUTHORITY_SEED, registry_id.as_ref()],
        bump,
    )]
    pub tree_authority_pda: AccountInfo<'info>,

    /// The Bubblegum Merkle tree account (created externally).
    /// CHECK: Verified by Bubblegum on CPI; we only store its address.
    pub merkle_tree: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MintUniverseCnft<'info> {
    /// Authority permitted to trigger a mint (admin or bounty-escrow PDA).
    pub authority: Signer<'info>,

    /// RegistryTreeConfig — provides tree address and PDA bump.
    #[account(
        mut,
        seeds = [REGISTRY_TREE_SEED, registry_tree_config.registry_id.as_ref()],
        bump = registry_tree_config.bump,
        constraint = registry_tree_config.admin == authority.key() @ CnftError::Unauthorized,
    )]
    pub registry_tree_config: Account<'info, RegistryTreeConfig>,

    /// Tree-authority PDA (must match config and signs the CPI).
    /// CHECK: Verified by seeds constraint.
    #[account(
        seeds = [TREE_AUTHORITY_SEED, registry_tree_config.registry_id.as_ref()],
        bump = registry_tree_config.tree_authority_bump,
    )]
    pub tree_authority_pda: AccountInfo<'info>,

    /// Buyer — receives the cNFT leaf (becomes leaf_owner).
    /// CHECK: Any valid pubkey; no additional validation needed.
    pub buyer: AccountInfo<'info>,

    /// Miner — listed as primary creator in cNFT metadata.
    /// CHECK: Any valid pubkey; no additional validation needed.
    pub miner: AccountInfo<'info>,

    /// The Bubblegum Merkle tree account (must match config).
    /// CHECK: Validated by Bubblegum on CPI; address checked against config.
    #[account(
        mut,
        constraint = merkle_tree.key() == registry_tree_config.merkle_tree @ CnftError::TreeMismatch,
    )]
    pub merkle_tree: AccountInfo<'info>,

    /// Payer — covers any rent/fees for the Bubblegum CPI.
    #[account(mut)]
    pub payer: Signer<'info>,

    /// SPL Noop program (required by Bubblegum for event logging).
    /// CHECK: Validated by Bubblegum on CPI; address checked below.
    #[account(
        constraint = log_wrapper.key() == spl_noop::ID @ CnftError::InvalidLogWrapper,
    )]
    pub log_wrapper: AccountInfo<'info>,

    /// SPL Account Compression program (required by Bubblegum).
    /// CHECK: Validated by Bubblegum on CPI; address checked below.
    #[account(
        constraint = compression_program.key() == spl_account_compression::ID @ CnftError::InvalidCompressionProgram,
    )]
    pub compression_program: AccountInfo<'info>,

    /// Bubblegum program (called via CPI).
    /// CHECK: Validated by hard-coded ID check below.
    #[account(
        constraint = bubblegum_program.key() == bubblegum::ID @ CnftError::InvalidBubblegumProgram,
    )]
    pub bubblegum_program: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct TransferAdmin<'info> {
    /// Current admin.
    pub admin: Signer<'info>,

    /// RegistryTreeConfig to update.
    #[account(
        mut,
        seeds = [REGISTRY_TREE_SEED, registry_tree_config.registry_id.as_ref()],
        bump = registry_tree_config.bump,
        constraint = registry_tree_config.admin == admin.key() @ CnftError::Unauthorized,
    )]
    pub registry_tree_config: Account<'info, RegistryTreeConfig>,

    /// New admin pubkey.
    /// CHECK: Any valid pubkey; caller's responsibility.
    pub new_admin: AccountInfo<'info>,
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

#[error_code]
pub enum CnftError {
    #[msg("Arithmetic overflow")]
    Overflow,
    #[msg("Unauthorized: signer is not the registered admin")]
    Unauthorized,
    #[msg("Provided merkle_tree does not match the registered tree")]
    TreeMismatch,
    #[msg("metadata_uri exceeds maximum length")]
    UriTooLong,
    #[msg("metadata_uri must begin with ipfs:// or https://")]
    InvalidUri,
    #[msg("log_wrapper must be the SPL Noop program")]
    InvalidLogWrapper,
    #[msg("compression_program must be the SPL Account Compression program")]
    InvalidCompressionProgram,
    #[msg("bubblegum_program must be the Metaplex Bubblegum program")]
    InvalidBubblegumProgram,
    #[msg("max_depth must be >= 16 (65 536 leaves)")]
    TreeTooShallow,
    #[msg("max_buffer_size must be > 0")]
    InvalidBufferSize,
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

#[event]
pub struct TreeInitialized {
    pub registry_id: [u8; 32],
    pub merkle_tree: Pubkey,
    pub tree_authority_pda: Pubkey,
    pub max_depth: u32,
    pub max_buffer_size: u32,
}

#[event]
pub struct UniverseMinted {
    pub registry_id: [u8; 32],
    pub merkle_tree: Pubkey,
    pub buyer: Pubkey,
    pub miner: Pubkey,
    pub bounty_id_prefix: [u8; 8],
    pub mint_count: u64,
}

#[event]
pub struct AdminTransferred {
    pub registry_id: [u8; 32],
    pub old_admin: Pubkey,
    pub new_admin: Pubkey,
}

// ---------------------------------------------------------------------------
// Unit tests (logic only — no SBF/BPF; compile with `cargo test --lib`)
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // -------------------------------------------------------------------------
    // format_universe_name
    // -------------------------------------------------------------------------

    #[test]
    fn universe_name_is_correctly_formatted() {
        let prefix: [u8; 8] = [0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe];
        let name = format_universe_name(&prefix);
        assert_eq!(name, "Universe deadbeefcafebabe");
    }

    #[test]
    fn universe_name_all_zeros() {
        let prefix: [u8; 8] = [0u8; 8];
        let name = format_universe_name(&prefix);
        assert_eq!(name, "Universe 0000000000000000");
    }

    #[test]
    fn universe_name_max_length() {
        let prefix: [u8; 8] = [0xffu8; 8];
        let name = format_universe_name(&prefix);
        assert_eq!(name, "Universe ffffffffffffffff");
        assert!(name.len() <= MAX_NAME_LEN as usize);
    }

    #[test]
    fn universe_name_fits_in_max_name_len() {
        // "Universe " (9) + 16 hex digits (16) = 25 ≤ MAX_NAME_LEN (32)
        let prefix: [u8; 8] = [0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef];
        let name = format_universe_name(&prefix);
        assert!(name.len() <= MAX_NAME_LEN);
    }

    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    #[test]
    fn creator_shares_sum_to_100() {
        assert_eq!(
            MINER_CREATOR_SHARE as u16 + PROTOCOL_CREATOR_SHARE as u16,
            100
        );
    }

    #[test]
    fn seller_fee_bps_is_5_pct() {
        assert_eq!(SELLER_FEE_BPS, 500);
    }

    #[test]
    fn min_max_depth_at_least_16() {
        assert!(MIN_MAX_DEPTH >= 16);
    }

    #[test]
    fn recommended_max_depth_exceeds_min() {
        assert!(RECOMMENDED_MAX_DEPTH > MIN_MAX_DEPTH);
    }

    #[test]
    fn registry_tree_config_len_at_least_154() {
        // Calculated minimum: 8+32+32+32+8+4+4+32+1+1 = 154
        assert!(RegistryTreeConfig::LEN >= 154);
    }

    // -------------------------------------------------------------------------
    // build_mint_v1_data
    // -------------------------------------------------------------------------

    fn dummy_pubkey(byte: u8) -> Pubkey {
        Pubkey::new_from_array([byte; 32])
    }

    #[test]
    fn mint_v1_data_starts_with_discriminant() {
        let miner = dummy_pubkey(0xaa);
        let protocol = dummy_pubkey(0xbb);
        let data = build_mint_v1_data(
            "Universe deadbeef",
            EMU_SYMBOL,
            "ipfs://QmTestCid",
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );
        let expected_disc: [u8; 8] = [145, 98, 192, 118, 184, 147, 118, 104];
        assert_eq!(&data[..8], &expected_disc);
    }

    #[test]
    fn mint_v1_data_contains_emu_symbol() {
        let miner = dummy_pubkey(0x01);
        let protocol = dummy_pubkey(0x02);
        let data = build_mint_v1_data(
            "Universe test",
            EMU_SYMBOL,
            "ipfs://QmFoo",
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );
        // Find "EMU" in the byte stream (after the name)
        let emu_bytes = b"EMU";
        let found = data.windows(3).any(|w| w == emu_bytes);
        assert!(found, "EMU symbol not found in serialised data");
    }

    #[test]
    fn mint_v1_data_encodes_seller_fee() {
        let miner = dummy_pubkey(0x01);
        let protocol = dummy_pubkey(0x02);
        let data = build_mint_v1_data(
            "Universe test",
            EMU_SYMBOL,
            "ipfs://QmFoo",
            500u16,
            &miner,
            &protocol,
        );
        // 500 in little-endian is [0xF4, 0x01]
        let fee_bytes = 500u16.to_le_bytes();
        let found = data.windows(2).any(|w| w == fee_bytes);
        assert!(found, "seller_fee_basis_points not found in serialised data");
    }

    #[test]
    fn mint_v1_data_encodes_miner_pubkey() {
        let miner = dummy_pubkey(0xaa);
        let protocol = dummy_pubkey(0xbb);
        let data = build_mint_v1_data(
            "Universe test",
            EMU_SYMBOL,
            "ipfs://QmFoo",
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );
        let miner_bytes = [0xaau8; 32];
        let found = data.windows(32).any(|w| w == miner_bytes);
        assert!(found, "miner pubkey not found in serialised data");
    }

    #[test]
    fn mint_v1_data_encodes_protocol_pubkey() {
        let miner = dummy_pubkey(0xaa);
        let protocol = dummy_pubkey(0xbb);
        let data = build_mint_v1_data(
            "Universe test",
            EMU_SYMBOL,
            "ipfs://QmFoo",
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );
        let protocol_bytes = [0xbbu8; 32];
        let found = data.windows(32).any(|w| w == protocol_bytes);
        assert!(found, "protocol pubkey not found in serialised data");
    }

    #[test]
    fn mint_v1_data_creator_shares() {
        // MINER_CREATOR_SHARE (95) and PROTOCOL_CREATOR_SHARE (5) must appear
        // in the data (after the creator pubkeys).
        let miner = dummy_pubkey(0xaa);
        let protocol = dummy_pubkey(0xbb);
        let data = build_mint_v1_data(
            "Universe test",
            EMU_SYMBOL,
            "ipfs://QmFoo",
            SELLER_FEE_BPS,
            &miner,
            &protocol,
        );
        assert!(
            data.contains(&MINER_CREATOR_SHARE),
            "miner share (95) not found"
        );
        assert!(
            data.contains(&PROTOCOL_CREATOR_SHARE),
            "protocol share (5) not found"
        );
    }

    #[test]
    fn mint_v1_data_minimum_length() {
        // Minimum: 8 (disc) + ≥1 (name) + ≥1 (symbol) + ≥1 (uri) + 2 (fee)
        //   + 1+1+1+1+1+1 (flags/options) + 4+66+66 (creators vec)
        let miner = dummy_pubkey(0x01);
        let protocol = dummy_pubkey(0x02);
        let data = build_mint_v1_data(
            "X",
            "Y",
            "ipfs://Z",
            0,
            &miner,
            &protocol,
        );
        // 8 disc + 4+1 (name) + 4+1 (symbol) + 4+8 (uri "ipfs://Z") + 2 + 6 flags + 4+34+34 creators
        // ≥ 106
        assert!(data.len() >= 106, "data length {} < 106", data.len());
    }

    // -------------------------------------------------------------------------
    // URI validation logic (mirroring the program constraints)
    // -------------------------------------------------------------------------

    #[test]
    fn uri_validation_accepts_ipfs_scheme() {
        let uri = "ipfs://QmSomeHash";
        assert!(uri.starts_with("ipfs://") || uri.starts_with("https://"));
    }

    #[test]
    fn uri_validation_accepts_https_scheme() {
        let uri = "https://arweave.net/some-tx-id";
        assert!(uri.starts_with("ipfs://") || uri.starts_with("https://"));
    }

    #[test]
    fn uri_validation_rejects_http_scheme() {
        let uri = "http://example.com/metadata.json";
        assert!(!(uri.starts_with("ipfs://") || uri.starts_with("https://")));
    }

    #[test]
    fn uri_length_within_max() {
        let uri = "ipfs://".to_string() + &"a".repeat(MAX_URI_LEN - 7);
        assert!(uri.len() <= MAX_URI_LEN);
    }

    #[test]
    fn uri_length_exceeds_max() {
        let uri = "ipfs://".to_string() + &"a".repeat(MAX_URI_LEN);
        assert!(uri.len() > MAX_URI_LEN);
    }
}
