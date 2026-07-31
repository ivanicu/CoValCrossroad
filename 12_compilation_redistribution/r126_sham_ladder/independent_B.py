"""r126 -- the sham ladder, independent design B.

CLAIM UNDER ATTACK
    "The compilation into coval_core does real work: core is better than what
    you would get without the compiler."

ESTIMAND (in words, before any code ran)
    For a rubric arm X (a set of k criteria, each with a satisfaction score
    sat(c, r) in [0,1] for response r), define the arm's response score as the
    unweighted mean satisfaction over its criteria:

        S_X(r) = mean_{c in X} sat(c, r)          [core: sat as-is]
        S_X(r) = mean_{c in X} oriented_sat(c, r)  [full-derived rungs, see below]

    Ground truth is the annotator's "world" ranking block (personal is the
    subjective per-annotator preference; world is the annotator's guess of the
    societally-best response -- the ranking coval was designed against; this is
    also the block covalx.human_pairs already reads).  Flatten every strict
    pairwise preference (a preferred to b, ties dropped) that every annotator
    of that prompt produced.  A pair is a HIT if S_X(a) > S_X(b), a MISS if
    S_X(a) < S_X(b), and gets 0.5 credit on an exact tie.

    ESTIMAND = E_prompt[ mean over that prompt's (annotator, pair) hits ]
             = the population mean of the PROMPT-LEVEL pairwise ranking
               accuracy, i.e. each prompt is one exchangeable cluster and
               contributes one number regardless of how many annotators or
               pairs it carries (17-237 pairs/prompt in this data -- an
               annotator-weighted mean would let chatty prompts dominate).

    This mirrors the external yardstick already used in this project
    (covalx/judge.py's positive-control docstring): OpenAI report ~60%
    pairwise accuracy for their own rubric scoring on this release.

WHY UNWEIGHTED MEAN, NOT IMPORTANCE-WEIGHTED
    coval_core ships with NO ratings (scores: null) -- a real compiled arm
    literally cannot be importance-weighted at scoring time.  To keep every
    rung on the ladder count-matched AND information-matched at the
    AGGREGATION step, every arm (core and every full-derived substitute) is
    scored by the same unweighted mean.  The only place importance ratings
    enter for full-derived rungs is (a) SELECTION -- which 4 criteria -- and
    (b) ORIENTATION -- see below -- both are "free" (already-collected human
    data, zero LLM calls), exactly the kind of cheap substitute the attack
    asks for.

ORIENTATION (a design decision, stated up front, sensitivity-checked below)
    A coval_full criterion's text is not always phrased as desired behaviour
    -- e.g. "pick a clear side in the beef debate ... instead of remaining
    neutral" carries importance scores of mostly -10..-6: most annotators
    think DOING this is bad.  Naively summing raw satisfaction over such a
    criterion would reward a response for doing something annotators marked
    as bad.  coval_core never has this problem because the compiler always
    phrases its 4 criteria as desired behaviour.  So every full-derived rung
    uses the ALREADY-AVAILABLE sign of the criterion's own mean importance
    score to orient it:

        oriented_sat(c, r) = sat(c, r)       if mean_importance(c) >= 0
                            = 1 - sat(c, r)   otherwise

    This costs no LLM call (the sign is sitting in the public data for every
    criterion, selected or not) and is applied UNIFORMLY to random / top /
    worst / mechanical rungs, so it cannot favour one selection rule over
    another -- only the *choice of which 4 criteria* varies between rungs.
    A no-orientation (raw mean) variant is run too, as a stated sensitivity
    check, never as an alternate primary.

THE LADDER (count-matched at k=4; population restricted to prompts whose own
coval_core has exactly 4 criteria -- see REGIME)
    PLACEBO           i.i.d. U(0,1) score per response, ignores all criteria.
                       Hand-derivable answer: 0.5 exactly, by symmetry -- not
                       evidence, a check that the harness's own arithmetic
                       and tie/bootstrap machinery are not lying.
    WORST-IMPORTANCE-4 bottom-4 full criteria by mean |importance|, oriented.
    RANDOM-4           uniform-random 4 of that prompt's full criteria,
                       oriented; >=5 seeds.
    MECHANICAL-4       linear regression on TEXT-ONLY features (length, word
                       count, concreteness/negation/hedge keyword counts,
                       relative position) fit on held-out prompts (5-fold CV)
                       to predict |importance|, applied out-of-sample to pick
                       the test prompt's own top-4 by predicted score,
                       oriented; >=5 seeds (reshuffled folds).
    TOP-IMPORTANCE-4   top-4 full criteria by the prompt's OWN mean
                       |importance| rating, oriented.  An oracle-LITE upper
                       bound: it uses information a real zero-annotation
                       compiler substitute would not have before humans rate
                       the new prompt, so it bounds how much value compilation
                       could add beyond ratings ALREADY collected.
    CORE               coval_core, unweighted mean of its own satisfaction.
    FULL-ALL (context) every coval_full criterion, oriented -- not
                       count-matched, reported only as a ceiling/sanity check
                       against the external ~60% yardstick.

DROPPED RUNGS (stated, not faked)
    "4 criteria from a different prompt" and "4 generic criteria reused for
    every prompt" both require a satisfaction score for a criterion evaluated
    against a response IT WAS NEVER SCORED AGAINST -- the precomputed tensors
    only contain each prompt's own (criterion, own-response) cells, and the
    task forbids running any LLM to fill that gap.  Both are dropped from the
    ladder; no value is fabricated for them.

STRONGEST CONFOUND (written before running)
    coval_core's 4 criteria are LLM-compiled: short, imperative, single-clause
    text.  The SAME Qwen judge that produced every satisfaction score may
    simply be more DECISIVE (produce a less noisy Yes/No logit gap) on short
    compiled text than on long, hedged, human-written full criteria --
    regardless of whether the compiled CONTENT is better selected.  That would
    make core win on judge-style sensitivity, not on "the compiler selects/
    synthesises better content", and the attack would misfire in the
    flattering direction.
    CONTROL (same script): for every arm/seed instance, record mean text
    length and mean judge "decisiveness" |sat - 0.5| over the cells it used,
    and regress cross-arm pairwise accuracy on decisiveness.  If core is the
    most decisive arm AND decisiveness predicts accuracy across the whole
    ladder, the verdict is caveated accordingly rather than taken at face
    value.

POSITIVE CONTROL
    TOP-IMPORTANCE-4 (real human salience) must clearly beat WORST-IMPORTANCE-4
    (real human non-salience) -- both drawn from the exact same instrument and
    prompts, differing only in which items were selected.  Pre-registered
    gate: absolute gap >= 0.05 (5 points) AND permutation p < 0.001.  If this
    fails, the whole pipeline (satisfaction lookup, pairing, accuracy,
    bootstrap) is not trustworthy and every other verdict below is UNVERIFIED.

MULTIPLICITY
    Primary family = {core vs RANDOM-4, core vs TOP-IMPORTANCE-4,
    core vs WORST-IMPORTANCE-4, core vs MECHANICAL-4} -- 4 tests, Holm-Bonferroni
    step-down at family alpha = 0.05.

PRE-REGISTERED VERDICT RULE (fixed before any number was seen)
    Let best_substitute = the ladder rung (excluding PLACEBO, FULL-ALL) with
    the highest point estimate.
    CONFIRMED  -- core beats best_substitute by >= 1.0 percentage point
                  absolute AND paired Cohen's dz >= 0.2 AND Holm-adjusted
                  p < 0.05 on that specific comparison, AND the positive
                  control and placebo both pass.
    OVERTURNED -- positive control and placebo pass, but core does NOT clear
                  all three bars above against best_substitute (i.e. a cheap
                  substitute matches, beats, or is statistically
                  indistinguishable from core at a non-trivial effect size).
    UNVERIFIED -- positive control fails, placebo fails, or regime data is
                  too thin to run the test.

CLUSTERING
    Prompt is the cluster (responses AND annotators nest inside it). Every
    inferential step -- bootstrap CI, permutation test -- resamples PROMPTS,
    never individual pairs.

SEED: 4409 (all 5 replicate seeds are 4409..4413, deterministic from it).
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from covalx import load_join, parse_ranking, LABELS  # noqa: E402

DATA = REPO / "data"
SAT_FULL = REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
SAT_CORE = REPO / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
OUT = Path(__file__).resolve().parent / "results" / "independent_B.json"

BASE_SEED = 4409
SEEDS = [BASE_SEED + i for i in range(5)]  # >=5 seeds, deterministic from BASE_SEED
N_BOOT = 2000
N_PERM = 5000
N_FOLDS = 5

CONCRETE_WORDS = ["specific", "evidence", "data", "cite", "citation", "study",
                  "studies", "number", "concrete", "example", "statistic",
                  "statistics", "source", "sources", "fact", "facts"]
NEGATION_WORDS = ["not", "avoid", "never", "refrain", "exclude", "without", "don't"]
HEDGE_WORDS = ["both", "multiple", "various", "perspective", "perspectives",
               "balance", "balanced", "consider", "several"]


def word_count(words, text_lower):
    return sum(len(re.findall(r"\b" + re.escape(w) + r"\b", text_lower)) for w in words)


def criterion_features(text: str, position: int, n_total: int) -> np.ndarray:
    tl = text.lower()
    return np.array([
        len(text) / 100.0,
        len(text.split()) / 10.0,
        word_count(CONCRETE_WORDS, tl),
        word_count(NEGATION_WORDS, tl),
        word_count(HEDGE_WORDS, tl),
        position / max(n_total - 1, 1),
        1.0,  # intercept
    ], dtype=np.float64)


# --------------------------------------------------------------------- load
def load_sat(npz_path: Path):
    d = np.load(npz_path, allow_pickle=True)
    idx = defaultdict(dict)
    for m, s in zip(d["meta"], d["sat"]):
        pid, ci, lab = m.split("|")
        idx[pid][(int(ci), lab)] = float(s)
    return idx


def build_records():
    joined = load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl")
    satF = load_sat(SAT_FULL)
    satC = load_sat(SAT_CORE)

    n_joined = len(joined)
    n_core_ne_4 = 0
    n_zero_pairs = 0
    records = []
    for pid, comp, rub in joined:
        full = rub["coval_full"]
        core = rub["coval_core"]
        if len(core) != 4:
            n_core_ne_4 += 1
            continue
        labels = [r["response_index"] for r in comp["responses"]]
        assessments = comp["metadata"]["assessments"]
        pairs = []
        for asm in assessments:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            r = parse_ranking(w[0].get("ranking", ""))
            flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
            for a, ga in flat:
                for b, gb in flat:
                    if ga < gb:
                        pairs.append((a, b))
        if not pairs:
            n_zero_pairs += 1
            continue

        imp_mag = np.empty(len(full))
        imp_dir = np.empty(len(full))
        texts = []
        for j, c in enumerate(full):
            sc = np.array([s["score"] for s in c["scores"]], dtype=float)
            imp_mag[j] = float(np.mean(np.abs(sc)))
            m = float(np.mean(sc))
            imp_dir[j] = 1.0 if m >= 0 else -1.0
            texts.append(c["criterion"])

        feats = np.stack([criterion_features(t, j, len(full))
                           for j, t in enumerate(texts)])

        records.append(dict(
            pid=pid, n_full=len(full), labels=labels, pairs=pairs,
            imp_mag=imp_mag, imp_dir=imp_dir, texts=texts, feats=feats,
            sat_full=satF[pid], sat_core=satC[pid],
        ))

    meta = dict(n_comparisons_lines=None, n_joined=n_joined,
                n_dropped_core_ne_4=n_core_ne_4, n_dropped_zero_pairs=n_zero_pairs,
                n_regime=len(records))
    return records, meta


# ------------------------------------------------------------------ scoring
def score_full(rec, sel_idx, oriented=True):
    out = {}
    for lab in rec["labels"]:
        vals = []
        for j in sel_idx:
            s = rec["sat_full"][(int(j), lab)]
            if oriented and rec["imp_dir"][j] < 0:
                s = 1.0 - s
            vals.append(s)
        out[lab] = float(np.mean(vals))
    return out


def score_core(rec):
    n = rec["sat_core"]
    labels = rec["labels"]
    ncrit = max(j for j, _ in n.keys()) + 1
    out = {}
    for lab in labels:
        vals = [n[(j, lab)] for j in range(ncrit)]
        out[lab] = float(np.mean(vals))
    return out


def score_placebo(rec, rng):
    return {lab: float(rng.uniform()) for lab in rec["labels"]}


def prompt_accuracy(rec, scores):
    hits, n = 0.0, 0
    for a, b in rec["pairs"]:
        sa, sb = scores[a], scores[b]
        if sa > sb:
            hits += 1.0
        elif sa == sb:
            hits += 0.5
        n += 1
    return hits / n


def decisiveness_and_length(rec, sel_idx=None, core=False):
    """Mean |sat-0.5| and mean criterion char-length for the cells an arm used."""
    devs, lens = [], []
    if core:
        n = rec["sat_core"]
        ncrit = max(j for j, _ in n.keys()) + 1
        for j in range(ncrit):
            for lab in rec["labels"]:
                devs.append(abs(n[(j, lab)] - 0.5))
    else:
        for j in sel_idx:
            lens.append(len(rec["texts"][int(j)]))
            for lab in rec["labels"]:
                devs.append(abs(rec["sat_full"][(int(j), lab)] - 0.5))
    return devs, lens


# ---------------------------------------------------------------- selectors
def sel_random(rec, rng):
    return rng.choice(rec["n_full"], size=4, replace=False)


def sel_top_importance(rec):
    return np.argsort(-rec["imp_mag"])[:4]


def sel_worst_importance(rec):
    return np.argsort(rec["imp_mag"])[:4]


def fit_mechanical_selection(records, seed):
    """5-fold CV: fit OLS(features -> |importance|) on train folds, predict
    each record's own criteria out-of-sample, pick top-4 by prediction."""
    rng = np.random.default_rng(seed)
    n = len(records)
    fold = rng.integers(0, N_FOLDS, size=n)
    selections = [None] * n
    for f in range(N_FOLDS):
        train_idx = np.where(fold != f)[0]
        test_idx = np.where(fold == f)[0]
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
        X_tr = np.concatenate([records[i]["feats"] for i in train_idx], axis=0)
        y_tr = np.concatenate([records[i]["imp_mag"] for i in train_idx], axis=0)
        coef, *_ = np.linalg.lstsq(X_tr, y_tr, rcond=None)
        for i in test_idx:
            pred = records[i]["feats"] @ coef
            selections[i] = np.argsort(-pred)[:4]
    return selections


# -------------------------------------------------------------- inference
def cluster_bootstrap_ci(vec, n_boot=N_BOOT, seed=0):
    rng = np.random.default_rng(seed)
    n = len(vec)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[b] = np.mean(vec[idx])
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)), boots


def paired_permutation_test(diff, n_perm=N_PERM, seed=0):
    """Sign-flip (Rademacher) permutation test on a paired per-prompt diff vector."""
    rng = np.random.default_rng(seed)
    obs = float(np.mean(diff))
    n = len(diff)
    null = np.empty(n_perm)
    for p in range(n_perm):
        flips = rng.choice([-1.0, 1.0], size=n)
        null[p] = np.mean(diff * flips)
    pval = (1 + np.sum(np.abs(null) >= abs(obs))) / (1 + n_perm)
    return obs, float(pval), null


def cohen_dz(diff):
    sd = np.std(diff, ddof=1)
    return float(np.mean(diff) / sd) if sd > 0 else float("nan")


def holm_bonferroni(pvals: dict, alpha=0.05):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj = {}
    running_max = 0.0
    for rank, (name, p) in enumerate(items, start=1):
        a = min(1.0, p * (m - rank + 1))
        running_max = max(running_max, a)
        adj[name] = running_max
    reject = {name: (adj[name] < alpha) for name in adj}
    return adj, reject


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    records, meta = build_records()
    n = len(records)
    print(f"regime: {n} prompts (dropped core!=4: {meta['n_dropped_core_ne_4']}, "
          f"zero-pairs: {meta['n_dropped_zero_pairs']})")

    labels_all = [r["pid"] for r in records]

    # ---- CORE ----
    acc_core = np.array([prompt_accuracy(r, score_core(r)) for r in records])

    # ---- FULL-ALL (context / ceiling, oriented) ----
    acc_full_all = np.array([
        prompt_accuracy(r, score_full(r, np.arange(r["n_full"]), oriented=True))
        for r in records
    ])
    acc_full_all_raw = np.array([
        prompt_accuracy(r, score_full(r, np.arange(r["n_full"]), oriented=False))
        for r in records
    ])

    # ---- TOP / WORST importance (deterministic) ----
    acc_top = np.array([prompt_accuracy(r, score_full(r, sel_top_importance(r))) for r in records])
    acc_worst = np.array([prompt_accuracy(r, score_full(r, sel_worst_importance(r))) for r in records])
    # unoriented sensitivity variants
    acc_top_raw = np.array([prompt_accuracy(r, score_full(r, sel_top_importance(r), oriented=False)) for r in records])

    # ---- RANDOM-4, 5 seeds ----
    acc_random_seeds = []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        sel = [sel_random(r, rng) for r in records]
        acc_random_seeds.append(np.array([prompt_accuracy(r, score_full(r, sel[i])) for i, r in enumerate(records)]))
    acc_random_seeds = np.stack(acc_random_seeds)          # (5, n)
    acc_random_avg = acc_random_seeds.mean(axis=0)          # per-prompt, averaged over seeds
    random_seed_means = acc_random_seeds.mean(axis=1)       # overall mean per seed

    # ---- MECHANICAL-4, 5 seeds (reshuffled folds) ----
    acc_mech_seeds = []
    mech_sel_by_seed = []
    for s in SEEDS:
        sel = fit_mechanical_selection(records, s)
        mech_sel_by_seed.append(sel)
        acc_mech_seeds.append(np.array([prompt_accuracy(r, score_full(r, sel[i])) for i, r in enumerate(records)]))
    acc_mech_seeds = np.stack(acc_mech_seeds)
    acc_mech_avg = acc_mech_seeds.mean(axis=0)
    mech_seed_means = acc_mech_seeds.mean(axis=1)

    # ---- PLACEBO, 5 seeds ----
    acc_placebo_seeds = []
    for s in SEEDS:
        rng = np.random.default_rng(s + 1000)
        acc_placebo_seeds.append(np.array([prompt_accuracy(r, score_placebo(r, rng)) for r in records]))
    acc_placebo_seeds = np.stack(acc_placebo_seeds)
    placebo_seed_means = acc_placebo_seeds.mean(axis=1)

    # ================================================================ CIs
    def ci(vec, seed):
        lo, hi, _ = cluster_bootstrap_ci(vec, seed=seed)
        return dict(mean=float(np.mean(vec)), ci95=[lo, hi], n=len(vec))

    ladder = {
        "placebo":            {**ci(acc_placebo_seeds.mean(axis=0), 1), "seed_means": placebo_seed_means.tolist()},
        "worst_importance_4": ci(acc_worst, 2),
        "random_4":           {**ci(acc_random_avg, 3), "seed_means": random_seed_means.tolist()},
        "mechanical_4":       {**ci(acc_mech_avg, 4), "seed_means": mech_seed_means.tolist()},
        "top_importance_4":   ci(acc_top, 5),
        "core":               ci(acc_core, 6),
        "full_all_context":   ci(acc_full_all, 7),
        "full_all_raw_unoriented_context": ci(acc_full_all_raw, 8),
        "top_importance_4_raw_unoriented_sensitivity": ci(acc_top_raw, 9),
    }

    # ============================================================ dropped
    dropped_rungs = {
        "different_prompt_4": "no precomputed satisfaction exists for a criterion "
            "scored against a response from a DIFFERENT prompt (a04_full.npz only "
            "has each prompt's own criterion x own-response cells); computing it "
            "requires a new LLM judge call, which this attack is not allowed to run.",
        "generic_4_reused": "same reason -- a fixed generic criterion set was never "
            "scored by the judge against any response; fabricating a value is "
            "explicitly forbidden by the task brief.",
    }

    # ==================================================== positive control
    pc_diff = acc_top - acc_worst
    pc_obs, pc_p, _ = paired_permutation_test(pc_diff, seed=11)
    pc_lo, pc_hi, _ = cluster_bootstrap_ci(pc_diff, seed=12)
    positive_control = dict(
        comparison="top_importance_4 vs worst_importance_4",
        gap_abs=pc_obs, ci95=[pc_lo, pc_hi], p_perm=pc_p,
        gate_gap_ge_0_05=bool(pc_obs >= 0.05),
        gate_p_lt_0_001=bool(pc_p < 0.001),
        passed=bool(pc_obs >= 0.05 and pc_p < 0.001),
    )

    # ============================================================= placebo
    placebo_overall = float(acc_placebo_seeds.mean())
    placebo_gap = abs(placebo_overall - 0.5)
    placebo_check = dict(
        overall_mean=placebo_overall, abs_gap_from_0_5=placebo_gap,
        seed_means=placebo_seed_means.tolist(),
        gate_abs_gap_lt_0_02=bool(placebo_gap < 0.02),
        passed=bool(placebo_gap < 0.02),
    )

    # ===================================================== primary family
    def paired(vec_x, name, seed_base):
        diff = acc_core - vec_x
        obs, p, _ = paired_permutation_test(diff, seed=seed_base)
        lo, hi, _ = cluster_bootstrap_ci(diff, seed=seed_base + 1)
        return dict(core_minus_X=obs, ci95=[lo, hi], p_perm=p, dz=cohen_dz(diff))

    primary = {
        "core_vs_random_4":            paired(acc_random_avg, "random_4", 101),
        "core_vs_top_importance_4":    paired(acc_top, "top_importance_4", 103),
        "core_vs_worst_importance_4":  paired(acc_worst, "worst_importance_4", 105),
        "core_vs_mechanical_4":        paired(acc_mech_avg, "mechanical_4", 107),
    }
    pvals = {k: v["p_perm"] for k, v in primary.items()}
    adj_p, reject = holm_bonferroni(pvals, alpha=0.05)
    for k in primary:
        primary[k]["p_holm"] = adj_p[k]
        primary[k]["reject_h0_holm_0_05"] = reject[k]

    # ==================================================== confound control
    arm_points = []  # (name, decisiveness_mean, length_mean, accuracy_mean)

    def add_arm(name, sel_fn_per_record, acc_vec):
        devs_all, lens_all = [], []
        for i, r in enumerate(records):
            sel = sel_fn_per_record(i, r)
            d, l = decisiveness_and_length(r, sel_idx=sel)
            devs_all.extend(d)
            lens_all.extend(l)
        arm_points.append((name, float(np.mean(devs_all)), float(np.mean(lens_all)), float(np.mean(acc_vec))))

    add_arm("worst_importance_4", lambda i, r: sel_worst_importance(r), acc_worst)
    add_arm("top_importance_4", lambda i, r: sel_top_importance(r), acc_top)
    for si, s in enumerate(SEEDS):
        rng = np.random.default_rng(s)
        sels = [sel_random(r, rng) for r in records]
        add_arm(f"random_4_seed{s}", (lambda sels: (lambda i, r: sels[i]))(sels), acc_random_seeds[si])
    for si, s in enumerate(SEEDS):
        sels = mech_sel_by_seed[si]
        add_arm(f"mechanical_4_seed{s}", (lambda sels: (lambda i, r: sels[i]))(sels), acc_mech_seeds[si])

    # core: no "sel_idx" (uses its own core criteria, not full)
    core_devs = []
    core_lens = []
    for r in records:
        d, _ = decisiveness_and_length(r, core=True)
        core_devs.extend(d)
        core_lens.extend([len(c) for c in [r["texts"]]])  # placeholder unused
    # core criterion text length: read straight from conversation_rubrics via a second pass is
    # avoided; instead measure length distribution over coval_core text directly.
    core_lens = []
    for pid, comp, rub in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        if len(rub["coval_core"]) == 4:
            core_lens.extend(len(c["criterion"]) for c in rub["coval_core"])
    arm_points.append(("core", float(np.mean(core_devs)), float(np.mean(core_lens)), float(np.mean(acc_core))))

    dec = np.array([p[1] for p in arm_points])
    length = np.array([p[2] for p in arm_points])
    accv = np.array([p[3] for p in arm_points])
    r_dec_acc = float(np.corrcoef(dec, accv)[0, 1])
    r_len_dec = float(np.corrcoef(length, dec)[0, 1])
    core_dec_rank = int(1 + np.sum(dec > dec[-1]))  # rank 1 = most decisive

    confound_control = dict(
        description="mean judge decisiveness |sat-0.5| and mean criterion char-length "
                     "per arm/seed instance, regressed against that instance's pairwise "
                     "accuracy across the whole ladder.",
        arms=[dict(name=p[0], decisiveness=p[1], mean_len_chars=p[2], accuracy=p[3]) for p in arm_points],
        corr_decisiveness_vs_accuracy=r_dec_acc,
        corr_length_vs_decisiveness=r_len_dec,
        core_decisiveness_rank_desc=core_dec_rank,
        n_arms=len(arm_points),
        interpretation="if core is the (or near the) most decisive arm AND "
                        "corr_decisiveness_vs_accuracy is large and positive, core's ladder "
                        "position is confounded by judge-style sensitivity to short compiled "
                        "text, not cleanly attributable to better content selection.",
    )

    # ============================================================== verdict
    substitute_names = ["random_4", "top_importance_4", "worst_importance_4", "mechanical_4"]
    substitute_means = {
        "random_4": float(np.mean(acc_random_avg)),
        "top_importance_4": float(np.mean(acc_top)),
        "worst_importance_4": float(np.mean(acc_worst)),
        "mechanical_4": float(np.mean(acc_mech_avg)),
    }
    best_sub_name = max(substitute_names, key=lambda k: substitute_means[k])
    best_sub_mean = substitute_means[best_sub_name]
    core_mean = float(np.mean(acc_core))
    gap_vs_best = core_mean - best_sub_mean
    key_for_best = {
        "random_4": "core_vs_random_4", "top_importance_4": "core_vs_top_importance_4",
        "worst_importance_4": "core_vs_worst_importance_4", "mechanical_4": "core_vs_mechanical_4",
    }[best_sub_name]
    best_test = primary[key_for_best]

    if not (positive_control["passed"] and placebo_check["passed"]):
        verdict = "UNVERIFIED"
        verdict_reason = "positive control or placebo failed -- the measurement instrument itself is not trustworthy here."
    else:
        confirmed = (gap_vs_best >= 0.01 and best_test["dz"] >= 0.2 and best_test["reject_h0_holm_0_05"])
        if confirmed:
            verdict = "CONFIRMED"
            verdict_reason = (f"core beats its best cheap substitute ({best_sub_name}) by "
                               f"{gap_vs_best*100:.2f} pp (dz={best_test['dz']:.2f}, "
                               f"Holm p={best_test['p_holm']:.4g}) -- all three pre-registered bars cleared.")
        else:
            verdict = "OVERTURNED"
            verdict_reason = (f"core does not clear the pre-registered bar over its best cheap "
                               f"substitute ({best_sub_name}): gap={gap_vs_best*100:.2f} pp, "
                               f"dz={best_test['dz']:.2f}, Holm p={best_test['p_holm']:.4g}.")

    scopes = dict(
        population=f"{meta['n_regime']} of {meta['n_joined']} comparisons<->rubrics-joined prompts "
                    f"(dropped {meta['n_dropped_core_ne_4']} where coval_core != 4 criteria, "
                    f"{meta['n_dropped_zero_pairs']} with no usable 'world' pairs). "
                    f"{meta['n_joined']}/986 raw rubric records joined to a comparison at all.",
        instrument="local Qwen3.5-2B-Base logit-gap satisfaction judge, PRECOMPUTED in "
                    "01_object_and_rebuild/r04_rebuild_satisfaction -- this attack reuses those "
                    "scores verbatim and does not re-validate the judge itself. All rungs share "
                    "the identical instrument, so instrument bias cancels in relative rung "
                    "comparisons but not in the absolute accuracy level.",
        baseline="'compiler adds real work' is tested against zero-LLM, count-matched (k=4) "
                 "substitutes built from THAT prompt's own coval_full pool only. Not tested: "
                 "compilation vs. a smarter LLM compiler, vs. a different core size, vs. "
                 "cross-prompt or generic criteria (dropped, see dropped_rungs). "
                 "top_importance_4 is an oracle-lite upper bound (uses the target prompt's own "
                 "already-collected ratings) rather than a deployable zero-annotation substitute; "
                 "mechanical_4 is the deployable one.",
        regime="prompts where coval_core compiled to exactly 4 criteria (96% of joined data); "
               "the ~4% of prompts where the compiler collapsed to 2-3 criteria are excluded and "
               "the verdict may not transfer to whatever made the compiler shrink there.",
    )

    result = dict(
        seed=BASE_SEED, seeds=SEEDS, n_boot=N_BOOT, n_perm=N_PERM, n_folds=N_FOLDS,
        estimand="prompt-clustered mean pairwise ranking accuracy of unweighted-mean-satisfaction "
                 "arm scores against annotators' strict 'world'-block pairwise preferences (ties dropped)",
        regime_meta=meta,
        ladder=ladder,
        dropped_rungs=dropped_rungs,
        positive_control=positive_control,
        placebo=placebo_check,
        primary_family_tests=primary,
        multiplicity=dict(method="Holm-Bonferroni step-down", family_alpha=0.05,
                           adjusted_p=adj_p, reject=reject),
        confound_control=confound_control,
        verdict=verdict,
        verdict_reason=verdict_reason,
        best_substitute=best_sub_name,
        best_substitute_mean=best_sub_mean,
        core_mean=core_mean,
        gap_core_minus_best_substitute=gap_vs_best,
        scopes=scopes,
        wall_clock_seconds=time.time() - t0,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {OUT} in {result['wall_clock_seconds']:.1f}s")
    print(f"VERDICT: {verdict} -- {verdict_reason}")


if __name__ == "__main__":
    main()
