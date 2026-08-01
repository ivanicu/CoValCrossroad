"""A calibrated jackknife: how concentrated is an effect, measured against what its own size allows.

r201 needed this and built it inline, and building it inline is how a check becomes a thing one
round did rather than a thing the project does. It also nearly shipped with an invented threshold
-- "fragile if deleting under 5% kills it" -- which is meaningless without knowing what a CLEAN
effect of the same size and n survives.

THE CALIBRATION IS THE WHOLE IDEA. Adversarially deleting the k most favourable observations will
kill any interval eventually; the number k is not interpretable on its own. So the reference is
simulated normal data with the SAME n, mean and sd -- no outliers by construction -- and the
question becomes whether the real data dies earlier than a clean effect of its size would.

    kill_at        deletions before the 95% interval touches zero
    reference      the same quantity on normal draws, as a distribution
    verdict        CONCENTRATED / NOT CONCENTRATED / MARGINAL -- and MARGINAL is not a hedge, it
                   is the case where the THRESHOLD ITSELF is noisier than the gap being judged

WHY THE VERDICT HAS THREE VALUES. Version one compared kill_at to a p10 estimated from one batch of
draws and returned a binary. Its first non-trivial use put a claim at 306 against a p10 of 314 --
and re-estimating that p10 with three other seeds gave 307, 311, 318. The verdict was a property of
the random seed. A threshold read off a simulation is a DISTRIBUTION, and a rule that reports it as
a line manufactures decisions out of Monte Carlo noise, which is the same defect as the invented
5% bar this module replaced. So the p10 is now estimated across several independent batches and a
result inside their spread is returned as MARGINAL by the tool rather than caught by a reader.

TWO THINGS ITS OWN ATTACK SUITE FOUND, both encoded rather than described:
  CONSERVATIVE   an effect carried entirely by 30 planted outliers comes back MARGINAL, not
                 CONCENTRATED. The rule under-calls, which is the safe direction for a tool whose
                 false positive would be an unwarranted retraction -- but it means MARGINAL should
                 be read as "possibly concentrated", not as "probably fine".
  NO RESOLUTION  below roughly z 3 the reference itself dies at k<=2, so nothing can score under
                 the threshold and every input would return NOT CONCENTRATED. That verdict is now
                 refused outright rather than issued as a clean bill.

WHAT IT DOES NOT DO. It says nothing about whether the effect is REAL -- a confounded effect can be
beautifully unconcentrated. It answers one question: is this number carried by a handful of units.
That was the question r191 failed, and the reason it failed was invisible until someone deleted one
prompt.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


def jackknife_calibrated(values, groups=None, *, draws=200, seed=0, batches=4, cap=None, name=""):
    """Return the concentration profile of a mean, with its own reference distribution.

    values  the per-unit contributions whose mean is the claim
    groups  optional labels; when given, leave-one-GROUP-out is also reported, because deleting a
            stratum is not deleting a prompt when a prompt contributes several strata
    """
    v = np.asarray(list(values), float)
    n = len(v)
    if n < 30:
        raise ValueError(f"{name or 'jackknife'}: {n} units is too few to characterise "
                         f"concentration; the reference would be noise")
    cap = cap or max(80, n // 10)
    m = float(v.mean())
    sd = float(v.std(ddof=1))
    se = sd / math.sqrt(n)

    def kill_k(x):
        o = np.argsort(x)[::-1] if x.mean() > 0 else np.argsort(x)
        for k in range(1, min(cap, len(x))):
            keep = np.delete(x, o[:k])
            mm = keep.mean()
            ss = keep.std(ddof=1) / math.sqrt(len(keep))
            if (mm - 1.96 * ss <= 0) if m > 0 else (mm + 1.96 * ss >= 0):
                return k
        return None

    observed = kill_k(v)
    # SEVERAL INDEPENDENT BATCHES, so the threshold's own spread is measured rather than assumed.
    ref_all, p10s = [], []
    for b in range(batches):
        rng = np.random.default_rng(seed + 1000 * b)
        batch = [kill_k(rng.normal(loc=m, scale=sd, size=n)) or cap for _ in range(draws)]
        ref_all.extend(batch)
        p10s.append(float(np.percentile(batch, 10)))
    p10, p10_lo, p10_hi = float(np.mean(p10s)), float(min(p10s)), float(max(p10s))
    # NO RESOLUTION IS A VERDICT, and leaving it out was this module's second defect. When the
    # reference itself dies at k=1 or 2 -- which happens for any weak effect, since a clean effect
    # at low z also cannot survive deleting its best points -- nothing can score BELOW the
    # threshold, so "NOT CONCENTRATED" would be returned for every input including a spike. That
    # is a clean bill the instrument cannot support: a check that cannot fail. Found by attacking
    # the tool with a deliberately weak effect, not by using it.
    if p10_hi <= 2:
        verdict = ("NO RESOLUTION -- the reference dies at k<=2, so concentration is undetectable "
                   "at this effect size")
    elif observed is None:
        verdict = "SURVIVES the deletion cap"
    elif observed < p10_lo:
        verdict = "CONCENTRATED"
    elif observed > p10_hi:
        verdict = "NOT CONCENTRATED"
    else:
        verdict = "MARGINAL (inside the threshold's own noise)"

    out = {"n": n, "mean": m, "se": se, "z": m / se if se else float("nan"),
           "kill_at": observed, "reference_mean": float(np.mean(ref_all)), "reference_p10": p10,
           "reference_p10_lo": p10_lo, "reference_p10_hi": p10_hi, "p10_batches": p10s,
           "reference_p90": float(np.percentile(ref_all, 90)),
           "draws": draws, "batches": batches, "verdict": verdict}

    # leave-one-out at the unit level, and at the group level when groups are given
    loo = [float(np.delete(v, i).mean()) for i in range(n)]
    out["max_single_unit_shift"] = float(max(abs(x - m) for x in loo))
    out["max_single_unit_shift_rel"] = out["max_single_unit_shift"] / abs(m) if m else float("nan")
    if groups is not None:
        g = list(groups)
        idx = defaultdict(list)
        for i, k in enumerate(g):
            idx[k].append(i)
        gloo = [float(np.delete(v, ii).mean()) for ii in idx.values()]
        out["n_groups"] = len(idx)
        out["max_single_group_shift"] = float(max(abs(x - m) for x in gloo))
        out["max_single_group_shift_rel"] = (out["max_single_group_shift"] / abs(m)
                                             if m else float("nan"))
    return out


def report(res, name=""):
    print(f"  {name:38s} n={res['n']:6d} mean {res['mean']:+.4f} z {res['z']:+5.1f}  "
          f"kill@{str(res['kill_at']):>4s} ref {res['reference_mean']:5.1f} "
          f"(p10 {res['reference_p10_lo']:.0f}-{res['reference_p10_hi']:.0f} over "
          f"{res['batches']} batches)")
    print(f"  {'':38s} -> {res['verdict']}")
    extra = f"one unit moves it {res['max_single_unit_shift_rel']:.1%}"
    if "max_single_group_shift_rel" in res:
        extra += f"; one group {res['max_single_group_shift_rel']:.1%} " \
                 f"({res['n_groups']} groups)"
    print(f"  {'':38s} {extra}")
