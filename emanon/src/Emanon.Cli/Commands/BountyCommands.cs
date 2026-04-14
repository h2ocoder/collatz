using System.ComponentModel;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

// ---------------------------------------------------------------------------
// Bounty commands — server-backed bounty board (no blockchain)
// ---------------------------------------------------------------------------

public class BountyPostCommand : Command<BountyPostCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--constraint <FILE>")]
        [Description("JSON file describing the bounty predicate/constraint")]
        public string? ConstraintFile { get; init; }

        [CommandOption("--max-price <AMOUNT>")]
        [Description("Maximum price willing to pay")]
        public double MaxPrice { get; init; }

        [CommandOption("--server <URL>")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Posting bounty to {server}…[/]");
        // TODO: POST {server}/api/bounties
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class BountyListCommand : Command<BountyListCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--min-price <AMOUNT>")] public double? MinPrice { get; init; }
        [CommandOption("--expires-before <DATE>")] public string? ExpiresBefore { get; init; }
        [CommandOption("--json")] public bool Json { get; init; }
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Listing bounties from {server}…[/]");
        // TODO: GET {server}/api/bounties
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class BountyShowCommand : Command<BountyShowCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<id>")] public string Id { get; init; } = "";
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Fetching bounty {settings.Id} from {server}…[/]");
        // TODO: GET {server}/api/bounties/{id}
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class BountyAcceptCommand : Command<BountyAcceptCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<id>")] public string Id { get; init; } = "";
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Accepting bounty {settings.Id} on {server}…[/]");
        // TODO: POST {server}/api/bounties/{id}/accept
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class BountyDeliverCommand : Command<BountyDeliverCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<id>")] public string Id { get; init; } = "";
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Delivering bounty {settings.Id} to {server}…[/]");
        // TODO: POST {server}/api/bounties/{id}/deliver
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}
