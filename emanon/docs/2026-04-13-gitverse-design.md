# Gitverse: Filesystem-Merge Multiverse Design

> **The game IS git.** Universes are repositories, snapshots are commits,
> forks are branches, contracts are signed commits, scars are merge commits,
> conflict resolution is `git merge` with a Collatz-aware driver. The
> multiverse is a federated distributed network of repos. Cross-universe
> observation is `git log`. Cross-universe interaction is `git merge`.
>
> Drafted 2026-04-13 from the session realizing that three decades of git
> tooling is already a physics engine for an information-theoretic
> multiverse. Emanon is the game that notices. Supersedes the
> [[2026-04-13-collatz-scrambling-protocol|Collatz Scrambling Protocol]]
> integer-log framing.

## The Reframe

We spent the session deriving an elaborate mechanic — universes as
filesystem trees, Merkle-hashed snapshots, three-way merges with Collatz
genus, contracts as byte-identical files across repos, forks as multiverse
branching — and then realized:

**Every one of those primitives is already built into git.**

| Gitverse concept | Git primitive |
|---|---|
| Universe | Repository / branch |
| Snapshot | Commit |
| Timeline / log | `git log` |
| Subtree / region | Directory |
| Artifact | File |
| Genesis | The initial commit |
| Fork | Branch or repo fork |
| Merge | `git merge` |
| Contract | Co-signed commit or merge commit with co-authors |
| Scar | Merge commit marked with conflict metadata |
| Host authority | Repo owner / maintainer |
| Entanglement | Shared commit ancestry |
| P-adic distance | Commits since `git merge-base` |
| Shared prefix depth | Length of common history |
| Observation | `git log other-remote -- path/` |
| Scan (cheap, shallow) | `git log --oneline -n K` |
| Probe (medium) | `git log -p` with filters |
| Entangle (persistent) | Adding a remote + `git fetch` on schedule |
| Compression (stellar) | $T^k$-driven file rewrite with bit destruction |
| Scrambling | Deterministic hash transform over diff |
| Values.json | `.gitverse/values.json` + merge driver config |
| Multiverse index | A shared remote publishing scrambled hashes |

The realization is not "use git as an implementation detail." It's that the
game's design *converges on git's design* because both are answering the
same question: **how do we represent divergent, hash-linked, mergeable
histories with causal integrity?**

Git answered it in 2005. The math you've been doing for Collatz papers 1-3
is about what happens when those same structures evolve under the map $T$.
Emanon is the game where players live inside that evolution.

## Why This Works

Three properties of git line up exactly with what the game needs:

1. **Merkle-hashed trees.** Every commit already hashes the entire tree
   bottom-up. Subtree equality is checkable in O(1) via hash comparison.
   The "Merkle hash at every folder, apply $T^k$ to each" step of the
   snapshot cycle is *a walk over the git object database*.

2. **Three-way merge is canonical.** Git has been doing base/ours/theirs
   merges for 20 years. The machinery for conflict detection,
   path-scoped resolution, and custom drivers via `.gitattributes` is
   battle-tested at planetary scale (every major software project).

3. **Distributed by design.** No central server. Each universe is a local
   repo; other universes are remotes you fetch from. This means Emanon is
   a **peer-to-peer 4X game by construction** — no backend, no hosting,
   no consensus protocol needed beyond what git already provides.

## Architecture

### The Minimum Viable Gitverse

Emanon's engine reduces to surprisingly little net-new code:

```
emanon-git/
  .git/                          # standard git, unmodified
  .gitverse/
    values.json                  # this universe's resolution preferences
    identity.key                 # player's signing key
    leverage.cache               # precomputed log-size, scar-count, etc.
    remotes.registry             # known universes and trust levels
  .gitattributes                 # registers the Collatz merge driver
  regions/                       # game-state files (player-shaped)
  contracts/                     # byte-identical files across signatories
  scars/                         # immutable records; append-only
  forks/                         # branch pointers + metadata
```

The engine consists of:

1. **A Collatz-aware merge driver** (`emanon-merge`), registered via
   `.gitattributes`:
   ```
   regions/**  merge=emanon-collatz
   contracts/** merge=emanon-contract
   scars/**     merge=emanon-append-only
   ```
   When `git merge` hits a conflict in a registered path, it invokes this
   driver with base/ours/theirs. The driver computes each side's genus,
   checks leverage, applies resolution rules, and writes the merged file
   or refuses with a conflict marker that triggers the negotiation UI.

2. **A snapshot hook** (`post-commit` or scheduled):
   - Walks the just-committed tree
   - Hashes each folder (git already did this — just read object IDs)
   - Applies $T^k$ to each hash
   - Publishes scrambled hashes to the multiverse index (a designated
     remote or a DHT)

3. **A leverage calculator** — pure `git log` operations:
   - Log size = `git log --oneline | wc -l` (or more sophisticated)
   - Scar count = `git log scars/.. | count merge commits`
   - Contract count = files in `contracts/` that are byte-identical in at
     least one remote's copy
   - Fork ancestry = depth of current branch in the multiverse graph

4. **A negotiation UI** — this is the only *actually new* software.
   Everything under the hood is git plumbing. The UI shows pending
   merges, leverage scores, proposal drafting, contract signing, fork
   declaration.

5. **A registry / multiverse index** — a shared git repo (or a DHT) where
   each universe publishes:
   - Its HEAD commit SHA
   - Its scrambled-hash tree
   - Its `values.json`
   - Its public signing key
   - Metadata about contracts it claims to hold

That's it. Five components, and most of the hard problems (conflict
detection, Merkle structure, distribution, identity via GPG, history
integrity) are solved by git itself.

### The merge driver in pseudocode

```python
# emanon-merge: invoked by git on conflict
def merge(base_path, ours_path, theirs_path, output_path):
    base = read(base_path)
    ours = read(ours_path)
    theirs = read(theirs_path)

    # Extract genus stamps from file metadata
    g_ours = ours.genus     # (Set_k, oddity_s, index_I, writer_sha, write_step)
    g_theirs = theirs.genus

    # Compute leverage from git history
    lev_ours = leverage_from_git(g_ours.writer_sha)
    lev_theirs = leverage_from_git(g_theirs.writer_sha)

    # Apply Collatz resolution rules
    if g_ours.set_k == g_theirs.set_k:
        # Same set: merge both edits, file becomes hybrid
        merged = hybrid_merge(ours, theirs)
        write(output_path, merged)
        return 0

    if g_ours.oddity_s == g_theirs.oddity_s:
        # Same oddity, different k: partial merge with attenuation
        beta = bit_destruction(g_ours.oddity_s)
        merged = weighted_merge(ours, theirs, beta)
        write(output_path, merged)
        return 0

    # Unrelated sets: defer to negotiation
    mark_conflict(output_path, g_ours, g_theirs, lev_ours, lev_theirs)
    return 1   # signals git that resolution needs player input
```

`dropping_genus`, `bit_destruction`, `T^k` are all existing functions in
`collatz/core.py` and `collatz/dropping.py`. The driver is ~200 lines.

## What Comes Free

This is a partial list. Each of these is a feature you'd otherwise have to
design and build; git gives you all of them out of the box.

### Gameplay primitives

- **`git bisect`** — detective mechanic. "When did this contamination enter
  my universe?" Players bisect their own history to find root causes.
- **`git cherry-pick`** — theft / extraction mechanic. Grab one specific
  change from another universe without merging everything. Spy gameplay.
- **`git rebase`** — temporal magic. Rewriting your own history is an
  ability available to some factions. Extremely powerful, extremely
  detectable if others have fetched you. The "unreliable narrator" faction
  has this as superpower.
- **`git blame`** — full causal attribution. Who wrote this line? Perfect
  for investigating betrayal, detecting false-flag edits, or sourcing lore.
- **`git tag`** — permanent immutable markers. Historical events, artifact
  names, epoch boundaries. Tags replace what you'd otherwise call "lore."
- **Submodules** — universes containing universes. Nested cosmologies,
  worlds-within-worlds. Trivially modeled as git submodules.
- **Signed commits & GPG** — unforgeable authorship. Reputation is real
  cryptographic identity. Contracts are literally cryptographically
  signed.
- **`.gitattributes` merge drivers** — per-path custom resolution. Your
  entire Collatz conflict-resolution system is ONE file of config plus
  merge drivers.
- **Hooks** — `pre-commit`, `post-merge`, `post-receive`, etc. The
  engine's event system, built in.
- **`git reflog`** — players can see their own recent history even across
  branch switches. A built-in "undo" limited by time.
- **Shallow clones & partial fetches** — observation cost literally
  controlled by fetch depth. Cheap scan = `git fetch --depth=3`.

### Infrastructure primitives

- **Federation.** Any git host works — GitHub, GitLab, Codeberg, self-hosted
  gitea. You have no hosting burden. Players choose where their universe
  lives.
- **Offline play.** Git is local-first. Play on your commute, sync when you
  connect. True async strategy.
- **No cheating via save-scumming.** Every commit is hash-chained. You can't
  edit history without breaking the chain; the break is detectable by
  anyone who fetched you.
- **GUI already exists.** SourceTree, GitKraken, Magit, VS Code's git
  panel, GitButler — every one is potentially a gitverse client. IDE
  integration is free.
- **Diff tools exist.** Any diff viewer shows you what changed in a
  universe. Meld, difftastic, GitHub's web UI — all work.
- **Replays are free.** The full history of a universe is literally its
  `git log`. Watch a universe evolve by stepping through commits.
- **Mods are forks.** Someone disagrees with the canonical merge driver?
  They fork it. Community rulesets are community-forked merge drivers.

## Implications

### For the player

**Version control literacy becomes a gameplay skill.**

Players who know git play better. Players who don't learn git through
play. The game teaches a genuinely useful real-world skill as a side effect
of being fun. This is an extraordinarily strong pedagogical hook — git is
notoriously hard to learn, and "learn git by playing a space game" is a
better introduction than any tutorial ever written.

### For the product

- **The game exports.** When you finish playing, the universe is a repo.
  Share it, archive it, publish papers about it. A competitive tournament
  could publish every participant's universe for post-game analysis.
- **Mods are trivial.** Change the merge driver, fork the tooling, publish
  your own. Gitverse becomes a platform, not a product.
- **Distribution is trivial.** `git clone emanon-starter && emanon play`.
  No installer, no DRM, no storefront dependence.

### For speedrunning and emergent communities

- **`No Force Push` is a speedrun category.** (Funny now; will be real later.)
- **`GPG-Signed-Only` is a tournament ruleset.** Authenticity-maxxing play.
- **Branching trees are leaderboards.** Most-forked universe. Deepest
  ancestry. Most signed contracts. All queryable by git commands on public
  repos.
- **Archaeological gameplay.** Find long-abandoned universes, fork them,
  resurrect them. Dead multiverses are public record.

## Universe Layout

```
universe-repo/
  .git/                          # standard git
  .gitverse/
    values.json                  # resolution preferences
    identity.key                 # signing key (not committed)
    leverage.cache               # derived from git history
  .gitattributes                 # registers merge drivers
  regions/                       # spatial layer — folders are places
    alpha/
      sector-01/
        events.log
        objects/
          artifact-42.json
      sector-02/
  contracts/                     # byte-identical across signatories
    tom-bob-alice-planet-xyz.contract
  scars/                         # immutable records, append-only
    2026-Q3-alpha-sector-03-battle-loss.scar
  forks/                         # branch pointers + metadata
    fork-alice-rebellion.ref
```

The top-level structure is canonical. Engine enforces it via git hooks and
merge drivers. Subtree organization inside `regions/` is player-shaped.

### values.json example

```json
{
  "conflict_preference": "contract",
  "fork_readiness": "high",
  "battle_threshold": 0.3,
  "host_authority_mode": "partition",
  "contract_defaults": {
    "min_duration_snapshots": 10,
    "auto_renew": false
  },
  "signatures": {
    "require_gpg": true,
    "trusted_keys": ["..."]
  }
}
```

Consulted by the merge driver when this universe is party to a conflict.

## The Snapshot Cycle, Git-Native

```
Turn phase (between snapshots):
  - Players edit files in their working tree
  - Local game dynamics may trigger $T^k$ on specific files (star burns)
  - Object interactions write genus-stamped metadata to object JSON

Snapshot boundary:
  1. git add . && git commit -m "snapshot N" --gpg-sign
  2. post-commit hook:
     - walks the tree object
     - scrambles each tree's SHA via $T^k$
     - writes scrambled_hashes.json
     - git push to multiverse registry remote
  3. git fetch from all known remotes
  4. for each pending merge from another universe:
       git merge <remote>/<branch>
       → Collatz merge driver runs
       → conflicts surface in negotiation UI
  5. for each resolved merge:
       git commit (signed, genus-stamped) finalizing the merge
```

Every step is either a native git operation or a short shell script wrapping
one. There is no separate "game engine" in the classical sense — there's
git, and there's the Collatz-aware merge policy.

## Merge Resolution Paths (git-native)

### Battle

Implemented as: both parties run scripts that commit "force" blobs derived
from their log history. The merge driver evaluates which side's forces
exhaust first under $T^k$ iteration. Loser's changes are reverted. The
merge commit itself becomes a **scar** — its message records the battle
outcome.

```bash
emanon battle --commit-bits 1024 --target <other-universe>
# writes a battle blob, commits it, pushes to contested branch
# merge driver resolves by running T^k on both sides' blobs
```

### Contract (diplomacy)

Implemented as: both parties agree on a contract file, each independently
writes it to `contracts/<name>.contract`, each signs it with GPG, each
pushes to the other. Byte-identical signed files = valid contract.

```bash
emanon contract draft --with <other-universe> --terms terms.json
emanon contract sign <pending-contract>
# results in git commits on both sides with identical contract file
```

Breach = any subsequent commit that modifies the contract file to no
longer be byte-identical. Detected automatically at next fetch.

### Fork

Implemented as: `git checkout -b fork-name` plus a pointer commit. The new
branch IS the forked universe. It can be pushed to a new remote to give it
a separate identity, or kept local for stealth forks.

```bash
emanon fork --reason "disagreement with Tom on planet-xyz"
# creates branch, writes forks/fork-<timestamp>.ref, updates values.json
```

Multiverse graph is the **graph of all branches across all remotes**. Git
already has the primitives to query this.

## Leverage from Git History

Leverage is a pure function of the git object database:

| Source | Query |
|---|---|
| Log size | Total blob size reachable from HEAD |
| Commits accumulated | `git rev-list --count HEAD` |
| Genus at write-step | `dropping_genus(commit_count)` at each write |
| Scar burden | `git log scars/` count + recency weighting |
| Contract count | Files in `contracts/` byte-identical in ≥1 remote |
| Fork ancestry | Depth in multiverse branch graph |
| Signing reputation | Fraction of commits GPG-signed by trusted keys |
| Host multiplier | +α if contest is on a path owned by this universe |

Leverage is public — anyone can clone your repo and compute it. No hidden
state. This is a **deliberate design choice** inherited from git: in the
gitverse, there is no fog of war about raw capability. Strategy is about
what you *do* with known resources, not what you hide.

(Asymmetric info can still enter via private branches never pushed — the
"secret arsenal" mechanic maps to local-only branches you haven't shared.)

## Signing and Identity

Every commit is GPG-signed. This is not optional; the engine rejects
unsigned commits.

Implications:

- **Identity is cryptographic.** Your universe is your signing key.
- **Forgery is hard.** Anyone claiming to be you without your key fails
  signature verification.
- **Trust is transitive.** A signs B's key, B signs C's key, players can
  build webs of trust à la PGP.
- **Contracts are self-proving.** A contract signed by Alice's published
  key is unforgeable evidence of her commitment.
- **Reputation persists.** Your key follows you across games, across
  tournaments, across the decades. Your gitverse reputation is a public
  record. (This is either wonderful or terrifying depending on how you
  played last year.)

## Communication with Other Universes

All cross-universe communication is **git operations over some transport**:

- `git fetch <remote>` — sync another universe's state
- `git push <remote>` — publish your state for others to fetch
- `git merge <remote>/<branch>` — attempt to integrate another universe
- `git log <remote>/<branch> -- path/` — observe what happened in their
  specified subtree
- `git diff <remote>/<branch> path/` — see how they differ from you

Transport can be:
- **HTTPS/SSH** to git hosts (normal case)
- **Direct TCP** peer-to-peer (LAN play)
- **Tor hidden services** (clandestine universes)
- **Sneakernet** (bundle files on USB, `git bundle create`)

The game doesn't care. All transports yield the same commit DAG.

## Multiverse Registry

One shared git repo — the "registry" — tracks:
- Each known universe's name, HEAD SHA, and public key
- Each universe's scrambled-hash snapshot
- Cross-universe relationship metadata (contracts registered, scars
  recorded from the perspective of observers)

Anyone can clone the registry. Anyone can submit PRs to update their
own entry. The registry itself is just a git repo with a CI-enforced
schema — no special infrastructure.

Alternative: use a DHT (IPFS, Hyperbee, libp2p) for the registry if we
want fully serverless. First version should just be a hosted git repo
for simplicity.

## The Solo-to-MMO Continuum

One of the most consequential properties of the gitverse framing is that
there is no categorical distinction between single-player, co-op, and
massively-multiplayer modes. They are points along a continuum determined
entirely by **which remotes a player adds and which they push to**.

This is not a design that supports multiple modes. It's a design in which
"mode" is not a concept. The game executable is the same in every case.
No separate server binary, no matchmaker, no session manager, no lobby
system, no dedicated infrastructure — everything is git operations between
peers, and the peer count is whatever the player wants it to be, right
now, possibly different than it was an hour ago.

### The continuum

| Player situation | Setup | Experience |
|---|---|---|
| **Solo, offline** | `git init`; never add a remote | Hermit universe. Pure local play, nothing pushed anywhere. |
| **Solo, multiple timelines** | `git init`; use branches to explore forks | Roguelite with branching alternate histories. Dead runs are preserved branches, not lost saves. |
| **Solo, observable** | Push to a public remote; no one merges into you | Livestreaming via git. Spectators clone and read-only observe your history. |
| **Solo with bots** | Add a "bot" remote that runs scripted commits | AI opponents are just other repos with automated commit loops. |
| **Asynchronous duo** | Two repos, each fetches the other daily | Play-by-mail. Works across timezones. No one has to be online together. |
| **Synchronous duo** | Two repos, live fetch during a shared session | Traditional multiplayer feel. Still no server. |
| **Small co-op** | N repos, all fetching each other, small N (3-8) | Friend group play. Similar to a tabletop RPG campaign. |
| **Federated league** | Dozens of repos + a shared registry + shared `values.json` defaults | Tournament structure. Registry enforces rules; peers still do the work. |
| **Open MMO** | Hundreds/thousands of repos, public registry, permissive join policy | The universe is open. Anyone can `git clone` a starter repo and push to the registry. |
| **Bystander / journalist** | Fetch from many remotes, never push | You exist but cannot be acted upon. Observer mode. |
| **Archaeologist** | Clone abandoned universes (repos not updated in months) | Explore dead worlds. Play in them, fork them, resurrect them. |
| **Exile** | Fork to a new remote, sever connections to old remotes | Secession. Your universe continues but no longer interacts. |
| **Anonymous / clandestine** | Push to Tor hidden services or unlisted remotes | Dark-forest play. You exist but are hard to find. |

Every row is **the same binary, with different `git remote` configuration
and different player habits**. The game code does not branch on mode. It
branches on "is there a pending merge from a remote?" — a question git
already answers.

### Why this matters design-wise

**One codebase, one community.** Traditional games ship with separate
multiplayer and single-player systems, often maintained by different
teams, with single-player features eventually cut or ported poorly. In
gitverse, every feature works identically regardless of how many peers
you have. A new merge-driver feature benefits the solo player exploring
branches *and* the tournament with 40 participants.

**Zero friction to change scale.** A player who starts solo can invite a
friend at any time by sharing their repo URL. A tournament player who
wants to play solo just stops fetching. There is no "start a new
campaign" flow, no "convert save to multiplayer" flow, no incompatibility
between modes. The player's existing universe supports any scale
natively.

**Scale is an emergent property, not a design axis.** Nobody decides
"Emanon supports up to 32 players." The engine doesn't know about player
counts. A universe scales until git's own scalability limits bite, which
are *well* beyond any reasonable player count.

**Onboarding is trivial.** There's no "start a server" vs. "join a
server" choice. The only question is "do you want to connect your
universe to anyone else's?" — a social question, not a technical one.

### The setup flow at every scale

At every scale in the continuum, the setup is essentially:

```bash
# Solo (or starting anywhere):
emanon init my-world && cd my-world
emanon play

# Add a peer (anywhere along the continuum):
git remote add alice <her-repo-url>
git fetch alice
emanon interact alice/main

# Join a registered league:
git clone https://registry.emanon.gg/my-league-starter my-world
cd my-world
git remote add registry https://registry.emanon.gg/my-league
emanon play
```

The first two blocks work **regardless of whether you're currently a
hermit or a tournament player**. Adding a peer is the same operation
whether it's your first peer or your fortieth.

Compare to the typical multiplayer game: account creation, DRM
activation, server selection, region selection, lobby entry, friend
invites, NAT traversal, matchmaking queues, rank placement matches, etc.
Gitverse has none of these *because it doesn't need any of them* —
every one of those mechanisms exists to paper over the fact that the
game wasn't designed to be peer-to-peer from the ground up.

### Implications for the game's growth over time

Because there's no categorical distinction between modes, the
multiverse's long-term state is organic. Some universes will be:

- **Dormant** — no commits in months, explorable as ruins
- **Solo-active** — regular commits, but never pushed; invisible to others
- **Small-group-active** — regular commits shared among 3-5 peers
- **Publicly visible** — pushed to GitHub or a registry; anyone can fetch
- **Registry-participating** — publishing to a shared registry with rules
- **Tournament-bound** — temporarily operating under tournament rules

And crucially, **a single universe can move between these categories
over its lifetime** without any engine intervention. A solo run that
becomes fun gets pushed to a public remote. A tournament universe gets
forked for solo replay after the tournament ends. A dormant universe
gets resurrected when a new player finds it.

The multiverse grows like a forest, not like a database. Individual
universes thrive, branch, die, or get colonized by scavengers. The
ecosystem persists even as individual universes don't.

### Save files and replays

There are no save files. There is no "replay" feature. Both are
subsumed by git:

- **Save** is every commit. Every snapshot is automatically a save.
- **Save-scum** is constrained by `git reflog` — you can rewind within
  a time window, and only along a path the engine records. The reflog's
  natural decay *is* the save-scum tax.
- **Replay** is `git log -p`. Any universe's complete history is
  playable frame-by-frame with any git tool.
- **Sharing a moment** is sharing a commit SHA. "Hey look at my world
  at commit abc123" and the other player can clone and `git checkout abc123`
  to see exactly that state.
- **Branching from a moment** is `git checkout -b`. Any commit in any
  universe can be branched from, producing a new universe rooted at
  that state. This is trivially free. **Any played game is available
  as a starting position for future play.**

### The "bring your own substrate" principle

Because a universe is *just a git repo*, nothing stops players from
bringing their own substrate:

- **Use your existing GitHub.** Your universe lives at
  `github.com/you/my-world` like any other repo. Familiar UI, familiar
  workflow, no new account to create.
- **Use an existing game's repo.** A novel-in-progress, a software
  project, a research codebase — install the merge driver and
  `values.json` and it becomes a gitverse universe overlaid on your
  real work.
- **Use dead repos.** Abandoned open-source projects are playgrounds.
  Fork them, install the overlay, play in their commit history as
  "dead worlds."
- **Use corporate repos.** With permission (!), a company's internal
  codebase could become a gitverse universe as a team-building
  exercise. The merge conflicts of your sprint become political
  events.

This is wildly unhinged and also entirely possible. Emanon is not just a
game; it's a **mode of looking at git repos** that surfaces their
political topology.

### Cost and infrastructure

Because the game is distributed and there's no central authority:

| Cost category | Traditional game | Gitverse |
|---|---|---|
| Backend servers | High (scaling, 24/7 uptime) | Zero (uses existing git hosts) |
| Account system | Required (email, password, 2FA) | Zero (GPG keys are identity) |
| Matchmaking | Required | Zero (peers find each other via registry or word of mouth) |
| Anti-cheat | Server-side validation | Zero (cryptographic integrity enforced by git + signed commits) |
| Save-file migration | Required (breaking changes) | Handled by git and merge drivers |
| Regional servers | Required (latency) | Not applicable (commits are async) |
| DDoS mitigation | Required | Not applicable (no central target) |
| Persistent world cost | Continuous | Only during commits + fetches |

The operational cost of running the game's *entire multiverse* is
approximately the cost of running a small git repository at a registry
host. That's near-zero compared to even the smallest traditional
multiplayer game.

This creates the possibility of **player-run leagues with zero operator
cost**. A group of players can start a federated league by agreeing on
a registry repo and some rules. The league persists as long as any
player still pushes to the registry. There is no "server shutting down"
event — the game dies only when its community does.

### Solo play is first-class, not an afterthought

A large number of multiplayer games have bad single-player modes. They're
retrofits, they lack depth, they exist to tutorialize the "real game"
(multiplayer). In gitverse, solo play is **structurally the primary mode**
— every other mode is solo play plus some remotes.

Solo gitverse has access to everything:

- Fork a branch to explore alternate strategies
- `cherry-pick` between branches to combine ideas
- `bisect` your own history to find turning points
- Tag historical moments for later review
- Use `git log -p` to replay your own development
- Branch endlessly to experiment
- Write and test your own merge drivers (modding)
- Fetch public universes and observe without interacting

A solo player has **more raw game mechanics available to them than a
networked player in any other 4X**, because the full git feature set is
available unconditionally.

### The emergent community shapes

When you remove the friction of mode-switching, players naturally form
new kinds of communities:

- **Gardeners** who tend long-running universes, occasionally inviting
  guests
- **Travelers** who add and drop remotes constantly, interacting with
  many universes briefly
- **Historians** who clone dormant universes and publish analyses
- **Duelists** who fork to private universes for 1v1 matches, then
  archive results
- **Cartographers** who maintain the registry's metadata, charting the
  multiverse graph
- **Forensicists** who investigate scar causes across universes
- **Mod authors** who fork the merge driver and publish alternative
  rulesets

None of these roles need engine support. They emerge because the game's
primitives are git primitives, and git is a medium that supports
arbitrary play around it.

## Worked Example: Tom, Bob, Alice, Planet XYZ

**Setup:**
- Tom's universe: `tom/emanon-world` on GitHub
- Alice's: `alice/emanon-world`
- Bob's: `bob/emanon-world`
- All three have each other as remotes
- Last common ancestor: commit `abc123` ("snapshot N")

**Between snapshots N and N+1:**
- Bob writes `regions/planet-xyz/continent-a/settlement.json` in his repo,
  commits it (genus stamp: Set_6, s=2)
- Alice writes `regions/planet-xyz/continent-a/settlement.json` in her
  repo, commits a *different* file (genus stamp: Set_13, s=5)
- Both push to their own remotes

**Snapshot N+1:**
- Tom fetches from Alice's and Bob's remotes
- Tom runs `git merge alice/main` and `git merge bob/main`
- Both merges hit conflict on `continent-a/settlement.json`
- Collatz merge driver activates:
  - Alice's genus: Set_13 (rare), s=5 (convergent) → high leverage
  - Bob's genus: Set_6 (common), s=2 → low leverage
  - Sets unrelated → defers to negotiation UI
- Tom's negotiation UI opens with proposals from both

**Between N+1 and N+2 — proposals:**
- Bob: "Battle. I commit 1024 bits."
- Alice: "Contract. I give Tom 20% of my next 10 compression yields in
  exchange for continent-a."
- Tom's `values.json` prefers contracts → inclined to accept Alice

**Snapshot N+2 — commitments:**
- Tom and Alice sign the contract. Both write
  `contracts/tom-alice-planet-xyz.contract` with identical content, both
  GPG-sign the commits, push.
- Tom invokes host authority: coalition with Alice.
- Tom+Alice combined leverage (public): ~1236
- Bob's leverage: 112
- Bob decides: battle is suicide; forks instead.
- Bob runs `emanon fork` — creates branch `bob-alt/main`, updates
  `forks/parent.ref`, pushes to new remote `bob-alt/emanon-world`.

**Snapshot N+3 — materialization:**
- Tom merges the contract. Final commit is a signed merge commit.
  `contracts/tom-alice-planet-xyz.contract` exists byte-identical in Tom's
  and Alice's repos. Alice's settlement.json is now in Tom's tree.
- `bob-alt/emanon-world` is a new universe in the registry. Bob's
  settlement.json is in *his new universe's* tree. He retains continent-a
  in the only world that matters to him.
- No battle scar. One contract signed. One fork in the multiverse graph.

**Registry state after N+3:**
- Three universes became four
- One new contract tracked
- No new scars
- Diplomatic reputations updated (Tom +1 contract, Alice +1 contract,
  Bob +1 fork-initiated)

Every operation above is a real git command. No game-specific database, no
custom sync protocol, no server-side state that isn't already a git repo.

## Open Questions

- **Snapshot cadence.** Is there a game-enforced minimum time between
  commits, or is it player-chosen? How does asynchronous play handle
  players who commit wildly different rates?
- **Multiverse graph visualization.** Who renders "the multiverse"? Is it a
  client that fetches all known remotes and draws the branch graph? A
  website? A dedicated IDE?
- **Trust bootstrapping.** How do new players find established universes to
  interact with? Initial registry, invitations, matchmaking?
- **Private universes.** Can you have a universe that exists but isn't in
  the public registry? Probably yes — analogous to private repos.
- **Rebase as cheating?** `git rebase` rewrites history. Is it allowed? If
  so, under what conditions? Perhaps only if no other universe has
  fetched you since the rebased range. The engine could enforce this by
  comparing your local history to what others have fetched.
- **Force-push handling.** Probably forbidden by hook/enforcement. But
  maybe some factions have it as a special power.
- **Signing key loss = permadeath?** If a player loses their signing key,
  their universe is orphaned. Recovery mechanics?
- **Registry schema evolution.** How does the multiverse-wide schema
  upgrade? Same problem as real distributed systems — hard.
- **Commits-per-turn economy.** Does the game impose a commit rate limit
  to prevent spam? Or is throughput constrained by git's own
  characteristics?
- **Git-specific operations as mechanics.** Should `bisect`, `cherry-pick`,
  `rebase`, `reflog` each become explicit game abilities with cost and
  restriction, or just be available as raw git commands players can run
  for strategic advantage?

## Relationship to Prior Docs

This doc supersedes:
- [[2026-04-13-collatz-scrambling-protocol|Collatz Scrambling Protocol]] —
  integer-log version; preserved for the 2-adic determinism insight that
  grounds shared-prefix logic
- The unwritten "filesystem-merge-multiverse-design" — this is that doc,
  with gitverse as primary framing rather than implementation note

Still relevant:
- [[2026-04-13-multiverse-ontology-design|Multiverse Ontology]] — hex=
  universe, Eisenstein lattice; maps to repo adjacency graph
- [[2026-04-13-game-mechanics-design|Game Mechanics]] — player experience
  and UX
- [[Merge & Governance]] — existing spec draft; now subsumed by "git merge"
- [[Event Schema & Log]] — individual event-to-file encoding

## Summary

The gitverse is the realization that **Collatz is to git what thermodynamics
is to chemistry**: the underlying irreversible process that makes structured
computation possible. Git gives us the *structure* of a mergeable, forkable,
hash-linked multiverse. Collatz gives us the *dynamics* — how information
destroys and scrambles inside that structure, and why it must.

Emanon is the game that puts players inside this space, with the Collatz
merge driver as the rule of interaction and the three resolution paths
(battle, contract, fork) as the political interface.

You play by committing. You observe by fetching. You fight by merging.
You ally by signing. You escape by branching.

You can play this game today, with tools you already have installed.
