using System.Diagnostics;
using System.Text;

namespace Emanon.Cli.Services;

/// <summary>
/// Thin wrapper around git subprocess calls.
/// All methods throw InvalidOperationException on non-zero exit.
/// </summary>
public static class GitService
{
    /// <summary>Run a git command; return trimmed stdout.</summary>
    public static string Run(string args, string? workingDir = null)
    {
        var (stdout, _, exitCode) = Execute("git", args, workingDir);
        if (exitCode != 0)
            throw new InvalidOperationException($"git {args} failed (exit {exitCode})");
        return stdout.Trim();
    }

    /// <summary>Run a git command; return (stdout, stderr, exitCode) without throwing.</summary>
    public static (string stdout, string stderr, int exitCode) TryRun(string args, string? workingDir = null)
        => Execute("git", args, workingDir);

    /// <summary>Run any executable; return (stdout, stderr, exitCode).</summary>
    public static (string stdout, string stderr, int exitCode) Execute(
        string exe, string arguments, string? workingDir = null)
    {
        var psi = new ProcessStartInfo(exe, arguments)
        {
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
            CreateNoWindow         = true,
        };
        if (workingDir != null) psi.WorkingDirectory = workingDir;

        using var proc = Process.Start(psi)!;
        var stdout = new StringBuilder();
        var stderr = new StringBuilder();
        proc.OutputDataReceived += (_, e) => { if (e.Data != null) stdout.AppendLine(e.Data); };
        proc.ErrorDataReceived  += (_, e) => { if (e.Data != null) stderr.AppendLine(e.Data); };
        proc.BeginOutputReadLine();
        proc.BeginErrorReadLine();
        proc.WaitForExit();

        return (stdout.ToString().TrimEnd(), stderr.ToString().TrimEnd(), proc.ExitCode);
    }

    /// <summary>Return the root of the current git repo, or null if not in one.</summary>
    public static string? FindRepoRoot(string startPath)
    {
        var (stdout, _, exit) = TryRun("rev-parse --show-toplevel", startPath);
        return exit == 0 ? stdout.Trim() : null;
    }

    /// <summary>True if there are staged or unstaged changes.</summary>
    public static bool HasChanges(string repoRoot)
    {
        var (stdout, _, _) = TryRun("status --porcelain", repoRoot);
        return !string.IsNullOrWhiteSpace(stdout);
    }

    /// <summary>Number of commits reachable from HEAD.</summary>
    public static int CommitCount(string repoRoot)
    {
        var (stdout, _, exit) = TryRun("rev-list --count HEAD", repoRoot);
        return exit == 0 && int.TryParse(stdout.Trim(), out int n) ? n : 0;
    }

    /// <summary>Current HEAD commit SHA (short).</summary>
    public static string HeadShort(string repoRoot)
    {
        var (stdout, _, exit) = TryRun("rev-parse --short HEAD", repoRoot);
        return exit == 0 ? stdout.Trim() : "unknown";
    }

    /// <summary>Configured user.email, or fallback.</summary>
    public static string UserEmail(string repoRoot)
    {
        var (stdout, _, exit) = TryRun("config user.email", repoRoot);
        return exit == 0 && !string.IsNullOrWhiteSpace(stdout) ? stdout.Trim() : "unknown@emanon";
    }
}
