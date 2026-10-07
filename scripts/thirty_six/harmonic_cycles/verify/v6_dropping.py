"""Skeptic check 6: Q1.6 (dropping thresholds) and the claimed equivalence with 'no cycles'.

Independent code path: dropping words are generated COMBINATORIALLY (all words whose every proper
prefix has 3^(s_j) > 2^j and whose total has 2^k > 3^s -- Terras' coefficient stopping time), not
by scanning integers; they are then compared with a scan of n < 2^20 and with the repo functions.

Conventions (two step counts, stated on every table):
  shortcut word w: k = len(w) shortcut steps, s = odd steps;
  repo / Paper 1:  dropping_time(n) = k + s (non-shortcut steps), orbital_oddity(n) = s.
Output: v6_dropping.log
"""
import os
import sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, "C:/repos/collatz")
from collatz import dropping as repo_dropping      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v6_dropping.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")
    LOG.flush()


def T(n, c=1, q=3):
    return n // 2 if n % 2 == 0 else (q * n + c) // 2


def dropping_words(kmax, q=3):
    """Words w with q^(s_j) > 2^j for every proper prefix (j >= 1) and 2^k > q^s for w itself."""
    res = defaultdict(list)
    stack = [((), 0)]
    while stack:
        w, s = stack.pop()
        k = len(w)
        if k >= 1 and 2 ** k > q ** s:
            res[(k, s)].append(w)
            continue
        if k == kmax:
            continue
        stack.append((w + (0,), s))
        stack.append((w + (1,), s + 1))
    return res


def const(w, q=3):
    C = 0
    for j, b in enumerate(w):
        if b:
            C = q * C + (1 << j)
    return C


def residue(w, c=1, q=3):
    """The residue class mod 2^k whose parity word is w (by lifting bit by bit)."""
    k = len(w)
    r = 0
    for j in range(k):
        # choose bit j of r so that the j-th parity is w[j]
        y = r
        for i in range(j):
            y = T(y, c, q)
        if (y & 1) != w[j]:
            r += 1 << j
    return r


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Dropping words of 3x+1 generated combinatorially, k <= 24; thresholds x(w) = C(w)/D")
out("=" * 78)
KMAX = 24
dw = dropping_words(KMAX)
counts = [len(dw[c]) for c in sorted(dw)]
out("cells (k,s) and number of dropping words:", [(c, len(dw[c])) for c in sorted(dw)])
out("counts:", counts)
assert counts[:13] == [1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652]
out("  = 1 followed by OEIS A100982 (1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, ...).")
out("")
out("  K=k+s  (k,s)    D        words   integer thresholds   max threshold/smallest member of its class")
int_thr = []
for (k, s) in sorted(dw):
    D = 2 ** k - 3 ** s
    worst = Fraction(0)
    ints = []
    for w in dw[(k, s)]:
        x = Fraction(const(w), D)
        if x.denominator == 1:
            ints.append(("".join(map(str, w)), int(x)))
        # n has parity word w  <=>  3^s n + C(w) = 0 (mod 2^k); cross-checked by bit lifting for k <= 13
        r = (-const(w) * pow(3 ** s, -1, 2 ** k)) % (2 ** k)
        if k <= 13:
            assert r == residue(w)
        # smallest member >= 2 of the class r mod 2^k
        m = r if r >= 2 else r + 2 ** k
        worst = max(worst, x / m)
    int_thr += [((k, s), t) for t in ints]
    out(f"  {k+s:4d}  ({k},{s})".ljust(16) + f"{D:<9d}{len(dw[(k, s)]):<7d} {str(ints) if ints else 'none':20s} "
        f"{float(worst):.4f}")
assert int_thr == [((1, 0), ("0", 0)), ((2, 1), ("10", 1))]
out("  -> integer thresholds only in (1,0) [K = 1] and (2,1) [K = 3]: confirmed for every dropping")
out("     word with k <= 24 (i.e. every residue class with coefficient stopping time <= 24).")
out("     Largest threshold/member ratio stays < 1 (Terras' coefficient-stopping-time statement).")

# scan and repo convention
N = 1 << 20
dwset = {c: set(v) for c, v in dw.items()}
bad = 0
chk = 0
n_scanned = 0
for n in range(2, N):
    w = []
    m = n
    while True:
        w.append(m & 1)
        m = T(m)
        if m < n:
            break
    k, s = len(w), sum(w)
    if k <= KMAX:
        n_scanned += 1
        if tuple(w) not in dwset.get((k, s), ()):
            bad += 1
    if n < 3000:
        assert repo_dropping.dropping_time(n) == k + s and repo_dropping.orbital_oddity(n) == s
        chk += 1
out(f"scan 2 <= n < 2^20: {n_scanned} integers with dropping time k <= {KMAX}; dropping words not in the")
out(f"combinatorial list: {bad};  repo convention (dropping_time = k+s, orbital_oddity = s) checked on "
    f"{chk} values")
assert bad == 0

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. Is 'integer thresholds only in unit cells' EQUIVALENT to 'no non-trivial positive cycle'?")
out("   No.  It is IMPLIED by it; the converse needs the cycle's word, read from its minimum, to be")
out("   a dropping word, and that can fail.  Demonstration in the 3x+c family, where cycles exist:")
out("=" * 78)


def dropping_word_of(n, c):
    """Coefficient dropping word of the class of n for 3x+c: shortest prefix with 2^j > 3^(s_j)."""
    w = []
    y = n
    s = 0
    while True:
        w.append(y & 1)
        s += y & 1
        y = T(y, c)
        if 2 ** len(w) > 3 ** s:
            return tuple(w)


examples = []
for c in (5, 7, 11, 13, 17, 23, 29):
    seen = set()
    for n0 in range(1, 3000):
        y = n0
        path = []
        pos = {}
        while y not in pos and y not in seen:
            pos[y] = len(path)
            path.append(y)
            y = T(y, c)
        if y in pos:
            cy = path[pos[y]:]
            m = min(cy)
            i = cy.index(m)
            cy = cy[i:] + cy[:i]
            k, s = len(cy), sum(z % 2 for z in cy)
            wcyc = tuple(z % 2 for z in cy)
            wd = dropping_word_of(m, c)
            D = 2 ** len(wd) - 3 ** sum(wd)
            thr = Fraction(c * const(wd), D)
            examples.append((c, m, k, s, len(wd), sum(wd), thr, wd == wcyc))
        seen.update(path)
out("   c   cycle min   cycle cell   class dropping word cell   its threshold   word of cycle = dropping word?")
n_not = 0
for c, m, k, s, kd, sd, thr, same in examples:
    out(f"  {c:3d}  {m:6d}      ({k},{s})".ljust(30) + f"({kd},{sd})".ljust(22) + f"{str(thr):14s}  {same}")
    n_not += (not same)
out(f"   {n_not} of {len(examples)} positive cycles have a minimum that sits BELOW a non-integer (or")
out("   integer but different) threshold of a SHORTER dropping word; their own word is not a dropping")
out("   word, so 'no integer threshold' would not detect them.  E.g. 3x+5: the cycle {1,4,2} has word")
out("   100, but the class 1 mod 4 has dropping word 10 with threshold 5; n = 1 is simply below it.")
out("   The statement that IS equivalent in spirit is Terras' coefficient-stopping-time conjecture")
out("   (every n >= 2 exceeds the threshold of its class); it implies 'no non-trivial cycle', and the")
out("   converse implication is not known.")

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Mirror and cousin: thresholds for 3x-1 and 5x+1 (positive integers)")
out("=" * 78)
# 3x-1: same dropping words (the condition is on (k, s) only), thresholds -C/D < 0
neg_int = []
for (k, s) in sorted(dw):
    D = 2 ** k - 3 ** s
    for w in dw[(k, s)]:
        x = Fraction(-const(w), D)
        if x.denominator == 1 and len(w) <= 20:
            neg_int.append(((k, s), int(x)))
out("  3x-1: thresholds are -C(w)/D <= 0: every positive member of every dropping class drops at its")
out(f"        coefficient stopping time; integer thresholds (k <= 20): {neg_int}")
out("        A positive integer fails to drop under 3x-1 iff its word never acquires a dropping prefix;")
out("        the known ones are the cycle minima 1, 5, 17 (cells with D < 0).")
dw5 = dropping_words(16, q=5)
ints5 = []
for (k, s) in sorted(dw5):
    D = 2 ** k - 5 ** s
    for w in dw5[(k, s)]:
        x = Fraction(const(w, 5), D)
        if x.denominator == 1:
            ints5.append(((k, s), "".join(map(str, w)), int(x)))
out(f"  5x+1: dropping cells (k <= 16): {[(c, len(v)) for c, v in sorted(dw5.items())]}")
out(f"        integer thresholds: {ints5}")
out("        (1,0) threshold 0 is the only D = +1 unit cell of 5x+1; the other integer thresholds are its")
out("        'accident' cycles through 1 (cell (5,2), D = 7) and through 13, 17 (cell (7,3), D = 3).")
assert sorted(t[2] for t in ints5) == [0, 1, 13, 17]
LOG.close()
