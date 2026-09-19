"""L14: cost model for proving Collatz computations in a SNARK/STARK, vs MinRoot.

Part 1 (verified arithmetic): divide-and-conquer identities.
  Evaluator: v = (v_low, v_high) where v_high is the parity vector of
             x = (3^{s_low} n + r_low) / 2^{k/2}  (mod 2^{k/2});  one big multiply per level,
             work O(M(k) log k), but v_high still WAITS for v_low -> depth Theta(k).
  Verifier:  r(v) = 3^{s_high} r_low + 2^{k/2} r_high,  s = s_low + s_high; both halves in
             PARALLEL -> work O(M(k) log k), depth O(log^2 k).
  So the congruence statement is not smaller than the step statement -- both are ~O(k) big
  operations -- its advantage is parallel depth only.  (Corrects section 6 of the note.)

Part 2 (cost model): constraints per step for a fixed-width "Collatz mod 2^w" delay step
  x -> (x + b (2x + 1)) / 2  with b = x mod 2, in an arithmetic circuit over a prime field:
    parity/range: the low bit b must be proved consistent -> bit-decompose x into w bits
                  (w boolean constraints + 1 linear) OR w/L lookups into a 2^L table;
    step:         2 x' = x + b (2x + 1)  -> 1 multiplication constraint;
    range of x':  x' < 2^(w-1) -> another decomposition or reuse.
  MinRoot (Khovratovich-Maller-Tiwari): x_{i+1} = (x_i + y_i)^{1/5} verified as x_{i+1}^5 = x_i + y_i
  -> 3 multiplication constraints per step, no bit operations.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/snark_cost_model.py
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity_vector_vdf import parity_vector, r_and_s, inverse  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def pv_dc(n, k):
    """Divide-and-conquer evaluator: O(M(k) log k) work, still sequential across halves."""
    if k <= 8:
        return parity_vector(n, k)
    h = k // 2
    v_low = pv_dc(n % (1 << h), h)  # only the low h bits matter for the first h parities
    r, s = r_and_s(v_low)
    x = ((3**s * n + r) >> h) % (1 << (k - h))
    return v_low + pv_dc(x, k - h)


def r_dc(v):
    """Divide-and-conquer r(v), s(v): both halves independent -> parallel."""
    k = len(v)
    if k <= 8:
        return r_and_s(v)
    h = k // 2
    r_lo, s_lo = r_dc(v[:h])
    r_hi, s_hi = r_dc(v[h:])
    return 3**s_hi * r_lo + (r_hi << h), s_lo + s_hi


if __name__ == "__main__":
    rng = random.Random(28)
    bad = 0
    for k in (16, 64, 256, 1000, 4096):
        for _ in range(20):
            n = rng.getrandbits(k + 30) | 1
            v = parity_vector(n, k)
            bad += pv_dc(n, k) != v
            bad += r_dc(v) != r_and_s(v)
            bad += inverse(v) != n % (1 << k)
    print(f"divide-and-conquer evaluator and verifier identities: mismatches = {bad} (k up to 4096, 20 random n each)")

    print("\nConstraints per delay step (arithmetic circuit over a prime field):")
    print("  state width w | bit-decompose (w+2) | 16-bit lookups (w/16+2) | MinRoot (3) | ratio lookup/MinRoot")
    rows = []
    for w in (64, 128, 256, 1024, 4096):
        dec = w + 2
        lut = w // 16 + 2
        rows.append(dict(w=w, decompose=dec, lookup=lut, minroot=3, ratio=lut / 3))
        print(f"  {w:13d} | {dec:19d} | {lut:23d} | {3:11d} | {lut/3:8.1f}x")

    print("\nWhole-statement cost for k steps of the k-bit parity vector (fixed width k, 16-bit lookups):")
    print("  k     | step-by-step k*(k/16+2) | congruence: r(v) via k multiply-by-3 mod 2^k, each k/16 limbs | ratio")
    rows2 = []
    for k in (1024, 4096, 16384, 65536):
        step = k * (k // 16 + 2)
        # congruence: k running products P_i = P_{i+1}(1+2v_{i+1}) mod 2^k (k/16 limb ops each, plus carries ~ same),
        # k accumulations of v_i 2^i P_i (k/16 limb ops), one modular inverse/product (~ k/16 * log k)
        cong = k * (k // 16) * 2 + (k // 16) * k.bit_length() * 4
        rows2.append(dict(k=k, step=step, congruence=cong, ratio=step / cong))
        print(f"  {k:5d} | {step:23d} | {cong:60d} | {step/cong:5.2f}")
    print("  -> same order (both Theta(k^2/16) naive, both ~O(k log k) with FFT multiplication gadgets); no k-fold gap.")

    json.dump(dict(per_step=rows, whole=rows2, dc_mismatches=bad), open(RESULTS / "snark_cost_model.json", "w"), indent=1)
