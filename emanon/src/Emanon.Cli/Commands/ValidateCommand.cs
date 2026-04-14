using System.ComponentModel;
using System.Text.Json;
using Emanon.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

public class ValidateCommand : Command<ValidateCommand.Settings>
{
    public class Settings : CommandSettings
    {
        [CommandOption("--strict")]
        [Description("Fail on warnings as well as errors")]
        public bool Strict { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        var repoRoot = GitService.FindRepoRoot(Directory.GetCurrentDirectory());
        if (repoRoot == null)
        {
            AnsiConsole.MarkupLine("[red]✗[/] Not inside a git repo.");
            return 1;
        }

        var errors   = new List<string>();
        var warnings = new List<string>();

        // Rule 1: required directories exist
        foreach (var dir in GitverseLayout.RequiredDirs)
        {
            var full = Path.Combine(repoRoot, dir);
            if (!Directory.Exists(full))
                errors.Add($"Missing required directory: {dir}");
        }

        // Rule 2: values.json exists and is valid JSON
        var valuesPath = Path.Combine(repoRoot, GitverseLayout.ValuesFile);
        if (!File.Exists(valuesPath))
        {
            errors.Add("Missing .gitverse/values.json");
        }
        else
        {
            try
            {
                var values = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(
                    File.ReadAllText(valuesPath));
                // Rule 3: required keys
                foreach (var key in new[] { "universe_name", "version", "snapshot_count" })
                    if (values == null || !values.ContainsKey(key))
                        errors.Add($"values.json missing required key: {key}");
            }
            catch (JsonException ex)
            {
                errors.Add($"values.json is invalid JSON: {ex.Message}");
            }
        }

        // Rule 4: .gitattributes has merge driver lines
        var attrPath = Path.Combine(repoRoot, ".gitattributes");
        if (!File.Exists(attrPath))
        {
            warnings.Add(".gitattributes not found — merge driver not registered");
        }
        else
        {
            var attr = File.ReadAllText(attrPath);
            if (!attr.Contains("emanon-collatz"))
                warnings.Add(".gitattributes missing emanon-collatz merge driver line");
        }

        // Rule 5: genus stamps in regions/ (warn only)
        var regionsDir = Path.Combine(repoRoot, "regions");
        if (Directory.Exists(regionsDir))
        {
            foreach (var file in Directory.GetFiles(regionsDir, "*", SearchOption.AllDirectories))
            {
                if (file.EndsWith(".gitkeep") || file.EndsWith(".genus")) continue;
                var genus = GenusStamper.ReadStamp(file);
                if (genus == null)
                    warnings.Add($"regions file missing genus stamp: {Path.GetRelativePath(repoRoot, file)}");
            }
        }

        // Print results
        AnsiConsole.Write(new Rule("[bold]Emanon Validate[/]"));
        if (errors.Count == 0 && warnings.Count == 0)
        {
            AnsiConsole.MarkupLine("[bold green]✓ Universe is valid.[/]");
            return 0;
        }

        foreach (var err in errors)
            AnsiConsole.MarkupLine($"[red]✗ ERROR:[/] {err}");
        foreach (var warn in warnings)
            AnsiConsole.MarkupLine($"[yellow]⚠ WARN:[/]  {warn}");

        bool fail = errors.Count > 0 || (settings.Strict && warnings.Count > 0);
        if (!fail)
            AnsiConsole.MarkupLine("[yellow]Valid with warnings.[/]");
        return fail ? 1 : 0;
    }
}
