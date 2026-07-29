"""r41 step 1 (GPU) -- persist the criterion x response satisfaction tensor.

r12 computed  z_R(r) = (s(c_1,r), ..., s(c_K,r))  for every response in both
sets and threw it away on the line that aggregated it:

    rounds/r12_response_set/run.py:152
        acc[kind][k, r] += float(s)          # <- collapses the criterion axis

That is the fifth time in this repository an expensive GPU round discarded a
tensor it already had (r10/r19, r22, r12's per-prompt arrays, r12's
generations, and now this).  Criterion-space support geometry is unreachable
without it, so this pass rebuilds and SAVES it.

WHAT THIS PASS DOES NOT DO
--------------------------
It does not regenerate responses.  r12's fresh generations were persisted on
2026-07-28 and are read verbatim from disk.  Re-generating at temperature 0.9
would produce a DIFFERENT response set and silently change what the r12
numbers refer to.

POSITIVE CONTROL -- why this pass rescoring is not just "some other run"
------------------------------------------------------------------------
A tensor that does not reproduce r12 is not r12's tensor, and analysing it
while quoting r12's attribution drop would be comparing two different
measurements.  So this pass reruns the FULL real+shuf arm and the gold arm and
asserts elementwise reproduction of the 1,500 published per-prompt numbers
(250 prompts x {real, shuffled, attribution} x {ORIGINAL, FRESH}).

For that to be possible the judge has to be the same INSTRUMENT, not merely
the same checkpoint.  bf16 batched inference is composition-dependent: the
same pair scored in a different batch can differ in the last bits, and a
last-bit difference flips a near-tied pairwise comparison, which changes a
per-prompt accuracy by 1/6.  So the task list is built in r12's exact order
(both arms interleaved per prompt, real before shuf) at r12's exact batch
size, and the donor permutation is redrawn from r12's seed.  The shuffled arm
is recomputed even though the analysis does not use it, purely to keep batch
composition identical.

Secondary judges (--tag != primary) cannot reproduce r12 by construction.  For
those the control is SKIPPED AND RECORDED AS SKIPPED, never as passed.
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
from transformers import AutoModel, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
sys.path.insert(0, str(_ROOT))

from covalx.judge import Judge, build_prompt, load_join  # noqa: E402

_RES = _HERE / "results"
MODEL_DIR = os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base")
M08 = os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base")
ART = "/home/ivan/research/causal-publication-protocol/artifacts"

# The panel the GPU directive asks to be frozen.  Recorded per run, not
# assumed: whichever is passed on --judge is what the receipt reports.
PANEL = {
    "qwen2b": MODEL_DIR,
    "phi": f"{ART}/model_phi-3.5-mini-instruct",
    "internlm": f"{ART}/model_internlm2-chat-1.8b",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    ap.add_argument("--gen", type=Path,
                    default=_ROOT / "rounds/r12_response_set/results/a12_fresh_generations.json")
    ap.add_argument("--r12", type=Path,
                    default=_ROOT / "rounds/r12_response_set/results/a12_response_set.json")
    ap.add_argument("--gold", type=Path,
                    default=_ROOT / "rounds/r08_gold_preference/results/a08_gold_08b.npz")
    ap.add_argument("--tag", default="qwen2b", choices=sorted(PANEL))
    ap.add_argument("--prompts", type=int, default=250)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--limit", type=int, default=0, help="smoke only; forces a SMOKE tag")
    ap.add_argument("--offset", type=int, default=0,
                    help="skip this many joined prompts; non-zero means a DIFFERENT "
                         "sample than r12's, so the r12 reproduction control cannot "
                         "apply and is reported as skipped")
    ap.add_argument("--stem", default=None, help="output stem override")
    a = ap.parse_args()

    judge_dir = PANEL[a.tag]
    # A non-zero offset is a different slice of prompts, so it cannot reproduce
    # r12 and must not be allowed to look like it did.
    primary = a.tag == "qwen2b" and a.offset == 0
    smoke = a.limit > 0
    if smoke:
        print("*** SMOKE RUN -- output is tagged and must never reach the README ***")

    # ---- rebuild r12's item list, in r12's order ----------------------
    joined = load_join(a.comparisons, a.rubrics)[a.offset: a.offset + a.prompts]
    items = []
    for pid, comp, rub in joined:
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if q and cr:
            items.append({"pid": pid, "q": q[-1], "crits": cr,
                          "orig": [r["messages"][0]["content"] for r in comp["responses"]]})
    n = len(items)

    gen = json.loads(a.gen.read_text())
    n_fresh = int(gen["per_prompt"])

    # The saved generations must be the ones these items refer to.  A silent
    # misalignment here would attach every fresh response to the wrong prompt
    # and the whole geometry would be noise with a plausible shape.
    if gen["prompt_ids"] != [it["pid"] for it in items]:
        raise SystemExit("REFUSING TO RUN: saved generations do not align with the "
                         "rebuilt item list -- prompt_ids differ")
    fresh = [t for row in gen["fresh"] for t in row]
    orig_saved = gen["original"]
    for k, it in enumerate(items):
        if orig_saved[k] != it["orig"]:
            raise SystemExit(f"REFUSING TO RUN: original responses differ at prompt {k}")
    print(f"prompts={n}  fresh_per_prompt={n_fresh}  judge={a.tag}  aligned with r12 generations")

    if smoke:
        n = min(n, a.limit)
        items = items[:n]
        fresh = fresh[: n * n_fresh]

    # r12's donor permutation, from r12's seed, drawn before anything else
    # consumes the stream -- exactly as r12 does it.
    rng = np.random.default_rng(20260727)
    donor = np.array([(i + 1 + rng.integers(0, len(items) - 1)) % len(items)
                      for i in range(len(items))])

    judge = Judge(judge_dir, batch=a.batch)

    def score_set(texts_of, n_resp, which):
        """r12's score_set, but keeping the criterion axis instead of summing it."""
        tasks, meta = [], []
        for k, it in enumerate(items):
            for kind, src in (("real", k), ("shuf", donor[k])):
                for ci, c in enumerate(items[src]["crits"]):
                    for r in range(n_resp):
                        tasks.append(build_prompt(c, texts_of(k, r)))
                        meta.append((kind, k, ci, r))
        print(f"  [{which}] judgements: {len(tasks):,}", flush=True)
        sat = judge.score(tasks)

        # ragged criterion axis: prompt k owns rows koff[k]:koff[k+1]
        kk = [len(it["crits"]) for it in items]
        koff = np.concatenate([[0], np.cumsum(kk)]).astype(int)
        dk = [len(items[donor[k]]["crits"]) for k in range(n)]
        doff = np.concatenate([[0], np.cumsum(dk)]).astype(int)
        Z = {"real": np.full((koff[-1], n_resp), np.nan),
             "shuf": np.full((doff[-1], n_resp), np.nan)}
        off = {"real": koff, "shuf": doff}
        acc = {kd: np.zeros((n, n_resp)) for kd in Z}
        cnt = {kd: np.zeros((n, n_resp)) for kd in Z}
        for (kind, k, ci, r), s in zip(meta, sat):
            Z[kind][off[kind][k] + ci, r] = float(s)
            acc[kind][k, r] += float(s)
            cnt[kind][k, r] += 1
        for kd in Z:
            if np.isnan(Z[kd]).any():
                raise SystemExit(f"REFUSING TO SAVE: {which}/{kd} tensor has unfilled cells")
        mean = {kd: acc[kd] / np.maximum(cnt[kd], 1) for kd in acc}
        return Z, off, mean

    Zo, offo, s_orig = score_set(lambda k, r: items[k]["orig"][r], 4, "ORIGINAL")
    Zf, offf, s_fresh = score_set(lambda k, r: fresh[k * n_fresh + r], n_fresh, "FRESH")
    # Only one offset table is saved, so the two calls must agree on it.  They
    # depend only on items/donor, but "must" is not "checked".
    for kd in ("real", "shuf"):
        if not np.array_equal(offo[kd], offf[kd]):
            raise SystemExit(f"REFUSING TO SAVE: {kd} criterion offsets differ between sets")
    del judge
    torch.cuda.empty_cache()

    # ---- gold arm, deterministic, exactly as r12 ----------------------
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
            enc = tk8(list(ts[i:i + 16]), return_tensors="pt", padding=True,
                      truncation=True, max_length=512).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
        E = (np.concatenate(out, 0) - mu) / (sd + 1e-6)
        L = np.array([[len(t), len(t.split())] for t in ts], dtype=float)
        L = (L - L.mean(0)) / (L.std(0) + 1e-6)
        return np.hstack([E, L]) @ w

    g_orig = gold([t for it in items for t in it["orig"]]).reshape(n, 4)
    g_fresh = gold(fresh).reshape(n, n_fresh)
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

    # ---- POSITIVE CONTROL: elementwise reproduction of r12 ------------
    r12 = json.loads(a.r12.read_text())
    control = {"attempted": bool(primary and not smoke), "passed": None,
               "skipped_because": None, "worst_abs_diff": None, "n_compared": 0}
    repro = {}
    for name, mean, gd, nr in (("ORIGINAL", s_orig, g_orig, 4),
                               ("FRESH", s_fresh, g_fresh, n_fresh)):
        ar = agreement(mean["real"], gd, nr)
        ash = agreement(mean["shuf"], gd, nr)
        repro[name] = {"real": ar, "shuffled": ash, "attribution": ar - ash}

    if not control["attempted"]:
        control["skipped_because"] = (
            "smoke run" if smoke else
            f"offset={a.offset} is a different prompt slice than r12's, so "
            f"reproduction is impossible by construction and is NOT claimed"
            if a.offset else
            f"judge '{a.tag}' is not the instrument r12 used; reproduction is "
            f"impossible by construction and is NOT claimed")
        print(f"\n  reproduction control SKIPPED: {control['skipped_because']}")
    else:
        worst, ncmp, bad = 0.0, 0, []
        for name in ("ORIGINAL", "FRESH"):
            pub = r12["sets"][name]["per_prompt"]
            for field in ("real", "shuffled", "attribution"):
                mine = repro[name][field]
                ref = np.array(pub[field], dtype=float)
                if len(mine) != len(ref):
                    bad.append(f"{name}/{field}: length {len(mine)} vs {len(ref)}")
                    continue
                d = np.abs(mine - ref)
                ncmp += len(d)
                worst = max(worst, float(d.max()))
                nz = int((d > 1e-9).sum())
                if nz:
                    bad.append(f"{name}/{field}: {nz}/{len(d)} prompts differ, max {d.max():.4f}")
        control.update(passed=not bad, worst_abs_diff=worst, n_compared=ncmp,
                       mismatches=bad)
        print(f"\n=== REPRODUCTION CONTROL vs r12 ({ncmp} published numbers) ===")
        if bad:
            for b in bad:
                print("  MISMATCH", b)
            print("  -> the tensor below is NOT the tensor r12 aggregated.")
        else:
            print(f"  all {ncmp} per-prompt values reproduce exactly (max |diff| = {worst:.2e})")

    # ---- persist ------------------------------------------------------
    _RES.mkdir(parents=True, exist_ok=True)
    stem = a.stem or (f"r41_satisfaction_{a.tag}" + ("_SMOKE" if smoke else ""))
    np.savez_compressed(
        _RES / f"{stem}.npz",
        z_orig_real=Zo["real"], z_orig_shuf=Zo["shuf"],
        z_fresh_real=Zf["real"], z_fresh_shuf=Zf["shuf"],
        off_real=offo["real"], off_shuf=offo["shuf"],
        mean_orig_real=s_orig["real"], mean_orig_shuf=s_orig["shuf"],
        mean_fresh_real=s_fresh["real"], mean_fresh_shuf=s_fresh["shuf"],
        gold_orig=g_orig, gold_fresh=g_fresh,
        donor=donor,
        acc_orig_real=repro["ORIGINAL"]["real"], acc_orig_shuf=repro["ORIGINAL"]["shuffled"],
        acc_fresh_real=repro["FRESH"]["real"], acc_fresh_shuf=repro["FRESH"]["shuffled"],
    )
    receipt = {
        "tag": a.tag, "judge_checkpoint": judge_dir, "gold_checkpoint": M08,
        "batch": a.batch, "dtype": "bfloat16", "prompts": n,
        "fresh_per_prompt": n_fresh, "smoke": smoke,
        "criteria_source": "coval_core",
        "verbalizer": "' Yes' vs ' No', divergence-token logit gap",
        "template": "covalx.judge.build_prompt (FEWSHOT + Criterion/Reply/Answer)",
        "responses_from": str(a.gen),
        "regenerated_responses": False,
        "reproduction_control": control,
        "criteria": [{"pid": it["pid"], "crits": it["crits"]} for it in items],
    }
    (_RES / f"{stem}_receipt.json").write_text(json.dumps(receipt, indent=1))
    print(f"\nwrote {_RES / (stem + '.npz')}")
    print(f"wrote {_RES / (stem + '_receipt.json')}")
    print(f"  z_orig_real  {Zo['real'].shape}   z_fresh_real {Zf['real'].shape}")


if __name__ == "__main__":
    main()
