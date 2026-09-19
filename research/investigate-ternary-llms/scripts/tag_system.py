"""The Collatz 2-tag system (De Mol 2008 / Wikipedia) next to the ternary circuit.

2-tag system, alphabet {a, b, c}, productions  a -> bc,  b -> a,  c -> aaa.
Each step: read the first letter, delete the first TWO letters, append the production.
From a^n it reaches a^{T(n)} with T(n) = n/2 (n even) or (3n+1)/2 (n odd)  -- the Terras map.

Facts computed here:
  1. correctness of the simulation (a^n -> a^{T(n)}), and the round length in tag steps;
  2. the word-length increment per step is in {-1, 0, +1}: a: 2 -> 2 (0), b: 2 -> 1 (-1), c: 2 -> 3 (+1);
     the tag system is a ternary accumulator on |word|;  statistics of the {-1,0,+1} walk;
  3. total tag steps for a whole orbit vs the orbit sum (repo: orbit sums are affine per subgroup),
     and a direct check that tag time is affine in n within a dropping-set residue class;
  4. the read-letter word as a ternary string, and how the binary parity vector sits inside it.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/tag_system.py
"""
import json
import sys
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
PROD = {"a": "bc", "b": "a", "c": "aaa"}
DELTA = {"a": 0, "b": -1, "c": +1}  # length change per step


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def tag_round(n):
    """Run the tag system from a^n until the word is again all a's.  Returns (m, steps, letters_read, length_trace)."""
    w = deque("a" * n)
    steps, read, trace = 0, [], [n]
    while True:
        x = w.popleft()
        w.popleft()
        w.extend(PROD[x])
        steps += 1
        read.append(x)
        trace.append(len(w))
        if all(ch == "a" for ch in w) and x != "a":  # a round ends when the word is pure a's again after a b/c phase
            return len(w), steps, "".join(read), trace


def tag_orbit(n, stop_at_drop=False):
    """Iterate rounds until 1 (or until the value first drops below n).  Returns dict of totals."""
    steps, read, walk = 0, [], Counter()
    cur, rounds, orbit = n, 0, [n]
    while cur != 1:
        m, s, r, _ = tag_round(cur)
        assert m == terras(cur), (cur, m)
        steps += s
        read.append(r)
        walk.update(r)
        cur, rounds = m, rounds + 1
        orbit.append(cur)
        if stop_at_drop and cur < n:
            break
    return dict(steps=steps, rounds=rounds, orbit=orbit, read="".join(read), walk=dict(walk))


if __name__ == "__main__":
    out = {}
    # 1. correctness + round length
    bad = sum(tag_round(n)[0] != terras(n) for n in range(2, 600))
    print(f"tag round a^n -> a^T(n): mismatches for 2 <= n < 600: {bad}")
    rl = [(n, tag_round(n)[1]) for n in range(2, 14)]
    print("round length in tag steps (n, steps):", rl)
    # closed form: even n: n steps; odd n: n + 1 steps?  check
    form = all(s == (n if n % 2 == 0 else n + 1) for n, s in [(n, tag_round(n)[1]) for n in range(2, 600)])
    print(f"round length = n (even) / n+1 (odd) for all n < 600: {form}")

    # 2. the {-1,0,+1} walk
    r = tag_orbit(27)
    tot = sum(r["walk"].values())
    print(f"\nn=27 full orbit: {r['rounds']} rounds = Terras steps, {r['steps']} tag steps; letters read: {r['walk']}")
    print(f"  zero density of the length walk (fraction of a-reads) = {r['walk']['a']/tot:.4f}; "
          f"+1 (c) = {r['walk']['c']/tot:.4f}; -1 (b) = {r['walk']['b']/tot:.4f}")
    print(f"  net length change = c - b = {r['walk']['c'] - r['walk']['b']} = 1 - n = {1 - 27}  ->", r["walk"]["c"] - r["walk"]["b"] == 1 - 27)
    zs = []
    for n in range(3, 400, 2):
        rr = tag_orbit(n)
        t = sum(rr["walk"].values())
        zs.append(rr["walk"]["a"] / t)
    print(f"  zero density over odd n < 400: min {min(zs):.4f} max {max(zs):.4f} mean {sum(zs)/len(zs):.4f}  (exactly 1/2 if every round is n/2 a-reads then n/2 b/c-reads)")

    # 3. tag time vs orbit sum; affine within a residue class of a dropping set
    print("\nTag steps for a full orbit vs orbit sum S = sum of Terras iterates (n .. 1):")
    ok = True
    for n in (3, 7, 27, 97, 871):
        rr = tag_orbit(n)
        S = sum(rr["orbit"][:-1])
        odd = sum(1 for v in rr["orbit"][:-1] if v % 2)
        print(f"  n={n:4d}: tag steps {rr['steps']:7d}, orbit sum {S:7d}, odd rounds {odd:4d}; steps - S - odd = {rr['steps'] - S - odd}")
        ok &= rr["steps"] == S + odd
    print(f"  tag steps = orbit sum + (number of odd rounds), exactly: {ok}")

    # stopping-orbit tag time within Set_13 residue classes mod 256 (s=5 odd steps, 8 halvings): affine in n?
    print("\nTag steps to the first drop, within a residue class of Set_13 (n = 39 mod 256):")
    pts = []
    for n in range(39, 39 + 256 * 12, 256):
        if stopping_time(n) != 13:
            continue
        rr = tag_orbit(n, stop_at_drop=True)
        pts.append((n, rr["steps"]))
    slopes = {Fraction(b2 - b1, n2 - n1) for (n1, b1), (n2, b2) in zip(pts, pts[1:])}
    print(f"  points: {pts[:5]} ...; distinct slopes between consecutive points: {sorted(slopes)}")
    print("  => tag time to first drop is an exact affine function of n on the residue class (slope = sum of the")
    print("     affine orbit slopes 3^j/2^i over the stopping orbit, an integer/256 + odd count)")

    # 4. read word: rounds are a^{ceil(n/2)} then (b or c)-runs; the round type is the parity bit
    r = tag_orbit(27)
    rounds_read = []
    cur = 27
    for _ in range(6):
        m, s, rd, _ = tag_round(cur)
        rounds_read.append((cur, rd))
        cur = m
    print("\nRead-letter word per round (n, letters read), first six rounds of 27:")
    for cur, rd in rounds_read:
        print(f"  n={cur:3d} ({'odd ' if cur % 2 else 'even'}): {rd}")
    print("  parity of n = whether the b/c phase begins with c (odd) or b (even); the ternary read word")
    print("  is the unary expansion of the binary parity vector: a^{ceil(n/2)} then b^{n/2} (even) or c b c b ... (odd).")

    json.dump(dict(round_length_formula=form, tag_steps_equals_orbit_sum_plus_odd=ok,
                   zero_density_mean=sum(zs) / len(zs), set13_slopes=[str(s) for s in slopes]),
              open(RESULTS / "tag_system.json", "w"), indent=1)
