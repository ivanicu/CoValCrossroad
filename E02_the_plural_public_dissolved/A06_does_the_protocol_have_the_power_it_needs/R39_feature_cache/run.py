"""r39 (plan item G33) -- One GPU pass. Cache representations of original and fresh responses, analyse nothing.

Why this is the only GPU work that earns its slot
--------------------------------------------------
C33-C36 closed same-sample leakage, forced-choice artifact, and population
dependence as explanations for the polarity channel. C38 showed the human
experiment is frame-limited rather than power-limited. What GPU can still add is
not another sweep: it is a MAP of how far the fresh responses sit from the
released ones, so that r12's inversion can be localised. If the inversion
concentrates where the responses are far out of distribution and the judges
disagree, it looks like measurement failure. If it appears at short distance
with judges agreeing, genuine transport failure becomes the better reading.

Neither conclusion is reachable here. This round computes features and stops.
Everything downstream is CPU (C37), which is the point: one expensive pass, then
the analysis is cheap, repeatable and attackable without re-spending the GPU.

Three lineages, and why exactly three
--------------------------------------
    qwen      Qwen3.5-0.8B-Base                Alibaba
    phi       phi-3.5-mini-instruct            Microsoft
    internlm  internlm2-chat-1.8b              Shanghai AI Lab

Three is the design, not a budget compromise: a distance that agrees across
three unrelated pretraining lineages is a property of the responses, and one that
does not is a property of a representation. A ten-model sweep would add cost
without adding that argument.

Getting to three took a pip install, which is worth recording. llama-3.2-3b on
this box is an empty shell -- LICENSE and README, no weights, the gated download
never completed. internlm2 has weights and appeared broken: its tokenizer raised
`Error parsing line b'\\x0e'`. The real message was one line above --
"SentencePieceExtractor requires the protobuf library but it was not found" --
after which transformers falls back to a TikToken extractor and fails on a
SentencePiece file. Installing protobuf fixed it. That is the THIRD time in this
project a missing dependency in the venv presented as a broken model and silently
removed a family from a cross-family analysis (tiktoken and sentencepiece were
the first two, and phi's exclusion from r22 was a tokenizer bug of my own).
A model that "fails to load" is a claim about the environment until proven
otherwise.

What is cached, per response, per backbone
-------------------------------------------
    mean_last     mean-pooled final hidden layer      global semantics
    final_tok     last-token final hidden state       what a causal head reads
    mean_mid      mean-pooled middle layer            pre-readout representation
    ll_resp       mean token log-prob of the response alone
    ll_cond       mean token log-prob of the response GIVEN the prompt

The two likelihoods are the cheapest OOD signal there is and they measure a
different thing from the hidden states: a response can be representationally
ordinary and still be improbable under a given model.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
ART = "/home/ivan/research/causal-publication-protocol/artifacts"

BACKBONES = {
    "qwen": (os.environ.get("COVALX_MODEL_08B",
             "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
             "Qwen3.5-0.8B-Base"), "qwen"),
    "phi": (f"{ART}/model_phi-3.5-mini-instruct", "phi"),
    "internlm": (f"{ART}/model_internlm2-chat-1.8b", "internlm"),
}


@torch.inference_mode()
def extract(model, tok, prompts, texts, batch, max_len):
    """Returns mean_last, final_tok, mean_mid, ll_resp, ll_cond."""
    ml, ft, mm, lr, lc = [], [], [], [], []
    nlayers = model.config.num_hidden_layers
    mid = nlayers // 2
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        pch = prompts[i:i + batch]
        enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                  max_length=max_len).to("cuda")
        out = model(**enc, output_hidden_states=True)
        h_last, h_mid = out.hidden_states[-1], out.hidden_states[mid]
        m = enc["attention_mask"].unsqueeze(-1).to(h_last.dtype)
        ml.append(((h_last * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
        mm.append(((h_mid * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
        idx = enc["attention_mask"].sum(1) - 1
        ft.append(h_last[torch.arange(len(chunk)), idx].float().cpu().numpy())
        # response-only mean token log-prob
        lg = out.logits[:, :-1].log_softmax(-1)
        tgt = enc["input_ids"][:, 1:]
        tokll = lg.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
        msk = enc["attention_mask"][:, 1:].to(tokll.dtype)
        lr.append(((tokll * msk).sum(1) / msk.sum(1).clamp(min=1)).float().cpu().numpy())
        del out, lg
        # prompt-conditioned: score the response continuation after the prompt
        joined = [f"{p}\n{t}" for p, t in zip(pch, chunk)]
        e2 = tok(joined, return_tensors="pt", padding=True, truncation=True,
                 max_length=max_len).to("cuda")
        plen = [len(tok(p, add_special_tokens=False)["input_ids"]) for p in pch]
        o2 = model(**e2)
        lg2 = o2.logits[:, :-1].log_softmax(-1)
        t2 = e2["input_ids"][:, 1:]
        ll2 = lg2.gather(-1, t2.unsqueeze(-1)).squeeze(-1)
        m2 = e2["attention_mask"][:, 1:].clone().to(ll2.dtype)
        for j, pl in enumerate(plen):
            m2[j, :max(pl - 1, 0)] = 0            # mask the prompt tokens out
        lc.append(((ll2 * m2).sum(1) / m2.sum(1).clamp(min=1)).float().cpu().numpy())
        del o2, lg2
        torch.cuda.empty_cache()
    return (np.concatenate(ml), np.concatenate(ft), np.concatenate(mm),
            np.concatenate(lr), np.concatenate(lc))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--generations", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--out", type=Path, default=_RES / "r39_feature_cache.npz")
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--max-len", type=int, default=512)
    a = p.parse_args()

    if not a.generations.exists():
        raise SystemExit(f"missing {a.generations} -- run r12 first")
    gen = json.loads(a.generations.read_text())
    pids, orig, fresh = gen["prompt_ids"], gen["original"], gen["fresh"]
    n = len(pids)

    # The generations file stores prompt IDS, not prompt TEXT, so the question
    # has to come from the release. The first version appended "" for every
    # prompt, which would have made `ll_cond` -- the prompt-conditioned response
    # likelihood -- condition on nothing at all: a silent duplicate of `ll_resp`,
    # produced by a SECOND forward pass over every response, and then reported
    # by r40 as an independent distance measure. Caught before it spent the GPU
    # rather than after.
    import sys as _sys
    _sys.path.insert(0, str(_ROOT))
    from covalx import load_join  # noqa: E402
    qtext = {}
    for pid, comp, _rub in load_join(_ROOT / "data/comparisons.jsonl",
                                     _ROOT / "data/conversation_rubrics.jsonl"):
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        if q:
            qtext[pid] = q[-1].strip()
    missing = [q for q in pids if q not in qtext]
    if missing:
        raise SystemExit(
            f"REFUSING TO CACHE: {len(missing)} of {len(pids)} prompts have no question "
            "text, so their prompt-conditioned likelihood would silently equal the "
            "unconditioned one. Fix the join before spending GPU.")

    # flatten, keeping (prompt index, set, slot) alignment recoverable
    texts, meta, prompts_for = [], [], []
    for k in range(n):
        for s, block in (("original", orig[k]), ("fresh", fresh[k])):
            for j, t in enumerate(block):
                texts.append(t if t.strip() else " ")
                meta.append(f"{pids[k]}|{s}|{j}")
                prompts_for.append(qtext[pids[k]])
    print(f"prompts {n}   responses {len(texts):,} "
          f"({sum(1 for m in meta if '|original|' in m):,} original, "
          f"{sum(1 for m in meta if '|fresh|' in m):,} fresh)\n")

    store = {"meta": np.array(meta)}
    for name, (path, lineage) in BACKBONES.items():
        if not Path(path).exists():
            print(f"  [{name}] SKIP -- not on disk at {path}")
            continue
        print(f"=== {name} ({lineage}) ===", flush=True)
        # trust_remote_code PER MODEL, not globally. internlm2 needs it; phi does
        # NOT, and forcing it sends phi down a bundled modeling_phi3.py that calls
        # DynamicCache.from_legacy_cache -- removed in transformers 5.14 -- so a
        # model that loads fine natively (as it did in r22, whose loader never set
        # the flag) fails with an AttributeError that reads like a broken model.
        # Native first, remote code only as a fallback.
        model = tok = None
        for remote in (False, True):
            try:
                tok = AutoTokenizer.from_pretrained(path, trust_remote_code=remote)
                if tok.pad_token_id is None:
                    tok.pad_token = tok.eos_token
                model = AutoModelForCausalLM.from_pretrained(
                    path, dtype=torch.bfloat16, device_map="cuda",
                    trust_remote_code=remote).eval()
                model.config.use_cache = False      # no cache needed for features
                print(f"  loaded with trust_remote_code={remote}")
                break
            except Exception as e:
                last = e
                model = None
                torch.cuda.empty_cache()
        try:
            if model is None:
                raise last
        except Exception as e:
            # A load failure is a claim about the ENVIRONMENT until proven
            # otherwise. Three of them in this project were missing pip packages.
            print(f"  FAILED TO LOAD: {type(e).__name__}: {str(e)[:150]}")
            print("  -> recorded as a load failure, NOT as a property of this model.")
            store[f"{name}|load_failed"] = np.array([str(e)[:300]])
            continue
        # Hidden states for ALL layers are materialised, and each response gets
        # two forward passes. Scale the batch down for the larger backbones
        # rather than discovering the ceiling by dying halfway through.
        nparam = sum(x.numel() for x in model.parameters())
        b = a.batch if nparam < 2.5e9 else max(2, a.batch // 4)
        print(f"  {nparam/1e9:.1f}B params -> batch {b}", flush=True)
        ml, ft, mm, lr, lc = extract(model, tok, prompts_for, texts, b, a.max_len)
        store[f"{name}|mean_last"] = ml.astype(np.float16)
        store[f"{name}|final_tok"] = ft.astype(np.float16)
        store[f"{name}|mean_mid"] = mm.astype(np.float16)
        store[f"{name}|ll_resp"] = lr.astype(np.float32)
        store[f"{name}|ll_cond"] = lc.astype(np.float32)
        # POSITIVE CONTROL on the second forward pass. If conditioning on the
        # question changes nothing, the pass was wasted and the feature is a
        # duplicate wearing a different name. Correlation near 1.0 is the
        # signature of exactly the bug fixed above.
        rr = float(np.corrcoef(lr, lc)[0, 1])
        flag = "  <- SUSPICIOUS: conditioning changed almost nothing" if rr > 0.995 else ""
        print(f"  cached {ml.shape} mean_last, dim {ml.shape[1]}")
        print(f"  ll_resp {lr.mean():+.3f}   ll_cond {lc.mean():+.3f}   "
              f"corr {rr:+.4f}{flag}")
        store[f"{name}|ll_corr"] = np.array([rr])
        del model
        torch.cuda.empty_cache()

    got = sorted({k.split("|")[0] for k in store if "|" in k and k != "meta"
                  and not k.endswith("load_failed")})
    _RES.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **store)
    mb = a.out.stat().st_size / 1e6
    print(f"\n  lineages cached: {got}  ({len(got)}/3)")
    if len(got) < 3:
        print("  ⚠ FEWER THAN THREE LINEAGES. The cross-lineage argument -- that a "
              "distance\n    agreeing across unrelated pretraining runs is a property of "
              "the responses --\n    is weakened accordingly, and C37 must say so rather "
              "than report the mean.")
    print(f"  wrote {a.out}  ({mb:.1f} MB)")
    print("\n  This round analyses nothing by design. C37 does the OOD map on CPU.")


if __name__ == "__main__":
    main()
