"""Collatz Zoo: generalized nx+1, x/y dynamical systems.

Provides a framework for studying arbitrary Collatz-like maps,
measuring their thermodynamic properties (conservation, dissipation,
spectral gap, criticality), and finding phase transitions.

The classical Collatz conjecture is the special case n=3, y=2.
"""

import math
from collections import Counter
from fractions import Fraction


class CollatzSystem:
    """A generalized Collatz-like dynamical system.

    Rule: if x divisible by y, x -> x/y; else x -> n*x + c.
    Classical Collatz: n=3, y=2, c=1.

    Parameters
    ----------
    n : int or Fraction
        Multiplier for the "kick" step (odd step in classical Collatz).
    y : int
        Divisor for the "drain" step (even step in classical Collatz).
    c : int
        Additive constant in the kick step. Default 1.
    max_steps : int
        Safety limit to prevent infinite loops. Default 10_000.
    """

    def __init__(self, n=3, y=2, c=1, max_steps=10_000):
        self.n = n
        self.y = y
        self.c = c
        self.max_steps = max_steps

    def __repr__(self):
        return f"CollatzSystem(n={self.n}, y={self.y}, c={self.c})"

    def step(self, x):
        """Single step: x/y if y divides x, else n*x + c."""
        if x % self.y == 0:
            return x // self.y
        else:
            return self.n * x + self.c

    def orbit(self, x, stop_at=None):
        """Full orbit from x until cycle detected or max_steps.

        Parameters
        ----------
        x : int
            Starting value.
        stop_at : set or None
            Stop if we hit any value in this set. Default {1} for classical.

        Returns
        -------
        seq : list of int
            The orbit sequence.
        status : str
            'converged' if hit stop_at, 'cycle' if repeated, 'timeout' if max_steps.
        """
        if stop_at is None:
            stop_at = {1}
        seq = [x]
        seen = {x}
        for _ in range(self.max_steps):
            x = self.step(x)
            seq.append(x)
            if x in stop_at:
                return seq, 'converged'
            if x in seen:
                return seq, 'cycle'
            seen.add(x)
        return seq, 'timeout'

    def syracuse_step(self, x):
        """Generalized Syracuse step: apply n*x+c, then divide by y until can't.

        Returns (next_value, drain_count) where drain_count is how many
        times we divided by y.
        """
        if x % self.y == 0:
            raise ValueError(f"x={x} is divisible by y={self.y}, not a kick candidate")
        x = self.n * x + self.c
        drains = 0
        while x % self.y == 0:
            x //= self.y
            drains += 1
        return x, drains

    def syracuse_orbit(self, x):
        """Generalized Syracuse orbit: kick-then-drain until cycle or timeout.

        Only visits values not divisible by y (the "odd" values).

        Returns
        -------
        seq : list of int
            Values visited.
        drains : list of int
            Number of drain steps after each kick (the alpha sequence).
        status : str
            'converged', 'cycle', or 'timeout'.
        """
        if x % self.y == 0:
            raise ValueError(f"x={x} must not be divisible by y={self.y}")
        seq = [x]
        drains = []
        seen = {x}
        for _ in range(self.max_steps):
            x, d = self.syracuse_step(x)
            drains.append(d)
            seq.append(x)
            if x == 1:
                return seq, drains, 'converged'
            if x in seen:
                return seq, drains, 'cycle'
            seen.add(x)
        return seq, drains, 'timeout'

    # -------------------------------------------------------------------
    # Thermodynamic measurements
    # -------------------------------------------------------------------

    def criticality(self):
        """Criticality parameter μ = n / y^(expected drains per kick).

        For classical Collatz: μ = 3 / 2^(expected v₂) ≈ 3/4.
        μ < 1 → subcritical (convergent), μ > 1 → supercritical (divergent).

        Estimated empirically over sample orbits.
        """
        total_kicks = 0
        total_drains = 0
        for x in range(1, 1000, 2 if self.y == 2 else 1):
            if x % self.y == 0:
                continue
            try:
                _, d = self.syracuse_step(x)
                total_kicks += 1
                total_drains += d
            except Exception:
                continue
        if total_kicks == 0:
            return float('inf')
        avg_drains = total_drains / total_kicks
        return self.n / (self.y ** avg_drains)

    def measure_orbit_physics(self, x):
        """Measure thermodynamic quantities along an orbit.

        Returns a dict with:
        - energy_initial: log_y(x) — initial "potential energy"
        - total_steps: T — total steps taken
        - kick_count: s — number of kick (multiply) steps
        - drain_count: total drain (divide) steps
        - conservation_residual: ε = s·log_y(ny) - T + log_y(x) (should be ≤ 0)
        - avg_contraction: geometric mean of step ratios
        - max_value: peak "energy" reached
        - status: convergence status
        """
        seq, status = self.orbit(x)
        if len(seq) < 2:
            return {'status': status, 'trivial': True}

        log_y = lambda v: math.log(v) / math.log(self.y) if v > 0 else float('-inf')

        kicks = 0
        drain_steps = 0
        for i in range(len(seq) - 1):
            if seq[i] % self.y != 0:
                kicks += 1
            else:
                drain_steps += 1

        T = len(seq) - 1
        fundamental_constant = log_y(self.n * self.y)
        energy_initial = log_y(x)

        # Conservation law: s·log_y(ny) should ≈ T - log_y(x_final/x_initial)
        if seq[-1] > 0:
            energy_final = log_y(seq[-1])
        else:
            energy_final = 0
        epsilon = kicks * fundamental_constant - T + energy_final

        ratios = [seq[i+1] / seq[i] for i in range(len(seq) - 1) if seq[i] > 0]
        avg_ratio = math.exp(sum(math.log(r) for r in ratios) / len(ratios)) if ratios else 1.0

        return {
            'energy_initial': energy_initial,
            'energy_final': energy_final,
            'total_steps': T,
            'kick_count': kicks,
            'drain_count': drain_steps,
            'fundamental_constant': fundamental_constant,
            'conservation_residual': epsilon,
            'avg_contraction': avg_ratio,
            'max_value': max(seq),
            'orbit_length': len(seq),
            'status': status,
        }

    def survey(self, x_range=range(3, 1000, 2)):
        """Survey many starting values, return aggregate statistics.

        Returns a dict with counts of convergent/cycle/timeout orbits
        and aggregate physics measurements.
        """
        results = Counter()
        epsilons = []
        contractions = []
        max_vals = []
        cycles_found = set()

        for x in x_range:
            if x % self.y == 0:
                continue
            physics = self.measure_orbit_physics(x)
            results[physics['status']] += 1

            if physics.get('trivial'):
                continue

            epsilons.append(physics['conservation_residual'])
            contractions.append(physics['avg_contraction'])
            max_vals.append(physics['max_value'])

            if physics['status'] == 'cycle':
                # Record the cycle
                seq, _ = self.orbit(x)
                cycle_start = seq[-1]
                cycles_found.add(cycle_start)

        return {
            'system': repr(self),
            'n': self.n,
            'y': self.y,
            'c': self.c,
            'criticality': self.criticality(),
            'outcomes': dict(results),
            'epsilon_mean': sum(epsilons) / len(epsilons) if epsilons else None,
            'epsilon_max': max(epsilons) if epsilons else None,
            'epsilon_min': min(epsilons) if epsilons else None,
            'avg_contraction': sum(contractions) / len(contractions) if contractions else None,
            'max_value_seen': max(max_vals) if max_vals else None,
            'cycles_found': len(cycles_found),
            'sample_size': sum(results.values()),
        }

    def spectral_gap_estimate(self, modulus=256):
        """Estimate spectral gap of the transition matrix on Z/modZ.

        The spectral gap measures how fast the system mixes across
        residue classes. Gap near 1 = fast mixing, near 0 = slow mixing.
        """
        import numpy as np

        # Build transition matrix: T[i,j] = fraction of inputs ≡ i (mod M)
        # that map to j (mod M)
        M = modulus
        T = np.zeros((M, M))

        for x in range(M):
            y_val = self.step(x + 1)  # +1 to avoid 0
            j = (y_val - 1) % M
            T[x, j] += 1

        # Normalize rows
        row_sums = T.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        T = T / row_sums

        eigenvalues = np.abs(np.linalg.eigvals(T))
        eigenvalues.sort()
        lambda_1 = eigenvalues[-1]  # should be ~1
        lambda_2 = eigenvalues[-2]  # second largest

        return {
            'modulus': M,
            'lambda_1': float(lambda_1),
            'lambda_2': float(lambda_2),
            'spectral_gap': float(1 - lambda_2 / lambda_1),
        }


# -------------------------------------------------------------------
# Zoo sweep functions
# -------------------------------------------------------------------

def zoo_sweep(n_range=range(3, 20, 2), y_range=[2], c_values=[1],
              x_range=range(3, 500, 2)):
    """Sweep parameter space and measure physics for each system.

    Returns list of survey dicts, one per (n, y, c) combination.
    """
    results = []
    for c in c_values:
        for y in y_range:
            for n in n_range:
                if n <= 1:
                    continue
                sys = CollatzSystem(n=n, y=y, c=c, max_steps=5000)
                survey = sys.survey(x_range)
                results.append(survey)
    return results


def find_phase_boundary(y=2, c=1, n_values=None, x_range=range(3, 500, 2)):
    """Find the critical n where the system transitions from convergent to divergent.

    Uses fractional n values to locate the phase boundary precisely.
    """
    if n_values is None:
        # Sweep from 1.5 to 5.0 in steps of 0.25
        n_values = [1.5 + 0.25 * i for i in range(15)]

    results = []
    for n in n_values:
        sys = CollatzSystem(n=n, y=y, c=c, max_steps=5000)
        # For fractional n, we need to work with rationals
        # Just measure criticality and survey behavior
        survey = sys.survey(x_range)
        results.append({
            'n': n,
            'y': y,
            'c': c,
            'criticality': survey['criticality'],
            'convergent_frac': survey['outcomes'].get('converged', 0) / max(survey['sample_size'], 1),
            'cycle_frac': survey['outcomes'].get('cycle', 0) / max(survey['sample_size'], 1),
            'timeout_frac': survey['outcomes'].get('timeout', 0) / max(survey['sample_size'], 1),
            'epsilon_mean': survey['epsilon_mean'],
        })
    return results


def print_zoo_table(results):
    """Pretty-print zoo sweep results."""
    print(f"{'System':<30} {'μ':>8} {'Conv%':>7} {'Cyc%':>7} {'Div%':>7} {'ε_mean':>10} {'ε_max':>10}")
    print("-" * 85)
    for r in results:
        conv = r['outcomes'].get('converged', 0) / max(r['sample_size'], 1) * 100
        cyc = r['outcomes'].get('cycle', 0) / max(r['sample_size'], 1) * 100
        div = r['outcomes'].get('timeout', 0) / max(r['sample_size'], 1) * 100
        eps_mean = f"{r['epsilon_mean']:.4f}" if r['epsilon_mean'] is not None else "N/A"
        eps_max = f"{r['epsilon_max']:.4f}" if r['epsilon_max'] is not None else "N/A"
        mu = f"{r['criticality']:.4f}" if r['criticality'] != float('inf') else "∞"
        print(f"{r['system']:<30} {mu:>8} {conv:>6.1f}% {cyc:>6.1f}% {div:>6.1f}% {eps_mean:>10} {eps_max:>10}")
