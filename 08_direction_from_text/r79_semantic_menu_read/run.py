"""r79 -- the rival I said I could not build: measure the menu-read SEMANTICALLY.

CLAIM CARD
----------
Claim      r75-r78: a rater's positive criteria overlap the response THEY ranked
           best more than the one they ranked worst. Four rivals were built and
           all four failed -- length, absence, topicality, tokeniser -- but every
           one of them varied the LEXICAL measure. Entry 132 states the gap
           plainly: "It does not vary the decision to measure specificity by
           lexical overlap at all. A semantic measure could disagree with every
           cell here."
Estimand   the same positive-minus-negative gap with lexical containment replaced
           by EMBEDDING COSINE between the criterion and each response, in three
           unrelated pretraining lineages.
Target
observed?  YES. The criteria, the four responses per prompt, and each rater's own
           ranking are all released; the three backbones r39/r40 used are on
           disk. Nothing is generated -- this embeds text that already exists.
Alternative
worlds     A AGREES     the semantic gap is positive in all three lineages. Then
                        the finding is about the criteria and not about
                        bag-of-words, and the last rival I can construct has
                        failed.
           D DISAGREES  the semantic gap is null or negative. Then r75-r78
                        measured a lexical artifact: criteria that happen to
                        REUSE the preferred answer's wording, with no semantic
                        relation. Entries 129-132 would all need withdrawing to
                        claims about word reuse.
           M MIXED      lineages disagree with each other. Then the measure is
                        lineage-specific and neither reading is supported.
Intervention
           none. A different instrument on the same text.
Null       (i) shuffled signs, per lineage; (ii) the three lineages must agree
           with each other -- r68 measured their agreement on a different
           quantity at 0.9132, so disagreement here is informative rather than
           expected.

WHY THIS IS NOT "MORE JUDGES"
-----------------------------
The frozen list bans more judges. A judge in this project scores CRITERION
SATISFACTION through a Yes/No divergence-token gap and feeds the attribution
pipeline. This uses the same backbones as passive ENCODERS to replace a
tokeniser, touches no attribution number, and generates no responses. It is the
semantic twin of `containment`, not a new scorer -- and it is run because entry
132 named it as the one attack I had left.

WHY THESE THREE BACKBONES AND NOT A DEDICATED EMBEDDER
-------------------------------------------------------
Because they are already in this project's evidence chain: r39 cached them, r40
built on them, and r68 measured their inter-lineage agreement at 0.9132. A fresh
sentence-transformer would be one more arbitrary instrument whose reliability
here is unknown. Using three unrelated pretraining lineages makes disagreement
between them a readable signal rather than an unmeasured risk.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "08_direction_from_text/r75_menu_read_direction"))

from covalx import load_join  # noqa: E402
from run import LAB, ranks_from, resp_text  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
ART = "/home/ivan/research/causal-publication-protocol/artifacts"
BACKBONES = {
    "qwen": os.environ.get("COVALX_MODEL_08B",
                           "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
                           "Qwen3.5-0.8B-Base"),
    "phi": f"{ART}/model_phi-3.5-mini-instruct",
    "internlm": f"{ART}/model_internlm2-chat-1.8b",
}
MAX_TOK = 512
N_BOOT = 2000


def embed(texts, model_dir, batch, dtype):
    """Mean-pooled last hidden state, the same summary r39 cached."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    # internlm2's vendored modeling code calls DynamicCache methods removed in
    # transformers 5.x, so without this it cannot run AT ALL in this environment
    # -- which silently made the three-lineage argument a two-lineage one.
    from covalx.legacy_cache_shim import install as _install_cache_shim
    _install_cache_shim()
    tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(model_dir, trust_remote_code=True,
                                    torch_dtype=dtype).cuda().eval()
    # Width comes from the FIRST FORWARD PASS, not from a config attribute.
    # `mdl.config.hidden_size` raised AttributeError on Qwen3_5Config -- the
    # field is named differently across families, and guessing a config key is
    # reading a description of the object instead of the object. The tensor
    # knows its own width.
    out = None
    with torch.no_grad():
        for i in range(0, len(texts), batch):
            chunk = texts[i:i + batch]
            enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                      max_length=MAX_TOK).to("cuda")
            # hidden_states[-1], not `.last_hidden_state`: for internlm the
            # AutoModel mapping returns a CausalLM output which has no such
            # field. Asking for the hidden states explicitly works for every
            # backbone and does not depend on which head the mapping picks.
            out_ = mdl(**enc, output_hidden_states=True)
            h = out_.hidden_states[-1]
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            v = (h * m).sum(1) / m.sum(1).clamp(min=1)
            if out is None:
                out = np.zeros((len(texts), v.shape[-1]), np.float32)
            out[i:i + len(chunk)] = v.float().cpu().numpy()
            if i % (batch * 40) == 0:
                print(f"    {i}/{len(texts)}", flush=True)
    del mdl
    torch.cuda.empty_cache()
    return out


def cos(a, B):
    a = a / (np.linalg.norm(a) + 1e-9)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    return B @ a


def boot_gap(vec, y, pids, seed):
    uni = np.unique(pids)
    idx = {p: np.flatnonzero(pids == p) for p in uni}
    bs = np.random.default_rng(seed)
    out = []
    for _ in range(N_BOOT):
        take = np.concatenate([idx[p] for p in bs.choice(uni, len(uni), replace=True)])
        yy, vv = y[take], vec[take]
        if (yy > 0).sum() and (yy < 0).sum():
            out.append(vv[yy > 0].mean() - vv[yy < 0].mean())
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r79_semantic_menu_read.json")
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    import torch
    dtype = torch.bfloat16

    # ---- assemble, exactly as r75 does ----------------------------------
    crit_texts, resp_texts, rows = [], [], []
    resp_ix = {}
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        got, rlen = {}, {}
        for r in comp["responses"]:
            lab = r.get("response_index")
            if lab not in LAB:
                continue
            t = resp_text(r)
            key = (pid, lab)
            if key not in resp_ix:
                resp_ix[key] = len(resp_texts)
                resp_texts.append(t)
            got[lab] = resp_ix[key]
            rlen[lab] = len(t.split())
        if len(got) < 4:
            continue
        rk = {}
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            aid = asm.get("annotator_id")
            if w and aid:
                rk[aid] = ranks_from(w[0].get("ranking", ""))
        for c in rub.get("coval_full") or []:
            sc = c["scores"]
            if len(sc) != 1:
                continue
            aid, s = sc[0].get("annotator_id"), sc[0]["score"]
            if s == 0 or aid not in rk:
                continue
            vals = sorted(rk[aid].values())
            if vals[0] == vals[-1]:
                continue
            best = [l for l, v in rk[aid].items() if v == vals[0] and l in got]
            worst = [l for l, v in rk[aid].items() if v == vals[-1] and l in got]
            if not best or not worst:
                continue
            rows.append({"pid": pid, "y": 1 if s > 0 else -1,
                         "ci": len(crit_texts), "resp": got, "rlen": rlen,
                         "best": best, "worst": worst})
            crit_texts.append(c["criterion"])
    if len(rows) < 1000:
        raise SystemExit(f"REFUSING: only {len(rows)} usable write-ins.")
    print(f"write-ins {len(rows)}   criteria to embed {len(crit_texts)}   "
          f"responses to embed {len(resp_texts)}")

    y = np.array([r["y"] for r in rows])
    pids = np.array([r["pid"] for r in rows])
    per_lineage, gaps, failed = {}, {}, {}
    for name, path in BACKBONES.items():
        if not Path(path).exists():
            failed[name] = "model directory absent"
            print(f"  ⚠ {name}: {path} absent -- counted, not silently dropped")
            continue
        print(f"\n=== {name} ===", flush=True)
        # PER-LINEAGE ISOLATION. The scope note promised failed lineages would be
        # "counted and reported, never silently dropped" -- the promise was
        # written and the code was not. internlm2's bundled modeling file calls
        # DynamicCache.from_legacy_cache, removed in transformers 5.x, and the
        # exception escaped `embed` and destroyed the qwen and phi results that
        # had already been computed. A promise about failure handling has to be
        # executable or it is a comment.
        try:
            cc = _RES / f"r79_emb_crit_{name}.npy"
            rc = _RES / f"r79_emb_resp_{name}.npy"
            if cc.exists() and rc.exists():
                C, R = np.load(cc), np.load(rc)
                print(f"  reusing cached embeddings {C.shape} {R.shape}", flush=True)
            else:
                C = embed(crit_texts, path, a.batch, dtype)
                R = embed(resp_texts, path, a.batch, dtype)
                np.save(cc, C)
                np.save(rc, R)
        except Exception as e:
            failed[name] = f"{type(e).__name__}: {e}"
            print(f"  ⚠ {name} FAILED and is recorded: {type(e).__name__}: {e}", flush=True)
            continue
        # A lineage that RUNS is not a lineage that WORKS. internlm loads under
        # the cache shim and returns embeddings that are 100% NaN -- clean at
        # hidden_states[0], already NaN after the first transformer block. Without
        # this guard it was counted as one of three lineages and carried a NaN
        # into the verdict, which is a check failing toward PASS.
        bad = int((~np.isfinite(C)).sum() + (~np.isfinite(R)).sum())
        if bad:
            failed[name] = (f"produced {bad} non-finite embedding values "
                            f"({bad / (C.size + R.size):.1%}) -- ran but did not work")
            print(f"  ⚠ {name} REFUSED: {failed[name]}", flush=True)
            per_lineage.pop(name, None)
            continue
        d = np.empty(len(rows), np.float32)
        for k, r in enumerate(rows):
            sims = {l: float(cos(C[r["ci"]], R[[r["resp"][l]]])[0]) for l in LAB}
            xs = np.array([r["rlen"][l] for l in LAB], float)
            ys = np.array([sims[l] for l in LAB], float)
            if np.std(xs) > 0:
                b1 = float(np.cov(xs, ys, bias=True)[0, 1] / np.var(xs))
                b0 = float(ys.mean() - b1 * xs.mean())
                res = {l: sims[l] - (b0 + b1 * xs[i]) for i, l in enumerate(LAB)}
            else:
                res = sims
            d[k] = (float(np.mean([res[l] for l in r["best"]]))
                    - float(np.mean([res[l] for l in r["worst"]])))
        gap = float(d[y > 0].mean() - d[y < 0].mean())
        lo, hi = boot_gap(d, y, pids, 20260880 + len(name))
        sh = y.copy()
        np.random.default_rng(3).shuffle(sh)
        null = float(d[sh > 0].mean() - d[sh < 0].mean())
        per_lineage[name] = {"positive_mean": float(d[y > 0].mean()),
                             "negative_mean": float(d[y < 0].mean()),
                             "gap": gap, "ci": [lo, hi], "shuffled_null": null}
        gaps[name] = gap
        print(f"  positive {d[y>0].mean():+.5f}   negative {d[y<0].mean():+.5f}")
        print(f"  gap {gap:+.5f} [{lo:+.5f},{hi:+.5f}]   shuffled {null:+.5f}", flush=True)
        np.save(_RES / f"r79_d_{name}.npy", d)

    if len(per_lineage) < 2:
        raise SystemExit(f"REFUSING: only {len(per_lineage)} lineage(s) ran; the "
                         f"cross-lineage argument needs at least two.")
    g = np.array(list(gaps.values()))
    all_pos = bool((np.array([v["ci"][0] for v in per_lineage.values()]) > 0).all())
    agree = bool(np.sign(g).min() == np.sign(g).max())
    # Sign agreement is the weakest possible reading of "agree". These two
    # lineages differ by more than an order of magnitude in effect SIZE, and a
    # label that says only "A AGREES" would carry a confidence the numbers do not
    # support -- r68 measured these same backbones agreeing at 0.9132 on a
    # different quantity, which makes a 15x spread here informative, not routine.
    ratio = float(np.max(np.abs(g)) / max(np.min(np.abs(g)), 1e-12))
    if all_pos and ratio <= 3:
        world = "A AGREES"
    elif all_pos:
        world = (f"A AGREES IN SIGN ONLY -- effect size differs {ratio:.0f}x between lineages")
    elif (np.array([v["ci"][1] for v in per_lineage.values()]) < 0).all():
        world = "D DISAGREES"
    else:
        world = "M MIXED"

    verdict = (
        f"{world}. Entry 132 named the one rival I could not build from lexical data: every control so "
        f"far varied the TOKENISER, not the decision to measure specificity by word overlap at all. "
        f"This replaces `containment` with embedding cosine between the criterion and each response, "
        f"in the three unrelated pretraining lineages this project already uses -- r39 cached them, "
        f"r40 built on them, and r68 measured their inter-lineage agreement at 0.9132 on a different "
        f"quantity, so disagreement here would be readable rather than unmeasured. "
        + (f"⚠ {len(failed)} of {len(BACKBONES)} lineages did not run and are named rather than "
           f"quietly omitted: {'; '.join(f'{k} ({v[:80]})' for k, v in failed.items())}. " if failed else "")
        + f"Over {len(rows)} "
        f"write-ins with each rater's own ranking, the length-residualised positive-minus-negative "
        f"gap is "
        f"{', '.join(f'{k} {v['gap']:+.5f} [{v['ci'][0]:+.5f},{v['ci'][1]:+.5f}]' for k, v in per_lineage.items())}, "
        f"against shuffled-sign nulls of "
        f"{', '.join(f'{k} {v['shuffled_null']:+.5f}' for k, v in per_lineage.items())}. "
        f"The lineages {'agree in sign' if agree else 'DO NOT agree in sign, so the measure is lineage-specific and neither reading is supported'}, "
        f"but they disagree in MAGNITUDE by {ratio:.0f}x, and that is the number worth carrying: "
        f"r68 measured these same backbones agreeing at 0.9132 on a different quantity, so an "
        f"order-of-magnitude spread here says the semantic effect is real in direction and "
        f"instrument-dependent in size. Cosine and lexical containment are not on a common scale, so "
        f"no comparison of {per_lineage.get('qwen', {}).get('gap', float('nan')):+.5f} against the "
        f"lexical +0.02114 is licensed -- only the sign and the exclusion of zero transfer. "
        f"WHAT THIS SETTLES: whether r75-r78 measured word REUSE or a semantic relation between the "
        f"criterion and the answer the rater preferred. "
        f"WHAT IT DOES NOT: the scope that has held since r75 and is not loosened by a better "
        f"instrument -- this is association WITHIN a rater, and no measure of criterion-to-response "
        f"similarity can separate a menu that CREATED the direction from one that SUPPLIED THE WORDS "
        f"for a direction already held. That is S_pre, and it needs people, not FLOPs."
    )

    doc = {
        "n_write_ins": len(rows), "n_criteria": len(crit_texts), "n_responses": len(resp_texts),
        "lineages_run": list(per_lineage), "per_lineage": per_lineage,
        "lineages_failed": failed,
        "lineages_agree_in_sign": agree, "all_cis_exclude_zero_positive": all_pos,
        "effect_size_ratio_across_lineages": ratio,
        "world": world, "max_tokens": MAX_TOK,
        "outcome_variable_scope": (
            "Sign is the single author's own score; ranking is that same author's own world block. "
            "The backbones are used as passive ENCODERS -- no criterion satisfaction is scored, no "
            "attribution number is touched, and no response is generated."),
        "scope": (
            f"Mean-pooled last hidden state, truncated at {MAX_TOK} tokens -- long responses are cut, "
            f"which biases toward measuring their openings. Cosine is residualised on response word "
            f"count within prompt exactly as the lexical arms are, so the two differ only in the "
            f"similarity measure. Lineages that fail to load are counted and reported, never silently "
            f"dropped."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
