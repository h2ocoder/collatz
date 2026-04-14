using Emanon.Server.Models;
using Emanon.Server.Storage;

namespace Emanon.Tests;

public class InMemoryStoreTests
{
    // ── Universe ─────────────────────────────────────────────────────────────

    [Fact]
    public void Add_And_GetUniverse_RoundTrips()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "alpha", OwnerEmail = "a@b.com", GitUrl = "https://git.example.com/alpha" };
        store.Add(u);

        var result = store.GetUniverse(u.Id);
        Assert.NotNull(result);
        Assert.Equal("alpha", result.Name);
    }

    [Fact]
    public void GetUniverse_MissingId_ReturnsNull()
    {
        var store = new InMemoryStore();
        Assert.Null(store.GetUniverse("does-not-exist"));
    }

    [Fact]
    public void FindUniverseByName_CaseInsensitive()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "MyUniverse" };
        store.Add(u);

        Assert.NotNull(store.FindUniverseByName("MYUNIVERSE"));
        Assert.NotNull(store.FindUniverseByName("myuniverse"));
        Assert.Null(store.FindUniverseByName("other"));
    }

    [Fact]
    public void AllUniverses_ReturnsAll()
    {
        var store = new InMemoryStore();
        store.Add(new Universe { Name = "u1" });
        store.Add(new Universe { Name = "u2" });
        store.Add(new Universe { Name = "u3" });

        Assert.Equal(3, store.AllUniverses().Count);
    }

    [Fact]
    public void UpdateUniverse_PersistsChanges()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "original" };
        store.Add(u);

        u.Name = "updated";
        var ok = store.UpdateUniverse(u);

        Assert.True(ok);
        Assert.Equal("updated", store.GetUniverse(u.Id)!.Name);
    }

    [Fact]
    public void UpdateUniverse_UnknownId_ReturnsFalse()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "ghost" };
        // never added
        Assert.False(store.UpdateUniverse(u));
    }

    // ── Bounty ───────────────────────────────────────────────────────────────

    [Fact]
    public void Add_And_GetBounty_RoundTrips()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "u1" };
        store.Add(u);

        var b = new Bounty { UniverseId = u.Id, Title = "Find the hero" };
        store.Add(b);

        var result = store.GetBounty(b.Id);
        Assert.NotNull(result);
        Assert.Equal("Find the hero", result.Title);
    }

    [Fact]
    public void GetBounty_MissingId_ReturnsNull()
    {
        var store = new InMemoryStore();
        Assert.Null(store.GetBounty("nope"));
    }

    [Fact]
    public void AllBounties_FilterByUniverseId()
    {
        var store = new InMemoryStore();
        var u1 = new Universe { Name = "u1" }; store.Add(u1);
        var u2 = new Universe { Name = "u2" }; store.Add(u2);

        store.Add(new Bounty { UniverseId = u1.Id, Title = "A" });
        store.Add(new Bounty { UniverseId = u1.Id, Title = "B" });
        store.Add(new Bounty { UniverseId = u2.Id, Title = "C" });

        var results = store.AllBounties(universeId: u1.Id);
        Assert.Equal(2, results.Count);
        Assert.All(results, b => Assert.Equal(u1.Id, b.UniverseId));
    }

    [Fact]
    public void AllBounties_FilterByStatus()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "u" }; store.Add(u);

        store.Add(new Bounty { UniverseId = u.Id, Title = "open1", Status = BountyStatus.Open });
        store.Add(new Bounty { UniverseId = u.Id, Title = "open2", Status = BountyStatus.Open });
        store.Add(new Bounty { UniverseId = u.Id, Title = "accepted", Status = BountyStatus.Accepted });

        Assert.Equal(2, store.AllBounties(status: BountyStatus.Open).Count);
        Assert.Single(store.AllBounties(status: BountyStatus.Accepted));
    }

    [Fact]
    public void UpdateBounty_PersistsStatusChange()
    {
        var store = new InMemoryStore();
        var u = new Universe { Name = "u" }; store.Add(u);
        var b = new Bounty { UniverseId = u.Id, Title = "t" };
        store.Add(b);

        b.Status     = BountyStatus.Accepted;
        b.AcceptedBy = "alice";
        var ok = store.UpdateBounty(b);

        Assert.True(ok);
        var updated = store.GetBounty(b.Id)!;
        Assert.Equal(BountyStatus.Accepted, updated.Status);
        Assert.Equal("alice", updated.AcceptedBy);
    }

    [Fact]
    public void UpdateBounty_UnknownId_ReturnsFalse()
    {
        var store = new InMemoryStore();
        var b = new Bounty { UniverseId = "ghost", Title = "ghost" };
        Assert.False(store.UpdateBounty(b));
    }
}
