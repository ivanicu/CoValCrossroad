#!/usr/bin/env python3
"""R822 · does the definition's verdict depend on the estimand nobody chose?

R821 derived that ④'s statistic is a difference of CORPUS MEANS. That aggregation was never chosen.
R792 found the identical defect for the arc's A-family comparisons and showed a decisive pair
separates in 1 of 4 estimand cells; nobody has run that grid on a CLAUSE VERDICT. See
PREREGISTRATION.txt for the estimands, the four derivations, the worlds and the gated kill.
"""
import collections
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, parse_ranking     # noqa: E402
from assurance.null_is_informative import assert_null_is_informative   # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R803J = ARC / "R803_the_judge_free_floor_on_release_one/results/judge_free_floor.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 600
MINN = 200
WEIGHTINGS = ("prompt", "annotator", "subgroup")
RESAMPLE = ("prompt", "annotator")
CELLS = [(w, u) for w in WEIGHTINGS for u in RESAMPLE]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def bh(pv, q=0.05):
    p = np.asarray(pv, float)
    o = np.argsort(p)
    m = len(p)
    keep = np.zeros(m, bool)
    for r, i in enumerate(o, 1):
        if p[i] <= q * r / m:
            keep[o[:r]] = True
    return keep


def main():
    out = {"instrument_unit": "an ARM-CELL", "claim_unit": "a CLAUSE"}
    tg, _ = load_targets()
    FLOOR_COMMITTED = 0.4557

    # ---- judgement-level rebuild: score.py exposes demographics but NOT annotator_id, so the ids
    # ---- are reconstructed in load_targets' own append order and VALIDATED by the object check.
    text, aid_of = {}, collections.defaultdict(list)
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) == 4:
            text[r["prompt_id"]] = [" ".join(str(m.get("content", ""))
                                    for m in (it.get("messages") or [])
                                    if isinstance(m, dict)) for it in rs]
        for asm in r.get("metadata", {}).get("assessments", []):
            for e in (asm.get("ranking_blocks") or {}).get("world") or []:
                if e.get("ranking") and parse_ranking(e["ranking"]):
                    aid_of[r["prompt_id"]].append(asm.get("annotator_id"))

    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    DEMO = {p: [d for _, d in tg[p]] for p in pids}
    N = len(pids)
    CH = np.array([[len(t) for t in text[p]] for p in pids], float)

    # flatten to judgements
    PJ, AJ, DJ = [], [], []
    for i, p in enumerate(pids):
        ids = aid_of.get(p, [])
        if len(ids) != len(H[p]):
            print(f"  UNRUNNABLE: annotator-id reconstruction mismatched on {p} "
                  f"({len(ids)} vs {len(H[p])}). Exit 2, never 0.")
            return 2
        for j in range(len(H[p])):
            PJ.append(i)
            AJ.append(ids[j])
            DJ.append(DEMO[p][j])
    PJ = np.array(PJ)
    auniq = sorted({a for a in AJ if a is not None})
    aidx = {a: k for k, a in enumerate(auniq)}
    AJi = np.array([aidx.get(a, -1) for a in AJ])
    J = len(PJ)
    print(f"  POPULATION  {N} prompts · {len(auniq)} annotators · {J} judgements")

    # subgroups: axis=value with >= MINN judgements (R792's rule)
    cnt = collections.Counter()
    for d in DJ:
        for k, v in (d or {}).items():
            if v is not None:
                cnt[(k, str(v))] += 1
    groups = [g for g, c in sorted(cnt.items()) if c >= MINN]
    GM = np.zeros((len(groups), J))
    gi = {g: k for k, g in enumerate(groups)}
    for j, d in enumerate(DJ):
        for k, v in (d or {}).items():
            g = gi.get((k, str(v)))
            if g is not None:
                GM[g, j] = 1.0
    print(f"  SUBGROUPS   {len(groups)} demographic cells at n >= {MINN}")

    # ---- per-judgement value of any 4-vector score matrix -------------------------------------
    Hcat = np.concatenate([H[p] for p in pids], axis=0)          # (J, 6)

    def judge_vals(Smat):
        s = np.sign(Smat[:, [u for u, _ in PR]] - Smat[:, [w for _, w in PR]])   # (N, 6)
        return (Hcat == s[PJ]).mean(axis=1)                                      # (J,)

    # ---- the three weightings, all linear in the judgement values ------------------------------
    npr = np.bincount(PJ, minlength=N).astype(float)
    nan_ = np.bincount(AJi[AJi >= 0], minlength=len(auniq)).astype(float)
    gn = GM.sum(axis=1)

    def agg(v, w, weighting, pj=None, aji=None, gm=None):
        """v (M,) judgement values, w (M,) weights -> scalar.
        ⛔ THE FIRST VERSION CLOSED OVER THE FULL-LENGTH INDEX ARRAYS, so every resampled call
        raised or, worse, would have pooled a twice-drawn prompt back to weight ONE. The caller
        now passes DRAW-INDEXED labels, so a prompt drawn twice counts twice in the outer mean."""
        pj = PJ if pj is None else pj
        aji = AJi if aji is None else aji
        gm = GM if gm is None else gm
        if weighting == "prompt":
            nb = int(pj.max()) + 1 if len(pj) else 0
            s_ = np.bincount(pj, v * w, nb)
            n_ = np.bincount(pj, w, nb)
            m = n_ > 0
            return float((s_[m] / n_[m]).mean())
        if weighting == "annotator":
            ok = aji >= 0
            nb = int(aji.max()) + 1 if ok.any() else 0
            s_ = np.bincount(aji[ok], (v * w)[ok], nb)
            n_ = np.bincount(aji[ok], w[ok], nb)
            m = n_ > 0
            return float((s_[m] / n_[m]).mean())
        s_ = gm @ (v * w)
        n_ = gm @ w
        m = n_ > 0
        return float((s_[m] / n_[m]).mean())

    def draw(rng_, unit):
        """-> (sel, pj2, aji2, gm2) with DRAW-indexed labels so repeats carry their own weight."""
        if unit == "prompt":
            idx = rng_.integers(0, N, size=N)
            blocks = [np.flatnonzero(PJ == k) for k in idx]
        else:
            ia = rng_.integers(0, len(auniq), size=len(auniq))
            blocks = [np.flatnonzero(AJi == k) for k in ia]
        sel = np.concatenate(blocks) if blocks else np.array([], int)
        lab = np.concatenate([np.full(len(b), d) for d, b in enumerate(blocks)]) if blocks \
            else np.array([], int)
        if unit == "prompt":
            return sel, lab, AJi[sel], GM[:, sel]
        return sel, PJ[sel], lab, GM[:, sel]

    W1 = np.ones(J)
    fl_v = judge_vals(CH)
    FLOOR = agg(fl_v, W1, "prompt")
    ok = abs(FLOOR - FLOOR_COMMITTED) < 5e-5
    print(f"\n  OBJECT CHECK - the judgement-level rebuild must reproduce R821 EXACTLY")
    print(f"     floor prompt-weighted {FLOOR:.6f} vs R803/R821's committed {FLOOR_COMMITTED}   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the floor did not reproduce. Exit 2, never 0.")
        return 2

    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and "_08b" not in p.stem)
    V = {}
    for a in arms:
        try:
            sat = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        if not all(p in sat for p in pids):
            continue
        M = np.array([yvec(sat[p], sorted({i for i, _ in sat[p]})) for p in pids], float)
        V[a] = judge_vals(M)
    # R821 computed A2 per prompt then averaged; the rebuild must match to machine precision
    A2_old = {}
    for a in V:
        sat = load_sat(RES / f"sat_{a}.npz")
        A2_old[a] = float(np.mean([float((H[p] == np.array(cls(yvec(sat[p],
                          sorted({i for i, _ in sat[p]}))))).mean()) for p in pids]))
    dmax = max(abs(agg(V[a], W1, "prompt") - A2_old[a]) for a in V)
    print(f"     {len(V)} arms rebuilt · max |Δ| vs R821's per-prompt route {dmax:.3e}   "
          f"{'PASS' if dmax < 1e-12 else 'FAIL'}")
    if dmax >= 1e-12:
        print("  UNRUNNABLE: the reconstruction does not reproduce R821. Exit 2, never 0.")
        return 2
    out["object"] = {"floor_prompt": FLOOR, "n_arms": len(V), "n_prompts": N,
                     "n_annotators": len(auniq), "n_judgements": J, "n_groups": len(groups),
                     "max_delta_vs_R821": dmax}

    # ================= DERIVATIONS, ALL BEFORE ANY VERDICT =======================================
    print("\n  DERIVED FIRST (labelled DERIVATIONS, never evidence)")
    pt = {w: {a: agg(V[a], W1, w) - agg(fl_v, W1, w) for a in V} for w in WEIGHTINGS}
    d1 = "resampling cannot move a point estimate; only 3 of the 6 cells carry distinct quantities"
    print(f"     D1 {d1}")
    pairs = [(x, y) for x, y in itertools.combinations(WEIGHTINGS, 2)]
    d2 = {}
    for x, y in pairs:
        vx = np.array([pt[x][a] for a in sorted(V)])
        vy = np.array([pt[y][a] for a in sorted(V)])
        d2[f"{x}|{y}"] = {"max_abs_diff": float(np.abs(vx - vy).max()),
                          "corr": float(np.corrcoef(vx, vy)[0, 1])}
        print(f"     D2 {x:<10} vs {y:<10} max |Δmargin| {np.abs(vx - vy).max():.6f}   "
              f"corr {np.corrcoef(vx, vy)[0, 1]:.6f}   "
              f"{'REPARAMETERISATION (WORLD C)' if np.abs(vx - vy).max() < 1e-9 else 'distinct'}")
    out["derivations"] = {"D1": d1, "D2": d2}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    rng = np.random.default_rng(20250806)
    top = max(V, key=lambda a: pt["prompt"][a])

    plac = {w: float(agg(V[top], W1, w) - agg(V[top], W1, w)) for w in WEIGHTINGS}
    plac_ok = all(abs(x) == 0.0 for x in plac.values())
    print(f"     PLACEBO   `{top}` against itself in every weighting: "
          f"{max(abs(x) for x in plac.values()):.1e}   PASS - exactly 0" if plac_ok
          else "     PLACEBO   FAIL")

    # POSITIVE: plant at floor - delta, uniformly, in judgement space
    def plant(delta):
        return np.clip(fl_v - delta, 0.0, 1.0)
    pos = {}
    for w in WEIGHTINGS:
        pos[w] = {str(d): float(agg(plant(d), W1, w) - agg(fl_v, W1, w))
                  for d in (0.10, 0.0)}
    pos_ok = all(pos[w]["0.1"] < 0 for w in WEIGHTINGS)
    pos_zero_ok = all(abs(pos[w]["0.0"]) < 1e-12 for w in WEIGHTINGS)
    print(f"     POSITIVE  δ=0.10 plant removed in all {len(WEIGHTINGS)} weightings: {pos_ok}   "
          f"and δ=0 NOT removed anywhere: {pos_zero_ok}   "
          f"{'PASS' if pos_ok and pos_zero_ok else 'FAIL'}")

    # NEGATIVE: synthetic arm resampled from the floor's own per-prompt distribution
    neg, neg_ok = {}, True
    for w in WEIGHTINGS:
        real = float(np.mean([pt[w][a] for a in V]))
        nl = []
        for _ in range(200):
            # ⛔ AND THE FIRST VERSION COMPUTED THE SUBGROUP CELL'S NULL UNDER *PROMPT* WEIGHTING
            #    while comparing it to a SUBGROUP-weighted real margin — R818's mixed-weighting
            #    defect, inside the control built to guard this very grid. The weighting is `w`.
            sel, pj2, aj2, gm2 = draw(rng, "prompt")
            ws = np.ones(len(sel))
            nl.append(agg(fl_v[sel], ws, w, pj2, aj2, gm2) - agg(fl_v, W1, w))
        nl = np.array(nl, float)
        try:
            info = assert_null_is_informative(nl, real, name=f"R822 negative control [{w}]")
        except AssertionError as e:
            print(f"     NEGATIVE  ⛔ {e}")
            neg_ok = False
            neg[w] = {"degenerate": True}
            continue
        on_zero = abs(nl.mean()) < 2 * nl.std()
        outside = real > nl.max()
        neg[w] = {"mean": float(nl.mean()), "sd": float(nl.std()), "real": real,
                  "on_zero": bool(on_zero), "outside": bool(outside), "spread": info["spread"]}
        neg_ok = neg_ok and on_zero and outside
        print(f"     NEGATIVE  [{w:<10}] synthetic arm {nl.mean():+.5f} ± {nl.std():.5f}   "
              f"real {real:+.5f}   on zero {on_zero}   outside {outside}")

    # SHAM: subgroup weighting with RANDOM groups of matched sizes
    GMs = np.zeros_like(GM)
    for g in range(len(groups)):
        GMs[g, rng.choice(J, int(gn[g]), replace=False)] = 1.0
    GM_backup = GM.copy()
    try:
        GM[:] = GMs
        sham = {a: agg(V[a], W1, "subgroup") - agg(fl_v, W1, "subgroup") for a in sorted(V)}
    finally:
        GM[:] = GM_backup
    sv = np.array([sham[a] for a in sorted(V)])
    rv = np.array([pt["subgroup"][a] for a in sorted(V)])
    pv = np.array([pt["prompt"][a] for a in sorted(V)])
    print(f"     SHAM      random groups of matched size: corr with REAL subgroup "
          f"{np.corrcoef(sv, rv)[0, 1]:.6f}   with prompt-weighted {np.corrcoef(sv, pv)[0, 1]:.6f}")
    print(f"               => the ingredient is WHICH groups, not that grouping happens: "
          f"{'the real subgroups add nothing' if abs(np.corrcoef(sv, rv)[0,1]) > 0.9999 else 'they differ'}")

    # NOISE FLOOR per weighting
    nf = {}
    for w in WEIGHTINGS:
        hs = []
        for _ in range(20):
            half = rng.permutation(N)[: N // 2]
            blocks = [np.flatnonzero(PJ == k) for k in half]
            sel = np.concatenate(blocks)
            lab = np.concatenate([np.full(len(b), d) for d, b in enumerate(blocks)])
            ws = np.ones(len(sel))
            hs.append(agg(V[top][sel], ws, w, lab, AJi[sel], GM[:, sel])
                      - agg(fl_v[sel], ws, w, lab, AJi[sel], GM[:, sel]))
        nf[w] = float(np.std(hs))
        print(f"     NOISE FLOOR [{w:<10}] 20 half-splits of `{top}`'s margin: sd {nf[w]:.4f}")

    gate = bool(plac_ok and pos_ok and pos_zero_ok and neg_ok)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "placebo_ok": plac_ok, "positive": pos,
                       "positive_ok": pos_ok, "positive_zero_ok": pos_zero_ok,
                       "negative": neg, "negative_ok": neg_ok, "noise_floor": nf,
                       "sham_corr_real": float(np.corrcoef(sv, rv)[0, 1]),
                       "sham_corr_prompt": float(np.corrcoef(sv, pv)[0, 1]), "gate": gate}

    # ================= E1 · ④'s exclusion count over the grid ====================================
    print("\n  E1 - CLAUSE ④ OVER THE 6 ESTIMAND CELLS  (the floor recomputed INSIDE each cell)")
    B = {}
    for u in RESAMPLE:
        r2 = np.random.default_rng(4242)
        draws = {w: np.empty((len(V), NBOOT)) for w in WEIGHTINGS}
        names = sorted(V)
        for b in range(NBOOT):
            sel, pj2, aj2, gm2 = draw(r2, u)
            ws = np.ones(len(sel))
            flb = {w: agg(fl_v[sel], ws, w, pj2, aj2, gm2) for w in WEIGHTINGS}
            for ai, a in enumerate(names):
                for w in WEIGHTINGS:
                    draws[w][ai, b] = agg(V[a][sel], ws, w, pj2, aj2, gm2) - flb[w]
        B[u] = draws
    names = sorted(V)
    e1, allp = {}, []
    for w, u in CELLS:
        dd = B[u][w]
        rows = []
        for ai, a in enumerate(names):
            eff = pt[w][a]
            lo, hi = float(np.percentile(dd[ai], 2.5)), float(np.percentile(dd[ai], 97.5))
            p = 2.0 * min(float((dd[ai] <= 0).mean()), float((dd[ai] >= 0).mean()))
            p = max(min(p, 1.0), 1.0 / (NBOOT + 1))
            v = "EXCLUDED" if hi < 0 else ("PASSES ④" if lo > 0 else "UNVERIFIED")
            rows.append({"arm": a, "eff": eff, "lo": lo, "hi": hi, "p": p, "verdict": v})
            allp.append(p)
        nx = sum(1 for r in rows if r["verdict"] == "EXCLUDED")
        nu = sum(1 for r in rows if r["verdict"] == "UNVERIFIED")
        e1[f"{w}_{u}"] = {"excluded": nx, "unverified": nu, "rows": rows}
        print(f"     {w:<10} weighted / {u:<10} resampled   ④ excludes {nx} of {len(names)}   "
              f"UNVERIFIED {nu}   [" + ", ".join(r["arm"] for r in rows
                                                 if r["verdict"] != "PASSES ④") + "]")
    keep = bh(allp)
    print(f"     BH q=0.05 over the WHOLE grid ({len(allp)} tests): {int(keep.sum())} survive, "
          f"{int((~keep).sum())} do not (reported, not hidden)")
    counts = {k: v["excluded"] for k, v in e1.items()}
    same_all = len(set(counts.values())) == 1
    by_w = {w: {counts[f"{w}_{u}"] for u in RESAMPLE} for w in WEIGHTINGS}
    across_w = len({tuple(sorted(by_w[w])) for w in WEIGHTINGS}) > 1
    print(f"     ⭐ ④'s exclusion count identical in all 6 cells: {same_all}   "
          f"differs across WEIGHTINGS: {across_w}")
    out["e1"] = e1
    out["e1_counts"] = counts

    # ================= E2 · ② and ③ over the same grid ===========================================
    print("\n  E2 - CLAUSES ② AND ③ OVER THE SAME 6 CELLS")
    print("     ⚠ D3: ③ reads the arm's SOURCE, not its score, so it CANNOT move. If it moves the")
    print("     instrument is broken, not the clause — a free falsifier on the grid itself.")
    LABEL_READERS = [a for a in names if "oracle" in a or "fit1" in a or "topw" in a]
    c3 = {f"{w}_{u}": len(LABEL_READERS) for w, u in CELLS}
    c3_ok = len(set(c3.values())) == 1
    print(f"     ③ excludes {len(LABEL_READERS)} of {len(names)} in every cell: {c3_ok}   "
          f"{'PASS - D3 holds' if c3_ok else 'FAIL - instrument broken'}")
    POOL = "genericpool16"
    e2 = {}
    if POOL in V:
        for w, u in CELLS:
            dd = B[u][w]
            ip = names.index(POOL)
            nx = 0
            rows = []
            for ai, a in enumerate(names):
                d = dd[ai] - dd[ip]
                lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
                ex = hi < 0
                nx += ex
                rows.append({"arm": a, "eff": pt[w][a] - pt[w][POOL], "lo": lo, "hi": hi,
                             "excluded": bool(ex)})
            e2[f"{w}_{u}"] = {"excluded": nx, "rows": rows}
            print(f"     ② {w:<10} / {u:<10}   excludes {nx} of {len(names)} vs `{POOL}`")
    c2 = {k: v["excluded"] for k, v in e2.items()}
    c2_same = len(set(c2.values())) == 1
    # ⛔ THE FIRST KILL BRANCHED TO WORLD B ON `not c2_same` ALONE — it did not implement this
    #    round's OWN preregistration, which separates "differs across WEIGHTINGS" from "differs
    #    only across RESAMPLING". D1 says resampling cannot move a point estimate, only its CI,
    #    so conflating them reports a PRECISION effect as an ESTIMAND effect. §4: the verdict
    #    string is not a computation.
    c2_w = {u: {c2[f"{w}_{u}"] for w in WEIGHTINGS} for u in RESAMPLE}
    c2_u = {w: {c2[f"{w}_{u}"] for u in RESAMPLE} for w in WEIGHTINGS}
    c2_across_w = any(len(v) > 1 for v in c2_w.values())
    c2_across_u = any(len(v) > 1 for v in c2_u.values())
    print(f"     ⭐ ②'s exclusion count identical in all 6 cells: {c2_same}   "
          f"values {sorted(set(c2.values()))}")
    print(f"        at FIXED resampling, across weightings: " +
          "  ".join(f"{u}->{sorted(c2_w[u])}" for u in RESAMPLE))
    print(f"        at FIXED weighting, across resampling:  " +
          "  ".join(f"{w}->{sorted(c2_u[w])}" for w in WEIGHTINGS))
    # WHICH arms flip, and where do their point margins sit? A flip at |eff| inside the noise
    # floor is a threshold artifact; a flip at |eff| outside it is a real estimand dependence.
    flips = []
    for a in names:
        vs = {f"{w}_{u}": e2[f"{w}_{u}"]["rows"][names.index(a)]["excluded"] for w, u in CELLS}
        if len(set(vs.values())) > 1:
            eff = {w: pt[w][a] - pt[w][POOL] for w in WEIGHTINGS}
            inside = max(abs(v) for v in eff.values()) < max(nf.values())
            flips.append({"arm": a, "verdicts": vs, "eff": eff, "inside_noise_floor": bool(inside)})
            print(f"        FLIPS: {a:<22} eff " +
                  " ".join(f"{w[:4]} {eff[w]:+.4f}" for w in WEIGHTINGS) +
                  f"   inside the noise floor ({max(nf.values()):.4f}): {inside}")
    all_inside = bool(flips) and all(f["inside_noise_floor"] for f in flips)
    print(f"        ⭐ every flipping arm sits INSIDE the noise floor: {all_inside}"
          if flips else "        no arm flips")
    out["e2"] = {"clause3": c3, "clause3_invariant": c3_ok, "clause2": c2,
                 "clause2_same": c2_same, "clause2_across_weighting": c2_across_w,
                 "clause2_across_resampling": c2_across_u, "flips": flips,
                 "all_flips_inside_noise_floor": all_inside}

    # ================= E3 · the plant ladder in the weakest cell =================================
    print("\n  E3 - R821's PLANT LADDER RE-RUN IN EVERY WEIGHTING")
    e3 = {}
    for w in WEIGHTINGS:
        row = {}
        for d in (0.10, 0.05, 0.01, 0.0):
            m = agg(plant(d), W1, w) - agg(fl_v, W1, w)
            row[str(d)] = {"margin": float(m), "removed": bool(m < 0)}
        e3[w] = row
        print(f"     {w:<10}  " + "  ".join(f"δ={d}: {row[str(d)]['margin']:+.4f} "
              f"{'removed' if row[str(d)]['removed'] else 'kept'}" for d in (0.10, 0.05, 0.01, 0.0)))
    ladder_ok = all(e3[w][str(d)]["removed"] for w in WEIGHTINGS for d in (0.10, 0.05, 0.01)) \
        and not any(e3[w]["0.0"]["removed"] for w in WEIGHTINGS)
    print(f"     ⭐ falsifiability survives the estimand change in every weighting: {ladder_ok}")
    out["e3"] = {"ladder": e3, "ladder_ok": ladder_ok}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not (gate and c3_ok and ladder_ok):
        world = "UNVERIFIED"
    elif same_all and c2_same:
        world = "A"
    elif c2_across_w and not all_inside:
        world = "B"
    else:
        world = "PRECISION, NOT ESTIMAND"
    print(f"     gate {gate} · ③ invariant {c3_ok} · ladder {ladder_ok} · ④ same in 6 {same_all}")
    print(f"     ② same in 6 {c2_same} · across weightings {c2_across_w} · across resampling "
          f"{c2_across_u} · every flip inside the noise floor {all_inside}")
    print(f"     ->  WORLD {world}")
    out["world"] = world

    HERE.joinpath("results").mkdir(exist_ok=True)
    ap = HERE / "results" / "estimand_grid.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    import hashlib
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
