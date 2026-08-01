"""A mean that refuses to be computed without naming what it is a mean OF.

WHY THIS EXISTS. On this corpus one prompt carries 929 assessments against a median of 14. An
assessment-weighted mean therefore counts that prompt 929 times, and in r191 that fabricated a
+4.9pp finding which r194 and r195 had to withdraw -- the effect collapsed to +0.4pp on removing
that single prompt. r197 then built a static scanner for the pattern and demonstrated that it
CANNOT SEE the r191 case, because r191 accumulates with `.extend()` and means a flat list.

So the enforcement has to sit at the point of computation, not in a scan afterwards. The rule this
module implements:

    A mean over grouped data is not well defined until someone says whether the unit is the
    OBSERVATION or the GROUP. Both are legitimate. Neither is the default.

`mean_by` requires the estimand as a keyword and returns the value together with the diagnostics
that would have caught r191: how many groups, how many observations, what share the largest group
holds, and BOTH means. When the estimand is "observation" and the two means actually disagree, it
raises -- not because the grouping looks lopsided, but because in that case the answer depends on
a choice the caller has not consciously made.

WHAT IT CANNOT DO, stated here rather than discovered later: a guard nobody calls is not a guard.
Any code path that reaches for np.mean directly bypasses this entirely, and there is no way to
prevent that from inside a library. This is a tool for rounds that opt in, and the honest claim is
that it makes the correct thing easy and the dangerous thing loud -- not that it makes the
dangerous thing impossible.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np

# HOW THIS THRESHOLD CHANGED, because the first version was the same mistake r197 diagnosed.
# v1 fired when one group held more than 5% of the rows. That is a SHAPE test, and its own attack
# suite killed it: four rows in four groups gives a 25% "dominant" group while the two estimands
# are IDENTICAL, so it refused a mean that had nothing wrong with it. A guard that fires where the
# choice does not matter trains its callers to pass acknowledge_dominance everywhere, which is
# worse than no guard.
# v2 tests the OUTCOME: refuse only when the two estimands actually disagree by more than TOL.
# That is exactly the condition under which naming the unit matters, it needs no assumption about
# group sizes, and it makes the error message carry both numbers.
TOL = 0.005          # a chosen constant: half a percentage point on a 0-1 quantity


class EstimandError(ValueError):
    """Raised when a mean is requested in a way that hides which unit it is over."""


def dominance(groups) -> dict:
    """describe the grouping without computing anything from the values"""
    c = Counter(groups)
    n = sum(c.values())
    if not n:
        return {"n": 0, "n_groups": 0, "max_share": 0.0, "largest": None}
    g, k = c.most_common(1)[0]
    return {"n": n, "n_groups": len(c), "max_share": k / n, "largest": g,
            "largest_n": k, "median_group_n": float(np.median(list(c.values())))}


def mean_by(values, groups, *, estimand, acknowledge_dominance=False, name=""):
    """Mean of `values`, with `groups` naming the unit each value belongs to.

    estimand="observation"  every value counts once. Correct when the sentence is about the
                            observations themselves ("a response is flagged 26% of the time it is
                            seen"). REFUSED when it disagrees with the group-weighted mean by more
                            than TOL, unless acknowledge_dominance=True.
    estimand="group"        each group contributes its own mean, once. Correct when the sentence is
                            about the groups ("prompts where the longest is ranked first").

    Returns (value, diagnostics). The diagnostics are not optional decoration -- they are what a
    reader needs to know the number's unit, and returning them forces the caller to have them.
    """
    values = list(values)
    groups = list(groups)
    if len(values) != len(groups):
        raise EstimandError(
            f"{name or 'mean_by'}: {len(values)} values against {len(groups)} groups. A mean whose "
            f"grouping does not line up with its values is not a mean of anything.")
    if not values:
        raise EstimandError(f"{name or 'mean_by'}: empty input. An empty mean is nan, and a nan "
                            f"printed with a percent sign reads as a measurement.")
    if estimand not in ("observation", "group"):
        raise EstimandError(
            f"{name or 'mean_by'}: estimand must be 'observation' or 'group', got {estimand!r}. "
            f"There is no default, because the default is what produced the r191 retraction.")

    d = dominance(groups)
    acc = defaultdict(list)
    for x, g in zip(values, groups):
        acc[g].append(x)
    obs = float(np.mean(values))
    grp = float(np.mean([float(np.mean(x)) for x in acc.values()]))

    if estimand == "observation":
        if abs(obs - grp) > TOL and not acknowledge_dominance:
            raise EstimandError(
                f"{name or 'mean_by'}: observation-weighted mean refused. It gives {obs:.4f} where "
                f"the group-weighted mean gives {grp:.4f}, a gap of {obs - grp:+.4f} -- so which "
                f"unit you meant CHANGES THE ANSWER. Largest group {d['largest']!r} holds "
                f"{d['largest_n']} of {d['n']} rows ({d['max_share']:.1%}) against a median group "
                f"of {d['median_group_n']:.0f}. On this corpus that configuration produced a "
                f"+4.9pp finding that was withdrawn. Pass estimand='group' if the claim is about "
                f"groups, or acknowledge_dominance=True if it really is about observations.")
        v = obs
    else:
        v = grp
    d = dict(d, observation=obs, group=grp, gap=obs - grp)

    d = dict(d, estimand=estimand, value=v,
             acknowledged=bool(acknowledge_dominance and estimand == "observation"))
    return v, d


def both(values, groups, *, name=""):
    """Compute the mean under BOTH estimands and report the gap.

    Cheaper than choosing wrongly. If the two agree the choice did not matter and the round can say
    so; if they disagree the disagreement IS the result, as it was for r191.
    """
    o, _ = mean_by(values, groups, estimand="observation",
                   acknowledge_dominance=True, name=name)
    g, d = mean_by(values, groups, estimand="group", name=name)
    return {"observation": o, "group": g, "gap": o - g,
            "n": d["n"], "n_groups": d["n_groups"], "max_share": d["max_share"],
            "largest": d["largest"]}
