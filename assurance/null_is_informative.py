"""A runtime assertion for negative controls. Installed by R820.

Five degenerate negative controls shipped in one session (R809, R810, R813, R816, R819) and every
one was caught by its output looking wrong, never by a check. A commit-time gate cannot catch them:
each was repaired before anything was written, so the artifact holds the repaired value.

Call this where the null is computed, not where it is reported.

    from assurance.null_is_informative import assert_null_is_informative
    assert_null_is_informative(nulls, observed, name="R821 negative control")

VALIDATED by R820 against ten labelled cases: fires on 4 of 5 known-broken nulls and 0 of 5
known-repaired ones. The fifth broken case (R816, an OVERSHOOT) is NOT caught, and the rule that
would catch it false-positives on a passing control — see R820's D1.
"""
import numpy as np

EPS = 1e-9


def assert_null_is_informative(nulls, observed, name="negative control", eps=EPS):
    """Raise if a null distribution destroyed nothing.

    nulls    : array-like of draws from the null
    observed : the real statistic the null is meant to be compared against
    """
    a = np.asarray(nulls, float)
    if a.size < 2:
        raise AssertionError(f"{name}: a null needs >=2 draws, got {a.size}")
    spread = float(a.max() - a.min())
    if spread <= eps:
        raise AssertionError(
            f"{name}: DEGENERATE NULL. spread {spread:.3e} <= {eps:.0e} over {a.size} draws "
            f"(centre {a.mean():+.6f}, observed {observed:+.6f}). A null with no variation "
            f"destroyed nothing -- the permutation is a no-op on this statistic. "
            f"Check whether the statistic is invariant to it BY CONSTRUCTION.")
    return {"spread": spread, "centre": float(a.mean()), "observed": float(observed),
            "sd": float(a.std())}
