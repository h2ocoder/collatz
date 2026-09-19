"""Controls and baselines for the pinball model -- all integer/Fraction.

Routers (drop-in replacements for PinballTable inside PinballModel):
  PrefixRouter   -- reads the same bits but never drains early (fixed depth).
                    Isolates: does the Collatz drain schedule help?
  ScrambleRouter -- hashes the launch integer before playing the table, so the
                    lane-size distribution is identical but lanes merge
                    unrelated inputs. Isolates: does lane coherence matter?

Baselines: IntegerNaiveBayes, IntegerTree. Metrics: accuracy, ece.
"""

import zlib
from fractions import Fraction

from collatz.pinball.model import Decision
from collatz.pinball.table import PinballTable


class PrefixRouter:
    """Lane = the first `depth` parities of n, with no early drain."""

    def __init__(self, depth: int = 8):
        self.depth = depth

    def lane(self, n: int):
        return tuple((n >> i) & 1 for i in range(self.depth + 1))


class ScrambleRouter:
    """Play the table on crc32(n) | 1 instead of n."""

    def __init__(self, q: int = 3, c: int = 1, depth: int = 8):
        self.depth = depth
        self._table = PinballTable(q, c, depth)

    def lane(self, n: int):
        scrambled = zlib.crc32(n.to_bytes((n.bit_length() + 7) // 8 or 1, "little")) | 1
        return self._table.lane(scrambled)


def with_router(model_members, router_factory):
    """Same bit orders, different router -- for controlled comparisons."""
    return [(order, router_factory(router.depth)) for order, router in model_members]


class IntegerNaiveBayes:
    """Bernoulli naive Bayes with integer counts and exact Fraction posteriors."""

    def __init__(self, smoothing: int = 1):
        self.smoothing = smoothing

    def fit(self, X, y):
        self.label_counts = {}
        self.on = {}
        for bits, label in zip(X, y):
            self.label_counts[label] = self.label_counts.get(label, 0) + 1
            row = self.on.setdefault(label, [0] * len(bits))
            for i, b in enumerate(bits):
                row[i] += b
        self.labels = list(self.label_counts)
        return self

    def decide(self, bits) -> Decision:
        a = self.smoothing
        n = sum(self.label_counts.values())
        joint = {}
        for label in self.labels:
            n_c = self.label_counts[label]
            numerator = n_c
            for i, b in enumerate(bits):
                on = self.on[label][i] + a
                numerator *= on if b else n_c + 2 * a - on
            joint[label] = Fraction(numerator, n * (n_c + 2 * a) ** len(bits))
        norm = sum(joint.values())
        probs = {label: v / norm for label, v in joint.items()}
        return Decision(max(self.labels, key=lambda c: probs[c]), probs)


class IntegerTree:
    """Greedy decision tree; splits minimise integer Gini impurity, leaves hold counts."""

    def __init__(self, max_depth: int = 8, min_leaf: int = 2, smoothing: int = 1):
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.smoothing = smoothing

    @staticmethod
    def _counts(y):
        counts = {}
        for label in y:
            counts[label] = counts.get(label, 0) + 1
        return counts

    @staticmethod
    def _impurity(counts, other):
        # n_L * n_R * (weighted Gini), cleared of denominators: compare as integers
        n_l, n_r = sum(counts.values()), sum(other.values())
        g_l = n_l * n_l - sum(v * v for v in counts.values())
        g_r = n_r * n_r - sum(v * v for v in other.values())
        return g_l * n_r + g_r * n_l, n_l * n_r

    def _grow(self, X, y, depth):
        counts = self._counts(y)
        if depth == self.max_depth or len(counts) == 1 or len(y) < 2 * self.min_leaf:
            return counts
        best = None
        for i in range(len(X[0])):
            y_on = [label for bits, label in zip(X, y) if bits[i]]
            if len(y_on) < self.min_leaf or len(y) - len(y_on) < self.min_leaf:
                continue
            num, den = self._impurity(self._counts(y_on), self._counts(
                [label for bits, label in zip(X, y) if not bits[i]]))
            if best is None or num * best[1] < best[0] * den:
                best = (num, den, i)
        if best is None:
            return counts
        i = best[2]
        on = [(b, label) for b, label in zip(X, y) if b[i]]
        off = [(b, label) for b, label in zip(X, y) if not b[i]]
        return (i,
                self._grow([b for b, _ in off], [label for _, label in off], depth + 1),
                self._grow([b for b, _ in on], [label for _, label in on], depth + 1))

    def fit(self, X, y):
        X, y = list(X), list(y)
        self.labels = list(self._counts(y))
        self.root = self._grow(X, y, 0)
        return self

    def decide(self, bits) -> Decision:
        node = self.root
        while isinstance(node, tuple):
            node = node[2] if bits[node[0]] else node[1]
        a = self.smoothing
        total = sum(node.values()) + a * len(self.labels)
        probs = {label: Fraction(node.get(label, 0) + a, total) for label in self.labels}
        return Decision(max(self.labels, key=lambda c: probs[c]), probs)


def accuracy(decisions, y) -> Fraction:
    y = list(y)
    return Fraction(sum(1 for d, label in zip(decisions, y) if d.choice == label), len(y))


def ece(decisions, y, bins: int = 10) -> Fraction:
    """Expected calibration error over equal-width confidence bins.

    Confidences are accumulated in 2^-32 fixed point: summing thousands of
    exact Fractions with unrelated denominators is ruinously slow, and the
    rounding error per example is below 2^-32.
    """
    y = list(y)
    scale = 1 << 32
    hits = [0] * bins
    conf = [0] * bins
    for d, label in zip(decisions, y):
        b = min(bins - 1, int(d.confidence * bins))
        conf[b] += int(d.confidence * scale)
        hits[b] += d.choice == label
    return Fraction(sum(abs(hits[b] * scale - conf[b]) for b in range(bins)), scale * len(y))
