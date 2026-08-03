#!/usr/bin/env python3
"""
ARTIFACT AUDIT -- the shortcut explanations for the core's deficit that have
nothing to do with compilation quality.

The ladder says the shipped core reaches Phi = 0.827 while a four-line
mechanical compiler built from the same criteria reaches 0.862.  Before that
gap can be read as compilation loss, three cheaper explanations have to be
killed, and each one is a property of the TEXT or of the JUDGE, not of the
compiler's choices:

  A1  DISCRIMINATION.  A criterion whose satisfaction is nearly the same on all
      four responses contributes nothing but noise to a unit-weighted sum.  If
      the core's criteria are less discriminative than the full ones, the gap is
      an instrument property.  MEASURED, not assumed.
  A2  LENGTH / STYLE.  Core criteria are edited sentences; full criteria are
      raw crowd fragments.  A length-matched mechanical compiler (built only
      from full criteria in the core's own length band) prices this.
  A3  SATURATION.  A judge pinned at 0 or 1 has no resolution left.  Measured as
      the share of |sat - 0.5| > 0.45 and the within-prompt across-response
      range.

Each check reports what it would take for the artifact to explain the whole
0.035 gap, so that "it is not the explanation" is a quantitative statement
rather than a reassurance.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import run as R

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
out = {}


def main():
    joined, how = R.load_join()
    sat_full, sat_core = R.load_sat("full"), R.load_sat("core")
    bundles, drop = R.build(joined, sat_full, sat_core)
    rub = {p: r for p, _c, r in joined}
    rng = np.random.default_rng(11)
    print(f"bundles={len(bundles)}")

    # ---- A1 discrimination --------------------------------------------------
    df, dc, rf, rc = [], [], [], []
    for pid, b in bundles.items():
        df += list(b["Sf"].std(1)); dc += list(b["Sc"].std(1))
        rf += list(b["Sf"].max(1) - b["Sf"].min(1))
        rc += list(b["Sc"].max(1) - b["Sc"].min(1))
    out["A1_discrimination"] = dict(
        full_sd_across_responses=float(np.mean(df)), core_sd_across_responses=float(np.mean(dc)),
        full_range=float(np.mean(rf)), core_range=float(np.mean(rc)),
        n_full=len(df), n_core=len(dc),
        core_over_full_sd=float(np.mean(dc) / np.mean(df)))
    print("A1", json.dumps(out["A1_discrimination"], indent=1))

    # ---- A3 saturation ------------------------------------------------------
    sf = np.concatenate([b["Sf"].ravel() for b in bundles.values()])
    sc = np.concatenate([b["Sc"].ravel() for b in bundles.values()])
    out["A3_saturation"] = dict(
        full_frac_saturated=float((np.abs(sf - 0.5) > 0.45).mean()),
        core_frac_saturated=float((np.abs(sc - 0.5) > 0.45).mean()),
        full_mean=float(sf.mean()), core_mean=float(sc.mean()),
        full_sd=float(sf.std()), core_sd=float(sc.std()))
    print("A3", json.dumps(out["A3_saturation"], indent=1))

    # ---- A2 length / style --------------------------------------------------
    lf, lc = [], []
    for pid, b in bundles.items():
        r = rub[pid]
        lf += [len(c["criterion"]) for c in r["coval_full"]]
        lc += [len(c["criterion"]) for c in r["coval_core"]]
    lo, hi = float(np.percentile(lc, 10)), float(np.percentile(lc, 90))
    out["A2_length"] = dict(full_mean_chars=float(np.mean(lf)),
                            core_mean_chars=float(np.mean(lc)),
                            core_band_p10_p90=[lo, hi])
    print("A2 lengths", json.dumps(out["A2_length"], indent=1))

    # LENGTH-MATCHED mechanical compiler: same rule as top4_pos but drawn only
    # from full criteria inside the core's own length band.
    C_ = R.cache(bundles, "z", "mean")
    res = defaultdict(list)
    nband = []
    for pid, b in bundles.items():
        Zf, Zc, w = C_[pid]
        L = np.array([len(c["criterion"]) for c in rub[pid]["coval_full"]], float)
        tgt = w @ Zf
        k = min(4, Zf.shape[0])
        res["core"].append(R.pairwise_conc(Zc.sum(0), tgt))
        res["top4_pos"].append(R.pairwise_conc(Zf[np.argsort(-w)[:k]].sum(0), tgt))
        band = np.flatnonzero((L >= lo) & (L <= hi))
        nband.append(len(band))
        if len(band) >= 1:
            kk = min(4, len(band))
            sel = band[np.argsort(-w[band])[:kk]]
            res["top4_pos_lenmatched"].append(R.pairwise_conc(Zf[sel].sum(0), tgt))
            res["core_paired"].append(R.pairwise_conc(Zc.sum(0), tgt))
            # SIZE-MATCHED SHAM for the length band: the SAME restriction in
            # size, drawn at random.  Any drop this sham reproduces is caused by
            # having fewer criteria to choose from, NOT by length.  Without it,
            # "length explains 59% of the gap" is a claim about pool size.
            rsel = rng.permutation(Zf.shape[0])[:len(band)]
            kk = min(4, len(rsel))
            sel = rsel[np.argsort(-w[rsel])[:kk]]
            res["top4_pos_SHAM_lenband_size"].append(R.pairwise_conc(Zf[sel].sum(0), tgt))
        # DISCRIMINATION-MATCHED: pick the 4 highest-weight criteria among those
        # whose across-response sd is closest to the core's mean sd on this prompt
        tgt_sd = float(b["Sc"].std(1).mean())
        npool = max(4, Zf.shape[0] // 2)
        near = np.argsort(np.abs(b["Sf"].std(1) - tgt_sd))[:npool]
        kk = min(4, len(near))
        sel = near[np.argsort(-w[near])[:kk]]
        res["top4_pos_discrimmatched"].append(R.pairwise_conc(Zf[sel].sum(0), tgt))
        # SIZE-MATCHED SHAM for the discrimination match, same pool size.
        rsel = rng.permutation(Zf.shape[0])[:npool]
        kk = min(4, len(rsel))
        sel = rsel[np.argsort(-w[rsel])[:kk]]
        res["top4_pos_SHAM_discrim_size"].append(R.pairwise_conc(Zf[sel].sum(0), tgt))
    out["A2_matched_compilers"] = {k: float(np.mean(v)) for k, v in res.items()}
    out["A2_matched_compilers"]["n_in_band_mean"] = float(np.mean(nband))
    out["A2_matched_compilers"]["n_prompts_with_band"] = int(len(res["core_paired"]))
    print("A2 matched", json.dumps(out["A2_matched_compilers"], indent=1))

    M = out["A2_matched_compilers"]
    gap = M["top4_pos"] - M["core"]
    gl = M["top4_pos_lenmatched"] - M["core_paired"]
    gd = M["top4_pos_discrimmatched"] - M["core"]
    gls = M["top4_pos_SHAM_lenband_size"] - M["core_paired"]
    gds = M["top4_pos_SHAM_discrim_size"] - M["core"]
    out["verdict"] = dict(
        raw_gap_top4pos_minus_core=gap,
        gap_after_length_matching=gl,
        gap_after_SIZE_MATCHED_SHAM_for_length=gls,
        gap_after_discrimination_matching=gd,
        gap_after_SIZE_MATCHED_SHAM_for_discrimination=gds,
        # The honest attribution: how much of the shrinkage survives once the
        # size-matched sham has been subtracted.  If sham == matched, the
        # covariate explained NOTHING and the pool size explained everything.
        length_effect_net_of_pool_size=float(gl - gls),
        discrimination_effect_net_of_pool_size=float(gd - gds),
        share_of_gap_explained_by_length_NET=(
            float((gls - gl) / gap) if abs(gap) > 1e-9 else None),
        share_of_gap_explained_by_discrimination_NET=(
            float((gds - gd) / gap) if abs(gap) > 1e-9 else None),
        note=("A restriction to a smaller candidate pool lowers Phi by itself. "
              "Any 'the covariate explains the gap' claim must be net of the "
              "size-matched sham, or it is a claim about pool size."))
    print("VERDICT", json.dumps(out["verdict"], indent=1))
    (RES / "artifact_checks.json").write_text(json.dumps(out, indent=1, default=float))
    print("wrote results/artifact_checks.json")


if __name__ == "__main__":
    main()
