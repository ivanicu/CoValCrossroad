#!/usr/bin/env python3
"""R1023 — censoring is an INTERVENTION, so the guard's value can be priced instead of asserted.

R1022 found imputation manufactures admission under `A1·consensus`, monotone in coverage, over the
three coverage levels the release happens to ship. Three points cannot separate a monotone relation
from a step, and they confound coverage with WHICH ARM. Censoring fixes both: take a full-coverage
arm, hide all but k of its prompts, impute exactly as the committed loader does, and read the same
operator. The arm's true signal is held fixed by construction.

⛔ THE ARITHMETIC FIRST, BECAUSE MOST OF THE PHENOMENON IS FORCED AND MUST NOT BE SOLD AS MEASURED.
   Censoring arm `v` to a set S and imputing gives a vector whose mean is EXACTLY mean(v_S) — the
   imputed cells carry the observed mean, so they cannot move it. The point estimate is therefore
   UNBIASED at every k. But 968−k of the entries become a single CONSTANT, so the bootstrap variance
   of that mean collapses toward zero as k falls. ⇒ `lo` (the 2.5th percentile) is dragged toward a
   point estimate that is still as noisy as k prompts allow. **"Imputation manufactures admission" is
   really "imputation collapses the interval around a small-sample mean", and that much is DERIVED.**

   What the algebra does NOT give is the RATE — how often a wrong verdict is certified at a given k.
   That is a false-positive rate, it is what a threshold should have been chosen against, and it has
   never been computed here.

ESTIMAND        P(the operator returns ADMITTED | the arm is censored to k real prompts), for arms
                whose full-coverage verdict is known, and for a pair whose true difference is EXACTLY
                zero by construction. Nominal level: `lo` is a one-sided 2.5th percentile, so a
                calibrated operator must return 0.025 on the exact null.
IDENTIFICATION  exact and INTERVENTIONAL. The true vector is on disk, censoring is an intervention on
                the mechanism under study, and the uncensored verdict is the ground truth. ⭐ Two
                register lines that are usually N/A on a single site — `causally identified` and
                `interventionally validated` — are available HERE and nowhere else in this arc,
                because the confound (which arm) is removed by construction rather than adjusted for.
SCOPE           population : 4 test arms × 968 prompts · instrument : R923's operator, NBOOT=2000
                baseline   : `generic`, `genericpool16`, and each null arm against ITSELF
                regime     : k ∈ {4,10,25,50,100,200,400,800,968} × 2 targets × 3 seeds × 100 draws
WORLDS          A THE GUARD'S VALUE IS SAFE — at k=200 the false-admission rate on the exact null is
                  at or below the operator's nominal 0.025. Then `200` is conservative, its exact
                  value is not load-bearing, and R1000's twins were inside the calibrated regime.
                B THE GUARD'S VALUE IS TOO LOW — at k=200 the rate is materially above nominal. Then
                  the operator is miscalibrated exactly where the twins were admitted, `200` does not
                  buy what it appears to, and the honest threshold is a MEASURED k, not a habit.
                prediction matrix: A -> FAR(200) <= ~0.025 and the curve is flat until small k.
                                   B -> FAR(200) > 0.025, rising monotonically as k falls.
KILL            pre-registered and CONDITIONAL, per the standard:
                  if positive fires and the null curve is computed at all k:
                      FAR_null(200) > 0.05 (double nominal) -> World B
                      FAR_null(200) <= 0.05                 -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   at k=968 (no censoring) every arm's verdict must equal its committed full-coverage
                verdict from R1022, and the null pair must give EXACTLY zero difference. It can fail:
                a censoring bug, an imputation bug, or a comparator mismatch all break it.
                ⚠ AND IT MUST FAIL WHEN IT SHOULD: a `g=0` check — the null arm against itself
                UNCENSORED must return lo == 0.0 exactly, never a positive margin.
NEGATIVE CTRL   the exact null itself: an arm against ITSELF, censored. True Δ = 0 by construction,
                so every admission is a false positive and no modelling assumption is involved. Two
                different null arms, so the rate is not one arm's peculiarity.
PLACEBO         k = 968 on the null pair: the censoring is empty, the difference vector is identically
                zero, and the admission rate must be exactly 0.000.
NOISE FLOOR     the binomial standard error at 300 draws is ~0.009 at p=0.025, printed beside every
                rate so a rate is never read finer than the design resolves.
MULTIPLICITY    9 k × 2 targets × (2 null pairs + 2 arms × 2 comparators) = 108 cells, all printed.
SEEDS           3 censoring seeds × 100 draws each; per-seed spread reported, never averaged silently.
IMPOSSIBLE      construct validity — whether A2 or A1·consensus is the RIGHT target needs an external
                gold standard. N/A, not planned. Nothing here bears on it; this prices the operator
                under each target as given.
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

NBOOT, DRAWS, SEEDS = 2000, 100, (1023, 2046, 3069)
KS = [4, 10, 25, 50, 100, 200, 400, 800, 968]
NOMINAL = 0.025
TEST_ARMS = ["coval_core", "topw_k6"]


def main() -> int:
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1022 = next(A27.glob("R1022_*/results/coverage_threshold_curve.json"), None)
    if not (r921 and r1022):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    curve = json.loads(r1022.read_text())["curve"]
    truth = {"A2": set(curve["A2|968"]["ext"]),
             "A1·consensus": set(curve["A1·consensus|968"]["ext"])}

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
            return a2, a1c
        return None

    V = {}
    for a in set(TEST_ARMS) | set(legit):
        r = raw(a)
        if r is None or not np.isfinite(r[0]).all():
            print(f"  UNRUNNABLE: `{a}` is not fully covered, so censoring has no ground truth. "
                  f"Exit 2, never 0.")
            return 2
        V[a] = {"A2": r[0], "A1·consensus": r[1]}
    print(f"  arms with a COMPLETE {n}-prompt vector (censoring needs ground truth): "
          f"{sorted(V)}")

    def censor(v, k, rng):
        """hide all but k prompts, then impute EXACTLY as the committed loader does."""
        if k >= n:
            return v.copy()
        S = rng.choice(n, size=k, replace=False)
        out = np.full(n, np.nan)
        out[S] = v[S]
        return np.nan_to_num(out, nan=float(np.nanmean(out)))

    boot = {s: np.random.default_rng(s + 77).integers(0, n, size=(NBOOT, n)) for s in SEEDS}

    def admitted(dvec, s):
        return float(np.percentile(dvec[boot[s]].mean(axis=1), 2.5)) > 0

    # ---------- POSITIVE CONTROL: k=968 must reproduce R1022's committed verdicts ----------
    print(f"\n  POSITIVE — at k={n} (no censoring) every verdict must equal R1022's committed one")
    bad = []
    for tn in ("A2", "A1·consensus"):
        for a in TEST_ARMS:
            got = all(admitted(V[a][tn] - V[c][tn], SEEDS[0]) for c in legit)
            wantv = a in truth[tn]
            print(f"     {tn:<14}{a:<12}mine {str(got):<6}R1022 {str(wantv):<6}"
                  f"{'PASS' if got == wantv else '⛔ FAIL'}")
            if got != wantv:
                bad.append((tn, a))
    zero_lo = float(np.percentile((V[legit[0]]["A2"] - V[legit[0]]["A2"])[boot[SEEDS[0]]]
                                  .mean(axis=1), 2.5))
    g0_ok = zero_lo == 0.0
    print(f"     g=0 CHECK — `{legit[0]}` against ITSELF uncensored must give lo exactly 0.0, "
          f"never positive: got {zero_lo:+.6f} {'PASS' if g0_ok else '⛔ FAIL'}")
    if bad or not g0_ok:
        print("  the instrument does not reproduce the committed answer. Exit 2, never 0.")
        return 2

    # ---------- the exact null: an arm against ITSELF, censored ----------
    print(f"\n  ⭐ THE EXACT NULL — an arm against ITSELF, censored to k. True Δ = 0 BY "
          f"CONSTRUCTION,\n     so every admission is a false positive and no model is involved. "
          f"Nominal level {NOMINAL}.")
    print(f"     {'null arm':<16}{'target':<14}" + "".join(f"{k:>7}" for k in KS))
    null_rows, far200 = [], {}
    for c in legit:
        for tn in ("A2", "A1·consensus"):
            per_k = []
            for k in KS:
                rates = []
                for s in SEEDS:
                    rng = np.random.default_rng(s * 1000 + k)
                    hits = sum(admitted(censor(V[c][tn], k, rng) - V[c][tn], s)
                               for _ in range(DRAWS))
                    rates.append(hits / DRAWS)
                per_k.append((float(np.mean(rates)), float(max(rates) - min(rates))))
            null_rows.append({"arm": c, "target": tn,
                              "rates": {str(k): per_k[i][0] for i, k in enumerate(KS)},
                              "seed_spread": {str(k): per_k[i][1] for i, k in enumerate(KS)}})
            far200[(c, tn)] = per_k[KS.index(200)][0]
            print(f"     {c:<16}{tn:<14}" + "".join(f"{r[0]:>7.3f}" for r in per_k))
    se = (NOMINAL * (1 - NOMINAL) / (DRAWS * len(SEEDS))) ** 0.5
    print(f"     binomial SE at {DRAWS * len(SEEDS)} draws and p={NOMINAL}: ±{se:.4f} — no rate is "
          f"read finer than this")
    worst_spread = max(max(r["seed_spread"].values()) for r in null_rows)
    print(f"     worst per-seed spread over all null cells: {worst_spread:.3f}")

    # ---------- MECHANISM CHECK: the algebra must PREDICT the measured rate ----------
    #   The bootstrap treats the 968-k imputed cells as CONSTANTS with zero variance, but they are
    #   an ESTIMATE of the arm's mean. Ratio of the true sampling SD of mean(d) to the bootstrap SE
    #   it reports is computable in closed form from sd(v) alone — and it CANCELS, so the predicted
    #   level depends on k and n only. If the measured curve does not track it, one of the two is
    #   wrong and the finding is not understood.
    from math import erfc, sqrt
    print(f"\n  ⭐ MECHANISM — the algebra must PREDICT the measured rate, or the finding is a "
          f"coincidence.")
    print(f"     {'k':>6}{'SD_true/SE_boot':>18}{'predicted level':>17}{'measured (mean)':>17}")
    mech = []
    for k in KS:
        if k >= n:
            mech.append({"k": k, "ratio": None, "predicted": 0.0}); continue
        f = (n - k) / n
        sd_true = f * sqrt(1.0 / k + 1.0 / (n - k))       # sd(v) cancels
        se_boot = sqrt(f) / sqrt(n)
        ratio = sd_true / se_boot
        pred = 0.5 * erfc((1.959964 / ratio) / sqrt(2.0))  # one-sided normal level
        meas = float(np.mean([r["rates"][str(k)] for r in null_rows]))
        mech.append({"k": k, "ratio": ratio, "predicted": pred, "measured": meas})
        print(f"     {k:>6}{ratio:>18.2f}{pred:>17.3f}{meas:>17.3f}")
    paired = [(m["predicted"], m["measured"]) for m in mech if m.get("measured") is not None]
    worst_gap = max(abs(a - b) for a, b in paired)
    mech_ok = worst_gap < 0.12
    print(f"     worst |predicted - measured| over the {len(paired)} censored levels: "
          f"{worst_gap:.3f}  {'✅ the algebra explains the curve' if mech_ok else '⚠ IT DOES NOT'}")
    print( "     ⚠ THIS IS A CONSISTENCY CHECK, NOT AN INDEPENDENT CONFIRMATION — both sides use the")
    print( "       same normal approximation. It rules out a coding artifact, never a shared model error.")

    # ---------- PLACEBO: k=968 on the null pair must be exactly 0.000 ----------
    plac = [r["rates"]["968"] for r in null_rows]
    plac_ok = all(p == 0.0 for p in plac)
    print(f"  PLACEBO — at k={n} the null difference vector is identically zero, so the rate must "
          f"be exactly 0.000: {plac} {'PASS' if plac_ok else '⛔ FAIL'}")

    # ---------- the real arms: how often does censoring FLIP a known verdict? ----------
    print(f"\n  ⭐ VERDICT FLIP RATE on arms whose uncensored verdict is committed:")
    print(f"     {'arm':<12}{'target':<14}{'truth':<8}" + "".join(f"{k:>7}" for k in KS))
    flip_rows = []
    for a in TEST_ARMS:
        for tn in ("A2", "A1·consensus"):
            wantv = a in truth[tn]
            per_k = []
            for k in KS:
                rates = []
                for s in SEEDS:
                    rng = np.random.default_rng(s * 7919 + k)
                    hits = 0
                    for _ in range(DRAWS):
                        cv = censor(V[a][tn], k, rng)
                        hits += all(admitted(cv - V[c][tn], s) for c in legit)
                    rates.append(hits / DRAWS)
                per_k.append(float(np.mean(rates)))
            flip_rows.append({"arm": a, "target": tn, "truth_admitted": bool(wantv),
                              "admit_rate": {str(k): per_k[i] for i, k in enumerate(KS)}})
            print(f"     {a:<12}{tn:<14}{str(wantv):<8}" + "".join(f"{r:>7.3f}" for r in per_k))
    print( "     (a cell far from its `truth` column is a censoring-induced WRONG verdict)")

    # ---------- the pre-registered, CONDITIONAL kill ----------
    worst200 = max(far200.values())
    print()
    if not plac_ok:
        world = "UNVERIFIED — the placebo did not return exactly zero; no verdict is admissible"
    elif worst200 > 0.05:
        world = (f"⭐ B THE GUARD'S VALUE IS TOO LOW — on the EXACT null, censoring to k=200 yields "
                 f"a false-admission rate of {worst200:.3f}, above twice the operator's nominal "
                 f"{NOMINAL}. The twins entered R1000's extension inside a regime where the "
                 f"operator is miscalibrated, and `200` does not buy what it appears to.")
    else:
        world = (f"⭐ A THE GUARD'S VALUE IS SAFE — on the EXACT null, censoring to k=200 yields a "
                 f"false-admission rate of {worst200:.3f}, at or below twice the nominal {NOMINAL}. "
                 f"`200` is conservative and its exact value is not load-bearing; what matters is "
                 f"that a threshold exists at all.")
    print(world)
    print(f"⛔ AND THE SHAPE OF THE CURVE IS THE DELIVERABLE, NOT THE VERDICT: the null rate at each")
    print(f"   k is a PRICE LIST for the guard. Any future threshold can be read off it instead of")
    print(f"   inherited — which is the thing 22 scripts could not do, because it did not exist.")
    print(f"⚠ THE COLLAPSE ITSELF IS DERIVED, NOT MEASURED. Imputing 968−k cells with the observed")
    print(f"   mean leaves that mean unchanged and drives the bootstrap variance to zero, so `lo`")
    print(f"   must approach a k-sized point estimate. Only the RATE above is a measurement.")
    print(f"⚠ AND THIS PRICES THE OPERATOR, NOT THE TARGET. Whether A2 or A1·consensus is the right")
    print(f"   thing to admit on needs an external criterion this release does not carry.")

    out = HERE / "results" / "false_admission_rate.json"
    out.write_text(json.dumps({
        "round": "R1023", "seeds": list(SEEDS), "nboot": NBOOT, "draws_per_seed": DRAWS,
        "ks": KS, "nominal": NOMINAL, "binomial_se": se,
        "derivation": "imputing 968-k cells with the observed mean leaves the mean exactly "
                      "unchanged and collapses the bootstrap variance; the point estimate stays "
                      "as noisy as k prompts allow",
        "positive_control_matched_r1022": True, "g0_lo": zero_lo,
        "placebo_zero_at_full_k": bool(plac_ok),
        "exact_null": null_rows, "verdict_flip": flip_rows,
        "far_at_k200_worst": worst200, "mechanism": mech,
        "mechanism_worst_gap": worst_gap, "mechanism_explains": bool(mech_ok),
        "world": world,
        "limitation": "prices the OPERATOR under each target as given; construct validity of the "
                      "target itself needs an external gold standard this release does not carry",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
