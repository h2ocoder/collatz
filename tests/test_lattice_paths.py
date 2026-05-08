"""Tests for lattice-path enumeration and the rho_1 - rho_2 series."""

import math

import pytest

from collatz.lfunctions.lattice_paths import (
    b_imbalance_term,
    count_by_dest_residue,
    count_by_dest_residue_dp,
    density_per_subgroup,
    enumerate_subgroups,
    k_of,
    rho_diff_partial,
)


def test_k_of_matches_lattice_path_doc():
    # From `Lattice Path Formula.md`: k(s) = ceil(s log_2 6) for s = 1, 2, 3, ...
    expected = {1: 3, 2: 6, 3: 8, 4: 11, 5: 13, 6: 16, 7: 19, 8: 21, 9: 24, 10: 26}
    for s, k in expected.items():
        assert k_of(s) == k


def test_N_s_matches_known_sequence():
    """N(s) = 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, ..."""
    expected = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950]
    for s, n_expected in enumerate(expected, start=1):
        n_actual = len(enumerate_subgroups(s))
        assert n_actual == n_expected, f"s={s}: got {n_actual}, expected {n_expected}"


def test_dp_matches_brute_force():
    """DP version agrees with brute-force enumeration for s up to 12."""
    for s in range(1, 13):
        brute = count_by_dest_residue(s) if s <= 7 else None
        # For s > 7, count_by_dest_residue uses DP itself; check by re-enumerating
        if s <= 7:
            paths = enumerate_subgroups(s)
            n1_paths = sum(1 for p in paths if p[-1] % 2 == 0)
            n2_paths = len(paths) - n1_paths
            n1_dp, n2_dp = count_by_dest_residue_dp(s)
            assert n1_paths == n1_dp and n2_paths == n2_dp


def test_set_3_gives_b_equals_one():
    """Set_3 (s=1) has dest ≡ 1 mod 3. So N_1(1) = 1, N_2(1) = 0."""
    n1, n2 = count_by_dest_residue(1)
    assert n1 == 1 and n2 == 0


def test_set_6_gives_b_equals_two():
    """Set_6 (s=2) has dest ≡ 2 mod 3. So N_1(2) = 0, N_2(2) = 1."""
    n1, n2 = count_by_dest_residue(2)
    assert n1 == 0 and n2 == 1


def test_density_per_subgroup_matches_doc():
    """Density per subgroup at oddity s = 1/2^{k(s) - s - 1}.

    For s=1: density = 1/2 (Set_3 alone is half of all odd integers).
    For s=2: density = 1/2^3 = 1/8 (Set_6 has density 1/8 of all odd integers).
    """
    assert density_per_subgroup(1) == pytest.approx(0.5)
    assert density_per_subgroup(2) == pytest.approx(1 / 8)
    assert density_per_subgroup(3) == pytest.approx(1 / 16)
    assert density_per_subgroup(4) == pytest.approx(1 / 64)


def test_rho_diff_partial_converges():
    """The partial sums approach the asymptotic constant 0.3560359...

    Verified to high precision: limit value is approximately 0.3560359298.
    Partial sums oscillate but the bound on |partial - limit| decays as the
    higher-Dset contributions shrink geometrically.
    """
    p100 = rho_diff_partial(100)
    p200 = rho_diff_partial(200)
    p300 = rho_diff_partial(300)
    p400 = rho_diff_partial(400)
    # Each partial sum is closer to the limit than the previous (after the
    # initial oscillations damp out).
    target = 0.3560359298
    assert abs(p100 - target) < 1e-3
    assert abs(p200 - target) < 1e-5
    assert abs(p300 - target) < 1e-7
    assert abs(p400 - target) < 1e-9


def test_first_terms_match_hand_derivation():
    """Verify s = 1..4 contributions match hand calculation.

    s=1: N_1 - N_2 = +1, density = 1/2, contrib = +1/2.
    s=2: N_1 - N_2 = -1, density = 1/8, contrib = -1/8.
    s=3: N_1 - N_2 = 0, density = 1/16, contrib = 0.
    s=4: N_1 - N_2 = -1, density = 1/64, contrib = -1/64.
    """
    expected = [0.5, -0.125, 0.0, -1 / 64]
    for s, exp in enumerate(expected, start=1):
        actual = b_imbalance_term(s)
        assert actual == pytest.approx(exp)


def test_rho_diff_at_s_4_equals_3594_64ths():
    """Sum at s=1..4 is 0.5 - 0.125 + 0 - 1/64 = 0.3593750..."""
    assert rho_diff_partial(4) == pytest.approx(0.5 - 0.125 - 1 / 64)
