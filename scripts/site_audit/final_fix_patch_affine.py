"""One-off patch used by the final fixer: 'subgroup' -> 'residue class' on proofs/affine-orbit.md
(a residue class mod 2^(k-s) is a coset, not a subgroup), and the dropping-time anchor.
Keeps the file's line endings. Each replacement must match exactly once."""
from pathlib import Path

path = Path(__file__).resolve().parents[2] / "site" / "proofs" / "affine-orbit.md"
raw = path.read_bytes()
crlf = b"\r\n" in raw
s = raw.decode("utf-8").replace("\r\n", "\n")

reps = [
    (r"[dropping time](/foundations/definitions#dropping-set) $k$ and orbital oddity $s$, within each residue-class subgroup mod $2^{k-s}$:",
     r"[dropping time](/foundations/definitions#dropping-time) $k$ and orbital oddity $s$, within each residue class mod $2^{k-s}$:"),
    (r"where $C$ is a constant depending only on the subgroup (residue class), not on $n$.",
     r"where $C$ is a constant depending only on the residue class, not on $n$."),
    (r"is an exact affine function of $n$ within each subgroup.",
     r"is an exact affine function of $n$ within each residue class."),
    (r"The theorem speaks about one subgroup at a time. Whether every subgroup of $\text{Dset}_k$ has the same $s$,",
     r"The theorem speaks about one residue class at a time. Whether every residue class of $\text{Dset}_k$ has the same $s$,"),
    (r"In that range the slope is the same across all subgroups of $\text{Dset}_k$,",
     r"In that range the slope is the same across all residue classes of $\text{Dset}_k$,"),
    (r"| Two subgroups, same slope |", r"| Two residue classes, same slope |"),
    (r"| Three subgroups, same slope |", r"| Three residue classes, same slope |"),
    (r"| Seven subgroups, same slope |", r"| Seven residue classes, same slope |"),
    (r"is also affine in $n$ within each subgroup.", r"is also affine in $n$ within each residue class."),
    (r"it is a single affine function on each subgroup (checked by computer",
     r"it is a single affine function on each residue class (checked by computer"),
    (r"the same holds for all large enough $n$ in a subgroup;",
     r"the same holds for all large enough $n$ in a residue class;"),
]
for a, b in reps:
    assert s.count(a) == 1, (s.count(a), a)
    s = s.replace(a, b)
assert "subgroup" not in s, [ln for ln in s.split("\n") if "subgroup" in ln]
if crlf:
    s = s.replace("\n", "\r\n")
path.write_bytes(s.encode("utf-8"))
print("patched", path.name, "crlf" if crlf else "lf")
