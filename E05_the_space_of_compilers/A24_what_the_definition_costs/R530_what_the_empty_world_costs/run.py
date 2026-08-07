#!/usr/bin/env python3
"""R530 — under ③-any the extension is EMPTY. How empty? Convert the verdict into a distance.

R529 forked ③ into ③-rank (extension 5) and ③-any (extension 0). A verdict of "empty" is not a
specification. The register's row 4 asks for "a strong ③-admissible prompt-aware arm" without
saying how strong. This measures it.

ESTIMAND (before method): among ③-any-admissible arms, the smallest shortfall against clause ②,
  in units of that arm's own MDE -- i.e. how far the ③-any world is from being non-empty.
IDENTIFICATION: fully identified from R294's stored contrasts; no new estimation.
SCOPE  population: the 25 ③-any-admissible arms in R294's census · instrument: R294's interval
  verdict · baseline: the size-matched blind pool · regime: first release, home judge.
WORLDS  A · the shortfall is small relative to MDE -- the ③-any world is one modest generator
              away, and "EMPTY" understates how close it is.
        B · the shortfall is large -- ③-any is far from satisfiable and "EMPTY" is the right
              headline.
KILL (pre-registered): a shortfall above 3 MDE on every ③-any arm kills world A.
POSITIVE CONTROL: recompute ok2 from each stored (eff, lo, hi, mde) via report.verdict and
  require it to match the census's own ok2 for ALL arms. If the reconstruction disagrees, my
  reading of WHY an arm fails ② is not the code's and no distance is admissible.
NEGATIVE CONTROL: at least one arm must fail ② by being RESOLVEDLY BELOW rather than unresolved,
  and at least one by being unresolved -- otherwise "shortfall" conflates two different failures
  and the minimum is not interpretable.
NOISE FLOOR: each arm's own mde2, as R294 computed it; distances are reported in those units.
MULTIPLICITY: 25 arms, one contrast each; the closest five printed with their failure MODE.
IMPOSSIBLE HERE: building the arm that would close the gap. That is generation plus judging,
  which the register already prices as row 4 on this site.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "corebench"))
from report import verdict, POS, NEG, UNRES, BELOW

RANK = ("oracle_k", "indep_k", "greedy_k")
WEIGHT = ("topw_k", "topabs_k", "topvar_k", "topwvar_k")

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]

    # POSITIVE CONTROL: reconstruct ok2 from the stored triple
    bad = []
    for a, r in cen.items():
        v = verdict(r["c2"][0], r["c2"][1], r["c2"][2], r["mde2"])
        if (v == POS) != bool(r["ok2"]): bad.append(a)
    print(f"  POSITIVE CONTROL  ok2 reconstructed from stored (eff, lo, hi, mde) for all "
          f"{len(cen)} arms: {len(cen)-len(bad)} match -> {'PASS' if not bad else 'FAIL ' + str(bad)}")
    if bad:
        print("  -> my reading of the verdict is not the code's; UNVERIFIED."); return 0

    modes = {a: verdict(r["c2"][0], r["c2"][1], r["c2"][2], r["mde2"]) for a, r in cen.items()}
    n_below = sum(1 for v in modes.values() if v == NEG)
    n_unres = sum(1 for v in modes.values() if v in (UNRES, BELOW))
    print(f"  NEGATIVE CONTROL  failure modes present: resolvedly-below {n_below}, "
          f"unresolved/below-resolution {n_unres} -> "
          f"{'PASS -- the two failures are distinguishable' if n_below and n_unres else 'FAIL'}")
    if not (n_below and n_unres): return 0

    anyadm = [a for a in cen if not a.startswith(RANK) and not a.startswith(WEIGHT)
              and a != "coval_core"]
    print(f"\n  ③-any-admissible arms: {len(anyadm)}")
    print(f"  {'arm':<18}{'c2':>10}{'mde':>9}{'shortfall/MDE':>15}  mode")
    rows, ranked = {}, sorted(anyadm, key=lambda a: -cen[a]["c2"][0])
    for a in ranked[:5]:
        r = cen[a]; short = -r["c2"][0] / r["mde2"]
        rows[a] = {"c2": r["c2"][0], "mde": r["mde2"], "shortfall_mde": short, "mode": modes[a]}
        print(f"  {a:<18}{r['c2'][0]:>+10.4f}{r['mde2']:>9.4f}{short:>15.2f}  {modes[a]}")

    # the closest arm that is PROMPT-RESPONSIVE (a fixed blind set beating the blind pool is
    # near self-comparison and is not what row 4 asks for)
    responsive = [a for a in anyadm if a in ("gen", "gen_sham") or a.startswith("promptecho")]
    best_resp = max((a for a in responsive if a in cen), key=lambda a: cen[a]["c2"][0], default=None)
    br = cen[best_resp]
    d = -br["c2"][0] / br["mde2"]
    print(f"\n  ⭐ closest PROMPT-RESPONSIVE ③-any arm: {best_resp}")
    print(f"     c2 {br['c2'][0]:+.4f}  CI [{br['c2'][1]:+.4f}, {br['c2'][2]:+.4f}]  "
          f"mde {br['mde2']:.4f}  ->  {d:.2f} MDE short of clearing ②")
    world = "A" if d <= 3.0 else "B"
    print(f"  WORLD {world} -- " +
          (f"the ③-any world is {d:.2f} MDE from non-empty; EMPTY understates how close"
           if world == "A" else "the shortfall is large; EMPTY is the right headline"))
    print(f"  ⚠ `generic` sits at {cen['generic']['c2'][0]:+.4f} but is {modes['generic']} -- a fixed "
          f"blind set against the blind pool is near self-comparison, not what row 4 asks for.")

    out = pathlib.Path(__file__).parent / "results/empty_world_cost.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_any_admissible": len(anyadm), "closest": rows,
                               "best_responsive": best_resp, "shortfall_mde": d,
                               "world": world, "modes_present": {"below": n_below,
                               "unresolved": n_unres}}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
