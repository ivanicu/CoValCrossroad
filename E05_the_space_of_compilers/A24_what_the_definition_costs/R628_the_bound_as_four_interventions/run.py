#!/usr/bin/env python3
"""
R628 -- the bound, written as four interventions with predicted outcomes

CHECK #227 CAUGHT THE ELEVENTH UNCOMPUTED UNIVERSAL, FALSE IN THE PESSIMISTIC DIRECTION.
  ⛔ "EVERY mechanical route to provenance has now failed" -- false, and the falsifier is my own
     R621: an exact-string intervention DID detect a real defect, and derive() genuinely re-derives
     119 values and would break on artifact drift. What failed is narrower and sharper:
     ROUTES THAT INFER PROVENANCE FROM VALUE COINCIDENCE. Routes that check an EXACT, AUTHOR-
     DECLARED BINDING work. Had that universal reached the register it would have understated the
     suite in the pessimistic direction -- the mirror of the usual error, and the second instance
     this arc of a closing line manufacturing a fault.

⭐ SO THE BOUND IS NOT "provenance cannot be mechanised". It is: PROVENANCE CANNOT BE INFERRED, IT
   MUST BE DECLARED AND THEN CHECKED. That is a different sentence with a different consequence for
   a next site, and it is what gets written into the register.

⚠ CLASSIFICATION: PRODUCTION -- it converts measured findings into the register. A register entry is
   a CLAIM ABOUT AN INSTRUMENT, so it is written as a PREDICTION and tested, not asserted. The
   register is committed only if all four predictions hold.

ESTIMAND        for each of four register lines, whether the suite's behaviour under a targeted
                intervention matches the line's prediction.
IDENTIFICATION  Exact and interventional -- the same method R621 used, applied to the register
                itself. ⚠ It validates the lines AS WRITTEN, not the completeness of the register:
                a defect class no line names is invisible here, and the register says so.
SCOPE           population : the four register lines
                instrument : the six committed gates' exit statuses on a mutated working tree
                             instrument unit = A GATE'S EXIT STATUS UNDER ONE MUTATION
                             claim unit      = A REGISTER LINE. NOT equal -- a line generalises
                             over a defect CLASS and each intervention samples one member.
                baseline   : the unmutated tree, all six passing
                regime     : this repository at this sha
WORLDS          A THE REGISTER IS ACCURATE: all four predictions hold; the lines can be written.
                B A LINE IS WRONG: any mismatch -> that line is not written, and the mismatch is
                  the finding, because a register that overstates OR understates is equally a
                  false specification for the next site.
KILL            pre-registered: any prediction failing -> that line is withheld and reported as a
                mismatch. All four must hold for the register block to be committed.
POSITIVE CTRL   line 1's intervention must be CAUGHT -- if the suite catches nothing, every "not
                caught" below is silence rather than a measurement.
NEGATIVE CTRL   the tree must return to all-pass after every intervention.
PLACEBO         a no-op edit (a trailing blank line) must change no verdict.
SEEDS           n/a, deterministic.
MULTIPLICITY    4 interventions x 6 gates = 24 cells + 3 controls. All reported.
ARTIFACT        results/the_bound.json
IMPOSSIBLE      the register's COMPLETENESS is not testable here -- a defect class no line names is
                invisible to a test derived from the lines. Stated in the register itself rather
                than left for a reader to discover.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
GATES = ["statement_provenance", "residue_debt", "retraction_reaches_the_artifact",
         "definition_matches_the_record", "next_line_quantifiers_are_computed",
         "every_round_is_committed"]
S, D = E05 / "STATEMENT.md", E05 / "DEFINITION.md"


def suite():
    return {g: subprocess.run([sys.executable, str(ROOT / "assurance" / f"{g}.py")], cwd=ROOT,
            capture_output=True, text=True, timeout=300).returncode for g in GATES}


def main():
    base = suite()
    if any(v for v in base.values()):
        print("UNRUNNABLE: the tree does not start clean. Exit 2, never 0."); return 2
    print("  baseline: all six gates pass\n")

    os_, od = S.read_text(), D.read_text()
    V = "0." + "7" + "0" + "4" + "2"          # runtime-assembled; never persisted as a value
    LINES = [
        ("a value cited to a round whose verdict is UNVERIFIED",
         "CAUGHT",
         lambda: S.write_text(os_ + f"\n\nThe value {V} (R466) is established here.\n")),
        ("a value LAUNDERED — written into DEFINITION.md first, then cited to a settled round",
         "NOT CAUGHT",
         lambda: (D.write_text(od + f"\n\n## R620 · a value\n\nThe measured value is {V}.\n"),
                  S.write_text(os_ + f"\n\nThe value {V} (R620) is established here.\n"))),
        ("a REAL artifact value asserted as a DIFFERENT quantity in a section that cites its round",
         "NOT CAUGHT",
         lambda: D.write_text(od + "\n\n## R624 · a value\n\nThe pass rate at document scope is "
                              "0.9110.\n")),
        ("a DRIFTED value for a label the gate re-derives",
         "CAUGHT",
         lambda: D.write_text(od.replace("0.5451", "0.5452", 1))),
    ]

    print("─── FOUR REGISTER LINES, EACH AN INTERVENTION WITH A PREDICTION ───")
    rows, ok = [], True
    for i, (desc, pred, mutate) in enumerate(LINES, 1):
        try:
            mutate()
            after = suite()
        finally:
            S.write_text(os_); D.write_text(od)
        flips = [g for g in GATES if after[g] != base[g]]
        got = "CAUGHT" if flips else "NOT CAUGHT"
        agree = got == pred
        ok &= agree
        rows.append({"line": desc, "predicted": pred, "observed": got, "gates": flips,
                     "agrees": agree})
        print(f"  {i}. {desc}")
        print(f"     predicted {pred:<10} observed {got:<10} "
              f"{'✓' if agree else '⛔ MISMATCH'}   {', '.join(flips) if flips else ''}")
        if any(v for v in suite().values()):
            print("     ⛔ NEGATIVE CONTROL: tree did not return to all-pass"); ok = False

    print(f"\n─── CONTROLS ───")
    pos = rows[0]["observed"] == "CAUGHT"
    print(f"  POSITIVE  line 1 is caught -> "
          f"{'PASS — a NOT CAUGHT below is a measurement, not silence' if pos else '⛔ FAIL'}")
    try:
        S.write_text(os_ + "\n")
        plc = [g for g in GATES if suite()[g] != base[g]]
    finally:
        S.write_text(os_)
    print(f"  PLACEBO   a no-op trailing newline -> {len(plc)} verdict change(s) -> "
          f"{'PASS' if not plc else '⛔ FAIL'}")
    print(f"  NEGATIVE  the tree returns to all-pass after every intervention -> "
          f"{'PASS' if all(v == 0 for v in suite().values()) else '⛔ FAIL'}")
    controls_ok = pos and not plc and all(v == 0 for v in suite().values())

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; the register is not written"
    elif ok:
        world = ("A THE REGISTER IS ACCURATE — all four predictions hold, so the bound can be "
                 "written: PROVENANCE CANNOT BE INFERRED, IT MUST BE DECLARED AND THEN CHECKED. "
                 "The suite verifies an author-declared binding; it does not verify that a number "
                 "was measured.")
    else:
        bad = [r["line"] for r in rows if not r["agrees"]]
        world = (f"B A LINE IS WRONG — {len(bad)} of 4 predictions failed, so those lines are "
                 f"WITHHELD: {bad}. A register that understates is as false a specification as one "
                 f"that overstates.")
    print(f"  {world}")
    print(f"\n  ⚠ COMPLETENESS IS NOT TESTABLE HERE: a defect class no line names is invisible to a "
          f"test derived from the lines. That limit belongs IN the register, not in a footnote.")
    print(f"  MULTIPLICITY: 4 interventions x {len(GATES)} gates = {4*len(GATES)} cells + 3 controls.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "the_bound.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "all_predictions_hold": ok, "lines": rows,
        "check227": ("'every mechanical route to provenance has failed' is false -- R621's exact-"
                     "string intervention worked and derive() re-derives 119 values. What failed "
                     "is routes that INFER provenance from value coincidence."),
        "impossible": "the register's completeness is not testable from the register's own lines",
    }, indent=2))
    print(f"\n  wrote {OUT / 'the_bound.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
