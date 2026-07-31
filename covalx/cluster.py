"""Two-way cluster-robust standard errors, derived once, because every CI in the phase assumed iid.

Every interval in r155 through r162 was `mean +- 1.96 sd/sqrt(n)` over (prompt, rater) rows. Those
rows are not independent in two directions at once:

    the same PROMPT contributes ~16 rows, all scoring the same four responses with the same rubric
    the same RATER contributes ~15 rows, carrying their own ranking style across prompts

An adversary recomputing with two-way clustering found the iid SE too small by factors of 2.3 to
2.8. That does not touch the point estimates -- they were reproduced to four decimals -- but it moves
z from 12.75 to 4.50 on one headline and from 10.25 to 3.30 on another, and it flips one claim from
supported to not-distinguishable-from-flat.

THE ESTIMATOR. Cameron-Gelbach-Miller two-way:

    V = V_prompt + V_rater - V_both

where each term is the usual cluster-robust variance of the mean, and the intersection is subtracted
because rows sharing BOTH a prompt and a rater are counted in the first two terms twice. For a simple
mean this reduces to combining the between-cluster variances of the cluster means, weighted by size.

WHEN IT MATTERS AND WHEN IT DOES NOT. Ties in the human rankings -- 13.9% of the six pairs per row --
are arm-independent, so they cancel exactly in any within-row paired contrast and cannot bias a
delta. What they do bias is any statement about a LEVEL: with that tie rate the achievable range of
concordance is [0.070, 0.930], not [0,1], because tied pairs contribute a fixed half credit whatever
the rubric says. A level quoted against an implicit [0,1] scale overstates how good it is.

SEEDS ARE NOT DATA. Pooling five seeds of a random split multiplies rows by five while the underlying
(prompt, rater) pairs recur 2.64 times on average. Collapsing to unique pairs before clustering is
not optional; stacking the two inflations compounds them.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


def _cluster_var(x: np.ndarray, g: np.ndarray) -> float:
    """Cluster-robust variance of the sample mean, clustering on g."""
    by: dict = defaultdict(list)
    for v, k in zip(x, g):
        by[k].append(v)
    n = x.size
    mu = float(x.mean())
    # sum over clusters of (sum of within-cluster deviations)^2, scaled to a variance of the mean
    s = sum((sum(v - mu for v in vals)) ** 2 for vals in by.values())
    G = len(by)
    if G < 2 or n == 0:
        return float("nan")
    return s / (n ** 2) * (G / (G - 1))


def two_way_se(x, prompt, rater) -> dict:
    """SE of a mean under two-way clustering, beside the iid SE it replaces."""
    x = np.asarray(x, float)
    p = np.asarray(prompt)
    r = np.asarray(rater)
    ok = np.isfinite(x)
    x, p, r = x[ok], p[ok], r[ok]
    if x.size < 3:
        return {"mean": float("nan"), "se_iid": float("nan"), "se_2way": float("nan")}
    both = np.array([f"{a}\x01{b}" for a, b in zip(p, r)])
    v = _cluster_var(x, p) + _cluster_var(x, r) - _cluster_var(x, both)
    se2 = math.sqrt(v) if v and v > 0 else float("nan")
    se_iid = float(x.std(ddof=1) / math.sqrt(x.size))
    m = float(x.mean())
    return {"mean": round(m, 5), "se_iid": round(se_iid, 5), "se_2way": round(se2, 5),
            "inflation": round(se2 / se_iid, 2) if se_iid and math.isfinite(se2) else None,
            "ci95_2way": [round(m - 1.96 * se2, 5), round(m + 1.96 * se2, 5)]
            if math.isfinite(se2) else None,
            "z_2way": round(m / se2, 2) if se2 and math.isfinite(se2) else None,
            "n": int(x.size), "n_prompts": int(len(set(p.tolist()))),
            "n_raters": int(len(set(r.tolist())))}


def collapse_seeds(rows: list[dict], key=("prompt", "rater"), value="v") -> list[dict]:
    """Average repeated measurements of the same unit before any inference.

    Five seeds of a random split are five looks at the same pair, not five pairs. Pooling them
    multiplies n without adding information, and the inflation compounds with unclustered SEs.
    """
    by: dict = defaultdict(list)
    for r in rows:
        by[tuple(r[k] for k in key)].append(r[value])
    return [{**dict(zip(key, k)), value: float(np.mean(v))} for k, v in by.items()]


def tie_rate(prefs) -> dict:
    """What share of the six response-pairs carry no information, and what range that leaves."""
    tied = tot = 0
    for pref in prefs:
        for i in range(4):
            for j in range(i + 1, 4):
                if np.isnan(pref[i]) or np.isnan(pref[j]):
                    continue
                tot += 1
                tied += (pref[i] == pref[j])
    f = tied / tot if tot else float("nan")
    return {"tied_pairs": int(tied), "total_pairs": int(tot), "tie_rate": round(f, 4),
            "achievable_min": round(0.5 * f, 4), "achievable_max": round(1 - 0.5 * f, 4),
            "note": "tied pairs contribute a fixed half credit whatever the rubric says, so a "
                    "concordance level quoted against an implicit [0,1] scale overstates it; "
                    "ties are arm-independent and cancel in any paired contrast"}
