using Emanon.Collatz;
using Emanon.Server.Models;
using Emanon.Server.Storage;

namespace Emanon.Server.Endpoints;

/// <summary>
/// Bounty board — post, list, accept, and deliver bounties.
/// </summary>
public static class BountyEndpoints
{
    public static void MapBounties(this WebApplication app)
    {
        var group = app.MapGroup("/api/bounties")
            .WithTags("Bounties");

        // ── List bounties ─────────────────────────────────────────────────────
        group.MapGet("/", (
            InMemoryStore store,
            string? universeId = null,
            string? status = null) =>
        {
            BountyStatus? parsed = null;
            if (status is not null && Enum.TryParse<BountyStatus>(status, true, out var s))
                parsed = s;

            var results = store.AllBounties(universeId, parsed);
            return Results.Ok(results);
        })
        .WithName("ListBounties")
        .WithSummary("List bounties, optionally filtered by universe or status");

        // ── Get bounty ────────────────────────────────────────────────────────
        group.MapGet("/{id}", (string id, InMemoryStore store) =>
        {
            var b = store.GetBounty(id);
            return b is null ? Results.NotFound() : Results.Ok(b);
        })
        .WithName("GetBounty")
        .WithSummary("Get a specific bounty by ID");

        // ── Post bounty ───────────────────────────────────────────────────────
        group.MapPost("/", (PostBountyRequest req, InMemoryStore store) =>
        {
            if (string.IsNullOrWhiteSpace(req.Title))
                return Results.BadRequest("Title is required.");
            if (string.IsNullOrWhiteSpace(req.UniverseId))
                return Results.BadRequest("UniverseId is required.");
            if (store.GetUniverse(req.UniverseId) is null)
                return Results.BadRequest($"Universe '{req.UniverseId}' not found.");
            if (req.RewardUsdc < 0)
                return Results.BadRequest("Reward must be non-negative.");

            var bounty = store.Add(new Bounty
            {
                UniverseId  = req.UniverseId,
                PostedBy    = req.PostedBy,
                Title       = req.Title,
                Description = req.Description,
                Predicate   = req.Predicate,
                RewardUsdc  = req.RewardUsdc,
            });

            return Results.Created($"/api/bounties/{bounty.Id}", bounty);
        })
        .WithName("PostBounty")
        .WithSummary("Post a new bounty against a universe");

        // ── Accept bounty ─────────────────────────────────────────────────────
        group.MapPost("/{id}/accept", (
            string id,
            AcceptBountyRequest req,
            InMemoryStore store) =>
        {
            var b = store.GetBounty(id);
            if (b is null) return Results.NotFound();
            if (b.Status != BountyStatus.Open)
                return Results.Conflict($"Bounty is already {b.Status}.");

            b.Status     = BountyStatus.Accepted;
            b.AcceptedBy = req.AcceptedBy;
            store.UpdateBounty(b);
            return Results.Ok(b);
        })
        .WithName("AcceptBounty")
        .WithSummary("Accept a bounty — claim it for delivery");

        // ── Deliver bounty ────────────────────────────────────────────────────
        group.MapPost("/{id}/deliver", (
            string id,
            DeliverBountyRequest req,
            InMemoryStore store) =>
        {
            var b = store.GetBounty(id);
            if (b is null) return Results.NotFound();
            if (b.Status != BountyStatus.Accepted)
                return Results.Conflict($"Bounty must be Accepted before delivery (current: {b.Status}).");
            if (!b.AcceptedBy!.Equals(req.DeliveredBy, StringComparison.OrdinalIgnoreCase))
                return Results.StatusCode(403);

            // Validate delivery proof (genus stamp)
            Genus? genus = null;
            try { genus = Genus.Parse(req.DeliveryProof); }
            catch { return Results.BadRequest("DeliveryProof must be a valid genus stamp."); }

            // Basic predicate evaluation — check set_k threshold if predicate specifies one
            var predicateResult = EvaluatePredicate(b.Predicate, genus.Value);
            if (!predicateResult.Pass)
                return Results.UnprocessableEntity(new
                {
                    error   = "Predicate not satisfied",
                    details = predicateResult.Reason
                });

            b.Status        = BountyStatus.Delivered;
            b.DeliveryProof = req.DeliveryProof;
            store.UpdateBounty(b);
            return Results.Ok(b);
        })
        .WithName("DeliverBounty")
        .WithSummary("Submit delivery proof for an accepted bounty");
    }

    // ── Predicate evaluation (simple MVP) ────────────────────────────────────

    private record PredicateResult(bool Pass, string Reason);

    private static PredicateResult EvaluatePredicate(string predicate, Genus genus)
    {
        // Predicate format: "field:op:value" or free-form (pass-through for MVP)
        // Examples:
        //   "genus.set_k >= 50"
        //   "genus.oddity_s == 0"
        //   "" (empty = always pass)
        if (string.IsNullOrWhiteSpace(predicate))
            return new(true, "No predicate");

        // Try parsing "genus.set_k >= N"
        var parts = predicate.Trim().Split(' ');
        if (parts.Length == 3)
        {
            var field = parts[0].ToLower();
            var op    = parts[1];
            if (int.TryParse(parts[2], out int threshold))
            {
                int actual = field switch
                {
                    "genus.set_k"    => genus.SetK,
                    "genus.oddity_s" => genus.OddityS,
                    "genus.index"    => genus.Index,
                    _                => -1
                };

                if (actual >= 0)
                {
                    bool pass = op switch
                    {
                        ">="  => actual >= threshold,
                        ">"   => actual > threshold,
                        "<="  => actual <= threshold,
                        "<"   => actual < threshold,
                        "=="  => actual == threshold,
                        "!="  => actual != threshold,
                        _     => true // unknown op → pass
                    };
                    return pass
                        ? new(true,  $"{field}={actual} satisfies {op} {threshold}")
                        : new(false, $"{field}={actual} does not satisfy {op} {threshold}");
                }
            }
        }

        // Unrecognised predicate format → pass with a warning in the reason
        return new(true, $"Predicate '{predicate}' not evaluated (unsupported format, passing)");
    }
}
