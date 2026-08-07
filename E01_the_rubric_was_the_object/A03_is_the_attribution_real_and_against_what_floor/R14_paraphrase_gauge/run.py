"""r14 -- Paraphrase gauge test on the satisfaction judge.

Symmetry group: semantic-preserving rewording of a criterion.
Property invariant under it: yes. Measurement invariant: to be determined.

Two paraphrase families, deliberately different in kind:

  MECHANICAL  auditable, no model in the loop: clause reordering, article and
              modal substitution, active/passive-ish rewrites. Weak paraphrases,
              but nobody can argue the meaning moved.
  MODEL       the local base model rewrites the criterion; kept only when its
              embedding similarity to the original clears a threshold, so a
              paraphrase that drifted in meaning cannot be counted as a
              measurement failure.

The fidelity filter matters: without it, a low invariance score is ambiguous
between "the judge is lexical" and "my paraphrases changed the meaning".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, Judge, build_prompt, human_pairs, load_join  # noqa: E402

MODEL = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")

SUBS = [
    (r"\bmust not\b", "should never"), (r"\bmust\b", "has to"),
    (r"\bshould\b", "ought to"), (r"\bavoid\b", "refrain from"),
    (r"\bprovide\b", "give"), (r"\binclude\b", "contain"),
    (r"\bmention\b", "refer to"), (r"\bclearly\b", "plainly"),
    (r"\bthe user\b", "the reader"), (r"\bresponse\b", "reply"),
    (r"\bexplain\b", "set out"), (r"\backnowledge\b", "recognise"),
]


def mechanical(c: str) -> str:
    out = c
    for pat, rep in SUBS:
        out = re.sub(pat, rep, out, flags=re.I)
    # move a trailing subordinate clause to the front, if there is one
    m = re.match(r"^(.*?),\s*(when|if|while|unless|because)\s+(.*)$", out, flags=re.I)
    if m:
        out = f"{m.group(2).capitalize()} {m.group(3).rstrip('.')}, {m.group(1)}"
    return out


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
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r14_paraphrase_gauge.json")
    ap.add_argument("--prompts", type=int, default=200)
    ap.add_argument("--fidelity", type=float, default=0.80)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items = []
    for pid, comp, rub in joined:
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        hp = human_pairs(comp["metadata"]["assessments"])
        if cr and hp:
            items.append({"pid": pid, "crits": cr, "pairs": hp,
                          "resp": {r["response_index"]: r["messages"][0]["content"]
                                   for r in comp["responses"]}})
    print(f"prompts: {len(items)}")

    flat = [(k, ci, c) for k, it in enumerate(items) for ci, c in enumerate(it["crits"])]
    print(f"criteria: {len(flat)}")

    # ---- build the two paraphrase families -------------------------
    mech = [mechanical(c) for _, _, c in flat]
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    gm = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16,
                                              device_map="cuda").eval()
    model_par = []
    with torch.inference_mode():
        prompts = [FEWSHOT + f"Criterion: {c.strip()}\nRewrite:" for _, _, c in flat]
        for i in range(0, len(prompts), 24):
            enc = tok(prompts[i:i+24], return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            o = gm.generate(**enc, do_sample=False, max_new_tokens=60,
                            pad_token_id=tok.pad_token_id)
            for j in range(len(enc["input_ids"])):
                t = tok.decode(o[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                model_par.append(t.split("Criterion:")[0].strip().split("\n")[0].strip())
            if (i // 24) % 10 == 0:
                print(f"  paraphrase {i}/{len(prompts)}", flush=True)
    del gm
    torch.cuda.empty_cache()

    # ---- fidelity filter: a drifted paraphrase is not a judge failure
    em = AutoModel.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda").eval()

    @torch.inference_mode()
    def emb(ts):
        out = []
        for i in range(0, len(ts), 32):
            enc = tok(list(ts[i:i+32]), return_tensors="pt", padding=True,
                      truncation=True, max_length=128).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h*m).sum(1)/m.sum(1).clamp(min=1)).float().cpu().numpy())
        E = np.concatenate(out, 0)
        return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

    orig_t = [c for _, _, c in flat]
    Eo, Em, Ep = emb(orig_t), emb(mech), emb(model_par)
    fid_m = (Eo * Em).sum(1)
    fid_p = (Eo * Ep).sum(1)
    del em
    torch.cuda.empty_cache()
    keep_m = fid_m >= a.fidelity
    keep_p = fid_p >= a.fidelity
    print(f"  fidelity>={a.fidelity}: mechanical {keep_m.mean():.1%}, model {keep_p.mean():.1%}")

    # ---- score all three criterion sets on the same responses -------
    judge = Judge(MODEL, batch=32)
    variants = {"original": orig_t, "mechanical": mech, "model": model_par}
    sat = {}
    for name, texts in variants.items():
        tasks, meta = [], []
        for (k, ci, _), ctext in zip(flat, texts):
            for lab in items[k]["resp"]:
                tasks.append(build_prompt(ctext, items[k]["resp"][lab]))
                meta.append((k, ci, lab))
        print(f"  [{name}] judgements: {len(tasks):,}", flush=True)
        s = judge.score(tasks)
        d = {}
        for mt, v in zip(meta, s):
            d[mt] = float(v)
        sat[name] = d
    del judge
    torch.cuda.empty_cache()

    # ---- invariance of the MEASUREMENT ------------------------------
    res = {"prompts": len(items), "criteria": len(flat),
           "fidelity_threshold": a.fidelity,
           "fidelity_kept": {"mechanical": float(keep_m.mean()),
                             "model": float(keep_p.mean())}}
    for name, keep in (("mechanical", keep_m), ("model", keep_p)):
        pairs_o, pairs_v = [], []
        for idx, (k, ci, _) in enumerate(flat):
            if not keep[idx]:
                continue
            for lab in items[k]["resp"]:
                pairs_o.append(sat["original"][(k, ci, lab)])
                pairs_v.append(sat[name][(k, ci, lab)])
        o, v = np.array(pairs_o), np.array(pairs_v)
        r = float(np.corrcoef(o, v)[0, 1])
        mad = float(np.mean(np.abs(o - v)))
        flip = float(np.mean((o > 0.5) != (v > 0.5)))
        res[name] = {"n_cells": int(len(o)), "pearson_r": r,
                     "mean_abs_shift": mad, "sign_flip_rate": flip}
        print(f"\n  {name:11s} r={r:+.4f}  mean|Δ|={mad:.4f}  "
              f"Yes/No flip rate={flip:.1%}  (n={len(o):,})")

    worst = min(res["mechanical"]["pearson_r"], res["model"]["pearson_r"])
    invariant = worst > 0.90 and max(res["mechanical"]["sign_flip_rate"],
                                     res["model"]["sign_flip_rate"]) < 0.10
    res["measurement_is_paraphrase_invariant"] = bool(invariant)
    print(f"\n  -> measurement is {'INVARIANT' if invariant else 'NOT INVARIANT'} under paraphrase")
    if not invariant:
        print("     W_C stands: attribution partly measures criterion WORDING, so "
              "'prompt-specific criterion content' overstates what is being measured.")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
