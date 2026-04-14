using System.ComponentModel;
using System.Text.Json;
using Emanon.Cli.Services;
using Emanon.Collatz;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class MergeCommand : Command<MergeCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<remote/branch>")]
        [Description("Remote branch to merge, e.g. alice/main")]
        public string RemoteBranch { get; init; } = "";
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe.");
            return 1;
        }

        var parts = settings.RemoteBranch.Split('/', 2);
        if (parts.Length != 2)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Remote branch must be in format remote/branch.");
            return 1;
        }
        var (remote, branch) = (parts[0], parts[1]);

        // Fetch latest
        AnsiConsole.MarkupLine($"[dim]Fetching {remote}…[/]");
        var (_, fetchErr, fetchExit) = GitService.TryRun($"fetch {remote}", repoRoot);
        if (fetchExit != 0)
        {
            AnsiConsole.MarkupLine($"[red]Fetch failed:[/] {fetchErr}");
            return 1;
        }

        // Attempt merge --no-commit --no-ff
        var (_, mergeErr, mergeExit) = GitService.TryRun(
            $"merge --no-commit --no-ff {remote}/{branch}", repoRoot);

        // Check for unmerged files
        var (lsOut, _, _) = GitService.TryRun("ls-files --unmerged", repoRoot);
        var conflictPaths = lsOut
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(line => line.Split('\t').LastOrDefault())
            .Where(p => p != null)
            .Distinct()
            .ToList();

        if (conflictPaths.Count == 0)
        {
            // Clean merge — commit it
            var msg = $"merge: integrate {remote}/{branch}";
            GitService.Run($"commit -m \"{msg}\"", repoRoot);
            AnsiConsole.MarkupLine($"[bold green]✓[/] Clean merge from [cyan]{settings.RemoteBranch}[/] committed.");
            return 0;
        }

        // Build conflict entries with genus info
        var conflicts = conflictPaths.Select(path =>
        {
            var oursGenus   = ReadGenusForStage(repoRoot, path!, 2);
        var theirsGenus = ReadGenusForStage(repoRoot, path!, 3);
            var oursLeverage   = CollatzMath.ComputeLeverage(oursGenus   ?? new Genus(1, 1, 1), GitService.CommitCount(repoRoot));
            var theirsLeverage = CollatzMath.ComputeLeverage(theirsGenus ?? new Genus(1, 1, 1), 10);

            return new
            {
                path,
                ours_genus    = oursGenus?.ToString()   ?? "unknown",
                theirs_genus  = theirsGenus?.ToString() ?? "unknown",
                ours_leverage   = Math.Round(oursLeverage, 2),
                theirs_leverage = Math.Round(theirsLeverage, 2),
                status = "pending"
            };
        }).ToList();

        // Write pending-merge.json
        var pendingPath = Path.Combine(repoRoot, GitverseLayout.PendingMerge);
        var pendingData = new
        {
            remote,
            branch,
            remote_branch = settings.RemoteBranch,
            conflicts,
            created_at = DateTime.UtcNow.ToString("O")
        };
        File.WriteAllText(pendingPath, JsonSerializer.Serialize(pendingData, new JsonSerializerOptions { WriteIndented = true }));

        AnsiConsole.MarkupLine($"[yellow]{conflictPaths.Count} conflict(s)[/] detected. Run [bold]emanon negotiate[/] to resolve.");

        var table = new Table();
        table.AddColumn("Path");
        table.AddColumn("Ours genus");
        table.AddColumn("Theirs genus");
        foreach (var c in conflicts)
            table.AddRow(c.path!, c.ours_genus, c.theirs_genus);
        AnsiConsole.Write(table);

        return 1; // Non-zero signals unresolved conflicts
    }

    private static Genus? ReadGenusForStage(string repoRoot, string path, int stage)
    {
        // Extract blob from index at given stage and read genus stamp
        var (sha, _, exit) = GitService.TryRun($"ls-files -u -- \"{path}\"", repoRoot);
        if (exit != 0) return null;
        var line = sha.Split('\n')
            .FirstOrDefault(l => l.StartsWith($"100") && l.Contains($"\t{path}") && l.Split('\t')[0].EndsWith($" {stage}"));
        if (line == null) return null;
        var blobSha = line.Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries)[1];
        var (content, _, catExit) = GitService.TryRun($"cat-file blob {blobSha}", repoRoot);
        if (catExit != 0) return null;
        var stampLine = content.Split('\n').LastOrDefault(l => l.Contains("emanon-genus"));
        if (stampLine == null) return null;
        return GenusStamper.ReadStamp(path); // Re-use parser via temp logic
    }
}
