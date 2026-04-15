using System.Text.Json;
using System.Text.Json.Serialization;

namespace Emanon.Cli.Services;

/// <summary>Typed model of <c>.gitverse/values.json</c>.</summary>
public sealed record GitverseValues
{
    [JsonPropertyName("universe_name")]
    public string UniverseName { get; init; } = "my-universe";

    [JsonPropertyName("version")]
    public string Version { get; init; } = "0.1.0";

    [JsonPropertyName("resolution_priority")]
    public string[] ResolutionPriority { get; init; } = ["contract", "battle", "fork"];

    [JsonPropertyName("snapshot_count")]
    public int SnapshotCount { get; init; }

    /// <summary>Server-assigned universe ID (set by first <c>registry push</c>).</summary>
    [JsonPropertyName("registry_id")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? RegistryId { get; init; }

    /// <summary>Registry server URL this universe pushes to.</summary>
    [JsonPropertyName("registry_server")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? RegistryServer { get; init; }
}

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

    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public static GitverseValues DefaultValues() => new();

    /// <summary>Read values.json from a repo root. Returns null if not found.</summary>
    public static GitverseValues? ReadValues(string repoRoot)
    {
        var path = Path.Combine(repoRoot, ValuesFile);
        if (!File.Exists(path)) return null;
        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<GitverseValues>(json, JsonOpts);
    }

    /// <summary>Write values.json.</summary>
    public static void WriteValues(string repoRoot, GitverseValues values)
    {
        var path = Path.Combine(repoRoot, ValuesFile);
        var json = JsonSerializer.Serialize(values, JsonOpts);
        File.WriteAllText(path, json);
    }

    /// <summary>
    /// Read values.json, apply an immutable update, write it back, return the new value.
    /// Creates the file with defaults if missing.
    /// </summary>
    public static GitverseValues UpdateValues(string repoRoot, Func<GitverseValues, GitverseValues> mutate)
    {
        var current = ReadValues(repoRoot) ?? DefaultValues();
        var next = mutate(current);
        WriteValues(repoRoot, next);
        return next;
    }

    /// <summary>Increment snapshot_count in values.json and return the new count.</summary>
    public static int IncrementSnapshotCount(string repoRoot)
        => UpdateValues(repoRoot, v => v with { SnapshotCount = v.SnapshotCount + 1 }).SnapshotCount;
}
