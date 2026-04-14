using System.Net;
using System.Net.Http.Json;
using Emanon.Server.Models;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Emanon.Tests;

public class RegistryApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public RegistryApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    // ── /health ───────────────────────────────────────────────────────────────

    [Fact]
    public async Task Health_Returns200()
    {
        var response = await _client.GetAsync("/health");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    // ── GET /api/registry/universes ───────────────────────────────────────────

    [Fact]
    public async Task ListUniverses_EmptyStore_ReturnsEmptyArray()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();
        var list    = await client.GetFromJsonAsync<Universe[]>("/api/registry/universes");
        Assert.NotNull(list);
        // Fresh factory = fresh InMemoryStore, should be empty
        Assert.Empty(list);
    }

    // ── POST /api/registry/universes ──────────────────────────────────────────

    [Fact]
    public async Task Register_ValidRequest_Returns201()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var req = new RegisterUniverseRequest(
            Name: "test-universe",
            OwnerEmail: "owner@test.com",
            GitUrl: "https://github.com/owner/test-universe");

        var response = await client.PostAsJsonAsync("/api/registry/universes", req);
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var u = await response.Content.ReadFromJsonAsync<Universe>();
        Assert.NotNull(u);
        Assert.Equal("test-universe", u.Name);
        Assert.NotNull(u.Id);
    }

    [Fact]
    public async Task Register_MissingName_Returns400()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var req = new RegisterUniverseRequest(
            Name: "",
            OwnerEmail: "owner@test.com",
            GitUrl: "https://github.com/owner/test");

        var response = await client.PostAsJsonAsync("/api/registry/universes", req);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task Register_Duplicate_Returns409()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var req = new RegisterUniverseRequest(
            Name: "dup-universe",
            OwnerEmail: "owner@test.com",
            GitUrl: "https://github.com/owner/dup");

        var first  = await client.PostAsJsonAsync("/api/registry/universes", req);
        var second = await client.PostAsJsonAsync("/api/registry/universes", req);

        Assert.Equal(HttpStatusCode.Created,  first.StatusCode);
        Assert.Equal(HttpStatusCode.Conflict, second.StatusCode);
    }

    // ── GET /api/registry/universes/{id} ──────────────────────────────────────

    [Fact]
    public async Task GetUniverse_NotFound_Returns404()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var response = await client.GetAsync("/api/registry/universes/nonexistent");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    [Fact]
    public async Task GetUniverse_AfterRegister_Returns200()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var req = new RegisterUniverseRequest("find-me", "a@b.com", "https://git.example.com/find-me");
        var created = await (await client.PostAsJsonAsync("/api/registry/universes", req))
                           .Content.ReadFromJsonAsync<Universe>();

        var response = await client.GetAsync($"/api/registry/universes/{created!.Id}");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var u = await response.Content.ReadFromJsonAsync<Universe>();
        Assert.Equal("find-me", u!.Name);
    }

    // ── POST /api/registry/universes/{id}/push ────────────────────────────────

    [Fact]
    public async Task Push_ValidGenus_Returns200()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var reg = new RegisterUniverseRequest("push-test", "a@b.com", "https://git.example.com/push");
        var u   = await (await client.PostAsJsonAsync("/api/registry/universes", reg))
                       .Content.ReadFromJsonAsync<Universe>();

        var pushReq = new PushUniverseRequest(
            UniverseId:    u!.Id,
            SnapshotCount: 1,
            HeadGenus:     "set_k=17 oddity_s=3 index_i=17",
            OwnerEmail:    "a@b.com");

        var response = await client.PostAsJsonAsync($"/api/registry/universes/{u.Id}/push", pushReq);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var updated = await response.Content.ReadFromJsonAsync<Universe>();
        Assert.Equal(1, updated!.SnapshotCount);
        Assert.Equal("set_k=17 oddity_s=3 index_i=17", updated.HeadGenus);
    }

    [Fact]
    public async Task Push_InvalidGenus_Returns400()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var reg = new RegisterUniverseRequest("bad-push", "a@b.com", "https://git.example.com/bp");
        var u   = await (await client.PostAsJsonAsync("/api/registry/universes", reg))
                       .Content.ReadFromJsonAsync<Universe>();

        var pushReq = new PushUniverseRequest(
            UniverseId:    u!.Id,
            SnapshotCount: 1,
            HeadGenus:     "this-is-not-a-genus",
            OwnerEmail:    "a@b.com");

        var response = await client.PostAsJsonAsync($"/api/registry/universes/{u.Id}/push", pushReq);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    // ── GET /api/registry/universes/{id}/pull ────────────────────────────────

    [Fact]
    public async Task Pull_AfterPush_ReturnsCurrentState()
    {
        var factory = new WebApplicationFactory<Program>();
        var client  = factory.CreateClient();

        var reg = new RegisterUniverseRequest("pull-test", "a@b.com", "https://git.example.com/pull");
        var u   = await (await client.PostAsJsonAsync("/api/registry/universes", reg))
                       .Content.ReadFromJsonAsync<Universe>();

        var pushReq = new PushUniverseRequest(u!.Id, 3, "set_k=7 oddity_s=1 index_i=7", "a@b.com");
        await client.PostAsJsonAsync($"/api/registry/universes/{u.Id}/push", pushReq);

        var response = await client.GetAsync($"/api/registry/universes/{u.Id}/pull");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var state = await response.Content.ReadFromJsonAsync<Universe>();
        Assert.Equal(3, state!.SnapshotCount);
        Assert.Equal("set_k=7 oddity_s=1 index_i=7", state.HeadGenus);
    }
}
