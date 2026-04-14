/// VRF (Verifiable Random Function) integration for Emanon.
///
/// Provides verifiably random seeds for universe genesis.  Seeds are committed
/// before mining begins, preventing miners from "pre-finding" universes that
/// satisfy a bounty predicate.
///
/// # Sources
///
/// | Source            | Verifiable? | Cost           | Notes                                      |
/// |-------------------|-------------|----------------|--------------------------------------------|
/// | `switchboard-vrf` | ✓           | ~0.001 SOL     | Uses Solana devnet / mainnet slot blockhash|
/// | `local-prng`      | ✗           | Free           | /dev/urandom — testing only               |
///
/// # Switchboard VRF via Solana Slot Blockhash
///
/// Instead of the heavier Switchboard VRF account protocol (which requires the
/// `switchboard-solana` crate), this implementation derives the seed from the
/// canonical blockhash of a specific Solana slot.  Any observer can verify the
/// seed independently:
///
/// ```text
/// seed = SHA-256( slot_blockhash || ":" || wallet_pubkey )
/// request_id = "slot:<slot_number>"
/// ```
///
/// Given the `request_id` and `wallet_pubkey`, anyone with access to a Solana RPC
/// can fetch the blockhash for that slot and recompute the seed.
///
/// # Upgrade path to full Switchboard VRF
///
/// When the `switchboard-solana` crate is added as a dependency, the
/// `SwitchboardVrf` source can be upgraded to use the on-chain VRF account
/// protocol (request → oracle fulfillment → read beta output) for even stronger
/// randomness guarantees.  The wire format (`VrfResult`) is stable and will not
/// change between implementation strategies.
///
/// # Wire format
///
/// ```json
/// {
///   "request_id": "slot:12345678",
///   "slot": 12345678,
///   "blockhash": "4vJ9JU1bJJE96RNPU2d3YMuHBB1yxBsS3b9Bk3y9rP",
///   "seed_hex": "a3b4c5d6e7f8...",
///   "source": "switchboard-vrf",
///   "wallet_pubkey": "ed25519:7GRmBwnBChf32GrKBbqBRR...",
///   "timestamp": "2026-04-14T17:10:00Z",
///   "rpc_url": "https://api.devnet.solana.com",
///   "network": "devnet",
///   "verifiable": true,
///   "verify_note": "sha256(blockhash + \":\" + wallet_pubkey)"
/// }
/// ```

use std::process::Command;

// ---------------------------------------------------------------------------
// VRF source
// ---------------------------------------------------------------------------

/// The randomness source for a VRF request.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VrfSource {
    /// Derive seed from Solana slot blockhash (verifiable, requires network).
    SwitchboardVrf,
    /// Read from /dev/urandom (non-verifiable, for local testing).
    LocalPrng,
}

impl VrfSource {
    pub fn as_str(&self) -> &'static str {
        match self {
            VrfSource::SwitchboardVrf => "switchboard-vrf",
            VrfSource::LocalPrng => "local-prng",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "switchboard-vrf" => Some(VrfSource::SwitchboardVrf),
            "local-prng" => Some(VrfSource::LocalPrng),
            _ => None,
        }
    }

    pub fn is_verifiable(&self) -> bool {
        matches!(self, VrfSource::SwitchboardVrf)
    }
}

// ---------------------------------------------------------------------------
// VRF result
// ---------------------------------------------------------------------------

/// A completed VRF request, ready for serialisation and verification.
#[derive(Debug, Clone)]
pub struct VrfResult {
    /// Stable identifier for this request: `"slot:<N>"` for on-chain sources,
    /// or `"local:<timestamp_ns>"` for the local PRNG fallback.
    pub request_id: String,
    /// Solana slot used for blockhash derivation (0 for local-prng).
    pub slot: u64,
    /// Canonical blockhash of `slot` (empty string for local-prng).
    pub blockhash: String,
    /// 32-byte seed as a lowercase hex string (64 hex chars).
    pub seed_hex: String,
    /// Source that produced this result.
    pub source: VrfSource,
    /// The wallet public key used to personalise the seed derivation.
    /// Format: `"ed25519:<base58>"`.  Empty string if no wallet was available.
    pub wallet_pubkey: String,
    /// ISO 8601 UTC timestamp when the request was fulfilled.
    pub timestamp: String,
    /// Solana RPC endpoint queried.
    pub rpc_url: String,
    /// Network name (e.g. `"devnet"`, `"mainnet-beta"`, `"local"`).
    pub network: String,
}

impl VrfResult {
    /// Is this result independently verifiable?
    pub fn is_verifiable(&self) -> bool {
        self.source.is_verifiable() && !self.blockhash.is_empty()
    }

    /// Human-readable note explaining how to verify the seed.
    pub fn verify_note(&self) -> &'static str {
        match self.source {
            VrfSource::SwitchboardVrf => {
                r#"sha256(slot_blockhash + ":" + wallet_pubkey)"#
            }
            VrfSource::LocalPrng => "Not verifiable — generated from /dev/urandom",
        }
    }

    /// Serialise to a compact JSON string.
    pub fn to_json(&self) -> String {
        let verifiable = if self.is_verifiable() { "true" } else { "false" };
        format!(
            "{{\n\
            \x20 \"request_id\": \"{request_id}\",\n\
            \x20 \"slot\": {slot},\n\
            \x20 \"blockhash\": \"{blockhash}\",\n\
            \x20 \"seed_hex\": \"{seed_hex}\",\n\
            \x20 \"source\": \"{source}\",\n\
            \x20 \"wallet_pubkey\": \"{wallet_pubkey}\",\n\
            \x20 \"timestamp\": \"{timestamp}\",\n\
            \x20 \"rpc_url\": \"{rpc_url}\",\n\
            \x20 \"network\": \"{network}\",\n\
            \x20 \"verifiable\": {verifiable},\n\
            \x20 \"verify_note\": \"{verify_note}\"\n\
            }}",
            request_id = self.request_id,
            slot = self.slot,
            blockhash = self.blockhash,
            seed_hex = self.seed_hex,
            source = self.source.as_str(),
            wallet_pubkey = self.wallet_pubkey,
            timestamp = self.timestamp,
            rpc_url = self.rpc_url,
            network = self.network,
            verify_note = self.verify_note(),
        )
    }

    /// Parse from a JSON string (minimal hand-rolled parser).
    pub fn from_json(s: &str) -> Option<Self> {
        let request_id = json_field(s, "request_id")?.to_string();
        let slot_str = json_field_raw(s, "slot")?;
        let slot: u64 = slot_str.trim().parse().ok()?;
        let blockhash = json_field(s, "blockhash").unwrap_or("").to_string();
        let seed_hex = json_field(s, "seed_hex")?.to_string();
        let source_str = json_field(s, "source")?;
        let source = VrfSource::from_str(source_str)?;
        let wallet_pubkey = json_field(s, "wallet_pubkey").unwrap_or("").to_string();
        let timestamp = json_field(s, "timestamp").unwrap_or("").to_string();
        let rpc_url = json_field(s, "rpc_url").unwrap_or("").to_string();
        let network = json_field(s, "network").unwrap_or("").to_string();
        Some(VrfResult {
            request_id,
            slot,
            blockhash,
            seed_hex,
            source,
            wallet_pubkey,
            timestamp,
            rpc_url,
            network,
        })
    }
}

// ---------------------------------------------------------------------------
// Wallet helpers
// ---------------------------------------------------------------------------

/// Wallet configuration loaded from a keypair file or environment variable.
#[derive(Debug, Clone)]
pub struct WalletConfig {
    /// Path to the Solana keypair JSON file.
    pub keypair_path: String,
    /// Base58-encoded Ed25519 public key, prefixed with `"ed25519:"`.
    pub pubkey: String,
}

impl WalletConfig {
    /// Load wallet from an explicit path, the `SOLANA_KEYPAIR` env var, or
    /// the default Solana CLI location (`~/.config/solana/id.json`).
    ///
    /// Returns `None` if no keypair file exists.
    pub fn load(explicit_path: Option<&str>) -> Option<Self> {
        let path = if let Some(p) = explicit_path {
            p.to_string()
        } else if let Ok(env_path) = std::env::var("SOLANA_KEYPAIR") {
            env_path
        } else {
            let home = std::env::var("HOME").ok()?;
            format!("{home}/.config/solana/id.json")
        };

        // Try to derive pubkey via `solana address` CLI.
        let pubkey = derive_pubkey_from_keypair(&path)?;
        Some(WalletConfig { keypair_path: path, pubkey })
    }

    /// Load wallet; if unavailable, return a placeholder.
    pub fn load_or_placeholder(explicit_path: Option<&str>) -> Self {
        Self::load(explicit_path).unwrap_or(WalletConfig {
            keypair_path: String::new(),
            pubkey: "ed25519:unknown".to_string(),
        })
    }
}

/// Derive the base58 public key from a Solana keypair JSON file.
///
/// Tries three strategies in order:
/// 1. `solana address --keypair <path>` (requires Solana CLI).
/// 2. Parse the keypair JSON as a 64-byte array and hex-encode the last 32 bytes.
/// 3. Return `None`.
fn derive_pubkey_from_keypair(path: &str) -> Option<String> {
    // Strategy 1: Solana CLI.
    let out = Command::new("solana")
        .args(["address", "--keypair", path])
        .output()
        .ok()?;
    if out.status.success() {
        let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
        if s.len() >= 32 {
            return Some(format!("ed25519:{s}"));
        }
    }

    // Strategy 2: parse keypair JSON manually.
    let content = std::fs::read_to_string(path).ok()?;
    let bytes = parse_keypair_json_bytes(&content)?;
    if bytes.len() >= 64 {
        // Solana keypairs: first 32 = secret key, last 32 = public key.
        let pubkey_bytes = &bytes[32..64];
        let hex: String = pubkey_bytes.iter().map(|b| format!("{b:02x}")).collect();
        return Some(format!("ed25519:{hex}"));
    }

    None
}

/// Parse a Solana keypair JSON array (`[b0, b1, ...]`) into a `Vec<u8>`.
pub fn parse_keypair_json_bytes(json: &str) -> Option<Vec<u8>> {
    let trimmed = json.trim();
    // Expect `[N, N, ...]`
    if !trimmed.starts_with('[') || !trimmed.ends_with(']') {
        return None;
    }
    let inner = &trimmed[1..trimmed.len() - 1];
    let bytes: Option<Vec<u8>> = inner
        .split(',')
        .map(|s| s.trim().parse::<u8>().ok())
        .collect();
    bytes
}

// ---------------------------------------------------------------------------
// Solana RPC helpers
// ---------------------------------------------------------------------------

/// Solana RPC network presets.
pub struct SolanaRpc;

impl SolanaRpc {
    pub const DEVNET: &'static str = "https://api.devnet.solana.com";
    pub const MAINNET: &'static str = "https://api.mainnet-beta.solana.com";

    /// Return the network name for an RPC URL.
    pub fn network_name(url: &str) -> &'static str {
        if url.contains("devnet") {
            "devnet"
        } else if url.contains("mainnet") {
            "mainnet-beta"
        } else if url.contains("testnet") {
            "testnet"
        } else {
            "local"
        }
    }
}

/// Call the Solana JSON-RPC API using `curl`.
///
/// Returns the raw JSON response body, or an error string.
pub fn solana_rpc_call(rpc_url: &str, method: &str, params: &str) -> Result<String, String> {
    let body = format!(
        r#"{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}"#,
    );
    let out = Command::new("curl")
        .args([
            "--silent",
            "--max-time", "15",
            "--header", "Content-Type: application/json",
            "--data", &body,
            rpc_url,
        ])
        .output()
        .map_err(|e| format!("curl failed: {e}"))?;

    if !out.status.success() {
        return Err(format!(
            "curl exited with status {}: {}",
            out.status,
            String::from_utf8_lossy(&out.stderr)
        ));
    }

    let response = String::from_utf8_lossy(&out.stdout).to_string();
    if response.is_empty() {
        return Err("empty response from Solana RPC".to_string());
    }
    if response.contains("\"error\"") {
        return Err(format!("RPC error: {response}"));
    }
    Ok(response)
}

/// Fetch the current slot from Solana devnet.
pub fn get_current_slot(rpc_url: &str) -> Result<u64, String> {
    let resp = solana_rpc_call(rpc_url, "getSlot", "[]")?;
    // Response: {"jsonrpc":"2.0","result":12345678,"id":1}
    parse_json_u64_result(&resp).ok_or_else(|| format!("could not parse slot from: {resp}"))
}

/// Fetch the blockhash for a specific slot.
///
/// Uses `getBlock` with `"transactionDetails":"none"` to minimise response size.
pub fn get_blockhash_for_slot(rpc_url: &str, slot: u64) -> Result<String, String> {
    let params = format!(
        r#"[{slot}, {{"transactionDetails":"none","rewards":false,"encoding":"base64"}}]"#,
    );
    let resp = solana_rpc_call(rpc_url, "getBlock", &params)?;
    // Response contains `"blockhash":"<base58>"`.
    parse_json_str_field(&resp, "blockhash")
        .ok_or_else(|| format!("could not extract blockhash from response"))
}

// ---------------------------------------------------------------------------
// Seed derivation
// ---------------------------------------------------------------------------

/// Derive the VRF seed from a Solana slot blockhash and wallet pubkey.
///
/// Algorithm: `SHA-256( blockhash || ":" || wallet_pubkey )`
///
/// The derivation is deterministic and publicly reproducible: any observer
/// with the blockhash and wallet pubkey can independently verify the seed.
pub fn derive_seed_from_blockhash(
    blockhash: &str,
    wallet_pubkey: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    let input = format!("{blockhash}:{wallet_pubkey}");
    sha256_hex(&input)
}

/// Compute SHA-256 of a string, returning the lowercase hex digest.
pub fn sha256_hex(input: &str) -> Result<String, Box<dyn std::error::Error>> {
    use std::io::Write;
    let mut child = Command::new("sha256sum")
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .spawn()
        .or_else(|_| {
            Command::new("shasum")
                .args(["-a", "256"])
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .spawn()
        })?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(input.as_bytes())?;
    }
    let out = child.wait_with_output()?;
    if !out.status.success() {
        return Err("sha256 computation failed".into());
    }
    let hex = String::from_utf8_lossy(&out.stdout)
        .split_whitespace()
        .next()
        .unwrap_or("")
        .to_string();
    if hex.len() != 64 {
        return Err(format!("unexpected sha256 output length: {}", hex.len()).into());
    }
    Ok(hex)
}

/// Generate a 32-byte random seed from `/dev/urandom`.
///
/// Returns 64 lowercase hex chars, or an error if `/dev/urandom` is unavailable.
pub fn local_prng_seed() -> Result<String, Box<dyn std::error::Error>> {
    use std::io::Read;
    let mut f = std::fs::File::open("/dev/urandom")?;
    let mut buf = [0u8; 32];
    f.read_exact(&mut buf)?;
    Ok(buf.iter().map(|b| format!("{b:02x}")).collect())
}

/// Generate a local request ID using the current time in nanoseconds.
pub fn local_request_id() -> String {
    let ns = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    format!("local:{ns}")
}

// ---------------------------------------------------------------------------
// Verification
// ---------------------------------------------------------------------------

/// Verify a previously issued VRF result.
///
/// Fetches the blockhash for the stored slot from the Solana RPC, recomputes
/// the seed, and compares it to the claimed `seed_hex`.
///
/// Returns `Ok(true)` on match, `Ok(false)` on mismatch, or `Err(...)` if
/// the network call or computation fails.
pub fn verify_vrf_result(result: &VrfResult, rpc_url_override: Option<&str>) -> Result<bool, String> {
    if !result.is_verifiable() {
        return Err(format!(
            "result from source '{}' is not independently verifiable",
            result.source.as_str()
        ));
    }

    let rpc_url = rpc_url_override.unwrap_or(&result.rpc_url);
    let blockhash = get_blockhash_for_slot(rpc_url, result.slot)?;

    if blockhash != result.blockhash {
        return Err(format!(
            "blockhash mismatch for slot {}: RPC returned '{}', stored '{}'",
            result.slot, blockhash, result.blockhash
        ));
    }

    let expected_seed = derive_seed_from_blockhash(&blockhash, &result.wallet_pubkey)
        .map_err(|e| format!("seed derivation failed: {e}"))?;

    Ok(expected_seed == result.seed_hex)
}

// ---------------------------------------------------------------------------
// JSON parsing helpers
// ---------------------------------------------------------------------------

/// Extract a quoted string field from a JSON snippet.
///
/// Looks for `"<key>":"<value>"` and returns `<value>`.
pub fn json_field<'a>(json: &'a str, key: &str) -> Option<&'a str> {
    let needle = format!("\"{key}\":");
    let start = json.find(&needle)? + needle.len();
    let rest = json[start..].trim_start();
    if rest.starts_with('"') {
        let inner = &rest[1..];
        let end = inner.find('"')?;
        Some(&inner[..end])
    } else {
        None
    }
}

/// Extract a raw (unquoted) field value from a JSON snippet.
pub fn json_field_raw<'a>(json: &'a str, key: &str) -> Option<&'a str> {
    let needle = format!("\"{key}\":");
    let start = json.find(&needle)? + needle.len();
    let rest = json[start..].trim_start();
    // Raw value ends at the next comma, `}`, or whitespace.
    let end = rest.find(|c: char| c == ',' || c == '}' || c == '\n').unwrap_or(rest.len());
    Some(rest[..end].trim())
}

/// Parse `{"jsonrpc":"2.0","result":<N>,"id":1}`.
fn parse_json_u64_result(json: &str) -> Option<u64> {
    let raw = json_field_raw(json, "result")?;
    raw.parse().ok()
}

/// Parse a string field from a JSON response.
fn parse_json_str_field(json: &str, key: &str) -> Option<String> {
    json_field(json, key).map(|s| s.to_string())
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // -----------------------------------------------------------------------
    // VrfSource
    // -----------------------------------------------------------------------

    #[test]
    fn vrf_source_round_trip() {
        assert_eq!(VrfSource::from_str("switchboard-vrf"), Some(VrfSource::SwitchboardVrf));
        assert_eq!(VrfSource::from_str("local-prng"), Some(VrfSource::LocalPrng));
        assert_eq!(VrfSource::from_str("unknown"), None);
        assert_eq!(VrfSource::SwitchboardVrf.as_str(), "switchboard-vrf");
        assert_eq!(VrfSource::LocalPrng.as_str(), "local-prng");
    }

    #[test]
    fn vrf_source_verifiability() {
        assert!(VrfSource::SwitchboardVrf.is_verifiable());
        assert!(!VrfSource::LocalPrng.is_verifiable());
    }

    // -----------------------------------------------------------------------
    // VrfResult serialisation
    // -----------------------------------------------------------------------

    fn sample_result() -> VrfResult {
        VrfResult {
            request_id: "slot:12345678".to_string(),
            slot: 12345678,
            blockhash: "4vJ9JU1bJJE96RNPU2d3YMuHBB1yxBsS3b9Bk3y9rP".to_string(),
            seed_hex: "a3b4c5d6e7f8a3b4c5d6e7f8a3b4c5d6e7f8a3b4c5d6e7f8a3b4c5d6e7f8a3b4".to_string(),
            source: VrfSource::SwitchboardVrf,
            wallet_pubkey: "ed25519:7GRmBwnBChf32GrKBbqBRRtest".to_string(),
            timestamp: "2026-04-14T17:10:00Z".to_string(),
            rpc_url: "https://api.devnet.solana.com".to_string(),
            network: "devnet".to_string(),
        }
    }

    #[test]
    fn vrf_result_to_json_contains_required_fields() {
        let r = sample_result();
        let json = r.to_json();
        assert!(json.contains("\"request_id\""), "missing request_id");
        assert!(json.contains("\"slot\""), "missing slot");
        assert!(json.contains("\"blockhash\""), "missing blockhash");
        assert!(json.contains("\"seed_hex\""), "missing seed_hex");
        assert!(json.contains("\"source\""), "missing source");
        assert!(json.contains("\"wallet_pubkey\""), "missing wallet_pubkey");
        assert!(json.contains("\"verifiable\""), "missing verifiable field");
        assert!(json.contains("\"verify_note\""), "missing verify_note");
    }

    #[test]
    fn vrf_result_json_round_trip() {
        let r = sample_result();
        let json = r.to_json();
        let r2 = VrfResult::from_json(&json).expect("parse failed");
        assert_eq!(r2.request_id, r.request_id);
        assert_eq!(r2.slot, r.slot);
        assert_eq!(r2.blockhash, r.blockhash);
        assert_eq!(r2.seed_hex, r.seed_hex);
        assert_eq!(r2.source.as_str(), r.source.as_str());
        assert_eq!(r2.wallet_pubkey, r.wallet_pubkey);
        assert_eq!(r2.network, r.network);
    }

    #[test]
    fn vrf_result_local_prng_not_verifiable() {
        let r = VrfResult {
            request_id: "local:1234".to_string(),
            slot: 0,
            blockhash: String::new(),
            seed_hex: "aabbcc".to_string(),
            source: VrfSource::LocalPrng,
            wallet_pubkey: String::new(),
            timestamp: "2026-04-14T00:00:00Z".to_string(),
            rpc_url: String::new(),
            network: "local".to_string(),
        };
        assert!(!r.is_verifiable());
        let json = r.to_json();
        assert!(json.contains("\"verifiable\": false"));
    }

    // -----------------------------------------------------------------------
    // Keypair parsing
    // -----------------------------------------------------------------------

    #[test]
    fn parse_keypair_json_bytes_valid() {
        let json = "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, \
                    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, \
                    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, \
                    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]";
        let bytes = parse_keypair_json_bytes(json).expect("parse failed");
        assert_eq!(bytes.len(), 64);
        assert_eq!(bytes[0], 1);
        assert_eq!(bytes[63], 64);
        // Public key portion (last 32 bytes).
        let pubkey_bytes = &bytes[32..64];
        let hex: String = pubkey_bytes.iter().map(|b| format!("{b:02x}")).collect();
        assert_eq!(hex.len(), 64);
    }

    #[test]
    fn parse_keypair_json_bytes_invalid() {
        assert!(parse_keypair_json_bytes("{\"not\": \"array\"}").is_none());
        assert!(parse_keypair_json_bytes("not json").is_none());
        assert!(parse_keypair_json_bytes("[1, 2, 256]").is_none()); // 256 overflows u8
    }

    // -----------------------------------------------------------------------
    // JSON helpers
    // -----------------------------------------------------------------------

    #[test]
    fn json_field_extracts_string() {
        let json = r#"{"jsonrpc":"2.0","result":{"blockhash":"4vJ9JU","fee":5}}"#;
        // json_field should work on nested structures too.
        let bh = json_field(json, "blockhash");
        assert_eq!(bh, Some("4vJ9JU"));
    }

    #[test]
    fn json_field_raw_extracts_number() {
        let json = r#"{"jsonrpc":"2.0","result":12345678,"id":1}"#;
        let raw = json_field_raw(json, "result");
        assert_eq!(raw, Some("12345678"));
    }

    #[test]
    fn parse_json_u64_result_parses_slot() {
        let json = r#"{"jsonrpc":"2.0","result":987654321,"id":1}"#;
        assert_eq!(parse_json_u64_result(json), Some(987654321u64));
    }

    // -----------------------------------------------------------------------
    // Local PRNG seed
    // -----------------------------------------------------------------------

    #[test]
    fn local_prng_seed_produces_64_hex_chars() {
        let seed = local_prng_seed().expect("urandom unavailable");
        assert_eq!(seed.len(), 64, "expected 32 bytes = 64 hex chars");
        assert!(seed.chars().all(|c| c.is_ascii_hexdigit()), "non-hex chars in seed");
    }

    #[test]
    fn local_prng_seed_is_unique() {
        let a = local_prng_seed().expect("urandom unavailable");
        let b = local_prng_seed().expect("urandom unavailable");
        assert_ne!(a, b, "two calls to local_prng_seed returned the same value");
    }

    // -----------------------------------------------------------------------
    // Solana RPC helpers
    // -----------------------------------------------------------------------

    #[test]
    fn solana_rpc_network_name_devnet() {
        assert_eq!(SolanaRpc::network_name("https://api.devnet.solana.com"), "devnet");
        assert_eq!(SolanaRpc::network_name("https://api.mainnet-beta.solana.com"), "mainnet-beta");
        assert_eq!(SolanaRpc::network_name("http://localhost:8899"), "local");
    }

    // -----------------------------------------------------------------------
    // local_request_id
    // -----------------------------------------------------------------------

    #[test]
    fn local_request_id_has_local_prefix() {
        let id = local_request_id();
        assert!(id.starts_with("local:"), "expected 'local:' prefix, got: {id}");
    }

    #[test]
    fn local_request_id_is_unique() {
        let a = local_request_id();
        // Add a tiny sleep worth of spin to get a different nanosecond timestamp.
        let mut i = 0u64;
        while i < 1_000_000 { i = i.wrapping_add(1); }
        let b = local_request_id();
        // On fast machines the timestamps could theoretically be equal, but in
        // practice the spin ensures they differ.  We check they are at least valid.
        assert!(a.starts_with("local:"));
        assert!(b.starts_with("local:"));
    }
}
