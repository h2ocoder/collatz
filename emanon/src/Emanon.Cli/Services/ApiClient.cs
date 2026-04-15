using System.Net.Http.Json;
using System.Text.Json;

namespace Emanon.Cli.Services;

/// <summary>
/// Typed HttpClient wrapper for the Emanon central authority API.
/// Commands call into this instead of using HttpClient directly.
/// Sync facade — commands are sync.
/// </summary>
public sealed class ApiClient : IDisposable
{
    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
    };

    private readonly HttpClient _http;
    public string BaseUrl { get; }

    public ApiClient(string baseUrl, HttpClient? http = null)
    {
        BaseUrl = baseUrl.TrimEnd('/');
        _http = http ?? new HttpClient();
        _http.BaseAddress = new Uri(BaseUrl + "/");
    }

    // Registry -----------------------------------------------------------------

    public UniverseDto Register(RegisterUniverseRequestDto req)
        => PostJson<RegisterUniverseRequestDto, UniverseDto>("api/registry/universes", req);

    public IReadOnlyList<UniverseDto> ListUniverses()
        => GetJson<UniverseDto[]>("api/registry/universes");

    public UniverseDto? GetUniverse(string id)
        => TryGetJson<UniverseDto>($"api/registry/universes/{id}");

    public UniverseDto Push(string id, PushUniverseRequestDto req)
        => PostJson<PushUniverseRequestDto, UniverseDto>($"api/registry/universes/{id}/push", req);

    public UniverseDto Pull(string id)
        => GetJson<UniverseDto>($"api/registry/universes/{id}/pull");

    // Bounties -----------------------------------------------------------------

    public IReadOnlyList<BountyDto> ListBounties(string? universeId = null, string? status = null)
    {
        var qs = new List<string>();
        if (universeId is not null) qs.Add($"universeId={Uri.EscapeDataString(universeId)}");
        if (status     is not null) qs.Add($"status={Uri.EscapeDataString(status)}");
        var path = qs.Count == 0 ? "api/bounties" : $"api/bounties?{string.Join('&', qs)}";
        return GetJson<BountyDto[]>(path);
    }

    public BountyDto? GetBounty(string id)
        => TryGetJson<BountyDto>($"api/bounties/{id}");

    public BountyDto PostBounty(PostBountyRequestDto req)
        => PostJson<PostBountyRequestDto, BountyDto>("api/bounties", req);

    public BountyDto AcceptBounty(string id, AcceptBountyRequestDto req)
        => PostJson<AcceptBountyRequestDto, BountyDto>($"api/bounties/{id}/accept", req);

    public BountyDto DeliverBounty(string id, DeliverBountyRequestDto req)
        => PostJson<DeliverBountyRequestDto, BountyDto>($"api/bounties/{id}/deliver", req);

    // Plumbing -----------------------------------------------------------------

    private T GetJson<T>(string path)
    {
        using var resp = _http.Send(new HttpRequestMessage(HttpMethod.Get, path));
        EnsureSuccess(resp, path);
        return DeserializeBody<T>(resp)!;
    }

    private T? TryGetJson<T>(string path) where T : class
    {
        using var resp = _http.Send(new HttpRequestMessage(HttpMethod.Get, path));
        if (resp.StatusCode == System.Net.HttpStatusCode.NotFound) return null;
        EnsureSuccess(resp, path);
        return DeserializeBody<T>(resp);
    }

    private TOut PostJson<TIn, TOut>(string path, TIn body)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path)
        {
            Content = JsonContent.Create(body, options: JsonOpts),
        };
        using var resp = _http.Send(req);
        EnsureSuccess(resp, path);
        return DeserializeBody<TOut>(resp)!;
    }

    private static void EnsureSuccess(HttpResponseMessage resp, string path)
    {
        if (resp.IsSuccessStatusCode) return;
        string body;
        try { body = resp.Content.ReadAsStringAsync().GetAwaiter().GetResult(); }
        catch { body = "<unreadable>"; }
        throw new ApiException(
            $"API call failed: {(int)resp.StatusCode} {resp.StatusCode} on {path}\n{body}",
            (int)resp.StatusCode, body);
    }

    private static T? DeserializeBody<T>(HttpResponseMessage resp)
    {
        var stream = resp.Content.ReadAsStream();
        return JsonSerializer.Deserialize<T>(stream, JsonOpts);
    }

    public void Dispose() => _http.Dispose();

    /// <summary>
    /// Resolve the registry server URL in priority order:
    /// explicit flag → $EMANON_SERVER → values.json registry_server.
    /// Returns null if nothing is configured — caller decides how to error.
    /// </summary>
    public static string? ResolveServerUrl(string? flag, string? repoRoot)
    {
        if (!string.IsNullOrWhiteSpace(flag)) return flag;
        var env = Environment.GetEnvironmentVariable("EMANON_SERVER");
        if (!string.IsNullOrWhiteSpace(env)) return env;
        if (repoRoot is not null)
        {
            var stored = GitverseLayout.ReadValues(repoRoot)?.RegistryServer;
            if (!string.IsNullOrWhiteSpace(stored)) return stored;
        }
        return null;
    }
}

public sealed class ApiException(string message, int statusCode, string body) : Exception(message)
{
    public int StatusCode { get; } = statusCode;
    public string Body { get; } = body;
}

// DTOs — mirror server models (kept local to avoid pulling Emanon.Server as a dep).

public record UniverseDto(
    string  Id,
    string  Name,
    string  OwnerEmail,
    string  GitUrl,
    string  Description,
    int     Version,
    int     SnapshotCount,
    string  CreatedAt,
    string  UpdatedAt,
    string? HeadGenus);

public record RegisterUniverseRequestDto(
    string Name,
    string OwnerEmail,
    string GitUrl,
    string Description = "");

public record PushUniverseRequestDto(
    string UniverseId,
    int    SnapshotCount,
    string HeadGenus,
    string OwnerEmail);

/// <summary>Mirror of server-side BountyStatus. Keep ordinals aligned.</summary>
public enum BountyStatus { Open, Accepted, Delivered, Verified, Cancelled }

public record BountyDto(
    string       Id,
    string       UniverseId,
    string       PostedBy,
    string       Title,
    string       Description,
    string       Predicate,
    decimal      RewardUsdc,
    BountyStatus Status,
    string?      AcceptedBy,
    string?      DeliveryProof,
    string       CreatedAt,
    string       UpdatedAt);

public record PostBountyRequestDto(
    string  UniverseId,
    string  PostedBy,
    string  Title,
    string  Description,
    string  Predicate,
    decimal RewardUsdc);

public record AcceptBountyRequestDto(string AcceptedBy);

public record DeliverBountyRequestDto(string DeliveryProof, string DeliveredBy);
