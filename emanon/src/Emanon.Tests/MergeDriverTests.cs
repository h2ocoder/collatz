using Emanon.Cli.Commands;
using Emanon.Cli.Services;
using Emanon.Collatz;

namespace Emanon.Tests;

public class MergeDriverTests : IDisposable
{
    private readonly string _tmpDir;

    public MergeDriverTests()
    {
        _tmpDir = Path.Combine(Path.GetTempPath(), "emanon-merge-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(_tmpDir);
    }

    public void Dispose() => Directory.Delete(_tmpDir, recursive: true);

    // ── ResolveWinner — pure rule ─────────────────────────────────────────────

    [Fact]
    public void Higher_SetK_Wins()
    {
        var ours   = new Genus(SetK: 7, OddityS: 1, Index: 7);
        var theirs = new Genus(SetK: 3, OddityS: 9, Index: 3);
        Assert.Equal(MergeWinner.Ours, MergeDriverCommand.ResolveWinner(ours, theirs));
    }

    [Fact]
    public void Tiebreak_On_OddityS_When_SetK_Equal()
    {
        var ours   = new Genus(SetK: 5, OddityS: 2, Index: 5);
        var theirs = new Genus(SetK: 5, OddityS: 4, Index: 5);
        Assert.Equal(MergeWinner.Theirs, MergeDriverCommand.ResolveWinner(ours, theirs));
    }

    [Fact]
    public void Tiebreak_On_Index_When_SetK_And_OddityS_Equal()
    {
        var ours   = new Genus(SetK: 5, OddityS: 3, Index: 12);
        var theirs = new Genus(SetK: 5, OddityS: 3, Index: 7);
        Assert.Equal(MergeWinner.Ours, MergeDriverCommand.ResolveWinner(ours, theirs));
    }

    [Fact]
    public void Ours_Wins_On_Full_Tie()
    {
        // Deterministic fallback: when all three components tie, 'ours' wins.
        // Guarantees the rule is total (never underdefined).
        var g = new Genus(SetK: 4, OddityS: 2, Index: 4);
        Assert.Equal(MergeWinner.Ours, MergeDriverCommand.ResolveWinner(g, g));
    }

    // ── End-to-end file-level behaviour (still a unit test — no git) ──────────

    [Fact]
    public void DriverWrites_WinnerContent_ToOursPath()
    {
        var basePath   = StampedFile("base.txt",   "base",    new Genus(0, 0, 0));
        var oursPath   = StampedFile("ours.txt",   "OURS",    new Genus(SetK: 2, OddityS: 1, Index: 2));
        var theirsPath = StampedFile("theirs.txt", "THEIRS",  new Genus(SetK: 9, OddityS: 1, Index: 9));

        int exit = InvokeDriver(basePath, oursPath, theirsPath);
        Assert.Equal(0, exit);

        // theirs had higher set_k — its content should now be in oursPath.
        Assert.StartsWith("THEIRS", File.ReadAllText(oursPath));
    }

    [Fact]
    public void DriverEnriches_WinnerStamp_WithDisplacedGenus()
    {
        var oursGenus   = new Genus(SetK: 3, OddityS: 2, Index: 3);
        var theirsGenus = new Genus(SetK: 11, OddityS: 5, Index: 11);

        var basePath   = StampedFile("base.txt",   "base",   new Genus(0, 0, 0));
        var oursPath   = StampedFileWithWriter("ours.txt",   "OURS",   oursGenus,   "alice@test");
        var theirsPath = StampedFileWithWriter("theirs.txt", "THEIRS", theirsGenus, "bob@test");

        int exit = InvokeDriver(basePath, oursPath, theirsPath);
        Assert.Equal(0, exit);

        var finalStamp = GenusStamper.ReadFullStamp(oursPath);
        Assert.NotNull(finalStamp);
        // Winner (theirs) preserved.
        Assert.Equal(theirsGenus, finalStamp!.ToGenus());
        Assert.Equal("bob@test", finalStamp.Writer);
        // Loser (ours) recorded as displaced.
        Assert.Equal(oursGenus, finalStamp.DisplacedGenus);
        Assert.Equal("alice@test", finalStamp.DisplacedWriter);
    }

    [Fact]
    public void DriverDoesNotLeaveTempFiles_AfterSuccessfulWrite()
    {
        var basePath   = StampedFile("base.txt",   "base",   new Genus(0, 0, 0));
        var oursPath   = StampedFile("ours.txt",   "OURS",   new Genus(1, 1, 1));
        var theirsPath = StampedFile("theirs.txt", "THEIRS", new Genus(9, 1, 9));

        int exit = InvokeDriver(basePath, oursPath, theirsPath);
        Assert.Equal(0, exit);

        // No ".emanon-*.tmp" sidecars lingering — atomic rename should have cleaned up.
        var strays = Directory.GetFiles(_tmpDir, ".*.emanon-*.tmp");
        Assert.Empty(strays);
    }

    [Fact]
    public void DriverDefers_WhenOursHasNoStamp()
    {
        var basePath   = StampedFile("base.txt",   "base", new Genus(0, 0, 0));
        var oursPath   = RawFile("ours.txt",       "unstamped");   // no stamp
        var theirsPath = StampedFile("theirs.txt", "THEIRS", new Genus(SetK: 5, OddityS: 1, Index: 5));

        int exit = InvokeDriver(basePath, oursPath, theirsPath);
        Assert.Equal(1, exit);
        // 'ours' must be untouched — driver's contract is "exit 1 → leave file alone for git".
        Assert.Equal("unstamped", File.ReadAllText(oursPath));
    }

    [Fact]
    public void DriverDefers_WhenTheirsHasNoStamp()
    {
        var basePath   = StampedFile("base.txt",   "base", new Genus(0, 0, 0));
        var oursPath   = StampedFile("ours.txt",   "OURS", new Genus(SetK: 5, OddityS: 1, Index: 5));
        var theirsPath = RawFile("theirs.txt",     "unstamped");

        int exit = InvokeDriver(basePath, oursPath, theirsPath);
        Assert.Equal(1, exit);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private int InvokeDriver(string basePath, string oursPath, string theirsPath)
    {
        // Spectre.Console CommandContext can't be constructed standalone, so we
        // drive the command via CommandApp which handles arg binding + context.
        var app = new Spectre.Console.Cli.CommandApp<MergeDriverCommand>();
        return app.Run(new[] { basePath, oursPath, theirsPath, "sample/relative/path" });
    }

    private string StampedFile(string name, string content, Genus genus)
        => StampedFileWithWriter(name, content, genus, "test@emanon");

    private string StampedFileWithWriter(string name, string content, Genus genus, string writer)
    {
        // Hand-built stamp line so we can pin genus values without relying on the
        // (path, snapshot)-based hash in GenusStamper.StampFile.
        var path = Path.Combine(_tmpDir, name);
        var stamp = $$"""
            {{content}}
            # emanon-genus: {"set_k":{{genus.SetK}},"oddity_s":{{genus.OddityS}},"index_i":{{genus.Index}},"writer":"{{writer}}","snapshot":0}
            """;
        File.WriteAllText(path, stamp);
        return path;
    }

    private string RawFile(string name, string content)
    {
        var path = Path.Combine(_tmpDir, name);
        File.WriteAllText(path, content);
        return path;
    }
}
