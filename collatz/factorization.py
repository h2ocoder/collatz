"""Prime factorization analysis & class characters (NEW research direction).

Investigates whether the Collatz classification of composite numbers
relates to the classifications of their prime factors.

Key question: given n = p₁^a₁ × p₂^a₂ × ..., do the Collatz
classifications of the primes combine in predictable ways?
"""

from collections import Counter

import pandas as pd

from .core import stopping_time, stopping_destination
from .dropping import dropping_set, dropping_modulus, dropping_genus, orbital_oddity
from .stopping import stopping_class, stopping_signature


def prime_factorization(n):
    """Prime factorization of n.

    Returns a dict {prime: exponent}.
    Example: prime_factorization(12) = {2: 2, 3: 1}
    Example: prime_factorization(7) = {7: 1}
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    factors = Counter()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] += 1
            n //= d
        d += 1
    if n > 1:
        factors[n] += 1
    return dict(factors)


def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def prime_class_character(n):
    """Map each prime factor of n to its Collatz classification.

    Returns a dict mapping each prime factor to a dict of its properties:
    {prime: {'dropping_set': k, 'dropping_modulus': m, 'orbital_oddity': oo,
             'stopping_time': st, 'stopping_destination': sd}}

    Example: prime_class_character(15) = {
        3: {'dropping_set': 6, ...},
        5: {'dropping_set': 3, ...}
    }
    """
    factors = prime_factorization(n)
    result = {}
    for p in factors:
        result[p] = {
            "dropping_set": dropping_set(p),
            "dropping_modulus": dropping_modulus(p),
            "orbital_oddity": orbital_oddity(p),
            "stopping_time": stopping_time(p),
            "stopping_destination": stopping_destination(p),
        }
    return result


def class_character_signature(n):
    """Hashable representation of the combined factor classifications.

    Returns a tuple of ((prime, exponent, dropping_set, stopping_time), ...)
    sorted by prime, providing a compact signature for comparison.
    """
    factors = prime_factorization(n)
    sig = []
    for p in sorted(factors):
        sig.append((
            p,
            factors[p],
            dropping_set(p),
            stopping_time(p),
        ))
    return tuple(sig)


def compare_composite_vs_factors(n):
    """Compare n's Collatz classification to its factors' classifications.

    Returns a dict with:
    - 'n': the number
    - 'factorization': {prime: exp}
    - 'composite_class': n's own classification
    - 'factor_classes': each factor's classification
    - 'same_class_as_any_factor': bool
    """
    factors = prime_factorization(n)
    n_ds = dropping_set(n)
    n_st = stopping_time(n)
    n_sd = stopping_destination(n)

    factor_classes = {}
    same_class = False
    for p in factors:
        p_ds = dropping_set(p)
        factor_classes[p] = {
            "exponent": factors[p],
            "dropping_set": p_ds,
            "stopping_time": stopping_time(p),
            "stopping_destination": stopping_destination(p),
        }
        if p_ds == n_ds:
            same_class = True

    return {
        "n": n,
        "factorization": factors,
        "composite_class": {
            "dropping_set": n_ds,
            "stopping_time": n_st,
            "stopping_destination": n_sd,
        },
        "factor_classes": factor_classes,
        "same_class_as_any_factor": same_class,
    }


def factor_classification_table(limit):
    """Build a DataFrame with n, its factorization, and each factor's class.

    Columns: n, is_prime, num_factors, factorization_str,
             dropping_set, stopping_time, stopping_destination,
             max_factor_dropping_set, min_factor_dropping_set

    Operates on n in [2, limit).
    """
    rows = []
    for n in range(2, limit):
        factors = prime_factorization(n)
        factor_sets = [dropping_set(p) for p in factors]
        rows.append({
            "n": n,
            "is_prime": is_prime(n),
            "num_distinct_factors": len(factors),
            "factorization": factors,
            "dropping_set": dropping_set(n),
            "stopping_time": stopping_time(n),
            "stopping_destination": stopping_destination(n),
            "max_factor_dropping_set": max(factor_sets),
            "min_factor_dropping_set": min(factor_sets),
        })
    return pd.DataFrame(rows)


def shared_class_primes(class_k, limit=10000):
    """Which primes share a given dropping set / stopping class?

    Returns a list of primes p < limit where dropping_set(p) == class_k.
    """
    return [p for p in range(2, limit) if is_prime(p) and dropping_set(p) == class_k]


def class_distribution_by_prime(p, limit=10000):
    """How do multiples of prime p distribute across dropping sets?

    Returns a Counter mapping dropping_set → count for multiples of p in [2*p, limit).
    """
    dist = Counter()
    for n in range(2 * p, limit, p):
        dist[dropping_set(n)] += 1
    return dict(sorted(dist.items()))
