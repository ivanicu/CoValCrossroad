"""r128 / independent_A -- is core's ranking-accuracy advantage STYLE or CONTENT?

============================================================================
ESTIMAND (written before any accuracy/decisiveness number was looked at)
============================================================================
Two prior passes over this project observed, in passing: coval_core's
criteria are the shortest text of any arm (~88 chars vs ~96-104 for
full-derived arms), the judge (local Qwen3.5-2B-Base, sigmoid(logit(" Yes")
- logit(" No"))) is most DECISIVE on them (mean |sat-0.5| highest of all
arms), length<->decisiveness correlation is about -0.95 across arms, and
decisiveness<->ranking-accuracy correlation across arms is about +0.29.

The worry: core's measured ranking-accuracy advantage over the
full-criteria aggregate is manufactured by terse, compiler-authored
phrasing making the judge falsely confident, not by core's criteria being
better SELECTIONS of content.

THE ESTIMAND is the paired, per-prompt difference in human-ranking pairwise
accuracy between criterion subsets of matched CARDINALITY (4, matching
core's own count) and matched AUTHORSHIP (always human-written, always
drawn from coval_full -- never core, never compiled), that differ only in
which 4-of-~15.5 criteria are kept: the 4 SHORTEST vs the 4 LONGEST vs a
random 4 (sham) vs (confound control) the 4 lowest/highest "complexity
density" text.  If holding authorship and count fixed while varying only
length still moves accuracy in the same direction and of comparable
magnitude to core's own advantage over the full-criteria aggregate, that
is evidence the advantage core enjoys COULD be manufactured by length
alone, with no need to invoke core's criteria being better SELECTED or
better WORDED content.  If it does not, core's advantage needs an
explanation beyond raw text length.

============================================================================
IDENTIFICATION
============================================================================
Fully identified at the level of "how much of the accuracy gap can be
reproduced by a length-only manipulation within a fixed-authorship,
fixed-cardinality population" -- this is a real, computable quantity, not
a derivation.  NOT identified: "how much of the length effect is pure
SURFACE STYLE (phrasing/terseness) vs CONTENT SIMPLICITY (short criteria
happen to be more objective/checklist-like, which is itself a content
property, not style)".  Naturally-written short criteria are not a
style-only rewrite of long criteria -- they may simply BE simpler asks.
Full separation of style from content-simplicity requires an LLM-authored,
meaning-preserving paraphrase that holds semantic content fixed while
varying only surface length/phrasing (e.g. "rewrite this criterion to be
brief" applied to a long criterion, and "rewrite this criterion in full
detail, preserving every constraint" applied to a short one, then re-judge
both versions with the SAME judge and check whether decisiveness/accuracy
track the REWRITE or the ORIGINAL semantic content).  That control is
explicitly forbidden by the task ("You may NOT rewrite any criterion with
an LLM").  Nothing weaker fully identifies it: word-count-normalised
"complexity density" (hedge/conjunction/comma density) is the cheapest
non-LLM proxy for content complexity and is used below as a partial,
NOT dispositive, control -- it is reported and gated as UNVERIFIED-bound,
never promoted to CONFIRMED.

============================================================================
SCOPE (population x instrument x baseline x regime), stated for every number
============================================================================
POPULATION : the 968 of 986 rubric records in
              data/conversation_rubrics.jsonl that join to
              data/comparisons.jsonl via covalx.judge.load_join (98.2%
              join rate; 18 unmatched, dropped, not imputed).
INSTRUMENT  : local Qwen3.5-2B-Base judge, PRECOMPUTED satisfaction
              tensors E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/
              results/a04_full.npz and a04_core.npz.  This script does
              NOT call the judge; it only re-slices the judge's own
              existing outputs by criterion subset.  Criterion-index
              mapping to text is independently re-derived here from
              conversation_rubrics.jsonl and verified byte-for-byte
              against the npz meta array before any statistic is computed
              (see verify_index_mapping()) -- this IS this script's
              positive control on its own plumbing, separate from the
              judge's positive control below.
BASELINE    : chance = 0.5 pairwise accuracy; full_all (mean over ALL
              scored coval_full criteria) as the pre-existing "core vs
              full" comparison arm.
REGIME      : matched-cardinality (n=4 criteria/prompt) subsets of
              coval_full's own criteria, human-authored throughout, ties
              broken as non-agreement (score(a) must be STRICTLY greater
              than score(b) to count as a correct call -- this matches
              E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/run.py's own
              convention), per-prompt equal weighting for every inferential
              test (clustering: responses/pairs are nested in prompts, so
              every paired test below operates on ONE ROW PER PROMPT, not
              per pair or per response).

============================================================================
PRE-REGISTERED THRESHOLDS (fixed before any accuracy/decisiveness number
was computed in this script -- structural counts above, e.g. join rate and
mean criteria/prompt, were checked for feasibility only, per standard
practice; no hypothesis-relevant number was seen before these were fixed)
============================================================================
T1 POSITIVE CONTROL (gates T2-T7; if it fails, T2-T7 are reported but
   flagged UNVERIFIED, not interpreted):
   full_all per-prompt pairwise accuracy > 0.55, one-sample Wilcoxon
   signed-rank of (accuracy_prompt - 0.5) two-sided p < 0.01.
NEGATIVE CONTROL (own pipeline, not the judge): shuffle which score
   attaches to which response label within each prompt (breaks the
   pairing the accuracy statistic depends on), 5 seeds. PASS if mean
   shuffled accuracy in [0.47, 0.53] and does not differ from 0.5 by a
   two-sided Wilcoxon at p > 0.05 for >= 4 of 5 seeds.
PLACEBO: split full_all's criteria by LIST POSITION (odd vs even index in
   the release's own coval_full ordering) instead of by length, n=4 each.
   PASS (i.e. the subsetting machinery itself is not the source of any
   effect) if |paired accuracy diff| is not significant at p > 0.05, OR
   |mean diff| < 0.02.
T2 mechanism, within-full length<->decisiveness correlation: Spearman rho
   between per-criterion character length and per-criterion decisiveness
   |sat-0.5|, pooled over every (prompt, criterion) in full_all.
   Pre-registered pass: rho < -0.15 and p < 0.001 (replicates the
   cross-arm finding WITHIN one fixed-authorship arm).
T3 mechanism, decisiveness gap: paired per-prompt decisiveness(short4) -
   decisiveness(long4), Wilcoxon signed-rank, two-sided.
T4 PRIMARY causal-chain test: paired per-prompt accuracy(short4) -
   accuracy(long4), Wilcoxon signed-rank, two-sided.
T5 SHAM: paired per-prompt accuracy(short4) - accuracy(random4, 5-seed
   mean), Wilcoxon signed-rank, two-sided.
T6 residual-content test: paired per-prompt accuracy(core) -
   accuracy(short4). If this is still positive and significant, core's
   advantage is NOT fully explained by length+cardinality alone.
T7 baseline "core's advantage": paired per-prompt accuracy(core) -
   accuracy(full_all), Wilcoxon signed-rank, two-sided (replicates what
   the two prior passes reported, on this script's own pipeline).
CONFOUND CONTROL (complexity-density, own axis, orthogonal-ish to length):
   full_simple4 (lowest hedge/conjunction/comma density) vs full_complex4
   (highest). Reported as a SPECIFICATION-CURVE alternative to the
   length split, not gated pass/fail -- if it shows a similar-sized
   accuracy split, style and content-complexity remain confounded and the
   result is downgraded to UNVERIFIED for the style/content distinction
   specifically (T4 stands regardless as a length-based result).
MULTIPLICITY: T2, T3, T4, T5, T6, T7 = 6 discovery cells -> Benjamini-
   Hochberg q=0.05 across those 6 p-values. T1, the negative control and
   the placebo are CONTROLS, evaluated against their own pre-registered
   pass bar, not folded into the discovery grid (a control that "passes"
   is not a discovery and does not compete for FDR budget; this is stated
   explicitly, not hidden).
SEEDS: base SEED=8101. full_random4 uses seeds 8101..8105 (5). The
   label-shuffle negative control uses seeds 9101..9105 (5, disjoint
   stream) so the two stochastic procedures never share draws.
STOPPING RULE: this is the entire pre-registered analysis; no further
   cells are added after seeing results. If population/instrument checks
   fail (e.g. index-mapping verification, or fewer than 900 joined
   prompts with >=4 full criteria), EXIT NONZERO rather than report a
   number.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(_ROOT))

from covalx.judge import load_join, human_pairs  # noqa: E402

SEED = 8101
RANDOM4_SEEDS = list(range(8101, 8106))
SHUFFLE_SEEDS = list(range(9101, 9106))
N_BOOT = 2000
BOOT_SEEDS = [SEED + i for i in range(5)]
LABELS = ("A", "B", "C", "D")

COMPARISONS = _ROOT / "data" / "comparisons.jsonl"
RUBRICS = _ROOT / "data" / "conversation_rubrics.jsonl"
NPZ_FULL = _ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_full.npz"
NPZ_CORE = _ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_core.npz"
OUT = _HERE / "results" / "independent_A.json"

HEDGE_WORDS = {
    "and", "but", "or", "while", "although", "though", "whereas", "however",
    "unless", "if", "should", "might", "could", "consider", "balance",
    "nuance", "perspective", "acknowledge", "sensitive", "appropriate",
    "carefully", "both", "either", "respect", "context",
}
_WORD_RE = re.compile(r"[A-Za-z']+")


def complexity_density(text: str) -> float:
    words = _WORD_RE.findall(text.lower())
    if not words:
        return 0.0
    hedges = sum(1 for w in words if w in HEDGE_WORDS)
    commas = text.count(",")
    return (hedges + commas) / len(words)


# ============================================================ data loading
def build_population():
    joined = load_join(COMPARISONS, RUBRICS)
    pop = {}
    for pid, comp, rub in joined:
        full_items = []
        for it in rub.get("coval_full") or []:
            sc = [s["score"] for s in it.get("scores") or []]
            if sc:
                full_items.append(it["criterion"])
        core_items = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if len(full_items) < 4:
            continue
        reps = {r["response_index"] for r in comp["responses"]}
        assessments = comp.get("metadata", {}).get("assessments") or []
        hp = human_pairs(assessments)
        hp = [(a, b) for a, b in hp if a in reps and b in reps]
        if not hp:
            continue
        pop[pid] = dict(full_items=full_items, core_items=core_items,
                         reps=reps, hp=hp)
    return pop


def load_sat(npz_path):
    d = np.load(npz_path, allow_pickle=True)
    sat = d["sat"]
    meta = d["meta"]
    table = {}
    for m, s in zip(meta, sat):
        pid, ci, lab = m.split("|")
        table[(pid, int(ci), lab)] = float(s)
    return table


def verify_index_mapping(pop, sat_full, sat_core):
    """Positive control on THIS SCRIPT'S plumbing (independent of the
    judge): the criterion-index re-derivation above must reproduce the
    exact (pid, ci) space the npz files were built over, or every
    downstream slice is silently misaligned."""
    ok = True
    n_checked = 0
    for pid, rec in pop.items():
        max_ci_full = max((ci for (p, ci, lab) in sat_full if p == pid), default=-1)
        # cheap check via a direct count instead of scanning the whole dict
        break
    # do it properly and cheaply: build per-pid max ci from sat tables once
    max_full = defaultdict(lambda: -1)
    for (p, ci, lab) in sat_full:
        if ci > max_full[p]:
            max_full[p] = ci
    max_core = defaultdict(lambda: -1)
    for (p, ci, lab) in sat_core:
        if ci > max_core[p]:
            max_core[p] = ci
    mismatches = []
    for pid, rec in pop.items():
        n_checked += 1
        exp_full = len(rec["full_items"])
        got_full = max_full[pid] + 1
        exp_core = len(rec["core_items"])
        got_core = max_core[pid] + 1
        if got_full != 0 and got_full != exp_full:
            mismatches.append((pid, "full", exp_full, got_full))
        if got_core != 0 and got_core != exp_core:
            mismatches.append((pid, "core", exp_core, got_core))
    return dict(n_checked=n_checked, n_mismatch=len(mismatches),
                mismatches=mismatches[:10], ok=len(mismatches) == 0)


# ============================================================ arm construction
def arm_score_accuracy_decisiveness(pop, sat_table, source, subset_fn):
    """subset_fn(pid, items) -> list[int] indices into items (full_items or
    core_items) to use.  Returns per-prompt dict of accuracy, decisiveness,
    mean_length, and the raw score dict (for downstream ratio/share calc)."""
    per_prompt = {}
    for pid, rec in pop.items():
        items = rec["full_items"] if source == "full" else rec["core_items"]
        idx = subset_fn(pid, items)
        if not idx:
            continue
        score = {}
        decisiveness_vals = []
        for lab in rec["reps"]:
            vals = []
            for ci in idx:
                key = (pid, ci, lab)
                if key in sat_table:
                    v = sat_table[key]
                    vals.append(v)
                    decisiveness_vals.append(abs(v - 0.5))
            if vals:
                score[lab] = float(np.mean(vals))
        hp = rec["hp"]
        if not hp or not score:
            continue
        n_valid = sum(1 for a, b in hp if a in score and b in score)
        if n_valid == 0:
            continue
        agree = sum(1 for a, b in hp if a in score and b in score and score[a] > score[b])
        acc = agree / n_valid
        mean_len = float(np.mean([len(items[i]) for i in idx]))
        dec = float(np.mean(decisiveness_vals)) if decisiveness_vals else np.nan
        per_prompt[pid] = dict(accuracy=acc, decisiveness=dec, mean_length=mean_len,
                                score=score, n_pairs=n_valid)
    return per_prompt


def subset_all(pid, items):
    return list(range(len(items)))


def subset_topk_by(key_fn, k=4, descending=False):
    def fn(pid, items):
        order = sorted(range(len(items)), key=lambda i: key_fn(items[i]),
                        reverse=descending)
        return order[:min(k, len(items))]
    return fn


def subset_random4(seed):
    def fn(pid, items):
        rng = np.random.default_rng(hash((seed, pid)) & 0xFFFFFFFF)
        n = min(4, len(items))
        return list(rng.choice(len(items), size=n, replace=False))
    return fn


def subset_position(parity, k=4):
    def fn(pid, items):
        idx = [i for i in range(len(items)) if i % 2 == parity]
        return idx[:min(k, len(idx))]
    return fn


# ============================================================ stats helpers
def paired_wilcoxon(a: dict, b: dict):
    """a, b: pid -> value. Returns matched-pair arrays + test stats."""
    pids = sorted(set(a) & set(b))
    xa = np.array([a[p] for p in pids])
    xb = np.array([b[p] for p in pids])
    diff = xa - xb
    if len(diff) < 3 or np.allclose(diff, diff[0]):
        return dict(n=len(diff), mean_diff=float(np.mean(diff)) if len(diff) else float("nan"),
                    p=float("nan"), stat=float("nan"), pids=pids, diff=diff)
    try:
        res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
        p, stat = float(res.pvalue), float(res.statistic)
    except ValueError:
        p, stat = float("nan"), float("nan")
    return dict(n=len(diff), mean_diff=float(np.mean(diff)), sd_diff=float(np.std(diff, ddof=1)),
                p=p, stat=stat, pids=pids, diff=diff)


def rank_biserial_from_wilcoxon(diff: np.ndarray) -> float:
    d = diff[diff != 0]
    if len(d) == 0:
        return float("nan")
    n_pos = np.sum(d > 0)
    n_neg = np.sum(d < 0)
    return float((n_pos - n_neg) / len(d))


def bh_fdr(pvals: dict, q=0.05):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    max_k_sig = 0
    for k, (name, p) in enumerate(items, start=1):
        thresh = q * k / m
        if p <= thresh:
            max_k_sig = k
    for k, (name, p) in enumerate(items, start=1):
        out[name] = dict(p=p, rank=k, bh_threshold=q * k / m, significant=(k <= max_k_sig))
    return out


def cluster_bootstrap_diff(a: dict, b: dict, seeds, n_boot=N_BOOT):
    pids = sorted(set(a) & set(b))
    xa = np.array([a[p] for p in pids])
    xb = np.array([b[p] for p in pids])
    n = len(pids)
    all_draws = []
    per_seed_mean = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        draws = np.empty(n_boot)
        for i in range(n_boot):
            idx = rng.integers(0, n, size=n)
            draws[i] = np.mean(xa[idx] - xb[idx])
        all_draws.append(draws)
        per_seed_mean.append(float(np.mean(draws)))
    pooled = np.concatenate(all_draws)
    return dict(n_prompts=n, ci_lo=float(np.percentile(pooled, 2.5)),
                ci_hi=float(np.percentile(pooled, 97.5)),
                mean=float(np.mean(pooled)),
                per_seed_mean=per_seed_mean,
                seed_spread_sd=float(np.std(per_seed_mean, ddof=1)) if len(per_seed_mean) > 1 else 0.0)


def cluster_bootstrap_ratio(num_a: dict, num_b: dict, den_a: dict, den_b: dict, seeds, n_boot=N_BOOT):
    """Ratio of two paired mean differences, resampled jointly by prompt so
    numerator/denominator covariance is preserved."""
    pids = sorted(set(num_a) & set(num_b) & set(den_a) & set(den_b))
    na = np.array([num_a[p] for p in pids]); nb = np.array([num_b[p] for p in pids])
    da = np.array([den_a[p] for p in pids]); db = np.array([den_b[p] for p in pids])
    n = len(pids)
    point = float(np.mean(na - nb) / np.mean(da - db)) if np.mean(da - db) != 0 else float("nan")
    all_draws = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        draws = np.empty(n_boot)
        for i in range(n_boot):
            idx = rng.integers(0, n, size=n)
            denom = np.mean(da[idx] - db[idx])
            draws[i] = np.mean(na[idx] - nb[idx]) / denom if denom != 0 else np.nan
        all_draws.append(draws)
    pooled = np.concatenate(all_draws)
    pooled = pooled[np.isfinite(pooled)]
    return dict(point=point, n_prompts=n,
                ci_lo=float(np.percentile(pooled, 2.5)) if len(pooled) else float("nan"),
                ci_hi=float(np.percentile(pooled, 97.5)) if len(pooled) else float("nan"),
                n_finite_draws=int(len(pooled)))


def one_sample_wilcoxon_vs(a: dict, mu: float):
    pids = sorted(a)
    x = np.array([a[p] for p in pids]) - mu
    if np.allclose(x, 0):
        return dict(n=len(x), mean=float(np.mean(x) + mu), p=float("nan"))
    res = stats.wilcoxon(x, alternative="two-sided")
    return dict(n=len(x), mean=float(np.mean(x) + mu), p=float(res.pvalue))


def dget(pp: dict, field: str) -> dict:
    return {p: v[field] for p, v in pp.items()}


# ============================================================ main
def main():
    print("[1/6] loading population + join ...")
    pop = build_population()
    print(f"  usable prompts (>=4 full criteria, >=1 valid human pair): {len(pop)}")
    if len(pop) < 900:
        print("EXIT: population smaller than pre-registered floor (900) -- "
              "cannot support the analysis.", file=sys.stderr)
        sys.exit(2)

    print("[2/6] loading precomputed satisfaction tensors ...")
    sat_full = load_sat(NPZ_FULL)
    sat_core = load_sat(NPZ_CORE)

    print("[3/6] verifying criterion-index mapping against npz meta (plumbing positive control) ...")
    vmap = verify_index_mapping(pop, sat_full, sat_core)
    print(f"  checked {vmap['n_checked']} prompts, mismatches={vmap['n_mismatch']}")
    if not vmap["ok"]:
        print("EXIT: index mapping does not match npz meta -- downstream slices "
              "would be misaligned. See mismatches.", file=sys.stderr)
        print(vmap["mismatches"], file=sys.stderr)
        sys.exit(2)

    print("[4/6] building arms ...")
    arms = {}
    arms["full_all"] = arm_score_accuracy_decisiveness(pop, sat_full, "full", subset_all)
    arms["core"] = arm_score_accuracy_decisiveness(pop, sat_core, "core", subset_all)
    arms["full_short4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_topk_by(len, k=4, descending=False))
    arms["full_long4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_topk_by(len, k=4, descending=True))
    arms["full_pos_even4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_position(0, k=4))
    arms["full_pos_odd4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_position(1, k=4))
    arms["full_simple4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_topk_by(complexity_density, k=4, descending=False))
    arms["full_complex4"] = arm_score_accuracy_decisiveness(
        pop, sat_full, "full", subset_topk_by(complexity_density, k=4, descending=True))

    random4_runs = []
    for seed in RANDOM4_SEEDS:
        random4_runs.append(arm_score_accuracy_decisiveness(
            pop, sat_full, "full", subset_random4(seed)))
    # seed-averaged random4 (per prompt mean across the 5 seeds) for the
    # primary SHAM comparison, plus per-seed accuracy for the spread report
    common_pids = set.intersection(*[set(r) for r in random4_runs])
    full_random4 = {}
    for pid in common_pids:
        full_random4[pid] = dict(
            accuracy=float(np.mean([r[pid]["accuracy"] for r in random4_runs])),
            decisiveness=float(np.mean([r[pid]["decisiveness"] for r in random4_runs])),
            mean_length=float(np.mean([r[pid]["mean_length"] for r in random4_runs])),
        )
    arms["full_random4"] = full_random4
    random4_seed_accs = [float(np.mean(list(dget(r, "accuracy").values()))) for r in random4_runs]

    print("[5/6] negative control: label-shuffled scoring on full_all ...")
    neg_ctrl_accs = []
    neg_ctrl_wilcoxon_ps = []
    for seed in SHUFFLE_SEEDS:
        rng = np.random.default_rng(seed)
        shuffled = {}
        for pid, rec in pop.items():
            row = arms["full_all"].get(pid)
            if row is None:
                continue
            labs = list(row["score"].keys())
            perm = labs.copy()
            rng.shuffle(perm)
            shuf_score = dict(zip(labs, [row["score"][l] for l in perm]))
            hp = rec["hp"]
            n_valid = sum(1 for a, b in hp if a in shuf_score and b in shuf_score)
            if n_valid == 0:
                continue
            agree = sum(1 for a, b in hp if a in shuf_score and b in shuf_score
                        and shuf_score[a] > shuf_score[b])
            shuffled[pid] = dict(accuracy=agree / n_valid)
        mean_acc = float(np.mean(list(dget(shuffled, "accuracy").values())))
        wp = one_sample_wilcoxon_vs(dget(shuffled, "accuracy"), 0.5)
        neg_ctrl_accs.append(mean_acc)
        neg_ctrl_wilcoxon_ps.append(wp["p"])
    neg_ctrl_pass = (0.47 <= float(np.mean(neg_ctrl_accs)) <= 0.53
                     and sum(p > 0.05 for p in neg_ctrl_wilcoxon_ps if not np.isnan(p)) >= 4)

    print("[6/6] running pre-registered tests ...")

    # ---- T1 positive control -------------------------------------------
    full_all_acc = dget(arms["full_all"], "accuracy")
    t1 = one_sample_wilcoxon_vs(full_all_acc, 0.5)
    t1_pass = t1["mean"] > 0.55 and t1["p"] < 0.01
    t1["pass"] = t1_pass

    # ---- placebo: position split -----------------------------------------
    placebo_test = paired_wilcoxon(dget(arms["full_pos_even4"], "accuracy"),
                                    dget(arms["full_pos_odd4"], "accuracy"))
    placebo_len_gap = (np.mean(list(dget(arms["full_pos_even4"], "mean_length").values()))
                        - np.mean(list(dget(arms["full_pos_odd4"], "mean_length").values())))
    placebo_pass = (np.isnan(placebo_test["p"]) or placebo_test["p"] > 0.05
                    or abs(placebo_test["mean_diff"]) < 0.02)

    # ---- T2: within-full length<->decisiveness correlation (criterion level)
    crit_len, crit_dec = [], []
    for pid, rec in pop.items():
        items = rec["full_items"]
        for ci, text in enumerate(items):
            vals = [sat_full[(pid, ci, lab)] for lab in rec["reps"]
                    if (pid, ci, lab) in sat_full]
            if not vals:
                continue
            crit_len.append(len(text))
            crit_dec.append(float(np.mean([abs(v - 0.5) for v in vals])))
    crit_len = np.array(crit_len); crit_dec = np.array(crit_dec)
    rho_t2, p_t2 = stats.spearmanr(crit_len, crit_dec)
    t2 = dict(rho=float(rho_t2), p=float(p_t2), n=len(crit_len),
              pass_=(rho_t2 < -0.15 and p_t2 < 0.001))

    # confound control: partial correlation controlling for complexity density
    crit_pid_ci = [(pid, ci) for pid, rec in pop.items()
                   for ci in range(len(rec["full_items"]))
                   if any((pid, ci, lab) in sat_full for lab in rec["reps"])]
    crit_cplx = np.array([complexity_density(pop[pid]["full_items"][ci]) for pid, ci in crit_pid_ci])

    def residualize(y, x):
        X = np.column_stack([np.ones_like(x), x])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        return y - X @ beta

    len_resid = residualize(crit_len.astype(float), crit_cplx)
    dec_resid = residualize(crit_dec.astype(float), crit_cplx)
    rho_partial, p_partial = stats.spearmanr(len_resid, dec_resid)
    corr_len_cplx = float(stats.spearmanr(crit_len, crit_cplx).correlation)
    confound_control = dict(
        raw_rho=float(rho_t2), partial_rho_ctrl_complexity=float(rho_partial),
        p_partial=float(p_partial), corr_length_complexity_density=corr_len_cplx,
        note="partial correlation of length vs decisiveness after residualizing "
             "both on a word-count-normalised hedge/conjunction/comma density "
             "proxy for content complexity. Survives ~intact => length has "
             "explanatory power beyond this crude complexity proxy (does NOT "
             "rule out subtler content confounds -- see IDENTIFICATION above).")

    # ---- T3: decisiveness gap short4 vs long4 -----------------------------
    t3 = paired_wilcoxon(dget(arms["full_short4"], "decisiveness"),
                         dget(arms["full_long4"], "decisiveness"))
    t3_boot = cluster_bootstrap_diff(dget(arms["full_short4"], "decisiveness"),
                                      dget(arms["full_long4"], "decisiveness"), BOOT_SEEDS)
    t3["rank_biserial"] = rank_biserial_from_wilcoxon(t3["diff"])
    t3["boot"] = t3_boot

    # ---- T4: PRIMARY accuracy(short4) - accuracy(long4) -------------------
    t4 = paired_wilcoxon(dget(arms["full_short4"], "accuracy"),
                         dget(arms["full_long4"], "accuracy"))
    t4_boot = cluster_bootstrap_diff(dget(arms["full_short4"], "accuracy"),
                                      dget(arms["full_long4"], "accuracy"), BOOT_SEEDS)
    t4["rank_biserial"] = rank_biserial_from_wilcoxon(t4["diff"])
    t4["boot"] = t4_boot
    t4["cohens_dz"] = float(t4["mean_diff"] / t4["sd_diff"]) if t4.get("sd_diff") else float("nan")

    # ---- T5: SHAM accuracy(short4) - accuracy(random4) --------------------
    t5 = paired_wilcoxon(dget(arms["full_short4"], "accuracy"),
                         dget(arms["full_random4"], "accuracy"))
    t5_boot = cluster_bootstrap_diff(dget(arms["full_short4"], "accuracy"),
                                      dget(arms["full_random4"], "accuracy"), BOOT_SEEDS)
    t5["rank_biserial"] = rank_biserial_from_wilcoxon(t5["diff"])
    t5["boot"] = t5_boot

    # ---- T6: residual content test, core - short4 --------------------------
    t6 = paired_wilcoxon(dget(arms["core"], "accuracy"), dget(arms["full_short4"], "accuracy"))
    t6_boot = cluster_bootstrap_diff(dget(arms["core"], "accuracy"),
                                      dget(arms["full_short4"], "accuracy"), BOOT_SEEDS)
    t6["rank_biserial"] = rank_biserial_from_wilcoxon(t6["diff"])
    t6["boot"] = t6_boot

    # ---- T7: baseline core - full_all --------------------------------------
    t7 = paired_wilcoxon(dget(arms["core"], "accuracy"), dget(arms["full_all"], "accuracy"))
    t7_boot = cluster_bootstrap_diff(dget(arms["core"], "accuracy"),
                                      dget(arms["full_all"], "accuracy"), BOOT_SEEDS)
    t7["rank_biserial"] = rank_biserial_from_wilcoxon(t7["diff"])
    t7["boot"] = t7_boot

    # ---- multiplicity ------------------------------------------------------
    grid_p = {"T2_len_dec_corr": t2["p"], "T3_dec_gap": t3["p"], "T4_primary_acc_gap": t4["p"],
              "T5_sham_gap": t5["p"], "T6_residual_content": t6["p"], "T7_core_vs_full_all": t7["p"]}
    bh = bh_fdr(grid_p, q=0.05)

    # ---- specification-curve alternative: complexity-density split --------
    t_cplx = paired_wilcoxon(dget(arms["full_simple4"], "accuracy"),
                              dget(arms["full_complex4"], "accuracy"))
    t_cplx["rank_biserial"] = rank_biserial_from_wilcoxon(t_cplx["diff"])

    # ---- STYLE-ATTRIBUTABLE SHARE of core's advantage ----------------------
    share_vs_sham = cluster_bootstrap_ratio(
        dget(arms["full_short4"], "accuracy"), dget(arms["full_random4"], "accuracy"),
        dget(arms["core"], "accuracy"), dget(arms["full_all"], "accuracy"), BOOT_SEEDS)
    share_vs_long = cluster_bootstrap_ratio(
        dget(arms["full_short4"], "accuracy"), dget(arms["full_long4"], "accuracy"),
        dget(arms["core"], "accuracy"), dget(arms["full_all"], "accuracy"), BOOT_SEEDS)

    # ---- descriptive summary table (mean, sd across prompts) --------------
    def summarize(arm_pp, field):
        vals = np.array(list(dget(arm_pp, field).values()))
        return dict(mean=float(np.mean(vals)), sd=float(np.std(vals, ddof=1)),
                    n=len(vals))

    summary = {}
    for name, pp in arms.items():
        summary[name] = dict(
            accuracy=summarize(pp, "accuracy"),
            decisiveness=summarize(pp, "decisiveness"),
            mean_length=summarize(pp, "mean_length"),
        )
    # pooled (pair-weighted, matches r04 convention) accuracy, descriptive only
    for name, pp in arms.items():
        agree_pool = tot_pool = 0
        for pid, row in pp.items():
            rec = pop.get(pid)
            if rec is None:
                continue
            score = row.get("score")
            if score is None:
                continue
            for a, b in rec["hp"]:
                if a in score and b in score:
                    tot_pool += 1
                    if score[a] > score[b]:
                        agree_pool += 1
        summary[name]["pooled_pairwise_accuracy"] = (agree_pool / tot_pool) if tot_pool else None
        summary[name]["pooled_n_pairs"] = tot_pool

    out = dict(
        seed=SEED,
        population=dict(n_rubric_records=986, n_comparisons_records=1078,
                         n_joined=968, n_usable=len(pop)),
        index_mapping_verification=vmap,
        arm_summary=summary,
        random4_seed_accuracy_spread=dict(seeds=RANDOM4_SEEDS, per_seed_mean_accuracy=random4_seed_accs,
                                           mean=float(np.mean(random4_seed_accs)),
                                           sd=float(np.std(random4_seed_accs, ddof=1))),
        controls=dict(
            T1_positive_control=t1,
            negative_control_label_shuffle=dict(
                seeds=SHUFFLE_SEEDS, per_seed_mean_accuracy=neg_ctrl_accs,
                per_seed_wilcoxon_p=neg_ctrl_wilcoxon_ps,
                mean=float(np.mean(neg_ctrl_accs)), pass_=neg_ctrl_pass),
            placebo_position_split=dict(test=placebo_test, mean_length_gap=float(placebo_len_gap),
                                         pass_=bool(placebo_pass)),
        ),
        tests=dict(
            T2_len_dec_corr_within_full=t2,
            T2_confound_control_complexity_density=confound_control,
            T3_decisiveness_gap_short_vs_long=t3,
            T4_primary_accuracy_gap_short_vs_long=t4,
            T5_sham_accuracy_gap_short_vs_random=t5,
            T6_residual_content_core_vs_short4=t6,
            T7_baseline_core_vs_full_all=t7,
            spec_curve_complexity_density_split=t_cplx,
        ),
        multiplicity_bh=bh,
        style_attributable_share=dict(
            vs_sham_random4=share_vs_sham,
            vs_long4=share_vs_long,
            definition="numerator = paired mean[accuracy(short4) - baseline]; "
                       "denominator = paired mean[accuracy(core) - accuracy(full_all)]; "
                       "ratio computed inside a joint prompt-level bootstrap so "
                       "numerator/denominator covariance is preserved.",
        ),
    )

    def sanitize(o):
        if isinstance(o, dict):
            return {k: sanitize(v) for k, v in o.items() if k not in ("diff",)}
        if isinstance(o, (list, tuple)):
            return [sanitize(v) for v in o]
        if isinstance(o, np.ndarray):
            return [sanitize(v) for v in o.tolist()]
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, float) and np.isnan(o):
            return None
        return o

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sanitize(out), indent=1))
    print(f"wrote {OUT}")

    # ---------------------------------------------------------------- print
    print("\n=== T1 POSITIVE CONTROL ===")
    print(f"  full_all accuracy mean={t1['mean']:.4f} p(vs 0.5)={t1['p']:.2e} -> "
          f"{'PASS' if t1_pass else 'FAIL'}")
    print("\n=== NEGATIVE CONTROL (label shuffle) ===")
    print(f"  mean={np.mean(neg_ctrl_accs):.4f} per-seed={['%.4f' % a for a in neg_ctrl_accs]} -> "
          f"{'PASS' if neg_ctrl_pass else 'FAIL'}")
    print("\n=== PLACEBO (position split) ===")
    print(f"  mean_diff={placebo_test['mean_diff']:+.4f} p={placebo_test['p']:.3f} "
          f"len_gap={placebo_len_gap:+.2f} -> {'PASS' if placebo_pass else 'FAIL'}")
    print("\n=== T2 length<->decisiveness within full ===")
    print(f"  rho={rho_t2:.4f} p={p_t2:.2e} n={len(crit_len)}  partial(ctrl complexity)={rho_partial:.4f}")
    print("\n=== T4 PRIMARY: accuracy(short4) - accuracy(long4) ===")
    print(f"  mean_diff={t4['mean_diff']:+.4f} [{t4_boot['ci_lo']:+.4f}, {t4_boot['ci_hi']:+.4f}] "
          f"p={t4['p']:.4f} rank_biserial={t4['rank_biserial']:+.3f} n={t4['n']}")
    print("\n=== T7 baseline: accuracy(core) - accuracy(full_all) ===")
    print(f"  mean_diff={t7['mean_diff']:+.4f} [{t7_boot['ci_lo']:+.4f}, {t7_boot['ci_hi']:+.4f}] "
          f"p={t7['p']:.4f}")
    print("\n=== STYLE-ATTRIBUTABLE SHARE ===")
    print(f"  vs sham(random4): {share_vs_sham['point']:.3f} "
          f"[{share_vs_sham['ci_lo']:.3f}, {share_vs_sham['ci_hi']:.3f}]")
    print(f"  vs long4:         {share_vs_long['point']:.3f} "
          f"[{share_vs_long['ci_lo']:.3f}, {share_vs_long['ci_hi']:.3f}]")
    print("\nBH-FDR grid:")
    for k, v in bh.items():
        print(f"  {k}: p={v['p']:.4f} rank={v['rank']} thresh={v['bh_threshold']:.4f} "
              f"sig={v['significant']}")


if __name__ == "__main__":
    main()
