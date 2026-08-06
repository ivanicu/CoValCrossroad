#!/usr/bin/env python3
"""R766 · every "scoring floor = 0" in this campaign was measured on within-pass replicas.

⛔ CHECK #368 KILLED THREE HYPOTHESES BEFORE ANY ROUND WAS BUILT:
 ① ORDER — `score.py:58` stores `int(i)`, so `sorted()` is numeric and `idxs[0:4] == [0,1,2,3]`.
 ② CONTEXT — the nested `topw_k{1,2,3,4,6,8,12}` family gives a shared criterion the SAME
   satisfaction to 9 decimals at every k, so satisfaction is not a function of the co-scored set.
 ③ JUDGE IDENTITY — R424/R426's anchor test is INADMISSIBLE for `generic`: its criteria appear in no
   full table, so the positive control returns 0.1087, near the ~0.03 coincidence floor.

WHAT SURVIVES CONTRADICTS TWO PUBLISHED ZEROS. `sat_generic` and `sat_genericpool16[0:4]` hold the
same four criterion strings (R765: string-identical on 968/968), same indices, same letters — and
differ on 957 of 968 prompts.
   R419: "the scoring-only floor is exactly zero" (`--limit 200`).
   R765: "same judge, identical criteria -> |Δ A2| = 0.0000 on 10 pairs."
⚠ EVERY ONE OF R765's 10 PAIRS IS A REPLICATION ARTIFACT BY NAME OR BY R730 — `_detA/_detB`,
  `_ctlS0/_ctlS1`, `_oracle_kA/kB`, `greedy_kA/kB`, `indep_kA/kB`. A pair built to be identical
  cannot measure whether scoring is identical. §4's first row, published as a finding.

⛔ FORCED, LABELLED:
  D1 a pair built to be identical returns zero BY CONSTRUCTION; the measurement is how many pairs
     are NOT of that kind.
  D2 |Δ A2| is |Δ satisfaction| pushed through a SIGN function, so a large cell discrepancy can give
     a small A2 discrepancy. "A2 barely moved" is not evidence the values agree — R765 read it so.

CONTROLS  POSITIVE (nested k-sweep, |Δ| = 0 to 1e-12) · g=0 (artifact vs itself) · NEGATIVE (two
          different criteria must differ) · SHAM (criterion identity removed: `gen`, overlap 0.0010)
          · PLACEBO (`topw_k4` vs `_detA` at the CELL level) · CONFOUND (signed mean and the
          share above 0.5, to separate run-to-run noise from a systematic offset).
UNIT      instrument = a CELL (prompt x criterion x response), 15,488 · claim = an A2 NUMBER, 1.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
L = "ABCD"
PAIRS4 = list(itertools.combinations(range(4), 2))
REPLICA_MARK = ("_det", "_ctl", "_kA", "_kB")


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def cells(A, B, pids, ks):
    """Paired satisfaction values over (prompt x criterion x response)."""
    a, b = [], []
    for p in pids:
        for i in ks:
            for x in L:
                if (i, x) in A[p] and (i, x) in B[p]:
                    a.append(A[p][(i, x)]); b.append(B[p][(i, x)])
    return np.array(a), np.array(b)


def main():
    G = load_sat(RES / "sat_generic.npz")
    P = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(G) & set(P))
    ks = list(range(4))

    # ---- CONTROLS on the comparison instrument ------------------------------------------------
    core = {k: json.loads((RES / f"core_topw_k{k}.json").read_text())
            for k in (1, 2, 3, 4, 6, 8, 12) if (RES / f"core_topw_k{k}.json").exists()}
    sat = {k: load_sat(RES / f"sat_topw_k{k}.npz") for k in core}
    kp = sorted(set.intersection(*[set(v) for v in core.values()]))
    worst = 0.0
    for p in kp:
        c0 = core[1][p][0]
        vals = []
        for k in sorted(core):
            j = list(core[k][p]).index(c0)
            vals.append([sat[k][p].get((j, x), float("nan")) for x in L])
        V = np.array(vals)
        worst = max(worst, float(np.nanmax(V.max(0) - V.min(0))))
    pos_ok = worst <= 1e-12
    print(f"  POSITIVE    nested topw_k sweep, one criterion at k={sorted(core)}: "
          f"worst spread {worst:.3e}  {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"              band: an all-different instrument fails this; an all-same one fails "
          f"NEGATIVE below. Unreachable from either degenerate end.")

    ga, gb = cells(G, G, pids, ks)
    g0 = int((ga != gb).sum())
    print(f"  g=0         `sat_generic` vs itself: {g0} differing of {len(ga)}  "
          f"{'PASS' if g0 == 0 else '⛔ FAIL'}")

    n0, n1 = cells(G, G, pids, [0]), cells(G, G, pids, [1])
    negd = float((n0[0] != n1[0]).mean()) if len(n0[0]) == len(n1[0]) else float("nan")
    print(f"  NEGATIVE    two DIFFERENT criteria (`generic[0]` vs `generic[1]`) differ on "
          f"{negd:.4f} of cells  {'PASS' if negd > 0.5 else '⛔ FAIL'}")

    D = load_sat(RES / "sat_topw_k4_detA.npz")
    T4 = load_sat(RES / "sat_topw_k4.npz")
    dp = sorted(set(D) & set(T4))
    pa, pb = cells(T4, D, dp, ks)
    plc = int((pa != pb).sum())
    print(f"  PLACEBO     `topw_k4` vs `_detA` AT THE CELL LEVEL: {plc} differing of {len(pa)}  "
          f"{'PASS' if plc == 0 else '⛔ FAIL'}")

    # ---- E1 · the across-pass discrepancy -----------------------------------------------------
    A, B = cells(G, P, pids, ks)
    d = A - B
    nz = int((d != 0).sum())
    pr_diff = sum(1 for p in pids
                  if any(abs(G[p].get((i, x), 0.0) - P[p].get((i, x), 0.0)) > 1e-12
                         for i in ks for x in L))
    share = float((d > 0).mean())
    print(f"\n  ⭐ E1 · ACROSS-PASS, identical criteria — {len(A)} cells, {len(pids)} prompts")
    print(f"  differing cells   {nz} / {len(A)} = {nz/len(A):.4f}      "
          f"differing prompts {pr_diff} / {len(pids)}")
    print(f"  |Δ| mean {np.abs(d).mean():.6f}  median {np.median(np.abs(d)):.6f}  "
          f"p95 {np.percentile(np.abs(d),95):.6f}  max {np.abs(d).max():.6f}")
    print(f"  ⚠ CONFOUND  signed mean {d.mean():+.6f}   share(generic > pool) {share:.4f}  -> "
          f"{'SYMMETRIC — run-to-run' if 0.40 <= share <= 0.60 else 'SYSTEMATIC OFFSET — judge or setting'}")

    # ---- SHAM · criterion identity removed ----------------------------------------------------
    GN = load_sat(RES / "sat_gen.npz")
    sp = sorted(set(G) & set(GN))
    sa, sb = cells(G, GN, sp, ks)
    ds = sa - sb
    print(f"  SHAM        `generic` vs `gen` (criteria NOT identical, overlap 0.0010): "
          f"|Δ| mean {np.abs(ds).mean():.6f}  median {np.median(np.abs(ds)):.6f}")
    print(f"              ratio identical/different = {np.abs(d).mean()/max(1e-12,np.abs(ds).mean()):.4f}"
          f"  -> criterion identity buys {1-np.abs(d).mean()/max(1e-12,np.abs(ds).mean()):.1%}")

    # ---- E2 · classify every identical-criteria pair -------------------------------------------
    cores, sats = {}, {}
    for p in sorted(RES.glob("core_*.json")):
        t = p.name[5:-5]
        if (RES / f"sat_{t}.npz").exists():
            try:
                cores[t] = json.loads(p.read_text())
            except Exception:
                pass
    key = {}
    for t, c in cores.items():
        if set(pids) <= set(c):
            key.setdefault(tuple(tuple(c[p]) for p in pids), []).append(t)
    groups = [sorted(v) for v in key.values() if len(v) > 1]
    def within_pass(x, y):
        return any(m in x or m in y for m in REPLICA_MARK)
    rows = []
    for grp in groups:
        for x, y in itertools.combinations(grp, 2):
            rows.append({"pair": f"{x} vs {y}", "within_pass": within_pass(x, y)})
    n_w = sum(1 for r in rows if r["within_pass"])
    print(f"\n  ⭐ E2 · identical-criteria pairs: {len(rows)}   WITHIN-PASS by name/R730: {n_w}   "
          f"ACROSS-PASS candidates: {len(rows)-n_w}")
    print(f"     ⚠ LOWER BOUND — 'same pass' is not recorded anywhere in the release; it is inferred")

    # ---- E3 · does the comparator's percentile move? -------------------------------------------
    targets, _ = load_targets()
    base = load_sat(RES / "sat_random_k4_s0.npz")
    P_ids = sorted({p for p in base if p in targets and p in P and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in P[P_ids[0]]})
    n_pool, NP = len(idxs), len(P_ids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in P_ids]
    Hm = max(len(h) for h in HC)
    HP = np.zeros((NP, Hm, 6)); HK = np.zeros((NP, Hm))
    for a, h in enumerate(HC):
        HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
    nH = HK.sum(1)
    T = np.zeros((NP, n_pool, 4))
    for a, p in enumerate(P_ids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = P[p].get((i, x), 0.0)

    def a2_of_y(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS4]] - Y[:, [j for _, j in PAIRS4]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    subs = list(itertools.combinations(range(n_pool), 4))
    means = np.array([a2_of_y(T[:, list(s), :].sum(axis=1)).mean() for s in subs])
    pub = subs.index(tuple(range(4)))
    pct0 = 100.0 * (means < means[pub]).mean()
    rng = np.random.default_rng(766)
    pcts = []
    sd = float(np.abs(d).std())
    for _ in range(200):
        Tn = T.copy()
        Tn[:, :4, :] += rng.normal(0, sd, (NP, 4, 4))
        m = a2_of_y(Tn[:, list(range(4)), :].sum(axis=1)).mean()
        pcts.append(100.0 * (means < m).mean())
    print(f"\n  ⭐ E3 · the comparator's percentile under the measured discrepancy")
    print(f"  committed (R527) 93.7 · recomputed {pct0:.2f} · perturbed x200 "
          f"{np.mean(pcts):.2f} [{np.percentile(pcts,2.5):.2f}, {np.percentile(pcts,97.5):.2f}]"
          f"  (sd = |Δ| sd = {sd:.6f})")
    moved = not (np.percentile(pcts, 2.5) <= pct0 <= np.percentile(pcts, 97.5))
    print(f"  percentile moves off its point: {moved}")

    ctrl = pos_ok and g0 == 0 and negd > 0.5 and plc == 0
    if not ctrl:
        world = "UNVERIFIED"
    elif 0.40 <= share <= 0.60 and nz < len(A):
        world = "A · the published zeros were within-pass; the across-pass floor is NOT zero"
    else:
        world = "B · systematic offset — judge or setting, not run-to-run variance"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/across_pass_scoring_floor.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_cells": len(A), "n_prompts": len(pids),
        "differing_cells": nz, "differing_prompts": pr_diff,
        "abs_mean": float(np.abs(d).mean()), "abs_median": float(np.median(np.abs(d))),
        "abs_p95": float(np.percentile(np.abs(d), 95)), "abs_max": float(np.abs(d).max()),
        "signed_mean": float(d.mean()), "share_generic_gt_pool": share,
        "sham_abs_mean": float(np.abs(ds).mean()),
        "controls": {"positive_kspread": worst, "g0_differing": g0,
                     "negative_diff_share": negd, "placebo_cell_differing": plc},
        "pairs_total": len(rows), "pairs_within_pass": n_w,
        "pairs_across_pass": len(rows) - n_w, "pair_rows": rows,
        "pct_committed": 93.7, "pct_recomputed": pct0,
        "pct_perturbed_mean": float(np.mean(pcts)),
        "pct_perturbed_lo": float(np.percentile(pcts, 2.5)),
        "pct_perturbed_hi": float(np.percentile(pcts, 97.5)),
        "percentile_moves": bool(moved), "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
