# tests/test_constellations.py
"""Tests for collatz.constellations — prime constellation dropping signatures."""

import numpy as np
import pytest

from collatz.constellations import prime_pairs


def _brute_pairs(n_max, gap):
    from collatz.residues import prime_sieve
    primes = set(prime_sieve(n_max + gap).tolist())
    return [p for p in sorted(primes) if p <= n_max and (p + gap) in primes]


def test_prime_pairs_twins_small():
    """Twins (g=2) up to 30: (3,5),(5,7),(11,13),(17,19),(29,31)."""
    ps = prime_pairs(30, 2)
    assert list(ps) == [3, 5, 11, 17, 29]


def test_prime_pairs_cousins_small():
    """Cousins (g=4) up to 20: (3,7),(7,11),(13,17),(19,23) — p<=n_max, p+g prime."""
    ps = prime_pairs(20, 4)
    assert list(ps) == [3, 7, 13, 19]


def test_prime_pairs_sexy_small():
    """Sexy (g=6) up to 20: (5,11),(7,13),(11,17),(13,19),(17,23)."""
    ps = prime_pairs(20, 6)
    assert list(ps) == [5, 7, 11, 13, 17]


def test_prime_pairs_matches_brute_force():
    """Agree with a set-membership brute force up to 10**4 for all three gaps."""
    for gap in (2, 4, 6):
        assert list(prime_pairs(10_000, gap)) == _brute_pairs(10_000, gap)


def test_prime_pairs_returns_int_array():
    ps = prime_pairs(30, 2)
    assert isinstance(ps, np.ndarray)
    assert ps.dtype.kind == "i"


def test_prime_pairs_rejects_bad_gap():
    """gap=0, gap=1, and gap=-2 must all raise ValueError."""
    for bad_gap in (0, 1, -2):
        with pytest.raises(ValueError):
            prime_pairs(30, bad_gap)


from collatz.constellations import pair_signature, joint_signature_counts
from collatz.dropping import dropping_set


def test_pair_signature_twin_3_5():
    """(3,5): dropping_set(3)=6, dropping_set(5)=3 -> capped unchanged."""
    assert pair_signature(3, 2) == (dropping_set(3), dropping_set(5))


def test_pair_signature_caps_large_k():
    """A k above the cap folds to K_CAP; small k passes through."""
    from collatz.constellations import K_CAP
    kp, kq = pair_signature(3, 2, k_cap=2)
    assert kp == 2 and kq == 2  # both real k>2, capped to 2


def test_joint_counts_total_equals_pair_count():
    """Sum of the joint histogram equals the number of pairs."""
    from collatz.constellations import prime_pairs
    pairs = prime_pairs(10_000, 2)
    counts = joint_signature_counts(pairs, 2)
    assert sum(counts.values()) == len(pairs)


def test_joint_counts_twin_fast_slow_forced():
    """Every twin pair has exactly one member in dropping set 3 (the 1-mod-4 one)."""
    from collatz.constellations import prime_pairs
    pairs = prime_pairs(100_000, 2)
    counts = joint_signature_counts(pairs, 2)
    # In every (kp, kq) key, exactly one coordinate is 3.
    for (kp, kq), c in counts.items():
        assert (kp == 3) ^ (kq == 3), f"twin signature {(kp, kq)} not fast/slow"


from collatz.constellations import coupling_null_counts


def test_null_keys_are_signature_pairs():
    """Null histogram keys are (int, int) dropping-set signatures."""
    null = coupling_null_counts(10_000, 2, stride=1)
    assert null
    for key in null:
        assert isinstance(key, tuple) and len(key) == 2


def test_null_is_deterministic():
    """Same arguments -> identical histogram (no RNG)."""
    a = coupling_null_counts(50_000, 2, stride=5)
    b = coupling_null_counts(50_000, 2, stride=5)
    assert a == b


def test_null_fast_slow_forced_for_twins():
    """The g=2 integer null also forces exactly one dropping-set-3 coordinate."""
    null = coupling_null_counts(20_000, 2, stride=1)
    for (kp, kq) in null:
        assert (kp == 3) ^ (kq == 3)


def test_null_stride_subsamples():
    """A larger stride yields no more sampled integers than a smaller one."""
    fine = sum(coupling_null_counts(50_000, 2, stride=1).values())
    coarse = sum(coupling_null_counts(50_000, 2, stride=10).values())
    assert coarse <= fine
    assert coarse > 0


from collatz.constellations import forced_coupling_table


def test_coupling_table_twin_one_of_each_mod4():
    """g=2: in every odd residue row, exactly one member is 1 mod 4 (fast)."""
    rows = forced_coupling_table(2, 8)
    for a, b, fast_a, fast_b in rows:
        assert fast_a == (a % 4 == 1)
        assert fast_b == (b % 4 == 1)
        assert fast_a ^ fast_b  # exactly one fast member


def test_coupling_table_cousin_same_mod4():
    """g=4: both members share their mod-4 class (both fast or both slow)."""
    rows = forced_coupling_table(4, 8)
    for a, b, fast_a, fast_b in rows:
        assert fast_a == fast_b


def test_coupling_table_covers_odd_residues():
    """Rows are exactly the odd residues mod the modulus."""
    rows = forced_coupling_table(2, 8)
    assert [r[0] for r in rows] == [1, 3, 5, 7]
