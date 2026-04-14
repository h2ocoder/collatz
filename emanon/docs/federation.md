# Federation Guide — Running Your Own Registry

> **Goal:** By the end of this guide you will have stood up a private Emanon registry
> for your friend group or league.  Other players in your group will be able to publish
> and discover universes through it.  Estimated time: 20–30 minutes.

---

## What is a federated registry?

The canonical registry at `https://github.com/forgetthefrets/emanon-registry` is
public and open to all players.  A **federated registry** is your own fork of that
repo — hosted on GitHub under your account or organisation — with your own CI rules,
membership policies, and optional `values.json` defaults.

You might want a private registry to:
- Keep your league's universes discoverable only within your group.
- Enforce custom rules (minimum snapshot count before publishing, required tags, etc.).
- Apply league-specific `values.json` defaults during universe validation.

A federated registry is still just a git repo.  Players in your league point their
`emanon` config at your fork's URL instead of the canonical one.

---

## Prerequisites

- A GitHub account (or organisation) that will host the registry.
- The `gh` CLI authenticated (`gh auth status`).
- Basic familiarity with GitHub Actions.

---

## Step 1 — Fork the canonical registry

```sh
gh repo fork forgetthefrets/emanon-registry --clone --fork-name my-league-registry
cd my-league-registry
```

This creates `https://github.com/<your-org>/my-league-registry` and clones it locally.

> **Tip:** Set the repository visibility to **private** if you want the league to be
> closed:
>
> ```sh
> gh repo edit --visibility private
> ```
>
> Note that `head_commit` CI checks make outbound HTTPS calls to each player's
> universe repo.  Players' universe repos must be reachable from GitHub Actions
> runners — either public or reachable via the same GitHub org.

---

## Step 2 — Configure CI policies

Open `.github/workflows/validate.yml`.  Customise the checks to match your league's
rules.  Common customisations are shown below.

### 2a — Minimum snapshot count

Add a policy check step after schema validation:

```yaml
- name: Enforce minimum snapshot count
  run: |
    for f in $(git diff --name-only origin/main...HEAD -- 'entries/*.json'); do
      count=$(jq '.snapshot_count' "$f")
      if [ "$count" -lt 5 ]; then
        echo "❌  $f: snapshot_count is $count (minimum: 5)"
        exit 1
      fi
    done
```

Change `5` to whatever minimum you want your league to require before a universe
can be listed.

### 2b — Required tags

Require at least one tag from a permitted set:

```yaml
- name: Enforce required tags
  run: |
    ALLOWED='["solo","duo","squad","league-s1"]'
    for f in $(git diff --name-only origin/main...HEAD -- 'entries/*.json'); do
      tags=$(jq -c '.tags' "$f")
      overlap=$(jq -n --argjson allowed "$ALLOWED" --argjson tags "$tags" \
        '($allowed | inside($tags)) or any($tags[]; . as $t | $allowed | index($t) != null)')
      if [ "$overlap" = "false" ]; then
        echo "❌  $f: must include at least one of: $ALLOWED"
        exit 1
      fi
    done
```

### 2c — Turn off remote HEAD verification (offline leagues)

If your league's universe repos are private or not reachable from GitHub Actions,
comment out or remove the `Remote reachability + HEAD commit` step in the workflow.
You will be trusting entry submitters to keep `head_commit` accurate.

```yaml
# - name: Remote reachability + HEAD commit
#   run: ...
```

### 2d — Allow only known submitters (closed league)

Gate PRs to a list of approved GitHub usernames:

```yaml
- name: Check submitter allowlist
  run: |
    ALLOWED='["alice","bob","carol","dave","eve"]'
    actor="${{ github.actor }}"
    ok=$(echo "$ALLOWED" | jq --arg u "$actor" 'index($u) != null')
    if [ "$ok" = "false" ]; then
      echo "❌  $actor is not in the allowed submitters list."
      exit 1
    fi
```

---

## Step 3 — Add a league-specific values.json validator (optional)

Your league may want to enforce that all universes share certain `values.json` defaults
— for example, requiring `set_k ≥ 3` or mandating a specific `scrambling_rounds` value.

Create a validation script at `scripts/validate-league-values.sh`:

```sh
#!/usr/bin/env bash
# Validates that the universe's values.json satisfies league defaults.
# Usage: validate-league-values.sh <git_url> <head_commit>
set -e
GIT_URL="$1"
HEAD="$2"

# Fetch just the values.json from the remote commit
VALUES=$(git archive --remote="$GIT_URL" "$HEAD" ".gitverse/values.json" \
  | tar -xO 2>/dev/null || echo "{}")

if [ -z "$VALUES" ] || [ "$VALUES" = "{}" ]; then
  echo "⚠️   Could not fetch values.json from $GIT_URL at $HEAD — skipping league check"
  exit 0
fi

# Example: require set_k between 3 and 17
SET_K=$(echo "$VALUES" | jq -r '.set_k // empty')
if [ -n "$SET_K" ]; then
  if [ "$SET_K" -lt 3 ] || [ "$SET_K" -gt 17 ]; then
    echo "❌  values.json: set_k=$SET_K is outside league range [3, 17]"
    exit 1
  fi
fi

echo "✅  values.json satisfies league constraints"
```

Add a CI step in `validate.yml` that calls this script for each changed entry:

```yaml
- name: League values.json policy
  run: |
    for f in $(git diff --name-only origin/main...HEAD -- 'entries/*.json'); do
      GIT_URL=$(jq -r '.git_url' "$f")
      HEAD=$(jq -r '.head_commit' "$f")
      bash scripts/validate-league-values.sh "$GIT_URL" "$HEAD"
    done
```

---

## Step 4 — Publish your registry URL to league members

Tell your league members the URL of your registry fork:

```
https://github.com/<your-org>/my-league-registry
```

Each player adds this to their `~/.config/emanon/config.toml`:

```toml
[registry]
url = "https://github.com/<your-org>/my-league-registry"
owner_pubkey = "THEIR_OWN_PUBKEY"
universe_name = "their-universe-name"
git_remote = "origin"
```

With this in place, all `emanon registry` commands will use your league registry by
default.

---

## Step 5 — Players publish to your registry

Players run the same command as for the canonical registry:

```sh
cd their-universe
emanon registry push
```

The push goes to your fork.  Your CI runs your custom policy checks.  You (or a
trusted co-maintainer) merge the PR once CI is green.

Players can also push to a specific registry without changing their config:

```sh
emanon registry push --registry https://github.com/<your-org>/my-league-registry
```

---

## Step 6 — Players browse the league registry

```sh
# Sync the registry locally
emanon registry pull --registry https://github.com/<your-org>/my-league-registry

# List all universes
emanon registry list --registry https://github.com/<your-org>/my-league-registry

# Add a league member's universe as a git remote
emanon registry add-remote alice-prime --registry https://github.com/<your-org>/my-league-registry

# Merge!
emanon merge alice-prime/main
```

---

## Maintenance

### Updating the schema

When the canonical `entry.schema.json` is updated (new optional fields, constraint
relaxations), pull the changes into your fork:

```sh
git remote add upstream https://github.com/forgetthefrets/emanon-registry
git fetch upstream
git merge upstream/main
git push origin main
```

Review any conflicts in `.github/workflows/validate.yml` — your league-specific
steps may need adjusting.

### Removing a universe

A player can open a PR deleting their `entries/<name>.json`.  You merge it.  No CI
check required for deletions.

### Transferring ownership

To hand the registry to a different GitHub user or org:

```sh
gh repo transfer my-league-registry new-owner
```

Players update their `config.toml` `url` field to the new location.

---

## Example: five-player league setup

Here is a concrete end-to-end example for a league of five players: Alice, Bob,
Carol, Dave, and Eve.  Alice runs the registry.

**Alice sets up the registry:**

```sh
gh repo fork forgetthefrets/emanon-registry --clone --fork-name alliance-registry
cd alliance-registry
gh repo edit --visibility private
# Add the submitter allowlist to validate.yml (see Step 2d above)
# Add minimum snapshot_count = 3 policy (see Step 2a above)
git add .github/
git commit -m "Add league policies: submitter allowlist + min 3 snapshots"
git push origin main
```

**Alice shares the URL:** `https://github.com/alice-org/alliance-registry`

**Each player (Bob through Eve) updates their config:**

```toml
# ~/.config/emanon/config.toml
[registry]
url = "https://github.com/alice-org/alliance-registry"
owner_pubkey = "THEIR_PUBKEY"
universe_name = "their-name"
git_remote = "origin"
```

**Bob publishes his universe:**

```sh
cd bob-universe
emanon snapshot -m "league launch — snapshot 3"
git push origin main
emanon registry push
# → opens PR at alice-org/alliance-registry
```

**Alice reviews and merges the PR** after CI passes.

**Carol discovers Bob:**

```sh
emanon registry pull
emanon registry list
# NAME         OWNER      SNAPSHOTS  TAGS
# bob-prime    2WqMzj...  3          league-s1

emanon registry add-remote bob-prime
emanon merge bob-prime/main
# → conflict negotiation or auto-resolve
```

---

## Troubleshooting

**`gh pr create` fails with "repository not found"**
Make sure you have write access to the registry fork (or that you have forked the
fork under your own account before running `emanon registry push`).

**CI step "Remote reachability" fails for private universe repos**
Either make the universe repos public, or remove the reachability step from your
custom workflow (see Step 2c).

**"submitter not in allowlist" CI failure**
Add the player's GitHub username to the `ALLOWED` array in your `validate.yml`.

**Player accidentally pushes to canonical registry instead of league registry**
They need to add `--registry` to the push command, or update `url` in their config.

---

## What's next

- **Publish your universe:** see [registry-walkthrough.md](registry-walkthrough.md)
- **Schema reference:** see [registry-schema.md](registry-schema.md)
- **Join the canonical registry:** push without `--registry` once you want to go public
