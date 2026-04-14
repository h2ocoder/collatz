using System.ComponentModel;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class WriteCommand : Command<WriteCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<path>")]
        [Description("File path to write (relative to repo root)")]
        public string Path { get; init; } = "";

        [CommandArgument(1, "[content]")]
        [Description("Content to write. If omitted, reads from stdin.")]
        public string? Content { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null)
        {
            AnsiConsole.MarkupLine("[red]Error:[/] Not inside an Emanon universe.");
            return 1;
        }

        string content = settings.Content ?? Console.In.ReadToEnd();
        string absPath = System.IO.Path.IsPathRooted(settings.Path)
            ? settings.Path
            : System.IO.Path.Combine(repoRoot, settings.Path);

        var dir = System.IO.Path.GetDirectoryName(absPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        File.WriteAllText(absPath, content);

        // Stamp with Collatz genus
        var values = GitverseLayout.ReadValues(repoRoot);
        int snapshotCount = values != null
            && values.TryGetValue("snapshot_count", out var sc)
            ? sc.GetInt32()
            : 0;
        string email = GitService.UserEmail(repoRoot);
        var genus = GenusStamper.StampFile(absPath, snapshotCount, email);

        AnsiConsole.MarkupLine(
            $"[green]✓[/] Wrote [cyan]{settings.Path}[/] " +
            $"[dim](genus: set_k={genus.SetK} oddity_s={genus.OddityS} index_i={genus.Index})[/]");
        return 0;
    }
}
