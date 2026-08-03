"""The control band: a positive control needs its CEILING computed before its threshold is set.

WHY THIS EXISTS -- four instances, three of them in five consecutive rounds
    R221  positive control demanded a ranking-fitter select a WINNER-predictor.
          Unreachable: the objective was full-rank agreement, and a one-hot vector fixes one
          position of four while destroying three. Read as "the compiler resists proxies".
    R225a demanded a tie-count ratio fall monotonically with planted rater dispersion.
          Unreachable: tie-count saturates at BOTH ends and returns to 1 at maximum signal.
    R225b same, with sparsity instead of dispersion. Same ceiling, same failure.
    R228  demanded recovery > 0.9 at zero noise, and got 0.7269.
          Unreachable: recovery at zero noise is exactly E[1/|ties|], and ties are the phenomenon
          under study. The threshold demanded the degeneracy not exist.

    In every case the instrument was FINE and the THRESHOLD was impossible. That is not three
    accidents, it is one habit: setting a control's target by intuition about what success looks
    like, without computing what the design can return when the plant is maximal.

THE RULE
    floor    = the statistic with NO plant                  (what chance returns)
    ceiling  = the statistic with a MAXIMAL plant, no noise  (what perfect detection returns)
    A registered threshold t is admissible only if   floor < t < ceiling.
      t >= ceiling  -> the control CANNOT PASS. Its failure says nothing about the world.
      t <= floor    -> the control CANNOT FAIL. Its success says nothing about the world.
    Both are the same defect seen from opposite sides, and realstat §4 already names the second
    ("check that cannot fail", built 4x, caught 4x). This file is the first one.

⚠ THE CEILING IS NOT 1.0 BY DEFAULT. It is 1.0 only when the design admits a unique correct
    answer. Wherever ties, degeneracy or saturation exist -- which is most places worth
    studying -- the ceiling is strictly below 1 and must be COMPUTED, not assumed.
"""
from __future__ import annotations


class ControlBandError(AssertionError):
    pass


def check(name: str, floor: float, ceiling: float, threshold: float, observed: float | None = None):
    """Return a verdict dict; raise if the threshold is outside the band.

    `observed` is optional: pass it and the verdict also reports whether the control fired, which
    is only meaningful once the band itself is admissible."""
    if not (ceiling > floor):
        raise ControlBandError(
            "%s: ceiling %.6f is not above floor %.6f -- the statistic cannot distinguish a "
            "maximal plant from no plant at all, so no threshold on it is admissible"
            % (name, ceiling, floor))
    if threshold >= ceiling:
        raise ControlBandError(
            "%s: threshold %.6f >= ceiling %.6f -- THE CONTROL CANNOT PASS. Its failure would say "
            "nothing about the instrument. Compute the ceiling first: it is what the design "
            "returns under a maximal plant, and it is 1.0 only when the answer is unique."
            % (name, threshold, ceiling))
    if threshold <= floor:
        raise ControlBandError(
            "%s: threshold %.6f <= floor %.6f -- THE CONTROL CANNOT FAIL (realstat §4)."
            % (name, threshold, floor))
    out = {"name": name, "floor": floor, "ceiling": ceiling, "threshold": threshold,
           "band_width": ceiling - floor, "admissible": True}
    if observed is not None:
        out["observed"] = observed
        out["fired"] = bool(observed >= threshold)
        out["headroom_used"] = ((observed - floor) / (ceiling - floor)) if ceiling > floor else None
    return out
