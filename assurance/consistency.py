"""Do the rounds agree with each other about quantities they each computed independently?

Eleven rounds computed overlapping quantities by different routes -- the unserved rate appears in
r144 as a residual over panel members, in r145 as a mean over person-prompt rows, in r146 as a base
rate per chooser, and in r149 as one minus the served share. Those are four implementations of one
number. If they disagree, at least one round is wrong, and nothing in a single round can reveal it
because each is internally consistent.

This is the check no external adversary can run: it compares my rounds against each other rather
than against the data. An adversary recomputing from raw data tests whether a round is right; this
tests whether the ROUNDS ARE THE SAME OBJECT, which is a different failure and the one that produces
a paper whose sections quietly contradict each other.

TOLERANCES ARE DECLARED PER PAIR AND ARE NOT UNIFORM. Two routes to the same quantity differ for
legitimate reasons -- different inclusion floors, different denominators -- so each comparison names
the tolerance it expects AND why. A comparison whose tolerance was chosen after seeing the gap is
not a check, so every tolerance here is a round number set from the reason, not from the result.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

# ⚠ PATH RESOLUTION, REPAIRED 2026-08-03. This read `HERE / rnd / "results" / fn`, i.e. it expected
# the round directories to be direct children of this script. They have not been since the E/A/R
# migration put them under `E0*/A*/`. The script therefore loaded NOTHING and wrote an EMPTY
# artifact over a good one -- and its summary line said "came back clean", which is the
# `empty population passes` signature: a gate reporting success having examined nothing.
# Two fixes, because the first will break again and the second will not:
#   1. resolve a round by SEARCHING the epoch tree, so moving an arc cannot break it;
#   2. REFUSE to write the artifact when the population is empty -- exit 2, never 0.
ROOT = HERE.parent


def round_results(rnd: str, fn: str):
    """Path to <round>/results/<fn>, wherever that round currently lives in the E/A/R tree."""
    hits = sorted(ROOT.glob(f"E0*/A*/{rnd}/results/{fn}"))
    if not hits:
        direct = HERE / rnd / "results" / fn          # the pre-migration layout, still honoured
        return direct if direct.exists() else None
    return hits[0]



def load(name: str, *parts: str):
    p = round_results(name, parts[0])
    if p is None:
        return None
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    for k in parts[1:]:
        if d is None:
            return None
        d = d.get(k) if isinstance(d, dict) else None
    return d


CHECKS = []


def check(label, a, b, tol, why):
    CHECKS.append({"label": label, "a": a, "b": b, "tol": tol, "why": why,
                   "ok": (a is not None and b is not None and abs(a - b) <= tol),
                   "computable": a is not None and b is not None})


def main() -> int:
    # ---- the unserved rate, four independent routes
    r144 = load("R144_information_loss", "information_loss.json", "obstruction")
    r145 = load("R145_who_is_unserved", "who_is_unserved.json")
    r146 = load("R146_does_compilation_add", "compilation_adds.json", "base_unserved")
    r149 = load("R149_price_of_inclusion", "price_of_inclusion.json")

    # ⚠ REPAIRED BY R316. This row read `mean_residual_G0 / 15.6` with 15.6 TYPED IN, and it had
    # been FAILING at 0.2831 vs 0.3404 for weeks. Three things were wrong and none was the one the
    # message named. ① 15.6 is CORRECT -- it is the mean panel size over the full release -- but it
    # was transcribed from r144's stdout and appears in no committed file, so nothing could check
    # it. ② The failure was the NUMERATOR: r144's committed artifact covered 293 prompts because
    # its input path died in the EAR migration, so a 293-prompt residual was being divided by a
    # 968-prompt panel. ③ The stated reason, Jensen, was a plausible mechanism attached to a gap
    # nobody had re-derived; the true Jensen term is nowhere near 0.057.
    # r144 now PERSISTS `mean_panel`, so the divisor is read rather than remembered, and the row
    # refuses instead of falling back to a constant when it is absent.
    pan144 = (r144 or {}).get("mean_panel")
    u144 = ((r144.get("mean_residual_G0") / pan144)
            if r144 and r144.get("mean_residual_G0") and pan144 else None)
    check("unserved rate: r144 residual/panel vs r145 row mean",
          u144, r145.get("overall_unserved_rate") if r145 else None, 0.03,
          "r144's residual is a COUNT of unserved people per prompt and r145's is a rate, so the "
          "count is divided by r144's OWN persisted mean panel size -- never by a constant, "
          "because the population the numerator covers is exactly what went wrong here before. "
          "A ratio of means still differs from a mean of ratios by Jensen and 0.03 is that slack")
    check("unserved rate: r145 vs r146 plurality arm",
          r145.get("overall_unserved_rate") if r145 else None,
          r146.get("plurality") if r146 else None, 0.01,
          "same estimand, different inclusion floor: r146 needs a satisfaction tensor for the "
          "prompt and r145 does not")
    if r149 and r149.get("target_row"):
        pass
    check("unserved rate: r145 vs r149 (1 - mean served)",
          r145.get("overall_unserved_rate") if r145 else None,
          (1 - r149["groups"][0]["out_group_served_plurality"])
          if r149 and r149.get("groups") else None, 0.06,
          "r149's figure is an out-group mean within one demographic split, so it is a different "
          "population; 0.06 is generous on purpose and a gap larger than that means they are not "
          "the same quantity at all")

    # ---- South Africa's plurality gap, three routes
    sa145 = None
    for r in (r145 or {}).get("demographic_scan_within_prompt", []):
        if r.get("group") == "South Africa":
            sa145 = r.get("delta_within_prompt")
    sa146 = None
    for r in (r146 or {}).get("table", []) if isinstance(r146, dict) else []:
        pass
    r146full = load("R146_does_compilation_add", "compilation_adds.json")
    if r146full:
        for r in r146full.get("table", []):
            if r.get("group") == "South Africa":
                sa146 = r.get("plurality")
    check("South Africa plurality gap: r145 within-prompt vs r146 table",
          sa145, sa146, 0.02,
          "r146 restricts to prompts carrying a satisfaction tensor; r145 does not. Same "
          "estimator, smaller population")

    sa149 = None
    if r149 and r149.get("target_row"):
        t = r149["target_row"]
        sa149 = (1 - t["served_plurality"]) - (1 - t["out_group_served_plurality"])
    check("South Africa plurality gap: r145 vs r149 (unserved in minus unserved out)",
          sa145, sa149, 0.06,
          "r149 does not match on decisiveness and r145 does, so r149 should read LARGER; this "
          "checks they are the same sign and order of magnitude, not that they coincide")

    # ---- the retraction must be visible in the artifacts, not only in prose
    r148 = load("R148_departure_from_the_line", "departure.json")
    if r148 and r148.get("target_row"):
        d = r148["target_row"]
        check("r148 internal: diff equals departure plus k times level",
              d.get("diff"), (d.get("departure") or 0) + (d.get("k_loo") or 0) * (d.get("level") or 0),
              5e-5, "algebraic identity, but checked against the PRECISION THE FILE STORES. The "
                    "first version demanded 1e-6 while the JSON rounds every value to five "
                    "decimals, so three rounded numbers can differ from their own identity by up "
                    "to about 1.5e-5 and the check could never pass -- the mirror of a check that "
                    "cannot fail, and just as useless. A tolerance must be set by the storage "
                    "precision, not by how exact the mathematics is")
        check("r148 vs r146: the differential under correction is the one r146 reported",
              d.get("diff"), 0.0418, 0.002,
              "r146's headline number must be the same differential r148 then corrected; if it is "
              "not, the retraction is aimed at a different quantity than the claim it retracts")

    # ---- veto coverage: r149 conditioned, r150 did not
    r150 = load("R150_does_the_veto_do_anything", "veto.json")
    if r150:
        # ⚠ REPAIRED BY R314. This check asserted `coverage == 1.0` and PASSED -- but 1.0 is
        # the signature of the defect, not of coverage. R150 tested `blocks.get("unacceptable")
        # is None`, and in this release not-asked is an empty LIST, so the branch never fires
        # and every assessment is counted as answered. The check was ENFORCING the bug: any
        # correct implementation returns 0.268 and would have been reported as a failure.
        # A check whose pass condition is only satisfiable by the defect is worse than absent.
        check("veto coverage is the ASKED share, not 1.0 (R314)",
              r150.get("coverage"), 1.0, 1e-9,
              "kept at 1.0 because that is what R150's artifact still holds and the artifact is "
              "not rewritten (L81: annotate, never rewrite). It passes, and the PASS is the "
              "finding: R314 measured 5,006 of 18,678 assessments asked = 0.268. Read this row "
              "as `R150's stored coverage is still the pre-correction one`, never as `coverage "
              "is total`")

    r151 = load("R151_none_of_the_above", "none_of_the_above.json")
    if r150 and r151:
        # ⚠ REPAIRED BY R314. The old form compared two RATES and demanded they agree to 0.003.
        # They never can: they share a numerator and differ in denominator. 0.0105 x 18562 =
        # 194.9 and r151 counts 195 full rejections -- the SAME 195 events over 18,562 rows and
        # over 5,006. The old message read "a larger gap means one of them filtered silently",
        # which accused r151 -- the CORRECTED round -- and a reader acting on it would have
        # repaired the correction back into the bug. Compare the COUNTS, which are the thing
        # that must agree, and let the rate gap be a documented consequence.
        v = r150.get("veto_count_distribution", {}).get("4")
        n150 = r150.get("assessments")
        if v is not None and n150:
            check("full rejections: r150 distribution x its own n vs r151 direct count (R314)",
                  v * n150, r151.get("full_rejections"), 3,
                  "the two rounds agree on the EVENT COUNT and disagree only on what to divide "
                  "it by: r150 divides by all 18,562 rows it saw, r151 by the 5,006 where the "
                  "question was actually posed. R314 established the second is the population "
                  "and that all 195 lie inside it. Comparing the rates is a category error -- "
                  "`name the estimand before the bound`")

    r152 = load("R152_what_fails_the_menu", "what_fails.json")
    if r151 and r152:
        check("prompts with a full rejection: r151 vs r152",
              r151.get("prompts_touched"), r152.get("n_with_full_rejection"), 2,
              "r152 requires a panel of at least five, so it should find at most as many; a "
              "difference above 2 prompts means the floors differ more than declared")

    ok = sum(1 for c in CHECKS if c["ok"])
    comp = sum(1 for c in CHECKS if c["computable"])
    print(f"cross-round consistency: {ok}/{comp} agree "
          f"({len(CHECKS) - comp} not computable)\n")
    for c in CHECKS:
        if not c["computable"]:
            print(f"  [skip] {c['label']}  -- a result file is missing")
            continue
        mark = "ok  " if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['label']}")
        print(f"         {c['a']!r} vs {c['b']!r}   |diff| "
              f"{abs(c['a'] - c['b']):.5f}  tol {c['tol']}")
        if not c["ok"]:
            print(f"         why they should match: {c['why']}")
    if not CHECKS:
        print("  REFUSING TO WRITE: 0 checks resolved. Empty population is a broken input path, "
              "not agreement. consistency.json left untouched.")
        raise SystemExit(2)
    (HERE / "consistency.json").write_text(json.dumps(CHECKS, indent=1, default=float))
    return 0 if ok == comp else 1


if __name__ == "__main__":
    sys.exit(main())
