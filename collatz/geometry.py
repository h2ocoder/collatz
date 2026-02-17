"""Pythagorean triples, circles, complex plane mappings (Papers 1 & 2).

Paper 1: Orbital Triple Mapping, Collatz Circle Proportionality, complex multiplier z₀
Paper 2: Stopping circles, golden ratio connections
Paper 3: Proportional Power Ratio P(x) base b
"""

import math
from fractions import Fraction

from .core import stopping_destination


def orbital_triple(n):
    """Map integer n to a Pythagorean triple via Orbital Triple Mapping.

    For odd n, let d = dropping destination. Then:
        a = n² - d²
        b = 2dn
        c = n² + d²

    These satisfy a² + b² = c² (Pythagorean triple).
    The Collatz-Pythagorean Convergence: b + c = (n + d)².

    For even n, the triple is computed but forms a degenerate triangle.

    Returns (a, b, c).
    Example: orbital_triple(3) = (5, 12, 13)
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    d = stopping_destination(n)
    a = n * n - d * d
    b = 2 * d * n
    c = n * n + d * d
    return (a, b, c)


def incircle_params(n):
    """Incircle parameters for the triangle from orbital_triple(n).

    For a right triangle with legs a (horizontal) and b (vertical):
    - Incircle radius r = (a + b - c) / 2
    - Incircle center at (r, r)

    Returns (radius, (center_x, center_y)).
    """
    a, b, c = orbital_triple(n)
    r = Fraction(a + b - c, 2)
    return (r, (r, r))


def circumcircle_params(n):
    """Circumcircle parameters for the triangle from orbital_triple(n).

    For a right triangle with legs a (horizontal) and b (vertical):
    - Circumcircle radius R = c / 2
    - Center at midpoint of hypotenuse = (a/2, b/2)

    Returns (radius, (center_x, center_y)).
    """
    a, b, c = orbital_triple(n)
    R = Fraction(c, 2)
    center = (Fraction(a, 2), Fraction(b, 2))
    return (R, center)


def stopping_circle(n):
    """Circle equation parameters derived from the stopping point of n.

    Returns a dict with incircle and circumcircle parameters:
    {
        'triple': (a, b, c),
        'incircle_radius': r,
        'incircle_center': (x, y),
        'circumcircle_radius': R,
        'circumcircle_center': (x, y),
    }
    """
    triple = orbital_triple(n)
    r, ic = incircle_params(n)
    R, oc = circumcircle_params(n)
    return {
        "triple": triple,
        "incircle_radius": r,
        "incircle_center": ic,
        "circumcircle_radius": R,
        "circumcircle_center": oc,
    }


def complex_multiplier(n):
    """Complex multiplier z₀ from the complex plane mapping.

    Given z = n + ni and z' = (n-d) + di where d = dropping destination,
    z₀ = z' / z satisfies z · z₀ = z'.

    The real part is always 1/2, and the imaginary part is (2d - n) / (2n),
    lying in the interval (0, 1/2) for odd n.

    Returns a complex number.
    Example: complex_multiplier(3)  ≈ 0.5 + 0.1667i  (= 1/2 + 1/6·i)
    Example: complex_multiplier(27) ≈ 0.5 + 0.3519i  (= 1/2 + 19/54·i)
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    d = stopping_destination(n)
    real = 0.5
    imag = (2 * d - n) / (2 * n)
    return complex(real, imag)


def complex_multiplier_exact(n):
    """Exact complex multiplier as (real_fraction, imag_fraction).

    Returns (Fraction(1, 2), Fraction(2d - n, 2n)).
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    d = stopping_destination(n)
    return (Fraction(1, 2), Fraction(2 * d - n, 2 * n))


def proportional_power_ratio(x, base=2):
    """Proportional Power Ratio P(x) base b (Paper 3).

    P(x) = (x - b^k) / (b^(k+1) - b^k)
    where k = floor(log_b(x)).

    Maps each integer to [0, 1), spreading values between consecutive
    powers of the base. Useful for polar coordinate visualizations.

    Example: proportional_power_ratio(5, 2) = 0.25
    Example: proportional_power_ratio(6, 2) = 0.5
    """
    if x < base:
        raise ValueError(f"x must be >= base ({base})")
    k = int(math.log(x, base))
    # Correct for floating point: ensure b^k <= x
    bk = base ** k
    if bk > x:
        k -= 1
        bk = base ** k
    bk1 = base ** (k + 1)
    return (x - bk) / (bk1 - bk)
