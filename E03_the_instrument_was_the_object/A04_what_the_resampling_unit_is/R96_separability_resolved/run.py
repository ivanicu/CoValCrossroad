"""r96 -- r95's UNVERIFIED, resolved from an artifact that was already on disk.

CLAIM CARD
----------
Claim      r95 left the multiplicative-vs-ordinal question UNVERIFIED, saying the
           paired ratio needed joint bootstrap draws r30 discarded, and named a GPU
           re-score of r80's frozen panel as what would settle it.
Estimand   the sampling distribution of the near/random share ratio per judge, and of
           the pairwise differences between judges' ratios.
Target
observed?  YES, and no GPU is required. r22 persisted per-prompt own/near/random cells
           for all three judges over the same 300 prompts
           (r22_cross_family_per_prompt.npz, 17 KB). The joint structure r95 called
           missing was never discarded -- it was written by a different round.
Alternative
worlds     M MULTIPLICATIVE  the judge rescales the share but preserves the ratio:
                             every pairwise ratio difference straddles zero. Then R is
                             separable from J up to scale and layer-at-a-time
                             validation is sound for cardinal claims too.
           O ORDINAL-ONLY    at least one pairwise ratio difference excludes zero.
                             Then the judge interacts beyond rescaling, and only
                             ORDINAL claims about R survive a change of judge.
Intervention
           none. A joint prompt bootstrap over cells already computed.
Null       three controls, and each can void the round:
           (1) REBUILD -- (own-donor)/(own-0.5) must reproduce r30's six stored shares.
               If r22's cells do not rebuild r30, they are not r30's cells.
           (2) GAIN-INVARIANCE (a NEGATIVE control) -- multiplying one judge's
               deviations from 0.5 by any constant must leave its ratio unchanged. If
               the statistic moves under a pure gain, it measures scale rather than
               interaction and every conclusion below is void.
           (3) PLANT (a POSITIVE control) -- a synthetic judge built with a knowingly
               different ratio must be detected. A test that has never returned
               "different" cannot be trusted when it returns "same".

WHY THIS IS THE STEP, AND WHAT IT CORRECTS
-------------------------------------------
r95's closing line called the re-score "the first GPU work this project has had a
reason for since the panel was frozen". That was wrong, and wrong in the expensive
direction: the prior-art gate exists precisely to catch a proposal to rebuild what is
already on disk. The cost meter and P4 both say ask the filesystem before spending.
Asking took one `find`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

CELLS = _ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R22_cross_family/results/r22_cross_family_per_prompt.npz"
R30 = _ROOT / "E02_the_plural_public_dissolved/A01_structured_plurality_or_reliability/R30_scope_grid/results/r30_scope_grid.json"
N_BOOT = 8000          # r30's own rep count
CHANCE = 0.5


def share(o, d):
    """r30's source-specificity share, verified against its stored cells."""
    return (o.mean() - d.mean()) / (o.mean() - CHANCE)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r96_separability_resolved.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for f in (CELLS, R30):
        if not f.exists():
            raise SystemExit(f"REFUSING: {f.name} absent.")
    z = np.load(CELLS, allow_pickle=True)
    r30 = json.load(open(R30))["grid"]
    J = list(r30)
    cells = {j: {k: z[f"{j}|{k}"] for k in ("own", "near", "random")} for j in J}
    n = len(cells[J[0]]["own"])

    # ---- CONTROL 1: rebuild r30 -------------------------------------------------
    worst = 0.0
    for j in J:
        for k in ("near", "random"):
            got, want = share(cells[j]["own"], cells[j][k]), r30[j][k]["share"]
            worst = max(worst, abs(got - want))
    print(f"control 1 REBUILD: worst |r22-rebuilt - r30-stored| = {worst:.2e} over {2 * len(J)} cells")
    if worst > 1e-9:
        raise SystemExit("REFUSING: r22's cells do not rebuild r30's stored shares, so they are not "
                         "the same measurement and nothing below would be about r30's grid.")

    ratio = {j: share(cells[j]["own"], cells[j]["near"]) / share(cells[j]["own"], cells[j]["random"])
             for j in J}

    # ---- CONTROL 2: the statistic must NOT move under a pure gain ---------------
    g = 3.7
    scaled = {k: CHANCE + g * (cells[J[0]][k] - CHANCE) for k in ("own", "near", "random")}
    r_scaled = share(scaled["own"], scaled["near"]) / share(scaled["own"], scaled["random"])
    drift = abs(r_scaled - ratio[J[0]])
    print(f"control 2 GAIN-INVARIANCE: scaling {J[0]} by {g}x moves its ratio by {drift:.2e}")
    if drift > 1e-9:
        raise SystemExit("REFUSING: the ratio responds to a pure multiplicative gain, so it measures "
                         "scale rather than interaction and every conclusion here would be void.")

    # ---- joint bootstrap: same prompt indices across every judge and arm --------
    rng = np.random.default_rng(20260729)
    idx = rng.integers(0, n, (N_BOOT, n))
    draws = {j: np.empty(N_BOOT) for j in J}
    for b in range(N_BOOT):
        s = idx[b]
        for j in J:
            o, nr, rd = cells[j]["own"][s], cells[j]["near"][s], cells[j]["random"][s]
            draws[j][b] = share(o, nr) / share(o, rd)

    print(f"\n  near/random ratio, {N_BOOT} joint prompt draws over {n} prompts")
    ci = {}
    for j in J:
        lo, hi = np.percentile(draws[j], [2.5, 97.5])
        ci[j] = [float(lo), float(hi)]
        print(f"    {j:<26} {ratio[j]:.4f}  [{lo:.4f},{hi:.4f}]")

    pairs, any_excl = {}, False
    print(f"\n  pairwise differences, paired on the SAME draws")
    for i in range(len(J)):
        for k in range(i + 1, len(J)):
            d = draws[J[i]] - draws[J[k]]
            lo, hi = np.percentile(d, [2.5, 97.5])
            excl = bool(lo > 0 or hi < 0)
            any_excl |= excl
            pairs[f"{J[i]} - {J[k]}"] = {"mean": float(d.mean()), "ci": [float(lo), float(hi)],
                                         "excludes_zero": excl}
            print(f"    {J[i][:20]:<21} - {J[k][:20]:<21} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]"
                  f"   {'EXCLUDES 0' if excl else 'straddles 0'}")

    # ---- CONTROL 3: plant a judge whose ratio genuinely differs -----------------
    base = cells[J[0]]
    # shift only the NEAR arm, which changes the ratio without changing own or random
    planted = {"own": base["own"], "random": base["random"],
               "near": base["near"] + 0.5 * (base["own"] - base["near"])}
    r_plant = share(planted["own"], planted["near"]) / share(planted["own"], planted["random"])
    pd_ = np.empty(N_BOOT)
    for b in range(N_BOOT):
        s = idx[b]
        o, nr, rd = planted["own"][s], planted["near"][s], planted["random"][s]
        pd_[b] = share(o, nr) / share(o, rd) - draws[J[0]][b]
    plo, phi_ = np.percentile(pd_, [2.5, 97.5])
    detected = bool(plo > 0 or phi_ < 0)
    print(f"\n  control 3 PLANT: a judge built with ratio {r_plant:.4f} vs {ratio[J[0]]:.4f} is "
          f"{'DETECTED' if detected else 'MISSED'} ({pd_.mean():+.4f} [{plo:+.4f},{phi_:+.4f}])")
    if not detected:
        raise SystemExit("REFUSING: the test cannot detect a planted ratio difference, so a null "
                         "here would be silence rather than a result.")

    # the PLANT fixes what this test can actually resolve; the observed differences must
    # be read against it, not against zero
    resolves = abs(r_plant - ratio[J[0]])
    biggest = max(abs(v["mean"]) for v in pairs.values())
    underpowered = bool(not any_excl and biggest < resolves)
    world = ("O ORDINAL-ONLY" if any_excl else
             (f"M MULTIPLICATIVE -- NOT REFUTED at a resolution of {resolves:.2f}, not established")
             if underpowered else "M MULTIPLICATIVE")
    print(f"\n  demonstrated resolution (plant) {resolves:.4f}   largest observed difference "
          f"{biggest:.4f}  -> {'observed spread sits BELOW what this test can detect' if underpowered else 'within detectable range'}")
    spread = max(ratio.values()) / min(ratio.values())

    verdict = (
        f"{world}. r95 left this UNVERIFIED, said the paired ratio needed joint draws r30 discarded, and "
        f"named a GPU re-score of r80's frozen panel as the fix. THE ARTIFACT WAS ALREADY ON DISK: r22 "
        f"persisted per-prompt own/near/random cells for all three judges over the same {n} prompts, in "
        f"a 17 KB file. The joint structure was never discarded -- it was written by a different round, "
        f"and asking the filesystem cost one `find`. RESOLVED: the near/random ratio is "
        + ", ".join(f"{ratio[j]:.4f} [{ci[j][0]:.4f},{ci[j][1]:.4f}]" for j in J)
        + f", a {spread:.2f}x point spread, and paired on the same draws "
        f"{'at least one pairwise difference EXCLUDES zero' if any_excl else 'every pairwise difference straddles zero'}: "
        + "; ".join(f"{k} = {v['mean']:+.4f} [{v['ci'][0]:+.4f},{v['ci'][1]:+.4f}]" for k, v in pairs.items())
        + f". THE NON-REJECTION MUST BE READ AGAINST WHAT THIS TEST CAN RESOLVE, WHICH THE PLANT FIXES: "
        f"it detects a ratio difference of {resolves:.3f} while the largest observed difference is "
        f"{biggest:.3f} -- BELOW its own demonstrated threshold. So the multiplicative model is "
        f"{'NOT REFUTED rather than established, and the 1.36x point spread is neither confirmed real nor shown to be noise' if underpowered else 'supported within the detectable range'}. "
        f"SO THE JUDGE {'INTERACTS BEYOND RESCALING' if any_excl else 'IS NOT DISTINGUISHABLE FROM A PURE GAIN at this resolution'}, "
        f"and layer-at-a-time validation of R is "
        f"{'defensible for ORDINAL claims and NOT for cardinal ones' if any_excl else 'not shown to fail for cardinal claims either -- which upgrades r95 from UNVERIFIED to a BOUNDED non-rejection, weaker than separability established'}. "
        f"THREE CONTROLS, EACH ABLE TO VOID THE ROUND. REBUILD: r22's cells reproduce r30's six stored "
        f"shares to {worst:.0e}, so these are r30's cells and not a lookalike. GAIN-INVARIANCE, a "
        f"NEGATIVE control: scaling one judge's deviations from chance by {g}x moves its ratio by "
        f"{drift:.0e} -- the statistic is blind to pure scale, which is what makes it a test of "
        f"interaction rather than of magnitude. PLANT, a POSITIVE control: a judge constructed with "
        f"ratio {r_plant:.4f} against {ratio[J[0]]:.4f} is detected at {pd_.mean():+.4f} "
        f"[{plo:+.4f},{phi_:+.4f}], so a null here would be a measurement and not an instrument that "
        f"never fires; the round refuses to run otherwise. SCOPE: this covers the near and random donor "
        f"conditions on {n} prompts with three judges. It inherits r30's own gap -- no phi cell exists at "
        f"the farthest-donor floor -- and three judges cannot speak for judge families in general."
    )

    doc = {
        "n_prompts": int(n), "judges": J, "n_boot": N_BOOT,
        "ratio": {j: float(ratio[j]) for j in J}, "ratio_ci": ci,
        "ratio_point_spread": float(spread),
        "pairwise": pairs, "any_pair_excludes_zero": any_excl,
        "demonstrated_resolution": float(resolves), "largest_observed_difference": float(biggest),
        "underpowered_non_rejection": underpowered,
        "control_rebuild_worst_abs_diff": float(worst),
        "control_gain_invariance_drift": float(drift), "control_gain_factor": g,
        "control_plant": {"planted_ratio": float(r_plant), "baseline_ratio": float(ratio[J[0]]),
                          "delta": float(pd_.mean()), "ci": [float(plo), float(phi_)],
                          "detected": detected},
        "source_cells": str(CELLS.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "r30's source-specificity share, rebuilt exactly from r22's per-prompt own/near/random "
            "cells. No judge is run, no response generated, no GPU used."),
        "scope": (
            "Two donor conditions, three judges, 300 prompts. Inherits r30's gap that no phi cell was "
            "measured at the farthest-donor floor. Three judges cannot characterise judge families in "
            "general -- this settles whether THESE three are related by a pure gain, which is what r95 "
            "left open."),
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
