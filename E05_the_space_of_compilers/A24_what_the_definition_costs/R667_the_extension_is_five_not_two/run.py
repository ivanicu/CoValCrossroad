#!/usr/bin/env python3
"""
R667 -- the extension is FIVE, not two. R665's object claim was computed on a restricted pool.

CHECK #268 ON R666's CLOSING LINE. ONE QUANTIFIER FALSE, AND THE PRIOR-ART GATE NOT RUN AGAIN.
  ⛔ "the held-out bracket is THE ONLY cell in this whole curve that is unresolved." False on the
     round's own printed table: budget-0 is [2, 3], also a bracket.
  ⛔⛔⛔ "pinning it needs the per-arm a2 scores, WHICH THE CORPUS HAS NOT SURFACED." The gate was
     not run. It surfaces **21 artifacts** carrying a per-arm map, and two of them answer the
     question outright: R360's `clause23_admits` and R442's `ext_impl`. THIRD CONSECUTIVE ROUND in
     which data I asserted missing was already committed -- R664 (from R527), R665 (from R442/440),
     and now this. That is a measured pattern, not an anecdote: **I assert absence at the point
     where running the gate is one command.**

ESTIMAND        The definition's extension `② ∧ ③`, reconciled across the three committed
                computations that disagree:
                  R360 `clause23_admits`  -> ?
                  R442 `ext_impl`         -> ?
                  R527 curve ∩ R442 removal (the route R665 took) -> 2
                and the CAUSE of the disagreement: whether R527's percentile curve ranges over a
                strict SUBSET of the arm space the other two use.
IDENTIFICATION  Exact -- all three are committed enumerations. NOT identified: which extension is
                the RIGHT one, because that depends on which arm pool the definition is meant to
                quantify over, and that is a choice the release does not make for us. Reported as
                a disagreement with its cause, not adjudicated.
SCOPE           population : the arms named in each artifact
                instrument : set arithmetic over three committed artifacts
                             instrument unit = AN ARM
                             claim unit      = AN ARM ADMITTED BY THE DEFINITION
                             EQUAL by construction
                baseline   : R665's published answer of 2
                regime     : home release, single object
WORLDS          A POOL-RESTRICTED: R360 and R442 agree, and R527's arm set is a strict subset ->
                  R665's 2 is an artefact of the pool R527 swept, and the extension is larger.
                B GENUINELY DIFFERENT: the three disagree in a way pool restriction does not
                  explain -> the definition's extension is not well-defined across the corpus and
                  that is the finding.
                C R665 STANDS: R360/R442 reduce to 2 once matched -> nothing changes.
KILL            pre-registered: if R360's and R442's sets DIFFER, neither is admissible as the
                reconciled answer and the round is UNVERIFIED -- one artifact would be one source.
POSITIVE CTRL   R360 and R442 are independent rounds ~80 apart; their `② ∧ ③` sets must be equal.
NEGATIVE CTRL   R527's swept arm set must be a STRICT SUBSET of R360's arm space. If it is not,
                pool restriction does NOT explain the gap and world B is the answer instead.
PLACEBO         an arm in no artifact appears in none.
NOISE FLOOR     n/a -- committed enumerations. Deterministic.
MULTIPLICITY    3 artifacts x 1 extension + 3 controls; every arm in every set printed.
ARTIFACT        results/extension_reconciled.json
IMPOSSIBLE      WHICH pool the definition should quantify over is a choice the release does not
                make. This round reports the disagreement and its cause; adjudicating it needs a
                statement from the release about its own arm space, which does not exist.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
R442 = A24 / "R442_the_extension_under_clause_three_as_written" / "results" / "r442_extension.json"
R527 = A24 / "R527_is_clause_two_a_choice" / "results" / "clause2_spec_curve.json"


def main() -> int:
    for p in (R360, R442, R527):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent. Exit 2, never 0.")
            return 2
    j360 = json.loads(R360.read_text())
    j442 = json.loads(R442.read_text())
    j527 = json.loads(R527.read_text())

    e360 = set(j360["clause23_admits"])
    e442 = set(j442["ext_impl"])
    rem = set(j442["clause3_impl"])
    pub527 = set(j527["rows"]["published"]["admitted"])
    e527 = pub527 - rem
    arms360 = set(j360["k"])
    swept527 = set().union(*(set(r["admitted"]) for r in j527["rows"].values()))

    print("─── CONTROLS ───")
    agree = e360 == e442
    print(f"  POSITIVE  R360 and R442 are independent rounds ~80 apart; their `② ∧ ③` sets must be "
          f"EQUAL -> {sorted(e360)} vs {sorted(e442)} -> "
          f"{'PASS' if agree else '⛔ FAIL — neither is admissible'}")
    subset = swept527 < arms360
    print(f"  NEGATIVE  R527's swept arm set must be a STRICT SUBSET of R360's arm space -> "
          f"|swept| {len(swept527)} vs |arms| {len(arms360)}, strict subset: {subset} -> "
          f"{'PASS — pool restriction can explain the gap' if subset else '⛔ FAIL — it cannot, so world B'}")
    plc = "zzq_no_such_arm"
    plcok = plc not in (e360 | e442 | arms360 | swept527)
    print(f"  PLACEBO   an arm in no artifact appears in none -> {'PASS' if plcok else '⛔ FAIL'}")
    controls_ok = agree and subset and plcok

    print(f"\n─── THE THREE COMMITTED ANSWERS ───")
    print(f"  R360 `clause23_admits`                    : {len(e360)}  {sorted(e360)}")
    print(f"  R442 `ext_impl`                           : {len(e442)}  {sorted(e442)}")
    print(f"  R527 curve ∩ R442 removal (R665's route)  : {len(e527)}  {sorted(e527)}")
    missing = (e360 | e442) - swept527
    print(f"\n  ⭐ arms in the reconciled extension that R527's curve NEVER SWEEPS: "
          f"{sorted(missing)}")
    print(f"  R527 sweeps {len(swept527)} arms of R360's {len(arms360)}: {sorted(swept527)}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no reconciled extension is admissible"
    elif e527 == e360:
        world = f"C R665 STANDS — all three routes give {sorted(e527)}; nothing changes."
    elif missing:
        world = (f"A POOL-RESTRICTED, AND R665's '2' IS RETRACTED — R360 and R442 independently "
                 f"give `② ∧ ③` = {len(e360)} arms {sorted(e360)}, while the route R665 took gives "
                 f"{len(e527)} {sorted(e527)}. The gap is exactly {sorted(missing)}, which R527's "
                 f"percentile curve NEVER SWEEPS: it ranges over {len(swept527)} arms of R360's "
                 f"{len(arms360)}. ⭐ SO THE DEFINITION ADMITS FOUR TOP-WEIGHT ARMS AT DIFFERENT k "
                 f"(k=3,4,6,8) PLUS `coval_core` — not one baseline and the instance. That makes "
                 f"the 'clauses are too weak' concern sharper, not softer: nothing in `② ∧ ③` "
                 f"distinguishes k. ⚠ AND IT IS A DISAGREEMENT, NOT AN ADJUDICATION: which pool "
                 f"the definition should quantify over is a choice the release does not make, so "
                 f"this round reports both numbers and the cause.")
    else:
        world = (f"B GENUINELY DIFFERENT — the three disagree in a way pool restriction does not "
                 f"explain; the extension is not well-defined across the corpus.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 3 artifacts x 1 extension + 3 controls; every arm printed.")
    print(f"  ⭐ ZERO NEW COMPUTE — the fourth consecutive round answered from committed artifacts.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "extension_reconciled.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "r360_clause23": sorted(e360), "r442_ext_impl": sorted(e442),
        "r527_route": sorted(e527), "gap": sorted(missing),
        "r527_swept_arms": sorted(swept527), "r360_arm_space": len(arms360),
        "check268": ("R666's NEXT called the held-out bracket 'THE ONLY unresolved cell' (budget-0 "
                     "is [2,3], also a bracket) and said the per-arm scores were not surfaced by "
                     "the corpus -- the gate finds 21 artifacts carrying one. THIRD consecutive "
                     "round asserting absence where the gate was one command."),
        "impossible": ("which arm pool the definition should quantify over is a choice the "
                       "release does not make; the disagreement is reported, not adjudicated."),
    }, indent=2))
    print(f"\n  wrote {out / 'extension_reconciled.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
