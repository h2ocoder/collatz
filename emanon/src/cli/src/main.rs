use clap::{Parser, Subcommand};
use collatz_rs::beta;
use crossterm::{
    event::{self, Event, KeyCode, KeyModifiers},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, ListState, Paragraph},
    Terminal,
};
use std::io;
use std::path::Path;
use std::process::Command;

/// Emanon — git-based game engine for the multiverse
///
/// The Emanon CLI is the primary interface for human players and AI agents.
/// It wraps git with game semantics: repos are universes, branches are timelines,
/// merges are the Collatz merge driver.
#[derive(Parser)]
#[command(name = "emanon", version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize a new Emanon universe (git repo with canonical .gitverse layout)
    Init {
        /// Name for the new universe directory
        name: String,
        /// Override existing-directory check (will not re-initialize an existing universe)
        #[arg(long, short = 'f')]
        force: bool,
    },

    /// Capture the current state as a snapshot (commit)
    Snapshot {
        /// Optional message describing this snapshot
        #[arg(short = 'm', long)]
        message: Option<String>,
        /// Skip `git add -A`; only commit already-staged files
        #[arg(long)]
        no_stage: bool,
    },

    /// Merge a remote timeline using the Collatz merge driver
    Merge {
        /// Remote and branch in the form <remote>/<branch>
        remote_branch: String,
    },

    /// Interactively resolve conflicts left by `emanon merge`
    ///
    /// Opens a terminal UI showing every conflict in `.gitverse/pending-merge.json`
    /// and lets the user pick a resolution for each: battle, contract, fork, or manual.
    /// After all conflicts are resolved, creates a merge commit.
    ///
    /// Pass `--non-interactive` to drive resolution programmatically: provide a
    /// JSON array on stdin, one entry per conflict, e.g.:
    ///   [{"path":"regions/foo.json","resolution":"battle","force_size":512}]
    Negotiate {
        /// Accept a JSON resolution plan from stdin instead of opening the TUI
        #[arg(long)]
        non_interactive: bool,
    },

    /// Low-level Collatz merge driver (invoked by git via .gitattributes)
    ///
    /// Implements git's custom merge driver protocol.  Reads genus stamps
    /// from the base/ours/theirs files and applies one of three resolution
    /// paths:
    ///   1. Same set_k  → hybrid merge (both versions concatenated)
    ///   2. Same oddity_s, different set_k → genus-attenuated merge
    ///   3. Unrelated sets (or no genus stamp) → exit 1 (defer to player)
    ///
    /// Invoked automatically by git for paths registered in .gitattributes:
    ///   regions/**     merge=emanon-collatz    → emanon merge-driver %O %A %B %P
    ///   contracts/**   merge=emanon-contract   → emanon merge-driver --contract-mode %O %A %B %P
    ///   scars/**       merge=emanon-append-only→ emanon merge-driver --append-only %O %A %B %P
    MergeDriver {
        /// Contract merge mode — resolves conflicts under contracts/; full
        /// implementation arrives in a later milestone (stub: falls back to
        /// Collatz resolution with a diagnostic note).
        #[arg(long)]
        contract_mode: bool,
        /// Append-only merge mode — resolves conflicts under scars/; full
        /// implementation arrives in a later milestone (stub: falls back to
        /// Collatz resolution with a diagnostic note).
        #[arg(long)]
        append_only: bool,
        /// Ancestor version path (git %O)
        base: String,
        /// Our version path (git %A); merged result is written here
        ours: String,
        /// Their version path (git %B)
        theirs: String,
        /// The filename being merged (git %P); recorded for diagnostics
        path: String,
        /// Optional explicit output path (default: writes to <ours>)
        #[arg(short = 'o', long)]
        output: Option<String>,
    },

    /// Fork the current timeline into a parallel branch
    Fork {
        /// Reason for the fork (recorded in commit metadata)
        #[arg(short = 'r', long)]
        reason: Option<String>,
    },

    /// Manage Emanon contracts (agreements between players)
    Contract {
        #[command(subcommand)]
        action: ContractAction,
    },

    /// Write a file into the universe with an embedded Collatz genus stamp
    ///
    /// Stamps are derived from the current snapshot count and the file path,
    /// ensuring every file written in the same snapshot has a unique genus.
    /// Text files get a trailing `# emanon-genus: {...}` line; binary files
    /// (piped via stdin without a content argument) get a `<file>.genus` sidecar.
    ///
    /// Example:
    ///   emanon write regions/alpha/test.json '{"foo": 1}'
    Write {
        /// Path to write (relative to universe root)
        path: String,
        /// Text content to write (omit to read binary content from stdin)
        content: Option<String>,
    },

    /// Print the Collatz genus stamp embedded in a file
    ///
    /// Reads the file and extracts the `# emanon-genus:` stamp written by
    /// `emanon write`.  Exits 1 if no stamp is found.
    ///
    /// Example:
    ///   emanon genus regions/alpha/test.json
    Genus {
        /// Path to the file to inspect (relative to universe root)
        path: String,
    },

    /// Scan a remote universe for open bounties and forks
    Scan {
        /// Remote name or URL to scan
        remote: String,
    },

    /// Manage bounties (tasks offered for collaboration)
    Bounty {
        #[command(subcommand)]
        action: BountyAction,
    },

    /// Manage tournament participation
    Tournament {
        #[command(subcommand)]
        action: TournamentAction,
    },

    /// Interact with the Emanon registry (universe publishing)
    Registry {
        #[command(subcommand)]
        action: RegistryAction,
    },

    /// Validate the current universe against the canonical Emanon schema
    ///
    /// Checks that all required directories and files exist, that
    /// `.gitverse/values.json` is well-formed, that `.gitattributes` has the
    /// three required merge-driver registrations, and that genus stamps in
    /// `regions/` files are parseable.  Missing genus stamps produce warnings
    /// (not errors); structural problems produce errors and a non-zero exit.
    ///
    /// Example:
    ///   cd my-universe && emanon validate
    Validate {
        /// Treat warnings as errors (strict mode)
        #[arg(long, short = 's')]
        strict: bool,
    },
}

#[derive(Subcommand)]
enum ContractAction {
    /// Draft a new contract
    Draft,
    /// Sign an existing contract
    Sign,
    /// List all contracts in this universe
    List,
}

#[derive(Subcommand)]
enum BountyAction {
    /// Post a new bounty
    Post,
    /// List open bounties
    List,
    /// Accept a bounty
    Accept,
    /// Deliver work for an accepted bounty
    Deliver,
}

#[derive(Subcommand)]
enum TournamentAction {
    /// Join a tournament
    Join,
    /// Leave a tournament
    Leave,
    /// Play the next move in an active tournament
    Play,
}

#[derive(Subcommand)]
enum RegistryAction {
    /// Publish this universe to the registry by generating a signed entry and opening a PR
    Push {
        /// Registry repo URL (overrides ~/.config/emanon/config.toml)
        #[arg(long)]
        registry: Option<String>,
    },
    /// Clone or fetch a registry locally for offline browsing
    Pull {
        /// Registry repo URL (overrides ~/.config/emanon/config.toml)
        #[arg(long)]
        registry: Option<String>,
    },
    /// List universes in the registry with optional filtering
    List {
        /// Registry repo URL (overrides ~/.config/emanon/config.toml)
        #[arg(long)]
        registry: Option<String>,
        /// jq expression to filter entries (e.g. '.tags | contains(["solo"])')
        #[arg(long)]
        filter: Option<String>,
    },
    /// Add a git remote pointing to a universe from the registry
    AddRemote {
        /// Name of the registry entry (matches entries/<name>.json)
        entry_name: String,
        /// Registry repo URL (overrides ~/.config/emanon/config.toml)
        #[arg(long)]
        registry: Option<String>,
        /// Local remote name to create (defaults to the entry name)
        #[arg(long)]
        remote_name: Option<String>,
    },
}

// ---------------------------------------------------------------------------
// emanon init
// ---------------------------------------------------------------------------

const VALUES_JSON: &str = r#"{
  "conflict_preference": "contract",
  "fork_readiness": "medium",
  "battle_threshold": 0.5,
  "host_authority_mode": "partition"
}
"#;

const GITATTRIBUTES: &str = "\
# Emanon merge driver registration.
# Each path pattern is routed to a specific merge driver registered in .git/config.
# These drivers are written automatically by `emanon init` — see .git/config for details.
#
regions/**       merge=emanon-collatz
contracts/**     merge=emanon-contract
scars/**         merge=emanon-append-only
";

/// Ephemeral files excluded from snapshots.
/// leverage.cache is regenerated at runtime; it must not be committed.
const GITIGNORE: &str = "\
# Emanon ephemeral files — regenerated at runtime, not part of universe state
.gitverse/leverage.cache
";

fn readme_template(name: &str) -> String {
    format!(
        "# {name}\n\
        \n\
        This is an Emanon universe — a git-based multiverse simulation.\n\
        \n\
        ## Structure\n\
        \n\
        - `regions/`  — spatial partitions of this universe\n\
        - `contracts/` — agreements with other players and universes\n\
        - `scars/`     — records of resolved conflicts and merges\n\
        - `forks/`     — active timeline divergences\n\
        - `.gitverse/values.json`    — resolution preferences for this universe\n\
        - `.gitverse/snapshot_count` — current snapshot counter\n\
        - `.gitattributes`            — merge driver registration (regions/contracts/scars)\n\
        \n\
        ## Getting Started\n\
        \n\
        ```sh\n\
        cd {name}\n\
        emanon snapshot -m 'first moment'\n\
        ```\n\
        \n\
        Run `emanon --help` to see available commands.\n"
    )
}

fn cmd_init(name: &str, force: bool) -> Result<(), Box<dyn std::error::Error>> {
    let target = Path::new(name);

    // --- Guard: existing directory ---
    if target.exists() {
        if !force {
            return Err(format!(
                "directory '{}' already exists.\n\
                 Use --force to initialise inside an existing directory\n\
                 (will not overwrite an existing Emanon universe).",
                name
            )
            .into());
        }
        // Even with --force, refuse to clobber an existing universe.
        if target.join(".gitverse").exists() {
            return Err(format!(
                "'{name}' is already an Emanon universe (.gitverse exists).\n\
                 --force does not re-initialise existing universes."
            )
            .into());
        }
    }

    // --- Create directory tree ---
    let dirs = [".gitverse", "regions", "contracts", "scars", "forks"];
    for dir in &dirs {
        std::fs::create_dir_all(target.join(dir))?;
    }

    // --- Write template files ---
    // .gitignore must be written before git add so leverage.cache stays untracked.
    std::fs::write(target.join(".gitignore"), GITIGNORE)?;
    std::fs::write(target.join(".gitverse/values.json"), VALUES_JSON)?;
    // leverage.cache is ephemeral — create it for runtime use but keep it gitignored.
    std::fs::write(target.join(".gitverse/leverage.cache"), "")?;
    std::fs::write(target.join(".gitattributes"), GITATTRIBUTES)?;
    std::fs::write(target.join("regions/.gitkeep"), "")?;
    std::fs::write(target.join("contracts/.gitkeep"), "")?;
    std::fs::write(target.join("scars/.gitkeep"), "")?;
    std::fs::write(target.join("forks/.gitkeep"), "")?;
    std::fs::write(target.join("README.md"), readme_template(name))?;

    // --- git init ---
    let git_init = Command::new("git")
        .args(["init", "-b", "main"])
        .current_dir(target)
        .output()?;

    if !git_init.status.success() {
        return Err(format!(
            "git init failed:\n{}",
            String::from_utf8_lossy(&git_init.stderr)
        )
        .into());
    }

    // --- Register merge drivers in .git/config ---
    //
    // Three drivers are registered per-repo so that `git merge` automatically
    // routes conflicts to the right handler based on .gitattributes:
    //   emanon-collatz    — Collatz genus-based merge for regions/**
    //   emanon-contract   — contract-aware merge for contracts/**
    //   emanon-append-only — append-only merge for scars/**
    //
    // %O = base, %A = ours (driver writes result here), %B = theirs, %P = path
    // Each entry: (display_name, name_key, driver_key, driver_command)
    let drivers: [(&str, &str, &str, &str); 3] = [
        (
            "Collatz merge driver",
            "merge.emanon-collatz.name",
            "merge.emanon-collatz.driver",
            "emanon merge-driver %O %A %B %P",
        ),
        (
            "Contract merge driver",
            "merge.emanon-contract.name",
            "merge.emanon-contract.driver",
            "emanon merge-driver --contract-mode %O %A %B %P",
        ),
        (
            "Append-only merge driver",
            "merge.emanon-append-only.name",
            "merge.emanon-append-only.driver",
            "emanon merge-driver --append-only %O %A %B %P",
        ),
    ];

    for (display_name, name_key, driver_key, driver_cmd) in drivers {
        let cfg_name = Command::new("git")
            .args(["config", name_key, display_name])
            .current_dir(target)
            .output()?;
        if !cfg_name.status.success() {
            return Err(format!(
                "git config {} failed:\n{}",
                name_key,
                String::from_utf8_lossy(&cfg_name.stderr)
            )
            .into());
        }

        let cfg_driver = Command::new("git")
            .args(["config", driver_key, driver_cmd])
            .current_dir(target)
            .output()?;
        if !cfg_driver.status.success() {
            return Err(format!(
                "git config {} failed:\n{}",
                driver_key,
                String::from_utf8_lossy(&cfg_driver.stderr)
            )
            .into());
        }
    }

    // --- git add . ---
    // leverage.cache is excluded via .gitignore; all other files are staged.
    let git_add = Command::new("git")
        .args(["add", "."])
        .current_dir(target)
        .output()?;

    if !git_add.status.success() {
        return Err(format!(
            "git add failed:\n{}",
            String::from_utf8_lossy(&git_add.stderr)
        )
        .into());
    }

    // --- initial commit ---
    let commit_msg = format!("init: bootstrap {} universe", name);
    let git_commit = Command::new("git")
        .args(["commit", "-m", &commit_msg])
        .current_dir(target)
        .output()?;

    if !git_commit.status.success() {
        return Err(format!(
            "git commit failed:\n{}",
            String::from_utf8_lossy(&git_commit.stderr)
        )
        .into());
    }

    println!("✨  Universe '{name}' initialised at ./{name}/");
    println!("    cd {name} && emanon snapshot -m 'first moment'");

    Ok(())
}

// ---------------------------------------------------------------------------
// emanon snapshot
// ---------------------------------------------------------------------------

fn cmd_snapshot(message: Option<String>, no_stage: bool) -> Result<(), Box<dyn std::error::Error>> {
    // --- Verify we are inside an Emanon universe ---
    let here = std::env::current_dir()?;
    let gitverse = here.join(".gitverse");
    if !gitverse.exists() {
        return Err(
            "not an Emanon universe — .gitverse/ not found in the current directory.\n\
             Run `emanon init <name>` to create one, then `cd <name>` first."
                .into(),
        );
    }

    // --- Stage user changes (unless --no-stage) ---
    if !no_stage {
        let git_add = Command::new("git").args(["add", "-A"]).output()?;
        if !git_add.status.success() {
            return Err(format!(
                "git add -A failed:\n{}",
                String::from_utf8_lossy(&git_add.stderr)
            )
            .into());
        }
    }

    // --- Check for staged user changes (excluding .gitverse/ engine files) ---
    //
    // We deliberately ignore changes inside .gitverse/ here because:
    //   - leverage.cache is ephemeral (gitignored)
    //   - snapshot_count is managed entirely by this command
    // If only engine files changed, there is nothing meaningful to snapshot.
    let git_diff = Command::new("git")
        .args(["diff", "--cached", "--name-only"])
        .output()?;
    if !git_diff.status.success() {
        return Err("git diff --cached --name-only failed".into());
    }
    let staged_output = String::from_utf8_lossy(&git_diff.stdout);
    let user_changed: Vec<&str> = staged_output
        .lines()
        .filter(|f| !f.starts_with(".gitverse/"))
        .collect();

    if user_changed.is_empty() {
        println!("📭  Nothing to snapshot — no changes staged.");
        return Ok(());
    }
    let file_count = user_changed.len();

    // --- Compute new snapshot number ---
    let count_file = gitverse.join("snapshot_count");
    let current_count: u64 = if count_file.exists() {
        std::fs::read_to_string(&count_file)?
            .trim()
            .parse()
            .unwrap_or(0)
    } else {
        0
    };
    let new_count = current_count + 1;

    // --- Write updated snapshot counter and stage it ---
    std::fs::write(&count_file, new_count.to_string())?;
    let _ = Command::new("git")
        .args(["add", ".gitverse/snapshot_count"])
        .output()?;

    // --- Build commit message with git trailers ---
    //
    // Format:
    //   snapshot N: <message>
    //
    //   Snapshot: N
    //   Genus: (placeholder — M1.4)
    let msg_text = message.as_deref().unwrap_or("(no message)");
    let commit_subject = format!("snapshot {new_count}: {msg_text}");
    let commit_body = format!(
        "Snapshot: {new_count}\nGenus: (placeholder \u{2014} M1.4)"
    );
    let full_message = format!("{commit_subject}\n\n{commit_body}");

    // --- Commit ---
    let git_commit = Command::new("git")
        .args(["commit", "-m", &full_message])
        .output()?;
    if !git_commit.status.success() {
        // Roll back the counter so the next attempt gets the same number.
        let _ = std::fs::write(&count_file, current_count.to_string());
        return Err(format!(
            "git commit failed:\n{}",
            String::from_utf8_lossy(&git_commit.stderr)
        )
        .into());
    }

    // --- Retrieve commit SHA for the summary line ---
    let sha = Command::new("git")
        .args(["rev-parse", "--short", "HEAD"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|| "(unknown)".to_string());

    // --- Print summary ---
    println!("📸  Snapshot {new_count} committed  [{sha}]");
    println!("    {file_count} file(s) changed");
    if let Some(ref m) = message {
        println!("    Message: \"{m}\"");
    }

    Ok(())
}

// ---------------------------------------------------------------------------
// emanon merge
// ---------------------------------------------------------------------------

/// A single file conflict deferred to player negotiation.
///
/// Produced by `cmd_merge` when the Collatz merge driver exits 1 (unrelated
/// genus sets or missing stamps that it cannot auto-resolve).
#[derive(Debug)]
struct ConflictEntry {
    /// Repo-relative path of the conflicted file.
    path: String,
    /// Git object SHA of the base (common ancestor) blob; empty if no common ancestor.
    base_sha: String,
    /// Git object SHA of our version of the blob.
    ours_sha: String,
    /// Git object SHA of their version of the blob.
    theirs_sha: String,
    /// Genus stamp embedded in our version (if any).
    ours_genus: Option<GenusStamp>,
    /// Genus stamp embedded in their version (if any).
    theirs_genus: Option<GenusStamp>,
    /// Leverage score for our side (commit count in our HEAD).
    ours_leverage: u64,
    /// Leverage score for their side (commit count reachable from FETCH_HEAD).
    theirs_leverage: u64,
}

/// Read a genus stamp from a git blob identified by SHA.
///
/// Uses `git cat-file -p <sha>` to retrieve the blob content, then parses
/// the embedded genus stamp.  Returns `None` if the SHA is empty, the blob
/// cannot be read, or no stamp is present.
fn read_genus_from_sha(sha: &str) -> Option<GenusStamp> {
    if sha.is_empty() {
        return None;
    }
    let output = Command::new("git")
        .args(["cat-file", "-p", sha])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let content = String::from_utf8_lossy(&output.stdout);
    parse_genus_stamp(&content)
}

/// Compute leverage as the count of commits reachable from `refspec`.
///
/// Leverage in the gitverse is a pure function of the git object database.
/// This implementation uses `git rev-list --count <refspec>` — the total
/// commits accumulated, which is the primary leverage component from the
/// design doc.  Returns 0 if the refspec is invalid or git fails.
fn compute_leverage(refspec: &str) -> u64 {
    let output = Command::new("git")
        .args(["rev-list", "--count", refspec])
        .output()
        .ok();
    match output {
        Some(o) if o.status.success() => String::from_utf8_lossy(&o.stdout)
            .trim()
            .parse()
            .unwrap_or(0),
        _ => 0,
    }
}

/// Serialize a [`ConflictEntry`] to a JSON object string.
///
/// Avoids a JSON dependency by constructing the object inline.  `null` is
/// used for missing genus fields so the downstream `emanon negotiate` command
/// can distinguish "no stamp" from "stamp with zero values".
fn conflict_entry_to_json(c: &ConflictEntry) -> String {
    let genus_json = |g: &Option<GenusStamp>| match g {
        Some(stamp) => format!(
            r#"{{"set_k": {}, "oddity_s": {}, "index_i": {}}}"#,
            stamp.set_k, stamp.oddity_s, stamp.index_i
        ),
        None => "null".to_string(),
    };
    format!(
        r#"    {{
      "path": "{}",
      "base_sha": "{}",
      "ours_sha": "{}",
      "theirs_sha": "{}",
      "ours_genus": {},
      "theirs_genus": {},
      "ours_leverage": {},
      "theirs_leverage": {}
    }}"#,
        c.path,
        c.base_sha,
        c.ours_sha,
        c.theirs_sha,
        genus_json(&c.ours_genus),
        genus_json(&c.theirs_genus),
        c.ours_leverage,
        c.theirs_leverage,
    )
}

/// Implements `emanon merge <remote>/<branch>`.
///
/// 1. `git fetch <remote>` — sync the remote.
/// 2. `git merge --no-commit --no-ff <remote>/<branch>` — run merge with the
///    Collatz driver active via `.gitattributes`.
/// 3. Inspect the outcome:
///    - No unmerged paths + exit 0 → auto-commit the merge.
///    - Unmerged paths exist → build conflict report, write
///      `.gitverse/pending-merge.json`, print summary.
fn cmd_merge(remote_branch: &str) -> Result<(), Box<dyn std::error::Error>> {
    // --- Parse <remote>/<branch> ---
    let slash_pos = remote_branch.find('/').ok_or_else(|| {
        format!(
            "invalid remote/branch '{}': expected format <remote>/<branch>\n\
             Example: emanon merge origin/main",
            remote_branch
        )
    })?;
    let remote = &remote_branch[..slash_pos];

    // --- Verify universe ---
    let here = std::env::current_dir()?;
    let gitverse = here.join(".gitverse");
    if !gitverse.exists() {
        return Err(
            "not an Emanon universe — .gitverse/ not found in the current directory.\n\
             Run `emanon init <name>` to create one, then `cd <name>` first."
                .into(),
        );
    }

    println!("Merging from {}...", remote_branch);

    // --- git fetch <remote> ---
    let fetch = Command::new("git")
        .args(["fetch", remote])
        .output()?;
    if !fetch.status.success() {
        return Err(format!(
            "git fetch {} failed:\n{}",
            remote,
            String::from_utf8_lossy(&fetch.stderr)
        )
        .into());
    }

    // --- git merge --no-commit --no-ff <remote>/<branch> ---
    //
    // --no-commit stops before the commit even when merge succeeds (so we can
    // inspect the result and optionally auto-commit).
    // --no-ff always creates a merge commit, which is correct for universe
    // timeline merges (fast-forwards would erase the fork history).
    // The Collatz merge driver fires automatically for paths in .gitattributes;
    // if a driver exits 1, git marks that path as unmerged and exits 1 itself.
    let merge = Command::new("git")
        .args(["merge", "--no-commit", "--no-ff", remote_branch])
        .output()?;

    // --- Identify unmerged paths ---
    //
    // `git diff --name-only --diff-filter=U` lists paths still in conflict
    // (unmerged, i.e. the driver returned 1 for them).
    let unmerged_output = Command::new("git")
        .args(["diff", "--name-only", "--diff-filter=U"])
        .output()?;
    let unmerged_paths: Vec<String> = if unmerged_output.status.success() {
        String::from_utf8_lossy(&unmerged_output.stdout)
            .lines()
            .filter(|l| !l.is_empty())
            .map(String::from)
            .collect()
    } else {
        vec![]
    };

    // --- Branch: no conflicts ---
    if unmerged_paths.is_empty() && merge.status.success() {
        // All paths were auto-resolved by the merge driver — commit the result.
        let commit = Command::new("git")
            .args(["commit", "--no-edit"])
            .output()?;
        if !commit.status.success() {
            return Err(format!(
                "git commit failed after clean merge:\n{}",
                String::from_utf8_lossy(&commit.stderr)
            )
            .into());
        }
        let sha = Command::new("git")
            .args(["rev-parse", "--short", "HEAD"])
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_else(|| "(unknown)".to_string());
        println!("Merge complete — no conflicts.  [{sha}]");
        return Ok(());
    }

    // --- Branch: conflicts need negotiation ---

    // Precompute leverage for both sides.  Leverage is a universe-level
    // quantity (commit count), not per-file, so we compute it once and reuse.
    let ours_leverage = compute_leverage("HEAD");
    let theirs_leverage = compute_leverage("FETCH_HEAD");

    // Build one ConflictEntry per unresolved path.
    let mut conflicts: Vec<ConflictEntry> = Vec::new();

    for path in &unmerged_paths {
        // `git ls-files -u -- <path>` lists index entries for this path.
        // Each line: "<mode> <sha> <stage>\t<path>"
        //   stage 1 = base (common ancestor)
        //   stage 2 = ours
        //   stage 3 = theirs
        let ls = Command::new("git")
            .args(["ls-files", "-u", "--", path])
            .output()?;
        let ls_out = String::from_utf8_lossy(&ls.stdout);

        let mut base_sha = String::new();
        let mut ours_sha = String::new();
        let mut theirs_sha = String::new();

        for line in ls_out.lines() {
            // Format: "mode sha stage\tpath"
            // Split on tab first to get "<mode> <sha> <stage>" and "<path>".
            let tab = line.find('\t').unwrap_or(line.len());
            let meta_str = &line[..tab];
            let meta: Vec<&str> = meta_str.splitn(3, ' ').collect();
            if meta.len() < 3 {
                continue;
            }
            let sha = meta[1];
            let stage = meta[2].trim();
            match stage {
                "1" => base_sha = sha.to_string(),
                "2" => ours_sha = sha.to_string(),
                "3" => theirs_sha = sha.to_string(),
                _ => {}
            }
        }

        // Read genus stamps from the blob objects.
        let ours_genus = read_genus_from_sha(&ours_sha);
        let theirs_genus = read_genus_from_sha(&theirs_sha);

        conflicts.push(ConflictEntry {
            path: path.clone(),
            base_sha,
            ours_sha,
            theirs_sha,
            ours_genus,
            theirs_genus,
            ours_leverage,
            theirs_leverage,
        });
    }

    // --- Write .gitverse/pending-merge.json ---
    let n = conflicts.len();
    let entries: Vec<String> = conflicts.iter().map(conflict_entry_to_json).collect();
    let pending_json = format!(
        "{{\n  \"remote_branch\": \"{remote_branch}\",\n  \"conflicts\": [\n{}\n  ]\n}}",
        entries.join(",\n")
    );
    let pending_path = gitverse.join("pending-merge.json");
    std::fs::write(&pending_path, &pending_json)?;

    // --- Print conflict summary ---
    println!(
        "{n} conflict{} deferred to negotiation:",
        if n == 1 { "" } else { "s" }
    );
    for c in &conflicts {
        println!("  {}", c.path);
        match &c.ours_genus {
            Some(g) => println!(
                "    your genus: Set_{} / s={} / leverage {}",
                g.set_k, g.oddity_s, c.ours_leverage
            ),
            None => println!("    your genus: unknown (no stamp) / leverage {}", c.ours_leverage),
        }
        match &c.theirs_genus {
            Some(g) => println!(
                "    their genus: Set_{} / s={} / leverage {}",
                g.set_k, g.oddity_s, c.theirs_leverage
            ),
            None => println!(
                "    their genus: unknown (no stamp) / leverage {}",
                c.theirs_leverage
            ),
        }
    }
    println!("\nRun `emanon negotiate` to resolve.");

    Ok(())
}

// ---------------------------------------------------------------------------
// emanon merge-driver
// ---------------------------------------------------------------------------

/// A Collatz genus stamp parsed from an Emanon file.
///
/// Two stamp formats are supported (both produced by different commands):
///
/// **Legacy first-line format** (written by earlier tooling):
/// ```text
/// # emanon:genus set_k=3 oddity_s=1 index_i=0
/// ```
///
/// **JSON trailing-line format** (written by `emanon write`, M1.4+):
/// ```text
/// # emanon-genus: {"set_k": 3, "oddity_s": 1, "index_i": 0, "writer": "...", "snapshot": 42}
/// ```
///
/// If neither format is found the file is considered "legacy" and the driver
/// defers to the user (exits 1).
#[derive(Debug, Clone, PartialEq, Eq)]
struct GenusStamp {
    set_k: u64,
    oddity_s: u64,
    #[allow(dead_code)]
    index_i: u64,
}

/// Parse a [`GenusStamp`] from any line of `content`.
///
/// Scans every line looking for either:
/// 1. `# emanon:genus set_k=<u64> oddity_s=<u64> index_i=<u64>`
/// 2. `# emanon-genus: {"set_k": <u64>, "oddity_s": <u64>, "index_i": <u64>, ...}`
///
/// Returns the first match found, or `None` if no stamp is present.
fn parse_genus_stamp(content: &str) -> Option<GenusStamp> {
    for line in content.lines() {
        let trimmed = line.trim();

        // ------------------------------------------------------------------
        // Format 1 (legacy): # emanon:genus set_k=K oddity_s=S index_i=I
        // ------------------------------------------------------------------
        if let Some(rest) = trimmed.strip_prefix("# emanon:genus ") {
            let mut set_k: Option<u64> = None;
            let mut oddity_s: Option<u64> = None;
            let mut index_i: Option<u64> = None;
            for part in rest.split_whitespace() {
                if let Some(v) = part.strip_prefix("set_k=") {
                    set_k = v.parse().ok();
                } else if let Some(v) = part.strip_prefix("oddity_s=") {
                    oddity_s = v.parse().ok();
                } else if let Some(v) = part.strip_prefix("index_i=") {
                    index_i = v.parse().ok();
                }
            }
            if let (Some(k), Some(s), Some(i)) = (set_k, oddity_s, index_i) {
                return Some(GenusStamp { set_k: k, oddity_s: s, index_i: i });
            }
        }

        // ------------------------------------------------------------------
        // Format 2 (M1.4): # emanon-genus: {"set_k": K, "oddity_s": S, ...}
        // ------------------------------------------------------------------
        if let Some(json_str) = trimmed.strip_prefix("# emanon-genus: ") {
            if let Some(stamp) = parse_genus_json(json_str) {
                return Some(stamp);
            }
        }
    }
    None
}

/// Parse a [`GenusStamp`] from a JSON object string produced by `emanon write`.
///
/// Handles the compact inline JSON format:
/// `{"set_k": 13, "oddity_s": 5, "index_i": 2, "writer": "...", "snapshot": 42}`
///
/// Uses simple substring search to avoid a JSON dependency.
fn parse_genus_json(json: &str) -> Option<GenusStamp> {
    fn extract_u64(json: &str, key: &str) -> Option<u64> {
        // Find `"key": N` where N is a sequence of digits.
        let search = format!("\"{}\":", key);
        let pos = json.find(&search)?;
        let after = json[pos + search.len()..].trim_start();
        // After the colon, collect digits (possibly quoted number but we emit unquoted).
        let digits: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
        digits.parse().ok()
    }
    let k = extract_u64(json, "set_k")?;
    let s = extract_u64(json, "oddity_s")?;
    let i = extract_u64(json, "index_i")?;
    Some(GenusStamp { set_k: k, oddity_s: s, index_i: i })
}

/// Hybrid merge: both versions contributed; produces a concatenated file.
///
/// Preserves the genus stamp from `ours` (same set_k means same set identity).
/// Inserts clear section markers so the content is readable by players.
fn hybrid_merge(ours: &str, theirs: &str) -> String {
    let separator_a = "<<<<<<< ours (same set_k — hybrid merge) >>>>>>>";
    let separator_b = "======= theirs =======";
    let separator_c = ">>>>>>> end hybrid merge >>>>>>>";
    format!("{separator_a}\n{ours}\n{separator_b}\n{theirs}\n{separator_c}\n")
}

/// Genus-attenuated merge: `theirs` wins but is annotated with the attenuation
/// coefficient β derived from the shared `oddity_s`.
///
/// Prepends an attenuation comment to the merged content and retains the
/// theirs content (higher convergence pressure wins per Paper 1 §4).
fn attenuated_merge(theirs: &str, oddity_s: u64) -> String {
    let b = beta(oddity_s);
    let comment = format!("# genus-attenuated by β={b:.7} (oddity_s={oddity_s})");
    format!("{comment}\n{theirs}")
}

/// Write conflict markers to `output_path` for deferred (player-resolved)
/// conflicts.
///
/// Uses the same format as git's own conflict markers so standard diff tools
/// and editors will highlight the conflict correctly.
fn write_conflict_markers(
    ours: &str,
    theirs: &str,
    reason: &str,
) -> String {
    format!(
        "<<<<<<< ours (emanon: {reason})\n{ours}=======\n{theirs}>>>>>>> theirs\n"
    )
}

/// Merge mode — controls which resolution strategy is attempted.
#[derive(Debug, Clone, PartialEq, Eq)]
enum MergeMode {
    /// Collatz genus-based merge (default, used for `regions/**`).
    Collatz,
    /// Contract-aware merge (used for `contracts/**`). Stub — full
    /// implementation arrives in M2+.  Currently falls back to Collatz with
    /// a stderr diagnostic so the driver is wired and testable.
    Contract,
    /// Append-only merge (used for `scars/**`). Stub — full implementation
    /// arrives in M2+.  Currently falls back to Collatz with a stderr
    /// diagnostic.
    AppendOnly,
}

/// Implements `emanon merge-driver [--contract-mode|--append-only] <base> <ours> <theirs> <path>`.
///
/// Returns the exit code that the driver should use:
/// - `0` — conflict resolved, output file written
/// - `1` — conflict deferred (git will show it as unresolved)
/// - `2` — I/O or internal error (handled by `main`)
fn cmd_merge_driver(
    mode: &MergeMode,
    base: &str,
    ours: &str,
    theirs: &str,
    path: &str,
    output: &str,
) -> Result<i32, Box<dyn std::error::Error>> {
    // Emit diagnostics for stub modes so the wiring is observable.
    match mode {
        MergeMode::Contract => {
            eprintln!(
                "emanon merge-driver: --contract-mode invoked for '{path}' \
                 (stub — falling back to Collatz resolution; \
                 full contract merge arrives in M2)"
            );
        }
        MergeMode::AppendOnly => {
            eprintln!(
                "emanon merge-driver: --append-only invoked for '{path}' \
                 (stub — falling back to Collatz resolution; \
                 full append-only merge arrives in M2)"
            );
        }
        MergeMode::Collatz => {}
    }
    let _ = base;  // base content is available for future leverage computation
    let _ = path;  // recorded for diagnostics / future use
    let ours_content = std::fs::read_to_string(ours)?;
    let theirs_content = std::fs::read_to_string(theirs)?;

    let g_ours = parse_genus_stamp(&ours_content);
    let g_theirs = parse_genus_stamp(&theirs_content);

    match (g_ours, g_theirs) {
        // ----------------------------------------------------------------
        // Rule 1: same set_k → hybrid merge
        // ----------------------------------------------------------------
        (Some(go), Some(gt)) if go.set_k == gt.set_k => {
            let merged = hybrid_merge(&ours_content, &theirs_content);
            std::fs::write(output, merged)?;
            eprintln!(
                "emanon merge-driver: hybrid merge (set_k={}) → {}",
                go.set_k, output
            );
            Ok(0)
        }

        // ----------------------------------------------------------------
        // Rule 2: same oddity_s, different set_k → genus-attenuated merge
        // ----------------------------------------------------------------
        (Some(go), Some(gt)) if go.oddity_s == gt.oddity_s => {
            let merged = attenuated_merge(&theirs_content, go.oddity_s);
            std::fs::write(output, merged)?;
            eprintln!(
                "emanon merge-driver: attenuated merge \
                 (oddity_s={}, set_k {} vs {}) → {}",
                go.oddity_s, go.set_k, gt.set_k, output
            );
            Ok(0)
        }

        // ----------------------------------------------------------------
        // Rule 3: unrelated sets or missing genus → defer to player
        // ----------------------------------------------------------------
        (g_o, g_t) => {
            let reason = match (&g_o, &g_t) {
                (None, _) | (_, None) => "no-genus-stamp",
                _ => "unrelated-sets",
            };
            let conflict = write_conflict_markers(&ours_content, &theirs_content, reason);
            std::fs::write(output, conflict)?;
            eprintln!(
                "emanon merge-driver: deferred ({reason}) — conflict markers written to {output}"
            );
            Ok(1)
        }
    }
}

// ---------------------------------------------------------------------------
// emanon write
// ---------------------------------------------------------------------------

/// Low 8 bits of the default hash of `path`.
///
/// Provides per-file genus variation: two files written in the same snapshot
/// use different seeds so they receive different genera.  8 bits (0–255) keeps
/// `n = snapshot + hash` small enough for `dropping_genus_u64` to run fast.
fn path_hash_low_bits(path: &str) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let mut h = DefaultHasher::new();
    path.hash(&mut h);
    h.finish() & 0xFF
}

/// Serialize a [`collatz_rs::Genus`] to the inline JSON stamp string used by
/// `emanon write`, including the `writer` and `snapshot` fields.
fn genus_stamp_json(genus: &collatz_rs::Genus, writer: &str, snapshot: u64) -> String {
    format!(
        r#"# emanon-genus: {{"set_k": {}, "oddity_s": {}, "index_i": {}, "writer": "{}", "snapshot": {}}}"#,
        genus.set_k, genus.oddity_s, genus.index_i, writer, snapshot
    )
}

/// Implements `emanon write <path> [content]`.
///
/// Writes `content` (or stdin if omitted) into `path` relative to the universe
/// root, appending a Collatz genus stamp computed from the current snapshot
/// count and the file path.
///
/// - Text content (supplied as a CLI arg or valid-UTF-8 stdin): stamp is
///   appended as a trailing `# emanon-genus: {...}` line.
/// - Binary stdin: stamp is written to a `<path>.genus` sidecar file as raw
///   JSON (without the `#` comment prefix, so binary files aren't corrupted).
fn cmd_write(path: &str, content: Option<String>) -> Result<(), Box<dyn std::error::Error>> {
    // --- Verify universe ---
    let here = std::env::current_dir()?;
    let gitverse = here.join(".gitverse");
    if !gitverse.exists() {
        return Err(
            "not an Emanon universe — .gitverse/ not found in the current directory.\n\
             Run `emanon init <name>` to create one, then `cd <name>` first."
                .into(),
        );
    }

    // --- Read snapshot count ---
    let count_file = gitverse.join("snapshot_count");
    let snapshot: u64 = if count_file.exists() {
        std::fs::read_to_string(&count_file)?.trim().parse().unwrap_or(0)
    } else {
        0
    };

    // --- Compute genus ---
    //
    // n = snapshot_count + path_hash_low_bits + 2
    //   - +2 ensures n > 1 (dropping_genus panics for n ≤ 1)
    //   - path_hash_low_bits (0–255) varies genus per file within a snapshot
    //   - Total n is small (< 2^16 in practice), so dropping_index is fast.
    let seed = snapshot.saturating_add(path_hash_low_bits(path)).saturating_add(2);
    let genus = collatz_rs::dropping_genus_u64(seed);

    // --- Get git author (best-effort) ---
    let writer = Command::new("git")
        .args(["config", "user.email"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|| "unknown".to_string());

    // --- Resolve target path ---
    let file_path = here.join(path);
    if let Some(parent) = file_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let stamp_line = genus_stamp_json(&genus, &writer, snapshot);

    match content {
        // ------------------------------------------------------------------
        // Text path: content supplied as CLI arg (always valid UTF-8)
        // ------------------------------------------------------------------
        Some(text) => {
            // Ensure content ends with a newline before appending stamp.
            let stamped = if text.ends_with('\n') {
                format!("{text}{stamp_line}\n")
            } else {
                format!("{text}\n{stamp_line}\n")
            };
            std::fs::write(&file_path, &stamped)?;

            println!("✍️  {path}");
            println!("    set_k={} oddity_s={} index_i={}", genus.set_k, genus.oddity_s, genus.index_i);
            println!("    snapshot={snapshot}  seed={seed}");
        }

        // ------------------------------------------------------------------
        // Binary/stdin path: read raw bytes from stdin
        // ------------------------------------------------------------------
        None => {
            use std::io::Read;
            let mut raw: Vec<u8> = Vec::new();
            std::io::stdin().read_to_end(&mut raw)?;

            if let Ok(text) = std::str::from_utf8(&raw) {
                // Valid UTF-8 — treat as text, embed stamp at bottom.
                let stamped = if text.ends_with('\n') {
                    format!("{text}{stamp_line}\n")
                } else {
                    format!("{text}\n{stamp_line}\n")
                };
                std::fs::write(&file_path, stamped.as_bytes())?;
            } else {
                // True binary — write raw bytes and create sidecar.
                std::fs::write(&file_path, &raw)?;
                let sidecar_path = format!("{path}.genus");
                let sidecar = here.join(&sidecar_path);
                // Sidecar is plain JSON (no `#` comment prefix; binary files
                // cannot safely embed line comments).
                let sidecar_json = format!(
                    r#"{{"set_k": {}, "oddity_s": {}, "index_i": {}, "writer": "{}", "snapshot": {}}}"#,
                    genus.set_k, genus.oddity_s, genus.index_i, writer, snapshot
                );
                std::fs::write(&sidecar, sidecar_json)?;
                println!("✍️  {path} (binary — genus written to {sidecar_path})");
                println!("    set_k={} oddity_s={} index_i={}", genus.set_k, genus.oddity_s, genus.index_i);
                return Ok(());
            }

            println!("✍️  {path}");
            println!("    set_k={} oddity_s={} index_i={}", genus.set_k, genus.oddity_s, genus.index_i);
            println!("    snapshot={snapshot}  seed={seed}");
        }
    }

    Ok(())
}

// ---------------------------------------------------------------------------
// emanon genus
// ---------------------------------------------------------------------------

/// Implements `emanon genus <path>`.
///
/// Reads `path` (relative to universe root) and extracts the embedded genus
/// stamp, printing it to stdout as JSON.  For binary files with a `.genus`
/// sidecar, reads the sidecar instead.
///
/// Exits 1 if no genus stamp is found (via `eprintln!` + error return).
fn cmd_genus(path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let here = std::env::current_dir()?;
    let file_path = here.join(path);

    // Try reading the file as text.
    if let Ok(content) = std::fs::read_to_string(&file_path) {
        // Scan for embedded stamp.
        if let Some(stamp) = parse_genus_stamp(&content) {
            println!(
                r#"{{"set_k": {}, "oddity_s": {}, "index_i": {}}}"#,
                stamp.set_k, stamp.oddity_s, stamp.index_i
            );
            return Ok(());
        }
        // No embedded stamp — check for sidecar (file might be "binary" stored as text).
    }

    // Try binary sidecar <path>.genus.
    let sidecar_path = here.join(format!("{path}.genus"));
    if sidecar_path.exists() {
        let sidecar = std::fs::read_to_string(&sidecar_path)?;
        println!("{}", sidecar.trim());
        return Ok(());
    }

    Err(format!("no genus stamp found in '{path}' (or '{path}.genus')").into())
}

// ---------------------------------------------------------------------------
// emanon negotiate
// ---------------------------------------------------------------------------

/// A pending conflict loaded from `.gitverse/pending-merge.json`.
#[derive(Debug, Clone)]
struct PendingConflict {
    path: String,
    ours_leverage: u64,
    theirs_leverage: u64,
    ours_genus_str: String,
    theirs_genus_str: String,
}

/// Parse the pending-merge.json file and return a list of conflicts.
///
/// The JSON is hand-parsed (no serde dep) using the same approach as the rest
/// of the codebase — substring search for known keys.
fn load_pending_conflicts(
    gitverse: &std::path::Path,
) -> Result<Vec<PendingConflict>, Box<dyn std::error::Error>> {
    let pending_path = gitverse.join("pending-merge.json");
    if !pending_path.exists() {
        return Err(
            "no pending conflicts found (.gitverse/pending-merge.json does not exist).\n\
             Run `emanon merge <remote>/<branch>` first."
                .into(),
        );
    }
    let raw = std::fs::read_to_string(&pending_path)?;

    // Extract "conflicts": [ ... ] array — find the array bounds by counting brackets.
    let conflicts_key = "\"conflicts\": [";
    let start = raw.find(conflicts_key).ok_or("malformed pending-merge.json: missing 'conflicts'")?;
    let array_start = start + conflicts_key.len() - 1; // position of '['

    // Walk forward counting [ and ] to find matching ]
    let mut depth = 0usize;
    let mut array_end = array_start;
    for (i, ch) in raw[array_start..].char_indices() {
        match ch {
            '[' => depth += 1,
            ']' => {
                depth -= 1;
                if depth == 0 {
                    array_end = array_start + i;
                    break;
                }
            }
            _ => {}
        }
    }
    let array_content = &raw[array_start + 1..array_end]; // contents between [ and ]

    // Split into individual object strings — split on "},\n    {" patterns.
    // Simpler: find each { ... } top-level object.
    let mut conflicts = Vec::new();
    let mut depth = 0i32;
    let mut obj_start: Option<usize> = None;
    for (i, ch) in array_content.char_indices() {
        match ch {
            '{' => {
                if depth == 0 {
                    obj_start = Some(i);
                }
                depth += 1;
            }
            '}' => {
                depth -= 1;
                if depth == 0 {
                    if let Some(start) = obj_start.take() {
                        let obj_str = &array_content[start..=i];
                        if let Some(c) = parse_conflict_obj(obj_str) {
                            conflicts.push(c);
                        }
                    }
                }
            }
            _ => {}
        }
    }

    Ok(conflicts)
}

/// Extract a string value for `"key": "value"` from a JSON object string.
fn json_str_field<'a>(obj: &'a str, key: &str) -> Option<&'a str> {
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

/// Extract a u64 value for `"key": N` from a JSON object string.
fn json_u64_field(obj: &str, key: &str) -> Option<u64> {
    let search = format!("\"{}\":", key);
    let pos = obj.find(&search)?;
    let after = obj[pos + search.len()..].trim_start();
    let digits: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
    digits.parse().ok()
}

/// Parse a single conflict object `{...}` string into a [`PendingConflict`].
fn parse_conflict_obj(obj: &str) -> Option<PendingConflict> {
    let path = json_str_field(obj, "path")?.to_string();
    let ours_leverage = json_u64_field(obj, "ours_leverage").unwrap_or(0);
    let theirs_leverage = json_u64_field(obj, "theirs_leverage").unwrap_or(0);

    // Summarise genus as a human string for display.
    let genus_str = |prefix: &str| -> String {
        // Look for `"<prefix>_genus": null` or `"<prefix>_genus": {..}`
        let genus_key = format!("\"{prefix}_genus\":");
        if let Some(pos) = obj.find(&genus_key) {
            let after = obj[pos + genus_key.len()..].trim_start();
            if after.starts_with("null") {
                "no stamp".to_string()
            } else if after.starts_with('{') {
                // Extract set_k and oddity_s from the sub-object.
                let k = json_u64_field(after, "set_k").map(|v| v.to_string()).unwrap_or_else(|| "?".to_string());
                let s = json_u64_field(after, "oddity_s").map(|v| v.to_string()).unwrap_or_else(|| "?".to_string());
                format!("Set_{k}/s={s}")
            } else {
                "?".to_string()
            }
        } else {
            "?".to_string()
        }
    };

    Some(PendingConflict {
        path,
        ours_leverage,
        theirs_leverage,
        ours_genus_str: genus_str("ours"),
        theirs_genus_str: genus_str("theirs"),
    })
}

// ---------------------------------------------------------------------------
// Resolution types
// ---------------------------------------------------------------------------

/// The chosen resolution for one conflict.
#[derive(Debug, Clone)]
enum Resolution {
    /// Accept ours; write a battle record noting the force committed.
    Battle { force_size: u64 },
    /// Write a contract file and accept theirs.
    Contract { terms: String },
    /// Branch theirs into a new branch; keep ours on main.
    Fork,
    /// Open $EDITOR so the user can manually resolve.
    Manual,
}

// ---------------------------------------------------------------------------
// Non-interactive path
// ---------------------------------------------------------------------------

/// Parse a JSON array of resolution plans from `input`.
///
/// Expected format:
/// ```json
/// [
///   {"path":"regions/foo.json","resolution":"battle","force_size":512},
///   {"path":"regions/bar.json","resolution":"contract","terms":"50/50 split"},
///   {"path":"regions/baz.json","resolution":"fork"},
///   {"path":"regions/qux.json","resolution":"manual"}
/// ]
/// ```
fn parse_resolution_plan(input: &str) -> Result<Vec<(String, Resolution)>, Box<dyn std::error::Error>> {
    let mut result = Vec::new();
    let mut depth = 0i32;
    let mut obj_start: Option<usize> = None;
    for (i, ch) in input.char_indices() {
        match ch {
            '{' => {
                if depth == 0 {
                    obj_start = Some(i);
                }
                depth += 1;
            }
            '}' => {
                depth -= 1;
                if depth == 0 {
                    if let Some(start) = obj_start.take() {
                        let obj = &input[start..=i];
                        let path = json_str_field(obj, "path")
                            .ok_or_else(|| format!("resolution entry missing 'path': {obj}"))?
                            .to_string();
                        let res_str = json_str_field(obj, "resolution")
                            .ok_or_else(|| format!("resolution entry missing 'resolution': {obj}"))?;
                        let resolution = match res_str {
                            "battle" => {
                                let force_size = json_u64_field(obj, "force_size").unwrap_or(256);
                                Resolution::Battle { force_size }
                            }
                            "contract" => {
                                let terms = json_str_field(obj, "terms")
                                    .unwrap_or("(no terms specified)")
                                    .to_string();
                                Resolution::Contract { terms }
                            }
                            "fork" => Resolution::Fork,
                            "manual" => Resolution::Manual,
                            other => {
                                return Err(format!("unknown resolution '{other}' for path '{path}'").into());
                            }
                        };
                        result.push((path, resolution));
                    }
                }
            }
            _ => {}
        }
    }
    Ok(result)
}

// ---------------------------------------------------------------------------
// Apply a single resolution
// ---------------------------------------------------------------------------

/// Apply one resolution to a conflicted path.
///
/// Mutates the working tree and index so the path is no longer in conflict.
/// Does NOT commit — the caller finalises with a merge commit.
fn apply_resolution(
    here: &std::path::Path,
    conflict: &PendingConflict,
    resolution: &Resolution,
) -> Result<(), Box<dyn std::error::Error>> {
    let path = &conflict.path;

    match resolution {
        Resolution::Battle { force_size } => {
            // Battle: accept our version (keep ours, discard theirs).
            // Write a battle record into scars/ so the outcome is traceable.
            let checkout = Command::new("git")
                .args(["checkout", "--ours", "--", path])
                .output()?;
            if !checkout.status.success() {
                return Err(format!(
                    "git checkout --ours failed for '{path}': {}",
                    String::from_utf8_lossy(&checkout.stderr)
                )
                .into());
            }

            // Write a battle scar.
            let scars_dir = here.join("scars");
            std::fs::create_dir_all(&scars_dir)?;
            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            let scar_name = format!(
                "{timestamp}-battle-{}.scar",
                path.replace('/', "-").replace('.', "_")
            );
            let scar_content = format!(
                "battle_path: {path}\n\
                 force_size: {force_size}\n\
                 outcome: ours_wins\n\
                 ours_leverage: {}\n\
                 theirs_leverage: {}\n\
                 timestamp: {timestamp}\n",
                conflict.ours_leverage, conflict.theirs_leverage
            );
            std::fs::write(scars_dir.join(&scar_name), &scar_content)?;

            // Stage both the resolved file and the new scar.
            let add = Command::new("git")
                .args(["add", "--", path, &format!("scars/{scar_name}")])
                .output()?;
            if !add.status.success() {
                return Err(format!(
                    "git add failed after battle resolution: {}",
                    String::from_utf8_lossy(&add.stderr)
                )
                .into());
            }
            println!("  ⚔  Battle resolved: kept ours for '{path}' (force={force_size}), scar written.");
        }

        Resolution::Contract { terms } => {
            // Contract: accept theirs; write a contract file.
            let checkout = Command::new("git")
                .args(["checkout", "--theirs", "--", path])
                .output()?;
            if !checkout.status.success() {
                return Err(format!(
                    "git checkout --theirs failed for '{path}': {}",
                    String::from_utf8_lossy(&checkout.stderr)
                )
                .into());
            }

            // Write contract file.
            let contracts_dir = here.join("contracts");
            std::fs::create_dir_all(&contracts_dir)?;
            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            let contract_name = format!(
                "{timestamp}-contract-{}.contract",
                path.replace('/', "-").replace('.', "_")
            );
            let contract_content = format!(
                "path: {path}\nterms: {terms}\nours_leverage: {}\ntheirs_leverage: {}\ntimestamp: {timestamp}\n",
                conflict.ours_leverage, conflict.theirs_leverage
            );
            std::fs::write(contracts_dir.join(&contract_name), &contract_content)?;

            let add = Command::new("git")
                .args(["add", "--", path, &format!("contracts/{contract_name}")])
                .output()?;
            if !add.status.success() {
                return Err(format!(
                    "git add failed after contract resolution: {}",
                    String::from_utf8_lossy(&add.stderr)
                )
                .into());
            }
            println!("  📜 Contract resolved: accepted theirs for '{path}', contract written.");
        }

        Resolution::Fork => {
            // Fork: create a new git branch from FETCH_HEAD (which contains theirs),
            // then keep ours on the current branch.
            // This fulfils: "create a new branch with theirs, accept ours on main".

            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            let branch_name = format!(
                "fork-{timestamp}-{}",
                path.split('/').last().unwrap_or("conflict").replace('.', "_")
            );

            // Create the fork branch at FETCH_HEAD (their universe's HEAD).
            // `git branch <name> FETCH_HEAD` works even during a pending merge.
            let branch_out = Command::new("git")
                .args(["branch", &branch_name, "FETCH_HEAD"])
                .output()?;
            if !branch_out.status.success() {
                return Err(format!(
                    "git branch {} FETCH_HEAD failed: {}",
                    branch_name,
                    String::from_utf8_lossy(&branch_out.stderr)
                )
                .into());
            }

            // Accept ours on main.
            let checkout = Command::new("git")
                .args(["checkout", "--ours", "--", path])
                .output()?;
            if !checkout.status.success() {
                return Err(format!(
                    "git checkout --ours failed for fork of '{path}': {}",
                    String::from_utf8_lossy(&checkout.stderr)
                )
                .into());
            }

            // Write a fork pointer recording the branch name.
            let forks_dir = here.join("forks");
            std::fs::create_dir_all(&forks_dir)?;
            let fork_name = format!(
                "{timestamp}-fork-{}.ref",
                path.replace('/', "-").replace('.', "_")
            );
            let fork_content = format!(
                "forked_path: {path}\nbranch: {branch_name}\nours_genus: {}\ntheirs_genus: {}\ntimestamp: {timestamp}\n\
                 note: theirs timeline diverged; branch '{branch_name}' holds their version.\n",
                conflict.ours_genus_str, conflict.theirs_genus_str
            );
            std::fs::write(forks_dir.join(&fork_name), &fork_content)?;

            let add = Command::new("git")
                .args(["add", "--", path, &format!("forks/{fork_name}")])
                .output()?;
            if !add.status.success() {
                return Err(format!(
                    "git add failed after fork resolution: {}",
                    String::from_utf8_lossy(&add.stderr)
                )
                .into());
            }
            println!(
                "  🌿 Fork resolved: kept ours for '{path}', branch '{branch_name}' holds theirs."
            );
        }

        Resolution::Manual => {
            // Open $EDITOR on the conflict file with markers intact.
            // After the editor exits, `git add` the file.
            let editor = std::env::var("EDITOR")
                .or_else(|_| std::env::var("VISUAL"))
                .unwrap_or_else(|_| "vi".to_string());
            let status = Command::new(&editor)
                .arg(here.join(path))
                .status()?;
            if !status.success() {
                return Err(format!("editor '{editor}' exited with non-zero status for '{path}'").into());
            }

            // After manual edit: re-check for conflict markers.
            let file_content = std::fs::read_to_string(here.join(path))?;
            if file_content.contains("<<<<<<<") {
                return Err(format!(
                    "file '{path}' still contains conflict markers after manual edit; \
                     resolve fully before continuing."
                )
                .into());
            }

            let add = Command::new("git").args(["add", "--", path]).output()?;
            if !add.status.success() {
                return Err(format!(
                    "git add failed after manual edit: {}",
                    String::from_utf8_lossy(&add.stderr)
                )
                .into());
            }
            println!("  ✏  Manual resolved: '{path}' staged.");
        }
    }

    Ok(())
}

// ---------------------------------------------------------------------------
// Finalize: merge commit
// ---------------------------------------------------------------------------

fn finalize_merge(
    conflicts: &[PendingConflict],
    pending_path: &std::path::Path,
) -> Result<(), Box<dyn std::error::Error>> {
    // Remove the pending-merge.json file — conflicts are resolved.
    std::fs::remove_file(pending_path)?;
    let _ = Command::new("git")
        .args(["rm", "--cached", "--", ".gitverse/pending-merge.json"])
        .output(); // best-effort; file was written outside git so may not be tracked

    // Build merge commit message with resolution trailers.
    let resolution_notes: Vec<String> = conflicts
        .iter()
        .map(|c| format!("Resolved-path: {}", c.path))
        .collect();
    let mut commit_msg = format!(
        "emanon: negotiate — {} conflict{} resolved\n\n{}\n",
        conflicts.len(),
        if conflicts.len() == 1 { "" } else { "s" },
        resolution_notes.join("\n")
    );
    commit_msg.push_str("\nEmanon-negotiate: complete\n");

    let commit = Command::new("git")
        .args(["commit", "--no-edit", "-m", &commit_msg])
        .output()?;
    if !commit.status.success() {
        // --no-edit might fail if there's nothing to commit or MERGE_HEAD is gone.
        // Try a plain commit.
        let commit2 = Command::new("git")
            .args(["commit", "-m", &commit_msg])
            .output()?;
        if !commit2.status.success() {
            return Err(format!(
                "git commit failed after conflict resolution:\n{}",
                String::from_utf8_lossy(&commit2.stderr)
            )
            .into());
        }
    }

    let sha = Command::new("git")
        .args(["rev-parse", "--short", "HEAD"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|| "(unknown)".to_string());

    println!("\nAll conflicts resolved. Merge committed [{sha}].");
    Ok(())
}

// ---------------------------------------------------------------------------
// TUI
// ---------------------------------------------------------------------------

/// UI state machine.
#[derive(Debug, Clone, PartialEq, Eq)]
enum UiMode {
    /// Browsing the conflict list.
    ConflictList,
    /// Selecting a resolution action for the currently highlighted conflict.
    ActionMenu,
    /// Prompting for a text parameter (force size for battle, terms for contract).
    TextPrompt { action_idx: usize },
    /// All done — exit TUI with resolutions collected.
    Done,
    /// User requested quit without completing (q or Ctrl-C).
    Quit,
}

const ACTIONS: &[&str] = &["Battle  (keep ours, write scar)", "Contract  (accept theirs, draft contract)", "Fork  (keep ours, write fork pointer)", "Manual  (open $EDITOR)"];

struct NegotiateState {
    conflicts: Vec<PendingConflict>,
    /// Which resolution (if any) has been chosen for each conflict.
    resolutions: Vec<Option<Resolution>>,
    /// The currently highlighted row in the list.
    list_state: ListState,
    /// The highlighted option in the action menu.
    action_cursor: usize,
    mode: UiMode,
    /// Text being typed in TextPrompt mode.
    prompt_buf: String,
    /// Status message shown at bottom.
    status: String,
}

impl NegotiateState {
    fn new(conflicts: Vec<PendingConflict>) -> Self {
        let n = conflicts.len();
        let mut list_state = ListState::default();
        if n > 0 {
            list_state.select(Some(0));
        }
        NegotiateState {
            conflicts,
            resolutions: vec![None; n],
            list_state,
            action_cursor: 0,
            mode: UiMode::ConflictList,
            prompt_buf: String::new(),
            status: "↑/↓ navigate  Enter to pick resolution  q to quit".to_string(),
        }
    }

    fn selected(&self) -> usize {
        self.list_state.selected().unwrap_or(0)
    }

    fn all_resolved(&self) -> bool {
        self.resolutions.iter().all(|r| r.is_some())
    }
}

fn run_tui(state: &mut NegotiateState) -> Result<(), Box<dyn std::error::Error>> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let result = tui_loop(&mut terminal, state);

    // Always restore terminal even if we errored or the user quit.
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    result?;

    if state.mode == UiMode::Quit {
        println!("Negotiate cancelled.");
        std::process::exit(0);
    }

    Ok(())
}

fn tui_loop<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    state: &mut NegotiateState,
) -> Result<(), Box<dyn std::error::Error>> {
    loop {
        terminal.draw(|f| draw_ui(f, state))?;

        match state.mode {
            UiMode::Done | UiMode::Quit => break,
            _ => {}
        }

        // Poll for events with a 200ms timeout so the UI stays responsive.
        if event::poll(std::time::Duration::from_millis(200))? {
            if let Event::Key(key) = event::read()? {
                handle_key(state, key.code, key.modifiers);
            }
        }

        match state.mode {
            UiMode::Done | UiMode::Quit => break,
            _ => {}
        }
    }
    Ok(())
}

fn handle_key(state: &mut NegotiateState, code: KeyCode, modifiers: KeyModifiers) {
    // Ctrl-C always quits (terminal cleanup happens in run_tui).
    if modifiers.contains(KeyModifiers::CONTROL) && code == KeyCode::Char('c') {
        state.mode = UiMode::Quit;
        return;
    }

    match &state.mode.clone() {
        UiMode::ConflictList => {
            match code {
                KeyCode::Char('q') => {
                    state.mode = UiMode::Quit;
                }
                KeyCode::Down | KeyCode::Char('j') => {
                    let n = state.conflicts.len();
                    let next = (state.selected() + 1) % n;
                    state.list_state.select(Some(next));
                }
                KeyCode::Up | KeyCode::Char('k') => {
                    let n = state.conflicts.len();
                    let sel = state.selected();
                    let prev = if sel == 0 { n - 1 } else { sel - 1 };
                    state.list_state.select(Some(prev));
                }
                KeyCode::Enter => {
                    state.action_cursor = 0;
                    state.mode = UiMode::ActionMenu;
                    state.status = "↑/↓ choose resolution  Enter confirm  Esc back".to_string();
                }
                _ => {}
            }
        }

        UiMode::ActionMenu => {
            match code {
                KeyCode::Esc => {
                    state.mode = UiMode::ConflictList;
                    state.status = "↑/↓ navigate  Enter to pick resolution  q to quit".to_string();
                }
                KeyCode::Down | KeyCode::Char('j') => {
                    state.action_cursor = (state.action_cursor + 1) % ACTIONS.len();
                }
                KeyCode::Up | KeyCode::Char('k') => {
                    state.action_cursor = if state.action_cursor == 0 {
                        ACTIONS.len() - 1
                    } else {
                        state.action_cursor - 1
                    };
                }
                KeyCode::Enter => {
                    // action_cursor: 0=battle, 1=contract, 2=fork, 3=manual
                    match state.action_cursor {
                        0 => {
                            // Battle — prompt for force size
                            state.prompt_buf = "512".to_string();
                            state.mode = UiMode::TextPrompt { action_idx: 0 };
                            state.status = "Enter force size (bits) then press Enter".to_string();
                        }
                        1 => {
                            // Contract — prompt for terms
                            state.prompt_buf.clear();
                            state.mode = UiMode::TextPrompt { action_idx: 1 };
                            state.status = "Enter contract terms then press Enter".to_string();
                        }
                        2 => {
                            // Fork — no params needed
                            let sel = state.selected();
                            state.resolutions[sel] = Some(Resolution::Fork);
                            state.mode = UiMode::ConflictList;
                            if state.all_resolved() {
                                state.mode = UiMode::Done;
                            } else {
                                state.status = format!(
                                    "Fork chosen for '{}'. {}/{} resolved.",
                                    state.conflicts[sel].path,
                                    state.resolutions.iter().filter(|r| r.is_some()).count(),
                                    state.conflicts.len()
                                );
                            }
                        }
                        3 => {
                            // Manual — no params needed in TUI; will open editor when applied
                            let sel = state.selected();
                            state.resolutions[sel] = Some(Resolution::Manual);
                            state.mode = UiMode::ConflictList;
                            if state.all_resolved() {
                                state.mode = UiMode::Done;
                            } else {
                                state.status = format!(
                                    "Manual chosen for '{}'. {}/{} resolved.",
                                    state.conflicts[sel].path,
                                    state.resolutions.iter().filter(|r| r.is_some()).count(),
                                    state.conflicts.len()
                                );
                            }
                        }
                        _ => {}
                    }
                }
                _ => {}
            }
        }

        UiMode::TextPrompt { action_idx } => {
            let action_idx = *action_idx;
            match code {
                KeyCode::Esc => {
                    state.mode = UiMode::ActionMenu;
                    state.prompt_buf.clear();
                    state.status = "↑/↓ choose resolution  Enter confirm  Esc back".to_string();
                }
                KeyCode::Backspace => {
                    state.prompt_buf.pop();
                }
                KeyCode::Enter => {
                    let input = state.prompt_buf.trim().to_string();
                    let sel = state.selected();
                    let resolution = match action_idx {
                        0 => {
                            let force_size = input.parse::<u64>().unwrap_or(512);
                            Resolution::Battle { force_size }
                        }
                        1 => {
                            let terms = if input.is_empty() { "(no terms)".to_string() } else { input };
                            Resolution::Contract { terms }
                        }
                        _ => unreachable!(),
                    };
                    state.resolutions[sel] = Some(resolution);
                    state.prompt_buf.clear();
                    state.mode = UiMode::ConflictList;
                    if state.all_resolved() {
                        state.mode = UiMode::Done;
                    } else {
                        let resolved = state.resolutions.iter().filter(|r| r.is_some()).count();
                        state.status = format!(
                            "{}/{} conflicts resolved. Select next.",
                            resolved,
                            state.conflicts.len()
                        );
                    }
                }
                KeyCode::Char(c) => {
                    state.prompt_buf.push(c);
                }
                _ => {}
            }
        }

        UiMode::Done => {}
    }
}

fn draw_ui(f: &mut ratatui::Frame, state: &mut NegotiateState) {
    let area = f.area();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Min(5),
            Constraint::Length(10),
            Constraint::Length(3),
        ])
        .split(area);

    // -- Top: conflict list --
    let items: Vec<ListItem> = state
        .conflicts
        .iter()
        .enumerate()
        .map(|(i, c)| {
            let resolved_tag = match &state.resolutions[i] {
                Some(Resolution::Battle { .. }) => " [⚔ battle]",
                Some(Resolution::Contract { .. }) => " [📜 contract]",
                Some(Resolution::Fork) => " [🌿 fork]",
                Some(Resolution::Manual) => " [✏ manual]",
                None => "",
            };
            let text = format!(
                "{} ours:{}/lev{} ↔ theirs:{}/lev{}{}",
                c.path,
                c.ours_genus_str,
                c.ours_leverage,
                c.theirs_genus_str,
                c.theirs_leverage,
                resolved_tag
            );
            ListItem::new(text)
        })
        .collect();

    let list = List::new(items)
        .block(Block::default().borders(Borders::ALL).title(" Pending Conflicts "))
        .highlight_style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
        .highlight_symbol("▶ ");

    f.render_stateful_widget(list, chunks[0], &mut state.list_state);

    // -- Middle: action menu or prompt --
    match &state.mode {
        UiMode::ActionMenu => {
            let action_items: Vec<ListItem> = ACTIONS
                .iter()
                .enumerate()
                .map(|(i, &a)| {
                    if i == state.action_cursor {
                        ListItem::new(Line::from(vec![
                            Span::styled("▶ ", Style::default().fg(Color::Yellow)),
                            Span::styled(a, Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                        ]))
                    } else {
                        ListItem::new(format!("  {a}"))
                    }
                })
                .collect();
            let sel = state.selected();
            let title = format!(" Resolve: {} ", state.conflicts[sel].path);
            let menu = List::new(action_items)
                .block(Block::default().borders(Borders::ALL).title(title));
            f.render_widget(menu, chunks[1]);
        }
        UiMode::TextPrompt { action_idx } => {
            let label = match action_idx {
                0 => "Force size (bits): ",
                1 => "Contract terms: ",
                _ => "Input: ",
            };
            let text = format!("{}{}_", label, state.prompt_buf);
            let prompt = Paragraph::new(text)
                .block(Block::default().borders(Borders::ALL).title(" Input "))
                .style(Style::default().fg(Color::Cyan));
            f.render_widget(prompt, chunks[1]);
        }
        _ => {
            // Show a help panel.
            let resolved = state.resolutions.iter().filter(|r| r.is_some()).count();
            let help_text = format!(
                "{}/{} conflicts resolved\n\nPress Enter on a conflict to select its resolution.",
                resolved,
                state.conflicts.len()
            );
            let help = Paragraph::new(help_text)
                .block(Block::default().borders(Borders::ALL).title(" Help "));
            f.render_widget(help, chunks[1]);
        }
    }

    // -- Bottom: status bar --
    let status = Paragraph::new(state.status.clone())
        .block(Block::default().borders(Borders::ALL))
        .style(Style::default().fg(Color::DarkGray));
    f.render_widget(status, chunks[2]);
}

// ---------------------------------------------------------------------------
// Main cmd_negotiate entry point
// ---------------------------------------------------------------------------

fn cmd_negotiate(non_interactive: bool) -> Result<(), Box<dyn std::error::Error>> {
    let here = std::env::current_dir()?;
    let gitverse = here.join(".gitverse");
    if !gitverse.exists() {
        return Err(
            "not an Emanon universe — .gitverse/ not found.\n\
             Run `emanon init <name>` and `cd <name>` first."
                .into(),
        );
    }

    let conflicts = load_pending_conflicts(&gitverse)?;
    if conflicts.is_empty() {
        println!("No pending conflicts. Nothing to negotiate.");
        return Ok(());
    }

    println!("Negotiating {} conflict{}...", conflicts.len(), if conflicts.len() == 1 { "" } else { "s" });

    let resolved_pairs: Vec<(PendingConflict, Resolution)> = if non_interactive {
        // Read JSON plan from stdin.
        let mut input = String::new();
        use std::io::Read;
        io::stdin().read_to_string(&mut input)?;
        let plan = parse_resolution_plan(&input)?;

        // Match plan entries to conflicts by path.
        let mut out = Vec::new();
        for conflict in &conflicts {
            let entry = plan.iter().find(|(p, _)| p == &conflict.path).ok_or_else(|| {
                format!(
                    "no resolution provided for path '{}' in the JSON plan",
                    conflict.path
                )
            })?;
            out.push((conflict.clone(), entry.1.clone()));
        }
        out
    } else {
        // Interactive TUI.
        let mut state = NegotiateState::new(conflicts.clone());
        run_tui(&mut state)?;

        // Collect results.
        conflicts
            .into_iter()
            .zip(state.resolutions.into_iter())
            .map(|(c, r)| {
                (c.clone(), r.unwrap_or(Resolution::Manual))
            })
            .collect()
    };

    // Apply each resolution.
    for (conflict, resolution) in &resolved_pairs {
        println!("Resolving '{}'...", conflict.path);
        apply_resolution(&here, conflict, resolution)?;
    }

    // Finalize with a merge commit.
    let all_conflicts: Vec<PendingConflict> = resolved_pairs.into_iter().map(|(c, _)| c).collect();
    let pending_path = gitverse.join("pending-merge.json");
    finalize_merge(&all_conflicts, &pending_path)?;

    Ok(())
}

// ---------------------------------------------------------------------------
// emanon validate
// ---------------------------------------------------------------------------

/// Walk a directory tree under `dir` and append a warning for any text file
/// in `regions/` that contains no parseable genus stamp.
///
/// Binary files and `.genus` sidecars are skipped.  `.gitkeep` sentinels are
/// also skipped (they are intentionally stamp-free).
fn check_genus_stamps_in_dir(
    dir: &Path,
    root: &Path,
    warnings: &mut Vec<String>,
) {
    let entries = match std::fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return,
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            check_genus_stamps_in_dir(&path, root, warnings);
        } else if path.is_file() {
            let name = path
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("");
            // Skip sentinels and sidecars.
            if name == ".gitkeep" || name.ends_with(".genus") {
                continue;
            }
            // Only attempt to parse text files.
            if let Ok(content) = std::fs::read_to_string(&path) {
                if parse_genus_stamp(&content).is_none() {
                    let rel = path.strip_prefix(root).unwrap_or(&path);
                    warnings.push(format!(
                        "no genus stamp in regions/ file: {}",
                        rel.display()
                    ));
                }
            }
        }
    }
}

/// Implements `emanon validate [--strict]`.
///
/// Validation is split into two severity levels:
///
/// **Errors** (non-zero exit):
///   - Missing required directory (`.gitverse/`, `regions/`, `contracts/`, `scars/`, `forks/`)
///   - Missing required file (`.gitverse/values.json`, `.gitattributes`)
///   - `values.json` missing a required schema key or has mismatched braces
///   - `.gitattributes` missing one of the three `merge=` driver lines
///
/// **Warnings** (zero exit unless `--strict`):
///   - A commit message does not match the `snapshot N:` or `init:` format
///   - A file in `regions/` has no parseable genus stamp
///
/// Exits 0 on success, 1 on validation error, 2 on internal I/O error.
fn cmd_validate(strict: bool) -> Result<(), Box<dyn std::error::Error>> {
    let here = std::env::current_dir()?;

    let mut errors: Vec<String> = Vec::new();
    let mut warnings: Vec<String> = Vec::new();

    // ------------------------------------------------------------------
    // Rule 1 — Required directories
    // ------------------------------------------------------------------
    for dir in &[".gitverse", "regions", "contracts", "scars", "forks"] {
        if !here.join(dir).is_dir() {
            errors.push(format!("missing required directory: {dir}/"));
        }
    }

    // ------------------------------------------------------------------
    // Rule 2 — Required files
    // ------------------------------------------------------------------
    for file in &[".gitverse/values.json", ".gitattributes"] {
        if !here.join(file).exists() {
            errors.push(format!("missing required file: {file}"));
        }
    }

    // ------------------------------------------------------------------
    // Rule 3 — values.json schema validation
    //
    // Required top-level keys (per cmd_init VALUES_JSON constant):
    //   conflict_preference, fork_readiness, battle_threshold, host_authority_mode
    //
    // We do not pull in a JSON schema crate to keep the dependency tree
    // minimal — the hand-parser already used throughout the codebase is
    // sufficient for this structural check.
    // ------------------------------------------------------------------
    let values_path = here.join(".gitverse/values.json");
    if values_path.exists() {
        match std::fs::read_to_string(&values_path) {
            Err(e) => errors.push(format!("cannot read .gitverse/values.json: {e}")),
            Ok(content) => {
                // Structural check: balanced braces.
                let opens = content.chars().filter(|&c| c == '{').count();
                let closes = content.chars().filter(|&c| c == '}').count();
                if opens == 0 || opens != closes {
                    errors.push(
                        "values.json is not valid JSON (unbalanced or missing braces)".to_string(),
                    );
                }
                // Required key presence check.
                for key in &[
                    "conflict_preference",
                    "fork_readiness",
                    "battle_threshold",
                    "host_authority_mode",
                ] {
                    let search = format!("\"{}\"", key);
                    if !content.contains(&search) {
                        errors.push(format!(
                            ".gitverse/values.json missing required key: \"{key}\""
                        ));
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    // Rule 4 — .gitattributes merge-driver lines
    //
    // Each of the three canonical path patterns must have a `merge=<driver>`
    // token on the same line.
    // ------------------------------------------------------------------
    let gitattr_path = here.join(".gitattributes");
    if gitattr_path.exists() {
        match std::fs::read_to_string(&gitattr_path) {
            Err(e) => errors.push(format!("cannot read .gitattributes: {e}")),
            Ok(content) => {
                let required = [
                    ("regions/**", "emanon-collatz"),
                    ("contracts/**", "emanon-contract"),
                    ("scars/**", "emanon-append-only"),
                ];
                for (pattern, driver) in &required {
                    let found = content.lines().any(|line| {
                        let l = line.trim();
                        // Accept both "regions/**" and "regions/**       merge=…"
                        l.starts_with(pattern)
                            && l.contains(&format!("merge={driver}"))
                    });
                    if !found {
                        errors.push(format!(
                            ".gitattributes missing: {pattern}   merge={driver}"
                        ));
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------------
    // Rule 5 (warn) — commit message format
    //
    // Every commit subject should be one of:
    //   "snapshot N: ..."  — produced by `emanon snapshot`
    //   "init: ..."        — bootstrap commit from `emanon init`
    //   "Merge …"          — git merge commits
    //
    // Commits that look like WIP or tool commits (feat/fix/chore/etc.) are
    // warned about but do not fail validation — teams may have commits from
    // tooling outside emanon.
    // ------------------------------------------------------------------
    let log_output = Command::new("git")
        .args(["log", "--format=%s", "HEAD"])
        .current_dir(&here)
        .output();
    match log_output {
        Ok(out) if out.status.success() => {
            let subjects = String::from_utf8_lossy(&out.stdout);
            for subject in subjects.lines() {
                let s = subject.trim();
                if s.is_empty() {
                    continue;
                }
                let ok = s.starts_with("snapshot ")
                    || s.starts_with("init:")
                    || s.starts_with("Merge ")
                    || s.starts_with("[WIP ")      // in-progress commits
                    || s.starts_with("feat(")      // tool commits (CI/CD)
                    || s.starts_with("chore(")
                    || s.starts_with("fix(");
                if !ok {
                    warnings.push(format!(
                        "commit message does not match emanon format: \"{s}\""
                    ));
                }
            }
        }
        // Not in a git repo or git not available — skip this check.
        _ => {}
    }

    // ------------------------------------------------------------------
    // Rule 6 (warn) — genus stamps in regions/
    // ------------------------------------------------------------------
    let regions_dir = here.join("regions");
    if regions_dir.is_dir() {
        check_genus_stamps_in_dir(&regions_dir, &here, &mut warnings);
    }

    // ------------------------------------------------------------------
    // Report
    // ------------------------------------------------------------------
    if !warnings.is_empty() {
        eprintln!("⚠️   Warnings ({}):", warnings.len());
        for w in &warnings {
            eprintln!("    • {w}");
        }
    }

    // In strict mode, warnings are promoted to errors.
    if strict {
        for w in warnings.drain(..) {
            errors.push(w);
        }
    }

    if errors.is_empty() {
        println!(
            "✅  Universe validates OK{}",
            if warnings.is_empty() { "." } else { " (with warnings — see above)." }
        );
        Ok(())
    } else {
        eprintln!(
            "❌  Validation failed ({} error{}):",
            errors.len(),
            if errors.len() == 1 { "" } else { "s" }
        );
        for e in &errors {
            eprintln!("    • {e}");
        }
        Err(format!(
            "{} validation error{}",
            errors.len(),
            if errors.len() == 1 { "" } else { "s" }
        )
        .into())
    }
}

// ---------------------------------------------------------------------------
// Registry — config, helpers, and commands
// ---------------------------------------------------------------------------

const DEFAULT_REGISTRY_URL: &str = "https://github.com/forgetthefrets/emanon-registry";

/// Runtime configuration loaded from `~/.config/emanon/config.toml`.
///
/// Minimal hand-rolled TOML reader: only `[registry]` section is parsed.
struct EmanonConfig {
    /// Registry repo HTTPS URL (default: DEFAULT_REGISTRY_URL).
    registry_url: String,
    /// Ed25519 public key (Base58, 43–44 chars) for registry entry signing.
    owner_pubkey: Option<String>,
    /// Universe name override (defaults to current directory name).
    universe_name: Option<String>,
    /// Git remote to use when reading git_url for push (default: "origin").
    git_remote: String,
}

/// Load configuration from `~/.config/emanon/config.toml`.
/// Falls back to defaults for any missing key.
fn load_emanon_config() -> EmanonConfig {
    let mut registry_url = DEFAULT_REGISTRY_URL.to_string();
    let mut owner_pubkey: Option<String> = None;
    let mut universe_name: Option<String> = None;
    let mut git_remote = "origin".to_string();

    let config_path = std::env::var("HOME")
        .map(|h| format!("{h}/.config/emanon/config.toml"))
        .unwrap_or_default();

    if !config_path.is_empty() {
        if let Ok(content) = std::fs::read_to_string(&config_path) {
            let mut in_registry = false;
            let mut in_universe = false;
            for line in content.lines() {
                let trimmed = line.trim();
                // Skip comments and blank lines.
                if trimmed.is_empty() || trimmed.starts_with('#') {
                    continue;
                }
                if trimmed.starts_with('[') {
                    in_registry = trimmed == "[registry]";
                    in_universe = trimmed == "[universe]";
                    continue;
                }
                if let Some((k, v)) = parse_toml_kv(trimmed) {
                    if in_registry {
                        match k {
                            "url" => registry_url = v.to_string(),
                            "owner_pubkey" => owner_pubkey = Some(v.to_string()),
                            "git_remote" => git_remote = v.to_string(),
                            _ => {}
                        }
                    } else if in_universe {
                        if k == "name" {
                            universe_name = Some(v.to_string());
                        }
                    }
                }
            }
        }
    }

    EmanonConfig { registry_url, owner_pubkey, universe_name, git_remote }
}

/// Convenience loader that overrides registry_url from the command-line flag.
fn load_amenon_config_for_url(registry_override: Option<&str>) -> EmanonConfig {
    let mut cfg = load_emanon_config();
    if let Some(url) = registry_override {
        cfg.registry_url = url.to_string();
    }
    cfg
}

/// Parse a single `key = "value"` or `key = value` TOML line.
/// Returns `(key, value)` with surrounding whitespace and quotes stripped.
fn parse_toml_kv(line: &str) -> Option<(&str, &str)> {
    let eq = line.find('=')?;
    let key = line[..eq].trim();
    let val_raw = line[eq + 1..].trim();
    // Strip surrounding double-quotes if present.
    let val = if val_raw.starts_with('"') && val_raw.ends_with('"') && val_raw.len() >= 2 {
        &val_raw[1..val_raw.len() - 1]
    } else {
        val_raw
    };
    Some((key, val))
}

/// Derive the local cache directory for a registry URL.
///
/// Uses a simple hash-like encoding: replace non-alphanumeric chars with `-`.
/// Example: `https://github.com/foo/bar` → `~/.local/share/emanon/registry/https---github-com-foo-bar`
fn registry_cache_dir(registry_url: &str) -> Result<std::path::PathBuf, Box<dyn std::error::Error>> {
    let home = std::env::var("HOME")
        .map_err(|_| "HOME environment variable not set")?;
    let slug: String = registry_url
        .chars()
        .map(|c| if c.is_alphanumeric() || c == '.' { c } else { '-' })
        .collect();
    // Collapse consecutive dashes.
    let mut prev_dash = false;
    let slug: String = slug.chars().filter(|&c| {
        if c == '-' {
            if prev_dash { return false; }
            prev_dash = true;
        } else {
            prev_dash = false;
        }
        true
    }).collect();
    Ok(std::path::PathBuf::from(format!(
        "{home}/.local/share/emanon/registry/{slug}"
    )))
}

/// Compute SHA-256 of a file's content using `sha256sum` (Linux) or
/// `shasum -a 256` (macOS) and return the hex digest string.
#[allow(dead_code)]
fn sha256_file(path: &std::path::Path) -> Result<String, Box<dyn std::error::Error>> {
    // Try sha256sum first (Linux/coreutils), then shasum (macOS).
    let out = Command::new("sha256sum")
        .arg(path)
        .output()
        .or_else(|_| Command::new("shasum").args(["-a", "256"]).arg(path).output())?;

    if !out.status.success() {
        return Err(format!(
            "sha256 computation failed: {}",
            String::from_utf8_lossy(&out.stderr)
        )
        .into());
    }
    // Both tools output "<hex>  <filename>" — take the first token.
    let hex = String::from_utf8_lossy(&out.stdout)
        .split_whitespace()
        .next()
        .unwrap_or("")
        .to_string();
    if hex.len() != 64 {
        return Err(format!("unexpected sha256 output: {hex}").into());
    }
    Ok(hex)
}

/// Compute SHA-256 of an in-memory string using `echo -n | sha256sum`.
fn sha256_str(content: &str) -> Result<String, Box<dyn std::error::Error>> {
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

    if let Some(stdin) = child.stdin.take() {
        let mut stdin = stdin;
        stdin.write_all(content.as_bytes())?;
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
        return Err(format!("unexpected sha256 output: {hex}").into());
    }
    Ok(hex)
}

/// Clone or fetch a registry to its local cache directory.
/// Returns the cache directory path.
fn sync_registry(registry_url: &str) -> Result<std::path::PathBuf, Box<dyn std::error::Error>> {
    let cache_dir = registry_cache_dir(registry_url)?;

    if cache_dir.exists() {
        // Already cloned — just fetch to refresh.
        let fetch = Command::new("git")
            .args(["fetch", "--all", "--quiet"])
            .current_dir(&cache_dir)
            .output()?;
        if !fetch.status.success() {
            eprintln!(
                "warning: registry fetch failed (using cached data):\n{}",
                String::from_utf8_lossy(&fetch.stderr)
            );
        }
    } else {
        // First time — clone.
        std::fs::create_dir_all(cache_dir.parent().unwrap())?;
        let clone = Command::new("git")
            .args(["clone", "--depth=1", "--quiet", registry_url])
            .arg(&cache_dir)
            .output()?;
        if !clone.status.success() {
            return Err(format!(
                "git clone {} failed:\n{}",
                registry_url,
                String::from_utf8_lossy(&clone.stderr)
            )
            .into());
        }
    }

    Ok(cache_dir)
}

/// Read and minimally parse a registry entry JSON file.
/// Returns a flat key→value map (string values only, arrays as comma-joined).
fn parse_entry_json(path: &std::path::Path) -> std::collections::HashMap<String, String> {
    let mut map = std::collections::HashMap::new();
    let content = match std::fs::read_to_string(path) {
        Ok(c) => c,
        Err(_) => return map,
    };
    // Walk every line looking for `"key": "value"` or `"key": number` patterns.
    // This is intentionally simple — registry entries are machine-generated, well-formed JSON.
    for line in content.lines() {
        let trimmed = line.trim().trim_end_matches(',');
        if !trimmed.starts_with('"') { continue; }
        // Look for `"key": ...`
        if let Some(colon_pos) = trimmed.find("\": ") {
            let key = trimmed[1..colon_pos].to_string();
            let rest = trimmed[colon_pos + 3..].trim();
            let value = if rest.starts_with('"') && rest.ends_with('"') && rest.len() >= 2 {
                rest[1..rest.len() - 1].to_string()
            } else if rest == "null" {
                String::new()
            } else if rest.starts_with('[') {
                // Array: extract quoted items.
                let items: Vec<&str> = rest
                    .trim_matches(|c| c == '[' || c == ']')
                    .split(',')
                    .map(|s| s.trim().trim_matches('"'))
                    .filter(|s| !s.is_empty())
                    .collect();
                items.join(", ")
            } else {
                rest.to_string()
            };
            map.insert(key, value);
        }
    }
    map
}

/// Implements `emanon registry pull [--registry <url>]`.
///
/// Clones the registry repo locally (or fetches it if already cloned) for
/// offline use by `emanon registry list` and `emanon registry add-remote`.
/// Local cache lives at `~/.local/share/emanon/registry/<url-slug>/`.
fn cmd_registry_pull(registry_url: &str) -> Result<(), Box<dyn std::error::Error>> {
    let cache_dir = sync_registry(registry_url)?;
    println!("✅  Registry synced → {}", cache_dir.display());
    println!("    Source: {registry_url}");
    let entries_dir = cache_dir.join("entries");
    if entries_dir.exists() {
        let count = std::fs::read_dir(&entries_dir)
            .map(|rd| rd.filter_map(|e| e.ok()).filter(|e| {
                e.path().extension().map_or(false, |x| x == "json")
            }).count())
            .unwrap_or(0);
        println!("    {count} universe(s) in registry");
    }
    Ok(())
}

/// Implements `emanon registry list [--registry <url>] [--filter <jq-expr>]`.
///
/// Renders a tabular view of all universes in the registry.  Automatically
/// syncs the local cache if missing.  If `--filter` is supplied and `jq` is
/// available, each entry JSON is piped through the expression and only
/// matching entries are shown.
fn cmd_registry_list(
    registry_url: &str,
    filter: Option<&str>,
) -> Result<(), Box<dyn std::error::Error>> {
    let cache_dir = sync_registry(registry_url)?;
    let entries_dir = cache_dir.join("entries");

    if !entries_dir.exists() {
        println!("Registry is empty — no entries/ directory found.");
        return Ok(());
    }

    // Collect entry files.
    let mut entries: Vec<std::path::PathBuf> = std::fs::read_dir(&entries_dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().map_or(false, |x| x == "json"))
        .collect();
    entries.sort();

    if entries.is_empty() {
        println!("Registry is empty (0 universes).");
        return Ok(());
    }

    // Check if jq is available for filtering.
    let jq_available = filter.is_some() && Command::new("jq").arg("--version").output()
        .map(|o| o.status.success())
        .unwrap_or(false);

    // Table header.
    println!(
        "{:<24} {:<18} {:>9}  {:<40}  {}",
        "Name", "Owner (truncated)", "Snapshots", "Git URL", "Tags"
    );
    println!("{}", "-".repeat(120));

    let mut shown = 0usize;
    for entry_path in &entries {
        // Apply jq filter if requested.
        if let Some(expr) = filter {
            if jq_available {
                let out = Command::new("jq")
                    .args(["-e", expr])
                    .arg(entry_path)
                    .output()?;
                if !out.status.success() {
                    // Filter did not match this entry — skip.
                    continue;
                }
            }
        }

        let fields = parse_entry_json(entry_path);
        let name = fields.get("name").cloned().unwrap_or_else(|| {
            entry_path.file_stem()
                .map(|s| s.to_string_lossy().into_owned())
                .unwrap_or_default()
        });
        let owner = fields.get("owner_pubkey").cloned().unwrap_or_default();
        let owner_short = if owner.len() > 16 {
            format!("{}…", &owner[..16])
        } else {
            owner
        };
        let snapshots: u64 = fields.get("snapshot_count")
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);
        let git_url = fields.get("git_url").cloned().unwrap_or_default();
        let git_short = if git_url.len() > 38 {
            format!("{}…", &git_url[..38])
        } else {
            git_url
        };
        let tags = fields.get("tags").cloned().unwrap_or_default();

        println!(
            "{:<24} {:<18} {:>9}  {:<40}  {}",
            name, owner_short, snapshots, git_short, tags
        );
        shown += 1;
    }

    if shown == 0 && filter.is_some() {
        if !jq_available {
            println!("(--filter requires jq to be installed; showing all {}):", entries.len());
            // Re-run without filter.
            return cmd_registry_list(registry_url, None);
        }
        println!("No universes match filter: {}", filter.unwrap_or(""));
    } else {
        println!("{}", "-".repeat(120));
        println!("  {shown} universe(s)  •  registry: {registry_url}");
    }

    Ok(())
}

/// Implements `emanon registry push [--registry <url>]`.
///
/// Generates a registry entry JSON for the current universe, creates a branch
/// in a local clone of the registry repo, commits the entry, pushes, and opens
/// a PR via the `gh` CLI.
///
/// **Prerequisites (user must configure):**
/// - `owner_pubkey` in `~/.config/emanon/config.toml` (43–44 char Base58 Ed25519 key)
/// - `git_url` derivable from `git remote get-url origin` (or configured `git_remote`)
/// - `gh` CLI authenticated for the registry's GitHub org
///
/// **Note on `scrambled_root_hash`:**
/// Full Collatz Tᵏ-scrambled Merkle root computation arrives in M6.  This
/// implementation uses `sha256(HEAD_COMMIT_SHA)` as a well-defined placeholder
/// that is deterministic, verifiable, and distinct per snapshot.  The registry
/// CI (once activated) will need updating when real scrambling ships.
fn cmd_registry_push(
    registry_url: &str,
    config: &EmanonConfig,
) -> Result<(), Box<dyn std::error::Error>> {
    // --- Verify universe ---
    let here = std::env::current_dir()?;
    let gitverse = here.join(".gitverse");
    if !gitverse.exists() {
        return Err(
            "not an Emanon universe — .gitverse/ not found.\n\
             Run `emanon init <name>` then cd into it first."
                .into(),
        );
    }

    // --- owner_pubkey is required ---
    let owner_pubkey = config.owner_pubkey.as_deref().ok_or_else(|| {
        "owner_pubkey not configured.\n\
         Add to ~/.config/emanon/config.toml:\n\
         [registry]\n\
         owner_pubkey = \"<your-ed25519-base58-key>\""
    })?;
    if owner_pubkey.len() < 43 || owner_pubkey.len() > 44 {
        return Err(format!(
            "owner_pubkey must be 43–44 chars (Base58 Ed25519); got {} chars",
            owner_pubkey.len()
        )
        .into());
    }

    // --- Derive universe name ---
    let name = config.universe_name.as_deref()
        .map(String::from)
        .or_else(|| {
            here.file_name()
                .map(|n| n.to_string_lossy().to_lowercase().replace(' ', "-"))
        })
        .unwrap_or_else(|| "my-universe".to_string());

    // Validate name pattern (^[a-z0-9][a-z0-9_-]{1,62}[a-z0-9]$).
    if !name_is_valid_registry_entry(&name) {
        return Err(format!(
            "universe name '{name}' is not a valid registry entry name.\n\
             Names must be 3–64 chars, lowercase alphanumeric/hyphens/underscores,\n\
             starting and ending with alphanumeric.\n\
             Set [universe] name = \"<override>\" in ~/.config/emanon/config.toml."
        ).into());
    }

    // --- Read snapshot_count ---
    let snapshot_count_path = gitverse.join("snapshot_count");
    let snapshot_count: u64 = if snapshot_count_path.exists() {
        std::fs::read_to_string(&snapshot_count_path)?
            .trim()
            .parse()
            .unwrap_or(0)
    } else {
        0
    };

    // --- Read HEAD commit SHA ---
    let head_output = Command::new("git")
        .args(["rev-parse", "HEAD"])
        .output()?;
    if !head_output.status.success() {
        return Err("git rev-parse HEAD failed — is this a git repository with commits?".into());
    }
    let head_commit = String::from_utf8_lossy(&head_output.stdout)
        .trim()
        .to_string();
    if head_commit.len() != 40 {
        return Err(format!("unexpected HEAD SHA length: {head_commit}").into());
    }

    // --- Compute values_hash (sha256 of values.json content) ---
    let values_path = gitverse.join("values.json");
    if !values_path.exists() {
        return Err(".gitverse/values.json not found".into());
    }
    let values_content = std::fs::read_to_string(&values_path)?;
    let values_hex = sha256_str(&values_content)?;
    let values_hash = format!("sha256:{values_hex}");

    // --- Compute scrambled_root_hash (placeholder: sha256 of HEAD SHA) ---
    // Real Tᵏ-scrambled Merkle root computation arrives in M6.
    // sha256(HEAD_commit_SHA) is deterministic and verifiable in the interim.
    let scrambled_hex = sha256_str(&head_commit)?;
    let scrambled_root_hash = format!("sha256:{scrambled_hex}");

    // --- Derive git_url from remote ---
    let git_remote = &config.git_remote;
    let remote_url_output = Command::new("git")
        .args(["remote", "get-url", git_remote])
        .output()?;
    if !remote_url_output.status.success() {
        return Err(format!(
            "git remote get-url {git_remote} failed.\n\
             Ensure a remote named '{git_remote}' is configured, or set\n\
             git_remote = \"<name>\" in [registry] in ~/.config/emanon/config.toml."
        ).into());
    }
    let git_url_raw = String::from_utf8_lossy(&remote_url_output.stdout)
        .trim()
        .to_string();
    // Convert SSH → HTTPS if needed (git@github.com:owner/repo.git → https://github.com/owner/repo)
    let git_url = normalise_git_url(&git_url_raw);
    if !git_url.starts_with("https://") {
        return Err(format!(
            "git_url must use HTTPS; got: {git_url}\n\
             Configure an HTTPS remote or set [universe] git_url in config."
        ).into());
    }

    // --- Current timestamp ---
    let now_ts = current_iso8601_timestamp();

    // --- Determine created_at (keep original if re-pushing an existing entry) ---
    let created_at = now_ts.clone();

    // --- Build entry JSON ---
    let entry_json = format!(
        r#"{{
  "name": "{name}",
  "owner_pubkey": "{owner_pubkey}",
  "git_url": "{git_url}",
  "head_commit": "{head_commit}",
  "snapshot_count": {snapshot_count},
  "values_hash": "{values_hash}",
  "scrambled_root_hash": "{scrambled_root_hash}",
  "created_at": "{created_at}",
  "updated_at": "{now_ts}",
  "tags": [],
  "cnft_mint": null
}}
"#
    );

    println!("📦  Preparing registry entry for universe '{name}'...");
    println!("    HEAD:           {head_commit}");
    println!("    snapshot_count: {snapshot_count}");
    println!("    git_url:        {git_url}");

    // --- Clone registry to a temp dir and open a PR ---
    let tmp_parent = std::env::temp_dir().join("emanon-registry-push");
    std::fs::create_dir_all(&tmp_parent)?;
    // Unique subdir per invocation using HEAD SHA prefix.
    let tmp_clone = tmp_parent.join(&head_commit[..8]);
    if tmp_clone.exists() {
        std::fs::remove_dir_all(&tmp_clone)?;
    }

    println!("🔄  Cloning registry...");
    let clone = Command::new("git")
        .args(["clone", "--depth=1", "--quiet", registry_url])
        .arg(&tmp_clone)
        .output()?;
    if !clone.status.success() {
        return Err(format!(
            "git clone {} failed:\n{}",
            registry_url,
            String::from_utf8_lossy(&clone.stderr)
        )
        .into());
    }

    // --- Create a branch for this PR ---
    let branch_name = format!("add-{name}-{}", &head_commit[..8]);
    let checkout = Command::new("git")
        .args(["checkout", "-b", &branch_name])
        .current_dir(&tmp_clone)
        .output()?;
    if !checkout.status.success() {
        return Err(format!(
            "git checkout failed:\n{}",
            String::from_utf8_lossy(&checkout.stderr)
        )
        .into());
    }

    // --- Write entry file ---
    let entries_dir = tmp_clone.join("entries");
    std::fs::create_dir_all(&entries_dir)?;
    let entry_file = entries_dir.join(format!("{name}.json"));
    std::fs::write(&entry_file, &entry_json)?;

    // --- Commit ---
    let git_add = Command::new("git")
        .args(["add", &format!("entries/{name}.json")])
        .current_dir(&tmp_clone)
        .output()?;
    if !git_add.status.success() {
        return Err("git add failed in registry clone".into());
    }

    let commit_msg = format!(
        "add(universe): {name} @ {}\n\
         \n\
         Universe:       {name}\n\
         Git-URL:        {git_url}\n\
         Head-Commit:    {head_commit}\n\
         Snapshot-Count: {snapshot_count}\n\
         \n\
         Co-Authored-By: Alpha36 <alpha36@nanoclaw.local>",
        &head_commit[..8]
    );
    let commit = Command::new("git")
        .args(["commit", "-m", &commit_msg])
        .current_dir(&tmp_clone)
        .output()?;
    if !commit.status.success() {
        return Err(format!(
            "git commit failed:\n{}",
            String::from_utf8_lossy(&commit.stderr)
        )
        .into());
    }

    // --- Push ---
    println!("🚀  Pushing branch '{branch_name}'...");
    let push = Command::new("git")
        .args(["push", "origin", &branch_name])
        .current_dir(&tmp_clone)
        .output()?;
    if !push.status.success() {
        let sha_out = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .current_dir(&tmp_clone)
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        return Err(format!(
            "git push failed (commit {} pending push):\n{}",
            sha_out,
            String::from_utf8_lossy(&push.stderr)
        )
        .into());
    }

    // --- Open PR via gh CLI ---
    println!("📬  Opening PR...");
    let pr_title = format!("Add universe: {name}");
    let pr_body = format!(
        "## New Universe\n\
         \n\
         | Field | Value |\n\
         |---|---|\n\
         | Name | `{name}` |\n\
         | Git URL | {git_url} |\n\
         | Head Commit | `{head_commit}` |\n\
         | Snapshot Count | {snapshot_count} |\n\
         | Values Hash | `{values_hash}` |\n\
         \n\
         > **Note on `scrambled_root_hash`:** Full Collatz Tᵏ-scrambled Merkle root\n\
         > computation arrives in M6. This entry uses `sha256(HEAD)` as a\n\
         > deterministic placeholder.\n\
         \n\
         Generated by `emanon registry push` — Alpha36 worker."
    );

    let gh_pr = Command::new("gh")
        .args([
            "pr", "create",
            "--repo", registry_url.trim_start_matches("https://github.com/"),
            "--title", &pr_title,
            "--body", &pr_body,
            "--head", &branch_name,
            "--base", "main",
        ])
        .current_dir(&tmp_clone)
        .output()?;

    if gh_pr.status.success() {
        let pr_url = String::from_utf8_lossy(&gh_pr.stdout).trim().to_string();
        println!("✅  PR opened: {pr_url}");
    } else {
        let stderr = String::from_utf8_lossy(&gh_pr.stderr);
        // If gh fails (not auth'd against the registry org, etc.), the commit is
        // already pushed — surface the branch URL so the user can open a PR manually.
        let registry_base = registry_url.trim_end_matches(".git");
        println!(
            "⚠️  gh pr create failed (branch is pushed — open PR manually):\n\
             Branch:  {branch_name}\n\
             Compare: {registry_base}/compare/{branch_name}\n\
             Error:   {stderr}"
        );
    }

    // --- Clean up temp clone ---
    let _ = std::fs::remove_dir_all(&tmp_clone);

    Ok(())
}

/// Implements `emanon registry add-remote <entry-name> [--registry <url>] [--remote-name <name>]`.
///
/// Reads the universe's `git_url` from the local registry cache and adds it
/// as a named git remote in the current universe.  The local registry is synced
/// first so freshly-published universes are visible.
fn cmd_registry_add_remote(
    entry_name: &str,
    registry_url: &str,
    remote_name: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    // --- Verify we're in a git repo (not necessarily an Emanon universe —
    //     a player might want to add a remote before init'ing) ---
    let git_check = Command::new("git")
        .args(["rev-parse", "--git-dir"])
        .output()?;
    if !git_check.status.success() {
        return Err("not inside a git repository".into());
    }

    // --- Sync registry ---
    let cache_dir = sync_registry(registry_url)?;
    let entry_path = cache_dir.join("entries").join(format!("{entry_name}.json"));

    if !entry_path.exists() {
        return Err(format!(
            "registry entry '{entry_name}' not found.\n\
             Run `emanon registry list` to see available universes.\n\
             (Looked in: {})",
            entry_path.display()
        )
        .into());
    }

    // --- Parse git_url from entry ---
    let fields = parse_entry_json(&entry_path);
    let git_url = fields.get("git_url").cloned().ok_or_else(|| {
        format!("entry '{entry_name}' has no git_url field")
    })?;
    if git_url.is_empty() {
        return Err(format!("entry '{entry_name}' has an empty git_url").into());
    }

    // --- Check if remote already exists ---
    let remote_check = Command::new("git")
        .args(["remote", "get-url", remote_name])
        .output()?;
    if remote_check.status.success() {
        let existing = String::from_utf8_lossy(&remote_check.stdout).trim().to_string();
        if existing == git_url {
            println!("✅  Remote '{remote_name}' already points to {git_url}");
            return Ok(());
        }
        return Err(format!(
            "remote '{remote_name}' already exists pointing to '{existing}'.\n\
             Use a different --remote-name, or remove the existing remote first:\n\
             git remote remove {remote_name}"
        )
        .into());
    }

    // --- Add remote ---
    let add = Command::new("git")
        .args(["remote", "add", remote_name, &git_url])
        .output()?;
    if !add.status.success() {
        return Err(format!(
            "git remote add failed:\n{}",
            String::from_utf8_lossy(&add.stderr)
        )
        .into());
    }

    println!("✅  Remote added:");
    println!("    {remote_name}  →  {git_url}");
    println!();
    println!("    Fetch with:  git fetch {remote_name}");
    println!("    Merge with:  emanon merge {remote_name}/main");

    Ok(())
}

// ---------------------------------------------------------------------------
// Registry helpers
// ---------------------------------------------------------------------------

/// Validate a registry entry name against the schema pattern:
/// `^[a-z0-9][a-z0-9_-]{1,62}[a-z0-9]$` (total 3–64 chars).
fn name_is_valid_registry_entry(name: &str) -> bool {
    let bytes = name.as_bytes();
    let n = bytes.len();
    if n < 3 || n > 64 {
        return false;
    }
    let is_alnum = |b: u8| b.is_ascii_alphanumeric();
    let is_inner = |b: u8| b.is_ascii_alphanumeric() || b == b'-' || b == b'_';
    is_alnum(bytes[0]) && is_alnum(bytes[n - 1]) && bytes[1..n - 1].iter().all(|&b| is_inner(b))
}

/// Convert a git remote URL to HTTPS form.
/// `git@github.com:owner/repo.git` → `https://github.com/owner/repo`
fn normalise_git_url(raw: &str) -> String {
    let s = raw.trim();
    if s.starts_with("https://") {
        return s.trim_end_matches(".git").to_string();
    }
    // SSH format: git@host:path
    if let Some(at_pos) = s.find('@') {
        if let Some(colon_pos) = s.find(':') {
            if colon_pos > at_pos {
                let host = &s[at_pos + 1..colon_pos];
                let path = s[colon_pos + 1..].trim_end_matches(".git");
                return format!("https://{host}/{path}");
            }
        }
    }
    s.to_string()
}

/// Return an RFC 3339 timestamp for "now" using the `date` command.
/// Falls back to a static placeholder if `date` is unavailable.
fn current_iso8601_timestamp() -> String {
    Command::new("date")
        .args(["-u", "+%Y-%m-%dT%H:%M:%SZ"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|| "1970-01-01T00:00:00Z".to_string())
}

// ---------------------------------------------------------------------------
// stub helper
// ---------------------------------------------------------------------------

fn not_yet(feature: &str) {
    eprintln!("⏳  `{feature}` is not yet implemented.");
    eprintln!("    This subcommand is stubbed in milestone M0.");
    eprintln!("    Implementation arrives in a later milestone — stay tuned.");
    std::process::exit(1);
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Init { name, force } => {
            if let Err(e) = cmd_init(&name, force) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::Snapshot { message, no_stage } => {
            if let Err(e) = cmd_snapshot(message, no_stage) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::Merge { remote_branch } => {
            if let Err(e) = cmd_merge(&remote_branch) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::Negotiate { non_interactive } => {
            if let Err(e) = cmd_negotiate(non_interactive) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::MergeDriver { contract_mode, append_only, base, ours, theirs, path, output } => {
            let mode = if contract_mode {
                MergeMode::Contract
            } else if append_only {
                MergeMode::AppendOnly
            } else {
                MergeMode::Collatz
            };
            let out_path = output.as_deref().unwrap_or(&ours);
            match cmd_merge_driver(&mode, &base, &ours, &theirs, &path, out_path) {
                Ok(exit_code) => std::process::exit(exit_code),
                Err(e) => {
                    eprintln!("merge-driver error: {e}");
                    std::process::exit(2);
                }
            }
        }
        Commands::Fork { reason } => {
            let flag = reason
                .map(|r| format!(" -r \"{r}\""))
                .unwrap_or_default();
            not_yet(&format!("emanon fork{flag}"));
        }
        Commands::Contract { action } => match action {
            ContractAction::Draft => not_yet("emanon contract draft"),
            ContractAction::Sign => not_yet("emanon contract sign"),
            ContractAction::List => not_yet("emanon contract list"),
        },
        Commands::Write { path, content } => {
            if let Err(e) = cmd_write(&path, content) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::Genus { path } => {
            if let Err(e) = cmd_genus(&path) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
        Commands::Scan { remote } => {
            not_yet(&format!("emanon scan {remote}"));
        }
        Commands::Bounty { action } => match action {
            BountyAction::Post => not_yet("emanon bounty post"),
            BountyAction::List => not_yet("emanon bounty list"),
            BountyAction::Accept => not_yet("emanon bounty accept"),
            BountyAction::Deliver => not_yet("emanon bounty deliver"),
        },
        Commands::Tournament { action } => match action {
            TournamentAction::Join => not_yet("emanon tournament join"),
            TournamentAction::Leave => not_yet("emanon tournament leave"),
            TournamentAction::Play => not_yet("emanon tournament play"),
        },
        Commands::Registry { action } => match action {
            RegistryAction::Push { registry } => {
                let config = load_emanon_config();
                let url = registry.as_deref().unwrap_or(&config.registry_url);
                if let Err(e) = cmd_registry_push(url, &config) {
                    eprintln!("error: {e}");
                    std::process::exit(1);
                }
            }
            RegistryAction::Pull { registry } => {
                let config = load_amenon_config_for_url(registry.as_deref());
                if let Err(e) = cmd_registry_pull(&config.registry_url) {
                    eprintln!("error: {e}");
                    std::process::exit(1);
                }
            }
            RegistryAction::List { registry, filter } => {
                let config = load_amenon_config_for_url(registry.as_deref());
                if let Err(e) = cmd_registry_list(&config.registry_url, filter.as_deref()) {
                    eprintln!("error: {e}");
                    std::process::exit(1);
                }
            }
            RegistryAction::AddRemote { entry_name, registry, remote_name } => {
                let config = load_amenon_config_for_url(registry.as_deref());
                let rname = remote_name.as_deref().unwrap_or(&entry_name);
                if let Err(e) = cmd_registry_add_remote(&entry_name, &config.registry_url, rname) {
                    eprintln!("error: {e}");
                    std::process::exit(1);
                }
            }
        },
        Commands::Validate { strict } => {
            if let Err(e) = cmd_validate(strict) {
                eprintln!("error: {e}");
                std::process::exit(1);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Unit tests — merge-driver resolution rules
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // -----------------------------------------------------------------------
    // parse_genus_stamp
    // -----------------------------------------------------------------------

    #[test]
    fn parse_genus_stamp_valid() {
        let content = "# emanon:genus set_k=3 oddity_s=1 index_i=0\nsome content\n";
        let g = parse_genus_stamp(content).expect("should parse");
        assert_eq!(g.set_k, 3);
        assert_eq!(g.oddity_s, 1);
        assert_eq!(g.index_i, 0);
    }

    #[test]
    fn parse_genus_stamp_missing_prefix() {
        let content = "# not-a-genus-stamp\nsome content\n";
        assert!(parse_genus_stamp(content).is_none());
    }

    #[test]
    fn parse_genus_stamp_empty_file() {
        assert!(parse_genus_stamp("").is_none());
    }

    #[test]
    fn parse_genus_stamp_partial_fields() {
        // Missing index_i — should return None
        let content = "# emanon:genus set_k=3 oddity_s=1\n";
        assert!(parse_genus_stamp(content).is_none());
    }

    #[test]
    fn parse_genus_stamp_large_values() {
        let content = "# emanon:genus set_k=96 oddity_s=37 index_i=0\n";
        let g = parse_genus_stamp(content).expect("should parse");
        assert_eq!(g.set_k, 96);
        assert_eq!(g.oddity_s, 37);
    }

    // -----------------------------------------------------------------------
    // hybrid_merge — Rule 1: same set_k
    // -----------------------------------------------------------------------

    #[test]
    fn hybrid_merge_contains_both_versions() {
        let ours = "# emanon:genus set_k=3 oddity_s=1 index_i=0\nours content\n";
        let theirs = "# emanon:genus set_k=3 oddity_s=1 index_i=5\ntheirs content\n";
        let merged = hybrid_merge(ours, theirs);
        assert!(merged.contains("ours content"), "must contain ours body");
        assert!(merged.contains("theirs content"), "must contain theirs body");
        assert!(merged.contains("hybrid merge"), "must include hybrid merge marker");
    }

    #[test]
    fn hybrid_merge_has_separator_markers() {
        let merged = hybrid_merge("A\n", "B\n");
        assert!(merged.contains("<<<<<<<"), "must have opening marker");
        assert!(merged.contains("======="), "must have middle separator");
        assert!(merged.contains(">>>>>>>"), "must have closing marker");
    }

    // -----------------------------------------------------------------------
    // attenuated_merge — Rule 2: same oddity_s, different set_k
    // -----------------------------------------------------------------------

    #[test]
    fn attenuated_merge_contains_theirs_content() {
        let theirs = "# emanon:genus set_k=11 oddity_s=4 index_i=0\ntheirs data\n";
        let result = attenuated_merge(theirs, 4);
        assert!(result.contains("theirs data"), "attenuated merge must include theirs content");
    }

    #[test]
    fn attenuated_merge_has_beta_comment() {
        let theirs = "# emanon:genus set_k=11 oddity_s=4 index_i=0\ncontent\n";
        let result = attenuated_merge(theirs, 4);
        assert!(
            result.contains("genus-attenuated by β="),
            "must have attenuation comment; got: {result}"
        );
        assert!(result.contains("oddity_s=4"), "comment must include oddity_s");
    }

    #[test]
    fn attenuated_merge_beta_is_valid() {
        // β(s) must be in (0, 1] for any s
        for s in [0u64, 1, 2, 4, 7, 37] {
            let b = collatz_rs::beta(s);
            assert!(b > 0.0 && b <= 1.0, "β({s}) = {b} out of range");
        }
    }

    // -----------------------------------------------------------------------
    // write_conflict_markers — Rule 3: unrelated sets / no genus
    // -----------------------------------------------------------------------

    #[test]
    fn conflict_markers_contain_both_sides() {
        let conflict = write_conflict_markers("ours\n", "theirs\n", "unrelated-sets");
        assert!(conflict.contains("ours"), "must contain ours");
        assert!(conflict.contains("theirs"), "must contain theirs");
    }

    #[test]
    fn conflict_markers_have_git_format() {
        // Must use git-compatible conflict markers so editors highlight them
        let conflict = write_conflict_markers("A\n", "B\n", "test");
        assert!(conflict.contains("<<<<<<<"), "must have git opening marker");
        assert!(conflict.contains("======="), "must have git separator");
        assert!(conflict.contains(">>>>>>>"), "must have git closing marker");
    }

    #[test]
    fn conflict_markers_embed_reason() {
        let conflict = write_conflict_markers("A\n", "B\n", "no-genus-stamp");
        assert!(
            conflict.contains("no-genus-stamp"),
            "reason must appear in conflict marker; got: {conflict}"
        );
    }

    // -----------------------------------------------------------------------
    // cmd_merge_driver integration — via temp files
    // -----------------------------------------------------------------------

    fn tmp_file(dir: &std::path::Path, name: &str, content: &str) -> std::path::PathBuf {
        let p = dir.join(name);
        std::fs::write(&p, content).unwrap();
        p
    }

    #[test]
    fn driver_same_set_k_exits_0() {
        let dir = tempdir();
        let ours_content = "# emanon:genus set_k=3 oddity_s=1 index_i=0\nours data\n";
        let theirs_content = "# emanon:genus set_k=3 oddity_s=1 index_i=5\ntheirs data\n";
        let base = tmp_file(&dir, "base.txt", "# emanon:genus set_k=3 oddity_s=1 index_i=0\nbase\n");
        let ours = tmp_file(&dir, "ours.txt", ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Collatz,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "regions/test.rg",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 0, "same set_k must exit 0");
        let merged = std::fs::read_to_string(&out).unwrap();
        assert!(merged.contains("ours data"));
        assert!(merged.contains("theirs data"));
    }

    #[test]
    fn driver_same_oddity_different_k_exits_0() {
        let dir = tempdir();
        // set_k 3 vs 11, both oddity_s=1
        let ours_content = "# emanon:genus set_k=3 oddity_s=1 index_i=0\nours content\n";
        let theirs_content = "# emanon:genus set_k=11 oddity_s=1 index_i=0\ntheirs content\n";
        let base = tmp_file(&dir, "base.txt", "# emanon:genus set_k=3 oddity_s=1 index_i=0\nbase\n");
        let ours = tmp_file(&dir, "ours.txt", ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Collatz,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "regions/test.rg",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 0, "same oddity_s must exit 0");
        let merged = std::fs::read_to_string(&out).unwrap();
        assert!(merged.contains("theirs content"), "attenuated merge should use theirs");
        assert!(merged.contains("genus-attenuated by β="), "must have attenuation comment");
    }

    #[test]
    fn driver_unrelated_sets_exits_1() {
        let dir = tempdir();
        // set_k 3 (s=1) vs set_k 7 (s=4) — different k and different s
        let ours_content = "# emanon:genus set_k=3 oddity_s=1 index_i=0\nours content\n";
        let theirs_content = "# emanon:genus set_k=7 oddity_s=4 index_i=0\ntheirs content\n";
        let base = tmp_file(&dir, "base.txt", "# emanon:genus set_k=3 oddity_s=1 index_i=0\nbase\n");
        let ours = tmp_file(&dir, "ours.txt", ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Collatz,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "regions/test.rg",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 1, "unrelated sets must exit 1");
        let conflict = std::fs::read_to_string(&out).unwrap();
        assert!(conflict.contains("<<<<<<<"), "must have conflict markers");
        assert!(conflict.contains("unrelated-sets"), "must note reason");
    }

    #[test]
    fn driver_no_genus_stamp_exits_1() {
        let dir = tempdir();
        let base = tmp_file(&dir, "base.txt", "legacy content\n");
        let ours = tmp_file(&dir, "ours.txt", "legacy ours\n");
        let theirs = tmp_file(&dir, "theirs.txt", "legacy theirs\n");
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Collatz,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "regions/test.rg",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 1, "missing genus stamp must exit 1");
        let conflict = std::fs::read_to_string(&out).unwrap();
        assert!(conflict.contains("no-genus-stamp"), "must note reason");
    }

    // -----------------------------------------------------------------------
    // stub merge modes — contract and append-only fall back to Collatz
    // -----------------------------------------------------------------------

    #[test]
    fn contract_mode_stub_exits_0_on_same_set_k() {
        // --contract-mode is a stub; same-set_k still exits 0 via Collatz fallback
        let dir = tempdir();
        let ours_content = "# emanon:genus set_k=5 oddity_s=2 index_i=0\ncontract data\n";
        let theirs_content = "# emanon:genus set_k=5 oddity_s=2 index_i=3\nother data\n";
        let base = tmp_file(&dir, "base.txt", "# emanon:genus set_k=5 oddity_s=2 index_i=0\nbase\n");
        let ours = tmp_file(&dir, "ours.txt", ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Contract,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "contracts/deal.ct",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 0, "contract-mode stub must exit 0 for same set_k");
        let merged = std::fs::read_to_string(&out).unwrap();
        assert!(merged.contains("contract data"), "must include ours content");
        assert!(merged.contains("other data"), "must include theirs content");
    }

    #[test]
    fn append_only_stub_exits_0_on_same_set_k() {
        // --append-only is a stub; same-set_k still exits 0 via Collatz fallback
        let dir = tempdir();
        let ours_content = "# emanon:genus set_k=9 oddity_s=3 index_i=0\nscar data\n";
        let theirs_content = "# emanon:genus set_k=9 oddity_s=3 index_i=2\nother scar\n";
        let base = tmp_file(&dir, "base.txt", "# emanon:genus set_k=9 oddity_s=3 index_i=0\nbase\n");
        let ours = tmp_file(&dir, "ours.txt", ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::AppendOnly,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "scars/event.sc",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        assert_eq!(code, 0, "append-only stub must exit 0 for same set_k");
        let merged = std::fs::read_to_string(&out).unwrap();
        assert!(merged.contains("scar data"), "must include ours content");
        assert!(merged.contains("other scar"), "must include theirs content");
    }

    // -----------------------------------------------------------------------
    // .gitattributes content verification
    // -----------------------------------------------------------------------

    #[test]
    fn gitattributes_has_correct_per_path_drivers() {
        // Verify the GITATTRIBUTES constant routes each path to the right driver
        assert!(
            GITATTRIBUTES.contains("regions/**") && GITATTRIBUTES.contains("merge=emanon-collatz"),
            "regions/** must use emanon-collatz"
        );
        assert!(
            GITATTRIBUTES.contains("contracts/**") && GITATTRIBUTES.contains("merge=emanon-contract"),
            "contracts/** must use emanon-contract"
        );
        assert!(
            GITATTRIBUTES.contains("scars/**") && GITATTRIBUTES.contains("merge=emanon-append-only"),
            "scars/** must use emanon-append-only"
        );
        // Ensure old incorrect routing is gone
        assert!(
            !GITATTRIBUTES.contains("contracts/**  merge=emanon-collatz"),
            "contracts must NOT use emanon-collatz"
        );
        assert!(
            !GITATTRIBUTES.contains("scars/**  merge=emanon-collatz"),
            "scars must NOT use emanon-collatz"
        );
    }

    // -----------------------------------------------------------------------
    // parse_genus_stamp — JSON format (M1.4)
    // -----------------------------------------------------------------------

    #[test]
    fn parse_genus_stamp_json_bottom_line() {
        // JSON stamp at the bottom — as written by `emanon write`
        let content = "{\"foo\": 1}\n# emanon-genus: {\"set_k\": 13, \"oddity_s\": 5, \"index_i\": 2, \"writer\": \"a@b.com\", \"snapshot\": 42}\n";
        let g = parse_genus_stamp(content).expect("should parse JSON stamp");
        assert_eq!(g.set_k, 13);
        assert_eq!(g.oddity_s, 5);
        assert_eq!(g.index_i, 2);
    }

    #[test]
    fn parse_genus_stamp_json_only() {
        // File with only the stamp line (edge case)
        let content = "# emanon-genus: {\"set_k\": 1, \"oddity_s\": 0, \"index_i\": 0, \"writer\": \"x\", \"snapshot\": 0}\n";
        let g = parse_genus_stamp(content).expect("should parse JSON stamp");
        assert_eq!(g.set_k, 1);
        assert_eq!(g.oddity_s, 0);
        assert_eq!(g.index_i, 0);
    }

    #[test]
    fn parse_genus_stamp_legacy_mid_file() {
        // Legacy format not on first line — now found because we scan all lines
        let content = "line1\nline2\n# emanon:genus set_k=7 oddity_s=4 index_i=1\nline4\n";
        let g = parse_genus_stamp(content).expect("should parse legacy stamp");
        assert_eq!(g.set_k, 7);
        assert_eq!(g.oddity_s, 4);
        assert_eq!(g.index_i, 1);
    }

    #[test]
    fn parse_genus_stamp_no_match() {
        let content = "just plain text\nno stamps here\n";
        assert!(parse_genus_stamp(content).is_none());
    }

    // -----------------------------------------------------------------------
    // parse_genus_json
    // -----------------------------------------------------------------------

    #[test]
    fn parse_genus_json_valid() {
        let json = r#"{"set_k": 96, "oddity_s": 37, "index_i": 5, "writer": "dev@example.com", "snapshot": 7}"#;
        let g = parse_genus_json(json).expect("should parse");
        assert_eq!(g.set_k, 96);
        assert_eq!(g.oddity_s, 37);
        assert_eq!(g.index_i, 5);
    }

    #[test]
    fn parse_genus_json_missing_key() {
        let json = r#"{"set_k": 3, "oddity_s": 1}"#; // no index_i
        assert!(parse_genus_json(json).is_none());
    }

    // -----------------------------------------------------------------------
    // path_hash_low_bits
    // -----------------------------------------------------------------------

    #[test]
    fn path_hash_low_bits_range() {
        let h = path_hash_low_bits("regions/alpha/test.json");
        assert!(h < 256, "must be 0–255, got {h}");
    }

    #[test]
    fn path_hash_low_bits_different_paths() {
        // Different paths should not always hash to the same value.
        // This could theoretically collide — but with 256 buckets the probability
        // of any two of these colliding is low.
        let paths = ["a.json", "b.json", "regions/x", "regions/y", "scars/z"];
        let hashes: Vec<u64> = paths.iter().map(|p| path_hash_low_bits(p)).collect();
        // At least 2 of 5 must differ (probability of all equal is (1/256)^4 ≈ 0)
        let first = hashes[0];
        assert!(
            hashes.iter().any(|&h| h != first),
            "all paths hashed to the same value — hash is degenerate"
        );
    }

    // -----------------------------------------------------------------------
    // genus_stamp_json
    // -----------------------------------------------------------------------

    #[test]
    fn genus_stamp_json_format() {
        let genus = collatz_rs::Genus { set_k: 13, oddity_s: 5, index_i: 2 };
        let stamp = genus_stamp_json(&genus, "a@b.com", 42);
        assert!(stamp.starts_with("# emanon-genus: "), "must start with prefix");
        assert!(stamp.contains("\"set_k\": 13"), "must contain set_k");
        assert!(stamp.contains("\"oddity_s\": 5"), "must contain oddity_s");
        assert!(stamp.contains("\"index_i\": 2"), "must contain index_i");
        assert!(stamp.contains("\"writer\": \"a@b.com\""), "must contain writer");
        assert!(stamp.contains("\"snapshot\": 42"), "must contain snapshot");
    }

    #[test]
    fn genus_stamp_json_parseable_by_parse_genus_stamp() {
        // Round-trip: genus_stamp_json → parse_genus_stamp
        let genus = collatz_rs::Genus { set_k: 7, oddity_s: 4, index_i: 3 };
        let stamp = genus_stamp_json(&genus, "test@test.com", 10);
        let content = format!("some content\n{stamp}\n");
        let parsed = parse_genus_stamp(&content).expect("stamp must be parseable");
        assert_eq!(parsed.set_k, 7);
        assert_eq!(parsed.oddity_s, 4);
        assert_eq!(parsed.index_i, 3);
    }

    // -----------------------------------------------------------------------
    // merge driver can extract stamps from files written by cmd_write
    // -----------------------------------------------------------------------

    #[test]
    fn merge_driver_understands_m14_stamps() {
        // Simulate two files written by `emanon write` with same set_k
        // (Genus { set_k: 1, oddity_s: 1, index_i: 0 } for seed=2)
        let genus_ours = collatz_rs::Genus { set_k: 1, oddity_s: 1, index_i: 0 };
        let genus_theirs = collatz_rs::Genus { set_k: 1, oddity_s: 1, index_i: 0 };
        let ours_content = format!(
            "{{\"foo\": 1}}\n{}\n",
            genus_stamp_json(&genus_ours, "alice@test.com", 5)
        );
        let theirs_content = format!(
            "{{\"foo\": 2}}\n{}\n",
            genus_stamp_json(&genus_theirs, "bob@test.com", 5)
        );

        let dir = tempdir();
        let base = tmp_file(&dir, "base.txt", "");
        let ours = tmp_file(&dir, "ours.txt", &ours_content);
        let theirs = tmp_file(&dir, "theirs.txt", &theirs_content);
        let out = dir.join("out.txt");

        let code = cmd_merge_driver(
            &MergeMode::Collatz,
            base.to_str().unwrap(),
            ours.to_str().unwrap(),
            theirs.to_str().unwrap(),
            "regions/alpha/test.json",
            out.to_str().unwrap(),
        )
        .expect("should not error");

        // same set_k → hybrid merge → exit 0
        assert_eq!(code, 0, "M1.4 stamps with same set_k must produce hybrid merge");
        let merged = std::fs::read_to_string(&out).unwrap();
        assert!(merged.contains("\"foo\": 1"), "must contain ours data");
        assert!(merged.contains("\"foo\": 2"), "must contain theirs data");
    }

    // -----------------------------------------------------------------------
    // Helper: create a temporary directory that cleans up on drop
    // -----------------------------------------------------------------------

    fn tempdir() -> std::path::PathBuf {
        let path = std::env::temp_dir().join(format!(
            "emanon-test-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .subsec_nanos()
        ));
        std::fs::create_dir_all(&path).unwrap();
        path
    }

    // -----------------------------------------------------------------------
    // cmd_merge helpers — unit tests (no git required)
    // -----------------------------------------------------------------------

    #[test]
    fn conflict_entry_to_json_with_both_genera() {
        let entry = ConflictEntry {
            path: "regions/planet-xyz/settlement.json".to_string(),
            base_sha: "aaa111".to_string(),
            ours_sha: "bbb222".to_string(),
            theirs_sha: "ccc333".to_string(),
            ours_genus: Some(GenusStamp { set_k: 13, oddity_s: 5, index_i: 2 }),
            theirs_genus: Some(GenusStamp { set_k: 6, oddity_s: 2, index_i: 1 }),
            ours_leverage: 387,
            theirs_leverage: 112,
        };
        let json = conflict_entry_to_json(&entry);
        assert!(
            json.contains("\"path\": \"regions/planet-xyz/settlement.json\""),
            "must contain path; got: {json}"
        );
        assert!(json.contains("\"base_sha\": \"aaa111\""), "must contain base_sha; got: {json}");
        assert!(json.contains("\"ours_sha\": \"bbb222\""), "must contain ours_sha; got: {json}");
        assert!(json.contains("\"theirs_sha\": \"ccc333\""), "must contain theirs_sha; got: {json}");
        assert!(json.contains("\"set_k\": 13"), "must contain ours set_k; got: {json}");
        assert!(json.contains("\"set_k\": 6"), "must contain theirs set_k; got: {json}");
        assert!(json.contains("\"ours_leverage\": 387"), "must contain ours leverage; got: {json}");
        assert!(json.contains("\"theirs_leverage\": 112"), "must contain theirs leverage; got: {json}");
    }

    #[test]
    fn conflict_entry_to_json_null_genus_when_missing() {
        let entry = ConflictEntry {
            path: "regions/binary.bin".to_string(),
            base_sha: String::new(),
            ours_sha: "abc".to_string(),
            theirs_sha: "def".to_string(),
            ours_genus: None,
            theirs_genus: None,
            ours_leverage: 5,
            theirs_leverage: 3,
        };
        let json = conflict_entry_to_json(&entry);
        assert!(
            json.contains("\"ours_genus\": null"),
            "missing ours genus must serialize to null; got: {json}"
        );
        assert!(
            json.contains("\"theirs_genus\": null"),
            "missing theirs genus must serialize to null; got: {json}"
        );
    }

    #[test]
    fn conflict_entry_to_json_mixed_genus() {
        // One side has a stamp, the other doesn't.
        let entry = ConflictEntry {
            path: "regions/notes.txt".to_string(),
            base_sha: String::new(),
            ours_sha: "s1".to_string(),
            theirs_sha: "s2".to_string(),
            ours_genus: Some(GenusStamp { set_k: 44, oddity_s: 17, index_i: 0 }),
            theirs_genus: None,
            ours_leverage: 612,
            theirs_leverage: 0,
        };
        let json = conflict_entry_to_json(&entry);
        assert!(json.contains("\"set_k\": 44"), "must contain ours genus; got: {json}");
        assert!(
            json.contains("\"theirs_genus\": null"),
            "missing theirs genus must be null; got: {json}"
        );
        assert!(json.contains("\"ours_leverage\": 612"), "leverage mismatch; got: {json}");
    }

    #[test]
    fn read_genus_from_sha_empty_returns_none() {
        // Empty SHA → no blob to read → None
        assert!(read_genus_from_sha("").is_none());
    }

    #[test]
    fn read_genus_from_sha_invalid_sha_returns_none() {
        // Invalid SHA → git cat-file fails → None (not an error)
        assert!(read_genus_from_sha("0000000000000000000000000000000000000000").is_none());
    }

    #[test]
    fn compute_leverage_invalid_refspec_returns_zero() {
        // A refspec that doesn't exist returns 0, not an error.
        let leverage = compute_leverage("refs/nonexistent/branch/xyz/abc");
        assert_eq!(leverage, 0, "invalid refspec must return 0");
    }

    // -----------------------------------------------------------------------
    // cmd_merge integration test — requires git
    // -----------------------------------------------------------------------

    /// Shared mutex to prevent concurrent tests from corrupting each other's cwd.
    static CWD_MUTEX: std::sync::Mutex<()> = std::sync::Mutex::new(());

    /// Run a git command inside `dir` with test identity env vars.
    fn git_in(dir: &std::path::Path, args: &[&str]) -> bool {
        Command::new("git")
            .args(args)
            .current_dir(dir)
            .env("GIT_AUTHOR_NAME", "Tester")
            .env("GIT_AUTHOR_EMAIL", "tester@emanon.test")
            .env("GIT_COMMITTER_NAME", "Tester")
            .env("GIT_COMMITTER_EMAIL", "tester@emanon.test")
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status()
            .map(|s| s.success())
            .unwrap_or(false)
    }

    /// Initialise a minimal Emanon universe in `dir` and make an initial commit.
    fn init_universe(dir: &std::path::Path) {
        std::fs::create_dir_all(dir.join(".gitverse")).unwrap();
        std::fs::create_dir_all(dir.join("regions")).unwrap();
        std::fs::write(dir.join(".gitverse/snapshot_count"), "1").unwrap();
        std::fs::write(dir.join(".gitattributes"), "regions/** merge=emanon-collatz\n").unwrap();
        std::fs::write(dir.join("README.md"), "universe\n").unwrap();
        assert!(git_in(dir, &["init", "-b", "main"]), "git init failed");
        assert!(git_in(dir, &["add", "."]), "git add failed");
        assert!(git_in(dir, &["commit", "-m", "init"]), "git commit failed");
    }

    #[test]
    fn cmd_merge_writes_pending_json_on_conflict() {
        let _lock = CWD_MUTEX.lock().unwrap_or_else(|p| p.into_inner());

        let base = tempdir();
        let local_dir = base.join("local");
        let remote_dir = base.join("remote");
        std::fs::create_dir_all(&local_dir).unwrap();
        std::fs::create_dir_all(&remote_dir).unwrap();

        // ── Step 1: Remote: init (no regions/shared.txt yet) + commit ──────────
        init_universe(&remote_dir);

        // ── Step 2: Clone into local (both sides share the same initial commit) ─
        assert!(
            git_in(&base, &["clone", remote_dir.to_str().unwrap(), "local"]),
            "git clone failed"
        );

        // ── Step 3: Local independently adds regions/shared.txt with set_k=3 ───
        // set_k=3, oddity_s=1 — these must differ from remote's genus below
        // so that the merge driver's Rule 3 (unrelated sets) fires → conflict.
        std::fs::write(
            local_dir.join("regions/shared.txt"),
            "local content\n# emanon:genus set_k=3 oddity_s=1 index_i=0\n",
        )
        .unwrap();
        assert!(git_in(&local_dir, &["add", "regions/shared.txt"]), "git add (local) failed");
        assert!(git_in(&local_dir, &["commit", "-m", "local: add shared"]), "git commit (local) failed");

        // ── Step 4: Remote independently adds the SAME file with set_k=7 ───────
        // Different set_k AND different oddity_s → merge driver exits 1 → conflict.
        std::fs::write(
            remote_dir.join("regions/shared.txt"),
            "remote content\n# emanon:genus set_k=7 oddity_s=4 index_i=0\n",
        )
        .unwrap();
        assert!(git_in(&remote_dir, &["add", "regions/shared.txt"]), "git add (remote) failed");
        assert!(git_in(&remote_dir, &["commit", "-m", "remote: add shared"]), "git commit (remote) failed");

        // ── Step 5: Run cmd_merge("origin/main") from inside local ──────────────
        // After git fetch, the merge sees:
        //   base  = (empty blob — file didn't exist at clone point)
        //   ours  = set_k=3  (local commit)
        //   theirs= set_k=7  (remote commit)
        // Merge driver: unrelated sets → exit 1 → conflict.
        let orig_dir = std::env::current_dir().ok();
        std::env::set_current_dir(&local_dir).expect("set_current_dir failed");

        let result = cmd_merge("origin/main");

        // Restore original cwd before any assertions.
        if let Some(orig) = orig_dir {
            let _ = std::env::set_current_dir(orig);
        }

        // Abort the merge state so subsequent tests are clean.
        let _ = git_in(&local_dir, &["merge", "--abort"]);

        match result {
            Ok(()) => {
                // Conflicts were deferred → pending-merge.json must exist.
                let pending = local_dir.join(".gitverse/pending-merge.json");
                assert!(
                    pending.exists(),
                    "pending-merge.json must be written when merge driver exits 1"
                );
                let json_str = std::fs::read_to_string(&pending).unwrap();
                let trimmed = json_str.trim();
                assert!(trimmed.starts_with('{'), "pending-merge.json must be a JSON object");
                assert!(trimmed.ends_with('}'), "pending-merge.json must be a complete JSON object");
                assert!(
                    json_str.contains("\"remote_branch\": \"origin/main\""),
                    "must record remote_branch; got: {json_str}"
                );
                assert!(
                    json_str.contains("\"conflicts\""),
                    "must contain conflicts array; got: {json_str}"
                );
                assert!(
                    json_str.contains("regions/shared.txt"),
                    "must list the conflicted file; got: {json_str}"
                );
            }
            Err(e) => {
                panic!("cmd_merge returned an unexpected error: {e}");
            }
        }
    }

    #[test]
    fn cmd_merge_clean_merge_no_pending_json() {
        let _lock = CWD_MUTEX.lock().unwrap_or_else(|p| p.into_inner());

        let base = tempdir();
        let local_dir = base.join("local");
        let remote_dir = base.join("remote");
        std::fs::create_dir_all(&local_dir).unwrap();
        std::fs::create_dir_all(&remote_dir).unwrap();

        // Set up the "remote" universe.
        init_universe(&remote_dir);

        // Clone locally; local is now identical to remote — no divergence.
        assert!(
            git_in(&base, &["clone", remote_dir.to_str().unwrap(), "local"]),
            "git clone failed"
        );

        // Remote adds a new file (non-conflicting with anything local has).
        let new_file = remote_dir.join("regions/new.txt");
        std::fs::write(&new_file, "brand new content\n").unwrap();
        assert!(git_in(&remote_dir, &["add", "regions/new.txt"]), "git add failed");
        assert!(git_in(&remote_dir, &["commit", "-m", "add new"]), "git commit failed");

        // Local has no changes — a merge of origin/main should be clean.
        let orig_dir = std::env::current_dir().ok();
        std::env::set_current_dir(&local_dir).expect("set_current_dir failed");

        let result = cmd_merge("origin/main");

        if let Some(orig) = orig_dir {
            let _ = std::env::set_current_dir(orig);
        }

        match result {
            Ok(()) => {
                // Clean merge — pending-merge.json should NOT exist (or be absent).
                let pending = local_dir.join(".gitverse/pending-merge.json");
                assert!(
                    !pending.exists(),
                    "clean merge must not write pending-merge.json"
                );
            }
            Err(e) => {
                panic!("cmd_merge failed on a clean merge: {e}");
            }
        }
    }

    // -----------------------------------------------------------------------
    // parse_conflict_obj / load_pending_conflicts parsing
    // -----------------------------------------------------------------------

    #[test]
    fn parse_conflict_obj_with_both_genera() {
        let obj = r#"{
      "path": "regions/foo.json",
      "base_sha": "abc",
      "ours_sha": "def",
      "theirs_sha": "ghi",
      "ours_genus": {"set_k": 13, "oddity_s": 5, "index_i": 2},
      "theirs_genus": {"set_k": 6, "oddity_s": 2, "index_i": 1},
      "ours_leverage": 387,
      "theirs_leverage": 112
    }"#;
        let c = parse_conflict_obj(obj).expect("should parse");
        assert_eq!(c.path, "regions/foo.json");
        assert_eq!(c.ours_leverage, 387);
        assert_eq!(c.theirs_leverage, 112);
        assert!(c.ours_genus_str.contains("Set_13"), "ours genus; got: {}", c.ours_genus_str);
        assert!(c.theirs_genus_str.contains("Set_6"), "theirs genus; got: {}", c.theirs_genus_str);
    }

    #[test]
    fn parse_conflict_obj_with_null_genus() {
        let obj = r#"{
      "path": "regions/bar.json",
      "base_sha": "",
      "ours_sha": "x1",
      "theirs_sha": "x2",
      "ours_genus": null,
      "theirs_genus": null,
      "ours_leverage": 10,
      "theirs_leverage": 5
    }"#;
        let c = parse_conflict_obj(obj).expect("should parse");
        assert_eq!(c.path, "regions/bar.json");
        assert_eq!(c.ours_genus_str, "no stamp");
        assert_eq!(c.theirs_genus_str, "no stamp");
    }

    // -----------------------------------------------------------------------
    // parse_resolution_plan (non-interactive input)
    // -----------------------------------------------------------------------

    #[test]
    fn parse_resolution_plan_battle() {
        let input = r#"[{"path":"regions/a.json","resolution":"battle","force_size":1024}]"#;
        let plan = parse_resolution_plan(input).expect("should parse");
        assert_eq!(plan.len(), 1);
        assert_eq!(plan[0].0, "regions/a.json");
        match &plan[0].1 {
            Resolution::Battle { force_size } => assert_eq!(*force_size, 1024),
            other => panic!("expected Battle, got {other:?}"),
        }
    }

    #[test]
    fn parse_resolution_plan_contract() {
        let input = r#"[{"path":"regions/b.json","resolution":"contract","terms":"50/50 resources"}]"#;
        let plan = parse_resolution_plan(input).expect("should parse");
        assert_eq!(plan.len(), 1);
        match &plan[0].1 {
            Resolution::Contract { terms } => assert_eq!(terms, "50/50 resources"),
            other => panic!("expected Contract, got {other:?}"),
        }
    }

    #[test]
    fn parse_resolution_plan_fork_and_manual() {
        let input = r#"[
          {"path":"regions/c.json","resolution":"fork"},
          {"path":"regions/d.json","resolution":"manual"}
        ]"#;
        let plan = parse_resolution_plan(input).expect("should parse");
        assert_eq!(plan.len(), 2);
        assert!(matches!(plan[0].1, Resolution::Fork));
        assert!(matches!(plan[1].1, Resolution::Manual));
    }

    #[test]
    fn parse_resolution_plan_unknown_resolution_errors() {
        let input = r#"[{"path":"regions/e.json","resolution":"surrender"}]"#;
        let err = parse_resolution_plan(input);
        assert!(err.is_err(), "unknown resolution must be an error");
    }

    #[test]
    fn parse_resolution_plan_default_force_size() {
        // Omitting force_size in a battle entry defaults to 256.
        let input = r#"[{"path":"regions/f.json","resolution":"battle"}]"#;
        let plan = parse_resolution_plan(input).expect("should parse");
        match &plan[0].1 {
            Resolution::Battle { force_size } => assert_eq!(*force_size, 256, "default force_size must be 256"),
            other => panic!("expected Battle, got {other:?}"),
        }
    }

    // -----------------------------------------------------------------------
    // load_pending_conflicts — round-trip through pending-merge.json
    // -----------------------------------------------------------------------

    #[test]
    fn load_pending_conflicts_round_trip() {
        // Build a minimal pending-merge.json using conflict_entry_to_json.
        let entry = ConflictEntry {
            path: "regions/test.json".to_string(),
            base_sha: "base000".to_string(),
            ours_sha: "ours111".to_string(),
            theirs_sha: "theirs222".to_string(),
            ours_genus: Some(GenusStamp { set_k: 13, oddity_s: 5, index_i: 0 }),
            theirs_genus: None,
            ours_leverage: 42,
            theirs_leverage: 7,
        };
        let entries_json = conflict_entry_to_json(&entry);
        let pending_json = format!(
            "{{\n  \"remote_branch\": \"origin/main\",\n  \"conflicts\": [\n{entries_json}\n  ]\n}}"
        );

        let dir = tempdir();
        let gitverse = dir.join(".gitverse");
        std::fs::create_dir_all(&gitverse).unwrap();
        std::fs::write(gitverse.join("pending-merge.json"), &pending_json).unwrap();

        let conflicts = load_pending_conflicts(&gitverse).expect("should load");
        assert_eq!(conflicts.len(), 1);
        assert_eq!(conflicts[0].path, "regions/test.json");
        assert_eq!(conflicts[0].ours_leverage, 42);
        assert_eq!(conflicts[0].theirs_leverage, 7);
        assert!(conflicts[0].ours_genus_str.contains("Set_13"), "ours genus; got: {}", conflicts[0].ours_genus_str);
        assert_eq!(conflicts[0].theirs_genus_str, "no stamp");
    }

    #[test]
    fn load_pending_conflicts_missing_file_errors() {
        let dir = tempdir();
        let gitverse = dir.join(".gitverse");
        std::fs::create_dir_all(&gitverse).unwrap();
        // Don't write pending-merge.json
        let err = load_pending_conflicts(&gitverse);
        assert!(err.is_err(), "missing file must be an error");
    }

    // -----------------------------------------------------------------------
    // validate helpers
    // -----------------------------------------------------------------------

    /// Build a minimal valid universe tree under `root` and return the path.
    fn make_valid_universe(root: &std::path::Path) {
        let gitverse = root.join(".gitverse");
        std::fs::create_dir_all(&gitverse).unwrap();
        for d in &["regions", "contracts", "scars", "forks"] {
            std::fs::create_dir_all(root.join(d)).unwrap();
        }
        std::fs::write(
            gitverse.join("values.json"),
            r#"{
  "conflict_preference": "contract",
  "fork_readiness": "medium",
  "battle_threshold": 0.5,
  "host_authority_mode": "partition"
}
"#,
        )
        .unwrap();
        std::fs::write(
            root.join(".gitattributes"),
            "regions/**       merge=emanon-collatz\ncontracts/**     merge=emanon-contract\nscars/**         merge=emanon-append-only\n",
        )
        .unwrap();
    }

    #[test]
    fn validate_passes_on_valid_universe() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Run cmd_validate from within the temp dir.
        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_ok(), "valid universe must pass: {:?}", result);
    }

    #[test]
    fn validate_fails_missing_required_dir() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Remove a required directory.
        std::fs::remove_dir_all(dir.join("forks")).unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_err(), "missing dir must fail");
        let msg = result.unwrap_err().to_string();
        assert!(msg.contains("validation error"), "error must mention validation: {msg}");
    }

    #[test]
    fn validate_fails_missing_values_json() {
        let dir = tempdir();
        make_valid_universe(&dir);
        std::fs::remove_file(dir.join(".gitverse/values.json")).unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_err(), "missing values.json must fail");
    }

    #[test]
    fn validate_fails_malformed_values_json() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Missing required keys.
        std::fs::write(
            dir.join(".gitverse/values.json"),
            r#"{"only_one_key": "yes"}"#,
        )
        .unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_err(), "malformed values.json must fail");
    }

    #[test]
    fn validate_fails_missing_gitattributes_driver() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Remove the scars merge driver line.
        std::fs::write(
            dir.join(".gitattributes"),
            "regions/**       merge=emanon-collatz\ncontracts/**     merge=emanon-contract\n",
        )
        .unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_err(), "missing merge driver must fail");
        let msg = result.unwrap_err().to_string();
        assert!(msg.contains("validation error"), "must be validation error: {msg}");
    }

    #[test]
    fn validate_warns_but_passes_on_unstamped_region_file() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Write a file in regions/ with no genus stamp.
        std::fs::write(
            dir.join("regions/unstamped.txt"),
            "hello world\n",
        )
        .unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        // Should pass (warnings, not errors).
        assert!(
            result.is_ok(),
            "unstamped region file = warning, not error: {:?}",
            result
        );
    }

    #[test]
    fn validate_strict_mode_fails_on_unstamped_region_file() {
        let dir = tempdir();
        make_valid_universe(&dir);
        std::fs::write(
            dir.join("regions/unstamped.txt"),
            "hello world\n",
        )
        .unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(true); // --strict
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_err(), "strict mode must fail on unstamped file");
    }

    #[test]
    fn validate_passes_on_stamped_region_file() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // Write a file in regions/ with a valid genus stamp.
        std::fs::write(
            dir.join("regions/stamped.txt"),
            "hello world\n# emanon-genus: {\"set_k\": 3, \"oddity_s\": 1, \"index_i\": 0, \"writer\": \"test\", \"snapshot\": 1}\n",
        )
        .unwrap();

        let original_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();
        let result = cmd_validate(false);
        std::env::set_current_dir(original_dir).unwrap();
        assert!(result.is_ok(), "stamped file should pass cleanly: {:?}", result);
    }

    #[test]
    fn validate_genus_stamp_check_skips_gitkeep() {
        let dir = tempdir();
        make_valid_universe(&dir);
        // .gitkeep has no stamp and must not produce a warning.
        std::fs::write(dir.join("regions/.gitkeep"), "").unwrap();

        let mut warnings: Vec<String> = Vec::new();
        check_genus_stamps_in_dir(&dir.join("regions"), &dir, &mut warnings);
        assert!(
            warnings.is_empty(),
            ".gitkeep must not produce a warning: {:?}",
            warnings
        );
    }

    // -----------------------------------------------------------------------
    // Registry helpers
    // -----------------------------------------------------------------------

    #[test]
    fn name_is_valid_registry_entry_accepts_valid_names() {
        assert!(name_is_valid_registry_entry("alice-prime"));
        assert!(name_is_valid_registry_entry("my-universe-01"));
        assert!(name_is_valid_registry_entry("abc")); // minimum 3 chars
        assert!(name_is_valid_registry_entry("a1b")); // alphanumeric boundaries
        assert!(name_is_valid_registry_entry("test_universe_2"));
    }

    #[test]
    fn name_is_valid_registry_entry_rejects_invalid() {
        assert!(!name_is_valid_registry_entry("ab"));       // too short (2 chars)
        assert!(!name_is_valid_registry_entry("-abc"));     // starts with dash
        assert!(!name_is_valid_registry_entry("abc-"));     // ends with dash
        assert!(!name_is_valid_registry_entry("Hello"));    // uppercase
        assert!(!name_is_valid_registry_entry("my universe")); // space
        assert!(!name_is_valid_registry_entry(&"a".repeat(65))); // too long
    }

    #[test]
    fn normalise_git_url_passthrough_https() {
        let url = "https://github.com/alice/her-world";
        assert_eq!(normalise_git_url(url), url);
    }

    #[test]
    fn normalise_git_url_strips_dot_git() {
        assert_eq!(
            normalise_git_url("https://github.com/alice/her-world.git"),
            "https://github.com/alice/her-world"
        );
    }

    #[test]
    fn normalise_git_url_converts_ssh_to_https() {
        assert_eq!(
            normalise_git_url("git@github.com:alice/her-world.git"),
            "https://github.com/alice/her-world"
        );
    }

    #[test]
    fn normalise_git_url_converts_ssh_no_git_suffix() {
        assert_eq!(
            normalise_git_url("git@github.com:alice/her-world"),
            "https://github.com/alice/her-world"
        );
    }

    #[test]
    fn parse_toml_kv_double_quoted_value() {
        let (k, v) = parse_toml_kv(r#"url = "https://github.com/foo/bar""#).unwrap();
        assert_eq!(k, "url");
        assert_eq!(v, "https://github.com/foo/bar");
    }

    #[test]
    fn parse_toml_kv_unquoted_value() {
        let (k, v) = parse_toml_kv("snapshot_count = 42").unwrap();
        assert_eq!(k, "snapshot_count");
        assert_eq!(v, "42");
    }

    #[test]
    fn parse_toml_kv_returns_none_on_no_eq() {
        assert!(parse_toml_kv("[registry]").is_none());
        assert!(parse_toml_kv("# comment").is_none());
    }

    #[test]
    fn load_amenon_config_uses_override_url() {
        let cfg = load_amenon_config_for_url(Some("https://example.com/my-registry"));
        assert_eq!(cfg.registry_url, "https://example.com/my-registry");
    }

    #[test]
    fn load_emanon_config_defaults() {
        // Without a config file, defaults are sane.
        let cfg = load_emanon_config();
        assert_eq!(cfg.registry_url, DEFAULT_REGISTRY_URL);
        assert_eq!(cfg.git_remote, "origin");
        // owner_pubkey is optional; may or may not be set on this machine.
    }

    #[test]
    fn parse_entry_json_valid_entry() {
        let dir = tempdir();
        let tmp_path = dir.join("alice-prime.json");
        std::fs::write(
            &tmp_path,
            r#"{
  "name": "alice-prime",
  "owner_pubkey": "AxL7YMzPqR5KoN2XvUhT1nJsLcW8FmBeDpVqRxGsP3k",
  "git_url": "https://github.com/alice/her-world",
  "head_commit": "abc1234def5678901234567890123456789012345678",
  "snapshot_count": 42,
  "values_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "scrambled_root_hash": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "created_at": "2026-04-14T00:00:00Z",
  "updated_at": "2026-04-14T00:00:00Z",
  "tags": ["solo", "early"],
  "cnft_mint": null
}"#,
        ).unwrap();
        let fields = parse_entry_json(&tmp_path);
        assert_eq!(fields.get("name").map(String::as_str), Some("alice-prime"));
        assert_eq!(
            fields.get("git_url").map(String::as_str),
            Some("https://github.com/alice/her-world")
        );
        assert_eq!(
            fields.get("snapshot_count").and_then(|s| s.parse::<u64>().ok()),
            Some(42)
        );
        // Tags array is joined.
        let tags = fields.get("tags").cloned().unwrap_or_default();
        assert!(tags.contains("solo"), "tags should contain 'solo': {tags}");
    }

    #[test]
    fn registry_cache_dir_produces_valid_path() {
        let dir = registry_cache_dir(DEFAULT_REGISTRY_URL).unwrap();
        let s = dir.to_string_lossy();
        assert!(s.contains(".local/share/emanon/registry/"));
        // Should not end with a separator.
        assert!(!s.ends_with('/'));
    }

    #[test]
    fn registry_cache_dir_distinct_for_different_urls() {
        let d1 = registry_cache_dir("https://github.com/foo/bar").unwrap();
        let d2 = registry_cache_dir("https://github.com/baz/qux").unwrap();
        assert_ne!(d1, d2);
    }
}
