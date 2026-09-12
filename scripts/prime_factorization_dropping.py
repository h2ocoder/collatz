"""How does a number's prime factorization affect its dropping behaviour?

Structure of the experiment
---------------------------
The dropping time k(n) of an odd n is a function of n mod 2^k (Terras).
Residues multiply, so the *only* channel through which factorization can
reach the first drop is the residue of each prime factor mod 2^K.  Part A
makes that channel explicit:

  A1. Dset_3 membership is the Dirichlet character chi_{-4}:  an odd n is in
      Dset_3 iff it has an even number of prime factors == 3 (mod 4), counted
      with multiplicity.  (Exact; verified numerically.)
  A2. 2-adic discrete-log coordinates.  (Z/2^K)^* = <-1> x <5>, so every odd
      residue is (-1)^eps * 5^t.  eps adds mod 2 and t adds mod 2^(K-2) under
      multiplication.  Each populated Dset_k is tabulated in (eps, t) form.
  A3. Product tables: exact P(Dset(pq) = k | Dset(p)=k1, Dset(q)=k2) under the
      Dirichlet null (primes uniform on the residues of their set), compared
      with the empirical table over actual prime pairs.

Part B asks whether factorization carries any signal *beyond* residues for
whole-orbit statistics (total stopping time, peak, number of drops), which
are NOT residue-determined:

  B1. Sieve n < N; features: is_prime, omega, Omega, spf class, squarefree,
      perfect square, 3 | n.
  B2. Compare each class's mean of the statistic against a residue-matched
      null: E[stat | n mod 2^J] averaged with the class's own residue weights.
      A class with signal beyond residues shows a residual z-score >> 3.

Part C: special families (odd squares, m^2 by m mod 8, prime squares,
Mersenne 2^a-1, Fermat-type 2^a+1, powers of 3).

Outputs: prints markdown tables; writes data/prime_factorization_dropping.csv
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data"
N = 1 << 20          # range for the whole-orbit sieve
K_EXACT = 16         # modulus 2^K for the exact residue tables
J_MATCH = 12         # residue modulus used for the matched null
RNG = np.random.default_rng(7)


# ----------------------------------------------------------------------
# vectorised Collatz statistics
# ----------------------------------------------------------------------

def orbit_stats(ns: np.ndarray):
    """Return (dropping_time, total_stopping_time, log2(peak), n_drops) for each n.

    Standard map: n -> 3n+1 (odd), n/2 (even).  n_drops counts the number of
    times the orbit sets a new minimum below the previous record-low (i.e. the
    number of dropping-set traversals until 1).  Uses the T-map for speed but
    reports standard-step counts.
    """
    ns = ns.astype(np.int64)
    cur = ns.copy()
    steps = np.zeros_like(ns)
    drop_time = np.full_like(ns, -1)
    peak = ns.copy()
    record = ns.copy()
    n_drops = np.zeros_like(ns)
    active = cur > 1
    while active.any():
        c = cur[active]
        odd = (c & 1) == 1
        nxt = np.where(odd, 3 * c + 1, c >> 1)
        st = steps[active] + 1
        # peak
        pk = peak[active]
        peak[active] = np.maximum(pk, nxt)
        # first drop
        dt = drop_time[active]
        newly = (dt < 0) & (nxt < ns[active])
        dt = np.where(newly, st, dt)
        drop_time[active] = dt
        # record lows
        rec = record[active]
        below = nxt < rec
        n_drops[active] += below
        record[active] = np.where(below, nxt, rec)
        cur[active] = nxt
        steps[active] = st
        active = cur > 1
    return drop_time, steps, np.log2(peak.astype(np.float64)), n_drops


# ----------------------------------------------------------------------
# factorization sieve
# ----------------------------------------------------------------------

def spf_sieve(n: int) -> np.ndarray:
    spf = np.zeros(n, dtype=np.int64)
    spf[1] = 1
    for i in range(2, n):
        if spf[i] == 0:
            spf[i::i][spf[i::i] == 0] = i
    return spf


def factor_features(n: int, spf: np.ndarray):
    """Return arrays omega, Omega, lpf, squarefree, is_square, is_primepower for 0..n-1."""
    omega = np.zeros(n, dtype=np.int64)
    Omega = np.zeros(n, dtype=np.int64)
    lpf = np.zeros(n, dtype=np.int64)
    sqfree = np.ones(n, dtype=bool)
    for m in range(2, n):
        x = m
        last = 0
        while x > 1:
            p = spf[x]
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            omega[m] += 1
            Omega[m] += e
            if e > 1:
                sqfree[m] = False
            last = p
        lpf[m] = last
    r = np.arange(n)
    root = np.floor(np.sqrt(r)).astype(np.int64)
    is_square = root * root == r
    is_pp = omega == 1
    return omega, Omega, lpf, sqfree, is_square, is_pp


# ----------------------------------------------------------------------
# Part A: exact residue algebra
# ----------------------------------------------------------------------

def residue_dropping_table(K: int):
    """Dropping time of every odd residue mod 2^K, using a large representative.

    Times > K are reported as K+1 ("undetermined at this modulus")."""
    M = 1 << K
    odd = np.arange(1, M, 2, dtype=np.int64)
    reps = odd + 3 * M  # large representative; drop time <= K is then exact
    dt, _, _, _ = orbit_stats(reps)
    dt = np.where(dt > K, K + 1, dt)
    return odd, dt


def discrete_log_coords(K: int):
    """Map odd residue r mod 2^K -> (eps, t) with r = (-1)^eps 5^t mod 2^K."""
    M = 1 << K
    half = 1 << (K - 2)
    t_of = np.full(M, -1, dtype=np.int64)
    eps_of = np.full(M, -1, dtype=np.int64)
    x = 1
    for t in range(half):
        t_of[x] = t
        eps_of[x] = 0
        t_of[(-x) % M] = t
        eps_of[(-x) % M] = 1
        x = (5 * x) % M
    return eps_of, t_of


def part_a():
    print("\n# Part A — exact residue algebra (mod 2^%d)\n" % K_EXACT)
    M = 1 << K_EXACT
    odd, dt = residue_dropping_table(K_EXACT)
    eps_of, t_of = discrete_log_coords(K_EXACT)
    sets = sorted(set(dt.tolist()))
    print("Populated dropping sets (k <= %d): %s\n" % (K_EXACT, [k for k in sets if k <= K_EXACT]))

    # A1: chi_{-4} law
    in3 = dt == 3
    print("A1. Dset_3 = {n odd : n ≡ 1 mod 4}:", bool(np.all(in3 == (odd % 4 == 1))))

    # A2: discrete-log description of each set, at its own modulus 2^k
    print("\nA2. Dropping sets in 2-adic discrete-log coordinates n = (-1)^eps · 5^t")
    print("    (t reduced mod 2^(k-2); eps=0 ⇔ n≡1 mod 4)\n")
    print("| k | #residues mod 2^k | eps | t mod 2^(k-2) |")
    print("|---|---|---|---|")
    for k in sets:
        if k > K_EXACT or k < 3:
            continue
        mk = 1 << k
        rs = sorted(set((odd[dt == k] % mk).tolist()))
        # coordinates at modulus 2^k
        e_k, t_k = discrete_log_coords(k)
        coords = sorted(set((int(e_k[r]), int(t_k[r])) for r in rs))
        eps_vals = sorted(set(e for e, _ in coords))
        ts = sorted(t for _, t in coords)
        tstr = str(ts) if len(ts) <= 24 else f"{len(ts)} values, e.g. {ts[:12]}…"
        print(f"| {k} | {len(rs)} | {eps_vals} | {tstr} |")

    # A3: product tables — exact under Dirichlet null
    print("\nA3. Dropping set of a product p·q, given the sets of p and q (exact, Dirichlet null)\n")
    pop = [k for k in sets if 3 <= k <= K_EXACT]
    res_by_k = {k: odd[dt == k] for k in pop}
    table = {}
    for k1 in pop:
        for k2 in pop:
            if k2 < k1:
                continue
            r1 = res_by_k[k1]
            r2 = res_by_k[k2]
            # sample products if too many pairs
            if len(r1) * len(r2) > 4_000_000:
                a = RNG.choice(r1, 2_000_000)
                b = RNG.choice(r2, 2_000_000)
            else:
                a, b = np.meshgrid(r1, r2)
                a, b = a.ravel(), b.ravel()
            prod = (a * b) % M
            dprod = dt[(prod - 1) // 2]
            c = Counter(dprod.tolist())
            tot = sum(c.values())
            table[(k1, k2)] = {k: v / tot for k, v in sorted(c.items())}
    cols = pop + [K_EXACT + 1]
    print("| Dset(p) × Dset(q) | " + " | ".join(f"→{k}" if k <= K_EXACT else f"→>{K_EXACT}" for k in cols) + " |")
    print("|---|" + "---|" * len(cols))
    for (k1, k2), dist in table.items():
        print(f"| {k1} × {k2} | " + " | ".join(f"{dist.get(k, 0):.3f}" for k in cols) + " |")

    # Marginal for comparison
    c = Counter(dt.tolist())
    tot = sum(c.values())
    print("\nMarginal over all odd n: " + ", ".join(f"{k}: {c[k]/tot:.3f}" for k in cols))
    return odd, dt, table


# ----------------------------------------------------------------------
# Part B: whole-orbit statistics vs factorization, residue-matched
# ----------------------------------------------------------------------

def matched_null(stat, resid, mask, base_mask):
    """Residual of mean(stat[mask]) vs the residue-matched expectation.

    Expectation = sum_r w_r * E[stat | resid=r, base_mask], where w_r is the
    residue histogram of the class.  Returns (obs, exp, z)."""
    J = 1 << J_MATCH
    base = base_mask
    sums = np.bincount(resid[base], weights=stat[base], minlength=J)
    cnts = np.bincount(resid[base], minlength=J).astype(float)
    sq = np.bincount(resid[base], weights=stat[base] ** 2, minlength=J)
    mean_r = np.divide(sums, cnts, out=np.zeros(J), where=cnts > 0)
    var_r = np.divide(sq, cnts, out=np.zeros(J), where=cnts > 0) - mean_r ** 2
    w = np.bincount(resid[mask], minlength=J).astype(float)
    n = w.sum()
    exp = (w * mean_r).sum() / n
    obs = stat[mask].mean()
    se = math.sqrt((w * var_r).sum()) / n
    return obs, exp, (obs - exp) / se if se > 0 else float("nan")


def part_b():
    print("\n# Part B — whole-orbit statistics vs factorization, residue-matched (n < 2^20, odd, n>1)\n")
    n = np.arange(N, dtype=np.int64)
    spf = spf_sieve(N)
    omega, Omega, lpf, sqfree, is_square, is_pp = factor_features(N, spf)
    is_prime = (spf == n) & (n >= 2)
    odd = (n & 1) == 1
    base = odd & (n > 1)

    dt, tst, lpk, nd = orbit_stats(n[base])
    stats = {}
    lg = np.log2(n[base].astype(float))
    stats["dropping_time"] = dt.astype(float)
    stats["total_steps / log2 n"] = tst / lg
    stats["log2(peak) - log2 n"] = lpk - lg
    stats["n_drops / log2 n"] = nd / lg
    idx = n[base]
    resid = (idx % (1 << J_MATCH))

    def sel(mask_full):
        return mask_full[base]

    classes = {
        "prime": is_prime,
        "composite": ~is_prime & (n > 1),
        "omega=1 (prime power)": is_pp,
        "omega=2": omega == 2,
        "omega>=3": omega >= 3,
        "Omega>=4": Omega >= 4,
        "squarefree": sqfree,
        "not squarefree": ~sqfree,
        "perfect square": is_square,
        "3 | n": n % 3 == 0,
        "5 | n": n % 5 == 0,
        "7 | n": n % 7 == 0,
        "spf >= 100": lpf >= 100,
        "all prime factors ≡ 1 mod 4": np.array([_all_pf_1mod4(m, spf) for m in range(N)]),
    }
    rows = []
    for cname, cmask in classes.items():
        m = sel(cmask)
        for sname, s in stats.items():
            obs, exp, z = matched_null(s, resid, m, np.ones_like(m))
            rows.append(dict(cls=cname, stat=sname, count=int(m.sum()),
                             observed=obs, residue_matched=exp, z=z,
                             overall=float(s.mean())))
    df = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "prime_factorization_dropping.csv", index=False)
    for sname in stats:
        print(f"\n## {sname}   (overall mean over odd n: {stats[sname].mean():.4f})\n")
        print("| class | count | observed | residue-matched | z |")
        print("|---|---:|---:|---:|---:|")
        for _, r in df[df.stat == sname].iterrows():
            print(f"| {r.cls} | {r['count']} | {r.observed:.4f} | {r.residue_matched:.4f} | {r.z:+.1f} |")

    # size-matched prime vs composite on total stopping time
    print("\n## primes vs odd composites by dyadic range: mean total steps / log2 n\n")
    print("| range | primes (n, mean) | composites (n, mean) | diff/se |")
    print("|---|---|---|---:|")
    tot = stats["total_steps / log2 n"]
    pm = sel(is_prime)
    cm = sel(~is_prime & (n > 1))
    for j in range(10, 20):
        rng = (idx >= (1 << j)) & (idx < (1 << (j + 1)))
        a = tot[rng & pm]
        b = tot[rng & cm]
        se = math.sqrt(a.var() / len(a) + b.var() / len(b))
        print(f"| [2^{j}, 2^{j+1}) | {len(a)}, {a.mean():.4f} | {len(b)}, {b.mean():.4f} | {(a.mean()-b.mean())/se:+.2f} |")
    return df


def _all_pf_1mod4(m, spf):
    if m < 2 or m % 2 == 0:
        return False
    while m > 1:
        p = spf[m]
        if p % 4 != 1:
            return False
        m //= p
    return True


# ----------------------------------------------------------------------
# Part C: special families
# ----------------------------------------------------------------------

def part_c():
    print("\n# Part C — special families\n")
    # odd squares
    m = np.arange(3, 4001, 2, dtype=np.int64)
    sq = m * m
    dt, tst, lpk, nd = orbit_stats(sq)
    print("C1. odd squares m^2, 3<=m<=3999: dropping time always 3?", bool(np.all(dt == 3)),
          "(m^2 ≡ 1 mod 8 ⇒ Dset_3, proof: (2t+1)^2 = 8·T(t)+1)")
    # second drop after a square: dest = (3m^2+1)/4; classify by m mod 8
    dest = (3 * sq + 1) // 4
    dt2, _, _, _ = orbit_stats(dest)
    print("\n    second dropping time of m^2 (i.e. of dest=(3m²+1)/4), by m mod 8:")
    print("    | m mod 8 | dest ≡ 1 mod 4 (next drop is 3) fraction | distribution of next dropping time |")
    print("    |---|---|---|")
    for r in (1, 3, 5, 7):
        sel = m % 8 == r
        c = Counter(dt2[sel].tolist())
        tot = sel.sum()
        print(f"    | {r} | {np.mean(dest[sel] % 4 == 1):.3f} | " + ", ".join(f"{k}: {v/tot:.3f}" for k, v in sorted(c.items())[:6]) + " |")

    # prime squares vs the prime itself: total stopping time correlation
    from sympy import primerange
    ps = np.array(list(primerange(3, 20000)), dtype=np.int64)
    _, t_p, _, _ = orbit_stats(ps)
    _, t_p2, _, _ = orbit_stats(ps * ps)
    _, t_p3, _, _ = orbit_stats(ps * ps * ps)
    r12 = np.corrcoef(t_p, t_p2)[0, 1]
    r13 = np.corrcoef(t_p, t_p3)[0, 1]
    # control: correlation of total stopping time between p and a random odd of size p^2
    ctrl = RNG.integers(1, ps * ps) | 1
    _, t_c, _, _ = orbit_stats(ctrl)
    rc = np.corrcoef(t_p, t_c)[0, 1]
    print(f"\nC2. corr(total steps of p, of p^2) = {r12:+.3f}; (p, p^3) = {r13:+.3f}; control (p, random odd ~p^2) = {rc:+.3f}")
    print(f"    mean total steps/log2 n: p: {np.mean(t_p/np.log2(ps)):.3f}, p^2: {np.mean(t_p2/np.log2(ps*ps)):.3f}, p^3: {np.mean(t_p3/np.log2(ps**3)):.3f}")

    # Mersenne / Fermat-type / powers of 3
    print("\nC3. structured families (dropping time k, oddity s of the first drop):")
    fam = {
        "2^a - 1": [(1 << a) - 1 for a in range(2, 40)],
        "2^a + 1": [(1 << a) + 1 for a in range(2, 40)],
        "3^b": [3 ** b for b in range(1, 26)],
        "3^b + 2": [3 ** b + 2 for b in range(1, 26)],
        "(4^a - 1)/3": [((1 << (2 * a)) - 1) // 3 for a in range(2, 20)],
    }
    for name, vals in fam.items():
        vals = np.array(vals, dtype=np.int64)
        vals = vals[vals < (1 << 40)]
        dt, tst, lpk, nd = orbit_stats(vals)
        print(f"    {name:12s} dropping times: {dt.tolist()[:20]}")


if __name__ == "__main__":
    part_a()
    part_c()
    part_b()
