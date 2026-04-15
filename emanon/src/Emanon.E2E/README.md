# Emanon.E2E

End-to-end tests that exercise the full vertical slice of Emanon: real subprocesses, real HTTP, real on-disk git repos. No mocks, no in-memory test servers.

Fast, component-level coverage of the wiring lives in `Emanon.Tests`. This project is for the tests that can only be honest if real processes actually talk to each other.

## Running

```bash
# from emanon/src
dotnet test Emanon.E2E/Emanon.E2E.csproj                          # E2E only
dotnet test                                                       # everything
dotnet test --filter Category=E2E                                 # E2E across all projects
dotnet test --filter "Category!=E2E"                              # skip E2E (unit/component only)
```

Every test in this project carries `[Trait("Category", "E2E")]` so CI can split fast and slow suites.

## What's covered

### `UniverseJourneyTests`

The three-phase journey: create a universe → explore it → push a compute-gated update.

| Test | What it proves |
|---|---|
| `FullLoop_CreateExploreDeliverBounty` | `emanon init` → `registry push` → `bounty post` → `bounty accept` → worker computes a file with `set_k ≥ K` → `bounty deliver`. The predicate gate is unfakeable: the only way to satisfy `set_k ≥ K` is to run real Collatz math. |
| `CreateUniverse_WritesValidGitverseLayout` | `emanon init` produces a real git repo + `.gitverse/` layout + genesis commit. Cheap guard against init regressions. |
| `BadDelivery_Rejected` | A delivery whose genus doesn't satisfy the predicate is rejected (422), bounty stays `Accepted`, no state drift. Proves the compute gate actually gates. |

Shared `ServerFixture` spawns a real `Emanon.Server` subprocess on a free loopback port for the class lifetime. `InMemoryStore` keeps tests isolated by scoping everything to unique universe IDs (GUID-suffixed names).

### `MergeDriverE2ETests`

The headline claim of the gitverse design: conflicts resolve deterministically via Collatz without any central authority.

| Test | What it proves |
|---|---|
| `Conflict_In_Regions_IsResolved_ByDriver_WithoutAuthority` | Two branches write to the same `regions/` file. `git merge` fires the custom driver. The driver picks a winner by genus, writes the resolution atomically, and stamps the merged file with the loser's genus as an audit trail. No server is touched. |
| `Conflict_WithUnstampedSide_LeavesGitConflictMarkers` | If either side has no stamp, the driver defers (exit 1), git leaves conflict markers. The invariant is: **unstamped writes cannot silently win**. |

## Fixtures

- **`ServerFixture`** — spawns the built `Emanon.Server.dll` via `dotnet exec` on a free port (`ASPNETCORE_URLS` env). Waits on `/health` before yielding. Kills the process tree on dispose.
- **`TempUniverse`** — per-test throwaway directory. Pre-runs `git init -b main` and sets `user.email` / `user.name` so commits work even on hosts with no global git config. `Cli` property exposes a `CliRunner` bound to the temp dir as working directory.
- **`CliRunner`** — invokes `Emanon.Cli.dll` as a subprocess. Strips ANSI colour (`NO_COLOR=1`) so assertions on stdout are stable. Carries extra env vars set via `SetEnv(...)` — this is how `MergeDriverE2ETests` passes `EMANON_CMD=dotnet exec <path to Cli.dll>` so git's merge driver can invoke the built binary without `emanon` being on PATH.

## Known follow-ups (intentionally not in scope)

- **Hybrid / weighted merges.** The full spec (`docs/2026-04-13-gitverse-design.md`) has three resolution paths: same `set_k` → hybrid merge, same `oddity_s` → weighted merge with bit-destruction attenuation, otherwise → defer. `MergeDriverCommand` currently implements winner-takes-all as a deterministic MVP and is swap-in replaceable.
- **`--contract-mode` and `--append-only` drivers.** Init registers them in git config (matching the existing convention) but the command stubs exit 1 (defer to manual resolution). Worth implementing before anyone relies on `contracts/**` or `scars/**` auto-merge.
- **Negotiation UI.** When the driver defers, there's no built-in path to resolve the conflict interactively; you fall back to plain git conflict markers.
- **Signed identity.** Bounty acceptance / delivery match on plaintext email strings — anyone with a known email can impersonate. Needs `.gitverse/identity.key` to be actually used for signing + verification.
- **Server auth.** None. Fine for local dev, not fine for any deployment.
