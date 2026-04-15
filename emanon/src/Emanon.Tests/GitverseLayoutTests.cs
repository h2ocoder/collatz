using Emanon.Cli.Services;

namespace Emanon.Tests;

public class GitverseLayoutTests
{
    // ── DefaultValues ─────────────────────────────────────────────────────────

    [Fact]
    public void DefaultValues_HasSensibleDefaults()
    {
        var defaults = GitverseLayout.DefaultValues();
        Assert.Equal("my-universe", defaults.UniverseName);
        Assert.Equal("0.1.0",       defaults.Version);
        Assert.Equal(0,             defaults.SnapshotCount);
        Assert.Null(defaults.RegistryId);
        Assert.Null(defaults.RegistryServer);
    }

    [Fact]
    public void DefaultValues_ResolutionPriorityPopulated()
    {
        var defaults = GitverseLayout.DefaultValues();
        Assert.Equal(["contract", "battle", "fork"], defaults.ResolutionPriority);
    }

    // ── ReadValues / WriteValues round-trip ───────────────────────────────────

    [Fact]
    public void WriteValues_Then_ReadValues_RoundTrips()
    {
        var tmpDir = CreateTempUniverse();
        try
        {
            var values = new GitverseValues
            {
                UniverseName   = "round-trip-test",
                Version        = "1.2.3",
                SnapshotCount  = 42,
                RegistryId     = "universe-abc",
                RegistryServer = "http://localhost:5050",
            };

            GitverseLayout.WriteValues(tmpDir, values);
            var read = GitverseLayout.ReadValues(tmpDir);

            Assert.NotNull(read);
            Assert.Equal("round-trip-test",     read.UniverseName);
            Assert.Equal("1.2.3",               read.Version);
            Assert.Equal(42,                    read.SnapshotCount);
            Assert.Equal("universe-abc",        read.RegistryId);
            Assert.Equal("http://localhost:5050", read.RegistryServer);
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    [Fact]
    public void ReadValues_MissingFile_ReturnsNull()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(tmpDir);
        try
        {
            Assert.Null(GitverseLayout.ReadValues(tmpDir));
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    [Fact]
    public void WriteValues_OmitsNullRegistryFields_ByDefault()
    {
        var tmpDir = CreateTempUniverse();
        try
        {
            GitverseLayout.WriteValues(tmpDir, GitverseLayout.DefaultValues());
            var raw = File.ReadAllText(Path.Combine(tmpDir, GitverseLayout.ValuesFile));
            Assert.DoesNotContain("registry_id", raw);
            Assert.DoesNotContain("registry_server", raw);
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    // ── IncrementSnapshotCount ────────────────────────────────────────────────

    [Fact]
    public void IncrementSnapshotCount_StartsAtZero_ReturnsOne()
    {
        var tmpDir = CreateTempUniverse();
        try
        {
            GitverseLayout.WriteValues(tmpDir, new GitverseValues { UniverseName = "inc-test" });
            Assert.Equal(1, GitverseLayout.IncrementSnapshotCount(tmpDir));
            Assert.Equal(1, GitverseLayout.ReadValues(tmpDir)!.SnapshotCount);
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    [Fact]
    public void IncrementSnapshotCount_IncreasesMonotonically()
    {
        var tmpDir = CreateTempUniverse();
        try
        {
            GitverseLayout.WriteValues(tmpDir, new GitverseValues
            {
                UniverseName  = "mono-test",
                SnapshotCount = 5,
            });

            Assert.Equal(6, GitverseLayout.IncrementSnapshotCount(tmpDir));
            Assert.Equal(7, GitverseLayout.IncrementSnapshotCount(tmpDir));
            Assert.Equal(8, GitverseLayout.IncrementSnapshotCount(tmpDir));
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    [Fact]
    public void UpdateValues_PreservesUnmentionedFields()
    {
        var tmpDir = CreateTempUniverse();
        try
        {
            GitverseLayout.WriteValues(tmpDir, new GitverseValues
            {
                UniverseName  = "preserve-test",
                SnapshotCount = 3,
            });

            GitverseLayout.UpdateValues(tmpDir, v => v with
            {
                RegistryId     = "uid-42",
                RegistryServer = "http://registry.local",
            });

            var read = GitverseLayout.ReadValues(tmpDir)!;
            Assert.Equal("preserve-test",        read.UniverseName);
            Assert.Equal(3,                      read.SnapshotCount);
            Assert.Equal("uid-42",               read.RegistryId);
            Assert.Equal("http://registry.local", read.RegistryServer);
        }
        finally { Directory.Delete(tmpDir, recursive: true); }
    }

    // ── Constants ─────────────────────────────────────────────────────────────

    [Fact]
    public void RequiredDirs_ContainsGitverseDir()
        => Assert.Contains(".gitverse", GitverseLayout.RequiredDirs);

    [Fact]
    public void RequiredDirs_ContainsRegionsDir()
        => Assert.Contains("regions", GitverseLayout.RequiredDirs);

    [Fact]
    public void ValuesFile_Constant_HasExpectedPath()
        => Assert.Equal(".gitverse/values.json", GitverseLayout.ValuesFile);

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static string CreateTempUniverse()
    {
        var tmpDir = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
        Directory.CreateDirectory(Path.Combine(tmpDir, ".gitverse"));
        return tmpDir;
    }
}
