"""corebench/report.py — an effect cannot be printed without its interval.

WHY THIS EXISTS, dated 2026-08-03. R290 computed correct intervals, stored them in its artifact,
and printed only the point estimate and a verdict word. I then wrote the prose off the SIGN of the
point estimate and published `the prompt-blind arm beats every prompt-specific one` in
FORMULATION.md. Printing the intervals showed it was true of ONE of three cells: the other two
spanned zero. **The defect was a print statement, and it produced a wrong sentence in a published
file within one round.**

Resolving to be careful does not survive the next round. This module makes the failure mechanical:

    row(...)      REFUSES to format an effect without (lo, hi). There is no argument list that
                  produces a bare number.
    verdict(...)  is COMPUTED from the interval and the MDE, three-valued, and never typed. It
                  distinguishes `resolvably negative` from `fails to clear`, which is exactly the
                  distinction the published sentence lost.

Neither is clever. The point is that the cheap wrong thing is no longer expressible.
"""
from __future__ import annotations

POS, NEG, UNRES, BELOW = "BEATS", "LOSES", "UNRESOLVED", "BELOW RESOLUTION"


def verdict(eff: float, lo: float, hi: float, mde: float | None = None) -> str:
    """Three-valued, computed. `resolvably negative` is NOT the same as `fails to clear`.

    With an MDE: an effect inside its own resolution is BELOW RESOLUTION even when the CI
    excludes zero, because a bootstrap CI and a design's MDE answer different questions.
    """
    if lo <= 0.0 <= hi:
        return UNRES
    if mde is not None and abs(eff) < mde:
        return BELOW
    return POS if lo > 0 else NEG


def row(label: str, eff: float, lo: float, hi: float, mde: float | None = None,
        width: int = 26, extra: str = "") -> str:
    """Format one comparison. There is no way to call this without an interval."""
    if lo is None or hi is None:
        raise ValueError(f"{label}: an effect without an interval is not reportable. "
                         "This is the R290 defect and it is not overridable.")
    if not (lo <= eff <= hi):
        raise ValueError(f"{label}: point estimate {eff:+.4f} lies outside its own interval "
                         f"[{lo:+.4f}, {hi:+.4f}] — one of them is computed wrong.")
    m = f"{mde:>8.4f}" if mde is not None else "     n/a"
    return (f"{label:<{width}}{eff:>+9.4f}  [{lo:+.4f}, {hi:+.4f}]{m}  "
            f"{verdict(eff, lo, hi, mde):<17}{extra}")


def header(what: str = "comparison", width: int = 26) -> str:
    return (f"{what:<{width}}{'effect':>9}  {'95% CI':<22}{'MDE':>8}  {'verdict':<17}")


def summarise(cells: dict) -> str:
    """cells: {label: (eff, lo, hi, mde)} -> a one-line count that cannot overstate.

    Reports the three outcomes separately, because collapsing UNRESOLVED into LOSES is precisely
    how `fails to clear` became `is beaten`.
    """
    v = [verdict(*c) for c in cells.values()]
    return (f"{v.count(POS)} beat · {v.count(NEG)} resolvably lose · "
            f"{v.count(UNRES)} unresolved · {v.count(BELOW)} below resolution   "
            f"(of {len(v)})")


def _selftest() -> None:
    # the R290 cells, verbatim, as the regression case
    R290 = {
        "2B coval_core":   (+0.0151, +0.0076, +0.0228, 0.0107),
        "2B topw_k4":      (+0.0128, +0.0050, +0.0206, 0.0108),
        "2B gen":          (-0.0162, -0.0247, -0.0081, 0.0119),
        "0.8B coval_core": (-0.0072, -0.0157, +0.0003, 0.0110),
        "0.8B topw_k4":    (-0.0109, -0.0201, -0.0020, 0.0110),
        "0.8B gen":        (-0.0031, -0.0112, +0.0040, 0.0110),
    }
    print("  " + header("R290 clause ② (regression case)"))
    for k, c in R290.items():
        print("  " + row(k, *c))
    print("\n  " + summarise(R290))
    # ⚠ THIS ASSERTION FAILED ON FIRST RUN AND THE MODULE WAS RIGHT.
    # I had just published a correction saying `topw_k4 at 0.8B is resolvably NEGATIVE, a genuine
    # sign reversal`. Its CI does exclude zero -- [-0.0201, -0.0020] -- but |eff| = 0.0109 is BELOW
    # its own MDE of 0.0110, and this arc has used |eff| >= MDE as the resolution criterion
    # throughout. So under the arc's own rule there are ZERO resolved reversals at 0.8B, not one.
    # The two criteria genuinely disagree on this cell and G4 says publish the disagreement:
    #   by CI-excludes-zero  -> resolvably negative
    #   by |eff| >= MDE      -> below resolution
    # The headline is unaffected either way: nothing at 0.8B is resolvably POSITIVE, so the
    # admitted set is empty under both. The tool built to stop overstatement caught the correction
    # that was itself an overstatement, on its first execution.
    assert verdict(*R290["0.8B coval_core"]) == UNRES, "the cell my prose called `beaten`"
    assert verdict(*R290["0.8B topw_k4"]) == BELOW, "the cell my CORRECTION called `beaten`"
    assert verdict(*R290["0.8B gen"]) == UNRES
    assert not any(verdict(*c) == POS for k, c in R290.items() if k.startswith("0.8B")), \
        "the headline: nothing at 0.8B is resolvably positive under either criterion"
    # a bare effect must be unformattable
    try:
        row("x", 0.01, None, None); raise SystemExit("FAIL: a bare effect was formatted")
    except ValueError:
        pass
    # an inconsistent interval must be caught
    try:
        row("x", 0.5, 0.0, 0.1); raise SystemExit("FAIL: point outside its interval was formatted")
    except ValueError:
        pass
    # BELOW RESOLUTION must be distinguishable from UNRESOLVED
    assert verdict(0.005, 0.001, 0.009, mde=0.012) == BELOW
    assert verdict(0.005, -0.001, 0.011, mde=0.012) == UNRES
    print("\n  SELFTEST PASS — the three cells my published sentence conflated are now three "
          "different strings,\n  a bare effect raises, and an inconsistent interval raises.")


if __name__ == "__main__":
    _selftest()
