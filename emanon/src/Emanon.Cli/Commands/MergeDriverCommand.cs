using System.ComponentModel;
using Emanon.Cli.Services;
using Emanon.Collatz;
using Spectre.Console;
using Spectre.Console.Cli;

namespace Emanon.Cli.Commands;

/// <summary>
/// Custom git merge driver. Invoked by git when two branches conflict on a
/// <c>regions/**</c> path — i.e., the files registered in <c>.gitattributes</c> as
/// <c>merge=emanon-collatz</c>.
///
/// Git passes four positional arguments:
///   %O — path to the common ancestor version (base)
///   %A — path to the current branch's version ("ours"). The driver WRITES its
///        resolution here; this is the output path.
///   %B — path to the incoming branch's version ("theirs")
///   %P — original repo-relative filename (informational)
///
/// Exit 0 → git treats the merge as resolved.
/// Exit 1 → git treats it as an unresolved conflict and leaves conflict markers.
///
/// ---
///
/// MVP rule — winner-takes-all.
/// Read the genus stamp from A and B. Whichever carries the lexicographically
/// larger (SetK, OddityS, Index, Writer) tuple wins; its full content replaces A.
/// If either side lacks a valid stamp, we exit 1 so a human (or the negotiation
/// UI) handles it — silently merging un-stamped content would violate the
/// protocol's "every write carries a genus" invariant.
///
/// This is intentionally a simplification of the full spec
/// (<c>docs/2026-04-13-gitverse-design.md</c>), which specifies three paths:
///   1. same set_k  → hybrid_merge(ours, theirs)
///   2. same oddity → weighted_merge with bit_destruction attenuation
///   3. unrelated   → defer to negotiation UI
/// Those are whole design exercises on their own. This command ships the
/// *mechanism* (driver fires, decides deterministically, no authority needed)
/// and is swap-in replaceable once hybrid/weighted merges are defined.
/// </summary>
public sealed class MergeDriverCommand : Command<MergeDriverCommand.Settings>
{
    public sealed class Settings : CommandSettings
    {
        [CommandOption("--contract-mode")]
        [Description("Byte-identical contract merge (NOT YET IMPLEMENTED — exits 1)")]
        public bool ContractMode { get; init; }

        [CommandOption("--append-only")]
        [Description("Append-only scar merge (NOT YET IMPLEMENTED — exits 1)")]
        public bool AppendOnly { get; init; }

        [CommandArgument(0, "<base>")]
        [Description("Path to the common-ancestor version (git %O)")]
        public string BasePath { get; init; } = "";

        [CommandArgument(1, "<ours>")]
        [Description("Path to our version — also the output path (git %A)")]
        public string OursPath { get; init; } = "";

        [CommandArgument(2, "<theirs>")]
        [Description("Path to their version (git %B)")]
        public string TheirsPath { get; init; } = "";

        [CommandArgument(3, "[original-path]")]
        [Description("Original repo-relative filename (git %P, informational)")]
        public string? OriginalPath { get; init; }
    }

    public override int Execute(CommandContext context, Settings settings)
    {
        if (settings.ContractMode || settings.AppendOnly)
        {
            AnsiConsole.MarkupLine(
                $"[yellow]emanon merge-driver:[/] --contract-mode / --append-only not yet implemented. " +
                "Leaving conflict markers for manual resolution.");
            return 1;
        }

        var oursStamp   = GenusStamper.ReadFullStamp(settings.OursPath);
        var theirsStamp = GenusStamper.ReadFullStamp(settings.TheirsPath);

        if (oursStamp is null || theirsStamp is null)
        {
            AnsiConsole.MarkupLine(
                $"[yellow]emanon-collatz:[/] missing genus on one or both sides of " +
                $"[cyan]{(settings.OriginalPath ?? "?").EscapeMarkup()}[/] — deferring to negotiation.");
            return 1;
        }

        var decision = ResolveWinner(oursStamp.ToGenus(), theirsStamp.ToGenus());

        var winnerPath   = decision == MergeWinner.Ours ? settings.OursPath   : settings.TheirsPath;
        var winnerStamp  = decision == MergeWinner.Ours ? oursStamp           : theirsStamp;
        var loserStamp   = decision == MergeWinner.Ours ? theirsStamp         : oursStamp;

        // Build the merged content: winner's file, but with the stamp line enriched
        // to carry the loser's genus + writer — that audit trail lets future readers
        // see a merge decision happened here and against what (git discards driver
        // stdout, so the commit message alone can't tell that story).
        var enriched = GenusStamper.BuildContentWithDisplacement(
            winnerPath,
            loserStamp.ToGenus(),
            loserStamp.Writer);

        if (enriched is null)
        {
            // Shouldn't happen — we already confirmed both sides parsed — but if
            // the winner's file shape is unexpected (binary, sidecar-only, etc.),
            // defer to the human rather than silently writing a worse file.
            AnsiConsole.MarkupLine(
                $"[yellow]emanon-collatz:[/] could not rewrite winner stamp on " +
                $"[cyan]{(settings.OriginalPath ?? "?").EscapeMarkup()}[/] — deferring.");
            return 1;
        }

        AtomicWriteText(settings.OursPath, enriched);

        AnsiConsole.MarkupLine(
            $"[green]emanon-collatz:[/] [cyan]{(settings.OriginalPath ?? "?").EscapeMarkup()}[/] " +
            $"resolved — {decision.ToString().ToLowerInvariant()} wins " +
            $"(winner: {winnerStamp.ToGenus()}, displaced: {loserStamp.ToGenus()})");
        return 0;
    }

    /// <summary>
    /// Write <paramref name="content"/> to <paramref name="targetPath"/> atomically:
    /// write to a sibling temp file, flush to disk, then rename over the target.
    /// A crash mid-write leaves either the original file or the temp file — never
    /// a truncated target that git might then commit.
    /// </summary>
    private static void AtomicWriteText(string targetPath, string content)
    {
        var dir = Path.GetDirectoryName(targetPath) ?? ".";
        var tmp = Path.Combine(dir, "." + Path.GetFileName(targetPath) + ".emanon-" + Guid.NewGuid().ToString("N")[..8] + ".tmp");
        try
        {
            using (var fs = new FileStream(tmp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var sw = new StreamWriter(fs))
            {
                sw.Write(content);
                sw.Flush();
                fs.Flush(flushToDisk: true);
            }
            File.Move(tmp, targetPath, overwrite: true);
        }
        catch
        {
            if (File.Exists(tmp)) { try { File.Delete(tmp); } catch { } }
            throw;
        }
    }

    /// <summary>Public so unit tests can exercise the rule without invoking the CLI.</summary>
    public static MergeWinner ResolveWinner(Genus ours, Genus theirs)
    {
        int cmp = Compare(ours, theirs);
        return cmp >= 0 ? MergeWinner.Ours : MergeWinner.Theirs;

        static int Compare(Genus a, Genus b)
        {
            int c = a.SetK.CompareTo(b.SetK);
            if (c != 0) return c;
            c = a.OddityS.CompareTo(b.OddityS);
            if (c != 0) return c;
            return a.Index.CompareTo(b.Index);
        }
    }
}

public enum MergeWinner { Ours, Theirs }
