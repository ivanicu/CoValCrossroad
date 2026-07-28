"""A12 -- Is the rubric's advantage about VALUES, or about these four responses?

The threat to A04's headline
----------------------------
Participants wrote their criteria AFTER seeing the four candidate responses.
So a criterion like "must not contain factual errors" may have been written
because response B contained one. Such a criterion predicts B's low rank
perfectly -- while encoding a fact about this response set, not a value.

If most of the 7.9-point "prompt-specific" contribution is that, then the
value-carrying share of a values rubric is near zero and A04's headline needs
a large downward revision.

Design
------
Measure the SAME attribution on two response sets with the same metric:

  ORIGINAL  the four released candidates, which the criteria authors saw
  FRESH     newly generated responses the criteria could not have been
            written in view of, generated WITHOUT showing the rubric

Human labels do not exist for FRESH, so both sets are scored against the same
independent yardstick: the 0.8B gold preference head (different backbone from
the judge, held-out accuracy 0.661).

  attribution(set) = agreement(real rubric, gold order)
                   - agreement(shuffled rubric, gold order)

  attribution(ORIGINAL) >> attribution(FRESH)  -> response-set-specific, headline shrinks
  attribution(ORIGINAL) ~= attribution(FRESH)  -> genuinely prompt/value-specific, headline stands

Generation is deliberately rubric-BLIND. Showing the rubric would make the real
rubric win by construction, which is the mistake this file exists to avoid.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from covalx import MODEL_DIR, Judge, build_prompt, load_join  # noqa: E402

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")

M08 = os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base")
LABELS = ("A", "B", "C", "D")

FEWSHOT = (
    "Answer the user's question helpfully and directly.\n\n"
    "Question: What is a good way to start running?\n"
    "Answer: Start with short sessions of about twenty minutes, three times a week, "
    "and alternate walking and jogging until you can run continuously.\n\n"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    ap.add_argument("--gold", type=Path, default=Path(_ROOT) / "rounds" / "r08_gold_preference" / "results" / "a08_gold_08b.npz")
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a12_response_set.json"))
    ap.add_argument("--prompts", type=int, default=250)
    ap.add_argument("--fresh", type=int, default=4)
    ap.add_argument("--max-new", type=int, default=180)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items = []
    for pid, comp, rub in joined:
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if q and cr:
            items.append({"pid": pid, "q": q[-1], "crits": cr,
                          "orig": [r["messages"][0]["content"] for r in comp["responses"]]})
    n = len(items)
    print(f"prompts: {n}")

    rng = np.random.default_rng(20260727)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    # ---- generate rubric-BLIND fresh responses ------------------------
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    gm = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16,
                                              device_map="cuda").eval()
    prompts = [FEWSHOT + f"Question: {it['q'].strip()}\nAnswer:" for it in items
               for _ in range(a.fresh)]
    fresh = []
    with torch.inference_mode():
        for i in range(0, len(prompts), 16):
            enc = tok(prompts[i:i+16], return_tensors="pt", padding=True,
                      truncation=True, max_length=640).to("cuda")
            o = gm.generate(**enc, do_sample=True, temperature=0.9, top_p=0.95,
                            max_new_tokens=a.max_new, pad_token_id=tok.pad_token_id)
            for j in range(len(enc["input_ids"])):
                t = tok.decode(o[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                fresh.append(t.split("Question:")[0].strip())
            if (i // 16) % 10 == 0:
                print(f"  gen {i}/{len(prompts)}", flush=True)
    del gm
    torch.cuda.empty_cache()
    print(f"fresh responses (rubric-blind): {len(fresh)}")

    # ---- judge both sets under real and shuffled rubrics --------------
    judge = Judge(MODEL_DIR, batch=32)

    def score_set(texts_of, n_resp, which):
        tasks, meta = [], []
        for k, it in enumerate(items):
            for kind, src in (("real", k), ("shuf", donor[k])):
                for ci, c in enumerate(items[src]["crits"]):
                    for r in range(n_resp):
                        tasks.append(build_prompt(c, texts_of(k, r)))
                        meta.append((kind, k, ci, r))
        print(f"  [{which}] judgements: {len(tasks):,}", flush=True)
        sat = judge.score(tasks)
        acc = {"real": np.zeros((n, n_resp)), "shuf": np.zeros((n, n_resp))}
        cnt = {"real": np.zeros((n, n_resp)), "shuf": np.zeros((n, n_resp))}
        for (kind, k, ci, r), s in zip(meta, sat):
            acc[kind][k, r] += float(s); cnt[kind][k, r] += 1
        return {kd: acc[kd] / np.maximum(cnt[kd], 1) for kd in acc}

    s_orig = score_set(lambda k, r: items[k]["orig"][r], 4, "ORIGINAL")
    s_fresh = score_set(lambda k, r: fresh[k * a.fresh + r], a.fresh, "FRESH")
    del judge
    torch.cuda.empty_cache()

    # ---- independent yardstick: 0.8B gold ----------------------------
    g = np.load(a.gold)
    w, mu, sd = g["w"], g["mean"], g["std"]
    em = AutoModel.from_pretrained(M08, dtype=torch.bfloat16, device_map="cuda").eval()
    tk8 = AutoTokenizer.from_pretrained(M08)
    if tk8.pad_token_id is None:
        tk8.pad_token = tk8.eos_token

    @torch.inference_mode()
    def gold(ts):
        out = []
        for i in range(0, len(ts), 16):
            enc = tk8(list(ts[i:i+16]), return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h*m).sum(1)/m.sum(1).clamp(min=1)).float().cpu().numpy())
        E = (np.concatenate(out, 0) - mu) / (sd + 1e-6)
        L = np.array([[len(t), len(t.split())] for t in ts], dtype=float)
        L = (L - L.mean(0)) / (L.std(0) + 1e-6)
        return np.hstack([E, L]) @ w

    g_orig = gold([t for it in items for t in it["orig"]]).reshape(n, 4)
    g_fresh = gold(fresh).reshape(n, a.fresh)
    del em
    torch.cuda.empty_cache()

    def agreement(sc, gd, n_resp):
        per = []
        for k in range(n):
            ok = tot = 0
            for x, y in combinations(range(n_resp), 2):
                if gd[k, x] == gd[k, y]:
                    continue
                tot += 1
                ok += int((sc[k, x] > sc[k, y]) == (gd[k, x] > gd[k, y]))
            if tot:
                per.append(ok / tot)
        return np.array(per)

    res = {}
    for name, sc, gd, nr in (("ORIGINAL", s_orig, g_orig, 4),
                             ("FRESH", s_fresh, g_fresh, a.fresh)):
        ar = agreement(sc["real"], gd, nr)
        ash = agreement(sc["shuf"], gd, nr)
        d = ar - ash
        bs = np.array([d[rng.integers(0, len(d), size=len(d))].mean() for _ in range(4000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        res[name] = {"real": float(ar.mean()), "shuffled": float(ash.mean()),
                     "attribution": float(d.mean()), "ci": [float(lo), float(hi)],
                     "prompts": int(len(d))}
        print(f"\n  {name:9s} real={ar.mean():.4f}  shuffled={ash.mean():.4f}  "
              f"attribution={d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]")

    dd = res["ORIGINAL"]["attribution"] - res["FRESH"]["attribution"]
    share = 1 - (res["FRESH"]["attribution"] / res["ORIGINAL"]["attribution"]) \
        if res["ORIGINAL"]["attribution"] > 1e-9 else float("nan")
    print(f"\n  drop from ORIGINAL to FRESH: {dd:+.4f}  "
          f"({share:.1%} of the advantage does not transfer to unseen responses)")
    verdict = ("RESPONSE-SET-SPECIFIC: most of the advantage does not transfer; the "
               "value-carrying share of A04's headline shrinks"
               if share > 0.5 else
               "TRANSFERS: the advantage survives on responses the authors never saw, "
               "so it is prompt/value-specific rather than response-set-specific"
               if res["FRESH"]["ci"][0] > 0 else
               "UNRESOLVED: attribution on fresh responses is not distinguishable "
               "from zero, so neither reading is established")
    print(f"  -> {verdict}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"prompts": n, "fresh_per_prompt": a.fresh,
                                 "sets": res, "drop": float(dd),
                                 "non_transferring_share": float(share),
                                 "verdict": verdict}, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
