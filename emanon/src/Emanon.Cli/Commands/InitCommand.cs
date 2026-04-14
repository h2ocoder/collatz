using System.ComponentModel;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class InitCommand : Command<InitCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "[name]")]
        [Description("Universe name (default: current directory name)")]
        public string? Name { get; init; }

        [CommandOption("--dir <DIR>")]
        [Description("Directory to initialise (default: current directory)")]
        public string? Dir { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var targetDir = settings.Dir ?? Directory.GetCurrentDirectory();
        if (!Directory.Exists(targetDir))
            Directory.CreateDirectory(targetDir);

        var universeName = settings.Name ?? Path.GetFileName(Path.GetFullPath(targetDir));

        AnsiConsole.MarkupLine($"[bold green]Initialising universe:[/] [cyan]{universeName}[/]");

        // 1. git init if needed
        var (_, _, gitExitCode) = GitService.TryRun("rev-parse --git-dir", targetDir);
        if (gitExitCode != 0)
        {
            GitService.Run("init", targetDir);
            AnsiConsole.MarkupLine("  [dim]git init[/]");
        }

        // 2. Create canonical directories
        foreach (var dir in GitverseLayout.RequiredDirs)
        {
            var full = Path.Combine(targetDir, dir);
            Directory.CreateDirectory(full);
        }

        // 3. .gitkeep placeholders for empty dirs
        foreach (var dir in new[] { "regions", "contracts", "scars", "forks" })
        {
            var keep = Path.Combine(targetDir, dir, ".gitkeep");
            if (!File.Exists(keep)) File.WriteAllText(keep, "");
        }

        // 4. values.json
        var valuesPath = Path.Combine(targetDir, GitverseLayout.ValuesFile);
        if (!File.Exists(valuesPath))
        {
            var defaults = GitverseLayout.DefaultValues();
            defaults["universe_name"] = universeName;
            GitverseLayout.WriteValues(targetDir, defaults);
        }

        // 5. .gitattributes
        var attrPath = Path.Combine(targetDir, ".gitattributes");
        if (!File.Exists(attrPath))
            File.WriteAllText(attrPath, GitverseLayout.DefaultGitAttributes + Environment.NewLine);

        // 6. .gitignore
        var ignorePath = Path.Combine(targetDir, ".gitignore");
        if (!File.Exists(ignorePath))
            File.WriteAllText(ignorePath, GitverseLayout.DefaultGitIgnore + Environment.NewLine);

        // 7. Register the Collatz merge driver in local git config
        GitService.Run("config merge.emanon-collatz.driver \"emanon merge-driver %O %A %B %P\"", targetDir);
        GitService.Run("config merge.emanon-contract.driver \"emanon merge-driver --contract-mode %O %A %B %P\"", targetDir);
        GitService.Run("config merge.emanon-append-only.driver \"emanon merge-driver --append-only %O %A %B %P\"", targetDir);

        // 8. Stage everything and make initial commit
        GitService.Run("add -A", targetDir);
        var (_, _, commitExit) = GitService.TryRun(
            "commit -m \"chore(emanon): genesis — initialise universe layout\n\nUniverse: " + universeName + "\"",
            targetDir);
        if (commitExit == 0)
            AnsiConsole.MarkupLine("  [dim]Genesis commit created[/]");
        else
            AnsiConsole.MarkupLine("  [dim]Nothing to commit (already initialised)[/]");

        AnsiConsole.MarkupLine($"[bold green]✓[/] Universe [cyan]{universeName}[/] ready at [dim]{targetDir}[/]");
        return 0;
    }
}
