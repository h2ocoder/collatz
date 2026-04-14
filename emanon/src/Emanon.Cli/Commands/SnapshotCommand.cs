using System.ComponentModel;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class SnapshotCommand : Command<SnapshotCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("-m|--message <MSG>")]
        [Description("Snapshot message (default: auto-generated)")]
        public string? Message { get; init; }

        [CommandOption("--no-stage")]
        [Description("Skip 'git add -A'; only commit already-staged changes")]
        public bool NoStage { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe (no git repo found).");
            return 1;
        }

        if (!settings.NoStage)
            GitService.Run("add -A", repoRoot);

        // Check if there's anything to commit
        var (status, _, _) = GitService.TryRun("diff --cached --quiet", repoRoot);
        var (_, _, nothingExit) = GitService.TryRun("diff --cached --stat", repoRoot);
        var (statOut, _, _) = GitService.TryRun("diff --cached --stat", repoRoot);

        if (string.IsNullOrWhiteSpace(statOut))
        {
            AnsiConsole.MarkupLine("[yellow]Nothing to snapshot.[/] Working tree is clean.");
            return 0;
        }

        // Increment snapshot count
        int count = GitverseLayout.IncrementSnapshotCount(repoRoot);
        // Re-stage values.json after mutation
        GitService.Run($"add {GitverseLayout.ValuesFile}", repoRoot);

        var message = settings.Message ?? $"snapshot {count:D4}";
        var email   = GitService.UserEmail(repoRoot);
        var head    = GitService.HeadShort(repoRoot);

        var fullMessage =
            $"snapshot: {message}\n\n" +
            $"Snapshot-Count: {count}\n" +
            $"Universe-Head: {head}\n" +
            $"Writer: {email}";

        GitService.Run($"commit -m \"{EscapeForShell(fullMessage)}\"", repoRoot);

        AnsiConsole.MarkupLine($"[bold green]✓[/] Snapshot [cyan]#{count}[/] committed — {message}");
        return 0;
    }

    private static string EscapeForShell(string s) =>
        s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n");
}
