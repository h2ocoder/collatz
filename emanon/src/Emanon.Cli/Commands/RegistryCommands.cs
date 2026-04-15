using System.ComponentModel;
using System.Security.Cryptography;
using System.Text;
using Emanon.Cli.Services;
using Emanon.Collatz;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

// ---------------------------------------------------------------------------
// Registry commands — talk to the Emanon central authority API.
// ---------------------------------------------------------------------------

/// <summary>
/// Publish this universe to the registry. Registers on first call, updates on subsequent calls.
/// </summary>
public class RegistryPushCommand : Command<RegistryPushCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--server <URL>")]
        [Description("Registry server URL (overrides $EMANON_SERVER and .gitverse/values.json)")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = RegistryHelpers.RequireRepoRoot();
        if (repoRoot is null) return 1;

        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured. " +
                "Pass [cyan]--server URL[/], set [cyan]$EMANON_SERVER[/], or run a previous push.");
            return 1;
        }

        var values = GitverseLayout.ReadValues(repoRoot) ?? GitverseLayout.DefaultValues();
        var ownerEmail = GitService.UserEmail(repoRoot);
        using var api = new ApiClient(serverUrl);

        // Register if we don't have an id yet.
        if (string.IsNullOrWhiteSpace(values.RegistryId))
        {
            var gitUrl = RegistryHelpers.TryGetOriginUrl(repoRoot);
            AnsiConsole.MarkupLine($"[dim]Registering universe [cyan]{values.UniverseName}[/] with {serverUrl}…[/]");
            try
            {
                var registered = api.Register(new RegisterUniverseRequestDto(
                    Name:        values.UniverseName,
                    OwnerEmail:  ownerEmail,
                    GitUrl:      gitUrl,
                    Description: ""));

                values = GitverseLayout.UpdateValues(repoRoot, v => v with
                {
                    RegistryId     = registered.Id,
                    RegistryServer = serverUrl,
                });
                AnsiConsole.MarkupLine($"[green]✓[/] Registered with id [cyan]{registered.Id}[/]");
            }
            catch (ApiException ex) when (ex.StatusCode == 409)
            {
                AnsiConsole.MarkupLine("[red]Error:[/] A universe with this name is already registered " +
                    "by another owner. Rename yours in values.json and retry.");
                return 2;
            }
            catch (ApiException ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] Register failed: {ex.Message.EscapeMarkup()}");
                return 2;
            }
        }

        // Push head state.
        var headSha    = GitService.HeadShort(repoRoot);
        var headGenus  = RegistryHelpers.ComputeHeadGenus(headSha, values.SnapshotCount);
        try
        {
            var updated = api.Push(values.RegistryId!, new PushUniverseRequestDto(
                UniverseId:    values.RegistryId!,
                SnapshotCount: values.SnapshotCount,
                HeadGenus:     headGenus.ToString(),
                OwnerEmail:    ownerEmail));

            AnsiConsole.MarkupLine(
                $"[green]✓[/] Pushed [cyan]{updated.Name}[/] " +
                $"[dim](snapshots={updated.SnapshotCount}, head={updated.HeadGenus})[/]");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Push failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
    }
}

/// <summary>Pull a universe's current registry state by slug (name).</summary>
public class RegistryPullCommand : Command<RegistryPullCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<slug>")]
        [Description("Universe name to pull")]
        public string Slug { get; init; } = "";

        [CommandOption("--server <URL>")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot  = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        using var api = new ApiClient(serverUrl);
        try
        {
            var match = api.ListUniverses().FirstOrDefault(u =>
                string.Equals(u.Name, settings.Slug, StringComparison.OrdinalIgnoreCase));
            if (match is null)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] Universe [cyan]{settings.Slug}[/] not found.");
                return 2;
            }

            var state = api.Pull(match.Id);
            AnsiConsole.MarkupLine($"[bold]{state.Name}[/] [dim]({state.Id})[/]");
            AnsiConsole.MarkupLine($"  snapshots: {state.SnapshotCount}");
            AnsiConsole.MarkupLine($"  head:      {state.HeadGenus ?? "[dim](none)[/]"}");
            AnsiConsole.MarkupLine($"  updated:   {state.UpdatedAt}");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Pull failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
    }
}

/// <summary>List all universes in the registry.</summary>
public class RegistryListCommand : Command<RegistryListCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--server <URL>")] public string? Server { get; init; }
        [CommandOption("--json")]         public bool    Json   { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot  = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        using var api = new ApiClient(serverUrl);
        IReadOnlyList<UniverseDto> universes;
        try { universes = api.ListUniverses(); }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] List failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }

        if (settings.Json)
        {
            AnsiConsole.WriteLine(System.Text.Json.JsonSerializer.Serialize(universes));
            return 0;
        }

        var table = new Table()
            .AddColumn("Name").AddColumn("Id").AddColumn("Snapshots").AddColumn("Head");
        foreach (var u in universes)
            table.AddRow(u.Name, u.Id, u.SnapshotCount.ToString(), u.HeadGenus ?? "-");
        AnsiConsole.Write(table);
        return 0;
    }
}

/// <summary>Add a remote universe's git URL as a local git remote.</summary>
public class RegistryAddRemoteCommand : Command<RegistryAddRemoteCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<slug>")] public string Slug { get; init; } = "";
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = RegistryHelpers.RequireRepoRoot();
        if (repoRoot is null) return 1;

        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        using var api = new ApiClient(serverUrl);
        UniverseDto? match;
        try
        {
            match = api.ListUniverses().FirstOrDefault(u =>
                string.Equals(u.Name, settings.Slug, StringComparison.OrdinalIgnoreCase));
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message.EscapeMarkup()}");
            return 2;
        }

        if (match is null)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Universe [cyan]{settings.Slug}[/] not found.");
            return 2;
        }
        if (string.IsNullOrWhiteSpace(match.GitUrl))
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Universe [cyan]{match.Name}[/] has no git URL.");
            return 2;
        }

        GitService.Run($"remote add {settings.Slug} {match.GitUrl}", repoRoot);
        AnsiConsole.MarkupLine($"[green]✓[/] Added remote [cyan]{settings.Slug}[/] → {match.GitUrl}");
        return 0;
    }
}

// ---------------------------------------------------------------------------

internal static class RegistryHelpers
{
    public static string? RequireRepoRoot()
    {
        var root = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (root is null)
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe.");
        return root;
    }

    public static string TryGetOriginUrl(string repoRoot)
    {
        var (stdout, _, exit) = GitService.TryRun("remote get-url origin", repoRoot);
        return exit == 0 ? stdout.Trim() : "";
    }

    /// <summary>Deterministically derive a head-genus from the HEAD sha + snapshot count.</summary>
    public static Genus ComputeHeadGenus(string headSha, int snapshotCount)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(headSha));
        ulong seed = BitConverter.ToUInt64(bytes, 0) ^ (ulong)snapshotCount;
        return CollatzMath.DroppingGenusFromSeed(seed);
    }
}
