using System.Collections.Concurrent;
using Emanon.Server.Models;

namespace Emanon.Server.Storage;

/// <summary>
/// Simple in-memory store for MVP. Swap for EF Core / SQLite when persistence is needed.
/// </summary>
public class InMemoryStore
{
    private readonly ConcurrentDictionary<string, Universe> _universes = new();
    private readonly ConcurrentDictionary<string, Bounty>   _bounties  = new();

    // ── Universe ─────────────────────────────────────────────────────────────

    public Universe Add(Universe u)
    {
        _universes[u.Id] = u;
        return u;
    }

    public Universe? GetUniverse(string id) =>
        _universes.TryGetValue(id, out var u) ? u : null;

    public Universe? FindUniverseByName(string name) =>
        _universes.Values.FirstOrDefault(u =>
            u.Name.Equals(name, StringComparison.OrdinalIgnoreCase));

    public IReadOnlyList<Universe> AllUniverses() =>
        _universes.Values.OrderBy(u => u.CreatedAt).ToList();

    public bool UpdateUniverse(Universe u)
    {
        if (!_universes.ContainsKey(u.Id)) return false;
        u.UpdatedAt = DateTime.UtcNow.ToString("O");
        _universes[u.Id] = u;
        return true;
    }

    // ── Bounty ───────────────────────────────────────────────────────────────

    public Bounty Add(Bounty b)
    {
        _bounties[b.Id] = b;
        return b;
    }

    public Bounty? GetBounty(string id) =>
        _bounties.TryGetValue(id, out var b) ? b : null;

    public IReadOnlyList<Bounty> AllBounties(
        string? universeId = null,
        BountyStatus? status = null)
    {
        var q = _bounties.Values.AsEnumerable();
        if (universeId != null) q = q.Where(b => b.UniverseId == universeId);
        if (status != null)     q = q.Where(b => b.Status == status);
        return q.OrderByDescending(b => b.CreatedAt).ToList();
    }

    public bool UpdateBounty(Bounty b)
    {
        if (!_bounties.ContainsKey(b.Id)) return false;
        b.UpdatedAt = DateTime.UtcNow.ToString("O");
        _bounties[b.Id] = b;
        return true;
    }
}
