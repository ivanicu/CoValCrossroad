#!/usr/bin/env python3
"""
R932 · recompute R141's 42 cells with the tie repaired — how much did the duplicated strata move
        the numbers, and does `length` stay still?

⛔ WHY. R931 established the mechanism: `np.percentile` on a low-cardinality integer covariate
returns TIED cut points (`raters` → `[1, 1, 1, 1, 10, 49]`, 3 distinct of 6, because 3,015 of 3,905
negatives have exactly one rater), and R141's bins are closed at BOTH ends, so the same stratum is
drawn up to four times. `mp` carries **45.7% duplicates** for `raters`, 14.2% for `magnitude`, 1.8%
for `length` — the ordering of R929's incoherence exactly. What nobody has measured is **what it
cost the numbers.**

⭐ **THE FIX IS MINIMAL AND ITS PLACEBO IS BUILT IN.** My first instinct — "use the covariate's
distinct VALUES as strata" — is wrong for a near-continuous covariate: `length` has hundreds of
distinct values and would become hundreds of strata, which is a different estimator, not a repair.
**The minimal fix is to DEDUPE THE CUT POINTS.** For `raters` that collapses `[1,1,1,1,10,49]` to
`[1,10,49]`; for `length`, whose six cuts are already distinct, it changes **nothing at all**.
**So `length` is a placebo the design cannot avoid running: if `length` moves, the tie story is
incomplete and something else is also wrong.**

⭐⭐ **AND THE CLOSED-BOTH-ENDS BOUNDARY IS A SECOND, SEPARABLE CHOICE**, so both are swept rather
than bundled: `dedupe only`, and `dedupe + half-open bins` (`[lo, hi)` except the last). Reporting
one would hide which change did the work.

⚠ **NOT FORCED, checked before running.** Under the tied rule `mp` is roughly 85–93% one-rater
positives; under deduped cuts the strata are weighted by the negatives, which are 3,015/3,905 =
**77.2%** one-rater. So the reweighting is real but its MAGNITUDE is not determined by the algebra —
it depends on how the outcome differs between one-rater and many-rater positives, which is a fact
about the corpus.

⛔ **AND I STILL RECONSTRUCTED THE LOOP INSTEAD OF TRANSCRIBING IT — CAUGHT BY THE WIRING CONTROL
BEFORE A SINGLE NUMBER.** My first version built **15 cells and 15,248 units** against R141's **14
cells**, because it dropped two guards that are plainly in the source:
`if len(F["stem_token"]) < 3: continue` (a UNIT filter) and
`if rep == "char3gram" and mn == "idf_weighted": continue` (idf on character 3-grams is meaningless,
since the idf table is built over words). This is the same defect as the earlier from-memory imports:
**I read the call and rebuild the loop, and the guards are exactly what a rebuild loses.**
⛔ **AND THEN A THIRD TIME, ON THE SAME ROUND.** With the guards restored, wiring still failed —
and ONLY on the five `idf_weighted` cells, which localised it precisely. R141 builds its `idf` table
over `core + full` criteria and over **STEMMED** tokens; mine used `full` only and RAW words. Two
more reconstructions of a loop that was three lines away. **The pattern is now unambiguous: every
time I rebuild rather than transcribe, the loss is a filter or a normalisation, never the arithmetic
— and the wiring control is the only thing that has ever caught it.**
⚠ **AND IT SCOPES R931 RETROACTIVELY:** R931's fill table counted 3,905 negatives WITHOUT the
`stem_token < 3` filter, so it ran on a slightly WIDER population than R141's. The tied-cut finding
is unaffected — the cut points come from the same covariate and the tie is 3,015 one-rater negatives
against 6 boundaries — but the exact counts in R931 are for the unfiltered corpus and are labelled
as such here rather than left to be discovered.

⚠ **AND R141's OWN HELPERS ARE IMPORTED, NOT RE-IMPLEMENTED.** `strip_neg`, `words`, `stem`,
`grams` and `METRICS` are read from `R141_verification/run.py` by path, so the recomputation is
definitionally the same instrument — re-typing them is how the from-memory-symbol defect gets in.

ESTIMAND        per (cell × stratifier): `delta_mean` under R141's rule and under each repair, and
                the shift between them.
IDENTIFICATION  exact — a deterministic function of the committed corpus and the stated rule.
                ⚠ Intervals are NOT recomputed here; this is about the POINT estimate only.
SCOPE           population: every rated `coval_full` criterion, R141's own unit definition
                instrument: R141's imported similarity metrics; matching seeds `SEEDS` as committed
                baseline:   R141's committed `finding_A.cells[*][scheme].delta_mean`
                regime:     the committed corpus
WORLDS          A · `raters` moves materially, `magnitude` a little, `length` not at all -> the tie
                    is the whole story and the repair is well-targeted
                B · `length` moves too -> the tie story is incomplete; something else is also wrong
                C · nothing moves anywhere -> the duplication is arithmetically inert on this
                    outcome and R929's incoherence needs a different explanation again
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce R141's committed `delta_mean` for all 42 cells under the
                     UNCHANGED rule, to 1e-9. Same seeds, imported helpers. **If the baseline does
                     not reproduce, nothing computed here describes R141** and the round stops.
                  ⭐ ② PLACEBO, and it is structural: `length`'s six cuts are already distinct, so
                     `dedupe only` must leave every `length` cell BIT-IDENTICAL. A repair that
                     moves a cell it cannot logically touch is a bug in the repair.
                  ⭐ ③ the two repairs are reported SEPARATELY, so it is visible which change did
                     the work rather than attributing both to one.
                  ⭐ ④ all 42 cells reported, including those that do not move.
MULTIPLICITY    14 cells × 3 stratifiers × 3 rules; every cell printed; shifts summarised per
                stratifier.
ARTIFACT        results/tie_repair_shift.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: the INTERVALS are not recomputed, so whether `ci[1] < 0` still
                holds is not answered here — only how far the points move.
"""
import importlib.util, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
R141 = ROOT / ("E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/"
               "R141_verification")
RUBRICS = ROOT / "data/conversation_rubrics.jsonl"
SEEDS = (8101, 4409, 20260730, 31337, 271828)
SCHEMES = ("magnitude", "length", "raters")
TOL = 1e-9


def load_r141():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("r141mod", R141 / "run.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def strata(cov, neg, rule):
    """R141's bins, and the two repairs. `raw` is the committed rule, verbatim."""
    qs = np.percentile(cov[neg], [0, 20, 40, 60, 80, 100])
    if rule != "raw":
        qs = np.unique(qs)
    out = []
    for i, (lo, hi) in enumerate(zip(qs[:-1], qs[1:])):
        last = i == len(qs) - 2
        if rule == "dedupe_halfopen" and not last:
            out.append((lo, hi, False))     # [lo, hi)
        else:
            out.append((lo, hi, True))      # [lo, hi]
    return out


def matched_positive(cov, neg, rule, seed):
    rng = np.random.default_rng(seed)
    pick = []
    for lo, hi, closed in strata(cov, neg, rule):
        inb_n = (cov[neg] >= lo) & ((cov[neg] <= hi) if closed else (cov[neg] < hi))
        inb_p = (~neg) & (cov >= lo) & ((cov <= hi) if closed else (cov < hi))
        want = int(inb_n.sum())
        pool = np.where(inb_p)[0]
        if len(pool) and want:
            pick += list(rng.choice(pool, min(want, len(pool)), replace=False))
    return np.array(pick, int)


def main() -> int:
    if not RUBRICS.exists() or not (R141 / "run.py").exists():
        print("  UNRUNNABLE: corpus or R141 source missing. Exit 2, never 0.")
        return 2
    m = load_r141()
    committed = json.loads((R141 / "results/r141_verification.json").read_text())["finding_A"]
    print(f"  R141 helpers imported: METRICS = {sorted(m.METRICS)}")

    prompts = []
    for line in open(RUBRICS):
        r = json.loads(line)
        core = [it.get("criterion") or "" for it in (r.get("coval_core") or [])]
        full = [(it.get("criterion") or "",
                 np.array([x["score"] for x in (it.get("scores") or [])], float))
                for it in (r.get("coval_full") or []) if it.get("scores")]
        if core and full:
            prompts.append((core, full))
    print(f"  {len(prompts):,} prompts loaded; building units (R141's similarity pipeline)…")

    # transcribed, not reconstructed: core + full criteria, STEMMED tokens
    df, docs = {}, 0
    for core, full in prompts:
        for t in core + [f[0] for f in full]:
            docs += 1
            for w in set(m.stem(x) for x in m.words(m.strip_neg(t))):
                df[w] = df.get(w, 0) + 1
    import math
    idf = {w: math.log(docs / (1 + c)) for w, c in df.items()}

    units = []
    for core, full in prompts:
        reps = {"stem_token": [set(m.stem(w) for w in m.words(m.strip_neg(t))) for t in core],
                "raw_token": [set(m.words(m.strip_neg(t))) for t in core],
                "char3gram": [m.grams(m.strip_neg(t)) for t in core]}
        for txt, sc in full:
            F = {"stem_token": set(m.stem(w) for w in m.words(m.strip_neg(txt))),
                 "raw_token": set(m.words(m.strip_neg(txt))),
                 "char3gram": m.grams(m.strip_neg(txt))}
            if len(F["stem_token"]) < 3:          # R141's unit filter — transcribed, not inferred
                continue
            best = {}
            for rep, cs in reps.items():
                for mn, fn in m.METRICS.items():
                    if rep == "char3gram" and mn == "idf_weighted":   # R141's cell guard
                        continue
                    best[f"{rep}|{mn}"] = max((fn(F[rep], c, idf) for c in cs), default=0.0)
            units.append((float(sc.mean()) < 0, abs(float(sc.mean())), len(sc), len(txt), best))
    neg = np.array([u[0] for u in units], bool)
    cov = {"magnitude": np.array([u[1] for u in units], float),
           "length": np.array([u[3] for u in units], float),
           "raters": np.array([u[2] for u in units], float)}
    keys = sorted(units[0][4])
    print(f"  {len(units):,} units · {len(keys)} cells · {int(neg.sum()):,} negative")

    def delta(k, scheme, rule):
        v = np.array([u[4][k] for u in units], float)
        return float(np.mean([v[neg].mean() - v[matched_positive(cov[scheme], neg, rule, s)].mean()
                              for s in SEEDS]))

    rules = ("raw", "dedupe", "dedupe_halfopen")
    rows, mism = [], []
    for k in keys:
        for s in SCHEMES:
            d = {r: delta(k, s, r) for r in rules}
            ref = committed["cells"][k][s]["delta_mean"]
            if abs(d["raw"] - ref) > TOL:
                mism.append((k, s, ref, d["raw"]))
            rows.append({"cell": k, "scheme": s, "committed": ref, **d,
                         "shift_dedupe": d["dedupe"] - d["raw"],
                         "shift_halfopen": d["dedupe_halfopen"] - d["raw"]})

    c1 = not mism
    print(f"\n  ① WIRING — committed `delta_mean` reproduced for all {len(rows)} cells at tol "
          f"{TOL}: {c1}  {'PASS' if c1 else 'FAIL'}")
    if mism:
        for x in mism[:4]:
            print(f"     {x[0]}|{x[1]}  committed {x[2]:+.9f}  here {x[3]:+.9f}")

    lenrows = [r for r in rows if r["scheme"] == "length"]
    c2 = all(abs(r["shift_dedupe"]) <= TOL for r in lenrows)
    print(f"\n  ② PLACEBO — `length`'s six cuts are already distinct, so `dedupe` cannot touch it:")
    print(f"     max |shift| over {len(lenrows)} length cells = "
          f"{max(abs(r['shift_dedupe']) for r in lenrows):.2e}: {c2}  {'PASS' if c2 else 'FAIL'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2,
                   "mismatches": [list(x) for x in mism[:20]], "rows": rows},
                  open(OUT / "tie_repair_shift.json", "w"), indent=2)
        return 2

    print(f"\n  ③④ SHIFTS PER STRATIFIER — the two repairs reported separately, all cells counted:")
    summ = {}
    print(f"     {'scheme':<12}{'median |Δ| dedupe':>20}{'max |Δ| dedupe':>17}"
          f"{'median |Δ| +halfopen':>22}{'sign flips':>12}")
    for s in SCHEMES:
        rs = [r for r in rows if r["scheme"] == s]
        md = float(np.median([abs(r["shift_dedupe"]) for r in rs]))
        mx = float(max(abs(r["shift_dedupe"]) for r in rs))
        mh = float(np.median([abs(r["shift_halfopen"]) for r in rs]))
        flip = sum(1 for r in rs if np.sign(r["dedupe"]) != np.sign(r["raw"]))
        summ[s] = {"median_abs_shift_dedupe": md, "max_abs_shift_dedupe": mx,
                   "median_abs_shift_halfopen": mh, "sign_flips": flip, "n": len(rs)}
        print(f"     {s:<12}{md:>20.6f}{mx:>17.6f}{mh:>22.6f}{flip:>12}")

    worst = max(SCHEMES, key=lambda s: summ[s]["median_abs_shift_dedupe"])
    length_still = summ["length"]["max_abs_shift_dedupe"] <= TOL
    moved = summ[worst]["median_abs_shift_dedupe"] > 1e-4
    world = "A" if (moved and worst == "raters" and length_still) else \
            ("C" if not moved else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: largest median shift is `{worst}` at "
          f"{summ[worst]['median_abs_shift_dedupe']:.6f}; `length` immobile: {length_still}")
    if world == "A":
        print(f"     The tie is the whole story. Deduping the cut points moves `raters` by a median")
        print(f"     {summ['raters']['median_abs_shift_dedupe']:.6f} and `magnitude` by "
              f"{summ['magnitude']['median_abs_shift_dedupe']:.6f}, while `length` — whose cuts")
        print(f"     never tied — does not move at all. **R141's `raters` column was computed on a")
        print(f"     matched group that over-weights one-rater positives by construction.**")
    elif world == "C":
        print(f"     The duplication is arithmetically INERT on this outcome: the reweighting does")
        print(f"     not move the contrast, so R929's incoherence needs a different explanation")
        print(f"     again and the tie is a defect without a consequence for the POINT estimate.")
    else:
        print(f"     `length` moved or the largest shift is not `raters` — the tie story does not")
        print(f"     account for the pattern and something else is also wrong.")
    print(f"     ⚠ INTERVALS ARE NOT RECOMPUTED HERE, so whether `ci[1] < 0` still holds — and")
    print(f"     therefore whether any of R141's conclusions move — is NOT answered by this round.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seeds": list(SEEDS), "tol": TOL,
               "n_units": len(units), "n_cells": len(keys),
               "guards_transcribed": ["len(F['stem_token']) < 3 -> skip unit",
                                      "char3gram|idf_weighted -> skip cell"],
               "r931_population_note": "R931's fill table omitted the stem_token<3 filter, so its "
                                       "counts are for a slightly wider corpus; the tied-cut "
                                       "finding is unaffected",
               "summary": summ, "worst": worst, "length_immobile": bool(length_still),
               "rows": rows,
               "fix": "dedupe the quantile cut points; the closed-both-ends boundary is swept as a "
                      "separate rule so it is visible which change did the work",
               "why_not_distinct_values": "`length` has hundreds of distinct values; distinct-value "
                                          "strata would be a different estimator, not a repair",
               "not_answered": "the intervals are not recomputed, so whether ci[1] < 0 still holds "
                               "is open",
               "unit_note": "shifts are in delta_mean units; counts are CELLS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "tie_repair_shift.json", "w"), indent=2)
    print(f"\n  artifact: results/tie_repair_shift.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
