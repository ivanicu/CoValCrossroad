"""The within-person resampling floor, derived once, because I got its scaling wrong three times.

An adversary re-deriving the floor rather than reusing it found that mine was too large by exactly
sqrt(2), which made every effect-over-floor ratio in the phase too small by the same factor. One of
those ratios decided a verdict.

THE DERIVATION, written out so the next use does not repeat the guess.

Let a person contribute n observations with per-observation variance s^2.

    full-sample mean        variance  s^2 / n
    half-sample mean        variance  2 s^2 / n          (half the observations, twice the variance)
    D = halfA - halfB       variance  4 s^2 / n          (two independent halves)

    SD(D) = 2s / sqrt(n) = 2 x SD(full-sample mean)

So the floor for a statistic computed on the FULL data is SD(D) / 2. Dividing by sqrt(2) -- which is
what I did -- treats the half-sample's own noise level as if it were the full sample's, comparing a
full-data spread against a half-data floor. It inflates the floor and deflates the ratio.

And SD(D) is not the mean absolute difference. For a mean-zero normal, E|D| = SD(D) sqrt(2/pi), so

    SD(D) = E|D| sqrt(pi/2)          and          floor = E|D| sqrt(pi/2) / 2 = E|D| sqrt(pi/8)

    correct   E|D| x 0.62666
    what I used   E|D| x 0.88623      = correct x sqrt(2)

WHAT THE CORRECTION DOES TO THE THREE PLACES IT WAS USED. Every ratio rises by sqrt(2):

    r142  own-vs-panel rating gap        0.187 -> 0.264   still far below 1.5, conclusion unchanged
    r145  unserved rate, between-person  1.06  -> 1.50    ON the line, was "clearly below"
    r151  full-rejection rate            1.72  -> 2.43    was above, now comfortably so

Only r145 changes what may be said, and it changes it in the direction that costs me a clean
verdict: the individual-level question is undecided rather than settled as rotating.

THE 1.5 THRESHOLD ITSELF IS A CHOICE AND IS NOT DERIVED HERE. It is the project's standing rule
that an effect below 1.5x its own resampling floor licenses a direction and not a count. Sitting at
1.50 is therefore the worst possible place to land, and the honest reading of a boundary value is
that the design cannot decide -- not that it passed.
"""
from __future__ import annotations

import math

import numpy as np

MAD_TO_SD = math.sqrt(math.pi / 2)     # E|D| -> SD(D) for a mean-zero normal
HALF_TO_FULL = 0.5                     # SD(D) -> SD of the full-sample statistic
SCALE = MAD_TO_SD * HALF_TO_FULL       # ~0.62666
LEGACY_SCALE = math.sqrt(math.pi / 4)  # ~0.88623, what this phase used before the correction
ADMISSIBLE = 1.5                       # standing project rule: below this, direction only


def split_half_floor(per_unit: dict, seeds, min_n: int = 4,
                     legacy: bool = False) -> float:
    """Resampling floor for a between-unit spread, from within-unit splits.

    `per_unit` maps a unit (a person) to its list of observations. Units with fewer than `min_n`
    observations are excluded rather than split, because a two-observation split is one point
    against one point and contributes noise about noise.
    """
    scale = LEGACY_SCALE if legacy else SCALE
    out = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        d = []
        for v in per_unit.values():
            x = np.asarray(v, float)
            if x.size < min_n:
                continue
            i = rng.permutation(x.size)
            h = x.size // 2
            d.append(abs(float(x[i[:h]].mean()) - float(x[i[h:]].mean())))
        if d:
            out.append(float(np.mean(d)) * scale)
    return float(np.mean(out)) if out else float("nan")


def read(effect: float, floor: float) -> dict:
    """The reading rule, applied rather than described."""
    ratio = abs(effect) / floor if floor else float("nan")
    if not math.isfinite(ratio):
        verdict = "UNCOMPUTED"
    elif ratio >= ADMISSIBLE * 1.2:
        verdict = "count admissible"
    elif ratio >= ADMISSIBLE:
        verdict = ("ON THE LINE -- a boundary value means the design cannot decide, which is not "
                   "the same as passing")
    else:
        verdict = "direction only, no count"
    return {"effect": effect, "floor": floor, "ratio": round(ratio, 3), "verdict": verdict}
