using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Emanon.Collatz;

namespace Emanon.Cli.Services;

/// <summary>
/// Serialised form of an on-file genus stamp.
///
/// The optional <c>Displaced*</c> fields form an audit trail: when a merge
/// driver resolves a conflict in favour of this stamp, it records the losing
/// side's genus + writer here so the decision is visible in the merged file
/// itself (since git discards merge-driver stdout).
/// </summary>
public sealed record GenusStamp(
    [property: JsonPropertyName("set_k")]    int SetK,
    [property: JsonPropertyName("oddity_s")] int OddityS,
    [property: JsonPropertyName("index_i")]  int Index,
    [property: JsonPropertyName("writer")]   string Writer,
    [property: JsonPropertyName("snapshot")] int Snapshot,

    [property: JsonPropertyName("displaced_set_k"),
               JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    int? DisplacedSetK = null,

    [property: JsonPropertyName("displaced_oddity_s"),
               JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    int? DisplacedOddityS = null,

    [property: JsonPropertyName("displaced_index_i"),
               JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    int? DisplacedIndex = null,

    [property: JsonPropertyName("displaced_writer"),
               JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    string? DisplacedWriter = null)
{
    public Genus ToGenus() => new(SetK, OddityS, Index);

    public Genus? DisplacedGenus =>
        DisplacedSetK is int k && DisplacedOddityS is int s && DisplacedIndex is int i
            ? new Genus(k, s, i)
            : null;
}

/// <summary>
/// Attaches and reads Collatz genus stamps on files.
/// Text files: stamp appended as a comment line at the end.
/// Binary files: stamp written to a .genus sidecar file.
/// </summary>
public static class GenusStamper
{
    private const string StampPrefix = "# emanon-genus: ";

    /// <summary>
    /// Compute a genus for a file path + snapshot count combo, then write
    /// the stamp into the file (or sidecar). Returns the computed genus.
    /// </summary>
    public static Genus StampFile(string filePath, int snapshotCount, string writerEmail)
    {
        ulong seed = ComputeSeed(filePath, snapshotCount);
        var genus = CollatzMath.DroppingGenusFromSeed(seed);
        var stamp = BuildStamp(genus, writerEmail, snapshotCount);

        if (IsBinary(filePath))
        {
            File.WriteAllText(filePath + ".genus", stamp);
        }
        else
        {
            AppendOrReplaceStamp(filePath, stamp);
        }

        return genus;
    }

    /// <summary>Read the genus stamp from a file (or its sidecar). Returns null if absent.</summary>
    public static Genus? ReadStamp(string filePath) => ReadFullStamp(filePath)?.ToGenus();

    /// <summary>
    /// Read the full stamp record from a file (or its sidecar), including any
    /// displacement audit fields. Returns null if no stamp is present.
    /// </summary>
    public static GenusStamp? ReadFullStamp(string filePath)
    {
        string? stampLine = null;
        var sidecar = filePath + ".genus";
        if (File.Exists(sidecar))
        {
            stampLine = File.ReadAllText(sidecar).Trim();
        }
        else if (File.Exists(filePath))
        {
            var lines = File.ReadAllLines(filePath);
            stampLine = Array.FindLast(lines, l => l.StartsWith(StampPrefix));
        }
        return stampLine is null ? null : ParseStampLine(stampLine);
    }

    // -------------------------------------------------------------------------

    private static ulong ComputeSeed(string filePath, int snapshotCount)
    {
        var bytes = Encoding.UTF8.GetBytes(filePath);
        var hash  = SHA256.HashData(bytes);
        ulong pathLow = BitConverter.ToUInt64(hash, 0);
        return (ulong)snapshotCount + (pathLow & 0xFFFF);
    }

    private static string BuildStamp(Genus genus, string writer, int snapshot)
    {
        var stamp = new GenusStamp(genus.SetK, genus.OddityS, genus.Index, writer, snapshot);
        return StampPrefix + JsonSerializer.Serialize(stamp);
    }

    /// <summary>
    /// Read a text file that already carries a stamp, produce new file content
    /// where the stamp line is replaced with an enriched version carrying the
    /// given displacement audit fields. Does NOT write anything — caller is
    /// responsible for durable write (see MergeDriverCommand for an atomic
    /// temp-file pattern).
    /// </summary>
    /// <returns>The enriched content, or null if the source file has no stamp.</returns>
    public static string? BuildContentWithDisplacement(
        string sourceFilePath,
        Genus displacedGenus,
        string displacedWriter)
    {
        if (!File.Exists(sourceFilePath)) return null;
        var lines = File.ReadAllLines(sourceFilePath).ToList();
        int idx = lines.FindLastIndex(l => l.StartsWith(StampPrefix));
        if (idx < 0) return null;

        var existing = ParseStampLine(lines[idx]);
        if (existing is null) return null;

        var enriched = existing with
        {
            DisplacedSetK    = displacedGenus.SetK,
            DisplacedOddityS = displacedGenus.OddityS,
            DisplacedIndex   = displacedGenus.Index,
            DisplacedWriter  = displacedWriter,
        };
        lines[idx] = StampPrefix + JsonSerializer.Serialize(enriched);
        return string.Join(Environment.NewLine, lines) + Environment.NewLine;
    }

    private static GenusStamp? ParseStampLine(string stampLine)
    {
        try
        {
            var json = stampLine[StampPrefix.Length..].Trim();
            return JsonSerializer.Deserialize<GenusStamp>(json);
        }
        catch { return null; }
    }

    private static void AppendOrReplaceStamp(string filePath, string stamp)
    {
        if (!File.Exists(filePath))
        {
            File.WriteAllText(filePath, stamp + Environment.NewLine);
            return;
        }

        var lines    = File.ReadAllLines(filePath).ToList();
        int existing = lines.FindLastIndex(l => l.StartsWith(StampPrefix));
        if (existing >= 0)
            lines[existing] = stamp;
        else
            lines.Add(stamp);

        File.WriteAllLines(filePath, lines);
    }

    private static bool IsBinary(string filePath)
    {
        if (!File.Exists(filePath)) return false;
        // Read first 8KB — if there are null bytes, treat as binary
        var buffer = new byte[8192];
        using var fs = File.OpenRead(filePath);
        int read = fs.Read(buffer, 0, buffer.Length);
        return Array.IndexOf(buffer, (byte)0, 0, read) >= 0;
    }
}
