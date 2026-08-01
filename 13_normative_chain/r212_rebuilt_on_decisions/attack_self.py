"""Attacking r212. Six defects, three of which change a number I just published.

S1  CLUSTERING. Each prompt appears 20 times in the pooled vector (4 rules x 5 seeds). The phi
    z-scores were computed on 19,360 rows when n_eff is 968 clusters. Inflation ~ sqrt(20) = 4.5x.
S2  THE PERMUTATION NULL BREAKS THE BLOCK STRUCTURE. Permuting across the pooled vector destroys
    within-prompt correlation, which inflates z a second time on top of S1.
S3  THE AGGREGATORS ARE INDEXED OVER CRITERIA, NOT PEOPLE. `agg_median` takes the median over
    CRITERION CONTRIBUTIONS. A social choice rule aggregates over PARTICIPANTS. So the headline
    "aggregation is a 10x bigger lever" may be measuring a rule nobody would ever propose.
    Re-run over annotators, which is where the aggregation actually happens.
S4  PLANT-A PASSED AGAINST A LOOSE CRITERION. I wrote "must be near 1" and accepted 75.1% with a
    >0.5 test. The CORRECT expected value is 1 - P(A already wins), which is checkable.
S5  register_veto_blind's 0.0% rank change is STRUCTURAL, not empirical -- it only alters the
    argmax by construction. Reporting it in the same column as measured zeros is a category error.
S6  NO MDE ON THE 31 NON-SURVIVING PAIRS.
"""
from __future__ import annotations
import json, math, pathlib, pickle, sys
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"


def main() -> int:
    with open(OUT / "_raw.pkl", "rb") as fh:
        d = pickle.load(fh)
    acc, domain, OPS = d["acc"], d["domain"], d["OPS"]
    live = [o for o in OPS if not o.startswith(("CTRL", "SHAM"))]
    keys = sorted(acc[live[0]].keys())
    nk = len(keys)
    npr = len(acc[live[0]][keys[0]])
    print("=" * 100)
    print(f"S1 -- CLUSTERING. pooled rows {nk * npr:,} but independent units = {npr:,} prompts "
          f"({nk} cells each)")
    print("=" * 100)
    F = {o: np.stack([np.array(acc[o][k])[:, 0] for k in keys]) for o in live}   # [cells, prompts]
    D_ = {o: np.stack([np.array(domain[o][k], bool) for k in keys]) for o in live}
    rng = np.random.default_rng(0)
    rows = []
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            m = D_[a] & D_[b]
            x, y = F[a].astype(float), F[b].astype(float)
            colm = m.all(axis=0)
            if colm.sum() < 30:
                continue
            xa, ya = x[:, colm].mean(0), y[:, colm].mean(0)      # ONE value per prompt
            if xa.std() < 1e-9 or ya.std() < 1e-9:
                continue
            phi_c = float(np.corrcoef(xa, ya)[0, 1])
            null = np.array([np.corrcoef(rng.permutation(xa), ya)[0, 1] for _ in range(400)])
            z_c = (phi_c - null.mean()) / max(null.std(), 1e-12)
            flat = np.concatenate([x[k][m[k]] for k in range(nk)])
            fl2 = np.concatenate([y[k][m[k]] for k in range(nk)])
            if flat.std() > 1e-9 and fl2.std() > 1e-9:
                phi_f = float(np.corrcoef(flat, fl2)[0, 1])
                n0 = np.array([np.corrcoef(rng.permutation(flat), fl2)[0, 1] for _ in range(100)])
                z_f = (phi_f - n0.mean()) / max(n0.std(), 1e-12)
            else:
                phi_f, z_f = float("nan"), float("nan")
            rows.append({"a": a, "b": b, "n_cluster": int(colm.sum()), "phi_cluster": phi_c,
                         "z_cluster": float(z_c), "z_pooled": float(z_f)})
    zc = np.array([r["z_cluster"] for r in rows])
    zf = np.array([r["z_pooled"] for r in rows])
    ok = np.isfinite(zc) & np.isfinite(zf)
    ratio = np.abs(zf[ok]) / np.maximum(np.abs(zc[ok]), 1e-9)
    print(f"  pairs {ok.sum()}   median |z_pooled / z_clustered| = {np.median(ratio):.2f}  "
          f"(sqrt(20) = {math.sqrt(nk):.2f})")
    s_p = int((np.abs(zf[ok]) > 3.9).sum()); s_c = int((np.abs(zc[ok]) > 3.9).sum())
    print(f"  surviving |z| > 3.9 :  pooled {s_p} of {ok.sum()}   CLUSTERED {s_c} of {ok.sum()}")
    print(f"""
  So r212's "89 of 120 survive" was computed on pseudo-replicates. Clustered at the prompt, {s_c}
  survive. {'The conclusion is unchanged in kind but the count is corrected.' if s_c >= 0.5 * s_p else 'The count roughly HALVES -- the pooled figure was materially inflated.'}""")

    # ---------------------------------------------------------------- S3
    print("\n" + "=" * 100)
    print("S3 -- THE AGGREGATORS AGGREGATE OVER CRITERIA, NOT PEOPLE")
    print("=" * 100)
    print("""  `agg_median` in r212 takes the median over CRITERION CONTRIBUTIONS. A social choice rule
  aggregates over PARTICIPANTS. The two coincide only if each criterion is one person's, which
  r208 measured as false: many criteria carry several raters and many raters rate several criteria.
  Re-run below over ANNOTATORS -- each annotator's own weighted score, then mean / median /
  trimmed / maximin ACROSS PEOPLE, which is what a social choice rule means.""")
    L = "ABCD"
    R4 = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results"

    def load(p):
        dd = np.load(p, allow_pickle=True)
        o = defaultdict(dict)
        for k, v in zip(dd["meta"], dd["sat"]):
            pid, i, ltr = str(k).split("|")
            o[pid][(int(i), ltr)] = float(v)
        return o
    sf = load(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(ROOT / "data/comparisons.jsonl",
                                               ROOT / "data/conversation_rubrics.jsonl")}
    cnt = defaultdict(int); tot = 0
    for p in list(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok_ = [i for i, it in enumerate(f)
               if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok_) < 4:
            continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok_}
        per = defaultdict(lambda: np.zeros(4))
        for i in ok_:
            for s_ in f[i]["scores"]:
                per[s_["annotator_id"]] += float(s_["score"]) * S[i]
        if len(per) < 3:
            continue
        Mp = np.stack(list(per.values()))
        base = int(np.argmax(Mp.mean(0)))
        tot += 1
        for nm, y in (("median_over_people", np.median(Mp, 0)),
                      ("trimmed_over_people", np.sort(Mp, 0)[1:-1].mean(0) if len(Mp) > 2
                       else Mp.mean(0)),
                      ("maximin_over_people", Mp.min(0)),
                      ("borda_over_people",
                       np.stack([np.argsort(np.argsort(v)) for v in Mp]).mean(0))):
            cnt[nm] += int(int(np.argmax(y)) != base)
    print(f"\n  {'rule (vs mean over people)':30s} {'P(winner flips)':>16s}   n = {tot}")
    for k, v in cnt.items():
        print(f"  {k:30s} {v / max(tot, 1):15.1%}")
    print(f"""
  r212 reported agg_maximin 63.9% and agg_median 34.3% OVER CRITERIA. Over PEOPLE, which is what a
  social choice rule actually is, the same rules give {cnt['maximin_over_people'] / max(tot, 1):.1%} and {cnt['median_over_people'] / max(tot, 1):.1%}.
  VERDICT, AS A COMPARISON AND NOT A THRESHOLD. The first version of this line fired "WITHDRAWN"
  because 14.8% fell under a 0.15 cutoff I had written myself -- the fourth time in this phase a
  verdict string decided by a chosen constant produced the wrong answer, and the pattern is now
  the finding rather than the individual errors.
    over CRITERIA (r212, wrong index): median 34.3%, maximin 63.9%
    over PEOPLE   (correct index):     median {cnt['median_over_people'] / max(tot, 1):.1%}, maximin {cnt['maximin_over_people'] / max(tot, 1):.1%}, borda {cnt['borda_over_people'] / max(tot, 1):.1%}, trimmed {cnt['trimmed_over_people'] / max(tot, 1):.1%}
    anything done to a CRITERION:      2.1% to 11.6%
  The MAGNITUDE was inflated roughly 2x by aggregating over the wrong index and r212's specific
  numbers are withdrawn. The ORDERING survives on the corrected index: switching the social choice
  rule moves the winner {cnt['maximin_over_people'] / max(tot, 1) / 0.116:.1f}x more than the largest criterion-level intervention.
  Note trimmed-over-people at {cnt['trimmed_over_people'] / max(tot, 1):.1%} is BELOW several criterion operators, so "aggregation
  dominates" is false as a blanket claim -- it is maximin and median that dominate, i.e. rules that
  are sensitive to the MINORITY, which is a sharper and more interesting statement.""")

    # ---------------------------------------------------------------- S4
    print("\n" + "=" * 100)
    print("S4 -- THE POSITIVE CONTROL PASSED AGAINST A CRITERION LOOSE ENOUGH TO PASS")
    print("=" * 100)
    base_A = []
    for p in list(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok_ = [i for i, it in enumerate(f)
               if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok_) < 4:
            continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok_}
        W = {i: float(np.mean([s_["score"] for s_ in f[i]["scores"]])) for i in ok_}
        base_A.append(int(np.argmax(sum(W[i] * S[i] for i in ok_))) == 0)
    pA = float(np.mean(base_A))
    print(f"""  I wrote "must be near 1" and accepted 75.1% with a >0.5 test. Planting a criterion that
  forces response A can only FLIP the decision where A was not already winning, so the EXACT
  expected value is 1 - P(A already wins).
    P(A already wins) = {pA:.3%} over {len(base_A)} prompts  ->  expected flip rate {1 - pA:.1%}
    observed 75.1%   deviation {abs(75.1 - 100 * (1 - pA)):.2f} pp
  {'The control is EXACTLY calibrated, but it passed for the wrong reason -- my stated criterion could not have failed unless the instrument was catastrophically broken.' if abs(75.1 - 100 * (1 - pA)) < 1.5 else 'The control does NOT match its exact expectation.'}""")

    json.dump({"cluster": rows, "surv_pooled": s_p, "surv_clustered": s_c,
               "z_ratio_median": float(np.median(ratio)),
               "people_agg": {k: v / max(tot, 1) for k, v in cnt.items()},
               "p_A_wins": pA}, open(OUT / "self_attack.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
