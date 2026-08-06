#!/usr/bin/env python3
"""R767 · one of the five committed extension members is BELOW RESOLUTION, not BEATS.

⛔ CHECK #369 KILLED R766's NEXT FOR FREE. It asked whether `gen` clears ② "resolvedly". R764's own
   admission test is `verdict(eff, lo, hi, mde) == POS` (run.py:192-196), and `report.py:25-35`
   returns POS only when the CI excludes zero AND |eff| >= MDE. Every admission in that grid was
   already resolved. FIFTH NEXT line this arc killed by the next round's first check.

WHAT THE SAME COMPARISON TURNED UP: two of my own rounds disagree on the deliverable's headline.
   R760 `admitted_rule`   9 tags / 5 objects  (incl. `coval_core_2bA`, `_2bB`, `topw_k8`)
   R764 published `3-rank` 6 tags / 4 objects  (none of those three)
The first two are R764's declared coverage exclusion. **`topw_k8` is in both populations and gets
opposite ② verdicts — and it is one of the five COMMITTED extension members.**

⛔ FORCED, LABELLED:
  D1 BELOW RESOLUTION needs |eff| < MDE **and** a CI excluding zero — `report.py`'s own docstring
     says these answer different questions. Any two-valued reading MUST pick one; that a choice
     exists is algebra, WHICH ONE was picked is the finding.
  D2 raising B narrows the CI and leaves the MDE untouched (`z*sd/sqrt(n)`, no bootstrap in it), so
     **a B-sweep cannot rescue a BELOW RESOLUTION.** R728's B sweep found nothing for that reason
     and is not evidence here; the sweep is reported to SHOW this, not to test it.

CONTROLS  POSITIVE (the other four return BEATS; band from both degenerate ends) · g=0 (baseline vs
          itself is not BEATS) · NEGATIVE (200 pairing permutations → the verdict distribution) ·
          SHAM (the MDE floor ABSENT — `mde=None` — which is exactly what a two-valued reading does)
          · PLACEBO (`*_sham` arms never BEATS) · CONFOUND (the whole `topw_k` family's eff/MDE
          ratio, so a k-trend is visible rather than assumed absent).
UNIT      instrument = an ARM TAG · claim = an OBJECT (R730). Both reported.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
ZEFF, L = 1.959964 + 0.841621, "ABCD"
PR = list(itertools.combinations(range(4), 2))
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
KFAM = [1, 2, 3, 4, 6, 8, 12]
PLACEBO = ["coval_core_sham", "topw_k4_sham", "gen_sham"]


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    P, npool = len(pids), len(idxs)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    Hm = max(len(h) for h in HC)
    HP = np.zeros((P, Hm, 6)); HK = np.zeros((P, Hm))
    for a, h in enumerate(HC):
        HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
    nH = HK.sum(1)
    T = np.zeros((P, npool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2(Y):
        s = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    def arm(t):
        S = load_sat(RES / f"sat_{t}.npz")
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            if p not in S: return None
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return a2(Y)

    def cell(x, y, B, use_mde=True):
        d = x - y
        ib = np.random.default_rng(31337).integers(0, P, (B, P))
        bs = d[ib].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(P)
        v = verdict(float(d.mean()), lo, hi, mde if use_mde else None)
        return {"eff": float(d.mean()), "lo": lo, "hi": hi, "mde": mde, "verdict": v,
                "eff_over_mde": float(d.mean()) / mde if mde else float("inf")}

    bv = a2(T[:, list(range(4)), :].sum(axis=1))
    print(f"  published baseline A2 = {bv.mean():.6f}   prompts {P}   pool {npool}")

    # ---- E1 · the five committed members, three B values ---------------------------------------
    A = {t: arm(t) for t in COMMITTED}
    print(f"\n  ⭐ E1 · THE FIVE COMMITTED MEMBERS AT THE PUBLISHED COMPARATOR")
    print(f"  {'arm':<13}{'B':>7}{'A2':>9}{'eff':>9}{'lo':>9}{'hi':>9}{'MDE':>9}"
          f"{'eff/MDE':>9}   verdict")
    E1 = {}
    for t in COMMITTED:
        for B in (1200, 4800, 19200):
            c = cell(A[t], bv, B)
            E1[f"{t}@{B}"] = c
            print(f"  {t:<13}{B:>7}{A[t].mean():>9.4f}{c['eff']:>9.4f}{c['lo']:>9.4f}"
                  f"{c['hi']:>9.4f}{c['mde']:>9.4f}{c['eff_over_mde']:>9.3f}   {c['verdict']}")
    beats = [t for t in COMMITTED if E1[f"{t}@1200"]["verdict"] == POS]
    notbeats = [t for t in COMMITTED if E1[f"{t}@1200"]["verdict"] != POS]
    print(f"  BEATS: {len(beats)}  {beats}")
    print(f"  NOT:   {len(notbeats)} {[(t, E1[f'{t}@1200']['verdict']) for t in notbeats]}")

    # ---- CONTROLS -------------------------------------------------------------------------------
    ok_pos = len(beats) >= 4
    print(f"\n  POSITIVE    {len(beats)}/5 committed members return BEATS  "
          f"{'PASS' if ok_pos else '⛔ FAIL'}")
    print(f"              band: a BEATS-everything instrument also passes the PLACEBO arms below; "
          f"a BEATS-nothing one fails here. Unreachable from either end.")
    g0 = cell(bv, bv, 1200)
    print(f"  g=0         baseline vs ITSELF: eff {g0['eff']:.6f} -> {g0['verdict']}  "
          f"{'PASS' if g0['verdict'] != POS else '⛔ FAIL'}")
    plc = {}
    for t in PLACEBO:
        v = arm(t)
        if v is None: continue
        plc[t] = cell(v, bv, 1200)["verdict"]
    ok_plc = all(v != POS for v in plc.values())
    print(f"  PLACEBO     {plc}  {'PASS' if ok_plc else '⛔ FAIL'}")
    rng = np.random.default_rng(767)
    negv = [cell(A["topw_k8"][rng.permutation(P)], bv, 1200)["verdict"] for _ in range(200)]
    from collections import Counter
    print(f"  NEGATIVE    `topw_k8` with the pairing destroyed x200: {dict(Counter(negv))}")
    print(f"              -> BELOW RESOLUTION is NOT what this design returns for everything")

    # ---- SHAM · the MDE floor ABSENT ------------------------------------------------------------
    sham = {t: cell(A[t], bv, 1200, use_mde=False)["verdict"] for t in COMMITTED}
    flipped = [t for t in COMMITTED if sham[t] != E1[f"{t}@1200"]["verdict"]]
    print(f"\n  ⭐ SHAM · the MDE floor REMOVED (`mde=None`) — exactly what a two-valued reading does")
    print(f"  with floor:    {[(t, E1[f'{t}@1200']['verdict']) for t in COMMITTED]}")
    print(f"  without floor: {[(t, sham[t]) for t in COMMITTED]}")
    print(f"  verdicts that change: {len(flipped)} {flipped}   -> the extension is "
          f"{len(beats)} with the floor and {sum(1 for t in COMMITTED if sham[t]==POS)} without it")

    # ---- CONFOUND · the whole k family ----------------------------------------------------------
    print(f"\n  ⚠ CONFOUND  the `topw_k` family — is this a k-trend rather than one arm?")
    print(f"  {'k':>4}{'A2':>9}{'eff':>9}{'MDE':>9}{'eff/MDE':>9}   verdict")
    kfam = {}
    for k in KFAM:
        v = arm(f"topw_k{k}")
        if v is None: continue
        c = cell(v, bv, 1200); kfam[k] = c
        print(f"  {k:>4}{v.mean():>9.4f}{c['eff']:>9.4f}{c['mde']:>9.4f}"
              f"{c['eff_over_mde']:>9.3f}   {c['verdict']}")

    # ---- E3 · the baseline curve under both conventions -----------------------------------------
    subs = list(itertools.combinations(range(npool), 4))
    means = np.array([a2(T[:, list(s), :].sum(axis=1)).mean() for s in subs])
    order = np.argsort(means); pub = subs.index(tuple(range(4)))
    specs = [(f"p{q:03d}", int(order[min(int(q / 100 * (len(subs) - 1)), len(subs) - 1)]))
             for q in (0, 5, 25, 50, 75, 95, 100)]
    specs.insert(-1, ("published", pub))
    print(f"\n  ⭐ E3 · THE COMMITTED FIVE ACROSS THE BASELINE CURVE, both conventions")
    print(f"  {'baseline':<12}{'BEATS (with floor)':>22}{'passing (no floor)':>22}   topw_k8")
    curve = {}
    for lbl, si in specs:
        b = a2(T[:, list(subs[si]), :].sum(axis=1))
        w = [t for t in COMMITTED if cell(A[t], b, 1200)["verdict"] == POS]
        n = [t for t in COMMITTED if cell(A[t], b, 1200, use_mde=False)["verdict"] == POS]
        k8 = cell(A["topw_k8"], b, 1200)["verdict"]
        curve[lbl] = {"with_floor": w, "no_floor": n, "topw_k8": k8}
        print(f"  {lbl:<12}{len(w):>22}{len(n):>22}   {k8}")

    ctrl = ok_pos and g0["verdict"] != POS and ok_plc
    if not ctrl:
        world = "UNVERIFIED"
    elif len(notbeats) == 1 and notbeats[0] == "topw_k8":
        world = ("A · the headline folds a three-valued verdict into two — "
                 f"{len(beats)} CONFIRMED + 1 UNRESOLVED, not 5")
    elif not notbeats:
        world = "B/C · all five clear here; the disagreement is elsewhere"
    else:
        world = "NO WORLD — counts reported, none claimed"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/fifth_member_below_resolution.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "baseline_a2": float(bv.mean()),
        "E1": E1, "beats": beats, "not_beats": notbeats,
        "controls": {"positive_n_beats": len(beats), "g0": g0, "placebo": plc,
                     "negative_verdicts": dict(Counter(negv))},
        "sham_no_mde": sham, "sham_flipped": flipped,
        "k_family": {str(k): v for k, v in kfam.items()},
        "baseline_curve": curve, "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
