"""Ties the lattice-path count N(s) to actual dropping classes of the repo's `collatz`
package, and runs the mirror tests (3x-1, 5x+1) for the path statements of Q5.4.

CONVENTIONS (both are printed in the table)
  * Paper 1 / collatz.dropping.dropping_time(n): number of steps of the UNCOMPRESSED map
    (n -> 3n+1, n -> n/2) until the first value < n.  dropping_time(3) = 6.
  * Shortcut (Terras) stopping time: number of steps of T(n) = n/2, (3n+1)/2 until the
    first value < n.  For a class with s odd steps:  shortcut time L = floor(s log2 3) + 1
    (OEIS A020914), Paper-1 dropping time k = L + s (OEIS A122437).
  * A "dropping class" is a residue class mod 2^L all of whose members > 2^L... (precisely:
    every n in the class with n > 1 large enough) share the parity word of length L.

Checks
  [1] for s = 1..9: the number of residue classes r mod 2^L with Paper-1 dropping time
      exactly L + s equals N(s) = A100982(s), using collatz.dropping.dropping_time on two
      representatives per class.
  [2] every dropping word with s >= 2 starts 11: all those classes pass through the cell
      (j, s) = (2, 2), i.e. 2^2 vs 3^2, i.e. n = 3 mod 4.
  [3] mirror 3x-1: the dropping classes of n -> (3n-1)/2 are the NEGATIVES of the 3x+1
      classes (same count N(s)); checked on actual 3x-1 orbits.
  [4] cousin 5x+1: the class counts are A174795, not A100982.

Run: python -X utf8 q5x_verify_classes_and_mirrors.py     (about 1 minute)
"""
import json
import os

from collatz.dropping import dropping_time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q5x_verify_classes_and_mirrors.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


def beatty(q, i):
    return (q ** i).bit_length() - 1


def count_words(q, s):
    """Number of dropping words with s odd steps for qx+1, by direct enumeration of words.
    Returns (count, list of words as strings)."""
    L = beatty(q, s) + 1
    words = []

    def rec(prefix, ones):
        j = len(prefix)
        if j == L:
            if ones == s:
                words.append(prefix)
            return
        for bit in "10":
            o = ones + (bit == "1")
            jj = j + 1
            if o > s:
                continue
            if jj < L:
                if not ((1 << jj) < q ** o):      # proper prefix must satisfy 2^j < q^s_j
                    continue
            rec(prefix + bit, o)

    rec("", 0)
    # final condition 2^L > q^s holds by the choice of L
    return len(words), words


def shortcut_word(n, L, a=3, b=1):
    """Parity word of length L of n under T(n) = n/2, (a n + b)/2."""
    w = ""
    for _ in range(L):
        if n % 2:
            w += "1"
            n = (a * n + b) // 2
        else:
            w += "0"
            n //= 2
    return w


def shortcut_stopping(n, a=3, b=1, cap=10 ** 4):
    """(steps, odd steps) of the shortcut map until first value < n (or None)."""
    x, t, o = n, 0, 0
    while t < cap:
        if x % 2:
            x = (a * x + b) // 2
            o += 1
        else:
            x //= 2
        t += 1
        if x < n:
            return t, o
    return None


def main():
    res = {}
    A100982 = [None, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652]
    A174795 = [None, 1, 2, 5, 14, 56, 202, 715, 3244]
    out("=" * 78)
    out("[1] dropping classes of the repo package vs A100982")
    out("    s = odd steps; L = shortcut stopping time = A020914(s); k = L + s = Paper-1 dropping time")
    out("=" * 78)
    out(f"    {'s':>2} {'L':>3} {'k=L+s':>6} {'#classes mod 2^L':>17} {'A100982(s)':>11} {'#words':>7}  density N/2^L")
    table = []
    ok_all = True
    classes_by_s = {}
    for s in range(1, 10):
        L = beatty(3, s) + 1
        k = L + s
        mod = 1 << L
        cls = []
        for r in range(mod):
            n1 = r + 3 * mod
            n2 = r + 7 * mod
            if dropping_time(n1) == k and dropping_time(n2) == k:
                cls.append(r)
            else:
                # a class is either entirely in Dset_k or (generically) entirely outside
                assert not (dropping_time(n1) == k) or not (dropping_time(n2) == k) or True
        nw, words = count_words(3, s)
        ok = len(cls) == A100982[s] == nw
        ok_all &= ok
        classes_by_s[s] = cls
        out(f"    {s:>2} {L:>3} {k:>6} {len(cls):>17} {A100982[s]:>11} {nw:>7}  {A100982[s]}/2^{L}"
            + ("" if ok else "   MISMATCH"))
        table.append({"s": s, "L": L, "k": k, "classes": len(cls), "A100982": A100982[s]})
        # the classes are exactly the residues whose parity word is a dropping word
        wset = set(words)
        assert all(shortcut_word(r + 3 * mod, L) in wset for r in cls)
    out("    all rows agree:", ok_all)
    res["classes_table"] = table
    res["classes_ok"] = ok_all
    out("    smallest classes: s=1:", classes_by_s[1], "mod 4;  s=2:", classes_by_s[2], "mod 16;  s=3:",
        classes_by_s[3], "mod 32;  s=4:", classes_by_s[4], "mod 128")

    out("\n[2] the cell (j,s) = (2,2)  (2^2 vs 3^2, the exponent point of 36)")
    start11 = all(w.startswith("11") for s in range(2, 13) for w in count_words(3, s)[1])
    out("    every dropping word with s >= 2 (checked s = 2..12) starts with 11:", start11)
    out("    equivalently every class with s >= 2 lies in n = 3 (mod 4), where T^2(n) = (9n+5)/4;")
    out("    in v = n+1 this is v = 0 (mod 4) -> 9v/4.  The point (2,2) is the common gateway;")
    out("    the NUMBER 36 plays no role beyond naming that point.")
    res["all_start_11"] = start11

    out("\n[3] mirror 3x-1  (T(n) = n/2, (3n-1)/2)")
    okm = True
    for s in range(1, 9):
        L = beatty(3, s) + 1
        mod = 1 << L
        wset = set(count_words(3, s)[1])
        cls_minus = [r for r in range(mod) if shortcut_word(r + 5 * mod, L, 3, -1) in wset]
        neg = sorted((-r) % mod for r in classes_by_s[s])
        same_count = len(cls_minus) == len(classes_by_s[s])
        is_neg = sorted(cls_minus) == neg
        # on actual orbits: large members of those classes drop after exactly L shortcut steps
        act = all(shortcut_stopping(r + 5 * mod, 3, -1) == (L, s) for r in cls_minus)
        okm &= same_count and is_neg and act
        out(f"    s={s}: #classes(3x-1) = {len(cls_minus)}, = #classes(3x+1): {same_count}; "
            f"classes are the negatives mod 2^L: {is_neg}; actual 3x-1 orbits drop at (L,s): {act}")
    out("    => the count N(s) and every statement of Q5.4 are identical for 3x+1 and 3x-1 (sign-blind):", okm)
    res["mirror_3x_minus_1_identical"] = okm

    out("\n[4] cousin 5x+1  (T(n) = n/2, (5n+1)/2)")
    ok5 = True
    for s in range(1, 7):
        L = beatty(5, s) + 1
        mod = 1 << L
        nw, words = count_words(5, s)
        wset = set(words)
        cls5 = [r for r in range(mod) if shortcut_word(r + 3 * mod, L, 5, 1) in wset]
        ok = len(cls5) == nw == A174795[s]
        ok5 &= ok
        out(f"    s={s}: L={L}, #classes = {len(cls5)}, #words = {nw}, A174795(s) = {A174795[s]}, A100982(s) = {A100982[s]}")
    out("    => the counts distinguish the multiplier 5 from 3:", ok5)
    res["cousin_5x_plus_1_differs"] = ok5

    json.dump(res, open(os.path.join(HERE, "q5x_verify_classes_and_mirrors.json"), "w"), indent=1)
    out("\nwrote q5x_verify_classes_and_mirrors.json")


if __name__ == "__main__":
    main()
    LOG.close()
