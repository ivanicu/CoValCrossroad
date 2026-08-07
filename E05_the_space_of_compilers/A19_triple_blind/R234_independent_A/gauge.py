#!/usr/bin/env python3
"""
GAUGE RUN -- how far do the numbers in run.py move when the instrument is asked
the same question differently?

Every estimand in run.py routes through ONE judge: Qwen3.5-2B-Base, few-shot,
sigmoid(logit(" Yes") - logit(" No")).  A number that routes through a model is a
claim about that MODEL's behaviour until somebody bounds the instrument.  This
file bounds it.

FOUR INSTRUMENTS on a seeded subsample of prompts:
  I0  fewshot_2b   -- the cached template and model.  POSITIVE CONTROL FOR THE
                      GAUGE ITSELF: if my re-implementation does not reproduce
                      the cached tensor, the gauge is measuring my code, not the
                      instrument, and nothing below may be read.
  I1  zeroshot_2b  -- same model, no few-shot exemplars.
  I2  flipped_2b   -- same model, the Yes/No option order reversed in the
                      question and the read-out gap reversed.  A LABEL-ORDER
                      control: a judge that is not order-symmetric is not
                      measuring satisfaction.
  I3  fewshot_0.8b -- a different-scale model, same template.  Cross-scale.

For each instrument the whole primary pipeline (Lambda) and S1 (A) are
recomputed on the SAME subsample, so the reported spread is instrument
dependence and not sampling.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import run as R  # the design under gauge

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
MODELS = {
    "2b": "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base",
    "0.8b": "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-0.8B-Base",
}

FEWSHOT = (
    "Task: decide whether an assistant reply satisfies an evaluation criterion.\n\n"
    "Criterion: The reply warns about legal risk.\n"
    "Reply: You should consult a lawyer before signing, since the clause may be unenforceable.\n"
    "Does the reply satisfy the criterion? Answer Yes or No.\n"
    "Answer: Yes\n\n"
    "Criterion: The reply gives step-by-step cooking instructions.\n"
    "Reply: I am sorry, I cannot help with that request.\n"
    "Does the reply satisfy the criterion? Answer No or Yes.\n"
    "Answer: No\n\n"
)
FEWSHOT_FWD = FEWSHOT.replace("Answer No or Yes.", "Answer Yes or No.")


def build_prompt(crit, reply, style, max_reply=1400):
    reply = reply[:max_reply]
    q = ("Does the reply satisfy the criterion? Answer No or Yes.\n"
         if style == "flipped" else
         "Does the reply satisfy the criterion? Answer Yes or No.\n")
    head = "" if style == "zeroshot" else FEWSHOT_FWD
    return (head + f"Criterion: {crit.strip()}\nReply: {reply.strip()}\n" + q + "Answer:")


class Judge:
    def __init__(self, path, batch=48):
        self.tok = AutoTokenizer.from_pretrained(path)
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.tok.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(
            path, dtype=torch.bfloat16, device_map="cuda").eval()
        self.batch = batch
        self.yes = self.tok.encode(" Yes", add_special_tokens=False)[0]
        self.no = self.tok.encode(" No", add_special_tokens=False)[0]

    @torch.inference_mode()
    def score(self, prompts):
        out = np.empty(len(prompts), np.float32)
        for i in range(0, len(prompts), self.batch):
            ch = prompts[i:i + self.batch]
            enc = self.tok(ch, return_tensors="pt", padding=True, truncation=True,
                           max_length=1024).to("cuda")
            lg = self.model(**enc, logits_to_keep=1).logits[:, -1, :].float()
            out[i:i + len(ch)] = torch.sigmoid(lg[:, self.yes] - lg[:, self.no]).cpu().numpy()
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--batch", type=int, default=48)
    a = ap.parse_args()
    t0 = time.time()

    joined, how = R.load_join()
    sat_full, sat_core = R.load_sat("full"), R.load_sat("core")
    bundles, drop = R.build(joined, sat_full, sat_core)
    rng = np.random.default_rng(a.seed)
    pids = sorted(bundles)
    sub = [pids[i] for i in rng.choice(len(pids), size=min(a.n, len(pids)), replace=False)]
    jmap = {p: (c, r) for p, c, r in joined}
    print(f"gauge subsample: {len(sub)} prompts   join={how}   dropped={drop}", flush=True)

    tasks, key = [], []
    for pid in sub:
        comp, rub = jmap[pid]
        reps = {r["response_index"]: r["messages"][0]["content"] for r in comp["responses"]}
        for src, items in (("full", rub["coval_full"]), ("core", rub["coval_core"])):
            for i, it in enumerate(items):
                for L in R.LABELS:
                    tasks.append((it["criterion"], reps[L]))
                    key.append((pid, src, i, L))
    print(f"judgements per instrument: {len(tasks):,}", flush=True)

    INSTR = [("I0_fewshot_2b", "2b", "fewshot"), ("I1_zeroshot_2b", "2b", "zeroshot"),
             ("I2_flipped_2b", "2b", "flipped"), ("I3_fewshot_0.8b", "0.8b", "fewshot")]
    sats = {}
    for name, mk, style in INSTR:
        j = Judge(MODELS[mk], batch=a.batch)
        pr = [build_prompt(c, r, style) for c, r in tasks]
        t = time.time()
        sats[name] = j.score(pr)
        print(f"  {name}: {time.time()-t:.0f}s  mean={sats[name].mean():.4f} "
              f"sd={sats[name].std():.4f}", flush=True)
        del j
        torch.cuda.empty_cache()

    # ---- POSITIVE CONTROL FOR THE GAUGE ------------------------------------
    cached = np.array([(sat_full if s == "full" else sat_core)[p][i, R.LABELS.index(L)]
                       for p, s, i, L in key])
    ctrl = {}
    for name in sats:
        r = float(np.corrcoef(cached, sats[name])[0, 1])
        ctrl[name] = dict(pearson_vs_cache=r,
                          mad=float(np.abs(cached - sats[name]).mean()))
    print("GAUGE POSITIVE CONTROL vs cached tensor:", json.dumps(ctrl, indent=1), flush=True)
    gauge_ok = ctrl["I0_fewshot_2b"]["pearson_vs_cache"] > 0.95
    print(f"  I0 reproduces the cache (r>0.95): {gauge_ok} "
          f"-- if False, NOTHING below may be read as instrument dependence.",
          flush=True)

    # ---- rebuild bundles under each instrument and rerun the estimands ------
    out = {"n_prompts": len(sub), "seed": a.seed, "gauge_positive_control": ctrl,
           "gauge_ok": bool(gauge_ok), "instruments": {}}
    subset = {p: bundles[p] for p in sub}
    for name in ["CACHED"] + [n for n, _, _ in INSTR]:
        bb = {}
        for p in sub:
            b = dict(subset[p])
            if name != "CACHED":
                v = sats[name]
                nf = b["Sf"].shape[0]
                nc = b["Sc"].shape[0]
                Sf = np.empty((nf, 4)); Sc = np.empty((nc, 4))
                for idx, (pp, s, i, L) in enumerate(key):
                    if pp != p:
                        continue
                    (Sf if s == "full" else Sc)[i, R.LABELS.index(L)] = v[idx]
                b["Sf"], b["Sc"] = Sf, Sc
            bb[p] = b
        R._CACHE.clear()
        C = R.cache(bb, "z", "mean")
        acc = defaultdict(list); ceil = []
        for p, b in bb.items():
            Zf, Zc, w = C[p]
            comps = R.compile_scores(p, b, Zf, Zc, w, a.seed)
            tgt = comps["full_signed"]
            for k, v in comps.items():
                acc[k].append(R.pairwise_conc(v, tgt))
            c = R.ceiling_split_half(b, Zf, "mean", "pairwise", np.random.default_rng(a.seed))
            if not np.isnan(c):
                ceil.append(c)
        rnd = float(np.mean([np.mean(acc[f"random4_s{s}"]) for s in range(20)]))
        ce = float(np.mean(ceil)); gap = ce - rnd
        lam = (float(np.mean(acc["core"])) - rnd) / gap if gap > 1e-9 else np.nan
        pol = R.polarity(bb, "z", "mean", np.random.default_rng(a.seed), nperm=400)
        # THE TWO HEADLINE CLAIMS, bounded on the same instruments:
        #   (i) the human-ranking ladder -- is the core still indistinguishable
        #       from the card's own selection rule, and still ~90% of the way
        #       from chance to the full signed rubric?
        #   (ii) the veto ladder -- does the core still recover most of the full
        #       rubric's above-floor ability to flag an unacceptable response
        #       while the sign-stripped full rubric still sits on the floor?
        hl = R.human_ladder(bb, "z", "mean", "world", a.seed,
                            np.random.default_rng(a.seed), nboot=500)
        vt = R.veto_auc(bb, "z", "mean", np.random.default_rng(a.seed), nboot=500)
        human = {nm: hl[nm]["acc"] for nm in R.LADDER}
        human["delta_top4pos_minus_core"] = hl["top4_pos"]["delta_vs_core"]
        human["delta_top4pos_ci95"] = hl["top4_pos"]["ci95"]
        human["above_chance_retention"] = (
            (hl["core"]["acc"] - hl["sham_core"]["acc"])
            / max(hl["full_signed"]["acc"] - hl["sham_core"]["acc"], 1e-9))
        veto = {k: v for k, v in vt.items() if k.startswith("auc_")}
        if not vt.get("EMPTY"):
            fl, fu = vt["auc_random4"], vt["auc_full"]
            veto["retention_core"] = (vt["auc_core"] - fl) / max(fu - fl, 1e-9)
            veto["retention_full_unit"] = (vt["auc_full_unit"] - fl) / max(fu - fl, 1e-9)
            veto["n_prompts"] = vt["n_prompts"]
        out["instruments"][name] = dict(human=human, veto=veto,
            phi_core=float(np.mean(acc["core"])), floor=rnd, ceiling=ce, gap=gap,
            Lambda=float(lam), phi_oracle4=float(np.mean(acc["oracle4"])),
            phi_sham=float(np.mean(acc["sham_core"])),
            phi_worst4=float(np.mean(acc["worst4"])),
            phi_top4_abs=float(np.mean(acc["top4_abs"])),
            R_P=pol["R_P"], R_N=pol["R_N"], A=pol["A"], p_A=pol["p_perm"],
            A_null_sd=pol["null_sd"])
        print(f"  {name:16s} Lambda={lam:+.4f}  A={pol['A']:+.4f} (p={pol['p_perm']:.4f})  "
              f"phi_core={np.mean(acc['core']):.4f} floor={rnd:.4f} ceil={ce:.4f}", flush=True)
        print(f"      HUMAN core={human['core']:.4f} full={human['full_signed']:.4f} "
              f"top4pos={human['top4_pos']:.4f} full_unit={human['full_unit']:.4f} "
              f"sham={human['sham_core']:.4f}  d(top4pos-core)={human['delta_top4pos_minus_core']:+.4f} "
              f"retention={human['above_chance_retention']:.3f}", flush=True)
        if "retention_core" in veto:
            print(f"      VETO  full={veto['auc_full']:.4f} core={veto['auc_core']:.4f} "
                  f"full_unit={veto['auc_full_unit']:.4f} floor={veto['auc_random4']:.4f} "
                  f"sham={veto['auc_sham_core']:.4f}  retention core={veto['retention_core']:.3f} "
                  f"full_unit={veto['retention_full_unit']:.3f}", flush=True)

    # ---- RE-JUDGE PENALTY --------------------------------------------------
    # THE CONFOUND THIS PRICES.  The mechanical compilers are literally rows of
    # the target's own basis, read by the SAME judge pass; the shipped core is a
    # separate set of texts read in a SEPARATE judge pass.  Part of any deficit
    # the core shows is therefore measurement noise, not compilation loss.
    # Bound it: score a mechanical compiler whose rows come from a DIFFERENT
    # instrument against the CACHED target.  The drop is the re-judge penalty,
    # and it is the fair allowance to give the core before calling it worse.
    pen = {}
    R._CACHE.clear()
    for name, _, _ in INSTR:
        v = sats[name]
        drops = []
        for p in sub:
            b = subset[p]
            nf = b["Sf"].shape[0]
            Sf = np.empty((nf, 4))
            for idx, (pp, s, i, L) in enumerate(key):
                if pp == p and s == "full":
                    Sf[i, R.LABELS.index(L)] = v[idx]
            Zf_c = R.normalise(b["Sf"], "z")
            Zf_x = R.normalise(Sf, "z")
            w = R.agg_weights(b["W"], "mean")
            tgt = w @ Zf_c
            k = min(4, nf)
            sel = np.argsort(-w)[:k]
            drops.append(R.pairwise_conc(Zf_c[sel].sum(0), tgt)
                         - R.pairwise_conc(Zf_x[sel].sum(0), tgt))
        pen[name] = float(np.mean(drops))
        print(f"  RE-JUDGE PENALTY {name}: {pen[name]:+.4f} Phi", flush=True)
    out["rejudge_penalty"] = pen

    lams = [v["Lambda"] for k, v in out["instruments"].items() if k != "CACHED"]
    As = [v["A"] for k, v in out["instruments"].items() if k != "CACHED"]
    out["gauge_bound"] = dict(
        Lambda_range=[float(min(lams)), float(max(lams))],
        Lambda_spread=float(max(lams) - min(lams)),
        A_range=[float(min(As)), float(max(As))],
        A_spread=float(max(As) - min(As)),
        A_sign_stable=bool(all(np.sign(x) == np.sign(As[0]) for x in As)))
    I = out["instruments"]
    ks = [k for k in I if k != "CACHED"]
    hd = [I[k]["human"]["delta_top4pos_minus_core"] for k in ks]
    hr = [I[k]["human"]["above_chance_retention"] for k in ks]
    vr = [I[k]["veto"].get("retention_core") for k in ks if "retention_core" in I[k]["veto"]]
    vu = [I[k]["veto"].get("retention_full_unit") for k in ks if "retention_full_unit" in I[k]["veto"]]
    out["gauge_bound"].update(
        human_delta_top4pos_minus_core_range=[float(min(hd)), float(max(hd))],
        human_delta_sign_stable=bool(all(np.sign(x) == np.sign(hd[0]) for x in hd)),
        human_above_chance_retention_range=[float(min(hr)), float(max(hr))],
        veto_retention_core_range=[float(min(vr)), float(max(vr))] if vr else None,
        veto_retention_full_unit_range=[float(min(vu)), float(max(vu))] if vu else None)
    out["seconds"] = time.time() - t0
    (RES / "gauge.json").write_text(json.dumps(out, indent=1, default=float))
    print("GAUGE BOUND:", json.dumps(out["gauge_bound"], indent=1), flush=True)
    print(f"wrote results/gauge.json in {out['seconds']:.0f}s")


if __name__ == "__main__":
    main()
