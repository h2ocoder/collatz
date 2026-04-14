using Emanon.Cli.Services;
using Xunit;

namespace Emanon.Tests;

public class GenusStamperTests : IDisposable
{
    private readonly string _tmpDir;

    public GenusStamperTests()
    {
        _tmpDir = Path.Combine(Path.GetTempPath(), "emanon-test-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(_tmpDir);
    }

    public void Dispose() => Directory.Delete(_tmpDir, recursive: true);

    [Fact]
    public void StampFile_AddsStampToTextFile()
    {
        var path = Path.Combine(_tmpDir, "test.txt");
        File.WriteAllText(path, "hello world\n");

        var genus = GenusStamper.StampFile(path, snapshotCount: 1, writerEmail: "test@emanon");

        var content = File.ReadAllText(path);
        Assert.Contains("emanon-genus", content);
        Assert.Contains($"\"set_k\":{genus.SetK}", content);
    }

    [Fact]
    public void ReadStamp_ReturnsGenus_AfterStamping()
    {
        var path = Path.Combine(_tmpDir, "stamped.txt");
        File.WriteAllText(path, "content\n");

        var written = GenusStamper.StampFile(path, 5, "writer@test");
        var read    = GenusStamper.ReadStamp(path);

        Assert.NotNull(read);
        Assert.Equal(written, read!.Value);
    }

    [Fact]
    public void StampFile_ReplacesExistingStamp()
    {
        var path = Path.Combine(_tmpDir, "replace.txt");
        File.WriteAllText(path, "data\n");

        var g1 = GenusStamper.StampFile(path, 1, "a@b");
        var g2 = GenusStamper.StampFile(path, 99, "a@b"); // different snapshot

        var lines = File.ReadAllLines(path);
        int stampCount = lines.Count(l => l.Contains("emanon-genus"));
        Assert.Equal(1, stampCount); // Only one stamp line
    }

    [Fact]
    public void ReadStamp_ReturnsNull_WhenNoStamp()
    {
        var path = Path.Combine(_tmpDir, "nostamp.txt");
        File.WriteAllText(path, "no stamp here\n");

        var result = GenusStamper.ReadStamp(path);
        Assert.Null(result);
    }

    [Fact]
    public void StampFile_IsDeterministic_ForSameSeed()
    {
        var path1 = Path.Combine(_tmpDir, "a.txt");
        var path2 = Path.Combine(_tmpDir, "a.txt"); // Same path
        File.WriteAllText(path1, "content\n");

        var g1 = GenusStamper.StampFile(path1, 3, "x@y");
        File.WriteAllText(path2, "content\n"); // Reset
        var g2 = GenusStamper.StampFile(path2, 3, "x@y");

        Assert.Equal(g1, g2);
    }
}
