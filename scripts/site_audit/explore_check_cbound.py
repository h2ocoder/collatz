"""C < 2^e for every dropping word (so a congruence candidate n is positive for d >= 1);
largest fixed point C/(2^e-3^s) per level (candidates n <= d need d <= that)."""
from fractions import Fraction
from explore_check_dictionary import words_bruteforce, word_affine

for s in range(1, 15):
    worst_ratio = Fraction(0)
    worst_fix = Fraction(0)
    for w in words_bruteforce(s):
        s_, e, C = word_affine(w)
        worst_ratio = max(worst_ratio, Fraction(C, 2 ** e))
        worst_fix = max(worst_fix, Fraction(C, 2 ** e - 3 ** s))
    print(f"s={s:2d}: max C/2^e = {float(worst_ratio):.4f}   max C/(2^e-3^s) = {float(worst_fix):.3f}")
