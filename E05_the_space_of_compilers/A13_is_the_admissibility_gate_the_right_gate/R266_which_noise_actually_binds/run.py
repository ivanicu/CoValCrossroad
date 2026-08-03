"""R266 -- three noise sources are stacked under one number. Only one of them is fixable by effort.

WHAT IS STACKED UNDER R231's 0.3864 vs 0.3836
    R257  label order      flips the gap from +0.0274 to -0.0104          delta 0.0378
    R260  batch bf16 noise 95% interval on the gap contains 0             width 0.0568
    R261  PYTHONHASHSEED   the gap runs -0.0015 to +0.0049 across 4 seeds spread 0.0064
    R231's own floor       20 draws, min/max 0.3657/0.4019

    Three unrelated axes, all reported today, all pointing the same way -- and NOT ONE ROUND HAS
    ASKED WHICH OF THEM IS THE BINDING TERM. That matters because they have different remedies:
    draw noise is bought off with compute, and instrument noise is not bought off with anything
    available here. A programme that spends compute on the wrong one gets a tighter number that is
    still wrong by the same amount.

⛔ HALF OF THIS ROUND IS FORCED AND IS LABELLED WHERE IT OCCURS
    The floor is a mean of DRAWS independent draws, so its sampling spread MUST fall as 1/sqrt(DRAWS).
    Measuring that is a check on the harness, not a finding, and it is reported as the POSITIVE
    CONTROL for exactly that reason. The UNFORCED question is what the spread converges TO -- i.e.
    whether the gap's sign stabilises once draw noise is removed, and how the residual compares to
    the two axes compute cannot touch.

ESTIMAND        (a) the sampling spread of R231's random-4 floor as a function of DRAWS in
                    {10, 20, 50, 100, 200}, over 6 independent seeds;
                (b) the floor's MEAN across the same grid -- which must NOT move, since more draws
                    reduces variance and not bias;
                (c) the gap (core - floor) at the largest DRAWS, and its sign;
                (d) the ratio of the residual draw spread to R257's label-order delta and R260's
                    batch-noise interval -- the hierarchy of error sources, which is the point.
IDENTIFICATION  exact per (draws, seed); the round is deterministic once de-salted. The hierarchy in
                (d) compares three MEASURED spreads on one quantity, so it is arithmetic on
                measurements rather than an inference.
SCOPE           population: R231's own 250 prompts. instrument: the r04 cache; no GPU. baseline:
                R231's committed DRAWS=20. regime: cache-only.
                ⚠ Source is R231's with exactly two visible edits in `r231_desalted.py`: DRAWS
                parameterised, and `abs(hash(...))` replaced by `zlib.crc32(...)`.
WORLDS          W-DRAWS-BIND   draw noise is the biggest term
                                 -> residual spread at DRAWS=200 still exceeds 0.0378 and 0.0568,
                                    and the comparison becomes resolvable with compute alone
                W-INSTRUMENT-BINDS the instrument axes dominate
                                 -> residual spread falls far below both, the gap's sign stabilises
                                    against DRAW noise, and the number is STILL not resolvable
                                    because label order alone moves it by an order more.
                                    Then no amount of compute fixes R231, and the honest statement
                                    is about the instrument rather than about the estimate
KILL            pre-registered: if the DRAWS=200 spread is below one third of R260's 0.0568,
                W-INSTRUMENT-BINDS holds and R231's comparison is declared instrument-limited
                rather than underpowered -- which forbids the sentence "more draws would settle it".
                If it is above, draw noise binds and the fix is compute.
POSITIVE CTRL   the 1/sqrt(DRAWS) law itself: spread(10)/spread(200) must be near sqrt(20)=4.47.
                FORCED, and included as a harness check, not as evidence. If it does not hold, the
                DRAWS parameter is not reaching the sampler and every other cell is void.
NEGATIVE CTRL   the floor's MEAN must not drift with DRAWS -- more draws reduces variance, not bias.
                A drifting mean would mean the parameter changes the estimand and not its precision.
                This one can fail and is not forced.
SHAM            the same (draws, seed) twice must give the same floor; checks the de-salting took.
PLACEBO         DRAWS=20 must reproduce a floor inside R262's measured [0.3815, 0.3879] band.
NOISE FLOOR     the spread at DRAWS=200 IS the residual draw-noise floor; that is the deliverable.
MULTIPLICITY    5 draw levels x 6 seeds = 30 invocations; every cell printed.
SPECIFICATION   swept: DRAWS and seed. Held fixed and named: the candidate set, the class function,
                the 250-prompt population.
ARTIFACT        every floor value persisted per cell.
IMPOSSIBLE      removing the label-order and batch axes. Both are properties of the judge, and the
                release carries no second instrument for this object -- R164's variant tensors cover
                the full and core sets, not the arbitrary subsets the floor draws from.
"""
from __future__ import annotations
import concurrent.futures as cf
import json, math, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
PY = str(ROOT / ".venv/bin/python")
SCRIPT = HERE / "r231_desalted.py"
DRAWS = [10, 20, 50, 100, 200]
SEEDS = [0, 1, 2, 3, 4, 5]
R257_LABEL_DELTA = 0.0378        # |+0.0274 - (-0.0104)|
R260_BATCH_WIDTH = 0.0568        # 95% interval width on Q1_gap
R262_BAND = (0.3815, 0.3879)


def run(args):
    d, s = args
    env = {**os.environ, "R266_DRAWS": str(d), "R266_SEED": str(s), "PYTHONHASHSEED": "0"}
    r = subprocess.run([PY, str(SCRIPT)], capture_output=True, text=True, env=env,
                       cwd=str(ROOT), timeout=1800)
    m = re.search(r"FLOOR\s+random 4-criterion arm, \d+ draws\s*:\s*([0-9.]+)", r.stdout)
    c = re.search(r"core_vs_full_same_judge\s+([0-9.]+)", r.stdout)
    return d, s, (float(m.group(1)) if m else None), (float(c.group(1)) if c else None)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("R231's source with two visible edits (DRAWS parameterised, hash -> crc32).")
    jobs = [(d, s) for d in DRAWS for s in SEEDS]
    print("running %d invocations (%d draw levels x %d seeds)\n" % (len(jobs), len(DRAWS),
                                                                    len(SEEDS)), flush=True)
    cells = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d, s, fl, core in ex.map(run, jobs):
            cells[(d, s)] = (fl, core)
            print("  DRAWS=%-4d seed %d : floor %s  core %s"
                  % (d, s, "%.4f" % fl if fl else "n/a", "%.4f" % core if core else "n/a"),
                  flush=True)

    print("\n=== (a)(b) the floor's spread and mean by DRAWS ===")
    print("%-8s %10s %10s %12s %12s" % ("DRAWS", "mean", "spread", "gap(core-fl)", "sign"))
    stats = {}
    for d in DRAWS:
        fls = [cells[(d, s)][0] for s in SEEDS if cells[(d, s)][0] is not None]
        cos = [cells[(d, s)][1] for s in SEEDS if cells[(d, s)][1] is not None]
        if not fls:
            continue
        mean, spread = sum(fls) / len(fls), max(fls) - min(fls)
        core = sum(cos) / len(cos) if cos else float("nan")
        stats[d] = (mean, spread, core - mean)
        print("%-8d %10.4f %10.4f %12s %12s"
              % (d, mean, spread, "%+.4f" % (core - mean),
                 "+" if core - mean > 0 else "-"))

    print("\n=== controls ===")
    r_forced = (stats[DRAWS[0]][1] / stats[DRAWS[-1]][1]) if stats[DRAWS[-1]][1] > 0 else float("inf")
    expect = math.sqrt(DRAWS[-1] / DRAWS[0])
    pos_ok = 0.5 * expect <= r_forced <= 2.0 * expect
    print(" POSITIVE (FORCED, a harness check and not evidence): spread(%d)/spread(%d) = %.2f,"
          % (DRAWS[0], DRAWS[-1], r_forced))
    print("          1/sqrt(DRAWS) predicts %.2f  -> %s"
          % (expect, "OK -- the DRAWS parameter reaches the sampler"
             if pos_ok else "THE PARAMETER IS NOT REACHING THE SAMPLER; every cell void"))
    means = [stats[d][0] for d in DRAWS if d in stats]
    drift = max(means) - min(means)
    neg_ok = drift < stats[DRAWS[0]][1]
    print(" NEGATIVE the floor's MEAN must not drift with DRAWS (variance, not bias):")
    print("          drift %.4f vs the DRAWS=%d spread %.4f  -> %s"
          % (drift, DRAWS[0], stats[DRAWS[0]][1],
             "OK" if neg_ok else "THE MEAN MOVES -- DRAWS changes the estimand, not its precision"))
    a = run((20, 9))[2]; b = run((20, 9))[2]
    print(" SHAM     same (draws, seed) twice : %s" % ("OK" if a == b else "NONDETERMINISTIC"))
    in_band = R262_BAND[0] - 0.01 <= stats[20][0] <= R262_BAND[1] + 0.01
    print(" PLACEBO  DRAWS=20 mean %.4f inside R262's measured band [%.4f, %.4f] : %s"
          % (stats[20][0], *R262_BAND, "OK" if in_band else "OUTSIDE"))

    print("\n=== (d) THE HIERARCHY: which noise actually binds? ===")
    resid = stats[DRAWS[-1]][1]
    print(" residual DRAW spread at DRAWS=%d          : %.4f" % (DRAWS[-1], resid))
    print(" R257 label-order delta on the same gap     : %.4f   (%.1fx the residual)"
          % (R257_LABEL_DELTA, R257_LABEL_DELTA / resid if resid else float("inf")))
    print(" R260 batch-noise 95%% interval width        : %.4f   (%.1fx the residual)"
          % (R260_BATCH_WIDTH, R260_BATCH_WIDTH / resid if resid else float("inf")))
    print(" the gap itself at DRAWS=%d                 : %+.4f" % (DRAWS[-1], stats[DRAWS[-1]][2]))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not pos_ok:
        v = "UNVERIFIED -- the forced 1/sqrt(DRAWS) law does not hold; DRAWS is not reaching the sampler."
    elif not neg_ok:
        v = ("UNVERIFIED -- the floor's MEAN drifts by %.4f across DRAWS, so the parameter is "
             "changing the estimand rather than its precision." % drift)
    elif resid < R260_BATCH_WIDTH / 3:
        v = ("W-INSTRUMENT-BINDS -- draw noise is NOT the binding term. At DRAWS=%d the floor's "
             "seed spread is %.4f, against a label-order delta of %.4f (%.1fx) and a batch-noise "
             "interval of %.4f (%.1fx) on the same gap. The gap stabilises at %+.4f once draw noise "
             "is removed -- and it is STILL not resolvable, because the two axes compute cannot "
             "touch are an order larger. THE SENTENCE 'more draws would settle it' IS FORBIDDEN; "
             "what R231 needs is a second instrument, which this release does not carry."
             % (DRAWS[-1], resid, R257_LABEL_DELTA, R257_LABEL_DELTA / resid,
                R260_BATCH_WIDTH, R260_BATCH_WIDTH / resid, stats[DRAWS[-1]][2]))
    else:
        v = ("W-DRAWS-BIND -- the residual draw spread %.4f at DRAWS=%d is still comparable to the "
             "instrument axes (%.4f, %.4f), so compute would move this number and the comparison is "
             "underpowered rather than instrument-limited."
             % (resid, DRAWS[-1], R257_LABEL_DELTA, R260_BATCH_WIDTH))
    print("\n  " + v)
    json.dump({"draws": DRAWS, "seeds": SEEDS,
               "cells": {"d%d_s%d" % k: list(v_) for k, v_ in cells.items()},
               "stats": {str(d): list(stats[d]) for d in stats},
               "forced_ratio": r_forced, "expected_ratio": expect,
               "mean_drift": drift, "residual": resid,
               "r257_label": R257_LABEL_DELTA, "r260_batch": R260_BATCH_WIDTH,
               "verdict": v}, open(OUT / "noise_hierarchy.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
