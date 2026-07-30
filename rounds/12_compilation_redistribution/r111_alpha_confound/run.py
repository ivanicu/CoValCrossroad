"""r111 -- is entry 21's rater component a property of PEOPLE, or of WHICH PROMPTS they were asked?

Entry 21 measured a real thing: var_rater rises 0.00422 -> 0.00626 under compilation, CI over
prompts [+0.00133,+0.00302], and the granularity control cleared it. Then it wrote a sentence:
"particular raters are systematically worse served by the compiled rule." The measurement supports
"there is rater-attached structure". The SENTENCE claims that structure is a property of the person.

A rater is not randomly assigned to prompts in the sense that matters here: each rater sees a
particular handful, and CoVal records, per assessment, how likely that rater would have asked a
question like this themselves. If the raters with large alpha are the ones rating prompts far
outside their own usage, then "worse served" is a fact about EXPOSURE, not about people, and the
subgroup reading -- which is the whole reason this programme cares -- does not follow.

WHY THIS COVARIATE AND NOT THE ONES THE LEDGER'S NEXT NAMED
-----------------------------------------------------------
The ledger's NEXT said: rank raters by alpha and test coherence on subjectivity,
representativeness and importance. Two of those three turned out to be the wrong instrument, and
finding that out cost one preflight:

  * `representativeness` is NOT a self-report of being representative of other people. Read in
    full it is "It is <X> likely that I would ask a question like this to an AI chatbot." It is
    PROMPT TYPICALITY FOR THAT RATER. So it is not a description of a subgroup -- it is the rival
    explanation for alpha, which makes it far more useful than the coherence test intended.
  * `subjectivity` has FOUR levels, not three, and the two largest are "depends on a person's
    values or culture" (8,650) and "depends on something else (the time, the weather, etc)"
    (1,551). Reading it as one bucket merges normative disagreement with factual indexicality --
    the programme's object with its opposite. It is NOMINAL, not ordinal: "depends on something
    else" is not MORE subjective than "depends on values".
  * Per-level crossed decomposition over 18,384 assessments and 1,078 prompts (run in preflight()
    below, so the numbers are in this round's own output and not quoted from elsewhere):
    the two subjectivity levels that carry the programme's object are PROMPT-driven (19.4% and
    21.1% prompt versus 16.1% and 15.8% rater), while representativeness is RATER-driven
    (7.8% prompt versus 32.6% rater on its top level). So a coherence test on subjectivity would
    substantially have measured WHICH PROMPTS A RATER SAW, and reported it as a property of people.

  The defect that produced the wrong NEXT: I printed those levels truncated to 28 characters to
  make a counter legible, then read the truncated output as the data. One truncation hid
  representativeness's meaning AND collapsed subjectivity's two decisive levels into one bucket.

CLAIM CARD
----------
Claim      Entry 21: "particular raters are systematically worse served by the compiled rule."
Estimand   Delta_var_rater AFTER removing the part of alpha_i predictable from rater-level
           exposure covariates, versus the raw +0.00204.
Target
observed?  YES. representativeness is on every assessment, and prompt composition is computable
           per rater from the same records. Nothing here needs a new subject or a demographic.
Worlds     W1 SUBGROUP   alpha survives conditioning on exposure. Entry 21's sentence stands, and
                         the compiled rubric has losers who are losers independent of what they
                         were asked.
           W2 EXPOSURE   alpha is largely prompt-familiarity and composition. The variance rise is
                         real but the sentence is wrong: it is about which prompts, not which
                         people, and entry 21 must be rewritten.
Intervention
           none. Rater-level covariates on the same 15,202 cells per arm.
Nulls      (i) POSITIVE CONTROL for the residualizer: plant an alpha proportional to rater-mean
           representativeness and require the residualizer to remove it. Without this, "residualizing
           changed nothing" is silence from an instrument never shown to remove anything.
           (ii) COMPLEMENTARY CONTROL, the load-bearing one: residualize on PERMUTED covariates --
           rater rows shuffled, marginal distribution preserved exactly. Regressing a 1,012-vector
           on 3 columns removes variance by arithmetic alone; the permuted fit is that floor.
           (iii) The within-prompt rater-identity shuffle floor from r110, recomputed here.

PRE-REGISTERED KILL, written before the run
-------------------------------------------
If residualizing on exposure removes >= 50% of Delta_var_rater (+0.00204 -> <= +0.00102) while the
PERMUTED control removes < 10%, world W2 wins: entry 21's subgroup sentence is OVERTURNED and gets
rewritten as an exposure finding. If the real and permuted residualizations remove comparable
shares, the test is UNVERIFIED -- not an acquittal -- because the instrument could not distinguish
signal from arithmetic.

AND THE DIRECTION QUESTION, because var_rater is a MAGNITUDE
-----------------------------------------------------------
"Worse served" needs a sign, and entry 21 asserted one from a magnitude.

  ⛔ MY FIRST ANSWER HERE WAS ALSO WRONG, and it is retracted in place rather than deleted.
  I reported "50.0% of raters have a larger alpha under core, so this is a symmetric widening --
  compilation creates better-served and worse-served raters in roughly equal number." That reads a
  RELATIVE quantity as an ABSOLUTE one. alpha is re-centred inside each arm every sweep
  (fit_crossed: `a -= a.mean()`), so alpha_i is a rater's position relative to THAT ARM'S mean --
  and the two arms' means are not the same: mu_core - mu_full is about -0.069. So a rater can rise
  in alpha while their absolute disagreement with the rubric FALLS. "Better served" and "worse
  served" are absolute claims and must be measured on absolute error.
  Found by the independent navigator, whose signed analysis is the method used below.

So direction is measured three ways, all on absolute error, none on centred alpha:
  (i) the mean shift itself;
  (ii) the share of raters whose OWN MEAN ERROR is higher under core, against a paired
       within-prompt identity-shuffle null for that share -- because a shuffle produces a nonzero
       share by sampling alone and the raw share would be read as harm;
  (iii) absolute error by percentile of alpha, so the claim "the badly-served get worse" is checked
       where it would have to be true.

FIXES r110's PERSISTENCE GAP: r110 persisted (prompt_index, rater_index, err) with no id map, so no
later round could join its vectors to any covariate -- which is exactly what "every round persists
its vectors so a later round can attack it" exists to prevent. This round persists the ids.
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402

FULL = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R110 = _ROOT / "rounds/12_compilation_redistribution/r110_rater_component/results/r110_cells.npz"

SEED = 20260729
N_BOOT, N_SHUFFLE, N_PERM = 2000, 200, 200
# Pre-registered thresholds. Both written before the run; neither tuned.
KILL_REMOVAL_SHARE = 0.50     # real residualization removing >= this much of Delta -> W2
PERM_CEILING_SHARE = 0.10     # ...and the permuted control must remove < this much
LEDGER_DELTA = 0.00204        # entry 21's raw Delta_var_rater, used as a rebuild control

VALUES_LEVEL = "The correct answer depends on a person's values or culture"
REP_ORDER = ["not at all likely", "slightly likely", "moderately likely",
             "very likely", "extremely likely"]


def nfkc(s) -> str:
    """CoVal writes its Likert words in mathematical sans-serif bold. Normalising is the robust
    move; hand-encoding the codepoints silently dropped a whole level of five on the first try."""
    return unicodedata.normalize("NFKC", str(s))


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


def rep_code(s: str):
    n = nfkc(s)
    hits = [i for i, w in enumerate(REP_ORDER) if w in n]
    if len(hits) != 1:
        return None          # ambiguous or absent -> caller refuses, never silently drops
    return hits[0]


# --------------------------------------------------------------------------- preflight

def preflight() -> dict:
    """Which of the three assessment fields is a RATER property and which is a PROMPT property.
    This decides which covariates are admissible, so it runs here rather than being cited."""
    recs, levels = [], defaultdict(set)
    for line in open(COMPARISONS):
        c = json.loads(line)
        for a in c["metadata"]["assessments"]:
            r = {"pid": c["prompt_id"], "rid": str(a["annotator_id"])}
            for f in ("subjectivity", "representativeness", "importance"):
                v = nfkc(a.get(f, ""))
                if v:
                    r[f] = v
                    levels[f].add(v)
            recs.append(r)
    print(f"preflight: {len(recs)} assessments, levels "
          f"{ {f: len(s) for f, s in sorted(levels.items())} }")
    out = {}
    for f in sorted(levels):
        for lev in sorted(levels[f]):
            sub = [r for r in recs if f in r]
            y = np.array([1.0 if r[f] == lev else 0.0 for r in sub])
            sp, sr = crossed_shares([r["pid"] for r in sub], [r["rid"] for r in sub], y)
            out[f"{f}::{lev}"] = {"n": int(y.sum()), "prompt_share": sp, "rater_share": sr}
            print(f"   {f[:12]:<12} {lev[:44]:<44} n={int(y.sum()):>5} "
                  f"prompt {sp:>6.1%}  rater {sr:>6.1%}  "
                  f"{'PROMPT' if sp > sr else 'RATER'}-driven")
    return out


def crossed_shares(pid, rid, y, niter=400):
    P = {p: i for i, p in enumerate(sorted(set(pid)))}
    R = {r: i for i, r in enumerate(sorted(set(rid)))}
    pi = np.array([P[p] for p in pid])
    ri = np.array([R[r] for r in rid])
    g, a, res = fit_crossed(pi, ri, np.asarray(y, float), len(P), len(R), niter)
    tot = g.var() + a.var() + res.var()
    return float(g.var() / tot), float(a.var() / tot)


# --------------------------------------------------------------------------- the fit

def fit_crossed(pi, ri, y, nP, nR, niter=200):
    """Alternating centering with alpha re-centred each sweep, matching r110 exactly. Converged:
    a sweep from 50 to 12,800 iterations moves the components by 0.0e+00 past 800, and 8.9e-08
    between 50 and 100 -- so the 0.00422-versus-0.00545 gap between r110 and this round is NOT
    convergence, it is two different estimands (see components())."""
    mu = y.mean()
    g = np.zeros(nP)
    a = np.zeros(nR)
    cP = np.maximum(np.bincount(pi, None, nP), 1)
    cR = np.maximum(np.bincount(ri, None, nR), 1)
    for _ in range(niter):
        g = np.bincount(pi, y - mu - a[ri], nP) / cP
        a = np.bincount(ri, y - mu - g[pi], nR) / cR
        a -= a.mean()
    return g, a, y - mu - g[pi] - a[ri]


def build() -> dict:
    """Mirrors r110's build EXACTLY -- same sorted orders, same filters -- but keeps the ids."""
    F, C = load_sat(FULL), load_sat(CORE)
    prompts, raters = {}, {}
    rows = {"full": [], "core": []}
    cov = defaultdict(lambda: {"rep": [], "values": [], "n": 0})
    joined = sorted(((pid, comp) for pid, comp, rub in load_join(COMPARISONS, RUBRICS)
                     if pid in F and pid in C), key=lambda t: t[0])
    for pid, comp in joined:
        sc = {"full": equal_weight_scores(F[pid]), "core": equal_weight_scores(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        pj = prompts.setdefault(pid, len(prompts))
        for a in sorted(comp["metadata"]["assessments"],
                        key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            P0 = strict_pairs(w[0].get("ranking", ""))
            rid = str(a.get("annotator_id"))
            ri = raters.setdefault(rid, len(raters))
            rc = rep_code(a.get("representativeness", ""))
            if rc is None:
                raise SystemExit("REFUSING: unmappable representativeness level -- a dropped "
                                 "level is a scope error, and it already happened once.")
            cov[rid]["rep"].append(rc)
            cov[rid]["values"].append(1.0 if nfkc(a.get("subjectivity", "")) == VALUES_LEVEL else 0.0)
            cov[rid]["n"] += 1
            for arm in ("full", "core"):
                s = sc[arm]
                P = {(x, y) for x, y in P0 if x in s and y in s and s[x] != s[y]}
                if not P:
                    continue
                rows[arm].append((pj, ri, sum(1 for x, y in P if s[x] < s[y]) / len(P)))
    inv = {v: k for k, v in raters.items()}
    X = np.array([[float(np.mean(cov[inv[i]]["rep"])),
                   float(np.mean(cov[inv[i]]["values"])),
                   float(np.log(cov[inv[i]]["n"]))] for i in range(len(raters))])
    return {"rows": {k: np.array(v, float) for k, v in rows.items()},
            "nP": len(prompts), "nR": len(raters), "X": X,
            "rater_ids": [inv[i] for i in range(len(raters))]}


def components(a: np.ndarray, cr: np.ndarray, var_resid: float) -> dict:
    """THREE estimands from the same fitted alphas, because entry 21 quoted one of them while
    making a claim about another, and neither is the variance COMPONENT.

      weighted    average alpha^2 weighted by cells -- variance PER OBSERVATION. What r110 quoted.
      unweighted  variance of alpha across PEOPLE, each rater once. What entry 21's sentence is
                  about ("particular raters are worse served").
      mom         unweighted minus var_resid * E[1/n_i] -- method of moments, because the variance
                  of fitted means is the component PLUS a sampling term. With E[1/n_i] = 0.092 and
                  var_resid ~ 0.045 that term is ~0.0042, i.e. most of the raw number.

    All three are reported against the SAME count-preserving shuffle floor, which is the only
    reason any of them is admissible: the floor carries the identical 1/n_i inflation."""
    m = cr > 0
    return {"weighted": float(np.average(a[m] ** 2, weights=cr[m])),
            "unweighted": float(a[m].var()),
            "mom": float(a[m].var() - var_resid * float(np.mean(1.0 / cr[m])))}


ESTIMATORS = ("weighted", "unweighted", "mom")


def shuffled_alpha(pi, ri, y, nP, nR, rng):
    """Rater identities permuted WITHIN prompt: preserves gamma, preserves each rater's COUNT,
    preserves the marginal error distribution, destroys real rater structure."""
    s = ri.copy()
    for p in np.unique(pi):
        ix = np.flatnonzero(pi == p)
        s[ix] = ri[rng.permutation(ix)]
    g, a, res = fit_crossed(pi, s, y, nP, nR)
    return a, np.bincount(s, None, nR), float(res.var(ddof=1))


def residual_var(alpha: np.ndarray, X: np.ndarray) -> tuple:
    """Variance of alpha after removing its linear projection on the exposure covariates."""
    A = np.column_stack([np.ones(len(alpha)), X])
    beta, *_ = np.linalg.lstsq(A, alpha, rcond=None)
    resid = alpha - A @ beta
    ss = alpha.var()
    return float(resid.var()), float(1.0 - resid.var() / ss) if ss > 0 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r111_alpha_confound.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    pre = preflight()

    B = build()
    nP, nR, X = B["nP"], B["nR"], B["X"]
    print(f"\ncells {len(B['rows']['full']):,} per arm   prompts {nP}   raters {nR}   "
          f"covariates {X.shape[1]} (mean rep, values-prompt share, log n)")

    # ---- REBUILD CONTROL against r110's persisted cells --------------------------
    z110 = np.load(R110, allow_pickle=True)
    drift = {arm: float(np.abs(B["rows"][arm] - z110[arm]).max()) for arm in ("full", "core")}
    print(f"REBUILD CONTROL vs r110 cells: max abs drift full {drift['full']:.2e} "
          f"core {drift['core']:.2e} -> {'PASS' if max(drift.values()) == 0 else 'FAIL'}")
    if max(drift.values()) != 0:
        raise SystemExit("REFUSING: this round's cells differ from r110's, so any contrast with "
                         "entry 21 would be comparing two different datasets.")

    fits, alpha, cr = {}, {}, {}
    for arm in ("full", "core"):
        R = B["rows"][arm]
        pi, ri, y = R[:, 0].astype(int), R[:, 1].astype(int), R[:, 2]
        g, a, res = fit_crossed(pi, ri, y, nP, nR)
        alpha[arm] = a
        cr[arm] = np.bincount(ri, None, nR)
        fits[arm] = {"var_case": float(g.var()), "var_resid": float(res.var(ddof=1)),
                     "pi": pi, "ri": ri, "y": y,
                     "comp": components(a, cr[arm], float(res.var(ddof=1)))}

    # ---- THE DESIGN FACTS, because r110's claim card got two of them wrong ---------
    c = cr["full"][cr["full"] > 0]
    design = {"min_n": int(c.min()), "median_n": int(np.median(c)), "max_n": int(c.max()),
              "mean_n": float(c.mean()), "n_eq_1": int((c == 1).sum()),
              "cells_share_n_le_2": float(cr["full"][cr["full"] <= 2].sum() / cr["full"].sum()),
              "E_inv_n": float(np.mean(1.0 / c))}
    print(f"\nDESIGN: min n {design['min_n']}  median {design['median_n']}  max {design['max_n']}"
          f"   E[1/n] {design['E_inv_n']:.4f}   raters with n=1: {design['n_eq_1']}"
          f"  holding {design['cells_share_n_le_2']:.2%} of cells")
    print("  r110's claim card said 'every rater appears on >= 2 prompts, median 20'. BOTH WRONG.")
    print(f"  And E[1/n]={design['E_inv_n']:.4f} x var_resid~{fits['full']['var_resid']:.3f} = "
          f"{design['E_inv_n']*fits['full']['var_resid']:.5f}, i.e. MOST of the raw variance of the "
          f"fitted alphas is a sampling term, not a component. Hence the floor.")

    # ---- COUNT-PRESERVING SHUFFLE FLOOR, per estimator, per arm -------------------
    floors = {arm: {k: [] for k in ESTIMATORS} for arm in ("full", "core")}
    for _ in range(N_SHUFFLE):
        for arm in ("full", "core"):
            sa, scr, sve = shuffled_alpha(fits[arm]["pi"], fits[arm]["ri"], fits[arm]["y"],
                                          nP, nR, rng)
            cm = components(sa, scr, sve)
            for k in ESTIMATORS:
                floors[arm][k].append(cm[k])
    floor = {arm: {k: float(np.mean(v)) for k, v in floors[arm].items()}
             for arm in ("full", "core")}

    print(f"\n{'estimator':<12}{'arm':>6}{'observed':>11}{'floor':>10}{'excess':>10}  Delta_excess")
    excess, dex = {}, {}
    for k in ESTIMATORS:
        for arm in ("full", "core"):
            excess[(k, arm)] = fits[arm]["comp"][k] - floor[arm][k]
        dex[k] = excess[(k, "core")] - excess[(k, "full")]
        for arm in ("full", "core"):
            print(f"{k if arm == 'full' else '':<12}{arm:>6}{fits[arm]['comp'][k]:>11.5f}"
                  f"{floor[arm][k]:>10.5f}{excess[(k, arm)]:>10.5f}"
                  + (f"  {dex[k]:+.5f}" if arm == "core" else ""))
    spread = max(dex.values()) - min(dex.values())
    print(f"  Delta_excess across THREE estimands spans {spread:.5f} -- the count-preserving floor "
          f"absorbs the 1/n_i inflation, so the contrast does not depend on which one is quoted.")
    raw_delta = dex["weighted"]

    # ---- LOW-n ROBUSTNESS --------------------------------------------------------
    robust = {}
    for MIN in (2, 3, 5):
        keep = set(np.flatnonzero(cr["full"] >= MIN).tolist())
        e2 = {}
        for arm in ("full", "core"):
            pi, ri, y = fits[arm]["pi"], fits[arm]["ri"], fits[arm]["y"]
            m = np.isin(ri, list(keep))
            p2, r2, y2 = pi[m], ri[m], y[m]
            nP2 = int(p2.max()) + 1
            g2, a2, res2 = fit_crossed(p2, r2, y2, nP2, nR)
            ob = components(a2, np.bincount(r2, None, nR), float(res2.var(ddof=1)))["weighted"]
            fv = []
            for _ in range(60):
                sa, scr, sve = shuffled_alpha(p2, r2, y2, nP2, nR, rng)
                fv.append(components(sa, scr, sve)["weighted"])
            e2[arm] = ob - float(np.mean(fv))
        robust[MIN] = e2["core"] - e2["full"]
        print(f"  robustness n>={MIN}: {len(keep):>4} raters, Delta_excess {robust[MIN]:+.5f}")

    # ---- DIRECTION, on ABSOLUTE error. See the retraction in the docstring. ------
    d_alpha = alpha["core"] - alpha["full"]
    m_, sd_ = d_alpha.mean(), d_alpha.std()
    skew = float(np.mean(((d_alpha - m_) / sd_) ** 3)) if sd_ > 0 else 0.0
    share_alpha_up = float(np.mean(d_alpha > 0))

    mu = {arm: float(fits[arm]["y"].mean()) for arm in ("full", "core")}
    def rater_means(arm, ri=None):
        r = fits[arm]["ri"] if ri is None else ri
        c = np.bincount(r, None, nR)
        tot = np.bincount(r, fits[arm]["y"], nR)
        m = c > 0
        out = np.full(nR, np.nan)
        out[m] = tot[m] / c[m]
        return out, m
    rm_f, mk = rater_means("full")
    rm_c, _ = rater_means("core")
    gain = rm_c[mk] - rm_f[mk]                       # negative = better served under core
    share_worse_raw = float(np.mean(gain > 0))
    # PAIRED shuffle null for that share: the SAME within-prompt permutation in both arms, which is
    # legitimate because the two arms are the identical (prompt, rater) grid.
    assert np.array_equal(fits["full"]["pi"], fits["core"]["pi"]) and \
           np.array_equal(fits["full"]["ri"], fits["core"]["ri"]), \
           "REFUSING: the arms are not the same cell grid, so a paired null is not available."
    null_share = []
    pi0, ri0 = fits["full"]["pi"], fits["full"]["ri"]
    for _ in range(N_SHUFFLE):
        sr = ri0.copy()
        for pp in np.unique(pi0):
            ix = np.flatnonzero(pi0 == pp)
            sr[ix] = ri0[rng.permutation(ix)]
        a_, _m = rater_means("full", sr)
        b_, _m2 = rater_means("core", sr)
        kk = ~np.isnan(a_) & ~np.isnan(b_)
        null_share.append(float(np.mean((b_[kk] - a_[kk]) > 0)))
    ns_m, ns_sd = float(np.mean(null_share)), float(np.std(null_share))
    excess_worse = share_worse_raw - ns_m
    # Deconvolution on the PAIRED difference. My first version subtracted
    # var_resid(core)/n + var_resid(full)/n, which over-subtracts badly: the two arms are the same
    # cells and are positively correlated, so the per-cell DIFFERENCE has much smaller noise than
    # the sum of the arms' noises. It drove the bias-free variance negative, hit the clamp, and
    # printed a clean-looking 0.00% that was the clamp and not an estimate.
    d_cell = fits["core"]["y"] - fits["full"]["y"]
    gd, ad, rd = fit_crossed(pi0, ri0, d_cell, nP, nR)
    var_d_noise = float(rd.var(ddof=1))
    g_var_unb = gain.var() - var_d_noise * design["E_inv_n"]
    from math import erf, sqrt
    if g_var_unb <= 0:
        g_unb, truly_worse = float("nan"), float("nan")
        print("  UNVERIFIED: the bias-free variance of the per-rater gain is non-positive, so the "
              "deconvolved share is not estimable here. Reporting nan, never a clamped zero.")
    else:
        g_unb = g_var_unb ** 0.5
        truly_worse = float(0.5 * (1.0 - erf((0.0 - gain.mean()) / (g_unb * sqrt(2.0)))))
    print(f"\nDIRECTION, on ABSOLUTE error (centred alpha cannot answer this -- see docstring)")
    print(f"  mu shift {mu['core'] - mu['full']:+.5f}: compilation LOWERS disagreement for the "
          f"corpus, so a rise in centred alpha is not harm")
    print(f"  raters with higher OWN MEAN error under core: {share_worse_raw:.1%}  "
          f"vs paired-shuffle null {ns_m:.1%} (sd {ns_sd:.1%})  -> genuine excess "
          f"{excess_worse:+.1%}, z {excess_worse / max(ns_sd, 1e-9):.1f}")
    print(f"  deconvolved truly-worse-off share {truly_worse:.2%}  (mean gain {gain.mean():+.5f}, "
          f"bias-free sd {g_unb:.4f})")
    # THE GRADIENT IS NOT IDENTIFIED BY BINNING ON EITHER ARM.
    # Bin on full's alpha and full's error is extreme by selection, so core regresses toward its own
    # mean: the gain looks small at the low end and large at the high end. Bin on core's alpha and
    # the identical argument runs the other way. Both are the change-score-versus-baseline fallacy
    # (Oldham 1962), and they produce OPPOSITE gradients from the same data -- which is how this was
    # found: the independent navigator binned on core and got the gain shrinking from -0.133 to
    # -0.032, I binned on full and got it growing from -0.043 to -0.077. Neither is the gradient.
    # Oldham's own remedy: bin on the AVERAGE of the two measurements, which is uncorrelated with
    # the difference under exchangeable noise. All three are reported; only the third is quotable.
    nn = int(mk.sum())
    axes = {"full alpha (regresses toward core)": alpha["full"][mk],
            "core alpha (regresses toward full)": alpha["core"][mk],
            "MEAN of both (Oldham, quotable)": 0.5 * (alpha["full"][mk] + alpha["core"][mk])}
    bins = [(0, 5), (5, 25), (25, 50), (50, 75), (75, 95), (95, 100)]
    perc, grads = {}, {}
    for name, ax in axes.items():
        order = np.argsort(np.argsort(ax))
        rows = {}
        for a0, b0 in bins:
            sel = (order >= a0 * nn / 100) & (order < max(b0 * nn / 100, a0 * nn / 100 + 1))
            ef, ec = float(rm_f[mk][sel].mean()), float(rm_c[mk][sel].mean())
            rows[f"{a0}-{b0}"] = {"n": int(sel.sum()), "full": ef, "core": ec, "gain": ec - ef}
        perc[name] = rows
        g0, g1 = rows["0-5"]["gain"], rows["95-100"]["gain"]
        grads[name] = g1 - g0
        print(f"  binned on {name}:")
        for k, v in rows.items():
            print(f"     pct {k:<7} n={v['n']:>4}  full {v['full']:.4f}  core {v['core']:.4f}  "
                  f"gain {v['gain']:+.4f}")
        print(f"     gradient worst-minus-best {g1 - g0:+.4f}  "
              f"({'gain GROWS' if g1 < g0 else 'gain SHRINKS'} toward the badly-served)")
    perc_q = perc["MEAN of both (Oldham, quotable)"]
    sign_flips = (grads["full alpha (regresses toward core)"]
                  * grads["core alpha (regresses toward full)"]) < 0
    print(f"  the two single-arm axes give OPPOSITE gradients: {sign_flips} -- so the gradient is a "
          f"selection artifact on either, and only the Oldham axis is admissible")
    n_lower = sum(1 for v in perc_q.values() if v["gain"] < 0)
    worse_at_every_pct = n_lower == len(perc_q)
    grad_q = grads["MEAN of both (Oldham, quotable)"]
    print(f"  ON THE ADMISSIBLE AXIS: absolute error lower under core in {n_lower} of "
          f"{len(perc_q)} bins; gradient {grad_q:+.4f}")
    # is the alpha-widening bigger among the well-served or the badly-served?
    lo_end = alpha["full"][mk] <= np.quantile(alpha["full"][mk], 0.05)
    hi_end = alpha["full"][mk] >= np.quantile(alpha["full"][mk], 0.95)
    spread_lo = float(np.abs(d_alpha[mk][lo_end]).mean())
    spread_hi = float(np.abs(d_alpha[mk][hi_end]).mean())
    print(f"  |Delta alpha| in the BEST-served 5% {spread_lo:+.4f} vs the WORST-served 5% "
          f"{spread_hi:+.4f} -> the widening is driven by the "
          f"{'well' if spread_lo > spread_hi else 'badly'}-served tail")

    # ---- POSITIVE CONTROL for the residualizer ----------------------------------
    planted = 0.05 * (X[:, 0] - X[:, 0].mean()) / max(X[:, 0].std(), 1e-9)
    pv, pr2 = residual_var(planted, X)
    print(f"POSITIVE CONTROL: an alpha built to BE mean-representativeness -> residual variance "
          f"{pv:.2e} of {planted.var():.5f}, R2 {pr2:.4f} -> "
          f"{'PASS' if pr2 > 0.99 else 'FAIL'}")
    if pr2 <= 0.99:
        raise SystemExit("REFUSING: the residualizer cannot remove a signal it was handed, so a "
                         "null from it would be silence.")

    # ---- THE MEASUREMENT: exposure, on the EXCESS scale --------------------------
    # The observed AND the floor are both residualized, so the comparison is like-for-like.
    r2 = {arm: residual_var(alpha[arm], X)[1] for arm in ("full", "core")}
    res_obs = {arm: float(residual_var(alpha[arm], X)[0]) for arm in ("full", "core")}
    res_floor = {arm: [] for arm in ("full", "core")}
    for _ in range(N_SHUFFLE):
        for arm in ("full", "core"):
            sa, _c, _v = shuffled_alpha(fits[arm]["pi"], fits[arm]["ri"], fits[arm]["y"],
                                        nP, nR, rng)
            res_floor[arm].append(residual_var(sa, X)[0])
    res_ex = {arm: res_obs[arm] - float(np.mean(res_floor[arm])) for arm in ("full", "core")}
    res_delta = res_ex["core"] - res_ex["full"]
    base_unw = excess[("unweighted", "core")] - excess[("unweighted", "full")]
    removed = 1.0 - res_delta / base_unw if base_unw != 0 else 0.0
    print(f"\n  arm   R2 of alpha on exposure   excess | exposure")
    for arm in ("full", "core"):
        print(f" {arm:>5}   {r2[arm]:>21.4f}   {res_ex[arm]:>16.5f}")
    print(f"  Delta_excess | exposure {res_delta:+.5f} vs unconditional {base_unw:+.5f} "
          f"-> exposure removes {removed:.1%}")

    perm_removed = []
    for _ in range(N_PERM):
        Xp = X[rng.permutation(nR)]          # rater ROWS permuted: marginals exact, link broken
        pf = residual_var(alpha["full"], Xp)[0] - float(np.mean(res_floor["full"]))
        pc = residual_var(alpha["core"], Xp)[0] - float(np.mean(res_floor["core"]))
        perm_removed.append(1.0 - (pc - pf) / base_unw)
    perm_removed = np.array(perm_removed)
    pm, plo, phi = perm_removed.mean(), *np.quantile(perm_removed, [0.025, 0.975])
    print(f"  PERMUTED control ({N_PERM} draws): removes {pm:.1%} [{plo:.1%},{phi:.1%}] "
          f"-- the arithmetic floor")

    # ---- prompt-clustered bootstrap on the EXCESS-scale weighted contrast --------
    boot = []
    for _ in range(N_BOOT):
        take = rng.integers(0, nP, nP)
        vals = {}
        for arm in ("full", "core"):
            pi, ri, y = fits[arm]["pi"], fits[arm]["ri"], fits[arm]["y"]
            keep_ix = np.concatenate([np.flatnonzero(pi == t) for t in take])
            npi = np.concatenate([np.full(int((pi == t).sum()), k) for k, t in enumerate(take)])
            g, a, res = fit_crossed(npi, ri[keep_ix], y[keep_ix], nP, nR, niter=80)
            vals[arm] = components(a, np.bincount(ri[keep_ix], None, nR),
                                   float(res.var(ddof=1)))["weighted"] - floor[arm]["weighted"]
        boot.append(vals["core"] - vals["full"])
    boot = np.array(boot)
    lo, hi_ = np.quantile(boot, [0.025, 0.975])
    print(f"  Delta_excess 95% CI over PROMPTS [{lo:+.5f},{hi_:+.5f}]  ({N_BOOT} draws)")

    # ---- verdict, generated, never hand-written --------------------------------
    perm_ok = pm < PERM_CEILING_SHARE
    ci_excludes_zero = not (lo <= 0 <= hi_)
    if not perm_ok:
        world = "UNVERIFIED"
    elif removed >= KILL_REMOVAL_SHARE:
        world = "W2 EXPOSURE"
    else:
        world = "W1 SUBGROUP"
    conclusion = (
        f"Entry 21 quoted var_rater 0.00422 and 0.00626 and called the rise 'particular raters are "
        f"systematically worse served'. Two corrections, neither of which overturns the effect. "
        f"FIRST, the number: the variance of fitted alphas is the component PLUS a sampling term "
        f"var_resid*E[1/n_i] = {design['E_inv_n'] * fits['full']['var_resid']:.5f}, which is most of "
        f"it, so the raw value is not a component under any of the three estimands "
        f"(per-observation {fits['full']['comp']['weighted']:.5f}/{fits['core']['comp']['weighted']:.5f}, "
        f"per-person {fits['full']['comp']['unweighted']:.5f}/{fits['core']['comp']['unweighted']:.5f}, "
        f"moment-corrected {fits['full']['comp']['mom']:.5f}/{fits['core']['comp']['mom']:.5f}). "
        f"On the EXCESS-over-count-preserving-floor scale the contrast is estimand-invariant: "
        f"{min(dex.values()):+.5f} to {max(dex.values()):+.5f}, a span of {spread:.5f}, "
        f"95% CI over prompts [{lo:+.5f},{hi_:+.5f}], and flat across low-n exclusions "
        f"({', '.join(f'n>={k}: {v:+.5f}' for k, v in sorted(robust.items()))}). "
        f"SECOND, the direction, and this retracts my own first answer as well as entry 21's. "
        f"Centred alpha cannot carry an absolute claim: mu falls {mu['core'] - mu['full']:+.5f} "
        f"under compilation, so a rater can rise in alpha while their disagreement falls. On "
        f"absolute error, {share_worse_raw:.1%} of raters have a higher own-mean error under core "
        f"against a paired-shuffle null of {ns_m:.1%} (sd {ns_sd:.1%}), a genuine excess of "
        f"{excess_worse:+.1%}, and deconvolution puts the truly-worse-off share at "
        f"{truly_worse:.2%}. Absolute error is lower under core in {n_lower} of {len(perc)} "
        f"equal-count bins of the Oldham axis (the mean of both arms' alpha, because binning on "
        f"either arm alone yields OPPOSITE gradients by regression to the mean -- "
        f"{grads['full alpha (regresses toward core)']:+.4f} versus "
        f"{grads['core alpha (regresses toward full)']:+.4f} -- and neither is the gradient), "
        f"with an admissible gradient of {grad_q:+.4f}, and |Delta alpha| is larger in the "
        f"best-served 5% "
        f"({spread_lo:.4f}) than the worst-served 5% ({spread_hi:.4f}). So nobody is meaningfully "
        f"worse served: compilation improves almost everyone and widens the INEQUALITY of that "
        f"improvement. Entry 21's 'systematically worse served' and my own 'better- and "
        f"worse-served in equal number' are both wrong. "
        f"THIRD, the rival explanation. Exposure -- mean prompt typicality, share of values-contested "
        f"prompts, log workload -- explains R2 {r2['full']:.4f} of full's alpha and {r2['core']:.4f} "
        f"of core's and removes {removed:.1%} of the contrast, against a permuted arithmetic floor "
        f"of {pm:.1%} [{plo:.1%},{phi:.1%}]. WORLD: {world}. "
        + ("The rater structure is not reducible to which prompts a rater met, so it is a property "
           "of people -- people whose SHARE of the universal improvement differs."
           if world == "W1 SUBGROUP" else
           "The structure is largely exposure; entry 21 must be rewritten as an exposure finding."
           if world == "W2 EXPOSURE" else
           "The permuted control removed a comparable share, so this instrument cannot separate "
           "signal from arithmetic. UNVERIFIED is not an acquittal for either world."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"preflight": pre, "n_cells": len(B["rows"]["full"]), "n_prompts": nP, "n_raters": nR,
           "rebuild_drift": drift, "design": design,
           "components": {a: fits[a]["comp"] for a in ("full", "core")},
           "var_case": {a: fits[a]["var_case"] for a in ("full", "core")},
           "var_resid": {a: fits[a]["var_resid"] for a in ("full", "core")},
           "floor": floor, "excess": {f"{k}|{a}": v for (k, a), v in excess.items()},
           "delta_excess": dex, "delta_excess_span": spread, "robustness_low_n": robust,
           "ledger_delta": LEDGER_DELTA,
           "r2_exposure": r2, "excess_given_exposure": res_ex,
           "residualized_delta": res_delta, "removed_share": removed,
           "delta_excess_ci": [float(lo), float(hi_)], "ci_excludes_zero": ci_excludes_zero,
           "permuted_removed": {"mean": float(pm), "ci": [float(plo), float(phi)]},
           "positive_control_r2": pr2,
           "direction": {"share_alpha_up": share_alpha_up, "skew": skew, "mu": mu,
                         "mu_shift": mu["core"] - mu["full"],
                         "share_worse_abs": share_worse_raw, "null_share": ns_m,
                         "null_share_sd": ns_sd, "excess_worse": excess_worse,
                         "truly_worse_deconvolved": truly_worse, "gain_mean": float(gain.mean()),
                         "gain_sd_biasfree": float(g_unb), "by_percentile": perc,
                         "bins_lower": n_lower, "bins_total": len(perc_q),
                         "gradients": grads, "gradient_admissible": grad_q,
                         "single_arm_axes_disagree_in_sign": bool(sign_flips),
                         "lower_at_every_bin": worse_at_every_pct,
                         "spread_best5": spread_lo, "spread_worst5": spread_hi},
           "kill": {"removal_share": KILL_REMOVAL_SHARE, "perm_ceiling": PERM_CEILING_SHARE},
           "world": world, "conclusion": conclusion}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    # Persist WITH the ids -- r110 persisted indices alone, so nothing could join it to a covariate.
    np.savez_compressed(_RES / "r111_alpha.npz",
                        rater_ids=np.array(B["rater_ids"], dtype=object),
                        alpha_full=alpha["full"], alpha_core=alpha["core"], X=X, boot=boot)
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
