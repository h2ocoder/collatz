"""Q4.1 (second half)  A(a,b) as a function on the lattice: rays, ridge, and the critical slope.

Coordinates.  X = a ln 2, Y = b ln 3, L = X + Y = ln(2^a 3^b), theta = X / L.
The Collatz critical line 2^a = 3^b is theta = 1/2, i.e. slope b/a = ln 2 / ln 3 = 0.6309.

HEURISTIC (not a theorem; it assumes the Pierpont-prime density conjecture).
If the Pierpont points (i,j) have density kappa / (X + Y) per unit dX dY -- "2^i 3^j + 1 is
prime with probability C / ln(2^i 3^j)", kappa = C / (ln 2 ln 3) -- then

    ln prod_P (1 + e^{-sX - tY})  ~  kappa (pi^2/12) ln(s/t)/(s - t)          (s, t -> 0)

and the saddle point gives

    ln A(a,b) ~ 2 sqrt( c L m(theta) ),   c = kappa pi^2 / 12,
    m(theta) = min_{lam>0} psi(lam) (theta + lam (1 - theta)),   psi(lam) = ln(lam)/(lam - 1).

m is symmetric, m(theta) = m(1 - theta), with maximum m(1/2) = 1.

EXACT SADDLE STATEMENT (no density assumption).  With Phi(sig,tau) = ln of the generating
function at X = e^-sig, Y = e^-tau, the saddle for (a,b) solves a = -dPhi/dsig, b = -dPhi/dtau,
and along a size level set d(ln A)/d(theta) = L (s - t) with s = sig/ln2, t = tau/ln3.  So the
ridge is where s = t, where every Pierpont prime p is weighted by 1/(1 + p^s') (s' = s, since
e^{sig i + tau j} = (2^i 3^j)^s), and

    theta_ridge = sum_p (i_p ln 2) w_p / sum_p ln(p - 1) w_p + (absorption terms),
    w_p = 1 / (1 + (p-1)^s).

The ridge direction is the Fermi-weighted CENTRE OF MASS of the Pierpont points.  It lies on
the critical line iff the 2-part and the 3-part of p - 1 are equally large on average.

This script measures all of that on exact data, and compares with random control sets of the
same density (same boundary effects, none of the arithmetic).

Run:  python -X utf8 q41_rays.py      (about 1-2 minutes)
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import brentq, minimize_scalar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pierpont import pierpont_points  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q41_rays.log"), "w", encoding="utf-8")
LN2, LN3 = math.log(2), math.log(3)
RCRIT = LN2 / LN3
LEVELS = (60, 100, 140, 180, 220, 260, 300, 320)


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def m_theta(theta):
    def f(u):
        lam = math.exp(u)
        psi = 1.0 if abs(lam - 1) < 1e-9 else math.log(lam) / (lam - 1)
        return psi * (theta + lam * (1 - theta))
    r = minimize_scalar(f, bounds=(-40, 40), method="bounded", options={"xatol": 1e-10})
    return r.fun


def table_float(points, amax, bmax):
    """float64 DP: D then A (same recurrences as q41_fibre_count.py)."""
    D = np.zeros((amax + 1, bmax + 1))
    D[0, 0] = 1.0
    for i, j in points:
        if i > amax or j > bmax:
            continue
        D[i:, j:] = D[i:, j:] + D[: amax + 1 - i, : bmax + 1 - j]
    E = D + np.cumsum(D, axis=0)
    A = E.copy()
    A[1:, :] += np.cumsum(E[:-1, :], axis=1)
    return D, A


class Interp:
    """Bilinear interpolation of ln A on real (a, b)."""

    def __init__(self, A):
        with np.errstate(divide="ignore"):
            self.lnA = np.log(A)
        self.amax, self.bmax = A.shape[0] - 1, A.shape[1] - 1

    def __call__(self, a, b):
        if not (1 <= a <= self.amax - 1 and 1 <= b <= self.bmax - 1):
            return float("nan")
        i, j = int(math.floor(a)), int(math.floor(b))
        fa, fb = a - i, b - j
        g = self.lnA
        return ((1 - fa) * (1 - fb) * g[i, j] + fa * (1 - fb) * g[i + 1, j]
                + (1 - fa) * fb * g[i, j + 1] + fa * fb * g[i + 1, j + 1])

    def at(self, L, theta):
        return self(theta * L / LN2, (1 - theta) * L / LN3)


def ridge(interp, L, lo=0.2, hi=0.8):
    """argmax over theta of ln A on the size level set X + Y = L (quartic least-squares fit)."""
    th = np.arange(lo, hi + 1e-9, 0.005)
    v = np.array([interp.at(L, t) for t in th])
    ok = np.isfinite(v)
    if ok.sum() < 20:
        return float("nan"), float("nan")
    co = np.polyfit(th[ok] - 0.5, v[ok], 4)
    fine = np.linspace(lo, hi, 6001)
    pv = np.polyval(co, fine - 0.5)
    k = int(np.argmax(pv))
    return float(fine[k]), float(pv[k])


class Saddle:
    """Equal-multiplier saddle (s = t) for the exact generating function of a point set."""

    def __init__(self, points):
        self.i = np.array([p[0] for p in points], dtype=float)
        self.j = np.array([p[1] for p in points], dtype=float)
        self.size = self.i * LN2 + self.j * LN3

    def ab(self, s):
        """(a, b) = -grad Phi at sig = s ln2, tau = s ln3, split into Pierpont and absorption parts."""
        w = 1.0 / (1.0 + np.exp(np.minimum(s * self.size, 700)))
        a_p, b_p = float(np.sum(self.i * w)), float(np.sum(self.j * w))
        x, y = math.exp(-s * LN2), math.exp(-s * LN3)
        a_r = x / (1 - x) - x / (2 - x) + x / (1 - y + x)
        b_r = y / (1 - y) - y / (1 - y + x)
        return a_p, b_p, a_r, b_r

    def phi(self, s):
        x, y = math.exp(-s * LN2), math.exp(-s * LN3)
        return (float(np.sum(np.log1p(np.exp(-s * self.size))))
                + math.log((2 - x) / (1 - x)) + math.log((1 - y + x) / (1 - y)))

    def solve(self, L):
        f = lambda s: (lambda t: (t[0] + t[2]) * LN2 + (t[1] + t[3]) * LN3 - L)(self.ab(s))
        s = brentq(f, 1e-3, 5.0)
        a_p, b_p, a_r, b_r = self.ab(s)
        a, b = a_p + a_r, b_p + b_r
        return {"s": s, "a": a, "b": b, "theta": a * LN2 / L,
                "theta_points_only": a_p * LN2 / (a_p * LN2 + b_p * LN3),
                "lnA0": s * L + self.phi(s)}


def main():
    t0 = time.time()
    AMAX, BMAX = 480, 300
    out(f"box: 1 <= a <= {AMAX}, 0 <= b <= {BMAX};  X_max = {AMAX * LN2:.1f}, Y_max = {BMAX * LN3:.1f}")
    P = pierpont_points(AMAX, BMAX)
    out(f"Pierpont points in the box (primality proved, Lucas): {len(P)}   [{time.time() - t0:.0f} s]")
    with open(os.path.join(HERE, "q41_pierpont_points_480x300.json"), "w", encoding="utf-8") as f:
        json.dump([list(p) for p in P], f)

    # ------------------------------------------------------------------ density of Pierpont points
    Lcap = min(AMAX * LN2, BMAX * LN3)
    sizes = np.array([i * LN2 + j * LN3 for i, j in P])
    Xs = np.array([i * LN2 for i, j in P])
    thetas = Xs / sizes
    out("\nDENSITY OF PIERPONT POINTS.  N(L) = #{(i,j) in P : ln(2^i 3^j) <= L}; heuristic N(L) ~ kappa L")
    out("    L      N(L)   N(L)/L    per decade = N(L)/L * ln 10")
    for L in (25, 50, 100, 150, 200, 250, 300, int(Lcap)):
        n = int(np.sum(sizes <= L))
        out(f"  {L:>5d}  {n:>6d}   {n / L:6.3f}    {n / L * math.log(10):6.3f}")
    inside = sizes <= Lcap
    kappa_emp = float(np.sum(inside) / Lcap)
    kappa_naive = 3.0 / (LN2 * LN3)
    out(f"  kappa (empirical, L <= {Lcap:.0f}) = {kappa_emp:.4f};  naive 3/(ln2 ln3) = {kappa_naive:.4f}"
        f"  (Gleason: 'about 9 per decade' = kappa {9 / math.log(10):.3f})")
    # refined (Bateman-Horn style) constant: q | 2^i 3^j + 1 for a fraction f_q of the pairs (i,j),
    # f_q = 1/|H_q| if |H_q| is even and 0 otherwise, H_q = subgroup of (Z/q)* generated by 2 and 3
    # (cyclic group: |H_q| = lcm(ord 2, ord 3), and -1 lies in H_q iff |H_q| is even).
    from sympy import n_order, primerange
    C = 3.0   # the primes 2 and 3 never divide: (1 - 0)/(1 - 1/2) * (1 - 0)/(1 - 1/3) = 3
    out("  refined constant C = 3 * prod_{q >= 5} (1 - f_q)/(1 - 1/q),  f_q = Pr[q | 2^i 3^j + 1]:")
    marks = {10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 3 * 10 ** 5}
    last = 5
    for Q in sorted(marks):
        for q in primerange(last, Q + 1):
            h = int(np.lcm(n_order(2, q), n_order(3, q)))
            C *= (1 - (1.0 / h if h % 2 == 0 else 0.0)) / (1 - 1.0 / q)
        last = Q + 1
        out(f"     q <= {Q:>6d}:  C = {C:.4f},  kappa = C/(ln2 ln3) = {C / (LN2 * LN3):.4f},"
            f"  per decade = {C / (LN2 * LN3) * math.log(10):.3f}")
    out(f"     observed: kappa = {kappa_emp:.4f} +- {kappa_emp / math.sqrt(np.sum(inside)):.4f} (Poisson),"
        f"  per decade = {kappa_emp * math.log(10):.3f}")
    out("     DEAD END: the partial products keep falling; they do not converge.  f_q = index/(q-1) for the")
    out("     primes where <2,3> has even order and index > 1 in (Z/q)*, and those have positive density,")
    out("     so sum (f_q - 1/q) diverges.  No constant is claimed; only the empirical kappa is used below.")
    out("  angular distribution of the points with L <= Lcap (heuristic: uniform in theta):")
    hist, edges = np.histogram(thetas[inside], bins=10, range=(0, 1))
    out("   theta bin :", "  ".join(f"{edges[k]:.1f}-{edges[k + 1]:.1f}" for k in range(10)))
    out("   count     :", "  ".join(f"{int(h):>7d}" for h in hist))
    exp = np.sum(inside) / 10
    chi2 = float(np.sum((hist - exp) ** 2 / exp))
    out(f"   chi^2 against uniform, 9 d.o.f.: {chi2:.2f}   (5% critical value 16.92)")
    lo_half, hi_half = int(np.sum(thetas[inside] < 0.5)), int(np.sum(thetas[inside] > 0.5))
    out(f"   theta < 1/2 (3-heavy): {lo_half};  theta > 1/2 (2-heavy): {hi_half};  "
        f"z = {(hi_half - lo_half) / math.sqrt(hi_half + lo_half):+.2f}")

    out("\nCENTRE OF MASS of the Pierpont points with ln(p-1) <= U:")
    out("  theta_cm(U) = sum_p i_p ln2 / sum_p ln(p-1).   On the critical line iff theta_cm = 1/2.")
    out("  sd = standard deviation of theta_cm if each theta_p were independent uniform on [0,1].")
    out("      U   points   sum i ln2   sum j ln3   theta_cm      sd     z")
    for U in (10, 20, 40, 80, 160, 240, int(Lcap)):
        sel = sizes <= U
        sx, st = float(np.sum(Xs[sel])), float(np.sum(sizes[sel]))
        sd = math.sqrt(float(np.sum(sizes[sel] ** 2)) / 12) / st
        out(f"  {U:>5d}   {int(sel.sum()):>5d}   {sx:9.1f}   {st - sx:9.1f}    {sx / st:6.4f}   {sd:6.4f}  {(sx / st - 0.5) / sd:+5.2f}")

    # ------------------------------------------------------------------ tables
    D, A = table_float(P, AMAX, BMAX)
    with open(os.path.join(HERE, "q41_table.json"), encoding="utf-8") as f:
        exact = json.load(f)
    Aex = np.array(exact["A"], dtype=float)
    rel = np.max(np.abs(A[:41, :41] - Aex) / np.maximum(Aex, 1))
    out(f"\nfloat64 table agrees with the exact table on 0<=a,b<=40: max relative error {rel:.2e}")
    I = Interp(A)
    c_emp = kappa_emp * math.pi ** 2 / 12
    out(f"largest entry: ln A({AMAX},{BMAX}) = {math.log(A[AMAX, BMAX]):.2f}")

    # ------------------------------------------------------------------ growth along rays
    out("\nTABLE 2.  GROWTH ALONG RAYS b = r a.   ln A(a, round(r a)) and ln A / sqrt(L),  L = ln(2^a 3^b)")
    out("  heuristic leading term: ln A ~ h(theta) sqrt(L), h = 2 sqrt(c m(theta)), c = kappa_emp pi^2/12")
    rays = [0.1, 0.25, RCRIT ** 2 / 1.0, 0.5, RCRIT, 0.796, 1.0, RCRIT ** 2 / 0.25, 2.5]
    summary = []
    for r in rays:
        theta = 1 / (1 + r * LN3 / LN2)
        h = 2 * math.sqrt(c_emp * m_theta(theta))
        pts = []
        for a in range(4, AMAX + 1):
            b = int(round(r * a))
            if b > BMAX:
                break
            L = a * LN2 + b * LN3
            pts.append((a, b, L, math.log(A[a, b])))
        Ls = np.array([p[2] for p in pts])
        ys = np.array([p[3] for p in pts])
        sel = Ls >= 40
        M = np.vstack([np.sqrt(Ls[sel]), np.log(Ls[sel]), np.ones(sel.sum())]).T
        alpha, beta, gamma = np.linalg.lstsq(M, ys[sel], rcond=None)[0]
        summary.append((r, theta, h, alpha, beta))
        tag = "  <-- critical slope ln2/ln3" if abs(r - RCRIT) < 1e-9 else ""
        out(f"\n  r = {r:.4f}   theta = {theta:.4f}   heuristic h(theta) = {h:.3f}{tag}")
        out(f"    fit over L >= 40:  ln A = {alpha:.3f} sqrt(L) {beta:+.3f} ln L {gamma:+.3f}")
        show = [p for p in pts if p[0] in (10, 20, 40, 80, 160, 320, 480)] + [pts[-1]]
        seen = set()
        for a, b, L, y in show:
            if a in seen:
                continue
            seen.add(a)
            out(f"    a={a:>4d} b={b:>4d}  L={L:7.2f}  ln A={y:8.3f}  ln A/sqrt(L)={y / math.sqrt(L):6.3f}")
    out("\n  summary:   slope r   theta   heuristic h   fitted sqrt(L) coefficient   fitted ln L coefficient")
    for r, theta, h, alpha, beta in summary:
        out(f"            {r:7.4f}  {theta:6.4f}     {h:6.3f}            {alpha:6.3f}                  {beta:+6.3f}")

    # ------------------------------------------------------------------ smoothness across the line
    out("\nSMOOTHNESS ACROSS THE CRITICAL LINE.  second difference of ln A in theta on level sets")
    out("  (a kink or jump at theta = 1/2 would show as an outlier in the theta = 0.50 column)")
    grid = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
    out("      L  " + "".join(f"  d2@{t:.2f}" for t in grid))
    for L in (100, 150, 200, 250, 300):
        row = []
        for t in grid:
            d = 0.05
            row.append((I.at(L, t + d) - 2 * I.at(L, t) + I.at(L, t - d)) / d ** 2)
        out(f"  {L:>5d}  " + "".join(f"{v:>9.1f}" for v in row))

    # ------------------------------------------------------------------ ridge and saddle prediction
    out("\nRIDGE TEST.  ridge of ln A on SIZE level sets L = ln m, exact data, against the")
    out("  equal-multiplier saddle of the exact generating function (see module docstring).")
    S = Saddle(P)
    out("      L   theta* measured   slope b/a   theta saddle   theta saddle, Pierpont part only"
        "    s      ln A measured   s L + Phi")
    real_ridge = []
    for L in LEVELS:
        th, val = ridge(I, L)
        sd = S.solve(L)
        real_ridge.append((L, th))
        out(f"  {L:>5d}      {th:6.3f}         {(1 - th) / th * RCRIT:6.3f}       {sd['theta']:6.3f}"
            f"              {sd['theta_points_only']:6.3f}                {sd['s']:6.4f}"
            f"     {val:8.3f}     {sd['lnA0']:8.3f}")
    out("  (s L + Phi is the saddle exponent without the Gaussian prefactor -(1/2) ln det, hence larger)")

    out("\nSYMMETRY TEST on level sets.  S = (E(theta)+E(1-theta))/2 - E(1/2)   (symmetric drop)")
    out("                              AS = (E(theta)-E(1-theta))/2            (antisymmetric part)")
    out("  E = ln A.  theta > 1/2 is the 2-heavy side.  perfect symmetry: AS = 0.")
    out("      L   theta   E(theta)  E(1-theta)       S        AS     AS/|S|")
    for L in (100, 200, 300):
        e0 = I.at(L, 0.5)
        for t in (0.6, 0.7, 0.8):
            e1, e2 = I.at(L, t), I.at(L, 1 - t)
            Ssym, AS = 0.5 * (e1 + e2) - e0, 0.5 * (e1 - e2)
            out(f"  {L:>5d}   {t:.2f}   {e1:8.3f}   {e2:8.3f}  {Ssym:8.3f}  {AS:8.3f}   {AS / abs(Ssym):7.3f}")

    # ------------------------------------------------------------------ what about a + b = n ?
    out("\nFOR COMPARISON: level sets a + b = n (not size).  argmax of A(a, n-a):")
    out("      n    a*    b*    b*/a*")
    for n in (40, 80, 120, 160, 200, 240, 280):
        best = max(((A[a, n - a], a) for a in range(1, n) if a <= AMAX and n - a <= BMAX))
        a = best[1]
        out(f"  {n:>5d}  {a:>4d}  {n - a:>4d}   {(n - a) / a:6.3f}")
    out("  (so 'where is A largest' depends on which level set one uses)")

    # ------------------------------------------------------------------ random control
    NTRIAL = 200
    out(f"\nCONTROL.  {NTRIAL} random point sets with inclusion probability kappa_emp ln2 ln3 / (i ln2 + j ln3)")
    out("  on i >= 1, j >= 1, plus the real j = 0 (Fermat) points; same DP, same ridge estimator.")
    rng = np.random.default_rng(36)
    ii, jj = np.meshgrid(np.arange(1, AMAX + 1), np.arange(1, BMAX + 1), indexing="ij")
    prob = np.minimum(1.0, kappa_emp * LN2 * LN3 / (ii * LN2 + jj * LN3))
    fermat_pts = [p for p in P if p[1] == 0]
    ctrl = {L: [] for L in LEVELS}
    for trial in range(NTRIAL):
        mask = rng.random(prob.shape) < prob
        pts = fermat_pts + list(zip(ii[mask].tolist(), jj[mask].tolist()))
        _, Ar = table_float(pts, AMAX, BMAX)
        Ir = Interp(Ar)
        for L in LEVELS:
            ctrl[L].append(ridge(Ir, L)[0])
    out("      L   theta* exact   control mean   control sd   z of exact   fraction of controls >= exact")
    for L, th in real_ridge:
        c = np.array(ctrl[L])
        out(f"  {L:>5d}     {th:6.3f}        {c.mean():6.3f}       {c.std(ddof=1):6.3f}      "
            f"{(th - c.mean()) / c.std(ddof=1):+5.2f}          {float(np.mean(c >= th)):.3f}")

    # mirror image of the real set across the critical line
    out("\nMIRROR CONTROL.  reflect the real Pierpont set across the critical line, (X,Y) -> (Y,X),")
    out("  rounding to the nearest lattice point with i >= 1 (duplicates merged), and recompute the ridge.")
    mir = set()
    for i, j in P:
        i2, j2 = int(round(j * LN3 / LN2)), int(round(i * LN2 / LN3))
        if i2 >= 1 and i2 <= AMAX and j2 <= BMAX:
            mir.add((i2, j2))
    _, Am = table_float(sorted(mir), AMAX, BMAX)
    Im = Interp(Am)
    out(f"  mirrored set: {len(mir)} points (real: {len(P)})")
    out("      L   theta* real   theta* mirrored   mean    half-difference")
    for L, th in real_ridge:
        tm = ridge(Im, L)[0]
        out(f"  {L:>5d}     {th:6.3f}        {tm:6.3f}       {(th + tm) / 2:6.3f}      {(th - tm) / 2:+6.3f}")
    out("  mean - 1/2 is the part of the offset that does not flip (lattice/absorption asymmetry and")
    out("  rounding); the half-difference is the part carried by the actual positions of the primes.")

    # heuristic leading-order comparison on the critical line
    out("\nLEADING TERM ON THE CRITICAL LINE.  ln A(L, 1/2) against 2 sqrt(c L), c = kappa_emp pi^2/12")
    for L in (50, 100, 200, 300):
        out(f"  L={L:>4d}  ln A = {I.at(L, 0.5):8.3f}   2 sqrt(cL) = {2 * math.sqrt(c_emp * L):8.3f}"
            f"   ratio = {I.at(L, 0.5) / (2 * math.sqrt(c_emp * L)):.3f}")
    out("  (the ratio is below 1 and rises slowly: the corrections are of order -ln L, cf. the fitted")
    out("   ln L coefficients of about -1.6 to -2.1 in Table 2)")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
