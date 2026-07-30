"""r22 -- Does the attribution survive a change of model family?

Every judge in this project has been Qwen3.5. r10 varied size and template and
found the attribution stable, but size and template are small perturbations
inside one pretraining lineage. A shared inductive bias would survive both and
show up as agreement.

Three other families are available locally. Each grades the same prompts under
own / nearest-topic / random criteria against the same real human rankings.

Per-judge positive control: a judge whose own-rubric arm cannot beat 0.55 on
human pairwise rankings is excluded, because a decomposition of noise is noise.
r19 had to apply that rule retroactively to a 0.5405 cell; here it is applied
before anything is read.
"""
from __future__ import annotations

import argparse, json, os, sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, Judge, build_prompt, human_pairs, load_join  # noqa: E402

ART = "/home/ivan/research/causal-publication-protocol/artifacts"
# (path, FAMILY).  The family is declared, never inferred from the nickname.
# The first version of this round derived it as `name.split("-")[0]`, which
# turns "qwen3.5-2b-base" and "qwen2.5-3b-instruct" into two different strings
# and therefore counted one lineage as two families -- so the round reported
# "SURVIVES A CHANGE OF FAMILY" on two Qwen judges, asserting precisely what it
# had failed to test.  A label is not a description.
JUDGES = {
    "qwen3.5-2b-base(ref)": (os.environ.get("COVALX_MODEL_2B", "Qwen/Qwen3.5-2B-Base"), "qwen"),
    "qwen2.5-3b-instruct":  (f"{ART}/model_qwen2.5-3b-instruct", "qwen"),
    "phi-3.5-mini-instruct": (f"{ART}/model_phi-3.5-mini-instruct", "phi"),
    "internlm2-chat-1.8b":  (f"{ART}/model_internlm2-chat-1.8b", "internlm"),
}
FLOOR = 0.55


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r22_cross_family.json")
    ap.add_argument("--prompts", type=int, default=300)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    joined = load_join(a.comparisons, a.rubrics)[: a.prompts]
    items = []
    for pid, comp, rub in joined:
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        hp = human_pairs(comp["metadata"]["assessments"])
        q = [m["content"] for m in comp["prompt"]["messages"] if m["role"] == "user"]
        if cr and hp and q:
            items.append({"crits": cr, "pairs": hp, "q": q[-1],
                          "resp": {r["response_index"]: r["messages"][0]["content"]
                                   for r in comp["responses"]}})
    n = len(items)
    print(f"prompts: {n}")

    # nearest-topic donor, computed once with the reference model
    ref = JUDGES["qwen3.5-2b-base(ref)"][0]
    tk = AutoTokenizer.from_pretrained(ref)
    if tk.pad_token_id is None:
        tk.pad_token = tk.eos_token
    em = AutoModel.from_pretrained(ref, dtype=torch.bfloat16, device_map="cuda").eval()
    with torch.inference_mode():
        out = []
        for i in range(0, n, 32):
            enc = tk([it["q"] for it in items][i:i+32], return_tensors="pt", padding=True,
                     truncation=True, max_length=256).to("cuda")
            h = em(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            out.append(((h*m).sum(1)/m.sum(1).clamp(min=1)).float().cpu().numpy())
    E = np.concatenate(out, 0); E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
    del em; torch.cuda.empty_cache()
    S = E @ E.T; np.fill_diagonal(S, -np.inf)
    near = S.argmax(1)
    rng = np.random.default_rng(20260727)
    rand = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
    arms = {"own": np.arange(n), "near": near, "random": rand}

    results, per_judge_prompt = {}, {}
    for jname, (jpath, _fam) in JUDGES.items():
        if not Path(jpath).exists() and "/" in jpath and jpath.startswith("/"):
            print(f"  [{jname}] SKIP -- not on disk"); continue
        print(f"\n=== judge: {jname} ===", flush=True)
        try:
            judge = Judge(jpath, batch=16)
        except Exception as e:
            print(f"  FAILED TO LOAD: {type(e).__name__}: {str(e)[:120]}"); continue
        tasks, meta = [], []
        for arm, src in arms.items():
            for k in range(n):
                for c in items[src[k]]["crits"]:
                    for lab in items[k]["resp"]:
                        tasks.append(build_prompt(c, items[k]["resp"][lab]))
                        meta.append((arm, k, lab))
        print(f"  judgements: {len(tasks):,}", flush=True)
        try:
            sat = judge.score(tasks)
        except Exception as e:
            print(f"  SCORING FAILED: {type(e).__name__}: {str(e)[:120]}")
            del judge; torch.cuda.empty_cache(); continue
        del judge; torch.cuda.empty_cache()

        # DEGENERACY GUARD, added 2026-07-28.  phi-3.5-mini scored own=near=
        # random=0.0000 in the previous run and was filed as
        # `positive_control_passed: False`, i.e. as a judge that cannot tell
        # good responses from bad.  It was the harness: its SentencePiece
        # tokenizer put " Yes" and " No" behind a shared whitespace token, so
        # the logit gap was identically zero and every response tied.  A judge
        # that emits CONSTANT output has not failed a control -- it has not
        # been measured, and the two must never share a label, because a
        # cleared claim is never re-examined.
        sd = float(np.std(sat))
        if sd < 1e-6:
            print(f"  HARNESS FAILURE, not a judge verdict: satisfaction sd={sd:.2e}. "
                  f"Every score is identical, so every pair ties. Check that "
                  f"' Yes'/' No' resolve to DIFFERENT token ids for this tokenizer.")
            results[jname] = {"own": None, "positive_control_passed": False,
                              "status": "DEGENERATE_OUTPUT_HARNESS_FAILURE",
                              "satisfaction_sd": sd}
            continue

        acc = {}
        for (arm, k, lab), s in zip(meta, sat):
            acc.setdefault((arm, k), {}).setdefault(lab, []).append(float(s))
        per = {}
        for arm in arms:
            v = []
            for k in range(n):
                d = acc.get((arm, k))
                if not d:
                    v.append(np.nan); continue
                score = {lab: float(np.mean(x)) for lab, x in d.items()}
                ok = tot = 0
                for x, y in items[k]["pairs"]:
                    if x in score and y in score:
                        tot += 1; ok += int(score[x] > score[y])
                v.append(ok / tot if tot else np.nan)
            per[arm] = np.array(v)
        good = ~np.isnan(np.vstack([per[x] for x in arms])).any(axis=0)
        per = {x: v[good] for x, v in per.items()}
        m = good.sum()
        per_judge_prompt[jname] = per

        own = float(per["own"].mean())
        passed = own > FLOOR
        d = per["own"] - per["random"]
        bs = np.array([d[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        dn = per["own"] - per["near"]
        bsn = np.array([dn[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        nlo, nhi = np.percentile(bsn, [2.5, 97.5])
        results[jname] = {
            "own": own, "near": float(per["near"].mean()), "random": float(per["random"].mean()),
            "attribution_vs_random": float(d.mean()), "ci": [float(lo), float(hi)],
            "attribution_vs_near": float(dn.mean()), "ci_near": [float(nlo), float(nhi)],
            "prompts": int(m), "positive_control_passed": bool(passed)}
        flag = "" if passed else f"   <- EXCLUDED: own arm {own:.4f} <= {FLOOR}"
        print(f"  own {own:.4f}  near {per['near'].mean():.4f}  random {per['random'].mean():.4f}")
        print(f"  attribution vs random {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]"
              f"   vs near {dn.mean():+.4f} [{nlo:+.4f},{nhi:+.4f}]{flag}")

    usable = [k for k, v in results.items() if v.get("positive_control_passed")]
    broken = [k for k, v in results.items() if v.get("status")]
    fams = sorted({JUDGES[k][1] for k in usable})
    print(f"\n=== judges passing their positive control: {len(usable)}/{len(results)} ===")
    print(f"    usable families: {fams or ['none']}")
    if broken:
        print(f"    HARNESS-BROKEN (not judged, NOT acquitted): {broken}")
    if usable:
        vals = [results[k]["attribution_vs_random"] for k in usable]
        print(f"  attribution vs random across {len(usable)} judges "
              f"({len(fams)} distinct famil{'y' if len(fams)==1 else 'ies'}): "
              f"{np.mean(vals):.4f} +- {np.std(vals):.4f}  "
              f"range {min(vals):.4f}..{max(vals):.4f}")
    allpos = bool(usable) and all(results[k]["ci"][0] > 0 for k in usable)
    # The gate is DISTINCT FAMILIES, not judge count.  Two judges from one
    # lineage cannot separate "the attribution is real" from "the attribution is
    # a property of how this lineage reads rubrics".
    if len(fams) >= 2 and allpos:
        verdict = (f"SURVIVES A CHANGE OF FAMILY: usable judges span {len(fams)} families "
                   f"({', '.join(fams)}) and every one shows a positive attribution with an "
                   "interval clear of zero, so the decomposition is not an artifact of a "
                   "single lineage.")
    elif len(fams) >= 2:
        verdict = ("FAMILY-DEPENDENT: at least one usable judge from another family does "
                   "not reproduce a positive attribution, so the decomposition cannot be "
                   "stated independently of the judge that produced it.")
    elif len(fams) == 1:
        verdict = (f"UNRESOLVED -- SINGLE FAMILY: {len(usable)} judge(s) passed their positive "
                   f"control but all are '{fams[0]}'. The attribution reproduces across a "
                   "generation change WITHIN that lineage, which is a weaker statement than "
                   "family-independence and must not be reported as it. Every non-"
                   f"{fams[0]} judge failed to load or failed its own-rubric floor, so this "
                   "round has NOT tested the thing its title names.")
    else:
        verdict = ("UNRESOLVED: no judge passed its positive control in this prompt format, "
                   "so family cannot be separated from format.")
    print(f"\n  -> {verdict}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"prompts": n, "floor": FLOOR, "judges": results,
                                 "usable": usable, "usable_families": fams,
                                 "judge_families": {k: v[1] for k, v in JUDGES.items()},
                                 "verdict": verdict}, indent=1))
    # PERSIST THE PER-PROMPT ARRAYS.  Added 2026-07-28.  This round already had
    # them in memory (`per_judge_prompt`) and threw them away, keeping only
    # cell-level means and the CIs computed from them.  That is exactly the
    # defect a statistics review found in r10/r19: the 27%-67% bracket rests on
    # two cells whose per-prompt scores were never saved, so no prompt-level
    # interval can be computed for it after the fact without paying the GPU cost
    # again.  With these arrays the prompt-specific SHARE -- attribution divided
    # by above-chance accuracy, which is the quantity the headline actually
    # reports -- can be bootstrapped properly, jointly over numerator and
    # denominator, instead of quoting a ratio of two point estimates.
    npz = a.out.with_name(a.out.stem + "_per_prompt.npz")
    np.savez_compressed(npz, **{f"{j}|{arm}": v
                                for j, per in per_judge_prompt.items()
                                for arm, v in per.items()})
    print(f"wrote {npz}  ({len(per_judge_prompt)} judges x {len(arms)} arms)")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
