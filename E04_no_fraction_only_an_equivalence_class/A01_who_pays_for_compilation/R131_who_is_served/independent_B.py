"""
independent_B.py -- who is served by compilation? A per-annotator attack.

======================================================================
ESTIMAND (write this before computing a single outcome number)
======================================================================
UNIT (primary): a named annotator ("person"), aggregated over every prompt
for which they (a) gave a personal "world" ranking of the four responses
that is not fully tied, and (b) rated at least one coval_full criterion in
that prompt.

UNIT (base, feeding the person aggregate): a (person, prompt, unordered
response-pair) triple -- 6 pairs per qualifying assessment.

For person i on prompt p, two response-scoring arms are built purely from
already-published data plus the precomputed satisfaction tensors:

  FULL, personalized  score_full_i(resp) = sum_c  rating_i(p,c) * sat_full(p,c,resp)
      summed over exactly the coval_full criteria THAT PERSON RATED in prompt p,
      using THEIR OWN signed -10..+10 rating as the weight. This is the
      maximum personalization the uncompiled rubric could in principle
      deliver to this one person: it uses nobody else's numbers, and it
      auto-handles the "roughly a quarter of criteria are negatively rated"
      fact person-by-person (a criterion the person marked undesirable gets
      a negative weight, flipping its contribution for THAT person) rather
      than through a population-mean sign flip.

  CORE, shared        score_core(resp)   = mean_c sat_core(p,c,resp)
      over the (2-4) coval_core criteria, unweighted, IDENTICAL for every
      person on prompt p -- coval_core ships no ratings, so there is no
      person-specific information left to weight with. This is the one and
      only "full arm" convention used for the person-level estimand; see
      POSITIVE CONTROL below for the one place a second, population-mean
      convention is used, for a different, explicitly labelled purpose.

AGREEMENT(arm, i, p) = mean over the 6 unordered response pairs of
  1 - |P_actual(pair) - P_predicted(pair)|,   P in {0, 0.5, 1}
(0.5 = a tie either in the person's stated ranking or in the arm's implied
score). This is a partial-credit pairwise concordance in [0, 1].

GAIN(i, p)   = AGREEMENT(full, i, p) - AGREEMENT(core, i, p)
g_i          = mean over person i's qualifying prompts of GAIN(i, p)

g_i > 0  => compilation LOSES information for person i relative to what a
            personalized full rubric could have delivered them ("loser").
g_i < 0  => the compiled arm matches or beats the personalized arm for this
            person ("winner" / at least as well served).

"The compiled rubric serves all the participants" translates to: the
distribution of g_i is not both (a) heterogeneous beyond resampling noise
and (b) predictable from measurable person characteristics. Both conditions
are tested below, pre-registered, before either was computed.

======================================================================
PRE-REGISTRATION (thresholds fixed before any outcome number was read)
======================================================================
- Exclude (person,prompt) units where the person's world ranking is a
  single fully-tied group over all 4 responses: mechanically forces
  AGREEMENT(any arm) to depend only on the (arm-independent) fraction of
  tied ACTUAL pairs, so gain would carry zero discriminating information
  by construction (see METRIC PLACEBO below, case 1, for the exact hand
  derivation of why).
- Exclude the (rare) units where the person rated zero coval_full criteria
  in that prompt (full-arm score undefined).
- Include a person only if they have >=3 remaining qualifying prompts.
- Multiplicity, family A (993-ish per-person tests of H0: g_i=0): BH-FDR
  q=0.05.
- Multiplicity, family B (covariate-of-loserness tests, 7 univariate +
  1 multivariate regression's coefficients): BH-FDR q=0.05, separately.
- Bootstrap: 2000 resamples; 5 seeds {4409,4410,4411,4412,4413}; report the
  spread of every stochastic headline number across seeds.
- "Real heterogeneity" requires BOTH: (a) a DerSimonian-Laird tau^2 > 0
  whose person-cluster-bootstrap 95% CI excludes 0, AND (b) raw
  between-person SD(g_i) >= 1.5x the median within-person bootstrap SE_i
  (an effect-size floor, not just a p<0.05 test, because n~1000 makes
  p-values cheap).
- Positive control: reusing the mean-of-all-raters ("population") full-arm
  convention (the one the "about a quarter carry a negative mean rating"
  fact was itself validated with), the resulting arm must beat the pooled
  human_pairs baseline at >0.55 pairwise accuracy, pre-registered floor
  well under the two external anchors (0.60 pairwise / 0.61 flipped-vs-0.39
  unflipped) so the bar is not set to a foregone pass.
- Loser flag for an individual: within-person bootstrap 95% percentile CI
  of g_i excludes 0, AND survives BH-FDR family A.

======================================================================
STRONGEST CONFOUNDS (written before running; controlled in this script)
======================================================================
1. MECHANICAL PERSONALIZATION ADVANTAGE. The full-arm score is built out of
   person i's OWN ratings; a person who rates more criteria, or rates them
   more extremely, gets a more differentiated predicted ranking almost by
   construction, which can correlate with their own separately-stated
   ranking even if the judge's satisfaction signal carries zero real
   information. CONTROL: (a) n_ratings and rating-extremity enter the
   loser-covariate regression explicitly; (b) an in-script SHUFFLE PLACEBO:
   recompute the full-arm score using person i's own rating VALUES but
   reassigned to a random permutation of the SAME set of criteria they
   rated (same quantity and extremity of signal, wrong pairing to the
   criterion text). If shuffled-full still beats core almost as much as
   true-full, the gain is mechanical (quantity), not about which criteria
   matched their values.
2. SHARED-PROMPT CONFOUND. Many people rate the same prompt; if a prompt's
   core criteria are unusually bad (or the judge is noisy on it) for
   EVERYONE who reviewed it, people who happen to have reviewed a few such
   prompts look like "losers" even though nothing about THEM differs from
   anyone else. CONTROL: (a) a prompt-cluster bootstrap (resample PROMPTS,
   not people or pairs) for every population/aggregate-level CI, since a
   prompt's whole slate of assessments must move together; (b) a
   prompt-demeaned residual gain, g_i_resid = mean_i(gain(i,p) -
   prompt_mean_gain(p)), used as a robustness check on whether
   between-person variance survives once shared prompt effects are removed.

Positive control, placebo (hand-derived), floor, confounds, multi-seed
spread, absolute + standardized effect sizes, and the multiplicity-corrected
loser list are all written to the single JSON output below.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats

REPO = next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(REPO))

from covalx import load_join, norm, parse_ranking, human_pairs  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "independent_B.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

SEED = 4409
SEEDS = [4409, 4410, 4411, 4412, 4413]
LABELS = ["A", "B", "C", "D"]
PAIRS = list(combinations(LABELS, 2))  # 6 pairs, fixed order
N_BOOT = 2000
MIN_PROMPTS = 3
FDR_Q = 0.05
POS_CONTROL_FLOOR = 0.55
HETEROGENEITY_SD_RATIO_FLOOR = 1.5

t_start = time.time()

PREREG = {
    "estimand_words": (
        "Per annotator i: gain_i(p) = agreement(personalized-full-arm, i, p) "
        "- agreement(shared-core-arm, i, p), agreement = partial-credit "
        "pairwise concordance of the arm's implied response ranking against "
        "person i's own stated world ranking of the 4 responses on prompt p. "
        "g_i = mean over i's qualifying prompts. g_i>0 means compilation "
        "loses relative to what personalization could deliver this specific "
        "person; g_i<0 means compilation matches or beats it."
    ),
    "unit_primary": "person (annotator_id)",
    "unit_base": "(person, prompt, unordered response-pair)",
    "full_arm_convention": (
        "personalized: weight = that person's own signed -10..+10 rating on "
        "each coval_full criterion they rated; no population averaging, no "
        "separate sign-flip step (the person's own sign already encodes it)"
    ),
    "core_arm_convention": "unweighted mean satisfaction over coval_core criteria; identical for every person on a prompt by construction",
    "exclude_fully_tied_world_ranking": True,
    "exclude_zero_rated_criteria": True,
    "min_prompts_per_person": MIN_PROMPTS,
    "fdr_q_family_A_person_tests": FDR_Q,
    "fdr_q_family_B_covariate_tests": FDR_Q,
    "n_bootstrap": N_BOOT,
    "seeds": SEEDS,
    "heterogeneity_requires": [
        "DerSimonian-Laird tau^2 > 0",
        "person-cluster-bootstrap 95% CI of tau^2 excludes 0",
        f"raw between-person SD(g_i) >= {HETEROGENEITY_SD_RATIO_FLOOR}x median within-person bootstrap SE_i",
    ],
    "positive_control_convention": "population: weight = mean rating across ALL raters of that criterion (matches the external 'quarter negative' validation methodology)",
    "positive_control_floor": POS_CONTROL_FLOOR,
    "loser_flag_rule": "within-person bootstrap 95% percentile CI of g_i excludes 0, AND survives BH-FDR family A",
}


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


# ====================================================================
# METRIC-CORRECTNESS PLACEBO -- hand-derived before touching real data
# ====================================================================
def relation_from_scores(scores: dict) -> dict:
    rel = {}
    for a, b in PAIRS:
        sa, sb = scores[a], scores[b]
        if sa > sb:
            rel[(a, b)] = 1.0
        elif sa < sb:
            rel[(a, b)] = 0.0
        else:
            rel[(a, b)] = 0.5
    return rel


def relation_from_ranking(ranking_str: str):
    groups = parse_ranking(ranking_str)
    rank_of = {}
    for gi, grp in enumerate(groups):
        for lab in grp:
            rank_of[lab] = gi
    rel = {}
    for a, b in PAIRS:
        if a not in rank_of or b not in rank_of:
            rel[(a, b)] = None
            continue
        if rank_of[a] < rank_of[b]:
            rel[(a, b)] = 1.0
        elif rank_of[a] > rank_of[b]:
            rel[(a, b)] = 0.0
        else:
            rel[(a, b)] = 0.5
    return rel, rank_of


def agreement(actual_rel: dict, pred_rel: dict):
    vals = []
    for k in PAIRS:
        av = actual_rel[k]
        if av is None:
            continue
        vals.append(1.0 - abs(av - pred_rel[k]))
    if not vals:
        return None, 0
    return float(np.mean(vals)), len(vals)


def run_metric_placebo():
    cases = {}

    # case 1: actual "A>B>C=D", predicted fully tied. Hand derivation:
    # actual pairs AB=1,AC=1,AD=1,BC=1,BD=1,CD=0.5(tie); predicted=0.5 always
    # -> credit = 1-|1-0.5|=0.5 for the 5 strict pairs, 1-|0.5-0.5|=1.0 for CD.
    # mean = (5*0.5 + 1.0)/6 = 3.5/6 = 0.583333...
    actual_rel, _ = relation_from_ranking("A>B>C=D")
    pred_rel = relation_from_scores({"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0})
    got, n = agreement(actual_rel, pred_rel)
    expected = 3.5 / 6.0
    cases["case1_tied_actual_vs_flat_predicted"] = {
        "expected": expected, "got": got, "pass": abs(got - expected) < 1e-9,
    }

    # case 2: actual "A>B>C>D", predicted strictly monotone in the same
    # order -> all 6 pairs strict and correctly ordered -> agreement = 1.0
    actual_rel, _ = relation_from_ranking("A>B>C>D")
    pred_rel = relation_from_scores({"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0})
    got, n = agreement(actual_rel, pred_rel)
    cases["case2_perfect_match"] = {"expected": 1.0, "got": got, "pass": abs(got - 1.0) < 1e-9}

    # case 3: actual "A>B>C>D", predicted exactly reversed -> every strict
    # pair flips -> credit 0 on every pair -> agreement = 0.0
    pred_rel = relation_from_scores({"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0})
    got, n = agreement(actual_rel, pred_rel)
    cases["case3_perfect_reversal"] = {"expected": 0.0, "got": got, "pass": abs(got - 0.0) < 1e-9}

    # case 4 (tie-handling sanity): actual fully tied "A=B=C=D", predicted
    # perfectly separated -> every pair actual=0.5, pred in {0,1} ->
    # credit = 1-|0.5-{0,1}| = 0.5 every time -> agreement = 0.5 exactly.
    actual_rel, _ = relation_from_ranking("A=B=C=D")
    pred_rel = relation_from_scores({"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0})
    got, n = agreement(actual_rel, pred_rel)
    cases["case4_flat_actual_vs_separated_predicted"] = {
        "expected": 0.5, "got": got, "pass": abs(got - 0.5) < 1e-9,
    }

    ok = all(c["pass"] for c in cases.values())
    return cases, ok


# ====================================================================
# LOAD
# ====================================================================
def load_sat_lut(npz_path: Path):
    d = np.load(npz_path, allow_pickle=True)
    meta, sat = d["meta"], d["sat"]
    lut = {}
    for m, s in zip(meta, sat):
        pid, ci, lab = m.split("|")
        lut[(pid, int(ci), lab)] = float(s)
    return lut


ORD_SUBJ = {"single correct answer": 0, "unsure whether": 1,
            "depends on something else": 2, "values or culture": 3}
ORD_IMP = {"not important": 0, "somewhat important": 1, "very important": 2}
ORD_REP = {"not at all": 0, "slightly": 1, "moderately": 2, "very": 3, "extremely": 4}


def ordinal_lookup(raw: str, table: dict):
    t = norm(raw)
    for key, val in table.items():
        if key in t:
            return val
    return None


def main():
    print("== metric placebo ==")
    placebo_cases, placebo_ok = run_metric_placebo()
    for k, v in placebo_cases.items():
        print(f"  {k}: expected={v['expected']:.6f} got={v['got']:.6f} pass={v['pass']}")
    if not placebo_ok:
        print("METRIC PLACEBO FAILED -- instrument is not measuring what it claims. Exiting nonzero.")
        sys.exit(1)

    print("== loading data ==")
    joined = load_join(REPO / "data" / "comparisons.jsonl", REPO / "data" / "conversation_rubrics.jsonl")
    n_prompts_joined = len(joined)

    sat_full_path = REPO / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_full.npz"
    sat_core_path = REPO / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_core.npz"
    if not sat_full_path.exists() or not sat_core_path.exists():
        print(f"MISSING precomputed satisfaction tensors at {sat_full_path} / {sat_core_path}. Exiting nonzero.")
        sys.exit(1)
    sat_full = load_sat_lut(sat_full_path)
    sat_core = load_sat_lut(sat_core_path)
    print(f"  sat_full entries={len(sat_full):,}  sat_core entries={len(sat_core):,}")

    # ---------------------------------------------------------------
    # POSITIVE CONTROL: population-mean-weighted full arm vs pooled
    # human_pairs, the SAME convention the "quarter negative" fact used.
    # ---------------------------------------------------------------
    print("== positive control (population-mean full arm vs pooled human_pairs) ==")
    pc_correct = 0
    pc_total = 0
    for pid, comp, rub in joined:
        full_items = []
        for it in (rub.get("coval_full") or []):
            sc = [s["score"] for s in (it.get("scores") or [])]
            if sc:
                full_items.append(float(np.mean(sc)))
        if not full_items:
            continue
        pop_scores = {lab: 0.0 for lab in LABELS}
        any_sat = False
        for ci, w in enumerate(full_items):
            for lab in LABELS:
                key = (pid, ci, lab)
                if key in sat_full:
                    pop_scores[lab] += w * sat_full[key]
                    any_sat = True
        if not any_sat:
            continue
        pairs = human_pairs(comp["metadata"]["assessments"])
        for a, b in pairs:  # a preferred over b
            if pop_scores[a] == pop_scores[b]:
                continue  # ties uninformative for a binary accuracy count
            pc_total += 1
            if pop_scores[a] > pop_scores[b]:
                pc_correct += 1
    pc_acc = pc_correct / pc_total if pc_total else float("nan")
    pc_pass = pc_total > 0 and pc_acc > POS_CONTROL_FLOOR
    print(f"  population full-arm pairwise accuracy = {pc_acc:.4f} on {pc_total:,} pairs (floor {POS_CONTROL_FLOOR}) pass={pc_pass}")
    if not pc_pass:
        print("POSITIVE CONTROL FAILED -- the satisfaction tensor + rating weighting carries no "
              "detectable signal about held-out human rankings in this replication. A person-level "
              "breakdown of an instrument that has never returned a positive signal is silence, not "
              "evidence. Exiting nonzero.")
        sys.exit(1)

    # ---------------------------------------------------------------
    # MAIN PASS: build per-prompt cache, then per-assessment units.
    # ---------------------------------------------------------------
    print("== main pass ==")
    rng_shuffle = {s: np.random.default_rng(s) for s in SEEDS}

    n_excluded_tied = 0
    n_excluded_zero_weight = 0
    n_assessments_total = 0

    # dense-matrix-friendly records
    units = []  # dict per (person, prompt)

    for pid, comp, rub in joined:
        full_crits = []  # list of {annotator_id: score}
        for it in (rub.get("coval_full") or []):
            sc = {s["annotator_id"]: float(s["score"]) for s in (it.get("scores") or [])}
            if sc:
                full_crits.append(sc)
        n_core = len(rub.get("coval_core") or [])
        if n_core == 0 or not full_crits:
            continue

        # shared CORE score (identical for every person on this prompt)
        core_scores = {lab: 0.0 for lab in LABELS}
        core_ok = True
        for ci in range(n_core):
            for lab in LABELS:
                key = (pid, ci, lab)
                if key not in sat_core:
                    core_ok = False
                    break
                core_scores[lab] += sat_core[key]
            if not core_ok:
                break
        if not core_ok:
            continue
        for lab in LABELS:
            core_scores[lab] /= n_core
        core_rel = relation_from_scores(core_scores)

        # per-criterion consensus (leave-one-out mean) prep
        crit_values = [list(sc.values()) for sc in full_crits]

        asm = comp["metadata"]["assessments"]
        for a in asm:
            n_assessments_total += 1
            pid_person = a["annotator_id"]
            w_block = (a.get("ranking_blocks") or {}).get("world") or []
            if not w_block:
                n_excluded_tied += 1  # no ranking at all, folded into same bucket
                continue
            ranking_str = w_block[0].get("ranking", "")
            actual_rel, rank_of = relation_from_ranking(ranking_str)
            if len(set(rank_of.values())) <= 1:
                n_excluded_tied += 1
                continue

            # personalized FULL score for this person on this prompt
            full_scores = {lab: 0.0 for lab in LABELS}
            n_rated = 0
            abs_sum = 0.0
            consensus_dist_sum = 0.0
            consensus_dist_n = 0
            rated_ci = []
            rated_w = []
            for ci, sc in enumerate(full_crits):
                if pid_person not in sc:
                    continue
                w = sc[pid_person]
                n_rated += 1
                abs_sum += abs(w)
                others = [v for k2, v in sc.items() if k2 != pid_person]
                if others:
                    consensus_dist_sum += abs(w - float(np.mean(others)))
                    consensus_dist_n += 1
                rated_ci.append(ci)
                rated_w.append(w)
                for lab in LABELS:
                    key = (pid, ci, lab)
                    if key in sat_full:
                        full_scores[lab] += w * sat_full[key]
            if n_rated == 0:
                n_excluded_zero_weight += 1
                continue
            full_rel = relation_from_scores(full_scores)

            agr_full, nf = agreement(actual_rel, full_rel)
            agr_core, nc = agreement(actual_rel, core_rel)
            if agr_full is None or agr_core is None:
                continue
            gain = agr_full - agr_core

            rec = {
                "prompt_id": pid,
                "annotator_id": pid_person,
                "gain": gain,
                "agr_full": agr_full,
                "agr_core": agr_core,
                "n_rated": n_rated,
                "extremity": abs_sum / n_rated,
                "consensus_dist": (consensus_dist_sum / consensus_dist_n) if consensus_dist_n else None,
                "subjectivity": ordinal_lookup(a.get("subjectivity", ""), ORD_SUBJ),
                "importance": ordinal_lookup(a.get("importance", ""), ORD_IMP),
                "representativeness": ordinal_lookup(a.get("representativeness", ""), ORD_REP),
            }
            # shuffle placebo, one per seed
            gains_shuffled = {}
            for s in SEEDS:
                perm = rng_shuffle[s].permutation(len(rated_w))
                w_shuf = [rated_w[j] for j in perm]
                shuf_scores = {lab: 0.0 for lab in LABELS}
                for ci, w in zip(rated_ci, w_shuf):
                    for lab in LABELS:
                        key = (pid, ci, lab)
                        if key in sat_full:
                            shuf_scores[lab] += w * sat_full[key]
                shuf_rel = relation_from_scores(shuf_scores)
                agr_shuf, _ = agreement(actual_rel, shuf_rel)
                gains_shuffled[s] = (agr_shuf - agr_core) if agr_shuf is not None else None
            rec["gain_shuffled"] = gains_shuffled

            units.append(rec)

    n_valid_units = len(units)
    print(f"  joined prompts={n_prompts_joined}  assessments_total={n_assessments_total}")
    print(f"  excluded (tied/no-ranking)={n_excluded_tied}  excluded (zero rated criteria)={n_excluded_zero_weight}")
    print(f"  valid (person,prompt) units={n_valid_units}")

    if n_valid_units < 200:
        print("Too few valid units to support a person-level analysis. Exiting nonzero.")
        sys.exit(1)

    # ---------------------------------------------------------------
    # Aggregate to persons and prompts (dense matrices for cluster boot)
    # ---------------------------------------------------------------
    persons = sorted(set(u["annotator_id"] for u in units))
    prompts = sorted(set(u["prompt_id"] for u in units))
    p_idx = {p: i for i, p in enumerate(persons)}
    q_idx = {q: i for i, q in enumerate(prompts)}
    n_person_all, n_prompt_all = len(persons), len(prompts)

    G = np.zeros((n_person_all, n_prompt_all))       # gain sum (real)
    Gs = {s: np.zeros((n_person_all, n_prompt_all)) for s in SEEDS}  # shuffled gain sum
    M = np.zeros((n_person_all, n_prompt_all))        # presence indicator (0/1; unique per person-prompt)

    per_person_units = defaultdict(list)
    for u in units:
        i, j = p_idx[u["annotator_id"]], q_idx[u["prompt_id"]]
        G[i, j] = u["gain"]
        for s in SEEDS:
            gs = u["gain_shuffled"][s]
            if gs is not None:
                Gs[s][i, j] = gs
        M[i, j] = 1.0
        per_person_units[u["annotator_id"]].append(u)

    m_i_all = M.sum(axis=1)
    keep_person_mask = m_i_all >= MIN_PROMPTS
    kept_persons = [persons[i] for i in range(n_person_all) if keep_person_mask[i]]
    n_person_kept = len(kept_persons)
    print(f"  distinct persons with >=1 valid unit={n_person_all}; kept (>= {MIN_PROMPTS} prompts)={n_person_kept}")

    g_i_raw = np.divide(G.sum(axis=1), m_i_all, out=np.full(n_person_all, np.nan), where=m_i_all > 0)

    # prompt-mean gain (equal weight per prompt) and prompt-demeaned residual
    m_q = M.sum(axis=0)
    prompt_mean_gain = np.divide(G.sum(axis=0), m_q, out=np.full(n_prompt_all, np.nan), where=m_q > 0)
    R = np.zeros_like(G)
    for j in range(n_prompt_all):
        if m_q[j] > 0:
            R[:, j] = np.where(M[:, j] > 0, G[:, j] - prompt_mean_gain[j], 0.0)
    g_i_resid = np.divide(R.sum(axis=1), m_i_all, out=np.full(n_person_all, np.nan), where=m_i_all > 0)

    # ---------------------------------------------------------------
    # WITHIN-PERSON BOOTSTRAP FLOOR: resample each kept person's OWN
    # per-prompt gains with replacement -> SE_i. Multi-seed.
    # ---------------------------------------------------------------
    print("== within-person floor (resample each person's own prompts) ==")
    se_i_by_seed = {s: np.full(n_person_all, np.nan) for s in SEEDS}
    boot_gi_by_seed = {s: {} for s in SEEDS}  # person -> array of N_BOOT bootstrap means (for CI)
    for s in SEEDS:
        rng = np.random.default_rng(s)
        for i, person in enumerate(persons):
            if not keep_person_mask[i]:
                continue
            vals = np.array([u["gain"] for u in per_person_units[person]])
            m = len(vals)
            idx = rng.integers(0, m, size=(N_BOOT, m))
            boot_means = vals[idx].mean(axis=1)
            se_i_by_seed[s][i] = max(boot_means.std(ddof=1), 1e-6)
            boot_gi_by_seed[s][person] = boot_means

    se_i_avg = np.nanmean(np.stack([se_i_by_seed[s] for s in SEEDS]), axis=0)
    median_se_kept = float(np.nanmedian(se_i_avg[keep_person_mask]))
    between_person_sd_raw = float(np.nanstd(g_i_raw[keep_person_mask], ddof=1))
    between_person_sd_resid = float(np.nanstd(g_i_resid[keep_person_mask], ddof=1))
    sd_ratio = between_person_sd_raw / median_se_kept if median_se_kept > 0 else float("inf")

    # ---------------------------------------------------------------
    # tau^2 (DerSimonian-Laird) + person-cluster bootstrap CI, per seed
    # ---------------------------------------------------------------
    def dl_tau2(g, se):
        w = 1.0 / (se ** 2)
        gbar = np.sum(w * g) / np.sum(w)
        Q = np.sum(w * (g - gbar) ** 2)
        k = len(g)
        C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
        tau2 = max(0.0, (Q - (k - 1)) / C) if C > 0 else 0.0
        return tau2, gbar, Q

    tau2_by_seed = {}
    tau2_ci_by_seed = {}
    for s in SEEDS:
        g = g_i_raw[keep_person_mask]
        se = se_i_by_seed[s][keep_person_mask]
        tau2, gbar, Q = dl_tau2(g, se)
        tau2_by_seed[s] = tau2

        rng = np.random.default_rng(s + 1000)
        n_k = len(g)
        boots = np.empty(N_BOOT)
        for b in range(N_BOOT):
            samp = rng.integers(0, n_k, size=n_k)
            t2, _, _ = dl_tau2(g[samp], se[samp])
            boots[b] = t2
        lo, hi = np.percentile(boots, [2.5, 97.5])
        tau2_ci_by_seed[s] = (float(lo), float(hi))

    tau2_point_primary = tau2_by_seed[SEED]
    tau2_ci_primary = tau2_ci_by_seed[SEED]
    heterogeneity_tau2_positive = all(tau2_ci_by_seed[s][0] > 0 for s in SEEDS)
    heterogeneity_effect_floor_met = sd_ratio >= HETEROGENEITY_SD_RATIO_FLOOR
    heterogeneity_confirmed = heterogeneity_tau2_positive and heterogeneity_effect_floor_met

    print(f"  between-person SD(g_i) raw={between_person_sd_raw:.4f} resid(prompt-adj)={between_person_sd_resid:.4f}")
    print(f"  median within-person SE_i={median_se_kept:.4f}  ratio={sd_ratio:.2f} (floor {HETEROGENEITY_SD_RATIO_FLOOR})")
    print(f"  tau^2 primary(seed {SEED})={tau2_point_primary:.5f} CI={tau2_ci_primary}")
    print(f"  tau^2 CI excludes 0 for all seeds: {heterogeneity_tau2_positive}")
    print(f"  HETEROGENEITY CONFIRMED = {heterogeneity_confirmed}")

    # ---------------------------------------------------------------
    # PROMPT-CLUSTER BOOTSTRAP for the 4 scopes (resample PROMPTS)
    # ---------------------------------------------------------------
    print("== prompt-cluster bootstrap for the 4 scopes ==")

    # scope 1: pair-level pooled mean gain (weight by number of valid pairs
    # per unit -- approximated by weighting each unit equally within a
    # prompt draw, since per-unit pair counts are all 6 except rare
    # exclusions already dropped upstream; unit-level == pair-level here).
    pair_gains = np.array([u["gain"] for u in units])
    unit_prompt = np.array([q_idx[u["prompt_id"]] for u in units])
    unit_person = np.array([p_idx[u["annotator_id"]] for u in units])

    def scope_estimates(counts_q):
        # counts_q: (n_prompt_all,) resample multiplicities
        w_unit = counts_q[unit_prompt]
        scope1 = float(np.sum(pair_gains * w_unit) / np.sum(w_unit))  # unit-pooled
        # scope 2 same as scope1 here (unit == assessment; kept identical
        # by construction since every valid unit already carries exactly
        # one gain value); report separately in case future revision
        # reweights by pair-validity count.
        scope2 = scope1
        # scope3: person-level, equal weight per person
        gi = np.divide((G * counts_q[None, :]).sum(axis=1),
                       (M * counts_q[None, :]).sum(axis=1),
                       out=np.full(n_person_all, np.nan),
                       where=(M * counts_q[None, :]).sum(axis=1) > 0)
        scope3 = float(np.nanmean(gi[keep_person_mask]))
        # scope4: prompt-level, equal weight per DISTINCT prompt actually
        # drawn (weighting by multiplicity would just reproduce scope1-ish;
        # equal weight per distinct prompt matches "prompt has many people,
        # report per-prompt" framing).
        drawn = counts_q > 0
        pm = np.divide(G.sum(axis=0), m_q, out=np.full(n_prompt_all, np.nan), where=m_q > 0)
        scope4 = float(np.nanmean(pm[drawn]))
        return scope1, scope2, scope3, scope4

    scope_boot = {s: {"scope1": [], "scope2": [], "scope3": [], "scope4": []} for s in SEEDS}
    for s in SEEDS:
        rng = np.random.default_rng(s + 2000)
        for b in range(N_BOOT):
            draw = rng.integers(0, n_prompt_all, size=n_prompt_all)
            counts_q = np.bincount(draw, minlength=n_prompt_all).astype(float)
            s1, s2, s3, s4 = scope_estimates(counts_q)
            scope_boot[s]["scope1"].append(s1)
            scope_boot[s]["scope2"].append(s2)
            scope_boot[s]["scope3"].append(s3)
            scope_boot[s]["scope4"].append(s4)

    counts_q_real = np.ones(n_prompt_all)
    point1, point2, point3, point4 = scope_estimates(counts_q_real)

    def ci_from_boot(arr):
        a = np.array(arr)
        return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), float(np.std(a, ddof=1))

    scopes_out = {}
    for name, point in zip(["pair_level", "assessment_level", "person_level", "prompt_level"],
                            [point1, point2, point3, point4]):
        key = {"pair_level": "scope1", "assessment_level": "scope2",
               "person_level": "scope3", "prompt_level": "scope4"}[name]
        per_seed = {}
        for s in SEEDS:
            lo, hi, se = ci_from_boot(scope_boot[s][key])
            per_seed[str(s)] = {"ci_lo": lo, "ci_hi": hi, "boot_se": se}
        primary = per_seed[str(SEED)]
        scopes_out[name] = {
            "point_estimate": point,
            "prompt_cluster_boot_ci95": [primary["ci_lo"], primary["ci_hi"]],
            "prompt_cluster_boot_se": primary["boot_se"],
            "n_units_or_persons_or_prompts": {
                "pair_level": n_valid_units, "assessment_level": n_valid_units,
                "person_level": n_person_kept, "prompt_level": n_prompt_all,
            }[name],
            "per_seed": per_seed,
        }
        print(f"  {name}: point={point:.4f} CI95(seed {SEED})=[{primary['ci_lo']:.4f},{primary['ci_hi']:.4f}]")

    # ---------------------------------------------------------------
    # LOSER / WINNER classification, family-A multiplicity control
    # ---------------------------------------------------------------
    print("== per-person loser/winner classification (BH-FDR family A) ==")
    kept_idx = [i for i in range(n_person_all) if keep_person_mask[i]]
    pvals = np.full(len(kept_idx), np.nan)
    ci_lo = np.full(len(kept_idx), np.nan)
    ci_hi = np.full(len(kept_idx), np.nan)
    for row, i in enumerate(kept_idx):
        person = persons[i]
        boots = boot_gi_by_seed[SEED][person]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        ci_lo[row], ci_hi[row] = lo, hi
        # two-sided bootstrap p-value: 2*min(P(boot<=0), P(boot>=0))
        p_le = np.mean(boots <= 0.0)
        p_ge = np.mean(boots >= 0.0)
        pvals[row] = min(1.0, 2 * min(max(p_le, 1e-4), max(p_ge, 1e-4)))

    def bh_fdr(pv, q=0.05):
        pv = np.asarray(pv)
        n = len(pv)
        order = np.argsort(pv)
        ranked = pv[order]
        thresh = (np.arange(1, n + 1) / n) * q
        passed = ranked <= thresh
        if not passed.any():
            return np.zeros(n, dtype=bool)
        cutoff_rank = np.max(np.where(passed)[0])
        cutoff_p = ranked[cutoff_rank]
        return pv <= cutoff_p

    sig_mask = bh_fdr(pvals, FDR_Q)
    kept_g = g_i_raw[kept_idx]
    loser_mask = sig_mask & (kept_g > 0)
    winner_mask = sig_mask & (kept_g < 0)
    n_losers = int(loser_mask.sum())
    n_winners = int(winner_mask.sum())
    print(f"  tested={len(kept_idx)}  BH-significant={int(sig_mask.sum())}  losers(g_i>0)={n_losers}  winners(g_i<0)={n_winners}")

    loser_rows = []
    for row, i in enumerate(kept_idx):
        if loser_mask[row]:
            person = persons[i]
            loser_rows.append({
                "annotator_id": person, "g_i": float(g_i_raw[i]), "g_i_resid": float(g_i_resid[i]),
                "m_i": int(m_i_all[i]), "ci95": [float(ci_lo[row]), float(ci_hi[row])],
                "p": float(pvals[row]),
            })
    loser_rows.sort(key=lambda r: -r["g_i"])

    winner_rows = []
    for row, i in enumerate(kept_idx):
        if winner_mask[row]:
            person = persons[i]
            winner_rows.append({
                "annotator_id": person, "g_i": float(g_i_raw[i]), "g_i_resid": float(g_i_resid[i]),
                "m_i": int(m_i_all[i]), "ci95": [float(ci_lo[row]), float(ci_hi[row])],
                "p": float(pvals[row]),
            })
    winner_rows.sort(key=lambda r: r["g_i"])

    # ---------------------------------------------------------------
    # CONFOUND 1 -- mechanical shuffle placebo
    # ---------------------------------------------------------------
    print("== confound 1: shuffle placebo (mechanical-advantage check) ==")
    shuffle_out = {}
    for s in SEEDS:
        real_mean = float(np.mean([u["gain"] for u in units]))
        shuf_vals = [u["gain_shuffled"][s] for u in units if u["gain_shuffled"][s] is not None]
        shuf_mean = float(np.mean(shuf_vals))
        shuffle_out[str(s)] = {"true_pairing_mean_gain": real_mean, "shuffled_pairing_mean_gain": shuf_mean,
                                "ratio_shuffled_over_true": (shuf_mean / real_mean) if real_mean else None}
    print(f"  seed {SEED}: true={shuffle_out[str(SEED)]['true_pairing_mean_gain']:.4f} "
          f"shuffled={shuffle_out[str(SEED)]['shuffled_pairing_mean_gain']:.4f}")

    # ---------------------------------------------------------------
    # CONFOUND 2 -- shared-prompt variance decomposition
    # ---------------------------------------------------------------
    print("== confound 2: shared-prompt variance decomposition ==")
    between_prompt_sd = float(np.nanstd(prompt_mean_gain[m_q > 0], ddof=1))
    var_raw = between_person_sd_raw ** 2
    var_resid = between_person_sd_resid ** 2
    variance_retained_after_prompt_adjustment = (var_resid / var_raw) if var_raw > 0 else float("nan")
    print(f"  between-prompt SD={between_prompt_sd:.4f}  between-person SD raw={between_person_sd_raw:.4f} "
          f"resid={between_person_sd_resid:.4f}  variance retained={variance_retained_after_prompt_adjustment:.3f}")

    # ---------------------------------------------------------------
    # COVARIATE CHARACTERIZATION -- who are the losers?
    # ---------------------------------------------------------------
    print("== covariate characterization (family B) ==")
    cov_names = ["subjectivity", "importance", "representativeness", "n_rated", "extremity", "consensus_dist"]
    person_cov = {name: np.full(n_person_all, np.nan) for name in cov_names}
    person_prompt_difficulty = np.full(n_person_all, np.nan)
    for i, person in enumerate(persons):
        if not keep_person_mask[i]:
            continue
        recs = per_person_units[person]
        for name in cov_names:
            vals = [r[name] for r in recs if r[name] is not None]
            if vals:
                person_cov[name][i] = float(np.mean(vals))
        diffs = []
        for r in recs:
            j = q_idx[r["prompt_id"]]
            if m_q[j] > 1:
                # leave-one-out prompt mean excluding this person
                loo = (G[:, j].sum() - r["gain"]) / (m_q[j] - 1)
                diffs.append(loo)
        if diffs:
            person_prompt_difficulty[i] = float(np.mean(diffs))

    kept = np.array(kept_idx)
    y = g_i_raw[kept]
    X_cols = {"prompt_difficulty": person_prompt_difficulty[kept]}
    for name in cov_names:
        X_cols[name] = person_cov[name][kept]
    X_cols["log_m_i"] = np.log(m_i_all[kept])

    valid_row = np.ones(len(kept), dtype=bool)
    for arr in X_cols.values():
        valid_row &= ~np.isnan(arr)
    y_v = y[valid_row]
    Xc_v = {k: v[valid_row] for k, v in X_cols.items()}
    n_reg = int(valid_row.sum())
    print(f"  regression n={n_reg} (of {len(kept)} kept persons)")

    # univariate correlations (family B, part 1)
    univ = {}
    univ_p = []
    univ_names = []
    for name, arr in Xc_v.items():
        if np.std(arr) == 0:
            continue
        r_p, p_p = stats.pearsonr(arr, y_v)
        r_s, p_s = stats.spearmanr(arr, y_v)
        univ[name] = {"pearson_r": float(r_p), "pearson_p": float(p_p),
                       "spearman_r": float(r_s), "spearman_p": float(p_s),
                       "raw_slope": float(np.polyfit(arr, y_v, 1)[0]),
                       "n": int(len(arr))}
        univ_p.append(p_p)
        univ_names.append(name)
    univ_sig = bh_fdr(np.array(univ_p), FDR_Q) if univ_p else np.array([])
    for name, sig in zip(univ_names, univ_sig):
        univ[name]["bh_significant"] = bool(sig)

    # multivariate OLS + HC1 robust SE, standardized coefficients too
    xnames = list(Xc_v.keys())
    Xraw = np.column_stack([Xc_v[n] for n in xnames])
    Xstd = (Xraw - Xraw.mean(axis=0)) / Xraw.std(axis=0)
    n_ols, k_ols = Xraw.shape

    def ols_hc1(X, y):
        Xd = np.column_stack([np.ones(len(y)), X])
        n, k = Xd.shape
        XtX_inv = np.linalg.inv(Xd.T @ Xd)
        beta = XtX_inv @ Xd.T @ y
        resid = y - Xd @ beta
        meat = (Xd * (resid ** 2)[:, None]).T @ Xd
        cov = XtX_inv @ meat @ XtX_inv * (n / (n - k))
        se = np.sqrt(np.diag(cov))
        tstat = beta / se
        pval = 2 * (1 - stats.t.cdf(np.abs(tstat), df=n - k))
        return beta, se, pval

    beta_raw, se_raw, p_raw = ols_hc1(Xraw, y_v)
    beta_std, se_std, p_std = ols_hc1(Xstd, y_v)
    reg_p = list(p_raw[1:])
    reg_sig = bh_fdr(np.array(reg_p), FDR_Q)
    regression = {
        "n": n_ols,
        "predictors": xnames,
        "intercept_raw": float(beta_raw[0]), "intercept_se": float(se_raw[0]),
        "coef_raw": {n: float(b) for n, b in zip(xnames, beta_raw[1:])},
        "coef_raw_se": {n: float(s) for n, s in zip(xnames, se_raw[1:])},
        "coef_raw_p": {n: float(p) for n, p in zip(xnames, p_raw[1:])},
        "coef_standardized": {n: float(b) for n, b in zip(xnames, beta_std[1:])},
        "coef_standardized_se": {n: float(s) for n, s in zip(xnames, se_std[1:])},
        "bh_significant": {n: bool(sig) for n, sig in zip(xnames, reg_sig)},
        "se_type": "HC1 (White heteroskedasticity-robust)",
    }
    print("  regression coefficients (raw, standardized, BH-sig):")
    for n_ in xnames:
        print(f"    {n_:20s} raw={regression['coef_raw'][n_]:+.4f}  std={regression['coef_standardized'][n_]:+.4f}  "
              f"p={regression['coef_raw_p'][n_]:.4f}  sig={regression['bh_significant'][n_]}")

    # loser vs winner covariate contrast (permutation test on the mean diff)
    print("== loser vs winner covariate contrast (permutation test) ==")
    contrast = {}
    if n_losers >= 3 and n_winners >= 3:
        loser_ids = set(r["annotator_id"] for r in loser_rows)
        winner_ids = set(r["annotator_id"] for r in winner_rows)
        li = [p_idx[a] for a in loser_ids]
        wi = [p_idx[a] for a in winner_ids]
        rng = np.random.default_rng(SEED + 3000)
        for name in cov_names:
            lv = person_cov[name][li]
            wv = person_cov[name][wi]
            lv, wv = lv[~np.isnan(lv)], wv[~np.isnan(wv)]
            if len(lv) < 2 or len(wv) < 2:
                continue
            obs_diff = float(np.mean(lv) - np.mean(wv))
            pooled = np.concatenate([lv, wv])
            n_l = len(lv)
            null_diffs = np.empty(2000)
            for b in range(2000):
                perm = rng.permutation(pooled)
                null_diffs[b] = perm[:n_l].mean() - perm[n_l:].mean()
            p_perm = float(np.mean(np.abs(null_diffs) >= abs(obs_diff)))
            contrast[name] = {
                "loser_mean": float(np.mean(lv)), "winner_mean": float(np.mean(wv)),
                "abs_diff": obs_diff, "permutation_p": p_perm,
                "n_losers_valid": int(len(lv)), "n_winners_valid": int(len(wv)),
            }
        contrast_p = [v["permutation_p"] for v in contrast.values()]
        contrast_sig = bh_fdr(np.array(contrast_p), FDR_Q) if contrast_p else np.array([])
        for name, sig in zip(contrast.keys(), contrast_sig):
            contrast[name]["bh_significant"] = bool(sig)
        for name, v in contrast.items():
            print(f"  {name:20s} loser={v['loser_mean']:+.3f} winner={v['winner_mean']:+.3f} "
                  f"diff={v['abs_diff']:+.3f} p={v['permutation_p']:.4f} sig={v.get('bh_significant')}")
    else:
        print(f"  too few losers({n_losers}) or winners({n_winners}) for a contrast test (need >=3 each)")

    # ---------------------------------------------------------------
    # VERDICT
    # ---------------------------------------------------------------
    shuffle_survives = shuffle_out[str(SEED)]["shuffled_pairing_mean_gain"] < 0.7 * shuffle_out[str(SEED)]["true_pairing_mean_gain"]
    any_bh_covariate = any(v.get("bh_significant") for v in univ.values()) or any(regression["bh_significant"].values())

    if heterogeneity_confirmed and n_losers > 0:
        if variance_retained_after_prompt_adjustment > 0.3 and shuffle_survives:
            verdict = "OVERTURNED"
            verdict_reason = (
                "Real, resampling-floor-exceeding between-person heterogeneity in gain exists "
                f"({n_losers} BH-significant losers, {n_winners} BH-significant winners out of "
                f"{len(kept_idx)} tested at FDR q={FDR_Q}); it survives both the shared-prompt "
                "demeaning and the mechanical-advantage shuffle placebo, so it is not merely a "
                "prompt-composition or signal-quantity artifact."
            )
        elif not shuffle_survives:
            verdict = "UNVERIFIED"
            verdict_reason = (
                "Heterogeneity is statistically real but the shuffle placebo shows the gain is "
                "driven mostly by HOW MUCH personalized signal a person supplied (quantity/extremity), "
                "not by WHICH criteria matched their values -- the 'loser' label is not safely "
                "interpretable as a values-based redistribution claim from this design alone."
            )
        else:
            verdict = "UNVERIFIED"
            verdict_reason = (
                "Heterogeneity is statistically real but mostly explained by which PROMPTS a person "
                "happened to review (variance retained after prompt-demeaning "
                f"={variance_retained_after_prompt_adjustment:.2f}), so 'who is served worse' is "
                "confounded with prompt assignment rather than cleanly a property of the person."
            )
    else:
        verdict = "CONFIRMED"
        verdict_reason = (
            "Between-person variance in gain does not clear the pre-registered heterogeneity bar "
            "(tau^2 CI excludes 0 for all seeds AND SD ratio >= "
            f"{HETEROGENEITY_SD_RATIO_FLOOR}): {heterogeneity_confirmed}; observed spread is "
            "consistent with resampling noise around a common mean, so no systematic subgroup of "
            "people is detectably worse served by compilation at this power."
        )

    print(f"\n== VERDICT: {verdict} ==")
    print(f"   {verdict_reason}")

    strongest_reason_wrong = (
        "The 'personalized full arm' is built from the SAME person's own ratings that also, "
        "indirectly, informed how they later stated their world ranking -- both draw on the same "
        "underlying preferences, so even with an independent judge supplying satisfaction scores, "
        "some of the full-arm advantage over the person-agnostic core arm could be definitional "
        "(a person's own numbers will tend to reconstruct their own ordering better than anyone "
        "else's numbers would, regardless of whether the JUDGE's satisfaction signal is any good) "
        "rather than evidence that compilation specifically discards VALUE-relevant information. "
        "The shuffle placebo (confound 1) is the direct control for this, but it only rules out pure "
        "quantity/extremity artifacts, not this deeper same-person-two-instruments correlation."
    )

    runtime_seconds = time.time() - t_start

    out = {
        "prereg": PREREG,
        "environment": {
            "git_commit": git_commit(),
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
            "seed_primary": SEED,
            "seeds": SEEDS,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "data_summary": {
            "n_prompts_joined": n_prompts_joined,
            "n_assessments_total": n_assessments_total,
            "n_excluded_tied_or_no_ranking": n_excluded_tied,
            "n_excluded_zero_rated_criteria": n_excluded_zero_weight,
            "n_valid_units": n_valid_units,
            "n_persons_with_any_valid_unit": n_person_all,
            "n_persons_kept_min_prompts": n_person_kept,
        },
        "metric_placebo": placebo_cases,
        "positive_control": {
            "convention": "population mean-of-all-raters full-arm weight vs pooled human_pairs",
            "pairwise_accuracy": pc_acc, "n_pairs": pc_total,
            "floor": POS_CONTROL_FLOOR, "passed": pc_pass,
        },
        "headline_scopes": scopes_out,
        "within_person_floor": {
            "median_within_person_bootstrap_SE_avg_across_seeds": median_se_kept,
            "between_person_SD_raw": between_person_sd_raw,
            "between_person_SD_prompt_demeaned": between_person_sd_resid,
            "SD_ratio_raw_over_floor": sd_ratio,
            "ratio_floor_prereg": HETEROGENEITY_SD_RATIO_FLOOR,
            "floor_met": bool(heterogeneity_effect_floor_met),
        },
        "heterogeneity": {
            "tau2_primary_seed": tau2_point_primary,
            "tau2_ci95_primary_seed": list(tau2_ci_primary),
            "tau2_by_seed": {str(s): tau2_by_seed[s] for s in SEEDS},
            "tau2_ci_by_seed": {str(s): list(tau2_ci_by_seed[s]) for s in SEEDS},
            "tau2_ci_excludes_zero_all_seeds": bool(heterogeneity_tau2_positive),
            "confirmed": bool(heterogeneity_confirmed),
        },
        "losers": {
            "n_tested": len(kept_idx), "fdr_q": FDR_Q,
            "n_bh_significant": int(sig_mask.sum()),
            "n_losers_gain_positive": n_losers, "n_winners_gain_negative": n_winners,
            "top_losers": loser_rows[:20],
            "top_winners": winner_rows[:20],
        },
        "confound_1_mechanical_shuffle_placebo": shuffle_out,
        "confound_1_verdict": {
            "shuffle_gain_below_70pct_of_true_gain": bool(shuffle_survives),
        },
        "confound_2_shared_prompt_decomposition": {
            "between_prompt_SD_of_prompt_mean_gain": between_prompt_sd,
            "between_person_variance_raw": var_raw,
            "between_person_variance_after_prompt_demeaning": var_resid,
            "fraction_of_person_variance_retained_after_prompt_demeaning": variance_retained_after_prompt_adjustment,
        },
        "covariates": {
            "univariate": univ,
            "regression": regression,
            "loser_vs_winner_contrast": contrast,
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "strongest_reason_this_could_be_wrong": strongest_reason_wrong,
        "runtime_seconds": runtime_seconds,
    }

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {OUT}  ({runtime_seconds:.1f}s)")


if __name__ == "__main__":
    main()
