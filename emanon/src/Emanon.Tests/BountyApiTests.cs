using System.Net;
using System.Net.Http.Json;
using Emanon.Server.Models;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Emanon.Tests;

public class BountyApiTests
{
    // Each test gets a fresh factory so state doesn't leak between tests
    private static (WebApplicationFactory<Program> factory, HttpClient client) Fresh()
    {
        var factory = new WebApplicationFactory<Program>();
        return (factory, factory.CreateClient());
    }

    private static async Task<Universe> RegisterUniverse(HttpClient client, string name = "bounty-universe")
    {
        var req = new RegisterUniverseRequest(name, "a@b.com", "https://git.example.com/" + name);
        var response = await client.PostAsJsonAsync("/api/registry/universes", req);
        return (await response.Content.ReadFromJsonAsync<Universe>())!;
    }

    // ── List bounties ─────────────────────────────────────────────────────────

    [Fact]
    public async Task ListBounties_Empty_ReturnsEmptyArray()
    {
        var (_, client) = Fresh();
        var list = await client.GetFromJsonAsync<Bounty[]>("/api/bounties");
        Assert.NotNull(list);
        Assert.Empty(list);
    }

    // ── Post bounty ───────────────────────────────────────────────────────────

    [Fact]
    public async Task PostBounty_ValidRequest_Returns201()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var req = new PostBountyRequest(
            UniverseId:  u.Id,
            PostedBy:    "alice",
            Title:       "Find the hero",
            Description: "Search in regions/main/",
            Predicate:   "genus.set_k >= 50",
            RewardUsdc:  100m);

        var response = await client.PostAsJsonAsync("/api/bounties", req);
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var b = await response.Content.ReadFromJsonAsync<Bounty>();
        Assert.NotNull(b);
        Assert.Equal(BountyStatus.Open, b.Status);
        Assert.Equal("Find the hero", b.Title);
    }

    [Fact]
    public async Task PostBounty_MissingTitle_Returns400()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var req = new PostBountyRequest(u.Id, "alice", "", "desc", "", 10m);
        var response = await client.PostAsJsonAsync("/api/bounties", req);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task PostBounty_UnknownUniverse_Returns400()
    {
        var (_, client) = Fresh();
        var req = new PostBountyRequest("nonexistent-id", "alice", "title", "desc", "", 10m);
        var response = await client.PostAsJsonAsync("/api/bounties", req);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    // ── Accept bounty ─────────────────────────────────────────────────────────

    [Fact]
    public async Task AcceptBounty_OpenBounty_Returns200()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b!.Id}/accept",
            new AcceptBountyRequest("bob"));

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var accepted = await response.Content.ReadFromJsonAsync<Bounty>();
        Assert.Equal(BountyStatus.Accepted, accepted!.Status);
        Assert.Equal("bob", accepted.AcceptedBy);
    }

    [Fact]
    public async Task AcceptBounty_AlreadyAccepted_Returns409()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        await client.PostAsJsonAsync($"/api/bounties/{b!.Id}/accept", new AcceptBountyRequest("bob"));
        var response = await client.PostAsJsonAsync($"/api/bounties/{b.Id}/accept", new AcceptBountyRequest("carol"));

        Assert.Equal(HttpStatusCode.Conflict, response.StatusCode);
    }

    [Fact]
    public async Task AcceptBounty_NotFound_Returns404()
    {
        var (_, client) = Fresh();
        var response = await client.PostAsJsonAsync("/api/bounties/ghost/accept", new AcceptBountyRequest("x"));
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    // ── Deliver bounty ────────────────────────────────────────────────────────

    [Fact]
    public async Task DeliverBounty_PredicateSatisfied_Returns200()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "genus.set_k >= 50", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        await client.PostAsJsonAsync($"/api/bounties/{b!.Id}/accept", new AcceptBountyRequest("bob"));

        // set_k=55 satisfies >= 50
        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b.Id}/deliver",
            new DeliverBountyRequest("set_k=55 oddity_s=3 index_i=55", "bob"));

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var delivered = await response.Content.ReadFromJsonAsync<Bounty>();
        Assert.Equal(BountyStatus.Delivered, delivered!.Status);
    }

    [Fact]
    public async Task DeliverBounty_PredicateNotSatisfied_Returns422()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "genus.set_k >= 50", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        await client.PostAsJsonAsync($"/api/bounties/{b!.Id}/accept", new AcceptBountyRequest("bob"));

        // set_k=10 does NOT satisfy >= 50
        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b.Id}/deliver",
            new DeliverBountyRequest("set_k=10 oddity_s=1 index_i=10", "bob"));

        Assert.Equal(HttpStatusCode.UnprocessableEntity, response.StatusCode);
    }

    [Fact]
    public async Task DeliverBounty_BadGenus_Returns400()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        await client.PostAsJsonAsync($"/api/bounties/{b!.Id}/accept", new AcceptBountyRequest("bob"));

        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b.Id}/deliver",
            new DeliverBountyRequest("not-a-genus", "bob"));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task DeliverBounty_WrongDeliverer_Returns403()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        await client.PostAsJsonAsync($"/api/bounties/{b!.Id}/accept", new AcceptBountyRequest("bob"));

        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b.Id}/deliver",
            new DeliverBountyRequest("set_k=5 oddity_s=1 index_i=5", "NOT-bob"));

        Assert.Equal(HttpStatusCode.Forbidden, response.StatusCode);
    }

    [Fact]
    public async Task DeliverBounty_NotAccepted_Returns409()
    {
        var (_, client) = Fresh();
        var u = await RegisterUniverse(client);

        var b = await (await client.PostAsJsonAsync("/api/bounties",
                    new PostBountyRequest(u.Id, "alice", "title", "desc", "", 5m)))
                   .Content.ReadFromJsonAsync<Bounty>();

        // Skip accept step — try to deliver directly
        var response = await client.PostAsJsonAsync(
            $"/api/bounties/{b!.Id}/deliver",
            new DeliverBountyRequest("set_k=5 oddity_s=1 index_i=5", "alice"));

        Assert.Equal(HttpStatusCode.Conflict, response.StatusCode);
    }
}
