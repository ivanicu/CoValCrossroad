"""r26 -- Decide the sign test by removing the split that made it undecidable.

The question this round exists to settle
----------------------------------------
r23 established that most of r01's cross-prompt persistence is an additive ACTOR
effect (47.2% of dyad variance) and that the pair-specific residual is real but
small.  What it could NOT settle is what that residual IS:

  M2   value blocs.  Out-bloc pairs disagree RELIABLY -- their residual is
       negative again and again, on prompt after prompt.
  M1b' a second axis of rater competence.  Pairs differ in how well they track
       each other, but a low-competence pair's agreement is ATTENUATED TOWARD
       ZERO, never driven below it.

The separator is an excess of pairs that are negative in *both* halves of their
prompt series.  Noise cannot manufacture that; only a real opposing structure can.

Why the previous version could not answer it
---------------------------------------------
r23 and r25 both estimate that excess by splitting each pair's prompts into two
random halves and asking whether both half-means are negative.  That estimator
carries the variance of the split itself, and the verdict moved with it:

    r23, 1 split, null at 1 split              z = +1.40   read as NULL
    r25, 25 splits observed / 5 in the null    z = +2.68   read as POSITIVE
    r25, 25 splits on BOTH sides (matched)     z = +2.26   marginal
    r23 smoke test, 2 null reps                z = +10.26  meaningless

Four answers to one question, differing only in how many coin flips were
averaged.  Whatever that is, it is not a measurement, and reporting any one of
them would have been reporting the estimator.

The fix
-------
Do not split.  A pair's residual series has a mean; use it.

    pair_mean[p] = mean of that pair's residuals over ALL its prompts

Under the null that pair identity carries nothing, pair_mean is a mean of
exchangeable residuals, so its distribution is symmetric about zero and its
spread is set purely by how many prompts the pair has.  Two statistics, both
computed on the same permutation null (residual values permuted across dyad
slots WITHIN each prompt, so the residual distribution is preserved and only
pair identity is destroyed):

  S1  weighted between-pair variance of pair_mean
        -> is there ANY pair-specific structure?  (direction-blind)
  S2  left-tail mass: fraction of pairs with pair_mean below the null's own
      5th percentile
        -> is that structure SIGNED, i.e. are there pairs that reliably
           DISAGREE?  This is the M2-vs-M1b' separator.

S2 is the decisive one.  A second competence axis inflates S1 and leaves S2 at
its null value, because attenuation is symmetric.  Blocs inflate both.

Restricted to pairs with >= MIN_PROMPTS shared prompts, because a pair seen
twice has a pair_mean that is mostly noise, and including them dilutes both
statistics toward the null -- conservative, but it wastes the signal.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))
from covalx.frozen import append_to as _freeze  # noqa: E402


import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def residual_series(data, cell, rng, permute=False):
    """Per-pair residual series after removing the additive actor effect."""
    res = defaultdict(list)
    for rec in data:
        mat = cell.standardize(rec["m"]) if cell_cfg["standardize"] else rec["m"]
        ag = cell.pair_agreements(mat, rec["raters"], cell_cfg["metric"],
                                  cell_cfg["min_overlap"])
        if len(ag) < 3:
            continue
        fit = cell.additive_fit(ag, rec["raters"])
        if fit is None:
            continue
        _yhat, resid, _r2 = fit
        vals = list(resid.values())
        if permute:
            vals = list(rng.permutation(vals))
        for k, v in zip(resid.keys(), vals):
            res[frozenset(k)].append(float(v))
    return res


def stats(series, min_prompts, tail_cut):
    """S1 weighted between-pair variance; S2 left-tail mass below tail_cut."""
    means, ns = [], []
    for vals in series.values():
        if len(vals) < min_prompts:
            continue
        means.append(float(np.mean(vals)))
        ns.append(len(vals))
    if len(means) < 50:
        return None
    means, ns = np.array(means), np.array(ns)
    w = ns / ns.sum()
    mu = float((w * means).sum())
    s1 = float((w * (means - mu) ** 2).sum())
    s2 = float(np.mean(means < tail_cut)) if tail_cut is not None else float("nan")
    return {"s1": s1, "s2": s2, "n_pairs": int(len(means)),
            "median_prompts": float(np.median(ns)), "means": means}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r26_sign_no_split.json")
    p.add_argument("--metric", default="pearson",
                   choices=["pearson", "spearman", "cosine", "negl1"])
    p.add_argument("--min-overlap", type=int, default=3)
    p.add_argument("--thr", default="majority")
    p.add_argument("--standardize", type=int, default=1)
    p.add_argument("--centre", type=int, default=1)
    p.add_argument("--min-prompts", type=int, default=3)
    p.add_argument("--null-reps", type=int, default=200)
    a = p.parse_args()

    global cell_cfg
    cell = _load("cell", "rounds/r25_actor_dyad_sweep/cell.py")
    cell_cfg = {"metric": a.metric, "min_overlap": a.min_overlap,
                "standardize": bool(a.standardize), "centre": bool(a.centre)}
    rng = np.random.default_rng(20260728)
    data = cell.load(a.data, a.thr)
    print(f"metric={a.metric}  prompts={len(data):,}  pairs need >= {a.min_prompts} prompts\n")

    obs_series = residual_series(data, cell, rng)
    # build the null FIRST so the tail cut is defined by the null, not by the data
    null_means = []
    null_s1 = []
    for i in range(a.null_reps):
        ns = residual_series(data, cell, rng, permute=True)
        st = stats(ns, a.min_prompts, None)
        if st:
            null_s1.append(st["s1"])
            null_means.append(st["means"])
        if (i + 1) % 50 == 0:
            print(f"  null {i+1}/{a.null_reps}", flush=True)
    pooled = np.concatenate(null_means)
    tail_cut = float(np.percentile(pooled, 5))
    print(f"\n  null 5th percentile of pair means = {tail_cut:+.5f}   (the tail cut)")

    obs = stats(obs_series, a.min_prompts, tail_cut)
    if obs is None:
        raise SystemExit("too few pairs meet --min-prompts")
    null_s2 = np.array([float(np.mean(m < tail_cut)) for m in null_means])
    null_s1 = np.array(null_s1)

    z1 = (obs["s1"] - null_s1.mean()) / (null_s1.std() + 1e-12)
    z2 = (obs["s2"] - null_s2.mean()) / (null_s2.std() + 1e-12)
    p1 = float((null_s1 >= obs["s1"]).mean())
    p2 = float((null_s2 >= obs["s2"]).mean())

    print(f"\n  pairs used: {obs['n_pairs']:,}   median prompts per pair: "
          f"{obs['median_prompts']:.0f}")
    print(f"\n  S1  between-pair variance   observed {obs['s1']:.6f}   "
          f"null {null_s1.mean():.6f} +- {null_s1.std():.6f}   z={z1:+.2f}  p={p1:.4g}")
    print(f"  S2  left-tail mass          observed {obs['s2']:.4f}   "
          f"null {null_s2.mean():.4f} +- {null_s2.std():.4f}   z={z2:+.2f}  p={p2:.4g}")

    # NAMES DESCRIBE THE TESTS, not the interpretation (FROZEN.md section 1,
    # entry 62). These are two dyad-permutation tail probabilities. The keys they
    # feed were called `pair_structure` and `structure_is_signed`, which asserted
    # the reading the freeze withdraws -- and a field NAME is unreachable by the
    # freeze text this file already carries. FROZEN.md records why s2 cannot bear
    # that reading: mean agreement is +0.25, so a centred residual gives "below
    # average" and "actually disagreeing" the SAME number.
    s1_exceeds_null = p1 < 0.05
    s2_exceeds_null = p2 < 0.05
    verdict = (
        "M2: pair identity carries structure AND that structure is signed -- there are "
        "pairs that reliably disagree, which attenuation toward zero cannot produce"
        if s1_exceeds_null and s2_exceeds_null else
        "M1b-PRIME: pair identity carries structure but it is NOT signed. A second axis "
        "of rater competence explains it as well as blocs do, and this observable cannot "
        "separate them"
        if s1_exceeds_null else
        "NO PAIR STRUCTURE: the residual is indistinguishable from a dyad-permutation null")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"cfg": {**cell_cfg, "thr": a.thr, "min_prompts": a.min_prompts},
         "null_reps": a.null_reps, "tail_cut": tail_cut,
         "n_pairs": obs["n_pairs"], "median_prompts_per_pair": obs["median_prompts"],
         "s1_observed": obs["s1"], "s1_null_mean": float(null_s1.mean()),
         "s1_null_sd": float(null_s1.std()), "s1_z": float(z1), "s1_p": p1,
         "s2_observed": obs["s2"], "s2_null_mean": float(null_s2.mean()),
         "s2_null_sd": float(null_s2.std()), "s2_z": float(z2), "s2_p": p2,
         "s1_exceeds_dyad_permutation_null": bool(s1_exceeds_null),
         "s2_exceeds_dyad_permutation_null": bool(s2_exceeds_null),
         "verdict": _freeze(verdict, "r26_sign_no_split"),
         "note": "no split-half anywhere. r23/r25 estimated the same quantity through a "
                 "random half-split and returned z = 1.40, 2.26, 2.68 and 10.26 for the "
                 "same data depending only on how many splits were averaged and whether "
                 "the null used the same number. This uses each pair's full residual "
                 "series, so there is no split variance to tune."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
