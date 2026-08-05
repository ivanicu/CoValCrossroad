#!/usr/bin/env python3
"""
R665 -- `② ∧ ③` is EMPTY at the definition's own literal reading. An OBJECT round.

CHECK #266 ON R664's CLOSING LINE. THE FACT HOLDS, ONE WORD IN THE INFERENCE DOES NOT.
  ✓ "②'s extension at p100 is exactly {greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1}
    and excludes coval_core" -- read from R527's committed curve.
  ⛔ "so the literal reading of 'the best' selects for FITTING." Imprecise, and the imprecision
    matters: `oracle_k4` carries no `fit1` marker -- it is an ORACLE arm, not a fitted one. Fitting
    and oracle access are different mechanisms. The correct statement is that ② at p100 selects
    for arms with PRIVILEGED ACCESS, fitted or oracle, which is a wider and stronger claim.

⭐⭐⭐ AND THE ANSWER TO THE QUESTION R664 ASKED WAS ALREADY ON DISK, IN TWO ARTIFACTS.
   P4's prior-art gate, run before any code: R442 (`the extension under clause three as written`)
   and R440 (`the four clauses on one arm space`) each record clause ③'s removal set, and it is
   the SAME four arms. This is the SECOND CONSECUTIVE ROUND whose object-level answer was already
   committed -- R664's came from R527, 137 rounds old. The apparatus rounds were spent while the
   object questions sat answered on disk.

ESTIMAND        |ext(②) ∩ ext(③)| at the baseline class MAXIMUM (p100), where
                  ext(②) at p100 is read from R527's committed spec curve, and
                  ext(③) is the complement of clause ③'s removal set, read from R442 and R440.
IDENTIFICATION  Exact -- both sets are committed enumerations over the same 42-arm space, and the
                intersection is set arithmetic. NOT identified: whether the coincidence has a
                MECHANISM (why the arms ② ranks highest are exactly the ones ③ removes). The round
                establishes the extension, not the cause.
SCOPE           population : the 42-arm space; the 1,820-subset baseline class
                instrument : two committed artifacts, cross-checked against each other
                             instrument unit = AN ARM
                             claim unit      = AN ARM ADMITTED BY THE DEFINITION
                             EQUAL by construction
                baseline   : the published baseline at percentile 93.74, where the extension is
                             NOT empty -- that contrast is the finding
                regime     : the home release, single object (R645's scope block)
WORLDS          A EMPTY AT p100: the two sets coincide -> read literally, the definition admits
                  NOTHING, and its non-emptiness is purchased entirely by the baseline choice.
                B PARTIAL: they overlap but do not coincide -> the definition survives its literal
                  reading with a smaller extension, and "empties" is too strong.
                C DISJOINT REMOVAL: ③ removes none of ②'s p100 arms -> `② ∧ ③` at p100 is a
                  definition of PRIVILEGED ACCESS, not of core.
KILL            pre-registered, before reading the intersection: if the two artifacts DISAGREE on
                clause ③'s removal set, neither is admissible and the round is UNVERIFIED. A single
                artifact would be one source read twice.
POSITIVE CTRL   R442 and R440 are independent rounds; their clause-③ removal sets must be IDENTICAL.
                Fails at g=0: an empty removal set would make the intersection trivially ②'s own.
NEGATIVE CTRL   ③'s removal set must NOT coincide with ②'s admitted set at the PUBLISHED percentile
                -- otherwise the coincidence is an artefact of ② rather than a fact about p100.
PLACEBO         an arm in neither set must appear in neither.
NOISE FLOOR     n/a -- set arithmetic over committed enumerations. Deterministic.
MULTIPLICITY    2 artifacts x 1 removal set + 8 percentiles from R527 + 3 controls.
ARTIFACT        results/empty_at_p100.json
IMPOSSIBLE      WHY ②'s top-ranked arms are exactly ③'s removals is not decided here. It is the
                obvious next question and it needs the arms' construction, not their scores.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R527 = A24 / "R527_is_clause_two_a_choice" / "results" / "clause2_spec_curve.json"
R442 = A24 / "R442_the_extension_under_clause_three_as_written" / "results" / "r442_extension.json"
R440 = A24 / "R440_the_four_clauses_on_one_arm_space" / "results" / "r440_one_space.json"


def main() -> int:
    for p in (R527, R442, R440):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent. Exit 2, never 0.")
            return 2
    c2 = json.loads(R527.read_text())
    a442 = json.loads(R442.read_text())
    a440 = json.loads(R440.read_text())

    rem442 = set(a442["clause3_impl"])
    rem440 = set(a440["clause3_set"])

    print("─── CONTROLS ───")
    agree = rem442 == rem440
    print(f"  POSITIVE  R442 and R440 are independent rounds; their clause-③ removal sets must be "
          f"IDENTICAL -> {sorted(rem442)} vs {sorted(rem440)} -> "
          f"{'PASS' if agree else '⛔ FAIL — neither is admissible'}")
    print(f"  g=0       an empty removal set would make the intersection trivially ②'s own -> "
          f"|removal| = {len(rem442)} -> {'PASS' if rem442 else '⛔ FAIL'}")
    pub = set(c2["rows"]["published"]["admitted"])
    negok = rem442 != pub
    print(f"  NEGATIVE  ③'s removal set must NOT coincide with ②'s admitted set at the PUBLISHED "
          f"percentile -> published admits {len(pub)}, removal is {len(rem442)}, identical: "
          f"{rem442 == pub} -> {'PASS — the coincidence is specific to p100' if negok else '⛔ FAIL'}")
    plc = "topw_k1"
    plcok = plc not in rem442 and plc not in set(c2["rows"]["p100"]["admitted"])
    print(f"  PLACEBO   an arm in neither set ({plc}) appears in neither -> "
          f"{'PASS' if plcok else '⛔ FAIL'}")
    controls_ok = agree and bool(rem442) and negok and plcok

    p100 = set(c2["rows"]["p100"]["admitted"])
    inter = p100 - rem442
    print(f"\n─── THE DEFINITION'S EXTENSION AT ITS OWN LITERAL READING ───")
    print(f"  ② admits at p100 (the class MAXIMUM) : {sorted(p100)}")
    print(f"  ③ removes                            : {sorted(rem442)}")
    print(f"  ⭐ ② ∧ ③ at p100                       : {sorted(inter) if inter else 'EMPTY'}")
    print(f"\n  and at the PUBLISHED baseline (percentile {c2['published_pct']:.2f}):")
    print(f"  ② admits                             : {sorted(pub)}")
    print(f"  ② ∧ ③                                : {sorted(pub - rem442)}")
    print(f"\n  the whole curve, so the contrast is visible (G4):")
    for k in sorted(c2["rows"]):
        a = set(c2["rows"][k]["admitted"])
        surv = sorted(a - rem442)
        print(f"    {k:>10}  ② admits {len(a)}  ② ∧ ③ admits {len(surv)}  {', '.join(surv)[:58]}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no extension claim is admissible"
    elif not inter:
        world = (f"A EMPTY AT p100 — ②'s four admitted arms at the class MAXIMUM are EXACTLY the "
                 f"four clause ③ removes, so `② ∧ ③` read literally admits NOTHING. ⭐ THE "
                 f"DEFINITION'S NON-EMPTINESS IS PURCHASED ENTIRELY BY THE BASELINE CHOICE: at "
                 f"the published percentile {c2['published_pct']:.2f} it admits "
                 f"{len(pub - rem442)}, and `coval_core` is among them; at p100 it admits 0 and "
                 f"`coval_core` is excluded by ② itself. ⚠ COULD THIS HAVE COME OUT OTHERWISE? "
                 f"Yes — ② admits 4 and ③ removes 4 out of 42 arms; partial overlap was the "
                 f"likelier outcome. This is a measurement, not a derivation.")
    elif inter == p100:
        world = (f"C DISJOINT — ③ removes none of ②'s p100 arms, so `② ∧ ③` at the maximum is a "
                 f"definition of PRIVILEGED ACCESS (fitted or oracle), not of core.")
    else:
        world = (f"B PARTIAL — `② ∧ ③` at p100 admits {sorted(inter)}; the definition survives its "
                 f"literal reading with a smaller extension and 'empties' is too strong.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 2 artifacts x 1 removal set + {len(c2['rows'])} percentiles + 3 "
          f"controls. Whole curve printed.")
    print(f"  ⭐ ZERO NEW COMPUTE: both inputs were committed rounds ago (R527, R442, R440). This "
          f"is the SECOND consecutive round whose object-level answer was already on disk.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "empty_at_p100.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "clause2_p100_admits": sorted(p100), "clause3_removes": sorted(rem442),
        "intersection_at_p100": sorted(inter),
        "published_pct": c2["published_pct"],
        "intersection_at_published": sorted(pub - rem442),
        "curve": {k: {"c2": len(c2["rows"][k]["admitted"]),
                      "c2_and_c3": sorted(set(c2["rows"][k]["admitted"]) - rem442)}
                  for k in sorted(c2["rows"])},
        "sources": [str(R527.relative_to(ROOT)), str(R442.relative_to(ROOT)),
                    str(R440.relative_to(ROOT))],
        "check266": ("R664's NEXT said the literal reading 'selects for FITTING'. Imprecise: "
                     "`oracle_k4` carries no fit1 marker -- it is an ORACLE arm. The correct "
                     "statement is PRIVILEGED ACCESS, fitted or oracle."),
        "impossible": ("WHY ②'s top-ranked arms are exactly ③'s removals is not decided here; it "
                       "needs the arms' construction, not their scores."),
    }, indent=2))
    print(f"\n  wrote {out / 'empty_at_p100.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
