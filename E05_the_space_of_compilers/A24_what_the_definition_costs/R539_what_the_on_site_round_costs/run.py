#!/usr/bin/env python3
"""R539 — price the on-site generation round the register calls rows 3 and 4.

R539 closes the loop my last line opened: "the next round can either spend that or state why not,
and the honest version of why not is a cost that has not been measured." It is measurable exactly,
because `gen` ALREADY EXISTS -- a generation round has been run on this site before, so its work is
readable from the artifact rather than estimated.

ESTIMAND (before method): the number of LLM calls a rows-3/4 round requires, split into GENERATION
  (one criterion set per prompt) and JUDGING (one satisfaction cell per criterion x response),
  counted from the existing `gen` artifacts.
IDENTIFICATION: fully identified for the CALL COUNT. ⚠ NOT identified for wall-clock or cost --
  that needs a throughput measurement on this box, which this round does not have and says so.
SCOPE  population: the prompts `sat_gen.npz` covers · instrument: cell counts in the .npz ·
  baseline: n/a, a census · regime: first release, home judge.
WORLDS  A · the round is cheap on this site -- call counts within what a local model does in a
              session, so "why not" cannot be cost.
        B · it is expensive -- the count is large enough that cost is a real answer.
KILL (pre-registered): judge cells above ~100k puts it in world B for a local 2B model.
POSITIVE CONTROL: the per-prompt cell count must equal k x 4 for the arms whose k is known --
  `topw_k4` must give exactly 16 cells per prompt. If the arithmetic does not hold, the counter is
  not measuring judge calls.
NEGATIVE CONTROL: `full` must have MORE cells per prompt than any k-limited arm, since it keeps
  every criterion. An arm-size ordering that inverts would mean the counter reads something else.
NOISE FLOOR: none -- exact counts.
MULTIPLICITY: 4 arms counted; all printed.
IMPOSSIBLE HERE: wall-clock and money. Converting calls to time needs a measured tokens/sec for
  the specific local model on this GPU, through pueue. Named, not marked planned, and NOT guessed.
"""
import collections, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "corebench/results"

def cells(tag):
    d = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    per = collections.Counter()
    for k in d["meta"]:
        pid, _i, _x = str(k).split("|")
        per[pid] += 1
    return len(d["meta"]), per

def main():
    rows = {}
    for t in ("gen", "topw_k4", "full", "coval_core"):
        n, per = cells(t)
        vals = list(per.values())
        rows[t] = {"total_cells": int(n), "prompts": len(per),
                   "cells_per_prompt_median": int(np.median(vals)),
                   "cells_per_prompt_min": int(min(vals)), "cells_per_prompt_max": int(max(vals))}
        r = rows[t]
        print(f"  {t:<12}{r['total_cells']:>8} cells  {r['prompts']:>5} prompts  "
              f"per-prompt median {r['cells_per_prompt_median']:>3} "
              f"[{r['cells_per_prompt_min']}, {r['cells_per_prompt_max']}]")

    pc = rows["topw_k4"]["cells_per_prompt_median"] == 16
    print(f"\n  POSITIVE CONTROL  topw_k4 must be k x 4 = 16 cells/prompt: "
          f"{rows['topw_k4']['cells_per_prompt_median']} -> {'PASS' if pc else 'FAIL'}")
    nc = rows["full"]["cells_per_prompt_median"] > rows["topw_k4"]["cells_per_prompt_median"]
    print(f"  NEGATIVE CONTROL  `full` keeps every criterion so must exceed a k-limited arm: "
          f"{rows['full']['cells_per_prompt_median']} > {rows['topw_k4']['cells_per_prompt_median']}"
          f" -> {'PASS' if nc else 'FAIL'}")
    if not (pc and nc):
        print("  -> the counter is not measuring judge cells; UNVERIFIED."); return 0

    g = rows["gen"]
    gen_calls = g["prompts"]
    judge_cells = g["total_cells"]
    total = gen_calls + judge_cells
    world = "B" if judge_cells > 100_000 else "A"
    print(f"\n  ⭐ ONE rows-3/4 generation round, priced from the `gen` precedent:")
    print(f"     generation : {gen_calls:>7} LLM calls  (one criterion set per prompt)")
    print(f"     judging    : {judge_cells:>7} satisfaction cells "
          f"({g['cells_per_prompt_median']} per prompt x {g['prompts']})")
    print(f"     TOTAL      : {total:>7} model calls")
    print(f"  WORLD {world} -- " +
          (f"{judge_cells} judge cells is within a local-model session; "
           f"cost cannot be the reason not to run it" if world == "A" else
           "large enough that cost is a real answer"))
    print(f"\n  ⚠ NOT MEASURED HERE: wall-clock and money. Converting {total} calls to time needs a "
          f"tokens/sec figure for the specific local model on this GPU, through pueue.")
    print(f"     That is the one number 'why not' would have to cite, and this round does not "
          f"invent it.")

    out = pathlib.Path(__file__).parent / "results/on_site_cost.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"arms": rows, "generation_calls": gen_calls,
                               "judge_cells": judge_cells, "total_calls": total,
                               "world": world,
                               "not_measured": "wall-clock; needs measured tokens/sec via pueue"},
                              indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
