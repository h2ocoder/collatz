use clap::{Parser, Subcommand};
use collatz_rs::beta;
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
    /// Publish this universe to the registry
    Push,
    /// Pull a universe from the registry
    Pull,
    /// List universes in the registry
    List,
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
            RegistryAction::Push => not_yet("emanon registry push"),
            RegistryAction::Pull => not_yet("emanon registry pull"),
            RegistryAction::List => not_yet("emanon registry list"),
        },
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
}
