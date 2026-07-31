"""r128_style_or_content / independent_B.py

ESTIMAND (fixed before any number was seen)
--------------------------------------------
Unit of analysis: one (prompt, criterion) instance, nested in prompt, crossed
with arm in {full, core}. Two outcomes per instance:
  decisiveness_i = mean_{r in A,B,C,D} |sat(i, r) - 0.5|
  accuracy_i     = mean over the prompt's pooled strict human pairs (winner,
                   loser) of 1[sat(i, winner) > sat(i, loser)]
                   (ties in sat, i.e. exact equality, contribute 0.5 credit)

Primary estimand:
  Delta_raw = E[accuracy | arm=core] - E[accuracy | arm=full]      (core's
  measured advantage in per-criterion pairwise ranking accuracy).

Decomposition estimand: how much of Delta_raw survives once the analysis
conditions on criterion TEXT LENGTH (chars), a pure style covariate that
carries no semantic content by construction (permuting it destroys nothing
about what the criterion asks for). Headline number:

  r_style = beta_arm(accuracy ~ arm + log(length)) / beta_arm(accuracy ~ arm)

r_style near 0  -> arm's effect on accuracy is fully explained by length
                   (style artefact hypothesis wins; "content, not style" is
                   OVERTURNED).
r_style near 1  -> arm keeps its effect net of length (content survives the
                   style control; "content, not style" is CONFIRMED).

Corroborating, non-regression estimand: the length-MATCHED gap. Take the
bottom tercile of FULL by length (naturally-occurring short full criteria,
matched toward core's regime WITHOUT touching content or calling an LLM) and
compare its mean accuracy to core's mean accuracy. If short-full closes most
of the raw gap to core, style (not core-ness per se) explains the advantage.

WHY NO LLM REWRITE IS USED, AND WHAT WOULD BE NEEDED
------------------------------------------------------
The causally clean test would be: take each full criterion, rewrite it into
core's terse register while holding meaning fixed exactly, re-score both
versions with the SAME frozen judge, and compare. That requires an LLM
rewrite step and is explicitly disallowed here. What this script does instead
is the second-best, LLM-free substitute: exploit the length variation that
already exists *within* full (full criteria range from short to long on
their own) as a naturally-occurring, observational analogue of a style
manipulation, plus a content-severity covariate (human importance score,
full-only) to partial out the obvious confound that terse criteria might
also just be less nuanced content. This is weaker than a controlled rewrite
-- it cannot fully separate "terse" from "simple content that happens to be
phrased tersely" -- and that gap is named explicitly as the residual
limitation in the final report, not hidden.

PRE-REGISTERED THRESHOLDS (fixed before this script computed anything)
------------------------------------------------------------------------
Hypothesis family (Holm-Bonferroni, m=6, two-sided, alpha=0.05):
  H1: beta_arm in (accuracy ~ arm)                              != 0
  H2: beta_length in (decisiveness ~ arm + log(length))         != 0   (sign: neg)
  H3: beta_arm in (accuracy ~ arm + log(length))                != 0   *** KEY ***
  H4: beta_arm in (accuracy ~ arm + decisiveness)                != 0
  H5: beta_length in (accuracy_full ~ log(length) + importance_z) != 0
  H6: mean(accuracy | short-full) - mean(accuracy | core)        != 0

Verdict rule (mechanical, on r_style = beta_arm(H3-model)/beta_arm(H1-model)
and H3's Holm-corrected p-value, corroborated by H6):
  OVERTURNED ("content,not style" is FALSE, i.e. style artefact confirmed) if
      r_style <= 0.30  AND  p_holm(H3) > 0.05
      AND matched-gap (H6) is not significant OR < 0.30 * Delta_raw in size.
  CONFIRMED ("content, not style") if
      r_style >= 0.60  AND  p_holm(H3) <= 0.05
      AND matched-gap (H6) is significant AND >= 0.40 * Delta_raw in size
      (same direction as Delta_raw).
  UNVERIFIED otherwise (including: Delta_raw itself not significant, i.e.
  nothing to decompose; or regression and matched-tercile evidence disagree).

Controls run in the SAME script (pre-registered, not post hoc):
  - Positive control: reproduce the r04 finding "the judge beats chance at
    predicting held-out human world rankings" on prompt-level aggregate
    scores, for BOTH arms independently. A null here means the whole
    satisfaction/human_pairs/join pipeline is broken and nothing downstream
    can be trusted (P5: an untested zero is silence, not acquittal).
  - Placebo 1 (shuffled length): randomly permute length across instances,
    recompute the length-decisiveness correlation; pre-registered to collapse
    to ~0, confirming the true correlation is not a pipeline artefact of
    shared sample composition.
  - Placebo 2 (list-position split, full only): split full's own criteria by
    whether their index within the prompt's list is in the first or second
    half. List position carries no known content or style signal, so no
    accuracy/length difference is expected; a "significant" split here would
    flag a hidden pipeline bias (e.g. an ordering artefact) independent of
    length or arm.
  - Strongest-confound control (H5): within full ONLY (content held to a
    single human-authored population), does length still predict accuracy
    net of the human IMPORTANCE score (a content-severity proxy)? If length's
    effect vanishes once importance is held constant, length was likely
    proxying for content simplicity, not pure style, and the style-artefact
    story is weaker than it looks.

Clustering: prompts are the cluster unit (criteria and the human-pair set are
nested in prompt). ALL inference (CIs, p-values) comes from a cluster
bootstrap that resamples PROMPTS with replacement and recomputes every
statistic on the resampled instance table -- never from naive per-instance
SEs.

Multi-seed: the cluster bootstrap is run independently at 5 seeds
(4409, 4410, 4411, 4412, 4413), 2000 resamples each. The pooled 10,000 draws
give the CIs and p-values used for the verdict; the per-seed CIs are reported
separately to show Monte Carlo stability (spread across seeds).

No LLM calls, no GPU. Pure numpy/stdlib over the precomputed a04 satisfaction
tensors and the release rubrics/comparisons files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from covalx import load_join, human_pairs  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 4409
SEEDS = [SEED, SEED + 1, SEED + 2, SEED + 3, SEED + 4]
N_BOOT = 2000
ALPHA = 0.05
LABELS = ("A", "B", "C", "D")


# ============================================================ 1. LOAD ======
def build_crit_lists(rub):
    """Replicate r04_rebuild_satisfaction/run.py's exact criterion filtering
    so that criterion index `ci` in the a04 npz meta lines up with the right
    text.  For full: only criteria that have a non-empty `scores` list are
    kept (index is over the FILTERED list, not the raw jsonl list); the
    weight is the mean human importance score.  For core: every listed
    criterion is kept, weight is None.
    """
    core = [(c["criterion"], None) for c in (rub.get("coval_core") or [])]
    full = []
    for it in rub.get("coval_full") or []:
        sc = [s["score"] for s in it.get("scores") or []]
        if sc:
            full.append((it["criterion"], float(np.mean(sc))))
    return full, core


def load_sat(npz_path):
    d = np.load(npz_path)
    meta, sat = d["meta"], d["sat"]
    table = {}
    for m, s in zip(meta, sat):
        pid, ci, lab = m.split("|")
        table.setdefault((pid, int(ci)), {})[lab] = float(s)
    return table


print("[load] joining comparisons <-> rubrics ...", flush=True)
joined = load_join(REPO / "data" / "comparisons.jsonl",
                    REPO / "data" / "conversation_rubrics.jsonl")

print("[load] precomputed satisfaction tensors ...", flush=True)
sat_full = load_sat(REPO / "01_object_and_rebuild" / "r04_rebuild_satisfaction"
                     / "results" / "a04_full.npz")
sat_core = load_sat(REPO / "01_object_and_rebuild" / "r04_rebuild_satisfaction"
                     / "results" / "a04_core.npz")

# ============================================================ 2. BUILD =====
# Per-instance rows. Columns kept as parallel python lists, cast to numpy at
# the end. pid is mapped to an integer cluster id for fast bootstrap grouping.
pid_to_int, next_pid_int = {}, 0

rows_pid, rows_arm, rows_len, rows_dec, rows_acc, rows_imp, rows_ci, rows_npairs = (
    [], [], [], [], [], [], [], [])

n_prompts_used = 0
skipped_no_pairs = 0
for pid, comp, rub in joined:
    hp = human_pairs(comp["metadata"]["assessments"])
    if not hp:
        skipped_no_pairs += 1
        continue
    if pid not in pid_to_int:
        pid_to_int[pid] = next_pid_int
        next_pid_int += 1
    pint = pid_to_int[pid]
    n_prompts_used += 1

    full_crits, core_crits = build_crit_lists(rub)

    for arm, crits, sat_table in (("full", full_crits, sat_full),
                                   ("core", core_crits, sat_core)):
        for ci, (text, weight) in enumerate(crits):
            if len(text) == 0:
                continue  # one malformed empty-string criterion in the release; log(0) undefined
            sv = sat_table.get((pid, ci))
            if sv is None or len(sv) != 4:
                continue  # should not happen (verified 4/4 coverage above)
            dec = float(np.mean([abs(sv[l] - 0.5) for l in LABELS]))
            correct = []
            for w, l in hp:
                if sv[w] > sv[l]:
                    correct.append(1.0)
                elif sv[w] < sv[l]:
                    correct.append(0.0)
                else:
                    correct.append(0.5)
            acc = float(np.mean(correct))

            rows_pid.append(pint)
            rows_arm.append(1 if arm == "core" else 0)
            rows_len.append(float(len(text)))
            rows_dec.append(dec)
            rows_acc.append(acc)
            rows_imp.append(weight if weight is not None else np.nan)
            rows_ci.append(ci)
            rows_npairs.append(len(hp))

pid_arr = np.array(rows_pid, dtype=np.int64)
arm_arr = np.array(rows_arm, dtype=np.int64)          # 1=core, 0=full
len_arr = np.array(rows_len, dtype=np.float64)
dec_arr = np.array(rows_dec, dtype=np.float64)
acc_arr = np.array(rows_acc, dtype=np.float64)
imp_arr = np.array(rows_imp, dtype=np.float64)        # nan for core
ci_arr = np.array(rows_ci, dtype=np.int64)
npairs_arr = np.array(rows_npairs, dtype=np.int64)
loglen_arr = np.log(len_arr)

n_total = len(pid_arr)
n_full = int((arm_arr == 0).sum())
n_core = int((arm_arr == 1).sum())
n_prompts = len(pid_to_int)

print(f"[build] instances: total={n_total} full={n_full} core={n_core} "
      f"prompts={n_prompts} (skipped {skipped_no_pairs} prompts w/ 0 human pairs)",
      flush=True)

# prompt -> row indices, for cluster bootstrap
prompt_rows = [[] for _ in range(n_prompts)]
for i, p in enumerate(pid_arr):
    prompt_rows[p].append(i)
prompt_rows = [np.array(v, dtype=np.int64) for v in prompt_rows]
prompt_sizes = np.array([len(v) for v in prompt_rows])


# ============================================================ 3. STATS ====
def ols(X, y):
    """Return coefficients of y ~ X (X must already include an intercept col)."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def design(*cols):
    n = len(cols[0])
    return np.column_stack([np.ones(n)] + list(cols))


def diff_means(mask_a, mask_b, y):
    return float(y[mask_a].mean() - y[mask_b].mean())


def stat_bundle(idx):
    """Compute every headline statistic on the instance-index array `idx`
    (with repetition, as produced by the cluster bootstrap). Returns a dict
    of scalars. `idx` may repeat rows -- all stats below only use means /
    OLS on the (possibly repeated) rows, which is exactly what a cluster
    bootstrap requires.
    """
    arm = arm_arr[idx]
    ll = loglen_arr[idx]
    dec = dec_arr[idx]
    acc = acc_arr[idx]
    imp = imp_arr[idx]
    length = len_arr[idx]
    ci = ci_arr[idx]

    out = {}

    # descriptive (positive-control support)
    out["mean_len_full"] = float(length[arm == 0].mean())
    out["mean_len_core"] = float(length[arm == 1].mean())
    out["mean_dec_full"] = float(dec[arm == 0].mean())
    out["mean_dec_core"] = float(dec[arm == 1].mean())

    # H1: accuracy ~ arm
    X1 = design(arm)
    b1 = ols(X1, acc)
    out["beta_arm_raw"] = float(b1[1])          # == Delta_raw

    # H2: decisiveness ~ arm + log(length)
    X2 = design(arm, ll)
    b2 = ols(X2, dec)
    out["beta_length_on_dec"] = float(b2[2])

    # H3 (key): accuracy ~ arm + log(length)
    X3 = design(arm, ll)
    b3 = ols(X3, acc)
    out["beta_arm_after_length"] = float(b3[1])
    out["beta_length_after_arm"] = float(b3[2])

    # H4: accuracy ~ arm + decisiveness
    X4 = design(arm, dec)
    b4 = ols(X4, acc)
    out["beta_arm_after_dec"] = float(b4[1])

    # H5 (full only): accuracy_full ~ log(length) + importance_z
    fmask = arm == 0
    imp_f = imp[fmask]
    ll_f = ll[fmask]
    acc_f = acc[fmask]
    imp_z = (imp_f - np.nanmean(imp_f)) / (np.nanstd(imp_f) + 1e-12)
    X5 = design(ll_f, imp_z)
    b5 = ols(X5, acc_f)
    out["beta_length_within_full_ctrl_importance"] = float(b5[1])
    out["beta_importance_within_full"] = float(b5[2])
    # simple corr(length, importance) within full -- confound diagnostic
    out["corr_length_importance_full"] = float(
        np.corrcoef(ll_f, imp_f)[0, 1]) if len(ll_f) > 2 else float("nan")

    # H6: length-matched tercile comparison
    full_len = length[fmask]
    p33 = float(np.percentile(full_len, 100 / 3))
    p67 = float(np.percentile(full_len, 200 / 3))
    short_full_mask = fmask & (length <= p33)
    long_full_mask = fmask & (length >= p67)
    core_mask = arm == 1
    out["p33_full_len"] = p33
    out["mean_len_short_full"] = float(length[short_full_mask].mean())
    out["mean_acc_short_full"] = float(acc[short_full_mask].mean())
    out["mean_acc_long_full"] = float(acc[long_full_mask].mean())
    out["mean_acc_core"] = float(acc[core_mask].mean())
    out["mean_acc_full_all"] = float(acc[fmask].mean())
    out["matched_gap"] = float(acc[short_full_mask].mean() - acc[core_mask].mean())
    out["within_full_len_gap"] = float(acc[short_full_mask].mean() - acc[long_full_mask].mean())

    # r_style headline
    denom = out["beta_arm_raw"]
    out["r_style"] = float(out["beta_arm_after_length"] / denom) if abs(denom) > 1e-9 else float("nan")

    # decisiveness overall correlation with length (pooled) -- diagnostic,
    # matches the "-0.95" style relationship reported by the prior analyses
    out["corr_length_dec_pooled"] = float(np.corrcoef(ll, dec)[0, 1])

    # positive control: prompt-level aggregate ranking accuracy per arm
    # (mean sat across ALL that arm's criteria per response, then compare to
    # human pairs) -- computed OUTSIDE the per-instance bootstrap, see below.

    return out


POINT = stat_bundle(np.arange(n_total))
print("[point estimates] r_style =", POINT["r_style"])


# ==================================================== 4. POSITIVE CONTROL ==
def prompt_level_accuracy(sat_table, crit_fn):
    """Aggregate ALL of an arm's criteria per (prompt,response) into a mean
    satisfaction score, rank the 4 responses, score against that prompt's
    human pairs. Returns per-prompt accuracy array + prompt-int array
    (aligned to the SAME pid_to_int mapping) for cluster bootstrap reuse.
    """
    accs, pints = [], []
    for pid, comp, rub in joined:
        if pid not in pid_to_int:
            continue  # dropped (0 human pairs)
        hp = human_pairs(comp["metadata"]["assessments"])
        crits = crit_fn(rub)
        vals = {l: [] for l in LABELS}
        for ci in range(len(crits)):
            sv = sat_table.get((pid, ci))
            if sv is None:
                continue
            for l in LABELS:
                vals[l].append(sv[l])
        if not vals["A"]:
            continue
        mean_sat = {l: float(np.mean(vals[l])) for l in LABELS}
        correct = []
        for w, l in hp:
            if mean_sat[w] > mean_sat[l]:
                correct.append(1.0)
            elif mean_sat[w] < mean_sat[l]:
                correct.append(0.0)
            else:
                correct.append(0.5)
        accs.append(float(np.mean(correct)))
        pints.append(pid_to_int[pid])
    return np.array(accs), np.array(pints, dtype=np.int64)


pc_acc_full, pc_pid_full = prompt_level_accuracy(
    sat_full, lambda rub: build_crit_lists(rub)[0])
pc_acc_core, pc_pid_core = prompt_level_accuracy(
    sat_core, lambda rub: build_crit_lists(rub)[1])

CHANCE = 0.5


def cluster_bootstrap_1sample(values, pints, seed, n_boot=N_BOOT):
    rng = np.random.default_rng(seed)
    uniq = np.unique(pints)
    # group value-indices by prompt
    groups = {p: np.where(pints == p)[0] for p in uniq}
    out = np.empty(n_boot)
    for b in range(n_boot):
        draw = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([groups[p] for p in draw])
        out[b] = values[idx].mean()
    return out


pc_full_boot = np.concatenate([cluster_bootstrap_1sample(pc_acc_full, pc_pid_full, s, 1000) for s in SEEDS])
pc_core_boot = np.concatenate([cluster_bootstrap_1sample(pc_acc_core, pc_pid_core, s, 1000) for s in SEEDS])

pc_full_mean = float(pc_acc_full.mean())
pc_core_mean = float(pc_acc_core.mean())
pc_full_ci = [float(np.percentile(pc_full_boot, 2.5)), float(np.percentile(pc_full_boot, 97.5))]
pc_core_ci = [float(np.percentile(pc_core_boot, 2.5)), float(np.percentile(pc_core_boot, 97.5))]
positive_control = {
    "description": "prompt-level aggregate ranking accuracy vs pooled human "
                    "world-pairs; must clear chance=0.5 in BOTH arms or the "
                    "whole pipeline is untrusted (reproduces r04's own "
                    "positive control).",
    "full_arm": {"mean": pc_full_mean, "ci95": pc_full_ci,
                 "beats_chance": bool(pc_full_ci[0] > CHANCE)},
    "core_arm": {"mean": pc_core_mean, "ci95": pc_core_ci,
                 "beats_chance": bool(pc_core_ci[0] > CHANCE)},
    "n_prompts_full": int(len(pc_acc_full)), "n_prompts_core": int(len(pc_acc_core)),
}
print("[positive control]", json.dumps(positive_control, indent=2))

PIPELINE_OK = positive_control["full_arm"]["beats_chance"] and positive_control["core_arm"]["beats_chance"]
if not PIPELINE_OK:
    print("POSITIVE CONTROL FAILED: judge does not beat chance in at least one "
          "arm. A null from here would be silence, not acquittal. Exiting nonzero.",
          file=sys.stderr)
    Path(OUT_DIR / "independent_B.json").write_text(json.dumps(
        {"verdict": "UNVERIFIED", "reason": "positive control failed",
         "positive_control": positive_control}, indent=2))
    sys.exit(1)


# ============================================================ 5. PLACEBOS =
rng_pl = np.random.default_rng(SEED)
shuffled_len = loglen_arr.copy()
rng_pl.shuffle(shuffled_len)
placebo_shuffled_corr = float(np.corrcoef(shuffled_len, dec_arr)[0, 1])

# placebo 2: full-only, split by list position (first half of that prompt's
# criterion list vs second half), test for a spurious accuracy difference
full_mask_all = arm_arr == 0
# recompute, per prompt, the median ci among its full criteria
median_ci_per_prompt = {}
for p in np.unique(pid_arr[full_mask_all]):
    cis = ci_arr[full_mask_all & (pid_arr == p)]
    median_ci_per_prompt[p] = np.median(cis)
med_arr = np.array([median_ci_per_prompt.get(p, np.nan) for p in pid_arr])
first_half_mask = full_mask_all & (ci_arr <= med_arr)
second_half_mask = full_mask_all & (ci_arr > med_arr)
placebo_position_gap = diff_means(first_half_mask, second_half_mask, acc_arr)
placebo_position_len_gap = diff_means(first_half_mask, second_half_mask, len_arr)

placebos = {
    "shuffled_length_vs_decisiveness_corr": placebo_shuffled_corr,
    "expect": "~0 (|r| < 0.1)",
    "list_position_accuracy_gap_full_only": placebo_position_gap,
    "list_position_length_gap_full_only": placebo_position_len_gap,
    "expect_position": "no reason to differ from 0",
}
print("[placebos]", json.dumps(placebos, indent=2))


# ===================================================== 6. CLUSTER BOOTSTRAP
def cluster_bootstrap(seed, n_boot):
    rng = np.random.default_rng(seed)
    keys = list(POINT.keys())
    draws = {k: np.empty(n_boot) for k in keys}
    uniq_prompts = np.arange(n_prompts)
    for b in range(n_boot):
        sampled = rng.choice(uniq_prompts, size=n_prompts, replace=True)
        idx = np.concatenate([prompt_rows[p] for p in sampled if len(prompt_rows[p])])
        res = stat_bundle(idx)
        for k in keys:
            draws[k][b] = res[k]
    return draws


print(f"[bootstrap] {len(SEEDS)} seeds x {N_BOOT} resamples over {n_prompts} prompt clusters ...",
      flush=True)
per_seed_draws = {}
for s in SEEDS:
    per_seed_draws[s] = cluster_bootstrap(s, N_BOOT)
    print(f"  seed {s} done: r_style CI95 = "
          f"[{np.percentile(per_seed_draws[s]['r_style'],2.5):.3f}, "
          f"{np.percentile(per_seed_draws[s]['r_style'],97.5):.3f}]", flush=True)

pooled_draws = {k: np.concatenate([per_seed_draws[s][k] for s in SEEDS]) for k in POINT}


def ci95(arr):
    return [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))]


def two_sided_p(arr):
    p_pos = float(np.mean(arr <= 0))
    p_neg = float(np.mean(arr >= 0))
    return float(min(1.0, 2 * min(p_pos, p_neg)))


def holm(pvals: dict, alpha=ALPHA):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj = {}
    running_max = 0.0
    for i, (k, p) in enumerate(items):
        val = min(1.0, p * (m - i))
        running_max = max(running_max, val)
        adj[k] = running_max
    return {k: adj[k] for k in pvals}, {k: adj[k] <= alpha for k in pvals}


raw_p = {
    "H1_beta_arm_raw": two_sided_p(pooled_draws["beta_arm_raw"]),
    "H2_beta_length_on_dec": two_sided_p(pooled_draws["beta_length_on_dec"]),
    "H3_beta_arm_after_length": two_sided_p(pooled_draws["beta_arm_after_length"]),
    "H4_beta_arm_after_dec": two_sided_p(pooled_draws["beta_arm_after_dec"]),
    "H5_beta_length_within_full": two_sided_p(pooled_draws["beta_length_within_full_ctrl_importance"]),
    "H6_matched_gap": two_sided_p(pooled_draws["matched_gap"]),
}
p_holm, reject = holm(raw_p)

print("[Holm-Bonferroni]", json.dumps({"raw_p": raw_p, "p_holm": p_holm, "reject_at_0.05": reject}, indent=2))


# ============================================================ 7. VERDICT ==
r_style_point = POINT["r_style"]
delta_raw = POINT["beta_arm_raw"]
matched_gap = POINT["matched_gap"]
matched_gap_frac = abs(matched_gap) / abs(delta_raw) if abs(delta_raw) > 1e-9 else float("nan")

h3_sig = reject["H3_beta_arm_after_length"]
h6_sig = reject["H6_matched_gap"]
h1_sig = reject["H1_beta_arm_raw"]

if not h1_sig:
    verdict = "UNVERIFIED"
    verdict_reason = "Delta_raw (core - full) is not itself distinguishable from 0 at Holm-corrected alpha; there is no established advantage to decompose."
elif r_style_point <= 0.30 and not h3_sig and (not h6_sig or matched_gap_frac < 0.30):
    verdict = "OVERTURNED"
    verdict_reason = ("core's advantage is explained away by criterion text length: "
                       "the arm effect on accuracy collapses under a length control "
                       "(r_style<=0.30, H3 not significant) and the length-matched "
                       "short-full subset closes most of the gap to core.")
elif r_style_point >= 0.60 and h3_sig and h6_sig and matched_gap_frac >= 0.40:
    verdict = "CONFIRMED"
    verdict_reason = ("core's advantage survives a length control: the arm effect "
                       "on accuracy remains large and significant net of log(length) "
                       "(r_style>=0.60, H3 significant), and length-matching full down "
                       "to core's regime does not close the gap.")
else:
    verdict = "UNVERIFIED"
    verdict_reason = (f"regression (r_style={r_style_point:.3f}, H3 sig={h3_sig}) and "
                       f"matched-tercile (gap fraction={matched_gap_frac:.3f}, H6 sig={h6_sig}) "
                       "evidence do not jointly clear either pre-registered bucket.")

print(f"\n[VERDICT] {verdict}: {verdict_reason}\n")


# ================================================ 8. WEIGHTING ROBUSTNESS =
# Pre-registered analyses above weight every CRITERION instance equally, so
# a prompt with many full criteria (up to ~30+) contributes more full rows
# than core's fixed 4. This is a legitimate default (the estimand is about
# criteria, not prompts) but it is a weighting CHOICE, not a fact, so check
# it does not drive the verdict: re-run H1 and H3 giving every PROMPT equal
# weight (per-prompt mean accuracy per arm, then average the per-prompt
# difference/residual across prompts). Labeled explicitly as a sensitivity
# check, not part of the pre-registered Holm family.
prompt_full_mean = {}
prompt_core_mean = {}
prompt_full_len_mean = {}
for p in range(n_prompts):
    idx = prompt_rows[p]
    a = arm_arr[idx]
    acc = acc_arr[idx]
    ll = loglen_arr[idx]
    fmask, cmask = a == 0, a == 1
    if fmask.any() and cmask.any():
        prompt_full_mean[p] = float(acc[fmask].mean())
        prompt_core_mean[p] = float(acc[cmask].mean())
        prompt_full_len_mean[p] = float(ll[fmask].mean())

pw_prompts = sorted(prompt_full_mean)
pw_diff = np.array([prompt_core_mean[p] - prompt_full_mean[p] for p in pw_prompts])
pw_full_acc = np.array([prompt_full_mean[p] for p in pw_prompts])
pw_core_acc = np.array([prompt_core_mean[p] for p in pw_prompts])
pw_full_len = np.array([prompt_full_len_mean[p] for p in pw_prompts])

pw_delta_raw = float(pw_diff.mean())
# residualize: does the per-prompt (core-full) gap shrink once the prompt's
# own mean full-criterion log-length is partialled out via OLS?
Xpw = np.column_stack([np.ones(len(pw_full_len)), pw_full_len])
b_pw = ols(Xpw, pw_diff)
pw_len_slope = float(b_pw[1])


def pw_bootstrap(seed, n_boot=1000):
    rng = np.random.default_rng(seed)
    n = len(pw_diff)
    out_mean = np.empty(n_boot)
    out_slope = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        out_mean[b] = pw_diff[idx].mean()
        Xb = np.column_stack([np.ones(n), pw_full_len[idx]])
        out_slope[b] = ols(Xb, pw_diff[idx])[1]
    return out_mean, out_slope


pw_means, pw_slopes = [], []
for s in SEEDS:
    m, sl = pw_bootstrap(s, 1000)
    pw_means.append(m)
    pw_slopes.append(sl)
pw_means = np.concatenate(pw_means)
pw_slopes = np.concatenate(pw_slopes)

sensitivity_prompt_weighted = {
    "description": "Robustness check, NOT part of the pre-registered Holm "
                    "family: equal weight per PROMPT (mean accuracy per arm "
                    "within prompt, then averaged) instead of equal weight "
                    "per criterion instance, to check the headline gap is "
                    "not an artefact of full having ~15.8x more criteria/prompt.",
    "n_prompts": len(pw_prompts),
    "delta_raw_prompt_weighted": pw_delta_raw,
    "delta_raw_prompt_weighted_ci95": ci95(pw_means),
    "delta_raw_criterion_weighted_for_comparison": POINT["beta_arm_raw"],
    "slope_of_per_prompt_gap_on_full_mean_loglength": pw_len_slope,
    "slope_ci95": ci95(pw_slopes),
    "note": "if this slope's CI excludes 0 with a sign that would erase "
            "delta_raw_prompt_weighted, length is a live confound under "
            "prompt-weighting too; otherwise the criterion-weighted verdict "
            "is not an artefact of the weighting choice.",
}
print("[sensitivity: prompt-weighted]", json.dumps(sensitivity_prompt_weighted, indent=2))


# ============================================================ 9. WRITE ====
def summarize(key):
    return {
        "point": POINT[key],
        "ci95_pooled": ci95(pooled_draws[key]),
        "per_seed_ci95": {str(s): ci95(per_seed_draws[s][key]) for s in SEEDS},
    }


results = {
    "seed": SEED,
    "seeds_used": SEEDS,
    "n_boot_per_seed": N_BOOT,
    "n_prompts": n_prompts,
    "n_instances_total": n_total,
    "n_instances_full": n_full,
    "n_instances_core": n_core,
    "n_prompts_skipped_zero_human_pairs": skipped_no_pairs,

    "estimand": ("per-criterion pairwise ranking accuracy against pooled "
                 "strict human world-pairs; core-vs-full gap decomposed by "
                 "criterion text length (chars)."),

    "positive_control": positive_control,
    "placebos": placebos,

    "descriptive": {
        "mean_len_full": POINT["mean_len_full"],
        "mean_len_core": POINT["mean_len_core"],
        "mean_dec_full": POINT["mean_dec_full"],
        "mean_dec_core": POINT["mean_dec_core"],
        "mean_acc_full_all": POINT["mean_acc_full_all"],
        "mean_acc_core": POINT["mean_acc_core"],
        "corr_length_decisiveness_pooled": POINT["corr_length_dec_pooled"],
        "corr_length_importance_within_full": POINT["corr_length_importance_full"],
    },

    "hypotheses": {
        "H1_beta_arm_raw_accuracy": {**summarize("beta_arm_raw"),
                                      "raw_p": raw_p["H1_beta_arm_raw"], "p_holm": p_holm["H1_beta_arm_raw"],
                                      "reject_0.05": reject["H1_beta_arm_raw"]},
        "H2_beta_length_on_decisiveness": {**summarize("beta_length_on_dec"),
                                            "raw_p": raw_p["H2_beta_length_on_dec"], "p_holm": p_holm["H2_beta_length_on_dec"],
                                            "reject_0.05": reject["H2_beta_length_on_dec"]},
        "H3_beta_arm_after_length_KEY": {**summarize("beta_arm_after_length"),
                                          "raw_p": raw_p["H3_beta_arm_after_length"], "p_holm": p_holm["H3_beta_arm_after_length"],
                                          "reject_0.05": reject["H3_beta_arm_after_length"]},
        "H4_beta_arm_after_decisiveness": {**summarize("beta_arm_after_dec"),
                                            "raw_p": raw_p["H4_beta_arm_after_dec"], "p_holm": p_holm["H4_beta_arm_after_dec"],
                                            "reject_0.05": reject["H4_beta_arm_after_dec"]},
        "H5_beta_length_within_full_ctrl_importance": {**summarize("beta_length_within_full_ctrl_importance"),
                                                         "raw_p": raw_p["H5_beta_length_within_full"], "p_holm": p_holm["H5_beta_length_within_full"],
                                                         "reject_0.05": reject["H5_beta_length_within_full"]},
        "H6_matched_gap_short_full_minus_core": {**summarize("matched_gap"),
                                                   "raw_p": raw_p["H6_matched_gap"], "p_holm": p_holm["H6_matched_gap"],
                                                   "reject_0.05": reject["H6_matched_gap"],
                                                   "matched_gap_fraction_of_delta_raw": matched_gap_frac,
                                                   "mean_len_short_full": POINT["mean_len_short_full"],
                                                   "p33_full_len_threshold": POINT["p33_full_len"],
                                                   "mean_acc_short_full": POINT["mean_acc_short_full"],
                                                   "mean_acc_long_full": POINT["mean_acc_long_full"],
                                                   "within_full_len_gap_short_minus_long": summarize("within_full_len_gap")},
    },

    "headline": {
        "r_style": summarize("r_style"),
        "delta_raw_accuracy_points": summarize("beta_arm_raw"),
        "interpretation": "r_style = beta_arm(accuracy~arm+log(length)) / beta_arm(accuracy~arm). "
                           "0 = fully explained by length; 1 = arm effect untouched by length control.",
    },

    "holm_bonferroni": {"family_size": 6, "alpha": ALPHA, "raw_p": raw_p, "p_holm": p_holm, "reject_0.05": reject},

    "scopes": {
        "population": f"{n_prompts} OpenAI Collective Alignment release prompts joined "
                       "across comparisons.jsonl and conversation_rubrics.jsonl, restricted "
                       "to those with a nonzero pooled strict human world-ranking and at "
                       "least one scored full criterion; full criteria without human "
                       "importance scores are excluded (mirrors r04's own filter).",
        "instrument": "local Qwen3.5-2B-Base logit-gap judge as implemented in "
                       "covalx.judge.Judge/build_prompt (few-shot, 1400-char reply "
                       "truncation), read from the precomputed a04_full.npz/a04_core.npz "
                       "satisfaction tensors -- not re-run here, no LLM calls made by this script.",
        "baseline": "per-criterion pairwise accuracy against POOLED (all-annotator, "
                    "tie-dropped) human 'world' ranking blocks via covalx.judge.human_pairs "
                    "-- not prompt-level concordance, not the official arm-aggregate CoVal "
                    "scoring rule, not the 'personal'/'unacceptable' ranking blocks.",
        "regime": "OBSERVATIONAL/quasi-experimental only: naturally-occurring length "
                   "variation within already-existing full criteria, no randomized or "
                   "LLM-rewritten length manipulation; conclusions about full's short "
                   "tercile do not extrapolate beyond the length range actually present "
                   "in full (see mean_len_short_full vs mean_len_core for residual gap).",
    },

    "strongest_confound": ("Text length may proxy for content severity/verifiability "
                            "(terse criteria could just be objectively simpler content, "
                            "not merely tersely PHRASED content) rather than pure style. "
                            "H5 partials out the human importance score as a content-severity "
                            "covariate within full; this is an imperfect control (importance "
                            "= how much annotators cared, not verifiability/complexity), so "
                            "residual confounding by unmeasured content properties cannot be "
                            "fully ruled out without the disallowed LLM rewrite."),

    "sensitivity_prompt_weighted": sensitivity_prompt_weighted,

    "verdict": verdict,
    "verdict_reason": verdict_reason,
}

out_path = OUT_DIR / "independent_B.json"
out_path.write_text(json.dumps(results, indent=2))
print(f"\n[write] {out_path}")
print(f"[done] verdict={verdict} r_style={r_style_point:.3f} delta_raw={delta_raw:.4f}")
