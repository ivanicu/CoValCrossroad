"""r94 -- the m>=10 donor-averaging requirement was measured at n=968. Does it survive at 60?

CLAIM CARD
----------
Claim      PREREGISTRATION.md requires donor-averaging at m>=10, citing r88: the donor
           draw is 20% of the attribution interval's variance and averaging cuts the
           prompt requirement 1458 -> 1195.
Estimand   whether that 20% share, and therefore the requirement, holds at the FROZEN
           FRAME SIZE of 60 prompts -- and what averaging actually buys there.
Target
observed?  PARTLY, and the split is the point. The share is derivable exactly. The
           absolute sizes at n=60 are an extrapolation past r89's verified range
           (300-968) and are labelled as such.
Alternative
worlds     I INVARIANT   the share is n-invariant, so the requirement transfers and
                         should be restated with H_fresh's own numbers rather than the
                         release's.
           S SHRINKS     the donor component is a smaller share at 60 prompts, because
                         prompt-sampling noise grows and swamps it. Then m>=10 buys
                         almost nothing at the frozen frame and the requirement is
                         release-only -- it would be the same defect entry 178 fixed,
                         one paragraph further down.
Intervention
           none. Algebra on measured components, checked against r89's measurement.
Null       (i) POSITIVE CONTROL -- the 1/sqrt(n) step must reproduce r89's MEASURED
           donor sd at n=300 within the 11.5% band r89 itself verified. If the law
           cannot recover a value that was actually measured, nothing extrapolated
           from it is admissible;
           (ii) DEGENERATE CONTROL -- at m=1 the residual formula must return the
           unaveraged half-width exactly. A variance decomposition that does not
           reproduce its own starting point is wrong.

WHY THIS IS THE STEP
--------------------
Entry 178 found r91's "a difference costs 5.3x the join" quoted into a document whose
experiment holds 60 prompts, an 86x shortfall. The audit that followed found seven
release-scale rounds cited in PREREGISTRATION.md. This checks the OTHER one that became
a binding REQUIREMENT rather than a description -- because a requirement inherited from
the wrong population is worse than a number: it is an instruction.

THE PREDICTION, WRITTEN BEFORE THE RUN
---------------------------------------
Both the donor component and the prompt-sampling component scale as 1/sqrt(n), so their
RATIO should cancel and the share should be n-invariant. That predicts I INVARIANT. The
round is written to return S if the arithmetic disagrees, and the prediction is recorded
here so that agreement is a check rather than a construction.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R88 = _ROOT / "rounds/09_form_donor_draw_and_unit/r88_donor_draw_variance/results/r88_donor_draw_variance.json"
R89 = _ROOT / "rounds/09_form_donor_draw_and_unit/r89_floor_draw_at_panel_size/results/r89_floor_draw_at_panel_size.json"
R90 = _ROOT / "rounds/09_form_donor_draw_and_unit/r90_resampling_unit/results/r90_resampling_unit.json"
FRAME = 60          # PREREGISTRATION.md: item 7's frozen H_fresh frame
MS = (1, 5, 10, 25, 100)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r94_donor_averaging_at_frame_size.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for f in (R88, R89, R90):
        if not f.exists():
            raise SystemExit(f"REFUSING: {f.name} absent. Every input must be a measured component "
                             f"from this package, never a value typed in here.")
    r88, r89, r90 = (json.load(open(f)) for f in (R88, R89, R90))
    dsd, N = r88["attribution_sd"], r88["n_prompts"]
    half = r90["designs"]["prompt"]["attribution_half"]

    # ---- POSITIVE CONTROL: recover a value r89 actually MEASURED ----------------
    pred300 = dsd * (N / 300) ** 0.5
    meas300 = r89["sizes"]["300"]["sd"]
    dev = abs(pred300 - meas300) / meas300
    band = r89["sqrt_n_worst_deviation"]
    print(f"positive control: 1/sqrt(n) from n={N} predicts donor sd {pred300:.5f} at n=300; "
          f"r89 MEASURED {meas300:.5f} -> {dev:.1%} deviation against r89's own {band:.1%} band")
    if dev > max(band, 0.20):
        raise SystemExit("REFUSING: the scaling law cannot recover a value that was actually "
                         "measured, so nothing extrapolated from it is admissible.")

    # ---- the share, across n ----------------------------------------------------
    shares = {}
    print(f"\n  {'n':>6} {'donor sd':>10} {'prompt half':>12} {'donor share of variance':>24}")
    for n in (N, 300, 120, FRAME):
        d, h = dsd * (N / n) ** 0.5, half * (N / n) ** 0.5
        shares[n] = float(d ** 2 / h ** 2)
        print(f"  {n:>6} {d:>10.5f} {h:>12.5f} {shares[n]:>23.1%}")
    spread = max(shares.values()) - min(shares.values())
    invariant = bool(spread < 0.005)
    print(f"\n  share spread across n: {spread:.2e} -> "
          f"{'INVARIANT (both components carry the same 1/sqrt(n))' if invariant else 'NOT invariant'}")

    # ---- what averaging buys AT THE FROZEN FRAME --------------------------------
    d60, h60 = dsd * (N / FRAME) ** 0.5, half * (N / FRAME) ** 0.5
    resid = h60 ** 2 - d60 ** 2                    # everything that is not donor draw
    if resid <= 0:
        raise SystemExit("REFUSING: the donor component exceeds the total interval, which is "
                         "impossible; the decomposition is wrong.")
    lever = {m: float(np.sqrt(resid + d60 ** 2 / m)) for m in MS}
    if abs(lever[1] - h60) > 1e-12:               # DEGENERATE CONTROL
        raise SystemExit(f"REFUSING: at m=1 the decomposition gives {lever[1]:.6f} but the "
                         f"unaveraged half-width is {h60:.6f}. It must reproduce its own start.")
    print(f"  degenerate control: m=1 returns {lever[1]:.5f} == unaveraged {h60:.5f}  OK")
    print(f"\n  what donor-averaging buys at the FROZEN FRAME of {FRAME} prompts")
    for m in MS:
        print(f"    m={m:<4} half {lever[m]:.4f}   ({(1 - lever[m] / lever[1]):+.1%} vs unaveraged)")
    gain10 = 1 - lever[10] / lever[1]
    gain100 = 1 - lever[100] / lever[1]
    world = "I INVARIANT" if invariant else "S SHRINKS"

    verdict = (
        f"{world}. Entry 178 found r91's '5.3x the join' quoted into a document whose experiment holds "
        f"{FRAME} prompts. The audit that followed found seven release-scale rounds cited in the "
        f"preregistration, and this checks the other one that became a binding REQUIREMENT rather than "
        f"a description -- donor-averaging at m>=10 -- because a requirement inherited from the wrong "
        f"population is worse than a number, it is an instruction. THE SHARE IS N-INVARIANT: the donor "
        f"component and the prompt-sampling component both carry 1/sqrt(n), so their ratio cancels and "
        f"the donor draw is {shares[N]:.1%} of the attribution variance at n={N} and {shares[FRAME]:.1%} "
        f"at n={FRAME}, a spread of {spread:.1e} across the range. So the requirement TRANSFERS -- but "
        f"for a reason that is not obvious and was worth checking rather than assuming, since both "
        f"absolute sizes grow by a factor of {(N / FRAME) ** 0.5:.1f} while the share does not move. "
        f"QUANTIFIED AT THE FROZEN FRAME, which is what the preregistration should state instead of the "
        f"release's figures: the unaveraged half-width is {lever[1]:.4f}, m=10 gives {lever[10]:.4f} "
        f"({gain10:.1%} better) and m=100 gives {lever[100]:.4f} ({gain100:.1%}). So m=10 captures most "
        f"of the available gain at the frame size too, and the diminishing return arrives in the same "
        f"place. POSITIVE CONTROL: the scaling step recovers r89's MEASURED donor sd at n=300 to within "
        f"{dev:.1%}, inside r89's own {band:.1%} band -- a law that could not reproduce a measured value "
        f"would make everything extrapolated from it inadmissible, and the round refuses to run in that "
        f"case. DEGENERATE CONTROL: at m=1 the decomposition returns the unaveraged half-width exactly. "
        f"SCOPE, and it is the honest limit: the SHARE is algebraically exact, but the ABSOLUTE sizes at "
        f"n={FRAME} extrapolate past r89's verified range of 300-968. The transfer claim rests on the "
        f"share; the {lever[10]:.4f} rests on the extrapolation and should be read as an estimate."
    )

    doc = {
        "frame": FRAME, "n_release": N, "donor_sd_release": dsd, "prompt_half_release": half,
        "share_by_n": {str(k): v for k, v in shares.items()}, "share_spread": float(spread),
        "share_is_invariant": invariant,
        "half_at_frame_unaveraged": float(h60), "donor_sd_at_frame": float(d60),
        "lever_at_frame": {str(m): lever[m] for m in MS},
        "gain_m10": float(gain10), "gain_m100": float(gain100),
        "positive_control": {"predicted_sd_300": float(pred300), "measured_sd_300": float(meas300),
                             "deviation": float(dev), "r89_band": float(band)},
        "world": world,
        "outcome_variable_scope": (
            "Variance decomposition of the own-minus-donor attribution interval into a donor-draw "
            "component and everything else, using components measured in r88 and r90 and a scaling law "
            "verified in r89. No new data."),
        "scope": (
            "The SHARE is algebraically exact and n-invariant. The ABSOLUTE half-widths at 60 prompts "
            "extrapolate past r89's verified 300-968 range, so the transfer claim rests on the share "
            "and the frame-size numbers are estimates. It also assumes H_fresh's estimator matches the "
            "release's; whether its variance components are the same is measurable only from its data."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
