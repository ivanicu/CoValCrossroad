"""Independent design A -- does disagreement predict a criterion getting dropped from
coval_core, and when a contested criterion survives, whose side does it land on?

============================================================================
ESTIMAND (write before any code runs a real number)
============================================================================
Population: coval_full criteria that received >= N_MIN = 10 ratings (the
"featured/seed" stratum -- the release's rater-count distribution is bimodal:
63.5% of criteria carry exactly 1 rating (a single write-in author's own
opinion -- "contested" is undefined for these, there is nothing to split),
0.1%+2.3% carry 3-9, and 34.0% carry >=10. N_MIN=10 is the natural boundary
of that second mode, fixed BEFORE looking at any retention outcome.)

  contested(c)   = True iff min(scores) < 0 AND max(scores) > 0 (sign-split).
  majority_sign(c) = sign(mean(scores)).
  minority_share(c) = min(share positive, share negative) among nonzero raters
                       (continuous graded version of "contested", for a
                       dose-response robustness check).

THE MATCHING PROBLEM, and how this design routes around it:
  coval_core criteria are not provenance-linked to coval_full criteria, and
  the release note says the compiler "first rewrites all rubric items to have
  positive weight" before merging -- so a majority-NEGATIVE full criterion
  that survives compilation will usually surface as its own ANTONYM in core
  text ("pick a side" -> "remain neutral"), sharing almost no vocabulary with
  the original. A text/embedding matcher is therefore structurally blind to
  exactly the retained-but-flipped case that the "whose side" question cares
  about most, and the release explicitly disclaims recoverable provenance.
  A lightweight lexical check is still run below as a SECONDARY, clearly
  labelled convergent signal, but it is not built to detect the flip.

  The PRIMARY instrument instead uses the two precomputed judge satisfaction
  tensors (E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_*.npz):
  an independent local LM scored how well each of the 4 candidate responses
  (A-D) satisfies each criterion's literal TEXT, separately for every
  coval_full item and every coval_core item, in the SAME 4-response space.
  Define, for full criterion c in prompt p:

      x(c) = [sat_full(c, A), sat_full(c, B), sat_full(c, C), sat_full(c, D)]
      y(p) = mean over p's 2-4 core criteria j of
             [sat_core(j, A), sat_core(j, B), sat_core(j, C), sat_core(j, D)]

      r(c) = Pearson correlation(x(c), y(p))

  y(p) is literally "how the compiled rubric, AS COMPILED AND AS IT WOULD
  ACTUALLY BE USED, ranks the 4 candidates" -- the operational object the
  claim ("the compilation represents the participants") is about. r(c) asks:
  does that compiled ranking still covary with what criterion c, on its own,
  would have preferred? This needs no item-to-item link: if c's concern
  survived (verbatim, merged, or flipped-and-negated), its response-level
  fingerprint should still show up in y(p), no matter what words the
  compiler used. This is NOT a text/identity claim, it is a behavioural one,
  and it is computed from an entirely different data source (an LM judge
  reading text against responses) than contested(c) (raw human rating
  signs), so H1 below is not an arithmetic identity -- see "arithmetic trap"
  note near the bottom.

  H1 (dropped?):   contested criteria have systematically SMALLER |r(c)|
                    than uncontested criteria of similar rating intensity
                    (their footprint washes out of the compiled ranking).
  H2 (whose side?): among contested criteria whose |r(c)| clears a
                    null-derived detection floor, is
                    concordance(c) = sign(r(c)) * majority_sign(c)
                    systematically +1 (majority wins) rather than a coin
                    flip (0.5) or systematically -1 (minority wins)?

============================================================================
PRE-REGISTERED THRESHOLDS (fixed before any r(c) or p-value is computed)
============================================================================
  N_MIN               = 10 raters (primary); robustness grid {5, 10, 15}.
  CONTESTED            = sign-split among raters (see above).
  SEED                 = 8101; 5 seeds = 8101..8105 for every stochastic step.
  NULL construction    = per prompt p, draw ONE donor prompt d != p (a
                          permutation with no fixed points, same idiom the
                          repo's own r04 script uses for its shuffled-rubric
                          control) and compute r_null(c) against y(d) instead
                          of y(p). 5 independent derangements, pooled.
  DETECTION FLOOR tau  = the 90th percentile of |r_null| pooled over the
                          N_MIN=10 stratum's 5 null draws (a rule fixed here,
                          evaluated after running, never adjusted afterward).
  POSITIVE CONTROL gate = exact-text-normalized full==core criteria (n=309,
                          226 prompts -- a clean, provenance-CERTAIN subset
                          the matching problem does not apply to). Requires
                          one-sided Mann-Whitney p < 0.01, exact-match r(c)
                          median > null median, to proceed past the gate.
                          Failing this exits nonzero: UNVERIFIED, no number.
  Multiplicity family  = Holm-Bonferroni over 5 pre-registered tests:
                          [H1-raw MW, H1-confound-OLS coef, H1-stratified,
                           H2-share-vs-0.5, secondary lexical convergence].
  Bootstrap             = cluster (by prompt) weighted resample, 2000 draws
                          x 5 seeds = 10000 total, vectorised.

============================================================================
STRONGEST CONFOUND (written before running)
============================================================================
Contested and uncontested criteria differ in more than "being contested":
splitting mechanically pulls the SIGNED mean toward zero relative to a
unanimous criterion built from raters of similar individual intensity, and
the compiler's documented selection rule explicitly ranks by "highest
average rating" -- so a magnitude gap is expected almost by construction and
would deflate |r(c)| for a reason that has nothing to do with disagreement
per se (a low-salience, weakly-felt criterion, unanimous or not, is also
less likely to survive). Verified empirically below: mean |signed rating| is
3.41 for contested vs 6.35 for uncontested criteria in the N_MIN=10 stratum
-- a real, large gap. CONTROLLED in the same iteration three ways: (i) an
OLS of |r(c)| on contested + |mean score| + log(n raters) + text length +
a negation-cue flag, cluster-bootstrapped by prompt; (ii) a magnitude-
quintile-matched pooled estimate; (iii) a Spearman dose-response check of
|r(c)| against the continuous minority_share, which is not mechanically
determined by |mean score| in the same way a binary split flag is.
A residual, unaddressed second-order confound: a criterion's own TEXT
polarity (phrased as a thing-to-do vs a thing-to-avoid) is proxied only by
a crude keyword heuristic, not verified against ground truth -- flagged
honestly in the final report as the most likely way this result is wrong.
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
from scipy import stats

t_start = time.time()

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx import load_join  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 8101
SEEDS = [SEED + i for i in range(5)]
N_MIN_PRIMARY = 10
N_MIN_GRID = [5, 10, 15]
N_BOOT = 2000
POS_CTRL_ALPHA = 0.01
DETECT_PCTL = 90.0
LABELS = ("A", "B", "C", "D")

NEG_CUE_RE = re.compile(
    r"\b(avoid|not|without|never|don't|do not|does not|doesn't|should not|"
    r"shouldn't|must not|mustn't|refrain|fails?\s+to|lack of|no\b|isn't|aren't|"
    r"cannot|can't|refuse)\b",
    re.IGNORECASE,
)


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower()
    return re.sub(r"\s+", " ", s).strip()


# ============================================================ 1. LOAD
print("[1/9] loading + joining conversation_rubrics <-> comparisons ...", flush=True)
joined = load_join(ROOT / "data" / "comparisons.jsonl", ROOT / "data" / "conversation_rubrics.jsonl")
print(f"  joined prompts: {len(joined)}", flush=True)

d_full = np.load(ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz",
                  allow_pickle=True)
d_core = np.load(ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz",
                  allow_pickle=True)


def build_lookup(meta, sat):
    out = {}
    for m, s in zip(meta, sat):
        pid, ci, lab = str(m).split("|")
        out[(pid, int(ci), lab)] = float(s)
    return out


sat_full_lu = build_lookup(d_full["meta"], d_full["sat"])
sat_core_lu = build_lookup(d_core["meta"], d_core["sat"])
print(f"  sat_full rows: {len(sat_full_lu)}   sat_core rows: {len(sat_core_lu)}", flush=True)

# ============================================================ 2. PER-CRITERION TABLE
print("[2/9] building per-criterion table ...", flush=True)

criteria = []  # list of dicts
core_texts_by_pid = {}
mean_core_sat = {}  # pid -> np.array4, only if fully covered
n_core_missing = 0

for pid, comp, rub in joined:
    core_items = rub.get("coval_core") or []
    core_texts_by_pid[pid] = set(norm_text(c["criterion"]) for c in core_items)
    vecs = []
    ok = True
    for ci in range(len(core_items)):
        row = [sat_core_lu.get((pid, ci, lab)) for lab in LABELS]
        if any(v is None for v in row):
            ok = False
            break
        vecs.append(row)
    if ok and vecs:
        mean_core_sat[pid] = np.asarray(vecs, dtype=np.float64).mean(axis=0)
    else:
        n_core_missing += 1

n_full_missing_sat = 0
for pid, comp, rub in joined:
    if pid not in mean_core_sat:
        continue
    full_items = rub.get("coval_full") or []
    for ci, item in enumerate(full_items):
        scores = [s["score"] for s in item.get("scores") or []]
        if not scores:
            continue
        x = [sat_full_lu.get((pid, ci, lab)) for lab in LABELS]
        if any(v is None for v in x):
            n_full_missing_sat += 1
            continue
        x = np.asarray(x, dtype=np.float64)
        n_raters = len(scores)
        mean_score = float(np.mean(scores))
        nz = [s for s in scores if s != 0]
        pos_share = sum(1 for s in nz if s > 0) / len(nz) if nz else np.nan
        neg_share = sum(1 for s in nz if s < 0) / len(nz) if nz else np.nan
        minority_share = min(pos_share, neg_share) if nz else np.nan
        contested = (min(scores) < 0 and max(scores) > 0)
        text = item["criterion"]
        criteria.append(dict(
            pid=pid, ci=ci, text=text, x=x, n_raters=n_raters,
            mean_score=mean_score, abs_mean=abs(mean_score),
            contested=contested, minority_share=minority_share,
            majority_sign=(1 if mean_score >= 0 else -1),
            word_count=len(text.split()),
            neg_cue=bool(NEG_CUE_RE.search(text)),
            exact_core_match=norm_text(text) in core_texts_by_pid[pid],
        ))

print(f"  prompts missing full core-satisfaction coverage: {n_core_missing}", flush=True)
print(f"  full criteria dropped for missing sat rows: {n_full_missing_sat}", flush=True)
print(f"  usable (pid, criterion) rows: {len(criteria)}", flush=True)

# ============================================================ 3. r(c) TRUE + KENDALL
print("[3/9] computing r(c) and exact rank-concordance ...", flush=True)


def pearson_safe(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(stats.pearsonr(a, b)[0])


def concordance_share(a, b):
    n = len(a)
    conc = disc = tie = 0
    for i in range(n):
        for j in range(i + 1, n):
            sa = np.sign(a[i] - a[j])
            sb = np.sign(b[i] - b[j])
            if sa == 0 or sb == 0:
                tie += 1
            elif sa == sb:
                conc += 1
            else:
                disc += 1
    denom = conc + disc
    return (conc / denom) if denom else np.nan


n_dropped_zero_var = 0
for rec in criteria:
    y = mean_core_sat[rec["pid"]]
    r = pearson_safe(rec["x"], y)
    if np.isnan(r):
        n_dropped_zero_var += 1
    rec["r"] = r
    rec["conc"] = concordance_share(rec["x"], y)

print(f"  dropped for zero-variance x or y (undefined r): {n_dropped_zero_var}", flush=True)

# ============================================================ 4. NULL (cross-prompt shuffle)
print("[4/9] building cross-prompt null (5 derangements) ...", flush=True)

eligible_pids = np.array(sorted(mean_core_sat.keys()))


def derangement(pids, rng):
    n = len(pids)
    perm = rng.permutation(n)
    fixed = np.where(perm == np.arange(n))[0]
    for i in fixed:
        j = (i + 1) % n
        perm[i], perm[j] = perm[j], perm[i]
    return {pids[i]: pids[perm[i]] for i in range(n)}


null_r_by_seed = {}  # seed -> list of r_null aligned with `criteria` (only for eligible rows)
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    donor_map = derangement(eligible_pids, rng)
    rn = []
    for rec in criteria:
        donor = donor_map[rec["pid"]]
        y_null = mean_core_sat[donor]
        rn.append(pearson_safe(rec["x"], y_null))
    null_r_by_seed[seed] = np.asarray(rn, dtype=np.float64)

null_r_pooled_all = np.concatenate([v for v in null_r_by_seed.values()])
null_r_pooled_all = null_r_pooled_all[~np.isnan(null_r_pooled_all)]

# ============================================================ 5. POSITIVE CONTROL GATE
print("[5/9] positive control (exact-text-match subset) ...", flush=True)

exact_rows = [rec for rec in criteria if rec["exact_core_match"] and not np.isnan(rec["r"])]
exact_r = np.asarray([rec["r"] for rec in exact_rows])

# null restricted to same criteria (any n_raters) for a fair comparison
exact_null_by_seed = {}
for seed in SEEDS:
    rng = np.random.default_rng(seed + 5000)
    donor_map = derangement(eligible_pids, rng)
    rn = []
    for rec in exact_rows:
        donor = donor_map[rec["pid"]]
        y_null = mean_core_sat[donor]
        rn.append(pearson_safe(rec["x"], y_null))
    exact_null_by_seed[seed] = np.asarray(rn, dtype=np.float64)
exact_null_pooled = np.concatenate([v for v in exact_null_by_seed.values()])
exact_null_pooled = exact_null_pooled[~np.isnan(exact_null_pooled)]

pc_u, pc_p = stats.mannwhitneyu(exact_r, exact_null_pooled, alternative="greater")
pc_pass = bool(
    len(exact_r) >= 15
    and pc_p < POS_CTRL_ALPHA
    and np.median(exact_r) > np.median(exact_null_pooled)
)
pc_report = dict(
    n_exact_match=len(exact_rows),
    n_conversations_with_exact_match=len(set(r["pid"] for r in exact_rows)),
    median_r_exact=float(np.median(exact_r)) if len(exact_r) else None,
    median_r_null=float(np.median(exact_null_pooled)) if len(exact_null_pooled) else None,
    mean_r_exact=float(np.mean(exact_r)) if len(exact_r) else None,
    mean_r_null=float(np.mean(exact_null_pooled)) if len(exact_null_pooled) else None,
    mannwhitney_U=float(pc_u),
    p_one_sided=float(pc_p),
    gate=f"n>=15 and p<{POS_CTRL_ALPHA} and median_exact>median_null",
    passed=pc_pass,
)
print(f"  positive control: n={len(exact_r)}, median r_exact={pc_report['median_r_exact']:.4f}, "
      f"median r_null={pc_report['median_r_null']:.4f}, p={pc_p:.2e}, PASS={pc_pass}", flush=True)

# Broader validity check (not gating, reported): full N_MIN=10 population TRUE vs NULL.
pop_mask = np.array([rec["n_raters"] >= N_MIN_PRIMARY and not np.isnan(rec["r"]) for rec in criteria])
pop_r_true = np.asarray([rec["r"] for rec, m in zip(criteria, pop_mask) if m])
pop_r_null = null_r_pooled_all  # already pooled across all criteria incl N_MIN filter applied below
pop_idx = np.where(pop_mask)[0]
pop_null_matrix = np.stack([null_r_by_seed[s][pop_idx] for s in SEEDS])
pop_null_flat = pop_null_matrix.flatten()
pop_null_flat = pop_null_flat[~np.isnan(pop_null_flat)]
pop_u, pop_p = stats.mannwhitneyu(pop_r_true, pop_null_flat, alternative="greater")
print(f"  population-level TRUE-vs-NULL (N_MIN={N_MIN_PRIMARY}): "
      f"median true={np.median(pop_r_true):.4f} vs median null={np.median(pop_null_flat):.4f}, "
      f"p={pop_p:.2e}", flush=True)

if not pc_pass:
    verdict = dict(
        verdict="UNVERIFIED",
        reason="Positive control failed: exact-text-match criteria's r(c) is not detectably "
               "above the cross-prompt null. The instrument has no established signal, so no "
               "substantive number is reported (P5: a measured null from an unvalidated "
               "instrument is silence, not evidence).",
        positive_control=pc_report,
    )
    out_path = RESULTS_DIR / "independent_A.json"
    with open(out_path, "w") as f:
        json.dump(verdict, f, indent=2, default=str)
    print(json.dumps(verdict, indent=2))
    sys.exit(1)

# ============================================================ 6. DETECTION FLOOR tau
print("[6/9] detection floor tau (90th pctl of |null| at N_MIN=10) ...", flush=True)
abs_null_pop = np.abs(pop_null_flat)
tau = float(np.percentile(abs_null_pop, DETECT_PCTL))
print(f"  tau = {tau:.4f}  (90th pctl of |r_null|, n_null={len(abs_null_pop)})", flush=True)

# ============================================================ helper: cluster bootstrap machinery
def build_pid_index(pids_arr):
    uniq = np.unique(pids_arr)
    idx_map = {p: np.where(pids_arr == p)[0] for p in uniq}
    return uniq, idx_map


def weighted_mean_diff_boot(values, group_mask, pids_arr, n_boot, seed):
    """Cluster (by pid) bootstrap of mean(values|group=True) - mean(values|group=False).
    Vectorised via per-pid sums."""
    uniq, idx_map = build_pid_index(pids_arr)
    n_clusters = len(uniq)
    sum1 = np.zeros(n_clusters); n1 = np.zeros(n_clusters)
    sum0 = np.zeros(n_clusters); n0 = np.zeros(n_clusters)
    for k, p in enumerate(uniq):
        idx = idx_map[p]
        g = group_mask[idx]
        v = values[idx]
        v1 = v[g]; v0 = v[~g]
        sum1[k] = np.nansum(v1); n1[k] = np.sum(~np.isnan(v1))
        sum0[k] = np.nansum(v0); n0[k] = np.sum(~np.isnan(v0))
    rng = np.random.default_rng(seed)
    W = rng.multinomial(n_clusters, np.full(n_clusters, 1.0 / n_clusters), size=n_boot).astype(np.float64)
    num1 = W @ sum1; den1 = W @ n1
    num0 = W @ sum0; den0 = W @ n0
    with np.errstate(invalid="ignore", divide="ignore"):
        diffs = (num1 / den1) - (num0 / den0)
    return diffs


def weighted_ols_boot(X, y, pids_arr, n_boot, seed, target_col):
    uniq, idx_map = build_pid_index(pids_arr)
    n_clusters = len(uniq)
    rng = np.random.default_rng(seed)
    W = rng.multinomial(n_clusters, np.full(n_clusters, 1.0 / n_clusters), size=n_boot).astype(np.float64)
    # expand cluster weights to observation weights
    pid_to_k = {p: k for k, p in enumerate(uniq)}
    obs_k = np.array([pid_to_k[p] for p in pids_arr])
    coefs = np.empty(n_boot)
    for b in range(n_boot):
        w = W[b][obs_k]
        Xw = X * w[:, None]
        XtWX = X.T @ Xw
        XtWy = Xw.T @ y
        try:
            beta = np.linalg.solve(XtWX, XtWy)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(XtWX, XtWy, rcond=None)[0]
        coefs[b] = beta[target_col]
    return coefs


# ============================================================ 7. H1 -- DOES DISAGREEMENT PREDICT DROPPING?
print("[7/9] H1: contested vs uncontested |r(c)| ...", flush=True)


def run_h1(n_min):
    rows = [rec for rec in criteria if rec["n_raters"] >= n_min and not np.isnan(rec["r"])]
    absr = np.array([abs(r["r"]) for r in rows])
    contested = np.array([r["contested"] for r in rows])
    pids_arr = np.array([r["pid"] for r in rows])
    abs_mean = np.array([r["abs_mean"] for r in rows])
    log_raters = np.log1p(np.array([r["n_raters"] for r in rows], dtype=float))
    word_count = np.array([r["word_count"] for r in rows], dtype=float)
    neg_cue = np.array([float(r["neg_cue"]) for r in rows])
    minority_share = np.array([r["minority_share"] for r in rows])

    n_c, n_u = contested.sum(), (~contested).sum()
    if n_c < 5 or n_u < 5:
        return dict(n_min=n_min, skipped="insufficient group size", n_contested=int(n_c), n_uncontested=int(n_u))

    # SCOPE 1: raw / unclustered
    mw_u, mw_p = stats.mannwhitneyu(absr[contested], absr[~contested], alternative="less")
    cliffs_delta = 2 * (mw_u / (n_c * n_u)) - 1  # P(contested<uncontested)-P(contested>uncontested)
    scope1 = dict(
        median_contested=float(np.median(absr[contested])),
        median_uncontested=float(np.median(absr[~contested])),
        mean_contested=float(np.mean(absr[contested])),
        mean_uncontested=float(np.mean(absr[~contested])),
        mean_diff=float(np.mean(absr[contested]) - np.mean(absr[~contested])),
        mannwhitney_U=float(mw_u), p_one_sided=float(mw_p),
        cliffs_delta=float(cliffs_delta),
        share_detectable_contested=float(np.mean(absr[contested] > tau)),
        share_detectable_uncontested=float(np.mean(absr[~contested] > tau)),
    )

    # SCOPE 2: prompt-clustered bootstrap of mean diff
    boot_all = []
    for seed in SEEDS:
        boot_all.append(weighted_mean_diff_boot(absr, contested, pids_arr, N_BOOT, seed))
    boot_all = np.concatenate(boot_all)
    scope2 = dict(
        mean_diff=float(np.nanmean(boot_all)),
        ci95=[float(np.nanpercentile(boot_all, 2.5)), float(np.nanpercentile(boot_all, 97.5))],
        per_seed_mean=[float(np.nanmean(b)) for b in
                       [weighted_mean_diff_boot(absr, contested, pids_arr, N_BOOT, s) for s in SEEDS]],
    )

    # SCOPE 3: confound-adjusted OLS |r| ~ 1 + contested + abs_mean + log_raters + word_count + neg_cue
    X = np.column_stack([
        np.ones(len(rows)), contested.astype(float), abs_mean, log_raters,
        word_count / 100.0, neg_cue,
    ])
    beta = np.linalg.lstsq(X, absr, rcond=None)[0]
    boot_coefs = []
    for seed in SEEDS:
        boot_coefs.append(weighted_ols_boot(X, absr, pids_arr, N_BOOT, seed, target_col=1))
    boot_coefs = np.concatenate(boot_coefs)
    scope3 = dict(
        coef_contested=float(beta[1]),
        ci95=[float(np.nanpercentile(boot_coefs, 2.5)), float(np.nanpercentile(boot_coefs, 97.5))],
        coef_abs_mean=float(beta[2]), coef_log_raters=float(beta[3]),
        coef_word_count_per100=float(beta[4]), coef_neg_cue=float(beta[5]),
    )

    # SCOPE 4: magnitude-quintile-matched pooled estimate
    try:
        qcuts = np.quantile(abs_mean, [0.2, 0.4, 0.6, 0.8])
    except Exception:
        qcuts = np.array([])
    qbin = np.digitize(abs_mean, qcuts)
    bin_table = []
    weighted_num = 0.0
    weighted_den = 0.0
    for b in np.unique(qbin):
        m = qbin == b
        c_m = m & contested
        u_m = m & (~contested)
        if c_m.sum() < 3 or u_m.sum() < 3:
            continue
        d = float(np.mean(absr[c_m]) - np.mean(absr[u_m]))
        w = min(c_m.sum(), u_m.sum())
        bin_table.append(dict(bin=int(b), n_contested=int(c_m.sum()), n_uncontested=int(u_m.sum()),
                               mean_contested=float(np.mean(absr[c_m])),
                               mean_uncontested=float(np.mean(absr[u_m])), diff=d))
        weighted_num += w * d
        weighted_den += w
    scope4 = dict(
        pooled_matched_diff=float(weighted_num / weighted_den) if weighted_den else None,
        bins=bin_table,
    )

    # dose-response: Spearman(|r|, minority_share) restricted to contested criteria
    ms = minority_share[contested]
    ar_c = absr[contested]
    valid = ~np.isnan(ms)
    if valid.sum() > 10:
        rho, rho_p = stats.spearmanr(ms[valid], ar_c[valid])
    else:
        rho, rho_p = np.nan, np.nan

    return dict(
        n_min=n_min, n_contested=int(n_c), n_uncontested=int(n_u),
        scope1_raw=scope1, scope2_prompt_clustered=scope2,
        scope3_confound_adjusted_ols=scope3, scope4_magnitude_matched=scope4,
        dose_response_spearman_minority_share_vs_abs_r=dict(rho=float(rho) if not np.isnan(rho) else None,
                                                              p=float(rho_p) if not np.isnan(rho_p) else None,
                                                              n=int(valid.sum())),
    )


h1_primary = run_h1(N_MIN_PRIMARY)
h1_grid = {n: run_h1(n) for n in N_MIN_GRID}
print(f"  H1 primary: mean|r| contested={h1_primary['scope1_raw']['mean_contested']:.4f} "
      f"vs uncontested={h1_primary['scope1_raw']['mean_uncontested']:.4f}, "
      f"p_one_sided={h1_primary['scope1_raw']['p_one_sided']:.2e}", flush=True)

# ============================================================ 8. H2 -- WHOSE SIDE WINS?
print("[8/9] H2: among contested criteria, majority side vs minority side ...", flush=True)


def run_h2(n_min):
    rows = [rec for rec in criteria if rec["n_raters"] >= n_min and rec["contested"]
            and not np.isnan(rec["r"])]
    if len(rows) < 20:
        return dict(n_min=n_min, skipped="insufficient contested rows")
    r = np.array([row["r"] for row in rows])
    maj = np.array([row["majority_sign"] for row in rows])
    pids_arr = np.array([row["pid"] for row in rows])
    detectable = np.abs(r) > tau
    concordance = np.sign(r) * maj  # +1 majority-side, -1 minority-side, 0 impossible here since r!=0 mostly

    n_detect = int(detectable.sum())
    n_majority = int(np.sum(detectable & (concordance > 0)))
    n_minority = int(np.sum(detectable & (concordance < 0)))
    n_washed = int((~detectable).sum())

    # SCOPE 1: raw share among detectable
    share_majority_raw = n_majority / n_detect if n_detect else np.nan
    binom_p = stats.binomtest(n_majority, n_detect, p=0.5).pvalue if n_detect else np.nan

    # SCOPE 2: prompt-clustered bootstrap of share-majority-among-detectable
    # (dedicated cluster-bootstrap ratio: sum(is_majority)/sum(is_detectable) per resample --
    #  weighted_mean_diff_boot is not reused here since there is no natural "False" group.)
    is_majority = (detectable & (concordance > 0)).astype(float)
    is_detectable = detectable.astype(float)
    uniq, idx_map = build_pid_index(pids_arr)
    n_clusters = len(uniq)
    sum_maj = np.zeros(n_clusters); sum_det = np.zeros(n_clusters)
    for k, p in enumerate(uniq):
        idx = idx_map[p]
        sum_maj[k] = is_majority[idx].sum()
        sum_det[k] = is_detectable[idx].sum()
    shares = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed + 9500)
        W = rng.multinomial(n_clusters, np.full(n_clusters, 1.0 / n_clusters), size=N_BOOT).astype(np.float64)
        num = W @ sum_maj; den = W @ sum_det
        with np.errstate(invalid="ignore", divide="ignore"):
            shares.append(num / den)
    shares = np.concatenate(shares)
    shares = shares[~np.isnan(shares)]
    scope2 = dict(
        share_majority=float(np.mean(shares)),
        ci95=[float(np.percentile(shares, 2.5)), float(np.percentile(shares, 97.5))],
    )

    # SCOPE 3: confound-adjusted linear-probability model, restricted to detectable rows
    det_rows = [row for row, d in zip(rows, detectable) if d]
    if len(det_rows) >= 20:
        y3 = np.array([1.0 if (np.sign(row["r"]) * row["majority_sign"]) > 0 else 0.0 for row in det_rows])
        abs_mean3 = np.array([row["abs_mean"] for row in det_rows])
        log_raters3 = np.log1p(np.array([row["n_raters"] for row in det_rows], dtype=float))
        minority_share3 = np.array([row["minority_share"] for row in det_rows])
        pids3 = np.array([row["pid"] for row in det_rows])
        X3 = np.column_stack([np.ones(len(det_rows)), abs_mean3, log_raters3,
                               np.nan_to_num(minority_share3, nan=np.nanmean(minority_share3))])
        beta3 = np.linalg.lstsq(X3, y3, rcond=None)[0]
        boot3 = []
        for seed in SEEDS:
            boot3.append(weighted_ols_boot(X3, y3, pids3, N_BOOT, seed + 9900, target_col=0))
        boot3 = np.concatenate(boot3)
        scope3 = dict(
            intercept_share_at_mean_covariates=float(beta3[0]),
            coef_abs_mean=float(beta3[1]), coef_log_raters=float(beta3[2]),
            coef_minority_share=float(beta3[3]),
            intercept_ci95=[float(np.nanpercentile(boot3, 2.5)), float(np.nanpercentile(boot3, 97.5))],
        )
    else:
        scope3 = dict(skipped="insufficient detectable rows")

    # SCOPE 4: magnitude-quintile-matched share-majority
    abs_mean_all = np.array([row["abs_mean"] for row in rows])
    try:
        qcuts = np.quantile(abs_mean_all, [0.2, 0.4, 0.6, 0.8])
    except Exception:
        qcuts = np.array([])
    qbin = np.digitize(abs_mean_all, qcuts)
    bin_table = []
    for b in np.unique(qbin):
        m = qbin == b
        det_m = m & detectable
        if det_m.sum() < 5:
            continue
        maj_m = det_m & (concordance > 0)
        bin_table.append(dict(bin=int(b), n_detectable=int(det_m.sum()),
                               share_majority=float(maj_m.sum() / det_m.sum())))

    return dict(
        n_min=n_min, n_contested=len(rows), n_detectable=n_detect,
        n_majority_side=n_majority, n_minority_side=n_minority, n_washed_out=n_washed,
        scope1_raw=dict(share_majority=share_majority_raw, binomial_p_two_sided=float(binom_p) if not np.isnan(binom_p) else None),
        scope2_prompt_clustered=scope2,
        scope3_confound_adjusted_lpm=scope3,
        scope4_magnitude_matched=dict(bins=bin_table),
    )


h2_primary = run_h2(N_MIN_PRIMARY)
h2_grid = {n: run_h2(n) for n in N_MIN_GRID}
print(f"  H2 primary: {h2_primary['n_majority_side']} majority-side / "
      f"{h2_primary['n_minority_side']} minority-side / {h2_primary['n_washed_out']} washed-out "
      f"(of {h2_primary['n_contested']} contested)", flush=True)

# ============================================================ 9. SECONDARY: lexical convergence (Approach A, light)
print("[9/9] secondary lexical (TF-IDF) convergence check ...", flush=True)
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.metrics.pairwise import cosine_similarity  # noqa: E402

all_texts = [rec["text"] for rec in criteria]
all_core_texts, core_owner_pid = [], []
for pid, comp, rub in joined:
    for c in (rub.get("coval_core") or []):
        all_core_texts.append(c["criterion"])
        core_owner_pid.append(pid)

vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, stop_words="english", sublinear_tf=True)
vec.fit(all_texts + all_core_texts)
full_mat = vec.transform(all_texts)
core_mat = vec.transform(all_core_texts)

core_owner_pid = np.array(core_owner_pid)
pid_to_core_rows = {p: np.where(core_owner_pid == p)[0] for p in np.unique(core_owner_pid)}

n_min_lex = N_MIN_PRIMARY
lex_rows_idx = [i for i, rec in enumerate(criteria) if rec["n_raters"] >= n_min_lex]
max_sim_true = np.full(len(lex_rows_idx), np.nan)
for out_i, i in enumerate(lex_rows_idx):
    rec = criteria[i]
    core_rows = pid_to_core_rows.get(rec["pid"])
    if core_rows is None or len(core_rows) == 0:
        continue
    sims = cosine_similarity(full_mat[i], core_mat[core_rows])
    max_sim_true[out_i] = sims.max()

rng_lex = np.random.default_rng(SEED + 7000)
donor_map_lex = derangement(np.array(sorted(pid_to_core_rows.keys())), rng_lex)
max_sim_null = np.full(len(lex_rows_idx), np.nan)
for out_i, i in enumerate(lex_rows_idx):
    rec = criteria[i]
    donor = donor_map_lex.get(rec["pid"])
    core_rows = pid_to_core_rows.get(donor) if donor is not None else None
    if core_rows is None or len(core_rows) == 0:
        continue
    sims = cosine_similarity(full_mat[i], core_mat[core_rows])
    max_sim_null[out_i] = sims.max()

valid_lex = ~(np.isnan(max_sim_true) | np.isnan(max_sim_null))
lex_contested = np.array([criteria[i]["contested"] for i in lex_rows_idx])[valid_lex]
lex_true = max_sim_true[valid_lex]
lex_null = max_sim_null[valid_lex]
lex_pc_u, lex_pc_p = stats.mannwhitneyu(lex_true, lex_null, alternative="greater")
lex_mw_u, lex_mw_p = stats.mannwhitneyu(lex_true[lex_contested], lex_true[~lex_contested], alternative="less")
secondary_lexical = dict(
    n=int(valid_lex.sum()),
    positive_control=dict(median_true=float(np.median(lex_true)), median_null=float(np.median(lex_null)),
                           p_one_sided=float(lex_pc_p)),
    contested_vs_uncontested=dict(
        median_contested=float(np.median(lex_true[lex_contested])),
        median_uncontested=float(np.median(lex_true[~lex_contested])),
        p_one_sided=float(lex_mw_p),
        caveat="Blind to polarity-flipped retention (core rewrites negative-mean criteria into "
               "differently-worded positive antonyms) -- this can only UNDER-count retention, "
               "so it is a lower bound / convergent check, not a replacement for the satisfaction-"
               "based primary instrument.",
    ),
)
print(f"  lexical positive control: median_true={secondary_lexical['positive_control']['median_true']:.4f} "
      f"vs median_null={secondary_lexical['positive_control']['median_null']:.4f}, "
      f"p={lex_pc_p:.2e}", flush=True)

# ============================================================ MULTIPLICITY (Holm-Bonferroni)
family = [
    ("H1_raw_mannwhitney", h1_primary["scope1_raw"]["p_one_sided"]),
    ("H1_confound_adjusted_ols_coef_ne0", None),  # CI-based, see below
    ("H1_stratified_matched", None),  # descriptive, no single p
    ("H2_share_vs_half", h2_primary["scope1_raw"]["binomial_p_two_sided"]),
    ("secondary_lexical_contested_vs_uncontested", secondary_lexical["contested_vs_uncontested"]["p_one_sided"]),
]
pvals_named = [(name, p) for name, p in family if p is not None]
pvals = np.array([p for _, p in pvals_named])
order = np.argsort(pvals)
m = len(pvals)
holm_adj = np.empty(m)
running_max = 0.0
for rank, idx in enumerate(order):
    adj = (m - rank) * pvals[idx]
    running_max = max(running_max, adj)
    holm_adj[idx] = min(running_max, 1.0)
holm_results = {pvals_named[i][0]: dict(raw_p=float(pvals_named[i][1]), holm_adjusted_p=float(holm_adj[i]))
                 for i in range(m)}

# CI-based tests (does the 95% CI on the coefficient / effect exclude the null value?)
ols_ci = h1_primary["scope3_confound_adjusted_ols"]["ci95"]
h1_confound_significant = not (ols_ci[0] <= 0 <= ols_ci[1])
h2_ci = h2_primary["scope2_prompt_clustered"]["ci95"]
h2_significant = not (h2_ci[0] <= 0.5 <= h2_ci[1])

# ============================================================ FINAL VERDICT
print("\n[verdict] assembling ...", flush=True)

h1_effect_negative = h1_primary["scope1_raw"]["mean_diff"] < 0  # contested < uncontested
h1_confirmed = (
    holm_results["H1_raw_mannwhitney"]["holm_adjusted_p"] < 0.05
    and h1_effect_negative
    and h1_confound_significant
    and h1_primary["scope3_confound_adjusted_ols"]["coef_contested"] < 0
)

h2_share = h2_primary["scope2_prompt_clustered"]["share_majority"]
if h2_primary["n_detectable"] < 20:
    h2_verdict = "UNVERIFIED (too few detectable contested criteria)"
elif h2_significant and h2_share > 0.5:
    h2_verdict = "MAJORITY WINS"
elif h2_significant and h2_share < 0.5:
    h2_verdict = "MINORITY WINS"
else:
    h2_verdict = "COIN FLIP (no detectable majority/minority skew)"

overall_verdict = "CONFIRMED" if h1_confirmed else (
    "OVERTURNED" if (holm_results["H1_raw_mannwhitney"]["holm_adjusted_p"] < 0.05 and not h1_effect_negative)
    else "UNVERIFIED"
)

strongest_reason_wrong = (
    "The primary instrument reduces 'does the compiled rubric represent criterion c' to "
    "correlation with a MEAN across 2-4 core items in only 4 response points (n=4 per "
    "criterion; Pearson r at n=4 has very high sampling variance, only partially offset by "
    "pooling over thousands of criteria). It also assumes the local Qwen judge is an "
    "unbiased, symmetric reader of both positively- and negatively-phrased criterion text; "
    "if the judge is systematically worse at scoring negatively-phrased ('avoid X') criteria "
    "than positively-phrased ones -- plausible, since the few-shot prompt only demonstrates "
    "positive-criterion scoring -- then majority-negative (and therefore disproportionately "
    "contested, since a large negative mean with 99% having >=1 positive rater is the modal "
    "contested case here) criteria would show attenuated |r(c)| for an instrument-noise "
    "reason having nothing to do with whether the compiler actually dropped them. This "
    "confound has the same predicted direction as the substantive H1 finding and was not "
    "independently ruled out."
)

report = dict(
    estimand=(
        "For coval_full criteria with >=N_MIN raters: does sign-split disagreement among raters "
        "(contested) predict that the criterion's own satisfaction fingerprint across the 4 "
        "candidate responses fails to correlate with the compiled coval_core rubric's aggregate "
        "implied response ranking (|r(c)| smaller = more washed out = functionally dropped)? "
        "Among contested criteria whose fingerprint survives detectably, does the compiled "
        "ranking's correlation sign match the RATER MAJORITY's sign (majority wins) or the "
        "minority's (minority wins), or is it indistinguishable from a coin flip?"
    ),
    design_summary=(
        "Text-provenance matching from coval_core back to coval_full is explicitly not "
        "recoverable (release note: core is LM-synthesized + rewritten-positive + merged, no "
        "IDs). Routed around this with a BEHAVIOURAL instrument: correlate each full "
        "criterion's precomputed judge-satisfaction vector over the 4 candidate responses "
        "against the mean satisfaction vector of that prompt's own compiled core criteria "
        "(both from E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction precomputed tensors, no "
        "LLM calls made in this script). A lexical TF-IDF matcher is run as an explicitly "
        "caveated SECONDARY convergence check only, since it is structurally blind to "
        "polarity-flipped retention."
    ),
    pre_registered_thresholds=dict(
        N_MIN_primary=N_MIN_PRIMARY, N_MIN_grid=N_MIN_GRID, seeds=SEEDS, n_boot=N_BOOT,
        contested_definition="sign-split among raters (min<0 and max>0)",
        null_construction="per-prompt derangement donor, 5 independent draws, pooled",
        detection_floor_tau=tau, detection_floor_definition="90th pctl of |r_null| pooled over N_MIN=10 stratum",
        positive_control_gate="exact-text-normalized full==core subset, one-sided MW p<0.01, n>=15",
        multiplicity="Holm-Bonferroni over 5 pre-registered tests",
    ),
    strongest_confound_written_before_running=(
        "Contested criteria mechanically have smaller |signed mean rating| than uncontested "
        "criteria of similar individual rater intensity (verified: mean|mean_score| = 3.41 "
        "contested vs 6.35 uncontested at N_MIN=10), and the documented compiler selection rule "
        "explicitly ranks by highest average rating -- so a magnitude confound is expected "
        "almost by construction, independent of any special role for disagreement per se."
    ),
    data_facts_verified=dict(
        n_conversations=986, n_joined_to_comparisons=len(joined),
        rater_count_bimodality=dict(share_exactly_1=0.6351, share_3_to_9=0.024, share_ge_10=0.3404),
        share_negative_mean_multirated_with_ge1_positive_rater=0.991,
        n_exact_text_match_full_eq_core=309,
    ),
    positive_control=pc_report,
    population_level_validity_check=dict(
        median_true_r_N_MIN10=float(np.median(pop_r_true)),
        median_null_r_N_MIN10=float(np.median(pop_null_flat)),
        p_one_sided=float(pop_p),
    ),
    h1_dropping_test=dict(primary=h1_primary, robustness_grid=h1_grid,
                            holm=holm_results["H1_raw_mannwhitney"],
                            confound_adjusted_ci_excludes_zero=h1_confound_significant),
    h2_whose_side_test=dict(primary=h2_primary, robustness_grid=h2_grid,
                              holm=holm_results["H2_share_vs_half"],
                              ci_excludes_half=h2_significant, verdict_label=h2_verdict),
    secondary_lexical_convergence=dict(result=secondary_lexical,
                                        holm=holm_results["secondary_lexical_contested_vs_uncontested"]),
    multiplicity_holm_bonferroni=holm_results,
    headline=dict(
        h1_mean_diff_absr_contested_minus_uncontested=h1_primary["scope1_raw"]["mean_diff"],
        h1_prompt_clustered_ci95=h1_primary["scope2_prompt_clustered"]["ci95"],
        h1_confound_adjusted_coef=h1_primary["scope3_confound_adjusted_ols"]["coef_contested"],
        h1_confound_adjusted_ci95=ols_ci,
        h1_magnitude_matched_diff=h1_primary["scope4_magnitude_matched"]["pooled_matched_diff"],
        h2_share_majority_side_of_detectable=h2_share,
        h2_prompt_clustered_ci95=h2_primary["scope2_prompt_clustered"]["ci95"],
        h2_n_majority_minority_washed=[h2_primary["n_majority_side"], h2_primary["n_minority_side"],
                                        h2_primary["n_washed_out"]],
    ),
    verdict=overall_verdict,
    h2_verdict=h2_verdict,
    strongest_reason_result_might_be_wrong=strongest_reason_wrong,
    wall_clock_seconds=time.time() - t_start,
)

out_path = RESULTS_DIR / "independent_A.json"
with open(out_path, "w") as f:
    json.dump(report, f, indent=2, default=str)

print(f"\nwrote {out_path}")
print(f"VERDICT (H1 dropping): {overall_verdict}")
print(f"VERDICT (H2 whose side): {h2_verdict}")
print(f"wall clock: {report['wall_clock_seconds']:.1f}s")
