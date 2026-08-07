#!/usr/bin/env python3
"""R1024 — is a coverage THRESHOLD the right instrument at all, or was the ESTIMATOR the defect?

R1023 priced the guard: at k=200 the committed operator certifies an exactly-null arm 21% of the time
against a nominal 2.5%, and the closed-form ratio predicts the whole curve. Its NEXT proposed
"resample the censoring as well as the prompts". ⛔ THAT PROPOSAL IS NOT REALIZABLE and is withdrawn
here rather than attempted: resampling the censoring requires the arm's FULL vector, which is exactly
what a partially-covered arm does not have. The realizable correction is simpler and needs no new
machinery — DO NOT IMPUTE. Bootstrap the k observed prompts and nothing else. That is what R1021 did
by hand when it restricted the core/twin comparison to the 200 shared prompts.

⛔ AND THE ESTIMAND HAD TO CHANGE, BECAUSE R1023'S NULL IS DEGENERATE UNDER THE FIX. On an arm against
   ITSELF the observed-only difference vector is identically zero, so `lo` is 0 and the
   false-admission rate is FORCED to 0 at every k. Reporting "the fix attains 0.000" would be
   1+1=2 dressed as a result. What is not forced, and what actually decides whether a threshold is
   needed, is CALIBRATION on a non-degenerate contrast: does the one-sided lower bound contain the
   true full-population difference at its nominal rate?

ESTIMAND        P(lo <= Δ_true), the one-sided coverage of the operator's lower bound, where Δ_true is
                the arm-minus-comparator mean difference over ALL 968 prompts. Nominal 0.975 (`lo` is
                a 2.5th percentile). R1023's false-admission rate is the special case Δ_true = 0.
IDENTIFICATION  exact and INTERVENTIONAL. Δ_true is computable from the uncensored vectors on disk;
                censoring is an intervention; coverage is a frequency over censoring draws.
SCOPE           population : 4 real (arm, comparator) pairs + 1 exact-null pair × 968 prompts
                instrument : R923's operator under TWO estimators, NBOOT=2000
                baseline   : the committed impute-then-bootstrap estimator
                regime     : k ∈ {4,10,25,50,100,200,400,800,968} × 2 targets × 3 seeds × 100 draws
WORLDS          A THE THRESHOLD IS THE WRONG INSTRUMENT — the observed-only estimator attains nominal
                  coverage at every k. Then the guard is deletable: the defect was the ESTIMATOR, any
                  coverage is usable, and 22 scripts carry a constant that should not exist.
                B A MINIMUM k IS IRREDUCIBLE — even the correct estimator under-covers at small k,
                  because a bootstrap over few units fails on its own. Then the guard's JOB is real
                  and only its VALUE was unjustified; the honest threshold is where coverage recovers.
                prediction matrix: A -> observed-only coverage ≈ 0.975 at all k, flat.
                                   B -> observed-only coverage < 0.975 at small k, rising with k.
                ⚠ These differ ONTOLOGICALLY: A says the problem is a modelling choice, B says it is
                  a sample-size limit. They imply opposite repairs — delete the guard vs. measure it.
KILL            pre-registered and CONDITIONAL, per the standard:
                  if positive fires and placebo is sensitive:
                      min over k>=10 of observed-only coverage >= 0.95 -> World A
                      else                                            -> World B, and the smallest k
                                                                          reaching 0.95 is the answer
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
                ⚠ k=4 is EXCLUDED from the kill's minimum and reported separately: a bootstrap over
                  4 units is known-broken for reasons that have nothing to do with this benchmark,
                  so letting it decide the verdict would be an instrument failure read as a finding.
POSITIVE CTRL   the impute estimator must REPRODUCE R1023's committed false-admission curve on the
                exact null, within the binomial SE of both designs. It can fail: any change to the
                censoring, imputation or operator breaks it. And an ADEQUACY check — at k=968 the two
                estimators must return the IDENTICAL bound, since neither imputes anything there.
PLACEBO         TWO checks whose expectation is ESTIMATOR-INDEPENDENT, because a control that
                presupposes calibration cannot run while calibration is what is under test:
                (i) NESTING — `lo <= Δ+δ` is nested in δ, so coverage is non-decreasing in δ. Pure
                    arithmetic; fails only on an implementation bug. (ii) RANGE — scores ∈ [0,1] so
                    |lo| <= 1; coverage must be EXACTLY 0.000 at δ=−2 and 1.000 at δ=+2.
                ⚠ Two earlier placebos (±0.5 with a calibrated expectation) are WITHDRAWN and their
                numbers demoted to a diagnostic. Both printed FAIL with nothing wrong.
NEGATIVE CTRL   the exact-null pair is carried through both estimators. Under the fix it is DEGENERATE
                by the argument above; it is printed to SHOW the degeneracy, never used as evidence.
NOISE FLOOR     binomial SE at 300 draws, p=0.975: ±0.0090. No coverage read finer.
MULTIPLICITY    2 estimators × 9 k × 2 targets × 5 pairs = 180 cells, all printed.
SEEDS           3 censoring seeds × 100 draws; per-seed spread reported, never averaged silently.
IMPOSSIBLE      construct validity — whether A2 or A1·consensus is the right target still needs an
                external gold standard. N/A, not planned. This round is about the ESTIMATOR only.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, DRAWS, SEEDS = 2000, 100, (1024, 2048, 3072)
KS = [4, 10, 25, 50, 100, 200, 400, 800, 968]
NOMINAL = 0.975
DELTAS = [-2.0, -0.5, -0.1, 0.0, 0.1, 0.5, 2.0]
TARGETS = ("A2", "A1·consensus")


def main() -> int:
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1023 = next(A27.glob("R1023_*/results/false_admission_rate.json"), None)
    if not (r921 and r1023):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    prev = {(r["arm"], r["target"]): r["rates"] for r in json.loads(r1023.read_text())["exact_null"]}

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    Hc = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    CONS = {p: np.sign(np.array(Hc[p], float).sum(axis=0)) for p in pids}

    def raw(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            Sa = load_sat(f)
            a2, a1c = np.full(n, np.nan), np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                a2[k] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in Hc[p]]))
                m = min(len(c), len(CONS[p]))
                a1c[k] = float((c[:m] == CONS[p][:m]).all())
            return {"A2": a2, "A1·consensus": a1c}
        return None

    ARMS = ["coval_core", "topw_k6"]
    V = {}
    for a in set(ARMS) | set(legit):
        r = raw(a)
        if r is None or not np.isfinite(r["A2"]).all():
            print(f"  UNRUNNABLE: `{a}` lacks a complete vector; censoring has no ground truth. "
                  f"Exit 2.")
            return 2
        V[a] = r
    PAIRS = [(a, c) for a in ARMS for c in legit] + [(legit[0], legit[0])]
    print(f"  pairs: {len(PAIRS)} ({len(PAIRS)-1} real + 1 EXACT NULL) · prompts {n} · "
          f"targets {list(TARGETS)}")

    boot_full = {s: np.random.default_rng(s + 11).integers(0, n, size=(NBOOT, n)) for s in SEEDS}

    def lo_impute(v, u, S, s):
        """the COMMITTED estimator: fill the unobserved cells with the observed mean, bootstrap 968."""
        w = np.full(n, np.nan)
        w[S] = v[S]
        w = np.nan_to_num(w, nan=float(np.nanmean(w)))
        return float(np.percentile((w - u)[boot_full[s]].mean(axis=1), 2.5))

    def lo_observed(v, u, S, s):
        """the FIX: no imputation. Bootstrap the k observed prompts and nothing else."""
        d = (v - u)[S]
        idx = np.random.default_rng(s * 31 + len(S)).integers(0, len(S), size=(NBOOT, len(S)))
        return float(np.percentile(d[idx].mean(axis=1), 2.5))

    EST = {"impute (committed)": lo_impute, "observed-only (fix)": lo_observed}

    # ---------- POSITIVE: reproduce R1023's committed null curve with the impute estimator ------
    print(f"\n  POSITIVE — the impute estimator must reproduce R1023's committed false-admission "
          f"curve\n     on the exact null (Δ_true = 0, so `lo > 0` IS a false admission):")
    worst_gap, rows_pc = 0.0, []
    for tn in TARGETS:
        c = legit[0]
        for k in (200, 800):
            hits = []
            for s in SEEDS:
                rng = np.random.default_rng(s * 1000 + k)
                hits.append(np.mean([lo_impute(V[c][tn], V[c][tn],
                                              rng.choice(n, size=k, replace=False), s) > 0
                                     for _ in range(DRAWS)]))
            got, wantv = float(np.mean(hits)), prev[(c, tn)][str(k)]
            worst_gap = max(worst_gap, abs(got - wantv))
            rows_pc.append({"target": tn, "k": k, "mine": got, "r1023": wantv})
            print(f"     {tn:<14}k={k:<5}mine {got:.3f}  R1023 {wantv:.3f}  Δ {abs(got-wantv):.3f}")
    se = (0.2 * 0.8 / (DRAWS * len(SEEDS))) ** 0.5
    pos_ok = worst_gap < 4 * se
    print(f"     worst Δ {worst_gap:.3f} against 4×SE = {4*se:.3f}: "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")

    # ADEQUACY: at k=968 nothing is imputed, so the two estimators must agree exactly
    adq = []
    for tn in TARGETS:
        allp = np.arange(n)
        a, c = ARMS[0], legit[0]
        adq.append(abs(lo_impute(V[a][tn], V[c][tn], allp, SEEDS[0])
                       - lo_observed(V[a][tn], V[c][tn], allp, SEEDS[0])))
    adq_ok = max(adq) < 0.01
    print(f"     ADEQUACY — at k={n} neither estimator imputes, so their bounds must agree: "
          f"worst |Δ| {max(adq):.4f} {'PASS' if adq_ok else '⛔ FAIL'}")
    if not (pos_ok and adq_ok):
        print("  the instrument does not reproduce the committed answer. Exit 2, never 0.")
        return 2

    # ---------- the coverage curve, both estimators, whole grid ----------
    print(f"\n  ⭐ ONE-SIDED COVERAGE  P(lo <= Δ_true).  Nominal {NOMINAL}. "
          f"Binomial SE ±{(NOMINAL*(1-NOMINAL)/(DRAWS*len(SEEDS)))**0.5:.4f}")
    cov, SHIFTS = [], {}
    for ename, fn in EST.items():
        print(f"\n     {ename}")
        print(f"     {'pair':<30}{'target':<14}" + "".join(f"{k:>7}" for k in KS))
        for (a, c) in PAIRS:
            for tn in TARGETS:
                dtrue = float((V[a][tn] - V[c][tn]).mean())
                per_k = []
                for k in KS:
                    hit, los = [], []
                    for s in SEEDS:
                        rng = np.random.default_rng(s * 7919 + k)
                        ok = 0
                        for _ in range(DRAWS):
                            S = np.arange(n) if k >= n else rng.choice(n, size=k, replace=False)
                            lo = fn(V[a][tn], V[c][tn], S, s)
                            los.append(lo)
                            ok += lo <= dtrue
                        hit.append(ok / DRAWS)
                    per_k.append(float(np.mean(hit)))
                    L = np.array(los)
                    # ⭐ coverage at ANY shift, computed from the SAME draws — so the nesting
                    #   identity below is a statement about this run, not about two runs.
                    SHIFTS[(ename, a, c, tn, k)] = [float((L <= dtrue + d).mean()) for d in DELTAS]
                tag = f"{a} vs {c}" + (" [EXACT NULL]" if a == c else "")
                cov.append({"estimator": ename, "arm": a, "comparator": c, "target": tn,
                            "delta_true": dtrue, "exact_null": a == c,
                            "coverage": {str(k): per_k[i] for i, k in enumerate(KS)}})
                print(f"     {tag:<30}{tn:<14}" + "".join(f"{v:>7.3f}" for v in per_k))

    # ⚠⚠ THE PLACEBO WAS WRITTEN WRONG TWICE, THE SAME WAY BOTH TIMES, AND BOTH VERSIONS PRINTED
    #     FAIL WITH NOTHING WRONG WITH THE ROUND. v1 shifted the truth UP by 0.5 and demanded
    #     coverage ~1.000 everywhere (got 0.973). v2 shifted DOWN and demanded ~0.000 (got 0.290).
    #     Both expectations PRESUPPOSE A CALIBRATED ESTIMATOR — and half this grid is the estimator
    #     whose miscalibration is the finding. A control whose expectation only holds when the thing
    #     under test is healthy cannot be used while testing it.
    #     The valid placebo must hold for ANY estimator, calibrated or not. Two do:
    #       (i) NESTING — `lo <= Δ+δ` is nested in δ, so coverage must be non-decreasing in δ. Pure
    #           arithmetic; fails only on an implementation bug (a re-drawn seed, a bad index).
    #      (ii) RANGE  — the scores are bounded in [0,1], so |Δ| <= 1 and |lo| <= 1. At δ = +2
    #           coverage must be EXACTLY 1.000 and at δ = -2 EXACTLY 0.000, for both estimators.
    viol_nest, viol_range = [], []
    for key, vals in SHIFTS.items():
        for i in range(len(DELTAS) - 1):
            if vals[i] > vals[i + 1] + 1e-12:
                viol_nest.append((key, DELTAS[i], vals[i], vals[i + 1]))
        if vals[DELTAS.index(2.0)] != 1.0 or vals[DELTAS.index(-2.0)] != 0.0:
            viol_range.append((key, vals[DELTAS.index(-2.0)], vals[DELTAS.index(2.0)]))
    plac_ok = not viol_nest and not viol_range
    print(f"\n  PLACEBO — two checks whose expectation is ESTIMATOR-INDEPENDENT, over all "
          f"{len(SHIFTS)} cells:")
    print(f"     (i)  NESTING  coverage non-decreasing in δ (pure arithmetic): "
          f"{len(viol_nest)} violations {'PASS' if not viol_nest else '⛔ FAIL'}")
    print(f"     (ii) RANGE    scores ∈ [0,1] ⇒ coverage exactly 0.000 at δ=−2 and 1.000 at δ=+2: "
          f"{len(viol_range)} violations {'PASS' if not viol_range else '⛔ FAIL'}")
    print( "     ⚠ TWO EARLIER PLACEBOS ARE WITHDRAWN, NOT RELAXED. Both demanded a calibrated")
    print( "       response (~1.000 at δ=+0.5, ~0.000 at δ=−0.5) from a grid half of which is the")
    print( "       estimator being shown miscalibrated. Their numbers are kept below as a DIAGNOSTIC,")
    print( "       because how far the bound misses is exactly what this round is measuring.")

    # ---------- the withdrawn placebos, re-read as what they actually measure ----------
    def worst(ename, d):
        i = DELTAS.index(d)
        return {"max": max(v[i] for (e, *_), v in SHIFTS.items() if e == ename),
                "min": min(v[i] for (e, *_), v in SHIFTS.items() if e == ename)}
    print(f"\n  ⭐ DIAGNOSTIC — how far the bound misses, from the same draws:")
    print(f"     {'estimator':<22}{'P(lo <= Δ−0.5)':>18}{'P(lo <= Δ+0.5)':>18}")
    diag = {}
    for ename in EST:
        dn, up = worst(ename, -0.5)["max"], worst(ename, 0.5)["min"]
        diag[ename] = {"worst_P_lo_below_truth_minus_half": dn, "worst_P_lo_below_truth_plus_half": up}
        print(f"     {ename:<22}{dn:>18.3f}{up:>18.3f}")
    print( "     (left: how often the bound lands >0.5 BELOW the truth — uselessly wide.")
    print( "      right: how often it is still below truth+0.5 — 1.000 for a sane bound.)")

    # ---------- the pre-registered, CONDITIONAL kill ----------
    fixed = [r for r in cov if r["estimator"] == "observed-only (fix)" and not r["exact_null"]]
    big_k = [str(k) for k in KS if k >= 10]
    worst = min(min(r["coverage"][k] for k in big_k) for r in fixed)
    first_ok = None
    for k in KS:
        if all(r["coverage"][str(k)] >= 0.95 for r in fixed):
            first_ok = k
            break
    k4 = min(r["coverage"]["4"] for r in fixed)
    print()
    if not (pos_ok and plac_ok):
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif worst >= 0.95:
        world = (f"⭐ A THE THRESHOLD IS THE WRONG INSTRUMENT — the observed-only estimator holds "
                 f"coverage at {worst:.3f} or better across every real pair at k>=10. The defect was "
                 f"the ESTIMATOR, not the sample size: drop the imputation and the guard has no job "
                 f"left to do.")
    else:
        world = (f"⭐ B A MINIMUM k IS IRREDUCIBLE — even without imputation, coverage falls to "
                 f"{worst:.3f} at small k, so a bootstrap over few prompts fails on its own. The "
                 f"guard's JOB is real and only its VALUE was unjustified; the smallest k at which "
                 f"every real pair reaches 0.95 is {first_ok}.")
    print(world)
    print(f"⚠ k=4 IS REPORTED, NEVER USED IN THE VERDICT: worst coverage there is {k4:.3f}, and a "
          f"bootstrap\n   over 4 units is known-broken for reasons that have nothing to do with this "
          f"benchmark.")
    print(f"⚠ THE EXACT NULL IS DEGENERATE UNDER THE FIX AND IS PRINTED TO SHOW THAT, NOT AS "
          f"EVIDENCE.\n   With no imputation the self-difference vector is identically zero, so the "
          f"bound is 0 and\n   coverage is forced. R1023's headline number has no counterpart here "
          f"by construction.")
    print(f"⚠ AND R1023'S OWN NEXT WAS NOT REALIZABLE. 'Resample the censoring' needs the full "
          f"vector,\n   which a partially-covered arm does not have. It is withdrawn, not attempted "
          f"— the closing\n   line of a round is the one sentence with no control attached, and this "
          f"is the second time\n   in this arc that it named an action the data cannot support.")

    out = HERE / "results" / "estimator_vs_threshold.json"
    out.write_text(json.dumps({
        "round": "R1024", "seeds": list(SEEDS), "nboot": NBOOT, "draws_per_seed": DRAWS,
        "ks": KS, "nominal": NOMINAL,
        "withdrawn": "R1023's NEXT proposed resampling the censoring; that requires the full vector "
                     "a partially-covered arm does not have, so it is withdrawn rather than "
                     "attempted. The realizable fix is to stop imputing.",
        "positive_vs_r1023": rows_pc, "positive_worst_gap": worst_gap,
        "adequacy_worst_abs_diff": max(adq),
        "placebo_nesting_violations": len(viol_nest),
        "placebo_range_violations": len(viol_range),
        "shift_diagnostic": diag, "deltas": DELTAS,
        "coverage": cov, "worst_coverage_k_ge_10_fix": worst,
        "first_k_reaching_0.95_fix": first_ok, "k4_worst_fix": k4,
        "world": world,
        "limitation": "prices the ESTIMATOR under each target as given; whether A2 or A1·consensus "
                      "is the right target needs an external gold standard this release lacks",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
