"""Tests for collatz.pinball: stopping vectors, table, model, Hilbert checks."""

from fractions import Fraction

import pytest

from collatz.core import stopping_time
from collatz.embeddings.keys import subgroup_id
from collatz.pinball import (
    PinballModel,
    PinballTable,
    bit_scores,
    class_coordinates,
    class_densities,
    encode_state,
    fixed_point,
    integer_bits,
    launch_integer,
    stopping_vector,
    subgroup_direction,
    terras_preimage_counts,
    vector_from_coordinates,
)
from collatz.pinball.baselines import (
    IntegerNaiveBayes,
    IntegerTree,
    PrefixRouter,
    ScrambleRouter,
    accuracy,
    ece,
)


# ---- stopping_vector / class_coordinates ----

def test_stopping_vector_of_5():
    """The ticket's example: 5 launches [5, 16, 8, 4], stopping class 3."""
    assert stopping_vector(5) == [5, 16, 8, 4]


def test_class_coordinates_examples():
    """5 = 1 + 1*4 in Set_3; 19 = 3 + 1*16 in Set_6."""
    assert class_coordinates(5) == (3, 1, 1, 1)
    assert class_coordinates(19) == (6, 2, 3, 1)


def test_class_coordinates_agree_with_subgroup_id():
    """(k, s, residue) matches the embeddings' subgroup_id for odd n."""
    for n in range(3, 2000, 2):
        assert class_coordinates(n)[:3] == subgroup_id(n)


def test_coordinates_round_trip():
    """vector_from_coordinates inverts class_coordinates for every n in 2..4095."""
    for n in range(2, 4096):
        assert vector_from_coordinates(*class_coordinates(n)) == stopping_vector(n)


def test_subgroup_is_a_lattice_line():
    """Consecutive members of a subgroup differ by the same integer direction."""
    assert subgroup_direction(5) == [4, 12, 6, 3]
    for n in (5, 3, 7, 11, 27):
        k, s, _, _ = class_coordinates(n)
        step = 2 ** (k - s)
        direction = subgroup_direction(n)
        for j in range(1, 6):
            moved = [a - b for a, b in zip(stopping_vector(n + j * step), stopping_vector(n))]
            assert moved == [j * d for d in direction]


def test_vector_from_coordinates_rejects_non_subgroup():
    """Residue 3 mod 4 is not in Set_3."""
    with pytest.raises(ValueError):
        vector_from_coordinates(3, 1, 3, 0)


# ---- PinballTable ----

def test_table_play_examples():
    """5 drains after bumper+gravity; 3 after bumper, bumper, gravity, gravity."""
    table = PinballTable()
    assert table.play(5) == ((1, 0), True)
    assert table.play(3) == ((1, 1, 0, 0), True)


def test_table_class_matches_stopping_time():
    """The lane's implied class equals stopping_time whenever the ball drains."""
    table = PinballTable(depth=40)
    for n in range(2, 5000):
        k = table.stopping_class(n)
        assert k == stopping_time(n) or (k is None and stopping_time(n) > 40)
    assert PinballTable(depth=59).stopping_class(27) == 96


def test_lane_depends_only_on_low_bits():
    """A lane of length j is determined by n mod 2^j."""
    table = PinballTable(depth=10)
    for n in range(3, 600, 2):
        lane = table.lane(n)
        assert table.lane(n + 2 ** len(lane) * 37) == lane


def test_table_rejects_even_parameters():
    with pytest.raises(ValueError):
        PinballTable(q=4)


# ---- encode ----

def test_launch_integer_round_trip():
    """launch_integer forces the low bit; integer_bits reads the rest back."""
    assert launch_integer((0, 1)) == 5
    assert integer_bits(5, 3) == (0, 1, 0)
    for n in range(1, 512, 2):
        assert launch_integer(integer_bits(n, 9)) == n


def test_encode_state_is_deterministic_and_typed():
    """Text and dict states hash to fixed-width 0/1 tuples."""
    a = encode_state("FREE entry, call now!", width=64)
    assert a == encode_state("FREE entry, call now!", width=64)
    assert len(a) == 64 and set(a) <= {0, 1}
    d = encode_state({"amount": 120, "note": "refund please"}, width=64)
    assert len(d) == 64 and sum(d) > 0


# ---- PinballModel ----

def _collatz_task(limit_bits, feature_bits):
    ns = list(range(3, 1 << limit_bits, 2))
    X = [integer_bits(n, feature_bits) for n in ns]
    y = [min(stopping_time(n), 21) for n in ns]
    return ns, X, y


def test_model_matches_exact_bayes_posterior():
    """Task A: on low bits, lane counts ARE the Bayes posterior per residue."""
    bits = 7
    ns, X, y = _collatz_task(14, bits)
    order = tuple(range(bits))
    model = PinballModel([(order, PinballTable(depth=bits + 1))], smoothing=0).fit(X, y)

    by_residue = {}
    for n, label in zip(ns, y):
        counts = by_residue.setdefault(n % (1 << (bits + 1)), {})
        counts[label] = counts.get(label, 0) + 1
    for residue, counts in by_residue.items():
        total = sum(counts.values())
        decision = model.decide(integer_bits(residue, bits))
        for label in model.labels:
            assert decision.probabilities[label] == Fraction(counts.get(label, 0), total)


def test_probabilities_are_exact_fractions_summing_to_one():
    """No floats: every probability is a Fraction and the total is exactly 1."""
    _, X, y = _collatz_task(10, 8)
    for combine in ("mean", "product"):
        model = PinballModel.build(8, n_members=5, tables=((3, 1), (5, 1)), depth=6,
                                   combine=combine).fit(X, y)
        for bits in X[:50]:
            decision = model.decide(bits)
            assert all(isinstance(p, Fraction) for p in decision.probabilities.values())
            assert sum(decision.probabilities.values()) == 1
            assert decision.confidence == max(decision.probabilities.values())


def test_decision_typed_questions():
    """probability_of answers a yes/no question; score is the expected label."""
    X = [(0, 0), (0, 1), (1, 0), (1, 1)] * 5
    y = [b[0] == 1 for b in X]
    model = PinballModel([((0, 1), PinballTable(depth=3))], smoothing=0).fit(X, y)
    assert model.decide((1, 0)).probability_of(True) == 1
    assert model.decide((0, 1)).probability_of(True) == 0
    numeric = PinballModel([((0, 1), PinballTable(depth=3))], smoothing=0).fit(X, [2 * b[0] for b in X])
    assert numeric.decide((1, 1)).score() == 2


def test_unseen_lane_backs_off_to_prefix():
    """A lane never seen in training falls back to its longest seen prefix."""
    model = PinballModel([((0, 1, 2), PinballTable(depth=4))], smoothing=0)
    model.fit([(1, 1, 0)], ["deep"]).fit([(0, 0, 0)], ["shallow"])
    assert model.decide((1, 0, 1)).choice == "deep"


def test_fit_soft_distils_teacher_probabilities():
    """Fixed-point teacher weights reproduce the teacher's distribution."""
    teacher = {"a": Fraction(3, 4), "b": Fraction(1, 4)}
    assert fixed_point(teacher, 8) == {"a": 192, "b": 64}
    model = PinballModel([((0,), PinballTable(depth=2))], smoothing=0)
    model.fit_soft([(0,)], [fixed_point(teacher, 8)])
    assert model.decide((0,)).probabilities == teacher


def test_bit_scores_zero_for_independent_bit():
    """Bit 0 decides the label, bit 1 is independent of it."""
    X = [(0, 0), (0, 1), (1, 0), (1, 1)]
    scores = bit_scores(X, [0, 0, 1, 1])
    assert scores[0] > 0 and scores[1] == 0


# ---- baselines and metrics ----

def test_baselines_learn_a_single_bit_rule():
    X = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)] * 4
    y = [bits[1] for bits in X]
    for learner in (IntegerNaiveBayes(), IntegerTree(max_depth=2)):
        learner.fit(X, y)
        decisions = [learner.decide(bits) for bits in X]
        assert accuracy(decisions, y) == 1
        assert sum(decisions[0].probabilities.values()) == 1


def test_control_routers_return_lanes():
    assert PrefixRouter(3).lane(0b1011) == (1, 1, 0, 1)
    assert ScrambleRouter(depth=6).lane(5) == ScrambleRouter(depth=6).lane(5)


def test_ece_zero_when_perfectly_calibrated():
    """Confidence 1 and always right -> ECE exactly 0."""
    X = [(0,), (1,)] * 10
    y = [bits[0] for bits in X]
    model = PinballModel([((0,), PrefixRouter(1))], smoothing=0).fit(X, y)
    assert ece([model.decide(bits) for bits in X], y) == 0


# ---- Hilbert checks ----

def test_terras_map_is_measure_preserving():
    """T: Z/2^B -> Z/2^(B-1) is exactly 2-to-1, for 3x+1 and 5x+1."""
    assert terras_preimage_counts(10) == {2}
    assert terras_preimage_counts(10, q=5) == {2}


def test_class_densities():
    """Squared norms of class indicators: 1/2, 1/4, 1/16, 1/16 (two residues mod 32), total 1."""
    d = class_densities(8)
    assert d[1] == Fraction(1, 2)
    assert d[3] == Fraction(1, 4)
    assert d[6] == Fraction(1, 16)
    assert d[8] == Fraction(1, 16)
    assert sum(d.values()) == 1


# ---- nesting, free composition, never-drain set ----

def test_drop_chain_examples():
    """27's class-96 orbit is 1 + 1 + 3 + 91; 5's is 1 + 1 + 1."""
    from collatz.pinball import drop_chain
    assert drop_chain(27) == [(82, 1), (41, 3), (31, 91)]
    assert drop_chain(5) == [(16, 1), (8, 1)]
    assert drop_chain(6) == []


def test_nesting_theorem():
    """Stopping orbit = first step + complete sub-drops, ending exactly at the destination."""
    from collatz.core import stopping_orbit
    from collatz.pinball import drop_chain
    for n in range(2, 6000):
        orbit = stopping_orbit(n)
        chain = drop_chain(n)
        assert len(orbit) == 1 + sum(k for _, k in chain)
        rebuilt = orbit[:1]
        for start, _ in chain:
            assert start > n and rebuilt[-1] == start
            rebuilt += stopping_orbit(start)
        assert rebuilt == orbit


def test_drop_tree_is_finite_and_consistent():
    """Every node's class is 1 + the sum of its children's classes."""
    from collatz.pinball import drop_tree

    def check(node):
        n, k, children = node
        assert k == 1 + sum(child[1] for child in children)
        for child in children:
            check(child)

    assert drop_tree(5) == (5, 3, [(16, 1, []), (8, 1, [])])
    for n in (27, 703, 871, 6171):
        check(drop_tree(n))


def test_any_sequence_of_parts_is_playable():
    """Free composition: concatenated lanes are realised by exactly one residue."""
    import random
    from collatz.pinball import realizing_residue
    table = PinballTable(depth=12)
    lanes = sorted({table.lane(n) for n in range(2, 600) if table.play(n)[1]})
    rng = random.Random(7)
    for _ in range(200):
        parts = [rng.choice(lanes) for _ in range(4)]
        word = tuple(b for part in parts for b in part)
        r, modulus = realizing_residue(word)
        assert _parities(r, len(word)) == word
        if modulus <= 4096:
            assert [m for m in range(modulus) if _parities(m, len(word)) == word] == [r]
        n = r + 5 * modulus
        for part in parts:
            assert table.lane(n) == part
            for parity in part:
                n = (3 * n + 1) // 2 if parity else n // 2


def _parities(n, length):
    word = []
    for _ in range(length):
        word.append(n % 2)
        n = (3 * n + 1) // 2 if n % 2 else n // 2
    return tuple(word)


def test_all_bumpers_is_minus_one():
    """The machine that never stops hitting bumpers is the 2-adic integer -1."""
    from collatz.pinball import realizing_residue
    for length in (1, 5, 20):
        assert realizing_residue((1,) * length) == (2 ** length - 1, 2 ** length)


def test_multiples_of_three_only_before_first_bumper():
    """Position rule: after a bumper no value in the vector is divisible by 3."""
    for n in range(2, 5000):
        vec = stopping_vector(n)
        first_odd = next(i for i, v in enumerate(vec) if v % 2 == 1) if any(v % 2 for v in vec) else len(vec)
        assert all(v % 3 for v in vec[first_odd + 1:])


def test_undrained_counts_and_dimension():
    """Undrained lanes thin out for 3x+1 at the entropy rate; not for 5x+1."""
    from collatz.pinball import entropy_dimension, undrained_count, undrained_growth_rate
    assert undrained_count(2) == 1
    assert undrained_count(4) == class_densities(4)[None] * 16
    assert round(entropy_dimension(), 4) == 0.95
    assert abs(undrained_growth_rate(400) - entropy_dimension()) < 0.01
    assert entropy_dimension(5) == 1.0
    assert undrained_growth_rate(200, q=5) > 0.99


# ---- mirror table: n -> n - |n/2| ----

def test_mirror_is_collatz_on_positives():
    from collatz.core import collatz_step
    from collatz.pinball.mirror import mirror_step
    assert all(mirror_step(n) == collatz_step(n) for n in range(1, 5000))


def test_mirror_negatives_escape_and_never_merge():
    """Magnitude rises every step, and the map is injective (no two orbits merge)."""
    from collatz.pinball.mirror import mirror_orbit, mirror_step
    assert mirror_orbit(-1, 6) == [-1, -2, -3, -8, -12, -18, -27]
    images = [mirror_step(-m) for m in range(1, 20000)]
    assert all(abs(img) > m for m, img in zip(range(1, 20000), images))
    assert len(set(images)) == len(images)


def test_mirror_back_inverts_step():
    from collatz.pinball.mirror import mirror_back, mirror_step
    for m in range(1, 5000):
        assert mirror_back(abs(mirror_step(-m)))[0] == m
    assert mirror_back(5) is None and mirror_back(4) is None


def test_halvings_become_powers_of_three():
    """Odd b -> next odd value: its 3-adic valuation equals v2(3b - 1)."""
    from collatz.core import v2
    from collatz.pinball.mirror import mirror_step
    for b in range(1, 4001, 2):
        n = mirror_step(-b)
        while n % 2 == 0:
            n = mirror_step(n)
        m, v3 = -n, 0
        while m % 3 == 0:
            m, v3 = m // 3, v3 + 1
        assert v3 == v2(3 * b - 1)


def test_age_is_three_adic_and_fibonacci():
    """min(age, t) depends only on m mod 2*3^t; P(age >= t) = F(t+3) / (2*3^t); no 'BB'."""
    from collatz.pinball.mirror import age, age_tail, age_word, seed
    assert (age(27), seed(27), age_word(27)) == (6, 1, "AAABAB")
    for t in range(1, 8):
        modulus = 2 * 3 ** t
        hits = sum(1 for r in range(modulus) if age(r + 7 * modulus) >= t)
        assert (hits, modulus) == age_tail(t)
        for r in range(0, modulus, 5):
            assert min(age(r + modulus), t) == min(age(r + 4 * modulus), t)
    assert not any("BB" in age_word(m) for m in range(1, 20000))
