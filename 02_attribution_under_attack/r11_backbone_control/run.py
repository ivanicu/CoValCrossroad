"""A11 -- Was A09's negative result a shared-backbone artifact?

A09 concluded: under best-of-16 selection against the rubric, gold human
preference ROSE (+0.53 [0.06, 0.99]) and gaming markers FELL, so no
overoptimization was detected at that pressure.

The weakness, stated in A09's own limits: the proxy judge and the gold
preference head both run on Qwen3.5-2B. If best-of-n selects surface features
that the shared backbone happens to like, gold rises for a reason that has
nothing to do with human preference, and the negative result is an artifact.

This rescores the SAME saved generations with a gold head built on the 0.8B
backbone -- a different model from the 2B judge -- and recomputes the curve.

  gold rises again      -> the negative result survives its main confound
  gold flattens / falls -> A09's conclusion was backbone leakage and is retracted

Nothing is regenerated: the texts, the proxy scores and the selection seed are
loaded from a09_overoptimization.npz, so the only thing that changes is who
plays gold.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

OUTCOME_SCOPE = (
    "Scored against the r08 MODEL GOLD HEAD, not against human rankings -- no hum"
    "an ranked these generated responses. The retraction it establishes is theref"
    "ore a statement about the proxy-world measurement, which is the correct scop"
    "e for overturning r09 (also proxy-world), but is not a statement about human"
    " preference."
)

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")

STRENGTHS = (1, 2, 4, 8, 16)
M08 = os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base")


@torch.inference_mode()
def embed(texts, model_dir, batch=16, max_len=512):
    tok = AutoTokenizer.from_pretrained(model_dir)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    m = AutoModel.from_pretrained(model_dir, dtype=torch.bfloat16, device_map="cuda").eval()
    out = []
    for i in range(0, len(texts), batch):
        enc = tok(list(texts[i:i+batch]), return_tensors="pt", padding=True,
                  truncation=True, max_length=max_len).to("cuda")
        h = m(**enc).last_hidden_state
        mk = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
        out.append(((h*mk).sum(1)/mk.sum(1).clamp(min=1)).float().cpu().numpy())
        if (i // batch) % 40 == 0:
            print(f"  embed {i}/{len(texts)}", flush=True)
    del m
    torch.cuda.empty_cache()
    return np.concatenate(out, 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a09", type=Path, default=Path(_ROOT) / "01_object_and_rebuild" / "r09_overoptimization" / "results" / "a09_overoptimization.npz")
    ap.add_argument("--gold", type=Path, default=Path(_ROOT) / "01_object_and_rebuild" / "r08_gold_preference" / "results" / "a08_gold_08b.npz")
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a11_backbone_control.json"))
    a = ap.parse_args()

    z = np.load(a.a09, allow_pickle=True)
    proxy, gold2b, texts = z["proxy"], z["gold"], z["texts"]
    n_items, n_cand = proxy.shape
    print(f"reusing A09 generations: {n_items} prompts x {n_cand} candidates")

    g = np.load(a.gold)
    w, mu, sd = g["w"], g["mean"], g["std"]
    flat = [str(t) for t in texts]
    E = (embed(flat, M08) - mu) / (sd + 1e-6)
    L = np.array([[len(t), len(t.split())] for t in flat], dtype=float)
    L = (L - L.mean(0)) / (L.std(0) + 1e-6)
    gold08 = (np.hstack([E, L]) @ w).reshape(n_items, n_cand)

    corr = float(np.corrcoef(gold2b.ravel(), gold08.ravel())[0, 1])
    print(f"correlation between the two gold heads: {corr:+.4f}")

    rng = np.random.default_rng(20260727)
    strengths = [s for s in STRENGTHS if s <= n_cand]
    per_prompt = {}
    rows = []
    for n in strengths:
        pg2, pg8 = np.zeros(n_items), np.zeros(n_items)
        for k in range(n_items):
            a2, a8 = [], []
            for _ in range(24):
                idx = rng.choice(n_cand, size=n, replace=False)
                best = idx[np.argmax(proxy[k, idx])]
                a2.append(gold2b[k, best]); a8.append(gold08[k, best])
            pg2[k], pg8[k] = np.mean(a2), np.mean(a8)
        per_prompt[n] = (pg2, pg8)
        rows.append({"n": n, "gold_2b": float(pg2.mean()), "gold_08b": float(pg8.mean())})
        print(f"  n={n:>2}  gold(2B, shared backbone)={pg2.mean():+.4f}   "
              f"gold(0.8B, independent)={pg8.mean():+.4f}")

    out = {"prompts": n_items, "gold_head_correlation": corr, "curve": rows}
    print("\n=== paired change from n=1 to n=%d ===" % strengths[-1])
    for i, name in ((0, "gold_2b_shared"), (1, "gold_08b_independent")):
        d = per_prompt[strengths[-1]][i] - per_prompt[strengths[0]][i]
        bs = np.array([d[rng.integers(0, len(d), size=len(d))].mean() for _ in range(4000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        verdict = ("rises" if lo > 0 else "falls" if hi < 0 else "indistinguishable from zero")
        out[name] = {"delta": float(d.mean()), "ci": [float(lo), float(hi)], "verdict": verdict}
        print(f"  {name:24s} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  -> {verdict}")

    shared = out["gold_2b_shared"]["verdict"]
    indep = out["gold_08b_independent"]["verdict"]
    if indep == "rises":
        concl = ("SURVIVES: an independent backbone reproduces the rise, so A09's "
                 "no-gaming-detected result is not backbone leakage")
    elif indep == "falls":
        concl = ("RETRACTED: the independent backbone shows the opposite sign; A09's "
                 "rise was shared-backbone leakage")
    else:
        concl = ("WEAKENED: the independent backbone cannot distinguish the change from "
                 "zero, so A09's rise is not established; the no-gaming reading stands "
                 "only as 'no effect detected either way'")
    print(f"\n  -> {concl}")
    out["conclusion"] = concl

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
