"""
R124_negative_quarter / independent_B.py
=========================================

INDEPENDENT DESIGN. Do not read sibling `run.py` files or `independent_A.py` --
this design was built from the data dictionary and the shared `covalx` library
only.

THE CLAIM UNDER ATTACK
-----------------------
"coval_core is a faithful compilation of coval_full."

THE SPECIFIC ATTACK
--------------------
coval_full criteria carry human importance ratings on a -10..+10 scale. A
criterion whose *mean* rating across annotators is negative encodes "the
response should NOT do this" (raters directionally want the described
behaviour absent, e.g. "pick a side instead of staying neutral" rated -10..-2
by most annotators in the very first record of the release -- they want the
model to STAY NEUTRAL). coval_core is written entirely as positive
prescriptive statements ("Frame individual freedom as the central
criterion."). The question: when coval_core's criteria are scored for
satisfaction against the four candidate responses to a prompt, does that
score track how well responses do on the *negatively-rated* portion of
coval_full (i.e. how well they AVOID the disfavoured behaviour) with anything
like the weight it gives the *positively-rated* portion? Or is the
negatively-rated 25% of the input effectively invisible to core?

ESTIMAND (state before any code runs)
--------------------------------------
Restrict to prompts whose coval_full rubric contains >=1 criterion with
positive mean human rating and >=1 with negative mean human rating, and for
which satisfaction scores exist for all 4 candidate responses (A-D) on the
relevant coval_full criteria and on all coval_core criteria.

For criterion c with mean rating m_c and per-response satisfaction sat(c,r)
in [0,1] (P(response satisfies c), from the precomputed Qwen judge), define
the "alignment with what raters wanted" as:
    a(c,r) = sat(c,r)       if m_c > 0   (raters want c satisfied)
    a(c,r) = 1 - sat(c,r)   if m_c < 0   (raters want c AVOIDED)
For each prompt p and response r, define three summary scores by averaging
a(c,r) over the appropriate criterion group of that prompt:
    FULL_POS(p,r) = mean over {c : m_c > 0} of a(c,r)
    FULL_NEG(p,r) = mean over {c : m_c < 0} of a(c,r)
    CORE(p,r)     = mean over coval_core criteria of sat(c',r)   (core has no
                    ratings and is asserted to be positive-prescriptive, so
                    satisfaction IS alignment directly)

Demean FULL_POS, FULL_NEG, CORE *within each prompt* (subtract the
prompt's own mean over its 4 responses) -- this removes any prompt-level
confound (topic, overall response-set quality, rubric length) and isolates
the RELATIVE, response-vs-response signal within a fixed prompt. Regress the
demeaned CORE on demeaned FULL_POS and demeaned FULL_NEG (no intercept, OLS,
prompts clustered via a cluster bootstrap over prompts):

    CORE_dm(p,r) = beta_pos * FULL_POS_dm(p,r) + beta_neg * FULL_NEG_dm(p,r) + eps

beta_pos, beta_neg are the (absolute-scale, satisfaction-units) weights core
places on positively- vs negatively-rated content when explaining
response-to-response variation. THE HEADLINE STATISTIC is
    ratio = beta_neg / beta_pos
and the absolute difference beta_pos - beta_neg. ratio near 1 => core reflects
negative content about as much as positive content (faithful, on this axis).
ratio near 0 => core is functionally blind to the negatively-rated quarter of
the input.

A different estimand -- e.g. lexical/semantic overlap between core and full
criterion TEXT -- is a different experiment. This one asks whether core's
score, at scoring time, carries independent information about how well a
response does on the negatively-rated content, not whether core's prose
literally paraphrases it.

STRONGEST CONFOUND (named before running)
------------------------------------------
Negatively-rated criteria are NOT just opposite in sign to positively-rated
ones -- they are also far FEWER per prompt (EDA: mean full-rubric size 15.5,
mean negative fraction ~25%, so a typical prompt averages ~4 negative vs ~12
positive criteria). FULL_NEG is therefore a noisier group average purely
from averaging over fewer items, which under OLS mechanically shrinks its
estimated weight toward zero relative to FULL_POS's -- even if core treated
every individual criterion with EQUAL true importance regardless of sign.
This is an averaging/measurement-noise artifact of GROUP SIZE, not evidence
that core drops negative CONTENT.

CONTROL (run in this same script): a permutation null that mutates the
*assignment*, not the label. For every qualifying prompt, keep the criterion
COUNT split (n_pos, n_neg) exactly as observed, but randomly scramble WHICH
criteria (drawn from the same pooled full-rubric criterion list, using each
criterion's own true a(c,r)) land in the size-n_pos vs size-n_neg pseudo-group,
ignoring true sign. Refit the identical regression on many such pseudo-splits
to build a null distribution of ratio_perm attributable to group-size alone.
If the REAL ratio sits far below this null (empirical one-sided p <= 0.05),
group-size noise cannot explain the disparity and it is attributable to
polarity itself. If the real ratio is unremarkable within the null, the
group-size confound is NOT ruled out.

POSITIVE CONTROL / PLACEBO (synthetic, hand-derivable ground truth)
---------------------------------------------------------------------
Before trusting the real-data regression, the exact same estimation pipeline
(demean -> OLS -> cluster bootstrap) is run on SYNTHETIC data with the same
shape (same n_prompts, same 4 responses/prompt) and a KNOWN generating law:
    CORE_true = 0.7 * FULL_POS_true + 0.2 * FULL_NEG_true + noise   (positive control)
    CORE_true = 0.7 * FULL_POS_true + 0.0 * FULL_NEG_true + noise   (negative control)
The pipeline must recover beta_pos ~= 0.7 and beta_neg ~= 0.2 (resp. ~= 0.0)
within a pre-registered absolute tolerance. Failing this means the estimator
itself is structurally biased toward beta_neg ~= 0 regardless of the truth,
which would make the real-data result meaningless.

PRE-REGISTERED THRESHOLDS (fixed before the real numbers are seen)
---------------------------------------------------------------------
See the ALPHA / *_THRESHOLD / *_TOLERANCE constants immediately below.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx import load_join  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results" / "independent_B.json"

# --------------------------------------------------------------------- PRE-REGISTRATION
BASE_SEED = 4409
N_SEEDS = 5
SEEDS = [BASE_SEED + i for i in range(N_SEEDS)]
N_BOOT_PER_SEED = 1000          # cluster bootstrap resamples, per seed
N_PERM_PER_SEED = 400           # confound-control permutations, per seed

ALPHA = 0.05                    # nominal two-sided CI level, before correction
MIN_QUALIFYING_PROMPTS = 30     # below this: exit nonzero, data cannot support the question

# Real-data positive control (does core track ANYTHING in full at all?)
POS_CONTROL_MIN_EFFECT = 0.05   # beta_pos point estimate must exceed this (satisfaction units)
# (and its bootstrap CI lower bound must exceed 0)

# Primary/secondary disparity test
DISPARITY_RATIO_THRESHOLD = 0.5     # ratio below this = "substantially underweighted"
FAITHFUL_BAND = (0.5, 1.5)          # ratio inside this band, CI-supported = "faithful" on this axis
WIDE_CI_RATIO_SPAN = 3.0            # bootstrap ratio CI wider than this = underpowered -> UNVERIFIED

# Confound-control permutation test
PERM_CONFOUND_ALPHA = 0.05          # one-sided: P(ratio_perm <= ratio_real)

# Synthetic placebo tolerance
SYNTH_TRUE_POS, SYNTH_TRUE_NEG_HI, SYNTH_TRUE_NEG_LO = 0.7, 0.2, 0.0
SYNTH_TOLERANCE = 0.10              # absolute, satisfaction units
SYNTH_NOISE_SD = 0.05
SYNTH_N_PROMPTS = 400               # comparable order of magnitude to real qualifying set

# Multiplicity: 2 formal claims on real data (raw-unweighted, importance-weighted).
# Holm-Bonferroni across these 2 p-values, family alpha = 0.05.
FAMILY_ALPHA = 0.05

DATA_DIR = ROOT / "data"
NPZ_FULL = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
NPZ_CORE = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz"
LABELS = ("A", "B", "C", "D")


# --------------------------------------------------------------------- data loading
def load_sat_dict(npz_path: Path) -> dict[tuple[str, int, str], float]:
    d = np.load(npz_path, allow_pickle=True)
    out = {}
    for key, val in zip(d["meta"], d["sat"]):
        pid, idx, label = str(key).split("|")
        out[(pid, int(idx), label)] = float(val)
    return out


def build_dataset():
    joined = load_join(DATA_DIR / "comparisons.jsonl", DATA_DIR / "conversation_rubrics.jsonl")
    sat_full = load_sat_dict(NPZ_FULL)
    sat_core = load_sat_dict(NPZ_CORE)

    records = []  # one dict per qualifying prompt
    qc = dict(n_joined=len(joined), n_no_mixed_sign=0, n_missing_full_sat=0,
              n_missing_core_sat=0, n_qualifying=0,
              n_pos_per_prompt=[], n_neg_per_prompt=[],
              mean_abs_rating_pos=[], mean_abs_rating_neg=[])

    for pid, cmp_rec, rub_rec in joined:
        full = rub_rec["coval_full"]
        core = rub_rec["coval_core"]

        means = []
        for c in full:
            scores = [s["score"] for s in c.get("scores") or []]
            means.append(float(np.mean(scores)) if scores else 0.0)

        pos_idx = [i for i, m in enumerate(means) if m > 0]
        neg_idx = [i for i, m in enumerate(means) if m < 0]
        if not pos_idx or not neg_idx:
            qc["n_no_mixed_sign"] += 1
            continue

        # keep only criteria with complete 4-response satisfaction coverage
        def complete_full(i):
            return all((pid, i, lab) in sat_full for lab in LABELS)

        pos_idx = [i for i in pos_idx if complete_full(i)]
        neg_idx = [i for i in neg_idx if complete_full(i)]
        if not pos_idx or not neg_idx:
            qc["n_missing_full_sat"] += 1
            continue

        core_idx = [j for j in range(len(core)) if all((pid, j, lab) in sat_core for lab in LABELS)]
        if not core_idx:
            qc["n_missing_core_sat"] += 1
            continue

        # per-response aligned satisfaction a(c,r), pos and neg groups, raw + weighted
        full_pos = np.array([[sat_full[(pid, i, lab)] for i in pos_idx] for lab in LABELS])       # 4 x n_pos
        full_neg = np.array([[1.0 - sat_full[(pid, i, lab)] for i in neg_idx] for lab in LABELS])  # 4 x n_neg
        core_sat = np.array([[sat_core[(pid, j, lab)] for j in core_idx] for lab in LABELS])       # 4 x n_core

        w_pos = np.array([abs(means[i]) for i in pos_idx])
        w_neg = np.array([abs(means[i]) for i in neg_idx])

        rec = dict(
            pid=pid,
            full_pos_raw=full_pos.mean(axis=1),                       # (4,)
            full_neg_raw=full_neg.mean(axis=1),                       # (4,)
            full_pos_w=(full_pos * w_pos).sum(axis=1) / w_pos.sum(),
            full_neg_w=(full_neg * w_neg).sum(axis=1) / w_neg.sum(),
            core=core_sat.mean(axis=1),                               # (4,)
            n_pos=len(pos_idx), n_neg=len(neg_idx),
            # criteria pool for the permutation confound control: (a(c,r) for all c in pos+neg, 4xN)
            pool=np.concatenate([full_pos, full_neg], axis=1),        # 4 x (n_pos+n_neg)
        )
        records.append(rec)
        qc["n_qualifying"] += 1
        qc["n_pos_per_prompt"].append(len(pos_idx))
        qc["n_neg_per_prompt"].append(len(neg_idx))
        qc["mean_abs_rating_pos"].append(float(np.mean(w_pos)))
        qc["mean_abs_rating_neg"].append(float(np.mean(w_neg)))

    return records, qc


# --------------------------------------------------------------------- estimator
def demean(x: np.ndarray) -> np.ndarray:
    """x: (4,) per-prompt vector -> demeaned in place style (returns new array)."""
    return x - x.mean()


def fit_ols_2reg(pos_dm: np.ndarray, neg_dm: np.ndarray, y_dm: np.ndarray) -> tuple[float, float]:
    X = np.stack([pos_dm, neg_dm], axis=1)
    beta, *_ = np.linalg.lstsq(X, y_dm, rcond=None)
    return float(beta[0]), float(beta[1])


def assemble_xy(records, pos_key: str, neg_key: str):
    """Stack demeaned (pos, neg, core) across all prompts/responses; return arrays + pid index."""
    pos_all, neg_all, y_all, pid_all = [], [], [], []
    for rec in records:
        pos_all.append(demean(rec[pos_key]))
        neg_all.append(demean(rec[neg_key]))
        y_all.append(demean(rec["core"]))
        pid_all.append(rec["pid"])
    return (np.concatenate(pos_all), np.concatenate(neg_all), np.concatenate(y_all),
            np.repeat(np.arange(len(records)), 4))


def cluster_bootstrap(records, pos_key, neg_key, seeds, n_boot_per_seed):
    n = len(records)
    all_ratio, all_pos, all_neg, per_seed = [], [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        seed_pos, seed_neg, seed_ratio = [], [], []
        for _ in range(n_boot_per_seed):
            idx = rng.integers(0, n, size=n)
            sample = [records[i] for i in idx]
            pos_dm, neg_dm, y_dm, _ = assemble_xy(sample, pos_key, neg_key)
            bp, bn = fit_ols_2reg(pos_dm, neg_dm, y_dm)
            seed_pos.append(bp); seed_neg.append(bn)
            seed_ratio.append(bn / bp if abs(bp) > 1e-9 else np.nan)
        all_pos.extend(seed_pos); all_neg.extend(seed_neg); all_ratio.extend(seed_ratio)
        per_seed.append(dict(seed=seed,
                              beta_pos_ci=[float(np.percentile(seed_pos, 2.5)), float(np.percentile(seed_pos, 97.5))],
                              beta_neg_ci=[float(np.percentile(seed_neg, 2.5)), float(np.percentile(seed_neg, 97.5))],
                              ratio_median=float(np.nanmedian(seed_ratio))))
    all_pos, all_neg, all_ratio = map(np.array, (all_pos, all_neg, all_ratio))
    diff = all_neg - all_pos
    p_two_sided = 2 * min((diff <= 0).mean(), (diff >= 0).mean())
    p_two_sided = min(1.0, p_two_sided)
    return dict(
        beta_pos_point=None, beta_neg_point=None,  # filled by caller with the real point estimate
        beta_pos_ci=[float(np.percentile(all_pos, 2.5)), float(np.percentile(all_pos, 97.5))],
        beta_neg_ci=[float(np.percentile(all_neg, 2.5)), float(np.percentile(all_neg, 97.5))],
        ratio_ci=[float(np.nanpercentile(all_ratio, 2.5)), float(np.nanpercentile(all_ratio, 97.5))],
        ratio_median=float(np.nanmedian(all_ratio)),
        diff_ci=[float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
        p_diff_bootstrap=float(p_two_sided),
        per_seed=per_seed,
        n_boot_total=len(all_pos),
    )


def permutation_confound_control(records, seeds, n_perm_per_seed, real_ratio):
    """Scramble which criteria land in the size-n_pos vs size-n_neg pseudo-group,
    keeping counts fixed and using each criterion's own true a(c,r). Tests whether
    group-SIZE alone (not polarity) explains the observed weight disparity."""
    ratios = []
    for seed in seeds:
        rng = np.random.default_rng(seed + 500_000)
        for _ in range(n_perm_per_seed):
            pos_all, neg_all, y_all = [], [], []
            for rec in records:
                pool = rec["pool"]           # 4 x (n_pos+n_neg), true a(c,r) values
                n_pos, n_neg = rec["n_pos"], rec["n_neg"]
                n_tot = n_pos + n_neg
                perm = rng.permutation(n_tot)
                pseudo_pos_cols = perm[:n_pos]
                pseudo_neg_cols = perm[n_pos:]
                pseudo_pos = demean(pool[:, pseudo_pos_cols].mean(axis=1))
                pseudo_neg = demean(pool[:, pseudo_neg_cols].mean(axis=1))
                pos_all.append(pseudo_pos); neg_all.append(pseudo_neg)
                y_all.append(demean(rec["core"]))
            pos_all = np.concatenate(pos_all); neg_all = np.concatenate(neg_all); y_all = np.concatenate(y_all)
            bp, bn = fit_ols_2reg(pos_all, neg_all, y_all)
            if abs(bp) > 1e-9:
                ratios.append(bn / bp)
    ratios = np.array(ratios)
    p_one_sided = float((ratios <= real_ratio).mean())
    return dict(n_perm=len(ratios), null_ratio_median=float(np.median(ratios)),
                null_ratio_ci=[float(np.percentile(ratios, 2.5)), float(np.percentile(ratios, 97.5))],
                p_one_sided=p_one_sided)


def synthetic_placebo(n_prompts, true_pos, true_neg, seeds, n_boot_per_seed, noise_sd):
    results_per_seed = []
    for seed in seeds:
        rng = np.random.default_rng(seed + 900_000)
        records = []
        for _ in range(n_prompts):
            fp = rng.uniform(0, 1, size=4)
            fn = rng.uniform(0, 1, size=4)
            core = true_pos * fp + true_neg * fn + rng.normal(0, noise_sd, size=4)
            core = np.clip(core, 0, 1)
            records.append(dict(pid="synthetic", full_pos_raw=fp, full_neg_raw=fn, core=core))
        pos_dm, neg_dm, y_dm, _ = assemble_xy(records, "full_pos_raw", "full_neg_raw")
        bp, bn = fit_ols_2reg(pos_dm, neg_dm, y_dm)
        boot = cluster_bootstrap(records, "full_pos_raw", "full_neg_raw", [seed], n_boot_per_seed)
        results_per_seed.append(dict(seed=seed, beta_pos=bp, beta_neg=bn,
                                      beta_pos_ci=boot["beta_pos_ci"], beta_neg_ci=boot["beta_neg_ci"]))
    return results_per_seed


def holm_bonferroni(pvals: list[float], alpha: float) -> list[bool]:
    order = np.argsort(pvals)
    m = len(pvals)
    reject = [False] * m
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if pvals[idx] <= thresh:
            reject[idx] = True
        else:
            break
    return reject


# --------------------------------------------------------------------- main
def main():
    records, qc = build_dataset()
    n_q = qc["n_qualifying"]
    print(f"qualifying prompts: {n_q} / joined {qc['n_joined']}  "
          f"(no-mixed-sign={qc['n_no_mixed_sign']}, missing-full-sat={qc['n_missing_full_sat']}, "
          f"missing-core-sat={qc['n_missing_core_sat']})")

    if n_q < MIN_QUALIFYING_PROMPTS:
        print(f"FATAL: only {n_q} qualifying prompts (< {MIN_QUALIFYING_PROMPTS}); "
              f"data cannot support this estimand.")
        sys.exit(1)

    n_pos_arr = np.array(qc["n_pos_per_prompt"]); n_neg_arr = np.array(qc["n_neg_per_prompt"])
    descriptive = dict(
        n_qualifying_prompts=n_q,
        mean_n_pos=float(n_pos_arr.mean()), mean_n_neg=float(n_neg_arr.mean()),
        median_n_pos=float(np.median(n_pos_arr)), median_n_neg=float(np.median(n_neg_arr)),
        mean_abs_rating_pos=float(np.mean(qc["mean_abs_rating_pos"])),
        mean_abs_rating_neg=float(np.mean(qc["mean_abs_rating_neg"])),
        mean_sd_full_pos_within_prompt=float(np.mean([r["full_pos_raw"].std() for r in records])),
        mean_sd_full_neg_within_prompt=float(np.mean([r["full_neg_raw"].std() for r in records])),
    )
    print("descriptive:", json.dumps(descriptive, indent=2))

    # ---- SYNTHETIC PLACEBO / POSITIVE + NEGATIVE CONTROL ----
    synth_pos = synthetic_placebo(SYNTH_N_PROMPTS, SYNTH_TRUE_POS, SYNTH_TRUE_NEG_HI,
                                   SEEDS, N_BOOT_PER_SEED, SYNTH_NOISE_SD)
    synth_neg = synthetic_placebo(SYNTH_N_PROMPTS, SYNTH_TRUE_POS, SYNTH_TRUE_NEG_LO,
                                   SEEDS, N_BOOT_PER_SEED, SYNTH_NOISE_SD)

    def synth_ok(runs, true_pos, true_neg):
        bp = np.mean([r["beta_pos"] for r in runs]); bn = np.mean([r["beta_neg"] for r in runs])
        return (abs(bp - true_pos) <= SYNTH_TOLERANCE) and (abs(bn - true_neg) <= SYNTH_TOLERANCE), bp, bn

    synth_pos_ok, synth_pos_bp, synth_pos_bn = synth_ok(synth_pos, SYNTH_TRUE_POS, SYNTH_TRUE_NEG_HI)
    synth_neg_ok, synth_neg_bp, synth_neg_bn = synth_ok(synth_neg, SYNTH_TRUE_POS, SYNTH_TRUE_NEG_LO)
    placebo_pass = bool(synth_pos_ok and synth_neg_ok)
    print(f"placebo (true beta_neg={SYNTH_TRUE_NEG_HI}): recovered beta_pos={synth_pos_bp:.3f} "
          f"beta_neg={synth_pos_bn:.3f}  ok={synth_pos_ok}")
    print(f"placebo (true beta_neg={SYNTH_TRUE_NEG_LO}): recovered beta_pos={synth_neg_bp:.3f} "
          f"beta_neg={synth_neg_bn:.3f}  ok={synth_neg_ok}")

    if not placebo_pass:
        out = dict(verdict="UNVERIFIED", reason="synthetic placebo failed: estimator does not "
                   "recover known ground-truth coefficients, so the pipeline cannot be trusted "
                   "on real data.", synth_pos=synth_pos, synth_neg=synth_neg)
        RESULTS.write_text(json.dumps(out, indent=2))
        print("FATAL: placebo failed.")
        sys.exit(1)

    # ---- REAL DATA: point estimates + cluster bootstrap, raw and importance-weighted ----
    pos_dm, neg_dm, y_dm, _ = assemble_xy(records, "full_pos_raw", "full_neg_raw")
    bp_raw, bn_raw = fit_ols_2reg(pos_dm, neg_dm, y_dm)
    boot_raw = cluster_bootstrap(records, "full_pos_raw", "full_neg_raw", SEEDS, N_BOOT_PER_SEED)
    boot_raw["beta_pos_point"], boot_raw["beta_neg_point"] = bp_raw, bn_raw
    ratio_raw = bn_raw / bp_raw if abs(bp_raw) > 1e-9 else float("nan")

    pos_w_dm, neg_w_dm, y_w_dm, _ = assemble_xy(records, "full_pos_w", "full_neg_w")
    bp_w, bn_w = fit_ols_2reg(pos_w_dm, neg_w_dm, y_w_dm)
    boot_w = cluster_bootstrap(records, "full_pos_w", "full_neg_w", SEEDS, N_BOOT_PER_SEED)
    boot_w["beta_pos_point"], boot_w["beta_neg_point"] = bp_w, bn_w
    ratio_w = bn_w / bp_w if abs(bp_w) > 1e-9 else float("nan")

    corr_pos_neg = float(np.corrcoef(pos_dm, neg_dm)[0, 1])

    print(f"RAW:      beta_pos={bp_raw:.4f} (CI {boot_raw['beta_pos_ci']})  "
          f"beta_neg={bn_raw:.4f} (CI {boot_raw['beta_neg_ci']})  ratio={ratio_raw:.3f} "
          f"(CI {boot_raw['ratio_ci']})  p_diff={boot_raw['p_diff_bootstrap']:.4f}")
    print(f"WEIGHTED: beta_pos={bp_w:.4f} (CI {boot_w['beta_pos_ci']})  "
          f"beta_neg={bn_w:.4f} (CI {boot_w['beta_neg_ci']})  ratio={ratio_w:.3f} "
          f"(CI {boot_w['ratio_ci']})  p_diff={boot_w['p_diff_bootstrap']:.4f}")
    print(f"corr(FULL_POS_dm, FULL_NEG_dm) = {corr_pos_neg:.3f}  (multicollinearity diagnostic)")

    # ---- multiplicity correction across the 2 formal tests ----
    reject = holm_bonferroni([boot_raw["p_diff_bootstrap"], boot_w["p_diff_bootstrap"]], FAMILY_ALPHA)
    raw_significant, weighted_significant = reject

    # ---- real-data positive control ----
    pos_control_pass = (bp_raw > POS_CONTROL_MIN_EFFECT) and (boot_raw["beta_pos_ci"][0] > 0)
    print(f"real-data positive control (beta_pos > {POS_CONTROL_MIN_EFFECT} and CI lower > 0): "
          f"{pos_control_pass}")

    # ---- confound control: permutation null on group SIZE alone ----
    perm = permutation_confound_control(records, SEEDS, N_PERM_PER_SEED, ratio_raw)
    confound_ruled_out = perm["p_one_sided"] <= PERM_CONFOUND_ALPHA
    print(f"permutation confound control: null ratio median={perm['null_ratio_median']:.3f} "
          f"CI={perm['null_ratio_ci']}  real ratio={ratio_raw:.3f}  "
          f"p_one_sided(perm<=real)={perm['p_one_sided']:.4f}  confound_ruled_out={confound_ruled_out}")

    # ---- decision tree / verdict ----
    ci_width_ratio = (boot_raw["ratio_ci"][1] - boot_raw["ratio_ci"][0]) if np.isfinite(boot_raw["ratio_ci"][0]) else np.inf
    underpowered = (not pos_control_pass) or (ci_width_ratio > WIDE_CI_RATIO_SPAN)

    if underpowered:
        verdict = "UNVERIFIED"
        verdict_reason = ("real-data positive control failed or bootstrap ratio CI too wide "
                           "to distinguish faithful compilation from substantial underweighting.")
    elif raw_significant and ratio_raw < DISPARITY_RATIO_THRESHOLD and confound_ruled_out:
        verdict = "OVERTURNED"
        verdict_reason = (f"core's weight on negatively-rated content (beta_neg={bn_raw:.3f}) is "
                           f"significantly below its weight on positively-rated content "
                           f"(beta_pos={bp_raw:.3f}), ratio={ratio_raw:.3f} < {DISPARITY_RATIO_THRESHOLD}, "
                           f"and a permutation control shows this is not explained by the smaller "
                           f"criterion count of the negative group alone (p={perm['p_one_sided']:.4f}). "
                           f"'Faithful compilation' does not hold on this axis.")
    elif raw_significant and ratio_raw < DISPARITY_RATIO_THRESHOLD and not confound_ruled_out:
        verdict = "UNVERIFIED"
        verdict_reason = ("disparity is statistically significant but the group-size permutation "
                           "control could not rule out that it is a pure counting artifact rather "
                           "than a polarity effect.")
    elif (FAITHFUL_BAND[0] <= boot_raw["ratio_ci"][0]) and (boot_raw["ratio_ci"][1] <= FAITHFUL_BAND[1] * 1.5):
        verdict = "CONFIRMED"
        verdict_reason = (f"ratio CI {boot_raw['ratio_ci']} is consistent with core weighting "
                           f"negatively- and positively-rated content comparably; no significant "
                           f"disparity detected at the pre-registered threshold.")
    else:
        verdict = "UNVERIFIED"
        verdict_reason = "point estimate and CI do not cleanly fall into a pre-registered decision cell."

    print(f"\nVERDICT: {verdict}\n{verdict_reason}")

    out = dict(
        estimand=("Within-prompt regression of core's demeaned satisfaction score on the "
                  "demeaned aligned-satisfaction of coval_full's positively-rated vs "
                  "negatively-rated criteria, across the 4 candidate responses per prompt."),
        pre_registered_thresholds=dict(
            ALPHA=ALPHA, MIN_QUALIFYING_PROMPTS=MIN_QUALIFYING_PROMPTS,
            POS_CONTROL_MIN_EFFECT=POS_CONTROL_MIN_EFFECT,
            DISPARITY_RATIO_THRESHOLD=DISPARITY_RATIO_THRESHOLD,
            FAITHFUL_BAND=FAITHFUL_BAND, WIDE_CI_RATIO_SPAN=WIDE_CI_RATIO_SPAN,
            PERM_CONFOUND_ALPHA=PERM_CONFOUND_ALPHA, SYNTH_TOLERANCE=SYNTH_TOLERANCE,
            FAMILY_ALPHA=FAMILY_ALPHA, BASE_SEED=BASE_SEED, SEEDS=SEEDS,
        ),
        qc=qc, descriptive=descriptive,
        placebo=dict(pass_=placebo_pass,
                     positive_case=dict(true_pos=SYNTH_TRUE_POS, true_neg=SYNTH_TRUE_NEG_HI,
                                         recovered_pos=synth_pos_bp, recovered_neg=synth_pos_bn,
                                         per_seed=synth_pos),
                     negative_case=dict(true_pos=SYNTH_TRUE_POS, true_neg=SYNTH_TRUE_NEG_LO,
                                         recovered_pos=synth_neg_bp, recovered_neg=synth_neg_bn,
                                         per_seed=synth_neg)),
        real_data=dict(
            raw=dict(beta_pos=bp_raw, beta_neg=bn_raw, ratio=ratio_raw, boot=boot_raw,
                      holm_significant=bool(raw_significant)),
            weighted=dict(beta_pos=bp_w, beta_neg=bn_w, ratio=ratio_w, boot=boot_w,
                          holm_significant=bool(weighted_significant)),
            corr_full_pos_full_neg_demeaned=corr_pos_neg,
        ),
        positive_control_real_data=dict(pass_=bool(pos_control_pass),
                                        beta_pos=bp_raw, ci=boot_raw["beta_pos_ci"],
                                        threshold=POS_CONTROL_MIN_EFFECT),
        confound_control_permutation=dict(**perm, confound_ruled_out=bool(confound_ruled_out)),
        verdict=verdict,
        verdict_reason=verdict_reason,
        scopes=dict(
            population=(f"{n_q} of {qc['n_joined']} joined Collective-Alignment prompts whose "
                        f"coval_full rubric mixes positively- and negatively-rated criteria with "
                        f"complete 4-response satisfaction coverage (986 total rubric records, "
                        f"968 joined to a comparisons prompt_id, {qc['n_no_mixed_sign']} single-sign, "
                        f"{qc['n_missing_full_sat']+qc['n_missing_core_sat']} missing satisfaction "
                        f"coverage)."),
            instrument=("Satisfaction is a single local Qwen3.5 base model's sigmoid(logit-gap) "
                        "between ' Yes'/' No' on one forward pass per (criterion, response), not "
                        "human-labeled ground truth; the result is conditional on this judge's "
                        "reliability, which may itself differ systematically for negated vs "
                        "affirmative criterion phrasing -- an instrument-level risk this design "
                        "does not separately rule out."),
            baseline=("'Faithful' is operationalized as beta_neg approx beta_pos under an "
                      "unweighted per-criterion mean and, secondarily, an |importance|-weighted "
                      "mean; sign of a criterion is the SIGN OF THE MEAN human rating (utility "
                      "rule) across its annotators, not majority-vote or consensus rules."),
            regime=("Within-prompt, response-vs-response relative comparison (core's ability to "
                    "rank the SAME 4 candidate responses consistently with full's negatively- vs "
                    "positively-rated criteria), after removing all between-prompt variation by "
                    "demeaning. Says nothing about cross-prompt absolute levels or about textual/"
                    "semantic coverage of core's prose."),
        ),
    )
    RESULTS.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
