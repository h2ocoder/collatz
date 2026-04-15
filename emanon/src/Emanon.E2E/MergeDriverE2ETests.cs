using Emanon.Cli.Commands;
using Emanon.Cli.Services;
using Emanon.Collatz;
using Emanon.E2E.Fixtures;
using Xunit.Abstractions;

namespace Emanon.E2E;

/// <summary>
/// Proves the headline claim of the gitverse design: two branches that write to
/// the same region file converge on a deterministic winner without any central
/// authority — the resolution is pure Collatz math fired from git's own merge
/// machinery. No server is touched in these tests.
/// </summary>
[Trait("Category", "E2E")]
public class MergeDriverE2ETests
{
    private readonly ITestOutputHelper _out;

    public MergeDriverE2ETests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void Conflict_In_Regions_IsResolved_ByDriver_WithoutAuthority()
    {
        using var tmp = new TempUniverse();

        // Point the merge-driver config at the built CLI DLL so `git merge` can
        // actually invoke us. Without this, git would try to run "emanon" and fail.
        tmp.Cli.SetEnv("EMANON_CMD", $"dotnet exec {tmp.Cli.CliDll}");

        // 1. Init universe — this writes the .gitattributes + git config for the
        //    emanon-collatz driver, using EMANON_CMD.
        AssertSucceeds(tmp.Cli.Run("init", "merge-test"), "emanon init");

        // 2. Seed a shared file on main with a known base stamp.
        const string sharedRel = "regions/shared.txt";
        var sharedAbs = tmp.ResolvePath(sharedRel);
        WriteStamped(sharedAbs, "base-content", snapshot: 0, writer: tmp.AuthorEmail);
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "seed shared region");

        // 3. Fork: create an 'alice' branch, overwrite with a DIFFERENT stamp by
        //    bumping the snapshot number. (The stamp is derived from path + snapshot,
        //    so a different snapshot yields a different genus on the same path.)
        tmp.Git("checkout", "-q", "-b", "alice");
        var aliceGenus = WriteStamped(sharedAbs, "alice-content", snapshot: 1, writer: tmp.AuthorEmail);
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "alice writes");

        // 4. Main: switch back and make a conflicting write with a different snapshot.
        tmp.Git("checkout", "-q", "main");
        var mainGenus = WriteStamped(sharedAbs, "main-content", snapshot: 2, writer: tmp.AuthorEmail);
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "main writes");

        // 5. Pre-compute what the driver MUST do — our oracle.
        var expected = MergeDriverCommand.ResolveWinner(ours: mainGenus, theirs: aliceGenus);
        var expectedContent = expected == MergeWinner.Ours ? "main-content" : "alice-content";
        _out.WriteLine($"main genus:  {mainGenus}");
        _out.WriteLine($"alice genus: {aliceGenus}");
        _out.WriteLine($"expected winner: {expected} → '{expectedContent}'");

        // 6. The actual moment: git merge. Conflict detected → driver fires → driver
        //    exits 0 → git commits the merge automatically.
        var merge = tmp.Git("merge", "--no-edit", "-m", "merge alice", "alice");
        _out.WriteLine("git merge stdout:\n" + merge.stdout);
        _out.WriteLine("git merge stderr:\n" + merge.stderr);
        Assert.Equal(0, merge.exit);

        // 7. Working tree and index must both be clean — confirmation that git
        //    considers the merge fully resolved.
        var (status, _, statusExit) = tmp.Git("status", "--porcelain");
        Assert.Equal(0, statusExit);
        Assert.True(string.IsNullOrWhiteSpace(status),
            $"Working tree should be clean after driver resolution. Saw:\n{status}");

        // 8. The merged file should carry the winner's content.
        var merged = File.ReadAllText(sharedAbs);
        Assert.Contains(expectedContent, merged);

        // 9. The merged file still carries a valid genus stamp (the winner's), and
        //    the stamp records the displaced side's genus so the resolution is
        //    auditable from the file alone (git discards merge-driver stdout).
        var finalStamp = GenusStamper.ReadFullStamp(sharedAbs);
        Assert.NotNull(finalStamp);
        var winnerGenus   = expected == MergeWinner.Ours ? mainGenus  : aliceGenus;
        var displacedGenus = expected == MergeWinner.Ours ? aliceGenus : mainGenus;
        Assert.Equal(winnerGenus, finalStamp!.ToGenus());
        Assert.Equal(displacedGenus, finalStamp.DisplacedGenus);

        // 10. A merge commit was created.
        var (log, _, _) = tmp.Git("log", "--oneline", "-n", "5");
        Assert.Contains("merge alice", log);
    }

    [Fact]
    public void Conflict_WithUnstampedSide_LeavesGitConflictMarkers()
    {
        using var tmp = new TempUniverse();
        tmp.Cli.SetEnv("EMANON_CMD", $"dotnet exec {tmp.Cli.CliDll}");

        AssertSucceeds(tmp.Cli.Run("init", "defer-test"), "emanon init");

        const string sharedRel = "regions/shared.txt";
        var sharedAbs = tmp.ResolvePath(sharedRel);
        WriteStamped(sharedAbs, "base-content", snapshot: 0, writer: tmp.AuthorEmail);
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "seed");

        // Branch alice: write unstamped content directly (no genus on this side).
        tmp.Git("checkout", "-q", "-b", "alice");
        File.WriteAllText(sharedAbs, "alice-unstamped");
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "alice (no stamp)");

        // Main: write stamped content.
        tmp.Git("checkout", "-q", "main");
        WriteStamped(sharedAbs, "main-content", snapshot: 1, writer: tmp.AuthorEmail);
        tmp.Git("add", sharedRel);
        tmp.Git("commit", "-q", "-m", "main writes");

        var merge = tmp.Git("merge", "--no-edit", "-m", "merge alice", "alice");
        // Driver exits 1 → git leaves conflict markers, merge command exits non-zero.
        Assert.NotEqual(0, merge.exit);

        // Working tree should NOT be clean — unresolved conflict remains.
        var (status, _, _) = tmp.Git("status", "--porcelain");
        Assert.False(string.IsNullOrWhiteSpace(status),
            "Expected git to report unresolved conflict after driver deferred.");
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static Genus WriteStamped(string absPath, string content, int snapshot, string writer)
    {
        var dir = Path.GetDirectoryName(absPath)!;
        Directory.CreateDirectory(dir);
        File.WriteAllText(absPath, content);
        return GenusStamper.StampFile(absPath, snapshot, writer);
    }

    private void AssertSucceeds(CliResult result, string label)
    {
        if (result.Succeeded) return;
        _out.WriteLine($"{label} FAILED (exit {result.ExitCode})");
        _out.WriteLine($"stdout:\n{result.Stdout}");
        _out.WriteLine($"stderr:\n{result.Stderr}");
        Assert.Fail($"{label} exited {result.ExitCode}");
    }
}
