//! # collatz-rs
//!
//! Collatz dropping-time primitives for the Emanon game engine.
//!
//! Every file written inside an Emanon universe is stamped with a [`Genus`] —
//! the Collatz signature of its content hash.  The merge driver compares genera
//! to decide how timelines resolve.  This crate provides the core maths.
//!
//! ## Theoretical background
//!
//! Based on Paper 1: *"The Collatz Conjecture, Pythagorean Triples, and the
//! Riemann Hypothesis"* (Darcy Thomas, 2026).
//!
//! Key definitions (Paper 1 terminology):
//! - **Dropping Time** (`k`): the minimum number of Collatz steps to reach a
//!   value strictly less than `n`.  Equivalent to `stopping_time(n)` in the
//!   Python reference (`collatz/core.py`).
//! - **Dropping Set** (`Set_k`): the set of all integers n > 1 with the same
//!   dropping time `k`.  E.g. `Set_1` = all even numbers ≥ 2.
//! - **Dropping Orbit**: the sequence `[n, f(n), …, last_value_≥_n]`.
//!   Excludes the first value that is strictly less than `n`.
//! - **Orbital Oddity** (`s`): count of odd integers in the dropping orbit.
//!   By Conjecture 1, all members of the same `Set_k` share the same `s`.
//! - **Dropping Index** (`i`): 0-based position of `n` among all integers in
//!   `Set_k`, ordered by magnitude.
//!
//! ## Complexity note
//!
//! [`dropping_index`] and [`dropping_genus`] are **O(n × orbit_cost)** —
//! they enumerate every integer from 2 to `n`.  They are suitable for small
//! `n` (≤ ~10^7) but infeasible for large inputs such as 10^20.  For large
//! `n`, call [`dropping_time`] and [`orbital_oddity`] directly.

use num_bigint::BigUint;
use num_traits::{One, Zero};

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/// Collatz genus: the `(set_k, oddity_s, index_i)` triple that characterises
/// how an integer behaves under dropping-time dynamics.
///
/// Stamped into every file written inside an Emanon universe.  The merge
/// driver uses `set_k` and `oddity_s` to classify writes; `index_i` gives a
/// total ordering within the same set.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Genus {
    /// Dropping set: equals `dropping_time(n)` — the number of Collatz steps
    /// until the first value strictly less than `n`.
    pub set_k: u64,

    /// Orbital oddity: count of odd integers in the dropping orbit of `n`.
    /// By Conjecture 1 (Paper 1), this is constant across all of `Set_k`.
    pub oddity_s: u64,

    /// Dropping index: 0-based rank of `n` within `Set_k` (ascending order).
    ///
    /// **Warning**: computed by enumeration — O(n).  Use only for small `n`
    /// (≤ ~10^7).  For large `n`, obtain `set_k` and `oddity_s` directly.
    pub index_i: u64,
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// Single step of the Collatz function:
/// `f(n) = n / 2` if `n` is even, `3n + 1` if `n` is odd.
fn collatz_step(n: &BigUint) -> BigUint {
    if n.bit(0) {
        // odd: 3n + 1
        BigUint::from(3u32) * n + BigUint::one()
    } else {
        // even: n >> 1
        n >> 1
    }
}

/// Collect the dropping orbit of `n`:
/// `[n, f(n), f²(n), …, last_value ≥ n]`.
///
/// Stops before including the first value < n.
///
/// # Panics
/// Panics if `n ≤ 1`.
fn dropping_orbit_vec(n: &BigUint) -> Vec<BigUint> {
    assert!(
        n > &BigUint::one(),
        "dropping orbit is undefined for n ≤ 1"
    );
    let mut orbit = vec![n.clone()];
    let mut current = collatz_step(n);
    while current >= *n {
        let next = collatz_step(&current);
        orbit.push(current);
        current = next;
    }
    orbit
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/// Number of Collatz steps from `n` to the first value strictly less than `n`.
///
/// Equivalent to `stopping_time(n)` in `collatz.core` (Python reference).
///
/// Uses [`num_bigint::BigUint`] for arbitrary-precision arithmetic so it
/// handles inputs such as 10^20 without overflow.
///
/// # Examples
///
/// ```
/// use collatz_rs::dropping_time;
/// use num_bigint::BigUint;
///
/// assert_eq!(dropping_time(&BigUint::from(5u64)), 3);  // 5 → 16 → 8 → 4
/// assert_eq!(dropping_time(&BigUint::from(13u64)), 3); // 13 → 40 → 20 → 10
/// ```
///
/// # Panics
/// Panics if `n ≤ 1`.
pub fn dropping_time(n: &BigUint) -> u64 {
    assert!(n > &BigUint::one(), "n must be > 1");
    let mut current = collatz_step(n);
    let mut steps: u64 = 1;
    while current >= *n {
        current = collatz_step(&current);
        steps += 1;
    }
    steps
}

/// Count of odd integers in the dropping orbit of `n`.
///
/// By Conjecture 1 (Paper 1), every member of the same Dropping Set_k has
/// the same orbital oddity.  This makes `oddity_s` a structural invariant.
///
/// # Examples
///
/// ```
/// use collatz_rs::orbital_oddity;
/// use num_bigint::BigUint;
///
/// // orbit [5, 16, 8]; odd: {5} → 1
/// assert_eq!(orbital_oddity(&BigUint::from(5u64)), 1);
/// // orbit [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10]; odd: {7,11,17,13} → 4
/// assert_eq!(orbital_oddity(&BigUint::from(7u64)), 4);
/// ```
///
/// # Panics
/// Panics if `n ≤ 1`.
pub fn orbital_oddity(n: &BigUint) -> u64 {
    dropping_orbit_vec(n)
        .iter()
        .filter(|x| x.bit(0))
        .count() as u64
}

/// 0-based rank of `n` within `Set_k`, ordered by magnitude.
///
/// Counts how many integers in `[2, n)` have `dropping_time == dropping_time(n)`.
///
/// **Complexity**: O(n × average_orbit_length).  Suitable for `n ≤ ~10^7`;
/// impractical for larger inputs.
///
/// # Panics
/// Panics if `n ≤ 1`.
pub fn dropping_index(n: &BigUint) -> u64 {
    assert!(n > &BigUint::one(), "n must be > 1");
    let target_k = dropping_time(n);
    let two = BigUint::from(2u32);
    let mut idx: u64 = 0;
    let mut m = two;
    while m < *n {
        if dropping_time(&m) == target_k {
            idx += 1;
        }
        m += BigUint::one();
    }
    idx
}

/// Collatz genus of `n`: the `(set_k, oddity_s, index_i)` triple.
///
/// Uniquely characterises `n`'s dropping-time dynamics.  Stamped into every
/// file write in an Emanon universe; compared by the Collatz merge driver.
///
/// # Examples
///
/// ```
/// use collatz_rs::{dropping_genus, Genus};
/// use num_bigint::BigUint;
///
/// assert_eq!(
///     dropping_genus(&BigUint::from(5u64)),
///     Genus { set_k: 3, oddity_s: 1, index_i: 0 }
/// );
/// assert_eq!(
///     dropping_genus(&BigUint::from(13u64)),
///     Genus { set_k: 3, oddity_s: 1, index_i: 2 }
/// );
/// ```
///
/// **Warning**: `index_i` is O(n) — see [`dropping_index`].
///
/// # Panics
/// Panics if `n ≤ 1`.
pub fn dropping_genus(n: &BigUint) -> Genus {
    Genus {
        set_k: dropping_time(n),
        oddity_s: orbital_oddity(n),
        index_i: dropping_index(n),
    }
}

/// Single step of the Syracuse (odd-only) map.
///
/// ```text
/// S(n) = (3n + 1) / 2^v₂(3n + 1)
/// ```
///
/// Advances directly from one odd number to the next in the Collatz orbit,
/// skipping all intermediate even values.
///
/// Equivalent to `syracuse_step(n)` in `collatz.core` (Python reference).
///
/// # Examples
///
/// ```
/// use collatz_rs::syracuse_step;
/// use num_bigint::BigUint;
///
/// assert_eq!(syracuse_step(&BigUint::from(3u64)), BigUint::from(5u64));  // 3→10→5
/// assert_eq!(syracuse_step(&BigUint::from(5u64)), BigUint::from(1u64));  // 5→16→…→1
/// assert_eq!(syracuse_step(&BigUint::from(7u64)), BigUint::from(11u64)); // 7→22→11
/// ```
///
/// # Panics
/// Panics if `n` is even.
pub fn syracuse_step(n: &BigUint) -> BigUint {
    assert!(n.bit(0), "syracuse_step requires an odd input");
    let val = BigUint::from(3u32) * n + BigUint::one();
    // val is always even when n is odd; trailing_zeros() is safe to unwrap
    let trailing = val
        .trailing_zeros()
        .expect("3n+1 is always positive and even for odd n");
    val >> trailing
}

/// Bit destruction rate for orbital oddity `s`.
///
/// ```text
/// β(s) = 1 − frac(s · log₂ 3)
/// ```
///
/// Measures how quickly the bit-length of the iterates shrinks per Collatz
/// step on average.  Always lies in `(0, 1]`.
///
/// Reference: Paper 1, §4 "Bit Destruction and the Riemann Connection".
///
/// # Examples
///
/// ```
/// use collatz_rs::beta;
///
/// // s = 0: no odd steps, no bit destruction
/// assert!((beta(0) - 1.0).abs() < 1e-10);
/// // s = 1: β ≈ 0.4150375
/// assert!(beta(1) > 0.0 && beta(1) < 1.0);
/// ```
pub fn beta(s: u64) -> f64 {
    let log2_3: f64 = (3f64).log2(); // ≈ 1.5849625007211563
    let product = s as f64 * log2_3;
    1.0 - product.fract()
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn n(v: u64) -> BigUint {
        BigUint::from(v)
    }

    // -----------------------------------------------------------------------
    // dropping_time — exact match against Python reference
    // -----------------------------------------------------------------------

    #[test]
    fn dropping_time_n2() {
        assert_eq!(dropping_time(&n(2)), 1); // 2→1
    }

    #[test]
    fn dropping_time_n3() {
        assert_eq!(dropping_time(&n(3)), 6); // 3→10→5→16→8→4→2
    }

    #[test]
    fn dropping_time_n5() {
        assert_eq!(dropping_time(&n(5)), 3); // 5→16→8→4
    }

    #[test]
    fn dropping_time_n7() {
        assert_eq!(dropping_time(&n(7)), 11); // 7→22→11→…→5
    }

    #[test]
    fn dropping_time_n13() {
        assert_eq!(dropping_time(&n(13)), 3); // 13→40→20→10
    }

    #[test]
    fn dropping_time_n27() {
        // 27 has a famously long Collatz orbit; dropping time = 96.
        assert_eq!(dropping_time(&n(27)), 96);
    }

    #[test]
    fn dropping_time_n41() {
        assert_eq!(dropping_time(&n(41)), 3);
    }

    #[test]
    fn dropping_time_n53() {
        assert_eq!(dropping_time(&n(53)), 3);
    }

    #[test]
    fn dropping_time_n137() {
        assert_eq!(dropping_time(&n(137)), 3);
    }

    #[test]
    fn dropping_time_n1234567() {
        // 1234567 ∈ Set_11
        assert_eq!(dropping_time(&n(1_234_567)), 11);
    }

    #[test]
    fn dropping_time_10_pow_20() {
        // 10^20 is even → one step reaches 5×10^19 < 10^20
        let big: BigUint = "100000000000000000000".parse().unwrap();
        assert_eq!(dropping_time(&big), 1);
    }

    #[test]
    #[should_panic(expected = "n must be > 1")]
    fn dropping_time_n1_panics() {
        dropping_time(&n(1));
    }

    // -----------------------------------------------------------------------
    // orbital_oddity — exact match against Python reference
    // -----------------------------------------------------------------------

    #[test]
    fn orbital_oddity_n2() {
        // orbit = [2]; 2 is even → 0
        assert_eq!(orbital_oddity(&n(2)), 0);
    }

    #[test]
    fn orbital_oddity_n3() {
        // orbit = [3,10,5,16,8,4]; odd: {3,5} → 2
        assert_eq!(orbital_oddity(&n(3)), 2);
    }

    #[test]
    fn orbital_oddity_n5() {
        // orbit = [5,16,8]; odd: {5} → 1
        assert_eq!(orbital_oddity(&n(5)), 1);
    }

    #[test]
    fn orbital_oddity_n7() {
        // orbit = [7,22,11,34,17,52,26,13,40,20,10]; odd: {7,11,17,13} → 4
        assert_eq!(orbital_oddity(&n(7)), 4);
    }

    #[test]
    fn orbital_oddity_n13() {
        // orbit = [13,40,20]; odd: {13} → 1
        assert_eq!(orbital_oddity(&n(13)), 1);
    }

    #[test]
    fn orbital_oddity_n27() {
        assert_eq!(orbital_oddity(&n(27)), 37);
    }

    #[test]
    fn orbital_oddity_n41() {
        assert_eq!(orbital_oddity(&n(41)), 1);
    }

    #[test]
    fn orbital_oddity_n53() {
        assert_eq!(orbital_oddity(&n(53)), 1);
    }

    #[test]
    fn orbital_oddity_n137() {
        assert_eq!(orbital_oddity(&n(137)), 1);
    }

    #[test]
    fn orbital_oddity_10_pow_20() {
        // 10^20 is even; orbit = [10^20]; 0 odd elements
        let big: BigUint = "100000000000000000000".parse().unwrap();
        assert_eq!(orbital_oddity(&big), 0);
    }

    // -----------------------------------------------------------------------
    // dropping_genus (small n) — exact match against Python reference
    // -----------------------------------------------------------------------

    #[test]
    fn dropping_genus_n5() {
        assert_eq!(
            dropping_genus(&n(5)),
            Genus { set_k: 3, oddity_s: 1, index_i: 0 }
        );
    }

    #[test]
    fn dropping_genus_n7() {
        assert_eq!(
            dropping_genus(&n(7)),
            Genus { set_k: 11, oddity_s: 4, index_i: 0 }
        );
    }

    #[test]
    fn dropping_genus_n9() {
        assert_eq!(
            dropping_genus(&n(9)),
            Genus { set_k: 3, oddity_s: 1, index_i: 1 }
        );
    }

    #[test]
    fn dropping_genus_n13() {
        assert_eq!(
            dropping_genus(&n(13)),
            Genus { set_k: 3, oddity_s: 1, index_i: 2 }
        );
    }

    #[test]
    fn dropping_genus_n27() {
        assert_eq!(
            dropping_genus(&n(27)),
            Genus { set_k: 96, oddity_s: 37, index_i: 0 }
        );
    }

    #[test]
    fn dropping_genus_n41() {
        assert_eq!(
            dropping_genus(&n(41)),
            Genus { set_k: 3, oddity_s: 1, index_i: 9 }
        );
    }

    #[test]
    fn dropping_genus_n53() {
        assert_eq!(
            dropping_genus(&n(53)),
            Genus { set_k: 3, oddity_s: 1, index_i: 12 }
        );
    }

    #[test]
    fn dropping_genus_n137() {
        assert_eq!(
            dropping_genus(&n(137)),
            Genus { set_k: 3, oddity_s: 1, index_i: 33 }
        );
    }

    /// Exact genus match for n = 1 234 567 (Python verified: index = 28 935).
    /// This test is slow (~1-2 s) because dropping_index is O(n).
    #[test]
    fn dropping_genus_n1234567() {
        let bn = n(1_234_567);
        // Verify set_k and oddity_s immediately (cheap)
        assert_eq!(dropping_time(&bn), 11);
        assert_eq!(orbital_oddity(&bn), 4);
        // Full genus including index (expensive but verifiable by CI)
        assert_eq!(
            dropping_genus(&bn),
            Genus { set_k: 11, oddity_s: 4, index_i: 28_935 }
        );
    }

    // -----------------------------------------------------------------------
    // Invariants
    // -----------------------------------------------------------------------

    #[test]
    fn set_k_matches_dropping_time() {
        for v in [5u64, 7, 13, 27, 41, 53, 137] {
            let bn = n(v);
            let g_set_k = dropping_genus(&bn).set_k;
            assert_eq!(
                g_set_k,
                dropping_time(&bn),
                "set_k ≠ dropping_time for n={v}"
            );
        }
    }

    #[test]
    fn oddity_matches_orbital_oddity() {
        for v in [5u64, 7, 13, 27, 41, 53, 137] {
            let bn = n(v);
            let g_s = dropping_genus(&bn).oddity_s;
            assert_eq!(
                g_s,
                orbital_oddity(&bn),
                "oddity_s ≠ orbital_oddity for n={v}"
            );
        }
    }

    /// Verify the arithmetic progression of Set_3:
    /// Set_3 = {n : n ≡ 1 (mod 4), n ≥ 5} = {5, 9, 13, 17, 21, 25, …}
    /// Index = (n − 5) / 4.
    #[test]
    fn set3_arithmetic_progression() {
        let cases: &[(u64, u64)] = &[
            (5, 0),
            (9, 1),
            (13, 2),
            (17, 3),
            (21, 4),
            (41, 9),
            (53, 12),
            (137, 33),
        ];
        for &(v, expected_idx) in cases {
            let bn = n(v);
            let g = dropping_genus(&bn);
            assert_eq!(g.set_k, 3, "n={v} set_k");
            assert_eq!(g.oddity_s, 1, "n={v} oddity_s");
            assert_eq!(g.index_i, expected_idx, "n={v} index_i");
        }
    }

    // -----------------------------------------------------------------------
    // syracuse_step
    // -----------------------------------------------------------------------

    #[test]
    fn syracuse_step_n3() {
        // 3 → 10 → 5 (next odd)
        assert_eq!(syracuse_step(&n(3)), n(5));
    }

    #[test]
    fn syracuse_step_n5() {
        // 5 → 16 → 8 → 4 → 2 → 1 (next odd = 1)
        assert_eq!(syracuse_step(&n(5)), n(1));
    }

    #[test]
    fn syracuse_step_n7() {
        // 7 → 22 → 11
        assert_eq!(syracuse_step(&n(7)), n(11));
    }

    #[test]
    fn syracuse_step_n11() {
        assert_eq!(syracuse_step(&n(11)), n(17));
    }

    #[test]
    fn syracuse_step_n13() {
        assert_eq!(syracuse_step(&n(13)), n(5));
    }

    #[test]
    fn syracuse_step_n15() {
        assert_eq!(syracuse_step(&n(15)), n(23));
    }

    #[test]
    #[should_panic(expected = "syracuse_step requires an odd input")]
    fn syracuse_step_even_panics() {
        syracuse_step(&n(4));
    }

    // -----------------------------------------------------------------------
    // beta
    // -----------------------------------------------------------------------

    #[test]
    fn beta_s0() {
        // frac(0) = 0 → β = 1.0
        assert!((beta(0) - 1.0).abs() < 1e-12);
    }

    #[test]
    fn beta_s1() {
        let expected = 1.0 - (3f64.log2()).fract();
        assert!((beta(1) - expected).abs() < 1e-12);
    }

    #[test]
    fn beta_s2() {
        let expected = 1.0 - (2.0 * 3f64.log2()).fract();
        assert!((beta(2) - expected).abs() < 1e-12);
    }

    #[test]
    fn beta_always_in_unit_interval() {
        for s in 0u64..=200 {
            let b = beta(s);
            assert!(b > 0.0, "beta({s}) must be positive");
            assert!(b <= 1.0, "beta({s}) must be ≤ 1.0");
        }
    }
}
