using System.ComponentModel;
using System.Text.Json;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

// ---------------------------------------------------------------------------
// Registry commands — talk to the central Emanon server API
// ---------------------------------------------------------------------------

public class RegistryPushCommand : Command<RegistryPushCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--server <URL>")]
        [Description("Registry server URL (default: $EMANON_SERVER or https://api.emanon.gg)")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null) { AnsiConsole.MarkupLine("[red]Error:[/] Not in a universe."); return 1; }

        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        var values = GitverseLayout.ReadValues(repoRoot);
        var name   = values?["universe_name"].GetString() ?? Path.GetFileName(repoRoot);
        var head   = GitService.HeadShort(repoRoot);

        AnsiConsole.MarkupLine($"[dim]Pushing universe [cyan]{name}[/] (HEAD: {head}) to {server}…[/]");
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending — universe entry prepared locally.");

        // TODO: POST to {server}/api/universes with JSON payload
        var entry = new { name, head, pushed_at = DateTime.UtcNow.ToString("O") };
        AnsiConsole.MarkupLine($"[green]✓[/] Entry: {JsonSerializer.Serialize(entry)}");
        return 0;
    }
}

public class RegistryPullCommand : Command<RegistryPullCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<slug>")]
        [Description("Universe slug to pull")]
        public string Slug { get; init; } = "";

        [CommandOption("--server <URL>")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Pulling [cyan]{settings.Slug}[/] from {server}…[/]");
        // TODO: GET {server}/api/universes/{slug}
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class RegistryListCommand : Command<RegistryListCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--server <URL>")]
        public string? Server { get; init; }
        [CommandOption("--json")]
        [Description("Output raw JSON")]
        public bool Json { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var server = settings.Server ?? Environment.GetEnvironmentVariable("EMANON_SERVER") ?? "https://api.emanon.gg";
        AnsiConsole.MarkupLine($"[dim]Listing universes from {server}…[/]");
        // TODO: GET {server}/api/universes
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}

public class RegistryAddRemoteCommand : Command<RegistryAddRemoteCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<slug>")]
        public string Slug { get; init; } = "";
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        AnsiConsole.MarkupLine($"[dim]Fetching git URL for [cyan]{settings.Slug}[/] from registry…[/]");
        // TODO: Fetch from server, then: git remote add <slug> <url>
        AnsiConsole.MarkupLine("[yellow]Note:[/] Server integration pending.");
        return 0;
    }
}
