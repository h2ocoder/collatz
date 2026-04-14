use clap::{Parser, Subcommand};

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
    /// Initialize a new Emanon universe (git repo)
    Init {
        /// Name for the new universe
        name: String,
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

fn not_yet(feature: &str) {
    eprintln!("⏳  `{feature}` is not yet implemented.");
    eprintln!("    This subcommand is stubbed in milestone M0.");
    eprintln!("    Implementation arrives in a later milestone — stay tuned.");
    std::process::exit(1);
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Init { name } => {
            not_yet(&format!("emanon init {name}"));
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
