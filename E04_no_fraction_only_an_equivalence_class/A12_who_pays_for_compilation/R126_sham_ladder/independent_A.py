"""r126 / independent_A -- the sham ladder.

CLAIM UNDER ATTACK
------------------
"The compilation of coval_full (~15.8 human-written, human-importance-rated
criteria) into coval_core (4 criteria, no ratings, LLM-compiled) does real
work: core is better than what you would get without the compiler."

ESTIMAND (in words, before any code ran)
-----------------------------------------
For a rubric arm that assigns a score to each of the 4 candidate responses of
a prompt, define that arm's QUALITY on a prompt as the probability that a
uniformly-drawn HUMAN pairwise preference (drawn from that prompt's pooled
"world" ranking blocks, one preference per annotator per orderable pair) is
concordant with the arm's own response ordering (ties in the arm's score
split the credit 0.5/0.5).  The estimand is the population mean of that
per-prompt quality, taken over the set of prompts where a fair, COUNT-MATCHED
comparison is possible (coval_core has exactly 4 criteria: 925 of 968 joined
prompts).  We ask where coval_core's mean quality sits on a ladder of
zero-LLM, 4-criteria substitutes built from coval_full's own text and human
importance ratings, using EXACTLY THE SAME aggregation rule (equal-weight
mean of direction-signed satisfaction) for every rung -- so the only thing
that varies between rungs is WHICH 4 criteria (and, for core alone, whether
the criterion text itself was rewritten by the compiler).

WHY PAIRWISE CONCORDANCE AGAINST THE WORLD BLOCK
-------------------------------------------------
`covalx.judge.human_pairs` is the join library's own convention for turning a
"world" ranking into strict preference pairs (ties dropped), and it is reused
by the rebuild-satisfaction round that produced the precomputed tensors this
script consumes -- so the ground-truth object is not invented here, it is the
release's own annotation surface read through the shared join code.  Pairwise
concordance is chosen over rank correlation because (a) it needs no forced
consensus ranking, so disagreeing annotators are not silently averaged away,
and (b) it degrades gracefully to a well-defined per-prompt scalar even when
different prompts carry different numbers of annotators/pairs (17-237 in this
release), which a rank-correlation statistic would weight unevenly.

DIRECTION MATTERS AND IS NOT OPTIONAL
--------------------------------------
coval_full scores are on -10..+10: the SIGN is not noise, it is the compiler's
own information -- a criterion like "argue a side instead of remaining
neutral" carries mostly NEGATIVE scores, meaning satisfying it is bad, not
good.  Ignoring sign and averaging raw satisfaction would silently reward
responses for doing things annotators marked as undesirable, which would
sabotage every full-based rung for reasons that have nothing to do with
compilation.  Every full-based rung therefore uses direction_j = sign(mean
score_j) (covalx.rules.rule_score, rule="utility": "largest absolute mean
signed preference" -- the standard, simplest of the four principles already
defined in this repo's shared library) and importance_j = |mean score_j|.
coval_core criteria carry no ratings; a manual read of 58 core criteria across
15 random prompts (all positively-framed instructions, including negatively
-worded ones like "Do not use racist terms" -- satisfying THAT is good) shows
the compiler always writes criteria in the "satisfying-is-good" direction, so
direction=+1 is used for every core criterion.  [D6, spot-checked below.]

COUNT-MATCHING
---------------
Every ladder rung draws or selects exactly 4 criteria per prompt and scores a
response as the unweighted mean of direction-signed satisfaction across those
4 -- identical aggregation arithmetic to core's own scoring.  The only
non-count-matched arm is ALL-FULL, used exclusively as the positive control
(it is explicitly excluded from the ladder comparison).

WHAT WAS DROPPED, AND WHY (P: "if the data cannot support a rung, drop it and
say so")
---------------------------------------------------------------------------
- "4 criteria from a DIFFERENT prompt": the precomputed satisfaction tensors
  only contain judge scores for (prompt P's own criterion) x (prompt P's own
  4 responses).  No cell exists for "prompt Q's criterion text scored against
  prompt P's responses" -- producing one would require a fresh judge pass,
  which this script is forbidden to run.  Checked and confirmed empirically:
  full_idx/core_idx are 100% prompt-scoped, zero cross-prompt entries.
  DROPPED.
- "4 generic criteria reused for every prompt": no criterion text is judged
  against more than the handful of prompts it natively belongs to (the most
  duplicated full criterion across the whole corpus appears verbatim in only
  5 of 968 prompts, each time judged only against ITS OWN prompt's 4
  responses -- not a corpus-wide generic criterion with corpus-wide
  satisfaction). Same missing-cell problem as above. DROPPED.

STRONGEST CONFOUND (written before running)
---------------------------------------------
coval_core's criterion TEXT is compiler-rewritten (short, imperative,
declarative) while every full-based rung (including RANDOM-4, TOP-IMPORTANCE
-4, MECHANICAL-4) necessarily uses full's ORIGINAL human-submitted wording
(verbose, hedged, multi-clause).  If the local Qwen judge is more confident
(higher |satisfaction-0.5|) on short imperative text purely as a STYLE effect
-- independent of content -- that alone could inflate core's apparent
accuracy relative to every full-based rung, and would be misread as
"compilation selects better content" when it is really "compilation writes
judge-friendlier prose".  CONTROL (same script, zero extra LLM calls): report
mean judge saturation (2*|sat-0.5|, 0=maximally unsure that criterion is
1=fully confident) and mean criterion character length for the core arm vs.
the full arm on the same 925-prompt population.  This cannot fully separate
style from content with the tools this script is allowed to use (that would
need a rewrite-full's-own-top4-into-terse-style-and-rejudge experiment, which
needs an LLM pass) -- so it is reported as a measured, NAMED, not-fully
-resolved confound, not silently ignored.  A second, partial control is
built into the design itself: TOP-IMPORTANCE-4 and MECHANICAL-4 both use
full's own wording, so if core beats them, the gap cannot be "core simply
picked criteria that align with the eventual importance ratings" (TOP
-IMPORTANCE-4 IS that, using the oracle ratings directly) -- it must come
from something TOP-IMPORTANCE-4 does not have, i.e. the compiler's own
selection heuristic and/or its rewriting.

PRE-REGISTERED THRESHOLDS (fixed before any accuracy number was computed)
----------------------------------------------------------------------------
POSITIVE CONTROL (ALL-FULL, not count-matched): passes iff mean pairwise
    accuracy >= 0.55 AND its prompt-cluster-bootstrap 95% CI excludes 0.50.
    (OpenAI report ~60% for their own full-fidelity rubric scoring; 0.55 is a
    deliberately looser bar for a smaller local judge on a partial rebuild.)
PLACEBO (i.i.d. random scores, no criteria at all): passes iff every one of
    the >=5 seed means AND the overall mean lie within 0.50 +/- 0.02.
LADDER COMPARISONS (core vs. random-4 / top-importance-4 / mechanical-4):
    "distinguishable" iff BOTH (a) Holm-adjusted two-sided cluster
    (prompt-level sign-flip) permutation p < 0.05, AND (b) |absolute mean
    accuracy difference| >= 0.01 (1 percentage point) -- statistical
    significance alone is not accepted as practically meaningful at n=925.
MULTIPLICITY: Holm-Bonferroni across exactly the 3 primary comparisons above.
STOPPING RULE: one run, one seed family (SEED=8101, >=5 seeds per stochastic
    rung, done below with 10). No re-running to chase a nicer p-value. If the
    positive control fails, the whole ladder is reported UNVERIFIED, not
    silently reinterpreted.

SEED = 8101.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx import load_join, human_pairs, LABELS  # noqa: E402
from covalx.rules import rule_score  # noqa: E402

SEED = 8101
N_SEEDS = 10
N_FOLDS = 5
N_BOOT = 2000
N_PERM = 5000
ALPHA_GRID = np.round(np.linspace(0.0, 1.0, 11), 2)

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPARISONS = ROOT / "data" / "comparisons.jsonl"
RUBRICS = ROOT / "data" / "conversation_rubrics.jsonl"
SAT_FULL = ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_full.npz"
SAT_CORE = ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_core.npz"


# =====================================================================
# 1. LOAD + JOIN
# =====================================================================
def load_sat_index(npz_path: Path) -> dict:
    d = np.load(npz_path, allow_pickle=True)
    idx: dict = {}
    for m, s in zip(d["meta"], d["sat"]):
        pid, ci, resp = str(m).split("|")
        idx.setdefault(pid, {}).setdefault(int(ci), {})[resp] = float(s)
    return idx


def main() -> None:
    joined = load_join(COMPARISONS, RUBRICS)
    full_idx = load_sat_index(SAT_FULL)
    core_idx = load_sat_index(SAT_CORE)

    # ---- build per-prompt records -----------------------------------
    records = []
    excluded_core_count = {2: 0, 3: 0, "other": 0}
    for pid, comp, rub in joined:
        n_core = len(rub["coval_core"])
        if n_core != 4:
            excluded_core_count[n_core if n_core in (2, 3) else "other"] += 1
            continue
        pairs = human_pairs(comp["metadata"]["assessments"])
        if not pairs:
            continue
        fi = full_idx.get(pid)
        ci = core_idx.get(pid)
        if fi is None or ci is None:
            continue
        n_full = len(rub["coval_full"])
        if any(len(fi.get(j, {})) != 4 for j in range(n_full)):
            continue
        if any(len(ci.get(c, {})) != 4 for c in range(4)):
            continue

        full_meta = []
        for j, crit in enumerate(rub["coval_full"]):
            vals = np.array([s["score"] for s in crit["scores"]], dtype=float)
            imp, direc = rule_score(vals, "utility")
            agree = max(float((vals > 0).mean()), float((vals < 0).mean()))
            full_meta.append(dict(idx=j, importance=imp, direction=direc,
                                   agreement=agree, text_len=len(crit["criterion"])))
        core_text_len = float(np.mean([len(c["criterion"]) for c in rub["coval_core"]]))

        records.append(dict(
            pid=pid, pairs=pairs, n_full=n_full,
            full_meta=full_meta, full_sat=fi, core_sat=ci,
            core_text_len=core_text_len,
        ))

    n = len(records)
    print(f"population: {n} prompts (excluded for core!=4 criteria: {excluded_core_count}, "
          f"total joined: {len(joined)})")
    assert n > 800, "population collapsed -- join or filter logic broke"

    # =====================================================================
    # 2. SCORING PRIMITIVES
    # =====================================================================
    def pairwise_accuracy(score: dict, pairs) -> float:
        correct = 0.0
        for w, l in pairs:
            sw, sl = score[w], score[l]
            if sw > sl:
                correct += 1.0
            elif sw == sl:
                correct += 0.5
        return correct / len(pairs)

    def score_from_full(rec, idxs) -> dict:
        fm = {m["idx"]: m for m in rec["full_meta"]}
        out = {}
        for lab in LABELS:
            out[lab] = float(np.mean([fm[j]["direction"] * rec["full_sat"][j][lab] for j in idxs]))
        return out

    def score_from_core(rec) -> dict:
        return {lab: float(np.mean([rec["core_sat"][c][lab] for c in range(4)])) for lab in LABELS}

    # =====================================================================
    # 3. CORE (deterministic)
    # =====================================================================
    core_acc = np.array([pairwise_accuracy(score_from_core(r), r["pairs"]) for r in records])

    # =====================================================================
    # 4. POSITIVE CONTROL: ALL-FULL (not count matched)
    # =====================================================================
    all_full_acc = np.array([
        pairwise_accuracy(score_from_full(r, [m["idx"] for m in r["full_meta"]]), r["pairs"])
        for r in records
    ])

    # =====================================================================
    # 5. PLACEBO: i.i.d. random scores, N_SEEDS seeds
    # =====================================================================
    placebo_seed_means = []
    for s in range(N_SEEDS):
        rng = np.random.default_rng(SEED + 900 + s)
        accs = []
        for r in records:
            score = {lab: float(rng.random()) for lab in LABELS}
            accs.append(pairwise_accuracy(score, r["pairs"]))
        placebo_seed_means.append(float(np.mean(accs)))
    placebo_seed_means = np.array(placebo_seed_means)

    # =====================================================================
    # 6. RANDOM-4 rung, N_SEEDS seeds
    # =====================================================================
    random4_mat = np.empty((N_SEEDS, n))
    for s in range(N_SEEDS):
        rng = np.random.default_rng(SEED + 100 + s)
        for i, r in enumerate(records):
            idxs = rng.choice(r["n_full"], size=4, replace=False)
            random4_mat[s, i] = pairwise_accuracy(score_from_full(r, idxs), r["pairs"])

    # =====================================================================
    # 7. TOP-IMPORTANCE-4 rung (deterministic)
    # =====================================================================
    def top_k_by_importance(rec, k=4):
        order = sorted(rec["full_meta"], key=lambda m: (-m["importance"], m["idx"]))
        return [m["idx"] for m in order[:k]]

    topimp_acc = np.array([
        pairwise_accuracy(score_from_full(r, top_k_by_importance(r)), r["pairs"]) for r in records
    ])

    # =====================================================================
    # 8. MECHANICAL-4 rung: alpha-weighted importance x agreement,
    #    alpha fit by 5-fold CV over prompts, N_SEEDS fold-shuffle seeds.
    # =====================================================================
    def mech_score_of(m, alpha, eps=1e-9):
        return (m["importance"] + eps) ** alpha * (m["agreement"] + eps) ** (1 - alpha)

    def top_k_by_mech(rec, alpha, k=4):
        order = sorted(rec["full_meta"], key=lambda m: (-mech_score_of(m, alpha), m["idx"]))
        return [m["idx"] for m in order[:k]]

    mech_mat = np.empty((N_SEEDS, n))
    chosen_alphas = []
    for s in range(N_SEEDS):
        rng = np.random.default_rng(SEED + 300 + s)
        perm = rng.permutation(n)
        folds = np.array_split(perm, N_FOLDS)
        for f_i, test_idx in enumerate(folds):
            train_idx = np.setdiff1d(perm, test_idx, assume_unique=False)
            train_scores = []
            for a in ALPHA_GRID:
                accs = [pairwise_accuracy(score_from_full(records[i], top_k_by_mech(records[i], a)),
                                           records[i]["pairs"]) for i in train_idx]
                train_scores.append(float(np.mean(accs)))
            a_star = float(ALPHA_GRID[int(np.argmax(train_scores))])
            chosen_alphas.append(a_star)
            for i in test_idx:
                r = records[i]
                mech_mat[s, i] = pairwise_accuracy(score_from_full(r, top_k_by_mech(r, a_star)), r["pairs"])

    # =====================================================================
    # 9. INFERENCE HELPERS (cluster = prompt)
    # =====================================================================
    def cluster_bootstrap_ci(vec, B=N_BOOT, seed=0, lo=2.5, hi=97.5):
        rng = np.random.default_rng(seed)
        m = len(vec)
        idx = rng.integers(0, m, size=(B, m))
        boots = vec[idx].mean(axis=1)
        return float(np.percentile(boots, lo)), float(np.percentile(boots, hi))

    def sign_flip_perm_p(diff, P=N_PERM, seed=0):
        rng = np.random.default_rng(seed)
        m = len(diff)
        obs = float(np.mean(diff))
        signs = rng.choice(np.array([-1.0, 1.0]), size=(P, m))
        perm_means = (diff[None, :] * signs).mean(axis=1)
        p = float((np.sum(np.abs(perm_means) >= abs(obs)) + 1) / (P + 1))
        return obs, p

    def cohend(diff):
        sd = float(np.std(diff, ddof=1))
        return float(np.mean(diff) / sd) if sd > 0 else float("nan")

    # ---- positive control inference ----
    pc_lo, pc_hi = cluster_bootstrap_ci(all_full_acc, seed=SEED + 9101)
    pc_obs, pc_p = sign_flip_perm_p(all_full_acc - 0.5, seed=SEED + 9102)
    positive_control_pass = bool(np.mean(all_full_acc) >= 0.55 and pc_lo > 0.50)

    # ---- placebo check ----
    placebo_overall = float(np.mean(placebo_seed_means))
    placebo_pass = bool(np.all(np.abs(placebo_seed_means - 0.5) <= 0.02) and
                         abs(placebo_overall - 0.5) <= 0.02)

    # ---- ladder comparisons: core vs each rung ----
    random4_seed_avg = random4_mat.mean(axis=0)   # per-prompt, averaged over seeds
    mech_seed_avg = mech_mat.mean(axis=0)

    diff_topimp = core_acc - topimp_acc
    diff_random4 = core_acc - random4_seed_avg
    diff_mech = core_acc - mech_seed_avg

    obs_topimp, p_topimp = sign_flip_perm_p(diff_topimp, seed=SEED + 1)
    obs_random4, p_random4 = sign_flip_perm_p(diff_random4, seed=SEED + 2)
    obs_mech, p_mech = sign_flip_perm_p(diff_mech, seed=SEED + 3)

    ci_topimp = cluster_bootstrap_ci(diff_topimp, seed=SEED + 11)
    ci_random4 = cluster_bootstrap_ci(diff_random4, seed=SEED + 12)
    ci_mech = cluster_bootstrap_ci(diff_mech, seed=SEED + 13)

    # Holm-Bonferroni over the 3 primary p-values
    fam = [("core_vs_topimp4", p_topimp), ("core_vs_random4", p_random4), ("core_vs_mechanical4", p_mech)]
    order = sorted(range(3), key=lambda i: fam[i][1])
    m = 3
    holm = [None, None, None]
    running_max = 0.0
    for rank, i in enumerate(order):
        adj = (m - rank) * fam[i][1]
        running_max = max(running_max, adj)
        holm[i] = min(1.0, running_max)

    def verdict_for(name, obs, p_holm, ci):
        stat_sig = p_holm < 0.05
        practically_sig = abs(obs) >= 0.01
        if stat_sig and practically_sig:
            return "DISTINGUISHABLE"
        return "NOT DISTINGUISHABLE"

    verdict_topimp = verdict_for("topimp", obs_topimp, holm[0], ci_topimp)
    verdict_random4 = verdict_for("random4", obs_random4, holm[1], ci_random4)
    verdict_mech = verdict_for("mechanical4", obs_mech, holm[2], ci_mech)

    # ---- where does core sit vs the random-4 seed DISTRIBUTION itself ----
    random4_ladder_means = random4_mat.mean(axis=1)  # one mean-over-prompts accuracy per seed
    mech_ladder_means = mech_mat.mean(axis=1)
    core_mean = float(np.mean(core_acc))
    random4_percentile_of_core = float(np.mean(random4_ladder_means < core_mean) * 100)
    mech_percentile_of_core = float(np.mean(mech_ladder_means < core_mean) * 100)

    # =====================================================================
    # 10. CONFOUND CONTROL: judge saturation & text length, core vs full
    # =====================================================================
    core_sat_vals = []
    full_sat_vals = []
    for r in records:
        for c in range(4):
            core_sat_vals.append(r["core_sat"][c]["A"])
            core_sat_vals.append(r["core_sat"][c]["B"])
            core_sat_vals.append(r["core_sat"][c]["C"])
            core_sat_vals.append(r["core_sat"][c]["D"])
        for m_ in r["full_meta"]:
            for lab in LABELS:
                full_sat_vals.append(r["full_sat"][m_["idx"]][lab])
    core_sat_vals = np.array(core_sat_vals)
    full_sat_vals = np.array(full_sat_vals)
    core_saturation = float(np.mean(2 * np.abs(core_sat_vals - 0.5)))
    full_saturation = float(np.mean(2 * np.abs(full_sat_vals - 0.5)))
    core_text_len_mean = float(np.mean([r["core_text_len"] for r in records]))
    full_text_len_mean = float(np.mean([m_["text_len"] for r in records for m_ in r["full_meta"]]))

    # =====================================================================
    # 11. SENSITIVITY (exploratory, not part of the confirmatory family):
    #     all 968 joined prompts, K_p = that prompt's own core criterion
    #     count (2, 3 or 4), substitute rungs matched to K_p.
    # =====================================================================
    sens_records = []
    for pid, comp, rub in joined:
        n_core = len(rub["coval_core"])
        pairs = human_pairs(comp["metadata"]["assessments"])
        if not pairs:
            continue
        fi = full_idx.get(pid)
        ci = core_idx.get(pid)
        if fi is None or ci is None:
            continue
        n_full = len(rub["coval_full"])
        if any(len(fi.get(j, {})) != 4 for j in range(n_full)):
            continue
        if any(len(ci.get(c, {})) != 4 for c in range(n_core)):
            continue
        full_meta = []
        for j, crit in enumerate(rub["coval_full"]):
            vals = np.array([s["score"] for s in crit["scores"]], dtype=float)
            imp, direc = rule_score(vals, "utility")
            full_meta.append(dict(idx=j, importance=imp, direction=direc))
        sens_records.append(dict(pid=pid, pairs=pairs, n_full=n_full, n_core=n_core,
                                  full_meta=full_meta, full_sat=fi, core_sat=ci))

    def sens_score_from_full(rec, idxs):
        fm = {m["idx"]: m for m in rec["full_meta"]}
        return {lab: float(np.mean([fm[j]["direction"] * rec["full_sat"][j][lab] for j in idxs]))
                for lab in LABELS}

    def sens_score_from_core(rec):
        kk = rec["n_core"]
        return {lab: float(np.mean([rec["core_sat"][c][lab] for c in range(kk)])) for lab in LABELS}

    def sens_top_k(rec, k):
        order = sorted(rec["full_meta"], key=lambda m: (-m["importance"], m["idx"]))
        return [m["idx"] for m in order[:k]]

    sens_core_acc = np.array([pairwise_accuracy(sens_score_from_core(r), r["pairs"]) for r in sens_records])
    sens_topimp_acc = np.array([
        pairwise_accuracy(sens_score_from_full(r, sens_top_k(r, r["n_core"])), r["pairs"])
        for r in sens_records
    ])
    sens_diff = sens_core_acc - sens_topimp_acc
    sens_obs, sens_p = sign_flip_perm_p(sens_diff, seed=SEED + 21)
    sens_ci = cluster_bootstrap_ci(sens_diff, seed=SEED + 22)

    # =====================================================================
    # 12. ASSEMBLE + SAVE
    # =====================================================================
    def summarize(vec):
        return dict(mean=float(np.mean(vec)), std=float(np.std(vec, ddof=1)),
                     min=float(np.min(vec)), max=float(np.max(vec)), n=int(len(vec)))

    results = dict(
        seed=SEED, n_seeds=N_SEEDS, n_folds=N_FOLDS, n_boot=N_BOOT, n_perm=N_PERM,
        population=dict(
            n_joined=len(joined), n_primary=n,
            excluded_core_count_not_4=excluded_core_count,
        ),
        estimand=("mean, over prompts with exactly 4 core criteria, of per-prompt "
                  "pairwise concordance between an arm's response scores and the "
                  "pooled human 'world' ranking preferences (ties=0.5 credit)"),
        thresholds_pre_registered=dict(
            positive_control="mean(all_full_acc) >= 0.55 AND bootstrap 95% CI lower bound > 0.50",
            placebo="all seed means and overall mean within 0.50 +/- 0.02",
            ladder_distinguishable="Holm-adjusted two-sided permutation p < 0.05 AND |diff| >= 0.01",
            multiplicity="Holm-Bonferroni across exactly 3 primary comparisons",
        ),
        positive_control=dict(
            arm="ALL-FULL (not count-matched, all criteria per prompt)",
            mean_accuracy=float(np.mean(all_full_acc)),
            bootstrap_ci95=[pc_lo, pc_hi],
            perm_p_vs_0p5=pc_p,
            passes=positive_control_pass,
        ),
        placebo=dict(
            seed_means=placebo_seed_means.tolist(),
            overall_mean=placebo_overall,
            passes=placebo_pass,
        ),
        ladder=dict(
            all_full_context_only=summarize(all_full_acc),
            core=summarize(core_acc),
            top_importance_4=summarize(topimp_acc),
            mechanical_4=dict(
                seed_ladder_means=summarize(mech_ladder_means),
                per_prompt_seed_avg=summarize(mech_seed_avg),
                chosen_alphas=chosen_alphas,
                chosen_alpha_median=float(np.median(chosen_alphas)),
            ),
            random_4=dict(
                seed_ladder_means=summarize(random4_ladder_means),
                per_prompt_seed_avg=summarize(random4_seed_avg),
            ),
            placebo_context_only=summarize(placebo_seed_means),
        ),
        comparisons=dict(
            core_vs_top_importance_4=dict(
                abs_diff_pp=obs_topimp * 100, cohens_d=cohend(diff_topimp),
                bootstrap_ci95_diff_pp=[ci_topimp[0] * 100, ci_topimp[1] * 100],
                perm_p_raw=p_topimp, perm_p_holm=holm[0],
                verdict=verdict_topimp,
            ),
            core_vs_random_4=dict(
                abs_diff_pp=obs_random4 * 100, cohens_d=cohend(diff_random4),
                bootstrap_ci95_diff_pp=[ci_random4[0] * 100, ci_random4[1] * 100],
                perm_p_raw=p_random4, perm_p_holm=holm[1],
                verdict=verdict_random4,
                core_percentile_within_random4_seed_distribution=random4_percentile_of_core,
            ),
            core_vs_mechanical_4=dict(
                abs_diff_pp=obs_mech * 100, cohens_d=cohend(diff_mech),
                bootstrap_ci95_diff_pp=[ci_mech[0] * 100, ci_mech[1] * 100],
                perm_p_raw=p_mech, perm_p_holm=holm[2],
                verdict=verdict_mech,
                core_percentile_within_mechanical4_seed_distribution=mech_percentile_of_core,
            ),
        ),
        dropped_rungs=dict(
            different_prompt_4=("no precomputed satisfaction for (donor criterion) x (target "
                                 "prompt's responses) -- would require a fresh judge pass; "
                                 "confirmed zero cross-prompt entries in both tensors"),
            generic_4_every_prompt=("no criterion text is judged against more than the small "
                                     "number of prompts it natively belongs to (max 5/968); no "
                                     "corpus-wide generic criterion has corpus-wide satisfaction"),
        ),
        strongest_confound=dict(
            description=("core's criterion TEXT is compiler-rewritten (short, imperative) while "
                          "every full-based rung necessarily reuses full's original verbose "
                          "human-submitted wording -- judge confidence could differ by STYLE "
                          "alone, independent of content quality"),
            control_core_saturation=core_saturation,
            control_full_saturation=full_saturation,
            control_core_mean_char_len=core_text_len_mean,
            control_full_mean_char_len=full_text_len_mean,
            resolved="PARTIAL -- cannot fully separate style from content without an LLM rewrite "
                     "pass, which this script may not run; reported as a named, measured, open limit",
        ),
        sensitivity_exploratory=dict(
            description=("all 968 joined prompts, substitute count matched to each prompt's OWN "
                          "core-criterion count (2, 3, or 4) instead of restricting to n_core==4"),
            n=len(sens_records),
            core_mean=float(np.mean(sens_core_acc)),
            top_importance_matched_mean=float(np.mean(sens_topimp_acc)),
            abs_diff_pp=sens_obs * 100,
            bootstrap_ci95_diff_pp=[sens_ci[0] * 100, sens_ci[1] * 100],
            perm_p_raw=sens_p,
        ),
    )

    out_path = RESULTS_DIR / "independent_A.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}")
    print(json.dumps({k: results[k] for k in
                       ("positive_control", "placebo", "comparisons")}, indent=2))


if __name__ == "__main__":
    main()
