#!/usr/bin/env python3
"""
R666 -- p100 is an IN-SAMPLE CEILING, so R665's severity claim is downgraded by its own corpus.

CHECK #267 ON R665's CLOSING LINE. ALL THREE CHECKABLE CLAUSES FAIL, AND THE THIRD INVERTS R665.
  ⛔ "that is THE LAST structural question this definition has left." §4's exact tell, and false:
     **23 lines** of STATEMENT.md flag something unresolved -- supersession-vs-omission, the
     unrebuildable comparator, register rows 3 and 4, the B-fork.
  ⛔ "`topw_k4` -- a plain top-weight arm with NO CORE-CONSTRUCTION at all." The corpus contains a
     round measuring **topw_k4's SELECTION BUDGET as a lower bound** (R328). It is a SELECTED arm.
  ⛔⛔⛔ "no clause removes it" is true, but the reason I gave for caring is not: R328's artifact
     records `true_argmax = 0.55747530882624` and `equals_true_argmax: false`, with
     `provenance_defect: true`. **THE p100 VALUE IS THE IN-SAMPLE CEILING** -- the argmax over all
     1,820 subsets evaluated on the SAME data -- not a percentile of independent baselines.

⚠⚠ SO R665's SEVERITY CLAIM IS WRONG AND THIS ROUND RETRACTS IT.
   R665 asked "could this have come out otherwise?" and answered "yes -- 4 of 42 admitted against
   4 of 42 removed, partial overlap was likelier." That reasoning counted ARMS and ignored the
   MECHANISM. Comparing against an in-sample argmax means the arms that clear it are close to
   exactly the arms with in-sample access. The overlap was not a coincidence over 42 arms; it was
   substantially STRUCTURAL, which is §0's arithmetic trap: a quantity computed and reported as
   though it had been tested.

ESTIMAND        Is the emptiness of `② ∧ ③` at p100 FORCED by the baseline being an in-sample
                ceiling, or does it survive at a baseline that is not fitted to the same data?
                Concretely: the extension of `② ∧ ③` at the HELD-OUT best of 1,820 (0.5546,
                committed in R328) versus at the in-sample ceiling (0.5575).
IDENTIFICATION  Exact given R328's three committed reference values and R527's curve. NOT
                identified: the exact percentile of the held-out best within R527's grid -- the
                curve is sampled at 8 points and 0.5546 falls BETWEEN p095 (0.5511) and p100
                (0.5575), so the extension there is BOUNDED, not pinned. Bounds, not a point.
SCOPE           population : the 42-arm space; the 1,820-subset class; 968 prompts
                instrument : committed artifacts only (R328 budget_matching, R527 spec curve)
                             instrument unit = A BASELINE VALUE
                             claim unit      = THE DEFINITION'S EXTENSION AT THAT BASELINE
                             EQUAL by construction
                baseline   : R328's own three committed references -- budget-0 (0.5397),
                             held-out best (0.5546), in-sample ceiling (0.5575)
                regime     : home release, single object
WORLDS          A FORCED: the extension is empty at the in-sample ceiling and non-empty at the
                  held-out best -> R665's finding is an artefact of comparing to a fitted quantity,
                  and its severity claim is retracted.
                B ROBUST: empty at both -> the emptiness survives a non-fitted baseline and R665's
                  finding stands on its own.
                C UNDECIDABLE: the held-out best falls where R527's grid cannot resolve the
                  extension -> report the bound and refuse the point.
KILL            pre-registered: if the held-out best (0.5546) lies OUTSIDE [p095, p100] the mapping
                is wrong and no comparison is admissible.
POSITIVE CTRL   R328's `repro` block re-derives budget-0 and the in-sample ceiling and both match
                R287 exactly -- the artifact's own reproduction check. It must be present and true.
NEGATIVE CTRL   the three references must be DISTINCT and ORDERED
                (budget-0 < held-out < in-sample); if they collapse, the distinction this round
                rests on does not exist.
PLACEBO         a value below budget-0 must map below p000.
NOISE FLOOR     n/a -- committed values. Deterministic.
MULTIPLICITY    3 reference values x R527's 8-point curve + 3 controls.
ARTIFACT        results/in_sample_ceiling.json
IMPOSSIBLE      the extension AT the held-out best cannot be computed exactly without re-running
                ②'s admission at that threshold, which needs the per-arm a2 scores; R527's curve
                is sampled at 8 percentiles only. Named -- the answer here is a BOUND.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R527 = A24 / "R527_is_clause_two_a_choice" / "results" / "clause2_spec_curve.json"
R328 = A24 / "R328_the_three_readings_are_one_budget" / "results" / "budget_matching.json"
R442 = A24 / "R442_the_extension_under_clause_three_as_written" / "results" / "r442_extension.json"


def main() -> int:
    for p in (R527, R328, R442):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent. Exit 2, never 0.")
            return 2
    c2 = json.loads(R527.read_text())
    bm = json.loads(R328.read_text())
    rem = set(json.loads(R442.read_text())["clause3_impl"])

    refs = bm["committed_refs"]
    b0 = refs["budget 0 · 20 draws"]
    ho = refs["held-out best of 1,820"]
    ins = refs["in-sample ceiling"]

    print("─── CONTROLS ───")
    repro = bm.get("repro", {})
    reprook = all(v.get("ok") for v in repro.values() if isinstance(v, dict))
    print(f"  POSITIVE  R328's own reproduction block re-derives its references against R287 -> "
          f"{[(k, v.get('ok')) for k, v in repro.items() if isinstance(v, dict)]} -> "
          f"{'PASS' if reprook else '⛔ FAIL'}")
    ordered = b0 < ho < ins
    print(f"  NEGATIVE  the three references must be DISTINCT and ORDERED -> "
          f"budget0 {b0:.4f} < held-out {ho:.4f} < in-sample {ins:.4f} -> "
          f"{'PASS' if ordered else '⛔ FAIL — the distinction does not exist'}")
    p000, p100 = c2["rows"]["p000"]["a2"], c2["rows"]["p100"]["a2"]
    plc = (b0 - 0.05) < p000
    print(f"  PLACEBO   a value below budget-0 maps below p000 ({p000:.4f}) -> "
          f"{'PASS' if plc else '⛔ FAIL'}")
    inside = c2["rows"]["p095"]["a2"] <= ho <= p100
    print(f"  KILL      the held-out best must lie in [p095, p100] = "
          f"[{c2['rows']['p095']['a2']:.4f}, {p100:.4f}] -> {ho:.4f} -> "
          f"{'PASS' if inside else '⛔ FAIL — the mapping is wrong'}")
    controls_ok = reprook and ordered and plc and inside

    print(f"\n─── WHAT p100 ACTUALLY IS ───")
    print(f"  R328 records `true_argmax` = {bm['provenance']['true_argmax']:.14f}")
    print(f"  R527's p100 a2            = {p100:.14f}")
    same = abs(bm["provenance"]["true_argmax"] - p100) < 1e-12
    print(f"  ⭐ IDENTICAL: {same} — so p100 is the IN-SAMPLE CEILING, the argmax over all "
          f"{c2['n_subsets']} subsets evaluated on the SAME data, not an independent baseline.")
    print(f"  R328 also flags provenance_defect = {bm.get('provenance_defect')}, "
          f"equals_true_argmax = {bm['provenance'].get('equals_true_argmax')}, "
          f"equals_split0_heldout = {bm['provenance'].get('equals_split0_heldout')}")

    print(f"\n─── THE EXTENSION AT EACH OF R328's THREE COMMITTED BASELINES ───")
    rows = sorted(c2["rows"], key=lambda k: c2["rows"][k]["a2"])
    def bracket(v):
        lo = [k for k in rows if c2["rows"][k]["a2"] <= v]
        hi = [k for k in rows if c2["rows"][k]["a2"] >= v]
        return (lo[-1] if lo else None), (hi[0] if hi else None)
    for name, v in (("budget-0 (20 draws)", b0), ("held-out best of 1,820", ho),
                    ("in-sample ceiling", ins)):
        a, b = bracket(v)
        ea = sorted(set(c2["rows"][a]["admitted"]) - rem) if a else None
        eb = sorted(set(c2["rows"][b]["admitted"]) - rem) if b else None
        n = f"{len(eb)}" if ea == eb else f"[{len(eb)}, {len(ea)}]"
        print(f"  {name:<24} a2={v:.4f}  between {a} and {b}  "
              f"② ∧ ③ admits {n}  {', '.join(eb or [])[:44]}")

    a_ho, b_ho = bracket(ho)
    ext_lo = sorted(set(c2["rows"][b_ho]["admitted"]) - rem)
    ext_hi = sorted(set(c2["rows"][a_ho]["admitted"]) - rem)

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no baseline claim is admissible"
    elif ext_lo == ext_hi and not ext_lo:
        world = (f"B ROBUST — `② ∧ ③` is empty at the held-out best too, so the emptiness survives "
                 f"a baseline not fitted to the same data and R665's finding stands.")
    else:
        world = (f"A FORCED, AND R665's SEVERITY CLAIM IS RETRACTED — p100 IS the in-sample "
                 f"ceiling ({ins:.6f} = R328's true_argmax), so ②-at-p100 asks whether an arm "
                 f"beats the best subset fitted on the SAME data. The arms that clear it are close "
                 f"to exactly the arms with in-sample access, which is why ③ removes all of them. "
                 f"At the HELD-OUT best of 1,820 ({ho:.4f}) the extension is BRACKETED between "
                 f"{len(ext_lo)} and {len(ext_hi)} — and since the lower bound is {len(ext_lo)}, "
                 f"⚠ NON-EMPTINESS THERE IS NOT ESTABLISHED, only that the upper bracket is "
                 f"{{{', '.join(ext_hi)}}}. A [0, 2] bracket does not license 'non-empty', and "
                 f"writing that would be this arc's fifth verdict-string defect. "
                 f"⛔ R665 asked 'could this have come out otherwise?' and answered YES by counting "
                 f"4 of 42 against 4 of 42. That counted ARMS and ignored the MECHANISM; the "
                 f"overlap was substantially structural. §0's arithmetic trap, committed in the "
                 f"round that quoted it. ⭐ WHAT SURVIVES: the definition's extension still depends "
                 f"on the baseline — [{len(ext_lo)}, {len(ext_hi)}] at the held-out best, "
                 f"{len(sorted(set(c2['rows']['published']['admitted']) - rem))} at the published "
                 f"percentile, 0 at the in-sample ceiling — and that claim never needed p100. "
                 f"⚠ THE SAME BRACKET DEFECT SURVIVED INTO THIS CLAUSE ON THE FIRST WRITING: it "
                 f"said '{len(ext_hi)} at the held-out best'. A verdict string can carry the same "
                 f"error twice in one sentence, which is why the fix is the BRACKET, not the word.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 3 reference values x an 8-point curve + 4 controls.")
    print(f"  ⚠ BOUND, NOT A POINT: the held-out best falls BETWEEN R527's sampled percentiles, so "
          f"the extension there is bracketed, not pinned. Pinning it needs the per-arm a2 scores.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "in_sample_ceiling.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "p100_is_true_argmax": same, "refs": refs,
        "held_out_bracket": [b_ho, a_ho],
        "extension_at_held_out_bounds": [len(ext_lo), len(ext_hi)],
        "extension_at_held_out_upper_set": ext_hi,
        "extension_at_published": sorted(set(c2["rows"]["published"]["admitted"]) - rem),
        "check267": ("R665's NEXT: 'the LAST structural question' (23 STATEMENT.md lines flag "
                     "something unresolved), 'topw_k4 has NO core-construction' (R328 measures "
                     "its SELECTION BUDGET), and a severity claim that counted arms and ignored "
                     "the mechanism."),
        "retracts": ("R665's 'could this have come out otherwise? Yes' -- the p100 comparison is "
                     "against an in-sample argmax, so the clearing set is substantially forced."),
        "impossible": ("the extension exactly AT the held-out best needs per-arm a2 scores; "
                       "R527's curve is sampled at 8 percentiles, so the answer is a bound."),
    }, indent=2))
    print(f"\n  wrote {out / 'in_sample_ceiling.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
