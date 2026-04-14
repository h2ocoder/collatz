using Emanon.Collatz;
using Emanon.Server.Models;
using Emanon.Server.Storage;

namespace Emanon.Server.Endpoints;

/// <summary>
/// Universe registry — central authority for Emanon universes.
/// </summary>
public static class RegistryEndpoints
{
    public static void MapRegistry(this WebApplication app)
    {
        var group = app.MapGroup("/api/registry")
            .WithTags("Registry");

        // ── List all universes ────────────────────────────────────────────────
        group.MapGet("/universes", (InMemoryStore store) =>
        {
            var all = store.AllUniverses();
            return Results.Ok(all);
        })
        .WithName("ListUniverses")
        .WithSummary("List all registered universes");

        // ── Get universe by id ────────────────────────────────────────────────
        group.MapGet("/universes/{id}", (string id, InMemoryStore store) =>
        {
            var u = store.GetUniverse(id);
            return u is null ? Results.NotFound() : Results.Ok(u);
        })
        .WithName("GetUniverse")
        .WithSummary("Get a universe by ID");

        // ── Register a new universe ───────────────────────────────────────────
        group.MapPost("/universes", (RegisterUniverseRequest req, InMemoryStore store) =>
        {
            if (string.IsNullOrWhiteSpace(req.Name))
                return Results.BadRequest("Name is required.");
            if (string.IsNullOrWhiteSpace(req.OwnerEmail))
                return Results.BadRequest("OwnerEmail is required.");

            // Reject duplicates
            if (store.FindUniverseByName(req.Name) is not null)
                return Results.Conflict($"Universe '{req.Name}' already registered.");

            var universe = store.Add(new Universe
            {
                Name        = req.Name.Trim(),
                OwnerEmail  = req.OwnerEmail.Trim(),
                GitUrl      = req.GitUrl.Trim(),
                Description = req.Description.Trim(),
            });

            return Results.Created($"/api/registry/universes/{universe.Id}", universe);
        })
        .WithName("RegisterUniverse")
        .WithSummary("Register a new universe with the central authority");

        // ── Push (update snapshot/genus) ─────────────────────────────────────
        group.MapPost("/universes/{id}/push", (
            string id,
            PushUniverseRequest req,
            InMemoryStore store) =>
        {
            var u = store.GetUniverse(id);
            if (u is null)
                return Results.NotFound();
            if (!u.OwnerEmail.Equals(req.OwnerEmail, StringComparison.OrdinalIgnoreCase))
                return Results.Forbid();

            // Validate genus stamp
            try
            {
                var genus = Genus.Parse(req.HeadGenus);
                u.HeadGenus     = genus.ToString();
            }
            catch
            {
                return Results.BadRequest("Invalid HeadGenus format.");
            }

            u.SnapshotCount = req.SnapshotCount;
            store.UpdateUniverse(u);

            return Results.Ok(u);
        })
        .WithName("PushUniverse")
        .WithSummary("Update universe head genus after a snapshot push");

        // ── Pull (get current state) ──────────────────────────────────────────
        group.MapGet("/universes/{id}/pull", (string id, InMemoryStore store) =>
        {
            var u = store.GetUniverse(id);
            return u is null ? Results.NotFound() : Results.Ok(new
            {
                u.Id,
                u.Name,
                u.HeadGenus,
                u.SnapshotCount,
                u.UpdatedAt
            });
        })
        .WithName("PullUniverse")
        .WithSummary("Pull current universe state");
    }
}
