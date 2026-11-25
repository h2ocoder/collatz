"""Tests for scripts/matmul_exponent/nine_fourths.py (SCRUM-82).

Every computed claim in docs/Explorations/Matrix Multiplication Exponent.md has a test here.
"""

import itertools
import sys
from fractions import Fraction as Fr
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "matmul_exponent"))

import nine_fourths as nf  # noqa: E402

GRID = [Fr(p, q) for q in (1, 2, 3, 4) for p in range(0, 3 * q + 1)]
POSITIVE = sorted({v for v in GRID if v > 0})
WEIGHTS = [(1, 1, 1), (1, 1, Fr(3, 4)), (1, 1, Fr(2, 3)), (1, 1, Fr(1, 2)), (1, 1, Fr(1, 4)),
           (2, 1, 1), (3, 2, 2), (5, 4, 3), (3, 1, 1), (2, 2, 1), (Fr(1, 3), 2, Fr(5, 2))]
# Just inside the triangle regime: the closed form beats the flat value x + y by 4e-4 down to 2e-10.
NEAR_BOUNDARY = [(5, 4, Fr(9, 4)), (10, 1, Fr(23, 25)), (3, 2, Fr(121, 100)),
                 (1, 1, Fr(501, 1000)), (1, 1, Fr(50001, 100000))]
ARM_GRID = [Fr(p, 12) for p in range(0, 13)]
HALVES = [Fr(p, 2) for p in range(1, 7)]


# ---- A. the tripod ([LB]) ----

def test_tripod_rate_at_unit_arms_is_eight_thirds():
    assert nf.tripod_rate((1, 1, 1)) == Fr(8, 3)


def test_tripod_rate_reciprocal_term_vanishes_on_a_zero_arm():
    assert nf.tripod_rate((2, 3, 0)) == 5
    assert nf.tripod_rate((0, 0, 7)) == 7


def test_tripod_rate_rejects_negative_arms():
    with pytest.raises(ValueError):
        nf.tripod_rate((1, -1, 1))


def test_square_product_three_wires_of_length_two():
    assert nf.wire_price((1, 1, 1), (1, 1, 1)) == 6
    assert nf.tripod_bound((1, 1, 1), (1, 1, 1)) == Fr(9, 4)


def test_wire_price_is_weight_times_distance():
    x, y, z = Fr(2), Fr(3), Fr(5)
    a, b, c = Fr(1, 2), Fr(1, 3), Fr(1, 7)
    assert nf.wire_price((x, y, z), (a, b, c)) == x * (a + c) + y * (a + b) + z * (b + c)


def test_square_bound_is_at_most_nine_fourths_with_equality_only_at_equal_arms():
    for arms in itertools.product(ARM_GRID, repeat=3):
        if sum(arms) == 0:
            continue
        value = nf.tripod_bound((1, 1, 1), arms)
        assert value <= Fr(9, 4)
        assert (value == Fr(9, 4)) == (arms[0] == arms[1] == arms[2])


def test_nine_fourths_is_two_over_one_minus_one_ninth():
    for arm in POSITIVE:
        equal = (arm, arm, arm)
        assert nf.tripod_rate(equal) == (1 - Fr(1, 9)) * sum(equal)
        assert nf.tripod_bound((1, 1, 1), equal) == Fr(2) / (1 - Fr(1, 9))
    assert abs(nf.sqrt_equation_defect((1, 1, 1), nf.rectangular_exponent(1, 1, 1))) < 1e-12


# ---- the rectangular closed form ([Lean]) ----

def test_lean_form_at_the_square_and_homogeneity():
    assert nf.rectangular_exponent(1, 1, 1) == Fr(9, 4)
    for t in POSITIVE:
        assert nf.rectangular_exponent(t, t, t) == Fr(9, 4) * t
        assert nf.rectangular_exponent(2 * t, 3 * t, 5 * t) == t * nf.rectangular_exponent(2, 3, 5)


def test_lean_form_equals_the_symmetric_form_everywhere_on_the_grid():
    for w in itertools.product(GRID, repeat=3):
        assert nf.rectangular_exponent(*w) == nf.rectangular_exponent_symmetric(*w)


def test_lean_form_is_symmetric_in_its_arguments():
    for w in itertools.combinations_with_replacement(GRID, 3):
        values = {nf.rectangular_exponent(*p) for p in itertools.permutations(w)}
        assert len(values) == 1


def test_lean_form_clamps_negative_weights_and_is_flat_on_coordinate_planes():
    assert nf.rectangular_exponent(2, 3, 0) == 5
    assert nf.rectangular_exponent(2, 3, -1) == 5
    assert nf.rectangular_exponent(2, -1, -1) == 2


def test_symmetric_form_clamps_negative_weights_like_the_lean_form():
    signed = [Fr(p, 2) for p in range(-4, 7)]
    for w in itertools.product(signed, repeat=3):
        assert nf.rectangular_exponent_symmetric(*w) == nf.rectangular_exponent(*w)


def test_one_one_z_family_is_a_square_over_z():
    for z in POSITIVE:
        if z > 1:
            continue
        expected = (z + Fr(1, 2)) ** 2 / z if z >= Fr(1, 2) else Fr(2)
        assert nf.rectangular_exponent(1, 1, z) == expected


def test_dual_exponent_is_one_half_in_the_closed_form():
    twos = [z for z in POSITIVE if z <= 1 and nf.rectangular_exponent(1, 1, z) == 2]
    assert max(twos) == Fr(1, 2)
    assert nf.rectangular_exponent(1, 1, Fr(1, 2) + Fr(1, 1000)) > 2


def test_closed_form_dominates_the_bounds_stated_in_the_paper():
    for x, y, z in itertools.product(POSITIVE, repeat=3):
        value = nf.rectangular_exponent(x, y, z)
        assert value >= max(nf.pair_sums((x, y, z)))
        assert value >= Fr(3, 4) * (x + y + z)
        assert (value == Fr(3, 4) * (x + y + z)) == (x == y == z)
        assert value >= nf.paper_rectangular_lower_bound(x, y, z)


def test_paper_bound_gives_alpha_at_most_two_thirds_and_closed_form_one_half():
    zs = [Fr(p, 120) for p in range(1, 121)]
    paper_twos = [z for z in zs if nf.paper_rectangular_lower_bound(1, 1, z) == 2]
    closed_twos = [z for z in zs if nf.rectangular_exponent(1, 1, z) == 2]
    assert max(paper_twos) == Fr(2, 3)
    assert max(closed_twos) == Fr(1, 2)


# ---- closed form == tripod bound ----

def test_optimal_arms_attain_the_closed_form_exactly():
    for w in itertools.product(POSITIVE, repeat=3):
        assert nf.tripod_bound(w, nf.optimal_arms(w)) == nf.rectangular_exponent(*w)


def test_optimal_arms_are_equal_for_the_square():
    arms = nf.optimal_arms((1, 1, 1))
    assert arms[0] == arms[1] == arms[2] > 0


def test_no_arms_on_the_grid_beat_the_closed_form():
    for w in WEIGHTS + NEAR_BOUNDARY:
        best = nf.rectangular_exponent(*w)
        for arms in itertools.product(ARM_GRID, repeat=3):
            if sum(arms) > 0:
                assert nf.tripod_bound(w, arms) <= best


@pytest.mark.parametrize("w", WEIGHTS)
def test_brute_force_supremum_matches_the_closed_form(w):
    value, arms = nf.tripod_sup_numeric(w)
    assert value == pytest.approx(float(nf.rectangular_exponent(*w)), abs=1e-9)
    assert min(arms) >= 0 and sum(arms) == pytest.approx(1.0)


@pytest.mark.parametrize("w", NEAR_BOUNDARY)
def test_brute_force_resolves_the_regime_boundary(w):
    """The search must find the interior optimum, not stop at the flat value x + y."""
    closed = nf.rectangular_exponent(*w)
    flat = max(nf.pair_sums(w))
    assert closed > flat
    value, arms = nf.tripod_sup_numeric(w)
    assert abs(value - float(closed)) < float(closed - flat) / 100
    assert min(arms) > 0


def test_brute_force_matches_the_closed_form_on_a_grid_of_weights():
    for w in itertools.product(HALVES, repeat=3):
        value, _ = nf.tripod_sup_numeric(w)
        assert value == pytest.approx(float(nf.rectangular_exponent(*w)), abs=1e-9)


def test_closed_form_is_the_least_feasible_point_of_the_square_root_equation():
    for w in WEIGHTS + NEAR_BOUNDARY:
        lam = nf.rectangular_exponent(*w)
        top = max(nf.pair_sums(w))
        assert lam >= top
        defect = nf.sqrt_equation_defect(w, lam)
        if nf.in_triangle_regime(*w):
            assert lam > top
            assert abs(defect) < 1e-9
            assert nf.sqrt_equation_defect(w, (lam + top) / 2) < 0
        else:
            assert lam == top
            assert defect >= -1e-12


# ---- B. the growth lemma ([UB]) ----

def test_growth_h_is_the_paper_product():
    value = Fr(1)
    for a in range(1, 60):
        assert nf.growth_h(a) == value
        value *= 1 + Fr(1, 3 * a)


def test_growth_lemma_inequalities_hold_exactly():
    h = Fr(1)
    for a in range(1, 400):
        if a > 1:
            h *= nf.growth_ratio(a)
        d = Fr(3 * a - 1, 2) * h
        assert h ** 3 >= a
        assert d ** 3 >= a ** 4


def test_growth_d_matches_its_definition():
    assert nf.growth_d(1) == 1
    assert nf.growth_d(7) == Fr(20, 2) * nf.growth_h(7)


def test_growth_exponent_is_four_thirds_and_gives_nine_fourths():
    assert nf.growth_exponent_numeric() == pytest.approx(4 / 3, abs=1e-4)
    assert nf.omega_from_growth() == Fr(9, 4)


@pytest.mark.parametrize("m,n", [(1, 2), (2, 3), (3, 4), (3, 5), (4, 6)])
def test_growth_sensitivity_exponent_is_two_m_over_n(m, n):
    assert nf.growth_exponent_numeric(m, n) == pytest.approx(2 * m / n, abs=1e-4)
    assert nf.omega_from_growth(m, n) == Fr(3 * n, 2 * m)


# ---- C. the Collatz side ----

def test_two_step_branches_of_3x_plus_1():
    assert nf.two_step_branches() == {
        0: (Fr(1, 4), Fr(0)),
        1: (Fr(3, 4), Fr(1, 4)),
        2: (Fr(3, 4), Fr(1, 2)),
        3: (Fr(9, 4), Fr(5, 4)),
    }


@pytest.mark.parametrize("a,c", [(3, 1), (3, -1), (3, 5), (5, 1), (7, 1), (5, -3)])
def test_two_step_branches_agree_with_iteration(a, c):
    branches = nf.two_step_branches(a, c)
    for n in range(12, 2000):
        slope, offset = branches[n % 4]
        assert nf.terras(nf.terras(n, a, c), a, c) == slope * n + offset


def test_two_step_branches_need_odd_parameters():
    with pytest.raises(ValueError):
        nf.two_step_branches(4, 1)
    with pytest.raises(ValueError):
        nf.two_step_branches(3, 2)


def test_nine_fourths_is_two_odd_steps_in_collatz_core():
    for n in range(3, 20000, 4):
        assert 4 * nf.four_collatz_steps(n) == 9 * n + 5


def test_slopes_and_densities_and_their_means():
    slopes = nf.two_step_slopes()
    assert slopes == {Fr(1, 4): Fr(1, 4), Fr(3, 4): Fr(1, 2), Fr(9, 4): Fr(1, 4)}
    assert sum(s * w for s, w in slopes.items()) == 1
    fourth_power_of_geometric_mean = Fr(1)
    for slope, density in slopes.items():
        fourth_power_of_geometric_mean *= slope ** int(4 * density)
    assert fourth_power_of_geometric_mean == Fr(3, 4) ** 4


def test_the_three_slopes_are_omega_minus_two_omega_over_three_and_omega():
    omega = Fr(9, 4)
    assert set(nf.two_step_slopes()) == {omega - 2, omega / 3, omega}


@pytest.mark.parametrize("c", [1, -1, 5, -5, 7, 11])
def test_slopes_are_blind_to_the_offset(c):
    assert nf.two_step_slopes(3, c) == nf.two_step_slopes(3, 1)


def test_mirror_map_has_extra_cycles_with_the_same_slopes():
    assert nf.cycles(3, 1) == [(1, 2)]
    mirror = nf.cycles(3, -1)
    assert [cycle[0] for cycle in mirror] == [1, 5, 17]
    assert mirror[1] == (5, 7, 10)


def test_only_a_equal_three_puts_the_top_slope_between_two_and_three():
    tops = {a: max(nf.two_step_slopes(a, 1)) for a in (3, 5, 7, 9, 11)}
    assert all(top == Fr(a, 2) ** 2 for a, top in tops.items())
    assert [a for a, top in tops.items() if 2 <= top <= 3] == [3]


def test_no_collatz_exponent_is_nine_fourths():
    values = nf.collatz_exponents()
    assert len(values) == 5
    assert min(abs(v - 9 / 4) for v in values.values()) > 0.3
    assert values["log2(9/4), bits gained by two odd shortcut steps"] == pytest.approx(
        2 * (values["log2(3), bits per tripling"] - 1))


# ---- D. look-elsewhere ----

def test_three_smooth():
    assert [n for n in range(1, 30) if nf.is_3_smooth(n)] == [1, 2, 3, 4, 6, 8, 9, 12, 16, 18, 24, 27]
    assert not nf.is_3_smooth(0)


def test_exponent_of_terminates_on_zero_and_rejects_bad_bases():
    assert nf.exponent_of(0, 3) is None
    assert nf.exponent_of(8, 1) is None
    assert nf.exponent_of(1, 2) == 0
    assert nf.exponent_of(81, 3) == 4
    assert nf.exponent_of(12, 2) is None


def test_shortcut_slopes_need_a_halving_for_every_tripling():
    assert nf.is_shortcut_slope(Fr(9, 4))
    assert nf.is_shortcut_slope(Fr(3, 2))
    assert nf.is_shortcut_slope(Fr(1, 4))
    assert not nf.is_shortcut_slope(3)
    assert not nf.is_shortcut_slope(Fr(9, 2))
    assert not nf.is_shortcut_slope(Fr(5, 4))
    assert not nf.is_shortcut_slope(0)


def test_every_two_step_slope_is_a_shortcut_slope():
    assert all(nf.is_shortcut_slope(s) for s in nf.two_step_slopes())


def test_simple_rationals_with_denominator_at_most_four():
    everything, smooth, slopes = nf.look_elsewhere(4)
    assert everything == [Fr(2), Fr(9, 4), Fr(7, 3), Fr(5, 2), Fr(8, 3), Fr(11, 4), Fr(3)]
    assert smooth == [Fr(2), Fr(9, 4), Fr(8, 3), Fr(3)]
    assert slopes == [Fr(9, 4)]


def test_look_elsewhere_counts():
    assert [(len(a), len(s), len(p)) for a, s, p in map(nf.look_elsewhere, (6, 8, 16, 32))] == [
        (13, 4, 1), (23, 4, 1), (81, 4, 1), (325, 6, 2)]
    assert nf.look_elsewhere(32)[2] == [Fr(9, 4), Fr(81, 32)]


def test_look_elsewhere_terminates_on_an_interval_containing_zero():
    everything, _, slopes = nf.look_elsewhere(4, lo=0, hi=3)
    assert Fr(0) in everything
    assert Fr(0) not in slopes and Fr(1, 2) in slopes


def test_simple_rationals_takes_exact_endpoints():
    assert Fr(3, 10) in nf.simple_rationals(Fr(1, 10), Fr(3, 10), 10)


# ---- reports ----

def test_reports_run_and_state_the_headline_numbers(capsys):
    assert nf.main(["nine_fourths.py", "all"]) == 0
    out = capsys.readouterr().out
    assert "ratio                 = 9/4" in out
    assert "r=3: 9/4 n + 5/4" in out
    assert "3-smooth:       ['2', '9/4', '8/3', '3']" in out


def test_unknown_report_is_an_error(capsys):
    assert nf.main(["nine_fourths.py", "bogus"]) == 2
    assert "usage" in capsys.readouterr().err
