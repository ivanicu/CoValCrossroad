"""r29 -- Is the gold model trustworthy on responses it was not trained around?

The question
------------
r12 is the most anomalous result in this repository. Grading the four RELEASED
candidates with their own rubric beats an unrelated rubric by +0.102. Grading
FRESH, rubric-blind responses to the same prompts, the advantage does not shrink
-- it inverts, to -0.042 [-0.068, -0.015].

r12 already rules out the confound that killed r09: its yardstick is the 0.8B
gold head, a different backbone from the judge, so this is not entry 4 again.
What it does not rule out is DISTRIBUTIONAL. The gold head was fitted on human
rankings of the released responses. The fresh set is generated at temperature
0.9 by a different model. If the gold is simply unreliable off that
distribution, then r12's inversion is a fact about the yardstick and not about
rubrics, and the repository's strangest claim is uninterpretable.

There are no human labels on the fresh set, so the gold cannot be validated
there directly. But it can be validated INDIRECTLY, and without any labels at
all, by asking how much its verdict depends on which half of the training data
it happened to see.

Design
------
Three disjoint folds of PROMPTS.

    fold 1 -> train gold head A
    fold 2 -> train gold head B          (disjoint human rankings)
    fold 3 -> evaluate both, on responses NEITHER head was trained around

On fold 3, score every ORIGINAL response and every FRESH response with A and
with B, and measure their within-prompt pairwise concordance: of all pairs of
responses to the same prompt, how often do A and B put them in the same order?

  Two heads fitted on disjoint halves of the same signal should agree
  substantially wherever that signal is present, and should agree at chance
  wherever it is absent.

Prediction matrix -- and both branches are informative, which is the point:

    world                             concordance ORIGINAL   concordance FRESH
    gold is stable off-distribution          high                  high
    gold is OOD on fresh                     high                  near 0.5

If concordance collapses on the fresh set, r12 measured the gold's confusion and
must be withdrawn to a statement about released responses only. If it holds,
r12's inversion survives its last named confound and becomes the sharpest open
question here.

Note on what this does NOT establish. Two heads agreeing is not two heads being
right; they share an architecture, an embedding model and a feature design, so a
shared bias survives this test intact. It is a RELIABILITY diagnostic, and
reliability is necessary for validity and does not imply it. On the original
fold-3 responses there ARE human labels, so absolute accuracy is reported there
as an anchor -- concordance can then be read against a case where the truth is
known.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join, human_pairs  # noqa: E402

M08 = os.environ.get("COVALX_MODEL_08B",
                     "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
                     "Qwen3.5-0.8B-Base")


def _r08():
    spec = importlib.util.spec_from_file_location(
        "r08", _ROOT / "01_object_and_rebuild/r08_gold_preference/run.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def feats(E, texts):
    L = np.array([[len(t), len(t.split())] for t in texts], dtype=float)
    L = (L - L.mean(0)) / (L.std(0) + 1e-6)
    return np.hstack([E, L])


def concordance(sa, sb):
    """Within-prompt pairwise agreement between two scorers. 0.5 = chance."""
    ok = tot = 0
    for i, j in combinations(range(len(sa)), 2):
        if abs(sa[i] - sa[j]) < 1e-12 or abs(sb[i] - sb[j]) < 1e-12:
            continue
        tot += 1
        ok += int((sa[i] > sa[j]) == (sb[i] > sb[j]))
    return ok, tot


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--generations", type=Path,
                   default=_ROOT / "02_attribution_under_attack/r12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--out", type=Path, default=_RES / "r29_gold_ood.json")
    p.add_argument("--boot", type=int, default=4000)
    a = p.parse_args()

    if not a.generations.exists():
        raise SystemExit(
            f"missing {a.generations}\n"
            "  r12 must be re-run first: its original run did not persist the fresh\n"
            "  generations, so this diagnostic has nothing to evaluate. Regenerating\n"
            "  produces a DIFFERENT sample at temperature 0.9, which is acceptable for\n"
            "  a reliability diagnostic but means this is not a re-analysis of r12's\n"
            "  exact responses -- state that wherever the result is used.")
    gen = json.loads(a.generations.read_text())
    orig, fresh = gen["original"], gen["fresh"]
    pids = gen["prompt_ids"]

    # Drop prompts carrying an empty response. Generation at temperature 0.9
    # produced exactly one empty string in 1,000, and an empty string's
    # mean-pooled embedding is degenerate -- it is not a response the gold model
    # can be right or wrong about, so including it would put a coin flip inside a
    # concordance measure. One prompt out of 250; the count is printed rather
    # than the exclusion being silent, because a filter is a scope claim.
    bad = [k for k in range(len(orig))
           if any(not t.strip() for t in orig[k]) or any(not t.strip() for t in fresh[k])]
    if bad:
        print(f"  excluding {len(bad)} prompt(s) with an empty response: "
              f"{[pids[k] for k in bad][:3]}{'...' if len(bad) > 3 else ''}")
        keepk = [k for k in range(len(orig)) if k not in set(bad)]
        orig = [orig[k] for k in keepk]
        fresh = [fresh[k] for k in keepk]
        pids = [pids[k] for k in keepk]
    n = len(orig)

    joined = {pid: comp for pid, comp, _rub in load_join(a.comparisons, a.rubrics)}
    r08 = _r08()

    # ---- disjoint halves of ANNOTATORS, not of prompts -------------------
    # The first design split PROMPTS three ways: head A on fold 1, head B on
    # fold 2, both evaluated on fold 3. That starved both heads. Each saw ~83
    # prompts where r08 used 968, and the anchor said so immediately -- held-out
    # human accuracy came back 0.5141 and 0.4823, i.e. AT CHANCE, one of them
    # below it. Two heads that cannot predict human preference where humans
    # actually labelled cannot be used to diagnose anything about a distribution
    # where they did not.
    #
    # Splitting by ANNOTATOR instead: both heads see every prompt, but disjoint
    # halves of the human labels. That isolates exactly what this diagnostic
    # needs -- how much the verdict depends on WHICH half of the human signal a
    # head saw -- without halving the prompts either head learns from. Every
    # prompt is then usable for evaluation, so n goes from 83 to all of them.
    rng = np.random.default_rng(20260728)
    all_ann = sorted({asm.get("annotator_id")
                      for comp in joined.values()
                      for asm in comp["metadata"]["assessments"]
                      if asm.get("annotator_id")})
    perm = rng.permutation(len(all_ann))
    side = {all_ann[i]: int(perm[j] % 2) for j, i in enumerate(range(len(all_ann)))}
    f3 = list(range(n))
    print(f"prompts: {n}   annotators: {len(all_ann):,} split "
          f"{sum(1 for v in side.values() if v==0)} / "
          f"{sum(1 for v in side.values() if v==1)}   evaluated on all {n} prompts\n")

    # ---- embed every response once --------------------------------------
    flat_o = [t for k in range(n) for t in orig[k]]
    flat_f = [t for k in range(n) for t in fresh[k]]
    print(f"embedding {len(flat_o):,} original + {len(flat_f):,} fresh responses...",
          flush=True)
    Eo = r08.embed(flat_o, model_dir=M08)
    Ef = r08.embed(flat_f, model_dir=M08)
    mu, sd = Eo.mean(0), Eo.std(0)
    Xo = feats((Eo - mu) / (sd + 1e-6), flat_o)
    Xf = feats((Ef - mu) / (sd + 1e-6), flat_f)
    no, nf = len(orig[0]), len(fresh[0])
    torch.cuda.empty_cache()

    # ---- train one head per fold on that fold's HUMAN pairs -------------
    # human_pairs() yields RESPONSE LABELS ("A"/"B"/...), not positions into the
    # response list.  The first version of this round indexed Xo with them
    # directly and died on `'>=' not supported between str and int`.  It failed
    # loudly, which was luck: had the labels been integers 0-3 in a different
    # order from `comp["responses"]`, every pair would have silently referred to
    # the wrong response and the concordance would have been noise reported as a
    # measurement.  The order in `orig[k]` is the order of comp["responses"], so
    # the map is recoverable here rather than needing another regeneration.
    labpos = {}
    for k in range(n):
        comp = joined.get(pids[k])
        if comp:
            labpos[k] = {r["response_index"]: i for i, r in enumerate(comp["responses"])}

    heads = {}
    for fid in (0, 1):
        D, y = [], []
        for k in range(n):
            comp = joined.get(pids[k])
            if not comp:
                continue
            lp = labpos.get(k, {})
            mine = [asm for asm in comp["metadata"]["assessments"]
                    if side.get(asm.get("annotator_id")) == fid]
            if not mine:
                continue
            for xl, zl in human_pairs(mine):
                x, z = lp.get(xl), lp.get(zl)
                if x is None or z is None or x >= no or z >= no:
                    continue
                D.append(Xo[k * no + x] - Xo[k * no + z]); y.append(1)
                D.append(Xo[k * no + z] - Xo[k * no + x]); y.append(0)
        D, y = np.array(D), np.array(y)
        heads[fid] = r08.fit_logistic(D, y)
        print(f"  head {fid}: trained on {len(y)//2:,} human pairs from fold {fid}")

    wa, wb = heads[0], heads[1]

    # ---- evaluate BOTH heads on fold 3, on both response sets -----------
    rows = {}
    for name, X, m in (("ORIGINAL", Xo, no), ("FRESH", Xf, nf)):
        per = []
        for k in f3:
            blk = X[k * m:(k + 1) * m]
            ok, tot = concordance(blk @ wa, blk @ wb)
            if tot:
                per.append(ok / tot)
        per = np.array(per)
        bs = np.array([per[rng.integers(0, len(per), len(per))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        rows[name] = {"concordance": float(per.mean()),
                      "ci": [float(lo), float(hi)], "prompts": int(len(per))}

    # ---- anchor: absolute accuracy where humans DID label ---------------
    anchor = {}
    for tag, w in (("head_A", wa), ("head_B", wb)):
        ok = tot = 0
        for k in f3:
            comp = joined.get(pids[k])
            if not comp:
                continue
            lp = labpos.get(k, {})
            s = Xo[k * no:(k + 1) * no] @ w
            for xl, zl in human_pairs(comp["metadata"]["assessments"]):
                x, z = lp.get(xl), lp.get(zl)
                if x is None or z is None or x >= no or z >= no:
                    continue
                tot += 1; ok += int(s[x] > s[z])
        anchor[tag] = ok / tot if tot else float("nan")

    print(f"\n{'response set':14s} {'A-B concordance':>17} {'95% CI':>22} {'prompts':>8}")
    for name in ("ORIGINAL", "FRESH"):
        r = rows[name]
        print(f"{name:14s} {r['concordance']:>17.4f} "
              f"{f'[{r[chr(99)+chr(105)][0]:.4f},{r[chr(99)+chr(105)][1]:.4f}]':>22} "
              f"{r['prompts']:>8}")
    print(f"\n  anchor, held-out human accuracy on fold 3 ORIGINAL: "
          f"A={anchor['head_A']:.4f}  B={anchor['head_B']:.4f}")

    drop = rows["ORIGINAL"]["concordance"] - rows["FRESH"]["concordance"]
    fresh_near_chance = rows["FRESH"]["ci"][1] < 0.60
    # THE ANCHOR GATES EVERYTHING BELOW IT. The first version computed this
    # number, printed it, and then wrote a verdict that never consulted it --
    # the third time in one day a conclusion string outranked its own control.
    # If the heads cannot beat chance on ORIGINAL responses, where humans DID
    # label, then their agreement on FRESH responses is two broken instruments
    # concurring and says nothing about the gold's transportability.
    anchor_ok = min(anchor.values()) > 0.55
    print(f"  concordance drop ORIGINAL -> FRESH: {drop:+.4f}")

    verdict = (
        f"UNVERIFIED -- THE DIAGNOSTIC IS UNFIT. Held-out human accuracy of the two "
        f"heads on ORIGINAL responses is {anchor['head_A']:.4f} and "
        f"{anchor['head_B']:.4f}, at or below chance, so neither head predicts human "
        "preference even where humans labelled. Their concordance on the fresh set is "
        "therefore two uninformative scorers agreeing, and says nothing about whether "
        "the gold transports. This is NOT evidence that the gold is fine off "
        "distribution, and it is NOT evidence that it is broken -- it is an instrument "
        "that failed its positive control, which is silence, not an acquittal."
        if not anchor_ok else
        "GOLD IS OOD ON FRESH: two heads fitted on disjoint halves of the same human "
        f"signal agree at {rows['ORIGINAL']['concordance']:.3f} on released responses and "
        f"{rows['FRESH']['concordance']:.3f} on generated ones, the latter near chance. "
        "r12's inversion is then a fact about the yardstick and must be withdrawn to a "
        "statement about released responses only."
        if fresh_near_chance else
        "GOLD IS STABLE OFF-DISTRIBUTION: the two independently-fitted heads agree about "
        f"as well on generated responses ({rows['FRESH']['concordance']:.3f}) as on "
        f"released ones ({rows['ORIGINAL']['concordance']:.3f}), so r12's inversion "
        "survives its last named confound. RELIABILITY only -- the two heads share an "
        "architecture and an embedding model, so a bias common to both is invisible here.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts_total": n, "eval_prompts": len(f3), "concordance": rows,
         "held_out_human_accuracy_original": anchor, "drop": float(drop),
         "verdict": verdict,
         "note": "label-free reliability diagnostic for r12's yardstick. Three disjoint "
                 "prompt folds; two gold heads fitted on folds 1 and 2; both evaluated "
                 "on fold 3, which neither saw. Reliability is necessary for validity "
                 "and does not imply it: a bias shared by both heads survives this test. "
                 "The fresh generations are a NEW temperature-0.9 sample, not r12's "
                 "exact responses, because r12 did not persist them."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
