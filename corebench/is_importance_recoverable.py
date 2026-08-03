#!/usr/bin/env python3
"""
corebench/is_importance_recoverable.py -- is the 45% gap structural, or just my generator?

The price-of-annotation round left an open end it named itself: the 55% share is measured
against ONE annotation-free method, and nothing bounds what annotation-free methods can do.

There is a bound, and it does not require inventing better generators. The rule that works
ranks by MEAN HUMAN IMPORTANCE. If that quantity is PREDICTABLE from the rubric text and the
responses, then some annotation-free rule can reconstruct it and the 45% is a failure of my
generator. If it is NOT predictable, the gap is structural: no amount of cleverness applied to
the text recovers what annotators supplied.

ESTIMAND        held-out R² and Pearson r for predicting a criterion's MEAN IMPORTANCE from
                features computable WITHOUT any human importance data. Split BY PROMPT.
                Named before the method.
⚠ FEATURE HYGIENE IS THE WHOLE DESIGN. Any feature derived from the importance scores --
  their sd, their count, their sign -- leaks the target. The admissible set is: satisfaction
  on the four responses (judged), criterion text length, position in the rubric, and the
  prompt's criterion count. Nothing else.
WORLDS          A predictable (held-out R² clearly > 0) -> a better annotation-free rule
                  exists and 55% understates what is achievable
                B NOT predictable -> the 45% is STRUCTURAL and no text-only method closes it
KILL            pre-registered: held-out R² CI includes 0 -> world B.
POSITIVE CTRL   a LEAKY arm that includes the importance sd must predict well. If even that
                fails, the regression is broken and neither arm is readable.
NEGATIVE CTRL   shuffle the target across criteria within the training set; held-out R² must
                collapse to ~0.
PLACEBO         predict importance from importance: R² exactly 1.
SEEDS           5 prompt splits.
"""
from __future__ import annotations
import collections, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"corebench"))
from score import load_sat
L, SEEDS = "ABCD", [0, 1, 2, 3, 4]
FULL_NPZ = ROOT/("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                 "/R04_rebuild_satisfaction/results/a04_full.npz")

def r2(y, p):
    ss = ((y - y.mean())**2).sum()
    return float(1 - ((y - p)**2).sum()/ss) if ss > 0 else float("nan")

def fit_predict(Xtr, ytr, Xte):
    Xtr = np.c_[Xtr, np.ones(len(Xtr))]; Xte = np.c_[Xte, np.ones(len(Xte))]
    w = np.linalg.solve(Xtr.T@Xtr + 1.0*np.eye(Xtr.shape[1]), Xtr.T@ytr)
    return Xte@w

if __name__ == "__main__":
    from covalx.judge import load_join
    joined = load_join(ROOT/"data"/"comparisons.jsonl", ROOT/"data"/"conversation_rubrics.jsonl")
    sat = load_sat(FULL_NPZ)
    rows = []
    for pid, _pr, r in joined:
        items = r.get("coval_full") or []
        if pid not in sat or not items: continue
        ok = [i for i in range(len(items)) if all(sat[pid].get((i,x)) is not None for x in L)]
        for i in ok:
            sc = [s["score"] for s in items[i].get("scores") or []]
            if not sc: continue
            s4 = np.array([sat[pid][(i,x)] for x in L], float)
            txt = items[i]["criterion"]
            rows.append((pid,
                # DEPLOYABLE ONLY -- nothing derived from the importance scores
                [np.var(s4), np.mean(s4), s4.max()-s4.min(), len(txt.split()),
                 len(txt), i, len(ok)],
                float(np.mean(sc)), float(np.std(sc))))
    pids = sorted({r[0] for r in rows})
    X = np.array([r[1] for r in rows]); Y = np.array([r[2] for r in rows])
    SD = np.array([r[3] for r in rows]); P = np.array([r[0] for r in rows])
    print(f"\n  IS MEAN IMPORTANCE RECOVERABLE FROM TEXT + RESPONSES?")
    print(f"    {len(rows)} criteria in {len(pids)} prompts | 7 deployable features | "
          f"5 prompt splits\n")
    res = collections.defaultdict(list)
    for s in SEEDS:
        rng = np.random.default_rng(s); pr = rng.permutation(pids); h = len(pr)//2
        tr = np.isin(P, pr[:h]); te = ~tr
        Xs = (X - X[tr].mean(0)) / (X[tr].std(0) + 1e-9)
        res["deployable"].append(r2(Y[te], fit_predict(Xs[tr], Y[tr], Xs[te])))
        res["r"].append(float(np.corrcoef(Y[te], fit_predict(Xs[tr], Y[tr], Xs[te]))[0,1]))
        XL = np.c_[Xs, (SD - SD[tr].mean())/(SD[tr].std()+1e-9)]     # POSITIVE: leaky
        res["LEAKY(+sd)"].append(r2(Y[te], fit_predict(XL[tr], Y[tr], XL[te])))
        ysh = Y[tr].copy(); rng.shuffle(ysh)                          # NEGATIVE
        res["shuffled y"].append(r2(Y[te], fit_predict(Xs[tr], ysh, Xs[te])))
        res["PLACEBO(y~y)"].append(r2(Y[te], fit_predict(Y[tr,None], Y[tr], Y[te,None])))
    for k in ("deployable","r","LEAKY(+sd)","shuffled y","PLACEBO(y~y)"):
        v = np.array(res[k])
        print(f"    {k:<15} mean {v.mean():>8.4f}   [{v.min():>7.4f}, {v.max():>7.4f}]")
    d = np.array(res["deployable"])
    ok_pos = np.mean(res["LEAKY(+sd)"]) > np.mean(d)
    ok_neg = abs(np.mean(res["shuffled y"])) < 0.02
    ok_pla = abs(np.mean(res["PLACEBO(y~y)"]) - 1.0) < 1e-6
    print(f"\n    [{'PASS' if ok_pos else 'FAIL'}] POSITIVE the leaky arm predicts better")
    print(f"    [{'PASS' if ok_neg else 'FAIL'}] NEGATIVE shuffled target collapses to ~0")
    print(f"    [{'PASS' if ok_pla else 'FAIL'}] PLACEBO  y from y gives R² = 1")
    v = ("WORLD B -- NOT RECOVERABLE. The 45% is STRUCTURAL: mean importance is not a function "
         "of the text or the responses, so no text-only rule reconstructs it."
         if d.max() <= 0.02 else
         f"WORLD A -- partially recoverable, held-out R² up to {d.max():.4f}")
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/"importance_recoverable.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "r2_deployable": list(d), "r": res["r"], "leaky": res["LEAKY(+sd)"],
         "shuffled": res["shuffled y"], "verdict": v}, indent=2, sort_keys=True))
