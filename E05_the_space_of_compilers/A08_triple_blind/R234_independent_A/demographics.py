#!/usr/bin/env python3
"""FAITHFUL TO WHOM?  The compression is a single object serving ~1000 people.
A mean deficit hides who pays it.  The release ships demographics, so the
question is answerable rather than rhetorical.

ESTIMAND: for each demographic cell g, D(g) = mean over that cell's assessments
of [ Acc_core(a) - Acc_own(a) ], where Acc_own uses the annotator's OWN weighted
rubric.  The contrast is DIFFERENCED against the annotator's own rubric so that
'people whose rankings are simply harder to predict' -- which lowers BOTH arms --
cannot manufacture a cell effect.

CONTROLS
  PLACEBO   the same table for D_pop(g) = Acc_pop - Acc_own (the population
            aggregate, which is what the core is a compression OF).  If a cell
            looks badly served by the core AND equally badly served by the
            population mean, the compiler is not what disserved it.
  NEGATIVE  demographic labels permuted across annotators, 500 draws: gives the
            null spread of the between-cell range, which is the only scale on
            which 'this group is worse served' can be read.
  MULTIPLICITY over every cell of every axis, BH q=0.05.
"""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import run as R

rng = np.random.default_rng(11)
joined, _ = R.load_join()
bundles, _ = R.build(joined, R.load_sat("full"), R.load_sat("core"))
C_ = R.cache(bundles, "z", "mean")

demo = {}
for line in open(R.ROOT / "data/merged_comparisons_annotators.jsonl", encoding="utf-8"):
    d = json.loads(line)
    demo[d["annotator_id"]] = d.get("demographics") or {}

recs = []
for pid in sorted(bundles):
    b = bundles[pid]
    Zf, Zc, w_all = C_[pid]
    core_s = Zc.sum(0); pop_s = w_all @ Zf
    Wf = np.nan_to_num(b["W"])
    by = defaultdict(list)
    for (_a, i, j) in R.human_pairs(b, "world"):
        by[_a].append((i, j))
    for k, a in enumerate(b["anns"]):
        pr = by.get(a) or []
        if not pr:
            continue
        pl = [(a, i, j) for i, j in pr]
        own = R.acc_on_pairs(Wf[k] @ Zf, pl)[0]
        recs.append((pid, a, R.acc_on_pairs(core_s, pl)[0] - own,
                     R.acc_on_pairs(pop_s, pl)[0] - own))

pid = np.array([r[0] for r in recs]); ann = np.array([r[1] for r in recs])
dcore = np.array([r[2] for r in recs]); dpop = np.array([r[3] for r in recs])
AXES = ["age", "gender", "education_level", "country_of_residence",
        "ai_concern_level", "generative_ai_usage"]
out = {"n": len(recs), "n_annotators": int(len(set(ann.tolist()))),
       "overall_core_minus_own": float(np.nanmean(dcore)),
       "overall_pop_minus_own": float(np.nanmean(dpop)), "axes": {}}
tests = []
for ax in AXES:
    lab = np.array([str(demo.get(a, {}).get(ax, "?")) for a in ann])
    cells = {}
    for v in sorted(set(lab.tolist())):
        m = lab == v
        if m.sum() < 100:
            continue
        # cluster bootstrap by prompt within the cell
        gp = sorted(set(pid[m].tolist()))
        gmap = {g: np.flatnonzero(m & (pid == g)) for g in gp}
        bs = []
        for _ in range(800):
            pick = rng.choice(len(gp), size=len(gp), replace=True)
            ii = np.concatenate([gmap[gp[i]] for i in pick])
            bs.append(np.nanmean(dcore[ii]))
        bs = np.array(bs); mu = float(np.nanmean(dcore[m]))
        p = float(min(1.0, (1 + 2 * min((bs > 0).sum(), (bs < 0).sum())) / (len(bs) + 1)))
        cells[v] = dict(n=int(m.sum()), n_prompts=len(gp), core_minus_own=mu,
                        PLACEBO_pop_minus_own=float(np.nanmean(dpop[m])),
                        se=float(bs.std()), p=p)
        tests.append((f"{ax}={v}", p))
    vals = [c["core_minus_own"] for c in cells.values()]
    obs_range = (max(vals) - min(vals)) if len(vals) > 1 else np.nan
    # NEGATIVE CONTROL: permute the labels across annotators, 500 draws
    uniq = sorted(set(ann.tolist()))
    null = []
    for _ in range(500):
        perm = dict(zip(uniq, rng.permutation(uniq)))
        pl_ = np.array([str(demo.get(perm[a], {}).get(ax, "?")) for a in ann])
        vv = [np.nanmean(dcore[pl_ == v]) for v in cells if (pl_ == v).sum() >= 100]
        if len(vv) > 1:
            null.append(max(vv) - min(vv))
    out["axes"][ax] = dict(cells=cells, observed_between_cell_range=float(obs_range),
                           NEGCTRL_permuted_label_range_mean=float(np.mean(null)) if null else None,
                           NEGCTRL_permuted_label_range_p95=float(np.percentile(null, 95)) if null else None,
                           EXCEEDS_NULL=bool(null and obs_range > np.percentile(null, 95)))
surv, C = R.bh([p for _, p in tests])
out["multiplicity"] = dict(C=C, surviving=int(surv.sum()),
                           tests=[{"cell": k, "p": p, "survives": bool(s)}
                                  for (k, p), s in zip(tests, surv)])
print(f"n={out['n']} assessments, {out['n_annotators']} annotators")
print(f"overall core-own = {out['overall_core_minus_own']:+.4f}   "
      f"pop-own = {out['overall_pop_minus_own']:+.4f}")
for ax, d in out["axes"].items():
    print(f"== {ax}: observed between-cell range={d['observed_between_cell_range']:.4f} "
          f"vs permuted-label null {d['NEGCTRL_permuted_label_range_mean']:.4f} "
          f"(p95 {d['NEGCTRL_permuted_label_range_p95']:.4f}) EXCEEDS={d['EXCEEDS_NULL']}")
    for v, c in sorted(d["cells"].items(), key=lambda kv: kv[1]["core_minus_own"]):
        print(f"     {v[:44]:46s} n={c['n']:5d} core-own={c['core_minus_own']:+.4f}"
              f" (+-{c['se']:.4f}) placebo pop-own={c['PLACEBO_pop_minus_own']:+.4f} p={c['p']:.3f}")
print(f"BH over C={C} demographic cells: {int(surv.sum())} survive")
Path("results/demographics.json").write_text(json.dumps(out, indent=1, default=float))
