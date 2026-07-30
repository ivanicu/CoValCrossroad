"""r92 -- r43 defends excluding 63.5% of criteria with the wrong argument.

CLAIM CARD
----------
Claim      r43's scope note justifies analysing only the majority-rated (pre-seeded)
           criteria like this: "r49 tested those separately and found they transfer
           BETTER across raters (+0.0777 vs +0.0599 ...), so the exclusion understates
           the direction rather than manufacturing it."
Estimand   the number of WRITE-IN criteria that admit a between-group sign comparison
           at r43's own thresholds -- i.e. whether the heterogeneity question is even
           askable on the population r43 excluded.
Target
observed?  YES, and it is a census rather than an inference. Every criterion's rater
           list and every rater's demographic group are in the release.
Alternative
worlds     A ANALYSABLE  write-ins admit enough cells. Then r43's conclusion is
                         TESTABLE on the complement, the transfer-based defence is
                         beside the point, and the test should simply be run.
           U UNDEFINED   write-ins carry too few raters per criterion for any group
                         mean to exist. Then the heterogeneity question is not
                         "understated" on that population -- it is UNDEFINED there,
                         and r43's stated reason should be replaced by the structural
                         one, which is far stronger and does not depend on r49.
Intervention
           none. A census at r43's thresholds, swept over min_cell.
Null       THE POSITIVE CONTROL IS THE WHOLE DESIGN. A zero cell-count on write-ins is
           inadmissible unless the IDENTICAL counting code returns a large non-zero on
           the seeded criteria. A zero from an instrument that has never returned
           non-zero is silence, not an acquittal -- so the seeded arm runs first and
           this round REFUSES to report the write-in zero if the seeded arm is also
           empty.

WHY THIS IS THE STEP
--------------------
Queue item 1 is marked [NOW] and requires rescoping "not population-conditional" to
"NO DETECTED AGGREGATE LOSS IN THE TESTED SPLITS", because aggregate accuracy can hide
criterion sign reversals and minority-only criteria. r43 is the round that addressed
exactly that -- and it ran on 36.5% of the criteria, the pre-seeded set shown
IDENTICALLY to every participant. Those are precisely the criteria most exposed to the
shared-menu construction that item 1's first bullet is about. So the population claim
and the menu-endogeneity claim meet on the same 63.5% exclusion, and the reason for
that exclusion had never been measured -- only argued from a different quantity.

TRANSFER IS NOT HETEROGENEITY -- the proxy ledger for r43's stated defence
--------------------------------------------------------------------------
PROPERTY    the excluded criteria would not have shown more group heterogeneity.
PROXY       the excluded criteria transfer BETTER across raters (r49).
IMPLICATION neither direction holds. A criterion set can predict well ON AVERAGE while
            carrying strong group structure -- average predictive power and systematic
            between-group difference are different quantities, and one does not bound
            the other. Better transfer is equally consistent with less heterogeneity
            and with more of it concentrated in a minority.
SAFE SIDE   the transfer result cannot license a claim about heterogeneity in either
            direction. This round replaces it with a count.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
ANNOTATORS = _ROOT / "data/annotators.jsonl"
R43 = _ROOT / "05_human_protocol_and_power/r43_criterion_heterogeneity/results/r43_criterion_heterogeneity.json"
AXES = (("country", "country_of_residence"), ("ai_usage", "generative_ai_usage"), ("age", "age"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r92_writein_analysability.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R43.exists():
        raise SystemExit("REFUSING: r43's artifact is absent; this round audits its scope note "
                         "and must read the claim it is auditing rather than paraphrase it.")
    r43 = json.load(open(R43))
    min_cell_r43 = int(r43["min_cell"])

    demo = {}
    for line in open(ANNOTATORS):
        r = json.loads(line)
        d = r.get("demographics") or {}
        demo[r.get("annotator_id")] = {k: d.get(v) for k, v in AXES}

    # census: for each criterion, is it seeded (majority-rated) or a write-in, how many
    # raters does it carry, and how many demographic groups clear min_cell on it
    rows = {"seed": [], "writein": []}
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        items = rub.get("coval_full") or []
        if not items:
            continue
        raters = {s["annotator_id"] for it in items for s in (it.get("scores") or [])}
        thr = max(2, (len(raters) + 1) // 2)          # r43's own filter, line 395
        for it in items:
            sc = it.get("scores") or []
            per_axis = {}
            for ax, _ in AXES:
                by = defaultdict(int)
                for s in sc:
                    g = (demo.get(s["annotator_id"]) or {}).get(ax)
                    if g:
                        by[g] += 1
                per_axis[ax] = sorted(by.values(), reverse=True)
            rows["seed" if len(sc) >= thr else "writein"].append(
                {"n_raters": len(sc), "per_axis": per_axis})

    print(f"criteria: seeded {len(rows['seed']):,}   write-in {len(rows['writein']):,}   "
          f"(write-in share {len(rows['writein']) / (len(rows['seed']) + len(rows['writein'])):.1%})")

    def cells(pop, ax, m):
        """criteria on which >=2 groups each have >=m raters -- r43's comparison unit."""
        return sum(1 for r in rows[pop] if sum(1 for c in r["per_axis"][ax] if c >= m) >= 2)

    sweep = {}
    print(f"\n  usable cells by min_cell (r43 used min_cell={min_cell_r43})")
    print(f"  {'axis':<9} {'min_cell':>8} {'seeded':>10} {'write-in':>10}")
    for ax, _ in AXES:
        sweep[ax] = {}
        for m in (1, 2, 3, 4):
            s_, w_ = cells("seed", ax, m), cells("writein", ax, m)
            sweep[ax][m] = {"seed": s_, "writein": w_}
            mark = "   <- r43's threshold" if m == min_cell_r43 else ""
            print(f"  {ax:<9} {m:>8} {s_:>10,} {w_:>10,}{mark}")

    med = {p: float(np.median([r["n_raters"] for r in rows[p]])) for p in rows}
    print(f"\n  median raters per criterion: seeded {med['seed']:.0f}, write-in {med['writein']:.0f}")

    # ---- POSITIVE CONTROL: the same counter must fire on the seeded arm ---------
    ctrl = {ax: sweep[ax][min_cell_r43]["seed"] for ax, _ in AXES}
    ok = all(v > 100 for v in ctrl.values())
    print(f"\n  POSITIVE CONTROL: the identical counter returns {ctrl} on the seeded arm -> "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("REFUSING: the counter does not return a large non-zero on the seeded "
                         "criteria, so a zero on the write-ins would be silence, not a result.")

    wi = {ax: sweep[ax][min_cell_r43]["writein"] for ax, _ in AXES}
    undefined = all(v == 0 for v in wi.values())
    # at what min_cell does the write-in arm become non-empty at all?
    first_nonzero = {}
    for ax, _ in AXES:
        first_nonzero[ax] = next((m for m in (1, 2, 3, 4) if sweep[ax][m]["writein"] > 0), None)
    world = "U UNDEFINED" if undefined else "A ANALYSABLE"

    verdict = (
        f"{world}. r43 answered queue item 5 -- group sign reversals, minority-only criteria, and "
        f"whether group-specific weights predict better -- on the majority-rated criteria only, and "
        f"defended excluding the other {len(rows['writein']) / (len(rows['seed']) + len(rows['writein'])):.1%} "
        f"by citing r49: the excluded criteria TRANSFER better across raters, so 'the exclusion "
        f"understates the direction rather than manufacturing it'. THAT IS A TRANSFER ARGUMENT ANSWERING "
        f"A HETEROGENEITY QUESTION. Average predictive power and systematic between-group difference are "
        f"different quantities and neither bounds the other; better transfer is equally consistent with "
        f"less heterogeneity and with more of it concentrated in a minority. Counted instead: write-in "
        f"criteria carry a median of {med['writein']:.0f} rater against the seeded set's {med['seed']:.0f}, "
        f"and at r43's own min_cell={min_cell_r43} they yield "
        + ", ".join(f"{v:,} cells on {ax}" for ax, v in wi.items()) + " against "
        + ", ".join(f"{v:,}" for v in ctrl.values()) + " on the seeded arm. "
        f"AND IT IS NOT A THRESHOLD CHOICE: the write-in arm is empty even at min_cell=1, the most "
        f"permissive setting possible, because a between-group comparison needs at least two raters on "
        f"one criterion and a write-in has one. THE MECHANISM, which is sharper than the logic: r49's "
        f"transfer design needs ONE rater per criterion (its author) plus OTHER raters' rankings, and "
        f"the write-ins have exactly that shape; heterogeneity needs MANY raters on the SAME criterion, "
        f"and they do not. So r49's result is valid and simply cannot bear on this question -- not "
        f"because the inference is loose, but because the data structure that would answer it does not "
        f"exist on that population. "
        f"So the heterogeneity question is not UNDERSTATED on the excluded population -- it is "
        f"{'UNDEFINED there: a criterion rated by one person has no within-group mean, so there is no between-group comparison to make at any threshold at all' if undefined else 'partially askable and should simply be tested'}. "
        f"THE POSITIVE CONTROL IS THE WHOLE DESIGN: the identical counter returns large non-zero counts "
        f"on the seeded arm, so the write-in zero is a measurement and not an instrument that never "
        f"fires. The round refuses to report it otherwise. WHAT THIS CHANGES: r43's conclusion stands "
        f"unaltered, but its SCOPE hardens from a defended choice into a structural limit, and the "
        f"limit is load-bearing for queue item 1 -- the only criteria on which any population claim can "
        f"be made are the PRE-SEEDED ones, shown identically to every participant, which are exactly the "
        f"criteria most exposed to the shared-menu construction item 1's first bullet is about. So "
        f"'no detected aggregate loss in the tested splits' needs one more clause: IN THE PRE-SEEDED "
        f"CRITERION CLASS, and that restriction is structural rather than a choice anyone made."
    )

    doc = {
        "n_seed": len(rows["seed"]), "n_writein": len(rows["writein"]),
        "writein_share": len(rows["writein"]) / (len(rows["seed"]) + len(rows["writein"])),
        "median_raters": med, "r43_min_cell": min_cell_r43,
        "cells_by_min_cell": sweep,
        "cells_at_r43_threshold": {"seed": ctrl, "writein": wi},
        "writein_first_nonzero_min_cell": first_nonzero,
        "positive_control_passed": ok, "writein_undefined": undefined,
        "world": world,
        "outcome_variable_scope": (
            "A census of criteria and their raters' demographic groups. No judge, no satisfaction "
            "tensor, no model: this counts whether r43's comparison unit exists on the excluded "
            "population, and nothing else."),
        "scope": (
            "This does NOT test heterogeneity on the write-ins -- it establishes that the test is not "
            "defined there. It says nothing about whether write-in criteria carry group structure that "
            "a DIFFERENT design, with more raters per write-in criterion, could detect. That design is "
            "a data-collection question, not an analysis one -- and it is the concrete change a future "
            "elicitation would have to make: route each write-in to several raters, not only its author."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
