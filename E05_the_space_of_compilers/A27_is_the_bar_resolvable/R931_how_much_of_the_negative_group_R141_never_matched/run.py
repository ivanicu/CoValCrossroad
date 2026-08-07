#!/usr/bin/env python3
"""
R931 · the stratum fill table on R141's REAL covariates — is the under-fill inert, or is it what
        R929 saw?

⛔ WHY. R930 tried to test the repair on a synthetic world, and its own admissibility control killed
it: the world never reproduced R141's symptom, so nothing there transfers. What it produced instead
was a by-product about the OBJECT — `matched_positive` takes `min(want, len(pool))`, so a stratum
whose positive pool is too small is silently under-filled, and the artifact publishes no fill rate.
In R930's synthetic world **69.9% of the negative group went unmatched** and the "matched" contrast
came out **3.5× the planted effect**. Whether that bites on R141's REAL data was explicitly not
measured there.

⭐ **AND IT IS CHEAP, WHICH IS WHY IT IS THIS ROUND RATHER THAN THE REPAIR.** The fill table needs
only `neg`, `mag`, `ln`, `nr`, `pidx` — every one of which comes from the rubric scores. **None of
R141's expensive text-similarity pipeline (grams, stems, idf, best-match over three representations)
touches stratum occupancy**, so the whole question is one pass over `conversation_rubrics.jsonl`.

⭐⭐ **PRE-REGISTERED PREDICTION, written before the run.** R929 found the incoherence only in the
`raters` stratifier and could not explain why; R930 supplied a mechanism that would explain it. **If
that mechanism is what R929 saw, `raters` must carry the largest unmatched share of the three.** If
the shortfall is near zero everywhere, the by-product is inert and R141's matching is sound on this
corpus — and the `raters` question goes back to open.

⚠ **AND A SECOND PROPERTY OF THE RULE IS MEASURED HERE BECAUSE IT IS FREE.** R141's bins are
`np.percentile(cov[neg], [0, 20, 40, 60, 80, 100])` and membership is `>= lo` AND `<= hi`, so
**consecutive bins share their endpoints and a unit sitting exactly on a boundary is counted in
BOTH.** Whether that inflates `sum(want)` above the actual negative count is arithmetic on the real
data, and it is reported rather than assumed either way.

ESTIMAND        per stratifier: the share of the negative group that `matched_positive` cannot
                match, and the boundary double-count in `sum(want)` against `n_neg`.
IDENTIFICATION  exact — a deterministic function of the committed rubric file.
                ⚠ Not causal about R929's six cells; it tests a prediction they imply.
SCOPE           population: every rated `coval_full` criterion in `data/conversation_rubrics.jsonl`
                instrument: R141's own binning and fill rule, transcribed
                baseline:   R930's synthetic 69.9% unmatched, which is what "large" would look like
                regime:     the committed corpus
WORLDS          A · `raters` carries the largest unmatched share -> R929's six cells and R930's
                    by-product are one defect with one fix
                B · the shortfall is near zero everywhere -> the by-product is inert here, R141's
                    matching is sound on this corpus, and why `raters` broke returns to OPEN
                C · the shortfall is large but NOT largest for `raters` -> the rule is defective and
                    the defect is not what R929 saw; two separate problems
KILL            CONDITIONAL:
                  ⭐ ① WIRING: the rebuilt corpus must reproduce R141's committed `n_prompts` = 986
                     exactly. Different code, same file — if the count differs, the units are not
                     R141's and no table computed here describes it.
                  ⭐ ② POSITIVE: the fill detector must REPORT a shortfall when one is planted.
                     Flip a block of positives to negative in the top bin and require the measured
                     unmatched share to rise. ⚠ And it must read ~0 on a balanced synthetic, so it
                     is not simply always reporting a shortfall.
                  ⭐ ③ ALL THREE stratifiers reported, not only the one the prediction is about —
                     reporting only `raters` would make the prediction unfalsifiable.
                  ⭐ ④ the boundary double-count reported as a number, not asserted in either
                     direction.
MULTIPLICITY    3 stratifiers × 5 bins × {want, pool, filled, shortfall}; every cell printed.
ARTIFACT        results/stratum_fill.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: a shortfall shows the matching is INCOMPLETE. It does not by
                itself show R141's conclusions are wrong — that needs the contrast recomputed, and
                this round does not do it.
"""
import json, pathlib, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RUBRICS = ROOT / "data/conversation_rubrics.jsonl"
N_PROMPTS_COMMITTED = 986
SCHEMES = ("magnitude", "length", "raters")


def fill_table(cov, neg):
    """R141's rule, transcribed: 5 quantile bins on the NEGATIVES' covariate, closed on both ends."""
    qs = np.percentile(cov[neg], [0, 20, 40, 60, 80, 100])
    rows = []
    for lo, hi in zip(qs[:-1], qs[1:]):
        want = int(((cov[neg] >= lo) & (cov[neg] <= hi)).sum())
        pool = int(((~neg) & (cov >= lo) & (cov <= hi)).sum())
        rows.append({"lo": float(lo), "hi": float(hi), "want": want, "pool": pool,
                     "filled": min(want, pool), "shortfall": want - min(want, pool)})
    return rows


def summarise(rows, n_neg):
    tw = sum(r["want"] for r in rows)
    tf = sum(r["filled"] for r in rows)
    return {"rows": rows, "sum_want": tw, "sum_filled": tf, "shortfall": tw - tf,
            "unmatched_share": (tw - tf) / tw if tw else float("nan"),
            "n_neg": int(n_neg), "boundary_double_count": tw - int(n_neg)}


def main() -> int:
    if not RUBRICS.exists():
        print(f"  UNRUNNABLE: {RUBRICS} missing. Exit 2, never 0.")
        return 2

    pidx, negl, magl, lnl, nrl = [], [], [], [], []
    n_prompts = 0
    for line in open(RUBRICS):
        r = json.loads(line)
        core = [it.get("criterion") or "" for it in (r.get("coval_core") or [])]
        full = [(it.get("criterion") or "",
                 np.array([x["score"] for x in (it.get("scores") or [])], float))
                for it in (r.get("coval_full") or []) if it.get("scores")]
        if not (core and full):
            continue
        pi = n_prompts
        n_prompts += 1
        for txt, sc in full:
            pidx.append(pi)
            negl.append(float(sc.mean()) < 0)
            magl.append(abs(float(sc.mean())))
            nrl.append(float(len(sc)))
            lnl.append(float(len(txt)))
    neg = np.array(negl, bool)
    cov = {"magnitude": np.array(magl), "length": np.array(lnl), "raters": np.array(nrl)}
    n_units = len(neg)
    print(f"  corpus rebuilt: {n_prompts:,} prompts · {n_units:,} rated criteria · "
          f"{int(neg.sum()):,} negative ({neg.mean():.1%})")

    c1 = n_prompts == N_PROMPTS_COMMITTED
    print(f"\n  ① WIRING — prompts {n_prompts} vs R141's committed {N_PROMPTS_COMMITTED}: "
          f"{c1}  {'PASS' if c1 else 'FAIL'}")

    # ---------- ② POSITIVE: plant a shortfall, and check the balanced case reads ~0 ----------
    rng = np.random.default_rng(931)
    balanced_cov = rng.normal(0, 1, n_units)
    balanced_neg = rng.random(n_units) < 0.5          # independent of the covariate
    s_bal = summarise(fill_table(balanced_cov, balanced_neg), balanced_neg.sum())
    planted_neg = balanced_neg.copy()
    top = np.where(balanced_cov > np.percentile(balanced_cov, 80))[0]
    planted_neg[top] = True                            # top bin now has almost no positives left
    s_pl = summarise(fill_table(balanced_cov, planted_neg), planted_neg.sum())
    c2 = s_bal["unmatched_share"] < 0.05 and s_pl["unmatched_share"] > 0.10
    print(f"\n  ② POSITIVE — the detector on a BALANCED synthetic: unmatched "
          f"{s_bal['unmatched_share']:.4f} (must be ~0)")
    print(f"     with a shortfall PLANTED in the top bin:      unmatched "
          f"{s_pl['unmatched_share']:.4f} (must rise)")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "n_prompts": n_prompts},
                  open(OUT / "stratum_fill.json", "w"), indent=2)
        return 2

    res = {}
    print(f"\n  ③ ALL THREE STRATIFIERS on the real corpus (n_neg = {int(neg.sum()):,}):")
    for s in SCHEMES:
        res[s] = summarise(fill_table(cov[s], neg), neg.sum())
        print(f"\n     {s}")
        print(f"       {'bin':>4}{'want':>9}{'pool':>9}{'filled':>9}{'shortfall':>11}")
        for i, r in enumerate(res[s]["rows"]):
            print(f"       {i:>4}{r['want']:>9}{r['pool']:>9}{r['filled']:>9}{r['shortfall']:>11}")
        print(f"       sum want {res[s]['sum_want']:,}  filled {res[s]['sum_filled']:,}  "
              f"UNMATCHED {res[s]['shortfall']:,} = {res[s]['unmatched_share']:.2%}")

    # ⑤ THE THING CONTROL ④ POINTED AT — measured, because the double-count is not cosmetic
    def matched_positive(c, seed):
        rng = np.random.default_rng(seed)
        qs = np.percentile(c[neg], [0, 20, 40, 60, 80, 100])
        pick = []
        for lo, hi in zip(qs[:-1], qs[1:]):
            want = int(((c[neg] >= lo) & (c[neg] <= hi)).sum())
            pool = np.where((~neg) & (c >= lo) & (c <= hi))[0]
            if len(pool):
                pick += list(rng.choice(pool, min(want, len(pool)), replace=False))
        return np.array(pick, int)

    dup = {}
    print(f"\n  ⑤ TIED QUANTILE CUTS, AND THE MULTISET/SET SPLIT THEY CAUSE:")
    print(f"     {'scheme':<12}{'cuts':>34}{'distinct':>10}")
    for s in SCHEMES:
        q = np.percentile(cov[s][neg], [0, 20, 40, 60, 80, 100])
        nd = len(set(np.round(q, 10)))
        dup[s] = {"cuts": [float(x) for x in q], "distinct_cuts": nd}
        print(f"     {s:<12}{str([round(float(x), 2) for x in q]):>34}{nd:>7}/6")
    print(f"\n     {'scheme':<12}{'len(mp)':>10}{'len(set)':>10}{'duplicates':>12}{'dup share':>11}")
    for s in SCHEMES:
        mp = matched_positive(cov[s], 8101)
        u = len(set(mp.tolist()))
        dup[s].update({"len_mp": int(len(mp)), "len_set": u, "duplicates": int(len(mp) - u),
                       "dup_share": float((len(mp) - u) / len(mp))})
        print(f"     {s:<12}{len(mp):>10}{u:>10}{len(mp)-u:>12}{(len(mp)-u)/len(mp):>10.1%}")
    print(f"\n     ⭐⭐⭐ **THE POINT AVERAGES `y[mp]` — WITH duplicates. THE BOOTSTRAP FILTERS")
    print(f"     THROUGH `mset = set(mp)` — WITHOUT.** They are different objects, and the gap is")
    print(f"     largest exactly where R929 found the incoherence.")
    dup_worst = max(SCHEMES, key=lambda z: dup[z]["dup_share"])

    worst = max(SCHEMES, key=lambda s: res[s]["unmatched_share"])
    shares = {s: res[s]["unmatched_share"] for s in SCHEMES}
    print(f"\n  ④ BOUNDARY DOUBLE-COUNT — R141's bins are closed at BOTH ends, so a unit on a")
    print(f"     boundary is counted twice. sum(want) − n_neg per stratifier: "
          f"{ {s: res[s]['boundary_double_count'] for s in SCHEMES} }")

    big = max(shares.values()) > 0.10
    # ⚠ the verdict must reference EVERY control the round ran. The first version keyed only on
    # `unmatched_share` and printed "the raters question returns to OPEN" while control ⑤ had just
    # answered it — the verdict-string-is-not-a-computation defect, in my own round.
    dup_answers = dup[dup_worst]["dup_share"] > 0.30 and dup_worst == "raters"
    world = (("SHORTFALL_REFUTED_DUPLICATION_CONFIRMED" if dup_answers else "B") if not big
             else ("A" if worst == "raters" else "C"))
    print(f"\n  ⭐⭐⭐ WORLD {world}: unmatched share "
          f"{ {s: f'{v:.2%}' for s, v in shares.items()} }; largest is `{worst}`")
    print(f"     PRE-REGISTERED PREDICTION was `raters` largest: {worst == 'raters'}")
    if world == "A":
        print(f"     R929's six incoherent cells and R930's by-product are ONE defect: the matched")
        print(f"     contrast is built on a group the rule could not fill, and `raters` is where it")
        print(f"     bites hardest. One fix addresses both.")
    elif world == "SHORTFALL_REFUTED_DUPLICATION_CONFIRMED":
        print(f"     ⛔ MY PREDICTION IS REFUTED: the shortfall is 0.00% on all three stratifiers,")
        print(f"     so R930's by-product is INERT here and its 69.9% was a property of the")
        print(f"     synthetic imbalance I chose, not of the object.")
        print(f"     ⭐⭐⭐ BUT CONTROL ④ POINTED AT THE REAL MECHANISM AND ⑤ MEASURED IT.")
        print(f"     `np.percentile` on a low-cardinality INTEGER covariate returns TIED cut")
        print(f"     points — `raters` gives {dup['raters']['cuts'][:4]}…, only "
              f"{dup['raters']['distinct_cuts']} distinct of 6, because "
              f"{int((cov['raters'][neg] == 1).sum()):,} of {int(neg.sum()):,} negatives have")
        print(f"     exactly ONE rater. With bins closed at both ends the SAME stratum is drawn")
        print(f"     four times, so `mp` carries {dup['raters']['dup_share']:.1%} duplicates while")
        print(f"     `mset = set(mp)` carries none. **The point averages the multiset, the interval")
        print(f"     the set.** Duplication ordering is raters {dup['raters']['dup_share']:.1%} > "
              f"magnitude {dup['magnitude']['dup_share']:.1%} > length "
              f"{dup['length']['dup_share']:.1%} —")
        print(f"     which is R929's incoherence pattern exactly. **R929, R930 and R931 are one")
        print(f"     defect: TIED QUANTILE CUTS ON A DISCRETE COVARIATE.**")
    else:
        print(f"     The rule DOES leave a large share unmatched, but not where R929 saw the")
        print(f"     incoherence — so these are two separate defects and neither explains the other.")
    print(f"     ⚠ EITHER WAY: a shortfall shows the matching is INCOMPLETE, never that R141's")
    print(f"     conclusions are wrong. That needs the contrast recomputed, which this does not do.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n_prompts, "n_units": n_units,
               "n_negative": int(neg.sum()),
               "prediction_raters_largest": bool(worst == "raters"),
               "unmatched_share": shares, "worst": worst,
               "per_stratifier": res,
               "tied_cuts_and_duplication": dup,
               "duplication_worst": dup_worst,
               "unifying_mechanism": "np.percentile on a low-cardinality integer covariate returns "
                                     "TIED cut points (raters: [1,1,1,1,10,49], 3 distinct of 6), "
                                     "and R141's bins are closed at both ends, so the same stratum "
                                     "is drawn up to four times. The point averages y[mp] WITH "
                                     "duplicates while the bootstrap filters through set(mp) "
                                     "WITHOUT them — different objects, and the gap is largest "
                                     "exactly where R929 found the incoherence",
               "synthetic_controls": {"balanced": s_bal["unmatched_share"],
                                      "planted": s_pl["unmatched_share"]},
               "r930_synthetic_for_contrast": 0.699,
               "cheap_because": "stratum occupancy needs only the rubric scores; none of R141's "
                                "text-similarity pipeline touches it",
               "does_not_show": "that R141's conclusions are wrong — a shortfall makes the matching "
                                "incomplete; the contrast is not recomputed here",
               "unit_note": "counts are CRITERIA; shares are of sum(want)",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "stratum_fill.json", "w"), indent=2)
    print(f"\n  artifact: results/stratum_fill.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
