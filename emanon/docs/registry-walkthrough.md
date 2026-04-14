# Registry Walkthrough — Publishing Your Universe

> **Goal:** By the end of this guide you will have published a listing for your Emanon universe
> to the canonical public registry so other players can discover and observe it.
> Estimated time: 10 minutes.

---

## Prerequisites

- The `emanon` CLI installed — see [install.md](install.md)
- A universe with at least one snapshot (`emanon snapshot` run at least once)
- Your universe pushed to a **public** GitHub repository
- The `gh` CLI authenticated (`gh auth status`) — needed to open the registry PR
- An Ed25519 keypair for signing your entry (see [Generating a keypair](#generating-a-keypair))

---

## Overview

The canonical registry lives at **https://github.com/forgetthefrets/emanon-registry**.
It is a plain git repository where each universe is represented by one JSON file
under `entries/<name>.json`.  Publishing a universe means opening a PR that adds
or updates that file.  The registry's CI validates the entry automatically; a
maintainer merges it once CI is green.

`emanon registry push` automates the entire process:
1. Reads your universe state (snapshot count, values hash, current HEAD).
2. Generates a schema-valid entry JSON.
3. Clones the registry, commits the entry, and opens a PR via `gh`.

---

## Step 1 — Configure your identity

Create `~/.config/emanon/config.toml` with your public key and universe details:

```toml
[registry]
url = "https://github.com/forgetthefrets/emanon-registry"
owner_pubkey = "YOUR_ED25519_PUBKEY_BASE58"
universe_name = "your-universe-name"
git_remote = "origin"
```

| Field | Description |
|-------|-------------|
| `url` | Registry repo URL. Defaults to the canonical registry — only change this for a private league registry. |
| `owner_pubkey` | Your Ed25519 public key in Base58 encoding. See [Generating a keypair](#generating-a-keypair). |
| `universe_name` | The slug used as your registry entry filename (`entries/<name>.json`). Must be 3–64 chars, lowercase alphanumeric with hyphens/underscores. |
| `git_remote` | The name of the git remote that points to your **public** universe repo. Usually `origin`. |

---

## Step 2 — Validate your universe

Before publishing, verify your universe is well-formed:

```sh
cd path/to/your-universe
emanon validate --strict
```

Expected output:

```
✓ Required directories present
✓ .gitverse/values.json valid
✓ .gitattributes merge driver registrations found
✓ Genus stamps readable in regions/
```

Fix any errors before continuing.  The registry CI will reject entries whose
`values_hash` or `head_commit` cannot be verified against the live repo.

---

## Step 3 — Push your universe to GitHub

The registry entry must point to a **publicly reachable** git URL.  The CI
fetches from it directly to verify `head_commit`.

```sh
# If you haven't already pushed:
gh repo create your-universe-name --public --source=. --push

# If the repo already exists, just push the latest snapshot:
git push origin main
```

Note the URL — it will be the `git_url` in your registry entry.

---

## Step 4 — Publish to the registry

Run from inside your universe directory:

```sh
emanon registry push
```

What happens:

1. `emanon` reads your `~/.config/emanon/config.toml`.
2. It computes the required hashes (`values_hash`, `scrambled_root_hash`) from
   your current working tree and `head_commit` from `git rev-parse HEAD`.
3. It clones or updates the registry repo locally
   (`~/.local/share/emanon/registry/...`).
4. It writes `entries/<your-universe-name>.json` with all required fields filled.
5. It commits the file, pushes to a fork of the registry, and opens a PR via `gh`.

Typical output:

```
Generating registry entry for "alice-prime"...
  head_commit: abc1234...
  snapshot_count: 7
  values_hash: sha256:e3b0c4...
  scrambled_root_hash: sha256:a665a4...
Cloning registry to ~/.local/share/emanon/registry/...
Writing entries/alice-prime.json
Pushing to fork and opening PR...
✅  PR opened: https://github.com/forgetthefrets/emanon-registry/pull/42
    Your universe will appear in the registry once the PR is merged.
```

### Overriding the registry URL

To push to a private league registry instead of the canonical one:

```sh
emanon registry push --registry https://github.com/my-league/my-registry
```

---

## Step 5 — Wait for CI and merge

Once the PR is open, the registry CI runs four checks automatically:

| Check | What it verifies |
|-------|-----------------|
| Schema | All required fields present and valid |
| Filename consistency | `name` field matches the filename stem |
| Remote reachability | `git_url` is publicly reachable |
| HEAD commit | `head_commit` matches the repo's current `HEAD` |

If CI fails, the PR will show error messages.  Fix the issue and push again:

```sh
# After addressing the issue:
emanon registry push
```

Once CI is green, a maintainer merges the PR.

---

## Step 6 — Verify your listing

After the PR is merged, pull the registry and confirm your entry appears:

```sh
emanon registry pull
emanon registry list
```

You should see your universe in the table:

```
NAME              OWNER              SNAPSHOTS  TAGS
alice-prime       2WqMzj...          7          solo, early
```

---

## Updating your entry

Whenever you advance your universe (new snapshots, changed `values.json`), update
your registry entry by running `emanon registry push` again.  It opens a new PR
updating `head_commit`, `snapshot_count`, `updated_at`, and the hashes.

---

## Removing your entry

Open a manual PR deleting `entries/<your-name>.json` in the registry repo.
Include a brief reason in the PR description.  Maintainers will merge without CI
checks (deletion always passes schema validation).

---

## Generating a keypair

The registry uses Ed25519 public keys to identify owners.  Generate one with any
standard tool:

**OpenSSH (recommended):**

```sh
ssh-keygen -t ed25519 -C "your@email.com" -f ~/.ssh/emanon_id_ed25519
# Public key: ~/.ssh/emanon_id_ed25519.pub
```

Extract the Base58 public key for your config:

```sh
# The public key in OpenSSH format:
cat ~/.ssh/emanon_id_ed25519.pub
# ssh-ed25519 AAAA... your@email.com
#             ^^^^
# The Base58 blob after "ssh-ed25519 " is your owner_pubkey.
```

Copy just the Base58 blob (the `AAAA...` part, without the prefix or comment)
into `owner_pubkey` in your config.

**GPG:**

```sh
gpg --full-generate-key   # choose EdDSA / Ed25519
gpg --list-keys           # find your key ID
gpg --export-ssh-key <KEY_ID>
# The Base58 payload after "ssh-ed25519 " is your owner_pubkey.
```

---

## What's next

- **Discover other universes:** `emanon registry list` shows everyone who has published.
- **Observe another universe:** `emanon registry add-remote <name>` then `emanon merge <name>/main`.
- **Run a private league registry:** see [federation.md](federation.md).
- **Full schema reference:** see [registry-schema.md](registry-schema.md).
