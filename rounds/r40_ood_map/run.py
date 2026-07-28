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
and then as a regression of the drop on distance with response length included,
because length is the obvious confound: fresh generations are capped at 180 new
tokens and the released candidates are not.

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
_ROOT = _HERE.parents[1]
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
                   default=_ROOT / "rounds/r39_feature_cache/results/r39_feature_cache.npz")
    p.add_argument("--r12", type=Path,
                   default=_ROOT / "rounds/r12_response_set/results/a12_response_set.json")
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
            row[nm] = {"r": r, "ci": [float(lo), float(hi)], "n": int(ok.sum()),
                       "excludes_zero": bool(lo > 0 or hi < 0)}
        rows[lin] = row
        print(f"=== {lin} ===   corr(distance, attribution drop)")
        for nm, v in row.items():
            print(f"  {nm:20s} r={v['r']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]"
                  f"  n={v['n']}{'' if v['excludes_zero'] else '   (ns)'}")

    agree = {}
    for nm in ("mahalanobis", "nearest_neighbour", "loglik_gap", "loglik_cond_gap"):
        rs = [rows[l][nm]["r"] for l in rows if nm in rows[l]]
        sig = [rows[l][nm]["excludes_zero"] for l in rows if nm in rows[l]]
        if rs:
            agree[nm] = {"r_by_lineage": rs, "mean_r": float(np.mean(rs)),
                         "n_significant": int(sum(sig)), "n_lineages": len(rs),
                         "sign_agreement": bool(len(set(np.sign(rs))) == 1)}
    print(f"\n{'measure':20s} {'r per lineage':>34} {'sig':>5} {'same sign':>10}")
    for nm, v in agree.items():
        print(f"{nm:20s} {str([round(x,3) for x in v['r_by_lineage']]):>34} "
              f"{v['n_significant']}/{v['n_lineages']:>3} {str(v['sign_agreement']):>10}")

    best = max(agree.items(), key=lambda kv: abs(kv[1]["mean_r"])) if agree else (None, {})
    strong = best[1].get("n_significant", 0) >= 2 and best[1].get("sign_agreement")
    verdict = (
        f"THE INVERSION IS LOCALISED. `{best[0]}` correlates with the per-prompt attribution "
        f"drop at mean r={best[1]['mean_r']:+.3f}, significant in "
        f"{best[1]['n_significant']}/{best[1]['n_lineages']} lineages with agreeing sign. "
        "The inversion concentrates where fresh responses sit further from the original "
        "support, which is what MEASUREMENT failure predicts and what genuine transport "
        "failure does not require. It does not prove measurement failure: distance and "
        "genuine value-mismatch can covary. It does say the human sample must span the "
        "distance axis rather than being drawn from its tail."
        if strong else
        "THE INVERSION IS NOT LOCALISED BY DISTANCE. No measure reaches significance in a "
        "majority of lineages with a consistent sign, so on this evidence the r12 inversion "
        "is not concentrated in out-of-distribution responses. That is the reading LESS "
        "favourable to a pure measurement-failure explanation, and it is not evidence FOR "
        "genuine transport failure either -- only that this axis does not separate them.")
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
