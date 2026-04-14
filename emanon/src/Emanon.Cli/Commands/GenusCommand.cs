using System.ComponentModel;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class GenusCommand : Command<GenusCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandArgument(0, "<path>")]
        [Description("File to read the genus stamp from")]
        public string Path { get; init; } = "";
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        var absPath  = System.IO.Path.IsPathRooted(settings.Path)
            ? settings.Path
            : System.IO.Path.Combine(repoRoot ?? Directory.GetCurrentDirectory(), settings.Path);

        if (!File.Exists(absPath))
        {
            AnsiConsole.MarkupLine($"[red]Error:[/] File not found: {settings.Path}");
            return 1;
        }

        var genus = GenusStamper.ReadStamp(absPath);
        if (genus == null)
        {
            AnsiConsole.MarkupLine($"[yellow]No genus stamp found in[/] [cyan]{settings.Path}[/]");
            return 0;
        }

        var table = new Table();
        table.AddColumn("Field");
        table.AddColumn("Value");
        table.AddRow("File",     settings.Path);
        table.AddRow("Set_k",    genus.Value.SetK.ToString());
        table.AddRow("Oddity_s", genus.Value.OddityS.ToString());
        table.AddRow("Index_i",  genus.Value.Index.ToString());
        AnsiConsole.Write(table);
        return 0;
    }
}
