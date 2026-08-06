#!/usr/bin/env python3
"""R792 · the arc's estimand was a DEFAULT NOBODY CHOSE — the 2x2 the prior round never separated.

CHECK #394 found three things. (a) R791's "construct-validity wall (R631)" is a FALSE CITATION —
R631 is `the_unrecorded_retraction`; the register lives at `corebench/score.py:34`. Four rounds cite
it wrongly. (b) `corebench/results/subgroup_coval_core_vs_topw_k4.json`, on disk since 2026-08-03 and
opened by no round in this arc, reads `verdict: SEPARABLE`. (c) Its round's own NEXT — "every
A-family comparison today was prompt-weighted by default, and nobody chose that" — was never acted
on, and it changed TWO things at once: the WEIGHTING and the RESAMPLING UNIT. A 2x2 separates them.

ESTIMAND        E1 ⭐ the 2x2 on `coval_core - topw_k4` · E2 ⭐ the same over 190 pairs with BH ·
                E3 ⭐ the clause-② admitted set per cell · E4 the audit, exact
IDENTIFICATION  E1-E4 exact. ⚠ "which estimand is CORRECT" is NOT identified by any data here — it
                is a choice about whose average matters. This round reports the sensitivity.
DERIVED FIRST   D1 weighting fixes the ESTIMAND, resampling fixes its SE — changing both confounds
                target with precision · D2 the 36 subgroups are six OVERLAPPING partitions of one
                judgement set · D3 alias arms must return exactly 0 in every cell · D4 if the two
                weightings correlate above ~0.99 the subgroup one is a reparameterisation
WORLDS          A the weighting does it · B the resampling unit does it · C only the corner — C is
                checked FIRST, being the reading that most constrains a single-cell claim
CONTROLS        OBJECT (REPRODUCE the committed artifact: 36 / 0.004107 / 0.8333) · PLACEBO ·
                POSITIVE (band + a SUBGROUP-SPECIFIC plant) · NEGATIVE (demographics permuted across
                annotators; the pooled estimate must be EXACTLY unchanged) · SHAM (random groups of
                the same sizes) · NOISE FLOOR (spread over 20 random assignments)
"""
import collections
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
from score import load_sat, cls, DEMO_AXES                             # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PRIOR = RES / "subgroup_coval_core_vs_topw_k4.json"
R789 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json")
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
MINN = 100                                                    # the prior script's own threshold
ZEFF = 2.801585
NBOOT = 1200
SEEDS = [31337, 31338, 31339]
CELLS = [("pooled", "prompt"), ("pooled", "annotator"),
         ("subgroup", "prompt"), ("subgroup", "annotator")]

INSTRUMENT_UNIT = "a (prompt, annotator) judgement"
CLAIM_UNIT = "an (arm, arm) PAIR"
CLAIM_UNIT_E3 = "an ADMITTED SET"


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


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


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
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT,
           "claim_unit_e3": CLAIM_UNIT_E3,
           "units_distinct": len({INSTRUMENT_UNIT, CLAIM_UNIT, CLAIM_UNIT_E3}) == 3}

    # ================= OBJECT: load the judgement table ===========================================
    print("  OBJECT CHECK")
    if not PRIOR.is_file() or not R789.is_file():
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0.")
        return 2
    prior = json.loads(PRIOR.read_text())
    prev = json.loads(R789.read_text())
    demo = {}
    for line in open(ROOT / "data" / "annotators.jsonl", encoding="utf-8"):
        r = json.loads(line)
        demo[r["annotator_id"]] = r.get("demographics") or {}
    recs = []                                                  # (pid, aid, class-tuple)
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        for asm in rec.get("metadata", {}).get("assessments", []):
            aid = asm.get("annotator_id")
            for e in (asm.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y:
                    recs.append((pid, aid, cls(np.array(y, float))))
    pids = sorted({r[0] for r in recs})
    aids = sorted({r[1] for r in recs})
    pidx = {p: i for i, p in enumerate(pids)}
    aidx = {a: i for i, a in enumerate(aids)}
    PJ = np.array([pidx[r[0]] for r in recs])
    AJ = np.array([aidx[r[1]] for r in recs])
    HJ = np.array([r[2] for r in recs], float)                 # (J, 6)
    J = len(recs)
    print(f"     judgements {J}   prompts {len(pids)}   annotators {len(aids)}")

    # subgroups: axis=value with >= MINN judgements, exactly the prior script's rule
    cnt = collections.Counter()
    for _, a, _ in recs:
        d = demo.get(a, {})
        for ax in DEMO_AXES:
            v = d.get(ax)
            if v is not None:
                cnt[f"{ax}={v}"] += 1
    groups = sorted(k for k, c in cnt.items() if c >= MINN)
    GM = np.zeros((len(groups), J), bool)
    gi = {g: i for i, g in enumerate(groups)}
    for j, (_, a, _) in enumerate(recs):
        d = demo.get(a, {})
        for ax in DEMO_AXES:
            v = d.get(ax)
            if v is not None and f"{ax}={v}" in gi:
                GM[gi[f"{ax}={v}"], j] = True
    print(f"     subgroups at n >= {MINN}: {len(groups)}   (the prior artifact says "
          f"{prior['n_subgroups']})")

    # ---- per-judgement agreement for every arm ---------------------------------------------------
    # ⭐ THE JUDGEMENT TABLE COVERS 1,078 PROMPTS AND THE ARC RUNS ON 968 (R784). The prior
    # subgroup script used every prompt each arm happened to have; this arc used the common 968.
    # That is a THIRD default the two differ on, beside weighting and resampling unit, so both
    # populations are carried: AVAIL[t] per arm for the REPRODUCTION, and the common mask for the
    # grid. A single population here would silently pick one of the two rounds' conventions.
    V, AVAIL = {}, {}
    for t in prev["e2"]["a2"]:
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        SGN = np.zeros((len(pids), 6))
        have = np.zeros(len(pids), bool)
        for k, p in enumerate(pids):
            if p not in S:
                continue
            ii = sorted({i for i, _ in S[p]})
            y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            SGN[k] = np.sign(y[[i for i, _ in PR]] - y[[j for _, j in PR]])
            have[k] = True
        V[t] = (SGN[PJ] == HJ).mean(axis=1)
        AVAIL[t] = have[PJ]
    names = sorted(V)
    common = np.ones(J, bool)
    for t in names:
        common &= AVAIL[t]
    ncp = len(set(PJ[common].tolist()))
    print(f"     arms with per-judgement vectors: {len(names)}")
    print(f"     ⭐ POPULATION: the judgement table spans {len(pids)} prompts; the arms share "
          f"{ncp}; the arc's rounds use 968. Both are carried.")

    # ---- REPRODUCE THE COMMITTED ARTIFACT -------------------------------------------------------
    def sg_means(v, av=None):
        m = np.ones(J, bool) if av is None else av
        return np.array([v[GM[g] & m].mean() for g in range(len(groups))])

    da = sg_means(V["coval_core"], AVAIL["coval_core"]) - sg_means(V["topw_k4"], AVAIL["topw_k4"])
    rep_mean, rep_win = float(da.mean()), float((da > 0).mean())
    ok_obj = (len(groups) == prior["n_subgroups"]
              and abs(rep_mean - prior["mean"]) < 1e-6
              and abs(rep_win - prior["win_rate"]) < 1e-6)
    print(f"     REPRODUCTION of the committed artifact: subgroups {len(groups)} vs "
          f"{prior['n_subgroups']}   mean {rep_mean:.6f} vs {prior['mean']:.6f}   win_rate "
          f"{rep_win:.6f} vs {prior['win_rate']:.6f}   {'PASS' if ok_obj else 'FAIL'}")
    if not ok_obj or len(names) < 20:
        print("  UNRUNNABLE: the artifact this round reconciles could not be reproduced, or the "
              "population is short. Exit 2, never 0.")
        return 2

    # aliases -> distinct objects
    par = {t: t for t in names}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    alias_pairs = [(x, y) for x, y in itertools.combinations(names, 2)
                   if np.array_equal(V[x][common], V[y][common])]
    for x, y in alias_pairs:
        par[find(x)] = find(y)
    reps = sorted({find(t) for t in names},
                  key=lambda t: np.bincount(PJ, V[t], len(pids)).sum())
    rep_of = {t: reps.index(find(t)) for t in names}
    n = len(reps)
    VM = np.array([V[t] for t in reps])                        # (n, J)
    print(f"     alias pairs {len(alias_pairs)}   distinct objects {n}   "
          f"pairs {n * (n - 1) // 2}")
    out["object"] = {"judgements": J, "common_prompts": ncp, "prompts": len(pids), "annotators": len(aids),
                     "subgroups": len(groups), "arms": len(names), "objects": n,
                     "reproduced": ok_obj, "rep_mean": rep_mean, "rep_win": rep_win}

    # ================= THE FOUR ESTIMATORS ========================================================
    NPc = np.bincount(PJ, minlength=len(pids)).astype(float)
    GMf = GM.astype(float)

    def estimate(Vm, w, gm=None):
        """Vm (n, J), w (J,) judgement weights, gm (G, J) group membership as float.
        -> (pooled, subgroup), each (n,). POOLED weights each PROMPT equally (the arc's A2);
        SUBGROUP weights each of the G groups equally."""
        gm = GMf if gm is None else gm
        sp = np.array([np.bincount(PJ, Vm[i] * w, len(pids)) for i in range(Vm.shape[0])])
        npr = np.bincount(PJ, w, len(pids))
        alive = npr > 0
        pooled = (sp[:, alive] / npr[alive]).mean(axis=1)
        sg_n = gm @ w
        sg_s = (gm @ (Vm * w).T).T
        live = sg_n > 0
        sub = (sg_s[:, live] / sg_n[live]).mean(axis=1)
        return pooled, sub

    w1 = common.astype(float)      # the grid runs on the COMMON population
    base_pool, base_sub = estimate(VM, w1)

    def boot(rng, unit, nb=NBOOT):
        """-> (pooled (n, nb), subgroup (n, nb)) with SHARED draws across arms."""
        P_, A_ = len(pids), len(aids)
        op = np.empty((n, nb))
        os_ = np.empty((n, nb))
        for b in range(nb):
            if unit == "prompt":
                c = rng.multinomial(P_, np.full(P_, 1.0 / P_))
                w = c[PJ].astype(float) * common
            else:
                c = rng.multinomial(A_, np.full(A_, 1.0 / A_))
                w = c[AJ].astype(float) * common
            p_, s_ = estimate(VM, w)
            op[:, b] = p_
            os_[:, b] = s_
        return op, os_

    print("\n  E1 - THE 2x2 ON THE DECISIVE PAIR")
    B = {}
    for unit in ("prompt", "annotator"):
        B[unit] = boot(np.random.default_rng(SEEDS[0]), unit)
    ci, iA, iB = {}, rep_of["coval_core"], rep_of["topw_k4"]
    for wt, unit in CELLS:
        base = (base_pool if wt == "pooled" else base_sub)
        draws = B[unit][0 if wt == "pooled" else 1]
        eff = float(base[iA] - base[iB])
        dd = draws[iA] - draws[iB]
        lo, hi = float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))
        p = 2.0 * min(float((dd <= 0).mean()), float((dd >= 0).mean()))
        p = max(min(p, 1.0), 1.0 / (NBOOT + 1))
        sep = lo > 0 or hi < 0
        ci[f"{wt}_{unit}"] = {"eff": eff, "lo": lo, "hi": hi, "p": p, "separable": sep}
        print(f"     {wt:<9} weighted / {unit:<9} resampled   eff {eff:+.6f}  "
              f"CI [{lo:+.6f}, {hi:+.6f}]  p {p:.4f}   {'SEPARABLE' if sep else 'not separable'}")
    out["e1"] = ci
    nsep = sum(1 for v in ci.values() if v["separable"])
    wt_both = ci["subgroup_prompt"]["separable"] and ci["subgroup_annotator"]["separable"] \
        and not ci["pooled_prompt"]["separable"] and not ci["pooled_annotator"]["separable"]
    un_both = ci["pooled_annotator"]["separable"] and ci["subgroup_annotator"]["separable"] \
        and not ci["pooled_prompt"]["separable"] and not ci["subgroup_prompt"]["separable"]
    print(f"     cells separating: {nsep} of 4")

    # ================= E2 · the whole grid ========================================================
    print("\n  E2 - THE SAME FOUR CELLS OVER ALL 190 PAIRS, BH OVER THE WHOLE GRID")
    PAIRS = list(itertools.combinations(range(n), 2))
    grid = {}
    for wt, unit in CELLS:
        base = (base_pool if wt == "pooled" else base_sub)
        draws = B[unit][0 if wt == "pooled" else 1]
        eff = np.array([base[i] - base[j] for i, j in PAIRS])
        dd = np.array([draws[i] - draws[j] for i, j in PAIRS])
        pv = 2.0 * np.minimum((dd <= 0).mean(axis=1), (dd >= 0).mean(axis=1))
        pv = np.maximum(np.minimum(pv, 1.0), 1.0 / (NBOOT + 1))
        keep = bh(pv)
        lo = np.percentile(dd, 2.5, axis=1)
        hi = np.percentile(dd, 97.5, axis=1)
        res = keep & ((lo > 0) | (hi < 0))
        grid[f"{wt}_{unit}"] = {"resolved": int(res.sum()), "tested": len(PAIRS),
                                "eff": eff.tolist(), "resolved_mask": res.tolist()}
        print(f"     {wt:<9} / {unit:<9}   resolved {int(res.sum()):>3} of {len(PAIRS)}   "
              f"not {len(PAIRS) - int(res.sum())}")
    flips = sum(1 for k in range(len(PAIRS))
                if grid["pooled_prompt"]["resolved_mask"][k]
                != grid["subgroup_annotator"]["resolved_mask"][k])
    corr = float(np.corrcoef(grid["pooled_prompt"]["eff"], grid["subgroup_annotator"]["eff"])[0, 1])
    print(f"     verdicts FLIPPING between the arc's default and the prior round's cell: {flips} "
          f"of {len(PAIRS)}")
    print(f"     D4: corr(pooled eff, subgroup eff) over the 190 pairs = {corr:.4f}   "
          f"{'>= 0.99 -> a reparameterisation' if corr >= 0.99 else '< 0.99 -> a different ordering'}")
    out["e2"] = {k: {kk: vv for kk, vv in v.items() if kk != "eff"} for k, v in grid.items()}
    out["e2"]["flips_default_vs_prior"] = flips
    out["e2"]["weighting_corr"] = corr

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plw = max(float(np.abs(V[x][common] - V[y][common]).max()) for x, y in alias_pairs)
    plok = plw == 0.0
    print(f"     PLACEBO   {len(alias_pairs)} alias pairs: worst per-judgement difference "
          f"{plw:.1e}   expected EXACTLY 0 by D3   {'PASS' if plok else 'FAIL'}")

    prng = np.random.default_rng(SEEDS[0] + 7)
    dose, fl, ce = {}, None, None
    for delta in (0.0, 0.002, 0.005, 0.01, 0.02):
        Vp = np.vstack([VM[iB], VM[iB] + delta])
        bp, bs = estimate(Vp, w1)
        seps = []
        for unit in ("prompt", "annotator"):
            r2 = np.random.default_rng(SEEDS[0] + 9)
            op = np.empty((2, 300))
            os_ = np.empty((2, 300))
            for b in range(300):
                if unit == "prompt":
                    c = r2.multinomial(len(pids), np.full(len(pids), 1.0 / len(pids)))
                    w = c[PJ].astype(float) * common
                else:
                    c = r2.multinomial(len(aids), np.full(len(aids), 1.0 / len(aids)))
                    w = c[AJ].astype(float) * common
                a_, b_ = estimate(Vp, w)
                op[:, b], os_[:, b] = a_, b_
            for dr in (op, os_):
                d_ = dr[1] - dr[0]
                seps.append(bool(np.percentile(d_, 2.5) > 0 or np.percentile(d_, 97.5) < 0))
        dose[str(delta)] = seps
        print(f"     POSITIVE  delta {delta:<6} cells separating {sum(seps)} of 4")
        if delta == 0.0:
            fl = sum(seps)
        if delta == 0.02:
            ce = sum(seps)
    posok = fl == 0 and ce == 4 and fl != ce
    print(f"     POSITIVE  band COMPUTED: floor {fl} of 4 at delta 0, ceiling {ce} of 4 at 0.02   "
          f"{'admissible' if fl != ce else 'DEGENERATE'}   {'PASS' if posok else 'FAIL'}")

    # ⛔ SUBGROUP-SPECIFIC plant. THE FIRST VERSION PLANTED ON THE LARGEST SUBGROUP (`gender=Male`)
    # AND FAILED AT ds 0.024743 < dp 0.026102 -- and MY OWN D2 says why, before any data: the 36
    # subgroups are SIX OVERLAPPING PARTITIONS of one judgement set, so a plant on a large group of
    # one axis contaminates every other axis's groups in proportion, and the two estimators must
    # agree by construction. A criterion that presumes disjoint groups is malformed here. §4's *the
    # control fails for its own reasons*. Repaired to a DOSE OVER GROUP SIZE, whose expectation is
    # derivable without the result: pooled weights a group by its SIZE and subgroup-weighting does
    # not, so the ratio (subgroup move)/(pooled move) must FALL as the planted group grows.
    order_g = np.argsort(GM.sum(axis=1))
    probe = [int(order_g[0]), int(order_g[len(order_g) // 2]), int(order_g[-1])]
    ratios, specrows = [], []
    for g0 in probe:
        Vs = np.vstack([VM[iB], VM[iB] + 0.05 * GM[g0]])
        sp_pool, sp_sub = estimate(Vs, w1)
        dp, ds = float(sp_pool[1] - sp_pool[0]), float(sp_sub[1] - sp_sub[0])
        r_ = ds / dp if dp != 0 else float("inf")
        ratios.append(r_)
        specrows.append({"group": groups[g0], "n": int(GM[g0].sum()), "pooled": dp,
                         "subgroup": ds, "ratio": r_})
        print(f"     POSITIVE  SUBGROUP-SPECIFIC plant on `{groups[g0]}` (n={int(GM[g0].sum())}): "
              f"pooled {dp:+.6f}  subgroup-weighted {ds:+.6f}  ratio {r_:.3f}")
    specok = ratios[0] > ratios[1] > ratios[2] and ratios[0] > 1.0
    print(f"     POSITIVE  ratio must FALL with group size (D2): {ratios[0]:.3f} > "
          f"{ratios[1]:.3f} > {ratios[2]:.3f}   {'PASS -- the two estimands are distinguishable' if specok else 'FAIL'}")
    dp, ds = specrows[0]["pooled"], specrows[0]["subgroup"]

    # NEGATIVE -- permute demographics across annotators
    nrng = np.random.default_rng(SEEDS[0] + 13)
    perm = nrng.permutation(len(aids))
    GMp = np.zeros_like(GM)
    a_of_j = AJ
    for g in range(len(groups)):
        member = np.zeros(len(aids), bool)
        member[np.unique(a_of_j[GM[g]])] = True
        GMp[g] = member[perm][a_of_j]
    npool, nsub = estimate(VM, w1, gm=GMp.astype(float))
    pool_inv = float(np.abs(npool - base_pool).max())
    sub_moved = float(np.abs((nsub[iA] - nsub[iB]) - (base_sub[iA] - base_sub[iB])))
    negok = pool_inv < 1e-12
    print(f"     NEGATIVE  demographics permuted across annotators: pooled estimate unchanged to "
          f"{pool_inv:.1e} (a DERIVATION, checked); the subgroup-weighted decisive difference moves "
          f"by {sub_moved:.6f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the subgroup difference is an artefact of "
          f"reweighting per se rather than of WHO is in which group'")

    # SHAM -- random groups of the same sizes; NOISE FLOOR -- its spread over 20 assignments
    srng = np.random.default_rng(SEEDS[0] + 17)
    sizes = GM.sum(axis=1)
    sham = []
    for _ in range(20):
        GMs = np.zeros_like(GM)
        for g in range(len(groups)):
            GMs[g, srng.choice(J, sizes[g], replace=False)] = True
        _, ss = estimate(VM, w1, gm=GMs.astype(float))
        sham.append(float(ss[iA] - ss[iB]))
    sham = np.array(sham)
    print(f"     SHAM      random groups of the same 36 sizes: decisive difference "
          f"{sham.mean():+.6f} [{sham.min():+.6f}, {sham.max():+.6f}]   real subgroup-weighted "
          f"{base_sub[iA] - base_sub[iB]:+.6f}")
    print(f"     NOISE FLOOR  sd of the sham over 20 random assignments: {sham.std(ddof=1):.6f}")

    gate = plok and posok and negok and specok
    out["controls"] = {"placebo_worst": plw, "placebo_ok": plok, "dose": dose, "floor": fl,
                       "ceiling": ce, "positive_ok": posok, "subgroup_specific": specok,
                       "plant_pooled": dp, "plant_subgroup": ds, "plant_rows": specrows,
                       "plant_ratios": ratios,
                       "negative_pool_invariance": pool_inv, "negative_sub_moved": sub_moved,
                       "negative_ok": negok, "sham_mean": float(sham.mean()),
                       "sham_sd": float(sham.std(ddof=1)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · the admitted set per cell =============================================
    print("\n  E3 - THE CLAUSE ② ADMITTED SET, PER CELL")
    gidx = rep_of["generic"]
    adm = {}
    for wt, unit in CELLS:
        key = f"{wt}_{unit}"
        base = (base_pool if wt == "pooled" else base_sub)
        mask = grid[key]["resolved_mask"]
        pk = {}
        for k, (i, j) in enumerate(PAIRS):
            pk[(i, j)] = pk[(j, i)] = k
        s = sorted(t for t in names
                   if rep_of[t] != gidx and base[rep_of[t]] > base[gidx]
                   and mask[pk[(rep_of[t], gidx)]])
        adm[key] = s
        print(f"     {key:<20} admits {len(s):>2} named arms")
    allsame = len({tuple(v) for v in adm.values()}) == 1
    print(f"     the four admitted sets are {'IDENTICAL' if allsame else 'NOT identical'}")
    if not allsame:
        base_set = set(adm["pooled_prompt"])
        for k, v in adm.items():
            d_ = sorted(set(v) ^ base_set)
            if d_:
                print(f"       {k:<20} differs from the arc's default by {d_}")
    out["e3"] = {"admits": adm, "identical": allsame}

    # ================= E4 · the audit =============================================================
    print("\n  E4 - THE AUDIT (exact, with a positive control on the pattern)")
    arc = sorted((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs").glob(
        "R7*/README.md"))
    mis = [p.parent.name for p in arc if "wall (R631)" in p.read_text()]
    pos = [p.parent.name for p in arc if "R631" in p.read_text()]
    print(f"     rounds citing R631 as the construct wall: {len(mis)}  {mis}")
    print(f"     POSITIVE CONTROL -- rounds mentioning R631 at all: {len(pos)} "
          f"(the pattern can see; {len(mis)} of them use it as the wall)")
    print(f"     R631's actual subject: `R631_the_unrecorded_retraction`; the register lives at "
          f"`corebench/score.py:34`")
    out["e4"] = {"miscite": mis, "mentions": pos,
                 "register": "corebench/score.py:34 X1_construct_validity"}

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif nsep == 1:
        world = "C"
    elif wt_both:
        world = "A"
    elif un_both:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   cells separating {nsep} of 4   ->  WORLD {world}")
    out["world"] = world
    out["cells_separating"] = nsep

    art = HERE / "results/estimand.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
