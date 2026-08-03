#!/usr/bin/env python
"""r134 independent_B -- do a person's OWN criterion ratings individuate their OWN
ranking better than a DIFFERENT person's ratings of the SAME criteria do?

===========================================================================
ESTIMAND (state before any code runs)
===========================================================================
UNIT: an (prompt, focal annotator P, stranger annotator Q, ranking-block T)
comparison, where T in {world, personal}.

For that unit, restrict to I = S_P intersect S_Q, the set of coval_full
criteria BOTH P and Q rated (a subset of the criteria rated by >=2 people in
that prompt -- write-in criteria rated by exactly one person can never enter
I by construction, so this design only ever compares on criteria for which a
genuine "own vs stranger" contrast is even possible).

  own_score(r)   = sum_{j in I} rating_P[j] * sat[prompt,j,r]
  stranger_score(r) = sum_{j in I} rating_Q[j] * sat[prompt,j,r]

sat[prompt,j,r] is the precomputed local-judge satisfaction proxy in [0,1]
(same fixed instrument for both arms -- it cancels in the direction of any
bias it carries). rating is the person's own signed -10..+10 score, so a
person who believes a criterion describes UNDESIRABLE behaviour contributes
a negative weight automatically (established fact: signed rating handles the
~quarter of negative-valence criteria per-person, no external convention
needed).

accuracy(score, actual_pairs) = fraction of the focal person's own actual
pairwise preferences (parsed from their own ranking string, ties dropped)
that `score` gets right (0.5 credit on an exact score tie).

  own_acc    = accuracy(own_score, P's own actual pairs)
  other_acc  = accuracy(stranger_score, P's own actual pairs)
  diff       = own_acc - other_acc

ESTIMAND: E[diff] over the population of eligible (prompt, P, Q, T) units.
diff > 0 (beyond the resampling floor, see below) means P's own ratings
carry information about P's own preferences that a same-criteria stranger's
ratings do not -- i.e. the elicitation individuated P. diff <= 0 (indistinct
from the floor) means a stranger's ratings on the identical criteria predict
P just as well as P's own ratings -- the elicitation did not individuate.

POPULATION scope: only (prompt, person) pairs where the person rated >= 3
criteria that were ALSO rated by >=2 people total (MIN_OWN), and only
strangers overlapping that person on >= MIN_SHARED of those criteria. This
excludes the ~9,684 single-rater write-in criteria entirely (no stranger
contrast is possible for them) and excludes people who rated too few shared
criteria to compute anything. Stated explicitly in the report, not implied.

INSTRUMENT scope: the local Qwen judge's satisfaction proxy + a linear
signed-weight rule. Not the OpenAI production compiler, not any other
aggregation rule.

BASELINE scope: a same-prompt, same-criteria-subset stranger. Not
population-average, not random noise, not a different prompt's stranger.

REGIME scope: coval_full criteria with >=2 raters only (empirically ~5.6
per prompt, capped at 6 in 968/968 prompts) -- a small, fixed "seed" pool,
not the full write-in-heavy criterion set.

===========================================================================
PRE-REGISTERED THRESHOLDS (fixed before the first accuracy number is seen)
===========================================================================
MIN_OWN         = 3   focal person must have rated >=3 multiply-rated criteria
MIN_SHARED_GRID = [3, 4, 6]   overlap-size grid for the multiplicity sweep
POS_CONTROL_PASS: leave-one-out crowd-vs-world pairwise accuracy > 0.55,
                  with bootstrap CI lower bound > 0.50
PLACEBO_BAND:     |random-weight accuracy - 0.5| < 0.01 (code-correctness
                  sanity, not a substantive claim)
FLOOR TEST:       observed |mean diff| must exceed the 95th percentile of
                  the stranger-vs-stranger placebo |diff| distribution
                  (one-sided) to count as a candidate finding
STANDARDIZED EFFECT: mean diff / floor SD ("individuation index"); SIG if
                  index > 2 AND Holm-corrected two-sided p < 0.05 on the
                  multiway-cluster bootstrap z-stat, in >= 1 grid cell
MULTIPLICITY:     Holm-Bonferroni across the 2 (block) x 3 (threshold) = 6
                  grid cells
CLUSTERING:       multiway (person-cluster + prompt-cluster - cell-cluster,
                  Cameron-Gelbach-Miller combination) cluster bootstrap,
                  B=2000, 5 seeds, report seed-to-seed spread
EXIT NONZERO:     if fewer than 500 valid units survive filtering in EITHER
                  block, or if the positive control fails outright (crowd
                  accuracy CI does not clear 0.50)

STRONGEST CONFOUND (written before running): if human preference for a
prompt is largely CONVERGENT -- most people agree on the best response
regardless of their own idiosyncratic ratings (e.g. one response is an
outright refusal or off-topic) -- then ANY plausible positively-weighted
combination of criteria applied to a satisfaction tensor that itself favors
the consensus response will get the right answer, inflating BOTH own_acc
and other_acc toward a shared ceiling and SHRINKING the observed diff toward
zero *regardless of true individuation*. This is a conservative confound
(it attenuates, not inflates, any positive finding) but it means a null
result here is also consistent with "individuation exists but this
prompt-set is too consensus-driven to reveal it". CONTROL run in this same
script: stratify by the focal person's own `subjectivity` field
("depends on a person's values/culture" vs "there is a single correct
answer") and report diff separately in each stratum. If real, the
own-advantage should be larger (or only present) in the values-dependent
stratum.

SEED: 4409 (base). BUDGET target: a few minutes wall clock, well under 35.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(REPO))
from covalx import load_join, parse_ranking  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

BASE_SEED = 4409
SEEDS = [BASE_SEED + i for i in range(5)]  # 5-seed requirement
MIN_OWN = 3
MIN_SHARED_GRID = [3, 4, 6]
N_BOOT = 2000
N_PLACEBO_DRAWS_PER_FOCAL = 8  # capped random stranger-pair draws for the floor
N_RANDOM_WEIGHT_UNITS = 20000  # subsample cap for the derive-by-hand placebo

LABELS = ("A", "B", "C", "D")


# --------------------------------------------------------------------- data
def build_prompt_table():
    """One row per prompt: sat matrix, shared-criterion index list, per-
    annotator rating dict restricted to shared criteria, and the parsed
    per-assessment (world, personal) pairwise preferences + subjectivity."""
    joined = load_join(str(REPO / "data/comparisons.jsonl"),
                        str(REPO / "data/conversation_rubrics.jsonl"))
    sat_full = np.load(REPO / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction"
                        "/results/a04_full.npz", allow_pickle=True)
    meta = sat_full["meta"]
    sat = sat_full["sat"]
    assert len(meta) == len(sat)
    assert len(meta) % 4 == 0

    # meta is grouped prompt-major, criterion-major, response-minor (A,B,C,D),
    # in the SAME prompt order as `joined` -- verified empirically against
    # load_join() before writing this script (order match + per-prompt count
    # match, both 100%). Reconstruct offsets by walking meta once.
    offsets = {}
    i = 0
    while i < len(meta):
        pid = meta[i].split("|")[0]
        start = i
        while i < len(meta) and meta[i].split("|")[0] == pid:
            i += 1
        offsets[pid] = (start, i)  # response-flat slice [start:end), len%4==0

    rows = []
    n_unmatched_offset = 0
    for pid, cmp_rec, rub_rec in joined:
        if pid not in offsets:
            n_unmatched_offset += 1
            continue
        start, end = offsets[pid]
        ncrit = (end - start) // 4
        sat_mat = sat[start:end].reshape(ncrit, 4)  # [criterion, response A-D]
        crits = rub_rec["coval_full"]
        assert len(crits) == ncrit

        shared_idx = []
        rating = defaultdict(dict)  # annotator_id -> {crit_idx: score}
        for j, c in enumerate(crits):
            if len(c["scores"]) >= 2:
                shared_idx.append(j)
                for s in c["scores"]:
                    rating[s["annotator_id"]][j] = float(s["score"])

        people = []
        for a in cmp_rec["metadata"]["assessments"]:
            aid = a["annotator_id"]
            rb = a.get("ranking_blocks") or {}
            wpairs = _pairs(rb.get("world"))
            ppairs = _pairs(rb.get("personal"))
            people.append(dict(
                annotator_id=aid,
                subjectivity=a.get("subjectivity"),
                world_pairs=wpairs,
                personal_pairs=ppairs,
                SP=set(rating.get(aid, {}).keys()) & set(shared_idx),
            ))

        rows.append(dict(prompt_id=pid, sat=sat_mat, shared_idx=shared_idx,
                          rating=rating, people=people))
    print(f"  prompts usable: {len(rows)} (offset-unmatched: {n_unmatched_offset})",
          flush=True)
    return rows


def _pairs(block):
    if not block:
        return []
    r = parse_ranking(block[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    out = []
    for a, ga in flat:
        for b, gb in flat:
            if ga < gb:
                out.append((a, b))
    return out


def accuracy(score, actual_pairs):
    lab2i = {l: i for i, l in enumerate(LABELS)}
    if not actual_pairs:
        return None
    correct = 0.0
    for a, b in actual_pairs:
        sa, sb = score[lab2i[a]], score[lab2i[b]]
        if sa > sb:
            correct += 1.0
        elif sa == sb:
            correct += 0.5
    return correct / len(actual_pairs)


# --------------------------------------------------------------- main build
def build_units(prompt_rows):
    """Flat record table: one row per (prompt, focal P, stranger Q, block)
    with own_acc/other_acc computed on I = SP & SQ (baseline MIN_SHARED=3)."""
    records = []  # dicts
    for row in prompt_rows:
        sat_mat = row["sat"]
        people = row["people"]
        n = len(people)
        for pi in range(n):
            P = people[pi]
            if len(P["SP"]) < MIN_OWN:
                continue
            for block, pairs_key in (("world", "world_pairs"), ("personal", "personal_pairs")):
                actual_pairs = P[pairs_key]
                if not actual_pairs:
                    continue
                for qi in range(n):
                    if qi == pi:
                        continue
                    Q = people[qi]
                    I = sorted(P["SP"] & Q["SP"])
                    if len(I) < 3:  # absolute floor to bother computing at all
                        continue
                    idx = np.array(I)
                    p_w = np.array([row["rating"][P["annotator_id"]][j] for j in I])
                    q_w = np.array([row["rating"][Q["annotator_id"]][j] for j in I])
                    sub = sat_mat[idx]  # [len(I), 4]
                    own_score = p_w @ sub
                    other_score = q_w @ sub
                    oa = accuracy(own_score, actual_pairs)
                    sa = accuracy(other_score, actual_pairs)
                    records.append((row["prompt_id"], P["annotator_id"],
                                     Q["annotator_id"], block, len(I), oa, sa,
                                     oa - sa, P["subjectivity"]))
    return records


# ------------------------------------------------------------- aggregation
def grid_cell(records, block, min_shared):
    rows = [r for r in records if r[3] == block and r[4] >= min_shared]
    return rows


def mean_diff(rows):
    if not rows:
        return None
    return float(np.mean([r[7] for r in rows]))


def _cluster_boot_means(codes, diffs, n_clusters, rng, n_boot):
    """Vectorized cluster bootstrap: resample `n_clusters` clusters with
    replacement (a multinomial draw of cluster multiplicities), then the
    resampled grand mean is (multiplicities . per-cluster sum) /
    (multiplicities . per-cluster count) -- exact, no per-draw Python loop
    over records, which is what makes B=2000 x tens-of-thousands-of-clusters
    tractable."""
    S = np.bincount(codes, weights=diffs, minlength=n_clusters)
    Cnt = np.bincount(codes, minlength=n_clusters).astype(float)
    M = rng.multinomial(n_clusters, np.full(n_clusters, 1.0 / n_clusters), size=n_boot)
    num = M @ S
    den = M @ Cnt
    return num / den


def multiway_cluster_bootstrap(rows, seeds, n_boot=N_BOOT):
    """Cameron-Gelbach-Miller two-way cluster bootstrap: person-cluster +
    prompt-cluster - cell-cluster (cell = (prompt,person) pair, i.e. the
    focal unit itself, its own aggregated mean-diff). Vectorized per cluster
    axis via multinomial resampling (see _cluster_boot_means)."""
    if not rows:
        return None
    diffs = np.array([r[7] for r in rows])
    prompts_raw = [r[0] for r in rows]
    persons_raw = [r[1] for r in rows]
    cells_raw = [f"{r[0]}|{r[1]}" for r in rows]

    _, prompt_codes = np.unique(prompts_raw, return_inverse=True)
    _, person_codes = np.unique(persons_raw, return_inverse=True)
    _, cell_codes = np.unique(cells_raw, return_inverse=True)
    n_prompts, n_persons, n_cells = prompt_codes.max() + 1, person_codes.max() + 1, cell_codes.max() + 1

    per_seed = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        m_prompt = _cluster_boot_means(prompt_codes, diffs, n_prompts, rng, n_boot)
        m_person = _cluster_boot_means(person_codes, diffs, n_persons, rng, n_boot)
        m_cell = _cluster_boot_means(cell_codes, diffs, n_cells, rng, n_boot)
        v_prompt, v_person, v_cell = m_prompt.var(ddof=1), m_person.var(ddof=1), m_cell.var(ddof=1)
        v_combined = max(v_prompt + v_person - v_cell, v_cell)  # floor at the finest estimate
        se = float(np.sqrt(v_combined))
        per_seed.append(dict(seed=sd, se_prompt=float(np.sqrt(v_prompt)),
                              se_person=float(np.sqrt(v_person)),
                              se_cell=float(np.sqrt(v_cell)),
                              se_combined=se))
    return per_seed


def stranger_vs_stranger_floor(records, block, min_shared, seeds):
    """Placebo: for each focal P, draw pairs of DISTINCT strangers (neither
    is P) and diff their other_acc against each other. Under the null of no
    individuation this should center at 0; its spread is the resampling
    floor any real own-vs-other difference must clear."""
    by_focal = defaultdict(list)  # (prompt,P,block) -> list of (Q, other_acc)
    for r in records:
        prompt_id, P, Q, blk, nI, oa, sa, diff, subj = r
        if blk != block or nI < min_shared:
            continue
        by_focal[(prompt_id, P)].append(sa)

    all_seed_diffs = {}
    for sd in seeds:
        rng = np.random.default_rng(sd)
        placebo_diffs = []
        for key, accs in by_focal.items():
            if len(accs) < 2:
                continue
            accs = np.array(accs)
            k = min(N_PLACEBO_DRAWS_PER_FOCAL, len(accs) * (len(accs) - 1) // 2)
            for _ in range(k):
                i, j = rng.choice(len(accs), size=2, replace=False)
                placebo_diffs.append(accs[i] - accs[j])
        all_seed_diffs[sd] = np.array(placebo_diffs)
    return all_seed_diffs


def random_weight_placebo(prompt_rows, seeds, cap=N_RANDOM_WEIGHT_UNITS):
    """Derive-by-hand placebo: weights drawn i.i.d. symmetric around 0,
    independent of the satisfaction tensor -> E[accuracy]=0.5 EXACTLY by
    symmetry, for any satisfaction structure. Verifies no code bug (e.g. a
    tie-break or direction error) rather than testing a substantive claim."""
    units = []  # (sat_sub[len(I),4], actual_pairs)
    for row in prompt_rows:
        sat_mat = row["sat"]
        for P in row["people"]:
            if len(P["SP"]) < MIN_OWN:
                continue
            for pairs in (P["world_pairs"], P["personal_pairs"]):
                if not pairs:
                    continue
                idx = np.array(sorted(P["SP"]))
                units.append((sat_mat[idx], pairs))

    results = {}
    for sd in seeds:
        rng = np.random.default_rng(sd)
        sub = units if len(units) <= cap else [units[i] for i in
                                                 rng.choice(len(units), size=cap, replace=False)]
        accs = []
        for sat_sub, pairs in sub:
            w = rng.normal(size=sat_sub.shape[0])
            score = w @ sat_sub
            a = accuracy(score, pairs)
            if a is not None:
                accs.append(a)
        results[sd] = float(np.mean(accs))
    return results, len(units)


def positive_control(prompt_rows, seeds, n_boot=1000):
    """Leave-one-out crowd (mean of all OTHER raters' signed ratings on the
    prompt's shared criteria) predicting the WORLD ranking. This is the
    'case whose answer is known': the project's own established result is
    that correctly-signed rubric scoring predicts held-out human rankings
    well above chance (~60%). If this in-script instrument does not clear
    chance here, the own-vs-stranger comparison downstream is not
    interpretable (a null from a dead instrument is silence, not evidence)."""
    accs = []
    prompt_ids_of_unit = []
    for row in prompt_rows:
        sat_mat = row["sat"]
        shared = row["shared_idx"]
        if not shared:
            continue
        idx = np.array(shared)
        for pi, P in enumerate(row["people"]):
            pairs = P["world_pairs"]
            if not pairs:
                continue
            # LOO crowd mean over shared idx, excluding P
            vals = []
            for j in shared:
                others = [row["rating"][q["annotator_id"]][j]
                          for q in row["people"] if q["annotator_id"] != P["annotator_id"]
                          and j in row["rating"].get(q["annotator_id"], {})]
                vals.append(np.mean(others) if others else 0.0)
            crowd_w = np.array(vals)
            score = crowd_w @ sat_mat[idx]
            a = accuracy(score, pairs)
            if a is not None:
                accs.append(a)
                prompt_ids_of_unit.append(row["prompt_id"])
    accs = np.array(accs)
    prompt_ids_of_unit = np.array(prompt_ids_of_unit)
    mean_acc = float(accs.mean())

    # prompt-cluster bootstrap CI, multi-seed
    uniq = np.unique(prompt_ids_of_unit)
    p2idx = defaultdict(list)
    for i, p in enumerate(prompt_ids_of_unit):
        p2idx[p].append(i)
    seed_cis = {}
    for sd in seeds:
        rng = np.random.default_rng(sd)
        means = np.empty(n_boot)
        for b in range(n_boot):
            draw = rng.choice(uniq, size=len(uniq), replace=True)
            idxs = np.concatenate([p2idx[k] for k in draw])
            means[b] = accs[idxs].mean()
        seed_cis[sd] = (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))
    return dict(n_units=len(accs), mean_acc=mean_acc, seed_cis=seed_cis)


def holm_bonferroni(pvals_named, alpha=0.05):
    items = sorted(pvals_named.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    for rank, (name, p) in enumerate(items):
        thresh = alpha / (m - rank)
        out[name] = dict(p=p, holm_threshold=thresh, reject=p < thresh)
    # enforce monotone stop rule: once a hypothesis fails, all lower-ranked ones fail too
    stopped = False
    for name, p in items:
        if stopped:
            out[name]["reject"] = False
        elif not out[name]["reject"]:
            stopped = True
    return out


def normal_p_two_sided(z):
    from scipy.stats import norm
    return float(2 * norm.sf(abs(z)))


# ------------------------------------------------------------------- main
def main():
    print("=== r134 independent_B: do ratings individuate? ===", flush=True)
    prompt_rows = build_prompt_table()

    print("[1/6] building flat comparison units (baseline overlap>=3) ...", flush=True)
    records = build_units(prompt_rows)
    print(f"  total records: {len(records)}", flush=True)
    n_world = sum(1 for r in records if r[3] == "world")
    n_personal = sum(1 for r in records if r[3] == "personal")
    print(f"  world={n_world} personal={n_personal}", flush=True)

    if n_world < 500 or n_personal < 500:
        print("FATAL: insufficient units to support the question at either block.", file=sys.stderr)
        sys.exit(1)

    print("[2/6] positive control: LOO crowd vs world ranking ...", flush=True)
    pc = positive_control(prompt_rows, SEEDS)
    pc_ci_lo = min(lo for lo, hi in pc["seed_cis"].values())
    pc_pass = pc["mean_acc"] > 0.55 and pc_ci_lo > 0.50
    print(f"  crowd accuracy = {pc['mean_acc']:.4f} (n={pc['n_units']}), "
          f"worst-seed CI lower bound = {pc_ci_lo:.4f}, PASS={pc_pass}", flush=True)
    if not pc_pass:
        print("FATAL: positive control failed -- instrument carries no "
              "demonstrated signal; a null downstream would be silence, "
              "not evidence.", file=sys.stderr)
        sys.exit(1)

    print("[3/6] derive-by-hand placebo: random weights -> E[accuracy]=0.5 ...", flush=True)
    rw_results, rw_n = random_weight_placebo(prompt_rows, SEEDS)
    rw_vals = list(rw_results.values())
    rw_ok = all(abs(v - 0.5) < 0.01 for v in rw_vals)
    print(f"  random-weight accuracy across {len(SEEDS)} seeds "
          f"(n_units~{min(rw_n, N_RANDOM_WEIGHT_UNITS)}): "
          f"{[round(v,4) for v in rw_vals]}  within-band={rw_ok}", flush=True)

    print("[4/6] multiplicity grid: 2 blocks x 3 thresholds ...", flush=True)
    grid = {}
    for block in ("world", "personal"):
        for thr in MIN_SHARED_GRID:
            rows = grid_cell(records, block, thr)
            md = mean_diff(rows)
            boot = multiway_cluster_bootstrap(rows, SEEDS)
            grid[f"{block}|thr{thr}"] = dict(
                block=block, min_shared=thr, n_units=len(rows), n_prompts=len(set(r[0] for r in rows)),
                n_focal_persons=len(set(r[1] for r in rows)), mean_diff=md,
                mean_own_acc=float(np.mean([r[5] for r in rows])) if rows else None,
                mean_other_acc=float(np.mean([r[6] for r in rows])) if rows else None,
                boot=boot,
            )

    print("[5/6] resampling floor: stranger-vs-stranger placebo per block/threshold ...", flush=True)
    floors = {}
    for block in ("world", "personal"):
        for thr in MIN_SHARED_GRID:
            seed_diffs = stranger_vs_stranger_floor(records, block, thr, SEEDS)
            sds = {sd: float(np.std(d)) if len(d) else None for sd, d in seed_diffs.items()}
            p95 = {sd: float(np.percentile(np.abs(d), 95)) if len(d) else None
                   for sd, d in seed_diffs.items()}
            n_draws = {sd: int(len(d)) for sd, d in seed_diffs.items()}
            floors[f"{block}|thr{thr}"] = dict(sd_by_seed=sds, p95_abs_by_seed=p95, n_draws_by_seed=n_draws)

    print("[6/6] assembling verdicts (Holm-Bonferroni over the 6-cell grid) ...", flush=True)
    pvals = {}
    for key, cell in grid.items():
        boot = cell["boot"]
        if boot is None or cell["mean_diff"] is None:
            pvals[key] = 1.0
            continue
        se = float(np.median([s["se_combined"] for s in boot]))  # median across seeds
        z = cell["mean_diff"] / se if se > 0 else 0.0
        pvals[key] = normal_p_two_sided(z)
        cell["se_combined_median"] = se
        cell["z"] = z
        floor_sd_med = float(np.nanmedian([v for v in floors[key]["sd_by_seed"].values() if v is not None]))
        floor_p95_med = float(np.nanmedian([v for v in floors[key]["p95_abs_by_seed"].values() if v is not None]))
        cell["floor_sd"] = floor_sd_med
        cell["floor_p95_abs"] = floor_p95_med
        cell["individuation_index"] = cell["mean_diff"] / floor_sd_med if floor_sd_med > 0 else None
        cell["clears_floor_p95"] = abs(cell["mean_diff"]) > floor_p95_med

    holm = holm_bonferroni(pvals)
    for key in grid:
        grid[key]["p_value"] = holm[key]["p"]
        grid[key]["holm_threshold"] = holm[key]["holm_threshold"]
        grid[key]["holm_reject"] = holm[key]["reject"]

    # secondary confound-control: subjectivity stratification (world block, thr=3)
    print("[extra] subjectivity stratification control ...", flush=True)
    strat = {}
    rows_w3 = grid_cell(records, "world", 3)
    subj_bucket = {}
    for r in rows_w3:
        subj = r[8] or ""
        bucket = ("values" if subj.startswith("The correct answer depends on a person")
                  else "single" if subj.startswith("There is a single correct")
                  else "other")
        subj_bucket.setdefault(bucket, []).append(r)
    for bucket, rows in subj_bucket.items():
        strat[bucket] = dict(n_units=len(rows), mean_diff=mean_diff(rows))

    any_finding = any(c["holm_reject"] and c["clears_floor_p95"] and
                       (c["individuation_index"] or 0) > 2 for c in grid.values())
    verdict = "CONFIRMED" if any_finding else "OVERTURNED"
    # if the instrument itself were degenerate this would be UNVERIFIED, but the
    # positive control gate above already exits nonzero in that case.

    out = dict(
        seed=BASE_SEED, seeds=SEEDS,
        estimand="own-vs-stranger accuracy at predicting the focal person's own "
                 "pairwise ranking, restricted to the exact criteria both rated",
        unit="(prompt, focal_person, stranger_person, ranking_block)",
        pre_registered=dict(MIN_OWN=MIN_OWN, MIN_SHARED_GRID=MIN_SHARED_GRID,
                             pos_control_pass_threshold=0.55,
                             placebo_band=0.01,
                             individuation_index_sig_threshold=2.0,
                             alpha=0.05),
        n_records_total=len(records), n_world=n_world, n_personal=n_personal,
        n_prompts_total=len(prompt_rows),
        positive_control=pc,
        random_weight_placebo=dict(by_seed=rw_results, n_units_pool=rw_n,
                                    within_band=rw_ok),
        grid=grid,
        floors=floors,
        subjectivity_stratification_control=strat,
        verdict=verdict,
    )

    out_path = RESULTS_DIR / "independent_B.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote {out_path}", flush=True)
    print(f"VERDICT: {verdict}", flush=True)
    for key, cell in grid.items():
        print(f"  {key}: n={cell['n_units']} mean_diff={cell['mean_diff']:.5f} "
              f"(own={cell['mean_own_acc']:.4f} other={cell['mean_other_acc']:.4f}) "
              f"floor_sd={cell['floor_sd']:.5f} idx={cell['individuation_index']:.3f} "
              f"p={cell['p_value']:.4g} holm_reject={cell['holm_reject']}", flush=True)


if __name__ == "__main__":
    main()
