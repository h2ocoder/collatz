"""PinballModel: an integer-only decision model with exact rational outputs.

A member is (bit order, router). It reads the state's feature bits in its own
order, launches the resulting odd integer into its router, and the lane the
ball lands in holds integer counts per answer. Training is counting; the
probability of an answer is a ratio of counts, returned as a Fraction.
An ensemble of members is combined by an exact mean (or product) of Fractions.

No float is used anywhere in fit or decide.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from collatz.pinball.encode import launch_integer
from collatz.pinball.table import PinballTable


@dataclass(frozen=True)
class Decision:
    """A typed answer: the chosen label plus the full distribution."""

    choice: object
    probabilities: dict

    @property
    def confidence(self) -> Fraction:
        return self.probabilities[self.choice]

    def probability_of(self, label) -> Fraction:
        """P(label) -- for a yes/no question, probability_of(True)."""
        return self.probabilities.get(label, Fraction(0))

    def score(self) -> Fraction:
        """Expected value of the label, for numeric (ordinal) labels."""
        return sum(Fraction(label) * p for label, p in self.probabilities.items())


class PinballModel:
    """Count-based ensemble over pinball lanes.

    members   : list of (order, router); order is a tuple of feature-bit
                indices, router has .lane(n) and .depth
    smoothing : integer pseudo-count added to every label (0 = raw ratios)
    combine   : 'mean' or 'product' of member posteriors
    """

    def __init__(self, members, smoothing: int = 1, combine: str = "mean"):
        if combine not in ("mean", "product"):
            raise ValueError("combine must be 'mean' or 'product'")
        self.members = list(members)
        self.smoothing = smoothing
        self.combine = combine
        self.labels = []
        self.prior = {}
        self.lanes = [dict() for _ in self.members]

    @classmethod
    def build(cls, width, n_members=32, tables=((3, 1),), depth=8, seed=0,
              bit_scores=None, subset=None, **kwargs):
        """Random-forest-style construction.

        Each member draws a random subset of `subset` feature bits. With
        bit_scores (see bit_scores()) the subset is read most-informative
        first -- the learned routing; without, in random order.
        """
        rng = random.Random(seed)
        subset = min(width, subset or width)
        members = []
        for m in range(n_members):
            order = rng.sample(range(width), subset)
            if bit_scores is not None:
                order.sort(key=lambda i: -bit_scores[i])
            q, c = tables[m % len(tables)]
            members.append((tuple(order[:depth]), PinballTable(q, c, depth)))
        return cls(members, **kwargs)

    # ---- routing ----

    def _lane(self, m, bits):
        order, router = self.members[m]
        return router.lane(launch_integer(bits[i] for i in order))

    # ---- training: counting ----

    def fit(self, X, y):
        """Add one count per example to its lane (and every prefix of it)."""
        return self.fit_soft(X, ({label: 1} for label in y))

    def fit_soft(self, X, weights):
        """Distillation: add integer weights per label instead of one hard count.

        `weights` yields a dict label -> non-negative int per example, e.g. a
        teacher's probabilities in fixed point (see fixed_point()).
        """
        for bits, w in zip(X, weights):
            for label, amount in w.items():
                if label not in self.prior:
                    self.labels.append(label)
                    self.prior[label] = 0
                self.prior[label] += amount
            for m in range(len(self.members)):
                lane = self._lane(m, bits)
                for cut in range(1, len(lane) + 1):
                    counts = self.lanes[m].setdefault(lane[:cut], {})
                    for label, amount in w.items():
                        counts[label] = counts.get(label, 0) + amount
        return self

    # ---- inference: ratios of counts ----

    def _posterior(self, counts):
        a = self.smoothing
        total = sum(counts.values()) + a * len(self.labels)
        if total == 0:
            return {label: Fraction(1, len(self.labels)) for label in self.labels}
        return {label: Fraction(counts.get(label, 0) + a, total) for label in self.labels}

    def member_posterior(self, m, bits):
        """Posterior from member m: its lane, backed off to the longest seen prefix."""
        lane = self._lane(m, bits)
        for cut in range(len(lane), 0, -1):
            counts = self.lanes[m].get(lane[:cut])
            if counts:
                return self._posterior(counts)
        return self._posterior(self.prior)

    def decide(self, bits) -> Decision:
        """Answer for one encoded state, with exact probabilities summing to 1."""
        posts = [self.member_posterior(m, bits) for m in range(len(self.members))]
        if self.combine == "mean":
            probs = {label: sum(p[label] for p in posts) / len(posts) for label in self.labels}
        else:
            prior = self._posterior(self.prior)
            probs = {}
            for label in self.labels:
                value = prior[label]
                for p in posts:
                    value *= p[label] / prior[label] if prior[label] else 0
                probs[label] = value
            norm = sum(probs.values())
            probs = {label: v / norm for label, v in probs.items()} if norm else prior
        choice = max(self.labels, key=lambda label: probs[label])
        return Decision(choice, probs)


def bit_scores(X, y) -> list[int]:
    """Integer informativeness of each feature bit: sum_c |n_1c * N - n_1 * N_c|.

    Zero when the bit is independent of the label; no division needed.
    """
    n_total = 0
    width = None
    label_counts = {}
    on_counts = None
    on_label = {}
    for bits, label in zip(X, y):
        if width is None:
            width = len(bits)
            on_counts = [0] * width
        n_total += 1
        label_counts[label] = label_counts.get(label, 0) + 1
        row = on_label.setdefault(label, [0] * width)
        for i, b in enumerate(bits):
            if b:
                on_counts[i] += 1
                row[i] += 1
    return [
        sum(abs(on_label[c][i] * n_total - on_counts[i] * label_counts[c]) for c in label_counts)
        for i in range(width)
    ]


def fixed_point(probabilities: dict, scale_bits: int = 16) -> dict:
    """Teacher probabilities (Fractions) -> integer weights, floor(p * 2^scale_bits)."""
    scale = 1 << scale_bits
    return {label: int(Fraction(p) * scale) for label, p in probabilities.items()}
