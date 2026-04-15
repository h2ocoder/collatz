using System.Diagnostics;

namespace Emanon.E2E.Fixtures;

/// <summary>
/// Spawns Emanon.Server as a real OS subprocess on a free loopback port for the
/// lifetime of the test class. Uses the built server DLL copied into the E2E test
/// output directory via project reference — no rebuild.
/// </summary>
public sealed class ServerFixture : IDisposable
{
    private readonly Process _proc;
    public string BaseUrl { get; }
    public HttpClient Http { get; }

    public ServerFixture()
    {
        int port = FreePort.Pick();
        BaseUrl = $"http://127.0.0.1:{port}";

        var serverDll = Path.Combine(AppContext.BaseDirectory, "Emanon.Server.dll");
        if (!File.Exists(serverDll))
            throw new FileNotFoundException(
                $"Cannot find Emanon.Server.dll at {serverDll}. " +
                "Ensure Emanon.E2E has a ProjectReference to Emanon.Server.");

        var psi = new ProcessStartInfo("dotnet", $"exec \"{serverDll}\"")
        {
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
            CreateNoWindow         = true,
        };
        psi.Environment["ASPNETCORE_URLS"]        = BaseUrl;
        psi.Environment["ASPNETCORE_ENVIRONMENT"] = "Production";  // skip swagger to cut noise

        _proc = Process.Start(psi)
            ?? throw new InvalidOperationException("Failed to start Emanon.Server subprocess.");
        _proc.BeginOutputReadLine();
        _proc.BeginErrorReadLine();

        Http = new HttpClient { BaseAddress = new Uri(BaseUrl + "/") };
        WaitForReady();
    }

    private void WaitForReady()
    {
        var deadline = DateTime.UtcNow.AddSeconds(20);
        Exception? last = null;
        while (DateTime.UtcNow < deadline)
        {
            if (_proc.HasExited)
                throw new InvalidOperationException(
                    $"Server exited prematurely (code {_proc.ExitCode}) before becoming ready.");
            try
            {
                using var resp = Http.GetAsync("health").GetAwaiter().GetResult();
                if (resp.IsSuccessStatusCode) return;
            }
            catch (Exception ex) { last = ex; }
            Thread.Sleep(100);
        }
        throw new TimeoutException(
            $"Server at {BaseUrl} did not become ready within 20s. Last error: {last?.Message}");
    }

    public void Dispose()
    {
        Http.Dispose();
        try
        {
            if (!_proc.HasExited)
            {
                _proc.Kill(entireProcessTree: true);
                _proc.WaitForExit(5_000);
            }
        }
        catch { /* best-effort teardown */ }
        _proc.Dispose();
    }
}
