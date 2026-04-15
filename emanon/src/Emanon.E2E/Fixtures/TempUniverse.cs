namespace Emanon.E2E.Fixtures;

/// <summary>
/// Ephemeral on-disk universe directory. Created empty — tests init it themselves
/// via `emanon init` to exercise the real init path. Auto-deletes on Dispose.
/// </summary>
public sealed class TempUniverse : IDisposable
{
    public string Path { get; }
    public CliRunner Cli { get; }

    public TempUniverse(string? authorEmail = null)
    {
        Path = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "emanon-e2e-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(Path);
        Cli = new CliRunner(Path);

        // Pre-init git with a deterministic identity so `emanon init`'s genesis
        // commit works even when the host has no global git config (CI, fresh containers).
        var email = authorEmail ?? $"e2e-{Guid.NewGuid().ToString("N")[..6]}@emanon.test";
        Git("init", "-q", "-b", "main");
        Git("config", "user.email", email);
        Git("config", "user.name",  "emanon-e2e");
        Git("config", "commit.gpgsign", "false");
        AuthorEmail = email;
    }

    public string AuthorEmail { get; } = "";

    public (string stdout, string stderr, int exit) Git(params string[] args)
    {
        var psi = new System.Diagnostics.ProcessStartInfo("git")
        {
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
            CreateNoWindow         = true,
            WorkingDirectory       = Path,
        };
        foreach (var a in args) psi.ArgumentList.Add(a);
        using var p = System.Diagnostics.Process.Start(psi)!;
        var so = p.StandardOutput.ReadToEnd();
        var se = p.StandardError.ReadToEnd();
        p.WaitForExit();
        return (so.TrimEnd(), se.TrimEnd(), p.ExitCode);
    }

    public string ResolvePath(string relative) => System.IO.Path.Combine(Path, relative);

    public void Dispose()
    {
        try { Directory.Delete(Path, recursive: true); } catch { }
    }
}
