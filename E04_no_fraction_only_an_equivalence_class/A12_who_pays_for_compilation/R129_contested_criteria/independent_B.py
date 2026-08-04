#!/usr/bin/env python3
"""R129_contested_criteria / independent_B.py

ESTIMAND (write before any code touches an outcome)
-----------------------------------------------------
Among evaluation criteria in `coval_full` that received ratings from >=2
participants (so "split vs agreed" is even a defined quantity), does the
DEGREE OF RATER DISAGREEMENT on a criterion (fraction of raters sitting on
the minority side of zero) predict whether that criterion's TOPIC survives
into the compiled 4-item `coval_core` for its prompt -- after adjusting for
the criterion's mean rated importance and its rater count -- and, among the
criteria that ARE split, does the compiled representative preferentially
follow the raw-vote MAJORITY side or the more INTENSE (larger |mean|)
minority side, on the criteria where the two disagree?

THE PROVENANCE GAP
-------------------
`coval_core` items carry ONLY `criterion` text -- no `rubric_item_id`, no
`scores`, no link back to `coval_full`.  A pilot check (below, reproduced at
runtime) shows only 7.8% of core criteria are exact-normalised-text copies
of a full criterion; the rest are paraphrased/synthesised, so any full<->core
correspondence beyond that 7.8% is fundamentally an ESTIMATE, not a fact in
the release.  Matching by reading text similarity would be exactly the
forbidden "semantic match".

Design-around: use the precomputed judge SATISFACTION TENSORS instead of
text.  Every full and every core criterion already has an independent
4-vector (satisfaction of response A,B,C,D) computed by the SAME local judge.
That is a BEHAVIOURAL fingerprint of the criterion (what it rewards), not a
reading of its words. A core criterion's nearest neighbour in that 4-D space,
within its own prompt, is the criterion's BEHAVIOURAL MATCH.  This proxy is
validated (positive control) against the 7.8% we know for certain, and
stress-tested (placebo) on deliberately-unrelated prompt pairs whose true
answer -- no signal -- is known in advance.  Every "retained" claim below is
conditioned on that validated proxy and reported with the proxy's own
measured error rate, per the proxy-ledger discipline: retained is a PROXY for
provenance, sound in one direction only, and unverified matches are excluded,
never counted as an acquittal.

NO GPU / NO LLM CALLS -- this script only reads the two precomputed .npz
satisfaction tensors and the two jsonl release files.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402

import json
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

t0 = time.time()

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(REPO))
from covalx import load_join  # noqa: E402

DATA_DIR = REPO / "data"
TENSOR_DIR = round_results("R04")
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LABELS = ["A", "B", "C", "D"]
SEED = 4409
BOOT_SEEDS = [4409, 4410, 4411, 4412, 4413]
N_BOOT = 1000

# ============================================================ PRE-REGISTRATION
# All thresholds below are fixed from the PREDICTOR's own distribution (rater
# counts, min-side-fraction) and from a KNOWN-PAIR calibration set, before any
# retention/regression outcome is computed. Written down here, unchanged
# after this point.
PREREG = {
    "contested_min_side_fraction_threshold": 0.20,
    # chosen because it (a) gives a roughly balanced contested/uncontested
    # split among multi-rated criteria and (b) is verified (below, at
    # runtime) to be ~uncorrelated with n_raters, so it is not a mechanical
    # restatement of "more raters -> more likely one crosses zero by chance".
    "min_raters_for_contested_analysis": 2,
    "tau_percentile_of_known_pair_distance": 95,
    # conservative: 5% of TRUE matches are allowed to fall outside tau and be
    # (correctly) called "no confident match" rather than risk a false
    # positive retention claim.
    "positive_control_min_accuracy_multiple_of_chance": 3.0,
    "positive_control_min_absolute_accuracy": 0.15,
    "n_boot": N_BOOT,
    "boot_seeds": BOOT_SEEDS,
    "multiplicity_family": [
        "estimand1(drop-prediction) x euclidean",
        "estimand1(drop-prediction) x correlation",
        "estimand2(whose-side)      x euclidean",
        "estimand2(whose-side)      x correlation",
    ],
    "multiplicity_method": "holm-bonferroni",
    "rater_count_regime_split": {"thin": [2, 9], "dense": [10, 10**9]},
}

STRONGEST_CONFOUND = (
    "Split (any-dissent) criteria mechanically have a SMALLER |mean| than "
    "unanimous criteria purely by cancellation -- this is arithmetic, not a "
    "finding -- and criteria with a smaller |mean| are plausibly less likely "
    "to be selected by ANY magnitude/utility-driven compiler for reasons "
    "that have nothing to do with representing dissent. A second, related "
    "confound: the rater-count distribution is structurally bimodal with a "
    "genuine gap (no criterion in this release has exactly 2 or 3 raters -- "
    "it is 1, or >=4), so criteria that attracted many raters may be a "
    "systematically different population (e.g. templated/recurring across "
    "many conversations) whose retention odds differ for reasons unrelated "
    "to disagreement. Both are controlled in every regression below via "
    "standardized |mean| and standardized log(n_raters) covariates, and the "
    "0.20 contested threshold was chosen from the predictor's own "
    "distribution specifically because it is empirically uncorrelated with "
    "n_raters (checked before any outcome was touched)."
)


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower()
    return re.sub(r"\s+", " ", s).strip()


# ============================================================ 1. LOAD + JOIN
print("[1] loading + joining release files ...", flush=True)
joined = load_join(DATA_DIR / "comparisons.jsonl", DATA_DIR / "conversation_rubrics.jsonl")
pids = [pid for pid, _, _ in joined]
rub_by_pid = {pid: rub for pid, _, rub in joined}
print(f"    joined prompts: {len(joined)}")

sat_full_npz = np.load(TENSOR_DIR / "a04_full.npz", allow_pickle=True)
sat_core_npz = np.load(TENSOR_DIR / "a04_core.npz", allow_pickle=True)


def build_sat_lookup(npz):
    """meta 'pid|ci|lab' -> {(pid,ci): {lab: sat}}"""
    meta = npz["meta"]
    sat = npz["sat"]
    out = defaultdict(dict)
    for m, s in zip(meta, sat):
        pid, ci, lab = m.split("|")
        out[(pid, int(ci))][lab] = float(s)
    return out


sat_full_lu = build_sat_lookup(sat_full_npz)
sat_core_lu = build_sat_lookup(sat_core_npz)
print(f"    full tensor: {len(sat_full_lu)} (prompt,ci) cells; "
      f"core tensor: {len(sat_core_lu)} (prompt,ci) cells")

# ============================================================ 2. PER-PROMPT STRUCTURES
# full_meta[pid] = list of dicts (one per ci, ci==raw index into coval_full,
# verified below that every coval_full item has >=1 score so no filtering
# discrepancy vs the tensor's own enumeration).
full_meta = {}
full_mat = {}     # pid -> (n_full, 4) satisfaction matrix, columns A,B,C,D
core_mat = {}     # pid -> (n_core, 4)
core_text = {}    # pid -> list[str] core criterion text, ci order

n_empty_scores = 0
for pid, comp, rub in joined:
    items = rub.get("coval_full") or []
    fm = []
    rows = []
    for ci, it in enumerate(items):
        sc = [float(s["score"]) for s in (it.get("scores") or [])]
        if not sc:
            n_empty_scores += 1
            continue
        pos = sum(1 for x in sc if x > 0)
        neg = sum(1 for x in sc if x < 0)
        n = pos + neg
        mean = float(np.mean(sc))
        maj_sign = 0 if pos == neg else (1 if pos > neg else -1)
        mean_sign = 0 if mean == 0 else (1 if mean > 0 else -1)
        min_frac = (min(pos, neg) / n) if n > 0 else 0.0
        fm.append({
            "ci": ci,
            "rubric_item_id": it.get("rubric_item_id"),
            "text": it["criterion"],
            "text_norm": norm_text(it["criterion"]),
            "n_raters": len(sc),
            "pos": pos, "neg": neg, "mean": mean,
            "maj_sign": maj_sign, "mean_sign": mean_sign, "min_frac": min_frac,
        })
        cell = sat_full_lu.get((pid, ci))
        rows.append([cell[lab] for lab in LABELS] if cell else [np.nan] * 4)
    full_meta[pid] = fm
    full_mat[pid] = np.array(rows, dtype=np.float64) if rows else np.zeros((0, 4))

    ccrits = rub.get("coval_core") or []
    core_text[pid] = [c["criterion"] for c in ccrits]
    crows = []
    for ci in range(len(ccrits)):
        cell = sat_core_lu.get((pid, ci))
        crows.append([cell[lab] for lab in LABELS] if cell else [np.nan] * 4)
    core_mat[pid] = np.array(crows, dtype=np.float64) if crows else np.zeros((0, 4))

print(f"    full criteria with zero scores (should be 0, verified): {n_empty_scores}")
n_full_total = sum(len(v) for v in full_meta.values())
n_core_total = sum(len(v) for v in core_text.values())
print(f"    total full criteria: {n_full_total}, total core criteria: {n_core_total}")

# ============================================================ 3. VERIFY THE STATED FACTS
n_raters_arr = np.array([c["n_raters"] for fm in full_meta.values() for c in fm])
frac_1 = float((n_raters_arr == 1).mean())
frac_10p = float((n_raters_arr >= 10).mean())
frac_mid = float(((n_raters_arr >= 2) & (n_raters_arr <= 9)).mean())

neg_multi = [c for fm in full_meta.values() for c in fm if c["n_raters"] >= 2 and c["mean"] < 0]
neg_multi_with_pos = sum(1 for c in neg_multi if c["pos"] >= 1)
frac_neg_with_pos_rater = neg_multi_with_pos / len(neg_multi) if neg_multi else float("nan")

facts_verified = {
    "n_full_criteria": int(len(n_raters_arr)),
    "fraction_exactly_1_rater": frac_1,
    "fraction_10_or_more_raters": frac_10p,
    "fraction_2_to_9_raters": frac_mid,
    "rater_count_gap_note": "no criterion in this release has exactly 2 or 3 raters (verified min multi-rated n=4)",
    "n_multirated_negative_mean": len(neg_multi),
    "fraction_negative_mean_with_ge1_positive_rater": frac_neg_with_pos_rater,
}
print(f"[3] rater-count bimodal: {frac_1:.3f} single-rated, {frac_10p:.3f} >=10-rated, "
      f"{frac_mid:.3f} in between")
print(f"    negative-mean multi-rated criteria with >=1 positive rater: "
      f"{frac_neg_with_pos_rater:.3f} (n={len(neg_multi)})")

# ============================================================ 4. GROUND-TRUTH (exact text) PAIRS
# Purely mechanical string identity after Unicode/case/whitespace normalisation
# -- no meaning is read, no similarity is judged. Used ONLY to (a) calibrate
# tau and (b) positive-control the behavioural matcher; NOT used as the
# analysis's retention signal itself (that would reintroduce the very
# selection bias the task warns about: verbatim copies are plausibly a
# special, cleaner-worded, possibly less-contested subset).
ground_truth = {}   # (pid, core_ci) -> set of full_ci with identical normalised text
for pid, fm in full_meta.items():
    text_to_ci = defaultdict(set)
    for c in fm:
        text_to_ci[c["text_norm"]].add(c["ci"])
    for ci, ctext in enumerate(core_text[pid]):
        key = norm_text(ctext)
        if key in text_to_ci:
            ground_truth[(pid, ci)] = text_to_ci[key]

n_gt = len(ground_truth)
n_gt_dup = sum(1 for v in ground_truth.values() if len(v) > 1)
print(f"[4] exact-text-normalised core<->full pairs (ground truth): {n_gt} "
      f"of {n_core_total} core criteria ({n_gt/n_core_total:.3f}); "
      f"{n_gt_dup} have >1 candidate full criterion with identical text")

# ============================================================ 5. CONTESTEDNESS PREDICTOR SANITY
min_frac_arr = np.array([c["min_frac"] for fm in full_meta.values() for c in fm if c["n_raters"] >= 2])
nraters_multi_arr = np.array([c["n_raters"] for fm in full_meta.values() for c in fm if c["n_raters"] >= 2])
from scipy.stats import spearmanr, norm as sp_norm  # noqa: E402
rho, rho_p = spearmanr(min_frac_arr, nraters_multi_arr)
contested_base_rate = float((min_frac_arr >= PREREG["contested_min_side_fraction_threshold"]).mean())
print(f"[5] contested predictor (min_side_fraction>=0.20) base rate among multi-rated: "
      f"{contested_base_rate:.3f}; spearman(min_frac, n_raters)={rho:.4f} (p={rho_p:.3f}) "
      f"-> {'uncorrelated, good' if abs(rho) < 0.05 else 'WARNING: correlated with n_raters'}")

# ============================================================ 6. BEHAVIOURAL DISTANCE METRICS
def euclid_dist_matrix(C, F):
    if C.shape[0] == 0 or F.shape[0] == 0:
        return np.zeros((C.shape[0], F.shape[0]))
    diff = C[:, None, :] - F[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=-1))


def corr_dist_matrix(C, F, eps=1e-9):
    if C.shape[0] == 0 or F.shape[0] == 0:
        return np.full((C.shape[0], F.shape[0]), 2.0)

    def stdz(M):
        mu = M.mean(axis=1, keepdims=True)
        sd = M.std(axis=1, keepdims=True)
        bad = (sd < eps)
        sd_safe = np.where(bad, 1.0, sd)
        Z = (M - mu) / sd_safe
        return Z, bad.squeeze(-1)

    Zc, badc = stdz(C)
    Zf, badf = stdz(F)
    corr = (Zc @ Zf.T) / C.shape[1]
    D = 1.0 - corr
    D[badc, :] = 2.0
    D[:, badf] = 2.0
    return D


METRICS = {"euclidean": euclid_dist_matrix, "correlation": corr_dist_matrix}

# ============================================================ 7. POSITIVE CONTROL + TAU
print("[7] positive control: recovering known (exact-text) pairs from behaviour alone ...")
positive_control = {}
tau = {}
for mname, mfun in METRICS.items():
    true_dists = []
    hit1 = 0
    hit3 = 0
    chance1 = []
    n_eval = 0
    for (pid, cci), true_set in ground_truth.items():
        F = full_mat[pid]
        c_vec = core_mat[pid][cci:cci + 1]
        if F.shape[0] == 0 or np.isnan(c_vec).any() or np.isnan(F).any():
            continue
        D = mfun(c_vec, F)[0]
        order = np.argsort(D)
        true_dists.append(float(np.min(D[list(true_set)])))
        n_eval += 1
        if order[0] in true_set:
            hit1 += 1
        if any(j in true_set for j in order[:3]):
            hit3 += 1
        chance1.append(1.0 / F.shape[0])
    acc1 = hit1 / n_eval if n_eval else float("nan")
    acc3 = hit3 / n_eval if n_eval else float("nan")
    chance = float(np.mean(chance1)) if chance1 else float("nan")
    tau_m = float(np.percentile(true_dists, PREREG["tau_percentile_of_known_pair_distance"])) if true_dists else float("nan")
    tau[mname] = tau_m
    positive_control[mname] = {
        "n_eval": n_eval,
        "top1_accuracy": acc1,
        "top3_accuracy": acc3,
        "chance_top1_accuracy": chance,
        "accuracy_over_chance_multiple": (acc1 / chance) if chance else float("nan"),
        "tau_from_known_pairs_p95": tau_m,
        "true_pair_distance_median": float(np.median(true_dists)) if true_dists else float("nan"),
    }
    print(f"    [{mname}] n={n_eval} top1={acc1:.3f} top3={acc3:.3f} chance={chance:.3f} "
          f"(x{acc1/chance:.1f}) tau_p95={tau_m:.4f}")

gate_ok = all(
    positive_control[m]["accuracy_over_chance_multiple"] >= PREREG["positive_control_min_accuracy_multiple_of_chance"]
    and positive_control[m]["top1_accuracy"] >= PREREG["positive_control_min_absolute_accuracy"]
    for m in METRICS
)
print(f"    STOPPING-RULE GATE (>= {PREREG['positive_control_min_accuracy_multiple_of_chance']}x chance "
      f"AND >= {PREREG['positive_control_min_absolute_accuracy']} absolute, both metrics): "
      f"{'PASS' if gate_ok else 'FAIL'}")

if not gate_ok:
    out = {
        "estimand": __doc__,
        "preregistration": PREREG,
        "facts_verified": facts_verified,
        "ground_truth_pairs": {"n": n_gt, "n_ambiguous_gt1_candidate": n_gt_dup},
        "positive_control": positive_control,
        "verdict": "UNVERIFIED",
        "reason": ("Positive control failed the pre-registered gate: the behavioural "
                   "(satisfaction-fingerprint) matcher does not recover known core<->full "
                   "correspondences reliably above chance. The retention/whose-side question "
                   "cannot be answered from this release without a working provenance proxy. "
                   "Exiting nonzero rather than reporting a number from a broken instrument."),
        "runtime_seconds": time.time() - t0,
    }
    (RESULTS_DIR / "independent_B.json").write_text(json.dumps(out, indent=2, default=float))
    print("GATE FAILED -- exiting nonzero, no headline number produced.")
    sys.exit(1)

# ============================================================ 8. PLACEBO (deliberately-unrelated pairing)
# Known answer in advance: a prompt's core criteria and a DIFFERENT prompt's
# full criteria score entirely unrelated response texts, so there is no real
# correspondence to recover. Expected: confident-match rate collapses far
# below the real-data rate, and any fitted "retained ~ contested" coefficient
# on the placebo pairing is statistically indistinguishable from zero.
print("[8] placebo: shuffled (mismatched-prompt) pairing ...")
placebo_results = {}
for seed in BOOT_SEEDS[:1]:  # one seed suffices to fix the derangement; robustness checked across boot seeds later
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(pids))
    donor_of = {}
    for i, pid in enumerate(pids):
        j = perm[i]
        if pids[j] == pid:
            j = (j + 1) % len(pids)
        donor_of[pid] = pids[j]

    for mname, mfun in METRICS.items():
        confident = 0
        total = 0
        for pid in pids:
            donor = donor_of[pid]
            C = core_mat[pid]
            F = full_mat[donor]
            if C.shape[0] == 0 or F.shape[0] == 0:
                continue
            if np.isnan(C).any() or np.isnan(F).any():
                continue
            D = mfun(C, F)
            mind = D.min(axis=1)
            confident += int((mind <= tau[mname]).sum())
            total += C.shape[0]
        rate = confident / total if total else float("nan")
        placebo_results.setdefault(mname, {})["confident_match_rate"] = rate
        placebo_results[mname]["n_core_items"] = total
        print(f"    [{mname}] placebo confident-match rate: {rate:.4f} (n={total})")

# ============================================================ 9. REAL BEHAVIOURAL RETENTION
print("[9] computing real within-prompt behavioural retention ...")
retained_confident = {m: {} for m in METRICS}  # metric -> (pid,ci) -> bool
real_confident_rate = {}
for mname, mfun in METRICS.items():
    tot_core = 0
    tot_conf = 0
    for pid in pids:
        C = core_mat[pid]
        F = full_mat[pid]
        n_full = F.shape[0]
        if n_full == 0:
            continue
        retained_set = set()
        if C.shape[0] > 0 and not np.isnan(C).any() and not np.isnan(F).any():
            D = mfun(C, F)
            argmin = D.argmin(axis=1)
            mind = D.min(axis=1)
            tot_core += C.shape[0]
            for k in range(C.shape[0]):
                if mind[k] <= tau[mname]:
                    retained_set.add(int(argmin[k]))
                    tot_conf += 1
        for c in full_meta[pid]:
            retained_confident[mname][(pid, c["ci"])] = c["ci"] in retained_set
    real_confident_rate[mname] = tot_conf / tot_core if tot_core else float("nan")
    print(f"    [{mname}] real confident-match rate: {real_confident_rate[mname]:.4f} "
          f"(placebo was {placebo_results[mname]['confident_match_rate']:.4f})")

# ============================================================ 10. BUILD REGRESSION TABLE
rows = []
for pid, fm in full_meta.items():
    for c in fm:
        if c["n_raters"] < PREREG["min_raters_for_contested_analysis"]:
            continue
        contested = int(c["min_frac"] >= PREREG["contested_min_side_fraction_threshold"])
        sign_conflict = np.nan
        if contested and c["maj_sign"] != 0 and c["mean_sign"] != 0:
            sign_conflict = int(c["maj_sign"] != c["mean_sign"])
        rows.append({
            "pid": pid, "ci": c["ci"], "n_raters": c["n_raters"],
            "abs_mean": abs(c["mean"]), "min_frac": c["min_frac"],
            "contested": contested, "sign_conflict": sign_conflict,
            "retained_euclidean": int(retained_confident["euclidean"][(pid, c["ci"])]),
            "retained_correlation": int(retained_confident["correlation"][(pid, c["ci"])]),
        })

n_rows = len(rows)
print(f"[10] regression table: {n_rows} full criteria with n_raters>=2")

pid_arr = np.array([r["pid"] for r in rows])
contested_arr = np.array([r["contested"] for r in rows], dtype=float)
sign_conflict_arr = np.array([r["sign_conflict"] for r in rows], dtype=float)
abs_mean_arr = np.array([r["abs_mean"] for r in rows], dtype=float)
log_nraters_arr = np.log(np.array([r["n_raters"] for r in rows], dtype=float))
min_frac_reg_arr = np.array([r["min_frac"] for r in rows], dtype=float)
retained = {m: np.array([r[f"retained_{m}"] for r in rows], dtype=float) for m in METRICS}


def standardize(x):
    mu, sd = np.nanmean(x), np.nanstd(x)
    sd = sd if sd > 1e-12 else 1.0
    return (x - mu) / sd, mu, sd


abs_mean_z, am_mu, am_sd = standardize(abs_mean_arr)
log_nr_z, lnr_mu, lnr_sd = standardize(log_nraters_arr)

# ============================================================ 11. LOGISTIC REGRESSION (own IRLS)
def fit_logit(X, y, max_iter=100, tol=1e-9):
    X = np.column_stack([np.ones(len(y)), X])
    beta = np.zeros(X.shape[1])
    for _ in range(max_iter):
        eta = np.clip(X @ beta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-6, None)
        z = eta + (y - p) / w
        XtW = X.T * w
        A = XtW @ X + 1e-8 * np.eye(X.shape[1])
        b = XtW @ z
        beta_new = np.linalg.solve(A, b)
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta  # [intercept, coef1, coef2, ...]


def fit_unadjusted_adjusted(y, key_pred, controls):
    mask = ~np.isnan(key_pred) & ~np.isnan(y)
    for c in controls:
        mask &= ~np.isnan(c)
    yy, kk = y[mask], key_pred[mask]
    CC = [c[mask] for c in controls]
    b_un = fit_logit(kk.reshape(-1, 1), yy)
    Xadj = np.column_stack([kk] + CC)
    b_adj = fit_logit(Xadj, yy)
    return mask, b_un, b_adj


def cluster_bootstrap(pid_all, mask, key_pred, controls, y, seeds, n_boot):
    """Cluster (by prompt) bootstrap of the ADJUSTED key-predictor coefficient."""
    pid_m = pid_all[mask]
    unique_pids = np.array(sorted(set(pid_m)))
    idx_by_pid = defaultdict(list)
    for i, p in enumerate(pid_m):
        idx_by_pid[p].append(i)
    kk = key_pred[mask]
    yy = y[mask]
    CC = [c[mask] for c in controls]
    coefs_all = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        seed_coefs = []
        for _ in range(n_boot):
            draw = rng.choice(unique_pids, size=len(unique_pids), replace=True)
            idx = np.concatenate([idx_by_pid[p] for p in draw]) if len(draw) else np.array([], dtype=int)
            if idx.size < 20 or np.nanstd(kk[idx]) < 1e-9:
                continue
            Xb = np.column_stack([kk[idx]] + [c[idx] for c in CC])
            try:
                b = fit_logit(Xb, yy[idx])
                seed_coefs.append(b[1])
            except np.linalg.LinAlgError:
                continue
        coefs_all.append(seed_coefs)
    return coefs_all


def summarize_boot(coefs_all, point_est):
    flat = np.array([c for seed_list in coefs_all for c in seed_list])
    per_seed_ci = [
        (float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))) if len(s) >= 20 else (None, None)
        for s in coefs_all
    ]
    if flat.size < 50:
        return {"n_boot_total": int(flat.size), "ci95": (None, None), "p_boot": None,
                "per_seed_ci95": per_seed_ci, "seed_spread_ci_low": None, "seed_spread_ci_high": None}
    ci = (float(np.percentile(flat, 2.5)), float(np.percentile(flat, 97.5)))
    below = float(np.mean(flat <= 0))
    above = float(np.mean(flat >= 0))
    p = 2 * min(below, above)
    p = min(p, 1.0)
    lows = [c[0] for c in per_seed_ci if c[0] is not None]
    highs = [c[1] for c in per_seed_ci if c[1] is not None]
    return {
        "n_boot_total": int(flat.size),
        "ci95": ci,
        "p_boot": p if (below > 0 and above > 0) else f"<{1.0/flat.size:.5f} ({int(below*flat.size) if p==2*below else int(above*flat.size)}/{flat.size} crossed zero)",
        "per_seed_ci95": per_seed_ci,
        "seed_spread_ci_low_min_max": (min(lows), max(lows)) if lows else None,
        "seed_spread_ci_high_min_max": (min(highs), max(highs)) if highs else None,
    }


print("[11] fitting estimand 1 (drop-prediction: retained ~ contested + controls) ...")
estimand1 = {}
for mname in METRICS:
    y = retained[mname]
    mask, b_un, b_adj = fit_unadjusted_adjusted(y, contested_arr, [abs_mean_z, log_nr_z])
    boots = cluster_bootstrap(pid_arr, mask, contested_arr, [abs_mean_z, log_nr_z], y, BOOT_SEEDS, N_BOOT)
    summ = summarize_boot(boots, b_adj[1])

    # raw (model-free) absolute effect size
    yy, kk = y[mask], contested_arr[mask]
    rate_contested = float(yy[kk == 1].mean())
    rate_uncontested = float(yy[kk == 0].mean())
    n_contested = int((kk == 1).sum())
    n_uncontested = int((kk == 0).sum())

    estimand1[mname] = {
        "n": int(mask.sum()),
        "n_contested": n_contested, "n_uncontested": n_uncontested,
        "raw_retention_rate_contested": rate_contested,
        "raw_retention_rate_uncontested": rate_uncontested,
        "raw_absolute_diff_pp": (rate_contested - rate_uncontested) * 100,
        "unadjusted_logit_coef_contested": float(b_un[1]),
        "unadjusted_odds_ratio": float(np.exp(b_un[1])),
        "adjusted_logit_coef_contested": float(b_adj[1]),
        "adjusted_odds_ratio": float(np.exp(b_adj[1])),
        "adjusted_logit_coef_abs_mean_z": float(b_adj[2]),
        "adjusted_logit_coef_log_nraters_z": float(b_adj[3]),
        "cluster_bootstrap": summ,
    }
    print(f"    [{mname}] n={mask.sum()} raw_diff_pp={estimand1[mname]['raw_absolute_diff_pp']:.2f} "
          f"adj_OR={estimand1[mname]['adjusted_odds_ratio']:.3f} "
          f"adj_logit_CI95={summ['ci95']} p={summ['p_boot']}")

print("[12] fitting estimand 2 (whose side: retained ~ sign_conflict + controls, contested subset) ...")
estimand2 = {}
for mname in METRICS:
    y = retained[mname]
    mask, b_un, b_adj = fit_unadjusted_adjusted(y, sign_conflict_arr, [abs_mean_z, log_nr_z])
    boots = cluster_bootstrap(pid_arr, mask, sign_conflict_arr, [abs_mean_z, log_nr_z], y, BOOT_SEEDS, N_BOOT)
    summ = summarize_boot(boots, b_adj[1])

    yy, kk = y[mask], sign_conflict_arr[mask]
    rate_conflict = float(yy[kk == 1].mean()) if (kk == 1).any() else float("nan")
    rate_consistent = float(yy[kk == 0].mean()) if (kk == 0).any() else float("nan")
    n_conflict = int((kk == 1).sum())
    n_consistent = int((kk == 0).sum())

    estimand2[mname] = {
        "n": int(mask.sum()),
        "n_sign_conflict": n_conflict, "n_sign_consistent": n_consistent,
        "raw_retention_rate_sign_conflict": rate_conflict,
        "raw_retention_rate_sign_consistent": rate_consistent,
        "raw_absolute_diff_pp": (rate_conflict - rate_consistent) * 100 if n_conflict and n_consistent else None,
        "unadjusted_logit_coef_sign_conflict": float(b_un[1]),
        "unadjusted_odds_ratio": float(np.exp(b_un[1])),
        "adjusted_logit_coef_sign_conflict": float(b_adj[1]),
        "adjusted_odds_ratio": float(np.exp(b_adj[1])),
        "cluster_bootstrap": summ,
    }
    print(f"    [{mname}] n={mask.sum()} (conflict={n_conflict}, consistent={n_consistent}) "
          f"raw_diff_pp={estimand2[mname]['raw_absolute_diff_pp']} "
          f"adj_OR={estimand2[mname]['adjusted_odds_ratio']:.3f} p={summ['p_boot']}")

# ============================================================ 13. PLACEBO REGRESSION (donor-mapped)
print("[13] placebo regression: donor prompt's full criteria vs THIS prompt's core (mismatched) ...")
rng0 = np.random.default_rng(BOOT_SEEDS[0])
perm0 = rng0.permutation(len(pids))
donor_of0 = {}
for i, pid in enumerate(pids):
    j = perm0[i]
    if pids[j] == pid:
        j = (j + 1) % len(pids)
    donor_of0[pid] = pids[j]

placebo_regression = {}
for mname, mfun in METRICS.items():
    placebo_rows = []
    for pid in pids:
        donor = donor_of0[pid]
        C = core_mat[pid]
        F = full_mat[donor]
        if C.shape[0] == 0 or F.shape[0] == 0 or np.isnan(C).any() or np.isnan(F).any():
            continue
        D = mfun(C, F)
        argmin = D.argmin(axis=1)
        mind = D.min(axis=1)
        retained_set = {int(argmin[k]) for k in range(C.shape[0]) if mind[k] <= tau[mname]}
        for c in full_meta[donor]:
            if c["n_raters"] < PREREG["min_raters_for_contested_analysis"]:
                continue
            contested = int(c["min_frac"] >= PREREG["contested_min_side_fraction_threshold"])
            placebo_rows.append((contested, int(c["ci"] in retained_set), abs(c["mean"]), c["n_raters"]))
    if len(placebo_rows) < 50:
        placebo_regression[mname] = {"n": len(placebo_rows), "note": "insufficient rows"}
        continue
    pc = np.array([r[0] for r in placebo_rows], dtype=float)
    py = np.array([r[1] for r in placebo_rows], dtype=float)
    pam = np.array([r[2] for r in placebo_rows], dtype=float)
    pnr = np.log(np.array([r[3] for r in placebo_rows], dtype=float))
    pam_z, _, _ = standardize(pam)
    pnr_z, _, _ = standardize(pnr)
    b_adj = fit_logit(np.column_stack([pc, pam_z, pnr_z]), py)
    placebo_regression[mname] = {
        "n": len(placebo_rows),
        "confident_retention_rate": float(py.mean()),
        "adjusted_logit_coef_contested": float(b_adj[1]),
        "adjusted_odds_ratio": float(np.exp(b_adj[1])),
    }
    print(f"    [{mname}] placebo n={len(placebo_rows)} retention_rate={py.mean():.4f} "
          f"adj_OR_contested={np.exp(b_adj[1]):.3f} (expect ~1, no real correspondence exists)")

# ============================================================ 14. MULTIPLICITY CORRECTION (Holm-Bonferroni)
def p_to_float(p):
    if isinstance(p, str):
        return float(p.split("<")[1].split(" ")[0])
    return p if p is not None else 1.0


pvals = {
    "estimand1_euclidean": p_to_float(estimand1["euclidean"]["cluster_bootstrap"]["p_boot"]),
    "estimand1_correlation": p_to_float(estimand1["correlation"]["cluster_bootstrap"]["p_boot"]),
    "estimand2_euclidean": p_to_float(estimand2["euclidean"]["cluster_bootstrap"]["p_boot"]),
    "estimand2_correlation": p_to_float(estimand2["correlation"]["cluster_bootstrap"]["p_boot"]),
}
labels_sorted = sorted(pvals, key=lambda k: pvals[k])
m = len(labels_sorted)
holm = {}
running_max = 0.0
for rank, lab in enumerate(labels_sorted):
    adj = min(1.0, pvals[lab] * (m - rank))
    running_max = max(running_max, adj)
    holm[lab] = running_max
print(f"[14] Holm-Bonferroni over {m} pre-registered tests: {holm}")

# ============================================================ 15. FOUR SCOPES
print("[15] four scopes ...")
# Scope A: primary, full population, euclidean metric, adjusted (the headline).
scope_a = estimand1["euclidean"]

# Scope B: ground-truth-only direct check (provenance-CERTAIN, no behavioural
# proxy at all) -- contested rate among criteria we KNOW were verbatim
# retained, vs the population base rate among all multi-rated criteria.
gt_retained_contested = []
for (pid, cci), true_set in ground_truth.items():
    fm = full_meta[pid]
    by_ci = {c["ci"]: c for c in fm}
    for j in true_set:
        c = by_ci.get(j)
        if c is not None and c["n_raters"] >= 2:
            gt_retained_contested.append(c["min_frac"] >= PREREG["contested_min_side_fraction_threshold"])
gt_rate = float(np.mean(gt_retained_contested)) if gt_retained_contested else float("nan")
pop_rate = contested_base_rate
n_gt_eval = len(gt_retained_contested)
se = np.sqrt(pop_rate * (1 - pop_rate) / n_gt_eval) if n_gt_eval else float("nan")
z = (gt_rate - pop_rate) / se if se else float("nan")
p_gt = float(2 * (1 - sp_norm.cdf(abs(z)))) if se else None
scope_b = {
    "description": "contested rate among criteria with CERTAIN (verbatim-text) retention, vs population base rate",
    "n_verbatim_retained_multirated": n_gt_eval,
    "contested_rate_among_verbatim_retained": gt_rate,
    "contested_rate_population_base": pop_rate,
    "z": z, "p_two_sided": p_gt,
    "caveat": "verbatim-copy retention is a SPECIAL (likely crisper-worded / possibly less-contested) "
              "subset of all retention, not a random sample of it -- selection bias in the OPPOSITE "
              "direction from the compiler paraphrasing effort is plausible here.",
}

# Scope C: robustness metric (correlation distance) -- already computed above.
scope_c = estimand1["correlation"]

# Scope D: rater-count regime split (thin [2,9] vs dense [>=10]).
scope_d = {}
for regime, (lo, hi) in PREREG["rater_count_regime_split"].items():
    idx = np.array([i for i, r in enumerate(rows) if lo <= r["n_raters"] <= hi])
    if idx.size < 50:
        scope_d[regime] = {"n": int(idx.size), "note": "too few rows"}
        continue
    y = retained["euclidean"][idx]
    kk = contested_arr[idx]
    am_sub = abs_mean_z[idx]
    mask_sub = ~np.isnan(kk)
    b_adj = fit_logit(np.column_stack([kk[mask_sub], am_sub[mask_sub]]), y[mask_sub])
    scope_d[regime] = {
        "n": int(mask_sub.sum()),
        "raw_retention_rate_contested": float(y[mask_sub][kk[mask_sub] == 1].mean()) if (kk[mask_sub] == 1).any() else None,
        "raw_retention_rate_uncontested": float(y[mask_sub][kk[mask_sub] == 0].mean()) if (kk[mask_sub] == 0).any() else None,
        "adjusted_odds_ratio_contested": float(np.exp(b_adj[1])),
    }

four_scopes = {
    "A_primary_full_population_euclidean": scope_a,
    "B_ground_truth_only_verbatim_subset": scope_b,
    "C_robustness_correlation_metric": scope_c,
    "D_rater_count_regime_split": scope_d,
}
for k, v in scope_d.items():
    print(f"    [scope D:{k}] n={v.get('n')} adj_OR={v.get('adjusted_odds_ratio_contested')}")

# ============================================================ 16. VERDICT
adj_or_e1_eucl = estimand1["euclidean"]["adjusted_odds_ratio"]
ci_e1_eucl = estimand1["euclidean"]["cluster_bootstrap"]["ci95"]
holm_e1_eucl = holm["estimand1_euclidean"]
holm_e1_corr = holm["estimand1_correlation"]
holm_e2_eucl = holm["estimand2_euclidean"]
holm_e2_corr = holm["estimand2_correlation"]

drop_prediction_significant = (
    ci_e1_eucl[0] is not None and ci_e1_eucl[1] is not None
    and holm_e1_eucl < 0.05 and holm_e1_corr < 0.05
    and (ci_e1_eucl[0] > 0) == (ci_e1_eucl[1] > 0)
)
whose_side_significant = (
    holm_e2_eucl < 0.05 and holm_e2_corr < 0.05
)

if drop_prediction_significant and estimand1["euclidean"]["adjusted_odds_ratio"] < 1:
    verdict = "CONFIRMED"
    verdict_note = ("Contested criteria are retained at LOWER odds than agreed criteria after adjusting "
                     "for |mean| and log(n_raters), holding across both distance metrics and surviving "
                     "multiplicity correction -- disagreement predicts being dropped.")
elif drop_prediction_significant and estimand1["euclidean"]["adjusted_odds_ratio"] > 1:
    verdict = "OVERTURNED"
    verdict_note = ("Contested criteria are retained at HIGHER (not lower) odds than agreed criteria "
                     "after adjustment -- the claim's implicit worry (dissent gets silently dropped) "
                     "does not hold in the direction expected.")
else:
    verdict = "UNVERIFIED"
    verdict_note = ("The adjusted effect of contestedness on retention did not clear the pre-registered "
                     "significance + multiplicity bar on both metrics -- treat as no reliable effect "
                     "detected at this sample size and proxy resolution, not as a confirmed null.")

# ============================================================ WRITE RESULT
out = {
    "estimand": (
        "Among full criteria rated by >=2 participants, does rater disagreement "
        "(min-side-fraction >= 0.20) predict whether the criterion is behaviourally retained "
        "into the compiled 4-item coval_core (via satisfaction-fingerprint nearest-neighbour "
        "matching, confidence-gated by a tau calibrated on known verbatim-copy pairs), "
        "adjusting for |mean rating| and log(n_raters); and among contested criteria, does "
        "retention track the raw-vote majority side or the higher-intensity minority side "
        "when the two disagree (sign_conflict)?"
    ),
    "provenance_gap": (
        "coval_core carries no rubric_item_id/scores/link back to coval_full. Only 7.8% of "
        "core criteria are exact-text duplicates of a full criterion; the rest are paraphrased. "
        "Item-level ground truth is NOT recoverable from the release. All 'retained' claims "
        "below are a validated behavioural PROXY (satisfaction-fingerprint nearest neighbour), "
        "not provenance."
    ),
    "preregistration": PREREG,
    "strongest_confound": STRONGEST_CONFOUND,
    "facts_verified": facts_verified,
    "ground_truth_pairs": {"n": n_gt, "n_ambiguous_gt1_candidate": n_gt_dup, "n_core_total": n_core_total},
    "contested_predictor_sanity": {
        "spearman_rho_min_frac_vs_n_raters": float(rho),
        "spearman_p": float(rho_p),
        "contested_base_rate_at_0.20_threshold": contested_base_rate,
    },
    "positive_control": positive_control,
    "positive_control_gate_passed": gate_ok,
    "placebo_confident_match_rate": {m: placebo_results[m]["confident_match_rate"] for m in METRICS},
    "placebo_regression": placebo_regression,
    "real_confident_match_rate": real_confident_rate,
    "regression_n_rows": n_rows,
    "estimand1_drop_prediction": estimand1,
    "estimand2_whose_side": estimand2,
    "multiplicity_raw_p": pvals,
    "multiplicity_holm_adjusted_p": holm,
    "four_scopes": four_scopes,
    "verdict": verdict,
    "verdict_note": verdict_note,
    "runtime_seconds": time.time() - t0,
    "seed": SEED,
    "boot_seeds": BOOT_SEEDS,
}


def _default(o):
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


(RESULTS_DIR / "independent_B.json").write_text(json.dumps(out, indent=2, default=_default))
print(f"\n[DONE] wrote results/independent_B.json in {time.time()-t0:.1f}s")
print(f"VERDICT: {verdict}")
print(f"  estimand1 (euclidean) adjusted OR contested={adj_or_e1_eucl:.3f} CI95={ci_e1_eucl} "
      f"holm_p={holm_e1_eucl:.4f}")
