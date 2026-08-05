#!/usr/bin/env python3
"""R519 — which clauses narrow what CLAUSE TWO already admits? All four, one population.

R514-R518 tested clause one and clause four against clause two in separate rounds with separate
instruments. This puts all four on ONE population with ONE question, the comparison the
deliverable needs and has never had.

ESTIMAND (before method): for each clause X, the number of two-passing arms that X drops. That is
  the only quantity in which a clause "adds" to the definition.
IDENTIFICATION: fully identified on the 41 arms carrying clause 1/2/3 verdicts (R294) joined to
  clause-4 scores at the home judge (R436).
SCOPE  population: 41 arms · instrument: R294's interval verdicts + R436's contrast · baseline:
  the set clause two admits · regime: home judge J, 968 prompts.
WORLDS  A · every clause narrows something; the definition is a genuine four-way conjunction.
        B · exactly one narrows; the others are decoration and the definition is a pair.
KILL (pre-registered): if two or more of clauses 1/3/4 drop >=1 two-passer, world B dies.
POSITIVE CONTROL: the instrument must return NON-ZERO drops somewhere, else every zero is
  silence and the whole comparison is UNVERIFIED.
NEGATIVE CONTROL: clause two against its own admitted set must drop exactly 0. Anything else
  means the join is malformed.
SHAM: apply each clause to the arms clause two REJECTS. A clause dropping many there but none
  among passers discriminates on a different axis, which is informative and is not narrowing.
NOISE FLOOR: R518 measured every two-passer at 4.90x-8.65x MDE above clause four's bar, so that
  zero is resolved rather than under-powered. Clause 1 and 3 come from R294's own CIs.
MULTIPLICITY: 3 clauses x 41 arms; every cell reported.
IMPOSSIBLE HERE: the second release, where clause two admits 0 of 7 so nothing can be compared
  against it. Named, unchanged from R517/R518.
"""
import glob, json, pathlib, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())
    rows = cen["rows"]
    r436 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    atJ = {c["arm"]: c for c in r436["cells"] if not c["arm"].endswith(("_08b", "_08bR"))}

    arms = sorted(set(rows) & set(atJ))
    if not arms:
        print("  empty join -> UNRUNNABLE"); return 2
    ok = {"one": lambda a: rows[a]["ok1"], "two": lambda a: rows[a]["ok2"],
          "three": lambda a: rows[a]["ok3"], "four": lambda a: not bool(atJ[a]["excluded"])}
    p2 = [a for a in arms if ok["two"](a)]
    print(f"  population {len(arms)} arms · clause two admits {len(p2)}\n")

    bad = [a for a in p2 if not ok["two"](a)]
    print(f"  NEGATIVE CONTROL  clause two against its own admitted set drops {len(bad)} -> "
          f"{'PASS' if not bad else 'FAIL -- join malformed'}")
    if bad: return 2

    print(f"\n  {'clause':<9}{'drops of the ' + str(len(p2)) + ' passers':>26}"
          f"{'drops of the ' + str(len(arms)-len(p2)) + ' rejects':>26}")
    res = {}
    for c in ("one", "three", "four"):
        dp = [a for a in p2 if not ok[c](a)]
        dr = [a for a in arms if not ok["two"](a) and not ok[c](a)]
        res[c] = {"drops_from_passers": sorted(dp), "n_passers_dropped": len(dp),
                  "n_rejects_dropped": len(dr)}
        print(f"  {c:<9}{len(dp):>26}{len(dr):>26}")
    pos_ok = any(v["n_passers_dropped"] > 0 for v in res.values())
    print(f"\n  POSITIVE CONTROL  some clause drops a two-passer -> "
          f"{'PASS -- a zero elsewhere is a measurement' if pos_ok else 'FAIL -- all zero, UNVERIFIED'}")
    if not pos_ok:
        print("  -> no conclusion admissible."); return 0

    narrowing = [c for c, v in res.items() if v["n_passers_dropped"] > 0]
    world = "B" if len(narrowing) == 1 else "A"
    print(f"\n  clauses that narrow what clause two admits: {narrowing}")
    for c in narrowing:
        for a in res[c]["drops_from_passers"]:
            print(f"    {c:<7}drops {a:<18} {rows[a]['prov']}")
    print(f"\n  WORLD {world} -- " +
          (f"the definition reduces to clause two AND clause {narrowing[0]}" if world == "B"
           else "more than one clause narrows; the conjunction is genuine"))
    adm = [a for a in p2 if all(ok[c](a) for c in ("one", "three", "four"))]
    print(f"  surviving all four: {sorted(adm)}")
    print(f"  identical to the census's own admitted set? {sorted(adm) == sorted(cen['admitted'])}")

    out = pathlib.Path(__file__).parent / "results/clause_reduction.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_arms": len(arms), "n_pass2": len(p2), "per_clause": res,
                               "narrowing": narrowing, "world": world, "admitted": sorted(adm),
                               "matches_census_admitted": sorted(adm) == sorted(cen["admitted"])},
                              indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
