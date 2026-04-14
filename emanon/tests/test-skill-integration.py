#!/usr/bin/env python3
"""
Emanon Skill Integration Test
==============================

Tests that a Claude agent, given the emanon skill context, correctly drives
a complete play session by invoking commands in the expected order.

Usage
-----
    export ANTHROPIC_API_KEY=your-key-here
    python emanon/tests/test-skill-integration.py

Requirements
------------
    pip install anthropic

Optional (for filesystem assertions)
--------------------------------------
    - emanon binary on $PATH  → actual filesystem state is verified
    - Without it              → only command-ordering is verified

Exit codes
----------
    0  All assertions passed
    1  One or more assertions failed
    2  Setup error (missing API key, import failure, etc.)
"""

import os
import sys
import json
import re
import subprocess
import tempfile
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(2)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# Locate skill files
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # emanon/tests -> emanon -> repo root
SKILL_DIR = REPO_ROOT / "emanon" / "src" / "skill"

assert SKILL_DIR.exists(), f"Skill directory not found: {SKILL_DIR}"


def load_skill_context() -> str:
    """Load SKILL.md and all workflow files as a single context block."""
    parts = []

    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        parts.append(f"# SKILL.md\n\n{skill_md.read_text()}\n")

    for wf_file in sorted((SKILL_DIR / "workflows").glob("*.md")):
        parts.append(f"# workflows/{wf_file.name}\n\n{wf_file.read_text()}\n")

    ref_dir = SKILL_DIR / "reference"
    if ref_dir.exists():
        for ref_file in sorted(ref_dir.glob("*.md")):
            parts.append(f"# reference/{ref_file.name}\n\n{ref_file.read_text()}\n")

    return "\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Test prompt
# ---------------------------------------------------------------------------

TEST_PROMPT = (
    "Start a new universe named alpha-test, write a planet file in regions/alpha "
    "called planet.json with some starter content, snapshot it, "
    "then fork it for an alternate timeline."
)

EXPECTED_COMMAND_ORDER = [
    r"emanon\s+init\s+alpha-test",
    r"emanon\s+write\s+regions/alpha/planet\.json",
    r"emanon\s+snapshot",
    r"emanon\s+fork",
]

# ---------------------------------------------------------------------------
# Call the Claude API
# ---------------------------------------------------------------------------

def call_claude(skill_context: str, prompt: str, model: str = "claude-sonnet-4-5") -> str:
    """
    Call the Claude API with the skill as system context and the test prompt.

    Returns the full assistant response text.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_message = (
        "You are an AI assistant helping a player with the Emanon gitverse game. "
        "You have the following skill documentation available:\n\n"
        "<skill>\n"
        + skill_context
        + "\n</skill>\n\n"
        "When the user asks you to perform game actions, provide the exact "
        "`emanon` CLI commands they should run, in the correct order, with "
        "brief explanations. Format commands in ```bash code blocks."
    )

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_message,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def assert_command_order(response: str) -> list[str]:
    """
    Extract all bash code blocks from the response and verify that the
    expected commands appear in the correct order.

    Returns a list of failure messages (empty = all passed).
    """
    failures = []

    # Extract commands from ```bash blocks
    code_blocks = re.findall(r"```(?:bash|sh)?\n(.*?)```", response, re.DOTALL)
    all_commands = "\n".join(code_blocks)

    # Find position of each expected command pattern
    positions = []
    for pattern in EXPECTED_COMMAND_ORDER:
        match = re.search(pattern, all_commands)
        if match:
            positions.append(match.start())
        else:
            # Also check full response (agent might not use code blocks)
            match = re.search(pattern, response)
            if match:
                positions.append(match.start())
            else:
                failures.append(f"Expected command not found: pattern={pattern!r}")
                positions.append(-1)

    # Check ordering: positions should be monotonically increasing
    valid_positions = [p for p in positions if p >= 0]
    for i in range(1, len(valid_positions)):
        if valid_positions[i] <= valid_positions[i - 1]:
            failures.append(
                f"Commands out of order: "
                f"'{EXPECTED_COMMAND_ORDER[i]}' appeared before or at same position as "
                f"'{EXPECTED_COMMAND_ORDER[i - 1]}'"
            )

    return failures


def assert_filesystem_state(universe_dir: Path) -> list[str]:
    """
    If the emanon binary is available, run the actual commands in a temp
    directory and verify the resulting filesystem state.

    Returns a list of failure messages (empty = all passed).
    Skips silently if the emanon binary is not installed.
    """
    failures = []

    emanon_bin = shutil.which("emanon")
    if not emanon_bin:
        print("  [SKIP] emanon binary not on $PATH — skipping filesystem assertions")
        return failures

    tmpdir = Path(tempfile.mkdtemp(prefix="emanon-skill-test-"))
    try:
        env = os.environ.copy()

        # 1. Init
        result = subprocess.run(
            ["emanon", "init", "alpha-test"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(f"emanon init failed: {result.stderr}")
            return failures

        universe = tmpdir / "alpha-test"

        # 2. Write planet file
        planet_content = json.dumps({"name": "Alpha Prime", "type": "terrestrial", "population": 0})
        result = subprocess.run(
            ["emanon", "write", "regions/alpha/planet.json", planet_content],
            cwd=universe,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(f"emanon write failed: {result.stderr}")
            return failures

        # Assert: planet file exists
        planet_file = universe / "regions" / "alpha" / "planet.json"
        if not planet_file.exists():
            failures.append(f"planet.json not created at {planet_file}")
        else:
            content = planet_file.read_text()
            if "emanon-genus" not in content:
                failures.append("planet.json missing genus stamp")

        # 3. Snapshot
        result = subprocess.run(
            ["emanon", "snapshot", "-m", "Genesis — planet Alpha recorded"],
            cwd=universe,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(f"emanon snapshot failed: {result.stderr}")
            return failures

        # Assert: git log shows a snapshot commit
        git_log = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            cwd=universe,
            capture_output=True,
            text=True,
        )
        if "Genesis — planet Alpha recorded" not in git_log.stdout:
            failures.append(f"Snapshot commit not found in git log. Got: {git_log.stdout}")

        # 4. Fork
        result = subprocess.run(
            ["emanon", "fork", "--reason", "Alternate timeline for alpha-test"],
            cwd=universe,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            failures.append(f"emanon fork failed: {result.stderr}")
            return failures

        # Assert: forks/ directory has a file
        forks_dir = universe / "forks"
        fork_files = list(forks_dir.glob("*.json"))
        if not fork_files:
            failures.append("No fork metadata file created in forks/")
        else:
            fork_data = json.loads(fork_files[0].read_text())
            for required_key in ("fork_at", "branch", "reason", "timestamp"):
                if required_key not in fork_data:
                    failures.append(f"Fork metadata missing key: {required_key}")

        # Assert: fork branch exists in git
        git_branches = subprocess.run(
            ["git", "branch", "--list", "fork/*"],
            cwd=universe,
            capture_output=True,
            text=True,
        )
        if "fork/" not in git_branches.stdout:
            failures.append(f"Fork branch not found. git branch output: {git_branches.stdout}")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return failures


# ---------------------------------------------------------------------------
# Main test runner
# ---------------------------------------------------------------------------

def run_tests(model: str = "claude-sonnet-4-5") -> bool:
    """Run all tests. Returns True if all pass."""
    print(f"=== Emanon Skill Integration Test ===")
    print(f"Model: {model}")
    print(f"Prompt: {TEST_PROMPT!r}\n")

    # Load skill context
    print("Loading skill context...", end=" ", flush=True)
    skill_context = load_skill_context()
    print(f"OK ({len(skill_context)} chars)\n")

    # Call Claude
    print("Calling Claude API...", end=" ", flush=True)
    response = call_claude(skill_context, TEST_PROMPT, model=model)
    print("OK\n")

    print("--- Agent response (excerpt) ---")
    # Show first 1500 chars
    print(response[:1500])
    if len(response) > 1500:
        print(f"... [{len(response) - 1500} more chars]")
    print("--- End response ---\n")

    all_failures = []

    # Test 1: Command ordering
    print("Test 1: Command order (init → write → snapshot → fork)")
    order_failures = assert_command_order(response)
    if order_failures:
        for f in order_failures:
            print(f"  FAIL: {f}")
        all_failures.extend(order_failures)
    else:
        print("  PASS: All expected commands found in correct order")

    # Test 2: Filesystem state (skipped if binary unavailable)
    print("\nTest 2: Filesystem state assertions")
    fs_failures = assert_filesystem_state(Path("."))
    if fs_failures:
        for f in fs_failures:
            print(f"  FAIL: {f}")
        all_failures.extend(fs_failures)
    elif shutil.which("emanon"):
        print("  PASS: Filesystem state matches expectations")

    # Summary
    print(f"\n{'='*40}")
    if all_failures:
        print(f"FAILED — {len(all_failures)} assertion(s) failed:")
        for f in all_failures:
            print(f"  - {f}")
        return False
    else:
        print("ALL TESTS PASSED")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Emanon skill integration test")
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5",
        help="Claude model to test against (default: claude-sonnet-4-5)",
    )
    args = parser.parse_args()

    success = run_tests(model=args.model)
    sys.exit(0 if success else 1)
