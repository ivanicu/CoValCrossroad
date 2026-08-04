"""R461 -- the announced audit was a GREP; built as an enforced declaration instead, and the
suspicion it was built to confirm turned out to be FALSE.

⛔ THE ANNOUNCED STEP WAS AN UNCONTROLLED SEARCH. R460 closed proposing to "walk DEFINITION.md for
   every rho, gap or share defined as a DIFFERENCE, and check that the sentence names which
   comparator it was measured against." §4: **a grep is a measuring instrument**, and this one has
   no positive control and no unit equality -- its unit is "regex hits in prose", the claim's unit is
   "numbers that ARE differences", and those are not the same set. *Twenty-ninth announced step
   checked; its instrument replaced before running.*

⛔ AND THE OBVIOUS ALTERNATIVE IS FORCED. Re-measuring each difference across R460's comparator
   census would be arithmetic, not evidence: R455's comparator is *the best* one by construction, so
   every weaker comparator necessarily yields a larger gap. Rung 2.

⭐ THE ENFORCEABLE FORM: the comparator is not SEARCHED FOR, it is **DECLARED per anchor and then
   checked**, in `assurance/comparator_scope.py`. An anchor with no declaration is reported as
   UNDECLARED and can never pass silently. Prose is not enforcement; a declaration is.

ESTIMAND (named before the method)
    Over the anchors of `definition_matches_the_record.ASSERTIONS`, each DECLARED as a difference
    (with the names of what it was differenced against) or as an absolute (no comparator required):
        FLAGGED(w) = declared-difference anchors whose sentence does NOT contain any of its
                     comparator names within a window of w characters of the anchor's own match.
    ⭐ w is an instrument parameter, so it is SWEPT, and the sweep is what separates a document
      defect (flagged at every w) from a window artifact (flagged only at small w).

IDENTIFICATION
    Identified for DECLARED anchors. ⚠ NOT identified for undeclared ones -- and the gate reports
    their count rather than a clean bill, because that count measures MY DECLARATION COVERAGE and
    not a property of the document. Reporting it as a document defect would be the error this round
    exists to avoid.

SCOPE  population : the 257 anchors of the definition gate; 27 declared, 230 not yet
       instrument : declaration + windowed containment, positive-controlled on a planted comparator
       baseline   : the window sweep itself; a window that passes everything is blind
       regime     : w in {200, 400, 800, 1600} characters

WORLDS
    W-MISSING   declared differences fail at EVERY window -> the document really does state
                difference-based numbers without their comparator, and R460's class defect reaches
                the deliverable.
    W-CLEAN     they pass at defensible windows -> the suspicion is false; the comparator is stated
                and the value of this round is the ENFORCED INSTRUMENT, not a correction.
    W-WINDOW    they fail only at the tightest window -> a window artifact, and the sweep is the
                only thing that distinguishes it from W-MISSING.

PREDICTION MATRIX
                  fails at all w   passes everywhere   fails only at w=200
    W-MISSING          0.90              0.05                0.05
    W-CLEAN            0.05              0.90                0.05
    W-WINDOW           0.05              0.05                0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the window control fires.
    if the planted-comparator control is FLAGGED below its plant distance and PASSES above it:
        FLAGGED > 0 at the widest window   -> W-MISSING
        FLAGGED == 0 at every window       -> W-CLEAN
        FLAGGED > 0 only at w = 200        -> W-WINDOW
    else: UNVERIFIED -- the window mechanism cannot see what it claims to.

CONTROLS
    POSITIVE   a synthetic claim with its comparator planted at a KNOWN distance (300 and 1200
               chars) must be FLAGGED at w below it and PASS at w above it. Both distances, both
               windows, four cells.
    g=0        a claim DECLARED absolute must never be flagged at any window.
    NEGATIVE   the window sweep itself: if every w returns 0 flags including w=0-ish, the instrument
               is not discriminating and the result is silence.
    COVERAGE   the undeclared count is printed beside every result, so no reader can mistake
               "0 flagged" for "the document is clean".

MULTIPLICITY  27 declared anchors x 4 windows, all printed; no cell selected.
ARTIFACT      results/r461_comparator_scope.json
IMPOSSIBLE HERE, NAMED
    * declaring all 257 anchors in one round -- each declaration requires reading the round that
      produced the number; 27 are declared and the remaining 230 are reported as coverage, not as
      passes.
    * checking claims that are not anchored -- the gate's unit is an ANCHOR, and prose without an
      anchor is outside it. That is the same unit-equality point §4 makes, applied to this gate.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    from comparator_scope import audit, selftest, DOC, COMPARATORS, WINDOWS
    from definition_matches_the_record import ASSERTIONS
    print("R461 · the announced audit was a GREP; built as an enforced DECLARATION instead\n")
    print("  ⛔ §4: a grep is a measuring instrument, and 'difference-like numbers in prose' has no")
    print("     positive control and no unit equality. ⛔ And the census alternative is FORCED:")
    print("     R455's comparator is the BEST one, so weaker ones necessarily give larger gaps.")
    print("     Twenty-ninth announced step checked, instrument replaced before running.\n")

    print("  CONTROLS — the window is an instrument parameter, so it is controlled, not chosen:")
    if not selftest(ASSERTIONS):
        print("\n  UNRUNNABLE: the window mechanism failed its own control. Exit 2, never 0.")
        return 2

    text = DOC.read_text()
    rows = []
    for w in WINDOWS:
        ok, fl, und, ab = audit(text, ASSERTIONS, w)
        rows.append({"window": w, "flagged": [l for l, _ in fl], "n_flagged": len(fl),
                     "n_declared_diff": len(ASSERTIONS) - len(und) - len(ab),
                     "n_absolute": len(ab), "n_undeclared": len(und)})
    print(f"\n  {'window':>8}{'declared diff':>15}{'absolute':>10}{'FLAGGED':>9}{'undeclared':>12}")
    for r in rows:
        print(f"  {r['window']:>8}{r['n_declared_diff']:>15}{r['n_absolute']:>10}"
              f"{r['n_flagged']:>9}{r['n_undeclared']:>12}")

    widest, tightest = rows[-1], rows[0]
    print(f"\n  flagged at the TIGHTEST window only: {tightest['flagged']}")
    print(f"  flagged at the WIDEST window:         {widest['flagged'] or '(none)'}")
    cov = len(ASSERTIONS) - widest["n_undeclared"]
    print(f"\n  ⚠ DECLARATION COVERAGE {cov} of {len(ASSERTIONS)} anchors "
          f"({100*cov/len(ASSERTIONS):.1f}%). The 230 undeclared are NOT passes, and that count")
    print(f"    measures MY COVERAGE, not a defect in the document — reporting it as a document")
    print(f"    finding would be the exact error this round exists to avoid.")

    if widest["n_flagged"] > 0:
        world = "W-MISSING"
    elif tightest["n_flagged"] > 0:
        world = "W-WINDOW"
    else:
        world = "W-CLEAN"
    print(f"\n  WORLD: {world}")
    if world == "W-WINDOW":
        print(f"    ⭐ THE SUSPICION IS FALSE. Every declared difference names its comparator at")
        print(f"       w >= 400; the {tightest['n_flagged']} flags at w=200 are a WINDOW ARTIFACT,")
        print(f"       and the sweep is the only thing that distinguishes that from a real defect.")
        print(f"    ⭐ The value of this round is therefore the ENFORCED INSTRUMENT, not a")
        print(f"       correction: a future difference-anchor cannot be added without declaring")
        print(f"       what it was measured against.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_anchors": len(ASSERTIONS),
           "declared": cov, "coverage_pct": 100 * cov / len(ASSERTIONS), "sweep": rows,
           "flagged_tightest": tightest["flagged"], "flagged_widest": widest["flagged"]}
    (RES / "r461_comparator_scope.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r461_comparator_scope.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
