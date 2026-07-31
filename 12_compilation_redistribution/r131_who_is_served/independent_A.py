"""r131 / independent_A -- who is served by compilation?

ESTIMAND (named before any code ran; see PRE-REGISTRATION below)
------------------------------------------------------------------
Unit = a PERSON-PROMPT observation (p, q): one named annotator's judgement on
one prompt.  For each such observation we build THREE per-response score
vectors over the four candidate replies {A,B,C,D}, each derived from the
local-Qwen satisfaction tensors (judge reads "does response R satisfy
criterion C", one forward pass per pair -- already computed upstream):

  score_core(q)      -- coval_core's criteria (the COMPILED, 4-ish-item
                         rubric OpenAI ships with no ratings attached), mean
                         satisfaction, unweighted, ONE vector shared by every
                         person on that prompt.  This is literally what "the
                         compiled rubric" gives a participant: no personal
                         say in it at all.

  score_personal(p,q) -- coval_full's criteria (the UNCOMPILED, ~15-item
                         list), weighted by THAT PERSON's own -10..+10
                         importance ratings (sign(w)*sat, weight |w|,
                         normalized).  This is what the uncompiled release
                         still carries for this person, before compilation
                         throws the per-annotator ratings away.

  score_full_pooled(q) -- same coval_full items, but POOLED (population
                         mean-sign, unweighted across people) -- a control
                         arm with the same item-count richness as
                         score_personal but NONE of the personalization.
                         Isolates "more criteria" from "my own weighting".

Each score vector induces a ranking of {A,B,C,D}; each person's own
`ranking_blocks.world[0].ranking` (e.g. "A>B>C=D") induces a set of strict
pairwise preferences (ties dropped, via covalx.parse_ranking -- exactly the
release's own convention, covalx.human_pairs, applied per-person instead of
pooled).  accuracy(arm, p, q) = fraction of that person's own pairs the arm's
score correctly orders.

  Delta(p,q)        = accuracy(core,p,q)         - accuracy(personal,p,q)
  Delta_pooled(p,q) = accuracy(core,p,q)         - accuracy(full_pooled,q)
  Delta_sham(p,q,s) = accuracy(core,p,q)         - accuracy(core_sham_s,p,q)

Delta(p,q) is the headline quantity: POSITIVE means compilation serves this
person-prompt AT LEAST AS WELL as their own uncompiled, personally-weighted
signal would; NEGATIVE means compilation is a worse fit for this person than
what the release's own uncompiled data already encoded about them.  If
compilation is redistribution rather than summary, Delta(p,q) should show
real between-PERSON structure (some people consistent losers, some
consistent winners), not just prompt-to-prompt noise.

STRONGEST CONFOUND (written before running)
------------------------------------------------------------------
score_personal uses information (this person's OWN ratings) that
score_core structurally cannot have by design -- so any Core-worse-than-
personal gap could be trivially "more information wins", unrelated to
compilation / redistribution per se.  CONTROL: score_full_pooled has the
same item-count advantage as score_personal (all ~15 full criteria) but
NONE of the personalization.  If Delta_pooled is small/null while Delta is
large and structured by person, the gap is about LOSING PERSONALIZATION,
not about item count.  Both are computed and tested in the same run.

PRE-REGISTRATION (fixed BEFORE any Delta was computed)
------------------------------------------------------------------
  MIN_RATINGS        = 3     person must have rated >=3 coval_full criteria
                              on that prompt for score_personal to be defined
  MIN_PROMPTS_PERSON  = 3     person needs >=3 eligible prompts to enter the
                              person-level / heterogeneity / "who loses" analysis
  ALPHA_FDR           = 0.05  Benjamini-Hochberg across the fixed 10-test grid
                              (headline, pooled-confound, sign-robustness,
                              sham, heterogeneity, 3 continuous covariates,
                              2 categorical covariates) -- see TEST_GRID below
  LOSER_QUANTILE      = 0.25  bottom/top quartile of person-level Delta_p
  POS_CTRL_A_BAR      = 0.55 pairwise accuracy (chance=0.50), binomial p<0.01
  POS_CTRL_B_ICC_TRUE = 0.15 planted heterogeneity for the synthetic ANOVA/
                              permutation-engine control; recovery tolerance
                              |ICC_hat-ICC_true| < 0.07; reject H0 in >=4/5 seeds
  POS_CTRL_B_G0_FPR   = <=2/5 seeds falsely reject at ICC_true=0 (placebo)
  PRACTICAL_FLOOR     = 2.0   percentage points; a BH-significant headline
                              Delta must also clear this to be called
                              practically meaningful, not just detectable
  SEEDS               = [8101, 8102, 8103, 8104, 8105]  (>=5, per protocol)

Everything below is the implementation of exactly this pre-registration.
Nothing is computed and named afterwards.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from covalx import load_join, parse_ranking, human_pairs, LABELS  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_SEED = 8101
SEEDS = [BASE_SEED + i for i in range(5)]
MIN_RATINGS = 3
MIN_PROMPTS_PERSON = 3
ALPHA_FDR = 0.05
LOSER_Q = 0.25
POS_CTRL_A_BAR = 0.55
POS_CTRL_B_ICC_TRUE = 0.15
PRACTICAL_FLOOR_PP = 2.0  # percentage points

LAB_IDX = {l: i for i, l in enumerate(LABELS)}


# ============================================================ data loading
def load_everything():
    joined = load_join(str(REPO / "data/comparisons.jsonl"),
                        str(REPO / "data/conversation_rubrics.jsonl"))
    d_full = np.load(REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz")
    d_core = np.load(REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz")

    sat_full = defaultdict(dict)   # pid -> (idx,label) -> sat
    for m, s in zip(d_full["meta"], d_full["sat"]):
        pid, idx, lab = m.rsplit("|", 2)
        sat_full[pid][(int(idx), lab)] = float(s)
    sat_core = defaultdict(dict)
    for m, s in zip(d_core["meta"], d_core["sat"]):
        pid, idx, lab = m.rsplit("|", 2)
        sat_core[pid][(int(idx), lab)] = float(s)

    return joined, sat_full, sat_core


def person_pairs(ranking_str: str):
    """Strict pairwise preferences for ONE person's own ranking string.
    Same convention as covalx.human_pairs but not pooled across annotators."""
    r = parse_ranking(ranking_str)
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    pairs = []
    for a, ga in flat:
        for b, gb in flat:
            if ga < gb:
                pairs.append((a, b))
    return pairs


def accuracy(score_vec: np.ndarray, pairs: list) -> float | None:
    if not pairs:
        return None
    hits = 0.0
    for win, lose in pairs:
        sw, sl = score_vec[LAB_IDX[win]], score_vec[LAB_IDX[lose]]
        if sw > sl:
            hits += 1.0
        elif sw == sl:
            hits += 0.5
    return hits / len(pairs)


# ============================================================ two-way cluster SE (CGM)
def two_way_cluster_test(x: np.ndarray, cl1: np.ndarray, cl2: np.ndarray):
    """Cameron-Gelbach-Miller (2011) two-way cluster-robust SE for a simple mean
    (= OLS on an intercept). V_2way = V_cl1 + V_cl2 - V_white."""
    x = np.asarray(x, float)
    n = len(x)
    mu = float(x.mean())
    u = x - mu

    def clustered_var(u, cl):
        s = pd.Series(u).groupby(pd.Series(cl)).sum()
        return float((s.values ** 2).sum()) / (n * n)

    v1 = clustered_var(u, cl1)
    v2 = clustered_var(u, cl2)
    v0 = float((u ** 2).sum()) / (n * n)
    v2way = v1 + v2 - v0
    guarded = False
    if v2way <= 0:
        v2way = max(v1, v2)
        guarded = True
    se = float(np.sqrt(v2way))
    z = mu / se if se > 0 else float("nan")
    p = float(2 * (1 - stats.norm.cdf(abs(z)))) if se > 0 else float("nan")
    return dict(mean=mu, se=se, z=z, p=p, n=n, v_person=v1, v_prompt=v2, v_white=v0,
                negative_variance_guard_used=guarded)


def cluster_bootstrap_mean(x: np.ndarray, cl: np.ndarray, seeds, reps_per_seed=400):
    """Resample clusters (of `cl`) with replacement, gather their rows, recompute mean."""
    df = pd.DataFrame({"x": x, "cl": cl})
    groups = {g: sub["x"].values for g, sub in df.groupby("cl")}
    uniq = np.array(list(groups.keys()))
    means = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for _ in range(reps_per_seed):
            draw = rng.choice(uniq, size=len(uniq), replace=True)
            vals = np.concatenate([groups[g] for g in draw])
            means.append(vals.mean())
    means = np.array(means)
    return dict(boot_mean=float(means.mean()), boot_se=float(means.std(ddof=1)),
                ci_lo=float(np.percentile(means, 2.5)), ci_hi=float(np.percentile(means, 97.5)),
                n_reps=len(means))


# ============================================================ one-way random-effects ANOVA / ICC
def anova_icc(x: np.ndarray, groups: np.ndarray):
    df = pd.DataFrame({"x": np.asarray(x, float), "g": groups})
    grand_mean = df["x"].mean()
    N = len(df)
    grp = df.groupby("g")["x"]
    means = grp.mean()
    ns = grp.size()
    k = len(ns)
    ssb = float((ns * (means - grand_mean) ** 2).sum())
    row_group_mean = df["g"].map(means)
    ssw = float(((df["x"] - row_group_mean) ** 2).sum())
    dfb, dfw = k - 1, N - k
    msb = ssb / dfb if dfb > 0 else float("nan")
    msw = ssw / dfw if dfw > 0 else float("nan")
    n0 = (N - (ns ** 2).sum() / N) / dfb if dfb > 0 else float("nan")
    sigma_w = max(msw, 0.0)
    sigma_b = max(0.0, (msb - msw) / n0) if n0 and n0 > 0 else 0.0
    icc = sigma_b / (sigma_b + sigma_w) if (sigma_b + sigma_w) > 0 else 0.0
    return dict(icc=icc, sigma_b=sigma_b, sigma_w=sigma_w, msb=msb, msw=msw, k=k, N=N)


def permutation_icc_test(x: np.ndarray, groups: np.ndarray, seeds, n_perm_per_seed=1000):
    observed = anova_icc(x, groups)
    x = np.asarray(x, float)
    per_seed = []
    all_null_sigma_b = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        null_vals = np.empty(n_perm_per_seed)
        for i in range(n_perm_per_seed):
            xp = rng.permutation(x)
            null_vals[i] = anova_icc(xp, groups)["sigma_b"]
        all_null_sigma_b.append(null_vals)
        p_seed = float((null_vals >= observed["sigma_b"]).mean())
        per_seed.append(dict(seed=int(seed), p=p_seed))
    all_null = np.concatenate(all_null_sigma_b)
    p_combined = float((all_null >= observed["sigma_b"]).mean())
    return dict(observed=observed, per_seed=per_seed, p_combined=p_combined,
                n_perm_total=len(all_null))


# ============================================================ synthetic positive-control / placebo for the ANOVA+permutation engine
def synth_variance_component_control(real_group_sizes: np.ndarray, icc_true: float,
                                      total_var: float, seeds):
    """Build fully synthetic Delta(p,q) with KNOWN ICC = icc_true, using the REAL
    per-person prompt-count structure for realism. Feed through the exact same
    anova_icc + permutation_icc_test used on the real data; report recovery."""
    sigma_b_true = np.sqrt(icc_true * total_var)
    sigma_w_true = np.sqrt((1 - icc_true) * total_var)
    results = []
    for seed in seeds:
        rng = np.random.default_rng(seed + 90000)
        groups = []
        vals = []
        for gi, n_p in enumerate(real_group_sizes):
            eff = rng.normal(0, sigma_b_true)
            obs = eff + rng.normal(0, sigma_w_true, size=int(n_p))
            groups.extend([gi] * int(n_p))
            vals.extend(obs.tolist())
        vals = np.array(vals)
        groups = np.array(groups)
        est = anova_icc(vals, groups)
        # single-seed permutation check (cheap: 300 draws) for reject/no-reject at this seed
        rng2 = np.random.default_rng(seed + 190000)
        null_sb = np.array([anova_icc(rng2.permutation(vals), groups)["sigma_b"]
                             for _ in range(300)])
        p = float((null_sb >= est["sigma_b"]).mean())
        results.append(dict(seed=int(seed), icc_hat=est["icc"], sigma_b_hat=est["sigma_b"],
                             sigma_w_hat=est["sigma_w"], p=p, reject_at_05=bool(p < 0.05)))
    return dict(icc_true=icc_true, sigma_b_true=float(sigma_b_true),
                sigma_w_true=float(sigma_w_true), per_seed=results)


# ============================================================ BH-FDR
def benjamini_hochberg(pvals: dict, alpha: float):
    names = list(pvals.keys())
    p = np.array([pvals[n] for n in names])
    order = np.argsort(p)
    m = len(p)
    thresh = alpha * (np.arange(1, m + 1) / m)
    sorted_p = p[order]
    passed = sorted_p <= thresh
    if passed.any():
        k_max = np.max(np.where(passed)[0])
        cutoff = sorted_p[k_max]
    else:
        cutoff = 0.0
    sig = {names[order[i]]: bool(sorted_p[i] <= cutoff and passed_any(passed))
           for i in range(m)}
    return sig, float(cutoff)


def passed_any(passed):
    return bool(passed.any())


# ============================================================ main
def main():
    print("[1/6] loading data ...", flush=True)
    joined, sat_full, sat_core = load_everything()
    print(f"  joined prompts: {len(joined)}", flush=True)

    rows = []          # person-prompt level
    pair_rows = []      # pair level
    n_neg_full = 0
    n_full_crit_total = 0
    core_len_counter = defaultdict(int)
    prompts_missing_tensor = 0

    for pid, comp, rub in joined:
        if pid not in sat_full or pid not in sat_core:
            prompts_missing_tensor += 1
            continue
        full_crits = rub["coval_full"]
        core_crits = rub["coval_core"]
        n_full = len(full_crits)
        n_core = len(core_crits)
        core_len_counter[n_core] += 1
        if n_full == 0 or n_core == 0:
            continue

        try:
            sat_full_arr = np.array(
                [[sat_full[pid][(i, l)] for l in LABELS] for i in range(n_full)])
            sat_core_arr = np.array(
                [[sat_core[pid][(i, l)] for l in LABELS] for i in range(n_core)])
        except KeyError:
            prompts_missing_tensor += 1
            continue

        # ---- per-criterion pooled rating stats (established fact: ~1/4 negative)
        ann_ratings = defaultdict(dict)  # annotator_id -> {crit_idx: score}
        crit_scores = [[] for _ in range(n_full)]
        for ci, crit in enumerate(full_crits):
            for s in crit["scores"]:
                ann_ratings[s["annotator_id"]][ci] = float(s["score"])
                crit_scores[ci].append(float(s["score"]))
        pooled_mean = np.array([np.mean(v) if v else 0.0 for v in crit_scores])
        pooled_sign = np.where(pooled_mean >= 0, 1.0, -1.0)
        n_neg_full += int((pooled_mean < 0).sum())
        n_full_crit_total += n_full

        score_core = sat_core_arr.mean(axis=0)
        score_full_pooled_signed = (pooled_sign[:, None] * sat_full_arr).mean(axis=0)
        score_full_pooled_unsigned = sat_full_arr.mean(axis=0)

        sham_scores = {}
        subset_size = min(n_core, n_full)
        for seed in SEEDS:
            rng = np.random.default_rng(seed * 1_000_003 + hash(pid) % 999979)
            idx = rng.choice(n_full, size=subset_size, replace=False)
            sham_scores[seed] = sat_full_arr[idx, :].mean(axis=0)

        # pooled human pairs for positive-control A (per prompt)
        pooled_pairs = human_pairs(comp["metadata"]["assessments"])

        for a in comp["metadata"]["assessments"]:
            ann_id = a["annotator_id"]
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            pp = person_pairs(w[0].get("ranking", ""))
            if not pp:
                continue
            ratings = ann_ratings.get(ann_id, {})
            if len(ratings) < MIN_RATINGS:
                continue
            idxs = np.array(sorted(ratings.keys()))
            w_vec = np.array([ratings[i] for i in idxs])
            denom = np.abs(w_vec).sum()
            if denom == 0:
                continue
            sat_sel = sat_full_arr[idxs, :]
            score_personal = (w_vec[:, None] * sat_sel).sum(axis=0) / denom
            dist_consensus = float(np.mean(np.abs(w_vec - pooled_mean[idxs])))
            mean_abs_rating = float(np.mean(np.abs(w_vec)))

            acc_core = accuracy(score_core, pp)
            acc_personal = accuracy(score_personal, pp)
            acc_pooled_signed = accuracy(score_full_pooled_signed, pp)
            acc_pooled_unsigned = accuracy(score_full_pooled_unsigned, pp)
            acc_sham = {seed: accuracy(sham_scores[seed], pp) for seed in SEEDS}

            rows.append(dict(
                pid=pid, annotator_id=ann_id,
                acc_core=acc_core, acc_personal=acc_personal,
                acc_pooled_signed=acc_pooled_signed, acc_pooled_unsigned=acc_pooled_unsigned,
                **{f"acc_sham_{seed}": acc_sham[seed] for seed in SEEDS},
                n_ratings=len(ratings), mean_abs_rating=mean_abs_rating,
                dist_consensus=dist_consensus,
                subjectivity=a.get("subjectivity"), importance=a.get("importance"),
            ))

            for win, lose in pp:
                sw_c, sl_c = score_core[LAB_IDX[win]], score_core[LAB_IDX[lose]]
                sw_p, sl_p = score_personal[LAB_IDX[win]], score_personal[LAB_IDX[lose]]
                conc_core = 1.0 if sw_c > sl_c else (0.5 if sw_c == sl_c else 0.0)
                conc_pers = 1.0 if sw_p > sl_p else (0.5 if sw_p == sl_p else 0.0)
                pair_rows.append(dict(pid=pid, annotator_id=ann_id,
                                       diff=conc_core - conc_pers))

    df = pd.DataFrame(rows)
    pdf = pd.DataFrame(pair_rows)
    print(f"[2/6] eligible person-prompt rows: {len(df)}  pair rows: {len(pdf)}", flush=True)
    if len(df) < 500:
        print("FATAL: too few eligible observations to support the question.", file=sys.stderr)
        sys.exit(1)

    df["delta"] = df["acc_core"] - df["acc_personal"]
    df["delta_pooled"] = df["acc_core"] - df["acc_pooled_signed"]
    df["delta_pooled_unsigned"] = df["acc_core"] - df["acc_pooled_unsigned"]
    for seed in SEEDS:
        df[f"delta_sham_{seed}"] = df["acc_core"] - df[f"acc_sham_{seed}"]

    frac_neg_full = n_neg_full / n_full_crit_total
    print(f"  established-fact sanity check: pooled-negative full criteria = "
          f"{frac_neg_full:.3f} (expect ~0.25)", flush=True)

    # ==================================================== positive control A
    print("[3/6] positive control A (judge instrument aliveness) ...", flush=True)
    def prompt_level_pooled_accuracy(score_key):
        hits, tot = 0, 0
        for pid, comp, rub in joined:
            if pid not in sat_core or pid not in sat_full:
                continue
            pooled_pairs = human_pairs(comp["metadata"]["assessments"])
            if not pooled_pairs:
                continue
            n_core = len(rub["coval_core"])
            if score_key == "core":
                sv = np.array([[sat_core[pid][(i, l)] for l in LABELS]
                               for i in range(n_core)]).mean(axis=0)
            hits_here = 0
            for win, lose in pooled_pairs:
                sw, sl = sv[LAB_IDX[win]], sv[LAB_IDX[lose]]
                hits_here += 1.0 if sw > sl else (0.5 if sw == sl else 0.0)
            hits += hits_here
            tot += len(pooled_pairs)
        return hits / tot, tot

    acc_A, n_A = prompt_level_pooled_accuracy("core")
    p_A = float(stats.binomtest(int(round(acc_A * n_A)), n_A, 0.5, alternative="greater").pvalue)
    pos_ctrl_A = dict(pooled_pairwise_accuracy_core=acc_A, n_pairs=n_A, p_vs_chance=p_A,
                       bar=POS_CTRL_A_BAR, passed=bool(acc_A > POS_CTRL_A_BAR and p_A < 0.01))
    print(f"  core-arm pooled pairwise accuracy vs human world-rankings: "
          f"{acc_A:.4f} (n={n_A}, p={p_A:.2e}) -> {'PASS' if pos_ctrl_A['passed'] else 'FAIL'}",
          flush=True)

    # ==================================================== positive control B (synthetic)
    print("[4/6] positive control B (synthetic ANOVA/permutation engine check) ...", flush=True)
    elig_counts = df.groupby("annotator_id").size()
    elig_persons = elig_counts[elig_counts >= MIN_PROMPTS_PERSON].index
    df_h = df[df["annotator_id"].isin(elig_persons)].copy()
    real_group_sizes = df_h.groupby("annotator_id").size().values
    total_var_real = float(df_h["delta"].var(ddof=1))

    posB_g = synth_variance_component_control(real_group_sizes, POS_CTRL_B_ICC_TRUE,
                                               total_var_real, SEEDS)
    posB_0 = synth_variance_component_control(real_group_sizes, 0.0, total_var_real, SEEDS)
    g_rejects = sum(r["reject_at_05"] for r in posB_g["per_seed"])
    g0_rejects = sum(r["reject_at_05"] for r in posB_0["per_seed"])
    icc_hats_g = [r["icc_hat"] for r in posB_g["per_seed"]]
    posB_pass = bool(
        abs(np.mean(icc_hats_g) - POS_CTRL_B_ICC_TRUE) < 0.07
        and g_rejects >= 4
        and g0_rejects <= 2
    )
    pos_ctrl_B = dict(planted=posB_g, placebo_g0=posB_0,
                       g_rejects_of_5=g_rejects, g0_false_rejects_of_5=g0_rejects,
                       mean_icc_hat_at_g=float(np.mean(icc_hats_g)),
                       passed=posB_pass)
    print(f"  planted ICC={POS_CTRL_B_ICC_TRUE}: recovered mean ICC_hat="
          f"{np.mean(icc_hats_g):.3f}, rejected H0 in {g_rejects}/5 seeds; "
          f"placebo (ICC=0) false-rejected in {g0_rejects}/5 -> "
          f"{'PASS' if posB_pass else 'FAIL'}", flush=True)

    # ==================================================== four scopes
    print("[5/6] four scopes + heterogeneity + who-loses ...", flush=True)
    scope_pair = two_way_cluster_test(pdf["diff"].values, pdf["annotator_id"].values,
                                       pdf["pid"].values)
    scope_person_prompt = two_way_cluster_test(df["delta"].values, df["annotator_id"].values,
                                                df["pid"].values)
    person_level = df.groupby("annotator_id")["delta"].mean()
    prompt_level = df.groupby("pid")["delta"].mean()

    def one_sample(x):
        x = np.asarray(x, float)
        mu, se = float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))
        z = mu / se if se > 0 else float("nan")
        p = float(2 * (1 - stats.norm.cdf(abs(z)))) if se > 0 else float("nan")
        return dict(mean=mu, se=se, z=z, p=p, n=len(x))

    scope_person = one_sample(person_level.values)
    scope_person_boot = cluster_bootstrap_mean(df["delta"].values, df["annotator_id"].values, SEEDS)
    scope_prompt = one_sample(prompt_level.values)
    scope_prompt_boot = cluster_bootstrap_mean(df["delta"].values, df["pid"].values, SEEDS)

    # pooled-confound test & sign-robustness spec cell
    test_pooled = two_way_cluster_test(df["delta_pooled"].values, df["annotator_id"].values,
                                        df["pid"].values)
    test_pooled_unsigned = two_way_cluster_test(df["delta_pooled_unsigned"].values,
                                                 df["annotator_id"].values, df["pid"].values)

    # sham
    sham_tests = {}
    for seed in SEEDS:
        sham_tests[seed] = two_way_cluster_test(df[f"delta_sham_{seed}"].values,
                                                  df["annotator_id"].values, df["pid"].values)
    sham_means = [sham_tests[s]["mean"] for s in SEEDS]
    test_sham_combined = two_way_cluster_test(
        np.mean([df[f"delta_sham_{s}"].values for s in SEEDS], axis=0),
        df["annotator_id"].values, df["pid"].values)

    # heterogeneity: ANOVA ICC + permutation, restricted to df_h (>=3 prompts/person)
    het = permutation_icc_test(df_h["delta"].values, df_h["annotator_id"].values, SEEDS,
                                n_perm_per_seed=1000)
    person_means_h = df_h.groupby("annotator_id")["delta"].mean()
    within_sd_h = df_h.groupby("annotator_id")["delta"].std(ddof=0).dropna()
    floor = dict(between_person_sd_pp=float(person_means_h.std(ddof=1) * 100),
                 median_within_person_sd_pp=float(within_sd_h.median() * 100),
                 icc_hat=het["observed"]["icc"], sigma_b=het["observed"]["sigma_b"],
                 sigma_w=het["observed"]["sigma_w"], p_permutation=het["p_combined"])

    # who loses
    lo_q, hi_q = person_means_h.quantile(LOSER_Q), person_means_h.quantile(1 - LOSER_Q)
    losers = person_means_h[person_means_h <= lo_q].index
    winners = person_means_h[person_means_h >= hi_q].index

    cov = df_h.groupby("annotator_id").agg(
        delta_p=("delta", "mean"),
        mean_abs_rating=("mean_abs_rating", "mean"),
        n_ratings=("n_ratings", "mean"),
        dist_consensus=("dist_consensus", "mean"),
        subjectivity=("subjectivity", lambda s: s.mode().iloc[0] if len(s.mode()) else None),
        importance=("importance", lambda s: s.mode().iloc[0] if len(s.mode()) else None),
    )

    rho_rating, p_rating = stats.spearmanr(cov["delta_p"], cov["mean_abs_rating"])
    rho_nrate, p_nrate = stats.spearmanr(cov["delta_p"], cov["n_ratings"])
    rho_dist, p_dist = stats.spearmanr(cov["delta_p"], cov["dist_consensus"])

    def kw_test(cov, col):
        groups = [g["delta_p"].values for _, g in cov.groupby(col) if len(g) >= 5]
        if len(groups) < 2:
            return float("nan"), float("nan"), 0
        stat, p = stats.kruskal(*groups)
        return float(stat), float(p), len(groups)

    kw_subj_stat, kw_subj_p, kw_subj_ngrp = kw_test(cov, "subjectivity")
    kw_imp_stat, kw_imp_p, kw_imp_ngrp = kw_test(cov, "importance")

    subj_means = cov.groupby("subjectivity")["delta_p"].agg(["mean", "count"]).sort_values("mean")
    imp_means = cov.groupby("importance")["delta_p"].agg(["mean", "count"]).sort_values("mean")

    # ==================================================== multiplicity (BH-FDR over the 10-test grid)
    print("[6/6] multiplicity control + assembling report ...", flush=True)
    pvals = {
        "1_headline_core_vs_personal": scope_person_prompt["p"],
        "2_confound_core_vs_pooled": test_pooled["p"],
        "3_spec_core_vs_pooled_unsigned": test_pooled_unsigned["p"],
        "4_sham_core_vs_random4": test_sham_combined["p"],
        "5_heterogeneity_permutation": het["p_combined"],
        "6_cov_rating_extremity": p_rating,
        "7_cov_n_ratings": p_nrate,
        "8_cov_dist_consensus": p_dist,
        "9_cov_subjectivity": kw_subj_p,
        "10_cov_importance": kw_imp_p,
    }
    sig, cutoff = benjamini_hochberg(pvals, ALPHA_FDR)

    headline_pp = scope_person_prompt["mean"] * 100
    practical = abs(headline_pp) >= PRACTICAL_FLOOR_PP

    # ==================================================== verdict
    if not pos_ctrl_A["passed"] or not pos_ctrl_B["passed"]:
        verdict = "UNVERIFIED"
        verdict_reason = "a validity control (positive control A or B) failed; instrument not trusted"
    elif sig["1_headline_core_vs_personal"] and headline_pp < 0 and practical:
        verdict = "OVERTURNED"
        verdict_reason = ("compiled arm reproduces the average person's own ranking worse than "
                           "their own uncompiled personalized signal would, beyond both the FDR "
                           "threshold and the practical floor")
    elif sig["1_headline_core_vs_personal"] and headline_pp > 0 and practical:
        verdict = "CONFIRMED"
        verdict_reason = "compiled arm reproduces personal rankings at least as well as personalization"
    else:
        verdict = "UNVERIFIED"
        verdict_reason = "headline effect did not clear both the FDR threshold and the practical floor"

    strongest_reason_wrong = (
        "score_personal's advantage may come from OVERFITTING to that person's own stated "
        "importance ratings via the SAME judge that scores satisfaction (both derive from the "
        "same Qwen instrument reading the same response text against related criteria text), so "
        "part of the core-vs-personal gap could be measurement leakage (the personal score is "
        "'told' more about what this person likes through weights correlated with their own "
        "ranking rationale) rather than a real personalization effect that a genuinely blind "
        "aggregator would also lose. The full_pooled control addresses item-count but not this "
        "leakage channel, since personal weights are informative in a way pooled sign is not."
    )

    report = {
        "estimand": "person-prompt level: does the compiled coval_core rubric reproduce a named "
                    "annotator's own 4-way response ranking as well as that same person's own "
                    "uncompiled, importance-weighted coval_full signal would",
        "unit": "primary unit = person-prompt observation (p,q); rolled up to person, prompt, "
                "and pair scopes below",
        "pre_registration": dict(
            MIN_RATINGS=MIN_RATINGS, MIN_PROMPTS_PERSON=MIN_PROMPTS_PERSON,
            ALPHA_FDR=ALPHA_FDR, LOSER_QUANTILE=LOSER_Q, POS_CTRL_A_BAR=POS_CTRL_A_BAR,
            POS_CTRL_B_ICC_TRUE=POS_CTRL_B_ICC_TRUE, PRACTICAL_FLOOR_PP=PRACTICAL_FLOOR_PP,
            SEEDS=SEEDS,
        ),
        "data_scale": dict(
            n_joined_prompts=len(joined), prompts_missing_tensor=prompts_missing_tensor,
            n_person_prompt_rows=len(df), n_pair_rows=len(pdf),
            n_unique_annotators=int(df["annotator_id"].nunique()),
            n_annotators_min_prompts=int(len(elig_persons)),
            core_len_distribution={str(k): v for k, v in core_len_counter.items()},
            established_fact_check_frac_pooled_negative_full_criteria=frac_neg_full,
        ),
        "positive_control_A_judge_alive": pos_ctrl_A,
        "positive_control_B_synthetic_engine": pos_ctrl_B,
        "confound_written_before_running": (
            "score_personal has strictly more information (this person's own importance "
            "ratings) than score_core can structurally have; any gap could just be "
            "'more information wins', unrelated to compilation/redistribution."
        ),
        "confound_control_result_delta_pooled": {
            "definition": "core vs full_pooled: same item-count richness as personal, "
                           "population-mean sign, but NO personalization",
            "two_way_cluster_test": test_pooled,
            "mean_pp": test_pooled["mean"] * 100,
        },
        "four_scopes": {
            "1_pair_level": {**scope_pair, "mean_pp": scope_pair["mean"] * 100,
                              "note": "diff = concordant_core - concordant_personal per pairwise "
                                      "comparison, two-way clustered by annotator and prompt"},
            "2_person_prompt_level_HEADLINE": {**scope_person_prompt,
                                                "mean_pp": scope_person_prompt["mean"] * 100},
            "3_person_level": {**scope_person, "mean_pp": scope_person["mean"] * 100,
                                "cluster_bootstrap_crosscheck": {
                                    **scope_person_boot,
                                    "boot_mean_pp": scope_person_boot["boot_mean"] * 100}},
            "4_prompt_level": {**scope_prompt, "mean_pp": scope_prompt["mean"] * 100,
                                "cluster_bootstrap_crosscheck": {
                                    **scope_prompt_boot,
                                    "boot_mean_pp": scope_prompt_boot["boot_mean"] * 100}},
        },
        "specification_curve": {
            "core_vs_personal_signed_full": {"mean_pp": scope_person_prompt["mean"] * 100,
                                              "p": scope_person_prompt["p"]},
            "core_vs_pooled_signed_full": {"mean_pp": test_pooled["mean"] * 100,
                                            "p": test_pooled["p"]},
            "core_vs_pooled_UNSIGNED_full": {"mean_pp": test_pooled_unsigned["mean"] * 100,
                                              "p": test_pooled_unsigned["p"],
                                              "note": "robustness cell ignoring the established "
                                                      "negative-quarter fact -- shown to "
                                                      "demonstrate the convention matters"},
        },
        "sham_curated_core_vs_random_k_subset": {
            "definition": "core's own criteria vs a random same-size subset of that prompt's "
                           "OWN coval_full criteria, unsigned mean satisfaction, no personalization",
            "per_seed": {str(s): {"mean_pp": sham_tests[s]["mean"] * 100, "p": sham_tests[s]["p"]}
                         for s in SEEDS},
            "combined_across_seeds": {**test_sham_combined, "mean_pp": test_sham_combined["mean"] * 100},
            "seed_spread_pp": {"min": min(sham_means) * 100, "max": max(sham_means) * 100,
                                "sd": float(np.std(sham_means, ddof=1)) * 100},
        },
        "heterogeneity_and_floor": {
            "restricted_to_persons_with_min_prompts": MIN_PROMPTS_PERSON,
            "n_persons": len(elig_persons),
            "anova_icc": het["observed"],
            "permutation_p_per_seed": het["per_seed"],
            "permutation_p_combined": het["p_combined"],
            "floor_comparison_pp": floor,
            "interpretation": (
                "between-person SD and median within-person SD are directly comparable in "
                "percentage points of pairwise accuracy; ICC_hat is the ANOVA variance-component "
                "share attributable to stable person effects, permutation-tested against a null "
                "that destroys person structure while preserving each person's sample size."
            ),
        },
        "who_loses": {
            "n_losers": len(losers), "n_winners": len(winners),
            "loser_mean_delta_pp": float(person_means_h[losers].mean() * 100),
            "winner_mean_delta_pp": float(person_means_h[winners].mean() * 100),
            "covariate_tests": {
                "rating_extremity_spearman": {"rho": float(rho_rating), "p": float(p_rating)},
                "n_ratings_contributed_spearman": {"rho": float(rho_nrate), "p": float(p_nrate)},
                "distance_from_consensus_spearman": {"rho": float(rho_dist), "p": float(p_dist)},
                "subjectivity_kruskal_wallis": {"stat": kw_subj_stat, "p": kw_subj_p,
                                                 "n_groups": kw_subj_ngrp},
                "importance_kruskal_wallis": {"stat": kw_imp_stat, "p": kw_imp_p,
                                               "n_groups": kw_imp_ngrp},
            },
            "delta_p_by_subjectivity_category": {
                str(k): {"mean_pp": float(v["mean"] * 100), "n_persons": int(v["count"])}
                for k, v in subj_means.iterrows()},
            "delta_p_by_importance_category": {
                str(k): {"mean_pp": float(v["mean"] * 100), "n_persons": int(v["count"])}
                for k, v in imp_means.iterrows()},
        },
        "multiplicity_control": {
            "method": "Benjamini-Hochberg FDR over the fixed 10-test pre-registered grid",
            "alpha": ALPHA_FDR, "bh_cutoff_p": cutoff,
            "raw_pvalues": pvals, "significant_after_bh": sig,
            "n_cells_tested": len(pvals),
            "n_cells_surviving": int(sum(sig.values())),
        },
        "headline": {
            "mean_delta_pp": headline_pp,
            "se_pp": scope_person_prompt["se"] * 100,
            "ci95_pp": [headline_pp - 1.96 * scope_person_prompt["se"] * 100,
                        headline_pp + 1.96 * scope_person_prompt["se"] * 100],
            "practical_floor_pp": PRACTICAL_FLOOR_PP,
            "clears_practical_floor": practical,
            "bh_significant": sig["1_headline_core_vs_personal"],
            "cohen_d": float(scope_person_prompt["mean"] / df["delta"].std(ddof=1)),
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "strongest_reason_result_might_be_wrong": strongest_reason_wrong,
    }

    out_path = OUT_DIR / "independent_A.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=float)
    print(f"\nwrote {out_path}", flush=True)
    print(f"HEADLINE: mean Delta(core-personal) = {headline_pp:+.2f}pp "
          f"(se={scope_person_prompt['se']*100:.2f}pp), BH-sig={sig['1_headline_core_vs_personal']}, "
          f"verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
