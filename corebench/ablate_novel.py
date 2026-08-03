#!/usr/bin/env python3
"""
corebench/ablate_novel.py -- is the NOVEL 40% of the released core doing work?

40.3% of coval_core's criteria have no counterpart in coval_full above similarity 0.60.
Every rule in this benchmark selects FROM full, so nothing tested so far can say whether
that novel content earns its place. This asks directly, and it costs no GPU: the incumbent's
satisfactions are already judged, so an ablation is a re-index.

⚠ THE ABLATION ALONE WOULD MEASURE k, NOT NOVELTY. Dropping the novel criteria shrinks the
core from ~4 to ~2.4, and a smaller core scores differently for reasons that have nothing to
do with what was dropped. So the comparison arm is a SIZE-MATCHED SHAM: remove the same
NUMBER of criteria, chosen at random, from the same prompt. The estimand is the difference
between those two removals, not between ablated and whole.

ESTIMAND        A1(core minus its NOVEL criteria) - A1(core minus an equal number of RANDOM
                criteria), paired over prompts, averaged over sham draws. Named first.
IDENTIFICATION  identified; both arms are re-indexings of the same judged satisfactions.
SCOPE           population : prompts whose core has >=1 novel and >=1 traceable criterion
                instrument : the same judged sat as row 0
                baseline   : the size-matched random removal
                regime     : novelty threshold swept, k as it falls out
WORLDS          W1 novel criteria carry MORE than random ones -> removing them hurts more
                W2 they carry the SAME -> indistinguishable from the sham
                W3 they carry LESS -> removing them hurts less, i.e. they are noise
KILL            pre-registered: paired CI on (novel-removal - random-removal). Includes
                zero -> W2, and the round says so.
POSITIVE CTRL   remove EVERYTHING: the core collapses to an empty sum, every class becomes
                the all-ties class, and A1 must fall to the rate of exact ties in the
                target. If it does not, the ablation is not ablating.
PLACEBO         remove NOTHING from both arms -> difference exactly 0.0000.
SHAM            the size-matched random removal IS the comparison arm, drawn >=5 times.
SPECIFICATION   novelty threshold swept over 0.50/0.60/0.70/0.80 -- the 0.60 in the headline
                is a choice, and a choice reported at one value is a cell.
SEEDS           3 held-out draws x 5 sham draws.
"""
from __future__ import annotations
import collections, difflib, itertools, json, hashlib, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
SEEDS, NSHAM, THRESH = [0, 1, 2], 5, [0.50, 0.60, 0.70, 0.80]
from score import cls, load_sat, load_targets


def yv(sat_p, idxs):
    return np.array([sum(sat_p.get((i, x), 0.0) for i in idxs) for x in L])


def main():
    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    core_t = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _q, r in joined}
    full_t = {p: [i["criterion"] for i in (r.get("coval_full") or [])] for p, _q, r in joined}
    sat = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    targets, _ = load_targets()

    sims = {}
    for p, cs in core_t.items():
        f = full_t.get(p, [])
        sims[p] = [max((difflib.SequenceMatcher(None, c, z).ratio() for z in f), default=0.0)
                   for c in cs]

    def hits(pid_sel, seed):
        rng = np.random.default_rng(seed)
        out = {}
        for p, sel in pid_sel.items():
            v = targets[p]
            hy = np.array(v[int(rng.integers(len(v)))][0], float)
            out[p] = float(cls(yv(sat[p], sel)) == cls(hy))
        return out

    print("\n  is the novel content doing work?  (size-matched ablation, 0 judge calls)\n")
    print(f"    {'thresh':>8}{'prompts':>9}{'novel k':>9}{'Δ novel−random':>17}{'95% CI':>22}")
    art = {}
    for th in THRESH:
        pids = [p for p in sat if p in targets and len(targets[p]) >= 2
                and p in sims and len(sims[p]) >= 2
                and 0 < sum(s < th for s in sims[p]) < len(sims[p])]
        if not pids:
            continue
        novel_sel, nnov = {}, []
        for p in pids:
            idx = list(range(len(sims[p])))
            nov = [i for i in idx if sims[p][i] < th]
            novel_sel[p] = [i for i in idx if i not in nov]
            nnov.append(len(nov))
        ds = []
        for s in SEEDS:
            hn = hits(novel_sel, s)
            for sh in range(NSHAM):
                rr = np.random.default_rng(900 + 17 * s + sh)
                rand_sel = {}
                for p in pids:
                    idx = list(range(len(sims[p])))
                    drop = set(rr.choice(idx, sum(1 for i in idx if sims[p][i] < th),
                                         replace=False))
                    rand_sel[p] = [i for i in idx if i not in drop]
                hr = hits(rand_sel, s)
                ds.append(np.array([hn[p] - hr[p] for p in pids]))
        d = np.concatenate(ds)
        rb = np.random.default_rng(3)
        b = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(2000)])
        lo, hi = np.percentile(b, 2.5), np.percentile(b, 97.5)
        art[str(th)] = [float(d.mean()), float(lo), float(hi), len(pids), float(np.mean(nnov))]
        print(f"    {th:>8.2f}{len(pids):>9}{np.mean(nnov):>9.2f}{d.mean():>+17.4f}"
              f"   [{lo:+.4f}, {hi:+.4f}]")

    # POSITIVE CONTROL: remove everything -> the empty sum is all-ties
    pids = [p for p in sat if p in targets and len(targets[p]) >= 2]
    # ⚠ THE FIRST VERSION OF THIS CONTROL WAS MIS-SPECIFIED and printed FAIL on a working
    # ablation. `hits` draws a RANDOM held-out annotator per prompt, but the tie rate was
    # computed against targets[p][0] -- the FIRST annotator. Two different draws compared as
    # though they were one. The ablation was fine; the control was comparing apples to a
    # different apple. Fix: compute the tie rate from the SAME draw.
    empty = hits({p: [] for p in pids}, 0)
    rng_same = np.random.default_rng(0)
    ties = float(np.mean([cls(np.array(
        targets[p][int(rng_same.integers(len(targets[p])))][0], float)) == (0.0,) * 6
        for p in pids]))
    ok_pos = abs(np.mean(list(empty.values())) - ties) < 1e-9
    # PLACEBO: remove nothing from both arms
    allsel = {p: list(range(len(sims[p]))) for p in pids if p in sims}
    pa, pb = hits(allsel, 0), hits(allsel, 0)
    ok_pla = all(pa[p] == pb[p] for p in pa)
    print(f"\n    [{'PASS' if ok_pos else 'FAIL'}] POSITIVE: removing EVERY criterion gives "
          f"{np.mean(list(empty.values())):.4f}, the all-ties rate {ties:.4f}")
    print(f"    [{'PASS' if ok_pla else 'FAIL'}] PLACEBO: removing nothing from both arms "
          f"differs by exactly 0")
    surv = [t for t, v in art.items() if v[1] > 0 or v[2] < 0]
    print(f"\n    cells tested {len(art)} | intervals excluding zero: {len(surv)}")
    print(f"\n    VERDICT: " + ("W2 -- the novel criteria are INDISTINGUISHABLE from randomly "
          "chosen ones at every threshold tested" if not surv else
          f"separable at {surv}") + "\n")
    (pathlib.Path(__file__).parent / "results" / "ablate_novel.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "by_threshold": art, "positive_ok": bool(ok_pos), "placebo_ok": bool(ok_pla)},
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
