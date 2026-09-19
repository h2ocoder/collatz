"""SCRUM-30: experiments on the mirror table n -> n - |n/2|.

Run:  python -X utf8 scripts/mirror_experiments.py
Writes research/investigate-pinball-analogy/results/mirror_experiments.json

E1  3-adic register on positive orbits vs the conservation law
E2  which rays the old negative cycles (-1, -5, -17) fall on
E3  independence of stopping coordinates and age coordinates
E4  complexity and entropy of age words and forward branch words
E5  is the Fibonacci law universal across qm-1 / qm/2 mirrors?
E6  exact mean age
E7-E9  +1 mirror, forward/backward run lengths, inverse-tree relation
E10 forward dual (Reyes Jimenez count = no '00')
E11 survival of positive integers in the no-'00' family
"""

import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collatz.core import alpha_value, stopping_time, syracuse_step  # noqa: E402
from collatz.pinball.mirror import age, age_tail, age_word, seed  # noqa: E402

OUT = ROOT / "research" / "investigate-pinball-analogy" / "results" / "mirror_experiments.json"


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def mutual_information(pairs):
    n = len(pairs)
    joint, left, right = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (left[a] * right[b])) for (a, b), c in joint.items())


def e1_register():
    """Register = 3^(halvings). At the first drop (Collatz steps), halvings = ceil(s * log2 3)?"""
    print("\nE1: 3-adic register on positive orbits")
    violations, checked, overshoot = 0, 0, Counter()
    for n in range(3, 200001, 2):
        x, s, halvings = n, 0, 0
        while x >= n:
            if x % 2:
                x, s = 3 * x + 1, s + 1
            else:
                x, halvings = x // 2, halvings + 1
        extra = 0
        while x % 2 == 0:
            x, extra = x // 2, extra + 1
        checked += 1
        violations += halvings != math.ceil(s * math.log2(3))
        overshoot[extra] += 1
    print(f"  odd n < 200001: register exponent at first drop == ceil(s*log2 3): "
          f"{checked - violations}/{checked}")
    dist = [round(overshoot[e] / checked, 4) for e in range(5)]
    print(f"  halvings still owed after the drop (Syracuse overshoot) 0..4: {dist}")
    return {"checked": checked, "violations": violations, "overshoot_distribution": dist}


def e2_cycle_rays():
    print("\nE2: where the old Collatz negative cycles sit on the mirror table")
    cycles = {"-1": [1, 2], "-5": [5, 14, 7, 20, 10],
              "-17": [17, 50, 25, 74, 37, 110, 55, 164, 82, 41, 122, 61, 182, 91, 272, 136, 68, 34]}
    out = {}
    for name, members in cycles.items():
        rows = [(m, seed(m), age(m)) for m in members]
        seeds = sorted({s for _, s, _ in rows})
        out[name] = {"members": rows, "distinct_seeds": len(seeds)}
        print(f"  cycle {name}: {len(members)} members on {len(seeds)} distinct rays; "
              f"ages {[a for _, _, a in rows]}")
    return out


def e3_independence():
    print("\nE3: stopping class vs age (mutual information, bits)")
    limit = 300000
    cap = lambda k: min(k, 30)
    all_pairs = [(cap(stopping_time(m)), min(age(m), 6)) for m in range(2, limit)]
    odd_pairs = [(cap(stopping_time(m)), min(age(m), 6)) for m in range(3, limit, 2)]
    # shuffle baseline: MI of finite samples is biased upward
    import random
    rng = random.Random(0)
    shuffled = [a for a, _ in odd_pairs]
    rng.shuffle(shuffled)
    baseline = mutual_information(list(zip(shuffled, [b for _, b in odd_pairs])))
    res = {"all_m": mutual_information(all_pairs), "odd_m": mutual_information(odd_pairs),
           "shuffled_baseline_odd": baseline}
    print(f"  all m:  {res['all_m']:.5f}   (dependence through parity: even m is class 1)")
    print(f"  odd m:  {res['odd_m']:.5f}   shuffled baseline {baseline:.5f}")
    # the one exact coupling: odd m has age >= 1 iff 3 | m
    assert all((age(m) >= 1) == (m % 3 == 0) for m in range(1, 5000, 2))
    return res


def e4_words():
    print("\nE4: word complexity")
    words = {age_word(m) for m in range(1, 400000)}
    complexity = []
    for n in range(1, 11):
        factors = {w[i:i + n] for w in words for i in range(len(w) - n + 1)}
        complexity.append(len(factors))
    print(f"  age-word factor complexity p(n), n=1..10: {complexity}")
    print(f"  Fibonacci F(n+2):                          {[fib(n + 2) for n in range(1, 11)]}")
    print("  (Sturmian words have p(n) = n + 1)")

    # forward branch word along one ray: B = odd magnitude, A = even
    rows = {}
    for start in (1, 5, 7, 4):
        m, word = start, []
        for _ in range(20000):
            word.append("B" if m % 2 else "A")
            m = 3 * m - 1 if m % 2 else 3 * m // 2
        text = "".join(word)
        blocks = Counter(text[i:i + 12] for i in range(len(text) - 12))
        total = sum(blocks.values())
        h12 = -sum(c / total * math.log2(c / total) for c in blocks.values())
        blocks11 = Counter(text[i:i + 11] for i in range(len(text) - 11))
        total11 = sum(blocks11.values())
        h11 = -sum(c / total11 * math.log2(c / total11) for c in blocks11.values())
        after_a = Counter(b for a, b in zip(text, text[1:]) if a == "A")
        rows[start] = {"freq_B": text.count("B") / len(text),
                       "P(B|A)": after_a["B"] / sum(after_a.values()),
                       "entropy_rate_est": h12 - h11}
        print(f"  ray of seed {start}: freq(B) {rows[start]['freq_B']:.4f}  "
              f"P(B|A) {rows[start]['P(B|A)']:.4f}  entropy rate ~ {h12 - h11:.4f} bits/step")
    print(f"  Markov prediction: freq(B) 1/3, P(B|A) 1/2, entropy 2/3 = 0.6667; "
          f"golden-mean maximum log2(phi) = {math.log2((1 + 5 ** 0.5) / 2):.4f}")
    return {"age_word_complexity": complexity, "forward_rays": rows}


def e5_universality():
    print("\nE5: mirrors of qm-1 (odd) / qm/2 (even): residues mod 2*q^t with age >= t")
    out = {}
    for q in (3, 5, 7, 9, 11):
        def back(m):
            if m % q == 0:
                return 2 * m // q
            if (m + 1) % q == 0 and m % 2 == 0:
                return (m + 1) // q
            return None

        def age_q(m):
            t = 0
            while (m := back(m)) is not None:
                t += 1
            return t

        counts = []
        for t in range(1, 6 if q <= 5 else 5):
            modulus = 2 * q ** t
            if modulus > 400000:
                break
            counts.append(sum(1 for r in range(modulus) if age_q(r + 3 * modulus) >= t))
        out[q] = counts
        print(f"  q={q}: {counts}   Fibonacci F(t+3): {[fib(t + 3) for t in range(1, len(counts) + 1)]}")
    return out


def e6_mean_age():
    print("\nE6: mean age")
    exact = sum(Fraction(*age_tail(t)) for t in range(1, 200))
    limit = 2 * 3 ** 11
    empirical = sum(age(m) for m in range(1, limit + 1)) / limit
    print(f"  sum of F(t+3)/(2*3^t) = {float(exact):.6f}  (closed form 11/10);  "
          f"empirical over m <= {limit}: {empirical:.6f}")
    return {"series": float(exact), "empirical": empirical}


def e7_positive_mirror():
    print("\nE7: the +1 mirror, m -> q*m+1 (odd), q*m/2 (even): same law?")
    out = {}
    for q in (3, 5, 7):
        def age_q(m):
            t = 0
            while True:
                if m % q == 0:
                    m = 2 * m // q
                elif (m - 1) % q == 0 and m % 2 == 0:
                    m = (m - 1) // q
                else:
                    return t
                t += 1
        counts = [sum(1 for r in range(2 * q ** t) if age_q(r + 6 * q ** t) >= t) for t in range(1, 5)]
        out[q] = counts
        print(f"  q={q}: {counts}")
    return out


def e8_arrow_of_time():
    """Run lengths of A: forward they are v2(3b-1) ~ Geom(1/2); backward ~ Geom(1/3)."""
    print("\nE8: halving-run lengths, forward vs backward")
    forward, backward = Counter(), Counter()
    for b in range(1, 600001, 2):
        a, m = 0, 3 * b - 1
        while m % 2 == 0:
            m, a = m // 2, a + 1
        forward[a] += 1
    for m in range(1, 600001):
        word = age_word(m)
        if word:
            run = len(word) - len(word.lstrip("A"))
            backward[run] += 1
    f_total, b_total = sum(forward.values()), sum(backward.values())
    f_tail = [round(sum(c for a, c in forward.items() if a >= r) / f_total, 4) for r in range(1, 6)]
    b_tail = [round(sum(c for a, c in backward.items() if a >= r) /
                    sum(c for a, c in backward.items() if a >= 1), 4) for r in range(1, 6)]
    print(f"  forward  P(run >= r), r=1..5: {f_tail}   (2^-(r-1): 1, .5, .25, .125, .0625)")
    print(f"  backward P(run >= r | run >= 1): {b_tail}   (3^-(r-1): 1, .3333, .1111, .037, .0123)")
    return {"forward_tail": f_tail, "backward_tail": b_tail}


def e9_inverse_tree():
    """Mirror-back B is the Collatz inverse-tree odd branch; A replaces 2m by 2m/3."""
    print("\nE9: +1 mirror back-step B vs Collatz inverse tree")
    agree = all(((m - 1) // 3) % 2 == 1 and 3 * ((m - 1) // 3) + 1 == m
                for m in range(4, 60000, 6))
    exclusive = not any(m % 3 == 0 and m % 6 == 4 for m in range(1, 60000))
    print(f"  m = 4 mod 6 -> (m-1)/3 is the odd Collatz predecessor: {agree}")
    print(f"  branches A (3 | m) and B (m = 4 mod 6) never both apply: {exclusive}")
    return {"B_is_collatz_inverse": agree, "branches_exclusive": exclusive}


def e10_forward_dual():
    """Reyes Jimenez (arXiv:2606.02621): odd n <= 2^m whose T-orbit avoids 4 mod 6 number F(m+1).

    Claim tested: those n are exactly the ones whose Terras parity word of length m
    has no two consecutive halvings ('00'), so the count follows from the Terras bijection.
    """
    print("\nE10: forward dual of the age law (avoid 4 mod 6  <=>  no '00')")
    rows = []
    for m in range(2, 15):
        avoid, no00 = set(), set()
        for n in range(1, 2 ** m + 1, 2):
            x, word, clean = n, [], True
            for step in range(1, m + 1):
                word.append(x % 2)
                x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
                if step <= m - 1 and x % 6 == 4:
                    clean = False
            if clean:
                avoid.add(n)
            if "00" not in "".join(map(str, word)):
                no00.add(n)
        rows.append((m, len(avoid), fib(m + 1), avoid == no00))
    print(f"  m, count, F(m+1), same set as no-'00': {rows}")
    return {"rows": rows}


def e11_survival():
    """How long can a positive integer go without two consecutive halvings?"""
    print("\nE11: survival in the no-'00' family (odd n < 4,000,001)")
    best, records, reach_one = 0, [], 0
    for n in range(3, 4_000_001, 2):
        x, steps, prev_even = n, 0, False
        while True:
            if x % 2 == 0:
                if prev_even:
                    break
                prev_even, x = True, x // 2
            else:
                prev_even, x = False, (3 * x + 1) // 2
            steps += 1
            if x == 1:
                reach_one += 1
                steps = 0
                break
        if steps - 1 > best:
            best = steps - 1
            records.append((n, best, round(best / math.log2(n), 2)))
    predicted = 1 / math.log2(2 / ((1 + 5 ** 0.5) / 2))
    print(f"  n > 1 reaching 1 without any '00': {reach_one}")
    print(f"  last records (n, steps, steps/log2 n): {records[-6:]}")
    print(f"  random-model prediction for records: {predicted:.2f} * log2 n")
    return {"reach_one": reach_one, "records": records, "predicted_ratio": predicted}


if __name__ == "__main__":
    results = {"E1": e1_register(), "E2": e2_cycle_rays(), "E3": e3_independence(),
               "E4": e4_words(), "E5": e5_universality(), "E6": e6_mean_age(),
               "E7": e7_positive_mirror(), "E8": e8_arrow_of_time(), "E9": e9_inverse_tree(), "E10": e10_forward_dual(), "E11": e11_survival()}
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nwrote {OUT}")
