#!/usr/bin/env python3
"""R520 — is clause ③'s provenance set COMPLETE, or does it admit a label-reader?

R519 established ③ is the only clause narrowing what ② admits. Its verdicts come from a
4-element hardcoded literal in R294, `USES_PROMPT_LABELS`, declared rather than derived. The
definition's entire working content now rests on that literal.

ESTIMAND (before method): the number of arms whose GENERATING RULE opens the human labels but
  which are absent from `USES_PROMPT_LABELS` -- i.e. label-readers that clause ③ silently admits.
IDENTIFICATION: fully identified. select_core.py:102 is an explicit conditional naming the exact
  rule families that open data/comparisons.jsonl, and every arm's rule is recoverable from its tag.
SCOPE  population: the arms R294 scored and the arms R436 scored at the home judge · instrument:
  the code's own gate, not a keyword search · baseline: the declared literal · regime: first
  release, home judge.
WORLDS  A · the literal is complete -- every arm in a label-reading family is in it, so ③'s
              4 exclusions are the true set and R519 stands.
        B · at least one arm in a label-reading family is absent, so ③ admits a cheater and the
              admitted set is inflated.
KILL (pre-registered): any arm matching a label-reading rule family and absent from the literal
  kills world A.
POSITIVE CONTROL: the derivation must recover all 4 declared members from their tags alone. If
  it cannot, the tag->rule mapping is wrong and no absence claim is admissible.
NEGATIVE CONTROL: rules the source documents as label-blind -- topw_k, random_k, topabs_k, full
  -- must NOT be derived as label-readers. A derivation that flags them is over-broad, which is
  the 19-of-19 failure a keyword search already produced on this exact question.
SHAM: the satisfaction axis. select_core.py documents FIVE rules consuming satisfaction
  (topvar_k, topwvar_k, oracle_k, greedy_k, indep_k) versus THREE consuming labels. Deriving on
  the satisfaction list instead must give a DIFFERENT, larger set -- proving the instrument is
  reading the label gate and not merely "any rule that consumes something".
MULTIPLICITY: one test per arm; every arm's classification printed.
IMPOSSIBLE HERE: whether an arm's tag faithfully records the rule it was built with. That needs
  the generating invocation, which the npz does not carry. Named, not marked planned.
"""
import glob, json, pathlib, re, sys

LABEL_RULES = ("oracle_k", "indep_k", "greedy_k")           # select_core.py:102
SAT_RULES   = ("topvar_k", "topwvar_k", "oracle_k", "greedy_k", "indep_k")   # --select-npz help
BLIND_RULES = ("random_k", "topw_k", "topabs_k", "full")    # documented satisfaction-blind
DECLARED    = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}

def rule_of(tag, fams):
    for f in fams:
        if tag.startswith(f):
            return f
    return None

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    src = (root / "corebench/select_core.py").read_text()
    # verify the gate is still what we think, from the object
    gate = re.search(r'if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\(ROOT / "data" / "comparisons\.jsonl"', src)
    print(f"  GATE READ FROM SOURCE: {gate.group(1).strip() if gate else 'NOT FOUND'}")
    if not gate:
        print("  cannot locate the label gate -> UNRUNNABLE"); return 2
    found = tuple(x.strip().strip('"') for x in gate.group(1).split(","))
    if set(found) != set(LABEL_RULES):
        print(f"  source gate {found} != assumed {LABEL_RULES} -> UNRUNNABLE"); return 2
    print(f"    matches the assumed families -> PASS\n")

    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    r436 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    atJ = [c["arm"] for c in r436["cells"] if not c["arm"].endswith(("_08b", "_08bR"))]
    universe = sorted(set(cen) | set(atJ))
    print(f"  universe: {len(universe)} arms ({len(cen)} scored by R294, {len(atJ)} by R436 at J)")

    derived = {t for t in universe if rule_of(t, LABEL_RULES)}
    pos_ok = DECLARED <= derived
    print(f"\n  POSITIVE CONTROL  derivation recovers all 4 declared members: "
          f"{'PASS' if pos_ok else 'FAIL -- ' + str(sorted(DECLARED - derived))}")
    blind = {t for t in universe if rule_of(t, BLIND_RULES)}
    neg_ok = not (blind & derived)
    print(f"  NEGATIVE CONTROL  no documented label-blind rule derived as a reader: "
          f"{'PASS' if neg_ok else 'FAIL -- ' + str(sorted(blind & derived))}  ({len(blind)} blind arms)")
    sat = {t for t in universe if rule_of(t, SAT_RULES)}
    sham_ok = sat != derived and len(sat) > len(derived)
    print(f"  SHAM  satisfaction list gives a DIFFERENT, larger set: {len(sat)} vs {len(derived)} -> "
          f"{'PASS' if sham_ok else 'FAIL -- instrument not specific to the label gate'}")
    if not (pos_ok and neg_ok):
        print("  -> instrument unvalidated; UNVERIFIED."); return 0

    missing = sorted(derived - DECLARED)
    scored  = [t for t in missing if t in cen]
    world = "B" if missing else "A"
    print(f"\n  arms in a LABEL-READING family: {len(derived)}")
    print(f"  declared in USES_PROMPT_LABELS : {len(DECLARED)}")
    print(f"  ⭐ ABSENT FROM THE LITERAL      : {len(missing)} -> {missing}")
    if missing:
        print(f"     of those, carrying a ③ verdict in R294's census: {scored}")
        for t in scored:
            print(f"       {t:<24} ok2={cen[t]['ok2']} ok3={cen[t]['ok3']}  prov={cen[t]['prov']!r}")
    print(f"\n  WORLD {world} -- " +
          ("the literal is INCOMPLETE; ③ admits at least one label-reading family member"
           if world == "B" else "the literal is complete over this universe"))

    out = pathlib.Path(__file__).parent / "results/provenance_completeness.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"gate_from_source": list(found), "n_universe": len(universe),
                               "derived_label_readers": sorted(derived), "declared": sorted(DECLARED),
                               "missing_from_literal": missing, "missing_with_clause3_verdict": scored,
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
