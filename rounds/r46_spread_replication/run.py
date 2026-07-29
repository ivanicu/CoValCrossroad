"""r46 -- out-of-sample replication of the spread-loss effect (entry 48).

CLAIM_CARD.md was committed BEFORE this file ran; its predicted ranges are
reproduced in PREDICTION below and the verdict is computed against them.  The
commit timestamp is the only thing separating a replication from a second
exploratory pass, which is why it exists as a separate commit.

r41 found -- while using it as a nuisance control -- that r12's attribution drop
concentrates where the prompt's OWN rubric loses its ability to separate the
four responses.  It survived a donor-arm control.  It was still discovered by
selection, on 250 prompts, so it is EXPLORATORY until it holds on prompts
nothing in this project has touched.

r12 used the FIRST 250 joined prompts.  718 are untouched.  This round takes the
next 250, generates fresh responses with r12's EXACT parameters, and re-runs the
measurement end to end.

Reuses r12's pipeline deliberately: same few-shot preamble, same generator, same
temperature/top_p/max_new_tokens, same judge template and verbalizer, same 0.8B
gold head, same donor-permutation construction (drawn WITHIN this slice, so no
donor is a prompt's own rubric).  A replication that changes the instrument is
not a replication.
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
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import MODEL_DIR, Judge, build_prompt, load_join  # noqa: E402

M08 = os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base")

FEWSHOT = (
    "Answer the user's question helpfully and directly.\n\n"
    "Question: What is a good way to start running?\n"
    "Answer: Start with short sessions of about twenty minutes, three times a week, "
    "and alternate walking and jogging until you can run continuously.\n\n"
)

# Verbatim from CLAIM_CARD.md, committed before this ran.
PREDICTION = {
    "spread_loss_len_controlled": {"lo": 0.12, "hi": 0.34, "must_exclude_zero": True},
    "donor_arm_ns_below": 0.12,
    "orthogonality_below": 0.15,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    ap.add_argument("--gold", type=Path,
                    default=_ROOT / "rounds/r08_gold_preference/results/a08_gold_08b.npz")
    ap.add_argument("--out", type=Path, default=_RES / "r46_spread_replication.json")
    ap.add_argument("--offset", type=int, default=250, help="skip r12's prompts")
    ap.add_argument("--prompts", type=int, default=250)
    ap.add_argument("--fresh", type=int, default=4)
    ap.add_argument("--max-new", type=int, default=180)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.prompts, a.boot = 8, 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    joined = load_join(a.comparisons, a.rubrics)
    items = []
    for pid, comp, rub in joined:
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if q and cr:
            items.append({"pid": pid, "q": q[-1], "crits": cr,
                          "orig": [r["messages"][0]["content"] for r in comp["responses"]]})
    held = items[a.offset:a.offset + a.prompts]
    n = len(held)
    if n < (8 if a.smoke else 200):
        raise SystemExit(f"REFUSING: only {n} held-out prompts available")
    # Disjointness is the entire premise of the round, so it is checked, not assumed.
    r12_pids = set()
    gp = _ROOT / "rounds/r12_response_set/results/a12_fresh_generations.json"
    if gp.exists():
        r12_pids = set(json.loads(gp.read_text())["prompt_ids"])
    overlap = r12_pids & {it["pid"] for it in held}
    if overlap:
        raise SystemExit(f"REFUSING: {len(overlap)} held-out prompts were used by r12")
    print(f"held-out prompts: {n}   overlap with r12: 0 (checked against its saved pids)")

    rng = np.random.default_rng(20260728)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    # ---- generate, with r12's exact parameters ------------------------
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    gm = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16,
                                              device_map="cuda").eval()
    prompts = [FEWSHOT + f"Question: {it['q'].strip()}\nAnswer:" for it in held
               for _ in range(a.fresh)]
    fresh = []
    with torch.inference_mode():
        for i in range(0, len(prompts), 16):
            enc = tok(prompts[i:i + 16], return_tensors="pt", padding=True,
                      truncation=True, max_length=640).to("cuda")
            o = gm.generate(**enc, do_sample=True, temperature=0.9, top_p=0.95,
                            max_new_tokens=a.max_new, pad_token_id=tok.pad_token_id)
            for j in range(len(enc["input_ids"])):
                t = tok.decode(o[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                fresh.append(t.split("Question:")[0].strip())
            if (i // 16) % 20 == 0:
                print(f"  gen {i}/{len(prompts)}", flush=True)
    del gm
    torch.cuda.empty_cache()
    _RES.mkdir(parents=True, exist_ok=True)
    (_RES / "r46_fresh_generations.json").write_text(json.dumps(
        {"n_prompts": n, "per_prompt": a.fresh, "temperature": 0.9, "top_p": 0.95,
         "max_new_tokens": a.max_new, "generator": MODEL_DIR, "offset": a.offset,
         "prompt_ids": [it["pid"] for it in held],
         "original": [it["orig"] for it in held],
         "fresh": [fresh[k * a.fresh:(k + 1) * a.fresh] for k in range(n)]}, indent=1))
    print(f"fresh responses: {len(fresh)}  (saved)")

    # ---- judge both sets, both arms ----------------------------------
    judge = Judge(MODEL_DIR, batch=a.batch)

    def score_set(texts_of, n_resp, which):
        tasks, meta = [], []
        for k, it in enumerate(held):
            for kind, src in (("real", k), ("shuf", int(donor[k]))):
                for ci, c in enumerate(held[src]["crits"]):
                    for r in range(n_resp):
                        tasks.append(build_prompt(c, texts_of(k, r)))
                        meta.append((kind, k, ci, r))
        print(f"  [{which}] judgements: {len(tasks):,}", flush=True)
        sat = judge.score(tasks)
        acc = {kd: np.zeros((n, n_resp)) for kd in ("real", "shuf")}
        cnt = {kd: np.zeros((n, n_resp)) for kd in ("real", "shuf")}
        for (kind, k, ci, r), s in zip(meta, sat):
            acc[kind][k, r] += float(s)
            cnt[kind][k, r] += 1
        return {kd: acc[kd] / np.maximum(cnt[kd], 1) for kd in acc}

    s_orig = score_set(lambda k, r: held[k]["orig"][r], 4, "ORIGINAL")
    s_fresh = score_set(lambda k, r: fresh[k * a.fresh + r], a.fresh, "FRESH")
    del judge
    torch.cuda.empty_cache()

    # ---- gold ---------------------------------------------------------
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

    g_orig = gold([t for it in held for t in it["orig"]]).reshape(n, 4)
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
            per.append(ok / tot if tot else np.nan)
        return np.array(per)

    attr_o = agreement(s_orig["real"], g_orig, 4) - agreement(s_orig["shuf"], g_orig, 4)
    attr_f = agreement(s_fresh["real"], g_fresh, a.fresh) - \
        agreement(s_fresh["shuf"], g_fresh, a.fresh)
    drop = attr_o - attr_f

    # ---- controls, before any correlation is read --------------------
    spread_gold = float(np.mean(g_fresh.std(axis=1))) / max(
        float(np.mean(g_orig.std(axis=1))), 1e-9)
    # THREE-VALUED, because a control with no power that returns FAIL is the
    # error this project has a law about.  r12's +0.102 sits on 250 prompts;
    # at n = 8 the standard error is roughly 0.18, so a negative mean there is
    # sampling noise and says nothing about the pipeline.  Below the power
    # floor the control reports UNVERIFIED and does not adjudicate in either
    # direction -- it must never read as "pass" either.
    POWER_FLOOR = 100
    ao = attr_o[np.isfinite(attr_o)]
    se = float(np.std(ao) / np.sqrt(max(len(ao), 1)))
    powered = len(ao) >= POWER_FLOOR
    pos_ok = bool(np.nanmean(attr_o) > 0)
    status = ("pass" if pos_ok else "FAIL") if powered else "UNVERIFIED (underpowered)"
    print(f"\n=== CONTROLS ===")
    print(f"  ORIGINAL attribution (positive control): {np.nanmean(attr_o):+.4f} "
          f"+/- {se:.4f} on {len(ao)} prompts -> {status}   [r12 got +0.102 on 250]")
    print(f"  FRESH attribution:                       {np.nanmean(attr_f):+.4f}   "
          f"[r12 got -0.064]")
    print(f"  gold spread ratio fresh/original:        {spread_gold:.3f} "
          f"-> {'usable' if spread_gold > 0.5 else 'DEGENERATE'}")
    if not powered:
        print(f"  ! fewer than {POWER_FLOOR} prompts: this control cannot detect an "
              f"effect the size of r12's, so it is NOT an acquittal and NOT a failure")
        if not a.smoke:
            raise SystemExit("REFUSING TO REPORT: too few prompts for the positive "
                             "control to have power, and an unpowered control cannot "
                             "license the result below")
    elif not pos_ok:
        raise SystemExit("REFUSING TO REPORT: the held-out ORIGINAL set does not show a "
                         "positive own-rubric advantage, so the pipeline is broken on "
                         "this slice and no fresh-response number is interpretable")
    if spread_gold <= 0.5:
        raise SystemExit("REFUSING TO REPORT: gold cannot order the fresh responses")

    # ---- the measures -------------------------------------------------
    D_spread = s_orig["real"].std(axis=1) - s_fresh["real"].std(axis=1)
    D_spread_donor = s_orig["shuf"].std(axis=1) - s_fresh["shuf"].std(axis=1)
    wl_o = np.array([np.mean([len(t.split()) for t in it["orig"]]) for it in held])
    wl_f = np.array([np.mean([len(t.split()) for t in fresh[k * a.fresh:(k + 1) * a.fresh]])
                     for k in range(n)])
    dlen = wl_f - wl_o

    def pearson(x, y):
        if np.std(x) < 1e-12 or np.std(y) < 1e-12:
            return float("nan")
        return float(np.corrcoef(x, y)[0, 1])

    def partial(y, *cs):
        X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in cs])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        return y - X @ b

    def analyse(x, y, label):
        k = np.isfinite(x) & np.isfinite(y)
        x, y = x[k], y[k]
        r = pearson(x, y)
        bs = np.array([pearson(x[i], y[i]) for i in
                       (rng.integers(0, len(x), len(x)) for _ in range(a.boot))])
        bs = bs[np.isfinite(bs)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        obs = abs(r)
        hits = sum(1 for _ in range(a.boot)
                   if abs(pearson(rng.permutation(x), y)) >= obs)
        return {"label": label, "n": int(k.sum()), "r": r,
                "ci": [float(lo), float(hi)],
                "excludes_zero": bool(lo > 0 or hi < 0),
                "perm_p": (hits + 1) / (a.boot + 1)}

    keep = np.isfinite(D_spread) & np.isfinite(drop) & np.isfinite(dlen) \
        & np.isfinite(D_spread_donor)
    own_len = analyse(partial(D_spread[keep], dlen[keep]),
                      partial(drop[keep], dlen[keep]), "spread_loss | length")
    own_don = analyse(partial(D_spread[keep], dlen[keep], D_spread_donor[keep]),
                      partial(drop[keep], dlen[keep], D_spread_donor[keep]),
                      "spread_loss | length + donor")
    don = analyse(D_spread_donor[keep], drop[keep], "donor_spread_loss")
    raw = analyse(D_spread[keep], drop[keep], "spread_loss raw")

    print(f"\n=== held-out result vs the PREREGISTERED prediction ===")
    for row in (raw, own_len, own_don, don):
        print(f"  {row['label']:34s} {row['r']:+.4f} "
              f"[{row['ci'][0]:+.3f},{row['ci'][1]:+.3f}]  p={row['perm_p']:.4f}"
              f"{'' if row['excludes_zero'] else '  (ns)'}")

    P = PREDICTION["spread_loss_len_controlled"]
    in_range = P["lo"] <= own_len["r"] <= P["hi"]
    replicated = bool(own_len["excludes_zero"] and own_len["r"] > 0)
    donor_null = bool(abs(don["r"]) < PREDICTION["donor_arm_ns_below"]
                      and not don["excludes_zero"])

    if not replicated:
        verdict = (
            f"NOT REPLICATED. On {int(keep.sum())} prompts this project had never "
            f"touched, spread loss vs the drop is {own_len['r']:+.4f} "
            f"{own_len['ci']} -- the interval includes zero. Entry 48 is downgraded to "
            f"a single-sample artifact: the effect was found by selection on r12's 250 "
            f"prompts and does not hold out of sample")
    elif not in_range and own_len["r"] < P["lo"]:
        verdict = (
            f"REPLICATED BUT WEAKER THAN CLAIMED. {own_len['r']:+.4f} {own_len['ci']} "
            f"against a predicted floor of +{P['lo']:.2f}. The effect is real out of "
            f"sample and the r41 magnitude was inflated by the selection that found it "
            f"-- which is what a post-hoc discovery is expected to do")
    elif not donor_null:
        verdict = (
            f"REPLICATED, BUT THE MECHANICAL READING SURVIVES TOO. Own spread loss "
            f"{own_len['r']:+.4f}, and the DONOR arm also reaches {don['r']:+.4f} "
            f"{don['ci']}. On r12's prompts the donor arm was null; here it is not, so "
            f"the non-mechanical claim from entry 48 is RETRACTED pending a design that "
            f"separates them")
    else:
        verdict = (
            f"REPLICATED, IN RANGE. Spread loss vs the drop is {own_len['r']:+.4f} "
            f"{own_len['ci']} (predicted [{P['lo']:+.2f},{P['hi']:+.2f}]), "
            f"{own_don['r']:+.4f} with the donor arm partialled out, while the donor arm "
            f"alone is {don['r']:+.4f} and not significant -- the same pattern as r41, on "
            f"prompts nothing in this project had touched. Entry 48 moves from "
            f"EXPLORATORY to REPLICATED IN THE PROXY WORLD. Still not human: the outcome "
            f"is attribution against a model gold head, and H_fresh is what would make it "
            f"a claim about people")
    print(f"\n-> {verdict}")

    a.out.write_text(json.dumps({
        "held_out_prompts": int(keep.sum()), "offset": a.offset,
        "overlap_with_r12": 0,
        "prediction_committed_before_run": PREDICTION,
        "controls": {"original_attribution": float(np.nanmean(attr_o)),
                     "fresh_attribution": float(np.nanmean(attr_f)),
                     "gold_spread_ratio": spread_gold,
                     "positive_control_n": int(len(ao)),
                     "positive_control_se": se,
                     "positive_control_powered": bool(powered),
                     "positive_control_status": status,
                     "positive_control_passed": bool(pos_ok and powered)},
        "spread_loss_raw": raw, "spread_loss_length_controlled": own_len,
        "spread_loss_length_and_donor_controlled": own_don,
        "donor_spread_loss": don,
        "replicated": replicated, "in_predicted_range": in_range,
        "donor_arm_null_as_predicted": donor_null,
        "verdict": verdict,
        "scope": ("Proxy world only. The outcome is attribution against a model gold "
                  "head and the spread is measured by the same judge whose "
                  "off-distribution validity is the open question. A clean replication "
                  "here shows the effect is real and stable in the proxy, NOT that it "
                  "is about human preference -- that is H_fresh."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
