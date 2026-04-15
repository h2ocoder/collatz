using System.Net.Http.Json;
using Emanon.Cli.Services;
using Emanon.E2E.Fixtures;
using Xunit.Abstractions;
using Bounty       = Emanon.Server.Models.Bounty;
using BountyStatus = Emanon.Server.Models.BountyStatus;
using Universe     = Emanon.Server.Models.Universe;

namespace Emanon.E2E;

/// <summary>
/// End-to-end tests that exercise the full vertical slice:
/// real Emanon.Server subprocess + real Emanon.Cli subprocess + real on-disk git repo.
///
/// The compute-gated bounty test proves the "git is the universe" loop: the only way
/// to satisfy the server's Collatz predicate is to actually run the Collatz genus
/// computation, write a stamped file, and deliver it.
/// </summary>
[Trait("Category", "E2E")]
public class UniverseJourneyTests : IClassFixture<ServerFixture>
{
    private readonly ServerFixture _server;
    private readonly ITestOutputHelper _out;

    public UniverseJourneyTests(ServerFixture server, ITestOutputHelper output)
    {
        _server = server;
        _out = output;
    }

    // -------------------------------------------------------------------------
    // Test 1: the canonical create → explore → compute-gated update journey.
    // -------------------------------------------------------------------------

    [Fact]
    public async Task FullLoop_CreateExploreDeliverBounty()
    {
        using var tmp = new TempUniverse();
        var universeName = "e2e-" + Guid.NewGuid().ToString("N")[..8];

        // 1. CREATE ─────────────────────────────────────────────────────────
        Require(tmp.Cli.Run("init", universeName),
            "emanon init");
        Assert.True(Directory.Exists(tmp.ResolvePath(".gitverse")), ".gitverse dir should exist");
        Assert.True(File.Exists(tmp.ResolvePath(".gitverse/values.json")), "values.json should exist");

        Require(tmp.Cli.Run("registry", "push", "--server", _server.BaseUrl),
            "emanon registry push (initial)");

        var values = GitverseLayout.ReadValues(tmp.Path);
        Assert.NotNull(values);
        Assert.False(string.IsNullOrWhiteSpace(values!.RegistryId),
            "registry_id must be populated after successful push");
        Assert.Equal(_server.BaseUrl, values.RegistryServer);

        // 2. EXPLORE ────────────────────────────────────────────────────────
        var listed = await _server.Http.GetFromJsonAsync<Universe[]>("api/registry/universes");
        Assert.NotNull(listed);
        Assert.Contains(listed!, u => u.Id == values.RegistryId && u.Name == universeName);

        var listCli = Require(tmp.Cli.Run("registry", "list"), "emanon registry list");
        Assert.Contains(universeName, listCli.Stdout);

        // 3. UPDATE (compute-gated) ────────────────────────────────────────
        const int requiredSetK = 3;
        var constraint = $$"""
        {
          "title": "Find a stamped region with set_k >= {{requiredSetK}}",
          "description": "E2E compute gate",
          "predicate": "genus.set_k >= {{requiredSetK}}",
          "reward_usdc": 10
        }
        """;
        File.WriteAllText(tmp.ResolvePath("bounty.json"), constraint);
        Require(tmp.Cli.Run("bounty", "post", "--constraint", "bounty.json"),
            "emanon bounty post");

        // Find the bounty id via the server (decoupled from CLI stdout parsing).
        var bounties = await _server.Http.GetFromJsonAsync<Bounty[]>(
            $"api/bounties?universeId={values.RegistryId}");
        Assert.NotNull(bounties);
        var bounty = Assert.Single(bounties!);
        Assert.Equal(BountyStatus.Open, bounty.Status);

        var bountyListCli = Require(tmp.Cli.Run("bounty", "list"), "emanon bounty list");
        Assert.Contains(bounty.Id, bountyListCli.Stdout);

        Require(tmp.Cli.Run("bounty", "accept", bounty.Id), "emanon bounty accept");

        // Worker loop: write files until one carries a genus meeting the predicate.
        string proofPath = FindProofPath(tmp, requiredSetK, maxAttempts: 64, _out);
        _out.WriteLine($"Worker produced proof file: {proofPath}");

        Require(tmp.Cli.Run("bounty", "deliver", bounty.Id, "--proof", proofPath),
            "emanon bounty deliver");

        var settled = await _server.Http.GetFromJsonAsync<Bounty>(
            $"api/bounties/{bounty.Id}");
        Assert.NotNull(settled);
        Assert.Equal(BountyStatus.Delivered, settled!.Status);
        Assert.False(string.IsNullOrWhiteSpace(settled.DeliveryProof));
    }

    // -------------------------------------------------------------------------
    // Test 2: init sanity — cheap guard against init regressions.
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateUniverse_WritesValidGitverseLayout()
    {
        using var tmp = new TempUniverse();
        Require(tmp.Cli.Run("init", "layout-check"), "emanon init");

        Assert.True(Directory.Exists(tmp.ResolvePath(".git")));
        foreach (var dir in new[] { ".gitverse", "regions", "contracts", "scars", "forks" })
            Assert.True(Directory.Exists(tmp.ResolvePath(dir)), $"{dir} should exist");

        Assert.True(File.Exists(tmp.ResolvePath(".gitverse/values.json")));
        Assert.True(File.Exists(tmp.ResolvePath(".gitattributes")));

        var values = GitverseLayout.ReadValues(tmp.Path);
        Assert.NotNull(values);
        Assert.Equal("layout-check", values!.UniverseName);
        Assert.Equal(0, values.SnapshotCount);

        var (log, _, exit) = tmp.Git("log", "--oneline");
        Assert.Equal(0, exit);
        Assert.Contains("genesis", log, StringComparison.OrdinalIgnoreCase);

        Require(tmp.Cli.Run("validate"), "emanon validate");
    }

    // -------------------------------------------------------------------------
    // Test 3: the compute gate actually gates — delivery without the required
    // genus must be rejected by the server and must not settle the bounty.
    // -------------------------------------------------------------------------

    [Fact]
    public async Task BadDelivery_Rejected()
    {
        using var tmp = new TempUniverse();
        var universeName = "reject-" + Guid.NewGuid().ToString("N")[..8];

        Require(tmp.Cli.Run("init", universeName), "emanon init");
        Require(tmp.Cli.Run("registry", "push", "--server", _server.BaseUrl), "emanon registry push");
        var values = GitverseLayout.ReadValues(tmp.Path)!;

        // set_k is bounded by dropping time of odd n < ~1,000,000; >= 10000 is unreachable.
        const string impossiblePredicate = "genus.set_k >= 10000";
        File.WriteAllText(tmp.ResolvePath("bounty.json"), $$"""
        {
          "title":      "Impossible",
          "description": "Guaranteed to fail",
          "predicate":   "{{impossiblePredicate}}",
          "reward_usdc": 1
        }
        """);
        Require(tmp.Cli.Run("bounty", "post", "--constraint", "bounty.json"), "emanon bounty post");

        var bounty = (await _server.Http.GetFromJsonAsync<Bounty[]>(
            $"api/bounties?universeId={values.RegistryId}"))!.Single();

        Require(tmp.Cli.Run("bounty", "accept", bounty.Id), "emanon bounty accept");

        // Produce any stamped file — doesn't matter, its set_k will be way below 10000.
        Require(tmp.Cli.Run("write", "regions/main/attempt.txt", "payload"), "emanon write");

        // Delivery should fail — CLI returns non-zero, bounty stays Accepted.
        var deliver = tmp.Cli.Run(
            "bounty", "deliver", bounty.Id, "--proof", "regions/main/attempt.txt");
        _out.WriteLine($"deliver stdout: {deliver.Stdout}");
        _out.WriteLine($"deliver stderr: {deliver.Stderr}");
        Assert.NotEqual(0, deliver.ExitCode);

        var after = await _server.Http.GetFromJsonAsync<Bounty>($"api/bounties/{bounty.Id}");
        Assert.Equal(BountyStatus.Accepted, after!.Status);
        Assert.Null(after.DeliveryProof);
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private CliResult Require(CliResult result, string label)
    {
        if (!result.Succeeded)
        {
            _out.WriteLine($"{label} FAILED (exit {result.ExitCode})");
            _out.WriteLine($"stdout:\n{result.Stdout}");
            _out.WriteLine($"stderr:\n{result.Stderr}");
            Assert.Fail($"{label} exited {result.ExitCode}");
        }
        return result;
    }

    /// <summary>
    /// The worker step: enumerate candidate paths, write payloads, and inspect
    /// each genus stamp. Return the relative path of the first file whose genus
    /// meets the threshold. Throws if no candidate succeeds within
    /// <paramref name="maxAttempts"/>.
    /// </summary>
    private static string FindProofPath(TempUniverse tmp, int requiredSetK, int maxAttempts, ITestOutputHelper log)
    {
        var samples = new List<string>();
        for (int i = 0; i < maxAttempts; i++)
        {
            var relPath = $"regions/main/attempt-{i}.txt";
            var res = tmp.Cli.Run("write", relPath, $"payload-{i}");
            if (!res.Succeeded)
                throw new InvalidOperationException(
                    $"emanon write failed: {res.Stderr} / {res.Stdout}");

            var abs = tmp.ResolvePath(relPath);
            var stamp = GenusStamper.ReadStamp(abs);
            if (stamp is null)
                throw new InvalidOperationException($"no stamp on {relPath} after write");
            samples.Add($"{i}:{stamp.Value.SetK}");
            if (stamp.Value.SetK >= requiredSetK)
                return relPath;
        }
        log.WriteLine("set_k samples: " + string.Join(" ", samples));
        throw new InvalidOperationException(
            $"Could not find a file with set_k >= {requiredSetK} in {maxAttempts} attempts.");
    }
}
