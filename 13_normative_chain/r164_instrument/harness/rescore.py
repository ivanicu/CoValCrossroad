"""Re-score the criterion x response satisfaction layer with a DIFFERENT judge model,
on the EXACT same (prompt, criterion-index, response-letter) grid that a04_full.npz /
a04_core.npz cover -- so the resulting sat/meta arrays drop into r155/r158/r159/r160's
own analysis code unchanged.

Mirrors 01_object_and_rebuild/r04_rebuild_satisfaction/run.py's crits-construction
EXACTLY (same filter: full criteria need >=1 score; core criteria unconditional), so the
`ci` indices line up with the shipped a04 tensors index-for-index. Uses covalx.judge's
FIXED Judge (generic, handles any tokenizer) or covalx.fastjudge.FastJudge (fast path,
requires " Yes"/" No" to be single, distinct tokens -- true for every Qwen judge here).
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT))

from covalx.judge import load_join, build_prompt, FEWSHOT, LABELS  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"


def build_tasks(joined):
    """Exact mirror of r04's crits construction for BOTH full and core."""
    tasks_full, meta_full = [], []
    tasks_core, meta_core = [], []
    for pid, comp, rub in joined:
        reps = {r["response_index"]: r["messages"][0]["content"] for r in comp["responses"]}

        crits_full = []
        for it in rub.get("coval_full") or []:
            sc = [s["score"] for s in it.get("scores") or []]
            if sc:
                crits_full.append(it["criterion"])
        for ci, ctext in enumerate(crits_full):
            for lab in LABELS:
                if lab not in reps:
                    continue
                tasks_full.append(build_prompt(ctext, reps[lab]))
                meta_full.append(f"{pid}|{ci}|{lab}")

        crits_core = [c["criterion"] for c in (rub.get("coval_core") or [])]
        for ci, ctext in enumerate(crits_core):
            for lab in LABELS:
                if lab not in reps:
                    continue
                tasks_core.append(build_prompt(ctext, reps[lab]))
                meta_core.append(f"{pid}|{ci}|{lab}")
    return tasks_full, meta_full, tasks_core, meta_core


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--engine", choices=["fast", "slow"], default="slow")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--limit-prompts", type=int, default=0, help="0 = all")
    ap.add_argument("--seed", type=int, default=20260731)
    args = ap.parse_args()

    joined = load_join(ROOT / "data" / "comparisons.jsonl", ROOT / "data" / "conversation_rubrics.jsonl")
    print(f"joined prompts: {len(joined)}")
    if args.limit_prompts:
        rng = np.random.default_rng(args.seed)
        idx = rng.permutation(len(joined))[: args.limit_prompts]
        joined = [joined[i] for i in sorted(idx)]
        print(f"sampled down to {len(joined)} prompts (seed={args.seed})")

    tasks_full, meta_full, tasks_core, meta_core = build_tasks(joined)
    print(f"full tasks {len(tasks_full):,}   core tasks {len(tasks_core):,}   "
          f"total {len(tasks_full) + len(tasks_core):,}")

    if args.engine == "fast":
        from covalx.fastjudge import FastJudge
        judge = FastJudge(args.model, batch=args.batch, shared_prefix=FEWSHOT)
        t0 = time.time()
        pref_len = judge.prefix_len
        suf_full = [t[len(FEWSHOT):] for t in tasks_full]
        sat_full = judge.score(tasks_full, suffix_only=suf_full)
        suf_core = [t[len(FEWSHOT):] for t in tasks_core]
        sat_core = judge.score(tasks_core, suffix_only=suf_core)
        dt = time.time() - t0
    else:
        from covalx.judge import Judge
        judge = Judge(args.model, batch=args.batch)
        t0 = time.time()
        sat_full = judge.score(tasks_full)
        sat_core = judge.score(tasks_core)
        dt = time.time() - t0

    n = len(tasks_full) + len(tasks_core)
    print(f"scored {n:,} in {dt/60:.1f} min ({n/max(dt,1e-9):.1f} pairs/s)")
    print(f"full: mean={sat_full.mean():.3f} sd={sat_full.std():.3f}   "
          f"core: mean={sat_core.mean():.3f} sd={sat_core.std():.3f}")

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"sat_full_{args.tag}.npz", sat=sat_full,
                        meta=np.array(meta_full))
    np.savez_compressed(OUT / f"sat_core_{args.tag}.npz", sat=sat_core,
                        meta=np.array(meta_core))
    print(f"wrote sat_full_{args.tag}.npz, sat_core_{args.tag}.npz")
    (OUT / f"receipt_{args.tag}.txt").write_text(
        f"model={args.model}\nengine={args.engine}\nprompts={len(joined)}\n"
        f"full_tasks={len(tasks_full)}\ncore_tasks={len(tasks_core)}\nseconds={dt:.1f}\n"
        f"pairs_per_sec={n/max(dt,1e-9):.2f}\n")


if __name__ == "__main__":
    main()
