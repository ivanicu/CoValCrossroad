#!/usr/bin/env python3
"""
R899 · is the common component a real prompt-level quantity, or an artifact of averaging 8 cells?

⛔ WHY. R897 measured the component at 56.7% of each cell's leakage gap. R898 then failed to name it
against every arm-free candidate the release exposes, and reported that as a fact about the release.
**But there is a cheaper explanation neither round excluded: that averaging 8 noisy gap vectors
manufactures a smooth common vector which correlates with each of its own inputs by construction.**
If so there is less to name than 57% suggests, and R898's negative was a negative about nothing.

⭐ **THE TEST IS SPLIT-HALF, AND IT CAN FAIL.** Compute the component on 4 cells, again on the
disjoint other 4, and correlate. A real prompt-level quantity survives; an averaging artifact does
not, because the two halves share no input.

⭐⭐ **AND THE 35 DISJOINT SPLITS ARE NOT EXCHANGEABLE, WHICH IS THE DESIGN POINT.** The 8 cells are
4 `greedy`, 3 `indep`, 1 `oracle`. A split that puts all four greedy cells on one side tests
something different from one that mixes rules: the first can be carried by a rule-family effect,
the second cannot. **Reporting the mean over all 35 would hide exactly the distinction that
matters**, so splits are stratified by how many rules they separate and every stratum is printed.

⚠ **SPEARMAN-BROWN IS A DERIVATION, NOT A MEASUREMENT.** `2r/(1+r)` corrects a half-length
reliability to full length under the assumption of parallel halves of equal length. The halves here
are 4 cells each, so the length assumption holds, but `parallel` does not — the cells differ in rule
and k. Both numbers are printed, and the corrected one is labelled DERIVED with its assumption.

ESTIMAND        the Pearson correlation between the per-prompt common component computed on one
                half of the cells and on the disjoint other half, over all 35 balanced splits,
                stratified by how many rules the split separates.
IDENTIFICATION  exact. The two halves share no arm and no cell.
SCOPE           population: the 8 2B judge-matched cells; 968 prompts
                instrument: per-prompt A2 margin vs comparator genericpool16
                baseline:   a prompt-permuted half — the floor for "two halves agree"
                regime:     home release, judge 2B
WORLDS          A · split-half r is high in EVERY stratum -> a real prompt-level quantity exists,
                    R897's 57% stands, and R898's failure to name it is a fact about the release
                B · high only where the split MIXES rules, low where it SEPARATES them -> the
                    component is substantially a rule-family effect, and calling it a prompt-level
                    quantity was wrong
                C · low everywhere -> the component is largely an averaging artifact; R897's 57%
                    overstates what is there and R898 was hunting a name for noise
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, on a REAL object with a known answer: the same split-half applied
                     to the arms' RAW margin vectors must come back high. Those genuinely share a
                     prompt-level quantity (they all score A2 on the same prompts against the same
                     target), so if the procedure cannot see reliability there, it cannot see it
                     anywhere.
                  ⭐ ② PLACEBO: permute prompts in one half. r must collapse to ~0. Without it a
                     high r could be any smoothness in the vectors.
                  ⭐ ③ STRATIFIED REPORTING is itself a control against the pooled mean hiding a
                     rule-family effect; each stratum's n is printed.
                  ④ pre-registered: WORLD A needs min-stratum mean r > 0.5; WORLD C is min < 0.2.
MULTIPLICITY    35 splits × 2 arms of the comparison; every stratum reported with its spread.
ARTIFACT        results/component_reliability.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: split-half reliability says the component is STABLE, never that
                it is INTERESTING. A reliable quantity nobody can name is still unnamed.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND = "genericpool16"
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
SEED = 899
CELLS = [("greedy", 2, "greedy_k2", "greedy_k2_fit1"),
         ("greedy", 4, "greedy_k4_greedy_kA", "greedy_k4_fit1"),
         ("greedy", 8, "greedy_k8", "greedy_k8_fit1"),
         ("greedy", 12, "greedy_k12", "greedy_k12_fit1"),
         ("indep", 2, "indep_k2", "indep_k2_fit1"),
         ("indep", 4, "indep_k4_indep_kA", "indep_k4_fit1"),
         ("indep", 8, "indep_k8", "indep_k8_fit1"),
         ("oracle", 4, "oracle_k4", "oracle_k4_fit1")]


def r_(a, b):
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    base = vec(BLIND)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2

    gaps, raws, rules = [], [], []
    for rule, k, l, h in CELLS:
        vl, vh = vec(l), vec(h)
        if vl is None or vh is None:
            continue
        gaps.append((vl - base) - (vh - base)); raws.append(vl - base); rules.append(rule)
    G, R = np.array(gaps), np.array(raws)
    m = len(G)
    print(f"  cells {m} · prompts {n} · rules {sorted(set(rules))}")
    if m < 6:
        print("  UNRUNNABLE: fewer than 6 cells. Exit 2, never 0.")
        return 2

    half = m // 2
    splits = [s for s in itertools.combinations(range(m), half) if 0 in s]
    print(f"  balanced disjoint splits: {len(splits)}  ({half} vs {m - half})")

    def sh(M, idx):
        other = [i for i in range(m) if i not in idx]
        return r_(M[list(idx)].mean(axis=0), M[other].mean(axis=0))

    # stratify by how many rules the split SEPARATES (a rule wholly on one side)
    def sep_count(idx):
        left = {rules[i] for i in idx}
        right = {rules[i] for i in range(m) if i not in idx}
        return len([u for u in set(rules) if (u in left) != (u in right)])

    rows = []
    for s in splits:
        rows.append({"split": list(s), "sep": sep_count(s), "r_gap": sh(G, s), "r_raw": sh(R, s)})

    # ---- CONTROLS -----------------------------------------------------------------------------
    raw_r = np.array([x["r_raw"] for x in rows])
    c1 = float(raw_r.mean()) > 0.5
    rng = np.random.default_rng(SEED)
    plac = []
    for s in splits:
        other = [i for i in range(m) if i not in s]
        plac.append(r_(G[list(s)].mean(axis=0)[rng.permutation(n)], G[other].mean(axis=0)))
    plac = np.array(plac)
    c2 = float(np.abs(plac).max()) < 0.2
    print(f"\n  ① POSITIVE split-half of the RAW arm margins (a real object that genuinely shares "
          f"a prompt quantity): mean r {raw_r.mean():.4f} > 0.5: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② PLACEBO  one half prompt-permuted: max |r| {np.abs(plac).max():.4f} < 0.2: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [bool(c1), bool(c2)]},
                  open(OUT / "component_reliability.json", "w"), indent=2)
        return 2

    strata = {}
    for x in rows:
        strata.setdefault(x["sep"], []).append(x["r_gap"])
    print(f"\n  ⭐ SPLIT-HALF RELIABILITY OF THE COMPONENT, STRATIFIED (③):")
    print(f"     {'rules separated':>16}{'n':>5}{'mean r':>10}{'min':>9}{'max':>9}"
          f"{'SB (DERIVED)':>15}")
    out_strata = []
    for k in sorted(strata):
        v = np.array(strata[k])
        sb = 2 * v.mean() / (1 + v.mean()) if v.mean() > -1 else float("nan")
        print(f"     {k:>16}{len(v):>5}{v.mean():>10.4f}{v.min():>9.4f}{v.max():>9.4f}"
              f"{sb:>15.4f}")
        out_strata.append({"rules_separated": k, "n": len(v), "mean_r": float(v.mean()),
                           "min": float(v.min()), "max": float(v.max()),
                           "spearman_brown_DERIVED": float(sb)})
    allr = np.array([x["r_gap"] for x in rows])
    print(f"     {'ALL':>16}{len(allr):>5}{allr.mean():>10.4f}{allr.min():>9.4f}"
          f"{allr.max():>9.4f}{2*allr.mean()/(1+allr.mean()):>15.4f}")
    print(f"     ⚠ SB is a DERIVATION: 2r/(1+r) assumes PARALLEL halves of equal length. Length")
    print(f"       holds (4 vs 4); parallel does not — the cells differ in rule and k. Labelled.")

    mins = min(s["mean_r"] for s in out_strata)
    world = "A" if mins > 0.5 else "C" if mins < 0.2 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"split-half reliability is above 0.5 in EVERY stratum (min {mins:.4f}) — a real "
             "prompt-level quantity exists, R897's 57% stands, and R898's failure to name it is a "
             "fact about what the release exposes",
        "B": f"reliability varies by stratum (min {mins:.4f}) — the component is partly carried by "
             "rule family, and calling it purely prompt-level was too strong",
        "C": f"reliability is below 0.2 in some stratum (min {mins:.4f}) — the component is largely "
             "an averaging artifact, R897's 57% overstates it, and R898 was hunting a name for "
             "noise"}[world])
    print(f"\n  ⚠ AND RELIABLE IS NOT INTERESTING. Split-half says the component is STABLE, never")
    print(f"    that it MATTERS. A reliable quantity nobody can name is still unnamed — R898's")
    print(f"    negative is not repaired by this round, it is only made readable.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_prompts": n, "n_cells": m,
               "n_splits": len(splits), "strata": out_strata,
               "all_splits": {"mean_r": float(allr.mean()), "min": float(allr.min()),
                              "max": float(allr.max()),
                              "spearman_brown_DERIVED": float(2 * allr.mean() /
                                                              (1 + allr.mean()))},
               "controls": {"positive_raw_margins_mean_r": float(raw_r.mean()),
                            "placebo_permuted_max_abs_r": float(np.abs(plac).max())},
               "spearman_brown_is_a_derivation": "2r/(1+r) assumes parallel halves of equal "
                                                 "length; length holds (4 vs 4), parallel does not",
               "stratification_rationale": "the 35 splits are NOT exchangeable — a split putting "
                                           "all four greedy cells on one side can be carried by a "
                                           "rule-family effect; the pooled mean would hide it",
               "reliable_is_not_interesting": "split-half says STABLE, never MATTERS. R898's "
                                              "failure to name the component is not repaired here.",
               "unit_note": "r is a correlation over PROMPTS; n is SPLITS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "component_reliability.json", "w"), indent=2)
    print(f"\n  artifact: results/component_reliability.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
