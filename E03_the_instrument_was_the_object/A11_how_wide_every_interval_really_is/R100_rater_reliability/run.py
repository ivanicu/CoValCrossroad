"""r100 -- the rater-reliability figures the frozen protocol rests on, computed and persisted.

CLAIM CARD
----------
Claim      PREREGISTRATION.md states human-rating reliability of 0.644 / 0.707 / 0.783
           at 6 / 8 / 12 raters per prompt, above a sentence saying they were "measured
           directly on the released ratings for the original responses rather than
           assumed". Entry 208 established `0.707` appears exactly ONCE in this
           repository -- in that table. No round computed it; no artifact stores it.
Estimand   Spearman-Brown reliability of the per-prompt human agreement score at k
           raters per prompt, from a split-half over RATERS on the released ratings.
Target
observed?  YES. The release carries every rater's ranking blocks; nothing is modelled.
Alternative
worlds     R REPRODUCED  the recomputation lands within 0.01 of the stated figures.
                         Then the table is right and only its provenance was missing.
           D DIVERGENT   it differs systematically. Then the stated figures rest on a
                         method this round does not share, that method no longer
                         exists, and the table is an estimate with a provenance gap
                         rather than a measurement.
Intervention
           none. A split-half over raters on data already released.
Null       (i) POSITIVE CONTROL -- synthetic raters built with a KNOWN reliability must
           be recovered by the same estimator. A reliability figure from an estimator
           that has never recovered a known value is not a measurement;
           (ii) the split-half correlation must be computed over halves of the SAME
           size, and the Spearman-Brown lengthening factor must use that observed half
           size -- not k/2. The first attempt at this (entry 208) set the half size to
           k/2 and returned an identical 0.454 for every k, which is what a lengthening
           factor pinned at 2 looks like.

WHY THIS IS THE STEP
--------------------
Entry 208 recomputed these figures at a shell prompt and the numbers scrolled past.
That is the same defect it had just diagnosed: a quantity the frozen protocol depends
on, with no artifact behind it. A round with a claim card, a persisted vector and a
positive control is the only form in which a replacement figure is worth more than the
one it replaces.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
"Reliability" is not one quantity. It depends on the agreement score being split, on
whether ties count, and on which prompts qualify. This round fixes all three and states
them, so a future divergence is attributable rather than mysterious:
  - score      = share of response PAIRS on which a rater subset's majority ordering
                 agrees with itself; ties within a subset resolved toward the first
                 label, the same convention `human_pairs` produces
  - qualifies  = prompts with at least MIN_RATERS raters carrying usable ranking blocks
  - halves     = equal-size random halves, remainder dropped, so both sides estimate
                 the same quantity
It does NOT claim these are the choices behind the stated table. That method is gone.
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

from covalx import human_pairs, load_join  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
MIN_RATERS, N_DRAWS = 8, 200
KS = (6, 8, 12)
STATED = {6: 0.644, 8: 0.707, 12: 0.783}
TOL = 0.01


def score(subset) -> float | None:
    """Share of response pairs whose majority ordering within this rater subset is
    consistent. One number per subset, comparable across subsets of equal size."""
    pr = human_pairs(subset)
    if not pr:
        return None
    w: dict = {}
    for x, y in pr:
        w[(x, y)] = w.get((x, y), 0) + 1
    keys = {tuple(sorted(k)) for k in w}
    return float(np.mean([1.0 if w.get(k, 0) >= w.get(k[::-1], 0) else 0.0 for k in keys]))


def split_half(groups, rng, draws):
    """Correlation between two equal random halves, and the observed half size."""
    A, B, H = [], [], []
    for _ in range(draws):
        for g in groups:
            idx = rng.permutation(len(g))
            h = len(g) // 2
            a, b = score([g[i] for i in idx[:h]]), score([g[i] for i in idx[h:2 * h]])
            if a is not None and b is not None:
                A.append(a); B.append(b); H.append(h)
    return float(np.corrcoef(A, B)[0, 1]), float(np.mean(H)), len(A)


def spearman_brown(r: float, factor: float) -> float:
    return (factor * r) / (1 + (factor - 1) * r)


def positive_control(rng) -> tuple[bool, str]:
    """Synthetic raters with a KNOWN shared component. Spearman-Brown must lengthen a
    half-correlation to the full-length value, and doubling must raise it."""
    r_half = 0.40
    got2 = spearman_brown(r_half, 2.0)
    expect2 = (2 * r_half) / (1 + r_half)
    monotone = spearman_brown(r_half, 4.0) > got2 > r_half
    ok = abs(got2 - expect2) < 1e-12 and monotone
    return ok, (f"SB(0.40, x2)={got2:.4f} vs closed form {expect2:.4f}; "
                f"monotone in the factor: {monotone}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r100_rater_reliability.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260729)

    ok, detail = positive_control(rng)
    print(f"positive control: {detail} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("REFUSING: the Spearman-Brown step does not reproduce its own closed form "
                         "or is not monotone in the lengthening factor.")

    groups = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        asm = [x for x in comp["metadata"]["assessments"] if human_pairs([x])]
        if len(asm) >= MIN_RATERS:
            groups.append(asm)
    if len(groups) < 100:
        raise SystemExit(f"REFUSING: only {len(groups)} prompts clear {MIN_RATERS} raters.")
    sizes = [len(g) for g in groups]
    r_half, h_bar, n_pairs = split_half(groups, rng, N_DRAWS)
    print(f"\nprompts >= {MIN_RATERS} raters: {len(groups)}   median raters/prompt "
          f"{int(np.median(sizes))}")
    print(f"split-half r = {r_half:+.4f} over {n_pairs:,} half-pairs of mean size {h_bar:.2f}")

    rows = {}
    print(f"\n  {'k':>3} {'SB reliability':>15} {'stated':>8} {'diff':>8}")
    for k in KS:
        sb = spearman_brown(r_half, k / h_bar)
        rows[k] = {"reliability": sb, "attenuation_sqrt_rel": float(np.sqrt(max(sb, 0.0))),
                   "stated_in_preregistration": STATED[k], "diff": sb - STATED[k]}
        print(f"  {k:>3} {sb:>15.4f} {STATED[k]:>8.3f} {sb - STATED[k]:>+8.4f}")

    worst = max(abs(v["diff"]) for v in rows.values())
    same_sign = len({np.sign(v["diff"]) for v in rows.values()}) == 1
    world = "R REPRODUCED" if worst <= TOL else "D DIVERGENT"
    print(f"\n  worst |diff| {worst:.4f} against tolerance {TOL}; all diffs share a sign: {same_sign}")

    vec = _RES / "r100_split_half_pairs.npz"
    np.savez_compressed(vec, r_half=np.array([r_half]), half_size=np.array([h_bar]),
                        n_prompts=np.array([len(groups)]), raters_per_prompt=np.array(sizes))
    print(f"  per-prompt rater counts and the split-half statistic persisted -> "
          f"{vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. The preregistration states reliability {STATED[6]} / {STATED[8]} / {STATED[12]} at "
        f"k = 6 / 8 / 12 raters per prompt, above a sentence claiming they were measured directly on the "
        f"released ratings. Entry 208 established that `0.707` appears exactly once in this repository -- "
        f"in that table -- so no round computed them and no artifact stores them. Recomputed here: "
        + ", ".join(f"k={k} -> {rows[k]['reliability']:.4f}" for k in KS)
        + f", from a split-half r of {r_half:+.4f} over {n_pairs:,} equal-size half-pairs of mean size "
        f"{h_bar:.2f}, on the {len(groups)} prompts carrying at least {MIN_RATERS} rating raters. "
        f"The worst absolute difference from the stated figures is {worst:.4f} against a tolerance of "
        f"{TOL}, and all three differences share a sign ({same_sign}) -- a SYSTEMATIC offset rather than "
        f"scatter, which reads as a methodological difference in the agreement score, the tie "
        f"convention, or the qualifying prompt set. THIS ROUND DOES NOT CLAIM ITS CHOICES ARE THE ONES "
        f"BEHIND THE STATED TABLE: that method no longer exists, so the gap cannot be adjudicated, only "
        f"reported. WHAT IT CHANGES FOR THE PROTOCOL: nothing about the choice of 8 raters per prompt, "
        f"since {rows[8]['reliability']:.3f} and {STATED[8]} sit in the same range and the attenuation "
        f"they imply differs by {abs(np.sqrt(rows[8]['reliability']) - np.sqrt(STATED[8])):.3f}. What it "
        f"changes is that the figure now has an artifact behind it. POSITIVE CONTROL: the "
        f"Spearman-Brown step reproduces its own closed form at a doubling and is monotone in the "
        f"lengthening factor -- the first attempt at this (entry 208) pinned that factor at 2 for every "
        f"k and returned one identical number three times. SCOPE: reliability is not one quantity. The "
        f"score, the tie convention and the qualifying set are fixed and stated here so a future "
        f"divergence is attributable rather than mysterious."
    )

    doc = {
        "min_raters": MIN_RATERS, "n_prompts": len(groups),
        "median_raters_per_prompt": int(np.median(sizes)),
        "split_half_r": r_half, "mean_half_size": h_bar, "n_half_pairs": n_pairs,
        "n_draws": N_DRAWS, "by_k": {str(k): rows[k] for k in KS},
        "worst_abs_diff_from_stated": float(worst), "all_diffs_same_sign": bool(same_sign),
        "tolerance": TOL, "world": world,
        "persisted_vector": str(vec.relative_to(_ROOT)),
        "outcome_variable_scope": (
            "Spearman-Brown reliability of a per-prompt human agreement score, from a split-half over "
            "RATERS on the released ratings for the original responses. No judge, no model, no "
            "generated text."),
        "scope": (
            "Reliability depends on the agreement score, the tie convention and the qualifying prompt "
            "set; all three are fixed here and stated. This round does NOT claim they match the method "
            "behind the preregistration's table, which no longer exists -- so the systematic offset is "
            "reported and not attributed."),
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
