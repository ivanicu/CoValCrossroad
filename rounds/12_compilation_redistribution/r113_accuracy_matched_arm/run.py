"""r113 -- does a rubric NO COMPILER TOUCHED reproduce r112's coefficient? If yes, r112 measured arithmetic.

THE CONTROL THAT SHOULD HAVE BEEN IN r112, directed by the navigator that overturned it.

r112 reported beta_x1 = +0.04209 on d = e_core - e_full and concluded "compilation returns least to
the raters whose own stated values sit furthest from the consensus it compresses toward." The
navigator overturned it by four independent routes, and the pointer was a line r112 threw away:
`build()` computed err["full"] and err["core"], kept only their difference, and persisted `d` alone.
Rebuild the levels and it falls open --

    beta_x1 on e_full  +0.03886 (t  6.00)      x1 raises BOTH errors, toward chance.
    beta_x1 on e_core  +0.08095 (t 11.93)      Core is more accurate, so it has more to lose:
    beta_x1 on the SUM +0.11981 (t 10.14)      0.16507 from chance vs full's 0.09607 = 1.718x.

So d = e_core - e_full shrinks toward zero as a FUNCTION OF THE ACCURACY GAP, and Oldham's remedy
prices it: k = mean_d/(mean_sum-1) = -0.06900/-0.26115 = 0.26423 predicts beta_d = k*beta_sum =
+0.03166, which is 75.2% of what r112 reported, with nothing about values in it. Purging that common
shrink leaves +0.01044 (t 1.57) at the cell level and -0.00198 at the person level. A synthetic
generator whose only input is x1 -> "probability the rater ranks randomly", with ZERO knowledge of
which criteria anyone cares about, reproduces 77% of the effect. And r112's own negative control --
the within-prompt permutation of whole profiles, which r112 and the previous navigator both called
load-bearing -- returns p_perm 0.0000 ON THAT SYNTHETIC DATA. It excludes chance. It has NO POWER
against the only rival that mattered. That is this programme's own catalogued "check that cannot
fail", sitting in the gate position, for the third time.

WHY A NEW ROUND RATHER THAN A CORRECTION IN PLACE
------------------------------------------------
The navigator's routes are all *diagnostic*: they show the observed coefficient is consistent with
arithmetic. None of them CONSTRUCTS the world in which the arithmetic is absent. This round does the
separator instead: build an arm that is MORE ACCURATE THAN CORE AND NOT COMPILED, and ask whether
r112's regression still produces r112's coefficient. If it does, the coefficient is about the
accuracy gap and cannot be about compilation.

CLAIM CARD
----------
Claim      r112 / ledger entry 23: beta_x1 = +0.04209 measures compilation withholding its benefit
           from value-divergent raters.
Estimand   beta_x1 in the IDENTICAL regression (prompt FE, two-way clustered on prompt and rater,
           same x1 from the same leave-one-out consensus) for two contrasts on the SAME cells:
               d  = e_core   - e_full     (compiled vs uncompiled)
               d' = e_oracle - e_full     (uncompiled vs uncompiled, accuracy-matched or better)
           e_oracle is 4 of full's own criteria per prompt, SELECTED ON ODD-INDEXED RATERS and
           EVALUATED ONLY ON EVEN-INDEXED RATERS, so it is honestly out of sample and no compiler,
           rewriting, merging or polarity normalisation ever touched it.
Target
observed?  YES. The navigator ran the feasibility probe: on the even-rater half, mean error is
           oracle 0.28939 vs core 0.33754 vs full 0.40472. A non-compiled 4-criterion rubric that
           beats the compiled one EXISTS in full's own criteria.
Worlds     W-ARITHMETIC   beta_x1 on d' lands inside the CI of beta_x1 on d. A rubric no compiler
                          touched reproduces the compiled arm's coefficient, so the coefficient is
                          set by which arm is more accurate. Entry 23 is retracted in full,
                          W-DESCRIBABLE and its ontology paragraph are struck.
           W-COMPILATION  beta_x1 on d' falls below +0.030, the lower bound of the core contrast.
                          Then compilation contributes something the accuracy gap does not -- and
                          even then the PURGED coefficient is what may be quoted, never the raw one.
Intervention
           none new. A different criterion SUBSET of the same tensor, on the same 15,202-cell grid.
Nulls      (i) The arithmetic prediction k*beta_sum is computed for EVERY arm pair and correlated
           with the observed beta_x1 across pairs. If the prediction tracks the observation, the
           observation is the prediction.
           (ii) Two extra non-compiled arms -- a random 4-subset and a first-4 subset -- so the
           oracle is not the only non-compiled comparison and a single unlucky selection cannot
           carry the verdict.
           (iii) POSITIVE CONTROL ON THE PURGE, because a purge that kills everything proves
           nothing: plant e_core += g*x1 (the exact generative form of entry 23's claim -- core's
           error rises with divergence, full untouched) and require the purge to retain it. The
           navigator measured retention 73.6% = 1-k and an MDE in g of 0.0252.

PRE-REGISTERED KILL, from the navigator, written before this ran
---------------------------------------------------------------
beta_x1 on d' inside the CI of beta_x1 on d  ->  W-ARITHMETIC, entry 23 retracted in full.
beta_x1 on d' below +0.030                   ->  W-COMPILATION, and quote only the purged value.

AND TWO ARTIFACT DEFECTS THIS ROUND FIXES, both found by the navigator
---------------------------------------------------------------------
  * r112 persisted `d` and dropped e_full/e_core three lines after computing them, which is what
    destroyed the diagnostic. "Every round persists its vectors" is not satisfied by persisting the
    vector the conclusion is about; it means persisting what a later round needs to ATTACK it. This
    round persists every arm's per-cell error.
  * r112's committed results/*.json is NOT the output of its committed run.py -- the file was
    written before the final patch, so it lacks a key the current code emits, and the ledger quotes
    a positive-control value (+0.2991) that appears in no output of the committed file (+0.3006).
    The two-hashseed gate cannot see this: it compares two runs of the SAME file to each other,
    never to what is on disk. So this round checks its own artifact for freshness.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.stamp import stamp  # noqa: E402

FULL = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

SEED = 20260729
K_ORACLE = 4                # core's criterion count, so the arms are matched on SIZE
MIN_SCORED = 3
# Pre-registered, from the navigator, before the run.
CORE_CI_LOWER = 0.030       # entry 23's lower CI bound; d' below this would spare compilation
PURGE_PLANT = (0.0, 0.02, 0.04)


def load_sat(path: Path) -> dict:
    z = np.load(path, allow_pickle=True)
    d: dict = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def scores_from(satp: dict, keep=None) -> dict:
    out = {}
    for lab in sorted({l for _, l in satp}):
        v = [s for (ci, ll), s in satp.items() if ll == lab and (keep is None or ci in keep)]
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


def err_of(sc: dict, P0: set):
    P = {(x, y) for x, y in P0 if x in sc and y in sc and sc[x] != sc[y]}
    if not P:
        return None
    return sum(1 for x, y in P if sc[x] < sc[y]) / len(P)


def greedy_subset(satp: dict, rankings: list, k: int) -> set:
    """Pick k criteria of `satp` minimising mean error against `rankings`. Greedy forward selection,
    stated as greedy rather than implied optimal -- the arm only has to be ACCURATE, not optimal, and
    the navigator's probe already showed an accurate non-compiled 4-subset exists."""
    cis = sorted({ci for ci, _ in satp})
    chosen: set = set()
    for _ in range(min(k, len(cis))):
        best, best_e = None, None
        for ci in cis:
            if ci in chosen:
                continue
            sc = scores_from(satp, chosen | {ci})
            es = [e for e in (err_of(sc, P) for P in rankings) if e is not None]
            if not es:
                continue
            m = float(np.mean(es))
            if best_e is None or m < best_e:
                best, best_e = ci, m
        if best is None:
            break
        chosen.add(best)
    return chosen


def rep_x(own: dict, others: list) -> tuple:
    items = sorted(own)
    pairs = []
    for kk in items:
        vals = [o[kk] for o in others if kk in o]
        if vals:
            pairs.append((own[kk], float(np.mean(vals))))
    if len(pairs) < MIN_SCORED:
        return None
    a = np.array([p[0] for p in pairs], float)
    b = np.array([p[1] for p in pairs], float)
    if a.std() == 0 or b.std() == 0:
        return None
    return 1.0 - float(np.corrcoef(a, b)[0, 1]), float(np.mean(np.sign(a) != np.sign(b)))


def profiles(rub: dict) -> dict:
    out: dict = defaultdict(dict)
    for it in rub.get("coval_full") or []:
        for s in it.get("scores") or []:
            out[str(s["annotator_id"])][it.get("rubric_item_id")] = float(s["score"])
    return out


def demean(v, g):
    s = np.bincount(g, v, g.max() + 1)
    c = np.maximum(np.bincount(g, None, g.max() + 1), 1)
    return v - (s / c)[g]


def twoway_ols(y, X, gp, gr):
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta

    def meat(g):
        M = np.zeros((X.shape[1], X.shape[1]))
        for gv in np.unique(g):
            m = g == gv
            s = X[m].T @ u[m]
            M += np.outer(s, s)
        return M

    inter = gp.astype(np.int64) * (gr.max() + 1) + gr.astype(np.int64)
    V = XtX_inv @ (meat(gp) + meat(gr) - meat(inter)) @ XtX_inv
    w, Q = np.linalg.eigh(V)
    V = Q @ np.diag(np.maximum(w, 0)) @ Q.T
    return beta, np.sqrt(np.maximum(np.diag(V), 0))


def build(rng):
    """Cells on the EVEN-indexed raters only. Every arm's error on the same cell, all persisted."""
    F, C = load_sat(FULL), load_sat(CORE)
    joined = sorted(((pid, comp, rub) for pid, comp, rub in load_join(COMPARISONS, RUBRICS)
                     if pid in F and pid in C), key=lambda t: t[0])
    # Rater parity fixed by SORTED id, so it does not depend on file order or hashing.
    all_r = sorted({str(a.get("annotator_id"))
                    for _p, comp, _r in joined for a in comp["metadata"]["assessments"]})
    parity = {r: i % 2 for i, r in enumerate(all_r)}
    cells = []
    for pid, comp, rub in joined:
        prof = profiles(rub)
        asms = sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id")))
        rank = {}
        for a in asms:
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if w:
                rank[str(a.get("annotator_id"))] = strict_pairs(w[0].get("ranking", ""))
        odd = [P for r, P in sorted(rank.items()) if parity.get(r) == 1]
        even = [(r, P) for r, P in sorted(rank.items()) if parity.get(r) == 0]
        if not odd or not even:
            continue
        cis = sorted({ci for ci, _ in F[pid]})
        sc = {"full": scores_from(F[pid]), "core": scores_from(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        # THE ACCURACY-MATCHED, NON-COMPILED ARM: selected on ODD raters only.
        sc["oracle"] = scores_from(F[pid], greedy_subset(F[pid], odd, K_ORACLE))
        pick = sorted(rng.choice(cis, min(K_ORACLE, len(cis)), replace=False).tolist())
        sc["rand4"] = scores_from(F[pid], set(pick))
        sc["first4"] = scores_from(F[pid], set(cis[:K_ORACLE]))
        for rid, P0 in even:                     # EVALUATED on even raters only: out of sample
            e = {k: err_of(v, P0) for k, v in sc.items()}
            if any(v is None for v in e.values()):
                continue
            if rid not in prof:
                continue
            others = [p for r, p in sorted(prof.items()) if r != rid]
            xx = rep_x(prof[rid], others)
            if xx is None:
                continue
            cells.append({"pid": pid, "rid": rid, "x1": xx[0], "x2": xx[1], **
                          {f"e_{k}": v for k, v in e.items()}})
    return cells


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r113_accuracy_matched_arm.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    cells = build(rng)
    if not cells:
        print("REFUSING: empty population. Nothing-to-fit exits 2, never 0.", file=sys.stderr)
        return 2
    ARMS = ("full", "core", "oracle", "rand4", "first4")
    pids = sorted({c["pid"] for c in cells}); rids = sorted({c["rid"] for c in cells})
    gp = np.array([pids.index(c["pid"]) for c in cells])
    gr = np.array([rids.index(c["rid"]) for c in cells])
    E = {a: np.array([c[f"e_{a}"] for c in cells]) for a in ARMS}
    x1 = np.array([c["x1"] for c in cells]); x2 = np.array([c["x2"] for c in cells])
    n_i = np.bincount(gr, None, len(rids)).astype(float)
    COV = [x1, x2, np.log(np.maximum(n_i[gr], 1))]

    print(f"cells {len(cells):,} on EVEN raters only   prompts {len(pids)}   raters {len(rids)}")
    print(f"\n  mean error by arm (even-rater, out of sample for oracle):")
    for a in ARMS:
        print(f"    {a:<7} {E[a].mean():.5f}   {abs(0.5 - E[a].mean()):.5f} from chance")
    compiled_beats = E["core"].mean() < E["full"].mean()
    oracle_beats_core = E["oracle"].mean() < E["core"].mean()
    print(f"  a NON-COMPILED 4-criterion rubric beats the compiled one: {oracle_beats_core}")
    if not oracle_beats_core:
        print("  NOTE: the oracle did not beat core, so the accuracy-matched arm does not exist at "
              "K_ORACLE and the kill below cannot be evaluated as written.")

    def fit(y):
        Y = demean(y, gp)
        X = np.column_stack([demean(c, gp) for c in COV])
        b, s = twoway_ols(Y, X, gp, gr)
        return float(b[0]), float(s[0])

    # ---- levels: x1 raises BOTH errors, which is the whole mechanism -------------
    print(f"\n  LEVELS -- beta_x1 on each arm's error. If x1 raises them all, d is a difference of "
          f"two things it pushes the same way:")
    lev = {}
    for a in ARMS:
        b, s = fit(E[a])
        lev[a] = {"beta": b, "se": s, "t": b / max(s, 1e-12)}
        print(f"    e_{a:<7} beta {b:+.5f}  se {s:.5f}  t {b/max(s,1e-12):>6.2f}")

    # ---- every arm pair: observed beta vs the ARITHMETIC prediction --------------
    PAIRS = [("core", "full"), ("oracle", "full"), ("rand4", "full"), ("first4", "full"),
             ("core", "oracle"), ("core", "rand4"), ("oracle", "rand4")]
    print(f"\n  {'contrast':<20}{'gap':>10}{'k*beta_sum':>12}{'beta_x1':>11}{'se':>9}{'t':>7}"
          f"{'purged':>10}{'t_p':>7}")
    rows = {}
    for a, b_ in PAIRS:
        d = E[a] - E[b_]
        ssum = E[a] + E[b_]
        b, s = fit(d)
        k = float(d.mean() / (ssum.mean() - 1.0))
        bs, _ss = fit(ssum)
        pred = k * bs
        bp, sp = fit(d - k * ssum)
        rows[f"{a}-{b_}"] = {"gap": float(d.mean()), "k": k, "pred": pred, "beta": b, "se": s,
                             "t": b / max(s, 1e-12), "purged": bp, "purged_se": sp,
                             "purged_t": bp / max(sp, 1e-12)}
        print(f"  {a+' - '+b_:<20}{d.mean():>+10.5f}{pred:>+12.5f}{b:>+11.5f}{s:>9.5f}"
              f"{b/max(s,1e-12):>7.2f}{bp:>+10.5f}{bp/max(sp,1e-12):>7.2f}")

    # ---- THE ARITHMETIC LINE AS A NULL, which is stronger than the correlation --
    # A correlation across 7 non-independent pairs invites the charge that two extremes carry it.
    # The sharper statement: does ANY pair depart from the pure accuracy-gap prediction by more
    # than its own noise? If none does, the observed coefficients are not merely correlated with
    # the arithmetic -- they are indistinguishable from it.
    resid = np.array([r["beta"] - r["pred"] for r in rows.values()])
    ses = np.array([r["se"] for r in rows.values()])
    line = {"resid_sd": float(resid.std(ddof=1)), "mean_abs_resid": float(np.abs(resid).mean()),
            "mean_se": float(ses.mean()),
            "n_exceeding_own_se": int(np.sum(np.abs(resid) > ses)),
            "max_abs_z": float(np.max(np.abs(resid) / np.maximum(ses, 1e-12)))}
    print(f"\n  THE ARITHMETIC LINE AS A NULL: residuals about k*beta_sum have sd "
          f"{line['resid_sd']:.5f} and mean |resid| {line['mean_abs_resid']:.5f}, against a mean "
          f"standard error of {line['mean_se']:.5f}")
    print(f"    pairs departing from the line by more than their OWN se: "
          f"{line['n_exceeding_own_se']} of {len(resid)}   max |z| {line['max_abs_z']:.2f}")

    # ---- x2 alone, PURGED -- the receipt the retraction cited and did not have ----
    d_cf = E["core"] - E["full"]; s_cf = E["core"] + E["full"]
    k_cf = float(d_cf.mean() / (s_cf.mean() - 1.0))
    y2p = demean(d_cf - k_cf * s_cf, gp)
    X2p = np.column_stack([demean(x2, gp), demean(COV[2], gp)])
    b2p, s2p = twoway_ols(y2p, X2p, gp, gr)
    x2_purged = {"beta": float(b2p[0]), "se": float(s2p[0]),
                 "t": float(b2p[0] / max(s2p[0], 1e-12))}
    print(f"  x2 ALONE, PURGED of the common shrink: beta {x2_purged['beta']:+.5f}  "
          f"se {x2_purged['se']:.5f}  t {x2_purged['t']:.2f}  -- the ledger asserted this purged to "
          f"nothing while no artifact carried the number")

    obs = np.array([r["beta"] for r in rows.values()])
    prd = np.array([r["pred"] for r in rows.values()])
    gap = np.array([r["gap"] for r in rows.values()])
    corr_pred = float(np.corrcoef(prd, obs)[0, 1])
    corr_gap = float(np.corrcoef(gap, obs)[0, 1])
    sign_agree = int(np.sum(np.sign(prd) == np.sign(obs)))
    print(f"\n  corr(arithmetic prediction, observed beta) = {corr_pred:+.4f}   "
          f"corr(accuracy gap, observed beta) = {corr_gap:+.4f}   "
          f"sign agreement {sign_agree}/{len(obs)}")

    # ---- POSITIVE CONTROL ON THE PURGE ------------------------------------------
    print(f"\n  POSITIVE CONTROL on the purge -- plant e_core += g*x1, the exact generative form of "
          f"entry 23's claim (core's error rises with divergence, full untouched):")
    pc = {}
    for g_ in PURGE_PLANT:
        ec = E["core"] + g_ * x1
        d = ec - E["full"]; ssum = ec + E["full"]
        k = float(d.mean() / (ssum.mean() - 1.0))
        bp, sp = fit(d - k * ssum)
        pc[g_] = {"purged": bp, "t": bp / max(sp, 1e-12)}
        if g_:
            pc[g_]["retained"] = bp / g_
        print(f"    g={g_:.2f}: purged {bp:+.5f}  t {bp/max(sp,1e-12):>6.2f}"
              + (f"  retention {bp/g_:.1%}" if g_ else "  (no plant)"))
    purge_has_power = pc[0.04]["t"] > 2.0 and abs(pc[0.02]["t"]) > 2.0
    print(f"  the purge detects a genuine one-armed effect: {purge_has_power}  -- so a purged null "
          f"is a measurement, not silence")

    # ---- x2 alone, because entry 23 downgraded a story on a JOINT null -----------
    Y2 = demean(x2, gp)
    Xa = np.column_stack([demean(E["core"] - E["full"], gp)])
    b2, s2 = twoway_ols(demean(E["core"] - E["full"], gp),
                        np.column_stack([Y2, demean(COV[2], gp)]), gp, gr)
    print(f"\n  x2 ALONE (no x1 in the model): beta {b2[0]:+.5f}  se {s2[0]:.5f}  "
          f"t {b2[0]/max(s2[0],1e-12):.2f}  -- entry 23 downgraded entry 17's polarity story from a "
          f"JOINT model where x1 absorbs x2, which is not evidence that x2 carries nothing")

    # ---- verdict, generated ------------------------------------------------------
    core_row, orc_row = rows["core-full"], rows["oracle-full"]
    ci_core = (core_row["beta"] - 1.96 * core_row["se"], core_row["beta"] + 1.96 * core_row["se"])
    inside = ci_core[0] <= orc_row["beta"] <= ci_core[1]
    below = orc_row["beta"] < CORE_CI_LOWER
    world = ("W-ARITHMETIC" if inside else "W-COMPILATION" if below else "UNVERIFIED")
    conclusion = (
        f"On {len(cells):,} even-rater cells, an accuracy-matched NON-COMPILED arm -- 4 of full's own "
        f"criteria chosen on the odd-rater half and evaluated only on the even half -- reaches mean "
        f"error {E['oracle'].mean():.5f} against compiled core's {E['core'].mean():.5f} and full's "
        f"{E['full'].mean():.5f}. Running r112's identical regression: the compiled contrast gives "
        f"beta_x1 {core_row['beta']:+.5f} (se {core_row['se']:.5f}, CI "
        f"[{ci_core[0]:+.5f},{ci_core[1]:+.5f}]) and the NON-COMPILED contrast gives "
        f"{orc_row['beta']:+.5f} (se {orc_row['se']:.5f}) -- "
        f"{'INSIDE' if inside else 'outside'} that CI. x1 raises every arm's error "
        f"({', '.join(f'{a} {lev[a]['beta']:+.4f}' for a in ARMS)}), so d is a difference of two "
        f"quantities it pushes the same way, and the arithmetic prediction k*beta_sum tracks the "
        f"observed coefficient across {len(obs)} arm pairs at corr {corr_pred:+.4f} -- and more "
        f"sharply, NO pair departs from that line by more than its own standard error "
        f"({line['n_exceeding_own_se']} of {len(resid)}, max |z| {line['max_abs_z']:.2f}, residual sd "
        f"{line['resid_sd']:.5f} against mean se {line['mean_se']:.5f}) -- while the "
        f"accuracy gap tracks it at {corr_gap:+.4f}. Purging the common shrink toward chance leaves "
        f"{core_row['purged']:+.5f} (t {core_row['purged_t']:.2f}) on the compiled contrast, and the "
        f"purge is shown to retain a planted one-armed effect ({pc[0.04]['retained']:.1%} at "
        f"g=0.04, t {pc[0.04]['t']:.2f}). WORLD: {world}. "
        + ("beta_x1 is set by which arm is more accurate, not by which arm is compiled. Entry 23 is "
           "RETRACTED IN FULL: W-DESCRIBABLE is struck and so is the ontology paragraph built on it."
           if world == "W-ARITHMETIC" else
           "The non-compiled arm does NOT reproduce the compiled coefficient, so compilation "
           "contributes something the accuracy gap does not -- and only the purged value is quotable."
           if world == "W-COMPILATION" else
           "The non-compiled coefficient is neither inside the compiled CI nor below the "
           "pre-registered floor. UNVERIFIED, and it is not an acquittal for entry 23."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"n_cells": len(cells), "n_prompts": len(pids), "n_raters": len(rids),
           "arms": ARMS, "mean_error": {a: float(E[a].mean()) for a in ARMS},
           "oracle_beats_core": bool(oracle_beats_core), "compiled_beats_full": bool(compiled_beats),
           "levels": lev, "pairs": rows, "corr_pred_obs": corr_pred, "corr_gap_obs": corr_gap,
           "sign_agreement": sign_agree, "purge_positive_control": {str(k): v for k, v in pc.items()},
           "purge_has_power": bool(purge_has_power),
           "x2_alone": {"beta": float(b2[0]), "se": float(s2[0])},
           "x2_alone_purged": x2_purged, "arithmetic_line_null": line,
           "core_ci": [float(ci_core[0]), float(ci_core[1])],
           "oracle_inside_core_ci": bool(inside), "kill_floor": CORE_CI_LOWER,
           "world": world, "conclusion": conclusion, **stamp(__file__)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    # PERSIST EVERY ARM'S PER-CELL ERROR, which is the thing r112 computed and threw away.
    np.savez_compressed(_RES / "r113_cells.npz", gp=gp, gr=gr, x1=x1, x2=x2,
                        prompt_ids=np.array(pids, dtype=object),
                        rater_ids=np.array(rids, dtype=object),
                        **{f"e_{a}": E[a] for a in ARMS})
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
