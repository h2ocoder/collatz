using System.Diagnostics;
using System.Text;

namespace Emanon.E2E.Fixtures;

/// <summary>Result of a CLI invocation.</summary>
public sealed record CliResult(int ExitCode, string Stdout, string Stderr)
{
    public bool Succeeded => ExitCode == 0;
}

/// <summary>
/// Invokes the built Emanon.Cli.dll as a real subprocess with a configurable working
/// directory. Tests rely on cwd-based repo discovery (GitService.FindRepoRoot).
/// </summary>
public sealed class CliRunner
{
    private readonly string _workingDir;
    private readonly string _cliDll;
    private readonly Dictionary<string, string> _extraEnv = new();

    public CliRunner(string workingDir)
    {
        _workingDir = workingDir;
        _cliDll = Path.Combine(AppContext.BaseDirectory, "Emanon.Cli.dll");
        if (!File.Exists(_cliDll))
            throw new FileNotFoundException(
                $"Cannot find Emanon.Cli.dll at {_cliDll}. " +
                "Ensure Emanon.E2E has a ProjectReference to Emanon.Cli.");
    }

    /// <summary>Absolute path to the CLI DLL — tests use this to build EMANON_CMD.</summary>
    public string CliDll => _cliDll;

    /// <summary>Set an env var that will be passed to every subsequent CLI invocation.</summary>
    public void SetEnv(string key, string value) => _extraEnv[key] = value;

    public CliResult Run(params string[] args)
    {
        var psi = new ProcessStartInfo("dotnet")
        {
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
            CreateNoWindow         = true,
            WorkingDirectory       = _workingDir,
        };
        psi.ArgumentList.Add("exec");
        psi.ArgumentList.Add(_cliDll);
        foreach (var a in args) psi.ArgumentList.Add(a);

        // Spectre.Console writes colour codes when a terminal is detected; strip them
        // for predictable assertions. NO_COLOR is respected by Spectre.
        psi.Environment["NO_COLOR"] = "1";
        psi.Environment["TERM"]     = "dumb";
        foreach (var (k, v) in _extraEnv) psi.Environment[k] = v;

        using var proc = Process.Start(psi)
            ?? throw new InvalidOperationException("Failed to start Emanon.Cli subprocess.");

        var stdout = new StringBuilder();
        var stderr = new StringBuilder();
        proc.OutputDataReceived += (_, e) => { if (e.Data != null) stdout.AppendLine(e.Data); };
        proc.ErrorDataReceived  += (_, e) => { if (e.Data != null) stderr.AppendLine(e.Data); };
        proc.BeginOutputReadLine();
        proc.BeginErrorReadLine();

        if (!proc.WaitForExit(30_000))
        {
            try { proc.Kill(entireProcessTree: true); } catch { }
            throw new TimeoutException(
                $"CLI command timed out after 30s: {string.Join(' ', args)}");
        }
        // Ensure async readers have drained.
        proc.WaitForExit();

        return new CliResult(
            proc.ExitCode,
            stdout.ToString().TrimEnd(),
            stderr.ToString().TrimEnd());
    }
}
