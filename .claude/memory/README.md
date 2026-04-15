# Shared Claude Code Memory

This directory is the authoritative source of Claude Code memories for this repo. Tracking memories in-repo keeps them synchronised across machines — without this, each machine accumulates its own memory store (overlapping in time, separate in space).

## How Claude Code finds these

Claude Code loads memories from a project-scoped path under the user's home dir:

```
~/.claude/projects/<repo-path-slug>/memory/
```

For this repo on this host the slug happens to be `-Users-darcythomas-alpha-workspace-collatz`, so the read path is:

```
~/.claude/projects/-Users-darcythomas-alpha-workspace-collatz/memory/
```

We link that path to this directory so the repo is the single source of truth.

## One-time setup on a new machine

```sh
# from the repo root
SLUG="$(pwd | sed 's|/|-|g')"          # e.g. -Users-darcythomas-alpha-workspace-collatz
TARGET="$HOME/.claude/projects/$SLUG"
mkdir -p "$TARGET"

# if a memory dir already exists there, move it aside first — review and merge manually
[ -e "$TARGET/memory" ] && mv "$TARGET/memory" "$TARGET/memory.pre-link-backup.$(date +%s)"

ln -s "$(pwd)/.claude/memory" "$TARGET/memory"
```

After that, Claude Code reads and writes through the symlink; edits hit `<repo>/.claude/memory/` directly. Commit changes the normal way. Other machines that have done the same setup see new memories on their next `git pull`.

## Contents

- `MEMORY.md` — the index Claude always loads. One line per memory.
- `<type>_<slug>.md` — individual memories. Types in use: `feedback`, `project`, `user`.

If anything looks outdated or wrong, edit the file directly — it's plain Markdown. Claude picks up edits next session.
