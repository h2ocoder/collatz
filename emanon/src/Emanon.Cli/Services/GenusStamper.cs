using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Emanon.Collatz;

namespace Emanon.Cli.Services;

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
    public static Genus? ReadStamp(string filePath)
    {
        string stampLine = null!;

        var sidecar = filePath + ".genus";
        if (File.Exists(sidecar))
        {
            stampLine = File.ReadAllText(sidecar).Trim();
        }
        else if (File.Exists(filePath))
        {
            var lines = File.ReadAllLines(filePath);
            stampLine = Array.FindLast(lines, l => l.StartsWith(StampPrefix))!;
        }

        if (stampLine == null) return null;

        try
        {
            var json = stampLine[StampPrefix.Length..].Trim();
            var obj  = JsonSerializer.Deserialize<JsonElement>(json);
            return new Genus(
                obj.GetProperty("set_k").GetInt32(),
                obj.GetProperty("oddity_s").GetInt32(),
                obj.GetProperty("index_i").GetInt32()
            );
        }
        catch
        {
            return null;
        }
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
        var obj = new
        {
            set_k    = genus.SetK,
            oddity_s = genus.OddityS,
            index_i  = genus.Index,
            writer,
            snapshot
        };
        return StampPrefix + JsonSerializer.Serialize(obj);
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
