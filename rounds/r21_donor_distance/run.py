"""r21 -- Is the "nearest-topic" donor actually topically near?

r15 and r20 both rest on a neighbour arm chosen by cosine in a mean-pooled
Qwen3.5-2B embedding. r15 printed, and I did not look at, `mean cosine to random
prompt: +0.750`. Mean-pooled embeddings are dominated by length and high-frequency
tokens, so two unrelated prompts sitting at 0.75 is exactly what a FLAT space looks
like -- and in a flat space the "near" and "random" arms are the same arm, and the
difference r15 measured between them is uninformative.

POSITIVE CONTROL FIRST. The embedding must separate known-related from
known-unrelated text before any donor distance is read from it. The control here is
a prompt against a paraphrase of itself (known related) versus against a random
other prompt (known unrelated). If that gap is small, the instrument is not a topic
instrument and nothing downstream of it may be interpreted.
"""
from __future__ import annotations

import argparse, json, os, sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import load_join  # noqa: E402

MODEL = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")
FEWSHOT = ("Rewrite each question in different words, keeping the meaning identical.\n\n"
           "Question: Should people stop eating beef?\n"
           "Rewrite: Ought the world to give up beef consumption?\n\n"
           "Question: How do I start running safely?\n"
           "Rewrite: What is a safe way to take up jogging?\n\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r21_donor_distance.json")
    ap.add_argument("--prompts", type=int, default=300)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    qs = []
    for _, comp, _ in joined:
        u = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        if u:
            qs.append(u[-1])
    n = len(qs)
    print(f"prompts: {n}")

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"

    # --- known-related text: paraphrase each prompt ---
    gm = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16,
                                              device_map="cuda").eval()
    para = []
    with torch.inference_mode():
        # ⚠ SCOPE (entry 57 sweep): this 400-character cut is on the GENERATION
        # INPUT, not on a display string. 52 of 968 prompts (5.4%) exceed it,
        # up to 829 characters, so for those the paraphrase -- this round's
        # "known-related" anchor -- is a paraphrase of a FRAGMENT.
        # Direction of the bias: a fragment paraphrase is less similar to the
        # full prompt than a complete one would be, so the known-related anchor
        # is WEAKER for those 52 and the distance scale they calibrate is
        # compressed. That inflates how far "related" looks, which works
        # AGAINST this round finding transfer rather than for it.
        # Left in place rather than silently changed: altering it would change
        # the published numbers, and the honest move is to state the bound.
        pr = [FEWSHOT + f"Question: {q.strip()[:400]}\nRewrite:" for q in qs]
        for i in range(0, len(pr), 24):
            enc = tok(pr[i:i+24], return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            o = gm.generate(**enc, do_sample=False, max_new_tokens=60,
                            pad_token_id=tok.pad_token_id)
            for j in range(len(enc["input_ids"])):
                t = tok.decode(o[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                para.append(t.split("Question:")[0].strip().split("\n")[0].strip())
    del gm; torch.cuda.empty_cache()

    em = AutoModel.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda").eval()

    @torch.inference_mode()
    def emb(ts):
        out = []
        for i in range(0, len(ts), 32):
            enc = tok(list(ts[i:i+32]), return_tensors="pt", padding=True,
                      truncation=True, max_length=256).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h*m).sum(1)/m.sum(1).clamp(min=1)).float().cpu().numpy())
        E = np.concatenate(out, 0)
        return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

    E, P = emb(qs), emb(para)
    del em; torch.cuda.empty_cache()

    self_para = float(np.mean((E * P).sum(1)))
    S = E @ E.T
    np.fill_diagonal(S, -np.inf)
    near = S.max(1)
    off = S[np.isfinite(S)]
    rng = np.random.default_rng(20260727)
    rand_pairs = float(np.mean([S[i, (i + 1 + rng.integers(0, n - 1)) % n] for i in range(n)]))
    far = np.where(np.isfinite(S), S, np.inf).min(1)

    print("\n=== POSITIVE CONTROL: can this embedding tell related from unrelated? ===")
    print(f"  prompt vs its own paraphrase (known related)   {self_para:.4f}")
    print(f"  prompt vs a random other prompt (unrelated)    {rand_pairs:.4f}")
    gap = self_para - rand_pairs
    ok = gap > 0.10
    print(f"  separation {gap:+.4f}  -> instrument {'USABLE' if ok else 'FLAT: not a topic instrument'}")

    print("\n=== where the donors actually sit ===")
    med = float(np.median(off))
    print(f"  nearest-neighbour cosine   mean {near.mean():.4f}  median {np.median(near):.4f}")
    print(f"  random-pair cosine         mean {rand_pairs:.4f}")
    print(f"  all off-diagonal           median {med:.4f}  p99 {np.percentile(off,99):.4f}")
    print(f"  farthest cosine            mean {far.mean():.4f}")
    pct = float(np.mean(off[:, None] < near[None, :].repeat(1, 0).ravel()[:1])) if False else None
    near_pctile = float(np.mean(off < near.mean()) * 100)
    print(f"  the mean NEAR cosine sits at the {near_pctile:.2f}th percentile of all pairs")
    span_near = near.mean() - rand_pairs
    span_para = self_para - rand_pairs
    print(f"\n  near-minus-random  {span_near:+.4f}")
    print(f"  para-minus-random  {span_para:+.4f}   (the ceiling: same question, reworded)")
    frac = span_near / span_para if abs(span_para) > 1e-9 else float("nan")
    print(f"  the NEAR donor covers {frac:.1%} of the distance from random to same-question")

    verdict = ("FLAT SPACE: the embedding does not separate related from unrelated text, "
               "so no donor-distance reading downstream of it is interpretable."
               if not ok else
               "NEAR IS GENUINELY NEARER, BUT ONLY MODESTLY: it covers "
               f"{frac:.0%} of the way from a random prompt to the same question reworded. "
               "r15's neighbour arm is a real contrast, not a duplicate of random, and its "
               "small margin should be read against that modest separation."
               if frac < 0.6 else
               "NEAR IS CLOSE TO THE CEILING: the neighbour arm is nearly a same-topic "
               "restatement, so its failure to transfer is a strong result.")
    print(f"\n  -> {verdict}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts": n, "self_paraphrase_cos": self_para, "random_pair_cos": rand_pairs,
         "nearest_cos_mean": float(near.mean()), "farthest_cos_mean": float(far.mean()),
         "offdiag_median": med, "positive_control_passed": bool(ok),
         "separation": float(gap), "near_fraction_of_ceiling": float(frac),
         "verdict": verdict}, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
