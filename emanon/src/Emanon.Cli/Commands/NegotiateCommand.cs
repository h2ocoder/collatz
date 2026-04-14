using System.ComponentModel;
using System.Text.Json;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

/// <summary>
/// Interactive negotiation UI for pending merge conflicts.
/// Uses Spectre.Console for rich terminal output and prompts.
/// </summary>
public class NegotiateCommand : Command<NegotiateCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--non-interactive")]
        [Description("Read a JSON resolution plan from stdin (for scripting)")]
        public bool NonInteractive { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe.");
            return 1;
        }

        var pendingPath = Path.Combine(repoRoot, GitverseLayout.PendingMerge);
        if (!File.Exists(pendingPath))
        {
            AnsiConsole.MarkupLine("[yellow]No pending merge.[/] Run [bold]emanon merge[/] first.");
            return 0;
        }

        var pending = JsonSerializer.Deserialize<JsonElement>(File.ReadAllText(pendingPath));
        var conflicts = pending.GetProperty("conflicts").EnumerateArray().ToList();
        string remoteBranch = pending.GetProperty("remote_branch").GetString() ?? "unknown";

        AnsiConsole.Write(new Rule($"[bold yellow]Negotiation — {conflicts.Count} conflict(s) with {remoteBranch}[/]"));
        AnsiConsole.WriteLine();

        var resolutions = settings.NonInteractive
            ? ReadPlanFromStdin()
            : InteractiveResolve(repoRoot, conflicts, remoteBranch);

        ApplyResolutions(repoRoot, resolutions);

        // Commit the merge
        var trailers = string.Join("\n", resolutions.Select(r =>
            $"Resolved-path: {r.Path} via {r.Resolution}"));
        var commitMsg = $"merge: resolve conflicts with {remoteBranch}\n\n{trailers}";
        GitService.Run($"add -A", repoRoot);
        GitService.Run($"commit -m \"{EscapeForShell(commitMsg)}\"", repoRoot);

        File.Delete(pendingPath);
        AnsiConsole.MarkupLine($"[bold green]✓[/] Merge committed. All conflicts resolved.");
        return 0;
    }

    // -------------------------------------------------------------------------

    private record ConflictResolution(string Path, string Resolution, string? Terms = null);

    private List<ConflictResolution> InteractiveResolve(
        string repoRoot, List<JsonElement> conflicts, string remoteBranch)
    {
        var resolutions = new List<ConflictResolution>();

        foreach (var conflict in conflicts)
        {
            var path        = conflict.GetProperty("path").GetString()!;
            var oursGenus   = conflict.GetProperty("ours_genus").GetString()!;
            var theirsGenus = conflict.GetProperty("theirs_genus").GetString()!;
            var oursLev     = conflict.GetProperty("ours_leverage").GetDouble();
            var theirsLev   = conflict.GetProperty("theirs_leverage").GetDouble();

            AnsiConsole.MarkupLine($"[bold]Conflict:[/] [cyan]{path}[/]");

            var table = new Table().NoBorder();
            table.AddColumn("Side");
            table.AddColumn("Genus");
            table.AddColumn("Leverage");
            table.AddRow("[blue]Ours[/]",   oursGenus,   $"[blue]{oursLev:F2}[/]");
            table.AddRow("[red]Theirs[/]", theirsGenus, $"[red]{theirsLev:F2}[/]");
            AnsiConsole.Write(table);

            var choice = AnsiConsole.Prompt(
                new SelectionPrompt<string>()
                    .Title("Choose resolution:")
                    .AddChoices("battle", "contract", "fork", "manual"));

            string? terms = null;
            if (choice == "contract")
                terms = AnsiConsole.Ask<string>("  Contract terms: ");

            resolutions.Add(new ConflictResolution(path, choice, terms));
            AnsiConsole.WriteLine();
        }

        return resolutions;
    }

    private List<ConflictResolution> ReadPlanFromStdin()
    {
        var json = Console.In.ReadToEnd();
        var plan = JsonSerializer.Deserialize<JsonElement>(json);
        return plan.EnumerateArray()
            .Select(item => new ConflictResolution(
                item.GetProperty("path").GetString()!,
                item.GetProperty("resolution").GetString()!,
                item.TryGetProperty("terms", out var t) ? t.GetString() : null))
            .ToList();
    }

    private void ApplyResolutions(string repoRoot, List<ConflictResolution> resolutions)
    {
        foreach (var r in resolutions)
        {
            var absPath = Path.Combine(repoRoot, r.Path);
            switch (r.Resolution)
            {
                case "battle":
                    // Keep ours — checkout our version
                    GitService.TryRun($"checkout --ours -- \"{r.Path}\"", repoRoot);
                    WriteScar(repoRoot, r.Path, "battle");
                    AnsiConsole.MarkupLine($"  [blue]⚔ Battle[/] — kept ours: [cyan]{r.Path}[/]");
                    break;

                case "contract":
                    // Accept theirs and write a contract file
                    GitService.TryRun($"checkout --theirs -- \"{r.Path}\"", repoRoot);
                    WriteContract(repoRoot, r.Path, r.Terms ?? "agreed");
                    AnsiConsole.MarkupLine($"  [green]📜 Contract[/] — accepted theirs: [cyan]{r.Path}[/]");
                    break;

                case "fork":
                    // Keep ours; record fork pointer
                    GitService.TryRun($"checkout --ours -- \"{r.Path}\"", repoRoot);
                    WriteForkPointer(repoRoot, r.Path);
                    AnsiConsole.MarkupLine($"  [yellow]🍴 Fork[/] — diverged: [cyan]{r.Path}[/]");
                    break;

                case "manual":
                    AnsiConsole.MarkupLine($"  [dim]Manual resolution expected for:[/] [cyan]{r.Path}[/]");
                    break;
            }
        }
    }

    private void WriteScar(string repoRoot, string path, string kind)
    {
        var scarDir  = Path.Combine(repoRoot, "scars");
        Directory.CreateDirectory(scarDir);
        var scarFile = Path.Combine(scarDir, $"{DateTime.UtcNow:yyyyMMddHHmmss}-{SanitizeName(path)}.scar");
        File.WriteAllText(scarFile, JsonSerializer.Serialize(new
        {
            kind,
            path,
            resolved_at = DateTime.UtcNow.ToString("O")
        }, new JsonSerializerOptions { WriteIndented = true }));
    }

    private void WriteContract(string repoRoot, string path, string terms)
    {
        var contractDir  = Path.Combine(repoRoot, "contracts");
        Directory.CreateDirectory(contractDir);
        var contractFile = Path.Combine(contractDir, $"{DateTime.UtcNow:yyyyMMddHHmmss}-{SanitizeName(path)}.contract");
        File.WriteAllText(contractFile, JsonSerializer.Serialize(new
        {
            path,
            terms,
            signed_at = DateTime.UtcNow.ToString("O")
        }, new JsonSerializerOptions { WriteIndented = true }));
    }

    private void WriteForkPointer(string repoRoot, string path)
    {
        var forkDir  = Path.Combine(repoRoot, "forks");
        Directory.CreateDirectory(forkDir);
        var forkFile = Path.Combine(forkDir, $"{DateTime.UtcNow:yyyyMMddHHmmss}-{SanitizeName(path)}.fork");
        File.WriteAllText(forkFile, JsonSerializer.Serialize(new
        {
            path,
            forked_at = DateTime.UtcNow.ToString("O"),
            head      = GitService.HeadShort(repoRoot)
        }, new JsonSerializerOptions { WriteIndented = true }));
    }

    private static string SanitizeName(string p) =>
        Path.GetFileNameWithoutExtension(p).Replace("/", "_").Replace("\\", "_");

    private static string EscapeForShell(string s) =>
        s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n");
}
