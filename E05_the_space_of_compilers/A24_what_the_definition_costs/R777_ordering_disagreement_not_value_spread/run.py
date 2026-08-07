#!/usr/bin/env python3
"""R777 · the pool quantity that matters is ORDERING DISAGREEMENT, not value spread.

CHECK #379: k IS DEAD ON INSPECTION, from committed numbers and no measurement.
    F3 x M  share k exactly (both {4})           -> relative correlation -0.0137  (LOWEST)
    Ra x M  share NO k ({2,3,6,8,12} vs {4})     -> +0.7151                        (HIGHEST)
  corr(k-overlap, relative) over the 15 pairs = +0.1620, with its extremes inverted. R776's
  registered NEXT closes before this round begins.

WHAT THE ORDERING ACTUALLY TRACKS: the top six pairs are exactly the six among {Ra, Rb, Rc, M} -- the
four families containing `random_k` arms. And R776's mechanism was right in spirit, wrong in
statistic: two random draws differ where the pool's criteria INDUCE DIFFERENT ORDERINGS, not where
their satisfaction VALUES are spread. `poolspread` measured the wrong pool quantity.

FORCED, LABELLED:
  D1 k is dead by the composition table -- a derivation, not a measurement.
  D2 `orderdisagree` and `poolspread` may be the same quantity relabelled; their mutual correlation
     is therefore reported FIRST, before any scale correlation.
  D3 a random draw's expected |d| rises with ordering disagreement BY CONSTRUCTION -- if all 16
     criteria induce one ordering, any two draws agree and |d| = 0 whatever k is. So a positive
     correlation for the random families is partly forced; the measurement is its SIZE and whether the
     NON-random families show it too.

CONTROLS  POSITIVE (a swept synthetic pool; at zero disagreement the correlation is UNDEFINED and is
          printed as such -- the defect R776 caught in its own g=0 cell) - g=0 - NEGATIVE (200
          permutations) - SHAM (a random draw from `orderdisagree`'s own distribution) - PLACEBO -
          CONFOUND (per-prompt tie share, and the partial holding it fixed).
UNIT      prompt - arm pair within a family - FAMILY (6) for E2, FAMILY PAIR for E3.
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
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
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
    """corr(x, y) holding z fixed."""
    rxy = float(np.corrcoef(x, y)[0, 1])
    rxz = float(np.corrcoef(x, z)[0, 1])
    ryz = float(np.corrcoef(y, z)[0, 1])
    den = math.sqrt(max((1 - rxz ** 2) * (1 - ryz ** 2), 1e-12))
    return (rxy - rxz * ryz) / den


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    NC = len(idxs)

    T = np.zeros((P, NC, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c_, x in enumerate(L):
                T[a, bi, c_] = POOL[p].get((i, x), 0.0)

    # ---- E1 : the arm-free covariates -----------------------------------------------------------
    S = np.sign(T[:, :, [i for i, _ in PR]] - T[:, :, [j for _, j in PR]])   # (P, NC, 6)
    dis = np.zeros(P)
    for a in range(P):
        d = 0.0
        for i, j in itertools.combinations(range(NC), 2):
            d += float((S[a, i] != S[a, j]).mean())
        dis[a] = d / math.comb(NC, 2)
    tieshare = (S == 0).mean(axis=(1, 2))
    poolspread = T.std(axis=(1, 2))
    print(f"  prompts {P}   pool criteria {NC}   response pairs {len(PR)}")
    print(f"  orderdisagree  mean {dis.mean():.4f} sd {dis.std():.4f} "
          f"quantiles {np.round(np.percentile(dis, [25, 50, 75]), 4).tolist()}")
    print(f"  tie share      mean {tieshare.mean():.4f}   poolspread mean {poolspread.mean():.4f}")

    # ---- D2 : are the two covariates the same quantity? Reported FIRST. -------------------------
    r_cov = float(np.corrcoef(dis, poolspread)[0, 1])
    print(f"\n  D2 FIRST    corr(orderdisagree, poolspread) = {r_cov:+.4f}   "
          f"-> {'SAME QUANTITY RELABELLED' if abs(r_cov) >= 0.7 else 'different quantities'}")
    print(f"              corr(orderdisagree, tieshare)   = "
          f"{float(np.corrcoef(dis, tieshare)[0, 1]):+.4f}   (the registered confound axis)")

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

    # ---- E2 : the covariate against each family --------------------------------------------------
    print(f"\n  E2 - corr(scale, orderdisagree) per family, with the tie-share partial")
    cov = {}
    for n in FAM:
        r1 = float(np.corrcoef(C[n], dis)[0, 1])
        pt = partial(C[n], dis, tieshare)
        cov[n] = {"raw": r1, "partial_tieshare": pt,
                  "random_containing": n in RANDOM_CONTAINING}
        print(f"     {n:<16}{'RANDOM' if n in RANDOM_CONTAINING else '  --  '}  "
              f"corr {r1:+.4f}   partial(tie share) {pt:+.4f}")
    rc = [cov[n]["raw"] for n in FAM if n in RANDOM_CONTAINING]
    nr = [cov[n]["raw"] for n in FAM if n not in RANDOM_CONTAINING]
    gap = float(np.mean(np.abs(rc)) - np.mean(np.abs(nr)))
    print(f"     random-containing mean |corr| {np.mean(np.abs(rc)):.4f} (n={len(rc)})   "
          f"others {np.mean(np.abs(nr)):.4f} (n={len(nr)})   gap {gap:+.4f}")
    n_hi = sum(1 for n in FAM if n in RANDOM_CONTAINING and abs(cov[n]["raw"]) >= 0.30)
    n_lo = sum(1 for v in cov.values() if abs(v["raw"]) < 0.15)
    collapse = sum(1 for v in cov.values()
                   if abs(v["partial_tieshare"]) < abs(v["raw"]) / 3)
    print(f"     random families with |corr| >= 0.30: {n_hi}/4   families < 0.15: {n_lo}/6   "
          f"partial collapsing below a third: {collapse}/6")

    # ---- E3 : does conditioning remove the M x R excess? -----------------------------------------
    print(f"\n  E3 - the M x R pairs, raw and holding `orderdisagree` fixed")
    e3 = {}
    for n in ("Ra_random_s0", "Rb_random_s1", "Rc_random_s2"):
        raw = float(np.corrcoef(C[n], C["M_mixed_sel"])[0, 1])
        pt = partial(C[n], C["M_mixed_sel"], dis)
        e3[n] = {"raw": raw, "partial": pt, "drop": 1 - abs(pt) / max(abs(raw), 1e-12)}
        print(f"     {n} x M   raw {raw:+.4f}   partial {pt:+.4f}   "
              f"drop {100 * e3[n]['drop']:.1f}%")
    mean_drop = float(np.mean([v["drop"] for v in e3.values()]))
    print(f"     mean drop {100 * mean_drop:.1f}%")

    # ---- CONTROLS --------------------------------------------------------------------------------
    rng = np.random.default_rng(777)
    plc = float(np.corrcoef(C["Ra_random_s0"], C["Ra_random_s0"])[0, 1])
    negd = [float(np.corrcoef(C["Ra_random_s0"], dis[rng.permutation(P)])[0, 1])
            for _ in range(NDRAW)]
    nlo, nhi = np.percentile(negd, 2.5), np.percentile(negd, 97.5)
    shamd = [float(np.corrcoef(C["Ra_random_s0"], rng.choice(dis, P, replace=True))[0, 1])
             for _ in range(NDRAW)]
    print(f"\n  PLACEBO     a family against ITSELF {plc:.6f}  "
          f"{'PASS' if abs(plc - 1) < 1e-9 else 'FAIL'}")
    print(f"  NEGATIVE    {NDRAW} permutations of the covariate: {np.mean(negd):+.4f} "
          f"[{nlo:+.4f}, {nhi:+.4f}]")
    print(f"  SHAM        a random draw from `orderdisagree`'s own distribution: "
          f"{np.mean(shamd):+.4f} [{np.percentile(shamd, 2.5):+.4f}, "
          f"{np.percentile(shamd, 97.5):+.4f}]")

    print(f"\n  POSITIVE    synthetic pool, ordering disagreement swept:")
    dose = {}
    for w in (0.0, 0.25, 0.5, 1.0):
        Tsyn = np.zeros((P, NC, 4))
        shared = rng.normal(0, 1, (P, 4))
        for i in range(NC):
            Tsyn[:, i, :] = shared + w * rng.normal(0, 1, (P, 4))
        Ssyn = np.sign(Tsyn[:, :, [i for i, _ in PR]] - Tsyn[:, :, [j for _, j in PR]])
        dsyn = np.array([np.mean([float((Ssyn[a, i] != Ssyn[a, j]).mean())
                                  for i, j in itertools.combinations(range(NC), 2)])
                         for a in range(P)])
        draws = []
        for _ in range(5):
            sel = rng.choice(NC, 4, replace=False)
            draws.append(Tsyn[:, sel, :].sum(1))
        sc = np.abs(np.array([np.sign(x[:, [i for i, _ in PR]] - x[:, [j for _, j in PR]]).mean(1)
                              - np.sign(y[:, [i for i, _ in PR]] - y[:, [j for _, j in PR]]).mean(1)
                              for x, y in itertools.combinations(draws, 2)])).mean(0)
        if dsyn.std() < 1e-12 or sc.std() < 1e-12:
            r = float("nan")
            note = "UNDEFINED (no disagreement, every draw identical)"
        else:
            r = float(np.corrcoef(sc, dsyn)[0, 1])
            note = f"detected {r > nhi}"
        dose[w] = r
        print(f"     width {w:>4.2f}  mean disagreement {dsyn.mean():.4f}  corr "
              f"{'undefined' if r != r else f'{r:+.4f}'}   {note}")
    pos = (dose[1.0] == dose[1.0]) and dose[1.0] > nhi
    g0 = dose[0.0] != dose[0.0]     # NaN: undefined, as registered
    finite = [dose[w] for w in (0.25, 0.5, 1.0) if dose[w] == dose[w]]
    mono = all(a <= b + 1e-9 for a, b in zip(finite, finite[1:]))
    print(f"              registered band - disagreement 0 must be UNDEFINED (not a small number); "
          f"1.00 must be detected: {pos and g0}  {'PASS' if pos and g0 else 'FAIL'}   "
          f"monotone over the defined cells: {mono}")

    ctrl = pos and g0 and abs(plc - 1) < 1e-9 and collapse <= 3
    if not ctrl:
        world = "UNVERIFIED"
    elif abs(r_cov) >= 0.7:
        world = f"C - SAME QUANTITY RELABELLED: corr(orderdisagree, poolspread) = {r_cov:+.4f}"
    elif n_hi >= 3 and gap >= 0.15 and mean_drop >= 0.25:
        world = ("A - ORDERING DISAGREEMENT IS THE AXIS: "
                 f"{n_hi}/4 random families >= 0.30, gap {gap:+.4f}, M x R drop "
                 f"{100 * mean_drop:.1f}%")
    elif n_lo >= 4:
        world = f"B - NOT THE AXIS EITHER: {n_lo}/6 families below 0.15"
    else:
        world = (f"NO WORLD - {n_hi}/4 random families >= 0.30, gap {gap:+.4f}, drop "
                 f"{100 * mean_drop:.1f}%; the registered bands are not all met")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/ordering_disagreement.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "n_criteria": NC,
        "orderdisagree_mean": float(dis.mean()), "orderdisagree_sd": float(dis.std()),
        "tieshare_mean": float(tieshare.mean()),
        "corr_orderdisagree_poolspread": r_cov,
        "corr_orderdisagree_tieshare": float(np.corrcoef(dis, tieshare)[0, 1]),
        "covariate": cov, "random_mean_abs": float(np.mean(np.abs(rc))),
        "other_mean_abs": float(np.mean(np.abs(nr))), "gap": gap,
        "n_random_above_030": n_hi, "n_below_015": n_lo, "n_partial_collapse": collapse,
        "E3": e3, "mean_drop": mean_drop,
        "controls": {"placebo": plc, "negative_lo": float(nlo), "negative_hi": float(nhi),
                     "sham_mean": float(np.mean(shamd)),
                     "dose": {str(k): (None if v != v else v) for k, v in dose.items()},
                     "positive": bool(pos), "g0": bool(g0), "monotone": bool(mono)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
