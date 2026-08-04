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
    a = art("R370_*")
    if a:
        out["pool_contrast"] = (round(a["results"]["pool|exact"]["contrast"], 4), "R370")
        out["pool_mde"] = (round(a["results"]["pool|exact"]["mde"], 4), "R370")
    else:
        out["pool_contrast"] = (None, "R370"); out["pool_mde"] = (None, "R370")
    a = art("R369_*")
    if a:
        out["dfloor_exact"] = (round(a["decomposition"]["exact"]["d_floor"], 4), "R369")
        out["dcore_exact"] = (round(a["decomposition"]["exact"]["d_core"], 4), "R369")
    else:
        out["dfloor_exact"] = (None, "R369"); out["dcore_exact"] = (None, "R369")
    a = art("R368_*")
    if a:
        out["transport_exact"] = (round(a["matched_contrast"]["exact"], 4), "R368")
        out["transport_mde"] = (round(a["mde"]["exact"], 4), "R368")
    else:
        out["transport_exact"] = (None, "R368"); out["transport_mde"] = (None, "R368")
    a = art("R367_*")
    if a:
        out["rule_b_2B"] = (round(a["rule_b"]["mean_2B"], 4), "R367")
        out["rule_b_08B"] = (round(a["rule_b"]["mean_08B"], 4), "R367")
        out["rule_b_n"] = (a["n_external"], "R367")
    else:
        for k in ("rule_b_2B", "rule_b_08B", "rule_b_n"):
            out[k] = (None, "R367")
    a = art("R366_*")
    if a:
        out["survive_n"] = (a["n_claims"], "R366")
        out["p_form"] = (round(a["table_form"]["p"], 4), "R366")
        out["p_null"] = (round(a["table_null"]["p"], 4), "R366")
        out["p_perfect"] = (round(a["controls"]["positive_p"], 4), "R366")
    else:
        for k in ("survive_n", "p_form", "p_null", "p_perfect"):
            out[k] = (None, "R366")
    a = art("R365_*")
    if a:
        out["mde_ratio_08B"] = (round(a["delta"]["0.8B"][1] / a["delta"]["2B"][1], 2), "R365")
        out["channel_mde_08B"] = (round(a["delta"]["0.8B"][1], 4), "R365")
    else:
        out["mde_ratio_08B"] = (None, "R365"); out["channel_mde_08B"] = (None, "R365")
    a = art("R364_*")
    if a:
        out["channel_mde"] = (round(a["delta_mde"], 4), "R364")
        out["plant_detected"] = (round(a["positive"]["0.5"][0], 4), "R364")
    else:
        out["channel_mde"] = (None, "R364"); out["plant_detected"] = (None, "R364")
    a = art("R363_*")
    if a:
        out["overlap_pct"] = (round(a["same"]["mean"] * 100, 1), "R363")
        out["overlap_ratio"] = (round(a["ratio"]), "R363")
        out["n_annotators"] = (a["n_annotators"], "R363")
        out["full_overlap_prompts"] = (a["all_overlap_prompts"], "R363")
    else:
        for k in ("overlap_pct", "overlap_ratio", "n_annotators", "full_overlap_prompts"):
            out[k] = (None, "R363")
    a = art("R362_*")
    if a:
        out["neg_sizes_08B"] = (sum(1 for k in a["ks"]
                                    if a["margins"][f"0.8B|{k}"][0] < 0), "R362")
        out["sign_flips"] = (len(a["sign_flips"]), "R362")
    else:
        out["neg_sizes_08B"] = (None, "R362"); out["sign_flips"] = (None, "R362")
    a = art("R361_*")
    out["labels_min_08B"] = (a["min_labels"]["0.8B"] if a else None, "R361")
    out["rank_p_2B"] = (round(a["rank_null"]["2B"]["two_sided_p"], 4) if a else None, "R361")
    out["rank_null_n"] = (a["rank_null"]["2B"]["n"] if a else None, "R361")
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
    # R361 — added when the closing claim was corrected. A claim that changes must bring its
    # check with it, or the gate silently certifies the OLD sentence's numbers.
    "labels_min_08B":        r"falls to \*\*(\d+)\*\* — references \*do\* purge them there",
    "rank_p_2B":             r"exact two-sided p = \*\*(\d\.\d+)\*\*",
    "rank_null_n":           r"C\(9,4\)=(\d+) assignments",
    # R362 — the size claim became judge-indexed; its numbers come with it.
    "neg_sizes_08B":         r"\*\*negative at (\d+) of 7 sizes\*\*",
    "sign_flips":            r"a \*sign\ninversion\* at \*\*(\d+) of 7 sizes\*\*",
    # R363 — clause ③ narrowed; its census numbers come with it.
    "overlap_pct":           r"are, at \*\*(\d+\.\d)%\*\*, the same",
    "overlap_ratio":         r"ratio \*\*(\d+)×\*\*",
    "n_annotators":          r"\*\*([\d,]+)\*\* distinct annotators",
    "full_overlap_prompts":  r"\*\*(\d+) of 968\*\* prompts have complete",
    # R364 — the channel was sized; the bound and its power come with the claim.
    "channel_mde":           r"MDE of (\d\.\d+)\*\*, with three seeds",
    "plant_detected":        r"detected from \*\*\+(\d\.\d+)\*\* upward",
    # R365 — the null survived a change of judge; its second-judge numbers come with it.
    "channel_mde_08B":       r"\*\*\+0\.0000 vs MDE (\d\.\d+) at 0\.8B\*\*",
    "mde_ratio_08B":         r"only \*\*(\d\.\d+)×\*\* 2B's",
    # R366 — the survival explanation was refuted; its counts come with the correction.
    "survive_n":             r"population of \*\*(\d+)\*\* claims run at both judges",
    "p_form":                r"neither `difference` \(Fisher\n\*\*p = (\d\.\d+)\*\*\)",
    "p_null":                r"nor `null` \(\*\*p = (\d\.\d+)\*\*\)",
    "p_perfect":             r"\*\*would\*\*\s+have reached \*\*p = (\d\.\d+)\*\*",
    # R367 — J became nameable; the external check's numbers come with the rule.
    "rule_b_2B":             r"last \*\*(\d\.\d+)\*\* of the time",
    "rule_b_08B":            r"against 0\.8B's \*\*(\d\.\d+)\*\*",
    "rule_b_n":              r"on the \*\*(\d+)\*\*\s*\n?prompts carrying such a rating",
    # R368 — transport measured; its numbers travel with the clause.
    "transport_exact":       r"by \*\*\+(\d\.\d+) against an MDE",
    "transport_mde":         r"against an MDE of (\d\.\d+)\*\*",
    # R369 — the decomposition; its two numbers travel with the caveat.
    "dfloor_exact":          r"is \*\*\+(\d\.\d+)\*\* on exact",
    "dcore_exact":           r"under both \(\*\*\+(\d\.\d+)\*\*",
    # R370 — transport demoted to a limit; the non-subset numbers travel with it.
    # ⚠ anchored on the R370 sentence: the bare `**+N vs MDE` form also matches R367's
    #   rule-A number (+0.0967) earlier in the document, and the gate caught that collision.
    "pool_contrast":         r"the contrast is \*\*\+(\d\.\d+) vs MDE",
    "pool_mde":              r"vs MDE (\d\.\d+)\*\* \(exact\)",
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
        got[label] = float(m.group(1).replace(",", "")) if m else None
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
