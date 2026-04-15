using System.ComponentModel;
using System.Text.Json;
using System.Text.Json.Serialization;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

// ---------------------------------------------------------------------------
// Bounty commands — server-backed bounty board (no blockchain).
// ---------------------------------------------------------------------------

/// <summary>JSON constraint file consumed by <c>bounty post</c>.</summary>
public sealed record BountyConstraintFile(
    [property: JsonPropertyName("title")]       string  Title,
    [property: JsonPropertyName("description")] string  Description,
    [property: JsonPropertyName("predicate")]   string  Predicate,
    [property: JsonPropertyName("reward_usdc")] decimal RewardUsdc);

public class BountyPostCommand : Command<BountyPostCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--constraint <FILE>")]
        [Description("JSON file describing the bounty (title, description, predicate, reward_usdc)")]
        public string? ConstraintFile { get; init; }

        [CommandOption("--server <URL>")]
        public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = BountyHelpers.RequireRepoRoot();
        if (repoRoot is null) return 1;

        var values = GitverseLayout.ReadValues(repoRoot);
        if (values?.RegistryId is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Universe is not registered. Run [cyan]emanon registry push[/] first.");
            return 1;
        }

        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        if (string.IsNullOrWhiteSpace(settings.ConstraintFile))
        {
            AnsiConsole.MarkupLine("[red]Error:[/] [cyan]--constraint FILE[/] is required.");
            return 1;
        }

        BountyConstraintFile constraint;
        try
        {
            var json = File.ReadAllText(settings.ConstraintFile);
            var parsed = JsonSerializer.Deserialize<BountyConstraintFile>(json);
            if (parsed is null) throw new InvalidDataException("constraint file deserialised to null");
            constraint = parsed;
        }
        catch (Exception ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Failed to read constraint file: {ex.Message.EscapeMarkup()}");
            return 1;
        }

        var postedBy = GitService.UserEmail(repoRoot);
        using var api = new ApiClient(serverUrl);
        try
        {
            var posted = api.PostBounty(new PostBountyRequestDto(
                UniverseId:  values.RegistryId,
                PostedBy:    postedBy,
                Title:       constraint.Title,
                Description: constraint.Description,
                Predicate:   constraint.Predicate,
                RewardUsdc:  constraint.RewardUsdc));
            AnsiConsole.MarkupLine($"[green]✓[/] Posted bounty [cyan]{posted.Id}[/] — {posted.Title.EscapeMarkup()}");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Post failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
    }
}

public class BountyListCommand : Command<BountyListCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--status <STATUS>")]
        [Description("Filter by status (Open, Accepted, Delivered, Verified, Cancelled)")]
        public string? Status { get; init; }

        [CommandOption("--all-universes")]
        [Description("List bounties across all universes, not just the current one.")]
        public bool AllUniverses { get; init; }

        [CommandOption("--json")]     public bool    Json   { get; init; }
        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        var values   = repoRoot is null ? null : GitverseLayout.ReadValues(repoRoot);

        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        string? universeFilter = settings.AllUniverses ? null : values?.RegistryId;
        using var api = new ApiClient(serverUrl);
        IReadOnlyList<BountyDto> bounties;
        try { bounties = api.ListBounties(universeFilter, settings.Status); }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] List failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }

        if (settings.Json)
        {
            AnsiConsole.WriteLine(JsonSerializer.Serialize(bounties));
            return 0;
        }

        var table = new Table()
            .AddColumn("Id").AddColumn("Title").AddColumn("Status").AddColumn("Reward").AddColumn("Predicate");
        foreach (var b in bounties)
            table.AddRow(b.Id, b.Title, b.Status.ToString(), b.RewardUsdc.ToString("0.##"), b.Predicate);
        AnsiConsole.Write(table);
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
            var b = api.GetBounty(settings.Id);
            if (b is null)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] Bounty [cyan]{settings.Id}[/] not found.");
                return 2;
            }
            AnsiConsole.MarkupLine($"[bold]{b.Title.EscapeMarkup()}[/] [dim]({b.Id})[/]");
            AnsiConsole.MarkupLine($"  status:    {b.Status}");
            AnsiConsole.MarkupLine($"  universe:  {b.UniverseId}");
            AnsiConsole.MarkupLine($"  posted by: {b.PostedBy}");
            AnsiConsole.MarkupLine($"  predicate: {b.Predicate.EscapeMarkup()}");
            AnsiConsole.MarkupLine($"  reward:    {b.RewardUsdc} USDC");
            if (b.AcceptedBy is not null)
                AnsiConsole.MarkupLine($"  accepted:  {b.AcceptedBy}");
            if (b.DeliveryProof is not null)
                AnsiConsole.MarkupLine($"  proof:     {b.DeliveryProof.EscapeMarkup()}");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Show failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
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
        var repoRoot  = BountyHelpers.RequireRepoRoot();
        if (repoRoot is null) return 1;
        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }

        var acceptedBy = GitService.UserEmail(repoRoot);
        using var api = new ApiClient(serverUrl);
        try
        {
            var accepted = api.AcceptBounty(settings.Id, new AcceptBountyRequestDto(acceptedBy));
            AnsiConsole.MarkupLine($"[green]✓[/] Accepted [cyan]{accepted.Id}[/] as {acceptedBy}");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Accept failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
    }
}

public class BountyDeliverCommand : Command<BountyDeliverCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<id>")] public string Id { get; init; } = "";

        [CommandOption("--proof <FILE>")]
        [Description("Path (relative to repo root) of the genus-stamped file to submit as proof")]
        public string? ProofFile { get; init; }

        [CommandOption("--server <URL>")] public string? Server { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot  = BountyHelpers.RequireRepoRoot();
        if (repoRoot is null) return 1;
        var serverUrl = ApiClient.ResolveServerUrl(settings.Server, repoRoot);
        if (serverUrl is null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] No registry server configured.");
            return 1;
        }
        if (string.IsNullOrWhiteSpace(settings.ProofFile))
        {
            AnsiConsole.MarkupLine("[red]Error:[/] [cyan]--proof FILE[/] is required.");
            return 1;
        }

        var absProof = Path.IsPathRooted(settings.ProofFile)
            ? settings.ProofFile
            : Path.Combine(repoRoot, settings.ProofFile);
        var stamp = GenusStamper.ReadStamp(absProof);
        if (stamp is null)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] No genus stamp found on [cyan]{settings.ProofFile}[/]. " +
                "Write to it with [cyan]emanon write[/] first.");
            return 1;
        }

        var deliveredBy = GitService.UserEmail(repoRoot);
        using var api = new ApiClient(serverUrl);
        try
        {
            var delivered = api.DeliverBounty(
                settings.Id,
                new DeliverBountyRequestDto(stamp.Value.ToString(), deliveredBy));
            AnsiConsole.MarkupLine(
                $"[green]✓[/] Delivered [cyan]{delivered.Id}[/] " +
                $"[dim](status={delivered.Status}, proof={delivered.DeliveryProof})[/]");
            return 0;
        }
        catch (ApiException ex)
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] Deliver failed: {ex.Message.EscapeMarkup()}");
            return 2;
        }
    }
}

// ---------------------------------------------------------------------------

internal static class BountyHelpers
{
    public static string? RequireRepoRoot()
    {
        var root = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (root is null)
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe.");
        return root;
    }
}
