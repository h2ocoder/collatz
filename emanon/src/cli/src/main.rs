use clap::{Parser, Subcommand};
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
    },

    /// Merge a remote timeline using the Collatz merge driver
    Merge {
        /// Remote and branch in the form <remote>/<branch>
        remote_branch: String,
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
# Register the Collatz merge driver for Emanon universes
# To activate, add to .git/config:
#   [merge \"collatz\"]
#       name = Collatz conflict resolver
#       driver = emanon-merge %O %A %B
*.contract  merge=collatz
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
        - `.gitverse/values.json` — resolution preferences for this universe\n\
        - `.gitattributes`         — Collatz merge driver registration (placeholder)\n\
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
    std::fs::write(target.join(".gitverse/values.json"), VALUES_JSON)?;
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

    // --- git add . ---
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
        Commands::Snapshot { message } => {
            let flag = message
                .map(|m| format!(" -m \"{m}\""))
                .unwrap_or_default();
            not_yet(&format!("emanon snapshot{flag}"));
        }
        Commands::Merge { remote_branch } => {
            not_yet(&format!("emanon merge {remote_branch}"));
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
