"""Aggregation rules and the signed top-k core, shared by synthetic and real studies.

Four defensible principles, matching the CoVal design space so results transfer:

    utility       largest absolute mean signed preference
    majority      direction supported by the greatest share of raters
    consensus     direction with the strongest lower-quartile support
    constituency  intense supporting constituency, weak minority penalty

A `core` is a frozenset of (item_index, direction) pairs.  Distance is signed
Jaccard: opposite directions on the same item do NOT count as a match, so a
rule that keeps an item but flips its sign is correctly scored as a change.
"""
from __future__ import annotations

import numpy as np

RULES = ("utility", "majority", "consensus", "constituency")
BASELINE_RULES = ("utility", "majority", "consensus")


def rule_score(values: np.ndarray, rule: str) -> tuple[float, int]:
    """Score one item's rating vector under `rule`. Returns (score, direction)."""
    v = values[~np.isnan(values)]
    if v.size == 0:
        return 0.0, 1
    if rule == "utility":
        m = float(v.mean())
        return abs(m), (1 if m >= 0 else -1)
    if rule == "majority":
        pos = float((v > 0).mean())
        neg = float((v < 0).mean())
        if pos >= neg:
            return pos, 1
        return neg, -1
    if rule == "consensus":
        lo = float(np.percentile(v, 25))
        hi = float(np.percentile(v, 75))
        if abs(lo) >= abs(hi) and lo > 0:
            return lo, 1
        if hi < 0:
            return abs(hi), -1
        # penalise strong opposition on the far side
        pos = max(lo, 0.0)
        neg = max(-hi, 0.0)
        return (pos, 1) if pos >= neg else (neg, -1)
    if rule == "constituency":
        # intensity of the strongest supporting bloc, mildly discounted for size
        pos = v[v > 0]
        neg = v[v < 0]
        ps = float(pos.mean() * (pos.size / v.size) ** 0.25) if pos.size else 0.0
        ns = float(-neg.mean() * (neg.size / v.size) ** 0.25) if neg.size else 0.0
        return (ps, 1) if ps >= ns else (ns, -1)
    raise ValueError(f"unknown rule {rule!r}")


def make_core(
    matrix: np.ndarray, rule: str, k: int, rows: np.ndarray | None = None
) -> frozenset[tuple[int, int]]:
    """Signed top-k core. `matrix` is raters x items; `rows` selects a resample."""
    work = matrix if rows is None else matrix[rows, :]
    scored = []
    for j in range(work.shape[1]):
        s, d = rule_score(work[:, j], rule)
        scored.append((s, j, d))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return frozenset((j, d) for _, j, d in scored[:k])


def signed_jaccard(a: frozenset, b: frozenset) -> float:
    u = a | b
    if not u:
        return 0.0
    return 1.0 - len(a & b) / len(u)
