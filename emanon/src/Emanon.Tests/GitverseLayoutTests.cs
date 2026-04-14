using System.Text.Json;
using Emanon.Cli.Services;

namespace Emanon.Tests;

public class GitverseLayoutTests
{
    // ── DefaultValues ─────────────────────────────────────────────────────────

    [Fact]
    public void DefaultValues_ContainsRequiredKeys()
    {
        var defaults = GitverseLayout.DefaultValues();
        Assert.True(defaults.ContainsKey("universe_name"), "missing universe_name");
        Assert.True(defaults.ContainsKey("version"),       "missing version");
        Assert.True(defaults.ContainsKey("snapshot_count"), "missing snapshot_count");
    }

    [Fact]
    public void DefaultValues_SnapshotCount_IsZero()
    {
        var defaults = GitverseLayout.DefaultValues();
        Assert.Equal(0, defaults["snapshot_count"]);
    }

    // ── ReadValues / WriteValues round-trip ───────────────────────────────────

    [Fact]
    public void WriteValues_Then_ReadValues_RoundTrips()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(Path.Combine(tmpDir, ".gitverse"));

        try
        {
            var values = new Dictionary<string, object>
            {
                ["universe_name"]   = "round-trip-test",
                ["version"]         = "1.2.3",
                ["snapshot_count"]  = 42,
            };

            GitverseLayout.WriteValues(tmpDir, values);
            var read = GitverseLayout.ReadValues(tmpDir);

            Assert.NotNull(read);
            Assert.Equal("round-trip-test", read["universe_name"].GetString());
            Assert.Equal(42, read["snapshot_count"].GetInt32());
        }
        finally
        {
            Directory.Delete(tmpDir, recursive: true);
        }
    }

    [Fact]
    public void ReadValues_MissingFile_ReturnsNull()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(tmpDir);

        try
        {
            var result = GitverseLayout.ReadValues(tmpDir);
            Assert.Null(result);
        }
        finally
        {
            Directory.Delete(tmpDir, recursive: true);
        }
    }

    // ── IncrementSnapshotCount ────────────────────────────────────────────────

    [Fact]
    public void IncrementSnapshotCount_StartsAtZero_ReturnsOne()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(Path.Combine(tmpDir, ".gitverse"));

        try
        {
            GitverseLayout.WriteValues(tmpDir, new Dictionary<string, object>
            {
                ["universe_name"]   = "inc-test",
                ["snapshot_count"]  = 0,
            });

            var next = GitverseLayout.IncrementSnapshotCount(tmpDir);
            Assert.Equal(1, next);

            var values = GitverseLayout.ReadValues(tmpDir)!;
            Assert.Equal(1, values["snapshot_count"].GetInt32());
        }
        finally
        {
            Directory.Delete(tmpDir, recursive: true);
        }
    }

    [Fact]
    public void IncrementSnapshotCount_Idempotent_IncreasesMonotonically()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(Path.Combine(tmpDir, ".gitverse"));

        try
        {
            GitverseLayout.WriteValues(tmpDir, new Dictionary<string, object>
            {
                ["universe_name"]   = "mono-test",
                ["snapshot_count"]  = 5,
            });

            var a = GitverseLayout.IncrementSnapshotCount(tmpDir);
            var b = GitverseLayout.IncrementSnapshotCount(tmpDir);
            var c = GitverseLayout.IncrementSnapshotCount(tmpDir);

            Assert.Equal(6, a);
            Assert.Equal(7, b);
            Assert.Equal(8, c);
        }
        finally
        {
            Directory.Delete(tmpDir, recursive: true);
        }
    }

    // ── Constants ─────────────────────────────────────────────────────────────

    [Fact]
    public void RequiredDirs_ContainsGitverseDir()
    {
        Assert.Contains(".gitverse", GitverseLayout.RequiredDirs);
    }

    [Fact]
    public void RequiredDirs_ContainsRegionsDir()
    {
        Assert.Contains("regions", GitverseLayout.RequiredDirs);
    }

    [Fact]
    public void ValuesFile_Constant_HasExpectedPath()
    {
        Assert.Equal(".gitverse/values.json", GitverseLayout.ValuesFile);
    }
}
