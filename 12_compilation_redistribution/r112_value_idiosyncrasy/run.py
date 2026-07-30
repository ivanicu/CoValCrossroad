"""r112 -- is the withheld improvement DESCRIBABLE? Whose gain does compilation keep?

THE LAST CoVal ROUND. Directed by the independent navigator, which replaced the ledger's own NEXT
(an alpha-coherence test) and gave four reasons, all of which check out:

  1. WRONG OUTCOME. Ranking raters by fitted alpha finds people who disagree with ANY rule, not
     people compilation serves worse. The navigator measured corr(alpha_full, alpha_core) = 0.6617
     on the fitted crossed alphas over 15,202 cells; this round recomputes 0.6925 on prompt-demeaned
     rater means over its own 14,637-cell population. Different estimators on different populations,
     same conclusion -- and the two numbers are stated separately rather than one being quoted as
     the other, which is the ninth-instance defect this programme keeps committing.
  2. DEAD ON POWER. r111 put the truly-worse-off share at ~6%, the navigator's route at ~1.6%. A
     coherence test on 16-60 people resolves nothing; this design uses the continuous gradient over
     every cell.
  3. WRONG CONSTRUCT. subjectivity / representativeness / importance are self-reports ABOUT THE
     PROMPT. r111's preflight measured it: the two subjectivity levels carrying the programme's
     object are PROMPT-driven (19.4% and 21.1% prompt versus 16.1% and 15.8% rater). Rater averages
     of them mostly encode which prompts a rater drew.
  4. THREE UNCONTROLLED TESTS with a hand-chosen high-alpha cut, in a ledger that already catalogued
     `if chi > 100` as exactly that defect class.

WHAT r111 ESTABLISHED, so this round knows what it is explaining
---------------------------------------------------------------
Compilation does NOT harm people. mu falls 0.06870; absolute error is lower under core in 6 of 6
equal-count bins of the Oldham axis, including the worst-served (0.5313 -> 0.5021). What it does is
redistribute the SIZE of a near-universal improvement: the gain runs -0.1038 at the best-served 5%
to -0.0292 at the worst, monotone. And the rater-attached component of that spread is not reducible
to which prompts a rater met -- exposure covariates remove 22.0% against a permuted floor of 2.6%.

So the open question is not whether there are losers. It is whether the people whose improvement is
WITHHELD are describable, or anonymous.

THE COVARIATE, verified against the object before it was used
-------------------------------------------------------------
`data/conversation_rubrics.jsonl` -> `coval_full[*]` = {criterion, rubric_item_id, scores}, where
scores = [{annotator_id, score}] and score is a signed -10..+10 importance weight. That is EVERY
RATER'S OWN VALUE PROFILE over the criteria of the prompt they judged, and 111 rounds never opened
it. (`coval_core[*]` = {criterion} alone -- the compiler has no provenance, so no ancestor-matching
design is available and no semantic matcher will be built to fake one.)

CLAIM CARD
----------
Claim      The withheld part of the improvement is attached to raters whose OWN STATED VALUES
           diverge from the consensus the rubric was compiled toward.
Estimand   beta in  d_{i,p} = prompt FE + beta_1 x1_{i,p} + beta_2 x2_{i,p} + controls + eps
           d = e_core - e_full  (paired, identical cells; NEGATIVE = better served under core)
           x1 = 1 - corr(rater i's scores, LEAVE-ONE-OUT consensus scores) on prompt p's criteria
           x2 = share of i's scored criteria on p whose SIGN disagrees with the LOO consensus sign
           beta > 0 means a value-divergent rater's gain is SMALLER.
           Leave-one-out matters: with the rater's own score inside the consensus, corr is
           mechanically inflated and inflated MORE for raters on prompts with few other scorers.
Target
observed?  YES, and measured here rather than assumed: coverage is printed before the fit and the
           round exits 2 if the population is empty.
Worlds     W-DESCRIBABLE   beta_1 or beta_2 significantly positive, surviving the profile
                           permutation. The compiled rubric withholds its benefit from a subgroup
                           with a statable character: people whose values are further from the
                           consensus it compresses toward. CoVal ends with a subject.
           W-ANONYMOUS     both CIs cover zero and the permuted null covers the observed effect.
                           The redistribution is real (r111) and undescribable by this covariate.
                           "Identifiable subgroup" leaves the claim permanently.
Intervention
           none. Prompt fixed effects absorb every prompt-level quantity, so the exposure confound
           r111 had to model away is DESIGNED OUT here rather than adjusted for.
Nulls      (i) NEGATIVE CONTROL, load-bearing: recompute x from a DIFFERENT rater's whole profile on
           the same prompt -- a within-prompt permutation of profiles. Preserves both marginals
           exactly, destroys the pairing. beta must not survive it.
           (ii) POSITIVE CONTROL: plant a synthetic gain proportional to x1 and require recovery,
           so a null is a measurement and not silence.
           (iii) Two-way cluster-robust SEs (Cameron-Gelbach-Miller 2011), clustered on prompt AND
           on rater, because a rater appears on many prompts and a prompt has many raters.

PRE-REGISTERED KILL, written before the run
-------------------------------------------
If the 95% two-way-clustered CI covers zero for BOTH x1 and x2, AND the profile-permutation null
covers the observed |beta| for both, then W-ANONYMOUS: the compilation line closes, CoVal is done,
and "identifiable subgroup" is struck from the claim for good. Community Notes does NOT open either
way -- a positive result gives CoVal a subject, and a negative one is a limitation CN inherits
rather than rescues.

CONTROLS IN THE SAME ITERATION, named before running (gate 7)
------------------------------------------------------------
n_scored (a rater who scored more criteria has a better-estimated profile AND may simply be more
engaged) and n_i (their workload). Both enter the regression, not a robustness appendix.
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

from covalx import load_join  # noqa: E402

FULL = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R110 = _ROOT / "12_compilation_redistribution/r110_rater_component/results/r110_cells.npz"

SEED = 20260729
N_PERM = 1000
MIN_SCORED = 3          # corr needs >= 3 points; pre-registered, not tuned
ALPHA = 0.05


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


def profiles(rub: dict) -> dict:
    """rater id -> {rubric_item_id: signed score} for one prompt, from coval_full."""
    out: dict = defaultdict(dict)
    for it in rub.get("coval_full") or []:
        rid_item = it.get("rubric_item_id")
        for s in it.get("scores") or []:
            out[str(s["annotator_id"])][rid_item] = float(s["score"])
    return out


def idiosyncrasy(own: dict, others: list, rng=None) -> tuple:
    """x1 = 1 - corr(own, LEAVE-ONE-OUT consensus); x2 = sign-disagreement share.
    `others` is the list of the OTHER raters' profiles on this prompt. Returns (x1, x2, n) or None
    when fewer than MIN_SCORED criteria have both a own score and a LOO consensus."""
    items = sorted(k for k in own if any(k in o for o in others))
    pairs = []
    for k in items:
        vals = [o[k] for o in others if k in o]
        if vals:
            pairs.append((own[k], float(np.mean(vals))))
    if len(pairs) < MIN_SCORED:
        return None
    a = np.array([p[0] for p in pairs], float)
    b = np.array([p[1] for p in pairs], float)
    if a.std() == 0 or b.std() == 0:
        return None                      # corr undefined; excluded and COUNTED, never imputed
    x1 = 1.0 - float(np.corrcoef(a, b)[0, 1])
    x2 = float(np.mean(np.sign(a) != np.sign(b)))
    # SPLIT-HALF for attenuation: x1 rests on at most 6 points because CoVal gives each rater a
    # bounded set of SHARED criteria plus their own contributed criteria, which no one else scores --
    # so a rater's self-invented criteria, arguably the purest statement of their values, can never
    # enter a divergence-from-consensus measure at all. Noise in x1 biases beta TOWARD ZERO, so the
    # uncorrected estimate is a floor, and this measures by how much.
    h1 = h2 = float("nan")
    if len(pairs) >= 6 and rng is not None:
        idx = rng.permutation(len(pairs))
        for tgt, part in ((0, idx[:len(idx) // 2]), (1, idx[len(idx) // 2:])):
            aa, bb = a[part], b[part]
            v = (1.0 - float(np.corrcoef(aa, bb)[0, 1])
                 if len(part) >= 3 and aa.std() > 0 and bb.std() > 0 else float("nan"))
            if tgt == 0:
                h1 = v
            else:
                h2 = v
    return x1, x2, len(pairs), h1, h2


def twoway_ols(y, X, gp, gr):
    """OLS with two-way cluster-robust covariance (Cameron-Gelbach-Miller 2011):
    V = V_prompt + V_rater - V_intersection. y and X are already within-prompt demeaned, which is
    the fixed-effects transform; the FE absorb every prompt-level quantity by construction."""
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
    # CGM's estimator can be non-PSD in finite samples; the standard fix is eigenvalue truncation,
    # applied here and REPORTED rather than hidden, because a silently repaired covariance is a
    # silently changed confidence interval.
    w, Q = np.linalg.eigh(V)
    fixed = bool((w < 0).any())
    V = Q @ np.diag(np.maximum(w, 0)) @ Q.T
    return beta, np.sqrt(np.maximum(np.diag(V), 0)), fixed


def demean(v, g):
    s = np.bincount(g, v, g.max() + 1)
    c = np.maximum(np.bincount(g, None, g.max() + 1), 1)
    return v - (s / c)[g]


def build(rng):
    F, C = load_sat(FULL), load_sat(CORE)
    cells, dropped = [], defaultdict(int)
    joined = sorted(((pid, comp, rub) for pid, comp, rub in load_join(COMPARISONS, RUBRICS)
                     if pid in F and pid in C), key=lambda t: t[0])
    for pid, comp, rub in joined:
        sc = {"full": equal_weight_scores(F[pid]), "core": equal_weight_scores(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        prof = profiles(rub)
        asms = sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id")))
        for a in asms:
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            P0 = strict_pairs(w[0].get("ranking", ""))
            rid = str(a.get("annotator_id"))
            err = {}
            for arm in ("full", "core"):
                s = sc[arm]
                P = {(x, y) for x, y in P0 if x in s and y in s and s[x] != s[y]}
                if not P:
                    break
                err[arm] = sum(1 for x, y in P if s[x] < s[y]) / len(P)
            if len(err) != 2:
                continue
            if rid not in prof:
                dropped["no_own_profile"] += 1
                continue
            others = [p for r, p in sorted(prof.items()) if r != rid]
            ix = idiosyncrasy(prof[rid], others, rng)
            if ix is None:
                dropped["too_few_scored_or_constant"] += 1
                continue
            cells.append({"pid": pid, "rid": rid, "d": err["core"] - err["full"],
                          "e_full": err["full"], "e_core": err["core"],
                          "x1": ix[0], "x2": ix[1], "n_scored": ix[2],
                          "x1a": ix[3], "x1b": ix[4]})
    return cells, dict(dropped)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r112_value_idiosyncrasy.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    cells, dropped = build(rng)
    if not cells:
        print("REFUSING: empty population. Nothing-to-fit exits 2, never 0.", file=sys.stderr)
        return 2

    z110 = np.load(R110, allow_pickle=True)
    n_ref = len(z110["full"])
    print(f"cells with a usable own profile: {len(cells):,} of {n_ref:,} analysis cells "
          f"({len(cells)/n_ref:.2%})   dropped {dropped}")
    ns = np.array([c["n_scored"] for c in cells])
    print(f"criteria scored per cell: median {int(np.median(ns))}  "
          f">= 5: {np.mean(ns >= 5):.1%}  min {ns.min()}  max {ns.max()}")

    pids = sorted({c["pid"] for c in cells})
    rids = sorted({c["rid"] for c in cells})
    PI = {p: i for i, p in enumerate(pids)}
    RI = {r: i for i, r in enumerate(rids)}
    gp = np.array([PI[c["pid"]] for c in cells])
    gr = np.array([RI[c["rid"]] for c in cells])
    d = np.array([c["d"] for c in cells])
    n_i = np.bincount(gr, None, len(rids)).astype(float)

    raw = {"x1": np.array([c["x1"] for c in cells]),
           "x2": np.array([c["x2"] for c in cells]),
           "n_scored": np.log(np.array([c["n_scored"] for c in cells], float)),
           "log_n_i": np.log(n_i[gr])}
    print(f"prompts {len(pids)}  raters {len(rids)}  mean gain {d.mean():+.5f}  "
          f"x1 mean {raw['x1'].mean():.3f} sd {raw['x1'].std():.3f}  "
          f"x2 mean {raw['x2'].mean():.3f} sd {raw['x2'].std():.3f}")

    NAMES = ["x1", "x2", "n_scored", "log_n_i"]

    def fit(dv, cov):
        y = demean(dv, gp)
        X = np.column_stack([demean(cov[k], gp) for k in NAMES])
        return twoway_ols(y, X, gp, gr)

    # ---- POSITIVE CONTROL -------------------------------------------------------
    planted = 0.30 * raw["x1"] + rng.normal(0, 0.05, len(cells))
    pb, pse, _ = fit(planted, raw)
    print(f"POSITIVE CONTROL: gain planted as 0.30*x1 -> beta_x1 {pb[0]:+.4f} "
          f"(se {pse[0]:.4f}) -> {'PASS' if abs(pb[0] - 0.30) < 0.05 else 'FAIL'}")
    if abs(pb[0] - 0.30) >= 0.05:
        print("REFUSING: the estimator cannot recover a coefficient it was handed.", file=sys.stderr)
        return 1

    # ---- THE FIT ----------------------------------------------------------------
    beta, se, psd_fixed = fit(d, raw)
    ci = [(b - 1.96 * s, b + 1.96 * s) for b, s in zip(beta, se)]
    print(f"\n  {'term':<10}{'beta':>10}{'se':>9}{'t':>7}   95% CI")
    for k, b, s, (lo, hi) in zip(NAMES, beta, se, ci):
        star = "  *" if not (lo <= 0 <= hi) else ""
        print(f"  {k:<10}{b:>+10.5f}{s:>9.5f}{b/max(s,1e-12):>7.2f}   "
              f"[{lo:+.5f},{hi:+.5f}]{star}")
    if psd_fixed:
        print("  NOTE: the two-way covariance was not PSD and was eigenvalue-truncated.")

    # ---- NEGATIVE CONTROL: within-prompt permutation of WHOLE profiles ----------
    by_p = defaultdict(list)
    for i, c in enumerate(cells):
        by_p[gp[i]].append(i)
    perm_beta = []
    for _ in range(N_PERM):
        pcov = {k: v.copy() for k, v in raw.items()}
        for p, ix in sorted(by_p.items()):
            if len(ix) < 2:
                continue
            order = rng.permutation(len(ix))
            for k in ("x1", "x2", "n_scored"):     # the PROFILE moves; workload stays with the rater
                pcov[k][np.array(ix)] = raw[k][np.array(ix)[order]]
        pb2, _s, _f = fit(d, pcov)
        perm_beta.append(pb2[:2])
    perm_beta = np.array(perm_beta)
    print(f"\n  NEGATIVE CONTROL ({N_PERM} within-prompt profile permutations):")
    covered = {}
    for j, k in enumerate(("x1", "x2")):
        q = np.quantile(perm_beta[:, j], [0.025, 0.975])
        covered[k] = bool(q[0] <= beta[j] <= q[1])
        p_two = float(np.mean(np.abs(perm_beta[:, j]) >= abs(beta[j])))
        print(f"    {k}: null beta in [{q[0]:+.5f},{q[1]:+.5f}], observed {beta[j]:+.5f}, "
              f"p_perm {p_two:.4f} -> null {'COVERS' if covered[k] else 'EXCLUDES'} observed")

    # ---- ATTENUATION: how much does noise in x1 hide? ---------------------------
    ha = np.array([c["x1a"] for c in cells]); hb = np.array([c["x1b"] for c in cells])
    ok = ~np.isnan(ha) & ~np.isnan(hb)
    h = float(np.corrcoef(ha[ok], hb[ok])[0, 1]) if ok.sum() > 10 else float("nan")
    rel = 2 * h / (1 + h) if h == h and h > -1 else float("nan")
    beta_deatt = beta[0] / rel if rel == rel and rel > 0 else float("nan")
    print(f"\n  ATTENUATION: split-half reliability of x1 on {ok.sum():,} cells with >=6 shared "
          f"criteria: h {h:.4f}, Spearman-Brown {rel:.4f}")
    att_quotable = rel == rel and rel >= 0.50
    print(f"    beta_x1 deattenuated {beta_deatt:+.5f} vs raw {beta[0]:+.5f} -- the raw estimate is "
          f"a FLOOR, because x1 rests on at most 6 points by CoVal's design")
    if not att_quotable:
        print(f"    NOT QUOTABLE: reliability {rel:.4f} is below 0.50, so the correction factor "
              f"1/{rel:.4f} = {1/rel:.2f}x carries large sampling error of its own. The "
              f"deattenuated value states the DIRECTION of the bias, not its size. Quote the raw "
              f"coefficient; a floor with a known sign beats a point estimate divided by a noisy "
              f"small number.")
    sd1 = float(raw["x1"].std())
    per_sd = beta[0] * sd1
    print(f"  EFFECT SIZE: +1 sd of value divergence ({sd1:.3f}) withholds {per_sd:+.5f} of gain, "
          f"i.e. {per_sd / abs(d.mean()):.1%} of the mean gain {d.mean():+.5f}"
          + (f"; deattenuated {beta_deatt * sd1 / abs(d.mean()):.1%} (DIRECTIONAL ONLY)"
             if rel == rel else ""))

    # ---- alpha correlation, the navigator's reason 1, recomputed ----------------
    a_full = np.zeros(len(rids)); a_core = np.zeros(len(rids))
    for arr, key in ((a_full, "e_full"), (a_core, "e_core")):
        v = np.array([c[key] for c in cells])
        vd = demean(v, gp)
        cnt = np.maximum(np.bincount(gr, None, len(rids)), 1)
        arr[:] = np.bincount(gr, vd, len(rids)) / cnt
    corr_alpha = float(np.corrcoef(a_full, a_core)[0, 1])
    print(f"\n  corr(alpha_full, alpha_core) = {corr_alpha:.4f} -- ranking raters by alpha would "
          f"have found people who disagree with ANY rule, which is why the outcome is the CHANGE")

    sig = {k: not (ci[j][0] <= 0 <= ci[j][1]) for j, k in enumerate(("x1", "x2"))}
    any_sig = any(sig.values())
    null_excludes = any(not covered[k] for k in ("x1", "x2"))
    world = "W-DESCRIBABLE" if (any_sig and null_excludes) else "W-ANONYMOUS"
    conclusion = (
        f"On {len(cells):,} of {n_ref:,} analysis cells ({len(cells)/n_ref:.1%}) carrying the "
        f"rater's own signed criterion scores, with prompt fixed effects absorbing every "
        f"prompt-level quantity and two-way clustering on prompt and rater: a rater's value "
        f"divergence from the leave-one-out consensus predicts their compilation gain with "
        f"beta_x1 {beta[0]:+.5f} (95% CI [{ci[0][0]:+.5f},{ci[0][1]:+.5f}]) and their "
        f"sign-disagreement share with beta_x2 {beta[1]:+.5f} "
        f"(95% CI [{ci[1][0]:+.5f},{ci[1][1]:+.5f}]), positive meaning a SMALLER gain. The "
        f"within-prompt profile permutation "
        f"{'covers' if not null_excludes else 'excludes'} the observed effect. "
        f"corr(alpha_full, alpha_core) = {corr_alpha:.4f}. In interpretable units, +1 sd of value "
        f"divergence withholds {per_sd:+.5f} of gain, {per_sd / abs(d.mean()):.1%} of the mean gain "
        f"{d.mean():+.5f}; x1's split-half reliability is {h:.4f} (Spearman-Brown {rel:.4f}) because "
        f"CoVal caps a rater's shared criteria at six, so the raw coefficient is a FLOOR; the "
        f"deattenuated {beta_deatt:+.5f} is reported to fix the sign of that bias and is NOT "
        f"quotable at a reliability of {rel:.4f}. WORLD: {world}. "
        + ("The withheld improvement is DESCRIBABLE: compilation returns less to raters whose own "
           "stated values sit further from the consensus it compresses toward. CoVal ends with a "
           "subject."
           if world == "W-DESCRIBABLE" else
           "The redistribution r111 measured is real and this covariate does not describe it. "
           "'Identifiable subgroup' leaves the claim permanently, and the compilation line closes "
           "on a corrected result rather than an impressive one."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_cells": len(cells), "n_reference_cells": int(n_ref), "dropped": dropped,
         "coverage": len(cells) / n_ref, "n_prompts": len(pids), "n_raters": len(rids),
         "n_scored": {"median": int(np.median(ns)), "share_ge_5": float(np.mean(ns >= 5)),
                      "min": int(ns.min()), "max": int(ns.max())},
         "mean_gain": float(d.mean()),
         "terms": NAMES, "beta": beta.tolist(), "se": se.tolist(),
         "ci": [[float(a), float(b)] for a, b in ci], "psd_truncated": psd_fixed,
         "significant": sig, "positive_control_beta_x1": float(pb[0]),
         "perm_null": {k: {"ci": np.quantile(perm_beta[:, j], [0.025, 0.975]).tolist(),
                           "covers_observed": covered[k],
                           "p_perm": float(np.mean(np.abs(perm_beta[:, j]) >= abs(beta[j])))}
                       for j, k in enumerate(("x1", "x2"))},
         "corr_alpha_arms": corr_alpha,
         "attenuation": {"split_half_h": h, "spearman_brown": rel,
                         "beta_x1_deattenuated": beta_deatt, "n_cells_split": int(ok.sum()),
                         "deattenuation_quotable": att_quotable},
         "effect_size": {"x1_sd": sd1, "gain_withheld_per_sd": per_sd,
                         "share_of_mean_gain": per_sd / abs(float(d.mean()))},
         "world": world, "conclusion": conclusion},
        indent=1, sort_keys=True))
    np.savez_compressed(_RES / "r112_cells.npz",
                        gp=gp, gr=gr, d=d, x1=raw["x1"], x2=raw["x2"],
                        n_scored=np.exp(raw["n_scored"]), perm_beta=perm_beta,
                        prompt_ids=np.array(pids, dtype=object),
                        rater_ids=np.array(rids, dtype=object))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
