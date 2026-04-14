#!/usr/bin/env bash
# emanon/tests/two-player-local.sh
# End-to-end two-player local play test for Emanon (M2.3 — ALPHA-38).
#
# Exercises the full M0–M2 stack:
#   • Two universes initialise independently (emanon init)
#   • Both write conflicting region files with controlled genus stamps
#   • Bob merges alice — same-genus file auto-resolves via hybrid merge;
#     two unrelated-set conflicts are deferred to negotiation
#   • emanon negotiate --non-interactive resolves conflicts:
#       - regions/beta/conflict.txt → contract
#       - regions/delta/fork.txt    → fork
#   • Final state: merge commit (2 parents), clean working tree,
#     contract file in contracts/, fork branch + ref in forks/
#
# Prerequisites:
#   • `emanon` binary must be in PATH (or set EMANON=/path/to/binary)
#   • git must be in PATH
#
# Usage:
#   bash emanon/tests/two-player-local.sh
#   EMANON=/path/to/emanon bash emanon/tests/two-player-local.sh

set -euo pipefail

EMANON="${EMANON:-emanon}"

echo "==========================================="
echo " Emanon two-player local play test (M2.3)  "
echo "==========================================="
echo "Using binary: $(command -v "$EMANON" 2>/dev/null || echo "NOT FOUND — will fail")"
echo ""

# ─── Temporary workspace ──────────────────────────────────────────────────────

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
cd "$WORK_DIR"

# Set git identity globally in this environment so emanon init / snapshot work.
# (CI runners often have no global git config.)
export GIT_AUTHOR_NAME="Emanon Test"
export GIT_AUTHOR_EMAIL="test@emanon.local"
export GIT_COMMITTER_NAME="Emanon Test"
export GIT_COMMITTER_EMAIL="test@emanon.local"

# ─── Helpers ─────────────────────────────────────────────────────────────────

fail() {
    echo ""
    echo "FAIL: $*" >&2
    exit 1
}

pass() {
    echo "  ✓ $*"
}

# Write a text file with an explicit genus stamp appended.
# Genus stamp uses the JSON format parsed by parse_genus_stamp() in main.rs.
#
# Usage: write_genus_file <path> <content> <set_k> <oddity_s> <index_i> <writer> <snapshot>
write_genus_file() {
    local fpath="$1" content="$2" set_k="$3" oddity_s="$4" index_i="$5"
    local writer="$6" snapshot="$7"
    mkdir -p "$(dirname "$fpath")"
    printf '%s\n# emanon-genus: {"set_k": %d, "oddity_s": %d, "index_i": %d, "writer": "%s", "snapshot": %d}\n' \
        "$content" "$set_k" "$oddity_s" "$index_i" "$writer" "$snapshot" > "$fpath"
}

# ─── Alice setup ──────────────────────────────────────────────────────────────

echo "--- [1/5] Setting up alice's universe ---"
"$EMANON" init alice
(
    cd alice
    git config user.email "alice@example.com"
    git config user.name "Alice"

    # File A — shared orbit notes.
    # set_k=5, oddity_s=3 — same as bob's copy → driver will hybrid-merge (exit 0).
    write_genus_file \
        "regions/gamma/shared.txt" \
        "Alice: gamma orbit confirmed stable. Third moon has been charted." \
        5 3 7 "alice@example.com" 0

    # File B — beta settlement.
    # set_k=3, oddity_s=2 — different set_k AND different oddity_s from bob (set_k=7, s=5)
    # → driver exits 1 → deferred to negotiate → resolved by contract.
    write_genus_file \
        "regions/beta/conflict.txt" \
        "Alice: beta settlement. Population: 4200. Resources: iron, silicate." \
        3 2 4 "alice@example.com" 0

    # File C — delta colony.
    # set_k=13, oddity_s=9 — different set_k AND different oddity_s from bob (set_k=17, s=11)
    # → driver exits 1 → deferred to negotiate → resolved by fork.
    write_genus_file \
        "regions/delta/fork.txt" \
        "Alice: delta colony. Coordinates: 7.3N 42.1W. Established T+12." \
        13 9 11 "alice@example.com" 0

    "$EMANON" snapshot -m "alice: establishes gamma, beta, delta regions"
)
pass "Alice universe: 3 region files committed"

# ─── Bob setup ────────────────────────────────────────────────────────────────

echo ""
echo "--- [2/5] Setting up bob's universe ---"
"$EMANON" init bob
(
    cd bob
    git config user.email "bob@example.com"
    git config user.name "Bob"
    git remote add alice ../alice

    # File A — same set_k=5, oddity_s=3 as alice → Collatz driver: hybrid merge (exit 0).
    write_genus_file \
        "regions/gamma/shared.txt" \
        "Bob: gamma orbit confirmed. Bob's moon survey notes appended here." \
        5 3 7 "bob@example.com" 0

    # File B — set_k=7, oddity_s=5: different from alice's (set_k=3, s=2)
    # Both set_k and oddity_s differ → driver exits 1 → conflict.
    write_genus_file \
        "regions/beta/conflict.txt" \
        "Bob: beta settlement. Population: 3100. Resources: copper, water-ice." \
        7 5 9 "bob@example.com" 0

    # File C — set_k=17, oddity_s=11: different from alice's (set_k=13, s=9)
    # Both set_k and oddity_s differ → driver exits 1 → conflict.
    write_genus_file \
        "regions/delta/fork.txt" \
        "Bob: delta colony. Coordinates: 7.3N 42.1W. Bob's survey flags anomaly." \
        17 11 13 "bob@example.com" 0

    "$EMANON" snapshot -m "bob: establishes gamma, beta, delta regions"
)
pass "Bob universe: 3 region files committed"

# ─── Bob merges alice ─────────────────────────────────────────────────────────

echo ""
echo "--- [3/5] Bob merges alice/main ---"
(
    cd bob

    # emanon merge:
    #   - Fetches alice remote
    #   - Runs git merge --no-commit --no-ff alice/main
    #   - Collatz driver fires per .gitattributes for regions/**:
    #       regions/gamma/shared.txt  → same set_k=5 → hybrid merge → exit 0 (auto-resolved)
    #       regions/beta/conflict.txt → set_k 3 vs 7, s 2 vs 5 → exit 1 (conflict)
    #       regions/delta/fork.txt    → set_k 13 vs 17, s 9 vs 11 → exit 1 (conflict)
    #   - Writes .gitverse/pending-merge.json listing the 2 deferred conflicts
    "$EMANON" merge alice/main

    # Verify pending-merge.json was written
    PENDING=".gitverse/pending-merge.json"
    [ -f "$PENDING" ] \
        || fail "pending-merge.json not created — expected 2 conflicts"
    pass "pending-merge.json exists"

    # Expect exactly 2 conflict entries
    CONFLICT_COUNT="$(grep -c '"path"' "$PENDING" || true)"
    [ "$CONFLICT_COUNT" -eq 2 ] \
        || fail "expected 2 conflicts in pending-merge.json, got $CONFLICT_COUNT. Content: $(cat "$PENDING")"
    pass "pending-merge.json lists 2 conflicts"

    # Verify hybrid-merged shared.txt contains content from both players
    SHARED="regions/gamma/shared.txt"
    grep -q "same set_k" "$SHARED" \
        || fail "hybrid merge markers not found in $SHARED (driver may not have run)"
    grep -q "Alice:" "$SHARED" \
        || fail "alice's content missing from hybrid-merged $SHARED"
    grep -q "Bob:" "$SHARED" \
        || fail "bob's content missing from hybrid-merged $SHARED"
    pass "regions/gamma/shared.txt was hybrid-merged (contains both sides)"
)

# ─── Negotiate ────────────────────────────────────────────────────────────────

echo ""
echo "--- [4/5] Negotiating conflicts (non-interactive) ---"
(
    cd bob

    # Resolution plan:
    #   beta/conflict.txt → contract: document resource-sharing terms
    #   delta/fork.txt    → fork: alice's timeline diverges into a separate branch
    RESOLUTION_PLAN='[
  {
    "path": "regions/beta/conflict.txt",
    "resolution": "contract",
    "terms": "Alpha Compact: 50pct iron to alice, 50pct copper to bob, joint water-ice extraction"
  },
  {
    "path": "regions/delta/fork.txt",
    "resolution": "fork"
  }
]'

    echo "$RESOLUTION_PLAN" | "$EMANON" negotiate --non-interactive
)
pass "emanon negotiate --non-interactive completed"

# ─── Verify final state ───────────────────────────────────────────────────────

echo ""
echo "--- [5/5] Verifying final state of bob's universe ---"
(
    cd bob

    # 1. No unmerged paths in index
    UNMERGED="$(git diff --name-only --diff-filter=U 2>/dev/null || true)"
    [ -z "$UNMERGED" ] \
        || fail "unmerged paths remain after negotiate: $UNMERGED"
    pass "no unmerged paths"

    # 2. Working tree clean (no tracked modifications or staged changes uncommitted)
    DIRTY="$(git status --porcelain | grep -v '^??' | grep -v '^!!' || true)"
    [ -z "$DIRTY" ] \
        || fail "working tree not clean after merge commit:$(echo; echo "$DIRTY")"
    pass "working tree clean"

    # 3. HEAD is a merge commit (exactly 2 parents)
    PARENT_COUNT="$(git log -1 --format='%P' | wc -w | tr -d ' \t')"
    [ "$PARENT_COUNT" -eq 2 ] \
        || fail "HEAD is not a merge commit (got $PARENT_COUNT parent(s)); log: $(git log --oneline -3)"
    pass "HEAD is a merge commit with 2 parents"

    # 4. Contract file written in contracts/
    CONTRACT_COUNT="$(find contracts/ -maxdepth 1 -name '*.contract' | wc -l | tr -d ' \t')"
    [ "$CONTRACT_COUNT" -ge 1 ] \
        || fail "no .contract file in contracts/ — contract resolution may have failed (found: $(ls contracts/))"
    CONTRACT_FILE="$(find contracts/ -maxdepth 1 -name '*.contract' | head -1)"
    # Verify contract file contains the terms we supplied
    grep -q "Alpha Compact" "$CONTRACT_FILE" \
        || fail "contract file does not contain expected terms ('Alpha Compact'): $(cat "$CONTRACT_FILE")"
    pass "contract file written and contains expected terms: $(basename "$CONTRACT_FILE")"

    # 5. Fork branch created at FETCH_HEAD (alice's HEAD)
    FORK_BRANCH="$(git branch --list 'fork-*' | head -1 | tr -d ' *')"
    [ -n "$FORK_BRANCH" ] \
        || fail "no fork branch created (branches: $(git branch))"
    pass "fork branch created: $FORK_BRANCH"

    # 6. Fork ref file written in forks/
    FORK_REF_COUNT="$(find forks/ -maxdepth 1 -name '*.ref' | wc -l | tr -d ' \t')"
    [ "$FORK_REF_COUNT" -ge 1 ] \
        || fail "no .ref file in forks/ — fork resolution may have failed (found: $(ls forks/))"
    FORK_REF="$(find forks/ -maxdepth 1 -name '*.ref' | head -1)"
    grep -q "regions/delta/fork.txt" "$FORK_REF" \
        || fail "fork ref does not reference delta/fork.txt: $(cat "$FORK_REF")"
    pass "fork ref written: $(basename "$FORK_REF")"

    # 7. Merge commit trailers reference both resolved paths
    COMMIT_MSG="$(git log -1 --format='%B')"
    echo "$COMMIT_MSG" | grep -q "Resolved-path: regions/beta/conflict.txt" \
        || fail "merge commit missing trailer 'Resolved-path: regions/beta/conflict.txt'"
    echo "$COMMIT_MSG" | grep -q "Resolved-path: regions/delta/fork.txt" \
        || fail "merge commit missing trailer 'Resolved-path: regions/delta/fork.txt'"
    pass "merge commit trailers reference both resolved paths"

    # 8. Log summary
    echo ""
    echo "=== Bob's git log (last 5 commits) ==="
    git log --oneline -5
    echo ""
    echo "=== Bob's branches ==="
    git branch
)

echo ""
echo "==========================================="
echo " ✅  Two-player local play test PASSED      "
echo "==========================================="
