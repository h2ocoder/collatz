/// Bounty data model and predicate language for Emanon's universe market.
///
/// A bounty describes a constraint that a mined universe must satisfy, expressed
/// as a JSON-AST predicate tree.  Miners run [`verify_predicate`] against their
/// candidate repo to check eligibility before submitting a bid.
///
/// # Wire format (bounty JSON)
///
/// ```json
/// {
///   "id": "550e8400-e29b-41d4-a716-446655440000",
///   "buyer_pubkey": "ed25519:<base58-key>",
///   "constraint": { "snapshot_count_at_least": 5 },
///   "max_price_usdc": 3.50,
///   "expires_at": "2026-05-01T00:00:00Z",
///   "starter_seed_source": "switchboard-vrf",
///   "deliverable_format": "git-bundle",
///   "min_miner_reputation": 0,
///   "created_at": "2026-04-14T00:00:00Z"
/// }
/// ```
///
/// # Predicate language v1
///
/// The `constraint` field is a JSON-AST predicate.  Supported atoms:
///
/// * `{"path_exists": "regions/alpha/planet.json"}`
/// * `{"file_contains": ["path", "substring"]}`
/// * `{"jq": ["path", ".field == value"]}` — evaluates via the `jq` binary
/// * `{"snapshot_count_at_least": N}`
/// * `{"genus_present": {"set_k": 13}}` — at least one file written with this genus
/// * `{"merge_count_at_least": N}`
///
/// Logical combinators:
///
/// * `{"and": [p1, p2, ...]}`
/// * `{"or": [p1, p2, ...]}`
/// * `{"not": p}`

use std::path::{Path, PathBuf};
use std::process::Command;

// ---------------------------------------------------------------------------
// Bounty data model
// ---------------------------------------------------------------------------

/// Seed source for the verifiable random seed committed before mining.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SeedSource {
    SwitchboardVrf,
    Drand,
    BlockHash,
}

impl SeedSource {
    pub fn as_str(&self) -> &'static str {
        match self {
            SeedSource::SwitchboardVrf => "switchboard-vrf",
            SeedSource::Drand => "drand",
            SeedSource::BlockHash => "block-hash",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "switchboard-vrf" => Some(SeedSource::SwitchboardVrf),
            "drand" => Some(SeedSource::Drand),
            "block-hash" => Some(SeedSource::BlockHash),
            _ => None,
        }
    }
}

/// Deliverable format for a mined universe.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DeliverableFormat {
    GitBundle,
}

impl DeliverableFormat {
    pub fn as_str(&self) -> &'static str {
        "git-bundle"
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "git-bundle" => Some(DeliverableFormat::GitBundle),
            _ => None,
        }
    }
}

/// A posted bounty.  All fields correspond 1-to-1 with the wire JSON.
#[derive(Debug, Clone)]
pub struct Bounty {
    /// UUID v4 identifier.
    pub id: String,
    /// Ed25519 public key of the buyer: `"ed25519:<base58>"`.
    pub buyer_pubkey: String,
    /// The predicate constraint the mined universe must satisfy.
    pub constraint: Predicate,
    /// Maximum price the buyer will pay, in USDC.
    pub max_price_usdc: f64,
    /// ISO-8601 expiry timestamp.
    pub expires_at: String,
    /// Verifiable random seed source.
    pub starter_seed_source: SeedSource,
    /// Expected deliverable format.
    pub deliverable_format: DeliverableFormat,
    /// Minimum miner reputation score (0 = no restriction).
    pub min_miner_reputation: u64,
    /// ISO-8601 creation timestamp.
    pub created_at: String,
}

impl Bounty {
    /// Serialize to a JSON string (hand-rolled, no serde dep).
    pub fn to_json(&self) -> String {
        format!(
            r#"{{
  "id": "{id}",
  "buyer_pubkey": "{buyer}",
  "constraint": {constraint},
  "max_price_usdc": {price:.2},
  "expires_at": "{expires}",
  "starter_seed_source": "{seed}",
  "deliverable_format": "{fmt}",
  "min_miner_reputation": {rep},
  "created_at": "{created}"
}}"#,
            id = self.id,
            buyer = self.buyer_pubkey,
            constraint = self.constraint.to_json(),
            price = self.max_price_usdc,
            expires = self.expires_at,
            seed = self.starter_seed_source.as_str(),
            fmt = self.deliverable_format.as_str(),
            rep = self.min_miner_reputation,
            created = self.created_at,
        )
    }

    /// Parse a bounty from a JSON string.
    /// Returns `None` if required fields are missing or malformed.
    pub fn from_json(json: &str) -> Option<Self> {
        let id = json_str_field(json, "id")?.to_string();
        let buyer_pubkey = json_str_field(json, "buyer_pubkey")?.to_string();
        let expires_at = json_str_field(json, "expires_at")?.to_string();
        let created_at = json_str_field(json, "created_at")?.to_string();
        let seed_str = json_str_field(json, "starter_seed_source")?;
        let starter_seed_source = SeedSource::from_str(seed_str)?;
        let fmt_str = json_str_field(json, "deliverable_format")?;
        let deliverable_format = DeliverableFormat::from_str(fmt_str)?;
        let min_miner_reputation = json_u64_field(json, "min_miner_reputation").unwrap_or(0);
        let max_price_usdc = json_f64_field(json, "max_price_usdc").unwrap_or(0.0);
        let constraint_raw = json_obj_field(json, "constraint")?;
        let constraint = Predicate::from_json(constraint_raw)?;

        Some(Bounty {
            id,
            buyer_pubkey,
            constraint,
            max_price_usdc,
            expires_at,
            starter_seed_source,
            deliverable_format,
            min_miner_reputation,
            created_at,
        })
    }
}

// ---------------------------------------------------------------------------
// Predicate language v1
// ---------------------------------------------------------------------------

/// A predicate in the bounty constraint language.
///
/// Each variant corresponds directly to a JSON object key.
#[derive(Debug, Clone)]
pub enum Predicate {
    /// Check that a path exists in the repo (relative to repo root).
    PathExists { path: String },

    /// Check that a file contains a specific substring.
    FileContains { path: String, substring: String },

    /// Evaluate a `jq` filter against a JSON file.  Returns true if `jq`
    /// exits 0 and prints a truthy JSON value.
    Jq { path: String, filter: String },

    /// The universe has at least N snapshots committed.
    SnapshotCountAtLeast { n: u64 },

    /// At least one file in the repo was written with a given Collatz genus.
    GenusPresentSetK { set_k: u64 },

    /// The repo has at least N merge commits.
    MergeCountAtLeast { n: u64 },

    /// All child predicates must be true.
    And { children: Vec<Predicate> },

    /// At least one child predicate must be true.
    Or { children: Vec<Predicate> },

    /// The child predicate must be false.
    Not { child: Box<Predicate> },
}

impl Predicate {
    /// Serialize this predicate to a compact JSON string.
    pub fn to_json(&self) -> String {
        match self {
            Predicate::PathExists { path } => {
                format!(r#"{{"path_exists": "{path}"}}"#)
            }
            Predicate::FileContains { path, substring } => {
                format!(r#"{{"file_contains": ["{path}", "{sub}"]}}"#, sub = substring)
            }
            Predicate::Jq { path, filter } => {
                let f = filter.replace('"', "\\\"");
                format!(r#"{{"jq": ["{path}", "{f}"]}}"#)
            }
            Predicate::SnapshotCountAtLeast { n } => {
                format!(r#"{{"snapshot_count_at_least": {n}}}"#)
            }
            Predicate::GenusPresentSetK { set_k } => {
                format!(r#"{{"genus_present": {{"set_k": {set_k}}}}}"#)
            }
            Predicate::MergeCountAtLeast { n } => {
                format!(r#"{{"merge_count_at_least": {n}}}"#)
            }
            Predicate::And { children } => {
                let parts: Vec<String> = children.iter().map(|c| c.to_json()).collect();
                format!(r#"{{"and": [{}]}}"#, parts.join(", "))
            }
            Predicate::Or { children } => {
                let parts: Vec<String> = children.iter().map(|c| c.to_json()).collect();
                format!(r#"{{"or": [{}]}}"#, parts.join(", "))
            }
            Predicate::Not { child } => {
                format!(r#"{{"not": {}}}"#, child.to_json())
            }
        }
    }

    /// Parse a predicate from a JSON object string.
    ///
    /// Returns `None` if the string does not match any known predicate form.
    pub fn from_json(json: &str) -> Option<Self> {
        let json = json.trim();

        // path_exists
        if let Some(path) = json_str_field(json, "path_exists") {
            return Some(Predicate::PathExists { path: path.to_string() });
        }

        // snapshot_count_at_least
        if let Some(n) = json_u64_field(json, "snapshot_count_at_least") {
            return Some(Predicate::SnapshotCountAtLeast { n });
        }

        // merge_count_at_least
        if let Some(n) = json_u64_field(json, "merge_count_at_least") {
            return Some(Predicate::MergeCountAtLeast { n });
        }

        // genus_present — value is a sub-object {"set_k": N}
        if json.contains("\"genus_present\"") {
            if let Some(sub) = json_obj_field(json, "genus_present") {
                if let Some(k) = json_u64_field(sub, "set_k") {
                    return Some(Predicate::GenusPresentSetK { set_k: k });
                }
            }
        }

        // file_contains — value is a 2-element JSON array ["path", "substring"]
        if json.contains("\"file_contains\"") {
            if let Some((p, s)) = parse_two_string_array(json, "file_contains") {
                return Some(Predicate::FileContains { path: p, substring: s });
            }
        }

        // jq — value is a 2-element JSON array ["path", "filter"]
        if json.contains("\"jq\"") {
            if let Some((p, f)) = parse_two_string_array(json, "jq") {
                return Some(Predicate::Jq { path: p, filter: f });
            }
        }

        // and / or — value is a JSON array of predicate objects
        if json.contains("\"and\"") {
            if let Some(children) = parse_predicate_array(json, "and") {
                return Some(Predicate::And { children });
            }
        }

        if json.contains("\"or\"") {
            if let Some(children) = parse_predicate_array(json, "or") {
                return Some(Predicate::Or { children });
            }
        }

        // not — value is a single predicate object
        if json.contains("\"not\"") {
            if let Some(inner) = json_nested_obj(json, "not") {
                if let Some(child) = Predicate::from_json(inner) {
                    return Some(Predicate::Not { child: Box::new(child) });
                }
            }
        }

        None
    }
}

// ---------------------------------------------------------------------------
// Predicate evaluator
// ---------------------------------------------------------------------------

/// Evaluate a predicate against a git repository at `repo_root`.
///
/// All file paths in predicates are treated as relative to `repo_root`.
/// Returns `true` if the predicate is satisfied, `false` otherwise (including
/// on I/O errors — a repo that can't be read fails conservatively).
pub fn verify_predicate(repo_root: &Path, predicate: &Predicate) -> bool {
    match predicate {
        Predicate::PathExists { path } => {
            repo_root.join(path).exists()
        }

        Predicate::FileContains { path, substring } => {
            let full = repo_root.join(path);
            match std::fs::read_to_string(&full) {
                Ok(content) => content.contains(substring.as_str()),
                Err(_) => false,
            }
        }

        Predicate::Jq { path, filter } => {
            let full = repo_root.join(path);
            if !full.exists() {
                return false;
            }
            let out = Command::new("jq")
                .arg("-e")
                .arg(filter)
                .arg(&full)
                .output();
            match out {
                Ok(o) => o.status.success(),
                Err(_) => false, // jq not available — conservative fail
            }
        }

        Predicate::SnapshotCountAtLeast { n } => {
            let count_file = repo_root.join(".gitverse/snapshot_count");
            let count: u64 = std::fs::read_to_string(&count_file)
                .ok()
                .and_then(|s| s.trim().parse().ok())
                .unwrap_or(0);
            count >= *n
        }

        Predicate::GenusPresentSetK { set_k } => {
            genus_present_in_repo(repo_root, *set_k)
        }

        Predicate::MergeCountAtLeast { n } => {
            let out = Command::new("git")
                .args(["rev-list", "--count", "--merges", "HEAD"])
                .current_dir(repo_root)
                .output();
            match out {
                Ok(o) if o.status.success() => {
                    let s = String::from_utf8_lossy(&o.stdout);
                    let count: u64 = s.trim().parse().unwrap_or(0);
                    count >= *n
                }
                _ => false,
            }
        }

        Predicate::And { children } => {
            children.iter().all(|c| verify_predicate(repo_root, c))
        }

        Predicate::Or { children } => {
            children.iter().any(|c| verify_predicate(repo_root, c))
        }

        Predicate::Not { child } => {
            !verify_predicate(repo_root, child)
        }
    }
}

// ---------------------------------------------------------------------------
// Internal helpers — genus scan
// ---------------------------------------------------------------------------

/// Walk `regions/` in the repo and look for any file that has a genus stamp
/// with `set_k == target_k`.
fn genus_present_in_repo(repo_root: &Path, target_k: u64) -> bool {
    let regions = repo_root.join("regions");
    if !regions.is_dir() {
        return false;
    }
    genus_scan_dir(&regions, target_k)
}

fn genus_scan_dir(dir: &Path, target_k: u64) -> bool {
    let entries = match std::fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return false,
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            if genus_scan_dir(&path, target_k) {
                return true;
            }
        } else if path.is_file() {
            if genus_stamp_matches(&path, target_k) {
                return true;
            }
        }
    }
    false
}

/// Return true if the file (or its `.genus` sidecar) contains an emanon-genus
/// stamp with `set_k == target_k`.
fn genus_stamp_matches(path: &Path, target_k: u64) -> bool {
    // Check text file itself.
    if let Ok(content) = std::fs::read_to_string(path) {
        for line in content.lines() {
            if let Some(k) = extract_set_k_from_stamp(line) {
                if k == target_k {
                    return true;
                }
            }
        }
    }
    // Check binary sidecar.  cmd_write creates the sidecar at "{original_path}.genus"
    // (e.g. "data/image.png" → "data/image.png.genus"), so we mirror that exactly.
    let sidecar = path.to_str()
        .map(|s| PathBuf::from(format!("{}.genus", s)))
        .unwrap_or_else(|| path.with_extension("genus"));
    if let Ok(content) = std::fs::read_to_string(&sidecar) {
        for line in content.lines() {
            if let Some(k) = extract_set_k_from_stamp(line) {
                if k == target_k {
                    return true;
                }
            }
        }
    }
    false
}

/// Try to extract `set_k` from a genus stamp line.
///
/// Handles both the legacy M1.2 format (`# emanon:genus set_k=K ...`) and
/// the JSON format (`# emanon-genus: {"set_k": K, ...}`).
fn extract_set_k_from_stamp(line: &str) -> Option<u64> {
    // JSON format: # emanon-genus: {...}
    if line.contains("emanon-genus:") {
        if let Some(brace_pos) = line.find('{') {
            let json_part = &line[brace_pos..];
            return json_u64_field(json_part, "set_k");
        }
    }
    // Legacy format: # emanon:genus set_k=K ...
    if line.contains("emanon:genus") {
        for token in line.split_whitespace() {
            if let Some(val) = token.strip_prefix("set_k=") {
                return val.parse().ok();
            }
        }
    }
    None
}

// ---------------------------------------------------------------------------
// JSON parsing helpers (no serde dep — consistent with rest of codebase)
// ---------------------------------------------------------------------------

/// Extract a `"key": "value"` string field from a JSON object string.
pub fn json_str_field<'a>(obj: &'a str, key: &str) -> Option<&'a str> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    if after.starts_with('"') {
        let inner = &after[1..];
        let end = inner.find('"')?;
        Some(&inner[..end])
    } else {
        None
    }
}

/// Extract a `"key": N` integer field from a JSON object string.
pub fn json_u64_field(obj: &str, key: &str) -> Option<u64> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    let digits: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
    digits.parse().ok()
}

/// Extract a `"key": N.N` float field from a JSON object string.
pub fn json_f64_field(obj: &str, key: &str) -> Option<f64> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    let num: String = after
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '.')
        .collect();
    num.parse().ok()
}

/// Extract the raw text of a `"key": { ... }` nested object (just the `{...}` part).
pub fn json_obj_field<'a>(obj: &'a str, key: &str) -> Option<&'a str> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    if after.starts_with('{') {
        find_matching_brace(after)
    } else {
        None
    }
}

/// Return the slice `{...}` starting at `s` (which must start with `{`),
/// balanced to the matching closing brace.
fn find_matching_brace(s: &str) -> Option<&str> {
    let mut depth = 0usize;
    let mut in_str = false;
    let mut escape = false;
    for (i, ch) in s.char_indices() {
        if escape {
            escape = false;
            continue;
        }
        if in_str {
            if ch == '\\' {
                escape = true;
            } else if ch == '"' {
                in_str = false;
            }
            continue;
        }
        match ch {
            '"' => in_str = true,
            '{' => depth += 1,
            '}' => {
                depth -= 1;
                if depth == 0 {
                    return Some(&s[..=i]);
                }
            }
            _ => {}
        }
    }
    None
}

/// Return the slice `{...}` for the value of a key whose value is an object.
/// Alias that accepts the parent JSON as the source.
fn json_nested_obj<'a>(parent: &'a str, key: &str) -> Option<&'a str> {
    json_obj_field(parent, key)
}

/// Parse `"key": ["string1", "string2"]` into `(String, String)`.
fn parse_two_string_array(obj: &str, key: &str) -> Option<(String, String)> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    if !after.starts_with('[') {
        return None;
    }
    // Extract the two quoted strings in the array, e.g. `["path", "value"]`.
    // rest_start: 1 (for '[') + 1 (opening '"') + content_len + 1 (closing '"')
    let first = extract_next_string(&after[1..])?;
    let rest_start = 1 + 1 + first.len() + 1;
    let rest = after.get(rest_start..)?;
    let comma_pos = rest.find(',')?;
    let second_part = rest[comma_pos + 1..].trim_start();
    let second = extract_next_string_val(second_part)?;
    Some((first, second))
}

/// Extract the content of the first `"..."` in `s` (after the leading `"`).
fn extract_next_string(s: &str) -> Option<String> {
    let s = s.trim_start();
    if !s.starts_with('"') {
        return None;
    }
    let inner = &s[1..];
    let mut result = String::new();
    let mut escape = false;
    for ch in inner.chars() {
        if escape {
            result.push(ch);
            escape = false;
        } else if ch == '\\' {
            escape = true;
        } else if ch == '"' {
            return Some(result);
        } else {
            result.push(ch);
        }
    }
    None
}

/// Extract the value of the first `"..."` token in `s`.
fn extract_next_string_val(s: &str) -> Option<String> {
    extract_next_string(s)
}

/// Parse `"key": [p1, p2, ...]` where each element is a predicate object.
fn parse_predicate_array(obj: &str, key: &str) -> Option<Vec<Predicate>> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    if !after.starts_with('[') {
        return None;
    }
    // Walk through the array, extracting each top-level `{...}` object.
    let inner = &after[1..]; // skip '['
    let mut result = Vec::new();
    let mut rest = inner.trim_start();
    while rest.starts_with('{') {
        let obj_str = find_matching_brace(rest)?;
        if let Some(p) = Predicate::from_json(obj_str) {
            result.push(p);
        }
        rest = &rest[obj_str.len()..].trim_start();
        if rest.starts_with(',') {
            rest = rest[1..].trim_start();
        } else {
            break;
        }
    }
    Some(result)
}

// ---------------------------------------------------------------------------
// Predicate utility helpers
// ---------------------------------------------------------------------------

/// Return `true` if the predicate tree contains at least one node of `kind`.
///
/// Kind strings match the JSON key names:
/// `"path_exists"`, `"file_contains"`, `"jq"`, `"snapshot_count_at_least"`,
/// `"genus_present"`, `"merge_count_at_least"`, `"and"`, `"or"`, `"not"`.
pub fn predicate_includes_kind(predicate: &Predicate, kind: &str) -> bool {
    match predicate {
        Predicate::PathExists { .. } => kind == "path_exists",
        Predicate::FileContains { .. } => kind == "file_contains",
        Predicate::Jq { .. } => kind == "jq",
        Predicate::SnapshotCountAtLeast { .. } => kind == "snapshot_count_at_least",
        Predicate::GenusPresentSetK { .. } => kind == "genus_present",
        Predicate::MergeCountAtLeast { .. } => kind == "merge_count_at_least",
        Predicate::And { children } => {
            kind == "and" || children.iter().any(|c| predicate_includes_kind(c, kind))
        }
        Predicate::Or { children } => {
            kind == "or" || children.iter().any(|c| predicate_includes_kind(c, kind))
        }
        Predicate::Not { child } => {
            kind == "not" || predicate_includes_kind(child, kind)
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    // -----------------------------------------------------------------------
    // Helper: create a temporary directory and return its path.
    // (We can't use tempfile crate — no dep — so we use a manual approach.)
    // -----------------------------------------------------------------------
    fn tmp_dir(suffix: &str) -> PathBuf {
        let base = std::env::temp_dir().join(format!("emanon_bounty_test_{suffix}_{}", std::process::id()));
        fs::create_dir_all(&base).expect("create test tmp dir");
        base
    }

    fn cleanup(p: &Path) {
        let _ = fs::remove_dir_all(p);
    }

    // -----------------------------------------------------------------------
    // Predicate::from_json / to_json round-trips
    // -----------------------------------------------------------------------

    #[test]
    fn parse_path_exists() {
        let p = Predicate::from_json(r#"{"path_exists": "regions/alpha/planet.json"}"#).unwrap();
        assert!(matches!(p, Predicate::PathExists { .. }));
        if let Predicate::PathExists { path } = &p {
            assert_eq!(path, "regions/alpha/planet.json");
        }
    }

    #[test]
    fn round_trip_path_exists() {
        let p = Predicate::PathExists { path: "regions/beta/base.json".to_string() };
        let json = p.to_json();
        let p2 = Predicate::from_json(&json).unwrap();
        assert!(matches!(p2, Predicate::PathExists { .. }));
    }

    #[test]
    fn parse_snapshot_count() {
        let p = Predicate::from_json(r#"{"snapshot_count_at_least": 5}"#).unwrap();
        assert!(matches!(p, Predicate::SnapshotCountAtLeast { n: 5 }));
    }

    #[test]
    fn parse_merge_count() {
        let p = Predicate::from_json(r#"{"merge_count_at_least": 3}"#).unwrap();
        assert!(matches!(p, Predicate::MergeCountAtLeast { n: 3 }));
    }

    #[test]
    fn parse_genus_present() {
        let p = Predicate::from_json(r#"{"genus_present": {"set_k": 13}}"#).unwrap();
        assert!(matches!(p, Predicate::GenusPresentSetK { set_k: 13 }));
    }

    #[test]
    fn parse_file_contains() {
        let p = Predicate::from_json(r#"{"file_contains": ["README.md", "Emanon"]}"#).unwrap();
        if let Predicate::FileContains { path, substring } = &p {
            assert_eq!(path, "README.md");
            assert_eq!(substring, "Emanon");
        } else {
            panic!("wrong variant: {:?}", p);
        }
    }

    #[test]
    fn parse_and() {
        let p = Predicate::from_json(
            r#"{"and": [{"snapshot_count_at_least": 3}, {"merge_count_at_least": 1}]}"#,
        )
        .unwrap();
        if let Predicate::And { children } = &p {
            assert_eq!(children.len(), 2);
        } else {
            panic!("wrong variant");
        }
    }

    #[test]
    fn parse_or() {
        let p = Predicate::from_json(
            r#"{"or": [{"path_exists": "regions/a.json"}, {"path_exists": "regions/b.json"}]}"#,
        )
        .unwrap();
        assert!(matches!(p, Predicate::Or { .. }));
    }

    #[test]
    fn parse_not() {
        let p = Predicate::from_json(r#"{"not": {"path_exists": "regions/forbidden.json"}}"#)
            .unwrap();
        assert!(matches!(p, Predicate::Not { .. }));
    }

    // -----------------------------------------------------------------------
    // verify_predicate — filesystem-backed tests
    // -----------------------------------------------------------------------

    #[test]
    fn verify_path_exists_true() {
        let dir = tmp_dir("path_exists_true");
        fs::create_dir_all(dir.join("regions/alpha")).unwrap();
        fs::write(dir.join("regions/alpha/planet.json"), r#"{"name": "Earth"}"#).unwrap();

        let p = Predicate::PathExists { path: "regions/alpha/planet.json".to_string() };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_path_exists_false() {
        let dir = tmp_dir("path_exists_false");
        let p = Predicate::PathExists { path: "regions/alpha/planet.json".to_string() };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_file_contains_true() {
        let dir = tmp_dir("file_contains_true");
        fs::write(dir.join("README.md"), "Welcome to the Emanon multiverse!").unwrap();

        let p = Predicate::FileContains {
            path: "README.md".to_string(),
            substring: "Emanon".to_string(),
        };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_file_contains_false() {
        let dir = tmp_dir("file_contains_false");
        fs::write(dir.join("README.md"), "Hello world").unwrap();

        let p = Predicate::FileContains {
            path: "README.md".to_string(),
            substring: "Emanon".to_string(),
        };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_snapshot_count_at_least_true() {
        let dir = tmp_dir("snap_count_true");
        fs::create_dir_all(dir.join(".gitverse")).unwrap();
        fs::write(dir.join(".gitverse/snapshot_count"), "7").unwrap();

        let p = Predicate::SnapshotCountAtLeast { n: 5 };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_snapshot_count_at_least_false() {
        let dir = tmp_dir("snap_count_false");
        fs::create_dir_all(dir.join(".gitverse")).unwrap();
        fs::write(dir.join(".gitverse/snapshot_count"), "2").unwrap();

        let p = Predicate::SnapshotCountAtLeast { n: 5 };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_snapshot_count_missing_file() {
        let dir = tmp_dir("snap_count_missing");
        let p = Predicate::SnapshotCountAtLeast { n: 1 };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_genus_present_true() {
        let dir = tmp_dir("genus_present_true");
        fs::create_dir_all(dir.join("regions/alpha")).unwrap();
        let stamp = r#"# emanon-genus: {"set_k": 13, "oddity_s": 1, "index_i": 5, "writer": "test@example.com", "snapshot": 3}"#;
        fs::write(dir.join("regions/alpha/colony.json"), format!("{{}}\n{stamp}")).unwrap();

        let p = Predicate::GenusPresentSetK { set_k: 13 };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_genus_present_false() {
        let dir = tmp_dir("genus_present_false");
        fs::create_dir_all(dir.join("regions/alpha")).unwrap();
        let stamp = r#"# emanon-genus: {"set_k": 7, "oddity_s": 1, "index_i": 3, "writer": "test@example.com", "snapshot": 1}"#;
        fs::write(dir.join("regions/alpha/colony.json"), format!("{{}}\n{stamp}")).unwrap();

        let p = Predicate::GenusPresentSetK { set_k: 13 };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_genus_present_legacy_format() {
        let dir = tmp_dir("genus_legacy");
        fs::create_dir_all(dir.join("regions")).unwrap();
        fs::write(dir.join("regions/base.txt"), "content\n# emanon:genus set_k=5 oddity_s=2 index_i=1\n").unwrap();

        let p = Predicate::GenusPresentSetK { set_k: 5 };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_and_all_true() {
        let dir = tmp_dir("and_all_true");
        fs::create_dir_all(dir.join(".gitverse")).unwrap();
        fs::write(dir.join(".gitverse/snapshot_count"), "5").unwrap();
        fs::write(dir.join("README.md"), "Emanon").unwrap();

        let p = Predicate::And {
            children: vec![
                Predicate::SnapshotCountAtLeast { n: 3 },
                Predicate::FileContains { path: "README.md".to_string(), substring: "Emanon".to_string() },
            ],
        };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_and_one_false() {
        let dir = tmp_dir("and_one_false");
        fs::create_dir_all(dir.join(".gitverse")).unwrap();
        fs::write(dir.join(".gitverse/snapshot_count"), "1").unwrap();
        fs::write(dir.join("README.md"), "Emanon").unwrap();

        let p = Predicate::And {
            children: vec![
                Predicate::SnapshotCountAtLeast { n: 5 },
                Predicate::FileContains { path: "README.md".to_string(), substring: "Emanon".to_string() },
            ],
        };
        assert!(!verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_or_one_true() {
        let dir = tmp_dir("or_one_true");
        fs::write(dir.join("README.md"), "Emanon").unwrap();

        let p = Predicate::Or {
            children: vec![
                Predicate::PathExists { path: "nonexistent.json".to_string() },
                Predicate::FileContains { path: "README.md".to_string(), substring: "Emanon".to_string() },
            ],
        };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    #[test]
    fn verify_not_inverts() {
        let dir = tmp_dir("not_inverts");
        let p = Predicate::Not {
            child: Box::new(Predicate::PathExists { path: "nonexistent.json".to_string() }),
        };
        assert!(verify_predicate(&dir, &p));
        cleanup(&dir);
    }

    // -----------------------------------------------------------------------
    // Bounty from_json / to_json round-trip
    // -----------------------------------------------------------------------

    #[test]
    fn bounty_round_trip() {
        let json = r#"{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "buyer_pubkey": "ed25519:4mFra4",
  "constraint": {"snapshot_count_at_least": 5},
  "max_price_usdc": 3.50,
  "expires_at": "2026-05-01T00:00:00Z",
  "starter_seed_source": "switchboard-vrf",
  "deliverable_format": "git-bundle",
  "min_miner_reputation": 0,
  "created_at": "2026-04-14T00:00:00Z"
}"#;
        let bounty = Bounty::from_json(json).expect("parse bounty");
        assert_eq!(bounty.id, "550e8400-e29b-41d4-a716-446655440000");
        assert_eq!(bounty.min_miner_reputation, 0);
        assert!(matches!(bounty.constraint, Predicate::SnapshotCountAtLeast { n: 5 }));
        assert!(matches!(bounty.starter_seed_source, SeedSource::SwitchboardVrf));

        // Serialize and re-parse.
        let out = bounty.to_json();
        let b2 = Bounty::from_json(&out).expect("re-parse bounty");
        assert_eq!(b2.id, "550e8400-e29b-41d4-a716-446655440000");
    }

    #[test]
    fn bounty_from_json_drand_seed() {
        let json = r#"{"id":"abc","buyer_pubkey":"ed25519:x","constraint":{"path_exists":"regions/alpha.json"},"max_price_usdc":1.00,"expires_at":"2026-06-01T00:00:00Z","starter_seed_source":"drand","deliverable_format":"git-bundle","min_miner_reputation":0,"created_at":"2026-04-14T00:00:00Z"}"#;
        let b = Bounty::from_json(json).unwrap();
        assert!(matches!(b.starter_seed_source, SeedSource::Drand));
    }

    // -----------------------------------------------------------------------
    // predicate_includes_kind
    // -----------------------------------------------------------------------

    #[test]
    fn includes_kind_leaf_path_exists() {
        let p = Predicate::PathExists { path: "regions/x".into() };
        assert!(predicate_includes_kind(&p, "path_exists"));
        assert!(!predicate_includes_kind(&p, "snapshot_count_at_least"));
        assert!(!predicate_includes_kind(&p, "genus_present"));
    }

    #[test]
    fn includes_kind_leaf_snapshot() {
        let p = Predicate::SnapshotCountAtLeast { n: 3 };
        assert!(predicate_includes_kind(&p, "snapshot_count_at_least"));
        assert!(!predicate_includes_kind(&p, "path_exists"));
    }

    #[test]
    fn includes_kind_leaf_genus() {
        let p = Predicate::GenusPresentSetK { set_k: 7 };
        assert!(predicate_includes_kind(&p, "genus_present"));
        assert!(!predicate_includes_kind(&p, "merge_count_at_least"));
    }

    #[test]
    fn includes_kind_leaf_merge() {
        let p = Predicate::MergeCountAtLeast { n: 2 };
        assert!(predicate_includes_kind(&p, "merge_count_at_least"));
    }

    #[test]
    fn includes_kind_leaf_file_contains() {
        let p = Predicate::FileContains { path: "f".into(), substring: "s".into() };
        assert!(predicate_includes_kind(&p, "file_contains"));
    }

    #[test]
    fn includes_kind_leaf_jq() {
        let p = Predicate::Jq { path: "f.json".into(), filter: ".x".into() };
        assert!(predicate_includes_kind(&p, "jq"));
    }

    #[test]
    fn includes_kind_and_self() {
        let p = Predicate::And { children: vec![] };
        assert!(predicate_includes_kind(&p, "and"));
        assert!(!predicate_includes_kind(&p, "or"));
    }

    #[test]
    fn includes_kind_nested_in_and() {
        // and(path_exists, snapshot_count_at_least)
        let p = Predicate::And {
            children: vec![
                Predicate::PathExists { path: "regions/x".into() },
                Predicate::SnapshotCountAtLeast { n: 5 },
            ],
        };
        assert!(predicate_includes_kind(&p, "path_exists"));
        assert!(predicate_includes_kind(&p, "snapshot_count_at_least"));
        assert!(!predicate_includes_kind(&p, "genus_present"));
        assert!(predicate_includes_kind(&p, "and")); // the combinator itself
    }

    #[test]
    fn includes_kind_nested_in_not() {
        let p = Predicate::Not {
            child: Box::new(Predicate::GenusPresentSetK { set_k: 13 }),
        };
        assert!(predicate_includes_kind(&p, "genus_present"));
        assert!(predicate_includes_kind(&p, "not"));
        assert!(!predicate_includes_kind(&p, "path_exists"));
    }

    #[test]
    fn includes_kind_deeply_nested() {
        // or(and(path_exists, merge_count_at_least), genus_present)
        let p = Predicate::Or {
            children: vec![
                Predicate::And {
                    children: vec![
                        Predicate::PathExists { path: "f".into() },
                        Predicate::MergeCountAtLeast { n: 1 },
                    ],
                },
                Predicate::GenusPresentSetK { set_k: 3 },
            ],
        };
        assert!(predicate_includes_kind(&p, "or"));
        assert!(predicate_includes_kind(&p, "and"));
        assert!(predicate_includes_kind(&p, "path_exists"));
        assert!(predicate_includes_kind(&p, "merge_count_at_least"));
        assert!(predicate_includes_kind(&p, "genus_present"));
        assert!(!predicate_includes_kind(&p, "jq"));
        assert!(!predicate_includes_kind(&p, "not"));
    }
}
