"""Iteration of concepts and closed-form lens advances."""

from collatz.core import collatz_step
from collatz.embeddings.concept import Concept


def _syr_step(n: int) -> int:
    """One Syracuse step: T_syr(n) = (3n+1)/2^v if n odd; n/2 if even (single halving)."""
    if n % 2 == 0:
        return n // 2
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n


def T(c: Concept) -> Concept:
    """Apply one Collatz step to each component independently."""
    return Concept(c.name, tuple(collatz_step(n) for n in c.vec))


def T_syracuse(c: Concept) -> Concept:
    """Apply one Syracuse step (collapse trailing halvings on odd-step result)."""
    return Concept(c.name, tuple(_syr_step(n) for n in c.vec))


_LENS_TRANSITIONS = {
    "sector": lambda v: (v - 1) % 12,
}


def advance_lens(value: int, lens_name: str) -> int:
    """Advance a discrete lens value by one Syracuse step in closed form.

    Only supported for lenses whose post-step value is a function of the
    pre-step value alone (currently: sector).
    """
    if lens_name not in _LENS_TRANSITIONS:
        raise ValueError(f"no closed-form advance for lens '{lens_name}'")
    return _LENS_TRANSITIONS[lens_name](value)
