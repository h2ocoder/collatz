#!/usr/bin/env bash
# Install the Emanon skill so Claude Code can discover it.
# Run from anywhere — script resolves its own directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${HOME}/.claude/skills/emanon"

if [ -e "$TARGET" ]; then
  echo "Skill already installed at $TARGET"
  exit 0
fi

mkdir -p "${HOME}/.claude/skills"
ln -s "$SCRIPT_DIR" "$TARGET"
echo "Emanon skill installed: $TARGET -> $SCRIPT_DIR"
echo "Claude will now recognize 'emanon' as a skill."
