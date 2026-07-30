"""A10 -- Is the 43%/57% attribution real, or an artifact of one judge and one shuffle?

A04 reported: of a rubric's predictive power over held-out human rankings,
~43% is prompt-specific criterion content and ~57% is generic response quality
that an unrelated rubric earns for free.

That number rests on one judge, one prompt template, and one way of shuffling.
Three attacks, all run here:

  ATTACK 1  judge size        2B vs 0.8B backbone
  ATTACK 2  judge template    two different few-shot framings
  ATTACK 3  donor distance    who supplies the "wrong" rubric?

Attack 3 is the sharp one. The shuffled control donates criteria from a RANDOM
other prompt. But a random prompt is usually about a different topic, so the
control may be measuring "topic mismatch" rather than "value mismatch". So we
grade three donors:

    far       the least similar prompt in the corpus
    random    a uniformly random other prompt        (what A04 used)
    near      the most similar OTHER prompt

If the near-donor rubric scores almost as well as the real one, then what A04
called "prompt-specific value content" is largely TOPIC specificity, and the
genuinely value-carrying share is smaller still. That would strengthen the
headline, not weaken it -- which is exactly why it has to be run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from covalx import LABELS, Judge, build_prompt, human_pairs, load_join  # noqa: E402

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")

MODELS = {
    "qwen3.5-2b": os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base"),
    "qwen3.5-0.8b": os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base"),
}

TEMPLATE_B_HEAD = (
    "You are grading assistant replies against evaluation criteria.\n\n"
    "Criterion: The reply names a concrete next action.\n"
    "Reply: Book an appointment with your GP this week and bring a symptom diary.\n"
    "Graded: Yes\n\n"
    "Criterion: The reply avoids giving medical advice.\n"
    "Reply: Take 400mg ibuprofen every four hours for the pain.\n"
    "Graded: No\n\n"
)


def build_prompt_b(criterion: str, reply: str, max_reply: int = 1400) -> str:
    return (TEMPLATE_B_HEAD + f"Criterion: {criterion.strip()}\n"
            + f"Reply: {reply[:max_reply].strip()}\nGraded:")


@torch.inference_mode()
def prompt_embeddings(texts, model_dir, batch=16):
    tok = AutoTokenizer.from_pretrained(model_dir)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    m = AutoModel.from_pretrained(model_dir, dtype=torch.bfloat16, device_map="cuda").eval()
    out = []
    for i in range(0, len(texts), batch):
        enc = tok(texts[i:i+batch], return_tensors="pt", padding=True,
                  truncation=True, max_length=256).to("cuda")
        h = m(**enc).last_hidden_state
        mk = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
        out.append(((h*mk).sum(1)/mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    torch.cuda.empty_cache()
    E = np.concatenate(out, 0)
    return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)


def accuracy(items, crit_of, sat_lut, kind):
    agree = tot = 0
    for k, it in enumerate(items):
        score = {}
        for lab in LABELS:
            vals = [sat_lut[(kind, k, ci, lab)] for ci in range(len(crit_of[k]))
                    if (kind, k, ci, lab) in sat_lut]
            score[lab] = float(np.mean(vals)) if vals else 0.0
        for x, y in it["pairs"]:
            tot += 1
            agree += int(score.get(x, 0) > score.get(y, 0))
    return agree / max(tot, 1), tot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a10_attribution.json"))
    ap.add_argument("--prompts", type=int, default=300)
    ap.add_argument("--batch", type=int, default=32)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items, crits = [], []
    qtexts = []
    for pid, comp, rub in joined:
        c = [x["criterion"] for x in (rub.get("coval_core") or [])]
        hp = human_pairs(comp["metadata"]["assessments"])
        if not c or not hp:
            continue
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        items.append({"pid": pid, "pairs": hp,
                      "resp": {r["response_index"]: r["messages"][0]["content"]
                               for r in comp["responses"]}})
        crits.append(c)
        qtexts.append(q[-1] if q else "")
    n = len(items)
    print(f"prompts: {n}")

    # ---- donor assignment by prompt similarity -----------------------
    E = prompt_embeddings(qtexts, MODELS["qwen3.5-2b"])
    S = E @ E.T
    np.fill_diagonal(S, -np.inf)
    near = S.argmax(1)
    S2 = S.copy(); S2[np.isneginf(S2)] = np.inf
    far = S2.argmin(1)
    rng = np.random.default_rng(20260727)
    rand = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
    donors = {"real": np.arange(n), "near": near, "random": rand, "far": far}
    print("  donor mean cosine:  " + "  ".join(
        f"{k}={float(np.mean([S[i, d[i]] if k!='real' else 1.0 for i in range(n)])):+.3f}"
        for k, d in donors.items()))

    results = {}
    for mname, mdir in MODELS.items():
        for tname, builder in (("A", build_prompt), ("B", build_prompt_b)):
            if mname == "qwen3.5-0.8b" and tname == "B":
                continue                      # 3 cells is enough to separate the axes
            judge = Judge(mdir, batch=a.batch)
            judge_lut = {}
            tasks, meta = [], []
            for kind, dmap in donors.items():
                for k in range(n):
                    src = crits[dmap[k]]
                    for ci, c in enumerate(src):
                        for lab in LABELS:
                            if lab not in items[k]["resp"]:
                                continue
                            tasks.append(builder(c, items[k]["resp"][lab]))
                            meta.append((kind, k, ci, lab))
            print(f"  [{mname}/{tname}] judgements: {len(tasks):,}", flush=True)
            sat = judge.score(tasks)
            for mt, s in zip(meta, sat):
                judge_lut[mt] = float(s)
            del judge
            torch.cuda.empty_cache()

            cell = {}
            for kind, dmap in donors.items():
                co = [crits[dmap[k]] for k in range(n)]
                acc, tot = accuracy(items, co, judge_lut, kind)
                cell[kind] = acc
            cell["attribution_vs_random"] = cell["real"] - cell["random"]
            cell["attribution_vs_near"] = cell["real"] - cell["near"]
            cell["topic_share_of_gap"] = (
                (cell["near"] - cell["random"]) / max(cell["real"] - cell["random"], 1e-9)
            )
            results[f"{mname}/{tname}"] = cell
            print(f"    real={cell['real']:.4f} near={cell['near']:.4f} "
                  f"random={cell['random']:.4f} far={cell['far']:.4f}   "
                  f"attribution(vs random)={cell['attribution_vs_random']:+.4f}  "
                  f"attribution(vs near)={cell['attribution_vs_near']:+.4f}")

    print("\n=== is the attribution stable across judge and template? ===")
    vals = [c["attribution_vs_random"] for c in results.values()]
    print(f"  attribution vs random: {np.mean(vals):.4f} +- {np.std(vals):.4f} "
          f"across {len(vals)} judge/template cells  (range {min(vals):.4f}..{max(vals):.4f})")
    vals2 = [c["attribution_vs_near"] for c in results.values()]
    print(f"  attribution vs NEAR  : {np.mean(vals2):.4f} +- {np.std(vals2):.4f}")
    ts = [c["topic_share_of_gap"] for c in results.values()]
    print(f"  share of the 'prompt-specific' gap that is merely TOPIC: {np.mean(ts):.1%}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"prompts": n, "cells": results,
                                 "attribution_mean": float(np.mean(vals)),
                                 "attribution_sd": float(np.std(vals)),
                                 "attribution_vs_near_mean": float(np.mean(vals2)),
                                 "topic_share_mean": float(np.mean(ts))}, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
