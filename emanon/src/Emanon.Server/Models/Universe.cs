namespace Emanon.Server.Models;

/// <summary>
/// Represents a registered Emanon universe in the central authority.
/// </summary>
public class Universe
{
    public string Id          { get; init; } = Guid.NewGuid().ToString("N")[..12];
    public string Name        { get; set; } = "";
    public string OwnerEmail  { get; set; } = "";
    public string GitUrl      { get; set; } = "";
    public string Description { get; set; } = "";
    public int    Version     { get; set; } = 1;
    public int    SnapshotCount { get; set; } = 0;
    public string CreatedAt   { get; init; } = DateTime.UtcNow.ToString("O");
    public string UpdatedAt   { get; set; } = DateTime.UtcNow.ToString("O");

    /// <summary>Genus stamp of the universe head (set on push).</summary>
    public string? HeadGenus  { get; set; }
}

public record RegisterUniverseRequest(
    string Name,
    string OwnerEmail,
    string GitUrl,
    string Description = "");

public record PushUniverseRequest(
    string UniverseId,
    int    SnapshotCount,
    string HeadGenus,
    string OwnerEmail);
