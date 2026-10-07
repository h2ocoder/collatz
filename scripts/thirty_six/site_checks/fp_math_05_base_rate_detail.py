"""Reviewer check 5 (detail of check 3): at p = 37, the kernels (d+1, d) where the algebraic and the geometric
multiplicity of the eigenvalue +-1 of A = 2K differ.  Exact (sympy over Q).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fp_math_05_base_rate_detail.py
"""
from __future__ import annotations

import sympy as sp
from sympy import n_order

x = sp.symbols("x")
P = 37


def matrix(d: int) -> sp.Matrix:
    inv = pow(d, -1, P)
    A = sp.zeros(P, P)
    for v in range(P):
        A[v, v * inv % P] += 1
        A[v, ((d + 1) * v + 1) * inv % P] += 1
    return A


def mult(poly: sp.Poly, root: int) -> int:
    m = 0
    f = sp.Poly(x - root, x)
    while True:
        q, r = sp.div(poly, f)
        if not r.is_zero:
            return m
        poly, m = q, m + 1


for d in (2, 12, 14, 34):
    q = (d + 1) % P
    oq = n_order(q, P)
    powers = {pow(q, i, P): i for i in range(oq)}
    m = next(i for i in range(1, P) if pow(d, i, P) in powers)
    t = powers[pow(d, m, P)]
    idx = (P - 1) // (oq * m)
    A = matrix(d)
    cp = A.charpoly(x)
    for c in (1, -1):
        forced = idx if (oq % 2 == 0 and c**m == (-1) ** (m + t)) else 0
        alg = mult(cp, c)
        geo = P - (A - c * sp.eye(P)).rank() if alg else 0
        print(f"d = {d:2d}: ord(d+1) = {oq:2d}, m = {m}, t = {t:2d}, idx = {idx} | eigenvalue {c:+d} of A: forced by Theorem C {forced}, geometric {geo}, algebraic {alg}")
