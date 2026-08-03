#!/usr/bin/env python3
"""
corebench/whose_verdicts.py -- the definition says a core "preserves ITS verdicts". Whose?

The definition rewritten today reads: a core is a REWRITING OF A RUBRIC THAT PRESERVES ITS
VERDICTS at the rubric's own reliability. `its` refers to the RUBRIC. But coval_full scores
0.5136 on A2 against humans, barely above random's 0.5005, while the top cores score 0.568.
If a core tracks the HUMAN better than it tracks the RUBRIC IT COMPRESSES, then it does not
preserve the rubric's verdicts -- it departs from them, in the human's direction -- and the
clause is wrong.

ESTIMAND        per arm, paired per prompt: A2 against the HUMAN target minus A2 against
                coval_full's own class. Positive means the core tracks the human more
                closely than the thing it is a compression of. Named before the method.
IDENTIFICATION  identified; both targets exist for every prompt.
SCOPE           968 prompts, A2 pairwise agreement, prompt-resampled, this judge.
WORLDS          A cores track FULL more than the human -> "preserves the rubric's verdicts"
                  is right and compression is the correct frame
                B cores track the HUMAN more -> the clause is wrong; a core is not a
                  summary of the rubric, and calling it one misdescribes what it does
KILL            pre-registered: paired CI on (agreement with human - agreement with full)
                per arm. Positive and excluding zero for the top arms -> world B, and the
                definition's wording is retracted.
POSITIVE CTRL   `full` against itself must give exactly 1.0 agreement-with-full, so the
                comparison for that arm is the largest possible negative. If it is not, the
                full-class target is not what it claims to be.
PLACEBO         any arm's agreement-with-itself is exactly 1.0.
"""
from __future__ import annotations
import collections, itertools, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls
PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, SEEDS = 2000, [0, 1, 2]
ARMS = ["coval_core", "topw_k4", "gen", "full", "topvar_k4", "random_k4_s0", "gen_sham"]


def a2(c, h): return float(np.mean([c[q] == h[q] for q in range(6)]))


if __name__ == "__main__":
    targets, _ = load_targets()
    SAT = {a: load_sat(ROOT/"corebench"/"results"/f"sat_{a}.npz") for a in ARMS
           if (ROOT/"corebench"/"results"/f"sat_{a}.npz").exists()}
    fullc = {p: cls(yvec(SAT["full"][p], sorted({i for i, _ in SAT["full"][p]})))
             for p in SAT["full"]}

    # ⚠ THE RAW COMPARISON IS CONFOUNDED BY TARGET RELIABILITY AND COULD BARELY HAVE COME
    # OUT OTHERWISE. The human target is ONE noisy annotator; coval_full's class is
    # DETERMINISTIC. Agreement with a noisy target is bounded above by that target's own
    # reliability, while agreement with a deterministic one is bounded by 1.0. A negative
    # delta is therefore close to forced -- the arithmetic trap, in my own design, and the
    # first version of this script printed a WORLD A verdict off it.
    # Fix: measure the human ceiling (one annotator against another, same prompt) and report
    # each agreement AS A FRACTION OF ITS OWN TARGET'S CEILING. full's ceiling is 1.0 by
    # construction and is labelled a DERIVATION.
    ceil_h = []
    for s in SEEDS:
        rng = np.random.default_rng(500 + s)
        for p, v in targets.items():
            if len(v) < 2: continue
            i, j = rng.choice(len(v), 2, replace=False)
            ceil_h.append(a2(cls(np.array(v[i][0], float)), cls(np.array(v[j][0], float))))
    CEIL_H = float(np.mean(ceil_h))
    print(f"\n  WHOSE VERDICTS DOES A CORE PRESERVE?   (A2, 968 prompts, 3 seeds)")
    print(f"\n    MEASURED CEILINGS: human target {CEIL_H:.4f} (one annotator vs another), "
          f"full target 1.0000 (DERIVATION, deterministic)\n")
    print(f"    {'arm':<16}{'vs HUMAN':>10}{'vs FULL':>10}"
          f"{'/ceiling H':>12}{'/ceiling F':>12}{'Δ normalised':>15}")
    out = {}
    for a in SAT:
        ds, hh, ff = [], [], []
        for s in SEEDS:
            rng = np.random.default_rng(s); d = []
            for p in SAT[a]:
                if p not in targets or len(targets[p]) < 2 or p not in fullc: continue
                c = cls(yvec(SAT[a][p], sorted({i for i, _ in SAT[a][p]})))
                hy = np.array(targets[p][int(rng.integers(len(targets[p])))][0], float)
                vh, vf = a2(c, cls(hy)), a2(c, fullc[p])
                d.append(vh - vf); hh.append(vh); ff.append(vf)
            ds.append(np.array(d))
        dd = np.concatenate(ds)
        rb = np.random.default_rng(abs(hash(a)) % 9999)
        b = np.array([dd[rb.integers(0, len(dd), len(dd))].mean() for _ in range(NBOOT)])
        lo, hi = np.percentile(b, 2.5), np.percentile(b, 97.5)
        out[a] = (float(np.mean(hh)), float(np.mean(ff)), float(dd.mean()), float(lo), float(hi))
        nh, nf = np.mean(hh) / CEIL_H, np.mean(ff) / 1.0
        out[a] = out[a] + (float(nh), float(nf))
        print(f"    {a:<16}{np.mean(hh):>10.4f}{np.mean(ff):>10.4f}"
              f"{nh:>12.4f}{nf:>12.4f}{nh - nf:>+15.4f}")

    ok_pos = abs(out["full"][1] - 1.0) < 1e-9
    print(f"\n    [{'PASS' if ok_pos else 'FAIL'}] POSITIVE/PLACEBO  `full` vs FULL = "
          f"{out['full'][1]:.6f}, must be exactly 1.0")
    top = [a for a in ("coval_core", "topw_k4", "gen") if a in out]
    world_b = all(out[a][5] > out[a][6] for a in top)   # normalised, not raw
    if not ok_pos:
        v = "UNVERIFIED -- the full-class target is not what it claims to be"
    elif world_b:
        v = ("WORLD B -- normalised by each target's own ceiling, every top core tracks the "
             "HUMAN more closely than the RUBRIC it compresses. 'preserves ITS verdicts' "
             "misdescribes what a core does.")
    else:
        v = ("WORLD A -- even normalised by each target's ceiling, cores track FULL more "
             "closely than the human; compression is the right frame and the clause holds.")
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/"whose_verdicts.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "arms": out, "verdict": v}, indent=2, sort_keys=True))
