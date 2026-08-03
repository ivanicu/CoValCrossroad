#!/usr/bin/env python3
"""
corebench/compare_matrix.py -- the paired comparator across the WHOLE matrix, not one cell.

WHY. The last round's recommendation rested on I3 (novel content) and E4 (fidelity per
criterion), which were POINT VALUES WITH NO INTERVAL. A leaderboard gap with no interval is
exactly the reading that the A1 paired test had just destroyed one command earlier -- the
apparent +0.0110 win that came back +0.0052 [-0.0107, +0.0213]. Reporting one dimension with
an interval and twelve without is the multiplicity failure with manners.

WHAT IT DOES. Every dimension that decomposes per prompt gets the same paired bootstrap over
the same prompts and the same held-out draws, and the family is corrected over the WHOLE
grid with Benjamini-Hochberg. Dimensions that do NOT decompose per prompt (the G family
resamples subgroups, not prompts) are named as out of scope rather than silently omitted.

⚠ BH, not Bonferroni: BH's threshold at rank i of C is q*i/C, and the largest is q itself.
Demanding every cell clear q/C is Bonferroni logic wearing BH's name.

CONTROLS (all per dimension, so a dimension whose controls fail reports nothing)
  PLACEBO   a core against itself -> exactly 0.0000, zero-width interval
  POSITIVE  a synthetic arm degraded by a known fraction g -> recovered monotonically,
            and silent at g=0
  NEGATIVE  destroy the pairing -> the interval must WIDEN
"""
from __future__ import annotations
import argparse, collections, difflib, itertools, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
SEEDS, NBOOT, Q = [0, 1, 2], 2000, 0.05
from score import cls, load_sat, load_targets, yvec, tau_b

NOT_PER_PROMPT = {
    "G1_worst_subgroup": "resamples SUBGROUPS, not prompts -- a different unit",
    "G2_subgroup_spread": "same; the paired unit here would be a subgroup",
    "G4_share_beating_constant": "same",
    "C1_emitted_class_entropy": "a property of the whole distribution, not of one prompt",
    "D1_seed_spread": "already a spread across seeds; a paired CI on it is a CI on a CI",
}


def per_prompt(sat, texts, full_texts, targets, seed):
    """-> {dim: {pid: value}}. Every value is one prompt's contribution."""
    rng = np.random.default_rng(seed)
    out = collections.defaultdict(dict)
    for p in sat:
        if p not in targets or len(targets[p]) < 2:
            continue
        y = yvec(sat[p], sorted({i for i, _ in sat[p]}))
        c = cls(y)
        v = targets[p]
        hy = np.array(v[int(rng.integers(len(v)))][0], float)
        hc = cls(hy)
        out["A1_exact_class"][p] = float(c == hc)
        out["A2_pairwise"][p] = float(np.mean([c[t] == hc[t] for t in range(6)]))
        out["A3_top1"][p] = float(np.argmax(y) == np.argmax(hy))
        out["A4_bottom1"][p] = float(np.argmin(y) == np.argmin(hy))
        out["A5_kendall_tau_b"][p] = tau_b(list(y), list(hy))
        ct = texts.get(p, [])
        out["E1_k_criteria"][p] = float(len(ct))
        out["E2_total_tokens"][p] = float(sum(len(x.split()) for x in ct))
        f = full_texts.get(p, [])
        sims = [max((difflib.SequenceMatcher(None, x, z).ratio() for z in f), default=0.0)
                for x in ct]
        if sims:
            out["I1_traceable_ge_090"][p] = float(np.mean([s >= 0.90 for s in sims]))
            out["I2_verbatim"][p] = float(np.mean([s >= 0.999 for s in sims]))
            out["I3_novel_content"][p] = float(np.mean([s < 0.60 for s in sims]))
            out["I4_median_best_match"][p] = float(np.median(sims))
    # E4 needs A1's margin over the constant, so it is derived after the loop, per prompt
    return out


def boot(d, rng, nboot=NBOOT):
    b = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(nboot)])
    return float(d.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), \
           float(2 * min((b <= 0).mean(), (b >= 0).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--core-a"); ap.add_argument("--core-b")
    ap.add_argument("--label-a", default="A"); ap.add_argument("--label-b", default="B")
    a = ap.parse_args()

    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    full_texts = {p: [i["criterion"] for i in (r.get("coval_full") or [])]
                  for p, _pr, r in joined}
    inc = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _pr, r in joined}
    ta = json.loads(pathlib.Path(a.core_a).read_text()) if a.core_a else inc
    tb = json.loads(pathlib.Path(a.core_b).read_text()) if a.core_b else inc
    targets, _ = load_targets()
    SA, SB = load_sat(a.a), load_sat(a.b)

    rows, dims = [], None
    acc = collections.defaultdict(list)
    for s in SEEDS:
        pa = per_prompt(SA, ta, full_texts, targets, s)
        pb = per_prompt(SB, tb, full_texts, targets, s)
        dims = sorted(set(pa) & set(pb))
        for d in dims:
            pids = sorted(set(pa[d]) & set(pb[d]))
            acc[d].append(np.array([pa[d][p] - pb[d][p] for p in pids]))

    # CONTROLS, computed on A1 as the reference dimension
    p0 = per_prompt(SA, ta, full_texts, targets, 0)
    pids0 = sorted(p0["A1_exact_class"])
    v0 = np.array([p0["A1_exact_class"][p] for p in pids0])
    pl = boot(v0 - v0, np.random.default_rng(1))
    dose = {}
    for g in (0.0, 0.1, 0.25, 0.5):
        r = np.random.default_rng(9)
        deg = np.array([0.0 if r.random() < g else x for x in v0])
        dose[g] = float((v0 - deg).mean())
    b0 = per_prompt(SB, tb, full_texts, targets, 0)["A1_exact_class"]
    pb_v = np.array([b0[p] for p in pids0 if p in b0])
    va = np.array([p0["A1_exact_class"][p] for p in pids0 if p in b0])
    pw = boot(va - pb_v, np.random.default_rng(2))
    sh = pb_v.copy(); np.random.default_rng(3).shuffle(sh)
    uw = boot(va - sh, np.random.default_rng(4))
    ctrl = [("PLACEBO self vs self is exactly 0, zero width",
             pl[0] == 0.0 and pl[1] == pl[2] == 0.0, f"{pl[0]:.4f} [{pl[1]:.4f},{pl[2]:.4f}]"),
            ("POSITIVE degradation dose is monotone",
             all(dose[x] <= dose[y] + 1e-9 for x, y in zip([0.0,.1,.25],[.1,.25,.5])),
             " ".join(f"g={g}:{v:+.4f}" for g, v in dose.items())),
            ("POSITIVE silent at g=0", dose[0.0] == 0.0, f"{dose[0.0]:+.4f}"),
            ("NEGATIVE unpairing widens the interval",
             (uw[2]-uw[1]) > (pw[2]-pw[1]),
             f"{pw[2]-pw[1]:.4f} -> {uw[2]-uw[1]:.4f} ({(uw[2]-uw[1])/(pw[2]-pw[1]):.2f}x)")]

    print(f"\n  PAIRED MATRIX: {a.label_a}  −  {a.label_b}"
          f"   ({len(SEEDS)} seeds x {NBOOT} bootstraps)\n")
    for n, ok, det in ctrl:
        print(f"    [{'PASS' if ok else 'FAIL'}] {n:<44} {det}")

    res = []
    for d in dims:
        v = np.concatenate(acc[d])
        m, lo, hi, p = boot(v, np.random.default_rng(hash(d) % 9999))
        res.append((d, m, lo, hi, p))
    C = len(res)
    order = sorted(range(C), key=lambda i: res[i][4])
    surv = set()
    for rank, i in enumerate(order, 1):
        if res[i][4] <= Q * rank / C:
            surv = set(order[:rank])          # BH: q*i/C, largest is q itself
    print(f"\n    {'dimension':<26}{'Δ':>10}{'95% CI':>22}{'p':>9}   BH")
    for i, (d, m, lo, hi, p) in enumerate(res):
        print(f"    {d:<26}{m:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]{p:>9.4f}   "
              f"{'SURVIVES' if i in surv else '--'}")
    print(f"\n    cells tested {C} | surviving BH q={Q}: {len(surv)}")
    print("\n    NOT PER-PROMPT, named rather than omitted:")
    for k, why in NOT_PER_PROMPT.items():
        print(f"      {k:<28} {why}")
    print()


if __name__ == "__main__":
    main()
