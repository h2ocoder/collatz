"""Tests for collatz.schwarzschild: word horizons, Haar rates, the reversible tape."""

import itertools
import math
import random
from fractions import Fraction

import numpy as np
import pandas as pd
import pytest

from collatz.core import collatz_step, stopping_time
from collatz.pinball.nesting import entropy_dimension, realizing_residue
from collatz.schwarzschild import (
    COLLATZ,
    CollatzLike,
    absorb,
    bits_destroyed,
    capture_cross_section,
    captured,
    causal_depth,
    certified_kicks,
    cheapest_climb,
    compactness,
    contraction_sums,
    contraction_word,
    contraction_words,
    cramer_exponent,
    drift,
    drop_fraction,
    emit,
    erased_bits,
    head_speed,
    horizon,
    horizon_table,
    information_radius,
    lapse,
    largest_horizon,
    lift_tail,
    log2_ratio,
    longest_fall,
    longest_hover,
    mach_number,
    mass_bound,
    memory_rate,
    page_curve,
    phase,
    place_exponents,
    reach_exponent,
    size_steps,
    stagnation_radius,
    step_sigma,
    tail_constant,
    trapping_radius,
    weak_field_exponent,
    word_mass,
)

from collatz.schwarzschild.rates import bisect_root

FAMILY = [
    COLLATZ,
    CollatzLike.qx_plus_a(3, 5),
    CollatzLike.qx_plus_a(5, 1),
    CollatzLike.qx_plus_a(3, -1),
    CollatzLike.from_multipliers((1, 4, 4)),
    CollatzLike.from_multipliers((1, 2, 4)),
    CollatzLike.from_multipliers((1, 5, 5)),
    CollatzLike.from_multipliers((1, 3, 5, 7)),
    CollatzLike.from_multipliers((1, 6, 6, 6, 6)),
]

POSITIVE_FAMILY = [system for system in FAMILY if min(system.a) >= 0]


def words_of(system, length):
    return itertools.product(range(system.d), repeat=length)


def member(system, word):
    """A positive integer realizing word."""
    r, modulus = system.residue(word)
    return r if r > 0 else modulus


# ---- CollatzLike ----

def test_rejects_invalid_maps():
    with pytest.raises(ValueError):
        CollatzLike(1, (1,), (0,))
    with pytest.raises(ValueError):
        CollatzLike(2, (1, 3, 5), (0, 1))
    with pytest.raises(ValueError):
        CollatzLike(2, (1, 3), (0, 2))       # (3n + 2) / 2 is not an integer
    with pytest.raises(ValueError):
        CollatzLike(3, (1, 3, 3), (0, 0, 0))  # gcd(3, 3) != 1
    with pytest.raises(ValueError):
        CollatzLike(2, (0, 3), (0, 1))


def test_classic_map_is_the_repo_map():
    """One Terras step is one even step, or an odd step and the halving that follows."""
    for n in range(1, 2000):
        expected = collatz_step(n)
        if n % 2:
            expected = collatz_step(expected)
        assert COLLATZ.step(n) == expected


def test_from_multipliers_picks_small_offsets():
    system = CollatzLike.from_multipliers((1, 4, 4))
    assert system.a == (0, 2, 1)
    assert system.step(1) == 2 and system.step(2) == 3 and system.step(3) == 1


@pytest.mark.parametrize("system", FAMILY)
def test_word_map_reproduces_the_orbit(system):
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randrange(1, 10 ** 6)
        k = rng.randrange(1, 40)
        Q, C, length = system.word_map(system.word(n, k))
        x = n
        for _ in range(k):
            x = system.step(x)
        assert length == k
        assert Fraction(Q * n + C, system.d ** k) == x


@pytest.mark.parametrize("system", FAMILY)
def test_digit_words_are_a_bijection_with_residues(system):
    """Each word is one residue class, the digit bijection behind the causal cone."""
    k = 8 if system.d == 2 else 4
    seen = {}
    for n in range(1, system.d ** k + 1):
        seen.setdefault(system.word(n, k), set()).add(n % system.d ** k)
    assert len(seen) == system.d ** k
    assert all(len(residues) == 1 for residues in seen.values())


def test_residue_matches_pinball_realizing_residue():
    for word in itertools.product((0, 1), repeat=6):
        assert COLLATZ.residue(word) == realizing_residue(word)


@pytest.mark.parametrize("system", FAMILY)
def test_residue_realizes_its_word(system):
    for word in words_of(system, 4):
        assert system.word(member(system, word), 4) == word


# ---- Horizons ----

@pytest.mark.parametrize("system", FAMILY)
def test_lapse_identity(system):
    """1 - A(n) / n = (1 - Q / d^k)(1 - F / n), exactly, for every n."""
    for length in (1, 2, 5):
        for word in itertools.islice(words_of(system, length), 200):
            Q, _, k = system.word_map(word)
            if Q == system.d ** k:
                continue
            for n in (1, 2, 3, 7, 1000, 10 ** 12):
                left = drop_fraction(word, n, system)
                assert left == (1 - Fraction(Q, system.d ** k)) * lapse(word, n, system)


@pytest.mark.parametrize("system", FAMILY)
def test_infall_onto_the_horizon(system):
    """T^k(n) - F = (Q / d^k)(n - F) along the word."""
    rng = random.Random(2)
    for _ in range(200):
        n = rng.randrange(1, 10 ** 8)
        word = system.word(n, rng.randrange(1, 30))
        value, _ = emit(n, len(word), system)
        Q, _, k = system.word_map(word)
        radius = horizon(word, system)
        assert value - radius == Fraction(Q, system.d ** k) * (n - radius)


def test_word_is_the_time_one_map_of_a_null_ray():
    """A(n) is the flow of dr/dt = -beta (1 - F/n) for one unit of time, r = log2 n."""
    for word, n in (((1, 0), 37.0), ((1, 1, 0, 1, 0), 37.0), ((1, 1, 1, 0, 0), 3.0)):
        Q, C, k = COLLATZ.word_map(word)
        beta = bits_destroyed(word)
        radius = float(horizon(word))
        r, h = math.log2(n), 1 / 4000

        def speed(position):
            return -beta * (1 - radius / 2 ** position)

        for _ in range(4000):
            a = speed(r)
            b = speed(r + h * a / 2)
            c = speed(r + h * b / 2)
            d = speed(r + h * c)
            r += h * (a + 2 * b + 2 * c + d) / 6
        assert 2 ** r == pytest.approx((Q * n + C) / 2 ** k, rel=1e-10)


@pytest.mark.parametrize("system", POSITIVE_FAMILY)
def test_drop_iff_outside_horizon(system):
    """For a contracting word, A(n) < n exactly when n > F."""
    for word in itertools.islice(words_of(system, 5), 300):
        Q, C, k = system.word_map(word)
        if Q >= system.d ** k:
            continue
        radius = horizon(word, system)
        for n in list(range(1, 60)) + [10 ** 6]:
            image = Fraction(Q * n + C, system.d ** k)
            assert (image < n) == (n > radius)
            assert (image == n) == (n == radius)


@pytest.mark.parametrize("system, n, period", [
    (COLLATZ, 1, 2),
    (CollatzLike.qx_plus_a(3, 5), 5, 2),
    (CollatzLike.qx_plus_a(3, 5), 19, None),
    (CollatzLike.qx_plus_a(5, 1), 13, None),
    (CollatzLike.qx_plus_a(5, 1), 17, None),
    (CollatzLike.qx_plus_a(3, -1), 5, None),
    (CollatzLike.qx_plus_a(3, -1), 17, None),
    (CollatzLike.from_multipliers((1, 4, 4)), 1, 3),
])
def test_cycles_sit_on_their_horizon(system, n, period):
    """A periodic point equals F of its cycle's word (Bohm-Sontacchi)."""
    cycle = system.cycle_through(n)
    assert n in cycle
    if period is not None:
        assert len(cycle) == period
    for start in cycle:
        assert horizon(system.word(start, len(cycle)), system) == start


def test_being_on_the_horizon_with_the_right_word_means_periodic():
    """A positive integer equal to F(w) and realizing w returns to itself after w."""
    system = CollatzLike.qx_plus_a(5, 1)
    for length in range(1, 11):
        for word in itertools.product((0, 1), repeat=length):
            radius = horizon(word, system)
            if radius.denominator == 1 and radius > 0:
                n = int(radius)
                if system.word(n, length) == word:
                    assert emit(n, length, system)[0] == n


def test_horizon_and_residue_share_a_center():
    """The class of w is the d-adic ball around the rational F(w), mod d^k."""
    for system in FAMILY:
        k = 6 if system.d == 2 else 3
        for word in words_of(system, k):
            radius = horizon(word, system)
            r, modulus = system.residue(word)
            assert (radius.numerator - r * radius.denominator) % modulus == 0


def test_mass_scaling_and_mirror():
    """F is linear in the offset, so -1 mirrors the sign (3x - 1 against 3x + 1)."""
    plus = COLLATZ
    for a in (3, 5, 7, -1, -5):
        scaled = CollatzLike.qx_plus_a(3, a)
        for word in itertools.product((0, 1), repeat=7):
            if any(word):
                assert horizon(word, scaled) == a * horizon(word, plus)
    assert horizon((1,), CollatzLike.qx_plus_a(3, -1)) == 1
    assert horizon((1,), plus) == -1


def test_mass_is_forced_by_integrality():
    """A map with no offset is not integer valued, so the +1 cannot be switched off."""
    with pytest.raises(ValueError):
        CollatzLike(2, (1, 3), (0, 0))
    for q in ((1, 3), (1, 4, 4), (1, 2, 5), (1, 3, 5, 7), (1, 6, 6, 6, 6)):
        system = CollatzLike.from_multipliers(q)
        for r in range(1, system.d):
            if math.gcd(r, system.d) == 1:
                assert system.a[r] != 0
    assert word_mass((0, 0, 0)) == 0
    assert horizon((0, 0, 0)) == 0


def test_cycle_side_is_set_by_the_sign_of_the_offset():
    """Positive cycles use contracting words for a > 0, expanding words for a < 0."""
    for system, starts in ((COLLATZ, (1,)), (CollatzLike.qx_plus_a(5, 1), (1, 13, 17)),
                           (CollatzLike.qx_plus_a(3, 5), (1, 5, 19, 23))):
        for start in starts:
            cycle = system.cycle_through(start)
            Q, _, k = system.word_map(system.word(cycle[0], len(cycle)))
            assert Q < 2 ** k
    mirror = CollatzLike.qx_plus_a(3, -1)
    for start in (1, 5, 17):
        cycle = mirror.cycle_through(start)
        Q, _, k = mirror.word_map(mirror.word(cycle[0], len(cycle)))
        assert Q > 2 ** k


def test_word_mass_formula():
    """1 + zeta / n is the product of (1 + a_r / (q_r n_i)) along the orbit."""
    rng = random.Random(3)
    for system in POSITIVE_FAMILY:
        for _ in range(100):
            n = rng.randrange(1, 10 ** 6)
            k = rng.randrange(1, 30)
            word, x = system.word(n, k), n
            product = Fraction(1)
            for r in word:
                product *= 1 + Fraction(system.a[r], system.q[r] * x)
                x = system.step(x)
            assert 1 + word_mass(word, system) / n == product


def test_bits_destroyed_is_the_bit_destruction_identity():
    """Over a first-drop word, beta = ceil(s log2 3) - s log2 3."""
    for s in range(1, 12):
        for word in contraction_words(s):
            assert sum(word) == s
            expected = math.ceil(s * math.log2(3)) - s * math.log2(3)
            assert bits_destroyed(word) == pytest.approx(expected, abs=1e-12)


def test_contraction_word_counts_are_a100982():
    counts = [len(contraction_words(s)) for s in range(0, 12)]
    assert counts == [1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961]


def test_contraction_words_contract_first_at_the_end():
    for s in range(1, 9):
        for word in contraction_words(s):
            kicks = 0
            for t, bit in enumerate(word, start=1):
                kicks += bit
                assert (3 ** kicks < 2 ** t) == (t == len(word))


def test_contraction_word_terras_length_matches_core_stopping_time():
    """Each odd step of the core map merges into a Terras step: k + s = stopping time."""
    for n in range(2, 5000):
        word = contraction_word(n)
        assert len(word) + sum(word) == stopping_time(n)


def test_coefficient_stopping_conjecture_on_a_range():
    """No n in 2..2^15 is on or inside the horizon of its first contraction word."""
    for n in range(2, 1 << 15):
        assert not captured(n)
    assert captured(1)
    assert compactness(1) == 1


def test_non_positive_integers_are_rejected():
    """The repo's core functions reject n <= 0, and a zero would divide by zero here."""
    for n in (0, -3):
        with pytest.raises(ValueError):
            compactness(n)
        with pytest.raises(ValueError):
            captured(n)
    with pytest.raises(ValueError):
        horizon_table(0, 5)


def test_compactness_examples():
    assert compactness(3) == Fraction(5, 21)
    assert compactness(5) == Fraction(1, 5)
    assert compactness(2) == 0


def test_most_compact_small_integer_is_47():
    best = max(range(2, 1 << 12), key=lambda n: compactness(n))
    assert best == 47
    assert float(compactness(47)) == pytest.approx(0.71337, abs=1e-5)


def test_mass_bound_on_first_contraction_words():
    for s in range(1, 10):
        for word in contraction_words(s):
            assert mass_bound(word) == Fraction(s, 3)
            assert word_mass(word) <= Fraction(s, 3)
            assert horizon(word) <= largest_horizon(s)


def test_mass_bound_holds_across_the_family():
    for system in POSITIVE_FAMILY:
        for n in range(2, 400):
            word = contraction_word(n, system, max_steps=2000)
            if word is not None:
                assert word_mass(word, system) <= mass_bound(word, system)


def test_largest_horizon_is_tight_at_one_kick():
    assert largest_horizon(0) == 0
    assert largest_horizon(1) == 1
    assert horizon((1, 0)) == largest_horizon(1)


def test_certified_kicks_logic():
    assert certified_kicks(10) == 4
    assert largest_horizon(5) > 10
    assert all(largest_horizon(s) <= 10 for s in range(1, 5))
    assert certified_kicks(10 ** 9, s_limit=50) == 50


def test_horizon_table_is_a_batch_dataframe():
    table = horizon_table(2, 200)
    assert isinstance(table, pd.DataFrame)
    assert len(table) == 198
    row = table[table.n == 3].iloc[0]
    assert row.k == 4 and row.kicks == 2
    assert row.horizon == pytest.approx(5 / 7)
    assert not table.captured.any()


def test_horizon_table_marks_words_that_never_contract():
    mirror = CollatzLike.qx_plus_a(3, -1)
    assert contraction_word(5, mirror, max_steps=300) is None
    assert compactness(2, mirror) is not None


def test_log2_ratio_is_accurate_near_one():
    x, y = 3 ** 306 * 2 ** 40, 3 ** 306 * 2 ** 40 + 1
    exact = float(Fraction(x - y, y)) / math.log(2)
    assert log2_ratio(x, y) == pytest.approx(exact, rel=1e-9)
    assert log2_ratio(8, 1) == 3


# ---- Haar rates ----

@pytest.mark.parametrize("system", FAMILY)
def test_ledger_is_exact(system):
    """c = g + memory, and the signed size steps average to -g."""
    assert head_speed(system) == pytest.approx(drift(system) + memory_rate(system))
    assert sum(size_steps(system)) / system.d == pytest.approx(-drift(system))


@pytest.mark.parametrize("system", POSITIVE_FAMILY)
def test_size_ledger_along_an_orbit(system):
    """T^t(n) / n = (Q / d^t) * product of the offset corrections, exactly."""
    rng = random.Random(4)
    for _ in range(100):
        n = rng.randrange(1, 10 ** 7)
        t = rng.randrange(1, 40)
        x, scale = n, Fraction(1)
        for _ in range(t):
            r = x % system.d
            scale *= Fraction(system.q[r], system.d) * (1 + Fraction(system.a[r], system.q[r] * x))
            x = system.step(x)
        assert Fraction(x, n) == scale


@pytest.mark.parametrize("system", FAMILY)
def test_product_formula(system):
    assert sum(place_exponents(system).values()) == pytest.approx(0.0, abs=1e-12)


def test_classic_constants():
    assert head_speed() == 1
    assert drift() == pytest.approx(1 - math.log2(3) / 2)
    assert memory_rate() == pytest.approx(math.log2(3) / 2)
    assert step_sigma() == pytest.approx(math.log2(3) / 2)
    assert drift() + step_sigma() == pytest.approx(1)
    assert mach_number() == pytest.approx(0.2618595, abs=1e-6)
    places = place_exponents()
    assert places[2] == pytest.approx(1)
    assert places[3] == pytest.approx(-math.log2(3) / 2)


def test_fastest_motion_is_speed_of_light_around_the_flow():
    """Up is sigma - g, down is -(sigma + g): the two null rays of a river."""
    down, up = size_steps()
    assert up == pytest.approx(step_sigma() - drift())
    assert down == pytest.approx(-(step_sigma() + drift()))


@pytest.mark.parametrize("q", [(1, 3), (1, 4, 4), (1, 1, 7), (1, 3, 5, 7), (1, 5, 5, 5), (1, 6, 6, 6, 6)])
def test_theta_is_one_when_multipliers_sum_to_d_squared(q):
    system = CollatzLike.from_multipliers(q)
    assert cramer_exponent(system) == 1.0
    assert phase(system) == "critical"
    assert sum((x / system.d) for x in q) / system.d == pytest.approx(1)


@pytest.mark.parametrize("q", [(1, 2, 4), (1, 2, 5), (1, 4, 5), (1, 5, 5), (1, 2, 7), (1, 4, 4, 6, 6)])
def test_theta_solves_the_moment_equation(q):
    system = CollatzLike.from_multipliers(q)
    theta = cramer_exponent(system)
    d = system.d
    assert sum((x / d) ** theta for x in q) / d == pytest.approx(1, abs=1e-10)
    assert theta > 0


def test_bisect_root_finds_a_sign_change():
    assert bisect_root(lambda x: x * x - 2, 0.0, 2.0) == pytest.approx(math.sqrt(2), abs=1e-14)
    assert bisect_root(lambda x: 1 - x, 0.0, 3.0) == pytest.approx(1.0, abs=1e-14)


def test_theta_edge_cases():
    assert cramer_exponent(CollatzLike.from_multipliers((1, 2, 2))) == math.inf
    assert cramer_exponent(CollatzLike.qx_plus_a(5, 1)) == 0.0
    assert reach_exponent(CollatzLike.qx_plus_a(5, 1)) == math.inf
    assert reach_exponent(CollatzLike.from_multipliers((1, 2, 2))) == 1


def test_weak_field_limit_improves_toward_criticality():
    """The Gaussian exponent 2g / (sigma^2 ln 2) tracks theta as g -> 0."""
    near = CollatzLike.from_multipliers((1, 5, 5))
    assert drift(near) < 0.04
    assert weak_field_exponent(near) == pytest.approx(cramer_exponent(near), rel=0.02)
    far = CollatzLike.from_multipliers((1, 2, 4))
    assert abs(weak_field_exponent(far) / cramer_exponent(far) - 1) > 0.25


def test_two_branch_mach_equation():
    """theta solves y M = ln cosh y with y = theta sigma ln 2, M = g / sigma."""
    y = cramer_exponent() * step_sigma() * math.log(2)
    assert y == pytest.approx(math.log(3) / 2)
    assert math.log(math.cosh(y)) == pytest.approx(mach_number() * y)


def test_cheapest_climb_matches_lagarias_weiss_slope():
    path = cheapest_climb()
    assert path.law == pytest.approx((0.25, 0.75))
    assert path.speed == pytest.approx(0.75 * math.log2(3) - 1)
    # Kontorovich-Lagarias quote the slope in natural logs as 0.75 ln 3 - ln 2 = 0.1308.
    assert path.speed * math.log(2) == pytest.approx(0.1308, abs=5e-5)
    assert path.cost == pytest.approx(path.speed)


@pytest.mark.parametrize("q", [(1, 2, 4), (1, 2, 5), (1, 4, 5), (1, 3, 5, 7), (1, 4, 4, 6, 6)])
def test_cheapest_climb_cost_over_speed_is_theta(q):
    system = CollatzLike.from_multipliers(q)
    path = cheapest_climb(system)
    assert path.cost / path.speed == pytest.approx(cramer_exponent(system), rel=1e-9)
    assert sum(path.law) == pytest.approx(1)


def test_climb_absent_when_undefined():
    assert cheapest_climb(CollatzLike.qx_plus_a(5, 1)) is None
    assert cheapest_climb(CollatzLike.from_multipliers((1, 2, 2))) is None


def test_longest_hover_is_the_never_drain_rate():
    path = longest_hover()
    assert path.speed == pytest.approx(0.0, abs=1e-12)
    assert path.cost == pytest.approx(1 - entropy_dimension(3), abs=1e-12)
    assert path.law[1] == pytest.approx(math.log(2) / math.log(3))
    assert 1 / path.cost == pytest.approx(19.98, abs=0.01)
    assert longest_hover(CollatzLike.from_multipliers((1, 2, 2))) is None
    assert longest_hover(CollatzLike.qx_plus_a(5, 1)) is None


def test_longest_fall_reproduces_lagarias_weiss_constant():
    """Saturating H(p) = E_p[log2 q] gives gamma = 41.677647 and ones-ratio 0.609091."""
    path = longest_fall()
    assert 1 / (path.cost * math.log(2)) == pytest.approx(41.677647, abs=2e-6)
    assert path.law[1] == pytest.approx(0.609090, abs=2e-6)
    assert path.speed == pytest.approx(-path.cost)


def test_longest_fall_handles_degenerate_maps():
    assert longest_fall(CollatzLike.qx_plus_a(5, 1)) is None
    equal = CollatzLike.from_multipliers((1, 1))
    assert longest_fall(equal).law == pytest.approx((0.5, 0.5))


def test_typical_lifetime_is_the_classical_constant():
    """B / g steps per bit is 2 / ln(4/3) = 6.95212 per unit of log n."""
    assert 1 / (drift() * math.log(2)) == pytest.approx(6.95212, abs=1e-5)


def test_tail_constant_closed_form():
    assert tail_constant() == pytest.approx(1 / math.log(27 / 16))
    assert tail_constant(CollatzLike.from_multipliers((1, 2, 4))) is None


def test_stagnation_radius_is_the_typical_word_horizon():
    for q, a in ((3, 1), (3, 5), (3, 7), (1, 1)):
        system = CollatzLike.qx_plus_a(q, a)
        assert stagnation_radius(system) == pytest.approx(a / (4 - q), rel=1e-9)
        assert float(horizon((1, 0), system)) == pytest.approx(a / (4 - q))
    assert stagnation_radius(CollatzLike.qx_plus_a(5, 1)) is None
    assert stagnation_radius(CollatzLike.qx_plus_a(3, -1)) is None
    assert horizon((1, 0), CollatzLike.qx_plus_a(5, 1)) == -1    # the 5x + 1 cycle at -1


def test_trapping_radius_is_a_hard_horizon():
    """Interior maps decrease on every branch above the radius, with no statistics."""
    for q in ((1, 2, 2), (1, 1), (1, 3, 3, 3), (1, 2, 3, 4, 4)):
        system = CollatzLike.from_multipliers(q)
        radius = trapping_radius(system)
        assert phase(system) == "interior"
        for n in range(1, 3000):
            if n > radius:
                assert system.step(n) < n
    assert trapping_radius(COLLATZ) is None
    assert trapping_radius(CollatzLike(3, (1, 2, 2), (0, -5, -1))) is None


def test_phase_labels():
    assert phase() == "critical"
    assert phase(CollatzLike.from_multipliers((1, 2, 4))) == "thin"
    assert phase(CollatzLike.from_multipliers((1, 4, 5))) == "heavy"
    assert phase(CollatzLike.qx_plus_a(5, 1)) == "outflow"
    assert phase(CollatzLike.from_multipliers((1, 2, 2))) == "interior"


def exact_lift_tail(lift, up, down, horizon_steps):
    """P(sup S_t >= lift) for a fair +up / -down walk, by dynamic programming."""
    mass = np.zeros(horizon_steps + 2)
    mass[0] = 1.0
    hit = 0.0
    kicks = np.arange(horizon_steps + 2)
    for t in range(1, horizon_steps + 1):
        new = 0.5 * mass
        new[1:] += 0.5 * mass[:-1]
        reached = kicks * up - (t - kicks) * down >= lift
        hit += new[reached].sum()
        new[reached] = 0
        mass = new
    return hit


def test_lift_tail_matches_exact_first_passage():
    up, down = math.log2(1.5), 1.0
    for lift in (1, 4, 8, 16):
        exact = exact_lift_tail(lift, up, down, 1500)
        assert lift_tail(lift) == pytest.approx(exact, rel=0.01)


def test_doob_inequality_holds():
    """n is a martingale up to offsets, so mu(lift >= M) <= 2^-M at theta = 1."""
    for lift in (1, 2, 5, 10, 20):
        assert lift_tail(lift) <= 2.0 ** -lift


def test_information_radius_is_linear_with_slope_theta():
    for system, depth in ((COLLATZ, 30), (CollatzLike.from_multipliers((1, 2, 5)), 12)):
        theta = cramer_exponent(system)
        slope = (information_radius(depth, system) - information_radius(depth / 2, system)) / (depth / 2)
        assert slope == pytest.approx(theta, rel=0.02)


def test_lift_tail_edge_cases():
    assert lift_tail(5, CollatzLike.qx_plus_a(5, 1)) == 1.0
    assert lift_tail(5, CollatzLike.from_multipliers((1, 2, 2))) == 0.0


def test_information_radius_edge_cases():
    """Lift is free in outflow, impossible in the interior, and never underflows."""
    assert information_radius(5, CollatzLike.qx_plus_a(5, 1)) == 0.0
    assert information_radius(5, CollatzLike.from_multipliers((1, 2, 2))) == math.inf
    assert information_radius(2000, samples=500) == pytest.approx(2000.26, abs=0.1)
    assert lift_tail(2000, samples=500) == 0.0


# ---- The tape ----

@pytest.mark.parametrize("system", FAMILY)
def test_tape_is_reversible(system):
    rng = random.Random(5)
    for _ in range(300):
        n = rng.randrange(1, 10 ** 9)
        t = rng.randrange(0, 60)
        value, word = emit(n, t, system)
        assert absorb(value, word, system) == n


@pytest.mark.parametrize("system", FAMILY)
def test_causal_cone(system):
    """Digit p of the address first reaches the word at step p, on every branch."""
    rng = random.Random(6)
    for _ in range(200):
        n = rng.randrange(1, 10 ** 6)
        position = rng.randrange(0, 20)
        assert causal_depth(n, position, position, system)
        assert not causal_depth(n, position, position + 1, system)


@pytest.mark.parametrize("system", FAMILY)
def test_values_depend_on_truncated_address(system):
    """T^t(n) mod d^m depends only on n mod d^(m + t)."""
    rng = random.Random(7)
    for _ in range(300):
        t = rng.randrange(1, 8)
        m = rng.randrange(1, 6)
        n = rng.randrange(1, 10 ** 6)
        other = n + rng.randrange(1, 50) * system.d ** (m + t)
        assert (emit(n, t, system)[0] - emit(other, t, system)[0]) % system.d ** m == 0


def test_page_curve_identities():
    table = page_curve(10, 60)
    assert table.value_entropy.iloc[0] == pytest.approx(10)
    assert table.mutual_information.iloc[0] == pytest.approx(0)
    assert table.word_entropy.iloc[10] == 10
    assert table.word_entropy.iloc[30] == 10
    assert (table.mutual_information >= -1e-9).all()
    assert table.mutual_information.idxmax() == 10


def test_page_curve_on_a_base_three_map():
    system = CollatzLike.from_multipliers((1, 4, 4))
    table = page_curve(6, 40, system)
    assert table.value_entropy.iloc[0] == pytest.approx(6 * math.log2(3))
    assert table.word_entropy.iloc[6] == pytest.approx(6 * math.log2(3))


def test_page_curve_survives_large_values():
    system = CollatzLike.from_multipliers((1, 5, 5))
    table = page_curve(4, 300, system)
    assert (table.value_entropy >= 0).all()


def test_page_curve_overflow_guard_sees_negative_values():
    """Exact integers past 64 bits, compared with a direct computation of the same orbit."""
    system = CollatzLike.qx_plus_a(5, -7)
    table = page_curve(4, 120, system)
    values = list(range(16, 32))
    for t in (60, 120):
        current = values
        for _ in range(t):
            current = [system.step(v) for v in current]
        assert table.value_entropy.iloc[t] == pytest.approx(
            -sum((c := current.count(v) / 16) * math.log2(c) for v in set(current)))


def test_drain_spectrum_is_exactly_geometric():
    """Over a full period, v2(3n + 1) = m on a fraction 2^-m of odd n."""
    period = 1 << 14
    counts = {}
    for n in range(1, 2 * period, 2):
        value = 3 * n + 1
        m = (value & -value).bit_length() - 1
        counts[m] = counts.get(m, 0) + 1
    for m in range(1, 12):
        assert counts[m] == period >> m


def test_erased_bits_identity_and_monotone_descent():
    """H(coin | y mod 3^m) = 1 - (H_m - H_(m-1)) / 2, falling toward g from above."""
    previous = 1.0
    for level in range(1, 8):
        result = erased_bits(level)
        assert result["identity_gap"] == pytest.approx(0, abs=1e-9)
        assert drift() < result["erased"] < previous
        previous = result["erased"]
    assert erased_bits(1)["erased"] == pytest.approx(2 / 3 * 0.8112781, abs=1e-6)


def test_equal_multipliers_have_no_step_spread():
    """With sigma = 0 the Mach number is infinite, not a division error."""
    inward = CollatzLike.from_multipliers((1, 1))
    assert mach_number(inward) == math.inf
    assert weak_field_exponent(inward) == math.inf
    outward = CollatzLike.from_multipliers((3, 3))
    assert mach_number(outward) == -math.inf


# ---- The mass-radius relation ----

def test_scaled_map_conjugates_by_the_mass():
    assert COLLATZ.scaled(5) == CollatzLike.qx_plus_a(3, 5)
    assert COLLATZ.scaled(-1) == CollatzLike.qx_plus_a(3, -1)
    with pytest.raises(ValueError):
        COLLATZ.scaled(2)
    for base, m in ((CollatzLike.from_multipliers((1, 4, 4)), 5),
                    (CollatzLike.from_multipliers((1, 2, 5)), 7),
                    (CollatzLike.from_multipliers((1, 3, 5, 7)), 3)):
        scaled = base.scaled(m)
        for n in range(1, 500):
            assert scaled.step(m * n) == m * base.step(n)


def test_scaled_horizon_is_linear_in_mass():
    """Digit r of T is digit m r of T_m, and F_m = m F on the matching words."""
    base = CollatzLike.from_multipliers((1, 4, 4))
    m = 5
    scaled = base.scaled(m)
    for word in words_of(base, 3):
        image = tuple(m * r % base.d for r in word)
        assert horizon(image, scaled) == m * horizon(word, base)


def test_contraction_sums_match_the_listing():
    sums = contraction_sums(9)
    for s in range(0, 10):
        words = contraction_words(s)
        k, count, total = sums[s]
        assert k == len(words[0])
        assert count == len(words)
        assert total == sum(COLLATZ.word_map(word).C for word in words)


def test_cross_section_is_the_mean_first_contraction_horizon():
    """Partial sums by listing agree with the DP, and the tail is negligible."""
    direct = sum(horizon(word) / 2 ** len(word)
                 for s in range(1, 11) for word in contraction_words(s))
    assert capture_cross_section(10) == pytest.approx(float(direct), rel=1e-12)
    assert capture_cross_section() == pytest.approx(1.8137, abs=5e-4)
    assert capture_cross_section(400) == pytest.approx(capture_cross_section(800), abs=1e-9)


def test_each_word_captures_its_expected_share_of_integers():
    """A word of length k captures a F / 2^k integers of 3x + a, up to one."""
    for a in (101, 1001):
        system = CollatzLike.qx_plus_a(3, a)
        for word in contraction_words(3) + contraction_words(5):
            radius = horizon(word, system)
            r, modulus = system.residue(word)
            members = range(r or modulus, int(radius) + 1, modulus)
            assert abs(len(members) - radius / modulus) <= 1
            for n in members:
                assert system.word(n, len(word)) == word and captured(n, system)


def test_captured_is_not_one_way():
    """A captured integer can still drop later: 3x + 7 at n = 3."""
    system = CollatzLike.qx_plus_a(3, 7)
    assert captured(3, system)
    value, _ = emit(3, len(contraction_word(3, system)), system)
    assert value >= 3
    assert emit(3, 3, system)[0] < 3 or emit(3, 4, system)[0] < 3
