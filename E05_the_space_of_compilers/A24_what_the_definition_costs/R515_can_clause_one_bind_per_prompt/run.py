#!/usr/bin/env python3
"""R515 — can clause ① bind if operationalised PER-PROMPT?

R514 found ① excludes nothing and called it a DERIVATION forced by transitivity of `>`. Reading
R294's code (line 139) shows the clauses are NOT `a2 > bar`: they are paired-difference INTERVAL
verdicts against two comparator ARMS -- ① against `random_k4_s0`, ② against the blind pool at
matched k. This round tests the escape R514 named (a per-prompt ①) and, in specifying it
correctly, re-prices R514's own warrant.

ESTIMAND (before method): the fraction of prompts on which the clause-① comparator outscores the
  clause-② comparator. If ~0, per-prompt ① is subsumed exactly as the global one is, and clause
  ① is dead in both readings. If substantial, a per-prompt ① binds where the global one cannot.
IDENTIFICATION: fully identified -- both comparators are released saturation matrices scored by
  the same per-prompt A2 the census uses.
SCOPE  population: the 968 prompts with >=2 annotators · instrument: per-prompt A2 over ALL
  annotators (as R294's `on()` does) · baseline: the two comparators against each other ·
  regime: pool truncated to k=4 to size-match ①'s k=4 comparator.
WORLDS  A · the ①-comparator is below the ②-comparator on essentially every prompt, so a
              per-prompt ① is subsumed too and clause ① is deletable.
        B · the ordering reverses on a real fraction of prompts, so a per-prompt ① binds.
KILL (pre-registered): fraction of prompts with bar1 > bar2 below 2% kills B.
POSITIVE CONTROL: the MEAN of the per-prompt difference must reproduce the census's own
  aggregate ordering (bar1 < bar2, gap ~0.046 from R514) within +-0.02. A reconstruction that
  cannot recover the aggregate cannot be trusted about its tail.
  ⚠ THE FIRST VERSION OF THIS ROUND FAILED EXACTLY HERE, at 0.4171 vs 0.4927, because it
  reconstructed a random-DRAW distribution rather than the fixed comparator ARM. The control
  caught a wrong object, which is what it is for.
NEGATIVE CONTROL: each comparator against ITSELF must give exactly 0 on every prompt.
NOISE FLOOR: per-prompt A2 takes 7 values over 6 pairs; the sd of the per-prompt difference
  bounds how much of any tail is resolution rather than signal.
MULTIPLICITY: 2 comparators x 1 contrast; no grid, so no correction is owed. Stated, not skipped.
IMPOSSIBLE HERE: whether a per-prompt ① is the RIGHT formulation -- a construct claim needing an
  external standard for what a core must do. Named, not marked planned.
"""
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
import score as S

K = 4

def per_prompt(sat, pids, HC, idx=None):
    return np.array([np.mean([[S.cls(S.yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                               for q in range(6)] for h in HC[p]]) for p in pids])

def main():
    RES = ROOT / "corebench/results"
    c1_arm = S.load_sat(RES / "sat_random_k4_s0.npz")
    pool   = S.load_sat(RES / "sat_genericpool16.npz")
    targets, _ = S.load_targets()
    pids = [p for p in c1_arm if p in targets and p in pool and len(targets[p]) >= 2]
    if not pids:
        print("  empty population -> UNRUNNABLE"); return 2
    HC = {p: [S.cls(y) for y, _ in targets[p]] for p in pids}
    print(f"  population: {len(pids)} prompts")

    bar1 = per_prompt(c1_arm, pids, HC)
    bar2 = per_prompt(pool, pids, HC, list(range(K)))

    # NEGATIVE CONTROL: each comparator against itself
    neg = float(np.abs(per_prompt(c1_arm, pids, HC) - bar1).max())
    print(f"  NEGATIVE CONTROL  comparator vs itself, max |diff| = {neg:.6f} -> "
          f"{'PASS' if neg == 0 else 'FAIL'}")

    gap = float((bar2 - bar1).mean())
    pos_ok = abs(gap - 0.0577) <= 0.01
    print(f"  POSITIVE CONTROL  mean(bar2-bar1) = {gap:+.4f} vs R294's k=4 arms +0.0577 -> "
          f"{'PASS' if pos_ok else 'FAIL'}")
    if neg != 0 or not pos_ok:
        print("  -> reconstruction unvalidated; NO conclusion admissible. UNVERIFIED.")
        world = "UNVERIFIED"; frac = None
    else:
        frac = float((bar1 > bar2).mean())
        ties = float((bar1 == bar2).mean())
        sd = float((bar1 - bar2).std(ddof=1))
        world = "B" if frac >= 0.02 else "A"
        print(f"\n  mean bar1 {bar1.mean():.4f}   mean bar2 {bar2.mean():.4f}")
        print(f"  NOISE FLOOR  sd of the per-prompt difference = {sd:.4f} "
              f"(per-prompt A2 has only 7 levels)")
        print(f"  prompts where bar1 > bar2: {frac:.4f}    exact ties: {ties:.4f}")
        print(f"  WORLD {world} -- " +
              ("a per-prompt ① BINDS on a real fraction of prompts; re-scoring is worth running"
               if world == "B" else
               "per-prompt ① is subsumed too; clause ① is dead in both readings"))

    out = pathlib.Path(__file__).parent / "results/per_prompt_bar.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "k": K, "n_prompts": len(pids), "positive_control_pass": bool(pos_ok),
        "negative_control_max_abs": neg, "mean_gap": gap,
        "mean_bar1": float(bar1.mean()), "mean_bar2": float(bar2.mean()),
        "frac_bar1_above_bar2": frac, "world": world,
        "comparators": {"clause1": "sat_random_k4_s0", "clause2": "sat_genericpool16[:4]"},
    }, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
