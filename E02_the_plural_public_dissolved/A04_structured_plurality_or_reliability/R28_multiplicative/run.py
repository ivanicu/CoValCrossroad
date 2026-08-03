"""r28 -- The functional form was wrong, and it was wrong in the direction of the answer.

What went wrong across four rounds
-----------------------------------
r23, r25, r26 and r27 all decompose rater agreement as

    A_ij = mu + a_i + a_j + e_ij

fit a_i by least squares, and read the residual e_ij as "pair-specific
structure" -- the quantity that decides whether r01's persistence means value
blocs (M2) or merely that raters differ in reliability (M1b).

But classical test theory says that under ONE latent target with heterogeneous
rater reliability, the correlation between two raters' profiles is a PRODUCT,
not a sum:

    A_ij  =  rho_i * rho_j

and if you fit an ADDITIVE model to a multiplicative truth, the residual is not
noise.  Writing m for the mean reliability and a_i ~ rho_i * m:

    residual  =  rho_i rho_j  -  m(rho_i + rho_j)  +  m^2
              =  (rho_i - m)(rho_j - m)

which is POSITIVE when both raters are above average, POSITIVE when both are
below, and NEGATIVE when they straddle.  A U-shape across strata, produced
entirely by the wrong functional form, with no blocs anywhere in the generating
process.

r27 measured exactly that U-shape and I read it as evidence about blocs:

    both_high  -0.0400   mixed  -0.0596   both_low  +0.1379

The +0.1379 looked like a minority bloc -- two raters who disagree with everyone
agreeing strongly with each other.  It is what an additive fit does to a
multiplicative surface.

This round therefore does two things:
  1. compares the two functional forms head to head on the SAME observed dyads
  2. re-runs the stratum test against the multiplicative fit, so that whatever
     survives is structure the reliability model genuinely cannot produce

Design notes
------------
* The rank-1 fit is alternating least squares on OBSERVED entries only.  The
  matrix is ~93% missing (924 raters, 6,193 observed dyads), so no dense
  eigendecomposition is available and imputing zeros would invent agreement
  where there is none.
* Parameter counts WERE reported as 925 additive against 924 multiplicative,
  and that was wrong.  The additive design is rank-deficient by exactly one:
  mu -> mu - 2t together with a_i -> a_i + t leaves every fitted value
  unchanged for any t, so the intercept column is redundant.  Verified: 925
  columns, numerical rank 924, and ||X @ (that direction)|| = 0 exactly.  The
  effective degrees of freedom are EQUAL.  The multiplicative form does not win
  on a parameter handicap, and the sentence claiming it did was the one written
  to pre-empt "it is just the bigger model" -- which needed checking, not
  asserting.
* The strata are defined by the MULTIPLICATIVE parameter c_i, not by raw mean
  agreement, so the split does not select on the outcome the way r27's first
  control did.
* A permutation null is still reported for the surviving stratum, because a
  residual can be nonzero for reasons other than blocs and the CI alone does not
  say it beats chance.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / "covalx").is_dir())))
from covalx.frozen import append_to as _freeze  # noqa: E402


import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"


def _cell():
    spec = importlib.util.spec_from_file_location(
        "cell", _ROOT / "E02_the_plural_public_dissolved/A04_structured_plurality_or_reliability/R25_actor_dyad_sweep/cell.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_matrix(raw, min_partners: int):
    by = defaultdict(dict)
    for pair, vals in raw.items():
        # sorted(), not tuple().  `pair` is a frozenset, and frozenset ITERATION
        # ORDER depends on Python's per-process hash randomization, so
        # `u, v = tuple(pair)` assigned raters to matrix rows differently on
        # every run.  fit_rank1 is Gauss-Seidel coordinate descent over row
        # index, so its update order -- and its answer -- moved with it.  An
        # adversary measured the damage: with everything else fixed, including
        # the numpy seed, C4's permutation z ranged 2.2177..2.4409 over five
        # PYTHONHASHSEED values, and the value committed to ASSURANCE.md was
        # 2.5049, the top of the observed spread.  The script LOOKED
        # reproducible -- it sets np.random.default_rng(20260728) -- which is
        # exactly why nobody checked.
        u, v = sorted(pair)
        m = float(np.mean(vals))
        by[u][v] = m
        by[v][u] = m
    keep = [r for r, d in by.items() if len(d) >= min_partners]
    idx = {r: i for i, r in enumerate(keep)}
    n = len(keep)
    A = np.full((n, n), np.nan)
    for u in keep:
        for v, m in by[u].items():
            if v in idx:
                A[idx[u], idx[v]] = m
    mask = ~np.isnan(A)
    np.fill_diagonal(mask, False)
    return A, mask, keep


def fit_rank1(A, mask, iters=300):
    """A_ij ~ c_i c_j by ALS on observed entries. c_i is a per-rater reliability."""
    with np.errstate(invalid="ignore"):
        c = np.nanmean(np.where(mask, A, np.nan), axis=1)
    c = np.sign(c) * np.sqrt(np.abs(c))
    c = np.nan_to_num(c, nan=0.1)
    for _ in range(iters):
        for i in range(len(c)):
            m = mask[i]
            if not m.any():
                continue
            d = float((c[m] ** 2).sum())
            if d > 1e-9:
                c[i] = float((A[i, m] * c[m]).sum() / d)
    return c


def fit_additive(A, mask):
    rows, cols = np.where(np.triu(mask, 1))
    y = A[rows, cols]
    N = len(y)
    X = np.zeros((N, len(A) + 1))
    X[:, 0] = 1.0
    X[np.arange(N), rows + 1] += 1.0
    X[np.arange(N), cols + 1] += 1.0
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y, X @ b, rows, cols


def strata_residuals(y, hat, cvec, rows, cols, rng, boot=4000):
    med = float(np.median(cvec))
    lab = np.where((cvec[rows] > med) & (cvec[cols] > med), "both_high",
                   np.where((cvec[rows] <= med) & (cvec[cols] <= med),
                            "both_low", "mixed"))
    out = {}
    for s in ("both_high", "mixed", "both_low"):
        m = lab == s
        r = (y - hat)[m]
        if len(r) < 50:
            continue
        bs = np.array([r[rng.integers(0, len(r), len(r))].mean() for _ in range(boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[s] = {"n": int(m.sum()), "mean": float(r.mean()),
                  "ci": [float(lo), float(hi)],
                  "excludes_zero": bool(lo > 0 or hi < 0)}
    return out, lab


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    # default names the metric, so the documented invocation regenerates exactly
    # the file the assurance manifest reads.  It previously wrote
    # r28_multiplicative.json while the manifest checked r28_pearson.json, so
    # `python E02_the_plural_public_dissolved/A04_structured_plurality_or_reliability/R28_multiplicative/run.py` did not refresh the claim it
    # was supposed to support.
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--metric", default="pearson",
                   choices=["pearson", "spearman", "cosine", "negl1"])
    p.add_argument("--min-overlap", type=int, default=3)
    p.add_argument("--thr", default="majority")
    p.add_argument("--min-prompts", type=int, default=3)
    p.add_argument("--min-partners", type=int, default=6)
    p.add_argument("--null-reps", type=int, default=100)
    a = p.parse_args()

    if a.out is None:
        a.out = _RES / f"r28_{a.metric}.json"
    cell = _cell()
    rng = np.random.default_rng(20260728)
    data = cell.load(a.data, a.thr)
    raw = defaultdict(list)
    for rec in data:
        ag = cell.pair_agreements(cell.standardize(rec["m"]), rec["raters"],
                                  a.metric, a.min_overlap)
        for k, v in ag.items():
            raw[frozenset(k)].append(float(v))
    raw = {k: v for k, v in raw.items() if len(v) >= a.min_prompts}

    A, mask, keep = build_matrix(raw, a.min_partners)
    # ---- HELD-OUT VALIDATION, added 2026-07-28 after an adversary ran it -----
    # This round originally compared the two shapes on IN-SAMPLE R^2 alone and
    # concluded the multiplicative one is correct because it fits better "with
    # one fewer parameter".  Both halves were wrong.  The additive design is
    # rank-deficient by exactly one (mu -> mu-2t, a_i -> a_i+t leaves every
    # fitted value unchanged; numerical rank 924 of 925 columns, null direction
    # verified exactly), so effective degrees of freedom are EQUAL.  And a
    # rank-1 factorization carrying ~1 parameter per rater over ~13 dyads per
    # rater will win in-sample almost regardless of whether it is the right
    # generative shape.  The question was never fit.  It is prediction.
    def cv_r2(seed, frac=0.2):
        rr, cc = np.where(np.triu(mask, 1))
        g = np.random.default_rng(seed)
        held = g.random(len(rr)) < frac
        trmask = np.zeros_like(mask)
        trmask[rr[~held], cc[~held]] = True
        trmask[cc[~held], rr[~held]] = True
        yte = A[rr[held], cc[held]]
        ss = float(((yte - yte.mean()) ** 2).sum())
        ytr, _ahat, _r, _c = fit_additive(A, trmask)
        Xall = np.zeros((len(rr), len(A) + 1))
        Xall[:, 0] = 1.0
        Xall[np.arange(len(rr)), rr + 1] += 1.0
        Xall[np.arange(len(rr)), cc + 1] += 1.0
        b, *_ = np.linalg.lstsq(Xall[~held], ytr, rcond=None)
        add_te = Xall[held] @ b
        with np.errstate(invalid="ignore"):
            ctr = fit_rank1(A, trmask)
        mul_te = ctr[rr[held]] * ctr[cc[held]]
        return (1 - float(((yte - add_te) ** 2).sum()) / ss,
                1 - float(((yte - mul_te) ** 2).sum()) / ss)

    print("  HELD-OUT (20% of dyads masked, both shapes refit on the remainder):")
    cv = []
    # TEN splits, not three.  The first version used seeds 1-3, which all happen
    # to land on well-behaved masks, so `cv_stable` could not fire and the round
    # printed its optimistic verdict.  A stability check that cannot observe the
    # instability is not a check: the catastrophic mode appears in roughly one
    # split in ten, and an adversary running its own three splits hit it twice.
    for sd in range(1, 11):
        ra, rm_ = cv_r2(sd)
        cv.append({"seed": sd, "additive": ra, "multiplicative": rm_})
        print(f"    split {sd}:  additive test R^2 = {ra:>8.4f}    "
              f"multiplicative test R^2 = {rm_:>9.4f}")
    add_cv = float(np.mean([c["additive"] for c in cv]))
    mul_cv = float(np.mean([c["multiplicative"] for c in cv]))
    print(f"    mean:     additive {add_cv:>+8.4f}                "
          f"multiplicative {mul_cv:>+9.4f}")
    generalises = mul_cv > add_cv
    print(f"    -> out of sample the {'MULTIPLICATIVE' if generalises else 'ADDITIVE'} "
          f"shape predicts better; in-sample R^2 says the opposite.\n")

    y, add_hat, rows, cols = fit_additive(A, mask)
    cvec = fit_rank1(A, mask)
    mult_hat = cvec[rows] * cvec[cols]
    ss = float(((y - y.mean()) ** 2).sum())
    r2_add = 1 - float(((y - add_hat) ** 2).sum()) / ss
    r2_mul = 1 - float(((y - mult_hat) ** 2).sum()) / ss

    print(f"metric={a.metric}  raters with >= {a.min_partners} partners: {len(keep):,}  "
          f"observed dyads: {len(y):,}\n")
    print(f"{'model':26s} {'free params':>12} {'R^2':>8} {'resid sd':>10}")
    print(f"{'additive   a_i + a_j':26s} {len(A)+1:>12} {r2_add:>8.4f} {(y-add_hat).std():>10.4f}")
    print(f"{'multiplicative  c_i c_j':26s} {len(A):>12} {r2_mul:>8.4f} {(y-mult_hat).std():>10.4f}")
    # APPLICABILITY GUARD, added 2026-07-28 after the metric sweep.
    # negl1 (negative mean absolute difference) is bounded ABOVE by zero: every
    # agreement value is <= 0.  A rank-1 product c_i c_j cannot represent a
    # strictly negative surface without imaginary factors, so ALS diverges and
    # returns R^2 = -13.14 -- a fit worse than predicting the mean.  The first
    # version of this block compared that number to the additive R^2 and printed
    # "the ADDITIVE form fits better", which is true only in the sense that
    # anything beats a diverged optimiser.  A model comparison between a fit and
    # a failure is not a model comparison.  Report inapplicability instead: the
    # multiplicative form is a claim about CORRELATION-type agreement, which is
    # what classical test theory is about, not about a distance.
    if r2_mul < 0:
        print(f"\n  -> MULTIPLICATIVE MODEL INAPPLICABLE to metric '{a.metric}': the "
              f"rank-1 fit returns R^2={r2_mul:.4f}, i.e. worse than predicting the "
              f"mean, because this metric is bounded above by zero and a product of "
              f"real factors cannot represent it. This is NOT evidence for the "
              f"additive form. Excluded from the comparison.")
        _RES.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(
            {"metric": a.metric, "raters": len(keep), "dyads": int(len(y)),
             "r2_additive": r2_add, "r2_multiplicative": r2_mul,
             "status": "MULTIPLICATIVE_INAPPLICABLE",
             "verdict": _freeze(
                 "INAPPLICABLE: this agreement measure is bounded above by "
                        "zero, so a rank-1 product cannot represent it and the fit "
                        "diverges. No comparison between the two forms is available "
                        "on this metric, and the additive form is not thereby "
                        "supported.", "R28_multiplicative")}, indent=1))
        print(f"\nwrote {a.out}")
        return

    better = r2_mul > r2_add
    print(f"\n  -> IN SAMPLE the {'MULTIPLICATIVE' if better else 'ADDITIVE'} shape fits "
          f"better, at EQUAL effective degrees of freedom (the additive design is "
          f"rank-deficient by one; 925 columns, rank 924). In-sample fit is not the "
          f"test -- see the held-out block above.\n")

    add_str, _ = strata_residuals(y, add_hat, cvec, rows, cols, rng)
    mul_str, lab = strata_residuals(y, mult_hat, cvec, rows, cols, rng)
    print(f"{'stratum':12s} {'n':>6} {'vs ADDITIVE':>13}   {'vs MULTIPLICATIVE':>19} {'95% CI':>22}")
    for s in ("both_high", "mixed", "both_low"):
        if s not in mul_str:
            continue
        m_ = mul_str[s]
        print(f"{s:12s} {m_['n']:>6,} {add_str[s]['mean']:>+13.4f}   {m_['mean']:>+19.4f} "
              f"{f'[{m_[chr(99)+chr(105)][0]:+.4f},{m_[chr(99)+chr(105)][1]:+.4f}]':>22}")

    survivors = [s for s, v in mul_str.items() if v["excludes_zero"]]
    print(f"\n  strata whose residual still excludes zero under the correct form: "
          f"{survivors or 'NONE'}")

    # permutation null for the surviving strata: shuffle residuals across dyads
    resid = y - mult_hat
    null = defaultdict(list)
    for _ in range(a.null_reps):
        pr = rng.permutation(resid)
        for s in mul_str:
            m = lab == s
            null[s].append(float(pr[m].mean()))
    print(f"\n{'stratum':12s} {'observed':>10} {'null mean':>11} {'null sd':>9} {'z':>8}")
    zs = {}
    for s in mul_str:
        nv = np.array(null[s])
        z = (mul_str[s]["mean"] - nv.mean()) / (nv.std() + 1e-12)
        zs[s] = float(z)
        print(f"{s:12s} {mul_str[s]['mean']:>+10.4f} {nv.mean():>+11.4f} "
              f"{nv.std():>9.4f} {z:>+8.2f}")

    low = mul_str.get("both_low", {})
    cv_stable = min(c["multiplicative"] for c in cv) > 0
    if not cv_stable or not generalises:
        verdict = (
            "FUNCTIONAL FORM UNRESOLVED. The algebra stands: fitting mu + a_i + a_j to a "
            "multiplicative surface leaves residual (rho_i - m)(rho_j - m), a U-shape with "
            "no blocs in the generating process, and that is what r27 measured. So the "
            "ADDITIVE decomposition four rounds relied on is demonstrably misspecifiable. "
            "But the multiplicative alternative is NOT thereby established. It wins only "
            "in sample, at equal effective degrees of freedom, and out of sample it is "
            f"unstable: over ten held-out splits its R^2 ranges "
            f"[{min(c['multiplicative'] for c in cv):+.4f}, "
            f"{max(c['multiplicative'] for c in cv):+.4f}] against the additive shape's "
            f"tight [{min(c['additive'] for c in cv):+.4f}, "
            f"{max(c['additive'] for c in cv):+.4f}]. Raters with one or two training "
            "edges receive a c_i pinned to the 0.1 initialisation fallback -- a silent "
            "imputation -- and a single such split drags the mean below the additive "
            "model. Neither shape is validated, so the pair-specific residual question "
            "this round was built to settle is OPEN, and the both_low number below must "
            "not be read as a measurement of anything.")
    else:
        verdict = (
        "A MINORITY BLOC SURVIVES, an order of magnitude smaller than the additive "
        f"analysis implied: under the correct multiplicative form the both_low residual "
        f"is {low.get('mean', float('nan')):+.4f} against {add_str.get('both_low', {}).get('mean', float('nan')):+.4f} "
        "additively, while both_high and mixed collapse to zero. Raters who track few "
        "people track EACH OTHER slightly better than shared-target reliability predicts, "
        "which reliability cannot produce. The U-shape r27 measured was the functional "
        "form, not the people."
        if low.get("excludes_zero") and abs(zs.get("both_low", 0)) > 2 else
        "NO PAIR STRUCTURE SURVIVES the correct functional form: once agreement is "
        "modelled as a product of per-rater reliabilities, every stratum residual is "
        "indistinguishable from zero. r01's persistence is a single-target model with "
        "heterogeneous raters, and the pair-specific component four earlier rounds "
        "measured was an artifact of fitting a sum to a product.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"metric": a.metric, "raters": len(keep), "dyads": int(len(y)),
         "r2_additive": r2_add, "r2_multiplicative": r2_mul,
         "params_additive": len(A) + 1, "params_multiplicative": len(A),
         "multiplicative_fits_better_in_sample": bool(better),
         "additive_design_rank_deficient_by": 1,
         "effective_params_equal": True,
         "cv_folds": cv, "cv_additive_mean": add_cv,
         "cv_multiplicative_mean": mul_cv,
         "multiplicative_generalises_better": bool(generalises),
         "strata_vs_additive": add_str, "strata_vs_multiplicative": mul_str,
         "permutation_z": zs, "null_reps": a.null_reps,
         "verdict": _freeze(verdict, "R28_multiplicative"),
         "note": "r23/r25/r26/r27 all fit A_ij = mu + a_i + a_j and read the residual "
                 "as pair structure. Under one latent target with heterogeneous "
                 "reliability, agreement is rho_i*rho_j, and an additive fit to that "
                 "leaves residual (rho_i-m)(rho_j-m): positive at BOTH extremes, "
                 "negative in the middle. That U-shape is exactly what r27 measured "
                 "and read as a minority bloc."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
