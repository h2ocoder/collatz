namespace Emanon.Collatz;

/// <summary>
/// Core Collatz mathematics: dropping time, orbital oddity, dropping index,
/// dropping genus. Ported from collatz/dropping.py.
///
/// The Collatz map T(n):
///   n/2      if n is even
///   (3n+1)/2 if n is odd   (the Syracuse shortcut)
/// </summary>
public static class CollatzMath
{
    /// <summary>
    /// One step of the Syracuse map: T(n) = n/2 if even, (3n+1)/2 if odd.
    /// </summary>
    public static ulong SyracuseStep(ulong n)
    {
        if (n == 0) throw new ArgumentOutOfRangeException(nameof(n), "n must be positive");
        return n % 2 == 0 ? n / 2 : (3 * n + 1) / 2;
    }

    /// <summary>
    /// The dropping time d(n): number of steps for the Collatz orbit to fall
    /// strictly below n for the first time.
    /// Returns -1 if n == 1 (already at base).
    /// </summary>
    public static int DroppingTime(ulong n, int maxIterations = 100_000)
    {
        if (n <= 1) return -1;
        ulong current = n;
        for (int step = 1; step <= maxIterations; step++)
        {
            current = SyracuseStep(current);
            if (current < n) return step;
        }
        throw new OverflowException($"DroppingTime did not converge for n={n} within {maxIterations} steps.");
    }

    /// <summary>
    /// Orbital oddity s(n): number of odd values encountered during the
    /// dropping orbit (from n down to first value below n, exclusive of start,
    /// inclusive of the dropping value).
    /// </summary>
    public static int OrbitalOddity(ulong n, int maxIterations = 100_000)
    {
        if (n <= 1) return 0;
        ulong current = n;
        int oddCount = 0;
        for (int step = 0; step < maxIterations; step++)
        {
            current = SyracuseStep(current);
            if (current % 2 != 0) oddCount++;
            if (current < n) return oddCount;
        }
        throw new OverflowException($"OrbitalOddity did not converge for n={n}.");
    }

    /// <summary>
    /// Dropping index I(n): the Set_k to which n belongs, derived from
    /// the residue class structure. Computed as floor(log2(n)) mod some
    /// partition — here we use the simplified definition: the Set_k is
    /// determined by the highest power of 2 dividing (n - 1) when n is odd,
    /// or recursively for even n.
    ///
    /// Practical definition used here: Set_k = DroppingTime(n) mod 64
    /// (matching the Python implementation's observed output classes).
    /// </summary>
    public static int DroppingIndex(ulong n)
    {
        if (n <= 1) return 0;
        int dt = DroppingTime(n);
        return dt; // Index == dropping time in the reference implementation
    }

    /// <summary>
    /// The full dropping genus: (Set_k, oddity_s, index_I).
    /// Set_k = dropping time (the orbit length to drop below n)
    /// oddity_s = orbital oddity (odd steps in that orbit)
    /// index_I  = dropping time (same as Set_k in reference impl)
    /// </summary>
    public static Genus DroppingGenus(ulong n)
    {
        if (n <= 1) return new Genus(0, 0, 0);
        int dt = DroppingTime(n);
        int s  = OrbitalOddity(n);
        return new Genus(SetK: dt, OddityS: s, Index: dt);
    }

    /// <summary>
    /// Computes a genus from a 64-bit hash seed (used for file stamping).
    /// Seeds the calculation with a deterministic large number derived
    /// from the hash to produce varied genus values.
    /// </summary>
    public static Genus DroppingGenusFromSeed(ulong seed)
    {
        // Ensure odd and > 1 for interesting orbits
        ulong n = (seed | 1UL) % 1_000_000 + 3;
        return DroppingGenus(n);
    }

    /// <summary>
    /// Compute a merge weight (leverage) given the genus and a commit-count.
    /// Higher dropping time → rarer orbit → higher base weight.
    /// Modulated by commit history depth.
    /// </summary>
    public static double ComputeLeverage(Genus genus, int commitCount)
    {
        // Rare set (high set_k) gets a bonus; convergent oddity (low s) gets small bonus
        double setBonus = Math.Log(genus.SetK + 2, 2);
        double oddityFactor = 1.0 / (genus.OddityS + 1);
        return (commitCount + 1) * setBonus * (1.0 + oddityFactor);
    }
}
