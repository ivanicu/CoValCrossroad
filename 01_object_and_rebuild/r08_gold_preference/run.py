"""A08 -- A gold preference model that never sees the rubric.

The overoptimization experiment needs two scores per response:

  PROXY  the rubric score        (what a model would be optimized against)
  GOLD   what humans actually prefer

Without a gold side there is no curve, only a proxy going up -- which proves
nothing. The release gives 18,384 real human rankings, so gold can be learned
from humans rather than asserted.

Construction
------------
* Represent each response by a mean-pooled hidden state from the local model.
* Learn a linear preference head by logistic regression on WITHIN-PROMPT pairs:
      P(x beaten y) = sigmoid( w . (emb_x - emb_y) )
* Split by PROMPT, never by pair, so no response and no prompt appears in both
  train and test.

Why this is not circular
------------------------
The gold head sees only response text and human labels. It never sees a
criterion. The proxy sees only criteria. They share no features, so a response
that scores high on the proxy has no mechanical reason to score high on gold.

Honest limit (states itself in the output)
------------------------------------------
A learned gold model is not fresh humans. It inherits whatever the 18,384
rankings encode, including the label-bias and two-regime problems found in A02.
It is the standard construction in the overoptimization literature and carries
the standard caveat: it can be fooled too, just not in the same way as the proxy.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

OUTCOME_SCOPE = (
    "This round FITS the gold head that later rounds use as an outcome. It is a M"
    "ODEL PROXY for preference, trained on released human rankings, and its featu"
    "re vector includes response length explicitly (hstack([embedding, [char_len,"
    " word_len]]) @ w). r47 measured what that costs: the head's within-prompt co"
    "rrelation with length rises from ~+0.05 on released candidates to ~+0.50 on "
    "generated ones. Any round scoring generated responses against this head inhe"
    "rits that channel."
)

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")

MODEL_DIR = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")
LABELS = ("A", "B", "C", "D")


def parse_ranking(s: str) -> list[list[str]]:
    out = []
    for grp in str(s).split(">"):
        m = [t.strip() for t in grp.split("=") if t.strip() in LABELS]
        if m:
            out.append(m)
    return out


@torch.inference_mode()
def embed(texts: list[str], batch: int = 16, max_len: int = 512,
          model_dir: str = MODEL_DIR) -> np.ndarray:
    tok = AutoTokenizer.from_pretrained(model_dir)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModel.from_pretrained(model_dir, dtype=torch.bfloat16, device_map="cuda").eval()
    outs = []
    for i in range(0, len(texts), batch):
        enc = tok(texts[i : i + batch], return_tensors="pt", padding=True,
                  truncation=True, max_length=max_len).to("cuda")
        h = model(**enc).last_hidden_state
        mask = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
        pooled = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        outs.append(pooled.float().cpu().numpy())
        if (i // batch) % 20 == 0:
            print(f"  embed {i}/{len(texts)}", flush=True)
    return np.concatenate(outs, 0)


def fit_logistic(D: np.ndarray, y: np.ndarray, l2: float = 1.0,
                 iters: int = 300, lr: float = 0.5) -> np.ndarray:
    """Logistic regression on difference vectors, no intercept (antisymmetric)."""
    w = np.zeros(D.shape[1])
    n = len(y)
    for t in range(iters):
        z = D @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        g = D.T @ (p - y) / n + l2 * w / n
        h = 1.0 / (1.0 + t / 40.0)
        w -= lr * h * g * D.shape[1] ** 0.5
    return w


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a08_gold.json"))
    ap.add_argument("--weights", type=Path, default=Path(_RES + "/a08_gold.npz"))
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--l2", type=float, default=3.0)
    ap.add_argument("--model", type=str, default=MODEL_DIR)
    a = ap.parse_args()

    texts, index, pairs = [], {}, []
    for line in open(a.comparisons, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        for r in rec["responses"]:
            index[(pid, r["response_index"])] = len(texts)
            texts.append(r["messages"][0]["content"])
        for asm in rec["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            rk = parse_ranking(w[0].get("ranking", ""))
            flat = [(lab, gi) for gi, grp in enumerate(rk) for lab in grp]
            for x, gx in flat:
                for y, gy in flat:
                    if gx < gy:
                        pairs.append((pid, x, y))
    print(f"responses: {len(texts):,}   human strict pairs: {len(pairs):,}")

    cache = a.weights.with_suffix(".emb.npz")
    if cache.exists():
        E = np.load(cache)["E"]
        print(f"embeddings from cache: {E.shape}")
    else:
        E = embed(texts, model_dir=a.model)
        np.savez_compressed(cache, E=E)
    print(f"embedding matrix: {E.shape}")
    E = (E - E.mean(0)) / (E.std(0) + 1e-6)
    length = np.array([[len(t), len(t.split())] for t in texts], dtype=float)
    length = (length - length.mean(0)) / (length.std(0) + 1e-6)
    F = np.hstack([E, length])

    prompts = sorted({p for p, _, _ in pairs})
    rng = np.random.default_rng(20260727)
    order = rng.permutation(len(prompts))
    fold_of = {prompts[order[i]]: i % a.folds for i in range(len(prompts))}

    accs, len_accs = [], []
    for f in range(a.folds):
        tr = [(p, x, y) for p, x, y in pairs if fold_of[p] != f]
        te = [(p, x, y) for p, x, y in pairs if fold_of[p] == f]
        Dtr = np.array([F[index[(p, x)]] - F[index[(p, y)]] for p, x, y in tr])
        ytr = np.ones(len(tr))
        # antisymmetric augmentation
        Dtr = np.vstack([Dtr, -Dtr])
        ytr = np.concatenate([ytr, np.zeros(len(tr))])
        from sklearn.linear_model import LogisticRegression
        clf = LogisticRegression(C=1.0 / a.l2, fit_intercept=False, max_iter=2000)
        clf.fit(Dtr, ytr)
        w = clf.coef_[0]
        Dte = np.array([F[index[(p, x)]] - F[index[(p, y)]] for p, x, y in te])
        acc = float((Dte @ w > 0).mean())
        la = float(np.array([len(texts[index[(p, x)]]) > len(texts[index[(p, y)]])
                             for p, x, y in te]).mean())
        accs.append(acc); len_accs.append(la)
        print(f"  fold {f}: held-out prompts={sum(1 for p in prompts if fold_of[p]==f):4d} "
              f"pairs={len(te):6,}  gold acc={acc:.4f}  (length-only {la:.4f})")

    # final head on everything, for use by A09
    D = np.array([F[index[(p, x)]] - F[index[(p, y)]] for p, x, y in pairs])
    D = np.vstack([D, -D])
    y = np.concatenate([np.ones(len(pairs)), np.zeros(len(pairs))])
    from sklearn.linear_model import LogisticRegression
    w_full = LogisticRegression(C=1.0 / a.l2, fit_intercept=False,
                                max_iter=3000).fit(D, y).coef_[0]

    mean_acc = float(np.mean(accs))
    usable = mean_acc > np.mean(len_accs) + 0.03
    print(f"\n  held-out gold accuracy: {mean_acc:.4f} +- {np.std(accs):.4f}")
    print(f"  length-only baseline  : {np.mean(len_accs):.4f}")
    print(f"  -> gold model {'USABLE' if usable else 'NOT USABLE'} as the gold side of an "
          f"overoptimization curve")

    np.savez_compressed(a.weights, w=w_full, mean=E.mean(0), std=E.std(0))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "responses": len(texts), "pairs": len(pairs), "folds": a.folds,
        "heldout_accuracy": mean_acc, "heldout_sd": float(np.std(accs)),
        "per_fold": accs, "length_baseline": float(np.mean(len_accs)),
        "usable": bool(usable),
        "caveat": "learned gold, not fresh humans; inherits label bias and the "
                  "two-regime split found in A02",
    }, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
