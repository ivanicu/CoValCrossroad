"""r15 -- In-distribution transfer, measured against real human rankings.

The cleanest form of r12's question available in this release.

For prompt P with nearest-topic neighbour Q, grade Q's four RELEASED responses
under three rubrics:

    authored  Q's own criteria  -- written by people who read these four
    neighbour P's criteria      -- topically close, never written against them
    random    some other prompt -- the generic-quality floor

and score every ordering against Q's REAL human world rankings. No gold model
appears anywhere, so the out-of-distribution objection that survives r13 cannot
apply: these are the same responses, judged by the same people, as everywhere
else in this repository.

Reading:
    authored > neighbour ~ random  -> the advantage needs criteria written
                                      against the very responses being graded
    authored ~ neighbour > random  -> the advantage is topic-level and transfers
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, Judge, build_prompt, human_pairs, load_join  # noqa: E402

MODEL = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")


@torch.inference_mode()
def prompt_embeddings(texts, batch=24):
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    m = AutoModel.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda").eval()
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r15_indistribution_transfer.json")
    ap.add_argument("--prompts", type=int, default=300)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items = []
    for pid, comp, rub in joined:
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        hp = human_pairs(comp["metadata"]["assessments"])
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        if cr and hp and q:
            items.append({"pid": pid, "crits": cr, "pairs": hp, "q": q[-1],
                          "resp": {r["response_index"]: r["messages"][0]["content"]
                                   for r in comp["responses"]}})
    n = len(items)
    print(f"prompts: {n}")

    S = prompt_embeddings([it["q"] for it in items])
    S = S @ S.T
    np.fill_diagonal(S, -np.inf)
    near = S.argmax(1)
    rng = np.random.default_rng(20260727)
    rand = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
    print(f"  mean cosine to nearest neighbour: {float(np.mean([S[i, near[i]] for i in range(n)])):+.3f}")
    print(f"  mean cosine to random prompt    : {float(np.mean([S[i, rand[i]] for i in range(n)])):+.3f}")

    # grade TARGET q's responses under three criterion sources
    sources = {"authored": np.arange(n), "neighbour": near, "random": rand}
    judge = Judge(MODEL, batch=32)
    tasks, meta = [], []
    for name, src in sources.items():
        for k in range(n):
            for ci, c in enumerate(items[src[k]]["crits"]):
                for lab in items[k]["resp"]:
                    tasks.append(build_prompt(c, items[k]["resp"][lab]))
                    meta.append((name, k, ci, lab))
    print(f"  judgements: {len(tasks):,}", flush=True)
    sat = judge.score(tasks)
    del judge
    torch.cuda.empty_cache()

    acc = {}
    for mt, s in zip(meta, sat):
        name, k, ci, lab = mt
        acc.setdefault((name, k), {}).setdefault(lab, []).append(float(s))

    per = {name: [] for name in sources}
    for name in sources:
        for k in range(n):
            d = acc.get((name, k))
            if not d:
                continue
            score = {lab: float(np.mean(v)) for lab, v in d.items()}
            ok = tot = 0
            for x, y in items[k]["pairs"]:
                if x in score and y in score:
                    tot += 1
                    ok += int(score[x] > score[y])
            if tot:
                per[name].append(ok / tot)

    res = {"prompts": n, "note": "graded against REAL human world rankings; no gold model"}
    arrs = {name: np.array(v) for name, v in per.items()}
    print(f"\n{'criterion source':18s} {'accuracy':>9} {'95% CI':>22} {'n':>6}")
    for name, arr in arrs.items():
        bs = np.array([arr[rng.integers(0, len(arr), size=len(arr))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        res[name] = {"accuracy": float(arr.mean()), "ci": [float(lo), float(hi)],
                     "prompts": int(len(arr))}
        print(f"{name:18s} {arr.mean():>9.4f} {f'[{lo:.4f},{hi:.4f}]':>22} {len(arr):>6}")

    # paired contrasts on the same prompts
    m = min(len(arrs[k]) for k in arrs)
    print()
    for lhs, rhs in (("authored", "random"), ("neighbour", "random"), ("authored", "neighbour")):
        d = arrs[lhs][:m] - arrs[rhs][:m]
        bs = np.array([d[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        verdict = "higher" if lo > 0 else "lower" if hi < 0 else "indistinguishable"
        res[f"{lhs}_minus_{rhs}"] = {"delta": float(d.mean()),
                                     "ci": [float(lo), float(hi)], "verdict": verdict}
        print(f"  {lhs:10s} - {rhs:10s} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  {verdict}")

    tr = res["neighbour_minus_random"]
    au = res["authored_minus_random"]
    if tr["verdict"] == "higher":
        concl = ("TRANSFERS IN DISTRIBUTION: criteria never written against these "
                 "responses still beat an unrelated rubric, so r12's failure was "
                 "out-of-distribution generation and the transfer-boundary claim "
                 "shrinks to a statement about my generator.")
    elif au["verdict"] == "higher":
        concl = ("BOUND IS REAL: only criteria authored against these very responses "
                 "beat the floor. Topically matched criteria do not transfer, so the "
                 "boundary is a property of rubric-graded evaluation, not of the "
                 "generator used in r12.")
    else:
        concl = ("UNRESOLVED: neither authored nor neighbour criteria beat the floor "
                 "on this subset; the instrument is not resolving anything here and "
                 "no transfer claim is established.")
    res["conclusion"] = concl
    print(f"\n  -> {concl}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
