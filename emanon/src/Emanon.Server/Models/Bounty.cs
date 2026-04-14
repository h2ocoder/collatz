namespace Emanon.Server.Models;

/// <summary>
/// A bounty posted against a universe — a request for work with an escrow reward.
/// </summary>
public class Bounty
{
    public string Id          { get; init; } = Guid.NewGuid().ToString("N")[..12];
    public string UniverseId  { get; set; } = "";
    public string PostedBy    { get; set; } = "";
    public string Title       { get; set; } = "";
    public string Description { get; set; } = "";
    public string Predicate   { get; set; } = ""; // e.g. "regions/main/hero.txt:genus.set_k >= 50"
    public decimal RewardUsdc { get; set; } = 0;
    public BountyStatus Status { get; set; } = BountyStatus.Open;
    public string? AcceptedBy { get; set; }
    public string? DeliveryProof { get; set; } // genus stamp of delivered file
    public string CreatedAt   { get; init; } = DateTime.UtcNow.ToString("O");
    public string UpdatedAt   { get; set; } = DateTime.UtcNow.ToString("O");
}

public enum BountyStatus { Open, Accepted, Delivered, Verified, Cancelled }

public record PostBountyRequest(
    string  UniverseId,
    string  PostedBy,
    string  Title,
    string  Description,
    string  Predicate,
    decimal RewardUsdc);

public record AcceptBountyRequest(string AcceptedBy);

public record DeliverBountyRequest(
    string DeliveryProof,
    string DeliveredBy);
