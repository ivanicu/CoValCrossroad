"""How many rounds does DEFINITION.md carry that the residue does not? Computed, never recalled.

WHY THIS EXISTS. A commit body pushed 2026-08-04 quoted "the 9 rounds cited in DEFINITION.md but
not STATEMENT.md". The real figure was 54. The 9 was correct when someone measured it, and was
then carried across rounds by memory while both documents grew -- so it decayed into a 6x
understatement of my own debt, in the flattering direction, inside the one sentence of a report
that a later round acts on.

A count of my own work is exactly the population I am worst at enumerating, and it is the kind of
number that reads as recapitulation rather than assertion, so it never gets a control. The remedy
is not vigilance. It is to make the number unavailable except by running this.

THE INSTRUMENT IS REPORTED WITH THE NUMBER, because the answer depends on it: citations appear as
`(R123)`, inside groups like `(R494, R495, R496)`, and bare in prose. Three patterns, three
answers, all printed. Quoting one without naming which is how the next stale number gets born.
A positive control runs first: a round known to be in each document must be found by each pattern,
otherwise a low count is silence rather than a measurement.
"""
from __future__ import annotations
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEF = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"

PATTERNS = {
    "tight   (R123) alone":        lambda t: {int(x) for x in re.findall(r"\(R(\d{3})\)", t)},
    "grouped (R1, R2, R3)":        lambda t: {int(x) for g in re.findall(r"\(R\d{3}(?:,\s*R\d{3})*\)", t)
                                              for x in re.findall(r"\d{3}", g)},
    "loose   any R123 in prose":   lambda t: {int(x) for x in re.findall(r"\bR(\d{3})\b", t)},
}


def main() -> int:
    if not DEF.exists() or not STM.exists():
        print("  one of the two documents is missing -- refusing to report a debt"); return 2
    d, s = DEF.read_text(), STM.read_text()

    # POSITIVE CONTROL: each pattern must find a citation that is certainly present.
    known_d = re.search(r"\(R(\d{3})\)", d)
    known_s = re.search(r"\(R(\d{3})\)", s)
    if not (known_d and known_s):
        print("  no unambiguous citation found in one document -- the probe is unfit"); return 1
    kd, ks = int(known_d.group(1)), int(known_s.group(1))
    bad = [n for n, f in PATTERNS.items() if kd not in f(d) or ks not in f(s)]
    if bad:
        print(f"  control failed: {bad} cannot see a citation known to be present"); return 1

    print(f"  positive control: every pattern sees R{kd} in DEFINITION and R{ks} in STATEMENT\n")
    print(f"  {'instrument':<30}{'DEFINITION':>11}{'STATEMENT':>10}{'debt':>7}")
    debts = {}
    for name, f in PATTERNS.items():
        D, S = f(d), f(s)
        debts[name] = len(D - S)
        print(f"  {name:<30}{len(D):>11}{len(S):>10}{len(D-S):>7}")

    lo, hi = min(debts.values()), max(debts.values())
    print(f"\n  DEBT = {lo}-{hi} rounds, depending on the instrument."
          f" Quote the range or name the pattern; never a bare number.")
    print(f"  Measured base rate from earlier triage: about 1 in 3 of these carries a conclusion"
          f" that has since moved, so the expected yield is {lo//3}-{hi//3} corrections.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
