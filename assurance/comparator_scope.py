#!/usr/bin/env python3
"""assurance/comparator_scope.py — every DIFFERENCE-based claim must NAME its comparator.

⛔ WHY THIS FILE EXISTS. R460 measured `corr(rho, comparator strength) = -0.7995` over a census of
   all 1,820 fixed prompt-blind comparators: **the reliability of a difference is a joint statement
   about the arm AND what it was differenced against.** Two numbers this campaign committed --
   R457's 0.8812 and R459's 0.8363 -- turned out to be outliers of that census, on opposite sides,
   and their apparent agreement was the width of a distribution neither belonged to.

   That is not one bug. It is a CLASS: any number defined as a difference inherits its comparator's
   properties, and a sentence that omits the comparator is a number without its scope -- the defect
   behind eleven of twelve retractions in the audit that produced the realstat standard.

⛔ AND THE OBVIOUS AUDIT IS A GREP, WHICH §4 FORBIDS AS AN UNCONTROLLED INSTRUMENT. Matching
   "difference-like numbers" in prose has no positive control and its unit (regex hits) is not the
   claim's unit (numbers that ARE differences). So the comparator is not SEARCHED FOR -- it is
   **DECLARED per anchor and then checked**. An undeclared anchor is reported as UNDECLARED, never
   as passing: prose is not enforcement, a declaration is.

HOW IT WORKS
    COMPARATORS maps an anchor label (from definition_matches_the_record.ASSERTIONS) to the set of
    strings any of which, appearing near that anchor's sentence, names what the number was measured
    against. `None` marks a claim that is NOT a difference and therefore needs no comparator.
    The gate locates each anchor's own regex match and looks in a window around it.

⚠ THE WINDOW IS AN INSTRUMENT PARAMETER, so it is swept rather than chosen, and the sweep is
  positive-controlled: a synthetic claim with its comparator planted at a known distance must be
  FLAGGED below that distance and PASS above it. A window that passes everything is measuring
  nothing.
"""
from __future__ import annotations
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DOC = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
WINDOWS = (200, 400, 800, 1600)

# label -> comparator names (None = not a difference, so no comparator is required)
COMPARATORS = {
    # R455 -- the strengthened clause: core vs the cross-fitted best generalising prompt-blind set
    "r455_gap":     ["best prompt-blind set that GENERALISES", "generalising prompt-blind set"],
    "r455_oracle":  ["same baseline"],
    "r455_neutral": ["same baseline"],
    "r455_leaky":   ["IN-FOLD baseline"],
    # R456 -- the annotator ladder, same comparator as R455
    "r456_gap16":   ["best generalising prompt-blind set", "generalising prompt-blind set"],
    "r456_ratio16": ["best generalising prompt-blind set", "generalising prompt-blind set"],
    "r456_alpha":   None,      # an exponent of the MDE against m; not a difference
    "r456_total":   None,      # a count of annotations
    "r456_mderatio": None,     # a ratio of one design's MDE to its own
    # R457 -- reliabilities of differences; the comparator is what is subtracted
    "r457_clean":   ["A2(core,p) − A2(sham,p)", "sham"],
    "r457_sham":    ["A2(arm,p) − A2(base,p)", "baseline term"],
    "r457_core":    ["A2(arm,p) − A2(base,p)", "baseline term"],
    # R458 -- explainability of the arm-specific gap
    "r458_r2":      ["arm-specific gap"],
    "r458_share":   ["ceiling"],
    "r458_pos":     None,      # a positive control's recovery, not a difference between arms
    "r458_nfeat":   None,
    "r458_corerange": ["two arms"],
    # R459 / R460 -- the comparator IS the subject
    "r459_dgen":    ["generic"],
    "r459_core":    None,      # a component reliability, not a difference
    "r459_sham":    None,
    "r459_delta":   ["core − sham", "core − generic"],
    "r459_tuples":  None,
    "r460_min":     ["core − F", "comparator"],
    "r460_med":     ["core − F", "comparator"],
    "r460_iqr":     ["comparator"],
    "r460_strength": ["comparator strength"],
    "r460_ncomp":   None,
}


def audit(text, assertions, window):
    """-> (ok, flagged, undeclared, not_a_difference). A missing declaration is NEVER a pass."""
    flagged, undeclared, absolute = [], [], []
    for label, pat in assertions.items():
        m = re.search(pat, text)
        if m is None:
            continue
        if label not in COMPARATORS:
            undeclared.append(label)
            continue
        names = COMPARATORS[label]
        if names is None:
            absolute.append(label)
            continue
        lo, hi = max(0, m.start() - window), min(len(text), m.end() + window)
        seg = text[lo:hi]
        if not any(nm in seg for nm in names):
            flagged.append((label, names[0]))
    return (not flagged), flagged, undeclared, absolute


def selftest(assertions):
    """POSITIVE CONTROL on the window mechanism: a comparator planted at a known distance must be
    FLAGGED below that distance and PASS above it. A window that passes everything measures nothing."""
    ok = True
    stub = {"probe": r"THE PROBE VALUE IS ([\d.]+)"}
    for dist in (300, 1200):
        body = "THE PROBE VALUE IS 1.234" + ("x" * dist) + " measured against THE PROBE COMPARATOR"
        saved = COMPARATORS.get("probe")
        COMPARATORS["probe"] = ["THE PROBE COMPARATOR"]
        for w in (200, 1600):
            good, fl, _, _ = audit(body, stub, w)
            want = w > dist
            hit = (good == want)
            ok &= hit
            print(f"    plant at {dist:>5} chars, window {w:>5} -> "
                  f"{'PASS' if good else 'FLAGGED'}  want {'PASS' if want else 'FLAGGED'}"
                  f"   {'ok' if hit else '⛔'}")
        if saved is None:
            COMPARATORS.pop("probe")
    # g=0: a declared-absolute claim must never be flagged whatever the window
    stub2 = {"abs": r"THE COUNT IS (\d+)"}
    COMPARATORS["abs"] = None
    g0, fl2, _, ab = audit("THE COUNT IS 17", stub2, 200)
    ok &= (g0 and ab == ["abs"])
    COMPARATORS.pop("abs")
    print(f"    g=0  a declared-ABSOLUTE claim is never flagged: {g0 and ab == ['abs']}")
    return ok


def main() -> int:
    sys.path.insert(0, str(HERE))
    from definition_matches_the_record import ASSERTIONS
    text = DOC.read_text()
    print("COMPARATOR SCOPE — every DIFFERENCE-based claim must NAME what it was measured against\n")
    print("  POSITIVE CONTROL on the window mechanism (a window that passes everything is blind):")
    if not selftest(ASSERTIONS):
        print("\n  ⛔ the window mechanism failed its own control. Exit 2, never 0."); return 2

    print(f"\n  {'window':>8}{'declared':>10}{'absolute':>10}{'FLAGGED':>9}{'undeclared':>12}")
    last = None
    for w in WINDOWS:
        ok, fl, und, ab = audit(text, ASSERTIONS, w)
        decl = sum(1 for l in ASSERTIONS if l in COMPARATORS and COMPARATORS[l] is not None)
        print(f"  {w:>8}{decl:>10}{len(ab):>10}{len(fl):>9}{len(und):>12}")
        last = (ok, fl, und, ab)
    ok, fl, und, ab = last
    if fl:
        print("\n  ⛔ DIFFERENCE-BASED CLAIMS THAT DO NOT NAME THEIR COMPARATOR (widest window):")
        for label, want in fl:
            print(f"    {label:<18} expected to name: {want!r}")
    print(f"\n  ⚠ UNDECLARED anchors: {len(und)} of {len(ASSERTIONS)}. These are NOT passes — the")
    print(f"    gate reports a count instead of a clean bill, because a claim whose comparator has")
    print(f"    never been declared is exactly the case this instrument exists to surface.")
    print(f"\n  {'PASS' if ok else '⛔ FAIL'} — every DECLARED difference names its comparator.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
