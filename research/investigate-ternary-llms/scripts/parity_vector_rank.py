"""L13: attack the parity-vector sequentiality conjecture with a communication-rank test.

For the forward map v = Phi_k(n mod 2^k), the output bit v_j depends on input bits 0..j.
Split those bits into a low half A (bits 0..h-1) and a high half B (bits h..j), h = ceil((j+1)/2),
and form the 2^h x 2^(j+1-h) matrix M[A][B] = v_j(A + 2^h B).  Its rank over GF(2) is the
number of terms in the smallest decomposition v_j = XOR_i f_i(A) g_i(B); a rank that is small
(polynomial in j) would give a divide-and-conquer evaluation of v_j from the two halves in
parallel, i.e. a parallel shortcut.  Full rank (2^h) says no such shortcut exists at this split.

Control: the same test on the closed-form INVERSE n = -r(v) 3^{-s} (mod 2^k), bit j as a
function of v_0..v_j split the same way.  The inverse is a log-depth computation (a sum and a
modular product), so if its rank is also full, communication rank -- like algebraic degree --
does not distinguish sequential from parallel here, and the test is uninformative.

Also reports the speculative-execution bound: with P processors (or a 2^p table), guess the
next log2(P) parities in parallel, giving exactly a log2(P)-fold speedup and no more.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/parity_vector_rank.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity_vector_vdf import inverse, parity_vector  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def gf2_rank(rows):
    """rows: list of Python ints (bitmasks).  Gaussian elimination over GF(2)."""
    rank = 0
    pivots = []
    for r in rows:
        for pv in pivots:
            r = min(r, r ^ pv)
        if r:
            pivots.append(r)
            rank += 1
    return rank


def q_rank(M):
    return int(np.linalg.matrix_rank(M.astype(np.float64)))


def matrix_forward(j):
    """M[A][B] = v_j(n) with n = A + 2^h B, A in [0, 2^h), B in [0, 2^(j+1-h))."""
    k = j + 1
    h = (k + 1) // 2
    nb = k - h
    M = np.zeros((1 << h, 1 << nb), dtype=np.uint8)
    for A in range(1 << h):
        for B in range(1 << nb):
            M[A, B] = parity_vector(A + (B << h), k)[j]
    return M


def matrix_inverse(j):
    """M[A][B] = bit j of inverse(v) with v_0..v_{h-1} = A, v_h..v_j = B."""
    k = j + 1
    h = (k + 1) // 2
    nb = k - h
    M = np.zeros((1 << h, 1 << nb), dtype=np.uint8)
    for A in range(1 << h):
        for B in range(1 << nb):
            code = A + (B << h)
            v = [(code >> i) & 1 for i in range(k)]
            M[A, B] = (inverse(v) >> j) & 1
    return M


if __name__ == "__main__":
    out = []
    print("   j   split h   forward rank GF2 / Q   inverse rank GF2 / Q   (full = 2^h)")
    t0 = time.time()
    for j in range(3, 22, 2):
        k = j + 1
        h = (k + 1) // 2
        Mf = matrix_forward(j)
        Mi = matrix_inverse(j)
        rows_f = [int("".join(map(str, row)), 2) for row in Mf]
        rows_i = [int("".join(map(str, row)), 2) for row in Mi]
        rf2, ri2 = gf2_rank(rows_f), gf2_rank(rows_i)
        rfq, riq = q_rank(Mf), q_rank(Mi)
        print(f"  {j:2d}     {h:2d}        {rf2:5d} / {rfq:5d}            {ri2:5d} / {riq:5d}          {1 << h:5d}   ({time.time()-t0:.0f}s)")
        out.append(dict(j=j, h=h, full=1 << h, fwd_gf2=rf2, fwd_q=rfq, inv_gf2=ri2, inv_q=riq))
    json.dump(out, open(RESULTS / "parity_vector_rank.json", "w"), indent=1)

    # a second split: A = bits 0..j-1 (everything but the top bit), B = bit j alone -> rank <= 2 trivially;
    # more interesting: A = bits 0..2, B = bits 3..j  (small low part): does v_j factor through a small
    # summary of the low bits?  Rank <= 2^3 = 8 always; report whether it is < 8.
    print("\nsmall-low-part split (A = bits 0..2, B = the rest): rank / 8")
    for j in (7, 11, 15):
        k = j + 1
        M = np.zeros((8, 1 << (k - 3)), dtype=np.uint8)
        for A in range(8):
            for B in range(1 << (k - 3)):
                M[A, B] = parity_vector(A + (B << 3), k)[j]
        print(f"  j={j}: GF2 rank {gf2_rank([int(''.join(map(str, r)), 2) for r in M])} / 8")

    print("\nspeculative execution: with P processors, guess the next log2(P) parities in parallel;")
    print("verified (parity_vector_vdf.py): a 2^p table jumps p steps per round -> speedup exactly log2(P). No larger speedup found here.")
