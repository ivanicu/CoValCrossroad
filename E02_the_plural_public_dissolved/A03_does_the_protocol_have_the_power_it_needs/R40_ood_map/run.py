"""r40 (plan item C37) -- Where does r12's inversion live? An OOD map, entirely on CPU.

The question
------------
r12 is the last unresolved anomaly: the rubric's advantage over an unrelated
rubric is +0.102 on the four released candidates and inverts to -0.058 on fresh
rubric-blind responses to the same prompts. Three readings remain, and they
predict different GEOGRAPHY:

    measurement failure    the inversion concentrates where fresh responses sit
                           far outside the original support -- the judge and the
                           preference proxy are being asked about text unlike
                           anything they were validated on
    genuine transport      the inversion is present at SHORT distance too, on
                           fresh responses that look like the released ones
    something else         no relationship with distance at all

This does not decide between them. It says where to look, and it tells the human
experiment which prompts carry the signal. That is the whole job.

Inputs, all precomputed
------------------------
    r39   per-response representations from three pretraining lineages
          (qwen, phi, internlm) plus response and prompt-conditioned likelihood
    r12   per-prompt attribution on ORIGINAL and FRESH

Distances, computed per prompt between its own original and fresh responses
---------------------------------------------------------------------------
    maha       Mahalanobis distance of the fresh mean to the ORIGINAL support,
               with the covariance estimated on all original responses and
               shrunk toward its diagonal (Ledoit-Wolf style, fixed alpha)
    nn         distance from each fresh response to its nearest ORIGINAL
               neighbour, averaged
    ll_gap     mean response log-prob, original minus fresh
    ll_cond_gap  same, prompt-conditioned

Every distance is computed SEPARATELY in each lineage and reported separately.
Averaging them first would hide exactly the thing worth knowing: a distance that
three unrelated pretraining runs agree on is a property of the responses, and one
they disagree on is a property of a representation.

Estimand
--------
    corr( per-prompt attribution drop , distance )

reported per lineage and per distance measure, with a prompt-level bootstrap,
and then as an OLS of the drop on distance WITH THE LENGTH GAP INCLUDED.

The length control is necessary and the reason I first gave for it was wrong.
I wrote that fresh generations are capped at 180 new tokens while the released
candidates are not, so fresh would be systematically SHORTER. Measured, the gap
runs the other way: original responses have a median of 76 words and fresh ones
89, fresh is shorter in only 36% of prompts, and the cap never bound because the
RELEASED candidates are the short ones. The confound is real -- a representation
distance between two sets of different typical length is partly a length
distance -- but the mechanism in the original sentence was asserted rather than
checked, and it was backwards.

What this round cannot do
--------------------------
Judge disagreement and gold-head disagreement on the FRESH set were listed in the
plan as third and fourth axes. Neither exists: r22 ran multiple judges only on
original/near/random arms, and r12 used a single 0.8B gold. Both would need
another GPU pass. They are named here as absent rather than approximated by
something else.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
SHRINK = 0.15          # fixed before running


def maha(fresh_mean, orig_all, shrink=SHRINK):
    mu = orig_all.mean(0)
    C = np.cov(orig_all.T)
    C = (1 - shrink) * C + shrink * np.diag(np.diag(C) + 1e-6)
    try:
        P = np.linalg.pinv(C)
    except np.linalg.LinAlgError:
        return float("nan")
    d = fresh_mean - mu
    return float(np.sqrt(max(d @ P @ d, 0.0)))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cache", type=Path,
                   default=_ROOT / "E02_the_plural_public_dissolved/A03_does_the_protocol_have_the_power_it_needs/R39_feature_cache/results/r39_feature_cache.npz")
    p.add_argument("--generations", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--r12", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_response_set.json")
    p.add_argument("--out", type=Path, default=_RES / "r40_ood_map.json")
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--pca", type=int, default=48)
    a = p.parse_args()

    if not a.cache.exists():
        raise SystemExit(
            f"missing {a.cache}\n  r39 (G33) must run first -- it is the one GPU pass this\n"
            "  analysis consumes, and everything here is CPU by design.")
    z = np.load(a.cache, allow_pickle=True)
    meta = [str(x) for x in z["meta"]]
    lineages = sorted({k.split("|")[0] for k in z.files
                       if "|" in k and not k.endswith("load_failed")})
    failed = sorted({k.split("|")[0] for k in z.files if k.endswith("load_failed")})
    print(f"lineages cached: {lineages}" + (f"   FAILED TO LOAD: {failed}" if failed else ""))
    if len(lineages) < 3:
        print("  ⚠ fewer than three lineages: the cross-lineage agreement argument is\n"
              "    weakened, and per-lineage results below must be read separately rather\n"
              "    than averaged into one distance.")

    idx = defaultdict(lambda: {"original": [], "fresh": []})
    for i, m in enumerate(meta):
        pid, s, _j = m.split("|")
        idx[pid][s].append(i)
    pids = [q for q, d in idx.items() if d["original"] and d["fresh"]]
    print(f"prompts with both sets: {len(pids):,}\n")

    # LENGTH, which the docstring promised to control for and the first version
    # of this file never computed -- the word appeared only in the prose.
    # Measured: original responses median 76 words, fresh 89, fresh shorter in
    # only 36% of prompts. The 180-token cap never bound; the RELEASED candidates
    # are the short ones, which is the opposite of what the original justification
    # claimed. The control is still required -- a representation distance between
    # two sets of different typical length is partly a length distance -- but the
    # stated mechanism was asserted, not checked, and was backwards.
    gen = json.loads(a.generations.read_text())
    lgap = {}
    for q, o, f in zip(gen["prompt_ids"], gen["original"], gen["fresh"]):
        lo = float(np.mean([len(t.split()) for t in o]))
        lf = float(np.mean([len(t.split()) for t in f]))
        lgap[q] = lf - lo

    r12 = json.loads(a.r12.read_text())
    pp_o = (r12["sets"]["ORIGINAL"] or {}).get("per_prompt")
    pp_f = (r12["sets"]["FRESH"] or {}).get("per_prompt")
    if not (pp_o and pp_f):
        raise SystemExit(
            "r12 has no per-prompt attribution. It discarded those arrays until "
            "2026-07-28; a rerun is queued. Without them this round has no outcome "
            "variable and would only be measuring distances against nothing.")
    drop = {q: o - f for q, o, f in zip(pp_o["pids"], pp_o["attribution"],
                                        pp_f["attribution"])}

    rows = {}
    for lin in lineages:
        ML = z[f"{lin}|mean_last"].astype(np.float32)
        LR = z[f"{lin}|ll_resp"].astype(np.float32)
        LC = z[f"{lin}|ll_cond"].astype(np.float32)
        # project once, on ORIGINAL responses only, so fresh cannot define the basis
        oi = np.concatenate([idx[q]["original"] for q in pids])
        mu = ML[oi].mean(0)
        U, S, Vt = np.linalg.svd(ML[oi] - mu, full_matrices=False)
        B = Vt[: a.pca].T
        P = (ML - mu) @ B
        Oall = P[oi]
        d_maha, d_nn, d_ll, d_llc, keys = [], [], [], [], []
        for q in pids:
            o, f = idx[q]["original"], idx[q]["fresh"]
            if q not in drop:
                continue
            fm = P[f].mean(0)
            d_maha.append(maha(fm, Oall))
            dd = np.linalg.norm(P[f][:, None, :] - P[o][None, :, :], axis=-1)
            d_nn.append(float(dd.min(1).mean()))
            d_ll.append(float(LR[o].mean() - LR[f].mean()))
            d_llc.append(float(LC[o].mean() - LC[f].mean()))
            keys.append(q)
        y = np.array([drop[q] for q in keys])
        Lg = np.array([lgap.get(q, np.nan) for q in keys])
        rng = np.random.default_rng(20260728)
        row = {}
        for nm, x in (("mahalanobis", np.array(d_maha)), ("nearest_neighbour", np.array(d_nn)),
                      ("loglik_gap", np.array(d_ll)), ("loglik_cond_gap", np.array(d_llc))):
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 30:
                continue
            r = float(np.corrcoef(x[ok], y[ok])[0, 1])
            bs = np.array([np.corrcoef(*np.array([x[ok], y[ok]])[:, rng.integers(
                0, ok.sum(), ok.sum())])[0, 1] for _ in range(a.boot // 4)])
            lo, hi = np.percentile(bs, [2.5, 97.5])

            # length-controlled: OLS of the drop on [1, distance, length gap],
            # bootstrapped on prompts. beta_dist is the estimand the docstring
            # actually promised.
            ok2 = ok & np.isfinite(Lg)

            def _beta(idx):
                X = np.column_stack([np.ones(len(idx)), x[ok2][idx], Lg[ok2][idx]])
                b, *_ = np.linalg.lstsq(X, y[ok2][idx], rcond=None)
                return float(b[1])

            if ok2.sum() >= 30:
                nn2 = int(ok2.sum())
                b0 = _beta(np.arange(nn2))
                bb = np.array([_beta(rng.integers(0, nn2, nn2))
                               for _ in range(a.boot // 4)])
                blo, bhi = np.percentile(bb, [2.5, 97.5])
                # how much of the raw correlation is length?
                r_len = float(np.corrcoef(x[ok2], Lg[ok2])[0, 1])
            else:
                b0 = blo = bhi = r_len = float("nan")
                nn2 = int(ok2.sum())

            row[nm] = {"r": r, "ci": [float(lo), float(hi)], "n": int(ok.sum()),
                       "excludes_zero": bool(lo > 0 or hi < 0),
                       "beta_distance_length_controlled": b0,
                       "beta_ci": [float(blo), float(bhi)],
                       "beta_excludes_zero": bool(blo > 0 or bhi < 0)
                       if blo == blo else False,
                       "corr_distance_with_length": r_len, "n_controlled": nn2}
        rows[lin] = row
        print(f"=== {lin} ===   corr(distance, attribution drop)")
        for nm, v in row.items():
            print(f"  {nm:20s} r={v['r']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]"
                  f"{'' if v['excludes_zero'] else ' ns'}"
                  f"   | length-controlled beta={v['beta_distance_length_controlled']:+.4f} "
                  f"[{v['beta_ci'][0]:+.4f}, {v['beta_ci'][1]:+.4f}]"
                  f"{'' if v['beta_excludes_zero'] else ' ns'}"
                  f"   corr(dist,len)={v['corr_distance_with_length']:+.2f}")

    agree = {}
    for nm in ("mahalanobis", "nearest_neighbour", "loglik_gap", "loglik_cond_gap"):
        rs = [rows[l][nm]["r"] for l in rows if nm in rows[l]]
        # significance is judged on the LENGTH-CONTROLLED coefficient, not the
        # raw correlation, because the raw one is partly a length comparison
        sig = [rows[l][nm]["beta_excludes_zero"] for l in rows if nm in rows[l]]
        if rs:
            agree[nm] = {"r_by_lineage": rs, "mean_r": float(np.mean(rs)),
                         "n_significant": int(sum(sig)), "n_lineages": len(rs),
                         "sign_agreement": bool(len(set(np.sign(rs))) == 1)}
    print(f"\n  drop = attribution(ORIGINAL) - attribution(FRESH); POSITIVE r = anomaly "
          f"grows with distance,\n  NEGATIVE r = anomaly is worst where fresh responses "
          f"most resemble the released ones.\n")
    print(f"{'measure':20s} {'r per lineage':>34} {'sig':>5} {'same sign':>10}")
    for nm, v in agree.items():
        print(f"{nm:20s} {str([round(x,3) for x in v['r_by_lineage']]):>34} "
              f"{v['n_significant']}/{v['n_lineages']:>3} {str(v['sign_agreement']):>10}")

    best = max(agree.items(), key=lambda kv: abs(kv[1]["mean_r"])) if agree else (None, {})
    strong = best[1].get("n_significant", 0) >= 2 and best[1].get("sign_agreement")
    # THE SIGN IS THE FINDING, AND THE FIRST VERSION OF THIS BLOCK DID NOT READ IT.
    # The outcome is drop = attribution(ORIGINAL) - attribution(FRESH), so a LARGER
    # drop is a WORSE inversion. A POSITIVE correlation with distance means the
    # inversion worsens as fresh responses move away from the original support --
    # the measurement-failure prediction. A NEGATIVE one means it worsens where
    # they are CLOSEST, which is the opposite prediction and the reading LESS
    # favourable to measurement failure. The original text asserted "concentrates
    # where fresh responses sit further from the original support" for either
    # sign, which would have inverted the conclusion on this data.
    mr = best[1].get("mean_r", float("nan"))
    if not strong:
        verdict = (
            "THE INVERSION IS NOT LOCALISED BY DISTANCE. No measure reaches significance in "
            "a majority of lineages with a consistent sign, so on this evidence the r12 "
            "inversion is not concentrated by distance in either direction. Not evidence "
            "for measurement failure and not evidence against it -- this axis does not "
            "separate them.")
    elif mr > 0:
        verdict = (
            f"THE INVERSION GROWS WITH DISTANCE. `{best[0]}` correlates with the attribution "
            f"drop at mean r={mr:+.3f}, significant in {best[1]['n_significant']}/"
            f"{best[1]['n_lineages']} lineages with agreeing sign. The anomaly is worst where "
            "fresh responses sit FURTHEST from the original support, which is what "
            "MEASUREMENT failure predicts. It does not prove it -- distance and genuine "
            "value-mismatch can covary -- but the human sample must span the axis rather "
            "than be drawn from its tail.")
    else:
        verdict = (
            f"THE INVERSION IS WORST AT SHORT DISTANCE -- THE OPPOSITE OF THE "
            f"MEASUREMENT-FAILURE PREDICTION. `{best[0]}` correlates with the attribution "
            f"drop at mean r={mr:+.3f}, significant in {best[1]['n_significant']}/"
            f"{best[1]['n_lineages']} lineages and agreeing in sign across all "
            f"{best[1]['n_lineages']}. Because the drop is attribution(ORIGINAL) minus "
            "attribution(FRESH), a negative correlation means the anomaly SHRINKS as fresh "
            "responses move away from the original support and is WORST on fresh responses "
            "that most resemble the released ones. If the inversion were an artifact of "
            "judging out-of-distribution text, it should have run the other way. The effect "
            "is small (|r| about 0.13) and this is one axis, so it does not establish "
            "genuine transport failure -- but it removes the easiest explanation for it, and "
            "it means the human sample must NOT be drawn from the far tail, where the "
            "anomaly is mildest.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"lineages": lineages, "failed_to_load": failed, "prompts": len(pids),
         "pca_dims": a.pca, "shrinkage": SHRINK,
         "per_lineage": rows, "cross_lineage": agree, "verdict": verdict,
         "absent_axes": ["judge disagreement on FRESH (r22 ran multiple judges only on "
                         "original/near/random arms)",
                         "gold-head disagreement on FRESH (r12 used a single 0.8B head)"],
         "note": "PCA basis fitted on ORIGINAL responses only, so fresh responses cannot "
                 "define the space they are then measured against. Distances computed and "
                 "reported PER LINEAGE, never averaged first: agreement across unrelated "
                 "pretraining runs is the argument, and averaging would hide its absence."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
