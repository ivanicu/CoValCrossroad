"""r24 -- The receipt for "step R^2=0.964 vs trend 0.448", and the control it lacked.

Raised by two independent reviews, 2026-07-28.  README.md carried
"effort steps -38.6% at task 6 (step R^2=0.964 vs trend 0.448)" as a headline.
No script in this repository computed it.  `git log --all -S"0.964"` finds the
number only in prose -- the README and the adversary brief -- never in code.
A reviewer rebuilt it from r02's stored `position_drift` array and matched all
three figures to three significant figures, so the arithmetic was never wrong.
It simply had no executable source, in a repository whose own README asserts
that every CPU round reproduces without further setup.

That is the smaller half of the problem.  The larger half:

  A two-segment step model with a breakpoint chosen AFTER looking at the data
  is not a two-parameter model.  The breakpoint is a fitted parameter, and a
  free-breakpoint step function will beat a straight line on almost any series,
  including pure noise.  Comparing 0.964 against 0.448 as though both models
  cost the same is exactly the failure this project keeps finding in its own
  work: a number reported without the scope over which it holds.

So this round does not merely transcribe the missing computation.  It adds the
control that makes the comparison legitimate:

  * scan EVERY admissible breakpoint, report the best and where it falls
  * permutation null -- shuffle the position order and repeat the entire
    best-breakpoint search, so the null absorbs the same selection advantage
    the observed statistic enjoys.  The question is not "does a step fit
    better than a line" (it always does) but "does it fit better than a step
    fitted to a series with no position structure"
  * report the within-segment slopes, because r02's actual argument was never
    the R^2 -- it was that effort RISES inside each segment, which a fatigue
    trend cannot produce

Two worlds:
  TREND   effort declines monotonically with task position (fatigue,
          satisficing).  A step wins only by selection.  Null z small.
  REGIME  something changes at one position -- a protocol boundary, a batch
          edge, a UI change -- and effort is roughly flat either side of it.
          Step beats its own selection-matched null, and within-segment
          slopes are non-negative.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"

MIN_SEG = 2   # each segment must hold at least this many positions


def r2(y: np.ndarray, yhat: np.ndarray) -> float:
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - float(((y - yhat) ** 2).sum()) / ss_tot if ss_tot > 1e-12 else float("nan")


def fit_trend(x: np.ndarray, y: np.ndarray):
    b = np.polyfit(x, y, 1)
    return r2(y, np.polyval(b, x)), float(b[0])


def fit_step(y: np.ndarray, cut: int) -> float:
    """Two means, split before index `cut`."""
    yhat = np.empty_like(y)
    yhat[:cut] = y[:cut].mean()
    yhat[cut:] = y[cut:].mean()
    return r2(y, yhat)


def best_step(y: np.ndarray):
    cands = range(MIN_SEG, len(y) - MIN_SEG + 1)
    scores = [(fit_step(y, c), c) for c in cands]
    return max(scores)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R02_label_and_regime/results/a02_position_bias.json")
    p.add_argument("--out", type=Path, default=_RES / "r24_regime_receipt.json")
    p.add_argument("--metric", default="rationale_chars")
    p.add_argument("--null-reps", type=int, default=20000)
    a = p.parse_args()

    if not a.source.exists():
        raise SystemExit(f"missing {a.source} -- run E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R02_label_and_regime/run.py first")
    drift = json.loads(a.source.read_text())["position_drift"]
    pos = np.array([d["position"] for d in drift], dtype=float)
    y = np.array([d[a.metric] for d in drift], dtype=float)
    n_at = {int(d["position"]): d["n"] for d in drift}
    print(f"metric = {a.metric}   positions = {len(y)}   n at pos 1 = {n_at.get(1)}\n")

    tr_r2, slope = fit_trend(pos, y)
    st_r2, cut = best_step(y)
    cut_pos = int(pos[cut])
    fixed6 = fit_step(y, int(np.argmax(pos >= 6)))
    drop = y[cut:].mean() / y[:cut].mean() - 1.0

    print(f"  linear trend        R^2 = {tr_r2:.4f}   slope = {slope:+.2f} chars/task")
    print(f"  best step           R^2 = {st_r2:.4f}   breakpoint BEFORE position {cut_pos}")
    print(f"  step fixed at 6     R^2 = {fixed6:.4f}   <- the README's model")
    print(f"  level change        {drop:+.1%}\n")

    rng = np.random.default_rng(20260728)
    null = np.array([best_step(rng.permutation(y))[0] for _ in range(a.null_reps)])
    pval = float((null >= st_r2).mean())
    z = (st_r2 - null.mean()) / (null.std() + 1e-12)
    print(f"  SELECTION-MATCHED NULL (breakpoint re-searched on each shuffle, {a.null_reps:,} reps)")
    print(f"    null best-step R^2: mean {null.mean():.4f}  sd {null.std():.4f}  "
          f"95th pct {np.percentile(null, 95):.4f}")
    print(f"    observed {st_r2:.4f}   z = {z:+.2f}   p = {pval:.4g}")
    print(f"    -> a free-breakpoint step reaches R^2 {null.mean():.3f} on POSITION-SHUFFLED data.")
    print(f"       Against a straight line ({tr_r2:.3f}) the step looks decisive; against its own")
    print(f"       selection advantage it is {'still decisive' if pval < 0.05 else 'NOT decisive'}.\n")

    seg = {}
    for name, sl in (("before", slice(0, cut)), ("after", slice(cut, len(y)))):
        if (sl.stop - (sl.start or 0)) >= 2:
            _, s = fit_trend(pos[sl], y[sl])
            seg[name] = float(s)
            print(f"  within-segment slope, {name} the break: {s:+.2f} chars/task")
    rises = all(v > 0 for v in seg.values())
    print(f"  -> effort {'RISES' if rises else 'does not rise'} inside every segment; "
          f"a monotone fatigue trend cannot produce that.\n")

    verdict = ("REGIME: the step survives a breakpoint-selection-matched null AND effort rises "
               "within each segment"
               if pval < 0.05 and rises else
               "REGIME (weak): effort rises within segments, but the step does not beat a "
               "free-breakpoint fit to position-shuffled data -- the R^2 gap over a line was "
               "mostly selection"
               if rises else
               "TREND: no regime change established beyond breakpoint selection")
    print(f"VERDICT: {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "metric": a.metric, "positions": int(len(y)),
        "trend_r2": tr_r2, "trend_slope": slope,
        "step_r2_best": st_r2, "step_breakpoint_position": cut_pos,
        "step_r2_fixed_at_6": fixed6, "level_change": float(drop),
        "null_reps": a.null_reps, "null_mean": float(null.mean()),
        "null_sd": float(null.std()), "null_p95": float(np.percentile(null, 95)),
        "z_vs_selection_matched_null": float(z), "p_value": pval,
        "within_segment_slopes": seg, "rises_within_every_segment": bool(rises),
        "verdict": verdict,
        "note": ("README carried step R^2=0.964 vs trend 0.448 with no code behind it. "
                 "The arithmetic reproduces, but comparing a free-breakpoint step against a "
                 "line charges the step nothing for choosing its breakpoint. The null here "
                 "re-searches the breakpoint on every shuffle, so it absorbs that advantage."),
    }, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
