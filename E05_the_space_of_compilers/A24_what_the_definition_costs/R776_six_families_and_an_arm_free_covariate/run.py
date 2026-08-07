#!/usr/bin/env python3
"""R776 · six disjoint families, and a prompt covariate computed without any arm.

CHECK #378, TWO CORRECTIONS BEFORE DESIGNING:
 (1) R775's NEXT claimed "2^6 - 2 = 62 labelings". That counts BIPARTITIONS; the axis test labels each
   family by its RULE, so with six families of which three share one the count is C(6,3) = 20 and
   the permutation p floors at 0.05, not 1/62. A real 5x improvement over R775's 1/4, smaller than
   claimed.
 (2) AND R775's READING MAY BE BACKWARDS. `random_k` arms draw criteria AT RANDOM, so two random
   families with different seeds hold DIFFERENT criteria -- yet their difference magnitudes co-move
   wherever the POOL is heterogeneous on a prompt, which is a PROMPT property. The same-rule block
   may be the strongest evidence FOR a prompt component, not against it.

Hence the instrument this thread has lacked: `poolspread(p)`, the spread of the 16 fixed pool
criteria on that prompt -- a property of (prompt, pool) with NO arm, NO selection, NO difference.

FORCED, LABELLED:
  D1 C(6,3) = 20 so p floors at 0.05; a result AT 0.05 is the permutation's resolution, not a
     cleared threshold.
  D2 the three `random_k` families differ only in SEED, so co-movement cannot come from shared
     criteria -- it must come from the prompt.
  D3 `poolspread` and the scales read the same satisfaction table, so a correlation shows the scale
     tracks the pool's per-prompt spread -- NOT arm-free evidence of a prompt property in general.

CONTROLS  DISJOINT (object level, exit 2) - POSITIVE (planted prompt-scale, swept) - g=0 - NEGATIVE
          (200 one-sided permutations) - SHAM (a random vector from `poolspread`'s own distribution) -
          PLACEBO (a family against itself) - CONFOUND (mean pool satisfaction, and the partial
          correlation holding it fixed, which is the saturation explanation).
UNIT      prompt - arm pair within a family - FAMILY PAIR (15) - FAMILY (6).
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
SAME_RULE = {"Ra_random_s0", "Rb_random_s1", "Rc_random_s2"}


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


def main():
    r730 = json.loads((A24 / "R730_seven_tags_are_not_seven_objects/results/"
                       "r730_object_partition.json").read_text())
    obj = {}
    for g in r730["multi_tag_classes"]:
        for t in g:
            obj[t] = sorted(g)[0]
    O = {n: {obj.get(t, t) for t in f} for n, f in FAM.items()}
    bad = [(a, b) for a, b in itertools.combinations(FAM, 2) if O[a] & O[b]]
    if bad:
        print(f"UNRUNNABLE: families share objects {bad}. Exit 2, never 0.")
        return 2
    assert not any(m in t for f in FAM.values() for t in f for m in ("_08b", "_ctl", "_det"))
    n_assign = math.comb(len(FAM), len(SAME_RULE))
    print(f"  DISJOINT    {len(FAM)} families x 5 arms, 0 shared OBJECTS, no foreign judge, "
          f"no replicas  PASS")
    print(f"  D1          rule-label assignments C({len(FAM)},{len(SAME_RULE)}) = {n_assign}  "
          f"-> permutation p floor {1 / n_assign:.4f}")

    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    idxs = sorted({i for i, _ in POOL[pids[0]]})

    T = np.zeros((P, len(idxs), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c_, x in enumerate(L):
                T[a, bi, c_] = POOL[p].get((i, x), 0.0)
    poolspread = T.std(axis=(1, 2))
    poolmean = T.mean(axis=(1, 2))
    print(f"  COVARIATE   `poolspread` from {len(idxs)} pool criteria x 4 responses -- no arm, no "
          f"selection, no difference.  mean {poolspread.mean():.4f} sd {poolspread.std():.4f}")

    def a2(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        o = np.zeros(P)
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            o[ai] = np.mean([(s == h).mean() for h in HC[ai]])
        return o

    A = {t: a2(t) for f in FAM.values() for t in f}
    M = {n: np.abs(np.array([A[a] - A[b] for a, b in itertools.combinations(FAM[n], 2)]))
         for n in FAM}
    C = {n: M[n].mean(0) for n in FAM}
    rng = np.random.default_rng(776)

    def rel(n):
        Mm, k = M[n], M[n].shape[0]
        rs = []
        for _ in range(NDRAW):
            i = rng.permutation(k)
            h1, h2 = Mm[i[:k // 2]].mean(0), Mm[i[k // 2:]].mean(0)
            if h1.std() > 0 and h2.std() > 0:
                r = float(np.corrcoef(h1, h2)[0, 1])
                rs.append(2 * r / (1 + r) if r > -1 else 0.0)
        return float(np.mean(rs))

    R = {n: rel(n) for n in FAM}
    print("\n  reliabilities " + "  ".join(f"{n[:2]} {R[n]:.3f}" for n in FAM))

    print(f"\n  E1 - {math.comb(len(FAM), 2)} CROSS-FAMILY CORRELATIONS, each against its OWN ceiling")
    print(f"  {'pair':<34}{'raw':>9}{'ceil':>8}{'relative':>10}   block")
    rows = {}
    for a, b in itertools.combinations(FAM, 2):
        raw = float(np.corrcoef(C[a], C[b])[0, 1])
        ceil = math.sqrt(max(R[a], 0) * max(R[b], 0))
        blk = "SAME-RULE" if (a in SAME_RULE and b in SAME_RULE) else "diff-rule"
        rows[f"{a} x {b}"] = {"raw": raw, "ceiling": ceil,
                              "rel": raw / max(ceil, 1e-12), "block": blk}
        print(f"  {a[:15] + ' x ' + b[:15]:<34}{raw:>9.4f}{ceil:>8.4f}"
              f"{raw / max(ceil, 1e-12):>10.4f}   {blk}")
    same = [v["rel"] for v in rows.values() if v["block"] == "SAME-RULE"]
    diff = [v["rel"] for v in rows.values() if v["block"] == "diff-rule"]
    obs = float(np.mean(same) - np.mean(diff))
    print(f"\n  E2 - SAME-RULE mean {np.mean(same):.4f} (n={len(same)})   "
          f"diff-rule mean {np.mean(diff):.4f} (n={len(diff)})   difference {obs:+.4f}")

    names = list(FAM)
    null = []
    for sel in itertools.combinations(names, len(SAME_RULE)):
        s = set(sel)
        a_ = [rows[k]["rel"] for k in rows
              if k.split(" x ")[0] in s and k.split(" x ")[1] in s]
        b_ = [rows[k]["rel"] for k in rows
              if not (k.split(" x ")[0] in s and k.split(" x ")[1] in s)]
        null.append(float(np.mean(a_) - np.mean(b_)))
    rank = sum(1 for x in null if x >= obs)
    print(f"  D1 NULL     all {len(null)} rule-label assignments: "
          f"[{min(null):+.4f}, {max(null):+.4f}]   observed rank {rank}/{len(null)}   "
          f"p = {rank / len(null):.4f}   (floor {1 / len(null):.4f})")

    print("\n  E3 - corr(scale, `poolspread`) per family, and the saturation partial")
    cov = {}
    rsm = float(np.corrcoef(poolspread, poolmean)[0, 1])
    for n in FAM:
        r1 = float(np.corrcoef(C[n], poolspread)[0, 1])
        rm = float(np.corrcoef(C[n], poolmean)[0, 1])
        den = math.sqrt(max((1 - rm ** 2) * (1 - rsm ** 2), 1e-12))
        part = (r1 - rm * rsm) / den
        cov[n] = {"raw": r1, "with_mean": rm, "partial": part}
        print(f"     {n:<16} corr {r1:+.4f}   with poolmean {rm:+.4f}   partial {part:+.4f}")
    print(f"     corr(poolspread, poolmean) = {rsm:+.4f}   (the saturation axis)")
    maj_hi = sum(1 for v in cov.values() if abs(v["raw"]) >= 0.30)
    maj_lo = sum(1 for v in cov.values() if abs(v["raw"]) < 0.15)
    coll = sum(1 for v in cov.values() if abs(v["partial"]) < abs(v["raw"]) / 3)
    print(f"     families with |corr| >= 0.30: {maj_hi}/{len(FAM)}   < 0.15: {maj_lo}/{len(FAM)}   "
          f"partial collapsing below a third: {coll}/{len(FAM)}")

    plc = float(np.corrcoef(C["Ra_random_s0"], C["Ra_random_s0"])[0, 1])
    negd = [float(np.corrcoef(C["Ra_random_s0"], C["F1_committed"][rng.permutation(P)])[0, 1])
            for _ in range(NDRAW)]
    nhi = float(np.percentile(negd, 97.5))
    shamd = [float(np.corrcoef(C["Ra_random_s0"], rng.choice(poolspread, P, replace=True))[0, 1])
             for _ in range(NDRAW)]
    print(f"\n  PLACEBO     a family against ITSELF {plc:.6f}  "
          f"{'PASS' if abs(plc - 1) < 1e-9 else 'FAIL'}")
    print(f"  NEGATIVE    {NDRAW} one-sided permutations {np.mean(negd):+.4f} "
          f"[{np.percentile(negd, 2.5):+.4f}, {nhi:+.4f}]")
    print(f"  SHAM        scale vs a RANDOM draw from `poolspread`'s own distribution: "
          f"{np.mean(shamd):+.4f} [{np.percentile(shamd, 2.5):+.4f}, "
          f"{np.percentile(shamd, 97.5):+.4f}]")

    v = {t: float(np.var(A[t])) for t in A}
    dose = {}
    for w in (0.0, 0.25, 0.5, 1.0):
        s = rng.lognormal(0, w, P) if w > 0 else np.ones(P)
        Asim = {t: rng.normal(0, math.sqrt(max(v[t], 1e-12)), P) * s for t in A}
        Cs = {n: np.abs(np.array([Asim[a] - Asim[b]
                                  for a, b in itertools.combinations(FAM[n], 2)])).mean(0)
              for n in FAM}
        cs = [float(np.corrcoef(Cs[a], Cs[b])[0, 1]) for a, b in itertools.combinations(FAM, 2)]
        # A CONSTANT VECTOR HAS NO CORRELATION. At width 0 the planted scale is `ones`, so
        # corr(scale, s) divides by a zero sd and is NaN -- UNDEFINED, not zero. My first g=0
        # criterion required it below 0.15 and NaN fails every comparison, so the control could not
        # pass. The covariate clause now applies only where a covariate EXISTS, and the width-0 cell
        # reports `undefined` rather than a number.
        cv = (float("nan") if w == 0.0
              else float(np.mean([abs(np.corrcoef(Cs[n], s)[0, 1]) for n in FAM])))
        dose[w] = {"min": float(min(cs)), "mean": float(np.mean(cs)), "cov": cv,
                   "all_detected": bool(min(cs) > nhi)}
        print(f"  POSITIVE    width {w:>4.2f} -> 15 correlations min {min(cs):+.4f} "
              f"mean {np.mean(cs):+.4f}  |corr with the planted covariate| "
              f"{'undefined (no plant)' if w == 0.0 else f'{cv:.4f}'}   "
              f"ALL detected {min(cs) > nhi}")
    pos = dose[1.0]["all_detected"] and dose[1.0]["cov"] > 0.3
    g0 = not dose[0.0]["all_detected"]        # the covariate clause is vacuous where no plant exists
    print(f"              registered band - 0.00 must NOT detect (its covariate is UNDEFINED, not "
          f"small); 1.00 must detect and show a covariate: {pos and g0}  "
          f"{'PASS' if pos and g0 else 'FAIL'}")

    # ⚠ A COMPOSITION FACT I SHOULD HAVE CHECKED BEFORE LABELLING THE BLOCKS.
    mixed = {n: sum(1 for t in FAM[n] if t.startswith("random_k")) for n in FAM}
    print(f"\n  ⚠ FAMILY COMPOSITION  `random_k` members per family: {mixed}")
    print(f"     `M_mixed_sel` holds 3 of 5 `random_k` arms, so every M x R pair I labelled "
          f"'diff-rule' is MAJORITY same-rule. The registered p below inherits that mislabelling.")
    pure = {n for n in FAM if mixed[n] == 5}
    post_same = [v["rel"] for k, v in rows.items()
                 if k.split(" x ")[0] in pure and k.split(" x ")[1] in pure]
    post_diff = [v["rel"] for k, v in rows.items()
                 if (k.split(" x ")[0] not in pure) and (k.split(" x ")[1] not in pure)]
    print(f"     POST-HOC, and labelled post-hoc: pure-random pairs mean "
          f"{np.mean(post_same):.4f} (n={len(post_same)}) vs pairs with NO pure-random family "
          f"{np.mean(post_diff):.4f} (n={len(post_diff)})")

    ctrl = pos and g0 and abs(plc - 1) < 1e-9
    if not ctrl:
        world = "UNVERIFIED"
    elif coll > len(FAM) // 2:
        world = f"C - SATURATION: the partial collapses for {coll} of {len(FAM)} families"
    elif maj_hi > len(FAM) // 2:
        world = f"A - PROMPT PROPERTY IDENTIFIED: |corr| >= 0.30 for {maj_hi} of {len(FAM)} families"
    elif maj_lo > len(FAM) // 2:
        world = f"B - RULE ARTIFACT: |corr| < 0.15 for {maj_lo} of {len(FAM)}; D2 refuted"
    else:
        world = (f"NO WORLD - {maj_hi} families >= 0.30 and {maj_lo} < 0.15 of {len(FAM)}; "
                 f"the covariate correlations straddle the registered bands")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/six_families_covariate.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "families": FAM, "reliability": R, "pairs": rows,
        "same_rule_mean": float(np.mean(same)), "diff_rule_mean": float(np.mean(diff)),
        "axis_difference": obs, "null_values": null, "axis_p": rank / len(null),
        "axis_p_floor": 1 / len(null), "n_assignments": len(null),
        "covariate": cov, "corr_poolspread_poolmean": rsm,
        "family_random_k_members": mixed,
        "posthoc_pure_random_mean": float(np.mean(post_same)),
        "posthoc_no_pure_random_mean": float(np.mean(post_diff)),
        "controls": {"placebo": plc, "negative_hi": nhi, "sham_mean": float(np.mean(shamd)),
                     "dose": {str(k): val for k, val in dose.items()},
                     "positive": bool(pos), "g0": bool(g0)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
