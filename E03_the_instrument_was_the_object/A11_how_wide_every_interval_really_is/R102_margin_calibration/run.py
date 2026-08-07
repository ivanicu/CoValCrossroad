"""r102 -- is the rebuilt satisfaction layer's CONFIDENCE calibrated, or only its sign?

CLAIM CARD
----------
Claim      the package reports agreement with human rankings as a single number, 0.686.
           Every claim built on it treats the estimator as one coin with one bias.
Estimand   agreement conditioned on the DECISION MARGIN |sa - sb|, the weighted-score
           gap the estimator itself produces for each comparison.
Target
observed?  YES. The margin is computed by the same expression `agree()` thresholds at
           zero; nothing new is measured and no value is modelled. What changes is that
           a quantity already produced and immediately discarded is kept.
Alternative
worlds     C CALIBRATED   agreement rises with the margin. Then the score's MAGNITUDE
                          carries information, not just its sign -- a strictly stronger
                          property than the ordinal results, and one that says the low
                          end of the headline is near-chance rather than uniformly 69%.
           F FLAT         agreement is constant across margins. Then the estimator is
                          confidently wrong as often as confidently right, its
                          magnitude is decoration, and 0.686 is the only summary it
                          admits.
           I INVERTED     agreement falls with the margin. That would be a defect: the
                          estimator would be most wrong exactly where it is most sure.
Intervention
           none. Bin the existing comparisons by margin decile.
Null       SHUFFLE CONTROL -- permute correctness against margin. The monotone gradient
           must collapse to noise. A gradient that survives its own shuffle is an
           artifact of the binning, not a property of the estimator, and this round
           refuses to report calibration without it.

WHY THIS IS THE STEP
--------------------
Entry 213 closed the numerical worry (no comparison is decided by float dust; the
smallest margin is 6.9e-4) and named its own residual: a large margin says the estimator
is not GUESSING, and says nothing about whether it is RIGHT. That residual is answerable
from the same data, and it is the difference between "0.686 of the time it agrees" and
"it knows when it agrees".

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Margin is not independent of the comparison's difficulty. Two responses that differ
wildly produce both a large margin AND an easy human judgement, so a gradient could
reflect item easiness rather than estimator calibration. This round CANNOT separate
those: it establishes that the margin predicts correctness, not that the estimator
"knows" anything. That distinction is in the verdict, not softened.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "E03_the_instrument_was_the_object/A10_what_the_resampling_unit_is/R85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import weights  # noqa: E402

SAT = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
N_BINS, N_SHUFFLE = 10, 400


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r102_margin_calibration.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    M, C, P = [], [], []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pr = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if not (pr and items and pid in sat):
            continue
        w, satp = weights(items), sat[pid]
        for a_, b_ in pr:
            sa = sb = 0.0
            for ci in range(len(items)):
                if w[ci] == 0.0:
                    continue
                va, vb = satp.get((ci, a_)), satp.get((ci, b_))
                if va is None or vb is None:
                    continue
                sa += w[ci] * va
                sb += w[ci] * vb
            M.append(abs(sa - sb)); C.append(float(sa > sb)); P.append(pid)
    M, C = np.array(M), np.array(C)
    print(f"comparisons {len(M):,}   overall agreement {C.mean():.4f}")

    q = np.quantile(M, np.linspace(0, 1, N_BINS + 1))
    bins = []
    print(f"\n{'decile':>7} {'margin range':>22} {'n':>8} {'agreement':>10}")
    for i in range(N_BINS):
        lo, hi = q[i], q[i + 1]
        m = (M >= lo) & (M <= hi if i == N_BINS - 1 else M < hi)
        bins.append({"decile": i + 1, "lo": float(lo), "hi": float(hi),
                     "n": int(m.sum()), "agreement": float(C[m].mean())})
        print(f"{i + 1:>7} {f'[{lo:.2f}, {hi:.2f})':>22} {m.sum():>8,} {C[m].mean():>10.4f}")

    acc = [b["agreement"] for b in bins]
    rise = acc[-1] - acc[0]
    mono = sum(acc[i + 1] >= acc[i] for i in range(N_BINS - 1))
    r_pb = float(np.corrcoef(M, C)[0, 1])
    print(f"\n  decile 1 {acc[0]:.4f} -> decile {N_BINS} {acc[-1]:.4f}   rise {rise:+.4f}")
    print(f"  non-decreasing steps {mono}/{N_BINS - 1}   corr(margin, correct) {r_pb:+.4f}")

    # ---- SHUFFLE CONTROL --------------------------------------------------------
    rng = np.random.default_rng(20260729)
    null_rise, null_mono = [], []
    for _ in range(N_SHUFFLE):
        cs = rng.permutation(C)
        na = []
        for i in range(N_BINS):
            lo, hi = q[i], q[i + 1]
            m = (M >= lo) & (M <= hi if i == N_BINS - 1 else M < hi)
            na.append(cs[m].mean())
        null_rise.append(na[-1] - na[0])
        null_mono.append(sum(na[i + 1] >= na[i] for i in range(N_BINS - 1)))
    nr = np.array(null_rise)
    lo95, hi95 = float(np.percentile(nr, 2.5)), float(np.percentile(nr, 97.5))
    beats = bool(rise > hi95)
    print(f"\n  SHUFFLE CONTROL ({N_SHUFFLE} permutations): rise null [{lo95:+.4f},{hi95:+.4f}], "
          f"max monotone steps {max(null_mono)}/{N_BINS - 1}")
    print(f"  observed rise {rise:+.4f} -> {'OUTSIDE' if beats else 'inside'} the null")
    if not beats:
        raise SystemExit("REFUSING: the gradient does not exceed its own shuffle, so it is an artifact "
                         "of the binning rather than a property of the estimator.")

    world = ("C CALIBRATED" if rise > 0 and mono >= N_BINS - 2 else
             "I INVERTED" if rise < 0 else "F FLAT")
    vec = _RES / "r102_margin_correct.npz"
    np.savez_compressed(vec, margin=M, correct=C)
    print(f"  margins and outcomes persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. The package reports agreement with human rankings as one number, {C.mean():.4f}, and "
        f"every claim built on it treats the estimator as a single coin. Conditioned on the DECISION "
        f"MARGIN the estimator itself produces -- the weighted-score gap `agree()` thresholds at zero "
        f"and then discards -- it is not one coin. Across margin deciles agreement runs {acc[0]:.4f} to "
        f"{acc[-1]:.4f}, a rise of {rise:+.4f}, with {mono} of {N_BINS - 1} steps non-decreasing and a "
        f"point-biserial correlation of {r_pb:+.4f}. THE BOTTOM DECILE SITS AT {acc[0]:.4f}, near "
        f"chance; THE TOP AT {acc[-1]:.4f}. So the score's MAGNITUDE carries information and not only "
        f"its sign, which is strictly stronger than the ordinal results this package already has. "
        f"SHUFFLE CONTROL: permuting correctness against margin {N_SHUFFLE} times puts the rise in "
        f"[{lo95:+.4f},{hi95:+.4f}] and never produces more than {max(null_mono)} of "
        f"{N_BINS - 1} monotone steps; the observed rise is OUTSIDE that null, and the round refuses to "
        f"report calibration otherwise. THE CONFOUND, WRITTEN BEFORE THE RUN AND NOT SOFTENED: margin is "
        f"not independent of item difficulty. Two responses that differ wildly produce both a large "
        f"margin and an easy human judgement, so this gradient may reflect EASINESS rather than the "
        f"estimator knowing anything. What is established is that the margin PREDICTS correctness -- "
        f"usable as a confidence signal regardless of which mechanism produces it -- not that the "
        f"estimator is self-aware. Separating those needs an item-difficulty measure independent of the "
        f"estimator, which this release does not carry."
    )

    doc = {
        "n_comparisons": int(len(M)), "overall_agreement": float(C.mean()),
        "n_bins": N_BINS, "bins": bins,
        "decile_1": acc[0], "decile_last": acc[-1], "rise": float(rise),
        "monotone_steps": int(mono), "point_biserial_r": r_pb,
        "shuffle": {"n": N_SHUFFLE, "rise_ci95": [lo95, hi95],
                    "max_monotone_steps": int(max(null_mono)), "observed_outside": beats},
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "Agreement with REAL HUMAN pairwise rankings, conditioned on the estimator's own weighted "
            "score gap. Satisfaction from r04's tensor; no new measurement."),
        "scope": (
            "Establishes that the margin PREDICTS correctness. Does NOT separate estimator calibration "
            "from item difficulty -- a large margin and an easy human judgement have a common cause, "
            "and no difficulty measure independent of the estimator exists in this release."),
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
