#!/usr/bin/env python3
"""R811 · source or rule — what is a core's advantage actually made of, at matched k?

R810 asked whether `topw_k` beats `POOL[0:k]` at matched k, to decide whether clause (2) names one
baseline or two. CHECK #413 found that gap is non-monotone (+0.0018, +0.0121, +0.0238, +0.0046) and
confounds SOURCE (the prompt's own rubric vs a fixed generic set of 16) with RULE (weight-ranked vs
uninformative). `random_k` — the rubric under an uninformative rule — sits far BELOW the generic
pool at every k, which decomposes it. And `POOL[0:k]` is ONE arbitrary subset of the 16 used as if
it were the cell; the pool is fixed across prompts, so the cell is the subset DISTRIBUTION and the
first-k's percentile in it is measurable.

ESTIMAND        E1 a 2x2 with one cell structurally absent · E2 ⭐ rule effect vs source effect ·
                E3 ⭐ is POOL[0:k] typical? · E4 R810's question answered directly
IDENTIFICATION  E3 EXACT wherever C(16,k) is enumerable; the count is printed per k
DERIVED FIRST   D1 the rule effect must vanish at k=n, so its decline is partly forced · D2 the
                pool's subset spread is a property of the 16, not of the prompts · D3 a pool
                advantage at matched rule is evidence AGAINST prompt-specificity · D4 R810's
                non-monotone gap should decompose into two cleaner pieces or the decomposition is
                wrong and this round says so
WORLDS          A rule dominates · B source dominates · C comparable — C checked FIRST
CONTROLS        OBJECT (R810's k=12 cells) · PLACEBO · POSITIVE (D1, with a g=0 check at k=2) ·
                NEGATIVE (200-permutation null) · NOISE FLOOR (three committed seeds at every k)
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R810J = ARC / "R810_is_the_level_gap_size_or_fitting/results/size_or_fitting.json"
KS = [2, 4, 8, 12]
SEEDS = [0, 1, 2]
NBOOT = 1200
ENUM_CAP = 20000


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "a k x a cell"}
    tg, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    FULL = load_sat(RES / "sat_full.npz")
    need = {}
    for k in KS:
        need[f"topw_k{k}"] = RES / f"sat_topw_k{k}.npz"
        for s in SEEDS:
            need[f"random_k{k}_s{s}"] = RES / f"sat_random_k{k}_s{s}.npz"
    missing = [n for n, p in need.items() if not p.is_file()]
    if missing:
        print(f"  UNRUNNABLE: missing arms {missing}. Exit 2.")
        return 2
    S = {n: load_sat(p) for n, p in need.items()}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(POOL) & set(FULL) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: np.array([cls(np.array(t[0], float))
                       for i, t in enumerate(tg[p]) if i % 2 == 0]) for p in pids}
    pids = [p for p in pids if len(H0[p]) >= 1]
    npool = len({i for i, _ in POOL[pids[0]]})
    eff = {n: {p: len({i for i, _ in sat[p]}) for p in pids} for n, sat in S.items()}
    ATT = {k: [p for p in pids
               if all(eff[f"{a}"][p] >= k for a in [f"topw_k{k}"] +
                      [f"random_k{k}_s{s}" for s in SEEDS])] for k in KS}
    COMMON = sorted(set.intersection(*(set(ATT[k]) for k in KS)))
    print(f"  POPULATION  {len(pids)} prompts · common intersection attaining nominal k at every k: "
          f"{len(COMMON)} · blind pool of {npool} FIXED generic criteria")

    def a2(sat, ps, idx=None):
        v = np.zeros(len(ps))
        for i, p in enumerate(ps):
            c = np.array(cls(yvec(sat[p], idx if idx is not None
                                  else sorted({j for j, _ in sat[p]}))))
            v[i] = float((H0[p] == c).mean())
        return v

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R810's committed k=12 cells on the common intersection")
    r810 = json.loads(R810J.read_text())["curves"]["common intersection"]["12"]
    tw = float(a2(S["topw_k12"], COMMON).mean())
    rd = float(a2(S["random_k12_s0"], COMMON).mean())
    pl = float(a2(POOL, COMMON, list(range(min(12, npool)))).mean())
    ok = (abs(tw - r810["topw"]) < 1e-6 and abs(rd - r810["random"]) < 1e-6
          and abs(pl - r810["pool"]) < 1e-6)
    print(f"     topw_k12 {tw:.6f} vs {r810['topw']:.6f} · random_k12_s0 {rd:.6f} vs "
          f"{r810['random']:.6f} · POOL[0:12] {pl:.6f} vs {r810['pool']:.6f}   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R810's cells did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"topw12": tw, "random12": rd, "pool12": pl}

    # ================= E1/E2 · the 2x2 ===========================================================
    print("\n  E1/E2 - THE 2x2 AT MATCHED k   (one cell is STRUCTURALLY ABSENT and is named)")
    print("     SOURCE {prompt rubric, generic pool} x RULE {uninformative, informative}")
    print("     ⚠ pool x informative CANNOT be built: the pool is a FIXED generic set of 16 with no")
    print("       per-prompt importance scores. It would require a release that weights them.")
    rng = np.random.default_rng(1234)
    idxb = rng.integers(0, len(COMMON), (NBOOT, len(COMMON)))
    cells, e3 = {}, {}
    print(f"\n     {'k':>3}{'rubric/uninf':>14}{'rubric/inform':>15}{'pool/uninf':>12}"
          f"{'POOL[0:k]':>11}{'full':>8}")
    for k in KS:
        rr = np.mean([a2(S[f"random_k{k}_s{s}"], COMMON) for s in SEEDS], axis=0)
        rr_seeds = [float(a2(S[f"random_k{k}_s{s}"], COMMON).mean()) for s in SEEDS]
        ti = a2(S[f"topw_k{k}"], COMMON)
        # the pool's uninformative cell: the DISTRIBUTION over k-subsets of the 16
        combs = list(itertools.combinations(range(npool), k))
        exact = len(combs) <= ENUM_CAP
        if not exact:
            combs = [combs[i] for i in rng.choice(len(combs), ENUM_CAP, replace=False)]
        sub = np.array([a2(POOL, COMMON, list(c)).mean() for c in combs])
        pk = a2(POOL, COMMON, list(range(k)))
        pct = float((sub <= pk.mean()).mean() * 100)
        cells[k] = {"rubric_uninf": float(rr.mean()), "rubric_inform": float(ti.mean()),
                    "pool_uninf_mean": float(sub.mean()), "pool_firstk": float(pk.mean()),
                    "full": float(a2(FULL, COMMON).mean()),
                    "seed_spread": float(np.std(rr_seeds)), "seeds": rr_seeds}
        e3[k] = {"n_subsets": len(combs), "exact": exact, "mean": float(sub.mean()),
                 "sd": float(sub.std()), "lo": float(sub.min()), "hi": float(sub.max()),
                 "firstk": float(pk.mean()), "percentile": pct}
        c = cells[k]
        print(f"     {k:>3}{c['rubric_uninf']:>14.4f}{c['rubric_inform']:>15.4f}"
              f"{c['pool_uninf_mean']:>12.4f}{c['pool_firstk']:>11.4f}{c['full']:>8.4f}")
        cells[k]["_rr"], cells[k]["_ti"], cells[k]["_pk"] = rr, ti, pk
        cells[k]["_sub_mean_vec"] = None

    print(f"\n     {'k':>3}{'RULE (inform-uninf, rubric)':>32}{'SOURCE (pool-rubric, uninf)':>34}")
    rows, pv = [], []
    for k in KS:
        c = cells[k]
        rule = c["_ti"] - c["_rr"]
        # SOURCE holds the rule uninformative on both sides: pool subset MEAN vs rubric random
        src = np.array([c["pool_uninf_mean"]] * len(COMMON)) - c["_rr"]
        br, bs = rule[idxb].mean(axis=1), src[idxb].mean(axis=1)
        rl, rh = np.percentile(br, [2.5, 97.5])
        sl, sh = np.percentile(bs, [2.5, 97.5])
        d = br - bs
        dl, dh = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        rows.append({"k": k, "rule": float(rule.mean()), "rule_lo": float(rl),
                     "rule_hi": float(rh), "source": float(src.mean()), "src_lo": float(sl),
                     "src_hi": float(sh), "diff": float(rule.mean() - src.mean()),
                     "diff_lo": dl, "diff_hi": dh})
        pv += [float(2 * min((br <= 0).mean(), (br >= 0).mean())),
               float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))]
        print(f"     {k:>3}   {rule.mean():+.4f} [{rl:+.4f}, {rh:+.4f}]        "
              f"{src.mean():+.4f} [{sl:+.4f}, {sh:+.4f}]")
    out["cells"] = {str(k): {x: v for x, v in cells[k].items() if not x.startswith("_")}
                    for k in KS}
    out["e2"] = rows

    # ================= E3 · is POOL[0:k] typical? ================================================
    print("\n  E3 - IS `POOL[0:k]` TYPICAL OF THE 16's SUBSETS, OR A LUCKY DRAW?")
    print(f"     {'k':>3}{'subsets':>10}{'exact':>7}{'subset mean':>13}{'sd':>8}"
          f"{'range':>18}{'POOL[0:k]':>11}{'percentile':>12}")
    for k in KS:
        e = e3[k]
        print(f"     {k:>3}{e['n_subsets']:>10}{str(e['exact']):>7}{e['mean']:>13.4f}"
              f"{e['sd']:>8.4f}  [{e['lo']:.4f}, {e['hi']:.4f}]{e['firstk']:>11.4f}"
              f"{e['percentile']:>11.1f}%")
    extreme = [k for k in KS if e3[k]["percentile"] > 90 or e3[k]["percentile"] < 10]
    print(f"     ⭐ k where the first-k subset is in a TAIL of the distribution (>90th or <10th): "
          f"{extreme if extreme else 'none'}")
    out["e3"] = {str(k): e3[k] for k in KS}

    # ================= E4 · R810's question ======================================================
    print("\n  E4 - R810's NEXT, ANSWERED DIRECTLY: topw_k - POOL[0:k]")
    e4 = []
    for k in KS:
        c = cells[k]
        g = c["_ti"] - c["_pk"]
        b = g[idxb].mean(axis=1)
        lo, hi = np.percentile(b, [2.5, 97.5])
        e4.append({"k": k, "gap": float(g.mean()), "lo": float(lo), "hi": float(hi)})
        pv.append(float(2 * min((b <= 0).mean(), (b >= 0).mean())))
        print(f"     k={k:>2}  {g.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]   "
              f"{'RESOLVED' if (lo > 0 or hi < 0) else 'holds 0'}")
    out["e4"] = e4

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = [float((a2(POOL, COMMON, list(range(k))) - a2(POOL, COMMON,
                                                         list(range(k)))).mean()) for k in KS]
    plac_ok = all(abs(v) < 1e-15 for v in plac)
    print(f"     PLACEBO   the pool's first-k against ITSELF: {['%.1e' % v for v in plac]}   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    rules = [r["rule"] for r in rows]
    shrink = rules[-1] < rules[0]
    g0_ok = rows[0]["rule_lo"] > 0
    print(f"     POSITIVE  D1 the RULE effect must shrink as k -> n: " +
          "  ".join(f"k={r['k']} {r['rule']:+.4f}" for r in rows) +
          f"   shrinks: {shrink}   {'PASS' if shrink else 'FAIL'}")
    print(f"     g=0 CHECK at k=2 the rule effect must NOT be 0: {rows[0]['rule']:+.4f} "
          f"[{rows[0]['rule_lo']:+.4f}, {rows[0]['rule_hi']:+.4f}]   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    rngn = np.random.default_rng(707)
    kmax = KS[-1]
    CLti = {p: np.array(cls(yvec(S[f"topw_k{kmax}"][p],
                                 sorted({j for j, _ in S[f"topw_k{kmax}"][p]})))) for p in COMMON}
    CLrr = {p: np.array(cls(yvec(S[f"random_k{kmax}_s0"][p],
                                 sorted({j for j, _ in S[f"random_k{kmax}_s0"][p]}))))
            for p in COMMON}
    nulls = []
    for _ in range(200):
        pm = rngn.permutation(len(COMMON))
        v = np.zeros(len(COMMON))
        for i, p in enumerate(COMMON):
            q = COMMON[pm[i]]
            v[i] = float((H0[p] == CLti[q]).mean()) - float((H0[p] == CLrr[q]).mean())
        nulls.append(float(v.mean()))
    nulls = np.array(nulls)
    nlo, nhi = float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))
    real = rows[-1]["rule"]
    neg_ok = bool(nlo < nhi and real > nulls.max())
    print(f"     NEGATIVE  every arm scored against ANOTHER prompt's parity-0 humans, 200 "
          f"permutations: null {nulls.mean():+.4f} [{nlo:+.4f}, {nhi:+.4f}] max {nulls.max():+.4f}")
    print(f"               real RULE effect at k={kmax}: {real:+.4f}   "
          f"{'PASS - outside the whole null' if neg_ok else 'FAIL'}")
    print(f"     NOISE FLOOR  the three committed random seeds, sd of the rubric/uninformative "
          f"cell: " + "  ".join(f"k={k} {cells[k]['seed_spread']:.4f}" for k in KS))
    gate = ok and plac_ok and shrink and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "shrink": shrink, "g0_ok": g0_ok,
                       "null_mean": float(nulls.mean()), "null_max": float(nulls.max()),
                       "negative_ok": neg_ok, "gate": gate,
                       "seed_spread": {str(k): cells[k]["seed_spread"] for k in KS}}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    keep = bh(pv)
    print(f"     BH q=0.05 over {len(pv)} cells: {int(keep.sum())} survive, "
          f"{len(pv) - int(keep.sum())} do not")
    last = rows[-1]
    if not gate:
        world = "UNVERIFIED"
    elif last["diff_lo"] <= 0 <= last["diff_hi"]:
        world = "C"
    elif last["diff_lo"] > 0:
        world = "A"
    elif last["diff_hi"] < 0:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     at k={last['k']}: RULE {last['rule']:+.4f}  SOURCE {last['source']:+.4f}  "
          f"difference {last['diff']:+.4f} [{last['diff_lo']:+.4f}, {last['diff_hi']:+.4f}]"
          f"  ->  WORLD {world}")
    out["world"] = world
    out["bh"] = [bool(x) for x in keep]

    art = HERE / "results/source_or_rule.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
