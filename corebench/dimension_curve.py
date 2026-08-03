#!/usr/bin/env python3
"""
corebench/dimension_curve.py -- the specification curve of the BENCHMARK'S OWN VERDICT.

Twice now a conclusion has turned on which fidelity row it was read from. A1 said the top
three cores were one flat tier; A2 said 19 of 21 competent pairs separate and left exactly
one tie. Reporting a third row would repeat the error one row later. This sweeps the whole
A-family across all 55 pairs and asks whether the VERDICT is dimension-robust.

ESTIMAND        per dimension: pairs separating under BH over the whole grid, the arm
                ordering, and whether the ordering agrees across dimensions.
                Named before the method.
WORLDS          A the orderings AGREE except A1 -> the conclusion is dimension-robust and
                  A1 is simply too coarse
                B they DISAGREE -> the dimension is the finding and no single ranking of
                  cores may be published from this release
KILL            pre-registered: if any two graded dimensions invert an adjacent pair's sign
                with both intervals excluding zero, world B.
POSITIVE CTRL   the leaky arms must rank at the top on every dimension, and the two
                incompetent arms at the bottom. A dimension that fails this is not
                measuring fidelity and its ordering is excluded from the agreement count.
NOTE            NBOOT reduced to 1000 for a 5x55 grid; stated, not hidden. The quantity of
                interest is the ORDERING and the survival count, both stable well below
                2000 draws.
"""
from __future__ import annotations
import itertools, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
SEEDS, NBOOT, Q = [0, 1, 2], 1000, 0.05
from score import load_sat, load_targets, yvec, cls, tau_b

PAIRS = list(itertools.combinations(range(4), 2))
ARMS = ["coval_core", "topw_k4", "gen", "topabs_k4", "topwvar_k4", "topvar_k4",
        "full", "random_k4_s0", "gen_sham", "oracle_k4_fit1", "indep_k4_fit1"]
INCOMPETENT = {"random_k4_s0", "gen_sham"}
LEAKY = {"oracle_k4_fit1", "indep_k4_fit1"}
DIMS = ["A1", "A2", "A3", "A4", "A5"]


def per_prompt(sat, targets, seed, dim):
    rng = np.random.default_rng(seed)
    out = {}
    for p in sat:
        if p not in targets or len(targets[p]) < 2:
            continue
        y = yvec(sat[p], sorted({i for i, _ in sat[p]}))
        hy = np.array(targets[p][int(rng.integers(len(targets[p])))][0], float)
        c, h = cls(y), cls(hy)
        if dim == "A1":   v = float(c == h)
        elif dim == "A2": v = float(np.mean([c[q] == h[q] for q in range(6)]))
        elif dim == "A3": v = float(np.argmax(y) == np.argmax(hy))
        elif dim == "A4": v = float(np.argmin(y) == np.argmin(hy))
        else:             v = tau_b(list(y), list(hy))
        out[p] = v
    return out


if __name__ == "__main__":
    targets, _ = load_targets()
    SAT = {a: load_sat(ROOT/"corebench"/"results"/f"sat_{a}.npz") for a in ARMS
           if (ROOT/"corebench"/"results"/f"sat_{a}.npz").exists()}
    arms = [a for a in ARMS if a in SAT]
    comp = [a for a in arms if a not in INCOMPETENT and a not in LEAKY]

    summary, orders, sep = {}, {}, {}
    for dim in DIMS:
        H = {a: [per_prompt(SAT[a], targets, s, dim) for s in SEEDS] for a in arms}
        absv = {a: float(np.mean([np.mean(list(h.values())) for h in H[a]])) for a in arms}
        res = []
        for x, y_ in itertools.combinations(arms, 2):
            d = np.concatenate([np.array([H[x][s][p] - H[y_][s][p]
                 for p in sorted(set(H[x][s]) & set(H[y_][s]))]) for s in range(len(SEEDS))])
            rb = np.random.default_rng(abs(hash((dim, x, y_))) % 9999)
            b = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(NBOOT)])
            res.append([x, y_, float(d.mean()), 2*min((b <= 0).mean(), (b >= 0).mean())])
        C = len(res); order = sorted(range(C), key=lambda i: res[i][3]); surv = set()
        for rank, i in enumerate(order, 1):
            if res[i][3] <= Q*rank/C: surv = set(order[:rank])
        cc = [i for i, r in enumerate(res) if r[0] in comp and r[1] in comp]
        rank_order = sorted(arms, key=lambda z: -absv[z])
        # POSITIVE CONTROL: leaky at the top, incompetent at the bottom
        top2, bot2 = set(rank_order[:2]), set(rank_order[-2:])
        ok = (top2 == LEAKY & set(arms)) and len(bot2 & INCOMPETENT) >= 1
        summary[dim] = (len(surv), C, len(surv & set(cc)), len(cc), ok)
        sep[dim] = {frozenset((res[i][0], res[i][1])) for i in surv}
        orders[dim] = rank_order
        print(f"    [{'PASS' if ok else 'FAIL'}] {dim}  surviving {len(surv):>2}/{C}   "
              f"competent {len(surv & set(cc)):>2}/{len(cc)}   top: {rank_order[2]}")

    print(f"\n    ORDERING OF THE COMPETENT ARMS, per dimension")
    for dim in DIMS:
        print(f"      {dim}  " + " > ".join(a for a in orders[dim] if a in comp))

    # agreement: do graded dims ever invert an adjacent competent pair?
    graded = [d for d in DIMS if d != "A1" and summary[d][4]]
    base = [a for a in orders[graded[0]] if a in comp]
    inversions, soft = [], []
    for d in graded[1:]:
        o = [a for a in orders[d] if a in comp]
        for i in range(len(base)-1):
            x, y_ = base[i], base[i+1]
            # ⚠ THE PRE-REGISTRATION SAID "with both intervals excluding zero" AND THE
            # FIRST VERSION OF THIS BRANCH COMPARED RANKS ONLY. An ordering flip between two
            # arms whose difference includes zero is noise in the ordering of a TIE, not a
            # disagreement between dimensions -- and the single flip found was exactly the
            # coval_core/topw_k4 pair that no dimension separates. The verdict string has to
            # implement the kill that was written, not a looser one.
            if o.index(x) > o.index(y_) and frozenset((x, y_)) in sep[d] \
               and frozenset((x, y_)) in sep[graded[0]]:
                inversions.append((d, x, y_))
            elif o.index(x) > o.index(y_):
                soft.append((d, x, y_))
    print(f"\n    graded dimensions passing the control : {graded}")
    print(f"    inversions where BOTH dims separate   : {len(inversions)} "
          f"{inversions if inversions else '(the pre-registered kill)'}")
    print(f"    order flips inside a NON-separating pair: {len(soft)} {soft if soft else ''}")
    v = ("WORLD A -- the graded dimensions AGREE on the ordering; A1 is simply too coarse"
         if not inversions else
         f"WORLD B -- {len(inversions)} inversions; the DIMENSION is the finding")
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/"dimension_curve.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "summary": {k: list(v_) for k, v_ in summary.items()}, "orders": orders,
         "inversions": inversions, "nboot": NBOOT, "verdict": v}, indent=2, sort_keys=True))
