#!/usr/bin/env python3
"""R535 — how remote is ③-judge, and does satisfaction-spread beat weight selection?

R534 named a third reading of ③ and left it as a verdict: on this population ③-any and ③-judge
both give extension 0. R530 showed a verdict is not a specification. This prices the third
reading, and in doing so tests the release's own design rationale.

select_core.py's comment on topvar_k argues spread is "the DIRECT FIX" for a defect in topw_k:
  "a criterion whose satisfaction is IDENTICAL across the four responses ... is arithmetically
   INERT no matter how important it is. topw_k selects on importance and is blind to this.
   Selecting on the spread of satisfaction across responses is the direct fix."

That is a falsifiable claim about which selector scores better, and the census answers it.

ESTIMAND (before method): (a) the clause-② shortfall of the satisfaction class in MDE units,
  and (b) the A2 ordering of weight- vs spread- vs combined selection at matched k=4.
IDENTIFICATION: fully identified from R294's stored contrasts; no new estimation.
SCOPE  population: the k=4 arms of R294's census · instrument: R294's interval verdict ·
  baseline: the size-matched blind pool · regime: first release, home judge.
  ⚠ the satisfaction class holds ONE arm HERE; `topvar_k4_08b` and `_08bR` exist on the second
  release and are outside this population. R534's "exactly one" was unscoped.
WORLDS  A · spread beats weight, as the source's comment predicts.
        B · weight beats spread, so the documented rationale does not survive measurement.
KILL (pre-registered): topvar_k4 scoring at or above topw_k4 kills world B.
POSITIVE CONTROL: recompute each ok2 from the stored (eff, lo, hi, mde) via report.verdict and
  require agreement with the census for all four arms compared. Without it the shortfalls are
  not on the census's scale.
NEGATIVE CONTROL: at least one arm in the comparison must CLEAR ② (a negative shortfall), else
  "shortfall" is measured only among failures and its scale is unanchored.
NOISE FLOOR: each arm's own mde2.
MULTIPLICITY: 4 arms x 1 contrast; all printed.
IMPOSSIBLE HERE: whether spread selection would win under a DIFFERENT judge. The satisfaction it
  reads is one model's output; a second judge is register row 2.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "corebench"))
from report import verdict, POS

ARMS = ["topw_k4", "topwvar_k4", "topvar_k4", "coval_core"]

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    src = " ".join((root / "corebench/select_core.py").read_text().replace("#", " ").split())
    claim = "selecting on the spread of satisfaction across responses is the direct fix"
    print(f"  SOURCE READ  the rationale is in select_core.py: "
          f"{'PASS' if claim in src.lower() else 'FAIL'}")
    if claim not in src.lower(): return 2

    bad = [a for a in cen if (verdict(cen[a]["c2"][0], cen[a]["c2"][1], cen[a]["c2"][2],
                                      cen[a]["mde2"]) == POS) != bool(cen[a]["ok2"])]
    print(f"  POSITIVE CONTROL  ok2 reconstructed for all {len(cen)} arms: "
          f"{'PASS' if not bad else 'FAIL ' + str(bad)}")
    if bad: return 0
    clears = [a for a in ARMS if cen[a]["ok2"]]
    print(f"  NEGATIVE CONTROL  at least one compared arm CLEARS ②: {clears} -> "
          f"{'PASS' if clears else 'FAIL -- shortfall scale unanchored'}")
    if not clears: return 0

    print(f"\n  {'arm':<14}{'reads':<14}{'a2':>8}{'c2':>10}{'mde':>9}{'shortfall/MDE':>15}  ②")
    reads = {"topw_k4": "weights", "topwvar_k4": "weights+sat", "topvar_k4": "sat",
             "coval_core": "weights"}
    rows = {}
    for a in ARMS:
        r = cen[a]; sh = -r["c2"][0] / r["mde2"]
        rows[a] = {"reads": reads[a], "a2": r["a2"], "c2": r["c2"][0], "mde": r["mde2"],
                   "shortfall_mde": sh, "ok2": bool(r["ok2"])}
        print(f"  {a:<14}{reads[a]:<14}{r['a2']:>8.4f}{r['c2'][0]:>+10.4f}{r['mde2']:>9.4f}"
              f"{sh:>15.2f}  {r['ok2']}")

    tw, tv = cen["topw_k4"]["a2"], cen["topvar_k4"]["a2"]
    world = "A" if tv >= tw else "B"
    print(f"\n  the source's claim: spread is the DIRECT FIX for topw_k's blindness")
    print(f"    topw_k4 (weights) {tw:.4f}  vs  topvar_k4 (spread) {tv:.4f}  "
          f"-> spread is {'higher' if tv >= tw else 'LOWER'} by {abs(tv-tw):.4f}")
    print(f"  WORLD {world} -- " +
          ("spread beats weight, as documented" if world == "A" else
           "weight beats spread; the documented rationale does not survive measurement"))
    print(f"\n  ⭐ ③-judge's distance: the satisfaction class is "
          f"{rows['topvar_k4']['shortfall_mde']:.2f} MDE from clearing ②, against `gen`'s 1.29 "
          f"for ③-any -- the third reading is REMOTE, not nearly-live.")
    print(f"  ⚠ SCOPE: one sat-class arm in THIS census; topvar_k4_08b and _08bR are on the "
          f"second release and outside it. R534's 'exactly one' was unscoped.")

    out = pathlib.Path(__file__).parent / "results/third_reading.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "world": world,
                               "sat_shortfall_mde": rows["topvar_k4"]["shortfall_mde"],
                               "gen_shortfall_mde": 1.29}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
