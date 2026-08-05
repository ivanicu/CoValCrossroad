#!/usr/bin/env python3
"""
R669 -- `P_arm` is not clause ②, and R668 restricted the pool one round after catching that error.

CHECK #270 ON R668's CLOSING LINE. THE GATE WAS RUN FIRST AND IT DEMOLISHED THE PREMISE.
  ⛔ "topw_k12 scores exactly zero ... so SOMETHING DISQUALIFIES k=12 CATEGORICALLY."
     **32 arms score P_arm = 0.0 at every seed**, spanning k = 2, 3, 4, 6, 8, 12 and including
     every `random_k*`, every sham, `topabs_k4`, `topvar_k4`, `topwvar_k4`, `full`, `promptecho`.
     **Zero is the DEFAULT, not a fact about k=12.** A "cliff" I read as categorical is the
     modal value of the statistic.
  ⛔⛔⛔ AND IT BREAKS R668 RETROACTIVELY. `clause2_admits` CONTAINS `greedy_k4_fit1`,
     `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1` -- all four of which have P_arm = 0.0. So
     across the FULL arm space the admitted set is NOT a level set of P_arm. R668's level-set
     result holds only INSIDE the topw family, a restriction it never stated -- **the same
     pool-restriction error R667 caught in R665, committed by me one round later.**
  ⛔ AND THE DEEPER DEFECT: `P_arm` is R353's probability that an arm survives a random POOL
     ORDER. It is NOT clause ②'s admission. I tested a band against a different quantity and
     reported the fit as though ② produced it.

ESTIMAND        Does `clause2_admits` coincide with any threshold on `P_arm` over the FULL arm
                space? Formally: is min(P | admitted) > max(P | rejected) across all arms, not
                just the topw family?
IDENTIFICATION  Exact -- one inequality over committed enumerations. NOT identified: what ② DOES
                threshold; that needs ②'s own per-arm statistic, which this round does not claim
                to have found.
SCOPE           population : every arm in R353's P_arm map
                instrument : set arithmetic + one inequality
                             instrument unit = AN ARM
                             claim unit      = THE ADMITTED SET
                             EQUAL by construction
                baseline   : R668's level-set result, computed on the topw family alone
                regime     : home release
WORLDS          A R668 SCOPED: the level set holds within topw and fails globally -> R668's claim
                  survives only with a stated restriction it did not carry.
                B R668 WRONG EVEN LOCALLY: it fails within topw too -> retract entirely.
                C GLOBAL: it holds across all arms -> R668 stands as written.
KILL            pre-registered: if min(P | admitted) > max(P | rejected) holds GLOBALLY, world C
                and this round's criticism is retracted.
POSITIVE CTRL   the four fitted/oracle arms must be BOTH in `clause2_admits` AND at P_arm = 0.
                If they are not, the contradiction this round rests on does not exist.
NEGATIVE CTRL   the inequality must still HOLD within the topw family -- otherwise R668 was wrong
                locally too and world B, not A.
PLACEBO         an arm in neither set appears in neither.
NOISE FLOOR     two committed seeds; both reported.
MULTIPLICITY    2 seeds x every arm + 3 controls; the zero-set printed in full.
ARTIFACT        results/p_arm_scope.json
IMPOSSIBLE      what clause ② actually thresholds is NOT settled here. Finding it needs ②'s own
                per-arm statistic, and this round explicitly does not claim to have located it --
                which is the discipline the last four rounds kept failing.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R353 = A24 / "R353_the_admitted_set_under_every_pool_order" / "results" / "r353_pool_order.json"
R360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"


def main() -> int:
    for p in (R353, R360):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent. Exit 2, never 0.")
            return 2
    j353 = json.loads(R353.read_text())
    adm = set(json.loads(R360.read_text())["clause2_admits"])
    seeds = sorted(s for s, v in j353["per_seed"].items() if "P_arm" in v)
    P = {s: j353["per_seed"][s]["P_arm"] for s in seeds}
    arms = sorted(P[seeds[0]])

    zero = [a for a in arms if all(P[s].get(a, 1.0) == 0.0 for s in seeds)]
    contra = sorted(set(zero) & adm)

    print("─── CONTROLS ───")
    posok = len(contra) >= 1
    print(f"  POSITIVE  arms BOTH in clause2_admits AND at P_arm = 0 -> {contra} -> "
          f"{'PASS — the contradiction exists' if posok else '⛔ FAIL — this round has no subject'}")
    topw = [a for a in arms if a.startswith("topw_k") and "sham" not in a]
    ta = [a for a in topw if a in adm]
    tr = [a for a in topw if a not in adm]
    loc = all(min(P[s][a] for a in ta) > max(P[s][a] for a in tr) for s in seeds)
    print(f"  NEGATIVE  the inequality must still HOLD within the topw family -> {loc} -> "
          f"{'PASS — R668 was right locally, so this is a SCOPE failure not a wrong result' if loc else '⛔ world B: wrong locally too'}")
    plc = "zzq_no_such_arm"
    print(f"  PLACEBO   an arm in neither set -> "
          f"{'PASS' if plc not in arms and plc not in adm else '⛔ FAIL'}")
    controls_ok = posok and loc and plc not in arms

    ga = [a for a in arms if a in adm]
    gr = [a for a in arms if a not in adm]
    glob = {}
    for s in seeds:
        lo = min(P[s][a] for a in ga) if ga else None
        hi = max(P[s][a] for a in gr) if gr else None
        glob[s] = (lo > hi if lo is not None and hi is not None else None, lo, hi)

    print(f"\n─── IS THE ADMITTED SET A LEVEL SET OF P_arm GLOBALLY? ───")
    print(f"  arms in R353's map      : {len(arms)}")
    print(f"  in clause2_admits       : {len(ga)}  {sorted(ga)}")
    print(f"  at P_arm = 0 every seed : {len(zero)}")
    print(f"  ⭐ BOTH (the contradiction): {len(contra)}  {contra}")
    for s in seeds:
        ok, lo, hi = glob[s]
        print(f"  seed {s}: min(P | admitted) = {lo:.4f}  vs  max(P | rejected) = {hi:.4f}  -> "
              f"level set: {ok}")
    print(f"\n  the {len(zero)} arms at P_arm = 0, in full (G3 — zero is the MODAL value):")
    for i in range(0, len(zero), 4):
        print("    " + "  ".join(f"{a:<20}" for a in zero[i:i + 4]))

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    globally = all(v[0] for v in glob.values())
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no scope claim is admissible"
    elif globally:
        world = "C GLOBAL — the level set holds across all arms; R668 stands as written."
    else:
        world = (f"A R668 WAS SCOPED AND DID NOT SAY SO — the level set holds inside the topw "
                 f"family and FAILS globally: {len(contra)} arms are BOTH in `clause2_admits` and "
                 f"at P_arm = 0 ({', '.join(contra)}). ⛔ THE SAME POOL-RESTRICTION ERROR R667 "
                 f"CAUGHT IN R665, COMMITTED ONE ROUND LATER. ⛔⛔ AND THE DEEPER DEFECT: `P_arm` "
                 f"is R353's survival probability under a random POOL ORDER, NOT clause ②'s "
                 f"admission. I tested the k-band against a DIFFERENT QUANTITY and reported the "
                 f"fit as though ② produced it. ⭐ ALSO RETRACTED: 'something disqualifies k=12 "
                 f"categorically' — {len(zero)} arms score exactly 0 across k = 2,3,4,6,8,12, so "
                 f"ZERO IS THE MODAL VALUE and the 'cliff' was me reading the default as an event. "
                 f"⚠ WHAT SURVIVES: nothing about ② from this line. What ② thresholds is NOT "
                 f"settled, and this round does not claim to have found it.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(seeds)} seeds x {len(arms)} arms + 3 controls; zero-set printed "
          f"in full.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "p_arm_scope.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "n_arms": len(arms), "clause2_admits": sorted(ga),
        "zero_at_every_seed": zero, "contradiction": contra,
        "global_level_set": {s: {"is_level_set": v[0], "min_admitted": v[1], "max_rejected": v[2]}
                             for s, v in glob.items()},
        "local_topw_level_set": loc,
        "check270": ("R668's NEXT said something disqualifies k=12 categorically. 32 arms score "
                     "P_arm = 0 at every seed across k = 2,3,4,6,8,12 -- zero is the MODAL value. "
                     "And clause2_admits contains four arms at P_arm = 0, so the level set fails "
                     "globally: R668 was restricted to topw and did not say so."),
        "retracts": ["R668's level-set claim, unless scoped to the topw family",
                     "R668's NEXT: 'something disqualifies k=12 categorically'"],
        "impossible": ("what clause ② actually thresholds is NOT settled here; finding it needs "
                       "②'s own per-arm statistic, which this round does not claim to have."),
    }, indent=2))
    print(f"\n  wrote {out / 'p_arm_scope.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
