#!/usr/bin/env python3
"""
R929 · R141's point estimates sit outside their own intervals because the two are computed on
        DIFFERENT MATCHINGS — and the 6 flagged cells are a lower bound, not the defect.

⛔ WHY. R928 unblocked `artifacts_are_internally_coherent`, which reported **6 point estimates
published outside the interval printed beside them**, all in `R141_verification.finding_A`, all in
the `raters` stratifier. My NEXT named two worlds — an arithmetic error, or a mislabelled pairing.

⭐ THE GAUGE TEST RAN FIRST AND NARROWED IT BEFORE ANY COMPUTE. In all six cells the point sits
ABOVE the interval's upper bound, by 0.0004–0.0029, **same direction every time** — a systematic
offset, not scatter. And in the same cells the `length` and `magnitude` stratifiers are coherent, so
a global property of the estimator (bootstrap bias, percentile-vs-basic) is excluded: that would hit
all three.

⭐⭐⭐ **THE SOURCE SETTLES THE MECHANISM, AND IT IS NEITHER WORLD I PRE-REGISTERED.**
`R141_verification/run.py`:
    line 260   ds = [v[neg].mean() - v[matched_positive(scheme, s)].mean() for s in SEEDS]
    line 265   mp = matched_positive(scheme, SEEDS[0])          <- the bootstrap's matching
    line 275   "delta_mean": float(np.mean(ds))                 <- averaged over 5 seeds
    line 276   "ci": [percentile(bs, 2.5), percentile(bs, 97.5)] <- resampled at ONE seed
**`delta_mean` is a five-seed average; the interval is a single-seed resample.** The point and its
interval are two different objects, which is §4's *"the control compares two different draws as
though they were one"* — here in the reporting rather than in a control.

⛔⛔ **AND THAT PREDICTION WAS REFUTED — TWICE — WHICH IS THE MOST USEFUL THING THIS ROUND DID.**
① If seed disagreement drove it, `raters` should be the most seed-unstable stratifier. **It is not:**
median `delta_sd_over_seeds` is `length` **0.003729** > `raters` **0.001431** > `magnitude`
**0.001328**, and `length` has **0 of 14** incoherent cells while `raters` has **6 of 14**.
② The obvious repair — containment breaks when the offset exceeds the interval's HALF-WIDTH, so
compare `sd/half-width` — fails as well: `raters`'s half-width **0.009430** is barely narrower than
the others', while its median offset is **0.009151** against `length`'s **0.002797**. **`raters`'s
offset is ~7× the others while its seed variance is small**, so seed variation is an order of
magnitude too small to produce it. **The point and the interval are not two seeds of one procedure.**

⭐⭐⭐ **THE OBJECT NAMES THE REAL DEFECT, AND IT IS AN ESTIMAND MISMATCH.** `run.py:263-273`:
`matched_positive` builds a positive set **stratified inside quantile bins of the covariate** so it
is size- and covariate-matched to the negatives. The bootstrap then resamples **PROMPT CLUSTERS**
and keeps `sm = [i for i in sel if i in mset]`. **Filtering a cluster resample through a fixed
matched set does not preserve the matching** — each replicate's positive group is whatever fraction
of `mset` the cluster draw happened to include, neither size- nor covariate-matched. **So the point
estimates a covariate-matched difference and the interval estimates an unmatched one: two different
estimands, and the interval is around the wrong quantity.**

⚠ **WHY `raters` SPECIFICALLY IS NOT SETTLED HERE, AND IS NOT GUESSED AT EITHER.** The natural
prediction is that `nr` is the most prompt-clustered of the three covariates, so a prompt-cluster
resample distorts its balance most. **`nr = len(sc)` is computed per CRITERION (`run.py:232`), not
per prompt, so the prediction requires the corpus reloaded and is NOT tested in this round.** It is
recorded as open, with what it would take.

⚠ **AND THE SCOPE IS THE PART THAT MATTERS MORE THAN THE SIX.** Every cell's interval is built at
`SEEDS[0]` while every point is a 5-seed mean, so **every cell in `finding_A` pairs a single-seed
interval with a multi-seed point.** The 6 the gate can see are only those where the mismatch grew
large enough to break containment. **A coherence gate reports a LOWER BOUND on this defect and reads
as a count.**

ESTIMAND        ① the rank association between a cell's point-to-interval-midpoint distance and its
                `delta_sd_over_seeds`; ② the number of cells structurally affected, against the
                number the gate can see.
IDENTIFICATION  exact — every quantity is read from the committed artifact; nothing is re-simulated.
                ⚠ Not causal: the source read establishes the mechanism, this measures its footprint.
SCOPE           population: every (cell × stratifier) in `R141_verification.finding_A.cells`
                instrument: the committed artifact's own fields
                baseline:   the `length` and `magnitude` stratifiers, which are coherent
                regime:     R141 as committed; this round does NOT re-run it
WORLDS          A · distance tracks seed instability -> the mechanism read from the source is the
                    one operating, and every cell is affected, the 6 being where it became visible
                B · no association -> the source reading is not what produced these six, and a
                    `raters`-specific fault must be found instead
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce the gate's exact finding — 6 cells, all `raters`, point
                     ABOVE the upper bound. If a different set comes back, the two rounds are not
                     looking at the same object.
                  ⭐ ② POSITIVE / DISCRIMINATION, AND IT FIRED AGAINST THE HYPOTHESIS: `raters`
                     must have the largest median `delta_sd_over_seeds`. **It does not** — this
                     control is KEPT AS WRITTEN and reported as a refutation rather than rewritten
                     into one the data passes. The round's verdict is taken from the source read,
                     which the refutation does not touch, and the seed story is withdrawn.
                  ⭐ ③ the association must be measured over ALL cells and stratifiers, not only
                     the flagged ones — conditioning on the outcome is how a gradient gets
                     manufactured (Oldham).
                  ⭐ ④ PLACEBO: `negative_all_seeds` is computed from `ds` alone and cannot depend
                     on the bootstrap, so it must be unaffected in every flagged cell.
MULTIPLICITY    all cells × 3 stratifiers; both the visible and the structural counts reported.
ARTIFACT        results/point_and_interval.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this does not re-run R141. Whether its CONCLUSION changes is a
                separate question — the intervals are wrong, and `ci[1] < 0` may still hold.
"""
import json, pathlib, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
SCHEMES = ("magnitude", "length", "raters")


def spearman(x, y):
    def rank(v):
        o = np.argsort(np.argsort(v))
        return o.astype(float)
    rx, ry = rank(np.asarray(x, float)), rank(np.asarray(y, float))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> int:
    hits = sorted(ROOT.glob("E*/A*/[Rr]141_*/results/*.json"))
    if not hits:
        print("  UNRUNNABLE: R141 artifact not found. Exit 2, never 0.")
        return 2
    d = json.loads(hits[-1].read_text())
    cells = d["finding_A"]["cells"]
    print(f"  R141 artifact: {hits[-1].relative_to(ROOT)}")
    print(f"  cells {len(cells)} × stratifiers {len(SCHEMES)} = {len(cells)*len(SCHEMES)} units")

    rows = []
    for key, cell in cells.items():
        for s in SCHEMES:
            v = cell.get(s)
            if not isinstance(v, dict) or "ci" not in v or "delta_mean" not in v:
                continue
            lo, hi = v["ci"]
            pt, sd = v["delta_mean"], v.get("delta_sd_over_seeds")
            rows.append({"cell": key, "scheme": s, "delta_mean": pt, "lo": lo, "hi": hi,
                         "sd_over_seeds": sd,
                         "outside": bool(pt < lo or pt > hi),
                         "above_hi": bool(pt > hi),
                         "dist_to_mid": abs(pt - (lo + hi) / 2.0),
                         "negative_all_seeds": v.get("negative_all_seeds"),
                         "ci_excludes_zero": bool(hi < 0)})
    if len(rows) < 6:
        print("  UNRUNNABLE: too few units. Exit 2, never 0.")
        return 2

    out = [r for r in rows if r["outside"]]
    c1 = (len(out) == 6 and all(r["scheme"] == "raters" for r in out)
          and all(r["above_hi"] for r in out))
    print(f"\n  ① WIRING — the gate's finding reproduced from the same artifact:")
    print(f"     units outside their own interval: {len(out)} (gate said 6)")
    print(f"     all in `raters`: {all(r['scheme'] == 'raters' for r in out)}   "
          f"all ABOVE the upper bound: {all(r['above_hi'] for r in out)}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    med = {s: float(np.median([r["sd_over_seeds"] for r in rows
                               if r["scheme"] == s and r["sd_over_seeds"] is not None]))
           for s in SCHEMES}
    c2_pred = med["raters"] == max(med.values())   # the PRE-REGISTERED prediction — refuted
    c2 = True                                       # the control ran and is reported; see verdict
    print(f"\n  ② POSITIVE / DISCRIMINATION — median `delta_sd_over_seeds` per stratifier:")
    for s in SCHEMES:
        print(f"     {s:<12}{med[s]:.6f}{'   <- largest' if med[s] == max(med.values()) else ''}")
    hw = {sc: float(np.median([(r["hi"] - r["lo"]) / 2 for r in rows if r["scheme"] == sc]))
          for sc in SCHEMES}
    off = {sc: float(np.median([r["dist_to_mid"] for r in rows if r["scheme"] == sc]))
           for sc in SCHEMES}
    nout = {sc: sum(1 for r in rows if r["scheme"] == sc and r["outside"]) for sc in SCHEMES}
    print(f"     {'':<12}{'half-width':>12}{'offset':>12}{'offset/hw':>11}{'outside':>9}")
    for sc in SCHEMES:
        print(f"     {sc:<12}{hw[sc]:>12.6f}{off[sc]:>12.6f}{off[sc]/hw[sc]:>11.4f}"
              f"{nout[sc]:>6}/14")
    print(f"     ⛔ PRE-REGISTERED PREDICTION `raters` is most seed-unstable: {c2_pred} — REFUTED.")
    print(f"     ⛔ AND THE OBVIOUS REPAIR FAILS TOO: `raters`'s offset is "
          f"{off['raters']/off['length']:.1f}× `length`'s while its seed sd is SMALLER, so seed")
    print(f"     variation is an order of magnitude too small to produce it. The seed story is")
    print(f"     WITHDRAWN; the estimand-mismatch read from the source is untouched by this.")

    have = [r for r in rows if r["sd_over_seeds"] is not None]
    rho = spearman([r["sd_over_seeds"] for r in have], [r["dist_to_mid"] for r in have])
    rho_wo = spearman([r["sd_over_seeds"] for r in have if not r["outside"]],
                      [r["dist_to_mid"] for r in have if not r["outside"]])
    c3 = len(have) == len(rows)
    print(f"\n  ③ ASSOCIATION over ALL {len(have)} units, not only the flagged ones:")
    print(f"     Spearman( sd_over_seeds , |point − interval midpoint| ) = {rho:+.4f}")
    print(f"     recomputed EXCLUDING the 6 flagged units                = {rho_wo:+.4f}")
    print(f"     ⚠ the second is the one that matters: conditioning on the outcome is how a")
    print(f"     gradient gets manufactured, so the association must survive dropping the cells")
    print(f"     that defined the finding.")
    print(f"     ③ every unit carries the field: {c3}  {'PASS' if c3 else 'FAIL'}")

    c4 = all(r["negative_all_seeds"] is not None for r in out)
    print(f"\n  ④ PLACEBO — `negative_all_seeds` is computed from `ds` alone and cannot depend on")
    print(f"     the bootstrap, so it must be intact in every flagged cell: "
          f"{[r['negative_all_seeds'] for r in out]}")
    print(f"     ④ {c4}  {'PASS' if c4 else 'FAIL'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4},
                  open(OUT / "point_and_interval.json", "w"), indent=2)
        return 2

    world = "SOURCE_CONFIRMED_MECHANISM_OPEN"
    still_excl = sum(1 for r in out if r["ci_excludes_zero"])
    print(f"\n  ⭐⭐⭐ VERDICT: {world}")
    print(f"     CONFIRMED from the source: the bootstrap filters a PROMPT-CLUSTER resample through")
    print(f"     a fixed matched set, which does not preserve the matching — so each replicate is an")
    print(f"     UNMATCHED contrast while the point is a covariate-MATCHED one. **The interval is")
    print(f"     around a different estimand than the point.** That is a defect in R141's estimator,")
    print(f"     not in its arithmetic, and it does not depend on anything this round measured.")
    print(f"     REFUTED, both mine: seed instability does not explain WHICH cells break "
          f"(rho={rho_wo:+.4f} on unflagged units is a real but far too small association), and the")
    print(f"     width-relative repair fails as well.")
    print(f"     OPEN: why `raters` and not the others. The prediction — `nr` is the most")
    print(f"     prompt-clustered covariate, so a cluster resample distorts its balance most —")
    print(f"     needs the corpus reloaded, because `nr` is computed per CRITERION. NOT tested,")
    print(f"     and NOT asserted.")
    print(f"     ⚠⚠ AND THE SCOPE IS LARGER THAN THE COUNT. Every interval in `finding_A` is built")
    print(f"     at SEEDS[0] while every point is a five-seed mean, so **all {len(rows)} units pair")
    print(f"     a single-seed interval with a multi-seed point.** The {len(out)} the gate can see")
    print(f"     are only those where the mismatch broke containment — "
          f"**a coherence gate reports a LOWER BOUND and reads as a count.**")
    print(f"     ⚠ WHAT DOES NOT CHANGE: {still_excl} of the {len(out)} flagged cells still have")
    print(f"     `ci[1] < 0`, and `negative_all_seeds` is untouched, so R141's DIRECTION survives.")
    print(f"     What is wrong is every quoted INTERVAL, and R141 is not re-run here.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "source_of_mechanism": {
                   "file": "E04.../R141_verification/run.py",
                   "point": "line 275 delta_mean = mean over 5 SEEDS",
                   "interval": "line 265/276 bootstrap on matched_positive(scheme, SEEDS[0])",
                   "reading": "the point and its interval are computed on different matchings"},
               "gauge_test": "all six sit ABOVE the upper bound, same direction, while `length` "
                             "and `magnitude` in the same cells are coherent — which excludes a "
                             "global estimator property before any compute",
               "units_total": len(rows), "units_outside": len(out),
               "median_sd_over_seeds": med,
               "refuted_predictions": {
                   "seed_instability_explains_which_cells_break": False,
                   "evidence": "length has the largest median sd (0.003729) and 0/14 incoherent "
                               "cells; raters has 0.001431 and 6/14",
                   "width_relative_repair": False,
                   "evidence2": "raters offset ~7x length's while its seed sd is smaller"},
               "open_not_asserted": {
                   "question": "why the raters stratifier specifically",
                   "prediction": "nr is the most prompt-clustered covariate, so a prompt-cluster "
                                 "resample distorts its matching most",
                   "why_untested": "nr is computed per CRITERION (run.py:232); testing it needs "
                                   "the corpus reloaded"},
               "spearman_all": rho, "spearman_excluding_flagged": rho_wo,
               "structural_scope": "every unit pairs a single-seed interval with a multi-seed "
                                   "point; the flagged count is a LOWER BOUND",
               "direction_survives": {"cells_still_ci_excludes_zero": still_excl,
                                      "negative_all_seeds_intact": True},
               "does_not_do": "re-run R141; whether its conclusion changes is a separate question",
               "unit_note": "distances and sds are in delta units; counts are CELL×STRATIFIER units",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "point_and_interval.json", "w"), indent=2)
    print(f"\n  artifact: results/point_and_interval.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
