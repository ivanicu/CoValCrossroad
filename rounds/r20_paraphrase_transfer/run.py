"""r20 -- Does the own-prompt advantage survive rewording its criteria?

r15: own criteria beat the floor by +0.073; nearest-topic criteria do not.
r14: the judge flips 15.4% of verdicts under faithful paraphrase.

Deflationary reading both allow: the advantage is lexical coupling. A criterion
written for prompt P carries P's vocabulary, P's responses were generated from P,
and a near-topic prompt has the topic without the wording.

So paraphrase the prompt's own criteria and re-grade its own responses against the
same real human rankings. Four arms on identical responses:

    original    the prompt's own criteria
    paraphrased same criteria, reworded, fidelity-filtered
    neighbour   nearest-topic prompt's criteria      (r15's null)
    random      a random other prompt's criteria     (the floor)

If paraphrase costs most of the advantage, the attribution reported throughout this
repository is substantially a vocabulary measurement.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, Judge, build_prompt, human_pairs, load_join  # noqa: E402

MODEL = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")

FEWSHOT = (
    "Rewrite each evaluation criterion in different words, keeping the meaning identical.\n\n"
    "Criterion: The reply must cite a source for any statistic.\n"
    "Rewrite: Any figure quoted in the answer needs an attributed source.\n\n"
    "Criterion: Avoid telling the user what to decide.\n"
    "Rewrite: Do not instruct the reader on which choice to make.\n\n"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r20_paraphrase_transfer.json")
    ap.add_argument("--prompts", type=int, default=300)
    ap.add_argument("--fidelity", type=float, default=0.80)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items = []
    for pid, comp, rub in joined:
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        hp = human_pairs(comp["metadata"]["assessments"])
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        if cr and hp and q:
            items.append({"crits": cr, "pairs": hp, "q": q[-1],
                          "resp": {r["response_index"]: r["messages"][0]["content"]
                                   for r in comp["responses"]}})
    n = len(items)
    print(f"prompts: {n}")

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"

    # ---- paraphrase every prompt's own criteria ----------------------
    flat = [(k, ci, c) for k, it in enumerate(items) for ci, c in enumerate(it["crits"])]
    gm = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16,
                                              device_map="cuda").eval()
    para = []
    with torch.inference_mode():
        prompts = [FEWSHOT + f"Criterion: {c.strip()}\nRewrite:" for _, _, c in flat]
        for i in range(0, len(prompts), 24):
            enc = tok(prompts[i:i+24], return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            o = gm.generate(**enc, do_sample=False, max_new_tokens=60,
                            pad_token_id=tok.pad_token_id)
            for j in range(len(enc["input_ids"])):
                t = tok.decode(o[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                para.append(t.split("Criterion:")[0].strip().split("\n")[0].strip())
            if (i // 24) % 15 == 0:
                print(f"  paraphrase {i}/{len(prompts)}", flush=True)
    del gm
    torch.cuda.empty_cache()

    # ---- fidelity filter + prompt embeddings for the neighbour arm ---
    em = AutoModel.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda").eval()

    @torch.inference_mode()
    def emb(ts, maxlen=256):
        out = []
        for i in range(0, len(ts), 32):
            enc = tok(list(ts[i:i+32]), return_tensors="pt", padding=True,
                      truncation=True, max_length=maxlen).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h*m).sum(1)/m.sum(1).clamp(min=1)).float().cpu().numpy())
        E = np.concatenate(out, 0)
        return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

    Eo, Ep = emb([c for _, _, c in flat], 128), emb(para, 128)
    fid = (Eo * Ep).sum(1)
    keep = fid >= a.fidelity
    print(f"  paraphrase fidelity >= {a.fidelity}: {keep.mean():.1%}")
    Eq = emb([it["q"] for it in items])
    S = Eq @ Eq.T
    np.fill_diagonal(S, -np.inf)
    near = S.argmax(1)
    del em
    torch.cuda.empty_cache()

    rng = np.random.default_rng(20260727)
    rand = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    # a prompt enters only if ALL its criteria produced faithful paraphrases,
    # so the paraphrased arm is never a mixture of reworded and original text
    ok_prompt = np.ones(n, dtype=bool)
    para_of = {k: list(it["crits"]) for k, it in enumerate(items)}
    for idx, (k, ci, _) in enumerate(flat):
        if keep[idx]:
            para_of[k][ci] = para[idx]
        else:
            ok_prompt[k] = False
    print(f"  prompts with every criterion faithfully reworded: {ok_prompt.sum()}/{n}")

    # ---- grade four arms on identical responses ----------------------
    judge = Judge(MODEL, batch=32)
    arms = {"original": lambda k: items[k]["crits"],
            "paraphrased": lambda k: para_of[k],
            "neighbour": lambda k: items[near[k]]["crits"],
            "random": lambda k: items[rand[k]]["crits"]}
    tasks, meta = [], []
    for name, get in arms.items():
        for k in range(n):
            if not ok_prompt[k]:
                continue
            for ci, c in enumerate(get(k)):
                for lab in items[k]["resp"]:
                    tasks.append(build_prompt(c, items[k]["resp"][lab]))
                    meta.append((name, k, ci, lab))
    print(f"  judgements: {len(tasks):,}", flush=True)
    sat = judge.score(tasks)
    del judge
    torch.cuda.empty_cache()

    acc = {}
    for (name, k, ci, lab), s in zip(meta, sat):
        acc.setdefault((name, k), {}).setdefault(lab, []).append(float(s))

    per = {name: [] for name in arms}
    order = [k for k in range(n) if ok_prompt[k]]
    for name in arms:
        for k in order:
            d = acc.get((name, k))
            if not d:
                per[name].append(np.nan); continue
            score = {lab: float(np.mean(v)) for lab, v in d.items()}
            ok = tot = 0
            for x, y in items[k]["pairs"]:
                if x in score and y in score:
                    tot += 1; ok += int(score[x] > score[y])
            per[name].append(ok / tot if tot else np.nan)
    arr = {nm: np.array(v) for nm, v in per.items()}
    good = ~np.isnan(np.vstack(list(arr.values()))).any(axis=0)
    arr = {nm: v[good] for nm, v in arr.items()}
    m = len(next(iter(arr.values())))
    print(f"\n  prompts scored in all four arms: {m}")

    res = {"prompts": m, "fidelity_threshold": a.fidelity,
           "paraphrase_kept": float(keep.mean())}
    print(f"\n{'arm':14s} {'accuracy':>9} {'95% CI':>22}")
    for nm, v in arr.items():
        bs = np.array([v[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        res[nm] = {"accuracy": float(v.mean()), "ci": [float(lo), float(hi)]}
        print(f"{nm:14s} {v.mean():>9.4f} {f'[{lo:.4f},{hi:.4f}]':>22}")

    print()
    for lhs, rhs in (("original", "random"), ("paraphrased", "random"),
                     ("original", "paraphrased"), ("neighbour", "random")):
        d = arr[lhs] - arr[rhs]
        bs = np.array([d[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        v = "higher" if lo > 0 else "lower" if hi < 0 else "indistinguishable"
        res[f"{lhs}_minus_{rhs}"] = {"delta": float(d.mean()), "ci": [float(lo), float(hi)],
                                     "verdict": v}
        print(f"  {lhs:12s} - {rhs:12s} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  {v}")

    a_orig = res["original_minus_random"]["delta"]
    a_para = res["paraphrased_minus_random"]["delta"]
    retained = a_para / a_orig if abs(a_orig) > 1e-9 else float("nan")
    res["advantage_retained_under_paraphrase"] = float(retained)
    print(f"\n  advantage retained under paraphrase: {retained:.1%}")
    if res["paraphrased_minus_random"]["verdict"] != "higher":
        concl = ("LEXICAL: the own-prompt advantage does not survive rewording the "
                 "criteria, so the attribution reported throughout this repository "
                 "is substantially a vocabulary measurement and every headline needs "
                 "restating in those terms.")
    elif retained > 0.7:
        concl = ("CONTENT: the advantage survives rewording largely intact, so it is "
                 "not vocabulary overlap and the transfer boundary is real "
                 "specificity.")
    else:
        concl = (f"MIXED: rewording costs {1-retained:.0%} of the advantage but does "
                 "not remove it. Part of what was called prompt-specific criterion "
                 "content is wording, and part is not.")
    res["conclusion"] = concl
    print(f"  -> {concl}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
