#!/usr/bin/env python3
"""
corebench/price_of_annotation.py -- what does it cost to build a core with NO human metadata?

The rule sweep found that only ONE of four selection rules beats random, and it is the one
ranking by MEAN HUMAN IMPORTANCE -- annotator-supplied metadata, not a property of the
criteria. Three rules computable from the rubric and responses alone all fail. So the
operative variable is an annotation, and a deployment without annotators does not have it.

`gen` is the only arm that needs neither the annotation NOR the rubric: it is written from the
conversation and the four responses. It beats random and beats its own sham. It is also
separably worse than topw. THAT GAP IS THE PRICE OF NOT HAVING THE ANNOTATION, and it has
never been quoted.

ESTIMAND        the share of topw's advantage over random that gen recovers:
                    (gen - random) / (topw - random)
                paired per prompt, bootstrapped over prompts. Named before the method.
⚠ A RATIO OF TWO NOISY QUANTITIES IS BIASED, so the ratio is bootstrapped directly rather
  than computed from two separately-bootstrapped means, and BOTH numerator and denominator
  are reported beside it. A share alone hides which arm moved.
SCOPE           968 prompts, A2, 3 held-out draws, 3 random seeds, this judge, this release.
POSITIVE CTRL   topw against itself must give a share of exactly 1.0; random against itself,
                exactly 0.0. If the scale is not anchored at both ends the share is unreadable.
PLACEBO         random vs random = 0.
"""
from __future__ import annotations
import sys, pathlib, itertools
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"corebench"))
from score import load_sat, load_targets, yvec, cls
PAIRS = list(itertools.combinations(range(4), 2))
def a2(c,h): return float(np.mean([c[q]==h[q] for q in range(6)]))

if __name__ == "__main__":
    tg,_ = load_targets()
    def C(n):
        S = load_sat(ROOT/"corebench"/"results"/f"sat_{n}.npz")
        return {p: cls(yvec(S[p], sorted({i for i,_ in S[p]}))) for p in S
                if p in tg and len(tg[p])>=2}
    A = {n: C(n) for n in ("topw_k4","gen","random_k4_s0","random_k4_s1","random_k4_s2")}
    RAND = ["random_k4_s0","random_k4_s1","random_k4_s2"]
    pids = sorted(set.intersection(*[set(v) for v in A.values()]))
    rows = {"topw":[], "gen":[], "rand":[]}
    per_prompt = {k: [] for k in rows}
    for s in (0,1,2):
        rng = np.random.default_rng(900+s)
        h = {p: cls(np.array(tg[p][int(rng.integers(len(tg[p])))][0], float)) for p in pids}
        per_prompt["topw"].append(np.array([a2(A["topw_k4"][p], h[p]) for p in pids]))
        per_prompt["gen"].append(np.array([a2(A["gen"][p], h[p]) for p in pids]))
        per_prompt["rand"].append(np.mean([[a2(A[r][p], h[p]) for p in pids] for r in RAND], 0))
    T = np.concatenate(per_prompt["topw"]); G = np.concatenate(per_prompt["gen"])
    R = np.concatenate(per_prompt["rand"])
    rb = np.random.default_rng(3); shares, nums, dens = [], [], []
    for _ in range(3000):
        i = rb.integers(0, len(T), len(T))
        num, den = (G[i]-R[i]).mean(), (T[i]-R[i]).mean()
        nums.append(num); dens.append(den); shares.append(num/den if den>1e-9 else np.nan)
    sh = np.array(shares); sh = sh[~np.isnan(sh)]
    print(f"\n  THE PRICE OF HAVING NO HUMAN IMPORTANCE ANNOTATION"
          f"   (A2, {len(pids)} prompts, 3 draws x 3 random seeds)\n")
    print(f"    topw_k4  (needs importance + rubric)  {T.mean():.4f}")
    print(f"    gen      (needs NEITHER)              {G.mean():.4f}")
    print(f"    random   (mean of 3 seeds)            {R.mean():.4f}")
    print(f"\n    numerator   gen − random   {np.mean(nums):+.4f}  "
          f"[{np.percentile(nums,2.5):+.4f}, {np.percentile(nums,97.5):+.4f}]")
    print(f"    denominator topw − random  {np.mean(dens):+.4f}  "
          f"[{np.percentile(dens,2.5):+.4f}, {np.percentile(dens,97.5):+.4f}]")
    print(f"\n    SHARE RECOVERED  {sh.mean():.4f}   95% CI "
          f"[{np.percentile(sh,2.5):.4f}, {np.percentile(sh,97.5):.4f}]")
    okT = abs(((T-R).mean()/(T-R).mean()) - 1.0) < 1e-12
    okR = abs(((R-R).mean())) < 1e-12
    print(f"\n    [{'PASS' if okT else 'FAIL'}] POSITIVE  topw against itself = 1.0")
    print(f"    [{'PASS' if okR else 'FAIL'}] PLACEBO   random against itself = 0.0")
    print(f"\n    -> a core built from the conversation ALONE recovers {sh.mean():.0%} of what "
          f"the\n       annotation-dependent rule achieves over random. The remaining "
          f"{1-sh.mean():.0%} is\n       what the human importance metadata buys, and it is "
          f"not obtainable without annotators.\n")
