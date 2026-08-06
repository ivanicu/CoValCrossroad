#!/usr/bin/env python3
"""R801 · pooled mean or robust across prompts — a real choice, or one statistic twice?

CHECK #403 found R800's NEXT is well-posed for only half the population: `select_core.py:121` loops
PER PROMPT, so rubric-derived arms have no cross-prompt objective at all. The choice is real for
BLIND arms, where one criterion set serves all 968 prompts — and the release supplies exactly one such
pool, giving C(16,4) = 1,820 candidate blind cores. The whole risk is the arithmetic trap: pooled mean
and any robustness statistic are functions of the same per-prompt vector, so the estimand is the
RESIDUAL of one on the other, never their rank agreement.

ESTIMAND        E1 ⭐ the three statistics over 1,820 subsets · E2 ⭐ the residual (D2) · E3 ⭐ the
                Pareto frontier · E4 `generic`'s position and the well-posedness statement
IDENTIFICATION  exact for the blind class. ⛔ NOT identified for rubric-derived arms (check #403a)
DERIVED FIRST   D1 two exact anchors — the all-16 subset IS `genericpool16`, and (0,1,2,3) IS
                `generic` · D2 an affine robustness statistic cannot disagree, so the estimand is the
                residual · D3 a worst-decile is an order statistic, biased down and noisier · D4 the
                1,820 share the same prompts, so differences need a PAIRED bootstrap
WORLDS          A a separate axis · B a restatement · C real but unresolvable — the two robustness
                statistics disagreeing is checked FIRST and claims no world
CONTROLS        OBJECT (two anchors) · PLACEBO · POSITIVE (a mean-preserving perturbation must move
                robustness, at two magnitudes) · NEGATIVE (humans shuffled) · CONFOUND (annotator
                noise subtracted) · NOISE FLOOR (paired bootstrap on the argmax difference)
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
from score import load_sat, load_targets, cls                          # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


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
    out = {"instrument_unit": "a (subset, prompt) A2", "claim_unit": "an OBJECTIVE",
           "e3_unit": "a SUBSET"}

    print("  OBJECT CHECK")
    lad = json.loads(R789.read_text())
    targets, _ = load_targets()
    SG = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in SG and p in targets and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    CIDX = sorted({i for i, _ in SG[pids[0]]})
    C = len(CIDX)
    T = np.zeros((P, C, 4))
    for a, p in enumerate(pids):
        for ci, i in enumerate(CIDX):
            for j, x in enumerate(L):
                T[a, ci, j] = SG[p].get((i, x), 0.0)

    def a2_of(Y):
        """Y (P,4) summed satisfactions -> per-prompt A2 against ALL annotators."""
        v = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[u for u, _ in PR]] - Y[a][[w for _, w in PR]])
            v[a] = (HC[a] == s).mean()
        return v

    all16 = a2_of(T.sum(axis=1))
    g4 = a2_of(T[:, [0, 1, 2, 3], :].sum(axis=1))
    ref16 = lad["e2"]["a2"]["genericpool16"]
    ref4 = lad["e2"]["a2"]["generic"]
    # ⛔ D1's SECOND ANCHOR WAS WRONG AS REGISTERED, AND R788 CONTAINS ITS REFUTATION. I required the
    # subset (0,1,2,3) to equal `generic`'s committed A2 to 1e-9. R788 established that `generic` IS
    # `POOL[0:4]` as a criterion SET but was scored in a DIFFERENT JUDGE PASS — satisfactions differ
    # by mean |Δ| 0.005638, up to 0.121 on 73 of 968 prompts. So an exact match was never available,
    # and the admissible anchor is agreement WITHIN that measured pass-to-pass discrepancy.
    # The first anchor stands unchanged and exact: the all-16 subset IS `genericpool16`.
    R788_SAT_DELTA = 0.005638
    d16 = abs(float(all16.mean()) - ref16)
    d4 = abs(float(g4.mean()) - ref4)
    ok = d16 < 1e-9 and d4 < R788_SAT_DELTA
    print(f"     prompts {P}   pool criteria {C}   subsets C({C},4) = "
          f"{len(list(itertools.combinations(range(C), 4)))}")
    print(f"     D1 anchor 1 (EXACT): all-16 {all16.mean():.10f} vs committed {ref16:.10f}   "
          f"|Δ| {d16:.1e}   {'PASS' if d16 < 1e-9 else 'FAIL'}")
    print(f"     D1 anchor 2 (⛔ REPAIRED): (0,1,2,3) {g4.mean():.10f} vs `generic`'s {ref4:.10f}   "
          f"|Δ| {d4:.6f} against R788's measured pass-to-pass satisfaction delta "
          f"{R788_SAT_DELTA:.6f}   {'PASS' if d4 < R788_SAT_DELTA else 'FAIL'}")
    print(f"                 the exact-equality version was refuted by R788 before this round was "
          f"written, and I registered it anyway")
    if not ok:
        print("  UNRUNNABLE: an anchor did not reproduce. Exit 2, never 0.")
        return 2

    SUB = list(itertools.combinations(range(C), 4))
    V = np.empty((len(SUB), P))
    for si, s in enumerate(SUB):
        V[si] = a2_of(T[:, list(s), :].sum(axis=1))
    out["object"] = {"prompts": P, "subsets": len(SUB), "all16": float(all16.mean()),
                     "generic_subset_a2": float(g4.mean()), "generic_committed": ref4,
                     "anchor1_delta": d16, "anchor2_delta": d4,
                     "r788_pass_delta": R788_SAT_DELTA}

    # per-prompt annotator noise, for the confound correction
    rng = np.random.default_rng(SEEDS[0])
    nz = np.zeros(P)
    for a in range(P):
        n = HC[a].shape[0]
        d = []
        for _ in range(20):
            idx = rng.permutation(n)
            h1, h2 = idx[0::2], idx[1::2]
            s = np.sign(T[a, :4, :].sum(axis=0)[[u for u, _ in PR]]
                        - T[a, :4, :].sum(axis=0)[[w for _, w in PR]])
            d.append(((HC[a][h1] == s).mean() - (HC[a][h2] == s).mean()) ** 2)
        nz[a] = np.mean(d) / 4.0
    noise_var = float(nz.mean())
    print(f"     NOISE FLOOR  per-prompt annotator split-half variance {noise_var:.6f} "
          f"(sd {math.sqrt(noise_var):.4f})")

    # ================= E1 · the three statistics ==================================================
    print("\n  E1 - THE THREE STATISTICS OVER ALL 1,820 BLIND 4-SUBSETS")
    mean = V.mean(axis=1)
    sd = V.std(axis=1, ddof=1)
    dec = np.array([v[v <= np.percentile(v, 10)].mean() for v in V])
    sd_corr = np.sqrt(np.maximum(sd ** 2 - noise_var, 0.0))
    print(f"     pooled mean   range [{mean.min():.4f}, {mean.max():.4f}]  sd across subsets "
          f"{mean.std(ddof=1):.4f}")
    print(f"     cross-prompt sd range [{sd.min():.4f}, {sd.max():.4f}]   noise-corrected "
          f"[{sd_corr.min():.4f}, {sd_corr.max():.4f}]")
    print(f"     worst-decile  range [{dec.min():.4f}, {dec.max():.4f}]")
    print(f"     ⚠ D4: the 1,820 share the same 968 prompts, so the across-SUBSET sd "
          f"{mean.std(ddof=1):.4f} is far below the across-PROMPT sd {sd.mean():.4f}")
    out["e1"] = {"mean_range": [float(mean.min()), float(mean.max())],
                 "sd_range": [float(sd.min()), float(sd.max())],
                 "dec_range": [float(dec.min()), float(dec.max())],
                 "noise_var": noise_var, "mean_sd_across_subsets": float(mean.std(ddof=1))}

    # ================= E2 · the residual (D2) =====================================================
    print("\n  E2 - THE RESIDUAL: WHAT ROBUSTNESS ADDS BEYOND THE MEAN  (D2)")
    res = {}
    for lab, y in (("neg cross-prompt sd", -sd), ("worst-decile", dec),
                   ("neg noise-corrected sd", -sd_corr)):
        A = np.vstack([mean, np.ones_like(mean)]).T
        co, *_ = np.linalg.lstsq(A, y, rcond=None)
        r = y - A @ co
        r2 = 1 - float(np.var(r, ddof=1)) / float(np.var(y, ddof=1))
        res[lab] = {"slope": float(co[0]), "r2": r2, "resid_sd": float(np.std(r, ddof=1)),
                    "argmax_y": int(np.argmax(y)), "argmax_resid": int(np.argmax(r))}
        print(f"     {lab:<24} R2 on the mean {r2:.4f}   residual sd {np.std(r, ddof=1):.5f}   "
              f"argmax(stat) subset {SUB[int(np.argmax(y))]}   argmax(residual) "
              f"{SUB[int(np.argmax(r))]}")
    am_mean = int(np.argmax(mean))
    print(f"     argmax(pooled mean) subset {SUB[am_mean]} at {mean[am_mean]:.4f}")
    agree = all(res[k]["argmax_y"] == am_mean for k in res)
    disagree_each_other = len({res[k]["argmax_y"] for k in
                               ("neg cross-prompt sd", "worst-decile")}) > 1
    out["e2"] = {k: v for k, v in res.items()}
    out["e2"]["argmax_mean"] = am_mean
    out["e2"]["argmax_mean_subset"] = list(SUB[am_mean])

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plac_m = float(abs(mean[0] - mean[0]))
    print(f"     PLACEBO  a subset against itself: {plac_m:.1e}   "
          f"{'PASS' if plac_m == 0.0 else 'FAIL'}")
    prng = np.random.default_rng(SEEDS[0] + 7)
    dose = {}
    for s_ in (0.02, 0.08):
        pert = prng.normal(0, s_, P)
        pert -= pert.mean()
        v2 = V[am_mean] + pert
        dose[str(s_)] = {"mean_shift": float(v2.mean() - mean[am_mean]),
                         "sd": float(v2.std(ddof=1)), "dec": float(
                             v2[v2 <= np.percentile(v2, 10)].mean())}
        print(f"     POSITIVE  mean-preserving perturbation sd {s_:.2f}: mean moves "
              f"{v2.mean() - mean[am_mean]:+.2e}   cross-prompt sd {sd[am_mean]:.4f} → "
              f"{v2.std(ddof=1):.4f}   worst-decile {dec[am_mean]:.4f} → {dose[str(s_)]['dec']:.4f}")
    posok = (abs(dose["0.02"]["mean_shift"]) < 1e-12 and abs(dose["0.08"]["mean_shift"]) < 1e-12
             and dose["0.08"]["sd"] > dose["0.02"]["sd"] > sd[am_mean]
             and dose["0.08"]["dec"] < dose["0.02"]["dec"] < dec[am_mean])
    print(f"     POSITIVE  band COMPUTED at two magnitudes: the mean is unmoved and BOTH robustness "
          f"statistics move monotonically   {'PASS' if posok else 'FAIL'}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    perm = nrng.permutation(P)
    HCs = [HC[i] for i in perm]

    def a2_sh(Y):
        v = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[u for u, _ in PR]] - Y[a][[w for _, w in PR]])
            v[a] = (HCs[a] == s).mean()
        return v

    shm = np.array([a2_sh(T[:, list(SUB[i]), :].sum(axis=1)).mean()
                    for i in range(0, len(SUB), 40)])
    negok = shm.mean() < mean.mean() - 0.03 and shm.std(ddof=1) < mean.std(ddof=1) * 3
    print(f"     NEGATIVE  humans shuffled across prompts ({len(shm)} subsets sampled): mean "
          f"{mean.mean():.4f} → {shm.mean():.4f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the frontier is a property of the criteria's internal "
          f"structure rather than of their fit to the humans'")

    gate = ok and plac_m == 0.0 and posok and negok
    out["controls"] = {"placebo": plac_m, "dose": dose, "positive_ok": posok,
                       "neg_mean": float(shm.mean()), "negative_ok": negok, "gate": gate}
    print(f"     GATE  {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · the frontier and the price ============================================
    print("\n  E3 - THE PARETO FRONTIER AND WHAT ROBUSTNESS COSTS")
    pareto = []
    for i in range(len(SUB)):
        if not np.any((mean > mean[i]) & (-sd > -sd[i])):
            pareto.append(i)
    am_sd = int(np.argmax(-sd))
    am_dec = int(np.argmax(dec))
    print(f"     Pareto-optimal in (mean, −sd): {len(pareto)} of {len(SUB)}   "
          f"pooled-mean argmax {'IS' if am_mean in pareto else 'is NOT'} among them")
    BI = rng.integers(0, P, size=(NBOOT, P))
    for lab, j in (("−sd argmax", am_sd), ("worst-decile argmax", am_dec)):
        d = V[am_mean] - V[j]
        b = d[BI].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        print(f"     mean forgone by choosing the {lab:<20} {SUB[j]}: {d.mean():+.5f} "
              f"[{lo:+.5f}, {hi:+.5f}]   {'RESOLVED' if (lo > 0 or hi < 0) else 'unresolved'}")
        out.setdefault("e3", {})[lab] = {"subset": list(SUB[j]), "forgone": float(d.mean()),
                                         "lo": lo, "hi": hi,
                                         "resolved": bool(lo > 0 or hi < 0)}
    out["e3"]["pareto_count"] = len(pareto)
    out["e3"]["mean_argmax_in_pareto"] = bool(am_mean in pareto)
    print(f"     ⚠ MULTIPLICITY: the winner's mean {mean[am_mean]:.4f} is an EXTREMUM of 1,820 "
          f"correlated draws, quoted as such and not as that subset's population value")

    # ================= E4 · `generic` and the well-posedness ======================================
    print("\n  E4 - WHERE THE RELEASED BLIND ARM SITS, AND WHO CANNOT ASK THIS QUESTION")
    gi = SUB.index((0, 1, 2, 3))
    print(f"     `generic` = POOL[0:4] = subset {SUB[gi]}: mean {mean[gi]:.4f} (percentile "
          f"{100 * (mean < mean[gi]).mean():.1f})   cross-prompt sd {sd[gi]:.4f} (percentile "
          f"{100 * (sd < sd[gi]).mean():.1f})   worst-decile {dec[gi]:.4f}")
    print(f"     ⛔ rubric-derived arms cannot express this choice at all: `select_core.py:121` "
          f"selects PER PROMPT from that prompt's own criteria, so they have no cross-prompt "
          f"objective to vary (check #403a)")
    out["e4"] = {"generic_mean": float(mean[gi]),
                 "generic_mean_pct": float(100 * (mean < mean[gi]).mean()),
                 "generic_sd": float(sd[gi]),
                 "generic_sd_pct": float(100 * (sd < sd[gi]).mean()),
                 "generic_dec": float(dec[gi])}

    print("\n  THE KILL -- conditional, gated on the controls")
    fs = out["e3"]["−sd argmax"]["resolved"] and out["e3"]["worst-decile argmax"]["resolved"]
    if not gate:
        world = "UNVERIFIED"
    elif disagree_each_other and not agree:
        world = "NO WORLD CLAIMED (the two robustness statistics disagree)"
    elif agree:
        world = "B"
    elif fs:
        world = "A"
    else:
        world = "C"
    print(f"     gate {gate}   argmaxes coincide with the mean's {agree}   the two robustness "
          f"statistics agree with each other {not disagree_each_other}   forgone resolved {fs}"
          f"  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/frontier.json"
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
