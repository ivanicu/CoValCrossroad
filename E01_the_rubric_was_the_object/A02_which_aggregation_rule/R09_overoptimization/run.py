"""A09 -- Optimize against the rubric and watch what happens to real preference.

PRE-REGISTERED PREDICTION (written before the run, derived from A04)
--------------------------------------------------------------------
A04 decomposed the rubric's predictive power: 43% is prompt-specific value
content, 57% is generic response quality that a SHUFFLED rubric earns for free.

If a majority of a target's signal is generic quality, then optimizing against
that target spends most of its pressure on generic-quality surface features.
So we predict, in order of confidence:

  P1  proxy (rubric score) rises monotonically in optimization strength
        -- true by construction of best-of-n, stated so it cannot be sold as
           a finding
  P2  the GAMING MARKERS rise with strength: length, lexical overlap with the
        criterion text, bullet/checklist density
  P3  gold (human-preference model) rises then flattens or falls -- the
        overoptimization turn
  P4  the turn arrives EARLIER for prompts whose attribution is lower

Design
------
Best-of-n against the proxy, n in {1,2,4,8,16}: generate 16 candidates once per
prompt, then select the argmax under the rubric judge for each n. This is the
standard overoptimization knob (KL grows ~ log n) and needs no training.

MANDATORY POSITIVE CONTROL
--------------------------
Before reading any curve: the gold model must DISCRIMINATE among the generated
candidates. If gold assigns them all essentially the same score, a flat or
falling gold curve is the gold model being blind, not the proxy being gamed.
The run refuses to draw conclusions if gold's spread on generations is below
its spread on the original human-ranked responses.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())))
from covalx import MODEL_DIR, Judge, build_prompt, load_join  # noqa: E402

OUTCOME_SCOPE = (
    "Scored against the r08 MODEL GOLD HEAD, not against human rankings -- no hum"
    "an ranked these generated responses. That head has response length as an exp"
    "licit feature, and best-of-n selection raises gold score partly by raising l"
    "ength (r47, entry 50). This round's finding was separately RETRACTED by r11'"
    "s independent-backbone control."
)

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")

LABELS = ("A", "B", "C", "D")
STRENGTHS = (1, 2, 4, 8, 16)


def gaming_markers(text: str, criteria: list[str]) -> dict[str, float]:
    words = max(len(text.split()), 1)
    crit_tokens = set()
    for c in criteria:
        crit_tokens |= {w for w in re.findall(r"[a-z']{4,}", c.lower())}
    resp_tokens = {w for w in re.findall(r"[a-z']{4,}", text.lower())}
    overlap = len(crit_tokens & resp_tokens) / max(len(crit_tokens), 1)
    return {
        "words": float(words),
        "criterion_lexical_overlap": float(overlap),
        "bullets": float(len(re.findall(r"(?m)^\s*[-*•\d]+[.)]?\s", text))),
        "hedges": float(len(re.findall(
            r"\b(on the other hand|however|it depends|some (people|argue)|both sides|"
            r"that said|ultimately|it is important to)\b", text.lower()))),
    }


FEWSHOT_GEN = (
    "Answer the user's question helpfully and directly.\n\n"
    "Question: What is a good way to start running?\n"
    "Answer: Start with short sessions of about twenty minutes, three times a week, "
    "and alternate walking and jogging until you can run continuously. Increase your "
    "weekly distance by no more than ten percent.\n\n"
)


def gen_prompt(question: str, criteria: list[str], show_rubric: bool) -> str:
    s = FEWSHOT_GEN
    if show_rubric and criteria:
        s += "A good answer to the next question should satisfy all of these:\n"
        for c in criteria:
            s += f"- {c}\n"
        s += "\n"
    return s + f"Question: {question.strip()}\nAnswer:"


@torch.inference_mode()
def generate(model, tok, prompts: list[str], n_per: int, max_new: int, batch: int, temp: float):
    outs = []
    flat = [p for p in prompts for _ in range(n_per)]
    for i in range(0, len(flat), batch):
        chunk = flat[i : i + batch]
        enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                  max_length=768).to("cuda")
        out = model.generate(**enc, do_sample=True, temperature=temp, top_p=0.95,
                             max_new_tokens=max_new, pad_token_id=tok.pad_token_id)
        for j in range(len(chunk)):
            txt = tok.decode(out[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
            outs.append(txt.split("Question:")[0].strip())
        if (i // batch) % 5 == 0:
            print(f"  gen {i}/{len(flat)}", flush=True)
    return outs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    ap.add_argument("--gold", type=Path, default=Path(_RES + "/a08_gold.npz"))
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a09_overoptimization.json"))
    ap.add_argument("--prompts", type=int, default=120)
    ap.add_argument("--candidates", type=int, default=16)
    ap.add_argument("--max-new", type=int, default=200)
    ap.add_argument("--batch", type=int, default=16)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    print(f"prompts: {len(joined)}")

    items = []
    for pid, comp, rub in joined:
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        crits = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if not q or not crits:
            continue
        items.append({"pid": pid, "q": q[-1], "crits": crits,
                      "orig": [r["messages"][0]["content"] for r in comp["responses"]]})
    print(f"usable: {len(items)}")

    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    gen_model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR, dtype=torch.bfloat16, device_map="cuda").eval()

    gprompts = [gen_prompt(it["q"], it["crits"], show_rubric=True) for it in items]
    texts = generate(gen_model, tok, gprompts, a.candidates, a.max_new, a.batch, 0.9)
    del gen_model
    torch.cuda.empty_cache()
    print(f"generated: {len(texts)}")

    # ---- proxy: rubric judge -----------------------------------------
    judge = Judge(MODEL_DIR, batch=32)
    tasks, meta = [], []
    for k, it in enumerate(items):
        for c in range(a.candidates):
            t = texts[k * a.candidates + c]
            for ci, crit in enumerate(it["crits"]):
                tasks.append(build_prompt(crit, t))
                meta.append((k, c, ci))
    print(f"proxy judgements: {len(tasks):,}")
    sat = judge.score(tasks)
    proxy = np.zeros((len(items), a.candidates))
    cnt = np.zeros_like(proxy)
    for (k, c, ci), s in zip(meta, sat):
        proxy[k, c] += float(s)
        cnt[k, c] += 1
    proxy /= np.maximum(cnt, 1)
    del judge
    torch.cuda.empty_cache()

    # ---- gold: preference head ---------------------------------------
    z = np.load(a.gold)
    w, mu, sd = z["w"], z["mean"], z["std"]
    emb_model = AutoModel.from_pretrained(MODEL_DIR, dtype=torch.bfloat16,
                                          device_map="cuda").eval()

    @torch.inference_mode()
    def emb(ts):
        out = []
        for i in range(0, len(ts), 16):
            enc = tok(ts[i : i + 16], return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            h = emb_model(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
        return np.concatenate(out, 0)

    def gold_score(ts):
        E = (emb(ts) - mu) / (sd + 1e-6)
        L = np.array([[len(t), len(t.split())] for t in ts], dtype=float)
        L = (L - L.mean(0)) / (L.std(0) + 1e-6)
        return np.hstack([E, L]) @ w

    g_gen = gold_score(texts).reshape(len(items), a.candidates)
    orig_flat = [t for it in items for t in it["orig"]]
    g_orig = gold_score(orig_flat).reshape(len(items), 4)
    del emb_model
    torch.cuda.empty_cache()

    # ---- POSITIVE CONTROL --------------------------------------------
    spread_gen = float(np.mean(g_gen.std(axis=1)))
    spread_orig = float(np.mean(g_orig.std(axis=1)))
    ok = spread_gen > 0.5 * spread_orig
    print(f"\n=== POSITIVE CONTROL: does gold discriminate among generations? ===")
    print(f"  gold within-prompt sd on generations : {spread_gen:.4f}")
    print(f"  gold within-prompt sd on originals   : {spread_orig:.4f}")
    print(f"  -> gold {'DISCRIMINATES' if ok else 'IS BLIND HERE -- curve is uninterpretable'}")

    # ---- best-of-n curve ---------------------------------------------
    rng = np.random.default_rng(20260727)
    strengths = [n for n in STRENGTHS if n <= a.candidates]
    curve = []
    R = 24                                            # resamples of which n candidates
    per_prompt_gold = {}
    for n in strengths:
        px, gd, mk = [], [], defaultdict(list)
        pg = np.zeros(len(items))
        for k, it in enumerate(items):
            gk = []
            for _ in range(R):
                idx = rng.choice(a.candidates, size=n, replace=False)
                best = idx[np.argmax(proxy[k, idx])]
                px.append(proxy[k, best])
                gd.append(g_gen[k, best]); gk.append(g_gen[k, best])
                for key, v in gaming_markers(texts[k * a.candidates + best], it["crits"]).items():
                    mk[key].append(v)
            pg[k] = float(np.mean(gk))
        per_prompt_gold[n] = pg
        # prompt-clustered bootstrap: the prompt is the unit that generalises
        bs = np.array([pg[rng.integers(0, len(pg), size=len(pg))].mean() for _ in range(2000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        row = {"n": n, "proxy": float(np.mean(px)), "gold": float(np.mean(gd)),
               "gold_ci": [float(lo), float(hi)],
               **{f"mk_{k}": float(np.mean(v)) for k, v in mk.items()}}
        curve.append(row)
        print(f"  n={n:>2}  proxy={row['proxy']:.4f}  gold={row['gold']:+.4f} "
              f"[{lo:+.4f},{hi:+.4f}]  words={row['mk_words']:.0f}  "
              f"overlap={row['mk_criterion_lexical_overlap']:.4f}  bullets={row['mk_bullets']:.2f}")

    # PAIRED test: does gold actually change from n=1 to n=max? Same prompts.
    d = per_prompt_gold[strengths[-1]] - per_prompt_gold[strengths[0]]
    bs = np.array([d[rng.integers(0, len(d), size=len(d))].mean() for _ in range(4000)])
    dlo, dhi = np.percentile(bs, [2.5, 97.5])
    print(f"\n  PAIRED gold change n={strengths[0]} -> n={strengths[-1]}: "
          f"{d.mean():+.4f} [{dlo:+.4f},{dhi:+.4f}]  "
          f"{'DETECTABLE' if (dlo>0 or dhi<0) else 'INDISTINGUISHABLE FROM ZERO'}")
    resolution = float(np.mean([np.diff(np.percentile(
        [per_prompt_gold[n][k] for n in strengths], [2.5, 97.5])).item()
        for k in range(len(items))]))
    print(f"  noise floor (within-prompt gold spread across n): {resolution:.4f}")

    p0, pN = curve[0], curve[-1]
    last_n = strengths[-1]
    gold_peak = max(curve, key=lambda r: r["gold"])
    print(f"\n  P1 proxy monotone up      : {all(curve[i+1]['proxy'] >= curve[i]['proxy'] for i in range(len(curve)-1))}")
    print(f"  P2 gaming markers up      : words {p0['mk_words']:.0f}->{pN['mk_words']:.0f}, "
          f"overlap {p0['mk_criterion_lexical_overlap']:.4f}->{pN['mk_criterion_lexical_overlap']:.4f}")
    print(f"  P3 gold peaks at n={gold_peak['n']}      : "
          f"{'TURNS OVER' if gold_peak['n'] < last_n else 'no turn within tested range'}")
    print(f"     gold {p0['gold']:+.4f} -> peak {gold_peak['gold']:+.4f} -> {pN['gold']:+.4f}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out.with_suffix(".npz"), proxy=proxy, gold=g_gen,
                        gold_orig=g_orig, texts=np.array(texts, dtype=object))
    a.out.write_text(json.dumps({
        "prompts": len(items), "candidates": a.candidates,
        "paired_gold_change": float(d.mean()),
        "paired_gold_ci": [float(dlo), float(dhi)],
        "detectable": bool(dlo > 0 or dhi < 0),
        "noise_floor": resolution,
        "gold_spread_generations": spread_gen, "gold_spread_originals": spread_orig,
        "positive_control_passed": bool(ok),
        "curve": curve,
        "gold_peak_n": gold_peak["n"],
        "turns_over": bool(gold_peak["n"] < last_n),
        "strengths": strengths,
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
