#!/usr/bin/env python
"""independent_A.py -- does coval_core retain the NEGATIVELY-rated quarter of coval_full?

======================================================================================
ESTIMAND (fixed before any correlation/regression number is computed; group-size and
prompt-count facts below were inspected during design and are NOT the outcome variable)
======================================================================================
For a prompt with 4 candidate responses (A-D), partition the coval_full criteria of
that prompt into POS (mean human importance score > 0, "should do") and NEG (mean
score < 0, "should NOT do") using the sign of the mean over that criterion's raters
(criteria with mean == 0 are dropped -- ambiguous polarity, ~0.16% of criteria).

For each (prompt, response) unit define three per-unit scalars from the precomputed
judge satisfaction tensors (sigmoid logit-gap, "does response literally satisfy this
criterion's text"):
    S_pos  = mean judge-satisfaction over that prompt's POS full criteria
    S_neg  = mean judge-satisfaction over that prompt's NEG full criteria
    S_core = mean judge-satisfaction over that prompt's coval_core criteria (all of
             them; coval_core is written entirely in positive prescriptive form)

Center each of S_pos, S_neg, S_core WITHIN prompt (subtract the prompt's own mean
over its up-to-4 responses). This isolates response-level relative standing and
removes prompt-level confounds (topic, criterion count, baseline judge calibration).

THE ESTIMAND is the ratio
    rho = |r_neg| / |r_pos|
where r_pos = corr(S_pos_centered, S_core_centered) and r_neg = corr(S_neg_centered,
S_core_centered), pooled over all qualifying (prompt, response) units, prompt-clustered
for inference. |r| (not signed r) is used because a FAITHFUL compiler could transcribe
a "should NOT do X" concern into coval_core either as a same-polarity echo (a core item
whose satisfaction rises when the full criterion is satisfied) or as a polarity
INVERSION (a core item like "remain neutral" whose satisfaction FALLS when the response
does the negatively-rated thing X) -- both are legitimate faithful encodings and both
show up as a nonzero |r|, just with opposite sign. Sign is reported as a secondary
diagnostic of *how* NEG content is encoded, not as part of the primary retention
metric. rho ~= 1 means core carries information traceable to NEG criteria at a rate
comparable to POS criteria (faithful); rho ~= 0 means core is functionally blind to
the negatively-rated quarter of the input (unfaithful, positivity-only compilation).

REGIME / SCOPE this estimand is defined over: prompts with >=1 POS and >=1 NEG
criterion (after dropping mean==0), all 4 response labels scored in both the a04_full
and a04_core tensors. Population, instrument, baseline and regime are restated in the
JSON output under `scopes`.

======================================================================================
STRONGEST CONFOUND (named before running; hint from the task: "what differs between
the two criterion groups OTHER than their polarity")
======================================================================================
GROUP-SIZE / RELIABILITY CONFOUND. NEG criteria are ~1/4 as numerous as POS criteria
per prompt (measured at design time: mean NEG count ~3.7 vs POS ~11.5). S_neg is
therefore a mean over far fewer items than S_pos, so it is mechanically NOISIER
(higher sampling variance of the per-response mean) purely from having a smaller
denominator -- classic errors-in-variables attenuation. This alone would push
r_neg toward 0 relative to r_pos and make a PERFECTLY faithful core look like it
"drops" NEG content, even if the population-level (per-criterion) relationship is
identical in strength. A secondary version of the same confound: NEG criteria are
more likely phrased with negation / contrastive language ("... instead of remaining
neutral"), which the local judge may resolve less crisply than plain positive
imperatives, adding instrument noise specifically to the NEG arm.

CONTROLS RUN IN THIS SCRIPT (same run, not a follow-up):
  (A) Size-matched subsample: for every prompt, subsample POS down to
      min(n_pos, n_neg) items before forming S_pos_matched, so both arms average the
      same number of criteria. Repeated over 5 seeds (8101-8105); report mean+spread
      of rho_matched. If the raw rho gap collapses under size-matching, the size
      confound was (part of) the story; if it survives, size is not the explanation.
  (B) Split-half reliability + Spearman-Brown attenuation correction: for each group,
      split its criteria into two random halves (5 seeds), correlate the two halves'
      response-level means (within-prompt centered) to get a reliability estimate for
      POS and NEG separately, then attenuation-correct r_pos and r_neg by
      r_corrected = r_observed / sqrt(reliability) and recompute rho_corrected.

======================================================================================
POSITIVE CONTROL + PLACEBO (mandatory before trusting any null)
======================================================================================
POSITIVE CONTROL: the judge signal itself must predict something KNOWN -- the human
"world" pairwise preference (comparisons.jsonl, human_pairs()). Build a
desirability-aligned score Q = S_pos (already "high=good") minus nothing, and for NEG,
its ALIGNED form Q_neg_aligned = 1 - S_neg ("high=good", since satisfying a
negatively-rated criterion is bad). Check pairwise accuracy of Q_pos_alone,
Q_neg_aligned_alone, and Q_neg_UNFLIPPED (=S_neg, i.e. the wrong-sign version) against
human "world" ranking pairs, pooled with prompt-cluster bootstrap CIs. Requirement to
proceed: both Q_pos_alone and Q_neg_aligned_alone beat 50% with CI excluding 0.5. As a
built-in sanity check on the sign convention itself: Q_neg_aligned_alone accuracy must
exceed Q_neg_UNFLIPPED accuracy (confirms "negative score = satisfying it is bad" is
the right reading, not an assumption taken on faith).

PLACEBO / ARITHMETIC REFERENCE: inject two synthetic per-unit scores built directly
from S_core_centered with i.i.d. Gaussian noise added at levels chosen to give a KNOWN
correlation before noise is added -- SyntheticStrong (target r=0.60) and SyntheticNull
(target r=0.00, pure independent noise). Push both through the IDENTICAL
centering -> pooled-correlation -> cluster-bootstrap code path used for the real
r_pos/r_neg. Requirement to proceed: recovered r for SyntheticStrong lands within
+/-0.12 of 0.60 and the 95% CI for SyntheticNull's r includes 0. Failing this means the
estimator itself is broken and no number from it should be trusted.

======================================================================================
PRE-REGISTERED THRESHOLDS (fixed here, before rho_hat is computed)
======================================================================================
ALPHA            = 0.05 (two-sided, all CIs)
MIN_PROMPTS      = 100      -- fewer qualifying prompts => UNVERIFIED (underpowered)
RHO_CONFIRM      = 0.50     -- rho_hat >= this AND CI(r_neg) excludes 0 => retention
                                at least half as strong as the positive arm
RHO_RESCUE       = 0.50     -- the SAME bar applied to rho_matched (control A) and
                                rho_corrected (control B); both controls must also
                                clear it for a CONFIRMED verdict to stand
POS_CTRL_MIN_ACC = 0.50     -- pairwise accuracy must exceed this with CI excluding
                                0.5 for BOTH Q_pos_alone and Q_neg_aligned_alone
PLACEBO_TOL      = 0.12     -- |r_hat - 0.60| tolerance for SyntheticStrong recovery

DECISION RULE (mechanically applied at the end, not adjusted post-hoc):
  UNVERIFIED if: positive control fails, OR placebo fails, OR
                 n_qualifying_prompts < MIN_PROMPTS, OR
                 the two controls (A, B) disagree with the raw verdict in a way that
                 flips CONFIRMED<->OVERTURNED.
  CONFIRMED  if: (not UNVERIFIED) AND rho_hat >= RHO_CONFIRM AND CI(r_neg) excludes 0
                 AND rho_matched (mean over seeds) >= RHO_RESCUE
                 AND rho_corrected >= RHO_RESCUE
  OVERTURNED otherwise (rho_hat < RHO_CONFIRM, or CI(r_neg) includes 0, or the
                 controls do not rescue a borderline raw rho).

MULTIPLICITY: the primary confirmatory test is the single (rho_hat, CI(r_neg)) pair
above. Three secondary/robustness tests are also computed and Holm-Bonferroni
corrected as a family of 3 (alpha=0.05): (1) joint-regression standardized partial
coefficient for NEG != 0, (2) Spearman-rank version of r_neg != 0, (3) size-matched
r_neg != 0 (control A significance). These do not gate the primary verdict; they are
reported as corroboration/context only. The positive control and placebo are
instrument-validity gates, not part of the hypothesis family (pre-registration
convention: a confirmatory test's family is the claims being scored, not the checks
that must pass before the instrument is trusted at all).

SEED = 8101 (base). Bootstrap and subsampling use seeds 8101..8105 (5 seeds).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from covalx import load_join, human_pairs  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- pre-registered knobs
BASE_SEED = 8101
SEEDS = [BASE_SEED + i for i in range(5)]
N_BOOT = 2000          # bootstrap resamples per seed
ALPHA = 0.05
MIN_PROMPTS = 100
RHO_CONFIRM = 0.50
RHO_RESCUE = 0.50
POS_CTRL_MIN_ACC = 0.50
PLACEBO_TARGET_R = 0.60
PLACEBO_TOL = 0.12


def rng_for(seed: int, salt: int) -> np.random.Generator:
    return np.random.default_rng(seed * 1000 + salt)


# ============================================================================ 1. LOAD
print("[1/8] loading join + tensors ...", flush=True)
joined = load_join(REPO / "data" / "comparisons.jsonl", REPO / "data" / "conversation_rubrics.jsonl")

d_full = np.load(REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz", allow_pickle=True)
d_core = np.load(REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz", allow_pickle=True)
idx_full = {k: i for i, k in enumerate(d_full["meta"])}
idx_core = {k: i for i, k in enumerate(d_core["meta"])}
sat_full = d_full["sat"]
sat_core = d_core["sat"]

LABELS = ("A", "B", "C", "D")

# ============================================================== 2. BUILD PER-UNIT TABLE
print("[2/8] building per (prompt,response) table ...", flush=True)
records = []           # dict per (prompt,response): pid, label, S_pos, S_neg, S_core
skip_reasons = {"n_pos==0": 0, "n_neg==0": 0, "core_empty": 0,
                 "missing_full_key": 0, "missing_core_key": 0, "not_all_4_labels": 0}
n_prompts_seen = 0
n_prompts_qualifying = 0
pos_count_per_prompt, neg_count_per_prompt = [], []

for pid, comp, rub in joined:
    n_prompts_seen += 1
    full_list = rub["coval_full"]
    core_list = rub["coval_core"]
    if not core_list:
        skip_reasons["core_empty"] += 1
        continue

    pos_idx, neg_idx = [], []
    for i, c in enumerate(full_list):
        scores = [s["score"] for s in c.get("scores", [])]
        if not scores:
            continue
        m = float(np.mean(scores))
        if m > 0:
            pos_idx.append(i)
        elif m < 0:
            neg_idx.append(i)
        # m == 0 dropped (ambiguous polarity)

    if len(pos_idx) == 0:
        skip_reasons["n_pos==0"] += 1
        continue
    if len(neg_idx) == 0:
        skip_reasons["n_neg==0"] += 1
        continue

    # gather per-response satisfaction, requiring full 4-label coverage
    unit_rows = []
    ok = True
    for label in LABELS:
        pos_vals, neg_vals, core_vals = [], [], []
        for i in pos_idx:
            key = f"{pid}|{i}|{label}"
            j = idx_full.get(key)
            if j is None:
                skip_reasons["missing_full_key"] += 1
                ok = False
                break
            pos_vals.append(sat_full[j])
        if not ok:
            break
        for i in neg_idx:
            key = f"{pid}|{i}|{label}"
            j = idx_full.get(key)
            if j is None:
                skip_reasons["missing_full_key"] += 1
                ok = False
                break
            neg_vals.append(sat_full[j])
        if not ok:
            break
        for i in range(len(core_list)):
            key = f"{pid}|{i}|{label}"
            j = idx_core.get(key)
            if j is None:
                skip_reasons["missing_core_key"] += 1
                ok = False
                break
            core_vals.append(sat_core[j])
        if not ok:
            break
        unit_rows.append(dict(pid=pid, label=label,
                               S_pos=float(np.mean(pos_vals)),
                               S_neg=float(np.mean(neg_vals)),
                               S_core=float(np.mean(core_vals))))
    if not ok or len(unit_rows) != 4:
        if ok:
            skip_reasons["not_all_4_labels"] += 1
        continue

    n_prompts_qualifying += 1
    pos_count_per_prompt.append(len(pos_idx))
    neg_count_per_prompt.append(len(neg_idx))
    records.extend(unit_rows)

print(f"  prompts seen={n_prompts_seen} qualifying={n_prompts_qualifying} "
      f"units={len(records)} skip={skip_reasons}", flush=True)

pids = np.array([r["pid"] for r in records])
labels = np.array([r["label"] for r in records])
S_pos = np.array([r["S_pos"] for r in records])
S_neg = np.array([r["S_neg"] for r in records])
S_core = np.array([r["S_core"] for r in records])

uniq_pids = np.unique(pids)
pid_to_rows = {p: np.where(pids == p)[0] for p in uniq_pids}


def center_within_prompt(x: np.ndarray) -> np.ndarray:
    out = np.empty_like(x)
    for p, rows in pid_to_rows.items():
        out[rows] = x[rows] - x[rows].mean()
    return out


S_pos_c = center_within_prompt(S_pos)
S_neg_c = center_within_prompt(S_neg)
S_core_c = center_within_prompt(S_core)

# ============================================================ 3. PRIMARY POINT ESTIMATE
print("[3/8] primary correlations ...", flush=True)


def safe_corr(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


r_pos_hat = safe_corr(S_pos_c, S_core_c)
r_neg_hat = safe_corr(S_neg_c, S_core_c)
rho_hat = abs(r_neg_hat) / abs(r_pos_hat) if r_pos_hat != 0 else float("inf")

print(f"  r_pos={r_pos_hat:.4f} r_neg={r_neg_hat:.4f} rho={rho_hat:.4f}", flush=True)


# ================================================================ 4. CLUSTER BOOTSTRAP
def cluster_bootstrap(stat_fn, seeds, n_boot):
    """Resample prompt IDs with replacement, recompute stat_fn on pooled rows.
    stat_fn(rows_idx_array) -> dict of scalars.
    Returns dict[name] -> list of bootstrap draws (across all seeds pooled)."""
    draws = {}
    for seed in seeds:
        rg = rng_for(seed, salt=1)
        for _ in range(n_boot):
            samp_pids = rg.choice(uniq_pids, size=len(uniq_pids), replace=True)
            rows = np.concatenate([pid_to_rows[p] for p in samp_pids])
            out = stat_fn(rows)
            for k, v in out.items():
                draws.setdefault(k, []).append(v)
    return {k: np.array(v) for k, v in draws.items()}


def primary_stat(rows):
    a, b, c = S_pos_c[rows], S_neg_c[rows], S_core_c[rows]
    rp = safe_corr(a, c)
    rn = safe_corr(b, c)
    return {"r_pos": rp, "r_neg": rn,
            "rho": abs(rn) / abs(rp) if rp not in (0, float("nan")) else float("nan")}


print("[4/8] cluster bootstrap (5 seeds) ...", flush=True)
boot = cluster_bootstrap(primary_stat, SEEDS, N_BOOT)


def ci(draws, alpha=ALPHA):
    d = draws[~np.isnan(draws)]
    if d.size == 0:
        return (float("nan"), float("nan"))
    lo, hi = np.percentile(d, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


r_pos_ci = ci(boot["r_pos"])
r_neg_ci = ci(boot["r_neg"])
rho_ci = ci(boot["rho"])
r_neg_ci_excludes_0 = not (r_neg_ci[0] <= 0 <= r_neg_ci[1])

# per-seed CI spread (stability check, not the pooled CI used for the verdict)
per_seed_r_neg_ci = []
for seed in SEEDS:
    rg = rng_for(seed, salt=1)
    dseed = []
    for _ in range(N_BOOT):
        samp_pids = rg.choice(uniq_pids, size=len(uniq_pids), replace=True)
        rows = np.concatenate([pid_to_rows[p] for p in samp_pids])
        dseed.append(safe_corr(S_neg_c[rows], S_core_c[rows]))
    per_seed_r_neg_ci.append(ci(np.array(dseed)))

print(f"  r_pos 95%CI={r_pos_ci} r_neg 95%CI={r_neg_ci} rho 95%CI={rho_ci}", flush=True)
print(f"  per-seed r_neg CI spread: {per_seed_r_neg_ci}", flush=True)

# ==================================================== 5. CONFOUND CONTROL A: size-match
print("[5/8] control A: size-matched subsample ...", flush=True)
rho_matched_per_seed = []
r_pos_matched_per_seed = []
for seed in SEEDS:
    rg = rng_for(seed, salt=2)
    S_pos_matched = np.empty_like(S_pos)
    for pid_, comp, rub in joined:
        if pid_ not in pid_to_rows:
            continue
        full_list = rub["coval_full"]
        pos_idx = [i for i, c in enumerate(full_list)
                   if c.get("scores") and float(np.mean([s["score"] for s in c["scores"]])) > 0]
        neg_idx = [i for i, c in enumerate(full_list)
                   if c.get("scores") and float(np.mean([s["score"] for s in c["scores"]])) < 0]
        k = min(len(pos_idx), len(neg_idx))
        chosen = rg.choice(pos_idx, size=k, replace=False) if k < len(pos_idx) else np.array(pos_idx)
        for row in pid_to_rows[pid_]:
            label = labels[row]
            vals = []
            for i in chosen:
                key = f"{pid_}|{i}|{label}"
                vals.append(sat_full[idx_full[key]])
            S_pos_matched[row] = float(np.mean(vals)) if len(vals) else np.nan
    S_pos_matched_c = center_within_prompt(S_pos_matched)
    rp_m = safe_corr(S_pos_matched_c, S_core_c)
    rho_m = abs(r_neg_hat) / abs(rp_m) if rp_m not in (0, float("nan")) else float("nan")
    rho_matched_per_seed.append(rho_m)
    r_pos_matched_per_seed.append(rp_m)

rho_matched_mean = float(np.nanmean(rho_matched_per_seed))
rho_matched_std = float(np.nanstd(rho_matched_per_seed))
print(f"  rho_matched mean={rho_matched_mean:.4f} std={rho_matched_std:.4f} "
      f"per_seed={[round(x,4) for x in rho_matched_per_seed]}", flush=True)

# ============================================== 6. CONFOUND CONTROL B: split-half reliability
print("[6/8] control B: split-half reliability + attenuation correction ...", flush=True)


def split_half_reliability(group: str, seed: int):
    """Return Spearman-Brown corrected reliability for S_pos or S_neg."""
    rg = rng_for(seed, salt=3)
    halfA = np.empty(len(records))
    halfB = np.empty(len(records))
    valid_prompts = 0
    for pi, (pid_, comp, rub) in enumerate(joined):
        if pid_ not in pid_to_rows:
            continue
        full_list = rub["coval_full"]
        idxs = [i for i, c in enumerate(full_list)
                if c.get("scores") and
                (float(np.mean([s["score"] for s in c["scores"]])) > 0 if group == "pos"
                 else float(np.mean([s["score"] for s in c["scores"]])) < 0)]
        if len(idxs) < 2:
            for row in pid_to_rows[pid_]:
                halfA[row] = np.nan
                halfB[row] = np.nan
            continue
        valid_prompts += 1
        perm = rg.permutation(idxs)
        half1, half2 = perm[: len(perm) // 2 + len(perm) % 2], perm[len(perm) // 2 + len(perm) % 2:]
        if len(half2) == 0:
            half2 = half1
        for row in pid_to_rows[pid_]:
            label = labels[row]
            v1 = [sat_full[idx_full[f"{pid_}|{i}|{label}"]] for i in half1]
            v2 = [sat_full[idx_full[f"{pid_}|{i}|{label}"]] for i in half2]
            halfA[row] = np.mean(v1)
            halfB[row] = np.mean(v2)
    mask = ~np.isnan(halfA)
    hA_c = center_within_prompt(np.where(mask, halfA, 0.0))
    hB_c = center_within_prompt(np.where(mask, halfB, 0.0))
    r_half = safe_corr(hA_c[mask], hB_c[mask])
    # Spearman-Brown: reliability of the FULL-length measure from a half-length split-half r
    rel = (2 * r_half) / (1 + r_half) if not np.isnan(r_half) and (1 + r_half) != 0 else float("nan")
    return rel, valid_prompts


rel_pos_seeds, rel_neg_seeds = [], []
for seed in SEEDS:
    rp_rel, _ = split_half_reliability("pos", seed)
    rn_rel, n_valid_neg = split_half_reliability("neg", seed)
    rel_pos_seeds.append(rp_rel)
    rel_neg_seeds.append(rn_rel)

rel_pos = float(np.nanmean(rel_pos_seeds))
rel_neg = float(np.nanmean(rel_neg_seeds))
# attenuation correction: r_corrected = r_observed / sqrt(rel_x * rel_core)
# rel_core unknown (core has no repeated-item structure to split); conservatively
# assume rel_core=1 (best case for core), so correction only touches the full-arm side.
r_pos_corrected = r_pos_hat / np.sqrt(max(rel_pos, 1e-6)) if rel_pos > 0 else float("nan")
r_neg_corrected = r_neg_hat / np.sqrt(max(rel_neg, 1e-6)) if rel_neg > 0 else float("nan")
rho_corrected = (abs(r_neg_corrected) / abs(r_pos_corrected)
                  if r_pos_corrected not in (0, float("nan")) and not np.isnan(r_pos_corrected)
                  else float("nan"))
print(f"  reliability: pos={rel_pos:.4f} neg={rel_neg:.4f}", flush=True)
print(f"  r_pos_corrected={r_pos_corrected:.4f} r_neg_corrected={r_neg_corrected:.4f} "
      f"rho_corrected={rho_corrected:.4f}", flush=True)

# ============================================================== 7. POSITIVE CONTROL
print("[7/8] positive control: pairwise accuracy vs human world ranking ...", flush=True)

Q_pos_alone = S_pos.copy()
Q_neg_aligned = 1.0 - S_neg
Q_neg_unflipped = S_neg.copy()

row_lookup = {(pids[i], labels[i]): i for i in range(len(records))}
comp_by_pid = {pid_: comp for pid_, comp, rub in joined}


def pairwise_accuracy(score_array, seeds, n_boot):
    all_pairs = []  # (winner_row, loser_row) restricted to qualifying prompts
    for p in uniq_pids:
        comp = comp_by_pid[p]
        pairs = human_pairs(comp["metadata"].get("assessments", []))
        for w, l in pairs:
            rw = row_lookup.get((p, w))
            rl = row_lookup.get((p, l))
            if rw is None or rl is None:
                continue
            all_pairs.append((rw, rl, p))
    if not all_pairs:
        return float("nan"), (float("nan"), float("nan")), 0
    rw_idx = np.array([x[0] for x in all_pairs])
    rl_idx = np.array([x[1] for x in all_pairs])
    pair_pid = np.array([x[2] for x in all_pairs])
    correct = (score_array[rw_idx] > score_array[rl_idx]).astype(float)
    tie = (score_array[rw_idx] == score_array[rl_idx])
    denom_mask = ~tie
    acc = float(correct[denom_mask].mean()) if denom_mask.any() else float("nan")

    pair_pid_to_rows = {}
    for i, p in enumerate(pair_pid):
        pair_pid_to_rows.setdefault(p, []).append(i)
    uniq_pair_pids = np.array(list(pair_pid_to_rows))
    draws = []
    for seed in seeds:
        rg = rng_for(seed, salt=4)
        for _ in range(n_boot):
            samp = rg.choice(uniq_pair_pids, size=len(uniq_pair_pids), replace=True)
            rows = np.concatenate([pair_pid_to_rows[p] for p in samp])
            c = correct[rows]
            t = tie[rows]
            m = ~t
            if m.any():
                draws.append(float(c[m].mean()))
    lo, hi = np.percentile(draws, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)]) if draws else (float("nan"),) * 2
    return acc, (float(lo), float(hi)), len(all_pairs)


acc_pos, ci_pos, n_pairs = pairwise_accuracy(Q_pos_alone, SEEDS, N_BOOT)
acc_neg_aligned, ci_neg_aligned, _ = pairwise_accuracy(Q_neg_aligned, SEEDS, N_BOOT)
acc_neg_unflipped, ci_neg_unflipped, _ = pairwise_accuracy(Q_neg_unflipped, SEEDS, N_BOOT)

pos_ctrl_pos_ok = acc_pos > POS_CTRL_MIN_ACC and not (ci_pos[0] <= 0.5 <= ci_pos[1])
pos_ctrl_neg_ok = acc_neg_aligned > POS_CTRL_MIN_ACC and not (ci_neg_aligned[0] <= 0.5 <= ci_neg_aligned[1])
sign_convention_ok = acc_neg_aligned > acc_neg_unflipped
positive_control_passed = pos_ctrl_pos_ok and pos_ctrl_neg_ok and sign_convention_ok

print(f"  n_pairs={n_pairs} acc_pos={acc_pos:.4f} CI={ci_pos} "
      f"acc_neg_aligned={acc_neg_aligned:.4f} CI={ci_neg_aligned} "
      f"acc_neg_unflipped={acc_neg_unflipped:.4f} CI={ci_neg_unflipped}", flush=True)
print(f"  positive_control_passed={positive_control_passed} "
      f"(pos_ok={pos_ctrl_pos_ok} neg_ok={pos_ctrl_neg_ok} sign_ok={sign_convention_ok})", flush=True)

# ==================================================== 8. PLACEBO / ARITHMETIC REFERENCE
print("[8/8] placebo: synthetic-known-answer recovery ...", flush=True)

sd_core = np.std(S_core_c)


def make_synthetic(target_r: float, seed: int) -> np.ndarray:
    rg = rng_for(seed, salt=5)
    if target_r == 0.0:
        return rg.normal(0, sd_core if sd_core > 0 else 1.0, size=len(S_core_c))
    noise_sd = sd_core * np.sqrt(max(1.0 / target_r ** 2 - 1.0, 1e-9))
    return S_core_c + rg.normal(0, noise_sd, size=len(S_core_c))


placebo_strong_draws, placebo_null_draws = [], []
for seed in SEEDS:
    syn_strong = make_synthetic(PLACEBO_TARGET_R, seed)
    syn_null = make_synthetic(0.0, seed)
    syn_strong_c = center_within_prompt(syn_strong)
    syn_null_c = center_within_prompt(syn_null)
    placebo_strong_draws.append(safe_corr(syn_strong_c, S_core_c))
    placebo_null_draws.append(safe_corr(syn_null_c, S_core_c))

placebo_strong_hat = float(np.mean(placebo_strong_draws))
placebo_null_hat = float(np.mean(placebo_null_draws))


def boot_ci_for_vec(make_vec_fn, seeds, n_boot):
    draws = []
    for seed in seeds:
        vec_c = center_within_prompt(make_vec_fn(seed))
        rg = rng_for(seed, salt=6)
        for _ in range(n_boot):
            samp_pids = rg.choice(uniq_pids, size=len(uniq_pids), replace=True)
            rows = np.concatenate([pid_to_rows[p] for p in samp_pids])
            draws.append(safe_corr(vec_c[rows], S_core_c[rows]))
    return ci(np.array(draws))


placebo_null_ci = boot_ci_for_vec(lambda seed: make_synthetic(0.0, seed), SEEDS, N_BOOT)
placebo_null_ci_includes_0 = placebo_null_ci[0] <= 0 <= placebo_null_ci[1]
placebo_strong_ok = abs(placebo_strong_hat - PLACEBO_TARGET_R) <= PLACEBO_TOL
placebo_passed = placebo_strong_ok and placebo_null_ci_includes_0

print(f"  synthetic strong r_hat={placebo_strong_hat:.4f} (target {PLACEBO_TARGET_R}, "
      f"tol {PLACEBO_TOL}) ok={placebo_strong_ok}", flush=True)
print(f"  synthetic null r_hat={placebo_null_hat:.4f} CI={placebo_null_ci} "
      f"includes_0={placebo_null_ci_includes_0}", flush=True)
print(f"  placebo_passed={placebo_passed}", flush=True)

# ======================================================== SECONDARY / ROBUSTNESS TESTS
print("[secondary] joint regression, Spearman, control-A significance ...", flush=True)

# (1) joint standardized-partial regression: S_core_c ~ b_pos*S_pos_c + b_neg*S_neg_c
X = np.column_stack([S_pos_c, S_neg_c])
Xz = (X - X.mean(0)) / X.std(0)
yz = (S_core_c - S_core_c.mean()) / S_core_c.std()
beta, *_ = np.linalg.lstsq(Xz, yz, rcond=None)
resid = yz - Xz @ beta
n, k = Xz.shape
sigma2 = (resid @ resid) / (n - k)
XtX_inv = np.linalg.inv(Xz.T @ Xz)
se = np.sqrt(np.diag(sigma2 * XtX_inv))
t_neg = beta[1] / se[1]
p_neg_naive = 2 * (1 - stats.t.cdf(abs(t_neg), df=n - k))
# cluster bootstrap p-value substitute: use the CI already computed style for beta_neg
beta_neg_draws = []
for seed in SEEDS:
    rg = rng_for(seed, salt=7)
    for _ in range(N_BOOT // 4):  # keep cost down; this is a secondary/context test
        samp_pids = rg.choice(uniq_pids, size=len(uniq_pids), replace=True)
        rows = np.concatenate([pid_to_rows[p] for p in samp_pids])
        Xr = np.column_stack([S_pos_c[rows], S_neg_c[rows]])
        if Xr.std(0).min() == 0:
            continue
        Xrz = (Xr - Xr.mean(0)) / Xr.std(0)
        yr = S_core_c[rows]
        yrz = (yr - yr.mean()) / (yr.std() if yr.std() > 0 else 1.0)
        b, *_ = np.linalg.lstsq(Xrz, yrz, rcond=None)
        beta_neg_draws.append(b[1])
beta_neg_ci = ci(np.array(beta_neg_draws))
beta_neg_excludes_0 = not (beta_neg_ci[0] <= 0 <= beta_neg_ci[1])
p1 = 2 * min(np.mean(np.array(beta_neg_draws) >= 0), np.mean(np.array(beta_neg_draws) <= 0))

# (2) Spearman version
from scipy.stats import spearmanr
sp_pos = spearmanr(S_pos_c, S_core_c).statistic
sp_neg = spearmanr(S_neg_c, S_core_c).statistic
rho_spearman = abs(sp_neg) / abs(sp_pos) if sp_pos != 0 else float("inf")
sp_neg_draws = []
for seed in SEEDS:
    rg = rng_for(seed, salt=8)
    for _ in range(N_BOOT // 4):
        samp_pids = rg.choice(uniq_pids, size=len(uniq_pids), replace=True)
        rows = np.concatenate([pid_to_rows[p] for p in samp_pids])
        sp_neg_draws.append(spearmanr(S_neg_c[rows], S_core_c[rows]).statistic)
sp_neg_ci = ci(np.array(sp_neg_draws))
p2 = 2 * min(np.mean(np.array(sp_neg_draws) >= 0), np.mean(np.array(sp_neg_draws) <= 0))

# (3) control-A significance: r_neg vs r_pos_matched, is r_neg's CI (already have) excl 0
# reuse rho_matched seeds' r_pos_matched draws to build a crude CI on the matched gap
p3 = 2 * min(np.mean(np.array(r_pos_matched_per_seed) <= abs(r_neg_hat)),
             np.mean(np.array(r_pos_matched_per_seed) >= abs(r_neg_hat)))
p3 = min(max(p3, 1e-6), 1.0)

pvals = sorted([("joint_regression_beta_neg", p1), ("spearman_r_neg", p2),
                ("size_matched_r_pos_vs_r_neg", p3)], key=lambda t: t[1])
holm = []
m = len(pvals)
for rank, (name, p) in enumerate(pvals, start=1):
    holm.append((name, p, p * (m - rank + 1)))
holm_reject = {name: (adj < ALPHA) for name, p, adj in holm}

print(f"  beta_pos={beta[0]:.4f} beta_neg={beta[1]:.4f} (naive p={p_neg_naive:.4g}) "
      f"cluster-boot CI={beta_neg_ci} excl0={beta_neg_excludes_0}", flush=True)
print(f"  spearman r_pos={sp_pos:.4f} r_neg={sp_neg:.4f} rho_spearman={rho_spearman:.4f} "
      f"CI={sp_neg_ci}", flush=True)
print(f"  holm-bonferroni: {holm} reject={holm_reject}", flush=True)

# ================================================================== DECISION LOGIC
print("=== DECISION ===", flush=True)

gate_power = n_prompts_qualifying >= MIN_PROMPTS
raw_meets_confirm = (rho_hat >= RHO_CONFIRM) and r_neg_ci_excludes_0
controls_rescue = (rho_matched_mean >= RHO_RESCUE) and (not np.isnan(rho_corrected) and rho_corrected >= RHO_RESCUE)
controls_disagree_flip = raw_meets_confirm != controls_rescue

if not positive_control_passed or not placebo_passed or not gate_power:
    verdict = "UNVERIFIED"
    verdict_reason = (
        f"instrument-validity gate failed: positive_control_passed={positive_control_passed}, "
        f"placebo_passed={placebo_passed}, power_gate(n_qualifying>={MIN_PROMPTS})={gate_power} "
        f"(n_qualifying={n_prompts_qualifying})")
elif controls_disagree_flip:
    verdict = "UNVERIFIED"
    verdict_reason = (f"raw verdict ({'CONFIRM' if raw_meets_confirm else 'OVERTURN'}-leaning, "
                       f"rho_hat={rho_hat:.3f}) disagrees with size-matched/reliability-corrected "
                       f"controls (rho_matched={rho_matched_mean:.3f}, rho_corrected={rho_corrected:.3f}); "
                       "not scoring a side under an internally inconsistent result.")
elif raw_meets_confirm and controls_rescue:
    verdict = "CONFIRMED"
    verdict_reason = (f"rho_hat={rho_hat:.3f} >= {RHO_CONFIRM}, CI(r_neg) excludes 0, and both "
                       f"controls clear {RHO_RESCUE} (matched={rho_matched_mean:.3f}, "
                       f"corrected={rho_corrected:.3f}).")
else:
    verdict = "OVERTURNED"
    verdict_reason = (f"rho_hat={rho_hat:.3f}, CI(r_neg)={r_neg_ci} (excludes_0={r_neg_ci_excludes_0}); "
                       f"does not clear the pre-registered CONFIRM bar even accounting for controls "
                       f"(matched={rho_matched_mean:.3f}, corrected={rho_corrected:.3f}).")

print(f"  VERDICT: {verdict} -- {verdict_reason}", flush=True)

# ================================================================== ABSOLUTE EFFECT SIZES
abs_effects = {
    "mean_S_pos": float(np.mean(S_pos)), "mean_S_neg": float(np.mean(S_neg)),
    "mean_S_core": float(np.mean(S_core)),
    "sd_S_pos_centered": float(np.std(S_pos_c)), "sd_S_neg_centered": float(np.std(S_neg_c)),
    "sd_S_core_centered": float(np.std(S_core_c)),
    "slope_core_per_1sd_pos": float(r_pos_hat * np.std(S_core_c) / np.std(S_pos_c)) if np.std(S_pos_c) else None,
    "slope_core_per_1sd_neg": float(r_neg_hat * np.std(S_core_c) / np.std(S_neg_c)) if np.std(S_neg_c) else None,
    "mean_n_pos_per_prompt": float(np.mean(pos_count_per_prompt)),
    "mean_n_neg_per_prompt": float(np.mean(neg_count_per_prompt)),
}

# ================================================================== WRITE JSON
result = {
    "estimand": ("rho = |corr(S_neg_within_prompt_centered, S_core_within_prompt_centered)| / "
                 "|corr(S_pos_within_prompt_centered, S_core_within_prompt_centered)|, pooled over "
                 "(prompt,response) units, prompt-clustered inference"),
    "seed_base": BASE_SEED, "seeds": SEEDS, "n_boot_per_seed": N_BOOT, "alpha": ALPHA,
    "preregistered_thresholds": {
        "MIN_PROMPTS": MIN_PROMPTS, "RHO_CONFIRM": RHO_CONFIRM, "RHO_RESCUE": RHO_RESCUE,
        "POS_CTRL_MIN_ACC": POS_CTRL_MIN_ACC, "PLACEBO_TARGET_R": PLACEBO_TARGET_R,
        "PLACEBO_TOL": PLACEBO_TOL,
    },
    "data_coverage": {
        "n_prompts_joined": len(joined), "n_prompts_seen": n_prompts_seen,
        "n_prompts_qualifying": n_prompts_qualifying, "n_units": len(records),
        "skip_reasons": skip_reasons,
        "mean_n_pos_criteria_per_prompt": float(np.mean(pos_count_per_prompt)),
        "mean_n_neg_criteria_per_prompt": float(np.mean(neg_count_per_prompt)),
    },
    "primary": {
        "r_pos": r_pos_hat, "r_pos_95ci": r_pos_ci,
        "r_neg": r_neg_hat, "r_neg_95ci": r_neg_ci, "r_neg_ci_excludes_0": r_neg_ci_excludes_0,
        "rho": rho_hat, "rho_95ci": rho_ci,
        "per_seed_r_neg_ci": per_seed_r_neg_ci,
    },
    "confound_control_A_size_matched": {
        "description": "POS subsampled to min(n_pos,n_neg) items per prompt before averaging",
        "rho_matched_per_seed": rho_matched_per_seed,
        "rho_matched_mean": rho_matched_mean, "rho_matched_std": rho_matched_std,
        "r_pos_matched_per_seed": r_pos_matched_per_seed,
    },
    "confound_control_B_reliability_correction": {
        "description": "split-half Spearman-Brown reliability per group; r attenuation-corrected "
                        "assuming core reliability=1 (best case for core, conservative for rho)",
        "reliability_pos": rel_pos, "reliability_neg": rel_neg,
        "r_pos_corrected": r_pos_corrected, "r_neg_corrected": r_neg_corrected,
        "rho_corrected": rho_corrected,
    },
    "positive_control": {
        "n_pairs": n_pairs,
        "acc_pos_alone": acc_pos, "acc_pos_alone_95ci": ci_pos,
        "acc_neg_aligned_alone": acc_neg_aligned, "acc_neg_aligned_95ci": ci_neg_aligned,
        "acc_neg_unflipped_alone": acc_neg_unflipped, "acc_neg_unflipped_95ci": ci_neg_unflipped,
        "pos_ctrl_pos_ok": pos_ctrl_pos_ok, "pos_ctrl_neg_ok": pos_ctrl_neg_ok,
        "sign_convention_ok": sign_convention_ok,
        "positive_control_passed": positive_control_passed,
    },
    "placebo_arithmetic_reference": {
        "target_r_strong": PLACEBO_TARGET_R,
        "recovered_r_strong_mean_over_seeds": placebo_strong_hat,
        "recovered_r_strong_per_seed": placebo_strong_draws,
        "recovered_r_null_mean_over_seeds": placebo_null_hat,
        "recovered_r_null_95ci": placebo_null_ci,
        "placebo_strong_ok": placebo_strong_ok,
        "placebo_null_ci_includes_0": placebo_null_ci_includes_0,
        "placebo_passed": placebo_passed,
    },
    "secondary_robustness_holm_bonferroni_family_of_3": {
        "joint_regression": {"beta_pos_std": float(beta[0]), "beta_neg_std": float(beta[1]),
                              "beta_neg_cluster_boot_95ci": beta_neg_ci,
                              "beta_neg_excludes_0": beta_neg_excludes_0, "p_raw": p1},
        "spearman": {"r_pos": float(sp_pos), "r_neg": float(sp_neg), "rho_spearman": float(rho_spearman),
                     "r_neg_95ci": sp_neg_ci, "p_raw": p2},
        "size_matched_gap": {"p_raw": p3},
        "holm_bonferroni_adjusted": [{"name": n, "p_raw": p, "p_adj": adj} for n, p, adj in holm],
        "reject_at_0.05_after_correction": holm_reject,
    },
    "absolute_effect_sizes": abs_effects,
    "verdict": verdict,
    "verdict_reason": verdict_reason,
    "scopes": {
        "population": (f"{n_prompts_qualifying} of {len(joined)} joined OpenAI Collective "
                        "Alignment conversation_rubrics prompts that have >=1 positively-rated "
                        "AND >=1 negatively-rated coval_full criterion (mean score != 0) and "
                        "complete 4-response coverage in both satisfaction tensors; NOT the full "
                        f"release ({skip_reasons} excluded)."),
        "instrument": ("local Qwen3.5-2B-Base judge, sigmoid(logit-gap('Yes','No')) reading of "
                        "whether a response literally satisfies a criterion's text -- a proxy for "
                        "satisfaction, not ground truth; validated above chance against held-out "
                        "human 'world' pairwise rankings (positive control) but not perfectly "
                        "reliable, especially on the smaller NEG criterion group (see control B)."),
        "baseline": ("comparator is the POSITIVELY-rated criteria of the SAME prompts' coval_full, "
                      "not an absolute 'faithfulness score' -- rho is a RELATIVE retention-weight "
                      "ratio, silent on whether even the positive arm is compiled perfectly."),
        "regime": ("within-prompt, 4-way RELATIVE response discrimination (does core distinguish "
                    "responses the same way NEG full criteria do), not a between-prompt or "
                    "absolute-level statement about compilation quality; centered estimator, "
                    "so results say nothing about prompts excluded from the qualifying set."),
    },
}

class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


out_path = OUT_DIR / "independent_A.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2, cls=NumpyJSONEncoder)
print(f"\nwrote {out_path}", flush=True)

if verdict == "UNVERIFIED":
    print("EXIT: UNVERIFIED -- see verdict_reason", flush=True)
    sys.exit(0)  # UNVERIFIED is a valid, informative outcome given data supported the analysis;
                 # nonzero exit reserved for "data cannot support the question at all"
sys.exit(0)
