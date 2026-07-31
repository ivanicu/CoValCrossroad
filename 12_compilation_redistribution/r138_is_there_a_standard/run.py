"""r138 -- is there a collective standard to aggregate? Zero model, straight off the release.

WHY THIS ROUND EXISTS
---------------------
The release does not ship its own satisfaction scores, so every comparison this campaign has made
routes through a rebuilt local 2B judge and is, strictly, a claim about what that model thinks. Ten
of eleven claims sit in that half. This round is in the other half: nothing here touches a model.

A3 says aggregating criteria across participants produces a COLLECTIVE STANDARD. Before asking
whether the compilation preserves it, ask whether it exists. If raters do not agree about which
criteria matter, there is nothing to aggregate -- not aggregated badly, but no object.

    ICC(1)  =  var_between_criteria / (var_between_criteria + var_within_criteria)

Between-criteria variance is the shared part: criteria the panel agrees are important score high
for everyone. Within-criteria variance is disagreement: the same criterion pulling +8 from one
person and -6 from another. ICC near 1 means a standard people read off; ICC near 0 means the
rating is about the rater, not the criterion.

TWO FLOORS, BECAUSE THE RAW NUMBER MEANS NOTHING ALONE
-------------------------------------------------------
RATER-STYLE NULL   Permute each rater's ratings ACROSS the criteria they rated, preserving that
                   person's own marginal distribution exactly -- their scale usage, their
                   extremeness, their mean. Any ICC this produces is what rater style alone gives
                   when nobody is reading the criterion at all. The observed ICC only means
                   something above it.
CRITERION-STYLE    Permute within criterion across raters. Destroys nothing (the criterion's own
                   set of numbers is preserved) so this must return the observed value; it is the
                   arithmetic check that the estimator is not broken.

AND THE SCALE ITSELF
--------------------
A6 says the -10..+10 ratings carry usable importance information. If the panel only ever writes +10
and -10, the scale is a two-valued vote wearing a 21-point costume, and "importance weight" is a
description of the form rather than the content. Measured here because it costs one histogram.

PRE-REGISTERED (fixed before any ICC was computed)
---------------------------------------------------
W-STANDARD-EXISTS   observed ICC exceeds the rater-style null by more than 0.10 and is itself above
                    0.40. There is a shared object; aggregating it is meaningful.
W-WEAK-STANDARD     observed exceeds the null by more than 0.10 but sits below 0.40. Something
                    shared exists and is swamped by disagreement; any aggregate is a summary of a
                    minority of the variance and must say so.
W-NO-STANDARD       observed does not exceed the rater-style null by 0.10. The ratings are about
                    raters. A3 has no referent and every claim about "collective values" in this
                    release, and in this campaign, loses its object.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx.stamp import stamp  # noqa: E402

RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
MIN_RATERS = 4          # pre-registered: the release has a literal hole at n=2 and n=3
SEEDS = (8101, 4409, 20260730, 31337, 271828)
N_PERM = 400
N_BOOT = 2000
MARGIN = 0.10           # pre-registered: observed must beat the null by this to mean anything
STRONG = 0.40


def icc1(groups):
    """One-way random-effects ICC(1) over ragged groups. Between over between-plus-within, using
    the standard unbiased mean-square form so unequal group sizes are handled rather than ignored."""
    ns = np.array([len(g) for g in groups], float)
    k = len(groups)
    N = ns.sum()
    if k < 2 or N <= k:
        return float("nan")
    gm = np.concatenate(groups).mean()
    means = np.array([g.mean() for g in groups])
    msb = float(((ns * (means - gm) ** 2).sum()) / (k - 1))
    msw = float(sum(((g - g.mean()) ** 2).sum() for g in groups) / (N - k))
    n0 = (N - (ns ** 2).sum() / N) / (k - 1)
    denom = msb + (n0 - 1) * msw
    return float((msb - msw) / denom) if denom > 0 else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r138_is_there_a_standard.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    if not RUBRICS.exists():
        print(f"REFUSING: missing {RUBRICS}. Exits 2, never 0.", file=sys.stderr)
        return 2

    crit = []                       # list of (cid, np.array of scores, list of annotator ids)
    by_rater = defaultdict(list)    # annotator -> list of (criterion index in `crit`, score)
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        for it in (r.get("coval_full") or []):
            sc = it.get("scores") or []
            if len(sc) < MIN_RATERS:
                continue
            idx = len(crit)
            crit.append((cid, np.array([x["score"] for x in sc], float),
                         [x["annotator_id"] for x in sc]))
            for x in sc:
                by_rater[x["annotator_id"]].append((idx, float(x["score"])))

    if len(crit) < 50:
        print(f"REFUSING: only {len(crit)} criteria clear the {MIN_RATERS}-rater floor. Exits 2.",
              file=sys.stderr)
        return 2
    groups = [c[1] for c in crit]
    allv = np.concatenate(groups)
    print(f"{len(crit):,} criteria with >= {MIN_RATERS} raters, {len(allv):,} ratings, "
          f"{len(by_rater):,} raters")

    # ---- the scale, because A6 rests on it ---------------------------------------------------
    print(f"\n  THE SCALE -10..+10, as actually used")
    for lo, hi, nm in ((10, 10, "exactly +10"), (-10, -10, "exactly -10"), (0, 0, "exactly 0")):
        m = ((allv >= lo) & (allv <= hi)).mean()
        print(f"    {nm:<14}{m:>8.1%}")
    ext = ((allv == 10) | (allv == -10)).mean()
    print(f"    {'|value| = 10':<14}{ext:>8.1%}      distinct values used: "
          f"{len(np.unique(allv))} of 21")
    print(f"    mean {allv.mean():+.2f}   sd {allv.std():.2f}   "
          f"median {np.median(allv):+.1f}")

    # ---- the observed ICC ---------------------------------------------------------------------
    obs = icc1(groups)
    print(f"\n  OBSERVED ICC(1) over criteria: {obs:.4f}")

    # ---- floor 1: rater-style null, permuting WITHIN each rater --------------------------------
    rater_ids = list(by_rater)
    null1 = []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        for _ in range(N_PERM // len(SEEDS)):
            buckets = defaultdict(list)
            for a in rater_ids:
                pairs = by_rater[a]
                vals = np.array([v for _i, v in pairs], float)
                rng.shuffle(vals)                      # this person's own marginal, reassigned
                for (i, _old), v in zip(pairs, vals):
                    buckets[i].append(v)
            g = [np.array(v) for v in buckets.values() if len(v) >= MIN_RATERS]
            if len(g) >= 50:
                null1.append(icc1(g))
    null1 = np.array([x for x in null1 if np.isfinite(x)])
    print(f"  RATER-STYLE NULL  (each rater's own numbers reassigned across the criteria they "
          f"rated)\n    mean {null1.mean():.4f}  sd {null1.std():.4f}  "
          f"95% range [{np.percentile(null1,2.5):.4f}, {np.percentile(null1,97.5):.4f}]  "
          f"({len(null1)} permutations, {len(SEEDS)} seeds)")

    # ---- floor 2: the arithmetic check --------------------------------------------------------
    rng = np.random.default_rng(SEEDS[0] + 1)
    g2 = [rng.permutation(g) for g in groups]
    chk = icc1(g2)
    print(f"  ARITHMETIC CHECK  permuting WITHIN each criterion preserves its numbers, so the "
          f"estimator must return the observed value: {chk:.6f} vs {obs:.6f}, "
          f"|diff| {abs(chk-obs):.2e}")

    # ---- positive control: a planted standard --------------------------------------------------
    pc = {}
    for rho in (0.0, 0.3, 0.7):
        rng = np.random.default_rng(SEEDS[1])
        gp = []
        for g in groups:
            mu = rng.normal(0, np.sqrt(rho))
            gp.append(mu + rng.normal(0, np.sqrt(1 - rho), size=len(g)))
        pc[rho] = icc1(gp)
    print(f"  POSITIVE CONTROL  planted ICC 0.0 -> {pc[0.0]:.4f}, 0.3 -> {pc[0.3]:.4f}, "
          f"0.7 -> {pc[0.7]:.4f}   (the estimator recovers what is planted)")

    # ---- uncertainty on the observed, clustered on the prompt ----------------------------------
    by_prompt = defaultdict(list)
    for i, (cid, _v, _a) in enumerate(crit):
        by_prompt[cid].append(i)
    cids = list(by_prompt)
    bs = []
    for s in SEEDS:
        rng = np.random.default_rng(s + 5)
        for _ in range(N_BOOT // len(SEEDS)):
            pick = rng.integers(0, len(cids), len(cids))
            g = [groups[i] for j in pick for i in by_prompt[cids[j]]]
            v = icc1(g)
            if np.isfinite(v):
                bs.append(v)
    bs = np.array(bs)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"  observed ICC 95% CI (clustered on prompt, {len(bs)} fits): [{lo:.4f}, {hi:.4f}]")

    excess = obs - null1.mean()
    world = ("W-STANDARD-EXISTS" if excess > MARGIN and obs > STRONG else
             "W-WEAK-STANDARD" if excess > MARGIN else "W-NO-STANDARD")
    conclusion = (
        f"No model is involved anywhere in this round. Over {len(crit):,} coval_full criteria rated "
        f"by at least {MIN_RATERS} people ({len(allv):,} ratings from {len(by_rater):,} raters), the "
        f"share of rating variance that is BETWEEN criteria rather than between raters of the same "
        f"criterion is ICC(1) = {obs:.4f} [{lo:.4f}, {hi:.4f}]. The floor that makes that number "
        f"mean anything is a rater-style null -- each person's own ratings reassigned across the "
        f"criteria they rated, preserving their scale usage and extremeness exactly -- which gives "
        f"{null1.mean():.4f} (sd {null1.std():.4f}). Excess over the floor: {excess:+.4f} against a "
        f"pre-registered margin of {MARGIN}. The estimator recovers planted ICCs of 0.0, 0.3 and 0.7 "
        f"as {pc[0.0]:.4f}, {pc[0.3]:.4f}, {pc[0.7]:.4f}, and permuting within a criterion returns "
        f"the observed value to {abs(chk-obs):.2e}. On the scale itself, {ext:.1%} of all ratings "
        f"are exactly +10 or -10 and {len(np.unique(allv))} of the 21 available values are used at "
        f"all. WORLD: {world}. "
        + ("There is a shared object that raters are reading off, and aggregating it is meaningful."
           if world == "W-STANDARD-EXISTS" else
           "Something shared exists and is swamped by disagreement: an aggregate summarises a "
           "minority of the variance in what people said mattered, and must be stated as such "
           "rather than as the panel's view."
           if world == "W-WEAK-STANDARD" else
           "The ratings are about raters, not criteria. A3 has no referent: there is no collective "
           "standard being aggregated, and every claim about collective values in this release -- "
           "and in this campaign -- loses its object."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_criteria": len(crit), "n_ratings": int(len(allv)), "n_raters": len(by_rater),
         "min_raters": MIN_RATERS, "icc_observed": obs, "icc_ci": [float(lo), float(hi)],
         "rater_style_null_mean": float(null1.mean()), "rater_style_null_sd": float(null1.std()),
         "excess_over_null": float(excess), "margin": MARGIN, "strong": STRONG,
         "arithmetic_check": float(chk), "positive_control": {str(k): float(v)
                                                              for k, v in pc.items()},
         "share_extreme_10": float(ext), "distinct_values_used": int(len(np.unique(allv))),
         "mean_rating": float(allv.mean()), "sd_rating": float(allv.std()),
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
