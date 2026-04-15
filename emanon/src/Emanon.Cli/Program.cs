using Emanon.Cli.Commands;
using Spectre.Console.Cli;

var app = new CommandApp();

app.Configure(config =>
{
    config.SetApplicationName("emanon");
    config.SetApplicationVersion("0.1.0");

    config.AddCommand<InitCommand>("init")
          .WithDescription("Initialise a new Emanon universe (git repo + .gitverse layout).");

    config.AddCommand<SnapshotCommand>("snapshot")
          .WithDescription("Take a snapshot (git add -A + commit with metadata).");

    config.AddCommand<WriteCommand>("write")
          .WithDescription("Write content to a file and stamp it with a Collatz genus.");

    config.AddCommand<GenusCommand>("genus")
          .WithDescription("Show the Collatz genus stamp for a file.");

    config.AddCommand<MergeCommand>("merge")
          .WithDescription("Merge a remote branch, invoking the Collatz merge driver on conflicts.");

    config.AddCommand<MergeDriverCommand>("merge-driver")
          .WithDescription("Internal: custom git merge driver. Invoked by git, not directly.");

    config.AddCommand<NegotiateCommand>("negotiate")
          .WithDescription("Open the negotiation UI for pending merge conflicts.");

    config.AddCommand<ValidateCommand>("validate")
          .WithDescription("Validate the universe structure and schema.");

    config.AddBranch("registry", registry =>
    {
        registry.SetDescription("Manage the multiverse registry.");
        registry.AddCommand<RegistryPushCommand>("push").WithDescription("Publish this universe to the registry.");
        registry.AddCommand<RegistryPullCommand>("pull").WithDescription("Fetch a universe from the registry.");
        registry.AddCommand<RegistryListCommand>("list").WithDescription("List universes in the registry.");
        registry.AddCommand<RegistryAddRemoteCommand>("add-remote").WithDescription("Add a universe as a git remote.");
    });

    config.AddBranch("bounty", bounty =>
    {
        bounty.SetDescription("Manage bounties (server-side).");
        bounty.AddCommand<BountyPostCommand>("post").WithDescription("Post a new bounty.");
        bounty.AddCommand<BountyListCommand>("list").WithDescription("List open bounties.");
        bounty.AddCommand<BountyShowCommand>("show").WithDescription("Show a bounty by ID.");
        bounty.AddCommand<BountyAcceptCommand>("accept").WithDescription("Accept a bounty.");
        bounty.AddCommand<BountyDeliverCommand>("deliver").WithDescription("Deliver a completed bounty.");
    });
});

return app.Run(args);
