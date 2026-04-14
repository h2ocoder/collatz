# Getting Started with Emanon

> **Goal:** By the end of this guide, you and one other player will have created universes, written regions, and completed a live merge with conflict resolution. Estimated time: 15 minutes.

---

## Prerequisites

- Git 2.30+ (`git --version`)
- Rust 1.75+ and the `emanon` CLI installed — see [install.md](install.md)
- A second terminal or a second person (for the multi-player section)

---

## Part 1 — Create your universe

```sh
emanon init my-world
cd my-world
```

This creates a `my-world/` directory that is a git repo with the canonical Emanon layout:

```
my-world/
├── regions/        ← your territory
├── contracts/      ← agreements with other universes
├── scars/          ← records of battles won and lost
├── forks/          ← active timeline divergences
├── .gitverse/
│   ├── values.json          ← your conflict preferences
│   └── snapshot_count       ← 0 at genesis
├── .gitattributes           ← merge driver registrations
└── .gitignore
```

Check what was created:

```sh
ls -la
cat .gitverse/values.json
```

---

## Part 2 — Write your first region

Write a file into your universe. `emanon write` stamps it with a Collatz genus:

```sh
emanon write regions/core/origin.md "# Origin

This universe began in the core sector.
Resources: abundant. Threats: unknown."
```

Look at the file that was created:

```sh
cat regions/core/origin.md
```

You'll see your content followed by a genus stamp line:

```
# Origin

This universe began in the core sector.
Resources: abundant. Threats: unknown.
# emanon-genus: {"set_k": 5, "oddity_s": 3, "index_i": 12, "writer": "you@example.com", "snapshot": 0}
```

The genus is a mathematical fingerprint. It determines how this file behaves in future merges. See [concepts.md](concepts.md) for what these numbers mean.

---

## Part 3 — Take your first snapshot

Seal the state of your universe:

```sh
emanon snapshot -m "genesis — core sector established"
```

This creates a git commit. Check the log:

```sh
git log --oneline
```

Write a second region and snapshot again:

```sh
emanon write regions/frontier/anomaly-1.md "# Anomaly 1

Unusual Collatz convergence detected at the frontier.
Investigating."
emanon snapshot -m "frontier probe initiated"
```

---

## Part 4 — Validate your universe

Before sharing your universe with anyone, validate it:

```sh
emanon validate
```

You should see output like:

```
✓ Required directories present
✓ .gitverse/values.json valid
✓ .gitattributes merge driver registrations found
✓ Genus stamps readable in regions/
```

If there are warnings, fix them before proceeding. `--strict` turns warnings into errors:

```sh
emanon validate --strict
```

---

## Part 5 — Multi-player: two universes merge

This section requires either two people on separate machines, or two terminal windows simulating two players locally.

### Player A and Player B: each create a universe

**Both players run in separate directories:**

```sh
# Player A
emanon init universe-alpha
cd universe-alpha
emanon write regions/core/manifest.md "# Alpha Manifest

Alpha claims the core sector."
emanon snapshot -m "alpha genesis"

# Player B (separate terminal or machine)
emanon init universe-beta
cd universe-beta
emanon write regions/core/manifest.md "# Beta Manifest

Beta claims the core sector too."
emanon snapshot -m "beta genesis"
```

Notice both players wrote to `regions/core/manifest.md`. This will conflict.

### Player A: observe and merge Player B's universe

```sh
cd universe-alpha

# Add Player B's universe as a remote
# (use a real GitHub URL if on separate machines, or a local path for local test)
git remote add beta ../universe-beta

# Merge
emanon merge beta/main
```

If Collatz auto-resolution applies (same `set_k`), you'll see a hybrid merge with no conflicts. More likely with different content, you'll see:

```
Merge conflict in regions/core/manifest.md
Conflicts require negotiation: 1 path(s)
Pending merge state saved to .gitverse/pending-merge.json
Run `emanon negotiate` to resolve.
```

### Player A: resolve the conflict

```sh
emanon negotiate
```

The terminal TUI opens showing the conflict. Use arrow keys to navigate:

```
┌──────────────────────────────────────────────┐
│ Conflicts (1)                                │
│                                              │
│ > regions/core/manifest.md                  │
│   Ours:   set_k=5 oddity_s=3  leverage=2    │
│   Theirs: set_k=7 oddity_s=1  leverage=2    │
│                                              │
│ [b]attle  [c]ontract  [f]ork  [m]anual      │
└──────────────────────────────────────────────┘
```

Choose a resolution:

- Press **b** — battle: Alpha's version wins, a scar is recorded
- Press **c** — contract: Beta's version is accepted, terms recorded in `contracts/`
- Press **f** — fork: both timelines diverge, fork pointer created in `forks/`
- Press **m** — manual: opens `$EDITOR`

After resolving all conflicts, `emanon negotiate` creates a merge commit.

Check the result:

```sh
git log --oneline
cat regions/core/manifest.md

# If you chose contract:
ls contracts/

# If you chose battle:
ls scars/

# If you chose fork:
git branch -a
ls forks/
```

---

## Part 6 — Share your universe

Push your universe to GitHub so others can observe and merge it:

```sh
# Create a public repo (requires gh CLI)
gh repo create my-world --public --source=. --push

# Or add an existing remote manually:
git remote add origin https://github.com/yourusername/my-world
git push -u origin main
```

Other players can now add your universe as a remote and run `emanon merge`.

---

## Part 7 — Publish to the registry

Publish your universe listing so any player can discover and observe you:

```sh
# Configure your identity first (one-time setup):
# edit ~/.config/emanon/config.toml — see registry-walkthrough.md

emanon registry push
```

This opens a PR on the canonical registry.  Once merged, your universe appears in
the global player list.

```sh
# Browse all published universes:
emanon registry pull
emanon registry list
```

For a full publishing walkthrough, see [registry-walkthrough.md](registry-walkthrough.md).

To run a private registry for a friend group or league, see [federation.md](federation.md).

---

## What's next

- **Start from the template:** instead of `emanon init`, fork the [emanon-starter](https://github.com/forgetthefrets/emanon-starter) template for a pre-configured universe
- **Understand the physics:** read [concepts.md](concepts.md) for plain-English explanations of every game term
- **Go deeper:** [Gitverse Design](2026-04-13-gitverse-design.md) explains the full mathematical model
- **Use the AI companion:** the [Claude Code skill](../src/skill/SKILL.md) can play alongside you, suggesting moves and explaining conflicts
- **Publish your universe:** follow the [registry walkthrough](registry-walkthrough.md) to list your universe publicly
- **Run a private league:** follow the [federation guide](federation.md) to host a registry for your group

---

## Troubleshooting

**`emanon: command not found`**
Make sure `~/.cargo/bin` is in your PATH. See [install.md](install.md).

**`fatal: not a git repository`**
You're running `emanon snapshot`, `emanon write`, or `emanon validate` outside an Emanon universe. `cd` into the directory created by `emanon init`.

**`emanon merge` exits with "nothing to merge"**
The remote branch is already part of your history (`git merge-base` returns the tip). This is fine — it means your universe already contains everything from that remote.

**Merge driver not invoked during `git merge`**
Your `.gitattributes` file may be missing or your local git config may not have the driver registered. Run `emanon validate` — it will identify the missing configuration.

**TUI doesn't render correctly**
`emanon negotiate` requires a terminal that supports 256-color mode. Most modern terminals do. If the display is garbled, try `TERM=xterm-256color emanon negotiate`.
