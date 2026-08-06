#!/usr/bin/env python3
"""R765 · `generic` IS `POOL[0:4]` — what survives of R764, and what an identical-criteria pair measures.

⛔ CHECK #367, ONE OBJECT READ, ZERO COMPUTE:
   `core_generic.json[p] == core_genericpool16.json[p][:4]` for **968 of 968** prompts — identical
   strings, exact PREFIX. **`generic` IS the published comparator, entered in the census as a
   candidate core.** `gen` is not: mean pool overlap 0.0010, prefix 0 of 968.

TWO CONSEQUENCES POINTING OPPOSITE WAYS:
 ① R764's WORLD B is mostly DEGENERATE — the comparator beating weaker draws from its own class.
 ② An identical-criteria pair is a SCORING REPLICATE, which is what R415 wanted and R416 showed it
   did not have (its `_08b`/`_08bR` pairs changed 91–99% of their criteria, so they measure the
   RULE's variance, not the JUDGE's).

⛔ FORCED, LABELLED, NOT MEASURED:
  D1 `POOL[0:4]` sits at percentile 93.7 (R527, committed), so a subset at percentile q beats every
     subset below q ON THE POINT ESTIMATE. "generic clears ② at p000..p050" is ALGEBRA. The only
     non-forced part is whether it clears RESOLVEDLY, and that is what gets reported.
  D2 excluding an arm can only shrink an extension — monotone by subset. WHICH cells survive measures.
  D3 identical criteria should give identical A2; R761 reports 0.5514 vs 0.5504. The difference is
     therefore the SCORING pipeline's own variance, not a property of the criteria.

CONTROLS  PROVENANCE (reproduce R764's grid exactly, exit 2) · POSITIVE (the test both sees `generic`
          at 968/968 and does NOT see `gen`; band from both degenerate ends) · g=0 (a shuffled pool
          breaks the prefix test) · NEGATIVE (deranged prompt pairing, 200 draws) · SHAM (a RANDOM
          size-4 subset instead of the prefix) · PLACEBO (`coval_core` must not be comparator-
          identical) · CONFOUND (identical criteria but different response sets is NOT a replicate).
UNIT      instrument = a PROMPT (968/pair) · claim = an ARM. Both reported.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R764 = A24 / "R764_is_clause_three_any_still_empty_at_ninetytwo/results/clause_three_readings_at_92.json"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
PAIRS4 = list(itertools.combinations(range(4), 2))
POOL_CORE = "genericpool16"


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    prev = json.loads(R764.read_text())
    cores = {}
    for p in sorted(RES.glob("core_*.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and d:
            cores[p.name[5:-5]] = d
    pool = cores.get(POOL_CORE)
    if pool is None:
        print("UNRUNNABLE: no pool core JSON. Exit 2, never 0."); return 2

    # ---- E1 · the containment census, over every arm with a core JSON ------------------------
    def relate(A, B):
        pids = sorted(set(A) & set(B))
        if not pids: return None
        k = len(A[pids[0]])
        pre = sum(1 for p in pids if list(A[p]) == list(B[p])[:k])
        sub = sum(1 for p in pids if set(A[p]) <= set(B[p]))
        ov = float(np.mean([len(set(A[p]) & set(B[p])) / max(1, len(set(A[p]))) for p in pids]))
        return {"n": len(pids), "k": k, "prefix": pre, "subset": sub,
                "prefix_rate": pre / len(pids), "subset_rate": sub / len(pids), "overlap": ov}

    cen = {a: relate(cores[a], pool) for a in sorted(cores) if a != POOL_CORE}
    cen = {a: v for a, v in cen.items() if v}
    ident = sorted(a for a, v in cen.items() if v["prefix_rate"] == 1.0)
    print(f"  E1 CENSUS   {len(cen)} arms with a core JSON compared to `{POOL_CORE}`")
    print(f"  ⭐ COMPARATOR-IDENTICAL (exact prefix on every shared prompt): {ident}")
    print(f"  {'arm':<26}{'n':>6}{'k':>4}{'prefix':>9}{'subset':>9}{'overlap':>9}")
    for a in sorted(cen, key=lambda x: -cen[x]["prefix_rate"])[:12]:
        v = cen[a]
        print(f"  {a:<26}{v['n']:>6}{v['k']:>4}{v['prefix_rate']:>9.4f}"
              f"{v['subset_rate']:>9.4f}{v['overlap']:>9.4f}")
    print(f"  ... {max(0, len(cen)-12)} more, all in the artifact")

    # ---- CONTROLS on the containment instrument ---------------------------------------------
    rng = np.random.default_rng(765)
    pos_g = cen.get("generic", {}).get("prefix_rate", -1)
    pos_n = cen.get("gen", {}).get("overlap", 1.0)
    ok_pos = pos_g == 1.0 and pos_n < 0.05
    print(f"\n  POSITIVE    `generic` prefix {pos_g:.4f} (need 1.0) · `gen` overlap {pos_n:.4f} "
          f"(need < 0.05)  {'PASS' if ok_pos else '⛔ FAIL'}")
    print(f"              band: an always-contained test gives `gen` 1.0; a never-contained test "
          f"gives `generic` 0.0. Both needed, unreachable from either end.")
    pids = sorted(set(cores["generic"]) & set(pool))
    shuf = {p: list(rng.permutation(pool[p])) for p in pids}
    g0 = relate(cores["generic"], shuf)["prefix_rate"]
    print(f"  g=0         `generic` vs a per-prompt SHUFFLED pool: prefix {g0:.4f}  "
          f"{'PASS' if g0 < 0.05 else '⛔ FAIL'}  (the test reads ORDER, not just membership)")
    negd = []
    for _ in range(200):
        perm = list(rng.permutation(pids))
        der = {p: pool[q] for p, q in zip(pids, perm)}
        negd.append(relate(cores["generic"], der)["prefix_rate"])
    # ⚠ AND THE NEGATIVE IS UNINFORMATIVE BY CONSTRUCTION HERE, WHICH IS ITSELF THE READING.
    # Deranging the prompt pairing leaves the prefix rate at 1.0 because BOTH sets are PROMPT-BLIND:
    # `generic` and `genericpool16` carry the SAME criteria for every one of the 968 prompts. That is
    # what "a strong generalising prompt-blind criterion set" means, so the control cannot separate
    # anything and is reported as uninformative-with-reason rather than as a pass.
    n_distinct = len({tuple(cores["generic"][p]) for p in pids})
    print(f"  NEGATIVE    deranged prompt pairing x200: prefix {np.mean(negd):.4f} "
          f"[{np.percentile(negd,2.5):.4f}, {np.percentile(negd,97.5):.4f}]  vs real 1.0000")
    print(f"              ⚠ UNINFORMATIVE BY CONSTRUCTION: `generic` has {n_distinct} distinct "
          f"criterion set(s) across {len(pids)} prompts -- it is prompt-blind, so a derangement "
          f"changes nothing. The SHAM below is what carries the identification.")
    shamd = []
    for _ in range(200):
        rs = {p: list(rng.choice(pool[p], size=4, replace=False)) for p in pids}
        r = relate(rs, pool)
        shamd.append((r["prefix_rate"], r["subset_rate"]))
    sp = [a for a, _ in shamd]; ss = [b for _, b in shamd]
    print(f"  SHAM        RANDOM size-4 subsets of the pool x200: prefix {np.mean(sp):.4f}, "
          f"subset {np.mean(ss):.4f}   -> the PREFIX structure is the ingredient, not membership")
    # ⛔ THE FIRST PLACEBO WAS A DEFAULTING `.get` AND COULD ONLY FAIL. I wrote
    # `cen.get("coval_core", {}).get("prefix_rate", 1.0)` -- and there IS NO `core_coval_core.json`
    # (R441 recorded exactly this: "arms with no core file -> UNKNOWN, never 0, never dropped", and
    # `coval_core` is on its list). So ABSENCE returned the default 1.0 and read as "the released
    # core IS the comparator", the most alarming possible reading of a missing file.
    # An absent key must be visible, never defaulted onto the scale being tested.
    plc_arm = "coval_core" if "coval_core" in cen else "full"
    plc = cen[plc_arm]["prefix_rate"]
    print(f"  PLACEBO     `{plc_arm}` prefix {plc:.4f}  {'PASS' if plc < 0.05 else '⛔ FAIL'}"
          f"   (⚠ `coval_core` has NO committed core JSON -- R441; it cannot be the placebo)")

    # ---- the population and R294's estimator --------------------------------------------------
    targets, _ = load_targets()
    POOLSAT = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    P_ids = sorted({p for p in base if p in targets and p in POOLSAT and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOLSAT[P_ids[0]]})
    n_pool, P = len(idxs), len(P_ids)
    subs = list(itertools.combinations(range(n_pool), 4))
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in P_ids]
    Hm = max(len(h) for h in HC)
    HP = np.zeros((P, Hm, 6)); HK = np.zeros((P, Hm))
    for a, h in enumerate(HC):
        HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
    nH = HK.sum(1)
    T = np.zeros((P, n_pool, 4))
    for a, p in enumerate(P_ids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOLSAT[p].get((i, x), 0.0)

    def a2_of_y(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS4]] - Y[:, [j for _, j in PAIRS4]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    def arm_vec(t):
        S = load_sat(RES / f"sat_{t}.npz")
        Y = np.zeros((P, 4))
        for ai, p in enumerate(P_ids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return a2_of_y(Y)

    arms = sorted(prev["class_of"])
    A = {t: arm_vec(t) for t in arms}
    K = prev["class_of"]
    READINGS = {"3-rank": {"weight", "sat", "weight+sat", "neither"},
                "3-any": {"sat", "neither"}, "3-judge": {"neither"}}
    Y = np.empty((len(subs), P))
    for si, s in enumerate(subs):
        Y[si] = a2_of_y(T[:, list(s), :].sum(axis=1))
    order = np.argsort(Y.mean(1)); pub = subs.index(tuple(range(4)))
    ib = np.random.default_rng(31337).integers(0, P, (NBOOT, P))

    def clears(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return verdict(float(d.mean()), float(np.percentile(bs, 2.5)),
                       float(np.percentile(bs, 97.5)),
                       ZEFF * d.std(ddof=1) / math.sqrt(P)) == POS

    specs = [(f"p{q:03d}", int(order[min(int(q / 100 * (len(subs) - 1)), len(subs) - 1)]))
             for q in (0, 5, 25, 50, 75, 95, 100)]
    specs.insert(-1, ("published", pub))

    # ---- CONTROL · PROVENANCE, then E2 --------------------------------------------------------
    grid_all, grid_excl, prov_ok = {}, {}, True
    for lbl, si in specs:
        p2 = [t for t in arms if clears(A[t], Y[si])]
        for tag, pop in (("all", p2), ("excl", [t for t in p2 if t not in ident])):
            row = {rd: sorted(t for t in pop if K.get(t) in adm) for rd, adm in READINGS.items()}
            (grid_all if tag == "all" else grid_excl)[lbl] = row
        for rd in READINGS:
            if len(grid_all[lbl][rd]) != prev["grid"][lbl][rd]["n_tags"]:
                prov_ok = False
    print(f"\n  PROVENANCE  R764's grid reproduced on all {len(specs)}x{len(READINGS)} cells: "
          f"{'PASS' if prov_ok else '⛔ FAIL'}")
    if not prov_ok:
        print("  -> this round is not R764 and may not contradict it. UNVERIFIED."); return 2

    print(f"\n  ⭐ E2 · ③-any WITH THE COMPARATOR-IDENTICAL ARM EXCLUDED")
    print(f"  {'baseline':<12}{'③-any (all)':>26}{'③-any (excl)':>26}")
    for lbl, _ in specs:
        a_, e_ = grid_all[lbl]["3-any"], grid_excl[lbl]["3-any"]
        print(f"  {lbl:<12}{str(a_) if a_ else '—':>26}{str(e_) if e_ else '—':>26}")
    surv = [l for l, _ in specs if grid_excl[l]["3-any"]]
    print(f"  ③-any non-empty after exclusion: {len(surv)} of {len(specs)} cells "
          f"{surv if surv else ''}")
    for l in surv:
        for t in grid_excl[l]["3-any"]:
            print(f"     {l}: {t}  pool-overlap {cen.get(t, {}).get('overlap', float('nan')):.4f}")

    # ---- E3 · the SCORING-ONLY floor, from identical-criteria pairs ---------------------------
    print(f"\n  ⭐ E3 · IDENTICAL-CRITERIA PAIRS = SCORING REPLICATES")
    have = [a for a in cores if (RES / f"sat_{a}.npz").exists()]
    key = {}
    for a in have:
        pj = sorted(set(cores[a]) & set(P_ids))
        if len(pj) != P: continue
        key.setdefault(tuple(tuple(cores[a][p]) for p in P_ids), []).append(a)
    reps = [v for v in key.values() if len(v) > 1]
    print(f"  identical-criteria groups over the full prompt set: {len(reps)}  {reps}")
    # the pool's own first-four column is the second member of `generic`'s replicate pair
    pool4 = a2_of_y(T[:, list(range(4)), :].sum(axis=1))
    floors = []
    if "generic" in A:
        d = A["generic"] - pool4
        bs = d[ib].mean(axis=1)
        floors.append({"pair": "generic vs genericpool16[:4]", "n": P,
                       "mean_abs_A2_gap": float(abs(d.mean())),
                       "A2_a": float(A["generic"].mean()), "A2_b": float(pool4.mean()),
                       "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                       "per_prompt_identical": int((d == 0).sum())})
    for grp in reps:
        for x, y in itertools.combinations(sorted(grp), 2):
            if x in A and y in A:
                d = A[x] - A[y]; bs = d[ib].mean(axis=1)
                floors.append({"pair": f"{x} vs {y}", "n": P,
                               "mean_abs_A2_gap": float(abs(d.mean())),
                               "A2_a": float(A[x].mean()), "A2_b": float(A[y].mean()),
                               "lo": float(np.percentile(bs, 2.5)),
                               "hi": float(np.percentile(bs, 97.5)),
                               "per_prompt_identical": int((d == 0).sum())})
    # ---- THE REGISTERED CONFOUND, now implemented: identical criteria but a DIFFERENT scored
    # response set is NOT a scoring replicate. Require the same prompts AND the same response keys.
    def keyset(t):
        S = load_sat(RES / f"sat_{t}.npz")
        return {p: frozenset(S[p].keys()) for p in P_ids if p in S}

    ks_cache = {}
    for f in floors:
        a_, _, b_ = f["pair"].partition(" vs ")
        if b_.startswith("genericpool16"):
            f["same_response_set"] = None; continue
        for t in (a_, b_):
            if t not in ks_cache: ks_cache[t] = keyset(t)
        ka, kb = ks_cache[a_], ks_cache[b_]
        shared = set(ka) & set(kb)
        f["same_response_set"] = bool(shared) and all(
            {x for _, x in ka[p]} == {x for _, x in kb[p]} for p in shared)

    bad_conf = [f["pair"] for f in floors if f.get("same_response_set") is False]
    print(f"  ⚠ CONFOUND  pairs whose scored RESPONSE SET differs (not replicates): "
          f"{len(bad_conf)}  {bad_conf if bad_conf else ''}")

    exact = [f for f in floors if f["per_prompt_identical"] == f["n"]]
    judge = [f for f in floors if f["pair"].count("08b") == 1 and f["mean_abs_A2_gap"] > 0]
    print(f"\n  ⭐⭐ THE FLOOR SPLITS IN TWO, AND ONLY ONE HALF IS 'NOISE'")
    print(f"  {'class':<38}{'pairs':>7}{'|Δ| mean':>11}{'min':>9}{'max':>9}")
    if exact:
        g = [f['mean_abs_A2_gap'] for f in exact]
        print(f"  {'SAME judge, identical criteria':<38}{len(exact):>7}{np.mean(g):>11.4f}"
              f"{min(g):>9.4f}{max(g):>9.4f}   <- the SCORING-ONLY floor")
    if judge:
        g = [f['mean_abs_A2_gap'] for f in judge]
        print(f"  {'DIFFERENT judge, identical criteria':<38}{len(judge):>7}{np.mean(g):>11.4f}"
              f"{min(g):>9.4f}{max(g):>9.4f}   <- the JUDGE effect")
    print(f"  {'R415, committed (a THIRD object)':<38}{'—':>7}{0.116489:>11.4f}"
          f"{'—':>9}{'—':>9}   <- re-SELECTION, not scoring")
    for f in floors:
        print(f"  {f['pair']:<40} A2 {f['A2_a']:.4f} vs {f['A2_b']:.4f}  |Δ| {f['mean_abs_A2_gap']:.4f}"
              f"  [{f['lo']:+.4f}, {f['hi']:+.4f}]  identical on {f['per_prompt_identical']}/{f['n']} prompts")
    e3 = ("REPORTED" if len(floors) >= 2 else "UNIDENTIFIED — fewer than 2 replicate pairs")
    print(f"  E3 verdict: {e3}   (R415's rule-level floor, a DIFFERENT object, is 0.116489)")

    ctrl = ok_pos and g0 < 0.05 and plc < 0.05 and prov_ok and float(np.mean(sp)) < 0.05
    if not ctrl:
        world = "UNVERIFIED"
    elif not surv:
        world = "A · R764's amendment is retracted; ③-any is empty once the comparator is excluded"
    elif any(cen.get(t, {}).get("overlap", 1.0) < 0.10
             for l in surv for t in grid_excl[l]["3-any"]):
        world = "B · survives in part, by a non-comparator arm"
    else:
        world = "NO WORLD — counts reported, none claimed"
    if len(ident) >= 2:
        world += "  ·  +C: the census contains its own baseline more than once"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/the_admitted_arm_was_the_baseline.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "containment": cen, "comparator_identical": ident,
        "controls": {"positive_generic_prefix": pos_g, "positive_gen_overlap": pos_n,
                     "g0_shuffled_prefix": g0, "placebo_covalcore_prefix": plc,
                     "negative_mean": float(np.mean(negd)),
                     "sham_prefix": float(np.mean(sp)), "sham_subset": float(np.mean(ss)),
                     "provenance_grid_reproduced": prov_ok},
        "grid_all": {l: {r: v for r, v in grid_all[l].items()} for l, _ in specs},
        "grid_excl": {l: {r: v for r, v in grid_excl[l].items()} for l, _ in specs},
        "surviving_cells": surv, "replicate_groups": reps, "scoring_floor": floors,
        "placebo_arm": plc_arm, "negative_uninformative_prompt_blind": True,
        "n_distinct_criterion_sets_generic": n_distinct,
        "confound_response_set_differs": bad_conf,
        "floor_same_judge_pairs": len(exact),
        "floor_same_judge_max": (max(f['mean_abs_A2_gap'] for f in exact) if exact else None),
        "judge_effect_pairs": len(judge),
        "judge_effect_mean": (float(np.mean([f['mean_abs_A2_gap'] for f in judge])) if judge else None),
        "e3": e3, "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
