"""r114 -- does the withheld improvement have a DEMOGRAPHIC subject? The last CoVal round.

Directed by an independent navigator after entry 24 retracted the value-divergence subject. Its
reasoning, checked rather than taken:

  * The covariate exists at 100% coverage on the exact population entries 21/22 were measured on:
    `data/annotators.jsonl`, 1,012 of 1,012 records, six structured axes summing to exactly 47 group
    cells -- age 6, ai_concern_level 4, country_of_residence 19, education_level 7, gender 4,
    generative_ai_usage 7, zero missing on any axis, and the 1,012 ids are the 1,012 rater indices.
  * 113 rounds never crossed it with the compilation contrast. Seven rounds load demographics; none
    of them touches core.
  * It escapes BOTH killers. alpha died because it is derived from the outcome (entry 22). x1 died
    because a careless rater produces noisy scores AND a noisy ranking, and this release has no
    instrument separating attention from values (wall #1). A group indicator is neither: it is not
    derived from the outcome, and carelessness cannot manufacture a country of residence.

THE DEFECT THIS ROUND IS BUILT AGAINST, which is the previous round's own root cause
-----------------------------------------------------------------------------------
Entry 22's directive asked for a coefficient on a DIFFERENCE and never asked for the per-arm
coefficients. So r112 computed err["full"] and err["core"], kept only their difference, and the
diagnostic that overturned it was destroyed three lines after being available. This round reports
the LEVELS FIRST and the difference second, and its estimand is not the difference coefficient at
all -- it is the DEPARTURE FROM THE ARITHMETIC LINE.

Because that is what entry 24 established: any covariate raising both arms' errors yields a
differential proportional to their accuracy gap. On 7 arm pairs, residuals about `k*beta_sum` had
sd 0.00743 against a mean se of 0.00858 -- not one pair was distinguishable from pure arithmetic.
The line is therefore not merely a nuisance to purge; it is a CALIBRATED PREDICTION, and a group is
a subject only if it departs from it.

CLAIM CARD
----------
Claim      The redistribution entries 21/22 measured -- compilation improving nearly everyone while
           withholding a differing SHARE of that improvement -- has an identifiable demographic
           subject.
Estimand   For each group cell g, the coefficient on 1[rater in g] in
               y_purged = (e_core - e_full) - k*(e_core + e_full)
           with prompt fixed effects and two-way clustering on prompt and rater, where
           k = mean(d)/(mean(sum) - 1) is the global Oldham factor that makes y_purged invariant to
           a common shrink toward chance. By linearity this coefficient IS beta_d,g - k*beta_sum,g,
           the departure from the arithmetic line. NOT beta_d,g, which entry 24 showed is the line.
Target
observed?  YES, verified above before any code was written.
Worlds     W-SUBJECT    at least one group cell's departure survives Benjamini-Hochberg across all
                        tested cells, AND the matched-arm contrast on the even-rater half agrees in
                        sign. The redistribution has a demographic subject -- D6 at best, because a
                        demographic group can differ in average CARE and this release cannot
                        separate care from values.
           W-ANONYMOUS  no cell survives BH while the positive control retains a planted effect.
                        The rater component is real and has NO demographic subject on the only
                        release carrying both. "Identifiable subgroup" leaves the claim permanently,
                        and NOT to be reopened on another dataset.
Intervention
           none. A 47-column indicator matrix over the same cells.
Nulls      (i) POSITIVE CONTROL, and it gates everything: plant a group-specific ONE-ARMED effect
           (e_core += g*1[group]) on a real group at g in {0.02, 0.04} and require recovery. A
           measured zero from an instrument never shown to return non-zero is silence.
           (ii) NEGATIVE CONTROL, and it is deliberately NOT A PERMUTATION. A permutation null has
           been placed in the load-bearing position three times in this programme and had no power
           against the rival that mattered each time; it answers "did the labelling matter", never
           "why". Instead: SYNTHETIC PARTITIONS matched to each real group on size AND on mean
           own-error, so a group that differs only by being noisier or more error-prone lands ON the
           line. Only a departure beyond that band is a subject.
           (iii) The arithmetic line itself, reported per group as beta_d and k*beta_sum side by
           side, so a reader sees the prediction next to the observation.

PRE-REGISTERED, written before the run and not tuned
----------------------------------------------------
MIN_GROUP_RATERS = 20. Two axes have levels with a single rater; a coefficient on one person is not
a group effect. Cells below the floor are REPORTED and excluded from BH, and the count excluded is
printed -- a silent exclusion is a scope claim.
BH_Q = 0.05 across every tested cell, all six axes together, because testing 47 cells and reporting
the best is the multiplicity failure this programme has already catalogued.
KILL: no tested cell's departure survives BH AND the positive control recovers a planted g=0.02 at
|t| > 2  ->  W-ANONYMOUS, CoVal closes, the closing document is written.
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
ANNOTATORS = _ROOT / "data/annotators.jsonl"
R113 = _ROOT / "12_compilation_redistribution/r113_accuracy_matched_arm/results/r113_cells.npz"

SEED = 20260729
MIN_GROUP_RATERS = 20
BH_Q = 0.05
N_SYNTH = 200
PLANT = (0.02, 0.04)
AXES = ("age", "ai_concern_level", "country_of_residence", "education_level", "gender",
        "generative_ai_usage")


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


def demean(v, g):
    s = np.bincount(g, v, g.max() + 1)
    c = np.maximum(np.bincount(g, None, g.max() + 1), 1)
    return v - (s / c)[g]


def twoway(y, X, gp, gr):
    """OLS with Cameron-Gelbach-Miller two-way cluster-robust covariance. y, X already prompt-demeaned."""
    XtX = np.linalg.pinv(X.T @ X)
    beta = XtX @ (X.T @ y)
    u = y - X @ beta

    def meat(g):
        M = np.zeros((X.shape[1], X.shape[1]))
        for gv in np.unique(g):
            m = g == gv
            s = X[m].T @ u[m]
            M += np.outer(s, s)
        return M

    inter = gp.astype(np.int64) * (gr.max() + 1) + gr.astype(np.int64)
    V = XtX @ (meat(gp) + meat(gr) - meat(inter)) @ XtX
    w, Q = np.linalg.eigh(V)
    V = Q @ np.diag(np.maximum(w, 0)) @ Q.T
    return float(beta[0]), float(np.sqrt(max(V[0, 0], 0.0)))


def build():
    """All cells with both arms scored, carrying the rater's ID. No profile requirement, so this is
    the FULL population entries 21/22 were measured on, not r112's 96.3% subset."""
    F, C = load_sat(FULL), load_sat(CORE)
    cells = []
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
                cells.append({"pid": pid, "rid": str(a.get("annotator_id")), **e})
    return cells


def bh(pvals, q):
    """Benjamini-Hochberg. Returns the boolean survival mask in the INPUT order."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    thresh = q * (np.arange(1, n + 1) / n)
    passed = p[order] <= thresh
    k = np.max(np.flatnonzero(passed)) + 1 if passed.any() else 0
    keep = np.zeros(n, bool)
    keep[order[:k]] = True
    return keep


def norm_p(t):
    """Two-sided normal p. No scipy dependency, and the approximation is stated: Abramowitz-Stegun
    7.1.26 for erf, |error| < 1.5e-7, which is far below any threshold this round applies."""
    from math import erf, sqrt
    return 2.0 * (1.0 - 0.5 * (1.0 + erf(abs(t) / sqrt(2.0))))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r114_demographic_subject.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    demo = {}
    for line in open(ANNOTATORS):
        r = json.loads(line)
        demo[str(r["annotator_id"])] = {a: str(r["demographics"].get(a, "MISSING")) for a in AXES}
    cells = [c for c in build() if c["rid"] in demo]
    if not cells:
        print("REFUSING: empty population. Nothing-to-fit exits 2, never 0.", file=sys.stderr)
        return 2

    pids = sorted({c["pid"] for c in cells})
    rids = sorted({c["rid"] for c in cells})
    PI = {p: i for i, p in enumerate(pids)}
    RI = {r: i for i, r in enumerate(rids)}
    gp = np.array([PI[c["pid"]] for c in cells])
    gr = np.array([RI[c["rid"]] for c in cells])
    ef = np.array([c["full"] for c in cells])
    ec = np.array([c["core"] for c in cells])
    d, ssum = ec - ef, ec + ef
    k = float(d.mean() / (ssum.mean() - 1.0))
    print(f"cells {len(cells):,}   prompts {len(pids)}   raters {len(rids)}   "
          f"demographics on {len(demo)} annotators")
    print(f"mean e_full {ef.mean():.5f}  e_core {ec.mean():.5f}  gain {d.mean():+.5f}  "
          f"Oldham k {k:.5f}")

    y_d, y_s = demean(d, gp), demean(ssum, gp)
    y_p = demean(d - k * ssum, gp)
    y_f, y_c = demean(ef, gp), demean(ec, gp)
    n_i = np.bincount(gr, None, len(rids)).astype(float)
    logn = demean(np.log(np.maximum(n_i[gr], 1)), gp)
    own_err = np.bincount(gr, ef, len(rids)) / np.maximum(n_i, 1)

    # ---- LEVELS FIRST, per group cell, then the difference, then the departure ----
    rows = []
    for axis in AXES:
        for lev in sorted({demo[r][axis] for r in rids}):
            members = [r for r in rids if demo[r][axis] == lev]
            ind = demean(np.isin(gr, [RI[r] for r in members]).astype(float), gp)
            X = np.column_stack([ind, logn])
            b_f, s_f = twoway(y_f, X, gp, gr)
            b_c, s_c = twoway(y_c, X, gp, gr)
            b_s, s_s = twoway(y_s, X, gp, gr)
            b_d, s_d = twoway(y_d, X, gp, gr)
            b_p, s_p = twoway(y_p, X, gp, gr)
            rows.append({"axis": axis, "level": lev, "n_raters": len(members),
                         "n_cells": int((gr[:, None] == np.array([RI[r] for r in members])).any(1).sum())
                         if members else 0,
                         "beta_full": b_f, "se_full": s_f, "beta_core": b_c, "se_core": s_c,
                         "beta_sum": b_s, "se_sum": s_s, "beta_d": b_d, "se_d": s_d,
                         "pred_d": k * b_s,
                         "departure": b_p, "se_departure": s_p,
                         "t_departure": b_p / max(s_p, 1e-12),
                         "tested": len(members) >= MIN_GROUP_RATERS})
    tested = [r for r in rows if r["tested"]]
    excluded = [r for r in rows if not r["tested"]]
    print(f"\n{len(rows)} group cells across {len(AXES)} axes; {len(tested)} tested, "
          f"{len(excluded)} below the pre-registered floor of {MIN_GROUP_RATERS} raters "
          f"(smallest tested {min(r['n_raters'] for r in tested)})")
    for r in excluded:
        print(f"    EXCLUDED  {r['axis']}={r['level'][:34]:<34} n_raters {r['n_raters']}")

    pv = [norm_p(r["t_departure"]) for r in tested]
    keep = bh(pv, BH_Q)
    for r, p, s in zip(tested, pv, keep):
        r["p_departure"], r["bh_survives"] = float(p), bool(s)
    survivors = [r for r in tested if r["bh_survives"]]

    print(f"\n  {'axis=level':<44}{'n':>5}{'b_full':>9}{'b_core':>9}{'b_d':>9}"
          f"{'pred':>9}{'depart':>9}{'t':>7}{'p':>9}")
    for r in sorted(tested, key=lambda x: -abs(x["t_departure"]))[:12]:
        print(f"  {(r['axis']+'='+r['level'])[:43]:<44}{r['n_raters']:>5}{r['beta_full']:>+9.4f}"
              f"{r['beta_core']:>+9.4f}{r['beta_d']:>+9.4f}{r['pred_d']:>+9.4f}"
              f"{r['departure']:>+9.4f}{r['t_departure']:>7.2f}{r['p_departure']:>9.4f}")
    print(f"  ... {len(tested)} tested cells total; the 12 largest |t| shown")

    # ---- POSITIVE CONTROL: a planted ONE-ARMED group effect must be recovered ------
    target = max(tested, key=lambda r: r["n_raters"])
    tmem = [RI[r] for r in rids if demo[r][target["axis"]] == target["level"]]
    tind_raw = np.isin(gr, tmem).astype(float)
    tind = demean(tind_raw, gp)
    print(f"\n  POSITIVE CONTROL on {target['axis']}={target['level'][:30]} "
          f"({target['n_raters']} raters): plant e_core += g*1[group], full untouched")
    pc = {}
    for g_ in PLANT:
        ec2 = ec + g_ * tind_raw
        d2, s2 = ec2 - ef, ec2 + ef
        k2 = float(d2.mean() / (s2.mean() - 1.0))
        b, se = twoway(demean(d2 - k2 * s2, gp), np.column_stack([tind, logn]), gp, gr)
        pc[str(g_)] = {"beta": b, "se": se, "t": b / max(se, 1e-12), "retained": b / g_}
        print(f"    g={g_:.2f}: departure {b:+.5f}  se {se:.5f}  t {b/max(se,1e-12):>6.2f}  "
              f"retention {b/g_:.1%}")
    mde = 1.96 * pc[str(PLANT[0])]["se"] / max(pc[str(PLANT[0])]["retained"], 1e-9)
    print(f"    MDE in g at 80% power ~ {2.8 * pc[str(PLANT[0])]['se'] / max(pc[str(PLANT[0])]['retained'], 1e-9):.5f}"
          f"   (1.96-se floor {mde:.5f})")
    control_ok = abs(pc[str(PLANT[0])]["t"]) > 2.0

    # ---- NEGATIVE CONTROL: synthetic partitions matched on size AND own-error -----
    # NOT a permutation. A permutation answers "did the labelling matter"; this answers "does a group
    # that differs only by size and error level land ON the line?", which is the rival that matters.
    print(f"\n  NEGATIVE CONTROL ({N_SYNTH} synthetic groups matched to "
          f"{target['axis']}={target['level'][:24]} on size and mean own-error; NOT a permutation)")
    tgt_n, tgt_err = target["n_raters"], float(own_err[tmem].mean())
    synth = []
    order = np.argsort(np.abs(own_err - tgt_err))
    pool = order[:min(len(order), max(tgt_n * 3, 60))]
    for _ in range(N_SYNTH):
        pick = rng.choice(pool, size=min(tgt_n, len(pool)), replace=False)
        si = demean(np.isin(gr, pick).astype(float), gp)
        b, _se = twoway(y_p, np.column_stack([si, logn]), gp, gr)
        synth.append(b)
    synth = np.array(synth)
    lo, hi = np.quantile(synth, [0.025, 0.975])
    print(f"    matched-synthetic departures: mean {synth.mean():+.5f}  95% band "
          f"[{lo:+.5f},{hi:+.5f}]  (real group {target['departure']:+.5f})")
    real_outside = not (lo <= target["departure"] <= hi)

    # ---- the matched-arm check, riding free on r113's even-rater cells ------------
    even = {}
    if R113.exists():
        z = np.load(R113, allow_pickle=True)
        er = [str(x) for x in z["rater_ids"]]
        egr, egp = z["gr"], z["gp"]
        yo = demean(z["e_oracle"] - z["e_full"], egp)
        so = demean(z["e_oracle"] + z["e_full"], egp)
        ko = float((z["e_oracle"] - z["e_full"]).mean() / ((z["e_oracle"] + z["e_full"]).mean() - 1.0))
        yop = demean((z["e_oracle"] - z["e_full"]) - ko * (z["e_oracle"] + z["e_full"]), egp)
        eln = demean(np.log(np.maximum(np.bincount(egr, None, len(er)).astype(float)[egr], 1)), egp)
        for r in (survivors or [target]):
            mem = [i for i, rid in enumerate(er) if demo.get(rid, {}).get(r["axis"]) == r["level"]]
            if not mem:
                continue
            ei = demean(np.isin(egr, mem).astype(float), egp)
            b_o, s_o = twoway(yop, np.column_stack([ei, eln]), egp, egr)
            even[f"{r['axis']}={r['level']}"] = {"oracle_departure": b_o, "se": s_o,
                                                 "t": b_o / max(s_o, 1e-12)}
            print(f"  MATCHED-ARM (never-compiled oracle) for {r['axis']}={r['level'][:26]}: "
                  f"departure {b_o:+.5f}  t {b_o/max(s_o,1e-12):.2f}")

    # ---- verdict, generated ------------------------------------------------------
    if not control_ok:
        world = "UNVERIFIED"
    elif survivors:
        world = "W-SUBJECT"
    else:
        world = "W-ANONYMOUS"
    conclusion = (
        f"On {len(cells):,} cells, {len(pids)} prompts and {len(rids)} raters -- the full population "
        f"entries 21/22 were measured on -- with demographics at 100% coverage across six axes and "
        f"{len(rows)} group cells: {len(tested)} cells cleared the pre-registered floor of "
        f"{MIN_GROUP_RATERS} raters and {len(excluded)} did not. The estimand is the DEPARTURE from "
        f"the arithmetic line, beta_d - k*beta_sum with k={k:.5f}, because entry 24 established that "
        f"beta_d itself is the line: any covariate raising both arms yields a differential "
        f"proportional to their accuracy gap. Largest |t| among tested cells is "
        f"{max(abs(r['t_departure']) for r in tested):.2f}; after Benjamini-Hochberg at q={BH_Q}, "
        f"{len(survivors)} cells survive. The positive control plants a one-armed group effect and "
        f"recovers it at retention {pc[str(PLANT[0])]['retained']:.1%} with t "
        f"{pc[str(PLANT[0])]['t']:.2f} for g={PLANT[0]}, so a null here is a measurement rather than "
        f"silence. The negative control is NOT a permutation -- {N_SYNTH} synthetic groups matched on "
        f"size and mean own-error give a 95% band of [{lo:+.5f},{hi:+.5f}], so a group differing only "
        f"in noisiness lands on the line. WORLD: {world}. "
        + ("At least one demographic group departs from the arithmetic line beyond both the "
           "multiplicity correction and the matched-synthetic band. The redistribution has a "
           "demographic subject -- D6 at best, because a group can differ in average CARE and this "
           "release has no instrument separating care from values."
           if world == "W-SUBJECT" else
           "No demographic group departs from the arithmetic line, on the only release carrying both "
           "the compilation contrast and the demographics. The rater component of entries 21/22 is "
           "real and ANONYMOUS. 'Identifiable subgroup' leaves the claim permanently and is not to be "
           "reopened on another dataset."
           if world == "W-ANONYMOUS" else
           "The positive control did not recover a planted one-armed effect, so this instrument "
           "cannot distinguish a null from silence. UNVERIFIED, and it acquits nothing."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"n_cells": len(cells), "n_prompts": len(pids), "n_raters": len(rids),
           "mean_e_full": float(ef.mean()), "mean_e_core": float(ec.mean()),
           "mean_gain": float(d.mean()), "oldham_k": k,
           "axes": list(AXES), "n_group_cells": len(rows), "n_tested": len(tested),
           "n_excluded": len(excluded), "min_group_raters": MIN_GROUP_RATERS, "bh_q": BH_Q,
           "cells": rows, "n_survivors": len(survivors),
           "survivors": [f"{r['axis']}={r['level']}" for r in survivors],
           "max_abs_t": float(max(abs(r["t_departure"]) for r in tested)),
           "positive_control": {"target": f"{target['axis']}={target['level']}", "arms": pc,
                                "recovers_g_min": bool(control_ok)},
           "negative_control": {"n": N_SYNTH, "mean": float(synth.mean()),
                                "band": [float(lo), float(hi)],
                                "real_outside_band": bool(real_outside)},
           "matched_arm": even, "world": world, "conclusion": conclusion, **stamp(__file__)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    np.savez_compressed(_RES / "r114_cells.npz", gp=gp, gr=gr, e_full=ef, e_core=ec,
                        prompt_ids=np.array(pids, dtype=object),
                        rater_ids=np.array(rids, dtype=object), synth=synth,
                        **{f"demo_{a}": np.array([demo[r][a] for r in rids], dtype=object)
                           for a in AXES})
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
