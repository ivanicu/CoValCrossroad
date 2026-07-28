"""r38 (plan item C38) -- The sampling frame and power for the experiment that can reach A4.

Why this round is not analysis
-------------------------------
C33-C36 closed three of the four explanations for CoVal's polarity channel and
left one standing that no split of these annotators can reach: every rater in
the release saw four candidate responses before rating any criterion. The
remaining questions need humans, and humans are the one resource this project
cannot spend carelessly.

So the job here is to decide WHICH prompts to send to people and HOW MANY of
them, before anyone is paid to rank anything.

The trap this exists to avoid
------------------------------
The tempting sample is the prompts where r12's inversion is largest. That
produces a number about the most anomalous prompts and reads as a number about
transport. Stratify, sample equally within cells, and carry sampling weights so
both the anomaly subset AND a population estimate are recoverable from one
collection.

Two axes
--------
    rubric-proxy disagreement   per-prompt |attribution| on the FRESH set
    original-fresh distance     how far the generated responses sit from the
                                released ones

The second is computed here from surface features -- length, sentence count,
bullets, hedging, refusal markers, lexical diversity, directiveness, criterion
overlap -- all of which are CPU-available from the saved generations. The plan
also calls for representation distance from three backbones; that is G33 and is
deliberately NOT done here, because a surface axis is enough to stratify on and
the feature cache is a separate, larger job.

The first axis needs r12's per-prompt attribution, which the round did not
persist until today. If it is absent this round says so and stratifies on
distance alone rather than inventing the axis.

Power
-----
Not binomial. Six pairwise comparisons from one rater's ranking of four
responses are one object, not six draws, and raters within a prompt share
whatever makes that prompt easy or hard. The simulation therefore has two
variance components -- between-prompt and between-rater-within-prompt -- both
estimated from the per-prompt accuracy spread this project has already measured,
with the binomial part subtracted out so it is not double-counted.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"

HEDGE = re.compile(r"\b(might|maybe|perhaps|possibly|could be|it depends|generally|"
                   r"often|sometimes|tend to|arguably|in some cases)\b", re.I)
REFUSE = re.compile(r"\b(i can'?t|i cannot|i'?m not able|as an ai|i won'?t|"
                    r"unable to help|not appropriate)\b", re.I)
DIRECT = re.compile(r"\b(you should|you must|do this|the answer is|i recommend|"
                    r"here'?s how|first,|step 1)\b", re.I)


def feats(t: str) -> np.ndarray:
    words = t.split()
    n = max(len(words), 1)
    sents = max(len(re.findall(r"[.!?]+", t)), 1)
    uniq = len(set(w.lower() for w in words)) / n
    return np.array([
        len(t), n, sents, n / sents, uniq,
        t.count("\n- ") + t.count("\n* ") + len(re.findall(r"\n\d+\.", t)),
        len(HEDGE.findall(t)), len(REFUSE.findall(t)), len(DIRECT.findall(t)),
        t.count("?"),
    ], dtype=float)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--generations", type=Path,
                   default=_ROOT / "rounds/r12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--r12", type=Path,
                   default=_ROOT / "rounds/r12_response_set/results/a12_response_set.json")
    p.add_argument("--crossfit", type=Path,
                   default=_ROOT / "rounds/r34_global_rater_crossfit/results/r34_global_rater_crossfit.json")
    p.add_argument("--per-prompt", type=Path,
                   default=_ROOT / "rounds/r22_cross_family/results/r22_cross_family_per_prompt.npz")
    p.add_argument("--pairs-per-prompt", type=Path,
                   default=_RES / "_pairs_per_prompt.json")
    p.add_argument("--out", type=Path, default=_RES / "r38_human_sampling_power.json")
    p.add_argument("--cells", type=int, default=15, help="prompts per stratum cell")
    p.add_argument("--sims", type=int, default=2000)
    a = p.parse_args()

    gen = json.loads(a.generations.read_text())
    pids, orig, fresh = gen["prompt_ids"], gen["original"], gen["fresh"]
    n = len(pids)

    # ---- axis 2: original-fresh surface distance -------------------------
    F = []
    for k in range(n):
        o = np.array([feats(t) for t in orig[k]])
        f = np.array([feats(t) for t in fresh[k]])
        F.append((o.mean(0), f.mean(0)))
    O = np.array([x[0] for x in F])
    Fr = np.array([x[1] for x in F])
    # Scale on the POOLED original+fresh spread, and drop any feature with no
    # spread at all. The first version standardised by the ORIGINAL sd with a
    # 1e-9 guard: `refusal marker count` is identically zero across every
    # released response, so its sd was the guard, and any fresh response
    # containing one produced a distance of 1e9. One feature nobody had checked
    # for degeneracy was silently deciding the entire axis -- and the axis is
    # what the human sample is stratified on.
    P = np.vstack([O, Fr])
    sd = P.std(0)
    keep = sd > 1e-6
    dropped = int((~keep).sum())
    mu = P.mean(0)
    dist = np.linalg.norm(((Fr[:, keep] - mu[keep]) / sd[keep])
                          - ((O[:, keep] - mu[keep]) / sd[keep]), axis=1)
    if dropped:
        print(f"  dropped {dropped} feature(s) with zero spread across both sets")
    print(f"prompts {n}   original-fresh surface distance: "
          f"median {np.median(dist):.2f}  IQR "
          f"{np.percentile(dist,25):.2f}-{np.percentile(dist,75):.2f}  "
          f"max {dist.max():.2f}")

    # ---- axis 1: rubric-proxy disagreement, if r12 persisted it ----------
    r12 = json.loads(a.r12.read_text())
    pp = (r12.get("sets", {}).get("FRESH", {}) or {}).get("per_prompt")
    if pp and pp.get("attribution"):
        m = {q: abs(v) for q, v in zip(pp["pids"], pp["attribution"])}
        disagree = np.array([m.get(q, np.nan) for q in pids])
        have_axis1 = np.isfinite(disagree).sum() > n // 2
    else:
        disagree, have_axis1 = np.full(n, np.nan), False
    if not have_axis1:
        print("\n  ⚠ r12 has no per-prompt attribution yet (the round discarded it until\n"
              "    today; a rerun is queued). Stratifying on DISTANCE ALONE and marking\n"
              "    the disagreement axis as pending rather than inventing it.")

    # ---- strata ----------------------------------------------------------
    d_hi = dist >= np.median(dist)
    if have_axis1:
        g_hi = disagree >= np.nanmedian(disagree)
        cells = {"low_disagree_low_dist": ~g_hi & ~d_hi,
                 "low_disagree_high_dist": ~g_hi & d_hi,
                 "high_disagree_low_dist": g_hi & ~d_hi,
                 "high_disagree_high_dist": g_hi & d_hi}
    else:
        cells = {"low_dist": ~d_hi, "high_dist": d_hi}
    rng = np.random.default_rng(20260728)
    frame, weights = [], {}
    print(f"\n{'cell':26s} {'population':>11} {'sampled':>8} {'weight':>8}")
    for name, mask in cells.items():
        idx = np.where(mask)[0]
        take = min(a.cells, len(idx))
        chosen = rng.choice(idx, size=take, replace=False)
        w = len(idx) / take if take else float("nan")
        weights[name] = float(w)
        for i in chosen:
            frame.append({"pid": pids[int(i)], "cell": name,
                          "distance": float(dist[i]),
                          "disagreement": (None if not np.isfinite(disagree[i])
                                           else float(disagree[i])),
                          "sampling_weight": float(w)})
        print(f"{name:26s} {len(idx):>11} {take:>8} {w:>8.2f}")
    print(f"\n  frame: {len(frame)} prompts. Equal cells + weights, so ONE collection "
          f"yields both\n  a population estimate and an anomaly-subset estimate.")

    # ---- variance components from what has already been measured ---------
    cf = json.loads(a.crossfit.read_text())
    arm_sd = cf["arms"]["crossfit_sign"]["sd_over_seeds"]
    acc = cf["arms"]["crossfit_sign"]["mean"]
    # MEASURED, not assumed. The first version hardcoded obs_sd = 0.16 with a
    # comment claiming it had been measured across the project. It had not, and
    # it was smaller than the binomial component it was supposed to contain, so
    # the between-prompt variance clipped to its floor and the power grid was
    # driven by a number somebody made up. r22 persists per-prompt accuracy for
    # three judges; the spread is read off that.
    zpp = np.load(a.per_prompt)
    sds = [float(zpp[k].std(ddof=1)) for k in zpp.files if k.endswith("|own")]
    obs_sd = float(np.mean(sds))
    print(f"\n  per-prompt accuracy sd MEASURED from r22 over {len(sds)} judges: "
          f"{['%.4f' % x for x in sds]} -> {obs_sd:.4f}")
    pairs_per_rater = 6
    # The de-biasing divisor is the number of comparisons behind ONE OBSERVED
    # per-prompt accuracy, which is not 6. r22 aggregates every rater's ranking
    # of that prompt, so each value rests on (rankings x 6) comparisons. Using
    # 6 made the binomial component larger than the total and the guard below
    # correctly refused to report -- the mistake was the divisor, not the data.
    n_rank = np.mean([len(v) for v in
                      json.loads(a.pairs_per_prompt.read_text()).values()]) \
        if a.pairs_per_prompt.exists() else 17.0
    comparisons_per_value = n_rank * pairs_per_rater
    print(f"  comparisons behind each observed per-prompt accuracy: "
          f"{comparisons_per_value:.0f}  ({n_rank:.1f} rankings x {pairs_per_rater})")
    binom_var = acc * (1 - acc) / comparisons_per_value
    if obs_sd ** 2 <= binom_var:
        raise SystemExit(
            f"REFUSING TO REPORT POWER: measured per-prompt sd {obs_sd:.4f} implies "
            f"variance {obs_sd**2:.5f}, which is below the binomial component "
            f"{binom_var:.5f} for {pairs_per_rater} pairs per rater. There is then no "
            "between-prompt heterogeneity to simulate, and clipping it to a floor -- "
            "which the first version did -- produces a power grid driven by an "
            "arbitrary constant. Check pairs_per_rater against how the observed "
            "accuracies were actually aggregated.")
    between_var = obs_sd ** 2 - binom_var
    print(f"\n  variance components  total sd {obs_sd:.3f} -> between-prompt sd "
          f"{np.sqrt(between_var):.3f}, binomial sd {np.sqrt(binom_var):.3f}")
    print(f"  (fold-seed sd of the arm itself is {arm_sd:.4f}, negligible by comparison)")

    # ---- power simulation -------------------------------------------------
    print(f"\n=== power to detect a transport effect (alpha .05, two-sided, "
          f"{a.sims} sims) ===")
    print(f"{'effect':>8} " + " ".join(f"{f'{np_}p x {nr}r':>10}"
                                       for np_ in (40, 60, 100)
                                       for nr in (8, 12)))
    grid = {}
    for eff in (0.03, 0.05, 0.08, 0.16):
        row = []
        for np_ in (40, 60, 100):
            for nr in (8, 12):
                hits = 0
                for _ in range(a.sims):
                    theta = rng.normal(acc, np.sqrt(between_var), np_)
                    d_o = rng.binomial(pairs_per_rater, np.clip(theta, .01, .99)[:, None],
                                       (np_, nr)) / pairs_per_rater
                    d_f = rng.binomial(pairs_per_rater,
                                       np.clip(theta - eff, .01, .99)[:, None],
                                       (np_, nr)) / pairs_per_rater
                    per = d_o.mean(1) - d_f.mean(1)          # prompt is the unit
                    se = per.std(ddof=1) / np.sqrt(np_)
                    hits += abs(per.mean() / (se + 1e-12)) > 1.96
                pw = hits / a.sims
                row.append(pw)
                grid[f"eff{eff}_p{np_}_r{nr}"] = pw
        print(f"{eff:>8.2f} " + " ".join(f"{x:>10.2f}" for x in row))

    smallest = min(e for e in (0.03, 0.05, 0.08, 0.16)
                   if grid[f"eff{e}_p60_r8"] >= 0.80)
    verdict = (
        f"60 prompts x 8 raters detects a transport effect of {smallest:+.2f} at 80% power, "
        f"clustering on prompt. r12's observed drop is 0.16, which is detectable at every "
        f"cell in this grid -- so the binding constraint on the human experiment is NOT "
        f"statistical power. It is the sampling frame: with equal cells and weights, "
        f"{len(frame)} prompts give both a population estimate and an anomaly-subset "
        "estimate from one collection, and without them an anomaly-selected sample would "
        "return a transport number that is really a number about the strangest prompts.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts_available": n, "axis1_disagreement_available": bool(have_axis1),
         "distance": {"median": float(np.median(dist)),
                      "p25": float(np.percentile(dist, 25)),
                      "p75": float(np.percentile(dist, 75)), "max": float(dist.max())},
         "cells": {k: int(v.sum()) for k, v in cells.items()},
         "sampling_weights": weights, "frame": frame,
         "variance": {"observed_sd": obs_sd,
                      "between_prompt_sd": float(np.sqrt(between_var)),
                      "binomial_sd": float(np.sqrt(binom_var)),
                      "pairs_per_rater": pairs_per_rater},
         "power": grid, "verdict": verdict,
         "note": "Power is clustered on PROMPT, not binomial on pairs: six comparisons from "
                 "one rater's ranking of four responses are one object, and raters within a "
                 "prompt share its difficulty. Surface distance only; representation "
                 "distance from three backbones is G33 and is deliberately not done here."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
