# Collatz Integration

How the Collatz conjecture research backs Emanon's physics.

## Prime Addressing
- `collatz/factorization.py` provides prime factorization, GCD, LCM
- These operations define shared state, merges, and independence between universe addresses
- Residue class structure (mod 2^(k-s)) partitions the address space into natural regions

## Energy Conservation
- Proved: `s * log2(6) = T - log2(n) + epsilon` where epsilon in [-0.33, 0]
- This IS the energy balance — base-6 lattice is the exact tradeoff between 3-growth (expansion) and 2-destruction (compression)
- Average contraction per drop ~0.605 = net energy released per step

## Speed of Light
- Spectral gap of the transition Markov chain converges to 5/6
- lambda_2 -> 1/6 at large moduli
- This governs mixing rate = how fast information propagates through the address space
- Mixing time O(log M) at all scales

## Turn Structure
- Dropping time k = ticks to resolve — Set_k = "all addresses resolving in k turns"
- Odd stopping time spectrum: only ceil(s * log2(6)) values are possible for odd n
- Gap classes (4, 5, 7, 9, 10, ...) are impossible — some tick counts can never occur

## Local Physics
- Affine orbit structure: dest(n) = (3^s / 2^(k-s)) * n + C within each residue subgroup
- Physics is locally linear but globally chaotic
- Slope is universal across all subgroups of a given Set_k — same "law" everywhere locally

## Determinism Depth
- 2-adic determinism: mod 2^p determines the next p turns of behavior
- 89% of odd numbers classified by mod 4096
- Deeper modular knowledge = deeper prophecy (more ticks of deterministic future)

## Transition Connectivity
- Dropping set transition graph is fully connected — every Set_k can reach every Set_j
- No forbidden transitions = no forbidden merges in the multiverse

## 3-Adic Lock
- Within each subgroup of Set_k: dest(n) is locked to single residue mod 3^s
- Destinations never ≡ 0 (mod 3)
- Constrains what states a merge can produce — the 3-adic structure limits governance outcomes

## Key Source Files
- `collatz/core.py` — orbit, stopping_time, dropping_time
- `collatz/factorization.py` — prime factorization, GCD, LCM
- `collatz/dropping.py` — dropping sets, genus, modulus
- `collatz/stopping.py` — stopping classes, signatures
- `collatz/geometry.py` — complex multiplier, orbital triples
- `collatz/zoo.py` — parameter variation exploration
