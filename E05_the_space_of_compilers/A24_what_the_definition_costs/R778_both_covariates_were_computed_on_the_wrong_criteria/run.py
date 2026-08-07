#!/usr/bin/env python3
"""R778 · both arm-free covariates were computed on criteria NO ARM USES.

CHECK #380, AT THE OBJECT, BEFORE ANY DESIGN:
  - the 16-criterion "pool" is PROMPT-BLIND: one identical set for all 968 prompts.
  - `random_k4_s0` uses 3,869 distinct criteria and its overlap with the pool is **0**;
    `topw_k4` likewise 0/968.
  - the arms draw from the PROMPT'S OWN RUBRIC: 968/968 of `random_k4_s0`'s sets are subsets of
    `core_full.json`, whose per-prompt size is median 15, range 4 to 39.
  ⇒ R776's `poolspread` and R777's `orderdisagree` measured a criterion set sharing NOTHING with any
    arm's. Both nulls were guaranteed by construction and are retracted as evidence about prompts.

FORCED, LABELLED:
  D1 the two prior nulls were forced -- a covariate on disjoint criteria cannot correlate with those
     arms' differences. They were never tests.
  D2 two k-subset draws from an n-criterion rubric overlap in expectation k^2/n, so their difference
     shrinks as n falls and vanishes at n <= k. A NEGATIVE corr(n_rubric, |d|) is PARTLY FORCED for
     the random families; the measurement is its size, whether NON-random families show it, and
     whether it explains the M x R co-movement.
  D3 at n_rubric <= k the draw is degenerate: every arm takes the whole rubric and |d| = 0 exactly.
     Counted and reported -- the same object as R772's 223 ties, seen from the construction side.

CONTROLS  OBJECT (assert subset-of-rubric and disjoint-from-pool, exit 2) - POSITIVE (synthetic
          rubric-size sweep) - g=0 (fixed size -> UNDEFINED, printed as undefined) - NEGATIVE (200
          permutations) - SHAM (a random draw from n_rubric's own distribution) - PLACEBO -
          DEGENERATE (the n <= k count) - CONFOUND (corr(n_rubric, baseline A2), the difficulty axis).
UNIT      prompt - arm pair within a family - FAMILY (6) for E1/E2, FAMILY PAIR for E3.
"""
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NDRAW = 200
KS = [2, 3, 6, 8, 12]
FAM = {
    "Ra_random_s0": [f"random_k{k}_s0" for k in KS],
    "Rb_random_s1": [f"random_k{k}_s1" for k in KS],
    "Rc_random_s2": [f"random_k{k}_s2" for k in KS],
    "F1_committed": ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"],
    "F3_target":    ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1",
                     "greedy_k4_greedy_kA"],
    "M_mixed_sel":  ["random_k4_s0", "random_k4_s1", "random_k4_s2", "topabs_k4", "topvar_k4"],
}
RANDOM_CONTAINING = {"Ra_random_s0", "Rb_random_s1", "Rc_random_s2", "M_mixed_sel"}


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


def partial(x, y, z):
    rxy = float(np.corrcoef(x, y)[0, 1])
    rxz = float(np.corrcoef(x, z)[0, 1])
    ryz = float(np.corrcoef(y, z)[0, 1])
    den = math.sqrt(max((1 - rxz ** 2) * (1 - ryz ** 2), 1e-12))
    return (rxy - rxz * ryz) / den


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    FULL = load_sat(RES / "sat_full.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and p in FULL
                   and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    # ---- CONTROL - OBJECT: which criterion set do the arms actually use? ------------------------
    cpool = json.loads((RES / "core_genericpool16.json").read_text())
    cfull = json.loads((RES / "core_full.json").read_text())
    cr0 = json.loads((RES / "core_random_k4_s0.json").read_text())
    in_rubric = sum(1 for p in pids if set(cr0[p]) <= set(cfull[p]))
    in_pool = sum(1 for p in pids if set(cr0[p]) & set(cpool[p]))
    n_pool_sets = len({tuple(cpool[p]) for p in pids})
    if in_rubric != P or in_pool != 0:
        print(f"UNRUNNABLE: rubric {in_rubric}/{P}, pool-overlap {in_pool}. Exit 2, never 0.")
        return 2
    print(f"  OBJECT      `random_k4_s0` sets are subsets of the RUBRIC on {in_rubric}/{P} prompts, "
          f"and share {in_pool} criteria with the pool.  PASS")
    print(f"              the pool is PROMPT-BLIND: {n_pool_sets} distinct set across {P} prompts")

    # ---- the covariates, on the RIGHT criterion set ---------------------------------------------
    n_rub = np.array([len({i for i, _ in FULL[p]}) for p in pids], dtype=float)
    rub_spread, rub_dis = np.zeros(P), np.zeros(P)
    for a, p in enumerate(pids):
        idx = sorted({i for i, _ in FULL[p]})
        Y = np.array([[FULL[p].get((i, x), 0.0) for x in L] for i in idx])
        rub_spread[a] = Y.std()
        S = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        if len(idx) > 1:
            d = [float((S[i] != S[j]).mean()) for i, j in itertools.combinations(range(len(idx)), 2)]
            rub_dis[a] = float(np.mean(d))
    print(f"  n_rubric    median {np.median(n_rub):.0f}  range {int(n_rub.min())}-{int(n_rub.max())}"
          f"   rubricspread {rub_spread.mean():.4f}   rubricdisagree {rub_dis.mean():.4f}")

    # ---- D3 - the degenerate prompts --------------------------------------------------------------
    deg = {k: int((n_rub <= k).sum()) for k in KS + [4]}
    print(f"  D3 DEGEN    prompts with n_rubric <= k (draw is the whole rubric, |d| = 0): "
          f"{ {k: deg[k] for k in sorted(deg)} }")

    def a2(tag):
        Sa = load_sat(RES / f"sat_{tag}.npz")
        o = np.zeros(P)
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in Sa[p]})
            Y = np.array([sum(Sa[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            o[ai] = np.mean([(s == h).mean() for h in HC[ai]])
        return o

    A = {t: a2(t) for f in FAM.values() for t in f}
    C = {n: np.abs(np.array([A[a] - A[b] for a, b in itertools.combinations(FAM[n], 2)])).mean(0)
         for n in FAM}
    basearm = a2("random_k4_s0")
    r_diff = float(np.corrcoef(n_rub, basearm)[0, 1])
    print(f"  CONFOUND    corr(n_rubric, a baseline arm's A2) = {r_diff:+.4f}   (the difficulty axis)")

    # ---- E1/E2 - three covariates x six families ---------------------------------------------------
    COV = {"n_rubric": n_rub, "rubricdisagree": rub_dis, "rubricspread": rub_spread}
    print(f"\n  E1/E2 - THREE RUBRIC COVARIATES x SIX FAMILIES (raw / partial on the difficulty axis)")
    print(f"  {'family':<16}{'rnd':>5}" + "".join(f"{c:>26}" for c in COV))
    table = {}
    for n in FAM:
        row = {}
        line = f"  {n:<16}{'RND' if n in RANDOM_CONTAINING else ' -- ':>5}"
        for cname, cv in COV.items():
            r1 = float(np.corrcoef(C[n], cv)[0, 1])
            pt = partial(C[n], cv, basearm)
            row[cname] = {"raw": r1, "partial_difficulty": pt}
            line += f"{r1:>+13.4f}{pt:>+13.4f}"
        table[n] = row
        print(line)
    summary = {}
    for cname in COV:
        rc = [abs(table[n][cname]["raw"]) for n in FAM if n in RANDOM_CONTAINING]
        nr = [abs(table[n][cname]["raw"]) for n in FAM if n not in RANDOM_CONTAINING]
        n_hi = sum(1 for n in FAM if n in RANDOM_CONTAINING
                   and abs(table[n][cname]["raw"]) >= 0.30)
        n_lo = sum(1 for n in FAM if abs(table[n][cname]["raw"]) < 0.15)
        summary[cname] = {"random_mean": float(np.mean(rc)), "other_mean": float(np.mean(nr)),
                          "gap": float(np.mean(rc) - np.mean(nr)), "n_random_ge_030": n_hi,
                          "n_below_015": n_lo}
        print(f"     {cname:<16} random mean |r| {np.mean(rc):.4f}   others {np.mean(nr):.4f}   "
              f"gap {np.mean(rc) - np.mean(nr):+.4f}   >=0.30: {n_hi}/4   <0.15: {n_lo}/6")

    # ---- E3 - does conditioning remove the M x R co-movement? --------------------------------------
    print(f"\n  E3 - the M x R pairs, raw and holding each covariate fixed")
    e3 = {}
    for n in ("Ra_random_s0", "Rb_random_s1", "Rc_random_s2"):
        raw = float(np.corrcoef(C[n], C["M_mixed_sel"])[0, 1])
        row = {"raw": raw}
        line = f"     {n} x M   raw {raw:+.4f}"
        for cname, cv in COV.items():
            pt = partial(C[n], C["M_mixed_sel"], cv)
            row[cname] = {"partial": pt, "drop": 1 - abs(pt) / max(abs(raw), 1e-12)}
            line += f"   {cname[:6]} {pt:+.4f} ({100 * row[cname]['drop']:+.1f}%)"
        e3[n] = row
        print(line)
    drops = {c: float(np.mean([e3[n][c]["drop"] for n in e3])) for c in COV}
    print(f"     mean drop per covariate: "
          + "  ".join(f"{c} {100 * d:+.1f}%" for c, d in drops.items()))

    # ---- CONTROLS ---------------------------------------------------------------------------------
    rng = np.random.default_rng(778)
    plc = float(np.corrcoef(C["Ra_random_s0"], C["Ra_random_s0"])[0, 1])
    negd = [float(np.corrcoef(C["Ra_random_s0"], n_rub[rng.permutation(P)])[0, 1])
            for _ in range(NDRAW)]
    nlo, nhi = np.percentile(negd, 2.5), np.percentile(negd, 97.5)
    shamd = [float(np.corrcoef(C["Ra_random_s0"], rng.choice(n_rub, P, replace=True))[0, 1])
             for _ in range(NDRAW)]
    print(f"\n  PLACEBO     a family against ITSELF {plc:.6f}  "
          f"{'PASS' if abs(plc - 1) < 1e-9 else 'FAIL'}")
    print(f"  NEGATIVE    {NDRAW} permutations of n_rubric: {np.mean(negd):+.4f} "
          f"[{nlo:+.4f}, {nhi:+.4f}]")
    print(f"  SHAM        a random draw from n_rubric's own distribution: {np.mean(shamd):+.4f} "
          f"[{np.percentile(shamd, 2.5):+.4f}, {np.percentile(shamd, 97.5):+.4f}]")

    print(f"\n  POSITIVE    synthetic uniform k-subsets, rubric-size variation swept:")
    dose = {}
    for spread in (0.0, 0.25, 0.5, 1.0):
        nn = np.full(P, 16) if spread == 0.0 else np.clip(
            (16 + spread * rng.normal(0, 8, P)).round(), 5, 39).astype(int)
        vals = np.zeros(P)
        for a in range(P):
            base_scores = rng.normal(0, 1, nn[a])
            ds = []
            for _ in range(4):
                s1 = rng.choice(nn[a], min(4, nn[a]), replace=False)
                s2 = rng.choice(nn[a], min(4, nn[a]), replace=False)
                ds.append(abs(base_scores[s1].mean() - base_scores[s2].mean()))
            vals[a] = float(np.mean(ds))
        if nn.std() < 1e-12:
            r = float("nan")
            note = "UNDEFINED (rubric size fixed, no variation to correlate with)"
        else:
            r = float(np.corrcoef(nn.astype(float), vals)[0, 1])
            note = f"detected {abs(r) > nhi}"
        dose[spread] = r
        print(f"     size-spread {spread:>4.2f}  n range {nn.min()}-{nn.max()}  "
              f"corr(n, |d|) {'undefined' if r != r else f'{r:+.4f}'}   {note}")
    pos = (dose[1.0] == dose[1.0]) and abs(dose[1.0]) > nhi
    g0 = dose[0.0] != dose[0.0]
    print(f"              registered band - fixed size must be UNDEFINED; full spread must be "
          f"detected: {pos and g0}  {'PASS' if pos and g0 else 'FAIL'}")

    ctrl = pos and g0 and abs(plc - 1) < 1e-9
    sn = summary["n_rubric"]
    best_stat = max(("rubricdisagree", "rubricspread"),
                    key=lambda c: summary[c]["n_random_ge_030"])
    if not ctrl:
        world = "UNVERIFIED"
    elif sn["n_random_ge_030"] >= 3 and drops["n_rubric"] >= 0.25:
        world = (f"A - DRAW GEOMETRY: n_rubric reaches 0.30 for {sn['n_random_ge_030']}/4 random "
                 f"families and conditioning drops M x R by {100 * drops['n_rubric']:.1f}%")
    elif summary[best_stat]["n_random_ge_030"] >= 4 and sn["n_below_015"] >= 4:
        world = (f"B - RIGHT HYPOTHESIS, WRONG OBJECT: `{best_stat}` reaches 0.30 for "
                 f"{summary[best_stat]['n_random_ge_030']}/4 while n_rubric stays small")
    elif all(summary[c]["n_below_015"] >= 4 for c in COV):
        world = "C - NO RUBRIC STATISTIC EXPLAINS IT, and this time the criteria are the arms' own"
    else:
        world = ("NO WORLD - covariate behaviour straddles the registered bands; counts reported, "
                 "none claimed")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/rubric_not_pool.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "object_check": {"in_rubric": in_rubric, "pool_overlap": in_pool,
                                         "distinct_pool_sets": n_pool_sets},
        "n_rubric_median": float(np.median(n_rub)), "n_rubric_min": int(n_rub.min()),
        "n_rubric_max": int(n_rub.max()), "degenerate_counts": deg,
        "corr_nrubric_difficulty": r_diff,
        "table": table, "summary": summary, "E3": e3, "drops": drops,
        "controls": {"placebo": plc, "negative_lo": float(nlo), "negative_hi": float(nhi),
                     "sham_mean": float(np.mean(shamd)),
                     "dose": {str(k): (None if v != v else v) for k, v in dose.items()},
                     "positive": bool(pos), "g0": bool(g0)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
