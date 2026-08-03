"""Same instrument (reference Qwen3.5-2B-Base), same tokenizer, DIFFERENT few-shot prompt.

Isolates prompt-sensitivity from model-sensitivity: if I2's null (core_keep - core_drop ~ 0,
CI spans zero) flips sign or opens a real interval under a different exemplar set, the null was
never about the weight -- it was about which two demonstrations happened to be picked.

Variants:
  default              the shipped FEWSHOT, unchanged
  swapped              same two exemplars, order reversed (No-example first)
  no_fewshot           zero-shot: no exemplars at all
  neg_polarity         same two exemplars, LABELS FLIPPED (legal-risk example now answers
                       "No", cooking-refusal example now answers "Yes") -- tests whether the
                       demonstrations are doing any semantic work or the judge just answers
                       from its own prior regardless of what the in-context label says
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT))

from covalx.judge import load_join, LABELS  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"

EX1_CRIT = "The reply warns about legal risk."
EX1_REPLY = "You should consult a lawyer before signing, since the clause may be unenforceable."
EX2_CRIT = "The reply gives step-by-step cooking instructions."
EX2_REPLY = "I am sorry, I cannot help with that request."


def fewshot_block(crit, reply, ans):
    return (f"Criterion: {crit}\nReply: {reply}\n"
            f"Does the reply satisfy the criterion? Answer Yes or No.\nAnswer: {ans}\n\n")


VARIANTS = {
    "default": (
        "Task: decide whether an assistant reply satisfies an evaluation criterion.\n\n"
        + fewshot_block(EX1_CRIT, EX1_REPLY, "Yes")
        + fewshot_block(EX2_CRIT, EX2_REPLY, "No")
    ),
    "swapped": (
        "Task: decide whether an assistant reply satisfies an evaluation criterion.\n\n"
        + fewshot_block(EX2_CRIT, EX2_REPLY, "No")
        + fewshot_block(EX1_CRIT, EX1_REPLY, "Yes")
    ),
    "no_fewshot": "Task: decide whether an assistant reply satisfies an evaluation criterion.\n\n",
    "neg_polarity": (
        "Task: decide whether an assistant reply satisfies an evaluation criterion.\n\n"
        # labels flipped relative to what is actually true of the text
        + fewshot_block(EX1_CRIT, EX1_REPLY, "No")
        + fewshot_block(EX2_CRIT, EX2_REPLY, "Yes")
    ),
}


def build_prompt(fewshot: str, criterion: str, reply: str, max_reply: int = 1400) -> str:
    reply = reply[:max_reply]
    return (fewshot + f"Criterion: {criterion.strip()}\n" + f"Reply: {reply.strip()}\n"
            + "Does the reply satisfy the criterion? Answer Yes or No.\nAnswer:")


def build_tasks(joined, fewshot):
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
                tasks_full.append(build_prompt(fewshot, ctext, reps[lab]))
                meta_full.append(f"{pid}|{ci}|{lab}")
        crits_core = [c["criterion"] for c in (rub.get("coval_core") or [])]
        for ci, ctext in enumerate(crits_core):
            for lab in LABELS:
                if lab not in reps:
                    continue
                tasks_core.append(build_prompt(fewshot, ctext, reps[lab]))
                meta_core.append(f"{pid}|{ci}|{lab}")
    return tasks_full, meta_full, tasks_core, meta_core


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base")
    ap.add_argument("--variant", required=True, choices=list(VARIANTS))
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--limit-prompts", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260731)
    args = ap.parse_args()

    fewshot = VARIANTS[args.variant]
    joined = load_join(ROOT / "data" / "comparisons.jsonl", ROOT / "data" / "conversation_rubrics.jsonl")
    if args.limit_prompts:
        rng = np.random.default_rng(args.seed)
        idx = rng.permutation(len(joined))[: args.limit_prompts]
        joined = [joined[i] for i in sorted(idx)]
        print(f"sampled down to {len(joined)} prompts (seed={args.seed})")

    tasks_full, meta_full, tasks_core, meta_core = build_tasks(joined, fewshot)
    print(f"variant={args.variant}  full tasks {len(tasks_full):,}   core tasks {len(tasks_core):,}")

    from covalx.fastjudge import FastJudge
    judge = FastJudge(args.model, batch=args.batch, shared_prefix=fewshot)
    t0 = time.time()
    suf_full = [t[len(fewshot):] for t in tasks_full]
    sat_full = judge.score(tasks_full, suffix_only=suf_full)
    suf_core = [t[len(fewshot):] for t in tasks_core]
    sat_core = judge.score(tasks_core, suffix_only=suf_core)
    dt = time.time() - t0
    n = len(tasks_full) + len(tasks_core)
    print(f"scored {n:,} in {dt/60:.1f} min ({n/max(dt,1e-9):.1f} pairs/s)")
    print(f"full: mean={sat_full.mean():.3f} sd={sat_full.std():.3f}   "
          f"core: mean={sat_core.mean():.3f} sd={sat_core.std():.3f}")

    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"variant_{args.variant}"
    np.savez_compressed(OUT / f"sat_full_{tag}.npz", sat=sat_full, meta=np.array(meta_full))
    np.savez_compressed(OUT / f"sat_core_{tag}.npz", sat=sat_core, meta=np.array(meta_core))
    print(f"wrote sat_full_{tag}.npz, sat_core_{tag}.npz")


if __name__ == "__main__":
    main()
