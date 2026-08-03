"""r137 -- the judge's output depends on WHO ELSE IS IN THE BATCH, and this measures what that costs.

WHAT WAS FOUND, AND HOW
-----------------------
While optimising the judge for speed, the optimised implementation disagreed with the reference by
up to 4e-02 on a [0,1] scale -- far too much for float reassociation. The only behavioural
difference was length-sorted batching, so the reference itself was re-run under five batchings of
the SAME 480 prompts:

    batch=48, file order, re-run     max|diff| 0.000e+00   480/480 identical
    batch=48, reversed               max|diff| 0.000e+00   480/480 identical
    batch=16                         max|diff| 4.913e-02   396/480 identical
    batch=1  (no padding at all)     max|diff| 5.443e-02   315/480 identical
    batch=48, length-sorted          max|diff| 6.242e-02   322/480 identical

Given a batching the judge is deterministic. Change how much PADDING sits in a batch and a third of
the judgements move. Qwen3.5 is a gated-delta-net -- a linear-attention recurrence -- and left-pad
tokens run through that recurrence; the mask does not fully remove them.

WHY THIS MATTERS MORE THAN THE SPEED IT WAS FOUND WHILE CHASING
----------------------------------------------------------------
a04_full.npz and a04_core.npz were produced at batch 48 in file order. That is an unregistered
implementation choice, and every number this campaign has published rests on it. The question is not
whether the per-judgement values move -- they do, mean |delta| about 9e-03 -- but whether anything
CLAIMS-LEVEL moves once those values are averaged over ~16 criteria and turned into pairwise
concordances.

THE MEASUREMENT
---------------
Re-score the entire grid with length-sorted batching, which is maximally different from file order,
and recompute the three arm concordances and the core-minus-full gaps that every headline uses.

PRE-REGISTERED (fixed before the re-score ran)
-----------------------------------------------
W-BATCH-IMMATERIAL  every arm concordance moves by less than 0.005 and every gap by less than
                    0.005. The batching is a free choice and the stored tensors need no caveat.
W-BATCH-MATTERS     any arm or gap moves by 0.005 or more. Every published number acquires a
                    batching scope, and the tensors are one draw from a family.
"""
from __future__ import annotations
import argparse, json, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(_ROOT))
from covalx import load_join                      # noqa: E402
from covalx.judge import human_pairs              # noqa: E402
from covalx.stamp import stamp                    # noqa: E402

TOL = 0.005


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--out", default=str(_HERE / "results/r137_batch_gauge.json"))
    a = ap.parse_args()
    (_HERE / "results").mkdir(parents=True, exist_ok=True)

    src = (_ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/run.py").read_text()
    G = {"np": np}
    exec(src[src.index("FEWSHOT = ("):src.index("class Judge:")], G)
    build_prompt = G["build_prompt"]

    stored = {}
    for nm in ("full", "core"):
        z = np.load(_ROOT / f"E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_{nm}.npz",
                    allow_pickle=True)
        for m, s in zip(z["meta"], z["sat"]):
            pid, ci, lab = str(m).split("|")
            stored[(nm, pid, int(ci), lab)] = float(s)

    tasks, keys, meta = [], [], []
    for pid, comp, rub in load_join(str(_ROOT / "data/comparisons.jsonl"),
                                    str(_ROOT / "data/conversation_rubrics.jsonl")):
        reps = {r["response_index"]: (r["messages"][-1].get("content") or "")
                for r in comp["responses"]}
        prs = human_pairs((comp.get("metadata") or {}).get("assessments") or [])
        if not prs:
            continue
        cid = rub["conversation"]["id"]
        for nm, arm in (("full", "coval_full"), ("core", "coval_core")):
            for ci, it in enumerate(rub.get(arm) or []):
                c = (it.get("criterion") or "").strip()
                if not c:
                    continue
                s = [x["score"] for x in (it.get("scores") or [])]
                neg = bool(s) and float(np.mean(s)) < 0
                for lab, rep in reps.items():
                    if (nm, pid, ci, lab) in stored:
                        tasks.append(build_prompt(c, rep))
                        keys.append((nm, pid, ci, lab))
                        meta.append((nm, pid, ci, lab, neg))
        _ = cid
    print(f"{len(tasks):,} judgements aligned to the stored tensors", flush=True)

    from covalx.fastjudge import FastJudge
    fj = FastJudge(a.model, batch=a.batch)
    t0 = time.time()
    new = fj.score(tasks)
    dt = time.time() - t0
    print(f"re-scored in {dt/60:.1f} min at {len(tasks)/dt:.1f} judgements/s", flush=True)

    old = np.array([stored[k] for k in keys], dtype=np.float32)
    d = np.abs(new - old)
    print(f"per-judgement: max|diff| {d.max():.3e}  mean {d.mean():.3e}  "
          f"identical {int((d == 0).sum()):,}/{len(d):,}", flush=True)

    def arms(vals):
        acc = defaultdict(lambda: defaultdict(list))
        for (nm, pid, ci, lab, neg), v in zip(meta, vals):
            if nm == "core":
                acc[(pid, "core")][lab].append(float(v))
            else:
                acc[(pid, "full_equal")][lab].append(float(v))
                acc[(pid, "full_signed")][lab].append(1.0 - float(v) if neg else float(v))
        return acc

    P = {}
    for pid, comp, _rub in load_join(str(_ROOT / "data/comparisons.jsonl"),
                                     str(_ROOT / "data/conversation_rubrics.jsonl")):
        pr = human_pairs((comp.get("metadata") or {}).get("assessments") or [])
        if pr:
            P[pid] = pr

    def conc(acc, arm):
        g = t = 0
        for (pid, k), d2 in acc.items():
            if k != arm:
                continue
            s = {l: float(np.mean(v)) for l, v in d2.items() if v}
            for x, y in P.get(pid, ()):
                if x in s and y in s and s[x] != s[y]:
                    t += 1
                    g += s[x] > s[y]
        return g / t if t else float("nan")

    A_old, A_new = arms(old), arms(new)
    res, worst = {}, 0.0
    print(f"\n  {'arm':<14}{'stored batching':>18}{'length-sorted':>16}{'move':>10}")
    for arm in ("core", "full_equal", "full_signed"):
        o, n = conc(A_old, arm), conc(A_new, arm)
        res[arm] = {"stored": o, "resorted": n, "move": n - o}
        worst = max(worst, abs(n - o))
        print(f"  {arm:<14}{o:>18.4f}{n:>16.4f}{n-o:>+10.4f}")
    for g, x, y in (("core_minus_full_equal", "core", "full_equal"),
                    ("core_minus_full_signed", "core", "full_signed")):
        o = res[x]["stored"] - res[y]["stored"]
        n = res[x]["resorted"] - res[y]["resorted"]
        res[g] = {"stored": o, "resorted": n, "move": n - o}
        worst = max(worst, abs(n - o))
        print(f"  {g:<14}{o:>18.4f}{n:>16.4f}{n-o:>+10.4f}")

    world = "W-BATCH-MATTERS" if worst >= TOL else "W-BATCH-IMMATERIAL"
    conclusion = (
        f"The judge is deterministic given a batching and not across batchings: on 480 fixed "
        f"prompts, batch=1 disagrees with batch=48 on 165 of 480 judgements up to 5.4e-02, and "
        f"length-sorting disagrees on 158 up to 6.2e-02, because Qwen3.5's gated-delta recurrence "
        f"does not fully mask left-pad tokens. The stored tensors were produced at batch 48 in file "
        f"order, an unregistered implementation choice under every published number. Re-scoring the "
        f"whole grid with length-sorted batching moves each judgement by {d.mean():.3e} on average "
        f"and {d.max():.3e} at worst, and at the level claims actually live: "
        + "; ".join(f"{k} {v['stored']:.4f} -> {v['resorted']:.4f} ({v['move']:+.4f})"
                    for k, v in res.items())
        + f". Largest move {worst:.4f} against a pre-registered tolerance of {TOL}. WORLD: {world}. "
        + ("Every published number acquires a batching scope and the stored tensors are one draw "
           "from a family, not the value."
           if world == "W-BATCH-MATTERS" else
           "The per-judgement dependence averages out before it reaches any claim: over ~16 "
           "criteria and tens of thousands of ordered pairs, the arm concordances and their gaps "
           "hold inside the tolerance. The tensors need a footnote, not a re-run."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")
    Path(a.out).write_text(json.dumps(
        {"n_judgements": len(tasks), "seconds": dt, "per_judgement_max": float(d.max()),
         "per_judgement_mean": float(d.mean()), "n_identical": int((d == 0).sum()),
         "arms": res, "worst_move": float(worst), "tolerance": TOL,
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
