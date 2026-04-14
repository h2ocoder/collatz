using System.Text.Json;

namespace Emanon.Cli.Services;

/// <summary>
/// Canonical .gitverse layout helpers — paths, defaults, read/write.
/// </summary>
public static class GitverseLayout
{
    public const string GitverseDir   = ".gitverse";
    public const string ValuesFile    = ".gitverse/values.json";
    public const string IdentityFile  = ".gitverse/identity.key";
    public const string LeverageCache = ".gitverse/leverage.cache";
    public const string RemotesFile   = ".gitverse/remotes.registry";
    public const string PendingMerge  = ".gitverse/pending-merge.json";
    public const string GenesisFile   = ".gitverse/genesis.json";

    public static readonly string[] RequiredDirs =
        ["regions", "contracts", "scars", "forks", GitverseDir];

    public static readonly string DefaultGitAttributes = """
        # Emanon merge drivers
        regions/**   merge=emanon-collatz
        contracts/** merge=emanon-contract
        scars/**     merge=emanon-append-only
        """;

    public static readonly string DefaultGitIgnore = """
        .gitverse/leverage.cache
        .gitverse/identity.key
        obj/
        bin/
        """;

    public static Dictionary<string, object> DefaultValues() => new()
    {
        ["universe_name"]       = "my-universe",
        ["version"]             = "0.1.0",
        ["resolution_priority"] = new[] { "contract", "battle", "fork" },
        ["snapshot_count"]      = 0,
    };

    /// <summary>Read values.json from a repo root. Returns null if not found.</summary>
    public static Dictionary<string, JsonElement>? ReadValues(string repoRoot)
    {
        var path = Path.Combine(repoRoot, ValuesFile);
        if (!File.Exists(path)) return null;
        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
    }

    /// <summary>Write values.json.</summary>
    public static void WriteValues(string repoRoot, object values)
    {
        var path = Path.Combine(repoRoot, ValuesFile);
        var json = JsonSerializer.Serialize(values, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(path, json);
    }

    /// <summary>Increment snapshot_count in values.json and return the new count.</summary>
    public static int IncrementSnapshotCount(string repoRoot)
    {
        var values = ReadValues(repoRoot) ?? new Dictionary<string, JsonElement>();
        int current = values.TryGetValue("snapshot_count", out var el)
            ? el.GetInt32()
            : 0;
        int next = current + 1;

        // Rebuild as a plain dict for serialisation
        var updated = new Dictionary<string, object>();
        foreach (var (k, v) in values)
            updated[k] = v.ValueKind == JsonValueKind.Number ? (object)v.GetInt32() : v.GetString()!;
        updated["snapshot_count"] = next;
        WriteValues(repoRoot, updated);
        return next;
    }
}
