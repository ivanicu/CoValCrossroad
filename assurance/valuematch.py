#!/usr/bin/env python3
"""The one place the value-membership test lives. Import it; do not re-implement it.

⭐ WHY THIS EXISTS (R1076, after R1075). R1047 found that a statement prints a ROUNDED display value
   while an artifact stores the FULL one, so an exact float comparison finds nothing. It wrote a
   rounding-aware test — inside its own round script. R1070 wrote a fresh EXACT one, and five rounds
   built on the empty population that produced. **A fix inside one round's script does not
   propagate.**

⛔ THE RULE: when one side of a comparison is a value READ FROM PROSE, match at that value's OWN
   displayed precision. Exact matching is correct only when both sides come from the same
   computation.
"""
from __future__ import annotations


def displayed_precision(token: str) -> int:
    """decimal places the statement actually shows — the precision the claim is made at"""
    return len(token.split(".")[1]) if "." in token else 0


def matches(token: str, value: float) -> bool:
    """does `value` (stored, full precision) match `token` (as written in prose)?"""
    dp = displayed_precision(token)
    return round(float(value), dp) == round(float(token), dp)


def in_pool(token: str, pool) -> bool:
    """is a value matching `token` present in `pool`? Use this, not `float(token) in pool`."""
    return any(matches(token, v) for v in pool)


def find_all(token: str, pool):
    """every stored value that the prose token could be a rounded rendering of"""
    return sorted(v for v in pool if matches(token, v))
