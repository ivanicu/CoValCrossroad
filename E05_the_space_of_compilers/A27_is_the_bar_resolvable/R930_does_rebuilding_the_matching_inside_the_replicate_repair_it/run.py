#!/usr/bin/env python3
"""
R930 · the synthetic world R929's mechanism predicts — does rebuilding the matching inside each
        bootstrap replicate restore coverage, and does prompt-clustering of the covariate decide
        which stratifier breaks?

⛔ WHY, AND WHY NOT ON R141's OWN DATA. R929 established from the source that R141's interval and
its point estimate different quantities: `matched_positive` builds a covariate-matched positive set,
and the bootstrap then resamples PROMPT CLUSTERS and keeps `[i for i in sel if i in mset]`, which
does not preserve the matching. My NEXT proposed re-running `finding_A` with the matching rebuilt
inside each replicate. **That would show whether the numbers move; it could not show whether the
repair is CORRECT, because R141's real data has no ground truth and coverage is undefined without
one.** So the world the mechanism predicts is built here instead — §3's ladder step 4 — where the
true matched effect is known by construction and coverage is measurable.

⭐⭐ **AND IT MAKES R929's OPEN QUESTION ANSWERABLE.** R929 left "why `raters` and not the others"
open, because testing it on the real corpus needs `nr` reloaded. The natural prediction is that a
prompt-cluster resample distorts a PROMPT-CLUSTERED covariate's balance most. Here the covariate's
intraclass correlation is a **swept axis**, so the prediction is tested directly rather than
asserted — and if the damage does not grow with clustering, that explanation dies too.

⛔ **THE FIRST WORLD I BUILT HAD NO GROUND TRUTH, AND ITS OWN CONTROLS SAID SO.** `x` was
continuous and `P(neg)` depended on it continuously, so quantile-bin matching leaves RESIDUAL
CONFOUNDING INSIDE EACH BIN: the negatives sit higher on `x` than their matched positives even
within a bin. **The covariate-matched difference is therefore not `effect`, and coverage of `effect`
came back ~0.00–0.05 for BOTH estimators** — I had asserted a ground truth the design does not
deliver, which is §4's *"the control targets a different statistic than the one being reported"*,
committed for the third time this session. Control ③ (placebo coverage must reach nominal) and
control ① (the symptom must appear) both fired, which is the only reason it did not get reported.
**Repaired by making `x` DISCRETE with `NLEV` levels and matching ON THE LEVEL**, so the matching is
EXACT and the matched estimand is `effect` by construction, with nothing left inside a bin to
confound it.

⛔⛔ **AND THE DISCRETE REPAIR DID NOT FIX IT EITHER — SO I STOPPED, BECAUSE A THIRD PATCH WOULD BE
FITTING A WORLD UNTIL A CONTROL PASSES**, which is the failure this file spends its length
cataloguing. Coverage stayed at 0.000 for both estimators. The cause, MEASURED rather than guessed:
`matched_positive` takes `min(want, len(pool))`, so wherever negatives outnumber positives in a
stratum it **silently under-fills**. In this world at icc 0.3 the per-level table is
`want 5/23/59/126/142` against `pool 139/121/85/18/2`, i.e. **248 of 355 negatives — 69.9% — go
unmatched**, and the rule's contrast comes out **+1.7362 against a planted +0.5000**, inflated 3.5×
by exactly the confounding the matching exists to remove.

⭐⭐⭐ **SO THIS ROUND IS UNVERIFIED ON ITS OWN QUESTION AND THE VERDICT SAYS SO.** Control ① is the
admissibility gate — the synthetic world never reproduced R141's symptom, so **nothing measured here
transfers to R141's intervals, and the repair question is untouched.** What the failure produced
instead is a second, cheaper finding about the object: **R141's matcher has no balance check and
publishes no fill rate**, so a stratum it could not fill is indistinguishable in the artifact from
one it filled exactly. Whether that bites on R141's real data is a one-pass question on the corpus
and is NOT answered here.

⚠ **WHAT A SYNTHETIC WORLD CANNOT DO**, stated before the result: it cannot show that R141's real
`raters` covariate IS strongly prompt-clustered. It can only show whether clustering is the kind of
thing that produces this failure. Confirming it for R141 still needs the corpus.

ESTIMAND        for each estimator and each covariate ICC: the empirical coverage of the TRUE
                matched effect, and the rate at which the published point falls outside its own
                published interval.
IDENTIFICATION  exact by construction — the data-generating process defines the true matched effect.
SCOPE           population: synthetic prompts × criteria with a planted matched effect
                instrument: the two interval constructions, committed and repaired
                baseline:   the committed construction, transcribed from `R141_verification/run.py`
                regime:     P prompts × C criteria, NBOOT replicates, REPS repetitions, seed 930
WORLDS          A · the repair restores coverage and the committed one is under-covering -> R141's
                    intervals are wrong in a way a rebuild fixes, and the fix is worth running
                B · both cover -> the mismatch is cosmetic and the six flagged cells are a display
                    artifact, not an estimator defect
                C · neither covers -> the cluster bootstrap is the wrong null for this contrast at
                    all, and rebuilding the matching does not save it
KILL            CONDITIONAL:
                  ⭐ ① SYMPTOM REPRODUCED: the committed estimator must produce points outside
                     their own intervals at a rate > 0 while the repaired one does so far less
                     often. **If the synthetic world does not reproduce the symptom, it is not a
                     model of R141 and nothing measured here transfers** — this is the control that
                     makes the whole round admissible.
                  ⭐ ② POSITIVE: at a large planted effect both estimators' intervals must exclude
                     zero, so neither is simply blind.
                  ⭐ ③ PLACEBO: at a planted effect of exactly zero the REPAIRED estimator's
                     coverage must be near its nominal 95%. A coverage number from an estimator
                     never shown to hit nominal anywhere is not a measurement.
                  ⭐ ④ the ICC sweep must MOVE something. If coverage is flat in ICC the sweep has
                     no power and the clustering explanation is neither supported nor refuted —
                     that must be said rather than read as support.
MULTIPLICITY    |ICC| × |effect| × 2 estimators × {coverage, outside-rate}; every cell printed.
ARTIFACT        results/matching_repair.json
IMPOSSIBLE      cross-release · construct validated · independently replicated. ⚠ AND, named
                because it is the tempting overreach: this cannot establish that R141's `raters`
                covariate is prompt-clustered, only whether clustering produces this failure mode.
"""
import json, pathlib, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

SEED, P, C, NBOOT, REPS, NLEV = 930, 60, 12, 300, 120, 5
ICCS = (0.0, 0.3, 0.6, 0.9)
EFFECTS = (0.0, 0.5)
MSEEDS = (0, 1, 2, 3, 4)          # the five matching seeds R141 averages over


def make_world(rng, icc, effect):
    """`x` is DISCRETE with NLEV levels and intraclass correlation `icc`. Matching on the LEVEL is
    exact, so the covariate-matched difference is `effect` by construction — see the repair note."""
    pidx = np.repeat(np.arange(P), C)
    u = rng.normal(0, 1, P)[pidx]
    e = rng.normal(0, 1, P * C)
    lat = np.sqrt(icc) * u + np.sqrt(1 - icc) * e
    cuts = np.percentile(lat, np.linspace(0, 100, NLEV + 1)[1:-1])
    x = np.digitize(lat, cuts).astype(float)               # 0..NLEV-1, exact bins
    pneg = 1 / (1 + np.exp(-(1.6 * (x - (NLEV - 1) / 2))))  # negatives concentrate at high levels
    neg = rng.random(P * C) < pneg
    y = 1.2 * x + effect * neg + rng.normal(0, 1.0, P * C)  # 1.2*x is the confound
    return pidx, x, neg.astype(bool), y


def matched_positive(rng, x, neg):
    """R141's rule with the bins made EXACT: one stratum per discrete level, so within a stratum
    there is nothing left to confound. Same shape as `R141_verification/run.py:243-253`."""
    pick = []
    for lev in range(NLEV):
        want = int(((x == lev) & neg).sum())
        pool = np.where((~neg) & (x == lev))[0]
        if len(pool) and want:
            pick += list(rng.choice(pool, min(want, len(pool)), replace=False))
    return np.array(pick, int)


def one_rep(rng, icc, effect):
    pidx, x, neg, y = make_world(rng, icc, effect)
    ds = [y[neg].mean() - y[matched_positive(np.random.default_rng(SEED + s), x, neg)].mean()
          for s in MSEEDS]
    point = float(np.mean(ds))

    up = np.unique(pidx)
    mp = matched_positive(np.random.default_rng(SEED + MSEEDS[0]), x, neg)
    mset = set(mp.tolist())
    bs_committed, bs_repaired = [], []
    for _ in range(NBOOT):
        take = rng.integers(0, len(up), len(up))
        sel = np.concatenate([np.where(pidx == up[j])[0] for j in take])
        sn = sel[neg[sel]]
        # COMMITTED: filter the resample through the FIXED matched set (R141 as written)
        sm = np.array([i for i in sel if i in mset], int)
        if len(sn) > 20 and len(sm) > 20:
            bs_committed.append(y[sn].mean() - y[sm].mean())
        # REPAIRED: rebuild the matching INSIDE the replicate
        if len(sn) > 20:
            sub_x, sub_neg = x[sel], neg[sel]
            loc = matched_positive(rng, sub_x, sub_neg)
            if len(loc) > 20:
                bs_repaired.append(y[sn].mean() - y[sel[loc]].mean())

    def ci(b):
        return (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))) if len(b) > 30 \
            else (float("nan"), float("nan"))
    return point, ci(bs_committed), ci(bs_repaired)


def main() -> int:
    rows = []
    for icc in ICCS:
        for eff in EFFECTS:
            rng = np.random.default_rng(SEED + int(icc * 100) * 7 + int(eff * 10))
            cov = {"committed": 0, "repaired": 0}
            outside = {"committed": 0, "repaired": 0}
            excl0 = {"committed": 0, "repaired": 0}
            n = 0
            for _ in range(REPS):
                pt, cc, cr = one_rep(rng, icc, eff)
                if not np.isfinite(cc[0]) or not np.isfinite(cr[0]):
                    continue
                n += 1
                for name, c in (("committed", cc), ("repaired", cr)):
                    cov[name] += int(c[0] <= eff <= c[1])
                    outside[name] += int(pt < c[0] or pt > c[1])
                    excl0[name] += int(c[1] < 0 or c[0] > 0)
            if n == 0:
                continue
            rows.append({"icc": icc, "effect": eff, "n_reps": n,
                         "coverage": {k: cov[k] / n for k in cov},
                         "outside_rate": {k: outside[k] / n for k in outside},
                         "excludes_zero": {k: excl0[k] / n for k in excl0}})
            print(f"  icc {icc:<5} effect {eff:<5} n {n:<5} "
                  f"coverage committed {cov['committed']/n:.3f} repaired {cov['repaired']/n:.3f}  "
                  f"outside committed {outside['committed']/n:.3f} repaired "
                  f"{outside['repaired']/n:.3f}")
    if not rows:
        print("  UNRUNNABLE: no usable repetitions. Exit 2, never 0.")
        return 2

    # ---------- ① SYMPTOM REPRODUCED ----------
    oc = max(r["outside_rate"]["committed"] for r in rows)
    orp = max(r["outside_rate"]["repaired"] for r in rows)
    c1 = oc > 0.05 and oc > 2 * max(orp, 1e-9)
    print(f"\n  ① SYMPTOM REPRODUCED — max point-outside-its-own-interval rate: "
          f"committed {oc:.3f}, repaired {orp:.3f}")
    print(f"     the synthetic world must show R141's symptom or nothing here transfers: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")

    # ---------- ② POSITIVE ----------
    big = [r for r in rows if r["effect"] == max(EFFECTS)]
    c2 = all(r["excludes_zero"]["committed"] > 0.5 and r["excludes_zero"]["repaired"] > 0.5
             for r in big)
    print(f"\n  ② POSITIVE — at effect {max(EFFECTS)} both must exclude zero most of the time:")
    for r in big:
        print(f"     icc {r['icc']:<5} committed {r['excludes_zero']['committed']:.3f}  "
              f"repaired {r['excludes_zero']['repaired']:.3f}")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL — an estimator that never fires proves nothing'}")

    # ---------- ③ PLACEBO ----------
    zero = [r for r in rows if r["effect"] == 0.0]
    best = max(r["coverage"]["repaired"] for r in zero)
    c3 = best >= 0.85
    print(f"\n  ③ PLACEBO — at a planted effect of exactly 0 the REPAIRED estimator's coverage:")
    for r in zero:
        print(f"     icc {r['icc']:<5} repaired {r['coverage']['repaired']:.3f}   "
              f"committed {r['coverage']['committed']:.3f}")
    print(f"     ③ reaches nominal somewhere ({best:.3f} >= 0.85): {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")

    # ---------- ④ THE SWEEP MUST MOVE SOMETHING ----------
    span = max(r["coverage"]["committed"] for r in rows) - \
        min(r["coverage"]["committed"] for r in rows)
    c4 = span > 0.05
    print(f"\n  ④ THE ICC SWEEP MUST MOVE SOMETHING — committed coverage spans {span:.3f} "
          f"across icc: {c4}  {'PASS' if c4 else 'FAIL — the sweep has no power'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        # persist the by-product: the stratum fill table that explains the zero coverage
        rr = np.random.default_rng(SEED)
        pidx, x, neg, _y = make_world(rr, 0.3, 0.5)
        fill = [{"level": lev,
                 "want": int(((x == lev) & neg).sum()),
                 "pool": int(((x == lev) & ~neg).sum())} for lev in range(NLEV)]
        for f in fill:
            f["filled"] = min(f["want"], f["pool"])
            f["shortfall"] = f["want"] - f["filled"]
        tw = sum(f["want"] for f in fill); tf = sum(f["filled"] for f in fill)
        print(f"\n  ⭐ BY-PRODUCT, measured: R141's `min(want, len(pool))` under-fills strata "
              f"silently.")
        print(f"     {'level':>6}{'want':>7}{'pool':>7}{'filled':>8}{'shortfall':>11}")
        for f in fill:
            print(f"     {f['level']:>6}{f['want']:>7}{f['pool']:>7}{f['filled']:>8}"
                  f"{f['shortfall']:>11}")
        print(f"     total wanted {tw}, filled {tf}, UNMATCHED {tw-tf} = {100*(tw-tf)/tw:.1f}%")
        print(f"     ⚠ this is THIS world's imbalance, faithfully transcribed from R141's rule. "
              f"Whether R141's real strata are this unbalanced is NOT measured here.")
        json.dump({"verdict": "UNVERIFIED",
                   "why": "control ① is the admissibility gate: the synthetic world never "
                          "reproduced R141's symptom, so nothing here transfers and the repair "
                          "question is untouched",
                   "c1": c1, "c2": c2, "c3": c3, "c4": c4, "rows": rows,
                   "byproduct_stratum_fill": {"table": fill, "wanted": tw, "filled": tf,
                                              "unmatched_share": (tw - tf) / tw},
                   "byproduct_claim": "R141's matcher takes min(want, len(pool)) and publishes no "
                                      "fill rate, so an unfillable stratum is indistinguishable "
                                      "in the artifact from a fully matched one",
                   "not_measured": "whether R141's real strata are unbalanced enough for this to "
                                   "bite — one pass over the corpus would settle it",
                   "two_dgp_repairs_then_stop": "a third patch would be fitting the world until a "
                                                "control passes"},
                  open(OUT / "matching_repair.json", "w"), indent=2)
        return 2

    gain = [(r["icc"], r["effect"],
             r["coverage"]["repaired"] - r["coverage"]["committed"]) for r in rows]
    trend = [r["coverage"]["committed"] for r in sorted(rows, key=lambda z: z["icc"])
             if r["effect"] == 0.0]
    monotone_down = all(trend[i] >= trend[i + 1] for i in range(len(trend) - 1))
    world = "A" if all(g[2] >= 0 for g in gain) and max(g[2] for g in gain) > 0.05 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: coverage gain from rebuilding the matching, per cell:")
    for icc, eff, g in gain:
        print(f"     icc {icc:<5} effect {eff:<5} repaired − committed = {g:+.3f}")
    print(f"\n     ⭐ AND R929's OPEN QUESTION, tested rather than asserted: committed coverage "
          f"across icc {[f'{t:.3f}' for t in trend]} — monotone worsening with clustering: "
          f"{monotone_down}")
    print(f"     ⚠ this shows whether CLUSTERING produces the failure. It does NOT show that "
          f"R141's `raters` covariate is clustered; that still needs the corpus.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED,
               "design": {"prompts": P, "criteria_per_prompt": C, "nboot": NBOOT, "reps": REPS,
                          "iccs": list(ICCS), "effects": list(EFFECTS)},
               "why_not_on_R141": "R141's real data has no ground truth, so coverage — the "
                                  "property that decides whether the repair is CORRECT rather "
                                  "than merely different — is undefined there",
               "rows": rows, "coverage_gain": [list(g) for g in gain],
               "committed_coverage_by_icc_at_zero": trend,
               "monotone_worsening_with_clustering": monotone_down,
               "cannot_say": "that R141's `raters` covariate is prompt-clustered — only whether "
                             "clustering produces this failure mode",
               "unit_note": "coverage and rates are shares of repetitions",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "matching_repair.json", "w"), indent=2)
    print(f"\n  artifact: results/matching_repair.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
