namespace Emanon.Collatz;

/// <summary>
/// Represents the Collatz dropping genus: (Set_k, oddity_s, index_I).
/// This is the per-write stamp used in merge conflict resolution.
/// </summary>
public readonly record struct Genus(int SetK, int OddityS, int Index)
{
    /// <summary>Parse from stamp string: "set_k=K oddity_s=S index_i=I"</summary>
    public static Genus Parse(string stamp)
    {
        var parts = stamp.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        int setK = 0, oddity = 0, index = 0;
        bool foundSetK = false;
        foreach (var part in parts)
        {
            var kv = part.Split('=');
            if (kv.Length != 2) continue;
            switch (kv[0])
            {
                case "set_k":    setK   = int.Parse(kv[1]); foundSetK = true; break;
                case "oddity_s": oddity = int.Parse(kv[1]); break;
                case "index_i":  index  = int.Parse(kv[1]); break;
            }
        }
        if (!foundSetK)
            throw new FormatException($"Invalid genus stamp — expected 'set_k=N oddity_s=N index_i=N', got: '{stamp}'");
        return new Genus(setK, oddity, index);
    }

    public override string ToString() => $"set_k={SetK} oddity_s={OddityS} index_i={Index}";
}
