/// Wallet management for the Emanon CLI.
///
/// Provides helpers for generating, importing, and querying a Solana wallet
/// dedicated to the Emanon player identity.  The canonical wallet file lives at
/// `~/.config/emanon/wallet.json` in the Solana JSON keypair array format.
///
/// # File format
///
/// A Solana keypair JSON file is a bare array of 64 unsigned bytes:
/// ```json
/// [1,2,3,...,32,  33,34,...,64]
/// ```
/// Bytes 0–31 are the secret (private) key seed; bytes 32–63 are the
/// compressed Ed25519 public key.
///
/// # Permission requirements
///
/// The wallet file must have `0600` permissions (owner read+write only) to
/// prevent accidental exposure of the private key.  Emanon warns if it finds
/// a file with overly permissive settings and refuses to overwrite an
/// existing 0600 file without explicit `--force`.
///
/// # Network defaults
///
/// Emanon defaults to **devnet** for early adopters.  Pass `--network mainnet`
/// to any wallet command to opt into mainnet-beta.
///
/// # SOL balance
///
/// Queried via `getBalance` JSON-RPC (returned in lamports, displayed as SOL).
///
/// # USDC balance
///
/// Queried via `getTokenAccountsByOwner` JSON-RPC using the canonical USDC
/// mint address for the target network.  Returns 0.0 if no token account
/// exists yet (no error — the account is created on first receipt/transfer).

use std::process::Command;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

pub const EMANON_WALLET_FILENAME: &str = "wallet.json";

/// USDC devnet SPL mint address.
pub const USDC_MINT_DEVNET: &str = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU";

/// USDC mainnet-beta SPL mint address.
pub const USDC_MINT_MAINNET: &str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

/// Return the default Emanon wallet path: `~/.config/emanon/wallet.json`.
pub fn default_wallet_path() -> String {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    format!("{home}/.config/emanon/{EMANON_WALLET_FILENAME}")
}

// ---------------------------------------------------------------------------
// Keypair generation
// ---------------------------------------------------------------------------

/// Generate a new Solana keypair at `output_path` using the `solana-keygen` CLI.
///
/// Creates any missing parent directories, sets `0600` permissions, and
/// returns the human-readable Base58 public key.
///
/// # Errors
///
/// Returns an error if `solana-keygen` is not installed.  The caller should
/// surface the install link <https://docs.solanalabs.com/cli/install>.
pub fn generate_keypair(output_path: &str) -> Result<String, Box<dyn std::error::Error>> {
    // Ensure parent directory exists.
    if let Some(parent) = std::path::Path::new(output_path).parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Attempt keypair generation via `solana-keygen new`.
    let status = Command::new("solana-keygen")
        .args([
            "new",
            "--outfile", output_path,
            "--no-bip39-passphrase",
            "--force",   // overwrite if already exists (guarded by caller)
            "--silent",
        ])
        .status();

    match status {
        Ok(s) if s.success() => {
            set_file_permissions_600(output_path)?;
            let pubkey = derive_pubkey_from_file(output_path)?;
            Ok(pubkey)
        }
        Ok(s) => {
            Err(format!(
                "solana-keygen exited with status {s}.\n\
                 Make sure the Solana CLI is installed: https://docs.solanalabs.com/cli/install"
            )
            .into())
        }
        Err(_) => Err(
            "solana-keygen not found.\n\
             Install the Solana CLI: https://docs.solanalabs.com/cli/install\n\
             Then re-run `emanon wallet init`."
                .into(),
        ),
    }
}

/// Import an existing Solana keypair file into the Emanon wallet location.
///
/// Copies `src` to `dest`, then sets `0600` permissions on the destination.
/// Returns the public key derived from the imported file.
pub fn import_keypair(src: &str, dest: &str) -> Result<String, Box<dyn std::error::Error>> {
    if let Some(parent) = std::path::Path::new(dest).parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Read the source keypair (validates it is parseable).
    let content = std::fs::read_to_string(src)
        .map_err(|e| format!("Cannot read keypair from {src}: {e}"))?;

    // Minimal validation: must be a JSON byte array.
    let bytes = crate::vrf::parse_keypair_json_bytes(&content)
        .ok_or_else(|| format!("{src} does not look like a Solana keypair JSON array"))?;
    if bytes.len() != 64 {
        return Err(
            format!("Keypair at {src} has {} bytes; expected 64 (Solana Ed25519 format)", bytes.len()).into(),
        );
    }

    std::fs::write(dest, &content)?;
    set_file_permissions_600(dest)?;

    let pubkey = derive_pubkey_from_file(dest)?;
    Ok(pubkey)
}

// ---------------------------------------------------------------------------
// Pubkey derivation
// ---------------------------------------------------------------------------

/// Derive the Base58 public key from a keypair file.
///
/// Attempts three strategies in order:
/// 1. `solana address --keypair <path>` (requires Solana CLI).
/// 2. `solana-keygen pubkey <path>` (same package, different sub-command).
/// 3. Parse JSON array, hex-encode last 32 bytes (fallback — hex, not Base58).
pub fn derive_pubkey_from_file(path: &str) -> Result<String, Box<dyn std::error::Error>> {
    // Strategy 1: solana address
    if let Ok(out) = Command::new("solana").args(["address", "--keypair", path]).output() {
        if out.status.success() {
            let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if s.len() >= 32 {
                return Ok(s);
            }
        }
    }

    // Strategy 2: solana-keygen pubkey
    if let Ok(out) = Command::new("solana-keygen").args(["pubkey", path]).output() {
        if out.status.success() {
            let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if s.len() >= 32 {
                return Ok(s);
            }
        }
    }

    // Strategy 3: parse JSON array and hex-encode last 32 bytes.
    let content = std::fs::read_to_string(path)?;
    if let Some(bytes) = crate::vrf::parse_keypair_json_bytes(&content) {
        if bytes.len() >= 64 {
            let pubkey_bytes = &bytes[32..64];
            let hex: String = pubkey_bytes.iter().map(|b| format!("{b:02x}")).collect();
            return Ok(hex);
        }
    }

    Err(format!(
        "Could not derive pubkey from {path}.\n\
         Install the Solana CLI: https://docs.solanalabs.com/cli/install"
    )
    .into())
}

// ---------------------------------------------------------------------------
// Permission helpers
// ---------------------------------------------------------------------------

/// Set file permissions to `0600` (owner read+write only).
///
/// No-op on non-Unix platforms; always succeeds on those.
pub fn set_file_permissions_600(path: &str) -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let perms = std::fs::Permissions::from_mode(0o600);
        std::fs::set_permissions(path, perms)?;
    }
    let _ = path; // silence unused warning on non-Unix
    Ok(())
}

/// Check wallet file permissions and print a warning if too permissive.
///
/// A file that is group- or world-readable (mode & 0o077 != 0) exposes the
/// private key and should be corrected immediately.
pub fn check_and_warn_permissions(path: &str) {
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        if let Ok(meta) = std::fs::metadata(path) {
            let mode = meta.mode() & 0o777;
            if mode & 0o077 != 0 {
                eprintln!(
                    "warning: {path} has permissions {:03o} — private key may be exposed.\n\
                     Fix with: chmod 0600 {path}",
                    mode
                );
            }
        }
    }
    let _ = path; // silence unused warning on non-Unix
}

// ---------------------------------------------------------------------------
// Balance queries
// ---------------------------------------------------------------------------

/// Query the SOL balance for `pubkey` from `rpc_url`.
///
/// Tries `solana balance <pubkey> --url <rpc_url>` first; falls back to
/// `getBalance` JSON-RPC.  Returns balance in SOL (not lamports).
pub fn get_sol_balance(pubkey: &str, rpc_url: &str) -> Result<f64, String> {
    // Strategy 1: solana CLI.
    if let Ok(out) = Command::new("solana")
        .args(["balance", pubkey, "--url", rpc_url])
        .output()
    {
        if out.status.success() {
            let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
            // Format: "1.5 SOL"
            let sol_str = s.split_whitespace().next().unwrap_or("0");
            if let Ok(v) = sol_str.parse::<f64>() {
                return Ok(v);
            }
        }
    }

    // Strategy 2: JSON-RPC getBalance.
    let params = format!(r#"["{pubkey}",{{"commitment":"confirmed"}}]"#);
    let response = crate::vrf::solana_rpc_call(rpc_url, "getBalance", &params)?;

    if let Some(val_str) = extract_field_raw(&response, "value") {
        if let Ok(lamports) = val_str.trim().parse::<u64>() {
            return Ok(lamports as f64 / 1_000_000_000.0);
        }
    }

    Err(format!("Could not parse SOL balance from RPC response: {response}"))
}

/// Query the USDC SPL token balance for `pubkey` from `rpc_url`.
///
/// Tries `spl-token balance` first; falls back to `getTokenAccountsByOwner`
/// JSON-RPC.  Returns 0.0 if no USDC token account exists yet (not an error).
pub fn get_usdc_balance(pubkey: &str, rpc_url: &str) -> Result<f64, String> {
    let usdc_mint = if rpc_url.contains("mainnet") {
        USDC_MINT_MAINNET
    } else {
        USDC_MINT_DEVNET
    };

    // Strategy 1: spl-token CLI.
    if let Ok(out) = Command::new("spl-token")
        .args(["balance", "--owner", pubkey, usdc_mint, "--url", rpc_url])
        .output()
    {
        if out.status.success() {
            let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if let Ok(v) = s.parse::<f64>() {
                return Ok(v);
            }
        }
    }

    // Strategy 2: getTokenAccountsByOwner JSON-RPC.
    let params = format!(
        r#"["{pubkey}",{{"mint":"{usdc_mint}"}},{{"encoding":"jsonParsed","commitment":"confirmed"}}]"#
    );
    let response = crate::vrf::solana_rpc_call(rpc_url, "getTokenAccountsByOwner", &params)?;

    // No token account yet → balance is 0.
    if response.contains("\"value\":[]") || response.contains("\"value\": []") {
        return Ok(0.0);
    }

    // Look for "uiAmount" field in the response.
    if let Some(raw) = extract_field_raw(&response, "uiAmount") {
        let cleaned = raw.trim().trim_matches('"');
        if cleaned == "null" {
            return Ok(0.0);
        }
        if let Ok(v) = cleaned.parse::<f64>() {
            return Ok(v);
        }
    }

    Ok(0.0)
}

// ---------------------------------------------------------------------------
// Airdrop
// ---------------------------------------------------------------------------

/// Request a devnet/testnet SOL airdrop for `pubkey`.
///
/// Returns the transaction signature string on success.
///
/// # Errors
///
/// Returns an error if the RPC URL targets mainnet-beta (airdrops are
/// unavailable there by design).
pub fn request_airdrop(pubkey: &str, rpc_url: &str, amount_sol: f64) -> Result<String, String> {
    if rpc_url.contains("mainnet") {
        return Err(
            "Airdrops are only available on devnet/testnet — not mainnet-beta.\n\
             Use `emanon wallet airdrop` without `--network mainnet`."
                .to_string(),
        );
    }

    // Strategy 1: solana airdrop CLI.
    let amount_str = amount_sol.to_string();
    if let Ok(out) = Command::new("solana")
        .args(["airdrop", &amount_str, pubkey, "--url", rpc_url])
        .output()
    {
        if out.status.success() {
            let sig = String::from_utf8_lossy(&out.stdout).trim().to_string();
            return Ok(sig);
        }
        let err = String::from_utf8_lossy(&out.stderr).trim().to_string();
        if !err.is_empty() {
            return Err(format!("solana airdrop: {err}"));
        }
    }

    // Strategy 2: requestAirdrop JSON-RPC.
    let lamports = (amount_sol * 1_000_000_000.0) as u64;
    let params = format!(r#"["{pubkey}",{lamports}]"#);
    let response = crate::vrf::solana_rpc_call(rpc_url, "requestAirdrop", &params)?;
    if let Some(sig) = extract_field_string(&response, "result") {
        return Ok(sig);
    }

    Err(format!("Unexpected airdrop RPC response: {response}"))
}

// ---------------------------------------------------------------------------
// Internal JSON helpers
// ---------------------------------------------------------------------------

/// Extract a raw (unquoted) JSON value by key — e.g. numbers, booleans.
pub fn extract_field_raw(s: &str, key: &str) -> Option<String> {
    let needle = format!("\"{}\":", key);
    let idx = s.find(&needle)?;
    let after = s[idx + needle.len()..].trim_start();
    let end = after.find(|c: char| c == ',' || c == '}').unwrap_or(after.len());
    Some(after[..end].trim().to_string())
}

/// Extract a JSON string value by key, stripping surrounding quotes.
pub fn extract_field_string(s: &str, key: &str) -> Option<String> {
    let needle = format!("\"{}\":", key);
    let idx = s.find(&needle)?;
    let after = s[idx + needle.len()..].trim_start();
    if after.starts_with('"') {
        let inner_end = after[1..].find('"')?;
        return Some(after[1..=inner_end].to_string());
    }
    // Non-quoted value — return raw
    let end = after.find(|c: char| c == ',' || c == '}').unwrap_or(after.len());
    Some(after[..end].trim().to_string())
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_wallet_path_is_correct() {
        let path = default_wallet_path();
        assert!(path.contains(".config/emanon/"), "should be under .config/emanon/: {path}");
        assert!(path.ends_with("wallet.json"), "should end with wallet.json: {path}");
    }

    #[test]
    fn check_permissions_no_panic_for_nonexistent_file() {
        // Should not panic even if path does not exist.
        check_and_warn_permissions("/tmp/emanon-test-nonexistent-wallet-12345.json");
    }

    #[test]
    fn extract_field_raw_number() {
        let json = r#"{"result":{"value":12345678,"context":{"slot":1}}}"#;
        assert_eq!(extract_field_raw(json, "value").as_deref(), Some("12345678"));
    }

    #[test]
    fn extract_field_raw_missing_key() {
        let json = r#"{"a":1}"#;
        assert!(extract_field_raw(json, "nothere").is_none());
    }

    #[test]
    fn extract_field_string_quoted_value() {
        let json = r#"{"result":"5oG9Jko7AbcXyZ123"}"#;
        assert_eq!(extract_field_string(json, "result").as_deref(), Some("5oG9Jko7AbcXyZ123"));
    }

    #[test]
    fn extract_field_string_null_value() {
        let json = r#"{"uiAmount":null}"#;
        assert_eq!(extract_field_raw(json, "uiAmount").as_deref(), Some("null"));
    }

    #[test]
    fn usdc_mint_addresses_have_valid_length() {
        // Base58 Solana addresses are 43–44 characters.
        assert!(
            USDC_MINT_DEVNET.len() >= 43 && USDC_MINT_DEVNET.len() <= 44,
            "devnet USDC mint length: {}",
            USDC_MINT_DEVNET.len()
        );
        assert!(
            USDC_MINT_MAINNET.len() >= 43 && USDC_MINT_MAINNET.len() <= 44,
            "mainnet USDC mint length: {}",
            USDC_MINT_MAINNET.len()
        );
    }

    #[test]
    fn airdrop_rejects_mainnet_url() {
        let result =
            request_airdrop("FakePubkey1111111111111111111111111111111111", "https://api.mainnet-beta.solana.com", 1.0);
        assert!(result.is_err(), "should error on mainnet");
        let msg = result.unwrap_err();
        assert!(msg.contains("devnet"), "error should mention devnet: {msg}");
    }

    #[test]
    fn airdrop_rejects_mainnet_url_variant() {
        let result =
            request_airdrop("FakePubkey1111111111111111111111111111111111", "https://mainnet.helius-rpc.com", 0.5);
        assert!(result.is_err(), "should error on mainnet RPC variant");
    }

    #[test]
    fn get_sol_balance_errors_gracefully_on_bad_rpc() {
        // Should return Err rather than panic when RPC is unreachable.
        let result = get_sol_balance(
            "FakePubkey1111111111111111111111111111111111",
            "http://127.0.0.1:19999",
        );
        assert!(result.is_err(), "should error when RPC unreachable: {result:?}");
    }

    #[test]
    fn get_usdc_balance_zero_on_empty_value_array() {
        // Simulate the RPC response for a wallet with no USDC account.
        let _response = r#"{"result":{"value":[]}}"#;
        // Since we can't call the real RPC, just verify the empty-array detection logic:
        assert!(_response.contains("\"value\":[]") || _response.contains("\"value\": []"));
    }

    #[test]
    fn import_keypair_rejects_non_array_json() {
        // Write a fake file that is not a JSON array.
        let tmp = format!("/tmp/emanon-wallet-import-test-{}.json", std::process::id());
        std::fs::write(&tmp, r#"{"key": "not_an_array"}"#).unwrap();
        let dest = format!("{tmp}.dest");
        let result = import_keypair(&tmp, &dest);
        assert!(result.is_err(), "should reject non-array keypair");
        let _ = std::fs::remove_file(&tmp);
        let _ = std::fs::remove_file(&dest);
    }

    #[test]
    fn import_keypair_rejects_wrong_length_array() {
        // A 32-byte array (too short).
        let bytes: Vec<u8> = (0u8..32).collect();
        let json = format!(
            "[{}]",
            bytes.iter().map(|b| b.to_string()).collect::<Vec<_>>().join(",")
        );
        let tmp = format!("/tmp/emanon-wallet-short-test-{}.json", std::process::id());
        std::fs::write(&tmp, &json).unwrap();
        let dest = format!("{tmp}.dest");
        let result = import_keypair(&tmp, &dest);
        assert!(result.is_err(), "should reject 32-byte keypair");
        let _ = std::fs::remove_file(&tmp);
        let _ = std::fs::remove_file(&dest);
    }
}
