"""SCRUM-30: pinball model experiments (Tasks A, B, C + distillation).

Run:  python -X utf8 scripts/pinball_experiments.py [A] [B] [C]
Writes research/investigate-pinball-analogy/results/pinball_experiments.json

All models are integer/Fraction; floats appear only when printing results.
Every ensemble comparison reuses the SAME bit orders, so rows differ only in
the router (Collatz table vs controls).
"""

import json
import random
import sys
import time
import urllib.request
import zipfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collatz.core import stopping_time  # noqa: E402
from collatz.pinball import (  # noqa: E402
    PinballModel, PinballTable, bit_scores, encode_state, fixed_point, integer_bits,
)
from collatz.pinball.baselines import (  # noqa: E402
    IntegerNaiveBayes, IntegerTree, PrefixRouter, ScrambleRouter, accuracy, ece,
)

RESULTS = ROOT / "research" / "investigate-pinball-analogy" / "results"
SMS_DIR = ROOT / "data" / "sms_spam"
SMS_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"


def evaluate(name, learner, X_test, y_test, rows, extra=None):
    start = time.time()
    decisions = [learner.decide(bits) for bits in X_test]
    row = {"model": name,
           "accuracy": float(accuracy(decisions, y_test)),
           "ece": float(ece(decisions, y_test)),
           "seconds": round(time.time() - start, 1)}
    row.update(extra or {})
    rows.append(row)
    print(f"  {name:<44} acc {row['accuracy']:.4f}   ece {row['ece']:.4f}")
    return decisions


def ensemble_rows(X_tr, y_tr, X_te, y_te, rows, width, depth, n_members, seed=0, tables=((3, 1),)):
    """Collatz ensemble, its two router controls, and the learned-routing variant."""
    scores = bit_scores(X_tr, y_tr)
    subset = max(depth, width // 4)
    for label, kwargs in (("random order", {}),
                          ("learned order", {"bit_scores": scores, "subset": subset})):
        base = PinballModel.build(width, n_members, tables, depth, seed, **kwargs)
        variants = {
            f"pinball 3x+1 [{label}]": base.members,
            f"  control: fixed-depth prefix [{label}]":
                [(o, PrefixRouter(depth - 1)) for o, _ in base.members],
            f"  control: scrambled lanes [{label}]":
                [(o, ScrambleRouter(depth=depth)) for o, _ in base.members],
        }
        for name, members in variants.items():
            evaluate(name, PinballModel(members).fit(X_tr, y_tr), X_te, y_te, rows)
    mixed = PinballModel.build(width, n_members, ((3, 1), (5, 1), (7, 1), (3, 5)), depth, seed,
                               bit_scores=scores, subset=subset)
    evaluate("pinball mixed qx+c tables [learned order]", mixed.fit(X_tr, y_tr), X_te, y_te, rows)
    product = PinballModel.build(width, n_members, tables, depth, seed, bit_scores=scores,
                                 subset=subset, combine="product")
    evaluate("pinball 3x+1 product-combine [learned order]", product.fit(X_tr, y_tr), X_te, y_te, rows)


def baselines(X_tr, y_tr, X_te, y_te, rows, depth):
    evaluate("integer naive Bayes", IntegerNaiveBayes().fit(X_tr, y_tr), X_te, y_te, rows)
    evaluate(f"integer decision tree (depth {depth})",
             IntegerTree(max_depth=depth).fit(X_tr, y_tr), X_te, y_te, rows)


# ---- Task A: stopping class from truncated bits ----

def task_a():
    print("\nTask A: stopping class of odd n < 2^16 from its low 10 bits")
    bits, rows = 10, []
    rng = random.Random(1)
    ns = list(range(3, 1 << 16, 2))
    rng.shuffle(ns)
    half = len(ns) // 2
    label = {n: min(stopping_time(n), 21) for n in ns}
    X = {n: integer_bits(n, bits) for n in ns}
    tr, te = ns[:half], ns[half:]
    X_tr, y_tr = [X[n] for n in tr], [label[n] for n in tr]
    X_te, y_te = [X[n] for n in te], [label[n] for n in te]

    by_residue = {}
    for n in ns:
        counts = by_residue.setdefault(n % (1 << (bits + 1)), {})
        counts[label[n]] = counts.get(label[n], 0) + 1
    ceiling = Fraction(sum(max(c.values()) for c in by_residue.values()), len(ns))
    print(f"  exact Bayes ceiling (population)             acc {float(ceiling):.4f}")

    order = tuple(range(bits))
    single = PinballModel([(order, PinballTable(depth=bits + 1))])
    evaluate("pinball 3x+1, single table, identity order", single.fit(X_tr, y_tr), X_te, y_te, rows,
             {"lanes": sum(1 for lane in single.lanes[0])})
    evaluate("  control: fixed-depth prefix",
             PinballModel([(order, PrefixRouter(bits))]).fit(X_tr, y_tr), X_te, y_te, rows)
    evaluate("  control: scrambled lanes",
             PinballModel([(order, ScrambleRouter(depth=bits + 1))]).fit(X_tr, y_tr), X_te, y_te, rows)
    baselines(X_tr, y_tr, X_te, y_te, rows, bits)
    return {"bayes_ceiling": float(ceiling), "rows": rows}


# ---- Task B: synthetic boolean functions ----

def task_b():
    width, n_train, n_test, depth, members = 15, 2000, 2000, 8, 64
    rng = random.Random(2)
    weights = [rng.randint(1, 9) for _ in range(width)]

    def noisy_rule_clean(b):
        return b[0] ^ (b[3] & b[7])

    tasks = {
        "majority": lambda b: int(sum(b) > width // 2),
        "weighted threshold": lambda b: int(2 * sum(w * x for w, x in zip(weights, b)) > sum(weights)),
        "parity of 3 bits": lambda b: b[1] ^ b[5] ^ b[9],
        "noisy rule (1/8 label flips)": noisy_rule_clean,
    }
    out = {}
    for name, fn in tasks.items():
        print(f"\nTask B: {name}  ({width} bits, {n_train} train / {n_test} test)")
        rows = []
        X = [tuple(rng.getrandbits(1) for _ in range(width)) for _ in range(n_train + n_test)]
        y = [fn(b) for b in X]
        if name.startswith("noisy"):
            y = [label ^ (rng.randrange(8) == 0) for label in y]
        X_tr, y_tr, X_te, y_te = X[:n_train], y[:n_train], X[n_train:], y[n_train:]
        ensemble_rows(X_tr, y_tr, X_te, y_te, rows, width, depth, members)
        baselines(X_tr, y_tr, X_te, y_te, rows, depth)
        out[name] = rows

    print("\nDistillation: noisy rule, 300 training examples, oracle teacher P(y|x) in {1/8, 7/8}")
    print("  (mean over 5 seeds; ceiling accuracy on noisy test labels = 0.875)")
    totals = {}
    for seed in range(5):
        X = [tuple(rng.getrandbits(1) for _ in range(width)) for _ in range(300 + n_test)]
        clean = [noisy_rule_clean(b) for b in X]
        noisy = [label ^ (rng.randrange(8) == 0) for label in clean]
        X_tr, X_te, y_te = X[:300], X[300:], noisy[300:]
        scores = bit_scores(X_tr, noisy[:300])
        teacher = [fixed_point({c: Fraction(7, 8), 1 - c: Fraction(1, 8)}) for c in clean[:300]]
        base = PinballModel.build(width, members, ((3, 1),), depth, seed, bit_scores=scores, subset=depth)
        students = {"3x+1 student": base.members,
                    "fixed-depth student": [(o, PrefixRouter(depth - 1)) for o, _ in base.members]}
        for student, student_members in students.items():
            for regime, fit in (("hard noisy labels", lambda m: m.fit(X_tr, noisy[:300])),
                                ("oracle soft labels", lambda m: m.fit_soft(X_tr, teacher))):
                fitted = fit(PinballModel(student_members))
                decisions = [fitted.decide(b) for b in X_te]
                acc, cal = totals.get((student, regime), (0, 0))
                totals[(student, regime)] = (acc + float(accuracy(decisions, y_te)),
                                             cal + float(ece(decisions, y_te)))
    rows = []
    for (student, regime), (acc, cal) in totals.items():
        rows.append({"model": f"{student}, {regime}", "accuracy": acc / 5, "ece": cal / 5})
        print(f"  {rows[-1]['model']:<44} acc {acc / 5:.4f}   ece {cal / 5:.4f}")
    out["distillation (oracle teacher)"] = rows
    return out


# ---- Task C: SMS spam ----

def load_sms():
    path = SMS_DIR / "SMSSpamCollection"
    if not path.exists():
        SMS_DIR.mkdir(parents=True, exist_ok=True)
        archive = SMS_DIR / "sms.zip"
        urllib.request.urlretrieve(SMS_URL, archive)
        zipfile.ZipFile(archive).extractall(SMS_DIR)
    rows = [line.split("\t", 1) for line in path.read_text(encoding="utf-8").splitlines() if "\t" in line]
    return [text for _, text in rows], [label == "spam" for label, _ in rows]


def task_c():
    width, depth, members = 512, 8, 64
    texts, labels = load_sms()
    idx = list(range(len(texts)))
    random.Random(3).shuffle(idx)
    cut = len(idx) * 4 // 5
    X = [encode_state(t, width) for t in texts]
    X_tr, y_tr = [X[i] for i in idx[:cut]], [labels[i] for i in idx[:cut]]
    X_te, y_te = [X[i] for i in idx[cut:]], [labels[i] for i in idx[cut:]]
    spam_rate = sum(y_te) / len(y_te)
    print(f"\nTask C: SMS spam  ({len(X_tr)} train / {len(X_te)} test, {width} hashed bits, "
          f"majority-class acc {1 - spam_rate:.4f})")
    rows = []
    ensemble_rows(X_tr, y_tr, X_te, y_te, rows, width, depth, members)
    nb = IntegerNaiveBayes().fit(X_tr, y_tr)
    evaluate("integer naive Bayes", nb, X_te, y_te, rows)
    evaluate(f"integer decision tree (depth {depth})",
             IntegerTree(max_depth=depth).fit(X_tr, y_tr), X_te, y_te, rows)

    print("  -- distillation: naive Bayes teacher -> pinball student --")
    scores = bit_scores(X_tr, y_tr)
    student = PinballModel.build(width, members, ((3, 1),), depth, 0, bit_scores=scores,
                                 subset=width // 4)
    soft = [fixed_point(nb.decide(bits).probabilities) for bits in X_tr]
    evaluate("pinball distilled from naive Bayes soft labels", student.fit_soft(X_tr, soft),
             X_te, y_te, rows)
    return {"majority_class_accuracy": 1 - spam_rate, "rows": rows}


if __name__ == "__main__":
    wanted = [a.upper() for a in sys.argv[1:]] or ["A", "B", "C"]
    RESULTS.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS / "pinball_experiments.json"
    results = json.loads(out_path.read_text()) if out_path.exists() else {}
    for key, fn in (("A", task_a), ("B", task_b), ("C", task_c)):
        if key in wanted:
            results[f"task_{key}"] = fn()
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out_path}")
