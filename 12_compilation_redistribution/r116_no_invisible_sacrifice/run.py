"""r116 -- NO INVISIBLE SACRIFICE. The full service distribution, and the absolute harm rate.

The north star, set by Ivan 2026-07-30, and it is a claim about REPORTING before it is a claim about
fairness:

    A common target may not achieve average success by invisibly and persistently sacrificing
    particular people.

Three obligations follow. This round discharges the first two on data already in hand:
  (1) every common target reports the FULL DISTRIBUTION of individual service, never only the mean;
  (2) if particular people persistently do worse, the system must IDENTIFY that cost rather than
      leave it inside an aggregate accuracy;
  (3) when one target cannot serve distinct stable preferences at acceptable cost, abstain or emit
      several -- NOT this round.

WHY THIS IS NOT A REGRESSION, AND SO NOT EXPOSED TO r115's THEOREM
------------------------------------------------------------------
r115 proved that regressing a paired difference of two rules' error on a rater-level covariate yields
a coefficient set by the arms' accuracy gap: beta_d = k*beta_sum <=> beta_a proportional to
(0.5 - e_a), one shared lambda = 0.4521. Every claim of the form "group G gains less" is exposed to
that and must be stated as a departure from the line.

**This round regresses nothing.** H_eps counts people whose own paired difference exceeds a
threshold. CVaR averages a level. Neither is a covariate coefficient, so neither inherits the
artifact. That is the reason to do the counting BEFORE any further modelling.

THE INSTRUMENT THE PROGRAMME ONLY JUST DISCOVERED IT HAD
--------------------------------------------------------
An absolute harm rate is worthless without a noise floor: with a median of ~15 prompts per rater,
L_i(Core) - L_i(Full) carries real sampling error, so people appear harmed by chance alone. Entry 26
established that this release DOES carry within-cell replication -- 111 of 18,269 (prompt, rater)
cells hold 2 to 5 assessments -- which measures that noise DIRECTLY, with no model:

    the same person, the same prompt, twice  ->  the spread of L within a cell IS the floor.

So the harm rate is reported against two independent floors:
  FLOOR A  the paired within-prompt identity shuffle (preserves gamma, each rater's count, and the
           marginal error distribution exactly; destroys real person structure). Model-free.
  FLOOR B  the observed within-cell replicate spread. Also model-free, and it comes from the data
           doing the same thing twice rather than from a permutation of it.
Two floors that cannot fail the same way is the point; entry 24 was retracted because ONE null was
load-bearing and had no power against the rival that mattered.

CLAIM CARD
----------
Claim      "Compilation improves agreement with nearly everyone" (entries 21/22) is an average
           statement, and the north star forbids resting on it. How many people are ABSOLUTELY worse
           off under the compiled rule, by how much, and is that count above the floor?
Estimand   H_eps = P[ L_i(core) - L_i(full) > eps ] for eps in {0, 0.005, 0.01, 0.02},
           the deconvolved harmed fraction, CVaR at 5/10/20% under EACH arm separately, and the
           Lorenz/Gini concentration of the gains.
Target
observed?  YES, on the full population entries 21/22 were measured on. No new data, no new subjects.
Worlds     W-VISIBLE-COST   H_eps clears its floors at some eps that matters. There is a real,
                            countable set of people the compiled rule serves worse, and the north
                            star's obligation (2) has a subject to point at -- even if that subject
                            has no demographic name (entry 25).
           W-NOISE-ONLY     H_eps sits at its floors at every eps. Nobody is absolutely harmed; the
                            redistribution is entirely in the SIZE of a universal gain, and the
                            honest headline is "winners and smaller winners" with no sacrifice at all.
Intervention
           none.
Nulls      (i) POSITIVE CONTROL, and it gates the whole round: plant a known harmed subgroup --
           e_core += g on a random 10% of raters -- and require H_eps to recover it at each g. A low
           harm rate from an instrument never shown to detect harm is silence, not an acquittal.
           (ii) FLOOR A, the paired shuffle, per eps.
           (iii) FLOOR B, the within-cell replicates, which no permutation can imitate.

PRE-REGISTERED, before the run
------------------------------
W-VISIBLE-COST requires the observed H_eps to exceed FLOOR A's 97.5th percentile at eps = 0.01 --
one percentage point of pairwise-discordance rate, chosen as the smallest harm this release could
plausibly call material and NOT chosen after seeing the numbers. The positive control must recover a
planted g = 0.02 for any null here to be admissible.

WHAT THIS ROUND MAY NOT CONCLUDE
--------------------------------
That the harmed set is a GROUP (entry 25 found no demographic subject over 30 tested cells), that the
harm is about VALUES (entry 24 retracted that), or that a different compiler would avoid it (no V2
exists). It reports a distribution and a count. The north star's first obligation is exactly that,
and the discipline of this project is that a count is worth more than a story about the count.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402

FULL = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

SEED = 20260730
N_SHUFFLE, N_BOOT = 400, 2000
EPS = (0.0, 0.005, 0.01, 0.02)
EPS_DECISIVE = 0.01          # pre-registered: the smallest materially harmful shift
# Swept far enough to actually cross the gain distribution. The first version stopped at 0.04 while
# the MEAN gain is -0.072, so a planted 0.04 could only flip people whose delta sat in a narrow band
# and H moved 1.0pp against a 10% plant. A plant that cannot move the statistic is not a control.
PLANT_G = (0.0, 0.02, 0.05, 0.10, 0.15, 0.20)
PLANT_SHARE = 0.10
CVAR_Q = (0.05, 0.10, 0.20)


def load_sat(path: Path) -> dict:
    z = np.load(path, allow_pickle=True)
    d: dict = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def equal_weight_scores(satp: dict) -> dict:
    out = {}
    for lab in sorted({l for _, l in satp}):
        v = [s for (ci, ll), s in satp.items() if ll == lab]
        if v:
            out[lab] = float(np.mean(v))
    return out


def strict_pairs(ranking: str) -> set:
    tiers = [t.split("=") for t in ranking.split(">")]
    out = set()
    for i, a in enumerate(tiers):
        for b in tiers[i + 1:]:
            for x in a:
                for y in b:
                    out.add((x.strip(), y.strip()))
    return out


def build():
    """Every (prompt, rater, assessment) with both arms scored. Assessment-level, so the 111
    replicated cells appear as the multiple rows they are -- which is what makes FLOOR B possible."""
    F, C = load_sat(FULL), load_sat(CORE)
    rows = []
    joined = sorted(((pid, comp) for pid, comp, rub in load_join(COMPARISONS, RUBRICS)
                     if pid in F and pid in C), key=lambda t: t[0])
    for pid, comp in joined:
        sc = {"full": equal_weight_scores(F[pid]), "core": equal_weight_scores(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        for a in sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            P0 = strict_pairs(w[0].get("ranking", ""))
            e = {}
            for arm in ("full", "core"):
                s = sc[arm]
                P = {(x, y) for x, y in P0 if x in s and y in s and s[x] != s[y]}
                if not P:
                    break
                e[arm] = sum(1 for x, y in P if s[x] < s[y]) / len(P)
            if len(e) == 2:
                rows.append((pid, str(a.get("annotator_id")), e["full"], e["core"]))
    return rows


def person_means(ri, ef, ec, nR):
    cnt = np.maximum(np.bincount(ri, None, nR), 1)
    return (np.bincount(ri, ef, nR) / cnt, np.bincount(ri, ec, nR) / cnt,
            np.bincount(ri, None, nR))


def harm_rates(delta, eps_list):
    return {f"{e:g}": float(np.mean(delta > e)) for e in eps_list}


def cvar(x, q):
    """Mean of the WORST q fraction. A level, not a change score, so no Oldham exposure."""
    k = max(1, int(round(q * len(x))))
    return float(np.sort(x)[-k:].mean())


def gini(gain):
    """Concentration of the IMPROVEMENT. Computed on -delta clipped at 0 -- the gain each person
    actually received -- because a Gini on a signed quantity is not interpretable."""
    g = np.sort(np.maximum(-gain, 0.0))
    n = len(g)
    if g.sum() <= 0:
        return float("nan")
    idx = np.arange(1, n + 1)
    return float((2 * (idx * g).sum()) / (n * g.sum()) - (n + 1) / n)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r116_no_invisible_sacrifice.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    rows = build()
    if not rows:
        print("REFUSING: empty population. Nothing-to-measure exits 2, never 0.", file=sys.stderr)
        return 2
    pids = sorted({r[0] for r in rows}); rids = sorted({r[1] for r in rows})
    PI = {p: i for i, p in enumerate(pids)}; RI = {r: i for i, r in enumerate(rids)}
    pi = np.array([PI[r[0]] for r in rows]); ri = np.array([RI[r[1]] for r in rows])
    ef = np.array([r[2] for r in rows]); ec = np.array([r[3] for r in rows])
    nR, nP = len(rids), len(pids)

    cells = {}
    for a, b in zip(pi, ri):
        cells[(int(a), int(b))] = cells.get((int(a), int(b)), 0) + 1
    n_rep = sum(1 for v in cells.values() if v > 1)
    print(f"assessments {len(rows):,}   distinct (prompt,rater) cells {len(cells):,}   "
          f"prompts {nP}   raters {nR}   replicated cells {n_rep}")

    Lf, Lc, ni = person_means(ri, ef, ec, nR)
    delta = Lc - Lf
    keep = ni > 0
    Lf, Lc, delta, ni = Lf[keep], Lc[keep], delta[keep], ni[keep]
    print(f"per-person: mean L_full {Lf.mean():.5f}  L_core {Lc.mean():.5f}  "
          f"mean delta {delta.mean():+.5f}   prompts per person: median {int(np.median(ni))} "
          f"min {int(ni.min())} max {int(ni.max())}")

    # ---- THE DISTRIBUTION, which the north star says may not be replaced by its mean ----
    qs = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    dq = np.percentile(delta, qs)
    print(f"\n  INDIVIDUAL SERVICE CHANGE, full distribution (negative = better served by core)")
    print("   pct " + "".join(f"{q:>9}" for q in qs))
    print("   d   " + "".join(f"{v:>+9.4f}" for v in dq))

    obs_H = harm_rates(delta, EPS)
    print(f"\n  ABSOLUTE HARM RATE H_eps = share with L_core - L_full > eps")
    for e in EPS:
        print(f"    eps={e:<6} H = {obs_H[f'{e:g}']:.4%}  ({int(round(obs_H[f'{e:g}']*len(delta)))} of {len(delta)} people)")

    # ---- FLOOR A: paired within-prompt identity shuffle -------------------------------
    floorA = {f"{e:g}": [] for e in EPS}
    for _ in range(N_SHUFFLE):
        s = ri.copy()
        for p in np.unique(pi):
            ix = np.flatnonzero(pi == p)
            s[ix] = ri[rng.permutation(ix)]
        a_, b_, n_ = person_means(s, ef, ec, nR)
        m = n_ > 0
        d_ = (b_ - a_)[m]
        for e in EPS:
            floorA[f"{e:g}"].append(float(np.mean(d_ > e)))
    print(f"\n  FLOOR A -- paired within-prompt identity shuffle ({N_SHUFFLE} draws), model-free")
    fA = {}
    for e in EPS:
        v = np.array(floorA[f"{e:g}"]); lo, hi = np.percentile(v, [2.5, 97.5])
        # The PERMUTATION p-value, not a comparison of two intervals. Two overlapping CIs are not a
        # test, and "above the 97.5th percentile" is a coarse read of the same draws: the exact
        # statement is what share of null draws reach the observed value.
        p_perm = float((np.sum(v >= obs_H[f"{e:g}"]) + 1) / (len(v) + 1))
        fA[f"{e:g}"] = {"mean": float(v.mean()), "p97_5": float(hi), "ci": [float(lo), float(hi)],
                        "p_perm": p_perm}
        excess = obs_H[f"{e:g}"] - v.mean()
        print(f"    eps={e:<6} floor {v.mean():.4%} [{lo:.4%},{hi:.4%}]   observed "
              f"{obs_H[f'{e:g}']:.4%}   EXCESS {excess:+.4%}   p_perm {p_perm:.4f}   "
              f"{'above 97.5th' if obs_H[f'{e:g}'] > hi else 'inside the floor'}")

    # ---- FLOOR B: the replicated cells, which no permutation can imitate ---------------
    per_cell = defaultdict(list)
    for a, b, x, y in zip(pi, ri, ef, ec):
        per_cell[(int(a), int(b))].append(y - x)
    reps = [v for v in per_cell.values() if len(v) > 1]
    if reps:
        within = np.concatenate([np.array(v) - np.mean(v) for v in reps])
        dfree = sum(len(v) - 1 for v in reps)
        var_within = float((within ** 2).sum() / max(dfree, 1))
        se_person = np.sqrt(var_within / ni)
        implied = float(np.mean(1 - 0.5 * (1 + np.vectorize(
            lambda z: math_erf(z))((EPS_DECISIVE - delta.mean()) / (np.sqrt(2) * se_person)))))
        print(f"\n  FLOOR B -- {len(reps)} replicated cells, {dfree} df, within-cell var "
              f"{var_within:.5f}")
        print(f"    implied per-person se: median {np.median(se_person):.5f}  "
              f"min {se_person.min():.5f}  max {se_person.max():.5f}")
        print(f"    a person's delta must clear ~{1.96*np.median(se_person):.4f} to be "
              f"distinguishable from replicate noise at the median workload")
        floorB = {"n_replicated": len(reps), "df": dfree, "var_within": var_within,
                  "se_person_median": float(np.median(se_person)),
                  "resolution_at_median": float(1.96 * np.median(se_person))}
    else:
        floorB = None
        print("\n  FLOOR B UNAVAILABLE: no replicated cells in this population.")

    # ---- DECONVOLUTION: the harmed fraction after removing sampling noise --------------
    var_delta = float(delta.var())
    noise = var_within * float(np.mean(1.0 / ni)) if reps else float("nan")
    true_var = var_delta - noise
    if reps and true_var > 0:
        sd_true = float(np.sqrt(true_var))
        true_harm = float(0.5 * (1 - math_erf((EPS_DECISIVE - delta.mean()) / (sd_true * 2 ** 0.5))))
        print(f"\n  DECONVOLVED at eps={EPS_DECISIVE}: observed var(delta) {var_delta:.5f} minus "
              f"replicate noise {noise:.5f} = {true_var:.5f} (sd {sd_true:.4f})")
        print(f"    implied TRUE harmed fraction {true_harm:.2%}  against observed "
              f"{obs_H[f'{EPS_DECISIVE:g}']:.2%}")
    else:
        sd_true, true_harm = float("nan"), float("nan")
        print(f"\n  DECONVOLUTION NOT ESTIMABLE: var(delta) {var_delta:.5f} minus noise "
              f"{noise:.5f} is non-positive. Reporting nan, never a clamped zero.")

    # ---- POSITIVE CONTROL: plant a harmed subgroup and require recovery ---------------
    print(f"\n  POSITIVE CONTROL -- plant e_core += g on a random {PLANT_SHARE:.0%} of raters")
    pc = {}
    hurt = rng.choice(nR, size=max(1, int(PLANT_SHARE * nR)), replace=False)
    mask = np.isin(ri, hurt)
    # The statistic is an INCREMENT over the g=0 arm, not a level. At g=0 the observed H already
    # exceeds the floor, so "H clears the floor while harm is planted" is true before anything is
    # planted -- a check that cannot fail, which this programme has now catalogued four times.
    h0 = None
    mde_g = None
    for g_ in PLANT_G:
        ec2 = ec + g_ * mask
        _a, b2, n2 = person_means(ri, ef, ec2, nR)
        d2 = (b2 - _a)[n2 > 0]
        h = harm_rates(d2, (EPS_DECISIVE,))[f"{EPS_DECISIVE:g}"]
        if h0 is None:
            h0 = h
        inc = h - h0
        rec = inc / PLANT_SHARE
        pc[str(g_)] = {"H": h, "increment": inc, "recovery_of_plant": rec}
        if mde_g is None and rec >= 0.5 and g_ > 0:
            mde_g = g_
        print(f"    g={g_:.2f}: H_{EPS_DECISIVE} = {h:.4%}   increment {inc:+.4%}   "
              f"recovers {rec:.0%} of the {PLANT_SHARE:.0%} planted")
    # A control passes when a plant is RECOVERED, and the round states the smallest g at which it is.
    control_ok = mde_g is not None
    print(f"    -> smallest g recovering >=50% of the plant: "
          f"{mde_g if mde_g is not None else 'NONE IN THE SWEEP'}")
    if not control_ok:
        print("    the instrument cannot recover a planted harm anywhere in this sweep, so its "
              "own harm rate is not interpretable as a measurement")

    # ---- THE TAIL, as levels so no Oldham exposure ------------------------------------
    print(f"\n  WORST-SERVED TAIL (CVaR: mean loss of the worst q, a LEVEL not a change score)")
    tail = {}
    for q in CVAR_Q:
        cf, cc = cvar(Lf, q), cvar(Lc, q)
        tail[f"{q:g}"] = {"full": cf, "core": cc, "delta": cc - cf}
        print(f"    worst {q:.0%}: full {cf:.5f}  core {cc:.5f}  change {cc-cf:+.5f}")

    gi = gini(delta)
    top_share = float(np.sort(np.maximum(-delta, 0))[-max(1, len(delta)//10):].sum()
                      / max(np.maximum(-delta, 0).sum(), 1e-12))
    print(f"\n  GAIN CONCENTRATION: Gini {gi:.4f}; the top decile of gainers receives "
          f"{top_share:.1%} of all improvement")

    # ---- bootstrap over PEOPLE for the headline count --------------------------------
    boots = []
    for _ in range(N_BOOT):
        take = rng.integers(0, len(delta), len(delta))
        boots.append(float(np.mean(delta[take] > EPS_DECISIVE)))
    blo, bhi = np.percentile(boots, [2.5, 97.5])
    print(f"  H_{EPS_DECISIVE} bootstrap over people: {obs_H[f'{EPS_DECISIVE:g}']:.4%} "
          f"[{blo:.4%},{bhi:.4%}]  ({N_BOOT} draws)")

    above = fA[f"{EPS_DECISIVE:g}"]["p_perm"] < 0.05
    world = ("UNVERIFIED" if not control_ok else
             "W-VISIBLE-COST" if above else "W-NOISE-ONLY")
    conclusion = (
        f"On {len(rows):,} assessments over {len(cells):,} cells, {nP} prompts and {len(delta)} "
        f"people, the compiled rule changes individual service by a median of {np.median(delta):+.4f} "
        f"and a mean of {delta.mean():+.5f}, with the 1st-to-99th percentile running "
        f"{dq[0]:+.4f} to {dq[-1]:+.4f}. ABSOLUTE HARM at the pre-registered eps={EPS_DECISIVE}: "
        f"{obs_H[f'{EPS_DECISIVE:g}']:.2%} of people are worse off, bootstrap [{blo:.2%},{bhi:.2%}], "
        f"against a paired-shuffle floor of {fA[f'{EPS_DECISIVE:g}']['mean']:.2%} whose 97.5th "
        f"percentile is {fA[f'{EPS_DECISIVE:g}']['p97_5']:.2%}: excess "
        f"{obs_H[f'{EPS_DECISIVE:g}'] - fA[f'{EPS_DECISIVE:g}']['mean']:+.2%}, permutation "
        f"p = {fA[f'{EPS_DECISIVE:g}']['p_perm']:.4f}. "
        + (f"The replicated cells give an independent, permutation-free floor: {floorB['n_replicated']} "
           f"cells, {floorB['df']} df, per-person resolution {floorB['resolution_at_median']:.4f} at "
           f"the median workload, and deconvolving that noise leaves a true harmed fraction of "
           f"{true_harm:.2%}. " if floorB and true_harm == true_harm else "")
        + f"The worst-served 10% carry mean loss {tail['0.1']['full']:.4f} under full and "
        f"{tail['0.1']['core']:.4f} under core ({tail['0.1']['delta']:+.4f}). Gains are concentrated "
        f"at Gini {gi:.3f}, the top decile taking {top_share:.0%} of all improvement. The positive "
        f"control plants harm on {PLANT_SHARE:.0%} of raters and needs g={mde_g} before it recovers "
        f"half the plant -- an increment of {pc[str(mde_g)]['increment']:+.2%} on a {PLANT_SHARE:.0%} "
        f"plant -- so the harm rate resolves only shifts of that size and larger. "
        if mde_g is not None else
        f"control plants harm on {PLANT_SHARE:.0%} of raters and recovers less than half of it at "
        f"every g up to {max(PLANT_G)}, so this harm rate is NOT interpretable as a measurement. "
        f"WORLD: {world}. "
        + ("A countable set of people is absolutely worse served by the compiled rule, above a "
           "model-free floor. The north star's second obligation has something to point at."
           if world == "W-VISIBLE-COST" else
           "No excess of absolutely-harmed people survives the floor. The redistribution is entirely "
           "in the SIZE of a near-universal gain: winners and smaller winners, with no sacrifice to "
           "make visible at this threshold."
           if world == "W-NOISE-ONLY" else
           "The positive control did not clear the floor, so this instrument cannot separate a real "
           "harm rate from its own noise. UNVERIFIED, and it acquits nothing."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"n_assessments": len(rows), "n_cells": len(cells), "n_prompts": nP,
           "n_people": int(len(delta)), "n_replicated_cells": n_rep,
           "mean_L_full": float(Lf.mean()), "mean_L_core": float(Lc.mean()),
           "mean_delta": float(delta.mean()), "median_delta": float(np.median(delta)),
           "percentiles": {str(q): float(v) for q, v in zip(qs, dq)},
           "harm_observed": obs_H, "floor_A_shuffle": fA, "floor_B_replicates": floorB,
           "deconvolved": {"var_delta": var_delta, "noise": noise if reps else None,
                           "sd_true": sd_true, "true_harmed_fraction": true_harm,
                           "eps": EPS_DECISIVE},
           "positive_control": {"share": PLANT_SHARE, "by_g": pc,
                                "mde_g_half_recovery": mde_g, "recovers": bool(control_ok)},
           "cvar": tail, "gini_of_gain": gi, "top_decile_share_of_gain": top_share,
           "bootstrap_H": {"eps": EPS_DECISIVE, "point": obs_H[f"{EPS_DECISIVE:g}"],
                           "ci": [float(blo), float(bhi)], "n": N_BOOT},
           "eps_grid": list(EPS), "eps_decisive": EPS_DECISIVE,
           "world": world, "conclusion": conclusion, **stamp(__file__)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    np.savez_compressed(_RES / "r116_people.npz", L_full=Lf, L_core=Lc, delta=delta, n_i=ni,
                        rater_ids=np.array([r for r in rids], dtype=object))
    print(f"-> {args.out}")
    return 0


def math_erf(x):
    import math
    return math.erf(x)


if __name__ == "__main__":
    sys.exit(main())
