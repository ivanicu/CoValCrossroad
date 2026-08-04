"""R370 (part 1) — judge the 16-criterion GENERIC POOL against the FRESH responses.

R369 named the instrument this produces and could not build it from cache:

    "The floor is a random draw from `full`'s OWN criteria -- among the items being summed to make
     the target -- while the core is a rewrite. A subset of an aggregation has a structural
     advantage at reproducing it. Separating it needs a floor drawn from criteria OUTSIDE `full`,
     and this cache contains only `core` and `full`."

⚠ THE TWO-COMMAND CHECK CAME BACK AGAINST THE CHEAP ANSWER. The previous NEXT line asked whether the
  generic pool had ever been judged against the FRESH responses, because that decides re-analysis vs
  GPU. It has not: the only fresh-response satisfaction file in the repository is R233's, and it
  contains `core` and `full` only. So this is a GPU job, and saying so is the point of having run
  the check instead of assuming.

WHAT THIS PRODUCES, and what it deliberately does NOT do. This script emits satisfaction labels
ONLY. It computes no contrast, fits nothing, and states no verdict -- the analysis is a separate
round against these labels, so that the instrument cannot be tuned against the answer it is being
built to produce.

WHY THE GENERIC POOL IS THE RIGHT NON-SUBSET FLOOR:
  · its 16 criteria are authored for the benchmark and are IDENTICAL across prompts, so they are
    outside any particular prompt's `full` rubric BY CONSTRUCTION -- which is exactly the property
    the subset floor lacks;
  · it is the same pool clause ② has used as its blind reference throughout this campaign, so it
    carries no new instrument and no new assumption;
  · it was already judged against the ORIGINAL responses (`sat_genericpool16.npz`), so the fresh
    labels complete a matched pair rather than starting a fresh axis.

SCOPE          the 250 prompts R12 generated fresh responses for · 16 pool criteria x 4 responses
               = 16,000 judgements · Qwen3.5-2B-Base, the same judge and the same `Judge` class
               R233 used, so the labels are comparable to the cache they will be joined to.
OUTPUT         results/sat_genericpool16_fresh.npz, in R233's exact meta format
               `pid|arm|set|criterion|response`, so the analysis round can concatenate rather than
               re-derive.
DETERMINISM    greedy read of the Yes/No logit gap; no sampling anywhere in this script.

⚠ AND ONE LIMIT DOES NOT MOVE, restated rather than dropped: the fresh responses carry NO HUMAN
  RANKINGS (R12's own `outcome_variable_scope` field says so, and R233 and R368 both restated it).
  Whatever floor this enables is a floor for agreement with the FULL RUBRIC, never with people.
"""
from __future__ import annotations
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from covalx.judge import Judge, build_prompt          # noqa: E402

MODEL = ("/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
         "Qwen3.5-2B-Base")
GEN = (ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor"
       / "R12_response_set/results/a12_fresh_generations.json")
POOL = ROOT / "corebench" / "results" / "core_genericpool16.json"
OUT = HERE / "results" / "sat_genericpool16_fresh.npz"
L = "ABCD"


def main() -> int:
    for f in (GEN, POOL):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2
    gen = json.loads(GEN.read_text())
    pool = json.loads(POOL.read_text())
    pids, fresh = gen["prompt_ids"], gen["fresh"]
    if len(pids) != len(fresh):
        print("  UNRUNNABLE: prompt_ids and fresh differ in length. Exit 2."); return 2

    # the pool is the SAME 16 criteria for every prompt; assert it rather than assume it,
    # because "identical across prompts" is the property that makes this floor non-subset.
    sets = {tuple(v) for v in pool.values()}
    if len(sets) != 1:
        print(f"  UNRUNNABLE: the generic pool is NOT identical across prompts "
              f"({len(sets)} distinct sets). The non-subset argument rests on it being "
              f"one fixed set; it is not. Exit 2, never 0.")
        return 2
    crits = list(next(iter(sets)))
    usable = [(p, r) for p, r in zip(pids, fresh) if isinstance(r, list) and len(r) == 4]
    if not usable:
        print("  UNRUNNABLE: no prompt carries 4 fresh responses. Exit 2, never 0."); return 2

    n = len(usable) * len(crits) * 4
    print(f"  {len(usable)} prompts x {len(crits)} pool criteria x 4 responses = {n} judgements")
    print(f"  pool is ONE fixed set across all prompts: asserted, not assumed")
    print(f"  judge {MODEL}\n", flush=True)

    prompts, meta = [], []
    for pid, resp in usable:
        for ci, c in enumerate(crits):
            for ri in range(4):
                prompts.append(build_prompt(c, resp[ri]))
                meta.append(f"{pid}|fresh|pool|{ci}|{ri}")

    j = Judge(MODEL)
    sat = j.score(prompts)

    OUT.parent.mkdir(exist_ok=True)
    np.savez_compressed(OUT, meta=np.array(meta), sat=sat.astype(np.float32),
                        weight=np.ones(len(sat), dtype=np.float32))
    print(f"\n  wrote {OUT.relative_to(ROOT)}  {len(sat)} labels")
    print(f"  sat: mean {float(sat.mean()):.4f}  min {float(sat.min()):.4f}  "
          f"max {float(sat.max()):.4f}")
    # a degenerate judge returns a constant; say so here rather than in the analysis round
    if float(sat.std()) < 1e-6:
        print("  ⛔ the judge returned a CONSTANT — these labels carry no information. "
              "The analysis round must refuse them.")
        return 1
    print(f"  sd {float(sat.std()):.4f} — non-degenerate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
