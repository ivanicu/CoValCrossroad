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

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())))
from covalx.legacy import round_results  # noqa: E402
from covalx import MODEL_DIR, Judge, build_prompt, load_join  # noqa: E402

OUTCOME_SCOPE = (
    "The FRESH arm is scored against the r08 MODEL GOLD HEAD, not against human r"
    "ankings -- the release contains none for generated responses. r47 showed tha"
    "t head's correlation with response length rises from +0.077 on the released "
    "candidates to +0.458 on these, and that roughly half the ORIGINAL-minus-FRES"
    "H gap rides on that channel; on held-out prompts (r46) the fresh arm stops b"
    "eing negative once length is removed. So the licensed reading is that the ow"
    "n-rubric advantage DOES NOT TRANSFER, not that an unrelated rubric BEATS it "
    "(entry 50)."
)

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")

M08 = os.environ.get("COVALX_MODEL_08B", "Qwen/Qwen3.5-0.8B-Base")
LABELS = ("A", "B", "C", "D")

FEWSHOT = (
    "Answer the user's question helpfully and directly.\n\n"
    "Question: What is a good way to start running?\n"
    "Answer: Start with short sessions of about twenty minutes, three times a week, "
    "and alternate walking and jogging until you can run continuously.\n\n"
)


def build_verdict(control_ok: bool, share: float, res: dict) -> str:
    """The verdict as a pure function of stored quantities.

    Factored out so it can be recomputed by --reverdict without regenerating
    responses.  A conclusion that cannot be re-derived from the numbers is a
    hand-written conclusion wearing a JSON field.
    """
    return ("VOID: the fresh response set is too homogeneous for any ordering to "
            "be measured, so nothing about transfer is established"
            if not control_ok else
            # States what fell, and names it correctly.  It deliberately does NOT
            # narrate which older wording was withdrawn: a results file is where a
            # round asserts its finding, and a withdrawal narrated here would put
            # the retired phrase back into the artifact an outsider greps.  The
            # withdrawal belongs in RETRACTIONS.md, which is the file for it.
            # NUMBERS, and the right WORD for them. Two defects, one fix.
            #
            # (1) This verdict cited no number at all -- so no prose check in the
            #     package could compare it to its own data, which is exactly the
            #     population `verdict_cites_its_own_contrasts` reports as
            #     unclassifiable. The most-cited round in the repository was in it.
            # (2) "most ... does not transfer" describes a PARTIAL loss. The stored
            #     share is 1.63: the fresh arm does not merely lose the advantage,
            #     it INVERTS. More than all of it goes. "Most" is weaker than the
            #     finding, and a verdict weaker than its own numbers is the quiet
            #     direction of the same error this project logs in the loud one.
            f"RESPONSE-SET-SPECIFIC, AND IT INVERTS: the own-rubric advantage is "
            f"{res['ORIGINAL']['attribution']:+.4f} "
            f"[{res['ORIGINAL']['ci'][0]:+.4f},{res['ORIGINAL']['ci'][1]:+.4f}] on the four "
            f"released candidates and {res['FRESH']['attribution']:+.4f} "
            f"[{res['FRESH']['ci'][0]:+.4f},{res['FRESH']['ci'][1]:+.4f}] on responses the "
            f"criteria authors never saw -- a drop of "
            f"{res['ORIGINAL']['attribution'] - res['FRESH']['attribution']:+.4f}, which is "
            f"{share:.0%} of the original advantage. Above 100% means the arm does not merely "
            f"fail to transfer, it changes sign, so 'most of it does not transfer' understates "
            f"what the numbers say. What falls is SOURCE SPECIFICITY -- own-rubric minus "
            f"reference-rubric performance -- which is a contrast between two rubrics, not "
            f"between rubric content and its absence"
            if share > 0.5 else
            "TRANSFERS: the advantage survives on responses the authors never saw, "
            "so it is prompt/value-specific rather than response-set-specific"
            if res["FRESH"]["ci"][0] > 0 else
            "UNRESOLVED: attribution on fresh responses is not distinguishable "
            "from zero, so neither reading is established")


def reverdict(path) -> None:
    """Recompute ONLY the verdict from an existing results file.

    Exists because this round's generation step is stochastic and unseeded: a
    re-run would produce a DIFFERENT fresh response set and silently invalidate
    every downstream artifact built on the saved one (r39's feature cache, r40,
    r41's satisfaction tensor).  So when a framing is withdrawn, the verdict is
    recomputed from the stored numbers and everything else is left untouched.
    """
    import json as _json
    doc = _json.loads(path.read_text())
    old = doc.get("verdict")
    new = build_verdict(bool(doc["control_passed"]),
                        float(doc["non_transferring_share"]), doc["sets"])
    doc["verdict"] = new
    doc["verdict_recomputed_without_rerun"] = (
        "The generation step is stochastic and unseeded, so re-running would "
        "replace the response set that r39/r40/r41 are all built on. Only the "
        "verdict was recomputed, from the numbers already in this file.")
    path.write_text(_json.dumps(doc, indent=1))
    print(f"verdict recomputed in {path}")
    print(f"  was: {old[:90]}...")
    print(f"  now: {new[:90]}...")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    ap.add_argument("--gold", type=Path, default=round_results("R08", "a08_gold_08b.npz"))
    ap.add_argument("--out", type=Path, default=Path(_RES + "/a12_response_set.json"))
    ap.add_argument("--prompts", type=int, default=250)
    ap.add_argument("--fresh", type=int, default=4)
    ap.add_argument("--max-new", type=int, default=180)
    ap.add_argument("--reverdict", action="store_true",
                    help="recompute the verdict from the stored numbers; no GPU, "
                         "no regeneration, nothing else touched")
    a = ap.parse_args()

    if a.reverdict:
        reverdict(a.out)
        return

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

    # PERSIST THE GENERATIONS.  Added 2026-07-28.  r12 is the most anomalous
    # result in this repository -- the attribution does not merely shrink on
    # unseen responses, it inverts -- and its generations were thrown away,
    # so nobody could re-analyse them without regenerating a DIFFERENT set at
    # temperature 0.9.  r09 saved its generations, which is the only reason
    # r11 could later run the independent-backbone control that retracted it
    # (entry 4).  The same control was unavailable here purely because of a
    # missing file write.  An expensive stochastic artifact that is not saved
    # is a result nobody can attack, including its author.
    gen_path = Path(_RES) / "a12_fresh_generations.json"
    Path(_RES).mkdir(parents=True, exist_ok=True)
    gen_path.write_text(json.dumps(
        {"n_prompts": n, "per_prompt": a.fresh, "temperature": 0.9, "top_p": 0.95,
         "max_new_tokens": a.max_new, "generator": MODEL_DIR,
         "prompt_ids": [it.get("pid") for it in items],
         "original": [it["orig"] for it in items],
         "fresh": [fresh[k * a.fresh:(k + 1) * a.fresh] for k in range(n)]},
        indent=1))
    print(f"  saved generations -> {gen_path}")

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

    # ---- MANDATORY DISCRIMINATION CONTROL ----------------------------
    # Both FRESH arms sitting near 0.5 is the signature of an UNDECIDABLE
    # comparison, not of a failing rubric. If the fresh responses are too
    # homogeneous for gold to separate them, this test measures nothing.
    def spread(gd):
        return float(np.mean(gd.std(axis=1)))

    def decidable(gd, n_resp, tol=1e-9):
        tot = dec = 0
        for k in range(n):
            for x, y in combinations(range(n_resp), 2):
                tot += 1
                dec += int(abs(gd[k, x] - gd[k, y]) > tol)
        return dec / max(tot, 1)

    def self_sim(texts_of, n_resp):
        """mean pairwise token-Jaccard within a prompt's response set"""
        import re as _re
        out = []
        for k in range(n):
            toks = [set(_re.findall(r"[a-z']{4,}", texts_of(k, r).lower()))
                    for r in range(n_resp)]
            for x, y in combinations(range(n_resp), 2):
                u = toks[x] | toks[y]
                out.append(len(toks[x] & toks[y]) / max(len(u), 1))
        return float(np.mean(out))

    ss_o = self_sim(lambda k, r: items[k]["orig"][r], 4)
    ss_f = self_sim(lambda k, r: fresh[k * a.fresh + r], a.fresh)
    print("\n=== DISCRIMINATION CONTROL (does the FRESH set admit an ordering at all?) ===")
    print(f"  gold within-prompt sd   ORIGINAL={spread(g_orig):.4f}   FRESH={spread(g_fresh):.4f}")
    print(f"  lexical self-similarity ORIGINAL={ss_o:.4f}   FRESH={ss_f:.4f}"
          f"   (higher = the four responses are more alike)")
    ratio = spread(g_fresh) / max(spread(g_orig), 1e-9)
    control_ok = ratio > 0.5 and ss_f < ss_o * 1.5
    print(f"  fresh/original gold spread ratio = {ratio:.3f}")
    print(f"  -> FRESH set is {'USABLE' if control_ok else 'DEGENERATE -- the comparison below is void'}")

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
                     "prompts": int(len(d)),
                     # PER-PROMPT ARRAYS, added 2026-07-28. `agreement()` already
                     # returned these and the round threw them away, keeping only
                     # the four cell means -- the third time in this project an
                     # expensive GPU round discarded values it had in hand (r10/r19,
                     # r22, now r12). Without them the rubric-vs-proxy disagreement
                     # per prompt cannot be recovered, and that is one of the two
                     # axes the human-ranking sampling frame has to stratify on.
                     "per_prompt": {
                         "pids": [it["pid"] for it in items][:len(d)],
                         "real": [float(x) for x in ar],
                         "shuffled": [float(x) for x in ash],
                         "attribution": [float(x) for x in d]}}
        print(f"\n  {name:9s} real={ar.mean():.4f}  shuffled={ash.mean():.4f}  "
              f"attribution={d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]")

    dd = res["ORIGINAL"]["attribution"] - res["FRESH"]["attribution"]
    share = 1 - (res["FRESH"]["attribution"] / res["ORIGINAL"]["attribution"]) \
        if res["ORIGINAL"]["attribution"] > 1e-9 else float("nan")
    print(f"\n  drop from ORIGINAL to FRESH: {dd:+.4f}  "
          f"({share:.1%} of the advantage does not transfer to unseen responses)")
    # ONE verdict path, not two. This line used to be a full inline COPY of
    # build_verdict's conditional, and the two had drifted apart:
    #
    #   * `--reverdict` used the function, which entry 138 corrected to state the
    #     numbers and to say the arm INVERTS rather than "most does not transfer";
    #   * a real rerun used this copy, which still said "most", and additionally
    #     carried the retired phrase "the value-carrying share" -- a framing the
    #     queue withdrew, sitting in source, ready to be written into an artifact
    #     by the next run.
    #
    # So entry 138's fix landed on one path of two and a rerun would have silently
    # reverted it. `no_withdrawn_framings` scans results JSONs and
    # `retired_framing_in_assertion_positions` scans prose; neither reads SOURCE
    # STRINGS, so nothing in the suite could see the retired phrase here.
    verdict = build_verdict(bool(control_ok), float(share), res)
    print(f"  -> {verdict}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"prompts": n, "fresh_per_prompt": a.fresh,
                                 "control_gold_spread_original": spread(g_orig),
                                 "control_gold_spread_fresh": spread(g_fresh),
                                 "control_selfsim_original": ss_o,
                                 "control_selfsim_fresh": ss_f,
                                 "control_passed": bool(control_ok),
                                 "sets": res, "drop": float(dd),
                                 "non_transferring_share": float(share),
                                 "verdict": verdict}, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
