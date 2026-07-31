"""The measurements -- and the two normalisations without which none of them mean anything.

An edit to a criterion moves a judge. Always, whatever the edit was. So a design that only runs
semantic edits will find movement and will report it as meaning. Every effect here is therefore
divided twice:

  by the NULL floor        what a meaning-preserving rewording moves. This is the instrument's own
                           noise and nothing smaller than it has been detected.
  by the DISRUPTION floor  what a content-free edit of comparable size moves. This is the price of
                           editing at all, and a semantic effect no larger than it demonstrates
                           nothing about semantics.

`effect_over_floor` below 1.5 means no count is admissible -- only a direction. That threshold is
not local taste: it is what killed a person-level harm count in this project after four rounds of
work, and it is applied here before any number is reported rather than after.

DIRECTIONAL CORRECTNESS IS A SEPARATE QUESTION FROM MAGNITUDE and is the one that actually decides
preservation. A large movement in the wrong direction is not preservation; it is a system reacting
to an edit it did not understand. A field is preserved only when the predicted sign appears, at a
magnitude clearing both floors.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


def _mean_ci(x: np.ndarray, clusters: np.ndarray | None = None) -> tuple[float, float, float, int]:
    """Mean with a cluster-robust 95% interval. n_eff is the number of CLUSTERS, never rows --
    80k pairs from 968 prompts is n=968, and quoting the row count is how an interval gets
    manufactured."""
    if clusters is None:
        n = len(x)
        m = float(np.mean(x))
        se = float(np.std(x, ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
        return m, m - 1.96 * se, m + 1.96 * se, n
    by: dict = defaultdict(list)
    for v, c in zip(x, clusters):
        by[c].append(v)
    g = np.array([np.mean(v) for v in by.values()])
    n = len(g)
    m = float(np.mean(g))
    se = float(np.std(g, ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    return m, m - 1.96 * se, m + 1.96 * se, n


def responsiveness(base: np.ndarray, mut: np.ndarray,
                   clusters: np.ndarray | None = None) -> dict:
    """How far the executor moved when the source changed. Absolute, unsigned."""
    d = np.abs(mut - base)
    m, lo, hi, n = _mean_ci(d, clusters)
    return {"mean_abs_delta": round(m, 5), "ci95": [round(lo, 5), round(hi, 5)], "n_eff": n}


def directional(base: np.ndarray, mut: np.ndarray, predicted: str,
                clusters: np.ndarray | None = None) -> dict:
    """Share of cases moving the way the operator said they would, BEFORE seeing the data.

    For INVERT the test is stricter than a sign test: a score above the midpoint must cross below
    it, and vice versa. A rule whose satisfaction merely dips is not a rule whose direction flipped.
    """
    delta = mut - base
    if predicted == "invert":
        hit = ((base > 0.5) & (mut < 0.5)) | ((base < 0.5) & (mut > 0.5))
    elif predicted == "decrease":
        hit = delta < 0
    elif predicted == "increase":
        hit = delta > 0
    elif predicted == "no_change":
        hit = np.abs(delta) < 0.05
    else:                                   # scope_gated -- decided by the scope test, not here
        return {"share": None, "note": "scope_gated is evaluated by scope_correctness"}
    m, lo, hi, n = _mean_ci(hit.astype(float), clusters)
    return {"share": round(m, 4), "ci95": [round(lo, 4), round(hi, 4)], "n_eff": n,
            "predicted": predicted}


def floors(null_deltas: np.ndarray, disruption_deltas: np.ndarray) -> dict:
    return {"null_floor": round(float(np.mean(np.abs(null_deltas))), 5),
            "disruption_floor": round(float(np.mean(np.abs(disruption_deltas))), 5)}


def over_floor(effect: float, f: dict) -> dict:
    nf, df = f["null_floor"], f["disruption_floor"]
    return {
        "effect_over_null": round(effect / nf, 3) if nf else None,
        "effect_over_disruption": round(effect / df, 3) if df else None,
        "admissible_as_count": bool(nf and df and effect / max(nf, df) >= 1.5),
    }


def scope_correctness(in_scope_delta: np.ndarray, out_scope_delta: np.ndarray,
                      clusters=None) -> dict:
    """A narrowed rule must leave in-scope behaviour alone and move out-of-scope behaviour toward
    not-applicable. Equal movement on both means the scope clause was read as decoration."""
    a, alo, ahi, na = _mean_ci(np.abs(in_scope_delta), clusters)
    b, blo, bhi, nb = _mean_ci(np.abs(out_scope_delta), clusters)
    return {"in_scope_abs_delta": round(a, 5), "out_scope_abs_delta": round(b, 5),
            "separation": round(b - a, 5), "ci_in": [round(alo, 5), round(ahi, 5)],
            "ci_out": [round(blo, 5), round(bhi, 5)], "n_eff": min(na, nb),
            "preserved": bool(b > a)}


def veto_preservation(scores_by_response: np.ndarray, veto_violated: np.ndarray,
                      other_quality: np.ndarray) -> dict:
    """A veto is preserved only if NO amount of other merit lets a violating response win.

    The test is a search for a counterexample, not a correlation: find any response that violates
    the veto and still outranks a response that does not. One is enough -- that is what
    'not tradeable at any price' means, and a rate would be answering a different question.
    """
    viol = np.where(veto_violated)[0]
    clean = np.where(~veto_violated)[0]
    if len(viol) == 0 or len(clean) == 0:
        return {"testable": False, "reason": "need both violating and non-violating responses"}
    worst_clean = float(np.min(scores_by_response[clean]))
    best_viol = float(np.max(scores_by_response[viol]))
    counterexamples = int(np.sum(scores_by_response[viol][:, None]
                                 > scores_by_response[clean][None, :]))
    return {"testable": True, "best_violating": round(best_viol, 4),
            "worst_clean": round(worst_clean, 4),
            "counterexample_pairs": counterexamples,
            "total_pairs": int(len(viol) * len(clean)),
            "preserved": counterexamples == 0,
            "note": ("one counterexample is enough; a veto that can be outranked has become a "
                     "preference regardless of what the text still says")}


def executor_variance(scores: dict[str, np.ndarray]) -> dict:
    """How much of a verdict is the executor. Reported as the full pairwise matrix, because a
    single mean agreement hides which pair disagrees."""
    names = sorted(scores)
    out = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            x, y = scores[a], scores[b]
            n = min(len(x), len(y))
            r = float(np.corrcoef(x[:n], y[:n])[0, 1]) if n > 2 else float("nan")
            out[f"{a}|{b}"] = {"pearson": round(r, 4),
                               "mean_abs_gap": round(float(np.mean(np.abs(x[:n] - y[:n]))), 4)}
    return out


def confidence_card(effect: float, ci: tuple[float, float], f: dict, n_eff: int,
                    seed_values: list[float], spec_signs: list[int],
                    held_out: list[bool], instrument: str, prior_art: str,
                    n_tests: int) -> dict:
    """P14. A single confidence number is a lie because it becomes a dial; this is a SET, each of
    which can independently veto the conclusion. A missing entry is UNCOMPUTED, never blank."""
    width = ci[1] - ci[0]
    nf = max(f["null_floor"], f["disruption_floor"])
    same = sum(1 for s in spec_signs if s == (1 if effect > 0 else -1))
    return {
        "n_eff": n_eff,
        "MDE": round(2.8 * (width / 3.92), 5) if width else "UNCOMPUTED",
        "effect_over_floor": round(abs(effect) / nf, 3) if nf else "UNCOMPUTED",
        "CI_width_over_effect": round(width / abs(effect), 3) if effect else "UNCOMPUTED",
        "spec_survival": f"{same}/{len(spec_signs)} same sign" if spec_signs else "UNCOMPUTED",
        "seed_spread_over_effect": (round((max(seed_values) - min(seed_values)) / abs(effect), 4)
                                    if seed_values and effect else "UNCOMPUTED"),
        "held_out": (f"{sum(held_out)}/{len(held_out)} confirmed" if held_out else "ABSENT"),
        "instrument": instrument,
        "prior_art": prior_art,
        "multiplicity": f"{n_tests} tests in family; BH applied",
        "reading": ("effect/floor < 1.5 -> direction only, no count"
                    if nf and abs(effect) / nf < 1.5 else "count admissible"),
    }


def bh(pvals: list[float], alpha: float = 0.05) -> list[bool]:
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    out = [False] * n
    kmax = -1
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= alpha * rank / n:
            kmax = rank
    for rank, i in enumerate(order, start=1):
        if rank <= kmax:
            out[i] = True
    return out
