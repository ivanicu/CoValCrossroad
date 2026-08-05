#!/usr/bin/env python3
"""R521 — what does the declared literal COST once the population widens?

R520 found ③'s hardcoded set misses 6 label-readers, with zero blast radius over the 41 arms it
was used on. This prices the hazard: how many arms change admission status between the DECLARED
literal and the DERIVED gate, over the 56-arm home-judge population.

⛔ FIRST, A CHECK THAT CANNOT FAIL, DEMOTED TO A CONTROL. The previous round's announced next
step was "re-run the derivation over the original 41 and see if it reproduces the admitted set".
R520's own output forces the answer: derived-minus-declared is 6 arms, of which 0 carry a ③
verdict, and the positive control already showed declared is a subset of derived. So over the 41
the two sets are EQUAL by construction and the reproduction could not have come out otherwise.
It is used below as a POSITIVE CONTROL on the instrument, which is what it is good for, and it
is not reported as a finding.

ESTIMAND (before method): the number of arms whose ③ status differs between literal and derived
  gate over the 56, and their A2 scores relative to the ② bar.
IDENTIFICATION: ⚠ PARTIAL and stated. 15 of the 56 have no ② verdict on disk, so for those,
  admission is a CANDIDACY judged by a point comparison against the ② bar, not the interval
  verdict R294 uses. Bounds, not verdicts.
SCOPE  population: 56 home-judge arms · instrument: the code gate at select_core.py:102 ·
  baseline: ②'s bar, taken at the conservative TOP of R514's measured range, 0.5504 ·
  regime: first release, home judge, 968 prompts.
WORLDS  A · the literal and the gate agree everywhere that matters -- the 6 extra label-readers
              would fail ② anyway, so the defect is free.
        B · the 6 sit ABOVE the ② bar, so the literal would admit top-scoring label-readers that
              the gate excludes, and the defect has a price.
KILL (pre-registered): if any of the 6 scores below the ② bar, it is not a candidate and world B
  weakens by one; if all 6 do, world B dies.
POSITIVE CONTROL: over R294's 41, literal and gate must agree exactly. Forced, hence a control.
NEGATIVE CONTROL: the 33 documented label-blind arms must have identical status under both.
SHAM: repeat the difference count on the SATISFACTION rule list instead of the label list. A
  different count proves the price is specific to the label gate, not to any rule partition.
NOISE FLOOR: the ② bar is a range [0.5386, 0.5504] across arms (R514); the conservative top is
  used, so a candidate above it is above it under every measured setting.
MULTIPLICITY: 56 arms x 1 status comparison; every disagreement printed.
IMPOSSIBLE HERE: an actual ② interval verdict for the 15 arms outside R294's census. It needs
  the blind-pool contrast recomputed on them, which is a scoring run. Named, not marked planned.
"""
import glob, json, pathlib, sys

LABEL_RULES = ("oracle_k", "indep_k", "greedy_k")
SAT_RULES   = ("topvar_k", "topwvar_k", "oracle_k", "greedy_k", "indep_k")
BLIND_RULES = ("random_k", "topw_k", "topabs_k", "full")
DECLARED    = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
BAR2        = 0.5504          # conservative TOP of R514's measured bar2 range

def fam(tag, fams):
    return next((f for f in fams if tag.startswith(f)), None)

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    r436 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    atJ = {c["arm"]: c for c in r436["cells"] if not c["arm"].endswith(("_08b", "_08bR"))}
    if not atJ:
        print("  empty population -> UNRUNNABLE"); return 2

    lit  = lambda t: t not in DECLARED          # passes ③ under the literal
    gate = lambda t: fam(t, LABEL_RULES) is None

    # POSITIVE CONTROL (forced, used as a control not a finding)
    dis41 = [t for t in cen if t in atJ and lit(t) != gate(t)]
    print(f"  POSITIVE CONTROL  over R294's {len([t for t in cen if t in atJ])} arms, literal and gate "
          f"disagree on {len(dis41)} -> {'PASS' if not dis41 else 'FAIL ' + str(dis41)}")
    print(f"    (forced by R520's output; a control, never a result)")

    # NEGATIVE CONTROL
    blind = [t for t in atJ if fam(t, BLIND_RULES)]
    dis_blind = [t for t in blind if lit(t) != gate(t)]
    print(f"  NEGATIVE CONTROL  {len(blind)} label-blind arms, disagreements {len(dis_blind)} -> "
          f"{'PASS' if not dis_blind else 'FAIL'}")

    # SHAM
    sat_gate = lambda t: fam(t, SAT_RULES) is None
    dis_sat = [t for t in atJ if lit(t) != sat_gate(t)]
    dis_lab = [t for t in atJ if lit(t) != gate(t)]
    print(f"  SHAM  satisfaction partition disagrees on {len(dis_sat)}, label partition on "
          f"{len(dis_lab)} -> {'PASS -- specific to the label gate' if len(dis_sat) != len(dis_lab) else 'FAIL'}")

    print(f"\n  arms whose ③ status DIFFERS between literal and gate, over all {len(atJ)}:")
    print(f"  {'arm':<28}{'A2':>9}{'vs ② bar ' + str(BAR2):>18}")
    above = 0
    rows = {}
    for t in sorted(dis_lab, key=lambda x: -atJ[x]["a2"]):
        s = atJ[t]["a2"]; ok = s > BAR2; above += ok
        rows[t] = {"a2": s, "above_bar2": bool(ok), "admitted_by_literal": lit(t),
                   "admitted_by_gate": gate(t)}
        print(f"  {t:<28}{s:>9.4f}{('ABOVE -- candidate' if ok else 'below'):>18}")
    world = "B" if above > 0 else "A"
    p2 = [a for a in cen if cen[a]["ok2"]]
    top9 = max(cen[a]["a2"] for a in p2)
    print(f"\n  {above} of {len(dis_lab)} sit above the ② bar and are admission CANDIDATES "
          f"under the literal, excluded under the gate")
    print(f"  the current 9 ②-passers span {min(cen[a]['a2'] for a in p2):.4f}-{top9:.4f}; "
          f"{sum(1 for t in dis_lab if atJ[t]['a2'] > top9)} of the {len(dis_lab)} outscore all of them")
    print(f"  WORLD {world} -- " + ("the declared literal has a price: top-scoring label-readers"
          if world == "B" else "the defect is free on this population"))
    print(f"  ⚠ BOUND: these are CANDIDACIES. 15 of the 56 carry no ② interval verdict on disk.")

    out = pathlib.Path(__file__).parent / "results/literal_price.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_pop": len(atJ), "bar2_conservative": BAR2,
                               "disagreements": rows, "n_above_bar": above, "world": world,
                               "identification": "PARTIAL -- 15 of 56 lack a ② interval verdict",
                               "positive_control_disagreements_over_41": dis41}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
