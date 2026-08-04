"""definition_matches_the_record — every number in DEFINITION.md is re-derived from an artifact.

WHY THIS EXISTS. `DEFINITION.md` states the definition once, in prose, with numbers in it. Prose
does not recompute. The campaign's own history says what happens next: a number stated in a document
drifts from the round that produced it, and the copy is never the one that gets corrected (R351/R352
found seven artifacts whose committed numbers no longer matched their source, and NO page quoted
them). A definition is the worst possible place for that, because it is the one document a reader
takes as settled.

So every quantitative claim in DEFINITION.md is written as a CHECKABLE ASSERTION and re-derived here
from the committed artifact of the round that measured it. If the artifact moves and the prose does
not — or the prose is edited and the artifact does not support it — this fails.

PROXY LEDGER, because this check approximates its property in one direction only:
  PROPERTY   "DEFINITION.md's claims are true of the record"
  PROXY      "the numbers this file knows how to extract match the artifacts"
  IMPLICATION  proxy fails => property fails.  proxy passes =/=> property holds: a claim written in
               prose that is NOT in the assertion table below is unchecked by construction.
  SAFE SIDE  the count of checked-vs-total assertions is PRINTED every run, so the unchecked
             remainder is visible rather than implied. This check may never be read as certifying
             the document.

EMPTY POPULATION: if DEFINITION.md is missing, or no assertion can be evaluated because artifacts
are absent, exit 2 — never 0. A gate that examined nothing has not passed.

POSITIVE CONTROL: the file mutates its own in-memory copy of each claimed value and requires the
comparison to reject it. A checker never shown able to fail is silence.
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"


def art(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def derive():
    """Each entry: label -> (value from the artifact, the round it came from).

    Returns None for a value whose artifact is absent, so the caller can count it as unevaluable
    rather than silently skipping it."""
    out = {}
    a = art("R347_*")
    out["clause1_excludes"] = (len(a["counterexamples"]) if a else None, "R347")
    out["n_arms_r347"] = (a["n_arms"] if a else None, "R347")
    a = art("R360_*")
    if a:
        out["clause2_excludes"] = (len(a["arms"]) - len(a["clause2_admits"]), "R360")
        out["clause3_excludes"] = (len(a["clause2_admits"]) - len(a["clause23_admits"]), "R360")
        out["n_arms_r360"] = (len(a["arms"]), "R360")
        out["sweep_levels"] = (len(a["sweep"]), "R360")
        out["label_users_min"] = (min(len(r["labels"]) for r in a["sweep"]), "R360")
        out["five_at_strongest"] = (len(a["sweep"][-1]["five"]), "R360")
    else:
        for k in ("clause2_excludes", "clause3_excludes", "n_arms_r360", "sweep_levels",
                  "label_users_min", "five_at_strongest"):
            out[k] = (None, "R360")
    a = art("R301_*")
    out["admitted_2B"] = (len(a["admitted_2b"]) if a else None, "R301")
    out["admitted_08B"] = (len(a["admitted_08b"]) if a else None, "R301")
    out["n_arms_r301"] = (a["n_arms"] if a else None, "R301")
    a = art("R331_*")
    out["published_ref_pctile"] = (round(a["r294_reference"]["pctile"], 1) if a else None, "R331")
    a = art("R355_*")
    out["closure_violations_2B"] = (a["totals"]["45"] if a else None, "R355")
    out["closure_k_count"] = (len(a["ks"]) if a else None, "R355")
    a = art("R358_*")
    out["closure_violations_08B"] = (a["totals_08b"]["45"] if a else None, "R358")
    return out


# label -> the regex that must find that number in DEFINITION.md. The pattern is the CLAIM's own
# wording, so an edit that changes the sentence without changing the artifact is caught too.
ASSERTIONS = {
    "clause1_excludes":      r"\*\*(\d+) of 41\*\*",
    "clause2_excludes":      r"\*\*(\d+) of 42\*\*",
    "clause3_excludes":      r"\*\*(\d+) of 42\*\*\s*\|\s*\*\*DERIVED\*\* that it excludes",
    "admitted_2B":           r"\*\*(\d+)\*\* arms admitted at Qwen3\.5-2B-Base",
    "admitted_08B":          r"\*\*(\d+)\*\* at\s*\n?\s*Qwen3\.5-0\.8B-Base",
    "n_arms_r301":           r"on all (\d+) arms",
    "published_ref_pctile":  r"\*\*(\d+\.\d)th percentile\*\*",
    "sweep_levels":          r"Across all \*\*(\d+)\*\* reference levels",
    "label_users_min":       r"never falls below (\d+)",
    "five_at_strongest":     r"published five fall to \*\*(\d+)\*\*",
}


def same(claimed, actual):
    """THE comparison. Factored out so the positive control below exercises THIS code path.

    ⚠ v1's positive control computed `abs((tv + 1.0) - tv) >= 1e-9` inline -- arithmetic that is
    true whatever this function does. Neutering the check to `return True` would have left the
    control passing, which is a control that does not run the instrument it certifies. Caught by
    attacking the gate after building it (P7), which is also where the previous fix's hole was."""
    return abs(float(claimed) - float(actual)) < 1e-9


def read_claims(text):
    got = {}
    for label, pat in ASSERTIONS.items():
        m = re.search(pat, text)
        got[label] = float(m.group(1)) if m else None
    return got


def main() -> int:
    if not DOC.exists():
        print(f"  UNRUNNABLE: {DOC.relative_to(ROOT)} is absent. Exit 2, never 0.")
        return 2
    text = DOC.read_text(encoding="utf-8")
    truth = derive()
    claimed = read_claims(text)

    evaluable = [k for k in ASSERTIONS
                 if truth.get(k, (None,))[0] is not None and claimed.get(k) is not None]
    if not evaluable:
        print("  UNRUNNABLE: not one assertion could be evaluated — either DEFINITION.md carries")
        print("  none of them or every artifact is absent. Exit 2; a gate that examined nothing")
        print("  has not passed.")
        return 2

    print(f"  DEFINITION.md checked against the committed artifacts of the rounds it cites\n")
    print(f"    {'assertion':>24}{'in the doc':>12}{'in the artifact':>17}   round   verdict")
    bad, missing = [], []
    for label in ASSERTIONS:
        tv, rnd = truth.get(label, (None, "?"))
        cv = claimed.get(label)
        if cv is None:
            missing.append(label)
            print(f"    {label:>24}{'NOT FOUND':>12}{str(tv):>17}   {rnd:<7} ⚠ claim absent from doc")
            continue
        if tv is None:
            print(f"    {label:>24}{cv:>12g}{'artifact absent':>17}   {rnd:<7} ⚠ UNEVALUABLE")
            continue
        ok = same(cv, tv)
        if not ok:
            bad.append((label, cv, tv, rnd))
        print(f"    {label:>24}{cv:>12g}{tv:>17}   {rnd:<7} {'ok' if ok else '⛔ MISMATCH'}")

    # ---- positive control: the comparison must reject a wrong value ------------------------------
    probe = evaluable[0]
    tv = float(truth[probe][0])
    caught = (not same(tv + 1.0, tv)) and same(tv, tv)
    print(f"\n  POSITIVE CONTROL  `same()` -- THE comparison this gate rules with, not a restatement")
    print(f"    of it -- is handed `{probe}` = {tv + 1:g} against the artifact's {tv:g} and must")
    print(f"    REJECT, and handed {tv:g} against {tv:g} and must ACCEPT: "
          f"{'caught' if caught else 'MISSED'}  {'PASS' if caught else 'FAIL'}")

    print(f"\n  PROXY LEDGER — {len(evaluable)} of {len(ASSERTIONS)} assertions were evaluable; "
          f"{len(missing)} are not in the document.")
    print(f"    This check is sound in ONE direction: a failure means the document is wrong about")
    print(f"    the record. A pass does NOT certify the document — every prose claim not in the")
    print(f"    assertion table is unchecked BY CONSTRUCTION, and that remainder is why this line")
    print(f"    prints a count instead of a clean bill.")

    if not caught:
        print("\n  FAIL: the comparison could not reject a planted wrong value.")
        return 1
    if bad:
        print(f"\n  FAIL: {len(bad)} claim(s) in DEFINITION.md no longer match their artifact:")
        for label, cv, tv, rnd in bad:
            print(f"    {label}: document says {cv:g}, {rnd} says {tv}")
        print("  Either the document drifted or a round was re-run. Fix the one that is wrong —")
        print("  and note the artifact is the authority, because it recomputes and prose does not.")
        return 1
    if missing:
        print(f"\n  FAIL: {len(missing)} assertion(s) are declared here but absent from the")
        print(f"  document: {missing}. An assertion that cannot be located is not a pass —")
        print(f"  it means the claim was deleted or reworded and this gate went blind to it.")
        return 1
    print(f"\n  PASS: every locatable claim in DEFINITION.md is re-derived from a committed artifact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
